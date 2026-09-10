"""Obligation, payment arrangement, movement and transaction-evidence tests."""

from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
import socket

import pytest

from eolas.banking.payments import (
    ARRANGEMENT_AGGREGATE,
    MoneyMovement,
    MovementDirection,
    Obligation,
    PaymentArrangement,
    TransactionObservation,
)
from eolas.banking.service import (
    BankingService,
    InstitutionCreateCommand,
    RelationshipCreateCommand,
)
from eolas.capture.models import CaptureInput
from eolas.capture.service import capturePrepare, captureWrite
from eolas.clann.models import ClannInput, PersonInput
from eolas.clann.service import clannCreate
from eolas.domain.codec import organisationEncode
from eolas.domain.entities import Organisation
from eolas.domain.storage import VersionConflictError, WriteOperation, YamlRecordStore
from eolas.domain.values import (
    Classification,
    DomainValidationError,
    Fact,
    FactState,
    Money,
    Observation,
    Provenance,
    RecordIdentity,
    RecordReference,
    ReviewState,
    Schedule,
)

NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)
CLANN = "clann-fictional-northbridge"


def _provenance() -> Provenance:
    return Provenance("fictionalFixture", "payments-scenario", NOW)


def _review() -> ReviewState:
    return ReviewState(
        Fact.factKnown(date(2026, 9, 1)),
        Fact(FactState.UNKNOWN),
        Fact(FactState.UNKNOWN),
    )


def _schedule() -> Schedule:
    return Schedule("monthly", Fact(FactState.UNKNOWN), "variable")


def _service(tmp_path: Path) -> BankingService:
    return BankingService(YamlRecordStore(tmp_path / "records.yaml", CLANN))


def _account(service: BankingService):
    organisation = Organisation(
        RecordIdentity.identityCreate(CLANN, "organisation", "shared"),
        "Northbridge Fictional Mutual",
        Classification.PRIVATE,
    )
    service.store.recordsCommit(
        (WriteOperation(organisationEncode(organisation), None),)
    )
    institution = service.institutionCreate(
        InstitutionCreateCommand(
            CLANN,
            organisation.identity.referenceCreate(),
            "Northbridge Fictional Mutual",
            "bank",
            Classification.PRIVATE,
            _provenance(),
            _review(),
        )
    )
    holder = RecordIdentity.identityCreate(CLANN, "contact", "shared").referenceCreate()
    from eolas.banking.models import AccountParty, BankingStatus

    relationship = service.relationshipCreate(
        RelationshipCreateCommand(
            CLANN,
            institution.identity.referenceCreate(),
            "Household operating account",
            "current",
            "Household bills and salary",
            "sole",
            BankingStatus.ACTIVE,
            Classification.CONFIDENTIAL,
            _provenance(),
            _review(),
            parties=(
                AccountParty(
                    holder, "legalHolder", "legalAndBeneficial", _provenance()
                ),
            ),
        )
    )
    return organisation, institution, relationship


def _obligation(purpose: str = "Electricity supply") -> Obligation:
    return Obligation(
        RecordIdentity.identityCreate(CLANN, "obligation", "banking"),
        purpose,
        Classification.CONFIDENTIAL,
        _provenance(),
        _review(),
        Fact(FactState.UNKNOWN),
        "essential",
    )


def testObligationIsNotAPaymentInstruction(tmp_path: Path) -> None:
    service = _service(tmp_path)
    _account(service)
    created = service.obligationCreate(_obligation())

    assert created.identity.aggregate_type == "obligation"
    assert created.identity.record_id.startswith("rec_")
    assert created.essentiality == "essential"


def testPaymentArrangementRequiresObligationAndFundingAccount(tmp_path: Path) -> None:
    service = _service(tmp_path)
    _organisation, _institution, relationship = _account(service)
    obligation = service.obligationCreate(_obligation())
    arrangement = PaymentArrangement(
        RecordIdentity.identityCreate(CLANN, ARRANGEMENT_AGGREGATE, "banking"),
        "directDebit",
        "Electricity Direct Debit",
        obligation.identity.referenceCreate(),
        relationship.identity.referenceCreate(),
        Classification.CONFIDENTIAL,
        _provenance(),
        _review(),
        _schedule(),
    )

    stored = service.arrangementCreate(arrangement)

    assert stored.mechanism == "directDebit"
    assert stored.obligation.record_id == obligation.identity.record_id
    assert stored.funding_account.record_id == relationship.identity.record_id
    assert stored.status == "active"


def testArrangementCannotUseInstructionAsObligation(tmp_path: Path) -> None:
    service = _service(tmp_path)
    _organisation, _institution, relationship = _account(service)
    fakeInstruction = RecordReference(
        RecordIdentity.identityCreate(CLANN, "paymentArrangement", "banking").record_id,
        CLANN,
        "paymentArrangement",
    )
    with pytest.raises(DomainValidationError, match="instruction as its obligation"):
        PaymentArrangement(
            RecordIdentity.identityCreate(CLANN, ARRANGEMENT_AGGREGATE, "banking"),
            "standingOrder",
            "Invalid",
            fakeInstruction,
            relationship.identity.referenceCreate(),
            Classification.CONFIDENTIAL,
            _provenance(),
            _review(),
            _schedule(),
        )


def testCancellingArrangementLeavesObligationOpen(tmp_path: Path) -> None:
    service = _service(tmp_path)
    _organisation, _institution, relationship = _account(service)
    obligation = service.obligationCreate(_obligation())
    arrangement = service.arrangementCreate(
        PaymentArrangement(
            RecordIdentity.identityCreate(CLANN, ARRANGEMENT_AGGREGATE, "banking"),
            "directDebit",
            "Electricity Direct Debit",
            obligation.identity.referenceCreate(),
            relationship.identity.referenceCreate(),
            Classification.CONFIDENTIAL,
            _provenance(),
            _review(),
            _schedule(),
        )
    )
    stored = service.store.recordGet(arrangement.identity)

    cancelled = service.arrangementRevise(
        arrangement.arrangementCancelled(), stored.record_version
    )
    reloaded = service.obligationGet(obligation.identity)

    assert cancelled.status == "cancelled"
    assert reloaded.status == "active"
    assert reloaded.purpose == "Electricity supply"


def testDirectDebitAndStandingOrderRemainDistinct(tmp_path: Path) -> None:
    service = _service(tmp_path)
    _organisation, _institution, relationship = _account(service)
    bill = service.obligationCreate(_obligation())
    rent = service.obligationCreate(_obligation("Fictional rent"))
    debit = service.arrangementCreate(
        PaymentArrangement(
            RecordIdentity.identityCreate(CLANN, ARRANGEMENT_AGGREGATE, "banking"),
            "directDebit",
            "Electricity Direct Debit",
            bill.identity.referenceCreate(),
            relationship.identity.referenceCreate(),
            Classification.CONFIDENTIAL,
            _provenance(),
            _review(),
            _schedule(),
        )
    )
    order = service.arrangementCreate(
        PaymentArrangement(
            RecordIdentity.identityCreate(CLANN, ARRANGEMENT_AGGREGATE, "banking"),
            "standingOrder",
            "Rent standing order",
            rent.identity.referenceCreate(),
            relationship.identity.referenceCreate(),
            Classification.CONFIDENTIAL,
            _provenance(),
            _review(),
            Schedule("monthly", Fact(FactState.UNKNOWN), "fixed"),
        )
    )

    assert debit.mechanism == "directDebit"
    assert order.mechanism == "standingOrder"
    assert debit.mechanism != order.mechanism


def testSalaryInflowDoesNotRequirePaymentArrangement(tmp_path: Path) -> None:
    service = _service(tmp_path)
    _organisation, _institution, relationship = _account(service)
    movement = service.movementCreate(
        MoneyMovement(
            RecordIdentity.identityCreate(CLANN, "moneyMovement", "banking"),
            MovementDirection.INFLOW,
            "Fictional salary",
            relationship.identity.referenceCreate(),
            Classification.CONFIDENTIAL,
            _provenance(),
            _review(),
            Schedule("monthly", Fact(FactState.UNKNOWN), "variable"),
            Fact.factKnown(Money(Decimal("1.00"), "GBP")),
        )
    )

    assert movement.direction is MovementDirection.INFLOW
    assert movement.arrangement.state is FactState.UNKNOWN


def testTransactionObservationDoesNotChangeArrangement(tmp_path: Path) -> None:
    service = _service(tmp_path)
    _organisation, _institution, relationship = _account(service)
    obligation = service.obligationCreate(_obligation())
    arrangement = service.arrangementCreate(
        PaymentArrangement(
            RecordIdentity.identityCreate(CLANN, ARRANGEMENT_AGGREGATE, "banking"),
            "directDebit",
            "Electricity Direct Debit",
            obligation.identity.referenceCreate(),
            relationship.identity.referenceCreate(),
            Classification.CONFIDENTIAL,
            _provenance(),
            _review(),
            _schedule(),
        )
    )
    movement = service.movementCreate(
        MoneyMovement(
            RecordIdentity.identityCreate(CLANN, "moneyMovement", "banking"),
            MovementDirection.OUTFLOW,
            "Electricity Direct Debit",
            relationship.identity.referenceCreate(),
            Classification.CONFIDENTIAL,
            _provenance(),
            _review(),
            _schedule(),
            Fact(FactState.UNKNOWN),
            Fact(FactState.UNKNOWN),
            Fact.factKnown(obligation.identity.referenceCreate()),
            Fact.factKnown(arrangement.identity.referenceCreate()),
        )
    )

    observed = service.transactionCreate(
        TransactionObservation(
            RecordIdentity.identityCreate(CLANN, "transactionObservation", "banking"),
            Observation(Money(Decimal("42.00"), "GBP"), NOW, _provenance()),
            relationship.identity.referenceCreate(),
            Classification.CONFIDENTIAL,
            _provenance(),
            "fictional statement line",
            Fact.factKnown(movement.identity.referenceCreate()),
            Fact.factKnown(arrangement.identity.referenceCreate()),
            Fact.factKnown(obligation.identity.referenceCreate()),
        )
    )
    reloaded = service.arrangementGet(arrangement.identity)

    assert observed.observation.as_of == NOW
    assert observed.observation.value.amount == Decimal("42.00")
    assert reloaded.status == "active"
    assert observed.identity.aggregate_type == "transactionObservation"
    assert observed.arrangement.value.record_type == "paymentArrangement"


def testTransactionCannotBeRecordedAsArrangement() -> None:
    account = RecordIdentity.identityCreate(
        CLANN, "bankingRelationship", "banking"
    ).referenceCreate()
    with pytest.raises(DomainValidationError, match="payment arrangement"):
        TransactionObservation(
            RecordIdentity.identityCreate(CLANN, "transactionObservation", "banking"),
            Observation(Money(Decimal("5.00"), "GBP"), NOW, _provenance()),
            account,
            Classification.CONFIDENTIAL,
            _provenance(),
            arrangement=Fact.factKnown(
                RecordIdentity.identityCreate(
                    CLANN, "moneyMovement", "banking"
                ).referenceCreate()
            ),
        )


def testPaymentPersistenceRoundTripAndVersionConflict(tmp_path: Path) -> None:
    service = _service(tmp_path)
    _organisation, _institution, relationship = _account(service)
    obligation = service.obligationCreate(_obligation())
    created = service.arrangementCreate(
        PaymentArrangement(
            RecordIdentity.identityCreate(CLANN, ARRANGEMENT_AGGREGATE, "banking"),
            "directDebit",
            "Electricity Direct Debit",
            obligation.identity.referenceCreate(),
            relationship.identity.referenceCreate(),
            Classification.CONFIDENTIAL,
            _provenance(),
            _review(),
            _schedule(),
        )
    )
    stored = service.store.recordGet(created.identity)
    updated = service.arrangementRevise(
        created.arrangementCancelled(), stored.record_version
    )

    assert service.arrangementGet(created.identity).status == "cancelled"
    assert (
        service.store.recordHistory(created.identity)[0].payload["status"] == "active"
    )
    with pytest.raises(VersionConflictError):
        service.arrangementRevise(updated, stored.record_version)


def testPaymentRecordsRejectCrossClannFunding(tmp_path: Path) -> None:
    service = _service(tmp_path)
    _organisation, _institution, relationship = _account(service)
    obligation = service.obligationCreate(_obligation())
    foreignAccount = RecordReference(
        relationship.identity.record_id, "another-clann", "bankingRelationship"
    )
    with pytest.raises(DomainValidationError, match="Cross-Clann"):
        PaymentArrangement(
            RecordIdentity.identityCreate(CLANN, ARRANGEMENT_AGGREGATE, "banking"),
            "directDebit",
            "Electricity Direct Debit",
            obligation.identity.referenceCreate(),
            foreignAccount,
            Classification.CONFIDENTIAL,
            _provenance(),
            _review(),
            _schedule(),
        )


def testPaymentSecretsAreRejected() -> None:
    identity = RecordIdentity.identityCreate(CLANN, "obligation", "banking")
    with pytest.raises(DomainValidationError, match="payment-card|Prohibited"):
        Obligation(
            identity,
            "4111 1111 1111 1111",
            Classification.CONFIDENTIAL,
            _provenance(),
            _review(),
        )


def testCaptureAdapterCreatesTypedPaymentRecords(tmp_path: Path) -> None:
    clann = clannCreate(
        ClannInput(
            "Example Clann",
            "Example Home",
            [PersonInput("Alex Example", "Alex", "householder", True, True)],
        ),
        tmp_path,
        timestampProvider=lambda: NOW,
    )
    capture = CaptureInput(
        "banking",
        "Household bills",
        {
            "institution": "Northbridge Fictional Mutual",
            "accountCategory": "current",
            "productName": "Fictional Everyday Current",
            "purpose": "Household bills",
            "owners": "Alex Example",
            "status": "active",
            "classification": "confidential",
            "lastReviewed": "2026-09-01",
            "obligationPurpose": "Electricity supply",
            "obligationEssentiality": "essential",
            "paymentMechanism": "directDebit",
            "paymentFrequency": "monthly",
            "transactionAmount": "42.00",
            "transactionCurrency": "GBP",
            "transactionAsOf": NOW.isoformat(),
        },
        "fictional statement photocopy",
    )

    targetPath, document = capturePrepare(capture, clann, timestampProvider=lambda: NOW)
    captureWrite(targetPath, document)
    store = YamlRecordStore(targetPath, "clann-example-clann")
    service = BankingService(store)

    assert document["payments"]["obligationId"].startswith("rec_")
    assert document["payments"]["arrangementId"].startswith("rec_")
    obligation = service.obligationGet(
        RecordIdentity(
            document["payments"]["obligationId"],
            "clann-example-clann",
            "obligation",
            "banking",
        )
    )
    arrangement = service.arrangementGet(
        RecordIdentity(
            document["payments"]["arrangementId"],
            "clann-example-clann",
            "paymentArrangement",
            "banking",
        )
    )
    transaction = service.transactionGet(
        RecordIdentity(
            document["payments"]["transactionId"],
            "clann-example-clann",
            "transactionObservation",
            "banking",
        )
    )
    assert obligation.purpose == "Electricity supply"
    assert arrangement.mechanism == "directDebit"
    assert arrangement.obligation.record_id == obligation.identity.record_id
    assert transaction.observation.as_of == NOW
    cancelled = service.arrangementRevise(
        arrangement.arrangementCancelled(),
        store.recordGet(arrangement.identity).record_version,
    )
    assert cancelled.status == "cancelled"
    assert service.obligationGet(obligation.identity).status == "active"


def testPaymentsRequireNoNetwork(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def networkFail(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "socket", networkFail)
    service = _service(tmp_path)
    _organisation, _institution, relationship = _account(service)
    obligation = service.obligationCreate(_obligation())
    assert service.obligationGet(obligation.identity).purpose == "Electricity supply"
    assert relationship.label == "Household operating account"
