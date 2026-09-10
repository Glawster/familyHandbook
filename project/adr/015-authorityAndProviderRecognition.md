# ADR-0015: Authority and provider recognition

- Status: accepted
- Date: 2026-09-01
- Related requirements: [007](../requirements/features/007-legalDocumentCustodyAndAccess.md), 009–018

## Context

Ownership, family relationship, account role, legal authority and a provider's
operational recognition are distinct. Collapsing them could encourage an
unauthorised person to act.

## Decision

`Authority` records the actor, grantor/subject, authority type, jurisdiction,
activation conditions, dated scope, restrictions, expiry/revocation and linked
evidence. `AuthorityRegistration` separately records a provider's recognition,
its scope, restrictions, references, expiry/revocation and evidence.

Authority never follows merely from ownership or a `PartyRole`. Acting requires
an active Authority whose scope and conditions allow the action and, where the
provider requires it, an effective provider registration. The model is generic
for executors, attorneys, deputies, trustees, business signatories and future
authority types; modules do not create banking-specific authority concepts.

## Consequences

- Legal validity and operational readiness can disagree without corrupting either fact.
- Expired, revoked, dormant and restricted states fail closed.
- Evidence is referenced, not copied into the authority aggregate.
