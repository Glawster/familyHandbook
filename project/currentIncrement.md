# Current increment

## Increment

Banking Core.

## Branch

`feature/banking-core`

## Objective

Implement the first Banking domain slice on the shared knowledge kernel so a
real banking relationship can be represented without loose capture dictionaries
or document-shaped data.

## Scope

- `FinancialInstitution` linked to shared `Organisation`.
- `BankingRelationship` as the real-world relationship aggregate.
- `AccountParty` ownership and interest, distinct from authority and access.
- Versioned `AccountContinuityRole` registry.
- Typed banking identifiers with masking, provenance and prohibited-secret
  rejection.
- `BalanceObservation` as a dated `Observation` of `Money`.
- Lifecycle/status, provenance, classification and review state using shared
  types.
- Persistence through the shared `RecordStore` port.
- CLI/curses `eolas capture banking` creating typed Banking records.

## Explicit exclusion

Do not implement in this increment:

- money movements and payment arrangements;
- transaction history, Direct Debits, standing orders or cancellation;
- bank-statement parsing, OCR or Open Banking;
- automatic institution lookup;
- executor or attorney banking workflows;
- banking reports;
- the full continuity dependency graph for Banking;
- cloud synchronisation or production encryption/key-management changes.

## Expected exit criteria

- Domain tests cover institution and relationship creation, opaque IDs, Clann
  isolation, joint ownership, non-owner authority references, continuity roles,
  identifiers, balances, provenance, classification, review, persistence and
  version conflicts.
- Capture/CLI adapter creates typed Banking records and existing non-banking
  capture continues to work.
- Tests use conspicuously fictional institutions and identifiers and require
  no network.
- Requirement 009 is updated but not marked completed.
- `pytest` passes.
- `manageProject --check` reports zero failures and zero warnings.

## Immediate next action

Money Movements and Payment Arrangements, keeping payment instructions separate
from the underlying obligation.
