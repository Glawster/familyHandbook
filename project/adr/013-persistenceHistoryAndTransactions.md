# ADR-0013: Persistence, history and transaction boundaries

- Status: accepted
- Date: 2026-09-01
- Related requirements: [008](../requirements/features/008-documentImportFramework.md), 009–018

## Context

The capture prototype writes YAML documents directly. Treating those documents
as the domain contract would bind validation, migration and concurrency to a
format selected for an early adapter.

## Decision

Domain services depend on a `RecordStore` port. A stored envelope carries Clann,
opaque identity, aggregate owner/type, schema name/version and record version.
Creates and updates are atomic; updates require an expected version and reject
conflicts. Multi-record user actions commit as one validated change set.

Consequential prior versions form append-only history. Current state is the
latest aggregate representation; observations and completed actions are dated
historical facts and are not overwritten into timeless fields. Migrations are
explicit ordered functions and unsupported versions fail closed.

YAML is the first local adapter, not the domain contract. Neither YAML, SQLite
nor a UI toolkit is required by the kernel. Encryption/key custody is an adapter
capability and must be established before that adapter persists protected
Highly Confidential values.

## Consequences

- Tests can use a temporary local store without network or UI.
- A future storage adapter must pass the same isolation, atomicity, history,
  conflict and migration contract.
- Storage technology can change without changing aggregates.
