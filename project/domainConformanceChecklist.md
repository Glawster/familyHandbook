# Domain conformance checklist

This checklist is the Phase 0/1 review gate derived from requirements
[008–018](requirements/requirementsIndex.md). It covers only shared-foundation
obligations. Passing it does not complete any domain requirement or authorise
Phase 2 Banking implementation by itself.

## Cross-cutting foundation gate

- [x] Canonical records use stable opaque IDs with one Clann, aggregate type and
  owner module.
- [x] Cross-aggregate references, nested evidence and provenance actors are
  rejected when they cross a Clann boundary.
- [x] Missing and invalid classifications fail closed; field handling cannot
  weaken its record classification.
- [x] Credentials, authentication material and complete payment-card numbers
  are prohibited independently of classification.
- [x] External identifiers have masked display values and remain distinct from
  canonical record identity.
- [x] Facts distinguish known, unknown, not applicable and absent states.
- [x] Observations are dated and sourced; money uses decimal values and explicit
  currency.
- [x] Evidence references use checksums, classification, provenance and opaque
  internal locators rather than document bytes or revealing paths.
- [x] Authority, party role, ownership and provider recognition remain separate.
- [x] Persistence demonstrates Clann isolation, owner/type checks, append-only
  prior versions, explicit migrations, atomic change sets and locked
  expected-version conflict detection.
- [x] Kernel tests run without Qt or network access.
- [x] The fictional scenario covers two households, organisations, an
  account-like relationship, income, an essential obligation, authority,
  dependency impact and death without usable identifiers or secrets.

## Requirement traceability

| Requirement | Shared Phase 0/1 obligation | Evidence | Deliberately deferred |
| --- | --- | --- | --- |
| [008: Document Import Framework](requirements/features/008-documentImportFramework.md) | Supply typed identity, classification, provenance, evidence-reference and atomic target-commit boundaries without allowing a plugin to own canonical facts. | ADRs 0012, 0013, 0016 and 0017; `eolas/domain/`; kernel conformance tests. | Ingestion, retained bytes, OCR, candidates, plugin runtime and import UI. |
| [009: Banking](requirements/features/009-bankingModule.md) | Define reusable organisations, identifiers, authority, observations, continuity actions and dependency traversal without Banking semantics. | ADRs 0012–0017; fictional dependency fixture. | All Banking aggregates, edge semantics, workflows and projections. |
| [010: Credit cards](requirements/features/010-creditCards.md) | Preserve the boundary between an external identifier, a future payment instrument and a module-owned liability. | Identity/ownership ADR and masked identifier tests. | Facilities, card instruments, balances and repayment workflows. |
| [011: Mortgages](requirements/features/011-mortgages.md) | Provide dated money/evidence, party roles, authority and typed cross-module references. | Value, authority, evidence and graph tests. | Mortgage facilities, property security and repayment strategies. |
| [012: Loans](requirements/features/012-loans.md) | Keep borrower/guarantor roles distinct from ownership and authority; retain dated evidence. | PartyRole, Authority and EvidenceReference contracts. | Loan, guarantee, security and settlement aggregates. |
| [013: Investments](requirements/features/013-investments.md) | Provide temporal observations, exact money, evidence and authority without credential storage. | Observation, Money, prohibited-secret and authority tests. | Portfolios, holdings, custody and investment workflows. |
| [014: Pensions](requirements/features/014-pensions.md) | Represent organisations, dated value evidence, authority and dependency references without asserting entitlement. | Organisation, Observation, EvidenceReference and graph contracts. | Pension arrangements, benefits, nominations and transfers. |
| [015: Insurance](requirements/features/015-insurance.md) | Support classified evidence, role/authority distinctions, actions and dated provider interactions. | Classification, PartyRole, Authority, ContinuityAction and Interaction tests. | Policies, cover, premiums and claims. |
| [016: Taxation](requirements/features/016-taxation.md) | Supply versioned jurisdiction, masked identifiers, authority, provenance and immutable prior versions. | Jurisdiction, Identifier, Authority and storage-history tests. | Tax relationships, periods, obligations and filings. |
| [017: Subscriptions](requirements/features/017-subscriptions.md) | Preserve obligation versus payment boundaries and provide dependency/action contracts. | ADR-0017, ContinuityAction and dependency graph tests. | Contracts, entitlements, renewals and cancellations. |
| [018: Utilities](requirements/features/018-utilities.md) | Support shared organisations, premises-ready references, classified contacts, authority and essential dependency impact. | Organisation/Contact, Authority and graph conformance tests. | Utility services, supply points, meters, support needs and incidents. |

## Phase 2 entry review

Before Banking begins, maintainers should confirm that:

- [ ] findings from the Phase 0/1 review are accepted as resolved;
- [ ] no unresolved ADR changes the Banking ownership or transaction boundary;
- [ ] Banking commands will use the shared identity, classification, authority,
  evidence, persistence and dependency contracts rather than duplicate them;
- [ ] Banking acceptance tests are mapped to requirement 009; and
- [ ] Phase 2 work is recorded as a separate increment.
