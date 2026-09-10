"""Persistence-neutral encoding for shared domain values and party aggregates."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Callable, Mapping, Optional

from eolas.domain.entities import Contact, Organisation, OrganisationBrand, Person
from eolas.domain.storage import StoredRecord
from eolas.domain.values import (
    Classification,
    DomainValidationError,
    EvidenceReference,
    Fact,
    FactState,
    Identifier,
    Jurisdiction,
    LifecycleState,
    Money,
    Observation,
    ObservationStatus,
    Provenance,
    RecordIdentity,
    RecordLifecycle,
    RecordReference,
    ReviewState,
    VerificationState,
)

ORGANISATION_SCHEMA = "organisation"
CONTACT_SCHEMA = "contact"
PERSON_SCHEMA = "person"
SHARED_SCHEMA_VERSION = 1
TValueDecode = Callable[[Any], Any]
TValueEncode = Callable[[Any], Any]


## contact


def contactDecode(record: StoredRecord) -> Contact:
    """Reconstitute a Contact aggregate from a stored envelope."""
    schemaValidate(record, CONTACT_SCHEMA, "contact")
    payload = record.payload
    represented = payload.get("representedParty")
    return Contact(
        record.identity,
        str(payload["displayName"]),
        Classification(str(payload["classification"])),
        None if represented is None else referenceDecode(represented),
    )


def contactEncode(contact: Contact) -> StoredRecord:
    """Encode a Contact without depending on a storage technology."""
    represented = contact.represented_party
    return StoredRecord(
        contact.identity,
        CONTACT_SCHEMA,
        SHARED_SCHEMA_VERSION,
        0,
        {
            "displayName": contact.display_name,
            "classification": contact.classification.value,
            "representedParty": (
                None if represented is None else referenceEncode(represented)
            ),
        },
    )


## person


def personDecode(record: StoredRecord) -> Person:
    """Reconstitute a Person aggregate from a stored envelope."""
    schemaValidate(record, PERSON_SCHEMA, "person")
    payload = record.payload
    return Person(
        record.identity,
        str(payload["displayName"]),
        Classification(str(payload["classification"])),
        lifecycleDecode(payload.get("lifecycle", {})),
    )


def personEncode(person: Person) -> StoredRecord:
    """Encode a Person without depending on a storage technology."""
    return StoredRecord(
        person.identity,
        PERSON_SCHEMA,
        SHARED_SCHEMA_VERSION,
        0,
        {
            "displayName": person.display_name,
            "classification": person.classification.value,
            "lifecycle": lifecycleEncode(person.lifecycle),
        },
    )


## evidence


def evidenceDecode(raw: Mapping[str, Any]) -> EvidenceReference:
    """Decode a checksum-backed evidence reference."""
    return EvidenceReference(
        str(raw["evidenceId"]),
        str(raw["clannId"]),
        str(raw["purpose"]),
        str(raw["checksumSha256"]),
        str(raw["locator"]),
        Classification(str(raw["classification"])),
        provenanceDecode(raw["provenance"]),
    )


def evidenceEncode(evidence: EvidenceReference) -> dict[str, Any]:
    """Encode an evidence reference as a mapping."""
    return {
        "evidenceId": evidence.evidence_id,
        "clannId": evidence.clann_id,
        "purpose": evidence.purpose,
        "checksumSha256": evidence.checksum_sha256,
        "locator": evidence.locator,
        "classification": evidence.classification.value,
        "provenance": provenanceEncode(evidence.provenance),
    }


## fact


def factDecode(
    raw: Mapping[str, Any], value_decode: TValueDecode = lambda value: value
) -> Fact[Any]:
    """Decode a Fact without coercing unknown, inapplicable or absent states."""
    state = FactState(str(raw["state"]))
    if state is FactState.KNOWN:
        return Fact.factKnown(value_decode(raw["value"]))
    return Fact(state)


def factEncode(
    fact: Fact[Any], value_encode: TValueEncode = lambda value: value
) -> dict[str, Any]:
    """Encode a Fact, omitting a value unless the fact is known."""
    encoded: dict[str, Any] = {"state": fact.state.value}
    if fact.state is FactState.KNOWN:
        encoded["value"] = value_encode(fact.value)
    return encoded


## identifier


def identifierDecode(raw: Mapping[str, Any]) -> Identifier:
    """Decode a typed external identifier."""
    provenanceRaw = raw.get("provenance")
    return Identifier(
        str(raw["identifierType"]),
        str(raw["maskedValue"]),
        Classification(str(raw["classification"])),
        raw.get("protectedValue"),
        None if provenanceRaw is None else provenanceDecode(provenanceRaw),
        VerificationState(
            str(raw.get("verification", VerificationState.UNVERIFIED.value))
        ),
    )


def identifierEncode(identifier: Identifier) -> dict[str, Any]:
    """Encode an identifier, keeping the protected value out of repr callers."""
    encoded = {
        "identifierType": identifier.identifier_type,
        "maskedValue": identifier.masked_value,
        "classification": identifier.classification.value,
        "protectedValue": identifier.protected_value,
        "verification": identifier.verification.value,
    }
    if identifier.provenance is not None:
        encoded["provenance"] = provenanceEncode(identifier.provenance)
    return encoded


## identity


def identityDecode(raw: Mapping[str, Any]) -> RecordIdentity:
    """Decode a stored identity mapping."""
    return RecordIdentity(
        str(raw["recordId"]),
        str(raw["clannId"]),
        str(raw["aggregateType"]),
        str(raw["ownerModule"]),
    )


def identityEncode(identity: RecordIdentity) -> dict[str, str]:
    """Encode identity using the shared persistence envelope names."""
    return {
        "recordId": identity.record_id,
        "clannId": identity.clann_id,
        "aggregateType": identity.aggregate_type,
        "ownerModule": identity.owner_module,
    }


## jurisdiction


def jurisdictionDecode(raw: Mapping[str, Any]) -> Jurisdiction:
    """Decode a versioned jurisdiction reference."""
    return Jurisdiction(str(raw["code"]), str(raw["scheme"]), str(raw["version"]))


def jurisdictionEncode(jurisdiction: Jurisdiction) -> dict[str, str]:
    """Encode a jurisdiction reference."""
    return {
        "code": jurisdiction.code,
        "scheme": jurisdiction.scheme,
        "version": jurisdiction.version,
    }


## lifecycle


def lifecycleDecode(raw: Mapping[str, Any]) -> RecordLifecycle:
    """Decode record lifecycle metadata."""
    return RecordLifecycle(
        LifecycleState(str(raw.get("state", LifecycleState.ACTIVE.value))),
        optionalDateDecode(raw.get("effectiveFrom")),
        optionalDateDecode(raw.get("effectiveTo")),
        raw.get("reason"),
    )


def lifecycleEncode(lifecycle: RecordLifecycle) -> dict[str, Any]:
    """Encode record lifecycle metadata."""
    return {
        "state": lifecycle.state.value,
        "effectiveFrom": optionalDateEncode(lifecycle.effective_from),
        "effectiveTo": optionalDateEncode(lifecycle.effective_to),
        "reason": lifecycle.reason,
    }


## money


def moneyDecode(raw: Mapping[str, Any]) -> Money:
    """Decode decimal money from a non-float representation."""
    return Money(Decimal(str(raw["amount"])), str(raw["currency"]))


def moneyEncode(money: Money) -> dict[str, str]:
    """Encode money as a decimal string plus currency."""
    return {"amount": str(money.amount), "currency": money.currency}


## observation


def observationDecode(
    raw: Mapping[str, Any], value_decode: TValueDecode
) -> Observation[Any]:
    """Decode a dated observation."""
    confidenceRaw = raw.get("confidence")
    return Observation(
        value_decode(raw["value"]),
        _datetimeDecode(raw["asOf"]),
        provenanceDecode(raw["provenance"]),
        ObservationStatus(str(raw.get("status", ObservationStatus.OBSERVED.value))),
        None if confidenceRaw is None else Decimal(str(confidenceRaw)),
    )


def observationEncode(
    observation: Observation[Any], value_encode: TValueEncode
) -> dict[str, Any]:
    """Encode a dated observation using an `asOf` timestamp."""
    encoded = {
        "value": value_encode(observation.value),
        "asOf": observation.as_of.isoformat(),
        "provenance": provenanceEncode(observation.provenance),
        "status": observation.status.value,
    }
    if observation.confidence is not None:
        encoded["confidence"] = str(observation.confidence)
    return encoded


## organisation


def organisationDecode(record: StoredRecord) -> Organisation:
    """Reconstitute an Organisation aggregate from a stored envelope."""
    schemaValidate(record, ORGANISATION_SCHEMA, "organisation")
    payload = record.payload
    brands = tuple(
        OrganisationBrand(
            str(item["name"]),
            optionalDateDecode(item.get("effectiveFrom")),
            optionalDateDecode(item.get("effectiveTo")),
        )
        for item in payload.get("brands", ())
    )
    return Organisation(
        record.identity,
        str(payload["legalName"]),
        Classification(str(payload["classification"])),
        brands,
        (),
        lifecycleDecode(payload.get("lifecycle", {})),
    )


def organisationEncode(organisation: Organisation) -> StoredRecord:
    """Encode an Organisation without depending on a storage technology."""
    return StoredRecord(
        organisation.identity,
        ORGANISATION_SCHEMA,
        SHARED_SCHEMA_VERSION,
        0,
        {
            "legalName": organisation.legal_name,
            "classification": organisation.classification.value,
            "brands": [
                {
                    "name": brand.name,
                    "effectiveFrom": optionalDateEncode(brand.effective_from),
                    "effectiveTo": optionalDateEncode(brand.effective_to),
                }
                for brand in organisation.brands
            ],
            "lifecycle": lifecycleEncode(organisation.lifecycle),
        },
    )


## provenance


def provenanceDecode(raw: Mapping[str, Any]) -> Provenance:
    """Decode provenance including an optional actor reference."""
    actorRaw = raw.get("actorReference")
    return Provenance(
        str(raw["sourceType"]),
        str(raw["sourceReference"]),
        _datetimeDecode(raw["recordedAt"]),
        None if actorRaw is None else referenceDecode(actorRaw),
        raw.get("derivation"),
    )


def provenanceEncode(provenance: Provenance) -> dict[str, Any]:
    """Encode provenance using timezone-aware timestamps."""
    encoded = {
        "sourceType": provenance.source_type,
        "sourceReference": provenance.source_reference,
        "recordedAt": provenance.recorded_at.isoformat(),
        "derivation": provenance.derivation,
    }
    if provenance.actor_reference is not None:
        encoded["actorReference"] = referenceEncode(provenance.actor_reference)
    return encoded


## reference


def referenceDecode(raw: Mapping[str, Any]) -> RecordReference:
    """Decode a typed cross-aggregate reference."""
    return RecordReference(
        str(raw["recordId"]), str(raw["clannId"]), str(raw["recordType"])
    )


def referenceEncode(reference: RecordReference) -> dict[str, str]:
    """Encode a typed cross-aggregate reference."""
    return {
        "recordId": reference.record_id,
        "clannId": reference.clann_id,
        "recordType": reference.record_type,
    }


## review


def reviewDecode(raw: Mapping[str, Any]) -> ReviewState:
    """Decode reusable review state."""
    return ReviewState(
        factDecode(raw["lastReviewed"], _dateDecode),
        factDecode(raw["nextReview"], _dateDecode),
        factDecode(raw["responsibleRole"], referenceDecode),
        tuple(str(item) for item in raw.get("findings", ())),
    )


def reviewEncode(review: ReviewState) -> dict[str, Any]:
    """Encode reusable review state."""
    return {
        "lastReviewed": factEncode(review.last_reviewed, _dateEncode),
        "nextReview": factEncode(review.next_review, _dateEncode),
        "responsibleRole": factEncode(review.responsible_role, referenceEncode),
        "findings": list(review.findings),
    }


## utilities


def _dateDecode(value: Any) -> date:
    return date.fromisoformat(str(value))


def _dateEncode(value: date) -> str:
    return value.isoformat()


def _datetimeDecode(value: Any) -> datetime:
    parsed = datetime.fromisoformat(str(value))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise DomainValidationError("Encoded timestamps must include a timezone.")
    return parsed


def optionalDateDecode(value: Any) -> Optional[date]:
    return None if value in (None, "") else _dateDecode(value)


def optionalDateEncode(value: Optional[date]) -> Optional[str]:
    return None if value is None else value.isoformat()


def schemaValidate(record: StoredRecord, schema_name: str, aggregate_type: str) -> None:
    if record.schema_name != schema_name:
        raise DomainValidationError(
            f"Expected schema {schema_name}; found {record.schema_name}."
        )
    if record.identity.aggregate_type != aggregate_type:
        raise DomainValidationError(
            f"Expected aggregate {aggregate_type}; found {record.identity.aggregate_type}."
        )
