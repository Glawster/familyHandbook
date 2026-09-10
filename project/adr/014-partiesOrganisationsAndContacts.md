# ADR-0014: People, organisations and contacts

- Status: accepted
- Date: 2026-09-01
- Related requirements: 009–018

## Context

Providers recur across banking, pensions, insurance, utilities and taxation,
while prototype fields are free text. A familiar brand, legal entity, contact
route and person are not interchangeable.

## Decision

`Person` is a canonical represented individual. `Organisation` is a canonical
legal entity, public body, trust, business or provider. `OrganisationBrand` is
a dated familiar/trading identity linked to an Organisation and is not legal
identity without evidence. `Contact` is a lightweight external contact not yet
represented as a canonical Person or Organisation.

Contact routes are dated, sourced, purpose-specific and classified. Provider
roles are typed relationships whose vocabulary belongs to the publishing
module. A Contact is promoted when durable identity, multiple roles, authority,
evidence or cross-domain reuse requires a canonical Person or Organisation;
the old contact links to the canonical party rather than being silently copied.

## Consequences

- One organisation can hold several domain roles without duplication.
- Brands and provider contact details may change without changing legal identity.
- A role never implies ownership or authority.
