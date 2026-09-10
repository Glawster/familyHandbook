# Change log

## 2026-09-10

- Implemented Banking Core: `FinancialInstitution`, `BankingRelationship`,
  `AccountParty`, versioned continuity roles, typed identifiers,
  `BalanceObservation`, authority links, and persistence through the shared
  `RecordStore` port.
- Adapted `eolas capture banking` so CLI/curses input creates typed Banking
  records rather than a loose capture dictionary.
- New Clann bootstrap allocates opaque `rec_` person and household IDs and
  persists `Person` aggregates to the shared store. Banking capture reuses
  existing people and institutions by stable reference or unique exact name.
- Added `Obligation`, `PaymentArrangement`, `MoneyMovement` and
  `TransactionObservation`, keeping the bill, the payment instruction, the
  expected flow and statement evidence as separate records.
- Requirement 009 remains in progress; statement import, payment processing
  and banking projections are not included.

## 2026-09-01

- Accepted the Phase 0 identity, persistence, party, authority, evidence and
  module-boundary ADRs.
- Implemented the Phase 1 shared knowledge kernel, dependency graph and
  versioned local persistence boundary.
- Refactored generic capture into a typed input adapter using shared secret and
  availability-state validation.
- Added the fictional Phase 1 cross-domain conformance scenario and tests.
