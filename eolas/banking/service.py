"""Banking domain service: validated commands over the shared RecordStore port."""

from dataclasses import dataclass
from typing import Optional, Tuple

from eolas.banking.codec import (
    institutionDecode,
    institutionEncode,
    relationshipDecode,
    relationshipEncode,
)
from eolas.banking.models import (
    BANKING_MODULE,
    INSTITUTION_AGGREGATE,
    RELATIONSHIP_AGGREGATE,
    AccountContinuityRole,
    AccountParty,
    AuthorityLink,
    BalanceObservation,
    BankingRelationship,
    BankingStatus,
    FinancialInstitution,
)
from eolas.banking.payments import (
    OBLIGATION_AGGREGATE,
    MoneyMovement,
    Obligation,
    PaymentArrangement,
    TransactionObservation,
)
from eolas.banking.paymentsCodec import (
    arrangementDecode,
    arrangementEncode,
    movementDecode,
    movementEncode,
    obligationDecode,
    obligationEncode,
    transactionDecode,
    transactionEncode,
)
from eolas.banking.roles import PRIMARY_OPERATING_ROLE
from eolas.domain.storage import RecordStore, WriteOperation
from eolas.domain.values import (
    Classification,
    DomainValidationError,
    Fact,
    FactState,
    Identifier,
    Jurisdiction,
    Provenance,
    RecordIdentity,
    RecordLifecycle,
    RecordReference,
    ReviewState,
)

OWNER_MODULE = BANKING_MODULE


@dataclass(frozen=True)
class InstitutionCreateCommand:
    """Create a FinancialInstitution linked to an existing Organisation."""

    clann_id: str
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
    identity: Optional[RecordIdentity] = None


@dataclass(frozen=True)
class RelationshipCreateCommand:
    """Create a BankingRelationship against an existing FinancialInstitution."""

    clann_id: str
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
    identity: Optional[RecordIdentity] = None


class BankingService:
    """Public Banking module boundary. Callers must not persist aggregates directly."""

    def __init__(self, store: RecordStore):
        self.store = store

    ## institution

    def institutionCreate(
        self, command: InstitutionCreateCommand
    ) -> FinancialInstitution:
        """Validate and persist a new FinancialInstitution."""
        institution = institutionBuild(command)
        committed = self.store.recordsCommit(
            (WriteOperation(institutionEncode(institution), None),)
        )[0]
        return institutionDecode(committed)

    def institutionGet(self, identity: RecordIdentity) -> FinancialInstitution:
        """Load a FinancialInstitution by opaque identity."""
        return institutionDecode(self.store.recordGet(identity))

    def institutionsList(self) -> Tuple[FinancialInstitution, ...]:
        """Return current FinancialInstitution aggregates in this Clann."""
        return tuple(
            institutionDecode(record)
            for record in self.store.recordsList(
                aggregate_type=INSTITUTION_AGGREGATE, owner_module=BANKING_MODULE
            )
        )

    ## relationship

    def relationshipCreate(
        self, command: RelationshipCreateCommand
    ) -> BankingRelationship:
        """Validate and persist a new BankingRelationship."""
        relationship = relationshipBuild(command)
        self.relationshipValidate(relationship)
        committed = self.store.recordsCommit(
            (WriteOperation(relationshipEncode(relationship), None),)
        )[0]
        return relationshipDecode(committed)

    def relationshipValidate(
        self,
        relationship: BankingRelationship,
        *,
        pending_institutions: Tuple[RecordIdentity, ...] = (),
    ) -> None:
        """Validate references and continuity-role uniqueness without writing."""
        pendingIds = {item.record_id for item in pending_institutions}
        if relationship.institution.record_id not in pendingIds:
            self._relationshipReferencesValidate(relationship)
        self._operatingRoleValidate(relationship, excluding=relationship.identity)

    def relationshipGet(self, identity: RecordIdentity) -> BankingRelationship:
        """Load a BankingRelationship by opaque identity."""
        return relationshipDecode(self.store.recordGet(identity))

    def relationshipRevise(
        self,
        relationship: BankingRelationship,
        expected_version: int,
    ) -> BankingRelationship:
        """Replace a relationship using optimistic expected-version checking."""
        self.relationshipValidate(relationship)
        committed = self.store.recordsCommit(
            (WriteOperation(relationshipEncode(relationship), expected_version),)
        )[0]
        return relationshipDecode(committed)

    ## obligation

    def obligationCreate(self, obligation: Obligation) -> Obligation:
        """Persist a new Obligation."""
        return obligationDecode(self._recordCreate(obligationEncode(obligation)))

    def obligationGet(self, identity: RecordIdentity) -> Obligation:
        """Load an Obligation by opaque identity."""
        return obligationDecode(self.store.recordGet(identity))

    ## arrangement

    def arrangementCreate(
        self,
        arrangement: PaymentArrangement,
        *,
        pending_obligations: Tuple[RecordIdentity, ...] = (),
        pending_relationships: Tuple[RecordIdentity, ...] = (),
    ) -> PaymentArrangement:
        """Persist a new PaymentArrangement after reference checks."""
        self.arrangementValidate(
            arrangement,
            pending_obligations=pending_obligations,
            pending_relationships=pending_relationships,
        )
        return arrangementDecode(self._recordCreate(arrangementEncode(arrangement)))

    def arrangementGet(self, identity: RecordIdentity) -> PaymentArrangement:
        """Load a PaymentArrangement by opaque identity."""
        return arrangementDecode(self.store.recordGet(identity))

    def arrangementRevise(
        self, arrangement: PaymentArrangement, expected_version: int
    ) -> PaymentArrangement:
        """Replace an arrangement using expected-version checking."""
        self.arrangementValidate(arrangement)
        committed = self.store.recordsCommit(
            (WriteOperation(arrangementEncode(arrangement), expected_version),)
        )[0]
        return arrangementDecode(committed)

    def arrangementValidate(
        self,
        arrangement: PaymentArrangement,
        *,
        pending_obligations: Tuple[RecordIdentity, ...] = (),
        pending_relationships: Tuple[RecordIdentity, ...] = (),
    ) -> None:
        """Require a real obligation and funding account, not an instruction."""
        pendingObligationIds = {item.record_id for item in pending_obligations}
        pendingRelationshipIds = {item.record_id for item in pending_relationships}
        if arrangement.obligation.record_id not in pendingObligationIds:
            try:
                self.obligationGet(
                    RecordIdentity(
                        arrangement.obligation.record_id,
                        arrangement.identity.clann_id,
                        OBLIGATION_AGGREGATE,
                        BANKING_MODULE,
                    )
                )
            except KeyError as error:
                raise DomainValidationError(
                    "PaymentArrangement requires a persisted Obligation."
                ) from error
        if arrangement.funding_account.record_id not in pendingRelationshipIds:
            try:
                self.relationshipGet(
                    RecordIdentity(
                        arrangement.funding_account.record_id,
                        arrangement.identity.clann_id,
                        RELATIONSHIP_AGGREGATE,
                        BANKING_MODULE,
                    )
                )
            except KeyError as error:
                raise DomainValidationError(
                    "PaymentArrangement requires a persisted BankingRelationship."
                ) from error

    ## movement

    def movementCreate(
        self,
        movement: MoneyMovement,
        *,
        pending_relationships: Tuple[RecordIdentity, ...] = (),
    ) -> MoneyMovement:
        """Persist a new expected MoneyMovement."""
        if movement.account.record_id not in {
            item.record_id for item in pending_relationships
        }:
            try:
                self.relationshipGet(
                    RecordIdentity(
                        movement.account.record_id,
                        movement.identity.clann_id,
                        RELATIONSHIP_AGGREGATE,
                        BANKING_MODULE,
                    )
                )
            except KeyError as error:
                raise DomainValidationError(
                    "MoneyMovement requires a persisted BankingRelationship."
                ) from error
        return movementDecode(self._recordCreate(movementEncode(movement)))

    def movementGet(self, identity: RecordIdentity) -> MoneyMovement:
        """Load a MoneyMovement by opaque identity."""
        return movementDecode(self.store.recordGet(identity))

    ## transaction

    def transactionCreate(
        self,
        transaction: TransactionObservation,
        *,
        pending_relationships: Tuple[RecordIdentity, ...] = (),
    ) -> TransactionObservation:
        """Persist dated transaction evidence without changing arrangements."""
        if transaction.account.record_id not in {
            item.record_id for item in pending_relationships
        }:
            try:
                self.relationshipGet(
                    RecordIdentity(
                        transaction.account.record_id,
                        transaction.identity.clann_id,
                        RELATIONSHIP_AGGREGATE,
                        BANKING_MODULE,
                    )
                )
            except KeyError as error:
                raise DomainValidationError(
                    "TransactionObservation requires a persisted BankingRelationship."
                ) from error
        return transactionDecode(self._recordCreate(transactionEncode(transaction)))

    def transactionGet(self, identity: RecordIdentity) -> TransactionObservation:
        """Load a TransactionObservation by opaque identity."""
        return transactionDecode(self.store.recordGet(identity))

    ## utilities

    def _recordCreate(self, record):
        return self.store.recordsCommit((WriteOperation(record, None),))[0]

    def _operatingRoleValidate(
        self,
        relationship: BankingRelationship,
        *,
        excluding: Optional[RecordIdentity] = None,
    ) -> None:
        activePrimary = [
            role
            for role in relationship.continuity_roles
            if role.role_id == PRIMARY_OPERATING_ROLE and role.roleEffective()
        ]
        if not activePrimary:
            return
        household = _householdResolve(relationship, activePrimary[0])
        if household is None:
            return
        if activePrimary[0].exception_reason:
            return
        for existing in self._relationshipsLoad():
            if excluding is not None and existing.identity == excluding:
                continue
            if existing.identity.clann_id != relationship.identity.clann_id:
                continue
            for role in existing.continuity_roles:
                if role.role_id != PRIMARY_OPERATING_ROLE or not role.roleEffective():
                    continue
                existingHousehold = _householdResolve(existing, role)
                if existingHousehold == household:
                    raise DomainValidationError(
                        "A household may have only one active primary operating "
                        "account unless an explicit exception is recorded."
                    )

    def _relationshipReferencesValidate(
        self, relationship: BankingRelationship
    ) -> None:
        try:
            institution = self.institutionGet(
                RecordIdentity(
                    relationship.institution.record_id,
                    relationship.institution.clann_id,
                    INSTITUTION_AGGREGATE,
                    BANKING_MODULE,
                )
            )
        except KeyError as error:
            raise DomainValidationError(
                "BankingRelationship requires a persisted FinancialInstitution."
            ) from error
        if institution.identity.clann_id != relationship.identity.clann_id:
            raise DomainValidationError("Cross-Clann references are prohibited.")

    def _relationshipsLoad(self) -> Tuple[BankingRelationship, ...]:
        return tuple(
            relationshipDecode(record)
            for record in self.store.recordsList(
                aggregate_type=RELATIONSHIP_AGGREGATE, owner_module=BANKING_MODULE
            )
        )


def institutionBuild(command: InstitutionCreateCommand) -> FinancialInstitution:
    """Construct a validated institution without persisting it."""
    identity = command.identity or RecordIdentity.identityCreate(
        command.clann_id, INSTITUTION_AGGREGATE, BANKING_MODULE
    )
    return FinancialInstitution(
        identity,
        command.organisation,
        command.display_name,
        command.institution_type,
        command.classification,
        command.provenance,
        command.review,
        command.jurisdiction,
        command.protection_group,
        command.identifiers,
        command.lifecycle,
    )


def relationshipBuild(command: RelationshipCreateCommand) -> BankingRelationship:
    """Construct a validated relationship without persisting it."""
    identity = command.identity or RecordIdentity.identityCreate(
        command.clann_id, RELATIONSHIP_AGGREGATE, BANKING_MODULE
    )
    return BankingRelationship(
        identity,
        command.institution,
        command.label,
        command.account_category,
        command.purpose,
        command.ownership_type,
        command.status,
        command.classification,
        command.provenance,
        command.review,
        command.product_name,
        command.currency,
        command.servicing_channel,
        command.signing_rule,
        command.household,
        command.parties,
        command.continuity_roles,
        command.identifiers,
        command.authority_links,
        command.balances,
        command.lifecycle,
    )


def _householdResolve(
    relationship: BankingRelationship, role: AccountContinuityRole
) -> Optional[str]:
    if role.household.state is FactState.KNOWN and role.household.value is not None:
        return role.household.value.record_id
    if (
        relationship.household.state is FactState.KNOWN
        and relationship.household.value is not None
    ):
        return relationship.household.value.record_id
    return None
