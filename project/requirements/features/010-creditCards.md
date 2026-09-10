# 010: Credit cards

Priority: high  
Owner: project maintainers

## Status

InProgress

## Outcome

As a cardholder, representative or personal representative, I need to identify
credit-card facilities, liabilities, cardholders, recurring authorities and
claims so that essential commitments and debts can be handled lawfully after an
emergency, incapacity or death.

## Context

A credit card is revolving credit, a payment instrument and sometimes the basis
of purchase protection, rewards or travel benefits. The principal borrower,
additional cardholder, account owner and person who made a purchase may differ.
Eolas must describe those relationships without storing card credentials or
encouraging use by an unauthorised person.

## Scope and information priorities

The module must support personal, joint-liability where offered, business,
corporate, charge, store, secured, balance-transfer, purchase, rewards, travel
and virtual-card facilities.

**Mandatory when applicable:** issuer, facility type and purpose, principal
borrower(s), liability basis, status, masked account reference, currency,
payment account, repayment mechanism, statement cycle, classification and last
review.

**Recommended:** credit limit and dated available-credit observation, current
or statement balance with date, minimum-payment basis, interest/fee reference,
promotional rate end, additional cardholders, cards and virtual cards, recurring
card payments, instalment plans, cash advances, balance transfers, arrears or
support arrangement, rewards/benefits, linked insurance, purchase claims,
provider contacts and event-specific actions.

**Optional:** full credit-account reference where justified, last four card
digits, expiry month/year, safe statement location, purchase evidence, foreign-
use settings and a card's safe physical-location reference.

**Never store:** full card number, PIN, CVV/CVC, magnetic-stripe/chip data,
password, app/session token, one-time code, security answer, recovery code or
transaction-signing secret.

## Functional requirements

### CC-1: Facility, parties and instruments

- Record the regulated/legal creditor separately from its brand and servicing
  provider.
- Distinguish principal borrower, joint borrower, guarantor, business, employee
  card user and additional cardholder. An additional card must not imply account
  ownership, liability or authority to administer the facility.
- Record cards as replaceable instruments linked to the enduring facility, with
  masked identity, named user, physical/virtual status, lifecycle and
  replacement relationship.
- Record attorney/deputy/executor authority and provider registration separately
  from possession of a card or knowledge of account details.

### CC-2: Liability and repayment

- Support point-in-time balances, credit limits, minimum payment, payment due
  date, currency and source; no amount may appear current without an `asOf`
  date.
- Link Direct Debit, standing order or manual repayment to the Banking module
  and identify full-balance, minimum, fixed or variable repayment intent.
- Record interest-bearing balance types, fees, promotional periods, instalment
  plans and balance transfers as dated terms, not timeless defaults.
- Track arrears, default, collections, hardship/support arrangement, disputed
  debt and settlement without calculating advice or payment priority.
- Link joint, guaranteed and business liability to the responsible parties and
  evidence; never infer liability from family relationship or card use.

### CC-3: Recurring payments, purchases and benefits

- Link recurring card authorities to the underlying subscription/contract and
  preserve merchant, purpose, typical amount, last seen date, essentiality and
  event-specific review action.
- Card replacement or cancellation must trigger review of recurring payments;
  it must not imply that merchant contracts are cancelled.
- Preserve material purchase evidence, refunds, chargebacks, disputes and
  statutory/provider claim references without guaranteeing eligibility.
- Distinguish Section 75, chargeback, insurance and merchant remedies. Current
  [MoneyHelper card-protection guidance](https://www.moneyhelper.org.uk/en/everyday-money/credit/how-youre-protected-when-you-pay-by-card)
  notes that additional-cardholder claims can depend on the principal
  cardholder and purchase context.
- Record rewards, points, cashback, lounge/travel benefits and linked insurance
  with owner, expiry/change risk and bereavement terms; never value them as cash
  without a dated provider basis.

### CC-4: Continuity workflows

- **Emergency/hospitalisation:** identify upcoming payment, essential recurring
  services, separately authorised help, fraud/lost-card route and hardship
  support; never share credentials.
- **Incapacity:** verify property/financial authority, restrictions and issuer
  registration; use representative access issued by the provider.
- **Death:** stop card use, preserve statements and purchase evidence, notify
  the issuer, obtain date-of-death liability/credit information, review
  recurring contracts and claims, and record estate treatment. A sole debt is
  not automatically a relative's debt; joint borrowers and guarantors require
  separate review. See [MoneyHelper debt-after-death guidance](https://www.moneyhelper.org.uk/en/family-and-care/death-and-bereavement/dealing-with-the-debts-of-someone-who-has-died.html).
- **Relationship/business-role change:** review cards, authorised users,
  recurring payments, liability, rewards and access before removal.
- Suspected fraud, coercion or financial difficulty must offer verified issuer,
  FCA-authorised support and free debt-advice routes without making automated
  decisions. FCA rules require appropriate treatment of borrowers in
  difficulty: [FCA policy statement](https://www.fca.org.uk/publications/policy-statements/ps24-2-strengthening-protections-borrowers-financial-difficulty).

## Reports

- Credit Card Summary: facilities, borrowers, masked cards, dated balances,
  limits, repayment source, promotional deadlines and review state.
- Recurring Card Payment Register: merchant, contract, card/facility,
  essentiality and event action.
- Debt and Support Checklist: liability, arrears/support status, authority,
  contacts, evidence and next actions.
- Purchase Protection Register: purchase, payer/cardholder, evidence, possible
  remedy, deadline source and outcome.

Reports must mask identifiers, state dates/classification and contain no card or
authentication secrets.

## Data and validation requirements

Models must include `CreditFacility`, `FacilityParty`, `CardInstrument`,
`CreditTermObservation`, `CardPurchase`, `CardClaim` and links to Banking
`MoneyMovement`, `Authority`, `FinancialInstitution` and evidence.

1. A facility requires issuer, type, purpose, responsible borrower, status,
   currency, classification and review date.
2. A balance/limit/payment requires amount, currency, effective date and source.
3. Additional-cardholder status cannot satisfy borrower, owner or authority.
4. Cancellation of a card or payment authority leaves linked contracts open.
5. Claim eligibility must be `potential`, `providerConfirmed`, `accepted`,
   `rejected`, `paid` or `unknown`, never inferred from purchase price alone.
6. Prohibited card/credential patterns block canonical storage and logs.

## Acceptance criteria

1. A fictional principal holder with two additional cardholders produces one
   facility, three card instruments and only the principal's documented
   liability; no extra ownership is inferred.
2. Replacing a card preserves the facility and history and lists every recurring
   payment for review without cancelling a contract.
3. A dated balance-transfer promotion, minimum-payment Direct Debit and arrears
   arrangement remain distinct and appear in the continuity checklist.
4. A deceased sole holder scenario stops unauthorised card use, preserves
   claims/evidence, identifies estate liability and does not assign debt to a
   relative without a joint/guarantee basis.
5. Full PAN, CVV, PIN and credentials are rejected from fields, imports, notes,
   logs and reports; permitted identifiers are masked by default.
6. A purchase by an additional cardholder is shown for provider eligibility
   review rather than promised Section 75 protection.
7. All records, reports and workflows operate offline and are accessible by
   keyboard and assistive technology without PySide6-dependent domain logic.

## Future opportunities

- Reviewed statement import, recurring-payment detection, promotional-deadline
  reminders, purchase-claim assistance and read-only regulated data feeds.
- Credit utilisation or repayment insights only under a separate non-advice,
  privacy-reviewed requirement.

## Out of scope

- Card use, payment initiation, credit applications, eligibility decisions,
  credit scoring, debt advice, claim submission or automatic cancellation.
- Treating rewards as guaranteed estate property or promising a statutory,
  chargeback or insurance outcome.
- UI design or implementation.

## Dependencies and traceability

- Requires [002](002-privacyAndSecurityModel.md) and [009](009-bankingModule.md);
  integrates with [008](008-documentImportFramework.md).
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
