# 013: Investments

Priority: high  
Owner: project maintainers

## Status

InProgress

## Outcome

As an investor, attorney, trustee or personal representative, I need an accurate
inventory of investment relationships, ownership, wrappers, advisers and
evidence so that assets can be safeguarded, valued and administered without
mistaking stale values for advice or using another person's credentials.

## Context

Investments may be held directly, jointly, in tax wrappers, trusts, nominee or
platform accounts and may be illiquid, volatile, foreign or subject to calls,
fees and tax reporting. Eolas records continuity knowledge, not portfolio
management or investment recommendations.

## Scope and information priorities

Support shares, funds, ETFs, bonds/gilts, investment trusts, managed portfolios,
ISAs other than Cash ISA, general investment accounts, employee shares,
certificates, crowdfunding/peer-to-peer, private companies, partnerships,
commodities, foreign holdings and digital assets as separately classified
assets. Pensions, cash deposits and life policies remain linked modules.

**Mandatory:** investment relationship/type, owner or beneficial owner,
provider/custodian/platform, wrapper, jurisdiction, status, currency context,
classification and review date.

**Recommended:** masked reference, holdings or safe portfolio reference,
nominee/legal title, adviser/discretionary manager, point-in-time value and
source, acquisition/cost evidence reference, income destination, fees, tax
documents, liquidity/restrictions, beneficiaries/trust, authority, protection
status, statements and event actions.

**Optional:** quantities, acquisition lots, target/allocation or stated strategy,
certificate location, voting/contact preferences and professional valuations.

**Never store:** trading credentials, private cryptographic keys, seed phrases,
wallet recovery material, transaction-signing codes or adviser portal tokens.

## Functional requirements

### IV-1: Ownership, custody and holdings

- Distinguish beneficial owner, registered/legal holder, nominee, trustee,
  custodian, platform, manager and adviser.
- Model a portfolio/account separately from holdings and preserve provider
  changes, transfers and historic custody.
- A holding must identify asset/instrument, quantity or `unknown`, currency,
  evidence date and ownership share; ticker/name alone cannot establish identity.
- Represent jointly held, trust, corporate, certificated, dematerialised,
  restricted, pledged and foreign assets with evidence and jurisdiction.
- Digital assets require custody type and safe access-arrangement reference;
  secrets remain outside Eolas.

### IV-2: Value, income, tax and protection

- Every price/value/cost/income observation requires date, currency, source and
  valuation status; reports must warn that value may change.
- Preserve dividends, interest, distributions and capital-return relationships
  through Banking and Taxation without becoming a transaction ledger.
- Record wrapper, tax document and cost-basis evidence, residency/source-country
  context and professional-advice needs without calculating liability.
- Protection scheme/authorisation status must be dated and verified, and must
  distinguish firm failure from investment loss. Eolas never guarantees FSCS or
  overseas coverage; link to [current FSCS coverage](https://protected.fscs.org.uk/what-we-cover/).
- Record illiquidity, lock-in, maturity, capital calls, guarantees, encumbrances,
  unlisted valuation and complaint/claim status.

### IV-3: Authority and continuity

- **Preparation:** inventory platforms and direct holdings, confirm title,
  statements, tax/cost evidence, income, beneficiaries/trusts, advisers and safe
  access references.
- **Incapacity:** verify financial authority and provider/platform registration;
  an attorney must follow applicable duties and cannot inherit an investment
  strategy automatically.
- **Death:** stop credential use, notify providers, obtain date-of-death holdings
  and valuations, identify title/beneficial interest, income, tax, transfer or
  sale restrictions and estate/probate route.
- **Provider failure/fraud:** independently verify FCA/provider/FSCS contacts,
  preserve evidence and avoid recovery-fee scams.
- **Transfer/maturity:** reconcile holdings, cash, tax documents and custody
  before closing the old relationship.
- The module must flag concentrated, illiquid, leveraged, foreign, trust,
  business and digital assets for qualified review without recommending action.

## Reports

- Investment Inventory; Ownership and Custody Map; Dated Valuation Schedule;
  Investment Income Register; Tax Evidence Checklist; Estate/Attorney Investment
  Guide; Illiquid and Restricted Asset Register.

Reports must distinguish observed value from current value, mask identifiers and
exclude access secrets.

## Data and validation requirements

Models must include `InvestmentRelationship`, `Portfolio`, `Holding`,
`InvestmentParty`, `ValuationObservation`, `CustodyArrangement`,
`InvestmentRestriction` and links to Institution, Asset, Banking, Taxation,
Authority, Trust and evidence.

1. Relationship requires owner, provider/custody, wrapper/type, jurisdiction,
   status, classification and review date.
2. Registered title, beneficial ownership and management authority are distinct.
3. Quantity, cost and value require effective date/source and cannot be silently
   aggregated across currencies.
4. Transfer reconciliation cannot mark complete with unexplained cash or holding
   differences.
5. Protection status requires scheme, scope, source and verification date.
6. Prohibited keys/credentials block storage and diagnostics.

## Acceptance criteria

1. Fictional direct shares, platform ISA, joint portfolio, trust holding,
   employee shares, private company and digital asset preserve distinct title,
   benefit, custody and authority.
2. A report containing a six-month-old valuation labels its date/source and does
   not calculate or imply a current total without an explicit dated basis.
3. Death workflow produces date-of-death holding/value, income, tax, title and
   transfer actions without recommending sale or using credentials.
4. Attorney workflow records authority restrictions, provider registration and
   decision evidence without assuming the donor's historic strategy must change
   or continue.
5. Provider failure distinguishes firm protection from market loss and uses a
   dated official source.
6. Seed phrases, private keys and portal credentials are rejected everywhere;
   reports work locally, accessibly and offline.

## Future opportunities

- Reviewed statement/contract-note import, price feeds, corporate-action and
  maturity reminders, cost-basis reconciliation and regulated-provider data
  access, each requiring explicit consent and non-advice controls.

## Out of scope

- Trading, portfolio optimisation, performance claims, suitability, valuation
  guarantees, tax computation, market feeds, custody or digital-asset recovery.
- UI design or implementation.

## Dependencies and traceability

- Requires [002](002-privacyAndSecurityModel.md) and [009](009-bankingModule.md);
  related to 012, 014, 015 and 016; integrates with [008](008-documentImportFramework.md).
- ADRs: [002](../../adr/002-offlineFirst.md), [003](../../adr/003-neverStorePasswords.md),
  [005](../../adr/005-informationClassification.md), [006](../../adr/006-sharedDomainModel.md),
  [007](../../adr/007-knowledgeBeforeDocuments.md), [011](../../adr/011-platformPrivateDataRoot.md).
- Principles: [P-001, P-002, P-004, P-005, P-007, P-009 and P-010](../../../documentation/principles.md).
- Implementation: shared Phase 1 kernel, dependency graph and typed capture input adapter; domain aggregate and workflows pending
- Tests: shared-kernel, storage, security, graph and capture-adapter conformance tests implemented; domain acceptance tests pending
- Documentation: pending
- Pull request: pending
- Agent runs: 2026-07-31 - Codex, initial domain specification.

## Change history

- 2026-07-31: created.
