# Current increment

## Increment

Banking Core identity cleanup.

## Branch

`feature/banking-core`

## Objective

Reuse canonical shared-domain identities during Banking capture: Clann people
instead of duplicate Contacts, and existing Organisation/FinancialInstitution
records instead of a new provider per relationship.

## Scope

- New Clann bootstrap allocates opaque `rec_` IDs for people and households.
- Bootstrap persists `Person` aggregates to the Clann `RecordStore`.
- Legacy prototype slug IDs remain readable; they are not allocated to new
  records.
- Banking capture resolves `ownerRefs` and unique exact person names to
  existing `Person` records.
- Unresolved owner names may still create a `Contact`.
- Duplicate person or institution names require explicit references.
- `institutionRef` / `organisationRef` reuse existing providers.
- Unique exact institution names reuse a stored provider.
- `createInstitution` forces a new provider.

## Explicit exclusion

Do not implement money movements, payment arrangements, fuzzy matching,
automatic institution directories, or destructive identity migration.

## Expected exit criteria

- Capture tests prove Person reuse, joint owners, Contact-only-for-unknown,
  duplicate-name rejection, institution reuse, explicit refs winning over
  names, and no duplicate Organisation on reuse.
- New bootstrap people use opaque IDs; legacy slug IDs still construct.
- `pytest` passes.
- `manageProject --check` reports zero failures and zero warnings.

## Immediate next action

Money Movements and Payment Arrangements, keeping payment instructions separate
from the underlying obligation.
