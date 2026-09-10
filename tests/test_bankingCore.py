"""Banking Core domain, persistence and capture-adapter tests."""

from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
import socket

import pytest

from eolas.banking.identifiers import identifierBankingCreate
from eolas.banking.models import (
    AccountContinuityRole,
    AccountParty,
    AuthorityLink,
    AuthorityReadiness,
    BalanceObservation,
    BankingRelationship,
    BankingStatus,
    FinancialInstitution,
)
from eolas.banking.roles import PRIMARY_OPERATING_ROLE, roleCurrent
from eolas.banking.service import (
    BankingService,
    InstitutionCreateCommand,
    RelationshipCreateCommand,
)
from eolas.capture.models import CaptureInput, CaptureValidationError
from eolas.capture.service import capturePrepare, captureWrite
from eolas.clann.models import ClannInput, PersonInput
from eolas.clann.records import clannRecordStoreOpen
from eolas.clann.service import clannCreate
from eolas.cli import cliRun
from eolas.domain.codec import organisationEncode, personEncode
from eolas.domain.directory import contactsLoad, peopleLoad
from eolas.domain.entities import Organisation, Person
from eolas.domain.storage import VersionConflictError, WriteOperation, YamlRecordStore
from eolas.domain.values import (
    Classification,
    DomainValidationError,
    Fact,
    FactState,
    Identifier,
    LifecycleState,
    Money,
    Observation,
    Provenance,
    RecordIdentity,
    RecordLifecycle,
    RecordReference,
    ReviewState,
)

NOW = datetime(2026, 9, 10, 11, 0, tzinfo=timezone.utc)
CLANN = "clann-fictional-northbridge"
OTHER_CLANN = "clann-fictional-willowmere"


def _provenance(source: str = "fictionalFixture") -> Provenance:
    return Provenance(source, "northbridge-scenario", NOW)


def _review(*findings: str) -> ReviewState:
    return ReviewState(
        Fact.factKnown(date(2026, 9, 1)),
        Fact.factKnown(date(2027, 9, 1)),
        Fact(FactState.UNKNOWN),
        findings,
    )


def _organisation(clann_id: str = CLANN) -> Organisation:
    return Organisation(
        RecordIdentity.identityCreate(clann_id, "organisation", "shared"),
        "Northbridge Fictional Mutual",
        Classification.PRIVATE,
    )


def _service(tmp_path: Path, clann_id: str = CLANN) -> BankingService:
    return BankingService(YamlRecordStore(tmp_path / f"{clann_id}.yaml", clann_id))


def _institutionCommand(
    organisation: Organisation, clann_id: str = CLANN
) -> InstitutionCreateCommand:
    return InstitutionCreateCommand(
        clann_id,
        organisation.identity.referenceCreate(),
        "Northbridge Fictional Mutual",
        "bank",
        Classification.PRIVATE,
        _provenance(),
        _review(),
        Fact(FactState.UNKNOWN),
        Fact.factKnown("Fictional Compensation Scheme Group"),
    )


def _holder(clann_id: str, _name: str) -> AccountParty:
    party = RecordIdentity.identityCreate(
        clann_id, "contact", "shared"
    ).referenceCreate()
    return AccountParty(
        party,
        "legalHolder",
        "legalAndBeneficial",
        _provenance(),
    )


def _relationshipCommand(
    institution: FinancialInstitution,
    *,
    parties: tuple[AccountParty, ...] | None = None,
    ownership_type: str = "sole",
    roles: tuple[AccountContinuityRole, ...] = (),
    identifiers: tuple[Identifier, ...] = (),
    authority_links: tuple[AuthorityLink, ...] = (),
    balances: tuple[BalanceObservation, ...] = (),
    household: Fact[RecordReference] | None = None,
    status: BankingStatus = BankingStatus.ACTIVE,
    lifecycle: RecordLifecycle | None = None,
    clann_id: str = CLANN,
    label: str = "Household operating account",
) -> RelationshipCreateCommand:
    holder = parties if parties is not None else (_holder(clann_id, "Morgan Example"),)
    return RelationshipCreateCommand(
        clann_id,
        institution.identity.referenceCreate(),
        label,
        "current",
        "Household bills and salary",
        ownership_type,
        status,
        Classification.CONFIDENTIAL,
        _provenance(),
        _review(),
        Fact.factKnown("Fictional Everyday Current"),
        Fact.factKnown("GBP"),
        Fact.factKnown("app"),
        (
            Fact.factKnown("notApplicable")
            if ownership_type == "sole"
            else Fact.factKnown("eitherToSign")
        ),
        household or Fact(FactState.UNKNOWN),
        holder,
        roles,
        identifiers,
        authority_links,
        balances,
        lifecycle or RecordLifecycle(),
    )


def _persistOrganisation(store: YamlRecordStore, organisation: Organisation) -> None:
    store.recordsCommit((WriteOperation(organisationEncode(organisation), None),))


def testInstitutionCreateLinksOrganisationNotFreeText(tmp_path: Path) -> None:
    service = _service(tmp_path)
    organisation = _organisation()
    _persistOrganisation(service.store, organisation)

    institution = service.institutionCreate(_institutionCommand(organisation))

    assert institution.identity.record_id.startswith("rec_")
    assert "northbridge" not in institution.identity.record_id.lower()
    assert institution.organisation.record_type == "organisation"
    assert institution.organisation.record_id == organisation.identity.record_id
    assert institution.display_name == "Northbridge Fictional Mutual"
    assert institution.identity.owner_module == "banking"


def testInstitutionRejectsFreeTextOrganisationReference() -> None:
    identity = RecordIdentity.identityCreate(CLANN, "financialInstitution", "banking")
    with pytest.raises(DomainValidationError, match="Organisation"):
        FinancialInstitution(
            identity,
            RecordReference("rec_" + "a" * 32, CLANN, "person"),
            "Northbridge Fictional Mutual",
            "bank",
            Classification.PRIVATE,
            _provenance(),
            _review(),
        )


def testRelationshipCreateUsesStableOpaqueIds(tmp_path: Path) -> None:
    service = _service(tmp_path)
    organisation = _organisation()
    _persistOrganisation(service.store, organisation)
    institution = service.institutionCreate(_institutionCommand(organisation))

    relationship = service.relationshipCreate(_relationshipCommand(institution))

    loaded = service.relationshipGet(relationship.identity)
    assert loaded.identity == relationship.identity
    assert loaded.identity.record_id.startswith("rec_")
    assert loaded.institution.record_id == institution.identity.record_id
    assert "FICT" not in loaded.identity.record_id


def testClannIsolationRejectsCrossBoundaryUse(tmp_path: Path) -> None:
    home = _service(tmp_path, CLANN)
    other = _service(tmp_path, OTHER_CLANN)
    organisation = _organisation(CLANN)
    _persistOrganisation(home.store, organisation)
    institution = home.institutionCreate(_institutionCommand(organisation))

    with pytest.raises(DomainValidationError, match="cross-Clann"):
        other.institutionGet(institution.identity)
    foreignOrg = _organisation(OTHER_CLANN)
    with pytest.raises(DomainValidationError, match="[Cc]ross-[Cc]lann"):
        home.institutionCreate(_institutionCommand(foreignOrg, OTHER_CLANN))


def testAccountPartyOwnershipIsNotAuthority(tmp_path: Path) -> None:
    service = _service(tmp_path)
    organisation = _organisation()
    _persistOrganisation(service.store, organisation)
    institution = service.institutionCreate(_institutionCommand(organisation))
    holder = _holder(CLANN, "Morgan Example")

    relationship = service.relationshipCreate(
        _relationshipCommand(institution, parties=(holder,))
    )

    assert relationship.parties[0].party_role == "legalHolder"
    assert relationship.authority_links == ()
    with pytest.raises(DomainValidationError, match="authority"):
        AccountParty(
            holder.party,
            "attorney",
            "legal",
            _provenance(),
        )


def testJointOwnershipKeepsHoldersAndSigningRuleSeparate(tmp_path: Path) -> None:
    service = _service(tmp_path)
    organisation = _organisation()
    _persistOrganisation(service.store, organisation)
    institution = service.institutionCreate(_institutionCommand(organisation))
    morgan = AccountParty(
        RecordIdentity.identityCreate(CLANN, "contact", "shared").referenceCreate(),
        "legalHolder",
        "legalAndBeneficial",
        _provenance(),
        Fact.factKnown("60%"),
        Fact.factKnown("eitherToSign"),
    )
    riley = AccountParty(
        RecordIdentity.identityCreate(CLANN, "contact", "shared").referenceCreate(),
        "legalHolder",
        "beneficial",
        _provenance(),
        Fact.factKnown("40%"),
        Fact.factKnown("eitherToSign"),
    )

    relationship = service.relationshipCreate(
        _relationshipCommand(
            institution,
            parties=(morgan, riley),
            ownership_type="joint",
        )
    )

    assert relationship.ownership_type == "joint"
    assert relationship.signing_rule.value == "eitherToSign"
    assert {party.proportion.value for party in relationship.parties} == {"60%", "40%"}
    with pytest.raises(DomainValidationError, match="two legal holders"):
        service.relationshipCreate(
            _relationshipCommand(
                institution,
                parties=(morgan,),
                ownership_type="joint",
                label="Invalid joint",
            )
        )


def testNonOwnerAuthorityReferenceIsNotOwnership(tmp_path: Path) -> None:
    service = _service(tmp_path)
    organisation = _organisation()
    _persistOrganisation(service.store, organisation)
    institution = service.institutionCreate(_institutionCommand(organisation))
    holder = _holder(CLANN, "Morgan Example")
    authority = RecordIdentity.identityCreate(CLANN, "authority", "shared")
    link = AuthorityLink(
        authority.referenceCreate(),
        AuthorityReadiness.EXPECTED_NOT_REGISTERED,
        _provenance(),
    )

    relationship = service.relationshipCreate(
        _relationshipCommand(institution, parties=(holder,), authority_links=(link,))
    )

    assert relationship.parties[0].party_role == "legalHolder"
    assert relationship.authority_links[0].authority.record_id == authority.record_id
    assert (
        relationship.authority_links[0].readiness
        is AuthorityReadiness.EXPECTED_NOT_REGISTERED
    )
    assert all(party.party_role != "attorney" for party in relationship.parties)


def testContinuityRoleUsesVersionedRegistry(tmp_path: Path) -> None:
    service = _service(tmp_path)
    organisation = _organisation()
    _persistOrganisation(service.store, organisation)
    institution = service.institutionCreate(_institutionCommand(organisation))
    household = RecordIdentity.identityCreate(
        CLANN, "household", "shared"
    ).referenceCreate()
    role = AccountContinuityRole(
        "salaryReceipt",
        _provenance(),
        Fact.factKnown(household),
    )
    unknownRole = AccountContinuityRole("futureRoleFromNewerRegistry", _provenance())

    relationship = service.relationshipCreate(
        _relationshipCommand(institution, roles=(role, unknownRole))
    )

    assert relationship.continuity_roles[0].roleCurrent()
    assert not relationship.continuity_roles[1].roleCurrent()
    assert not roleCurrent("futureRoleFromNewerRegistry")


def testPrimaryOperatingAccountUniquenessPerHousehold(tmp_path: Path) -> None:
    service = _service(tmp_path)
    organisation = _organisation()
    _persistOrganisation(service.store, organisation)
    institution = service.institutionCreate(_institutionCommand(organisation))
    household = RecordIdentity.identityCreate(
        CLANN, "household", "shared"
    ).referenceCreate()
    role = AccountContinuityRole(
        PRIMARY_OPERATING_ROLE,
        _provenance(),
        Fact.factKnown(household),
    )
    service.relationshipCreate(
        _relationshipCommand(
            institution, roles=(role,), household=Fact.factKnown(household)
        )
    )

    with pytest.raises(DomainValidationError, match="primary operating"):
        service.relationshipCreate(
            _relationshipCommand(
                institution,
                roles=(role,),
                household=Fact.factKnown(household),
                label="Second operating account",
            )
        )

    exceptionRole = AccountContinuityRole(
        PRIMARY_OPERATING_ROLE,
        _provenance(),
        Fact.factKnown(household),
        exception_reason="Split operating accounts after a house move",
    )
    allowed = service.relationshipCreate(
        _relationshipCommand(
            institution,
            roles=(exceptionRole,),
            household=Fact.factKnown(household),
            label="Exception operating account",
        )
    )
    assert allowed.continuity_roles[0].exception_reason is not None


def testLifecycleAndOperationalStatusRemainDistinct(tmp_path: Path) -> None:
    service = _service(tmp_path)
    organisation = _organisation()
    _persistOrganisation(service.store, organisation)
    institution = service.institutionCreate(_institutionCommand(organisation))

    relationship = service.relationshipCreate(
        _relationshipCommand(
            institution,
            status=BankingStatus.DORMANT,
            lifecycle=RecordLifecycle(LifecycleState.HISTORIC, date(2020, 1, 1)),
        )
    )

    assert relationship.status is BankingStatus.DORMANT
    assert relationship.lifecycle.state is LifecycleState.HISTORIC


def testTypedIdentifiersAreMaskedAndNeverAggregateIds(tmp_path: Path) -> None:
    service = _service(tmp_path)
    organisation = _organisation()
    _persistOrganisation(service.store, organisation)
    institution = service.institutionCreate(_institutionCommand(organisation))
    identifier = identifierBankingCreate(
        "accountNumber",
        "FICT-HOUSEHOLD-0042",
        Classification.CONFIDENTIAL,
        provenance=_provenance(),
    )
    iban = identifierBankingCreate(
        "iban",
        "GB00EOLASFICT000000000",
        Classification.CONFIDENTIAL,
        provenance=_provenance(),
    )

    relationship = service.relationshipCreate(
        _relationshipCommand(institution, identifiers=(identifier, iban))
    )

    assert relationship.identifiers[0].identifierDisplay() == "••••0042"
    assert relationship.identifiers[0].identifierDisplay(allow_protected=True) == (
        "FICT-HOUSEHOLD-0042"
    )
    assert relationship.identity.record_id != "FICT-HOUSEHOLD-0042"
    assert relationship.identifiers[1].identifier_type == "iban"


def testIdentifierMaskingAndProhibitedContent() -> None:
    identifier = identifierBankingCreate(
        "customerNumber",
        "FICT-MEMBER-99",
        Classification.CONFIDENTIAL,
    )
    assert identifier.identifierDisplay().startswith("••••")
    assert identifier.identifierDisplay() != "FICT-MEMBER-99"

    with pytest.raises(DomainValidationError, match="Prohibited"):
        identifierBankingCreate("pin", "0000", Classification.CONFIDENTIAL)
    with pytest.raises(DomainValidationError, match="payment-card|Prohibited"):
        identifierBankingCreate(
            "creditCardAccountReference",
            "4111 1111 1111 1111",
            Classification.CONFIDENTIAL,
        )
    with pytest.raises(DomainValidationError, match="IBAN format"):
        identifierBankingCreate("iban", "not-an-iban", Classification.CONFIDENTIAL)


def testBalanceObservationRequiresAsOf(tmp_path: Path) -> None:
    service = _service(tmp_path)
    organisation = _organisation()
    _persistOrganisation(service.store, organisation)
    institution = service.institutionCreate(_institutionCommand(organisation))
    observation = Observation(
        Money(Decimal("12.34"), "GBP"),
        NOW,
        _provenance(),
    )

    relationship = service.relationshipCreate(
        _relationshipCommand(
            institution, balances=(BalanceObservation(observation, "emergency review"),)
        )
    )

    assert relationship.balances[0].observation.as_of == NOW
    assert relationship.balances[0].observation.value.amount == Decimal("12.34")
    with pytest.raises(TypeError):
        Observation(Money(Decimal("1.00"), "GBP"), provenance=_provenance())  # type: ignore[call-arg]


def testProvenanceClassificationAndReviewStateRoundTrip(tmp_path: Path) -> None:
    service = _service(tmp_path)
    organisation = _organisation()
    _persistOrganisation(service.store, organisation)
    institution = service.institutionCreate(_institutionCommand(organisation))
    review = _review("confirm salary still arrives here")

    created = service.relationshipCreate(
        RelationshipCreateCommand(
            CLANN,
            institution.identity.referenceCreate(),
            "Savings reserve",
            "savings",
            "Emergency reserve",
            "sole",
            BankingStatus.ACTIVE,
            Classification.CONFIDENTIAL,
            Provenance("manualCapture", "Willowmere passbook photocopy", NOW),
            review,
            parties=(_holder(CLANN, "Morgan Example"),),
        )
    )

    loaded = service.relationshipGet(created.identity)
    assert loaded.provenance.source_reference == "Willowmere passbook photocopy"
    assert loaded.classification is Classification.CONFIDENTIAL
    assert loaded.review.findings == ("confirm salary still arrives here",)
    assert loaded.review.last_reviewed.value == date(2026, 9, 1)


def testPersistenceRoundTripAndVersionConflict(tmp_path: Path) -> None:
    service = _service(tmp_path)
    organisation = _organisation()
    _persistOrganisation(service.store, organisation)
    institution = service.institutionCreate(_institutionCommand(organisation))
    created = service.relationshipCreate(_relationshipCommand(institution))
    stored = service.store.recordGet(created.identity)

    revised = BankingRelationship(
        created.identity,
        created.institution,
        "Household operating account",
        created.account_category,
        "Salary and essential bills",
        created.ownership_type,
        BankingStatus.ACTIVE,
        created.classification,
        created.provenance,
        created.review,
        created.product_name,
        created.currency,
        created.servicing_channel,
        created.signing_rule,
        created.household,
        created.parties,
        created.continuity_roles,
        created.identifiers,
        created.authority_links,
        created.balances,
        created.lifecycle,
    )
    updated = service.relationshipRevise(revised, stored.record_version)
    assert updated.purpose == "Salary and essential bills"
    assert service.store.recordHistory(created.identity)[0].payload["purpose"] == (
        "Household bills and salary"
    )
    with pytest.raises(VersionConflictError):
        service.relationshipRevise(revised, stored.record_version)


def testCaptureAdapterCreatesTypedBankingRecords(tmp_path: Path) -> None:
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
        "Northbridge bills",
        {
            "institution": "Northbridge Fictional Mutual",
            "institutionType": "bank",
            "accountCategory": "current",
            "productName": "Fictional Everyday Current",
            "purpose": "Household bills",
            "owners": ["Morgan Example", "Riley Example"],
            "status": "active",
            "classification": "confidential",
            "lastReviewed": "2026-09-01",
            "continuityRole": "primaryHouseholdBills",
            "identifierKind": "accountNumber",
            "identifierProtected": "FICT-HOUSEHOLD-0042",
            "currency": "GBP",
            "balanceAmount": "42.00",
            "balanceCurrency": "GBP",
            "balanceAsOf": NOW.isoformat(),
        },
        "fictional statement photocopy",
    )

    targetPath, document = capturePrepare(capture, clann, timestampProvider=lambda: NOW)
    assert targetPath == clann / "shared" / "records.yaml"
    assert document["aggregateType"] == "bankingRelationship"
    assert document["institution"]["displayName"] == "Northbridge Fictional Mutual"
    assert document["relationship"]["ownershipType"] == "joint"
    assert document["id"].startswith("rec_")

    captureWrite(targetPath, document)
    store = YamlRecordStore(targetPath, document["clannRef"])
    service = BankingService(store)
    relationship = service.relationshipGet(
        RecordIdentity(
            document["id"],
            document["clannRef"],
            "bankingRelationship",
            "banking",
        )
    )
    assert relationship.ownership_type == "joint"
    assert len(relationship.parties) == 2
    assert relationship.continuity_roles[0].role_id == "primaryHouseholdBills"
    assert relationship.identifiers[0].identifierDisplay() == "••••0042"
    assert relationship.balances[0].observation.as_of == NOW
    assert any(
        record.identity.aggregate_type == "organisation"
        for record in store.recordsList()
    )


def testCliCaptureBankingWritesTypedStore(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    clann = clannCreate(
        ClannInput(
            "Example Clann",
            "Example Home",
            [PersonInput("Alex Example", "Alex", "householder", True, True)],
        ),
        tmp_path,
        timestampProvider=lambda: NOW,
    )
    inputPath = tmp_path / "bank.yaml"
    inputPath.write_text(
        "institution: Willowmere Example Building Society\n"
        "accountCategory: savings\n"
        "productName: Fictional Instant Saver\n"
        "purpose: Emergency reserve\n"
        "owners: Morgan Example\n"
        "status: active\n"
        "classification: confidential\n"
        "lastReviewed: 2026-09-01\n"
        "continuityRole: emergencyReserve\n",
        encoding="utf-8",
    )
    arguments = [
        "capture",
        "banking",
        "--clann",
        str(clann),
        "--input",
        str(inputPath),
        "--label",
        "Emergency reserve",
        "--source",
        "fictional passbook",
    ]
    storePath = clann / "shared/records.yaml"

    assert cliRun(arguments) == 0
    store = YamlRecordStore(storePath, "clann-example-clann")
    assert store.recordsList(aggregate_type="bankingRelationship") == ()
    assert "Preview complete; no files were created" in capsys.readouterr().out

    assert cliRun([*arguments, "--confirm"]) == 0
    assert storePath.is_file()
    assert "Capture complete:" in capsys.readouterr().out
    store = YamlRecordStore(storePath, "clann-example-clann")
    relationships = store.recordsList(aggregate_type="bankingRelationship")
    assert len(relationships) == 1
    assert relationships[0].payload["purpose"] == "Emergency reserve"


def testBankingRequiresNoNetwork(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def networkFail(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "socket", networkFail)
    service = _service(tmp_path)
    organisation = _organisation()
    _persistOrganisation(service.store, organisation)
    institution = service.institutionCreate(_institutionCommand(organisation))
    relationship = service.relationshipCreate(_relationshipCommand(institution))
    assert service.relationshipGet(relationship.identity).label == (
        "Household operating account"
    )


def testCaptureStillRejectsProhibitedSecrets() -> None:
    fields = {
        "institution": "Northbridge Fictional Mutual",
        "accountCategory": "current",
        "productName": "Fictional Everyday Current",
        "purpose": "Household bills",
        "owners": "Morgan Example",
        "status": "active",
        "classification": "confidential",
        "lastReviewed": "2026-09-01",
        "password": "never-store",
    }
    with pytest.raises(CaptureValidationError, match="Prohibited"):
        CaptureInput("banking", "Bills", fields, "statement").captureValidate()


def _exampleClann(tmp_path: Path, people: list[PersonInput] | None = None) -> Path:
    return clannCreate(
        ClannInput(
            "Example Clann",
            "Example Home",
            people or [PersonInput("Alex Example", "Alex", "householder", True, True)],
        ),
        tmp_path,
        timestampProvider=lambda: NOW,
    )


def _bankingFields(**overrides: object) -> dict:
    fields: dict = {
        "institution": "Northbridge Fictional Mutual",
        "institutionType": "bank",
        "accountCategory": "current",
        "productName": "Fictional Everyday Current",
        "purpose": "Household bills",
        "owners": "Alex Example",
        "status": "active",
        "classification": "confidential",
        "lastReviewed": "2026-09-01",
    }
    fields.update(overrides)
    return fields


def testCaptureReusesExistingPersonAsSoleOwner(tmp_path: Path) -> None:
    clannPath = _exampleClann(tmp_path)
    people = peopleLoad(clannRecordStoreOpen(clannPath, "clann-example-clann"))
    alex = people[0]
    capture = CaptureInput("banking", "Bills", _bankingFields(), "fictional statement")

    targetPath, document = capturePrepare(
        capture, clannPath, timestampProvider=lambda: NOW
    )
    captureWrite(targetPath, document)
    store = YamlRecordStore(targetPath, "clann-example-clann")
    relationship = BankingService(store).relationshipGet(
        RecordIdentity(
            document["id"], "clann-example-clann", "bankingRelationship", "banking"
        )
    )

    assert relationship.parties[0].party.record_id == alex.identity.record_id
    assert relationship.parties[0].party.record_type == "person"
    assert contactsLoad(store) == ()
    assert all(
        operation["identity"]["aggregateType"] != "contact"
        for operation in document["operations"]
    )


def testCaptureReusesTwoPeopleAsJointOwners(tmp_path: Path) -> None:
    clannPath = _exampleClann(
        tmp_path,
        [
            PersonInput("Morgan Example", "Morgan", "householder", True, True),
            PersonInput("Riley Example", "Riley", "partner", True),
        ],
    )
    people = {
        person.display_name: person
        for person in peopleLoad(clannRecordStoreOpen(clannPath, "clann-example-clann"))
    }
    capture = CaptureInput(
        "banking",
        "Joint bills",
        _bankingFields(owners=["Morgan Example", "Riley Example"]),
        "fictional statement",
    )

    targetPath, document = capturePrepare(
        capture, clannPath, timestampProvider=lambda: NOW
    )
    captureWrite(targetPath, document)
    store = YamlRecordStore(targetPath, "clann-example-clann")
    relationship = BankingService(store).relationshipGet(
        RecordIdentity(
            document["id"], "clann-example-clann", "bankingRelationship", "banking"
        )
    )

    assert relationship.ownership_type == "joint"
    assert {party.party.record_id for party in relationship.parties} == {
        people["Morgan Example"].identity.record_id,
        people["Riley Example"].identity.record_id,
    }
    assert contactsLoad(store) == ()


def testCaptureUnresolvedPersonBecomesContact(tmp_path: Path) -> None:
    clannPath = _exampleClann(tmp_path)
    capture = CaptureInput(
        "banking",
        "Bills",
        _bankingFields(owners="Pat External"),
        "fictional statement",
    )

    targetPath, document = capturePrepare(
        capture, clannPath, timestampProvider=lambda: NOW
    )
    captureWrite(targetPath, document)
    store = YamlRecordStore(targetPath, "clann-example-clann")
    relationship = BankingService(store).relationshipGet(
        RecordIdentity(
            document["id"], "clann-example-clann", "bankingRelationship", "banking"
        )
    )

    assert relationship.parties[0].party.record_type == "contact"
    assert contactsLoad(store)[0].display_name == "Pat External"


def testCaptureDuplicatePersonNamesRequireOwnerRefs(tmp_path: Path) -> None:
    clannPath = _exampleClann(tmp_path)
    store = clannRecordStoreOpen(clannPath, "clann-example-clann")
    duplicate = Person(
        RecordIdentity.identityCreate("clann-example-clann", "person", "shared"),
        "Alex Example",
        Classification.PRIVATE,
    )
    store.recordsCommit((WriteOperation(personEncode(duplicate), None),))
    capture = CaptureInput("banking", "Bills", _bankingFields(), "fictional statement")

    with pytest.raises(DomainValidationError, match="ownerRefs"):
        capturePrepare(capture, clannPath, timestampProvider=lambda: NOW)

    people = peopleLoad(store)
    capture = CaptureInput(
        "banking",
        "Bills",
        _bankingFields(ownerRefs=[people[0].identity.record_id]),
        "fictional statement",
    )
    targetPath, document = capturePrepare(
        capture, clannPath, timestampProvider=lambda: NOW
    )
    captureWrite(targetPath, document)
    relationship = BankingService(store).relationshipGet(
        RecordIdentity(
            document["id"], "clann-example-clann", "bankingRelationship", "banking"
        )
    )
    assert relationship.parties[0].party.record_id == people[0].identity.record_id


def testCaptureReusesExistingFinancialInstitution(tmp_path: Path) -> None:
    clannPath = _exampleClann(tmp_path)
    first = CaptureInput("banking", "Bills", _bankingFields(), "fictional statement")
    targetPath, firstDocument = capturePrepare(
        first, clannPath, timestampProvider=lambda: NOW
    )
    captureWrite(targetPath, firstDocument)
    institutionId = firstDocument["institution"]["id"]
    organisationId = firstDocument["institution"]["organisationId"]

    second = CaptureInput(
        "banking",
        "Savings",
        _bankingFields(
            purpose="Emergency reserve",
            accountCategory="savings",
            institutionRef=institutionId,
        ),
        "fictional statement",
    )
    targetPath, secondDocument = capturePrepare(
        second, clannPath, timestampProvider=lambda: NOW
    )
    captureWrite(targetPath, secondDocument)
    store = YamlRecordStore(targetPath, "clann-example-clann")

    assert secondDocument["institution"]["id"] == institutionId
    assert secondDocument["institution"]["organisationId"] == organisationId
    assert len(store.recordsList(aggregate_type="organisation")) == 1
    assert len(store.recordsList(aggregate_type="financialInstitution")) == 1
    assert len(store.recordsList(aggregate_type="bankingRelationship")) == 2


def testCaptureUniqueInstitutionNameReusesProvider(tmp_path: Path) -> None:
    clannPath = _exampleClann(tmp_path)
    first = CaptureInput("banking", "Bills", _bankingFields(), "fictional statement")
    targetPath, firstDocument = capturePrepare(
        first, clannPath, timestampProvider=lambda: NOW
    )
    captureWrite(targetPath, firstDocument)
    second = CaptureInput(
        "banking",
        "Savings",
        _bankingFields(purpose="Emergency reserve", accountCategory="savings"),
        "fictional statement",
    )
    targetPath, secondDocument = capturePrepare(
        second, clannPath, timestampProvider=lambda: NOW
    )
    captureWrite(targetPath, secondDocument)
    store = YamlRecordStore(targetPath, "clann-example-clann")

    assert secondDocument["institution"]["id"] == firstDocument["institution"]["id"]
    assert len(store.recordsList(aggregate_type="organisation")) == 1
    assert len(store.recordsList(aggregate_type="financialInstitution")) == 1


def testCaptureInstitutionRefWinsOverDisplayName(tmp_path: Path) -> None:
    clannPath = _exampleClann(tmp_path)
    first = CaptureInput("banking", "Bills", _bankingFields(), "fictional statement")
    targetPath, firstDocument = capturePrepare(
        first, clannPath, timestampProvider=lambda: NOW
    )
    captureWrite(targetPath, firstDocument)

    second = CaptureInput(
        "banking",
        "Other label",
        _bankingFields(
            institution="Willowmere Example Building Society",
            institutionRef=firstDocument["institution"]["id"],
            purpose="Savings",
        ),
        "fictional statement",
    )
    targetPath, secondDocument = capturePrepare(
        second, clannPath, timestampProvider=lambda: NOW
    )
    captureWrite(targetPath, secondDocument)
    store = YamlRecordStore(targetPath, "clann-example-clann")

    assert secondDocument["institution"]["id"] == firstDocument["institution"]["id"]
    assert len(store.recordsList(aggregate_type="financialInstitution")) == 1


def testCaptureDuplicateInstitutionNamesRequireExplicitRef(tmp_path: Path) -> None:
    clannPath = _exampleClann(tmp_path)
    first = CaptureInput(
        "banking",
        "Bills",
        _bankingFields(createInstitution=True),
        "fictional statement",
    )
    targetPath, _document = capturePrepare(
        first, clannPath, timestampProvider=lambda: NOW
    )
    captureWrite(targetPath, _document)
    second = CaptureInput(
        "banking",
        "Other bills",
        _bankingFields(createInstitution=True, purpose="Second provider"),
        "fictional statement",
    )
    targetPath, secondDocument = capturePrepare(
        second, clannPath, timestampProvider=lambda: NOW
    )
    captureWrite(targetPath, secondDocument)
    assert (
        len(
            YamlRecordStore(targetPath, "clann-example-clann").recordsList(
                aggregate_type="financialInstitution"
            )
        )
        == 2
    )

    third = CaptureInput(
        "banking", "Third", _bankingFields(purpose="Ambiguous"), "fictional statement"
    )
    with pytest.raises(DomainValidationError, match="institutionRef"):
        capturePrepare(third, clannPath, timestampProvider=lambda: NOW)


def testCaptureRejectsUnknownInstitutionAndOwnerRefs(tmp_path: Path) -> None:
    clannPath = _exampleClann(tmp_path)
    missingInstitution = CaptureInput(
        "banking",
        "Bills",
        _bankingFields(
            institutionRef=RecordIdentity.identityCreate(
                "clann-example-clann", "financialInstitution", "banking"
            ).record_id
        ),
        "fictional statement",
    )
    with pytest.raises(DomainValidationError, match="institutionRef"):
        capturePrepare(missingInstitution, clannPath, timestampProvider=lambda: NOW)

    missingOwner = CaptureInput(
        "banking",
        "Bills",
        _bankingFields(
            ownerRefs=[
                RecordIdentity.identityCreate(
                    "clann-fictional-willowmere", "person", "shared"
                ).record_id
            ]
        ),
        "fictional statement",
    )
    with pytest.raises(DomainValidationError, match="Unknown party|Cross-Clann"):
        capturePrepare(missingOwner, clannPath, timestampProvider=lambda: NOW)
