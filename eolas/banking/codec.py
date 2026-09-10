"""Encode and decode Banking aggregates for the shared RecordStore port."""

from typing import Any, Mapping

from eolas.banking.models import (
    INSTITUTION_AGGREGATE,
    RELATIONSHIP_AGGREGATE,
    AccountContinuityRole,
    AccountParty,
    AuthorityLink,
    AuthorityReadiness,
    BalanceObservation,
    BankingRelationship,
    BankingStatus,
    FinancialInstitution,
)
from eolas.domain.codec import (
    evidenceDecode,
    evidenceEncode,
    factDecode,
    factEncode,
    identifierDecode,
    identifierEncode,
    jurisdictionDecode,
    jurisdictionEncode,
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
    optionalDateDecode,
    optionalDateEncode,
    schemaValidate,
)
from eolas.domain.storage import StoredRecord
from eolas.domain.values import Classification, FactState

BANKING_SCHEMA_VERSION = 1


## institution


def institutionDecode(record: StoredRecord) -> FinancialInstitution:
    """Reconstitute a FinancialInstitution from a stored envelope."""
    schemaValidate(record, INSTITUTION_AGGREGATE, INSTITUTION_AGGREGATE)
    payload = record.payload
    return FinancialInstitution(
        record.identity,
        referenceDecode(payload["organisation"]),
        str(payload["displayName"]),
        str(payload["institutionType"]),
        _classificationDecode(payload["classification"]),
        provenanceDecode(payload["provenance"]),
        reviewDecode(payload["review"]),
        factDecode(payload.get("jurisdiction", _unknownFact()), jurisdictionDecode),
        factDecode(payload.get("protectionGroup", _unknownFact())),
        tuple(identifierDecode(item) for item in payload.get("identifiers", ())),
        lifecycleDecode(payload.get("lifecycle", {})),
    )


def institutionEncode(institution: FinancialInstitution) -> StoredRecord:
    """Encode a FinancialInstitution payload."""
    return StoredRecord(
        institution.identity,
        INSTITUTION_AGGREGATE,
        BANKING_SCHEMA_VERSION,
        0,
        {
            "organisation": referenceEncode(institution.organisation),
            "displayName": institution.display_name,
            "institutionType": institution.institution_type,
            "classification": institution.classification.value,
            "provenance": provenanceEncode(institution.provenance),
            "review": reviewEncode(institution.review),
            "jurisdiction": factEncode(institution.jurisdiction, jurisdictionEncode),
            "protectionGroup": factEncode(institution.protection_group),
            "identifiers": [identifierEncode(item) for item in institution.identifiers],
            "lifecycle": lifecycleEncode(institution.lifecycle),
        },
    )


## relationship


def relationshipDecode(record: StoredRecord) -> BankingRelationship:
    """Reconstitute a BankingRelationship from a stored envelope."""
    schemaValidate(record, RELATIONSHIP_AGGREGATE, RELATIONSHIP_AGGREGATE)
    payload = record.payload
    return BankingRelationship(
        record.identity,
        referenceDecode(payload["institution"]),
        str(payload["label"]),
        str(payload["accountCategory"]),
        str(payload["purpose"]),
        str(payload["ownershipType"]),
        BankingStatus(str(payload["status"])),
        _classificationDecode(payload["classification"]),
        provenanceDecode(payload["provenance"]),
        reviewDecode(payload["review"]),
        factDecode(payload.get("productName", _unknownFact())),
        factDecode(payload.get("currency", _unknownFact())),
        factDecode(payload.get("servicingChannel", _unknownFact())),
        factDecode(payload.get("signingRule", _unknownFact())),
        factDecode(payload.get("household", _unknownFact()), referenceDecode),
        tuple(_partyDecode(item) for item in payload.get("parties", ())),
        tuple(_roleDecode(item) for item in payload.get("continuityRoles", ())),
        tuple(identifierDecode(item) for item in payload.get("identifiers", ())),
        tuple(_authorityLinkDecode(item) for item in payload.get("authorityLinks", ())),
        tuple(_balanceDecode(item) for item in payload.get("balances", ())),
        lifecycleDecode(payload.get("lifecycle", {})),
    )


def relationshipEncode(relationship: BankingRelationship) -> StoredRecord:
    """Encode a BankingRelationship payload."""
    return StoredRecord(
        relationship.identity,
        RELATIONSHIP_AGGREGATE,
        BANKING_SCHEMA_VERSION,
        0,
        {
            "institution": referenceEncode(relationship.institution),
            "label": relationship.label,
            "accountCategory": relationship.account_category,
            "purpose": relationship.purpose,
            "ownershipType": relationship.ownership_type,
            "status": relationship.status.value,
            "classification": relationship.classification.value,
            "provenance": provenanceEncode(relationship.provenance),
            "review": reviewEncode(relationship.review),
            "productName": factEncode(relationship.product_name),
            "currency": factEncode(relationship.currency),
            "servicingChannel": factEncode(relationship.servicing_channel),
            "signingRule": factEncode(relationship.signing_rule),
            "household": factEncode(relationship.household, referenceEncode),
            "parties": [_partyEncode(item) for item in relationship.parties],
            "continuityRoles": [
                _roleEncode(item) for item in relationship.continuity_roles
            ],
            "identifiers": [
                identifierEncode(item) for item in relationship.identifiers
            ],
            "authorityLinks": [
                _authorityLinkEncode(item) for item in relationship.authority_links
            ],
            "balances": [_balanceEncode(item) for item in relationship.balances],
            "lifecycle": lifecycleEncode(relationship.lifecycle),
        },
    )


## nested


def _authorityLinkDecode(raw: Mapping[str, Any]) -> AuthorityLink:
    return AuthorityLink(
        referenceDecode(raw["authority"]),
        AuthorityReadiness(str(raw["readiness"])),
        provenanceDecode(raw["provenance"]),
        factDecode(raw.get("registration", _unknownFact()), referenceDecode),
    )


def _authorityLinkEncode(link: AuthorityLink) -> dict[str, Any]:
    return {
        "authority": referenceEncode(link.authority),
        "readiness": link.readiness.value,
        "provenance": provenanceEncode(link.provenance),
        "registration": factEncode(link.registration, referenceEncode),
    }


def _balanceDecode(raw: Mapping[str, Any]) -> BalanceObservation:
    return BalanceObservation(
        observationDecode(raw["observation"], moneyDecode),
        str(raw.get("purpose", "continuitySnapshot")),
    )


def _balanceEncode(balance: BalanceObservation) -> dict[str, Any]:
    return {
        "observation": observationEncode(balance.observation, moneyEncode),
        "purpose": balance.purpose,
    }


def _classificationDecode(value: Any) -> Classification:
    return Classification(str(value))


def _partyDecode(raw: Mapping[str, Any]) -> AccountParty:
    return AccountParty(
        referenceDecode(raw["party"]),
        str(raw["partyRole"]),
        str(raw["interestType"]),
        provenanceDecode(raw["provenance"]),
        factDecode(raw.get("proportion", _unknownFact())),
        factDecode(raw.get("signingRule", {"state": FactState.NOT_APPLICABLE.value})),
        optionalDateDecode(raw.get("effectiveFrom")),
        optionalDateDecode(raw.get("effectiveTo")),
        tuple(evidenceDecode(item) for item in raw.get("evidence", ())),
    )


def _partyEncode(party: AccountParty) -> dict[str, Any]:
    return {
        "party": referenceEncode(party.party),
        "partyRole": party.party_role,
        "interestType": party.interest_type,
        "provenance": provenanceEncode(party.provenance),
        "proportion": factEncode(party.proportion),
        "signingRule": factEncode(party.signing_rule),
        "effectiveFrom": optionalDateEncode(party.effective_from),
        "effectiveTo": optionalDateEncode(party.effective_to),
        "evidence": [evidenceEncode(item) for item in party.evidence],
    }


def _roleDecode(raw: Mapping[str, Any]) -> AccountContinuityRole:
    return AccountContinuityRole(
        str(raw["roleId"]),
        provenanceDecode(raw["provenance"]),
        factDecode(raw.get("household", _unknownFact()), referenceDecode),
        str(raw.get("registryVersion", "1")),
        optionalDateDecode(raw.get("effectiveFrom")),
        optionalDateDecode(raw.get("effectiveTo")),
        raw.get("exceptionReason"),
    )


def _roleEncode(role: AccountContinuityRole) -> dict[str, Any]:
    return {
        "roleId": role.role_id,
        "provenance": provenanceEncode(role.provenance),
        "household": factEncode(role.household, referenceEncode),
        "registryVersion": role.registry_version,
        "effectiveFrom": optionalDateEncode(role.effective_from),
        "effectiveTo": optionalDateEncode(role.effective_to),
        "exceptionReason": role.exception_reason,
    }


def _unknownFact() -> dict[str, str]:
    return {"state": FactState.UNKNOWN.value}
