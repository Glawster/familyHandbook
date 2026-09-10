# ADR-0016: Evidence and document references

- Status: accepted
- Date: 2026-09-01
- Related requirements: [008](../requirements/features/008-documentImportFramework.md), 009–018

## Context

Statements and documents support knowledge but are not automatically canonical
facts. Phase 1 needs safe targets for later import without implementing import.

## Decision

An `EvidenceReference` points to an immutable original through an opaque secure
locator and records purpose, Clann, classification, SHA-256 checksum and
provenance. Originals are never changed in place; correction creates a new
evidence object. Evidence and extracted candidates do not become canonical
knowledge until the owning module validates and commits a command.

Original bytes, encryption, key custody, extraction attempts and candidate
decisions will belong to the Document Import module. Locators must not reveal
credentials or unsafe filesystem detail. Adapters fail closed if they cannot
meet the classification's protection policy.

## Consequences

- Phase 1 implements references and provenance, not OCR or file ingestion.
- Facts can cite evidence without coupling aggregates to document storage.
- Checksums support integrity checking but do not replace access control or encryption.
