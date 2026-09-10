# 012: Loans and other borrowing

Priority: high  
Owner: project maintainers

## Status

InProgress

## Outcome

As a borrower, guarantor or authorised representative, I need to identify loans,
liability, security and repayment commitments so that debts are not missed,
wrongly assumed or paid by an unauthorised person during disruption or estate
administration.

## Context

Loans range from family agreements to regulated personal, vehicle, student,
business, hire-purchase and secured lending. Borrower, co-borrower, guarantor,
owner of security and user of an asset may differ. Eolas must explain the
relationship and evidence, not calculate advice or assume a relative inherits a
sole debt.

## Scope and information priorities

Support personal, joint, guarantor, family/private, employee, student, business,
director, hire-purchase, conditional-sale, lease/PCP-style finance, payday,
credit-union, secured and consolidation loans. Mortgages and credit cards remain
separate linked modules.

**Mandatory:** lender/creditor, loan type and purpose, borrowers, joint/several
liability status where known, security/asset link, status, currency,
classification and review date.

**Recommended:** masked agreement reference, guarantors, original and dated
outstanding amount, repayment account/amount/frequency, term/maturity, interest
and fee basis reference, balloon/final payment, arrears/support, early-settlement
route, insurance, authority, evidence and event actions.

**Optional:** full agreement reference, statements, settlement quotations,
credit-agreement copy, private-loan terms and witness/professional references.

**Never store:** lender credentials, payment secrets or identity-verification
answers.

## Functional requirements

### LN-1: Parties, liability and security

- Distinguish creditor, servicer, debt purchaser and collector with assignment
  evidence and dates.
- Record borrower, co-borrower, guarantor, indemnifier and security owner as
  separate roles; family relationship never implies liability.
- Record secured asset, charge/security type, priority and release status
  without making a legal-validity conclusion.
- Preserve private/family loan evidence, amount advanced, repayments, interest,
  gift/loan character and parties' stated terms; ambiguity must be explicit.
- Link financed asset ownership and use separately from borrowing liability.

### LN-2: Terms, repayment and difficulty

- Financial observations require currency, effective date and source.
- Model fixed/variable interest basis, repayment schedule, term, deferred,
  balloon/final and early-settlement terms as dated evidence.
- Link repayment instructions through Banking and keep them separate from debt.
- Track arrears/default, collection, court/insolvency status, support plan,
  breathing-space reference, dispute and complaint without giving debt advice.
- A guarantor obligation must record scope and evidence. Current guidance notes
  a guarantor may remain liable when the borrower does not pay: [MoneyHelper
  guarantor guidance](https://www.moneyhelper.org.uk/en/everyday-money/credit/guarantor-loans-explained).
- Financial difficulty must direct the user to the creditor and free authorised
  debt advice; no automated prioritisation or settlement recommendation.

### LN-3: Continuity workflows

- **Temporary disruption/incapacity:** identify next payments, authority,
  support route, secured-asset risk and separately authorised representative.
- **Death:** inventory debts, notify creditor, obtain date-of-death balance and
  security, identify joint borrower/guarantor/estate liability and insurance,
  preserve creditor claims and avoid distribution or repayment conclusions.
- **Relationship/business change:** review joint/several liability, guarantees,
  asset use and creditor-approved release; a private agreement between people
  does not itself release a borrower.
- **Final payment/settlement:** obtain dated quotation, confirm payment and
  security release, retain closure evidence.
- The executor guide must distinguish sole, joint, guaranteed, secured,
  disputed and insolvent-estate debts. See [MoneyHelper debt-after-death
  guidance](https://www.moneyhelper.org.uk/en/family-and-care/death-and-bereavement/dealing-with-the-debts-of-someone-who-has-died.html).

## Reports

- Borrowing Summary; Repayment and Maturity Register; Guarantee Exposure
  Register; Secured Asset Dependencies; Estate Debt Checklist.
- Reports show dated balances and status, mask references, flag disputes and
  never state that a non-borrower owes a debt without evidence.

## Data and validation requirements

Models must include `LoanFacility`, `LoanParty`, `LoanTermObservation`,
`SecurityInterest`, `Guarantee`, `RepaymentPlan` and links to Banking, Asset,
Property, Insurance, Authority and evidence.

1. A loan requires creditor, type, purpose, borrower, security status,
   classification and review date.
2. Borrower, guarantor, asset owner and user cannot be inferred from each other.
3. Outstanding amount, repayment and rate require date/source; estimates are
   labelled.
4. A stopped payment leaves the debt open.
5. Debt assignment requires source; unverified collection contact cannot replace
   the recorded legal creditor.
6. Closure requires zero/settled evidence and security-release review.

## Acceptance criteria

1. Fictional sole, joint, guaranteed, secured, vehicle-finance and family loans
   preserve distinct liability and security roles.
2. Death of a sole borrower produces an estate review and does not assign debt
   to relatives; a co-borrower and guarantor remain separately flagged from
   documented terms.
3. A missed repayment shows creditor/support and secured-asset consequences but
   offers no automated payment priority or advice.
4. A debt-sale notice preserves old/new parties and remains unverified until
   evidence is confirmed; message-supplied payment details are not trusted.
5. Settlement keeps the record open until balance and security release are
   evidenced.
6. All reports work offline, meet accessibility requirements, mask identifiers
   and exclude credentials from storage and logs.

## Future opportunities

- Statement import, payment/maturity reminders, reviewed agreement extraction
  and debt-advice referrals under separate requirements.

## Out of scope

- Lending, credit scoring, affordability, debt counselling, insolvency advice,
  settlement negotiation, payment or legal enforceability decisions.
- UI design or implementation.

## Dependencies and traceability

- Requires [002](002-privacyAndSecurityModel.md) and [009](009-bankingModule.md);
  related to 010, 011, 015 and 016.
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
