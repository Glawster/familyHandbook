# 017: Subscriptions and recurring services

Priority: medium  
Owner: project maintainers

## Status

InProgress

## Outcome

As a household member or authorised representative, I need to identify recurring
services, users, contracts and payment authorities so that essential services
continue and unwanted costs can be reviewed lawfully after a life event.

## Context

Subscriptions may be contractual, month-to-month, free trials, memberships,
licences, donations or app-store bundles. The purchaser, account owner, users,
beneficiary and payer may differ. Stopping payment does not necessarily cancel
the contract, and using a deceased person's login can be unauthorised.

## Scope and information priorities

Support digital/media, software/cloud, telecom add-ons, clubs/gyms, publications,
food/retail, maintenance, security/monitoring, professional memberships,
charitable recurring payments, app-store and other recurring services. Core
electricity, gas, water, telecom and council services belong to Utilities.

**Mandatory:** service/provider, purpose, service category, contract/account
owner, primary beneficiary/users, status, payment mechanism/source,
essentiality, classification and review date.

**Recommended:** masked customer reference, start/renewal/end date, term and
notice/cancellation source, trial/discount end, amount/currency/frequency/date,
contract link, additional users, device/data dependencies, transferable content
or licence status, contact/cancellation route and event actions.

**Optional:** full reference, account email/username if not authentication-
sensitive, order history, loyalty balance, safe export/location reference and
reason for retention.

**Never store:** password, recovery code, MFA secret, security answer, session
token, full card details or instructions to impersonate the account owner.

## Functional requirements

### SB-1: Service, contract and people

- Distinguish provider, billing intermediary/app store, contract owner, payer,
  administrator, invited user, household beneficiary and authorised
  representative.
- Model service entitlement and underlying contract separately from its Direct
  Debit, standing order, recurring card payment or Variable Recurring Payment.
- Record term, renewal, minimum commitment, notice/cancellation method and data/
  content consequences as dated provider evidence, not guaranteed interpretation.
- Support bundles and dependencies: cancelling a parent service must list child
  services, stored data, devices, domains, monitoring and household workflows.
- Record essentiality by event: medical/care, home security, communications and
  work services may need continuity before review.

### SB-2: Discovery, review and lifecycle

- Link statement-detected candidates through the Document Import Framework;
  repeated transactions are evidence, not proof of a subscription.
- Track trial, active, paused, cancellation requested, ending, cancelled,
  expired, disputed and unknown states with evidence.
- Renewal and price observations require date/source; variable usage must not be
  mislabelled a fixed subscription.
- Cancellation action requires authorised actor, channel, confirmation,
  effective date, final charge/refund and data/asset disposition.
- Stopping a payment mandate leaves contract status unresolved. Current
  [MoneyHelper payment guidance](https://www.moneyhelper.org.uk/en/everyday-money/banking/direct-debits-and-standing-orders.html)
  explicitly distinguishes payment cancellation from contract cancellation.

### SB-3: Continuity workflows

- **Preparation:** identify essential/shared services, ownership, payer,
  renewal, export/recovery arrangements and safe contact routes.
- **Hospital/incapacity:** preserve essential services, verify representative
  authority and use provider-supported delegation rather than shared credentials.
- **Death:** inventory services from records/statements, preserve essential home
  and digital assets, notify provider through bereavement/contract route, review
  transfer/cancellation, data and final charges; never use the deceased's login.
- **Move/separation:** identify location/person-dependent services, port/transfer
  needs, shared data, equipment return and liability.
- **Provider failure:** preserve invoices/content/export evidence and payment
  disputes without promising recovery.

## Reports

- Subscription Register; Renewal/Trial Calendar; Essential Services Checklist;
  Shared User and Data Dependency Map; Payment Authority Register; Bereavement
  and Moving-Home Subscription Checklist.

## Data and validation requirements

Models must include `Subscription`, `ServiceParty`, `ServiceEntitlement`,
`SubscriptionTerm`, `RenewalObservation`, `CancellationAction` and links to
Banking MoneyMovement, Person, Household, Device, DigitalAsset and evidence.

1. Subscription requires provider/service, purpose, owner, beneficiary,
   essentiality, payment relation, status, classification and review date.
2. Payment stop cannot set contract `cancelled`.
3. Renewal/price requires date/source and exact/estimated type.
4. Account owner, payer and user cannot be inferred from one another.
5. Cancellation cannot complete without provider confirmation or an explicit
   unconfirmed end state.
6. Credential-shaped values block storage and logging.

## Acceptance criteria

1. Fictional app-store bundle, gym contract, shared cloud plan, charity payment
   and home alarm service preserve owner, payer, users and intermediary.
2. Cancelling a recurring card authority leaves the service contract open and
   lists provider follow-up.
3. A death checklist prioritises home alarm/shared data before entertainment and
   never instructs credential use.
4. A cancellation records notice source, actor, confirmation, effective date,
   final charge and equipment/data consequences.
5. Statement detection remains a candidate until user confirmation and can be
   rejected without creating a subscription.
6. Reports are local, accessible and offline, mask references and contain no
   credentials or card secrets.

## Future opportunities

- Explainable recurring-payment detection, renewal/price reminders, provider-
  supported cancellation links and data-export planning under separate approval.

## Out of scope

- Automated cancellation, provider login, purchasing, price comparison,
  recommendation, contract interpretation or guaranteed refund.
- UI design or implementation.

## Dependencies and traceability

- Requires [002](002-privacyAndSecurityModel.md) and [009](009-bankingModule.md);
  related to 010, 015 and 018; integrates with [008](008-documentImportFramework.md).
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
