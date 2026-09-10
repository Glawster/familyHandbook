# ADR-0017: Module and plugin boundaries

- Status: accepted
- Date: 2026-09-01
- Related requirements: [008](../requirements/features/008-documentImportFramework.md), 009–018

## Context

Financial modules and future import plugins need shared concepts without
becoming one generic record model or writing each other's persistence shapes.

## Decision

The shared kernel owns cross-cutting values and shared party, authority,
evidence-reference, action and dependency contracts. Each domain module owns
its aggregates and dependency-type semantics. Modules communicate through typed
references, validated commands and public services. They never write another
module's aggregate directly.

Import plugins own import attempts and candidates only. They submit proposed
commands to the target module; they cannot commit facts or mutate evidence.
Graph traversal belongs to the shared graph service while source modules
publish explained edges. Domain and plugin code is UI-independent; CLI, curses,
Qt, reports and storage are adapters or projections.

## Consequences

- Banking can become a financial relationship core without owning pensions,
  utilities or their obligations.
- Cancelling a payment cannot implicitly cancel a contract in another module.
- Plugins can be isolated and permissioned without changing domain objects.
