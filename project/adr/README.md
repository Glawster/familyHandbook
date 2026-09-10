# Architecture decision records

Architecture decision records (ADRs) preserve important project-shaping choices
and the reasons behind them. Architecture here includes the handbook's content,
information model, privacy boundaries and delivery approach—not only software.

Name records `<threeDigitNumber>-<shortName>.md`. Each record states its
status, context, decision and consequences and links to affected requirements.
ADRs are append-only historical records: do not rewrite an accepted decision to
make a new choice appear inevitable. Instead, add a new ADR and mark the old
record `superseded`, with links in both directions.

Valid statuses are `proposed`, `accepted`, `deprecated` and `superseded`.

## Keystone ADR

[007: Knowledge before documents](007-knowledgeBeforeDocuments.md) is
the project's keystone architectural decision. When work is uncertain, begin
with its test:

> **Am I modelling knowledge, or am I modelling a document?**

Document-shaped models usually indicate that the underlying knowledge should be
identified first. Requirements concerned genuinely with presentation remain
valid, but presentation must not become the source of truth.

## Records

- [001: Handbook before software](001-handbookBeforeSoftware.md)
- [002: Offline first](002-offlineFirst.md)
- [003: Never store passwords](003-neverStorePasswords.md)
- [004: Public templates and private data](004-publicTemplatesPrivateData.md)
- [005: Information classification](005-informationClassification.md)
- [006: One shared domain model, many projections](006-sharedDomainModel.md) — superseded by ADR-0007
- [007: Knowledge before documents](007-knowledgeBeforeDocuments.md) — keystone ADR
- [008: Handbook as a projection of household knowledge](008-handbookAsProjection.md)
- [009: Markdown as the canonical handbook source](009-markdownHandbookSource.md)
- [010: Private Clann data location](010-privateClannDataLocation.md) — superseded by ADR-0011
- [011: Platform-resolved private data root](011-platformPrivateDataRoot.md)
- [012: Local-first encrypted Clann sharing and synchronisation](012-secureClannSharingAndSync.md) — proposed
