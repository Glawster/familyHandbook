"""Obligation, payment arrangement, expected movement and transaction evidence.

A Direct Debit instruction is not the bill. A statement transaction is not the
standing arrangement that caused it. Cancelling a payment arrangement does not
settle or cancel the obligation.
"""

from dataclasses import dataclass, replace
from enum import Enum
from typing import Mapping, Optional, Tuple

from eolas.banking.models import RELATIONSHIP_AGGREGATE, bankingIdentityValidate
from eolas.domain.security import classificationResolve, secretsValidate
from eolas.domain.values import (
    Classification,
    DomainValidationError,
    EvidenceReference,
    Fact,
    FactState,
    Identifier,
    Money,
    Observation,
    Provenance,
    RecordIdentity,
    RecordLifecycle,
    RecordReference,
    ReviewState,
    Schedule,
    clannBoundaryValidate,
)

OBLIGATION_AGGREGATE = "obligation"
ARRANGEMENT_AGGREGATE = "paymentArrangement"
MOVEMENT_AGGREGATE = "moneyMovement"
TRANSACTION_AGGREGATE = "transactionObservation"

INSTRUCTION_TYPES = {
    ARRANGEMENT_AGGREGATE,
    MOVEMENT_AGGREGATE,
    TRANSACTION_AGGREGATE,
}

CURRENT_MECHANISM_REGISTRY_VERSION = "1"
PAYMENT_MECHANISM_REGISTRY: Mapping[str, Mapping[str, str]] = {
    CURRENT_MECHANISM_REGISTRY_VERSION: {
        "directDebit": "Direct Debit instruction",
        "standingOrder": "Standing order",
        "scheduledTransfer": "Scheduled bank transfer",
        "internalTransfer": "Internal transfer",
        "recurringCard": "Recurring card payment or continuous payment authority",
        "cheque": "Cheque",
        "manualTransfer": "Manual bank transfer",
        "variableRecurringPayment": "Variable Recurring Payment permission",
        "unknown": "Unknown mechanism",
    }
}

ESSENTIALITY_VALUES = {"essential", "important", "nonEssential", "unknown"}
OBLIGATION_STATUSES = {"active", "ended", "unknown"}
ARRANGEMENT_STATUSES = {"active", "paused", "cancelled", "expired", "unknown"}


class MovementDirection(str, Enum):
    """Whether money is expected to arrive or leave."""

    INFLOW = "inflow"
    OUTFLOW = "outflow"


def mechanismCurrent(
    mechanism: str, registry_version: str = CURRENT_MECHANISM_REGISTRY_VERSION
) -> bool:
    """Unknown mechanisms are retained but cannot drive current workflows."""
    return mechanism in PAYMENT_MECHANISM_REGISTRY.get(registry_version, {})


@dataclass(frozen=True)
class Obligation:
    """What has to be paid or maintained; never a payment instruction."""

    identity: RecordIdentity
    purpose: str
    classification: Classification
    provenance: Provenance
    review: ReviewState
    counterparty: Fact[RecordReference] = Fact(FactState.UNKNOWN)
    essentiality: str = "unknown"
    status: str = "active"
    subject: Fact[RecordReference] = Fact(FactState.UNKNOWN)
    lifecycle: RecordLifecycle = RecordLifecycle()

    def __post_init__(self) -> None:
        bankingIdentityValidate(self.identity, OBLIGATION_AGGREGATE)
        classificationResolve(self.classification)
        if not self.purpose.strip():
            raise DomainValidationError("An obligation requires a purpose.")
        if self.essentiality not in ESSENTIALITY_VALUES:
            raise DomainValidationError(
                f"Unsupported essentiality: {self.essentiality}."
            )
        if self.status not in OBLIGATION_STATUSES:
            raise DomainValidationError(
                f"Unsupported obligation status: {self.status}."
            )
        secretsValidate({"purpose": self.purpose})
        _obligationReferencesValidate(self)


@dataclass(frozen=True)
class PaymentArrangement:
    """How an obligation is normally paid; never the obligation itself."""

    identity: RecordIdentity
    mechanism: str
    purpose: str
    obligation: RecordReference
    funding_account: RecordReference
    classification: Classification
    provenance: Provenance
    review: ReviewState
    schedule: Schedule
    status: str = "active"
    typical_amount: Fact[Money] = Fact(FactState.UNKNOWN)
    payee: Fact[RecordReference] = Fact(FactState.UNKNOWN)
    customer_reference: Optional[Identifier] = None
    lifecycle: RecordLifecycle = RecordLifecycle()

    def __post_init__(self) -> None:
        bankingIdentityValidate(self.identity, ARRANGEMENT_AGGREGATE)
        classificationResolve(self.classification)
        if not self.purpose.strip():
            raise DomainValidationError("A payment arrangement requires a purpose.")
        if self.obligation.record_type in INSTRUCTION_TYPES:
            raise DomainValidationError(
                "A payment arrangement cannot treat an instruction as its obligation."
            )
        if self.funding_account.record_type != RELATIONSHIP_AGGREGATE:
            raise DomainValidationError(
                "A payment arrangement must be funded by a BankingRelationship."
            )
        if self.status not in ARRANGEMENT_STATUSES:
            raise DomainValidationError(
                f"Unsupported arrangement status: {self.status}."
            )
        secretsValidate({"purpose": self.purpose, "mechanism": self.mechanism})
        _arrangementReferencesValidate(self)

    def arrangementCancelled(self) -> "PaymentArrangement":
        """Mark the instruction cancelled without changing the obligation."""
        return replace(self, status="cancelled")


@dataclass(frozen=True)
class MoneyMovement:
    """Expected recurring inflow or outflow; not evidence that it occurred."""

    identity: RecordIdentity
    direction: MovementDirection
    purpose: str
    account: RecordReference
    classification: Classification
    provenance: Provenance
    review: ReviewState
    schedule: Schedule
    typical_amount: Fact[Money] = Fact(FactState.UNKNOWN)
    counterparty: Fact[RecordReference] = Fact(FactState.UNKNOWN)
    obligation: Fact[RecordReference] = Fact(FactState.UNKNOWN)
    arrangement: Fact[RecordReference] = Fact(FactState.UNKNOWN)
    lifecycle: RecordLifecycle = RecordLifecycle()

    def __post_init__(self) -> None:
        bankingIdentityValidate(self.identity, MOVEMENT_AGGREGATE)
        classificationResolve(self.classification)
        if not self.purpose.strip():
            raise DomainValidationError("A money movement requires a purpose.")
        if self.account.record_type != RELATIONSHIP_AGGREGATE:
            raise DomainValidationError(
                "A money movement must reference a BankingRelationship."
            )
        if (
            self.arrangement.state is FactState.KNOWN
            and self.arrangement.value is not None
            and self.arrangement.value.record_type != ARRANGEMENT_AGGREGATE
        ):
            raise DomainValidationError(
                "A movement arrangement link must reference a PaymentArrangement."
            )
        if (
            self.obligation.state is FactState.KNOWN
            and self.obligation.value is not None
            and self.obligation.value.record_type in INSTRUCTION_TYPES
        ):
            raise DomainValidationError(
                "A money movement cannot treat an instruction as its obligation."
            )
        secretsValidate({"purpose": self.purpose})
        _movementReferencesValidate(self)


@dataclass(frozen=True)
class TransactionObservation:
    """Evidence that a movement occurred; never the standing arrangement."""

    identity: RecordIdentity
    observation: Observation[Money]
    account: RecordReference
    classification: Classification
    provenance: Provenance
    purpose: str = "statementEvidence"
    movement: Fact[RecordReference] = Fact(FactState.UNKNOWN)
    arrangement: Fact[RecordReference] = Fact(FactState.UNKNOWN)
    obligation: Fact[RecordReference] = Fact(FactState.UNKNOWN)
    evidence: Tuple[EvidenceReference, ...] = ()
    lifecycle: RecordLifecycle = RecordLifecycle()

    def __post_init__(self) -> None:
        bankingIdentityValidate(self.identity, TRANSACTION_AGGREGATE)
        classificationResolve(self.classification)
        if not isinstance(self.observation.value, Money):
            raise DomainValidationError("A transaction observation requires Money.")
        if self.account.record_type != RELATIONSHIP_AGGREGATE:
            raise DomainValidationError(
                "A transaction observation must reference a BankingRelationship."
            )
        if not self.purpose.strip():
            raise DomainValidationError("A transaction observation requires a purpose.")
        if (
            self.arrangement.state is FactState.KNOWN
            and self.arrangement.value is not None
            and self.arrangement.value.record_type != ARRANGEMENT_AGGREGATE
        ):
            raise DomainValidationError(
                "Transaction evidence cannot be recorded as a payment arrangement."
            )
        if (
            self.movement.state is FactState.KNOWN
            and self.movement.value is not None
            and self.movement.value.record_type != MOVEMENT_AGGREGATE
        ):
            raise DomainValidationError(
                "Transaction evidence must link a MoneyMovement if a movement is given."
            )
        _transactionReferencesValidate(self)


def _arrangementReferencesValidate(arrangement: PaymentArrangement) -> None:
    references = [arrangement.obligation, arrangement.funding_account]
    if arrangement.payee.state is FactState.KNOWN:
        references.append(arrangement.payee.value)
    if arrangement.review.responsible_role.state is FactState.KNOWN:
        references.append(arrangement.review.responsible_role.value)
    clannBoundaryValidate(
        arrangement.identity.clann_id,
        references=references,
        provenances=(arrangement.provenance,),
    )


def _movementReferencesValidate(movement: MoneyMovement) -> None:
    references = [movement.account]
    for fact in (movement.counterparty, movement.obligation, movement.arrangement):
        if fact.state is FactState.KNOWN:
            references.append(fact.value)
    if movement.review.responsible_role.state is FactState.KNOWN:
        references.append(movement.review.responsible_role.value)
    clannBoundaryValidate(
        movement.identity.clann_id,
        references=references,
        provenances=(movement.provenance,),
    )


def _obligationReferencesValidate(obligation: Obligation) -> None:
    references = []
    if obligation.counterparty.state is FactState.KNOWN:
        references.append(obligation.counterparty.value)
    if obligation.subject.state is FactState.KNOWN:
        references.append(obligation.subject.value)
    if obligation.review.responsible_role.state is FactState.KNOWN:
        references.append(obligation.review.responsible_role.value)
    clannBoundaryValidate(
        obligation.identity.clann_id,
        references=references,
        provenances=(obligation.provenance,),
    )


def _transactionReferencesValidate(transaction: TransactionObservation) -> None:
    references = [transaction.account]
    for fact in (transaction.movement, transaction.arrangement, transaction.obligation):
        if fact.state is FactState.KNOWN:
            references.append(fact.value)
    clannBoundaryValidate(
        transaction.identity.clann_id,
        references=references,
        evidence=transaction.evidence,
        provenances=(transaction.observation.provenance, transaction.provenance),
    )
