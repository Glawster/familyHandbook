# 014: Pensions

Priority: high  
Owner: project maintainers

## Status

InProgress

## Outcome

As a pension member, dependant, attorney or personal representative, I need to
identify pension rights, providers, nominations, income and death benefits so
that entitlements can be claimed and providers notified without confusing a
wish, scheme discretion, estate asset or guaranteed benefit.

## Context

Pensions can be state, workplace or personal; defined benefit or contribution;
active, deferred, crystallised, transferred or in payment. Death-benefit and tax
rules vary by scheme, age, date, jurisdiction and legislation. Eolas must retain
scheme evidence and dated guidance, not calculate retirement or tax advice.

## Scope and information priorities

Support State Pension, defined-benefit/final-salary/career-average schemes,
defined-contribution pots, workplace/master-trust, personal/stakeholder/SIPP,
annuities, drawdown, overseas pensions, AVCs, protected rights/guarantees and
death-in-service benefits.

**Mandatory:** pension type, member, provider/scheme/administrator, status,
jurisdiction, masked reference, classification and review date.

**Recommended:** employer link, service/membership dates, retirement/status
dates, point-in-time pot/value or promised-income evidence, contribution and
income account, benefit basis, guarantees/protections, adviser, beneficiaries/
dependants, expression-of-wish or binding-direction status/date/location,
spouse/dependant benefits, death-in-service link, authority, tax documents,
contacts and event actions.

**Optional:** full reference, transfer history/value, annual/lifetime allowance
evidence relevant to its date, protected tax-free cash, escalation/indexation,
early/ill-health options and forecasts.

**Never store:** provider credentials, National Insurance account credentials,
activation/access codes, security answers or signing secrets.

## Functional requirements

### PN-1: Scheme, benefit and parties

- Distinguish scheme, employer, trustee, administrator, provider, insurer,
  adviser and payroll.
- Record member, dependant, nominee, successor, beneficiary and estate as
  distinct roles with scheme-specific meaning.
- Model defined-benefit rights, defined-contribution funds, annuity income,
  drawdown and State Pension without reducing them to one balance.
- Preserve active/deferred/in-payment/transferred/paid-out status and transfer
  lineage; closed employer does not imply a lost pension.
- Link divorce/dissolution sharing or attachment orders, guarantees, protected
  terms and trust/death-in-service benefits to evidence.

### PN-2: Nominations, income and tax context

- Distinguish non-binding expression of wish, binding direction where valid,
  scheme-rule dependant benefit and estate destination. Do not call every named
  person a beneficiary with guaranteed entitlement.
- Record nomination date, scope, people/charities, proportions if stated,
  acknowledgement and review triggers such as marriage, divorce, birth or death.
- Current guidance notes many providers retain discretion despite expressions
  of wish: [MoneyHelper pensions after death](https://www.moneyhelper.org.uk/en/pensions-and-retirement/pension-problems/pensions-after-death)
  and [HMRC death-benefit principles](https://www.gov.uk/hmrc-internal-manuals/pensions-tax-manual/ptm071000).
- Income, forecast, pot and transfer values require date/source and cannot be
  presented as guaranteed unless the evidence says so.
- Tax rules must be versioned by effective date. The planned UK inheritance-tax
  treatment from 2027 must not be applied before its effective date and must
  link to [current HMRC guidance](https://www.gov.uk/government/publications/inheritance-tax-unused-pension-funds-and-death-benefits).

### PN-3: Continuity workflows

- **Preparation:** find all schemes, update nominations, identify dependant/
  spouse benefits, statements, guarantees, advisers and access arrangements.
- **Incapacity:** verify financial authority and each scheme's permitted
  representative actions; benefit decisions require scheme/advice confirmation.
- **Death:** use Tell Us Once for covered state/public schemes, separately notify
  private/workplace schemes, obtain claim packs, preserve nomination/dependant
  evidence, record deadlines, options and tax/professional review. GOV.UK states
  most private/workplace schemes require separate contact: [Tell Us Once](https://www.gov.uk/after-a-death/organisations-you-need-to-contact-and-tell-us-once).
- **Retirement/transfer:** record advice requirement, quotations, guarantees,
  scams checks, decision evidence and completion reconciliation without
  recommending an option.
- **Lost scheme:** retain employer/service history and use official tracing
  routes without disclosing credentials.

## Reports

- Pension Summary; Scheme and Employer Map; Income and Contribution Register;
  Nomination Review; Retirement/Transfer Evidence Checklist; Bereavement Pension
  Guide; Tax-Rule Review Flags.

## Data and validation requirements

Models must include `PensionArrangement`, `PensionScheme`, `PensionParty`,
`BenefitEntitlement`, `PensionValueObservation`, `Nomination`, `PensionIncome`
and links to Employer, Banking, Insurance, Taxation, Authority and evidence.

1. Arrangement requires member, type, scheme/provider, status, jurisdiction,
   classification and review date.
2. Forecast, pot, transfer value and income require type, date, currency/source
   and guarantee status.
3. Nomination type and scheme discretion are mandatory when a nomination is
   represented; missing status is `unknown`, not binding.
4. State, defined-benefit, defined-contribution and annuity benefits cannot be
   merged into a generic pot.
5. Time-dependent tax guidance cannot drive actions outside its effective dates.
6. Transfer/closure requires destination and reconciliation evidence.

## Acceptance criteria

1. Fictional State Pension, deferred DB, workplace DC, SIPP drawdown, annuity
   and overseas pension retain their different benefits and parties.
2. An expression of wish appears as a dated wish subject to scheme rules, while
   a documented binding direction remains distinguishable.
3. Death workflow identifies Tell Us Once coverage and separately lists all
   other schemes, evidence, claim options and tax review without promising a
   recipient or amount.
4. A future tax rule is displayed with effective date and cannot alter a
   pre-effective-date scenario.
5. A transfer preserves source/destination, guarantees, advice/decision evidence
   and reconciliation rather than deleting the old arrangement.
6. Credentials/codes are rejected; reports are masked, accessible, local and
   fully usable offline.

## Future opportunities

- Statement import, official pension tracing, nomination/review reminders,
  regulated dashboards and benefit modelling under separate requirements.

## Out of scope

- Pension advice, forecasts/calculation, consolidation recommendations,
  transfers, claims submission, beneficiary decisions or tax calculation.
- UI design or implementation.

## Dependencies and traceability

- Requires [002](002-privacyAndSecurityModel.md) and [009](009-bankingModule.md);
  related to 013, 015 and 016; integrates with [008](008-documentImportFramework.md).
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
