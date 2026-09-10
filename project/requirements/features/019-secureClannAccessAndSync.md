# 019: Secure Clann access and synchronisation

Priority: critical  
Owner: project maintainers

## Status

ToDo

## Outcome

As a Clann owner or authorised trusted person, I need Eolas data to remain available securely across approved devices and locations without making a cloud service the mandatory source of truth, so that the Clann can access continuity information when it is needed while preserving privacy, least privilege and offline operation.

## Context

The initial CLI stores private Clann data locally beneath the platform-resolved `eolasDataRoot`. That is appropriate for single-device use but does not by itself support a family in which several authorised people need controlled access from different locations.

A continuity system must also avoid a single-point-of-failure design where the only usable copy or decryption capability belongs to one person or one device. At the same time, remote access must not turn Eolas into a conventional hosted plaintext household database or weaken the existing local-first, privacy and information-classification decisions.

This requirement establishes the product outcome and security constraints for local encrypted storage, identity, access grants, trusted devices, optional synchronisation, revocation and recoverability. Detailed cryptographic and synchronisation mechanisms require separate architecture decisions before production implementation.

## Scope

- Local-first Clann data operation with optional remote synchronisation.
- Encryption of private Clann data at rest where supported by the selected production storage adapter.
- Encryption in transit for any synchronisation transport.
- Provider-neutral synchronisation architecture.
- `Person`, `ClannMembership`, `UserIdentity`, `DeviceIdentity`, `AccessGrant`, role and legal `Authority` kept as distinct concepts.
- Explicit, least-privilege access to shared, restricted and member-specific Clann information.
- Trusted-device enrolment, identification and revocation.
- Stable record identity and safe change/conflict handling across devices.
- Backup/export/restore treated separately from synchronisation.
- Recovery design that does not depend solely on one person, device or provider account.
- Audit-relevant records for access grants, enrolment, revocation, synchronisation and recovery actions without logging private values or cryptographic secrets.
- Support for CLI, desktop, mobile and future web interfaces through shared domain/storage/security contracts.

## Out of scope

- Selecting a mandatory cloud provider.
- Requiring an Eolas-hosted service for normal operation.
- Implementing Open Banking or bank authentication.
- Storing passwords, PINs, recovery codes, private authentication secrets or full payment-card credentials as ordinary Clann data.
- Treating Eolas application permissions as legal authority over external assets or services.
- Final selection of cryptographic algorithms, key derivation parameters, secure hardware integration or threshold-recovery scheme in this requirement.
- Guaranteeing secure deletion from third-party storage systems that Eolas does not control.
- Assuming synchronisation is a substitute for backup.

## Functional requirements

### SAR-1 Local-first availability

Eolas must support normal Clann read/write workflows using a local store without requiring a network connection, except where a specifically requested external feature inherently needs one.

A Clann must be able to operate without enabling synchronisation.

### SAR-2 Storage abstraction

Domain services must use a shared storage contract rather than depend directly on YAML, SQLite, browser storage, a cloud API or a literal filesystem path.

The storage contract must preserve stable opaque record identity, schema/version metadata, classification, atomic updates, migration behaviour and conflict detection required by the shared domain model.

### SAR-3 Encryption at rest

Production adapters that store private Clann data on a device or remote service must provide an approved encryption-at-rest boundary appropriate to that platform and threat model.

Cryptographic keys must be managed separately from ordinary domain records and must never be exposed as routine user-entered fields, logs, exports or diagnostics.

### SAR-4 Synchronisation confidentiality and integrity

Any remote or peer synchronisation mechanism must:

- use encrypted transport;
- preserve end-to-end confidentiality against an untrusted transport or storage provider where the approved adapter design claims that property;
- verify integrity before accepting synchronised content;
- resume safely after interrupted transfer; and
- fail closed when authenticity, integrity, classification or authorisation cannot be established.

A provider must not silently receive canonical plaintext Clann content merely because synchronisation is enabled.

### SAR-5 Identity separation

The model must distinguish at least:

- a real-world `Person`;
- the person's `ClannMembership`;
- a system `UserIdentity`;
- an enrolled `DeviceIdentity`;
- an application `AccessGrant`; and
- real-world legal or operational `Authority`.

One concept must not be inferred automatically from another.

A person may exist in the Clann without being a system user, and a system user may have limited application access without possessing legal authority over the underlying real-world asset.

### SAR-6 Explicit access grants

Access to non-public Clann information must be based on explicit grants or approved role policy and must default to denial when the required decision cannot be established.

The access model must support:

- Clann-wide shared information;
- restricted information available to a defined subset of authorised users;
- member-specific information;
- stronger controls for more restrictive information classifications; and
- revocation without requiring deletion of the represented `Person` or historic facts.

### SAR-7 Classification preservation

Synchronisation, sharing, projection and export must respect the source information classification.

A workflow must never silently downgrade classification to enable access or transfer.

Missing or invalid classification must use the project's fail-closed classification behaviour.

### SAR-8 Device enrolment and revocation

The system must maintain explicit device identity for devices permitted to access synchronised Clann data.

Enrolment must require an authenticated or otherwise approved trust-establishment workflow.

Revocation must prevent subsequent authorised synchronisation or new key access by that device to the extent supported by the approved cryptographic design and must record the revocation event without exposing private content.

### SAR-9 Provider-neutral synchronisation

Synchronisation must be exposed through a reusable provider interface independent of household domain models.

The architecture may support multiple providers or transports over time, including hosted, self-hosted, object-storage, WebDAV, peer-to-peer or local-network implementations, but no provider is required by this requirement.

Changing provider must not require remodelling Clann knowledge or changing stable domain identifiers.

### SAR-10 Safe multi-device change handling

Synchronisation must identify new, changed and conflicting records using stable identity and version information.

Consequential conflicting changes must not be silently resolved using unconditional last-writer-wins behaviour.

The system must either merge deterministically under an approved rule or present a conflict for controlled resolution while preserving sufficient history to understand both changes.

### SAR-11 Clann isolation

Data, identities, access grants, encryption context and synchronisation state for one Clann must not be readable or writable through another Clann's context.

Cross-Clann references or key use must be rejected unless a future explicit cross-Clann sharing requirement and ADR define the behaviour.

### SAR-12 Backup, restore and export

Eolas must treat backup and restore as separate capabilities from live synchronisation.

A synchronised Clann must still be able to produce a controlled backup or export suitable for its approved recovery workflow.

Backup/restore operations must preserve integrity, classification and schema/version information and must report failures without leaking private values.

### SAR-13 Recovery and continuity

The security design must avoid making the Clann permanently inaccessible solely because one primary user's device, memorised secret or provider account is unavailable.

Before production recovery is implemented, the project must define and threat-model a recovery policy covering at least:

- device loss;
- forgotten or unavailable authentication material;
- incapacity;
- death;
- trusted-person participation where applicable;
- revocation;
- recovery audit/evidence; and
- resistance to unilateral unauthorised recovery.

The final mechanism may use recovery keys, trusted contacts, threshold/multiple-party recovery or another reviewed technique, but the mechanism is not selected by this requirement.

### SAR-14 Authority boundary

Eolas must state and enforce the conceptual boundary that application access is not evidence of legal authority to operate an external account, property, service or asset.

Where a workflow involves an executor, attorney, deputy, trustee, business signatory or similar role, the relevant domain `Authority` and supporting evidence remain separate from the Eolas `AccessGrant` that permits software access.

### SAR-15 Audit and privacy-safe diagnostics

Security-relevant operations must provide audit-capable metadata sufficient to investigate:

- access-grant creation/change/revocation;
- device enrolment/revocation;
- synchronisation success/failure/conflict;
- restore/recovery initiation and completion; and
- key lifecycle events where safe to record them.

Logs and diagnostics must not include plaintext private Clann values, cryptographic keys, authentication secrets or other prohibited secret material.

### SAR-16 No mandatory hosted dependency

A user who chooses not to enable remote synchronisation must retain the core Eolas local workflow, subject only to platform capabilities and explicitly external features.

The open data/domain model and backup/export path must not depend on the continuing operation of an Eolas-hosted service.

## Security and privacy principles

1. Local-first is the default operating model.
2. Encryption is necessary but does not replace authentication, authorisation, classification or backup.
3. Least privilege is preferred over Clann-wide disclosure.
4. Synchronisation providers are transport/storage dependencies, not domain authorities.
5. Application access and real-world legal authority are separate.
6. No single device should be an unavoidable continuity dependency.
7. No recovery mechanism may be introduced without a documented threat model.
8. Cryptographic design must use established libraries and protocols rather than bespoke algorithms.
9. Metadata leakage must be considered explicitly even when content is encrypted.
10. Security failures must fail closed and avoid disclosing private values.

## Acceptance criteria

1. Given a supported Eolas installation with synchronisation disabled, when an authorised user creates, reads and updates a Clann, then the core workflow succeeds using only the local store and no network dependency is required.
2. Given private Clann records in a production storage adapter, when the underlying storage is inspected outside the authorised Eolas access path, then the adapter meets its approved at-rest encryption design and does not expose the protected records as ordinary plaintext files or database values.
3. Given a Clann containing a represented person who is not a user, a user with restricted access, an enrolled device and a person with legal authority, when the identity model is inspected, then each concept has a distinct stable identity and none is automatically inferred from another.
4. Given information of different classifications, when access, sync, export or projection is attempted, then the explicit access policy and classification rules are applied; missing or invalid classification fails closed and no workflow silently lowers classification.
5. Given two authorised devices making non-conflicting changes, when synchronisation occurs, then both converge on the accepted records with stable IDs and integrity preserved.
6. Given two authorised devices making conflicting consequential changes to the same logical record, when synchronisation occurs, then neither change is silently discarded by unconditional last-writer-wins behaviour; the approved conflict policy preserves or presents both changes for controlled resolution.
7. Given a revoked device, when it attempts subsequent authorised synchronisation or obtains new protected key material, then the attempt is rejected according to the approved device/key lifecycle design and the rejection is auditable without exposing private data.
8. Given two separate Clanns, when identities, records, keys or sync references from one are presented in the other's context, then the cross-Clann operation is rejected.
9. Given synchronised Clann data and a remote transport/storage provider, when provider-held content is inspected under the approved end-to-end encrypted adapter design, then private domain content is not available to that provider as canonical plaintext and integrity tampering is detectable.
10. Given a synchronised Clann, when the user requests backup and later restores to a supported clean environment, then the documented backup/restore path operates independently of live synchronisation and preserves domain identity, classification and supported history.
11. Given a user who has Eolas read access to banking or estate information but lacks corresponding external legal authority, when continuity guidance is produced, then Eolas does not describe that application permission as authority to transact, close accounts or act for another person.
12. Given the proposed production recovery design, when the documented threat review tests device loss, incapacity/death, malicious recovery, collusion assumptions, revocation and provider loss, then every scenario has an explicit mitigation or remains a release blocker; production emergency recovery is not enabled merely by this requirement.
13. Given security-relevant logs, support bundles and diagnostics, when they are reviewed, then they identify events and state needed for support/audit without containing private record values, credentials, keys or prohibited secret material.

## Dependencies and decisions

- Depends on:
  - [002 — Privacy and security model](002-privacyAndSecurityModel.md);
  - [007 — Legal document custody and access](007-legalDocumentCustodyAndAccess.md);
  - the shared domain/storage foundation used by requirements 009–018.
- Related requirements:
  - [008 — Document Import Framework](008-documentImportFramework.md), because imported evidence must respect the same local, classification and access boundaries;
  - [009 — Banking module](009-bankingModule.md), because banking data is an early high-sensitivity consumer of this capability.
- ADRs:
  - [002 — Offline first](../../adr/002-offlineFirst.md);
  - [003 — Never store passwords](../../adr/003-neverStorePasswords.md);
  - [004 — Public templates and private data](../../adr/004-publicTemplatesPrivateData.md);
  - [005 — Information classification](../../adr/005-informationClassification.md);
  - [007 — Knowledge before documents](../../adr/007-knowledgeBeforeDocuments.md);
  - [011 — Platform-resolved private data root](../../adr/011-platformPrivateDataRoot.md);
  - [012 — Local-first encrypted Clann sharing and synchronisation](../../adr/012-secureClannSharingAndSync.md).

## Verification

- Contract tests for local/offline storage behaviour and Clann isolation.
- Storage-adapter tests for encryption boundary, atomicity, migration and error redaction.
- Identity/access tests covering persons, memberships, users, devices, grants, classifications and legal authority separation.
- Synchronisation conformance tests using an injectable local/fake transport before any hosted provider integration.
- Multi-device deterministic tests for normal convergence, interrupted transfer, duplicate delivery and conflicts.
- Revocation tests covering an enrolled then revoked device.
- Backup/export/restore round-trip tests independent of sync.
- Privacy review of logs, metadata and provider-visible state.
- Threat-model review before approving production key management, remote sync or recovery mechanisms.
- No verification fixture may contain real household information, realistic private identifiers or usable credentials.

## Delivery guidance

A safe implementation order is:

1. shared local storage abstraction;
2. encrypted local-store/key-management boundary;
3. backup/export/restore;
4. user and device identity plus Clann membership/access grants;
5. enrolment and revocation;
6. provider-neutral sync engine with fake/local conformance adapter;
7. production remote sync adapter;
8. remote multi-user workflows;
9. separately approved recovery/emergency-access mechanism.

Banking and other domain modules should consume these shared capabilities rather than implement their own encryption, identity or sharing rules.

## Traceability

- Implementation: pending
- Tests: pending
- Documentation: pending
- Pull request: pending
- ADR: [ADR-0012](../../adr/012-secureClannSharingAndSync.md)

## Change history

- 2026-09-10: created to define secure local-first multi-device and remote Clann access, optional synchronisation, access-control separation and recovery constraints.
