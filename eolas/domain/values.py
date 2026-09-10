"""Small immutable values shared by Eolas domain modules."""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
import re
from typing import Generic, Iterable, Optional, Tuple, TypeVar
from urllib.parse import unquote, urlsplit
from uuid import uuid4


class DomainValidationError(ValueError):
    """Raised when shared-domain knowledge violates an invariant."""


class Classification(str, Enum):
    """Ordered handling classification for knowledge and individual fields."""

    PUBLIC = "public"
    PRIVATE = "private"
    CONFIDENTIAL = "confidential"
    HIGHLY_CONFIDENTIAL = "highlyConfidential"

    @property
    def rank(self) -> int:
        """Return the restriction order for policy comparisons."""
        return tuple(Classification).index(self)

    def classificationCombine(
        self, override: Optional["Classification"]
    ) -> "Classification":
        """Apply a field override without permitting weaker handling."""
        if override is None:
            return self
        return max(self, override, key=lambda item: item.rank)


class FactState(str, Enum):
    """Explicit semantic availability of a fact."""

    KNOWN = "known"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "notApplicable"
    ABSENT = "absent"


T = TypeVar("T")


@dataclass(frozen=True)
class Fact(Generic[T]):
    """A value whose unknown, inapplicable and absent states remain distinct."""

    state: FactState
    value: Optional[T] = None

    def __post_init__(self) -> None:
        if self.state is FactState.KNOWN and self.value is None:
            raise DomainValidationError("A known fact requires a value.")
        if self.state is not FactState.KNOWN and self.value is not None:
            raise DomainValidationError(
                f"A {self.state.value} fact cannot carry a value."
            )

    @classmethod
    def factKnown(cls, value: T) -> "Fact[T]":
        """Create a known fact without coercing false-like values."""
        return cls(FactState.KNOWN, value)


@dataclass(frozen=True)
class RecordIdentity:
    """Stable opaque identity owned by exactly one Clann and module."""

    record_id: str
    clann_id: str
    aggregate_type: str
    owner_module: str

    def __post_init__(self) -> None:
        if not self.record_id.startswith("rec_") or len(self.record_id) < 20:
            raise DomainValidationError("Record IDs must be opaque rec_ identifiers.")
        if (
            not self.clann_id.strip()
            or not self.aggregate_type.strip()
            or not self.owner_module.strip()
        ):
            raise DomainValidationError("Identity ownership fields cannot be empty.")

    @classmethod
    def identityCreate(
        cls, clann_id: str, aggregate_type: str, owner_module: str
    ) -> "RecordIdentity":
        """Allocate an opaque ID which does not encode names or record type."""
        return cls(f"rec_{uuid4().hex}", clann_id, aggregate_type, owner_module)

    def referenceCreate(self) -> "RecordReference":
        """Create a typed reference without transferring aggregate ownership."""
        return RecordReference(self.record_id, self.clann_id, self.aggregate_type)


@dataclass(frozen=True)
class RecordReference:
    """A stable typed cross-aggregate reference."""

    record_id: str
    clann_id: str
    record_type: str

    def referenceValidate(self, clann_id: str) -> None:
        """Reject references which cross the private Clann boundary."""
        if self.clann_id != clann_id:
            raise DomainValidationError("Cross-Clann references are prohibited.")


def clannBoundaryValidate(
    clann_id: str,
    *,
    references: Iterable[RecordReference] = (),
    evidence: Iterable["EvidenceReference"] = (),
    provenances: Iterable["Provenance"] = (),
) -> None:
    """Validate every nested identity-bearing value against one Clann boundary."""
    for reference in references:
        reference.referenceValidate(clann_id)
    for item in evidence:
        if item.clann_id != clann_id:
            raise DomainValidationError("Evidence must belong to the same Clann.")
        if item.provenance.actor_reference is not None:
            item.provenance.actor_reference.referenceValidate(clann_id)
    for provenance in provenances:
        if provenance.actor_reference is not None:
            provenance.actor_reference.referenceValidate(clann_id)


class LifecycleState(str, Enum):
    ACTIVE = "active"
    HISTORIC = "historic"
    SUPERSEDED = "superseded"
    TOMBSTONED = "tombstoned"


@dataclass(frozen=True)
class RecordLifecycle:
    """Non-destructive lifecycle state for an aggregate."""

    state: LifecycleState = LifecycleState.ACTIVE
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    reason: Optional[str] = None

    def __post_init__(self) -> None:
        if (
            self.effective_to
            and self.effective_from
            and self.effective_to < self.effective_from
        ):
            raise DomainValidationError("Lifecycle end cannot precede its start.")
        if self.state is LifecycleState.TOMBSTONED and not self.reason:
            raise DomainValidationError("A tombstone requires a reason.")


@dataclass(frozen=True)
class Provenance:
    """Origin and derivation context for a fact."""

    source_type: str
    source_reference: str
    recorded_at: datetime
    actor_reference: Optional[RecordReference] = None
    derivation: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.source_type.strip() or not self.source_reference.strip():
            raise DomainValidationError(
                "Provenance requires source type and reference."
            )
        if self.recorded_at.tzinfo is None or self.recorded_at.utcoffset() is None:
            raise DomainValidationError("Provenance time must include a timezone.")


@dataclass(frozen=True)
class EvidenceReference:
    """Secure reference to immutable evidence; never the evidence bytes."""

    evidence_id: str
    clann_id: str
    purpose: str
    checksum_sha256: str
    locator: str
    classification: Classification
    provenance: Provenance

    def __post_init__(self) -> None:
        checksum = self.checksum_sha256.lower()
        if len(checksum) != 64 or any(
            char not in "0123456789abcdef" for char in checksum
        ):
            raise DomainValidationError("Evidence requires a SHA-256 checksum.")
        if (
            not self.evidence_id.strip()
            or not self.purpose.strip()
            or not self.locator.strip()
        ):
            raise DomainValidationError(
                "Evidence identity, purpose and secure locator are required."
            )
        _evidenceLocatorValidate(self.locator)


def _evidenceLocatorValidate(locator: str) -> None:
    """Require an opaque internal locator, never a path, URL, or credential."""
    parsed = urlsplit(locator)
    segments = unquote(parsed.path).split("/")[1:]
    tokenPattern = re.compile(r"[A-Za-z0-9][A-Za-z0-9._~-]*")
    if (
        parsed.scheme != "evidence"
        or not tokenPattern.fullmatch(parsed.netloc)
        or parsed.query
        or parsed.fragment
        or not segments
        or any(
            segment in {"", ".", ".."} or not tokenPattern.fullmatch(segment)
            for segment in segments
        )
    ):
        raise DomainValidationError(
            "Evidence locator must be an opaque evidence:// namespace/reference."
        )


class VerificationState(str, Enum):
    UNVERIFIED = "unverified"
    USER_CONFIRMED = "userConfirmed"
    PROVIDER_CONFIRMED = "providerConfirmed"


@dataclass(frozen=True)
class Identifier:
    """Typed external identifier which is never an aggregate identity."""

    identifier_type: str
    masked_value: str
    classification: Classification
    protected_value: Optional[str] = field(default=None, repr=False)
    provenance: Optional[Provenance] = None
    verification: VerificationState = VerificationState.UNVERIFIED

    def __post_init__(self) -> None:
        if not self.identifier_type.strip() or not self.masked_value.strip():
            raise DomainValidationError(
                "Identifier type and masked display are required."
            )
        if self.masked_value == self.protected_value:
            raise DomainValidationError(
                "Masked display must not reveal the protected value."
            )
        from eolas.domain.security import secretsValidate

        secretsValidate({"identifier": self.protected_value or self.masked_value})

    def identifierDisplay(self, allow_protected: bool = False) -> str:
        """Return the full value only under an explicit protected policy."""
        if allow_protected and self.protected_value is not None:
            return self.protected_value
        return self.masked_value


class ObservationStatus(str, Enum):
    OBSERVED = "observed"
    ESTIMATED = "estimated"
    USER_CONFIRMED = "userConfirmed"
    PROVIDER_CONFIRMED = "providerConfirmed"


@dataclass(frozen=True)
class Observation(Generic[T]):
    """A fact that is true only as of a particular time."""

    value: T
    as_of: datetime
    provenance: Provenance
    status: ObservationStatus = ObservationStatus.OBSERVED
    confidence: Optional[Decimal] = None

    def __post_init__(self) -> None:
        if self.as_of.tzinfo is None or self.as_of.utcoffset() is None:
            raise DomainValidationError("Observation time must include a timezone.")
        if self.confidence is not None and not Decimal(
            "0"
        ) <= self.confidence <= Decimal("1"):
            raise DomainValidationError(
                "Observation confidence must be between 0 and 1."
            )


@dataclass(frozen=True)
class Money:
    """Exact decimal money in an ISO 4217 currency."""

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if isinstance(self.amount, float):
            raise DomainValidationError(
                "Money must not use a binary floating-point value."
            )
        try:
            Decimal(self.amount)
        except InvalidOperation as error:
            raise DomainValidationError("Money amount must be decimal.") from error
        if (
            len(self.currency) != 3
            or not self.currency.isalpha()
            or not self.currency.isupper()
        ):
            raise DomainValidationError(
                "Money currency must be a three-letter uppercase code."
            )


@dataclass(frozen=True)
class Schedule:
    """Timing of a recurring or expected event without financial assumptions."""

    frequency: str
    next_occurrence: Fact[date]
    variability: str = "fixed"
    timing_note: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.frequency.strip() or self.variability not in {
            "fixed",
            "variable",
            "irregular",
        }:
            raise DomainValidationError("Schedule frequency/variability is invalid.")


@dataclass(frozen=True)
class Jurisdiction:
    """Stable versioned jurisdiction reference, separate from display guidance."""

    code: str
    scheme: str
    version: str

    def __post_init__(self) -> None:
        if not all(value.strip() for value in (self.code, self.scheme, self.version)):
            raise DomainValidationError(
                "Jurisdiction code, scheme and version are required."
            )


@dataclass(frozen=True)
class ReviewState:
    """Review timing, responsibility and unresolved findings."""

    last_reviewed: Fact[date]
    next_review: Fact[date]
    responsible_role: Fact[RecordReference]
    findings: Tuple[str, ...] = ()
