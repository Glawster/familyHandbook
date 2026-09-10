# 018: Utilities and essential household services

Priority: high  
Owner: project maintainers

## Status

InProgress

## Outcome

As a household member or authorised representative, I need to identify essential
utility services, premises, meters, account responsibility, support needs and
payments so that heat, power, water and communications can continue safely
during emergency, incapacity, bereavement or a move.

## Context

Utilities are operational services tied to premises and people, not merely
subscriptions. Supply, network, meter, landlord, billing and payment parties may
differ. Loss of service can create immediate health and safety risk, especially
for people using medical equipment or needing accessible support.

## Scope and information priorities

Support electricity, gas, water/wastewater, heating oil/LPG/district heat,
telephone, broadband, mobile, television licence, council/local services, waste,
septic/private water and other essential premises services. Home maintenance and
optional media remain linked Subscription records.

**Mandatory:** utility type/purpose, premises, supplier/provider, account holder,
status, payment relationship, essentiality, classification and review date.

**Recommended:** network/operator and emergency contact, masked account
reference, tariff/contract and end date, billing frequency/method, meter/fuel
type and safe identifier, reading/date, supply identifiers where justified,
responsible residents, Priority Services/support status, nominated contact,
medical/care dependency, arrears/support, equipment, move/death/incapacity
actions and verified contact date.

**Optional:** full customer/supply identifier, meter serial/location, readings,
usage and bill evidence, landlord responsibility, smart-meter/export details,
access instructions and maintenance contacts.

**Never store:** provider credentials, prepayment top-up secrets, property alarm
or key-safe codes, payment-card secrets, Wi-Fi passwords or support-service
identity passwords used to authenticate visiting staff.

## Functional requirements

### UT-1: Service, premises and parties

- Distinguish supplier, network/distribution operator, meter operator, billing
  agent, landlord, account holder, payer, resident, nominated contact and
  authorised representative.
- Link service to a Property/premises and effective occupancy period; a person
  moving does not necessarily end supply.
- Model supply, account, tariff/contract, meter/equipment and payment separately.
- Support shared/communal supply, landlord-included service, prepayment, smart
  meter, export generation, private supply and multiple meters/fuels.
- Supply identifiers and exact equipment locations are Confidential by default
  and included only for a clear continuity purpose.

### UT-2: Billing, readings and support

- Every reading, charge, balance and usage observation requires date, unit,
  source and actual/estimated status.
- Link Direct Debit or other payment through Banking; stopping it leaves the
  service/account obligation open.
- Track arrears, repayment/support plan, complaint, outage, safety issue and
  compensation claim without giving debt or engineering advice.
- Record accessibility/vulnerability needs, consent, duration, nominated
  contact and supplier/network registration separately.
- For UK energy, the Priority Services Register can support temporary or
  enduring needs, including bereavement and hospital recovery, and supplier and
  network registers may both matter: [Ofgem guidance](https://www.ofgem.gov.uk/information-consumers/energy-advice-households/join-your-suppliers-priority-services-register).
- Sensitive health/support detail must be minimised to the functional need and
  re-reviewed; the report should say what help is requested, not unnecessary
  diagnosis.

### UT-3: Continuity workflows

- **Immediate outage/emergency:** prioritise safety and official emergency
  services/operator contacts, medically dependent equipment, alternate heat/
  power/communication and incident reference; Eolas does not provide technical
  repair instructions.
- **Hospital/incapacity:** preserve supply/payment, verify representative or
  nominated-contact authority, update temporary support needs and arrange safe
  meter/top-up access through the provider.
- **Death:** identify services in the deceased's name, keep essential premises
  supplied, notify providers separately from Tell Us Once, change responsible
  party/payment, obtain final/interim readings and settle/transfer only with
  authority. GOV.UK lists utilities among private organisations requiring
  separate contact: [Tell Us Once](https://www.gov.uk/after-a-death/organisations-you-need-to-contact-and-tell-us-once).
- **Move:** record responsibility/end dates, readings/evidence, forwarding
  contact, equipment return, old/new supplier, support-register re-enrolment and
  final-bill status; avoid closing supply prematurely.
- **Supplier failure/switch:** preserve bills/readings, verify official successor
  information and reconcile balances without assuming tariff or credit outcome.
- **Seasonal/fuel:** track fuel level/delivery dependency and weather-related
  review for non-network heating without predicting consumption.

## Reports

- Utility and Premises Summary; Emergency Utility Sheet; Meter/Reading Register;
  Essential Service and Medical Dependency Checklist; Priority Support Register;
  Moving-Home Handover; Bereavement Utility Checklist; Billing/Payment Register.

Emergency reports must minimise account/health data while retaining verified
operator contact, premises, supply type and immediate dependency.

## Data and validation requirements

Models must include `UtilityService`, `UtilityAccount`, `ServiceParty`,
`SupplyPoint`, `MeterOrEquipment`, `ReadingObservation`, `UtilitySupportNeed`,
`OutageOrIncident` and links to Property, Person, Banking, Subscription,
Authority and evidence.

1. Service requires type, premises, supplier/responsibility, account holder,
   status, essentiality, classification and review date.
2. Supplier and network operator cannot be substituted for one another.
3. Reading requires date, unit, meter/supply and actual/estimated/source status.
4. Account closure is blocked while occupancy, final reading/bill, equipment,
   payment or ongoing essential supply is unresolved.
5. Support registration requires organisation, consent/authority, need, status
   and review date; switching triggers re-verification.
6. Payment cancellation cannot mark service ended.

## Acceptance criteria

1. Fictional electricity, gas, water, broadband, mobile, heating-oil and
   landlord-included services preserve supplier, operator, premises, account
   holder, payer and resident roles.
2. A power-dependent medical need produces a minimised emergency/support record
   and both supplier/network review without storing unnecessary diagnosis.
3. Death workflow keeps occupied-premises essentials visible, requires separate
   provider contact and does not close services merely because payment belonged
   to the deceased.
4. Moving-home workflow records dated readings, responsibility, final bill,
   equipment and support re-registration before closure readiness.
5. Stopping a Direct Debit leaves the utility obligation open and identifies
   payment/provider follow-up.
6. Credentials, property access/alarm codes and support authentication passwords
   are rejected; emergency and normal reports are accessible, local and offline.

## Future opportunities

- Bill import, explainable tariff/deadline extraction, meter-reading reminders,
  outage-data links, consumption insights and provider-supported moves under
  separate privacy and safety requirements.

## Out of scope

- Switching, tariff recommendation, energy/debt advice, payment, meter control,
  outage prediction, emergency dispatch, engineering or automated notification.
- UI design or implementation.

## Dependencies and traceability

- Requires [002](002-privacyAndSecurityModel.md), [009](009-bankingModule.md)
  and Property/Household concepts; related to 015 and 017; integrates with
  [008](008-documentImportFramework.md).
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
