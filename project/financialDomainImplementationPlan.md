# Financial domain implementation plan and model proposal

Status: Phase 0 and Phase 1 implemented
Date: 2026-07-31  
Owner: project maintainers

## Purpose

This document proposes how Eolas can implement the financial and household-
continuity requirements in phases without creating separate, incompatible data
models for each module. It covers requirements
[008](requirements/features/008-documentImportFramework.md) through
[018](requirements/features/018-utilities.md).

It is a planning and design proposal, not an accepted architecture decision,
database schema, API contract or implementation specification. Significant
choices identified here require ADR approval before code fixes them into the
application.

Phase 0 decisions were accepted on 2026-09-01 in ADRs 0012–0017. Phase 1 is
implemented in `eolas.domain`; Phase 2 Banking remains unimplemented. The graph
foundation was brought forward from Phase 2 because all later domains need its
Clann isolation and traversal contract, but no Banking edge semantics or
aggregates were added.

## Goals

- Identify the smallest useful set of shared entities and value concepts.
- Give each module clear ownership of its canonical records and rules.
- Make cross-module continuity dependencies explicit and traversable.
- Keep private-data, evidence, audit and guidance policies consistent.
- Sequence delivery so each phase produces testable domain capability.
- Keep domain logic independent of PySide6, storage technology and reports.
- Let document importers propose changes without owning domain records.
- Avoid a generic financial super-record that loses important distinctions.

## Design constraints

The proposal must preserve these accepted decisions:

1. **Knowledge before documents.** Domain records represent household knowledge;
   statements, policies, reports and screens are evidence or projections.
2. **One shared model, many projections.** A report selects canonical knowledge;
   it does not maintain a second copy.
3. **Offline and local first.** Core use cannot require a network or hosted
   account.
4. **Privacy by default.** Classification, minimisation, safe references and
   prohibited-secret validation apply throughout the model.
5. **Explicit authority.** Relationship, ownership, access and authority are
   distinct.
6. **Temporal truth.** Balances, values, rates, terms, guidance and statuses are
   observations with dates and sources, not timeless attributes.
7. **Module ownership.** One module owns each canonical record. Other modules
   refer to it by stable ID and typed relationship.

## Proposed architecture

The domain should be organised into four layers of responsibility:

```text
Shared knowledge kernel
    Household, Party, Organisation, Property, Asset, authority,
    classification, provenance, review, action and temporal observations
        |
        v
Financial relationship core
    Institution, account, money movement, payment arrangement,
    payment instrument and continuity dependency graph
        |
        v
Domain modules
    Credit, mortgage, loan, investment, pension, insurance,
    taxation, subscription and utility aggregates
        |
        v
Adapters and projections
    Storage, document import, guidance packages, reports and Qt workflows
```

Dependencies point downward. The shared kernel must not import a financial
module. Domain modules may depend on shared contracts and reference each other
through stable IDs and declared relationships, but they must not write another
module's aggregate directly.

## Shared knowledge kernel

### Existing concepts to retain

The proposal retains the conceptual entities already described by the shared
[domain model](../documentation/domainModel.md):

- **Clann:** private planning boundary and authorisation scope.
- **Household:** practical living and continuity context within a Clann.
- **Person:** individual whose life or responsibility is represented.
- **Contact:** person or organisation contact not otherwise represented as a
  Clann Person.
- **Property:** premises or place-related responsibility.
- **Asset:** thing of practical or financial value.
- **Document:** safe reference to evidence or authority that exists elsewhere.
- **Account:** relationship with an organisation, never a credential container.
- **Instruction, Wish and Review:** practical guidance, preference and evidence
  of review.

The current conceptual `Account` is deliberately broad. Implementation should
introduce typed domain relationships beneath it rather than put every banking,
tax, pension and utility field on one account table or class.

### Proposed shared entities

| Entity | Responsibility | Important boundary |
| --- | --- | --- |
| `Organisation` | Legal entity, public body, provider, employer, trust or business identity | Trading brands and service contacts are separate relationships |
| `OrganisationBrand` | Familiar or trading identity associated with an Organisation | Never used as legal identity without evidence |
| `OrganisationRole` | Provider role in a domain, such as lender, insurer, scheme administrator or utility operator | Domain module defines permitted role types |
| `PartyRole` | Typed, dated role held by a Person, Contact or Organisation in relation to a record | Role does not imply authority or ownership |
| `Authority` | Evidence that one party may act for another within a scope | Jurisdiction, activation, restrictions and registration are mandatory concepts |
| `AuthorityRegistration` | Recognition of an Authority by a specific provider | Legal evidence and provider readiness remain distinct |
| `Identifier` | Typed external reference with masked display and protected value where allowed | Never a canonical entity ID or credential |
| `EvidenceReference` | Link to a Document or retained evidence object plus locator and purpose | Evidence does not become canonical knowledge automatically |
| `Provenance` | Source, actor/import attempt, time and derivation of a fact | Required for consequential or imported facts |
| `ReviewState` | Last review, next date/trigger, responsible role and open findings | Reusable composition rather than duplicated date fields |
| `ContinuityAction` | Event-specific task, authority, responsible role, state, evidence and outcome | Guidance suggestion and completed action remain distinct |
| `GuidanceReference` | Jurisdiction package, version/effective date and source used for an action | Mutable rules do not become hard-coded domain facts |
| `ContinuityDependency` | Typed directed graph edge between canonical entities | Graph service owns traversal; modules own edge semantics they publish |
| `Interaction` | Dated contact with a provider/authority, request, evidence shared, outcome and follow-up | Must contain privacy-safe summaries by default |

### Shared value concepts

These should be immutable, typed values or embedded concepts rather than
independently managed entities unless later evidence justifies otherwise:

- `RecordIdentity`: opaque stable ID plus Clann ownership.
- `RecordLifecycle`: active, historic, superseded or deleted/tombstoned state.
- `Classification`: `public`, `private`, `confidential` or
  `highlyConfidential`, including field-level override.
- `TemporalRange`: start/end with known/estimated precision.
- `Money`: decimal amount and ISO currency; never a binary floating-point value.
- `Observation`: value, `asOf`, source, confidence and observed/estimated/
  provider-confirmed status.
- `PercentageOrRate`: value, basis, period and effective range.
- `MaskedValue`: safe display plus separately protected original where permitted.
- `Jurisdiction`: versioned stable identifier, not a display string.
- `ContactRoute`: channel, purpose, source, verified date and accessibility.
- `LocationReference`: proportionate description rather than an access secret.
- `Schedule`: frequency, timing, variability and known next/last occurrence.
- `ValidationFinding`: stable code, severity, affected fact and safe explanation.

### Cross-cutting policies

Every information-bearing aggregate must support:

- Clann ownership and cross-Clann isolation;
- stable opaque identity and schema version;
- record and field classification;
- created/changed actor context and timestamps;
- provenance and evidence references where applicable;
- review state and staleness;
- append-only history for consequential changes;
- explicit `unknown`, `notApplicable` and absent states;
- prohibited-secret validation; and
- transactional create/update with expected-version conflict detection.

These policies should be supplied by shared domain services or compositions.
They should not be independently reimplemented in every module.

## Financial relationship core

The Banking module provides the shared financial relationship core because
accounts, institutions, payments and dependencies are reused by every other
financial module.

### Canonical banking entities

| Entity | Owned knowledge |
| --- | --- |
| `FinancialInstitution` | Organisation link, institution type, jurisdiction, legal entity/brand and dated protection-group references |
| `BankingRelationship` | Deposit/payment account type, purpose, status, currency and service context |
| `AccountParty` | Holder, beneficial owner, trustee, signatory or responsible party with dates/evidence |
| `AccountContinuityRole` | Typed role such as primary operating account, salary receipt or emergency reserve |
| `MoneyMovement` | Incoming/outgoing relationship, source/destination, purpose, mechanism and schedule |
| `PaymentArrangement` | Direct Debit, standing order, recurring card authority or payment permission and its lifecycle |
| `PaymentInstrument` | Debit, cash, prepaid or linked credit-card instrument identity and lifecycle |
| `BalanceObservation` | Dated account balance or overdraft observation |
| `BankingEquipment` | Passbook, cheque book, card reader or token reference without secrets |

`MoneyMovement` represents an expected or material flow, not a complete ledger
transaction. Transaction-level storage remains outside the initial scope.

### Continuity dependency graph

`ContinuityDependency` must be a shared graph whose nodes are canonical domain
record IDs. Initial edge types should include:

| Edge | Example |
| --- | --- |
| `paidInto` | Pension income → current account |
| `funds` | Current account → mortgage payment |
| `paidBy` | Insurance premium → Direct Debit |
| `dependsOn` | Home alarm service → broadband |
| `linkedTo` | Offset account → mortgage facility |
| `secures` | Property → mortgage facility |
| `covers` | Home policy → property |
| `usedBy` | Debit card → person |
| `administeredUnder` | Banking relationship → authority registration |
| `supportedBy` | Canonical fact → evidence reference |

Each module publishes edges for records it owns. The graph service validates
endpoints, dates and Clann scope and provides forward/reverse traversal,
cycle-safe path explanation and event impact analysis. It must not own or mutate
the referenced aggregates.

## Module boundaries

### Ownership matrix

| Module | Owns | References but does not own |
| --- | --- | --- |
| Banking (009) | Institutions, deposit/payment accounts, account parties, debit/prepaid instruments, money movements, payment arrangements and account continuity | Credit liability, mortgages, subscriptions, utilities and incoming product entitlements |
| Credit cards (010) | Revolving facility, borrowers, credit terms/balance, repayment obligation, card purchase and claim | Financial institution, payment account, card instrument presentation and recurring payment |
| Mortgages (011) | Mortgage facility/parts, borrower liability, repayment strategy and property security | Property, payment account, insurance, investment/endowment and valuation evidence |
| Loans (012) | Loan facility, borrowers, guarantee, security interest, terms and repayment plan | Asset/property, payment account and insurance |
| Investments (013) | Portfolio, holding, custody, investment parties, restrictions and valuation | Institution, banking income/cash, tax evidence, trust and adviser |
| Pensions (014) | Arrangement, scheme, benefit entitlement, nomination, value and pension income | Employer, banking receipt, tax rules, insurance and trust |
| Insurance (015) | Policy, policy parties, insured subject, coverage, premium and claim | Person/property/asset/debt/pension, payment arrangement and evidence |
| Taxation (016) | Tax relationship, period, obligation, amount status, deadline and agent authority | Income, asset, estate, trust, payment and evidence from all modules |
| Subscriptions (017) | Service contract, entitlement, parties, term, renewal and cancellation | Payment arrangement, user/device/digital asset and utility dependency |
| Utilities (018) | Utility service/account, supply point, meter, reading, support need and incident | Property, residents, payment arrangement, subscription and authority |
| Document import (008) | Evidence, import job/attempt, candidates, decisions and provenance | Every target module's public commit contract |

### Important shared boundaries

#### Credit cards

Banking owns the payment instrument and its funding relationships. Credit Cards
owns the revolving liability facility, balance, interest and settlement. A
card-instrument record links to exactly one facility without copying the
facility's financial terms.

#### Payment versus obligation

Banking owns a payment arrangement. The target module owns the contract,
premium, mortgage, loan, tax or service obligation. Cancelling the arrangement
must never mark the obligation cancelled or settled.

#### Organisation versus domain provider

The shared kernel owns Organisation identity, brand and contacts. A module owns
the provider's role in its aggregate. One Organisation can be a bank, lender,
insurer and pension administrator without four duplicated organisations.

#### Person role versus authority

A module owns role relationships such as borrower, insured person or pension
member. The shared kernel owns authority to act. Being a spouse, joint holder,
beneficiary or additional cardholder does not create Authority.

#### Evidence versus canonical facts

The import/evidence services own original bytes, checksums, extraction attempts
and candidate provenance. A module owns only user-confirmed facts committed
through its public domain service.

#### Guidance versus workflow state

Documentation packages own mutable jurisdiction guidance. The shared action
model stores the guidance ID/version used, the selected action and its result.
It does not copy an external rule into every domain record.

## Aggregate and transaction proposal

An aggregate is the smallest consistency boundary that can enforce its own
invariants. Proposed initial aggregate roots are:

- Household and Person in the shared Clann domain;
- Organisation;
- Authority;
- BankingRelationship;
- PaymentArrangement;
- CreditFacility;
- MortgageFacility;
- LoanFacility;
- Portfolio;
- PensionArrangement;
- InsurancePolicy;
- TaxRelationship;
- Subscription; and
- UtilityService.

ContinuityDependency, EvidenceReference, ReviewState and interactions are
attached through services and stable IDs rather than expanding every aggregate
transaction. A workflow that changes several aggregates must first build a
serialisable proposed change set, validate expected versions and commit
atomically where the user expects one action. Cross-aggregate business processes
should use explicit orchestration rather than hidden object cascades.

## Public domain-service boundaries

No concrete interface syntax is proposed yet. Each module should nevertheless
offer equivalent responsibilities:

- create and revise an aggregate through validated commands;
- retrieve an aggregate and its permitted history by stable ID;
- search/match candidates without disclosing another Clann;
- produce a proposed change set for review;
- validate domain and cross-module references;
- publish dependency edges and impact facts;
- attach/detach evidence references without modifying evidence;
- create review findings and continuity actions;
- expose projection-ready read models; and
- migrate supported schema versions explicitly.

Qt views, report generators and import plugins call these services. They do not
write persistence models or reproduce validation rules.

## Phased implementation plan

### Phase 0: Decisions and conformance fixtures

**Objective:** approve the boundaries before creating production schemas.

Deliverables:

- ADR for shared entity identity, aggregate ownership and cross-module
  references;
- ADR for persistence, history, migrations and transaction boundaries;
- ADR for Organisation/Contact modelling;
- ADR for authority and provider-registration modelling;
- ADR for evidence encryption/key custody and plugin isolation;
- fictional `Morgan`-style cross-domain scenario covering two households,
  institutions, accounts, income, essential commitments, authority and death;
- glossary additions for observation, obligation, payment arrangement,
  continuity role and dependency; and
- [domain conformance checklist](domainConformanceChecklist.md) derived from
  requirements 008-018.

Exit gate:

- every proposed aggregate has one owner;
- every cross-module relationship has a direction and ownership rule;
- no fixture contains usable identifiers or secrets; and
- maintainers accept the ADRs needed for Phase 1.

### Phase 1: Shared knowledge kernel

**Objective:** establish reusable privacy, identity, temporal and evidence
concepts without financial behaviour.

Deliverables:

- stable Clann-scoped IDs and schema/version metadata;
- Classification, ReviewState, Provenance, EvidenceReference, Identifier,
  Observation, Money, Schedule and Jurisdiction concepts;
- Organisation, brand, contact route and PartyRole;
- Authority and AuthorityRegistration;
- ContinuityAction, GuidanceReference and Interaction;
- validation for unknown/not-applicable, prohibited secrets and cross-Clann
  references; and
- storage-adapter contract tests using temporary private roots.

Exit gate:

- kernel tests run without Qt or network;
- missing classification fails closed;
- history and expected-version conflicts are demonstrated; and
- every sensitive value has an explicit masking/export policy.

### Phase 2: Banking relationship core

**Objective:** deliver manual structured banking knowledge and the dependency
foundation required by other modules.

Deliverables:

- FinancialInstitution, BankingRelationship, AccountParty, Identifier and
  BalanceObservation;
- versioned AccountContinuityRole registry;
- MoneyMovement, PaymentArrangement, debit/prepaid PaymentInstrument and
  BankingEquipment;
- dependency graph storage, validation, forward/reverse traversal and impact
  explanation;
- manual create/review/close-readiness workflows; and
- Banking Summary and dependency report projections.

Exit gate:

- the acceptance scenarios in requirement 009 pass;
- the primary operating account and its upstream/downstream dependencies can be
  explained;
- account closure cannot silently orphan an essential dependency; and
- all capability remains local/offline and UI-independent.

### Phase 3: Household obligations and essential services

**Objective:** validate payment-versus-obligation and premises continuity with
Subscriptions and Utilities.

Deliverables:

- Subscription, ServiceEntitlement, term/renewal and cancellation action;
- UtilityService, UtilityAccount, SupplyPoint, meter/reading and support need;
- links from obligations to Banking payment arrangements and Property/Person;
- essential-service and move/bereavement continuity projections; and
- graph impact across broadband, alarms, power-dependent care and payments.

Exit gate:

- cancelling a payment never cancels a contract;
- changing an account shows every affected service;
- move and bereavement scenarios preserve essential supply; and
- sensitive support needs are demonstrably minimised.

### Phase 4: Credit and secured liabilities

**Objective:** add Credit Cards, Loans and Mortgages on one common liability
pattern while preserving their domain distinctions.

Deliverables:

- shared internal liability vocabulary for borrower, creditor, dated balance,
  repayment obligation, arrears/support and settlement status;
- CreditFacility linked to Banking card instruments;
- LoanFacility, Guarantee and SecurityInterest;
- MortgageFacility/parts, PropertySecurity and RepaymentStrategy;
- payment, asset/property, insurance and authority dependencies; and
- debt/repayment and housing-continuity projections.

Exit gate:

- borrower, cardholder, guarantor, owner and occupier are never inferred from
  one another;
- a stopped payment leaves liability open;
- death scenarios distinguish sole, joint, guaranteed and secured debt; and
- no module duplicates institution, account or property identity.

### Phase 5: Protection and claims

**Objective:** implement Insurance as the shared protection/claim domain.

Deliverables:

- InsurancePolicy, PolicyParty, InsuredSubject, coverage and premium;
- InsuranceClaim and evidence/request lifecycle;
- links to people, property, assets, debts, pensions and payments;
- renewal, emergency and bereavement projections; and
- field-level treatment of medical and claim evidence.

Exit gate:

- policyholder, insured, beneficiary and payer remain distinct;
- missed payment does not assert lapse;
- potential and accepted claims cannot be confused; and
- claim evidence follows retention/classification policy.

### Phase 6: Long-term assets and entitlements

**Objective:** add Investments and Pensions after custody, evidence and authority
contracts are proven.

Deliverables:

- Portfolio, Holding, CustodyArrangement, restrictions and dated valuation;
- PensionArrangement, Scheme, BenefitEntitlement, Nomination and pension income;
- title/beneficial owner/custodian distinctions;
- nomination/wish/discretion/entitlement distinctions;
- banking income, tax evidence, trust, employer and adviser relationships; and
- estate, attorney and nomination-review projections.

Exit gate:

- no stale value is presented as current;
- no expression of wish is represented as guaranteed entitlement;
- credentials and cryptographic recovery secrets are rejected; and
- transfers preserve source/destination history and reconciliation.

### Phase 7: Tax relationships and evidence

**Objective:** organise tax obligations after source domains can provide linked
evidence.

Deliverables:

- TaxRelationship, TaxPeriod, TaxObligation, amount/status and deadline;
- TaxAgentAuthority and links to shared Authority;
- evidence links from income, property, investment, pension, insurance, debt and
  estate records;
- versioned jurisdiction-rule inputs and retention actions; and
- tax evidence, deadline and estate-administration projections.

Exit gate:

- estimated, submitted, assessed, paid and refunded amounts remain distinct;
- a rule outside its effective period cannot drive an action;
- pre-death and estate-administration obligations are separable; and
- no calculation, filing or tax conclusion is implied.

### Phase 8: Document Import Framework

**Objective:** add extraction only after target domain commands and validation
are stable.

Deliverables:

- evidence store, import job/item lifecycle and processing attempts;
- PDF text/OCR, classification and review contracts;
- entity resolution against Organisation, Person and BankingRelationship;
- atomic proposed-change integration with domain services;
- bank-statement plugin as the first importer; and
- import history and provenance projections.

Exit gate:

- imported values cannot bypass domain validation or confirmation;
- original evidence is immutable and integrity checked;
- duplicate evidence and records are controlled; and
- all Phase 1 import scenarios operate offline.

Later document plugins should be sequenced by domain stability and user value,
not implemented inside this phase merely because the framework exists.

### Phase 9: Continuity projections and guided workflows

**Objective:** assemble cross-module knowledge into event-specific experiences.

Deliverables:

- household operating-account view;
- income/payment/service dependency map;
- emergency, hospitalisation, incapacity, bereavement and moving-home
  checklists;
- executor and attorney packs;
- classification-aware print/export; and
- guidance-package version selection with action provenance.

Exit gate:

- every projection traces to canonical records;
- no projection becomes an editable duplicate source;
- stale/unknown facts and guidance are visible; and
- print, keyboard and screen-reader acceptance scenarios pass.

### Phase 10: Hardening and extension readiness

**Objective:** prove production safety, portability and extension contracts.

Deliverables:

- cross-platform storage and recovery conformance;
- migration and backwards-compatibility suite;
- performance tests at requirement scales;
- threat-model closure, fuzzing and malicious-document tests;
- accessibility and privacy review;
- plugin authoring/conformance documentation; and
- backup, restore, export, redaction and deletion verification.

Exit gate:

- no unresolved critical/high security risk;
- recovery tests prove atomicity and audit continuity;
- required performance/accessibility targets pass on supported platforms; and
- a fictional second importer adds no core-domain modifications.

## Suggested delivery increments

Phases are architectural dependencies, not necessarily one release each. A
practical vertical sequence is:

1. **Banking inventory:** kernel plus manual accounts, parties and reviews.
2. **Household continuity:** operating role, income, essential payments and
   dependency traversal.
3. **Essential services:** utilities/subscriptions and move/emergency workflows.
4. **Liabilities:** credit cards, loans and mortgages with housing/debt views.
5. **Protection:** insurance policies and claims.
6. **Long-term planning:** investments and pensions.
7. **Administration:** taxation and executor evidence.
8. **Assisted entry:** bank-statement import after the Banking commit contract is
   stable.
9. **Full projections:** cross-domain packs, print and guided event workflows.

Each increment should include domain tests, storage/migration tests, one
accessible projection and a fictional end-to-end scenario. Avoid delivering a
large invisible model with no user-verifiable outcome.

## Migration and compatibility strategy

- Assign stable IDs before introducing cross-module links.
- Add schema versions at aggregate boundaries, not one global application
  version that forces unrelated records to migrate together.
- Migrations must be explicit, transactional and recorded, with a backup/recovery
  path before destructive transformation.
- Unknown enum/relationship values from a newer compatible source should be
  preserved but prevented from driving unsafe current behaviour.
- Replace duplicated organisations/accounts through reviewed merge proposals;
  never silently coalesce by name or masked identifier.
- Preserve imported evidence and provenance across domain migrations.
- Projection formats may change independently because they are derived.

## Test strategy by layer

| Layer | Required evidence |
| --- | --- |
| Shared values | Boundary, classification, masking, temporal precision and prohibited-secret tests |
| Aggregate | State transition, invariant, expected-version and history tests |
| Module contract | Public command/query conformance without Qt or real storage |
| Cross-module | Reference validity, ownership protection and no cascade mutation |
| Dependency graph | Forward/reverse paths, cycles, stale edges, event filters and cross-Clann denial |
| Persistence | Atomicity, migration, corruption, backup and recovery contract tests |
| Import | Candidate validation, duplicate evidence, provenance and atomic commit |
| Projection | Traceability, staleness, masking, accessibility, print and no duplicate source |
| Security | Malicious input, privilege boundary, log disclosure and export/deletion controls |

The primary conformance fixture should tell one coherent fictional household
story across modules. Smaller fixtures should isolate rules. No fixture may use
real institutions with realistic usable identifiers or private household data.

## Decisions required before implementation

The following should become ADRs or explicit maintained decisions:

1. Persistence format and aggregate transaction mechanism.
2. Stable ID format, Clann boundary enforcement and expected-version strategy.
3. Organisation, brand, Contact and Professional relationship.
4. Generic PartyRole/Identifier/Observation composition versus module-specific
   value types.
5. Authority scope language and jurisdiction extension mechanism.
6. Dependency graph storage, edge registry and query limits.
7. Append-only audit/history representation and privacy-aware correction.
8. Evidence encryption, key recovery, retention and deletion.
9. Plugin trust and isolation.
10. Guidance package format, signing/versioning and update governance.
11. Projection/read-model refresh and offline print/export format.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Generic model erases domain meaning | Keep module-owned aggregate types and typed roles/edges |
| Modules duplicate people, organisations or accounts | Shared IDs, ownership matrix and conformance tests |
| Cross-module transactions become fragile | Proposed change sets, expected versions and explicit orchestration |
| Guidance is mistaken for timeless fact | Separate versioned packages and GuidanceReference on actions |
| Graph becomes an unbounded knowledge dump | Registered edge types, purpose, dates, review and bounded traversal |
| Observation history becomes a ledger | Store only purpose-limited observations; transaction ledger remains out of scope |
| Import drives the schema | Stabilise manual domain contracts before importer mappings |
| Privacy controls vary by module | Shared classification, masking, export and prohibited-secret policies |
| Early UI shapes the model | Domain and projection tests precede Qt workflow implementation |
| Delivery takes too long before user value | Use vertical increments with one useful projection per increment |

## Definition of domain readiness

A module is ready for UI or importer implementation only when:

- its aggregate owner and public responsibilities are documented;
- every shared and cross-module concept has an ownership rule;
- unknown, stale, conflicting and not-applicable data behaviour is defined;
- classification, masking, provenance and history are specified;
- state transitions and destructive-action readiness rules are testable;
- its dependency edges and event impact are defined;
- fictional conformance scenarios pass at the domain-service level;
- storage migration/recovery behaviour is known; and
- no unresolved ADR blocks the module's trust or transaction boundary.

## Traceability

- Requirements: [008-018](requirements/requirementsIndex.md)
- Domain model: [shared conceptual model](../documentation/domainModel.md)
- Principles: [project principles](../documentation/principles.md)
- Keystone decision: [ADR-0007](adr/007-knowledgeBeforeDocuments.md)
- Projection decision: [ADR-0008](adr/008-handbookAsProjection.md)
- Phase 0 decisions: [ADRs 0012–0017](adr/adrIndex.md)
- Phase 0/1 review: [domain conformance checklist](domainConformanceChecklist.md)
- Banking guidance: [guidance index](../documentation/banking/bankingIndex.md)
- Implementation: Phase 0/1 shared kernel in `eolas/domain/`; typed capture
  adapter in `eolas/capture/`; Phase 2 and Document Import remain pending
- Tests: shared kernel, security, dependency graph, persistence and capture
  adapter conformance in `tests/`
- Pull request: pending

## Change history

- 2026-09-01: recorded completion of Phase 0/1 foundations and the deliberate
  early delivery of the generic dependency graph; Banking remains Phase 2.

- 2026-07-31: created from requirements 008-018 as a proposed phased plan and
  financial-domain model.
