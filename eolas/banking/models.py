"""Banking-owned knowledge: institutions, relationships, parties and balances."""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional, Tuple

from eolas.banking.identifiers import identifierKindValidate
from eolas.banking.roles import CURRENT_REGISTRY_VERSION, roleRegistered
from eolas.domain.security import classificationResolve, secretsValidate
from eolas.domain.values import (
    Classification,
    DomainValidationError,
    EvidenceReference,
    Fact,
    FactState,
    Identifier,
    Jurisdiction,
    Money,
    Observation,
    Provenance,
    RecordIdentity,
    RecordLifecycle,
    RecordReference,
    ReviewState,
    clannBoundaryValidate,
)

BANKING_MODULE = "banking"
INSTITUTION_AGGREGATE = "financialInstitution"
RELATIONSHIP_AGGREGATE = "bankingRelationship"

OWNERSHIP_TYPES = {"sole", "joint", "trust", "business", "unknown"}
ACCOUNT_PARTY_ROLES = {
    "legalHolder",
    "beneficialOwner",
    "trustee",
    "signatory",
    "responsibleParty",
    "nominee",
    "beneficiary",
}
AUTHORITY_DISGUISES = {
    "attorney",
    "deputy",
    "executor",
    "administrator",
    "accessGrant",
    "user",
    "device",
}
INTEREST_TYPES = {"legal", "beneficial", "legalAndBeneficial", "unknown"}
SIGNING_RULES = {"eitherToSign", "allToSign", "notApplicable", "unknown"}
INSTITUTION_TYPES = {
    "bank",
    "buildingSociety",
    "creditUnion",
    "eMoneyProvider",
    "cardIssuer",
    "other",
    "unknown",
}


class BankingStatus(str, Enum):
    """Operational status of a banking relationship, not record lifecycle."""

    ACTIVE = "active"
    DORMANT = "dormant"
    RESTRICTED = "restricted"
    CLOSURE_PENDING = "closurePending"
    CLOSED = "closed"
    UNKNOWN = "unknown"


class AuthorityReadiness(str, Enum):
    """Whether a referenced Authority is operationally usable for this account."""

    HAS_AUTHORITY = "hasAuthority"
    EXPECTED_NOT_REGISTERED = "expectedNotRegistered"
    REGISTRATION_IN_PROGRESS = "registrationInProgress"
    RESTRICTED = "authorityRestricted"
    ENDED = "authorityEnded"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class AccountParty:
    """Ownership or interest in a relationship; never legal authority."""

    party: RecordReference
    party_role: str
    interest_type: str
    provenance: Provenance
    proportion: Fact[str] = Fact(FactState.UNKNOWN)
    signing_rule: Fact[str] = Fact(FactState.NOT_APPLICABLE)
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    evidence: Tuple[EvidenceReference, ...] = ()

    def __post_init__(self) -> None:
        if self.party_role in AUTHORITY_DISGUISES:
            raise DomainValidationError(
                "Account-party roles cannot represent authority or application access."
            )
        if self.party_role not in ACCOUNT_PARTY_ROLES:
            raise DomainValidationError(
                f"Unsupported account-party role: {self.party_role}."
            )
        if self.interest_type not in INTEREST_TYPES:
            raise DomainValidationError(
                f"Unsupported interest type: {self.interest_type}."
            )
        if (
            self.signing_rule.state is FactState.KNOWN
            and self.signing_rule.value not in SIGNING_RULES
        ):
            raise DomainValidationError("Unsupported signing rule.")


@dataclass(frozen=True)
class AccountContinuityRole:
    """Dated continuity purpose published from the banking role registry."""

    role_id: str
    provenance: Provenance
    household: Fact[RecordReference] = Fact(FactState.UNKNOWN)
    registry_version: str = CURRENT_REGISTRY_VERSION
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    exception_reason: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.role_id.strip():
            raise DomainValidationError("A continuity role identifier is required.")

    def roleCurrent(self) -> bool:
        """Unknown registry entries are retained but cannot drive workflows."""
        return roleRegistered(self.role_id, self.registry_version)

    def roleEffective(self, on_date: Optional[date] = None) -> bool:
        """Return whether the role applies on a date, or currently if omitted."""
        if on_date is None:
            return self.effective_to is None
        return (self.effective_from is None or self.effective_from <= on_date) and (
            self.effective_to is None or self.effective_to >= on_date
        )


@dataclass(frozen=True)
class AuthorityLink:
    """Reference to shared Authority; not ownership and not an AccessGrant."""

    authority: RecordReference
    readiness: AuthorityReadiness
    provenance: Provenance
    registration: Fact[RecordReference] = Fact(FactState.UNKNOWN)

    def __post_init__(self) -> None:
        if self.authority.record_type != "authority":
            raise DomainValidationError(
                "Authority links must reference an Authority aggregate."
            )
        if (
            self.registration.state is FactState.KNOWN
            and self.registration.value is not None
            and self.registration.value.record_type != "authorityRegistration"
        ):
            raise DomainValidationError(
                "Registration links must reference an AuthorityRegistration."
            )


@dataclass(frozen=True)
class BalanceObservation:
    """A dated balance; never timeless account state."""

    observation: Observation[Money]
    purpose: str = "continuitySnapshot"

    def __post_init__(self) -> None:
        if not isinstance(self.observation.value, Money):
            raise DomainValidationError("A balance observation requires Money.")
        if not self.purpose.strip():
            raise DomainValidationError("A balance observation requires a purpose.")


@dataclass(frozen=True)
class FinancialInstitution:
    """Banking view of a provider, always linked to a shared Organisation."""

    identity: RecordIdentity
    organisation: RecordReference
    display_name: str
    institution_type: str
    classification: Classification
    provenance: Provenance
    review: ReviewState
    jurisdiction: Fact[Jurisdiction] = Fact(FactState.UNKNOWN)
    protection_group: Fact[str] = Fact(FactState.UNKNOWN)
    identifiers: Tuple[Identifier, ...] = ()
    lifecycle: RecordLifecycle = RecordLifecycle()

    def __post_init__(self) -> None:
        bankingIdentityValidate(self.identity, INSTITUTION_AGGREGATE)
        classificationResolve(self.classification)
        if self.organisation.record_type != "organisation":
            raise DomainValidationError(
                "A financial institution must reference a shared Organisation."
            )
        if not self.display_name.strip():
            raise DomainValidationError("Institution display name cannot be empty.")
        if self.institution_type not in INSTITUTION_TYPES:
            raise DomainValidationError(
                f"Unsupported institution type: {self.institution_type}."
            )
        _identifiersValidate(self.identity, self.identifiers)
        clannBoundaryValidate(
            self.identity.clann_id,
            references=(self.organisation,),
            provenances=(self.provenance,),
        )
        if self.review.responsible_role.state is FactState.KNOWN:
            clannBoundaryValidate(
                self.identity.clann_id,
                references=(self.review.responsible_role.value,),
            )


@dataclass(frozen=True)
class BankingRelationship:
    """The real-world banking relationship, not a statement or document."""

    identity: RecordIdentity
    institution: RecordReference
    label: str
    account_category: str
    purpose: str
    ownership_type: str
    status: BankingStatus
    classification: Classification
    provenance: Provenance
    review: ReviewState
    product_name: Fact[str] = Fact(FactState.UNKNOWN)
    currency: Fact[str] = Fact(FactState.UNKNOWN)
    servicing_channel: Fact[str] = Fact(FactState.UNKNOWN)
    signing_rule: Fact[str] = Fact(FactState.UNKNOWN)
    household: Fact[RecordReference] = Fact(FactState.UNKNOWN)
    parties: Tuple[AccountParty, ...] = ()
    continuity_roles: Tuple[AccountContinuityRole, ...] = ()
    identifiers: Tuple[Identifier, ...] = ()
    authority_links: Tuple[AuthorityLink, ...] = ()
    balances: Tuple[BalanceObservation, ...] = ()
    lifecycle: RecordLifecycle = RecordLifecycle()

    def __post_init__(self) -> None:
        bankingIdentityValidate(self.identity, RELATIONSHIP_AGGREGATE)
        classificationResolve(self.classification)
        if self.institution.record_type != INSTITUTION_AGGREGATE:
            raise DomainValidationError(
                "A banking relationship must reference a FinancialInstitution."
            )
        if not self.label.strip():
            raise DomainValidationError("A banking relationship needs a safe label.")
        if not self.account_category.strip() or not self.purpose.strip():
            raise DomainValidationError("Account category and purpose are required.")
        if self.ownership_type not in OWNERSHIP_TYPES:
            raise DomainValidationError(
                f"Unsupported ownership type: {self.ownership_type}."
            )
        if (
            self.signing_rule.state is FactState.KNOWN
            and self.signing_rule.value not in SIGNING_RULES
        ):
            raise DomainValidationError("Unsupported signing rule.")
        _partiesValidate(self)
        _identifiersValidate(self.identity, self.identifiers)
        secretsValidate({"purpose": self.purpose, "label": self.label})
        references = [self.institution]
        provenances = [self.provenance]
        evidence = []
        for party in self.parties:
            references.append(party.party)
            provenances.append(party.provenance)
            evidence.extend(party.evidence)
        for role in self.continuity_roles:
            provenances.append(role.provenance)
            if role.household.state is FactState.KNOWN:
                references.append(role.household.value)
        for link in self.authority_links:
            references.append(link.authority)
            provenances.append(link.provenance)
            if link.registration.state is FactState.KNOWN:
                references.append(link.registration.value)
        for balance in self.balances:
            provenances.append(balance.observation.provenance)
        if self.household.state is FactState.KNOWN:
            references.append(self.household.value)
        if self.review.responsible_role.state is FactState.KNOWN:
            references.append(self.review.responsible_role.value)
        clannBoundaryValidate(
            self.identity.clann_id,
            references=references,
            evidence=evidence,
            provenances=provenances,
        )


def bankingIdentityValidate(identity: RecordIdentity, aggregate_type: str) -> None:
    if identity.owner_module != BANKING_MODULE:
        raise DomainValidationError("Banking aggregates must be owned by banking.")
    if identity.aggregate_type != aggregate_type:
        raise DomainValidationError(
            f"Expected aggregate {aggregate_type}; found {identity.aggregate_type}."
        )


def _identifiersValidate(
    identity: RecordIdentity, identifiers: Tuple[Identifier, ...]
) -> None:
    for identifier in identifiers:
        identifierKindValidate(
            identifier.identifier_type,
            identifier.masked_value,
            format_check=False,
        )
        if identifier.protected_value is not None:
            identifierKindValidate(
                identifier.identifier_type, identifier.protected_value
            )
            if identifier.protected_value == identity.record_id:
                raise DomainValidationError(
                    "A banking identifier cannot be used as aggregate identity."
                )
        if identifier.masked_value == identity.record_id:
            raise DomainValidationError(
                "A banking identifier cannot be used as aggregate identity."
            )


def _partiesValidate(relationship: BankingRelationship) -> None:
    legalHolders = [
        party for party in relationship.parties if party.party_role == "legalHolder"
    ]
    if relationship.ownership_type == "joint" and len(legalHolders) < 2:
        raise DomainValidationError(
            "Joint ownership requires at least two legal holders."
        )
    if relationship.ownership_type == "sole" and len(legalHolders) > 1:
        raise DomainValidationError(
            "Sole ownership cannot have multiple legal holders."
        )
    for party in relationship.parties:
        if party.party.record_id == relationship.identity.record_id:
            raise DomainValidationError("A party cannot be the relationship itself.")
