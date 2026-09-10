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
- [012: Shared identity and aggregate ownership](012-sharedIdentityAndOwnership.md)
- [013: Persistence, history and transaction boundaries](013-persistenceHistoryAndTransactions.md)
- [014: People, organisations and contacts](014-partiesOrganisationsAndContacts.md)
- [015: Authority and provider recognition](015-authorityAndProviderRecognition.md)
- [016: Evidence and document references](016-evidenceAndDocumentReferences.md)
- [017: Module and plugin boundaries](017-moduleAndPluginBoundaries.md)
- [018: Local-first encrypted Clann sharing and synchronisation](012-secureClannSharingAndSync.md) — proposed

ADRs 0012–0017 settle the Phase 0 prerequisites for the shared knowledge
kernel. ADR-0013 clarifies the apparent tension with ADR-0005: ordinary handbook
and current YAML capture output still reject Highly Confidential values, while
future protection-capable stores may retain legitimate highly classified
knowledge. Credentials and payment-card secrets remain prohibited everywhere.
