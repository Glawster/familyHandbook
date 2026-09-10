# ADR-0012: Shared identity and aggregate ownership

- Status: accepted
- Date: 2026-09-01
- Related requirements: [008](../requirements/features/008-documentImportFramework.md), [009](../requirements/features/009-bankingModule.md), 010–018

## Context

Prototype records use names and slugs as identifiers. That makes renaming risky
and gives no enforceable Clann or module boundary.

## Decision

Every implemented aggregate has a stable opaque ID, its owning Clann, aggregate
type and one owner module. IDs do not encode type and are never account numbers,
names, filenames or slugs. Cross-module relationships use typed references and
must remain within one Clann. Only the owner changes an aggregate; other modules
use its public service and may publish references or dependency edges.

Lifecycle is explicit (`active`, `historic`, `superseded`, `tombstoned`). A
tombstone retains identity and reason so references and history remain
explainable. Prototype slug IDs remain readable during migration but are not
allocated to new shared-domain records.

## Consequences

- Renames and storage moves do not change identity.
- References validate Clann scope and type independently of storage.
- Cross-aggregate workflows use explicit atomic change sets, not object cascades.
- Aggregate ownership is recorded in code, persistence metadata and the plan's ownership matrix.
