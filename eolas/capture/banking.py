"""Translate capture input into typed Banking commands and persist them."""

from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from eolas.banking.codec import institutionEncode, relationshipEncode
from eolas.banking.identifiers import identifierBankingCreate
from eolas.banking.models import (
    BANKING_MODULE,
    INSTITUTION_AGGREGATE,
    RELATIONSHIP_AGGREGATE,
    AccountContinuityRole,
    AccountParty,
    BalanceObservation,
    BankingRelationship,
    BankingStatus,
    FinancialInstitution,
)
from eolas.banking.service import (
    BankingService,
    InstitutionCreateCommand,
    RelationshipCreateCommand,
    institutionBuild,
    relationshipBuild,
)
from eolas.capture.adapter import captureCommandBuild
from eolas.capture.models import CaptureInput
from eolas.clann.records import clannRecordStoreOpen, clannRecordStorePath
from eolas.domain.codec import (
    contactEncode,
    identityEncode,
    organisationEncode,
)
from eolas.domain.directory import (
    organisationLoad,
    organisationsLoad,
    partyLoadById,
    peopleNamed,
)
from eolas.domain.entities import Contact, Organisation
from eolas.domain.security import classificationResolve
from eolas.domain.storage import (
    RecordStore,
    StoredRecord,
    WriteOperation,
    YamlRecordStore,
)
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
)

STATUS_ALIASES = {
    "inactive": BankingStatus.DORMANT,
    "active": BankingStatus.ACTIVE,
    "dormant": BankingStatus.DORMANT,
    "restricted": BankingStatus.RESTRICTED,
    "closurePending": BankingStatus.CLOSURE_PENDING,
    "closed": BankingStatus.CLOSED,
    "unknown": BankingStatus.UNKNOWN,
}


def bankingCapturePrepare(
    capture: CaptureInput,
    clannPath: Path,
    clann_id: str,
    captured_at: datetime,
) -> tuple[Path, Dict[str, Any]]:
    """Validate capture input and return the store path plus a typed preview."""
    store = clannRecordStoreOpen(clannPath, clann_id)
    built = bankingRecordsBuild(capture, clann_id, captured_at, store)
    targetPath = clannRecordStorePath(clannPath)
    return targetPath, bankingDocumentBuild(built, capture, targetPath)


def bankingCaptureWrite(targetPath: Path, document: Mapping[str, Any]) -> Path:
    """Commit a prepared Banking change set through the shared store port."""
    clann_id = str(document["clannRef"])
    store = YamlRecordStore(targetPath, clann_id)
    service = BankingService(store)
    operations = []
    pendingInstitutions: List[RecordIdentity] = []
    relationship: Optional[BankingRelationship] = None
    for raw in document["operations"]:
        identity = RecordIdentity(
            raw["identity"]["recordId"],
            raw["identity"]["clannId"],
            raw["identity"]["aggregateType"],
            raw["identity"]["ownerModule"],
        )
        record = StoredRecord(
            identity,
            str(raw["schemaName"]),
            int(raw["schemaVersion"]),
            0,
            dict(raw["payload"]),
        )
        operations.append(WriteOperation(record, None))
        if identity.aggregate_type == INSTITUTION_AGGREGATE:
            pendingInstitutions.append(identity)
        if identity.aggregate_type == RELATIONSHIP_AGGREGATE:
            relationship = relationshipBuild(_relationshipCommandFromRecord(record))
    if relationship is None:
        raise DomainValidationError("Banking capture is missing a relationship.")
    service.relationshipValidate(
        relationship, pending_institutions=tuple(pendingInstitutions)
    )
    store.recordsCommit(operations)
    return targetPath


def bankingRecordsBuild(
    capture: CaptureInput,
    clann_id: str,
    captured_at: datetime,
    store: RecordStore,
) -> Dict[str, Any]:
    """Turn capture fields into typed Banking records, reusing store identities."""
    command = captureCommandBuild(capture, clann_id, captured_at)
    fields = capture.fields
    classification = classificationResolve(command.classification)
    provenance = command.provenance
    review = _reviewBuild(fields, provenance)
    findings: List[str] = list(review.findings)
    service = BankingService(store)

    organisation, institution, newOrganisation, newInstitution = _providerResolve(
        store,
        service,
        clann_id,
        fields,
        command.label,
        classification,
        provenance,
        review,
        findings,
    )
    parties, contacts = _partiesBuild(
        store, clann_id, fields, classification, provenance, findings
    )
    ownership_type = _ownershipType(fields, parties)
    relationship = relationshipBuild(
        RelationshipCreateCommand(
            clann_id,
            institution.identity.referenceCreate(),
            command.label,
            _knownText(fields.get("accountCategory"), "unknown"),
            _knownText(fields.get("purpose"), "unknown"),
            ownership_type,
            _statusParse(fields.get("status")),
            classification,
            provenance,
            ReviewState(
                review.last_reviewed,
                review.next_review,
                review.responsible_role,
                tuple(findings),
            ),
            _factFromCapture(fields.get("productName")),
            _factFromCapture(fields.get("currency")),
            _factFromCapture(fields.get("servicingChannel")),
            _factFromCapture(fields.get("signingRule")),
            Fact(FactState.UNKNOWN),
            tuple(parties),
            _rolesBuild(fields, provenance),
            _identifiersBuild(fields, classification, provenance),
            (),
            _balancesBuild(fields, provenance),
        )
    )
    return {
        "organisation": organisation,
        "contacts": tuple(contacts),
        "institution": institution,
        "relationship": relationship,
        "newOrganisation": newOrganisation,
        "newInstitution": newInstitution,
        "classification": classification,
        "label": command.label,
        "clann_id": clann_id,
    }


def bankingDocumentBuild(
    built: Mapping[str, Any], capture: CaptureInput, targetPath: Path
) -> Dict[str, Any]:
    """Project typed Banking records into an adapter preview envelope."""
    organisation: Organisation = built["organisation"]
    institution: FinancialInstitution = built["institution"]
    relationship: BankingRelationship = built["relationship"]
    operations = []
    if built.get("newOrganisation"):
        operations.append(_operationEncode(organisationEncode(organisation)))
    operations.extend(
        _operationEncode(contactEncode(contact)) for contact in built["contacts"]
    )
    if built.get("newInstitution"):
        operations.append(_operationEncode(institutionEncode(institution)))
    operations.append(_operationEncode(relationshipEncode(relationship)))
    return {
        "schema": "eolas/bankingRelationship/v1",
        "schemaVersion": 1,
        "recordVersion": 1,
        "id": relationship.identity.record_id,
        "aggregateType": RELATIONSHIP_AGGREGATE,
        "ownerModule": BANKING_MODULE,
        "clannRef": built["clann_id"],
        "label": built["label"],
        "classification": built["classification"].value,
        "institution": {
            "id": institution.identity.record_id,
            "displayName": institution.display_name,
            "organisationId": organisation.identity.record_id,
            "organisationLegalName": organisation.legal_name,
            "institutionType": institution.institution_type,
        },
        "relationship": {
            "id": relationship.identity.record_id,
            "accountCategory": relationship.account_category,
            "purpose": relationship.purpose,
            "ownershipType": relationship.ownership_type,
            "status": relationship.status.value,
            "partyCount": len(relationship.parties),
            "continuityRoles": [role.role_id for role in relationship.continuity_roles],
            "identifierCount": len(relationship.identifiers),
            "balanceCount": len(relationship.balances),
        },
        "operations": operations,
        "metadata": {
            "source": capture.source.strip(),
            "sourceType": "manualCapture",
            "capturedAt": institution.provenance.recorded_at.isoformat(),
            "target": str(targetPath),
        },
    }


def _balancesBuild(
    fields: Mapping[str, Any], provenance: Provenance
) -> Tuple[BalanceObservation, ...]:
    amount = fields.get("balanceAmount")
    currency = fields.get("balanceCurrency")
    asOf = fields.get("balanceAsOf")
    if amount in (None, "", "unknown") or currency in (None, "", "unknown"):
        return ()
    if asOf in (None, "", "unknown"):
        raise DomainValidationError("A balance observation requires asOf.")
    observation = Observation(
        Money(Decimal(str(amount)), str(currency)),
        datetime.fromisoformat(str(asOf)),
        provenance,
    )
    return (BalanceObservation(observation),)


def _factFromCapture(value: Any) -> Fact[str]:
    if value is None or value == "":
        return Fact(FactState.ABSENT)
    if value == FactState.UNKNOWN.value:
        return Fact(FactState.UNKNOWN)
    if value == FactState.NOT_APPLICABLE.value:
        return Fact(FactState.NOT_APPLICABLE)
    return Fact.factKnown(str(value))


def _identifiersBuild(
    fields: Mapping[str, Any],
    classification: Classification,
    provenance: Provenance,
) -> Tuple[Any, ...]:
    kind = fields.get("identifierKind")
    value = fields.get("identifierProtected") or fields.get("identifierValue")
    if not kind or value in (None, "", "unknown"):
        return ()
    identifierClassification = classification
    if str(kind) in {"accountNumber", "iban", "customerNumber", "sortCode"}:
        if classification.rank < Classification.CONFIDENTIAL.rank:
            identifierClassification = Classification.CONFIDENTIAL
    return (
        identifierBankingCreate(
            str(kind), str(value), identifierClassification, provenance=provenance
        ),
    )


def _institutionDisplay(fields: Mapping[str, Any], label: str) -> str:
    value = fields.get("institution")
    if value in (None, "", "unknown", "notApplicable"):
        return label
    return str(value)


def _knownText(value: Any, default: str) -> str:
    if value in (None, "", "unknown", "notApplicable"):
        return default
    return str(value)


def _operationEncode(record: StoredRecord) -> Dict[str, Any]:
    return {
        "identity": identityEncode(record.identity),
        "schemaName": record.schema_name,
        "schemaVersion": record.schema_version,
        "payload": dict(record.payload),
    }


def _organisationName(
    fields: Mapping[str, Any], label: str, findings: List[str]
) -> str:
    value = fields.get("institution")
    if value in (None, "", "unknown"):
        findings.append("institution identity unknown")
        return label
    if value == "notApplicable":
        findings.append("institution marked notApplicable")
        return label
    return str(value)


def _ownershipType(fields: Mapping[str, Any], parties: Sequence[AccountParty]) -> str:
    explicit = fields.get("ownershipType")
    if explicit in {"sole", "joint", "trust", "business", "unknown"}:
        return str(explicit)
    holders = [party for party in parties if party.party_role == "legalHolder"]
    if len(holders) >= 2:
        return "joint"
    if len(holders) == 1:
        return "sole"
    return "unknown"


def _booleanFlag(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "yes", "1"}


def _idsList(value: Any) -> List[str]:
    if value in (None, "", [], ()):
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [part.strip() for part in str(value).split(",") if part.strip()]


def _institutionIdentity(clann_id: str, record_id: str) -> RecordIdentity:
    return RecordIdentity(record_id, clann_id, INSTITUTION_AGGREGATE, BANKING_MODULE)


def _organisationIdentity(clann_id: str, record_id: str) -> RecordIdentity:
    return RecordIdentity(record_id, clann_id, "organisation", "shared")


def _partiesBuild(
    store: RecordStore,
    clann_id: str,
    fields: Mapping[str, Any],
    classification: Classification,
    provenance: Provenance,
    findings: List[str],
) -> tuple[List[AccountParty], List[Contact]]:
    ownerRefs = _idsList(fields.get("ownerRefs"))
    raw = fields.get("owners")
    contacts: List[Contact] = []
    parties: List[AccountParty] = []
    if ownerRefs:
        resolved = [
            _partyFromRef(store, clann_id, record_id) for record_id in ownerRefs
        ]
    elif raw in (None, "", "unknown"):
        findings.append("account owners unknown")
        return [], []
    else:
        names = _idsList(raw)
        resolved = [
            _partyFromName(store, clann_id, name, classification, contacts)
            for name in names
        ]
    signing = (
        Fact.factKnown("eitherToSign")
        if len(resolved) > 1
        else Fact(FactState.NOT_APPLICABLE)
    )
    for partyRef in resolved:
        parties.append(
            AccountParty(
                partyRef,
                "legalHolder",
                "legalAndBeneficial",
                provenance,
                Fact(FactState.UNKNOWN),
                signing,
            )
        )
    return parties, contacts


def _partyFromName(
    store: RecordStore,
    clann_id: str,
    name: str,
    classification: Classification,
    contacts: List[Contact],
) -> RecordReference:
    matches = peopleNamed(store, name)
    if len(matches) > 1:
        raise DomainValidationError(
            f"Multiple Clann people are named {name!r}; supply ownerRefs."
        )
    if len(matches) == 1:
        person = matches[0]
        if person.identity.clann_id != clann_id:
            raise DomainValidationError("Cross-Clann references are prohibited.")
        return person.identity.referenceCreate()
    contact = Contact(
        RecordIdentity.identityCreate(clann_id, "contact", "shared"),
        name,
        classification,
    )
    contacts.append(contact)
    return contact.identity.referenceCreate()


def _partyFromRef(store: RecordStore, clann_id: str, record_id: str) -> RecordReference:
    party = partyLoadById(store, clann_id, record_id)
    if party.identity.clann_id != clann_id:
        raise DomainValidationError("Cross-Clann references are prohibited.")
    return party.identity.referenceCreate()


def _providerResolve(
    store: RecordStore,
    service: BankingService,
    clann_id: str,
    fields: Mapping[str, Any],
    label: str,
    classification: Classification,
    provenance: Provenance,
    review: ReviewState,
    findings: List[str],
) -> tuple[Organisation, FinancialInstitution, bool, bool]:
    institutionRef = str(fields.get("institutionRef") or "").strip()
    organisationRef = str(fields.get("organisationRef") or "").strip()
    forceCreate = _booleanFlag(fields.get("createInstitution"))
    displayName = _institutionDisplay(fields, label)
    if institutionRef:
        try:
            institution = service.institutionGet(
                _institutionIdentity(clann_id, institutionRef)
            )
            organisation = organisationLoad(
                store,
                RecordIdentity(
                    institution.organisation.record_id,
                    clann_id,
                    "organisation",
                    "shared",
                ),
            )
        except (KeyError, DomainValidationError) as error:
            raise DomainValidationError(
                "Unknown or cross-Clann institutionRef."
            ) from error
        return organisation, institution, False, False
    if organisationRef:
        try:
            organisation = organisationLoad(
                store, _organisationIdentity(clann_id, organisationRef)
            )
        except (KeyError, DomainValidationError) as error:
            raise DomainValidationError(
                "Unknown or cross-Clann organisationRef."
            ) from error
        linked = [
            item
            for item in service.institutionsList()
            if item.organisation.record_id == organisation.identity.record_id
        ]
        if len(linked) > 1:
            raise DomainValidationError(
                "Multiple financial institutions use this organisation; "
                "supply institutionRef."
            )
        if len(linked) == 1 and not forceCreate:
            return organisation, linked[0], False, False
        institution = _institutionCreate(
            clann_id,
            organisation,
            displayName,
            fields,
            classification,
            provenance,
            review,
        )
        return organisation, institution, False, True
    return _providerResolveByName(
        store,
        service,
        clann_id,
        fields,
        displayName,
        forceCreate,
        classification,
        provenance,
        review,
        findings,
    )


def _providerResolveByName(
    store: RecordStore,
    service: BankingService,
    clann_id: str,
    fields: Mapping[str, Any],
    displayName: str,
    forceCreate: bool,
    classification: Classification,
    provenance: Provenance,
    review: ReviewState,
    findings: List[str],
) -> tuple[Organisation, FinancialInstitution, bool, bool]:
    nameUnknown = fields.get("institution") in (None, "", "unknown", "notApplicable")
    if nameUnknown:
        _organisationName(fields, displayName, findings)
    institutions = [
        item for item in service.institutionsList() if item.display_name == displayName
    ]
    organisations = [
        item for item in organisationsLoad(store) if item.legal_name == displayName
    ]
    if not forceCreate and not nameUnknown:
        if len(institutions) > 1 or len(organisations) > 1:
            raise DomainValidationError(
                "Multiple providers match that name; supply institutionRef "
                "or organisationRef."
            )
        if len(institutions) == 1:
            institution = institutions[0]
            organisation = organisationLoad(
                store,
                RecordIdentity(
                    institution.organisation.record_id,
                    clann_id,
                    "organisation",
                    "shared",
                ),
            )
            return organisation, institution, False, False
        if len(organisations) == 1:
            organisation = organisations[0]
            linked = [
                item
                for item in service.institutionsList()
                if item.organisation.record_id == organisation.identity.record_id
            ]
            if len(linked) > 1:
                raise DomainValidationError(
                    "Multiple financial institutions use this organisation; "
                    "supply institutionRef."
                )
            if len(linked) == 1:
                return organisation, linked[0], False, False
            institution = _institutionCreate(
                clann_id,
                organisation,
                displayName,
                fields,
                classification,
                provenance,
                review,
            )
            return organisation, institution, False, True
    organisation = Organisation(
        RecordIdentity.identityCreate(clann_id, "organisation", "shared"),
        (
            _organisationName(fields, displayName, findings)
            if nameUnknown
            else displayName
        ),
        classification,
    )
    institution = _institutionCreate(
        clann_id,
        organisation,
        displayName,
        fields,
        classification,
        provenance,
        review,
    )
    return organisation, institution, True, True


def _institutionCreate(
    clann_id: str,
    organisation: Organisation,
    displayName: str,
    fields: Mapping[str, Any],
    classification: Classification,
    provenance: Provenance,
    review: ReviewState,
) -> FinancialInstitution:
    return institutionBuild(
        InstitutionCreateCommand(
            clann_id,
            organisation.identity.referenceCreate(),
            displayName,
            str(fields.get("institutionType", "unknown")),
            classification,
            provenance,
            review,
        )
    )


def _relationshipCommandFromRecord(record: StoredRecord) -> RelationshipCreateCommand:
    from eolas.banking.codec import relationshipDecode

    relationship = relationshipDecode(record)
    return RelationshipCreateCommand(
        relationship.identity.clann_id,
        relationship.institution,
        relationship.label,
        relationship.account_category,
        relationship.purpose,
        relationship.ownership_type,
        relationship.status,
        relationship.classification,
        relationship.provenance,
        relationship.review,
        relationship.product_name,
        relationship.currency,
        relationship.servicing_channel,
        relationship.signing_rule,
        relationship.household,
        relationship.parties,
        relationship.continuity_roles,
        relationship.identifiers,
        relationship.authority_links,
        relationship.balances,
        relationship.lifecycle,
        relationship.identity,
    )


def _reviewBuild(fields: Mapping[str, Any], provenance: Provenance) -> ReviewState:
    del provenance
    reviewed = date.fromisoformat(str(fields["lastReviewed"]))
    return ReviewState(
        Fact.factKnown(reviewed),
        Fact(FactState.UNKNOWN),
        Fact(FactState.UNKNOWN),
    )


def _rolesBuild(
    fields: Mapping[str, Any], provenance: Provenance
) -> Tuple[AccountContinuityRole, ...]:
    raw = fields.get("continuityRole") or fields.get("continuityRoles")
    if raw in (None, "", "unknown"):
        return ()
    if isinstance(raw, list):
        roleIds = [str(item) for item in raw]
    else:
        roleIds = [str(raw)]
    return tuple(
        AccountContinuityRole(role_id, provenance) for role_id in roleIds if role_id
    )


def _statusParse(value: Any) -> BankingStatus:
    if value in (None, ""):
        return BankingStatus.UNKNOWN
    try:
        return BankingStatus(str(value))
    except ValueError:
        return STATUS_ALIASES.get(str(value), BankingStatus.UNKNOWN)
