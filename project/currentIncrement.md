# Current increment

## Increment

Shared Domain Foundation, Phases 0 and 1.

## Branch

`feature/shared-domain-foundation`

## Objective

Complete the Phase 0 architecture decisions and Phase 1 shared knowledge kernel
described by the
[financial domain implementation plan](financialDomainImplementationPlan.md).

## Scope

- Establish the architecture boundaries and decisions needed by requirements
  [008 through 018](requirements/requirementsIndex.md).
- Implement the shared identity, ownership, classification, provenance,
  evidence, authority, temporal-value and persistence foundations.
- Provide the shared continuity-dependency graph contract required by later
  domain modules, without adding Banking-owned semantics.
- Keep the kernel independent of user-interface, network and Banking concerns.

## Explicit exclusion

Phase 2 Banking implementation is outside this increment. No Banking
aggregates, Banking edge semantics or Banking workflows are included.

## Expected exit criteria

- Phase 0 decisions are recorded in accepted ADRs and linked from the source
  plan.
- Phase 1 shared-kernel contracts are implemented in the project package with
  no dependency on UI frameworks or network services.
- Automated tests cover identity and Clann isolation, fact states,
  classification, prohibited secrets, provenance and evidence, temporal money,
  authority, graph traversal, persistence history, optimistic concurrency,
  atomic changes and migration.
- The fictional conformance fixture demonstrates multiple households and a
  cross-domain dependency chain without introducing Banking implementation.
- The [domain conformance checklist](domainConformanceChecklist.md) traces the
  shared foundation to requirements 008–018 and keeps later domain work
  explicitly deferred.
- `pytest` passes.
- `manageProject --check` reports zero failures and zero warnings.

## Immediate next action

Complete the Phase 2 entry review in the domain conformance checklist, close
this increment, and record any Banking work as a separate increment.
