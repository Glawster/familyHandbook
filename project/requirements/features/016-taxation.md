# 016: Taxation

Priority: high  
Owner: project maintainers

## Status

InProgress

## Outcome

As a taxpayer, attorney or personal representative, I need to identify tax
relationships, obligations, agents, deadlines and evidence so that required
matters can be found and referred to the correct authority or professional
without Eolas becoming a tax-calculation or filing service.

## Context

Tax duties depend on person/entity, residence, jurisdiction, tax type, period,
event and changing law. Death can create separate pre-death and estate-
administration obligations. Eolas must organise provenance and actions, never
infer liability from incomplete household data or expose government credentials.

## Scope and information priorities

Support personal income/self assessment, PAYE records, National Insurance,
capital gains, inheritance/estate, property/rental, council/local property,
vehicle, VAT, corporation/business, payroll, trust, foreign and other
jurisdictional taxes as typed relationships. This list does not assert that a
person is liable for every type.

**Mandatory:** taxpayer/entity, authority, jurisdiction, tax type, registration/
filing status, relevant period, classification and review date.

**Recommended:** masked taxpayer reference, agent/adviser and authority,
deadlines and source, return/payment status, dated liability/refund observation,
payment account, correspondence, elections/reliefs evidence, income/gain/asset
source links, records-retention rule/source, open enquiries/disputes, event
actions and last authority confirmation.

**Optional:** full reference where needed, computations supplied by an adviser,
returns/notices/receipts, residency evidence and estate/trust registrations.

**Never store:** government gateway credentials, activation codes, filing
tokens, one-time codes, adviser credentials, card security data or identity
verification answers.

## Functional requirements

### TX-1: Tax relationship and periods

- Distinguish taxpayer, personal representative, trustee, business, employer,
  agent/adviser and authority; representation requires scope/evidence.
- Model obligation/return by tax type, jurisdiction and period, including
  amended/superseded versions and authority acknowledgements.
- Link taxable-source evidence to Banking, Employment, Property, Investment,
  Pension, Insurance, Gift, Trust, Business and Estate records without computing
  a tax result.
- Every amount must identify tax/interest/penalty/refund type, currency, date,
  source and whether estimated, submitted, assessed, paid, appealed or final.
- Deadlines require official/adviser source, effective date, jurisdiction and
  review; a generic calendar date cannot be treated as universal.

### TX-2: Evidence, retention and actions

- Support returns, calculations, assessments, coding notices, certificates,
  payslips/P45/P60, statements, invoices, valuations, receipts, elections,
  correspondence, submission/payment confirmations and professional workpapers.
- Preserve originals and version/provenance; an imported number remains a
  candidate until confirmed.
- Retention actions must be tied to applicable period/rule and backups. For UK
  estate valuation, HMRC may request records for up to 20 years after
  Inheritance Tax is paid: [GOV.UK estate record guidance](https://www.gov.uk/valuing-estate-of-someone-who-died/records).
- Link payment instruction separately from liability. Payment, refund and
  allocation require authority confirmation; Eolas must not submit or pay.
- Track enquiry, appeal, penalty, time-to-pay/support and professional escalation
  without advising on merits.

### TX-3: Continuity workflows

- **Preparation:** inventory tax authorities/types, agents, references,
  deadlines, record locations, income/assets and unresolved matters.
- **Incapacity:** verify financial authority and tax-authority/agent recognition;
  preserve deadlines and records without using the taxpayer's credentials.
- **Death:** record date/jurisdiction and personal representative, use applicable
  notification service, separate final personal returns from estate income,
  value assets/liabilities at required dates, preserve records and professional
  questions. GOV.UK confirms pre-death and estate income may require separate
  returns: [returns for someone who died](https://www.gov.uk/self-assessment-tax-returns/returns-for-someone-who-has-died).
- **Estate administration:** track Inheritance Tax, income/gains during
  administration, beneficiary statements, payments/refunds, clearance and
  evidence without distributing or calculating advice.
- **Move/residency/business change:** review jurisdictions, authorities,
  registrations, payroll/VAT/property and adviser needs; do not infer residence.

## Reports

- Tax Relationship Summary; Deadline and Filing Register; Evidence and
  Retention Schedule; Payment/Refund Register; Estate Tax Checklist; Adviser and
  Authority Contact Log; Unresolved Enquiry/Appeal Report.

## Data and validation requirements

Models must include `TaxRelationship`, `TaxPeriod`, `TaxObligation`,
`TaxAmountObservation`, `TaxAgentAuthority`, `TaxEvidence`, `TaxDeadline` and
links to Person, Estate, Trust, Business, Asset, Income, Banking and documents.

1. Tax record requires taxpayer, authority, jurisdiction, type, period/status,
   classification and review date.
2. Taxpayer reference is typed by authority and masked by default.
3. Amounts cannot be summed across periods/currencies/statuses without an
   explicit report basis.
4. A filed return, assessed liability and paid amount are separate states.
5. Amending data preserves submitted versions and evidence.
6. Time-sensitive rules outside effective dates are blocked from current action.

## Acceptance criteria

1. Fictional PAYE, Self Assessment, rental, CGT, business VAT and estate tax
   records preserve taxpayer, period, authority, agent and evidence separately.
2. A death scenario creates distinct pre-death and estate-administration work
   and does not treat Tell Us Once as filing a return.
3. A changed deadline/rule updates current guidance without rewriting historic
   periods or completed actions.
4. Estimated, submitted, assessed, paid and refunded amounts remain distinct and
   traceable to evidence.
5. A retention report identifies the rule/source and does not recommend deletion
   while an enquiry, estate, backup or legal hold remains unresolved.
6. Credentials/codes are rejected; reports mask references, work offline and are
   accessible; no tax calculation or personalised conclusion is generated.

## Future opportunities

- Document import, deadline reminders, evidence-pack export, reviewed data
  exchange with authorised agents and official APIs under separate approval.

## Out of scope

- Tax advice, residence/domicile determination, calculation, filing, payment,
  refund claim, valuation, avoidance planning or authority impersonation.
- UI design or implementation.

## Dependencies and traceability

- Requires [002](002-privacyAndSecurityModel.md) and shared domain records;
  related to 009-015 and integrates with [008](008-documentImportFramework.md).
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
