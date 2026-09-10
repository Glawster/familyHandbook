# 015: Insurance

Priority: high  
Owner: project maintainers

## Status

InProgress

## Outcome

As a policyholder, insured person, beneficiary or authorised representative, I
need to identify insurance cover, obligations, claims and evidence so that
protection is not unintentionally lost and valid claims can be pursued during
an emergency, incapacity or bereavement.

## Context

Insurance connects policyholders, insured risks/lives, beneficiaries, premiums,
conditions, property and evidence. Cover may lapse, renew or depend on prompt
notification. Eolas must support continuity and claim preparation without
interpreting cover, underwriting, or promising a claim outcome.

## Scope and information priorities

Support life, term, whole-of-life, critical illness, income protection, health,
travel, home/buildings/contents, landlord/tenant, motor, pet, legal expenses,
breakdown, business/key-person, liability, accident, funeral and packaged
insurance, including group/employer cover and self-insurance references.

**Mandatory:** policy type/purpose, insurer and administrator, policyholder,
insured person/property/risk, status, jurisdiction, masked reference,
classification and review date.

**Recommended:** beneficiaries/trust, cover period and renewal, sum/limit and
currency as dated evidence, excess, premium/funding account, material
conditions/exclusions reference, named/additional insured people, broker,
claim/emergency contacts, evidence/document location, linked asset/debt,
authority, claims and event-specific actions.

**Optional:** full policy reference, schedule wording, valuation, no-claims
history, health/medical details strictly required for a purpose, safe key/item
location and professional advice.

**Never store:** insurer credentials, card security data, alarm/access codes,
medical portal credentials or identity-verification answers.

## Functional requirements

### IN-1: Policy, parties and cover

- Distinguish insurer/underwriter, brand, administrator, broker, employer/group
  sponsor, policyholder, premium payer, insured person, beneficiary, trustee,
  claimant and loss payee.
- Link insured subjects to Person, Property, Vehicle, Asset, Business, Mortgage,
  Loan, Travel or Pet records without copying them.
- Record policy period, renewal model, cover/limit/excess observations,
  endorsements, exclusions/conditions references and territorial scope with
  source/effective date.
- Distinguish named beneficiary, trust beneficiary, estate, nominated contact
  and insured person; none is inferred from another.
- Link overlapping/packaged/group policies and record which primary evidence
  controls; never conclude duplicate cover automatically.

### IN-2: Premiums, renewal and claims

- Link premiums to Banking and Subscriptions while preserving the policy
  obligation if a payment instruction stops.
- Track renewal/expiry, auto-renewal, cancellation, grace period and insurer-
  confirmed continuity as dated terms.
- A claim must record incident, claimant/authority, notification date, policy,
  claimed subject, evidence requested/supplied, insurer reference, status,
  decision, payment and complaint/appeal route.
- Potential claims and notification deadlines require source and verification;
  Eolas must not determine coverage or limitation periods.
- Health, disability, bereavement and vulnerability data must be minimised,
  field-classified and accessible only for the stated purpose.

### IN-3: Continuity workflows

- **Preparation:** inventory cover, beneficiaries/trusts, premiums, renewal,
  evidence, emergency contacts and gaps marked for professional review.
- **Emergency/incident:** protect life/property, contact emergency services where
  appropriate, mitigate further loss safely, notify insurer through verified
  route, preserve evidence and avoid admitting liability on Eolas's authority.
- **Incapacity:** verify representative authority and insurer registration;
  preserve premiums and claims, particularly health/income-protection cover.
- **Death:** identify life, employer, pension, mortgage, accident, travel and
  funeral cover; notify insurers separately where required, obtain claim
  requirements and preserve trust/beneficiary status. Tell Us Once does not
  generally notify private insurers: [GOV.UK guidance](https://www.gov.uk/after-a-death/organisations-you-need-to-contact-and-tell-us-once).
- **Move/change/disposal:** review risk address, occupancy, drivers, assets,
  beneficiaries, employment and linked debt before assuming cover continues.

## Reports

- Insurance Summary; Renewal and Premium Register; Insured Subject/Cover Map;
  Beneficiary and Trust Review; Emergency Insurance Pack; Claim Evidence
  Checklist; Bereavement Insurance Guide.

## Data and validation requirements

Models must include `InsurancePolicy`, `PolicyParty`, `InsuredSubject`,
`CoverageObservation`, `Premium`, `InsuranceClaim`, `ClaimEvidence` and links to
Banking, Property, Asset, Vehicle, Debt, Pension, Authority and documents.

1. Policy requires insurer, type/purpose, policyholder, insured subject, status,
   jurisdiction, classification and review date.
2. Cover, premium, excess and value require date/currency/source and must not be
   presented as a coverage conclusion.
3. Beneficiary, insured, policyholder and payer roles remain distinct.
4. Stopped premium payment leaves policy status `unknown` pending insurer
   confirmation; it cannot mark the policy cancelled or active.
5. Claim state is explicit and append-only; potential is not accepted.
6. Medical and claim evidence gets field-level classification and retention.

## Acceptance criteria

1. Fictional life-in-trust, employer death-in-service, home, motor, travel,
   income-protection and packaged policies preserve distinct parties and risks.
2. A missed premium creates urgent insurer/status review without asserting lapse
   or cancelling the underlying policy.
3. Death workflow finds private and workplace policies after Tell Us Once and
   preserves beneficiary/trust uncertainty pending insurer/trustee decision.
4. A claim records evidence requests, submissions and outcomes without Eolas
   promising cover or calculating settlement.
5. Moving home lists property, contents, vehicle, pet and service-linked cover
   for review before old records are closed.
6. Credentials and access/alarm codes are rejected; sensitive health data is
   minimised; all reports are masked, accessible, local and offline.

## Future opportunities

- Policy/renewal document import, coverage-map assistance, claim-pack export,
  reminders and regulated-provider data connections under separate approval.

## Out of scope

- Quotes, sales, underwriting, advice, coverage interpretation, claim decision,
  valuation, fraud assessment, emergency response or insurer notification.
- UI design or implementation.

## Dependencies and traceability

- Requires [002](002-privacyAndSecurityModel.md) and [009](009-bankingModule.md);
  related to 010-014, 017 and 018; integrates with [008](008-documentImportFramework.md).
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
