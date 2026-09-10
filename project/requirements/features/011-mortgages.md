# 011: Mortgages

Priority: high  
Owner: project maintainers

## Status

InProgress

## Outcome

As a borrower, household member or authorised representative, I need to
understand mortgages, secured property interests and payment dependencies so
that housing can be protected and informed action taken during incapacity,
bereavement or financial disruption.

## Context

A mortgage connects a debt, lender, borrower, property, legal charge, ownership,
insurance and household occupancy. Property ownership does not necessarily
match mortgage liability. Delay or an incorrect assumption can threaten the
home, while premature repayment or sale can create penalties or legal harm.

## Scope and information priorities

Support residential, buy-to-let, repayment, interest-only, part-and-part,
fixed, variable, tracker, discounted, offset, flexible, shared-ownership,
equity-loan, lifetime and foreign-property mortgages, plus further advances and
second charges.

**Mandatory:** lender/servicer, mortgage type/purpose, property link, borrowers,
liability basis, legal-charge/security link, repayment method, status,
classification and review date.

**Recommended:** masked mortgage reference, currency, point-in-time balance,
payment amount/frequency/account, interest basis and deal end, remaining term,
repayment strategy for interest-only debt, ownership and occupancy, arrears or
support status, insurance/endowment links, early-repayment terms reference,
authority, contacts and event actions.

**Optional:** full reference, original advance/date, loan-to-value observation,
valuation evidence, overpayment/underpayment facilities and correspondence.

**Never store:** lender credentials, property access codes, payment-card secrets
or security answers.

## Functional requirements

### MT-1: Mortgage and security model

- Separate lender, current servicer, broker and legal-charge holder.
- Model borrowers, guarantors, property legal owners, beneficial owners and
  occupiers independently with source and effective dates.
- Link each facility to the secured property, charge priority and official-title
  or deed reference without asserting legal effect.
- Support product parts with different balances, rates, terms or repayment
  methods under one facility.
- Link offset accounts, endowments, investments, life/critical-illness/income-
  protection policies, guarantees, shared-ownership rent/service charges and
  equity loans without duplicating their records.

### MT-2: Terms, payments and risk

- Every balance, payment, valuation, interest rate and loan-to-value value must
  carry currency, date and source.
- Record fixed/tracker/variable basis, benchmark and margin, deal/reversion date,
  term/maturity, repayment method and overpayment/early-repayment references.
- Interest-only or part-and-part records require a repayment-strategy status and
  evidence link, without claiming sufficiency.
- Link payment source and essentiality through Banking; a payment instruction
  must remain distinct from the mortgage obligation.
- Track arrears, possession action, payment holiday, term/rate change,
  forbearance/support plan, complaint and vulnerability needs.
- Provide a contact-lender-early action when payment difficulty is anticipated;
  do not calculate or recommend a product. See [FCA borrower-support rules](https://www.fca.org.uk/publications/policy-statements/ps24-2-strengthening-protections-borrowers-financial-difficulty).

### MT-3: Continuity workflows

- **Preparation:** confirm borrowers versus owners, essential payment source,
  rate/deal deadlines, interest-only strategy, insurance and representative
  authority.
- **Hospital/incapacity:** preserve payments, verify authority and lender
  registration, identify support needs and avoid unapproved contract changes.
- **Death:** notify lender, obtain date-of-death balance and terms, identify
  surviving borrower liability, property ownership/succession, insurance
  claims, affordability and estate/probate needs; do not promise transfer,
  forbearance or sale outcome.
- **Separation/move:** review occupation, ownership, liability, consent-to-let,
  address, payment and insurance; Eolas must not infer release from liability.
- **End of deal/term:** identify decision date, redemption statement need,
  repayment vehicle and professional-advice flags.
- Joint debt and secured-debt consequences require lender/legal confirmation;
  [MoneyHelper debt-after-death guidance](https://www.moneyhelper.org.uk/en/family-and-care/death-and-bereavement/dealing-with-the-debts-of-someone-who-has-died.html)
  explains why ownership and liability must be reviewed separately.

## Reports

- Mortgage Summary: property, lender, borrowers/owners, parts, dated balance,
  payment, term, rate/deal dates, security and review state.
- Housing Continuity Checklist: occupancy, essential payments, authority,
  insurance, support contacts and event actions.
- Interest-only Repayment Review and Mortgage/Insurance Dependency Report.

## Data and validation requirements

Models must include `MortgageFacility`, `MortgagePart`, `SecuredParty`,
`PropertySecurity`, `MortgageTermObservation`, `RepaymentStrategy` and links to
Property, Banking, Insurance, Investment, Authority and evidence records.

1. A mortgage requires property, lender, borrower, repayment method, security
   status, classification and review date.
2. Owner, occupier and borrower roles cannot be inferred from one another.
3. Product parts reconcile to the total only when observations share the same
   effective date and currency; discrepancies remain visible.
4. Interest-only debt without strategy is valid but must create a review action.
5. Closure/readiness is blocked by unresolved charge, balance, insurance claim,
   payment, ownership or redemption evidence.
6. Guidance and rate information require source/effective dates.

## Acceptance criteria

1. A fictional property with two owners, one borrower and one occupier preserves
   all roles without inventing liability or ownership.
2. A part-repayment/part-interest-only mortgage records two parts, one facility
   and a visible repayment-strategy review.
3. A death scenario identifies surviving liability, date-of-death balance,
   insurance, occupancy and legal/professional questions without promising that
   the debt or property transfers automatically.
4. A payment-difficulty scenario preserves arrears/support history and directs
   early verified lender contact without generating financial advice.
5. Changing or closing a funding account lists the mortgage as an essential
   unresolved dependency.
6. Reports mask references, date every financial value, work offline and remain
   accessible; prohibited credentials never persist or enter logs.

## Future opportunities

- Statement/redemption import, rate-deadline reminders, reviewed affordability
  evidence and regulated-data connections under separate requirements.

## Out of scope

- Applications, advice, affordability decisions, valuations, conveyancing,
  payment/refinancing, possession prediction or legal/tax conclusions.
- UI design or implementation.

## Dependencies and traceability

- Requires [002](002-privacyAndSecurityModel.md), [009](009-bankingModule.md)
  and the shared Property model; related to 012, 013, 015 and 016.
- ADRs: [002](../../adr/002-offlineFirst.md),
  [003](../../adr/003-neverStorePasswords.md),
  [005](../../adr/005-informationClassification.md),
  [006](../../adr/006-sharedDomainModel.md),
  [007](../../adr/007-knowledgeBeforeDocuments.md),
  [011](../../adr/011-platformPrivateDataRoot.md).
- Principles: [P-001, P-002, P-004, P-005, P-007, P-009 and P-010](../../../documentation/principles.md).
- Implementation: shared Phase 1 kernel, dependency graph and typed capture input adapter; domain aggregate and workflows pending
- Tests: shared-kernel, storage, security, graph and capture-adapter conformance tests implemented; domain acceptance tests pending
- Documentation: pending
- Pull request: pending
- Agent runs: 2026-07-31 - Codex, initial domain specification.

## Change history

- 2026-07-31: created.
