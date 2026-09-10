"""Shared people, organisation, authority and continuity compositions."""

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Optional, Tuple

from eolas.domain.values import (
    Classification,
    DomainValidationError,
    EvidenceReference,
    Fact,
    FactState,
    Jurisdiction,
    Provenance,
    RecordIdentity,
    RecordLifecycle,
    RecordReference,
    ReviewState,
    clannBoundaryValidate,
)


def _contactRoutesValidate(
    clann_id: str, contact_routes: Tuple["ContactRoute", ...]
) -> None:
    """Keep contact-route provenance inside its containing aggregate's Clann."""
    clannBoundaryValidate(
        clann_id, provenances=(route.provenance for route in contact_routes)
    )


@dataclass(frozen=True)
class ContactRoute:
    """Dated, purpose-specific way to contact a person or organisation."""

    channel: str
    address: str
    purpose: str
    classification: Classification
    verified_on: Fact[date]
    provenance: Provenance
    accessibility_note: Optional[str] = None


@dataclass(frozen=True)
class Person:
    """An individual represented as a canonical Clann aggregate."""

    identity: RecordIdentity
    display_name: str
    classification: Classification
    lifecycle: RecordLifecycle = RecordLifecycle()
    contact_routes: Tuple[ContactRoute, ...] = ()

    def __post_init__(self) -> None:
        _contactRoutesValidate(self.identity.clann_id, self.contact_routes)


@dataclass(frozen=True)
class Contact:
    """A lightweight external contact which may later link to a canonical party."""

    identity: RecordIdentity
    display_name: str
    classification: Classification
    represented_party: Optional[RecordReference] = None
    contact_routes: Tuple[ContactRoute, ...] = ()

    def __post_init__(self) -> None:
        references = () if self.represented_party is None else (self.represented_party,)
        clannBoundaryValidate(self.identity.clann_id, references=references)
        _contactRoutesValidate(self.identity.clann_id, self.contact_routes)


@dataclass(frozen=True)
class OrganisationBrand:
    """A familiar trading identity, distinct from legal organisation identity."""

    name: str
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    evidence: Tuple[EvidenceReference, ...] = ()


@dataclass(frozen=True)
class Organisation:
    """A legal/public/provider entity reusable across domain modules."""

    identity: RecordIdentity
    legal_name: str
    classification: Classification
    brands: Tuple[OrganisationBrand, ...] = ()
    contact_routes: Tuple[ContactRoute, ...] = ()
    lifecycle: RecordLifecycle = RecordLifecycle()

    def __post_init__(self) -> None:
        clannBoundaryValidate(
            self.identity.clann_id,
            evidence=(item for brand in self.brands for item in brand.evidence),
        )
        _contactRoutesValidate(self.identity.clann_id, self.contact_routes)


@dataclass(frozen=True)
class OrganisationRole:
    """A dated provider role whose vocabulary is owned by its domain module."""

    organisation: RecordReference
    role_type: str
    owner_module: str
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None


@dataclass(frozen=True)
class PartyRole:
    """A role held in relation to a record; it does not imply authority."""

    party: RecordReference
    subject: RecordReference
    role_type: str
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    provenance: Optional[Provenance] = None

    def __post_init__(self) -> None:
        provenances = () if self.provenance is None else (self.provenance,)
        clannBoundaryValidate(
            self.subject.clann_id,
            references=(self.party, self.subject),
            provenances=provenances,
        )


class AuthorityState(str, Enum):
    DRAFT = "draft"
    DORMANT = "dormant"
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass(frozen=True)
class Authority:
    """Legal/practical authority for one party to act for another."""

    identity: RecordIdentity
    grantor: RecordReference
    actor: RecordReference
    authority_type: str
    jurisdiction: Jurisdiction
    scope: Tuple[str, ...]
    activation_conditions: Tuple[str, ...]
    restrictions: Tuple[str, ...]
    state: AuthorityState
    effective_from: Optional[date]
    expires_on: Optional[date]
    evidence: Tuple[EvidenceReference, ...]
    classification: Classification

    def __post_init__(self) -> None:
        clannBoundaryValidate(
            self.identity.clann_id,
            references=(self.grantor, self.actor),
            evidence=self.evidence,
        )
        if not self.scope or not self.evidence:
            raise DomainValidationError("Authority requires scope and evidence.")

    def authorityAllows(self, action_scope: str, on_date: date) -> bool:
        """Evaluate lifecycle, date and explicit restrictions, not provider recognition."""
        return (
            self.state is AuthorityState.ACTIVE
            and action_scope in self.scope
            and (self.effective_from is None or self.effective_from <= on_date)
            and (self.expires_on is None or self.expires_on >= on_date)
            and action_scope not in self.restrictions
        )


class RegistrationState(str, Enum):
    PENDING = "pending"
    RECOGNISED = "recognised"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass(frozen=True)
class AuthorityRegistration:
    """A provider's recognition of an Authority, distinct from the Authority itself."""

    identity: RecordIdentity
    authority: RecordReference
    provider: RecordReference
    state: RegistrationState
    provider_reference: Optional[str]
    recognised_scope: Tuple[str, ...]
    restrictions: Tuple[str, ...]
    expires_on: Optional[date]
    evidence: Tuple[EvidenceReference, ...]

    def __post_init__(self) -> None:
        clannBoundaryValidate(
            self.identity.clann_id,
            references=(self.authority, self.provider),
            evidence=self.evidence,
        )


@dataclass(frozen=True)
class GuidanceReference:
    """Versioned, dated source of jurisdiction guidance used by a workflow."""

    guidance_id: str
    jurisdiction: Jurisdiction
    version: str
    effective_on: date
    verified_on: date
    source: str


@dataclass(frozen=True)
class ContinuityAction:
    """Event-specific action and its outcome, separate from mutable guidance."""

    identity: RecordIdentity
    action_type: str
    subject: RecordReference
    responsible_role: PartyRole
    state: str
    authority: Fact[RecordReference]
    guidance: Tuple[GuidanceReference, ...]
    evidence: Tuple[EvidenceReference, ...]
    outcome: Fact[str]
    review: ReviewState

    def __post_init__(self) -> None:
        references = [
            self.subject,
            self.responsible_role.party,
            self.responsible_role.subject,
        ]
        if self.authority.state is FactState.KNOWN:
            references.append(self.authority.value)
        if self.review.responsible_role.state is FactState.KNOWN:
            references.append(self.review.responsible_role.value)
        clannBoundaryValidate(
            self.identity.clann_id,
            references=references,
            evidence=self.evidence,
        )
        if self.responsible_role.subject != self.subject:
            raise DomainValidationError(
                "A continuity action's responsible role must concern its subject."
            )


@dataclass(frozen=True)
class Interaction:
    """Privacy-safe record of a dated provider or authority contact."""

    identity: RecordIdentity
    occurred_at: datetime
    parties: Tuple[RecordReference, ...]
    purpose: str
    summary: str
    outcome: Fact[str]
    follow_up: Fact[date]
    evidence: Tuple[EvidenceReference, ...]
    classification: Classification
    provenance: Provenance

    def __post_init__(self) -> None:
        clannBoundaryValidate(
            self.identity.clann_id,
            references=self.parties,
            evidence=self.evidence,
            provenances=(self.provenance,),
        )
