"""Encode and decode payment-related Banking aggregates."""

from typing import Any, Mapping

from eolas.banking.codec import BANKING_SCHEMA_VERSION
from eolas.banking.payments import (
    ARRANGEMENT_AGGREGATE,
    MOVEMENT_AGGREGATE,
    OBLIGATION_AGGREGATE,
    TRANSACTION_AGGREGATE,
    MoneyMovement,
    MovementDirection,
    Obligation,
    PaymentArrangement,
    TransactionObservation,
)
from eolas.domain.codec import (
    evidenceDecode,
    evidenceEncode,
    factDecode,
    factEncode,
    identifierDecode,
    identifierEncode,
    lifecycleDecode,
    lifecycleEncode,
    moneyDecode,
    moneyEncode,
    observationDecode,
    observationEncode,
    provenanceDecode,
    provenanceEncode,
    referenceDecode,
    referenceEncode,
    reviewDecode,
    reviewEncode,
    scheduleDecode,
    scheduleEncode,
    schemaValidate,
)
from eolas.domain.storage import StoredRecord
from eolas.domain.values import Classification, FactState


def _classificationDecode(value: Any) -> Classification:
    return Classification(str(value))


def _unknownFact() -> dict[str, str]:
    return {"state": FactState.UNKNOWN.value}


## arrangement


def arrangementDecode(record: StoredRecord) -> PaymentArrangement:
    """Reconstitute a PaymentArrangement from a stored envelope."""
    schemaValidate(record, ARRANGEMENT_AGGREGATE, ARRANGEMENT_AGGREGATE)
    payload = record.payload
    referenceRaw = payload.get("customerReference")
    return PaymentArrangement(
        record.identity,
        str(payload["mechanism"]),
        str(payload["purpose"]),
        referenceDecode(payload["obligation"]),
        referenceDecode(payload["fundingAccount"]),
        _classificationDecode(payload["classification"]),
        provenanceDecode(payload["provenance"]),
        reviewDecode(payload["review"]),
        scheduleDecode(payload["schedule"]),
        str(payload.get("status", "active")),
        factDecode(payload.get("typicalAmount", _unknownFact()), moneyDecode),
        factDecode(payload.get("payee", _unknownFact()), referenceDecode),
        None if referenceRaw is None else identifierDecode(referenceRaw),
        lifecycleDecode(payload.get("lifecycle", {})),
    )


def arrangementEncode(arrangement: PaymentArrangement) -> StoredRecord:
    """Encode a PaymentArrangement payload."""
    return StoredRecord(
        arrangement.identity,
        ARRANGEMENT_AGGREGATE,
        BANKING_SCHEMA_VERSION,
        0,
        {
            "mechanism": arrangement.mechanism,
            "purpose": arrangement.purpose,
            "obligation": referenceEncode(arrangement.obligation),
            "fundingAccount": referenceEncode(arrangement.funding_account),
            "classification": arrangement.classification.value,
            "provenance": provenanceEncode(arrangement.provenance),
            "review": reviewEncode(arrangement.review),
            "schedule": scheduleEncode(arrangement.schedule),
            "status": arrangement.status,
            "typicalAmount": factEncode(arrangement.typical_amount, moneyEncode),
            "payee": factEncode(arrangement.payee, referenceEncode),
            "customerReference": (
                None
                if arrangement.customer_reference is None
                else identifierEncode(arrangement.customer_reference)
            ),
            "lifecycle": lifecycleEncode(arrangement.lifecycle),
        },
    )


## movement


def movementDecode(record: StoredRecord) -> MoneyMovement:
    """Reconstitute a MoneyMovement from a stored envelope."""
    schemaValidate(record, MOVEMENT_AGGREGATE, MOVEMENT_AGGREGATE)
    payload = record.payload
    return MoneyMovement(
        record.identity,
        MovementDirection(str(payload["direction"])),
        str(payload["purpose"]),
        referenceDecode(payload["account"]),
        _classificationDecode(payload["classification"]),
        provenanceDecode(payload["provenance"]),
        reviewDecode(payload["review"]),
        scheduleDecode(payload["schedule"]),
        factDecode(payload.get("typicalAmount", _unknownFact()), moneyDecode),
        factDecode(payload.get("counterparty", _unknownFact()), referenceDecode),
        factDecode(payload.get("obligation", _unknownFact()), referenceDecode),
        factDecode(payload.get("arrangement", _unknownFact()), referenceDecode),
        lifecycleDecode(payload.get("lifecycle", {})),
    )


def movementEncode(movement: MoneyMovement) -> StoredRecord:
    """Encode a MoneyMovement payload."""
    return StoredRecord(
        movement.identity,
        MOVEMENT_AGGREGATE,
        BANKING_SCHEMA_VERSION,
        0,
        {
            "direction": movement.direction.value,
            "purpose": movement.purpose,
            "account": referenceEncode(movement.account),
            "classification": movement.classification.value,
            "provenance": provenanceEncode(movement.provenance),
            "review": reviewEncode(movement.review),
            "schedule": scheduleEncode(movement.schedule),
            "typicalAmount": factEncode(movement.typical_amount, moneyEncode),
            "counterparty": factEncode(movement.counterparty, referenceEncode),
            "obligation": factEncode(movement.obligation, referenceEncode),
            "arrangement": factEncode(movement.arrangement, referenceEncode),
            "lifecycle": lifecycleEncode(movement.lifecycle),
        },
    )


## obligation


def obligationDecode(record: StoredRecord) -> Obligation:
    """Reconstitute an Obligation from a stored envelope."""
    schemaValidate(record, OBLIGATION_AGGREGATE, OBLIGATION_AGGREGATE)
    payload = record.payload
    return Obligation(
        record.identity,
        str(payload["purpose"]),
        _classificationDecode(payload["classification"]),
        provenanceDecode(payload["provenance"]),
        reviewDecode(payload["review"]),
        factDecode(payload.get("counterparty", _unknownFact()), referenceDecode),
        str(payload.get("essentiality", "unknown")),
        str(payload.get("status", "active")),
        factDecode(payload.get("subject", _unknownFact()), referenceDecode),
        lifecycleDecode(payload.get("lifecycle", {})),
    )


def obligationEncode(obligation: Obligation) -> StoredRecord:
    """Encode an Obligation payload."""
    return StoredRecord(
        obligation.identity,
        OBLIGATION_AGGREGATE,
        BANKING_SCHEMA_VERSION,
        0,
        {
            "purpose": obligation.purpose,
            "classification": obligation.classification.value,
            "provenance": provenanceEncode(obligation.provenance),
            "review": reviewEncode(obligation.review),
            "counterparty": factEncode(obligation.counterparty, referenceEncode),
            "essentiality": obligation.essentiality,
            "status": obligation.status,
            "subject": factEncode(obligation.subject, referenceEncode),
            "lifecycle": lifecycleEncode(obligation.lifecycle),
        },
    )


## transaction


def transactionDecode(record: StoredRecord) -> TransactionObservation:
    """Reconstitute a TransactionObservation from a stored envelope."""
    schemaValidate(record, TRANSACTION_AGGREGATE, TRANSACTION_AGGREGATE)
    payload = record.payload
    return TransactionObservation(
        record.identity,
        observationDecode(payload["observation"], moneyDecode),
        referenceDecode(payload["account"]),
        _classificationDecode(payload["classification"]),
        provenanceDecode(payload["provenance"]),
        str(payload.get("purpose", "statementEvidence")),
        factDecode(payload.get("movement", _unknownFact()), referenceDecode),
        factDecode(payload.get("arrangement", _unknownFact()), referenceDecode),
        factDecode(payload.get("obligation", _unknownFact()), referenceDecode),
        tuple(evidenceDecode(item) for item in payload.get("evidence", ())),
        lifecycleDecode(payload.get("lifecycle", {})),
    )


def transactionEncode(transaction: TransactionObservation) -> StoredRecord:
    """Encode a TransactionObservation payload."""
    return StoredRecord(
        transaction.identity,
        TRANSACTION_AGGREGATE,
        BANKING_SCHEMA_VERSION,
        0,
        {
            "observation": observationEncode(transaction.observation, moneyEncode),
            "account": referenceEncode(transaction.account),
            "classification": transaction.classification.value,
            "provenance": provenanceEncode(transaction.provenance),
            "purpose": transaction.purpose,
            "movement": factEncode(transaction.movement, referenceEncode),
            "arrangement": factEncode(transaction.arrangement, referenceEncode),
            "obligation": factEncode(transaction.obligation, referenceEncode),
            "evidence": [evidenceEncode(item) for item in transaction.evidence],
            "lifecycle": lifecycleEncode(transaction.lifecycle),
        },
    )
