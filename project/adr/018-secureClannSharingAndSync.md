# ADR-0012: Local-first encrypted Clann sharing and synchronisation

- Status: proposed
- Date: 2026-09-10
- Related requirements: [002](../requirements/features/002-privacyAndSecurityModel.md), [019](../requirements/features/019-secureClannAccessAndSync.md)
- Related ADRs: [002](002-offlineFirst.md), [003](003-neverStorePasswords.md), [004](004-publicTemplatesPrivateData.md), [005](005-informationClassification.md), [007](007-knowledgeBeforeDocuments.md), [011](011-platformPrivateDataRoot.md)

## Context

Eolas is local-first and currently creates private Clann data beneath a platform-resolved local data root. That is suitable for a single user or device, but a real Clann may need authorised family members, executors, attorneys or other trusted people to access selected information from other devices or locations.

A single shared database hosted on a server would make remote access simpler, but it would materially increase privacy, security, availability and operational risk. It would also weaken the existing offline-first principle if the server became the canonical source required for normal use.

Conversely, keeping all data solely on one person's device creates a continuity failure: if that device is lost, inaccessible or the primary user is incapacitated, the information intended to help the Clann may be unavailable when it is most needed.

The architecture therefore needs to separate:

- local storage;
- encryption and key custody;
- identity and device trust;
- application access control;
- legal authority;
- synchronisation transport; and
- emergency or recovery access.

These concerns must not be collapsed into one provider-specific cloud design.

## Decision

Eolas will use a **local-first encrypted data model with optional secure synchronisation**.

Each supported device keeps a local Eolas store suitable for offline use. Remote services or peer-to-peer transports may synchronise Clann data, but synchronisation is an adapter capability rather than the domain model or canonical application architecture.

The design follows these rules.

### Local-first operation

- Normal application use must not require a live network connection unless a specific feature inherently requires one.
- Each authorised device maintains a local store through the shared storage contract.
- The domain layer must not depend on a cloud provider, filesystem layout, database engine or synchronisation technology.
- A Clann may operate indefinitely without enabling remote synchronisation.

### Encryption boundary

- Private Clann data must be encrypted at rest where the selected storage adapter can provide that control.
- Synchronised private data must be encrypted in transit and must not be exposed to an untrusted synchronisation provider as plaintext.
- Remote storage should hold ciphertext that is decryptable only by authorised Eolas identities or devices unless a future accepted ADR explicitly approves another trust model.
- Eolas must use established cryptographic libraries and protocols rather than inventing proprietary cryptographic algorithms.
- Key material must be managed separately from ordinary domain records and must never be represented as ordinary user-entered fields.

### Identity, membership and access

The architecture must distinguish these concepts:

- `Person`: a real-world person represented by the Clann knowledge model;
- `ClannMembership`: that person's relationship to a Clann;
- `UserIdentity`: an identity capable of authenticating to Eolas;
- `DeviceIdentity`: an enrolled device or installation;
- `AccessGrant`: application permission to access specified information;
- `Role` or equivalent reusable access grouping;
- `Authority`: real-world legal or operational authority modelled by the domain.

Application access must never imply legal authority. A person who can read a banking record in Eolas is not thereby authorised to operate the corresponding bank account.

### Least privilege and classification

- Access decisions must respect Eolas information classification.
- Sharing must be explicit and fail closed.
- Clann-wide access must not automatically expose every member's private or highly confidential information.
- The design must support shared, restricted and member-specific information without requiring each domain to invent its own access-control system.
- Export and synchronisation policies must preserve or increase source classification, never silently lower it.

### Synchronisation boundary

Synchronisation must be implemented behind a reusable provider-neutral contract.

Potential adapters may include an Eolas-hosted service, self-hosted service, WebDAV, S3-compatible object storage, peer-to-peer synchronisation, local network transfer or encrypted removable backup. Listing an adapter here does not approve or require its implementation.

The synchronisation contract must support, at minimum:

- identifying the Clann and device without exposing private domain content unnecessarily;
- detecting new or changed records;
- preserving stable opaque record IDs;
- version/conflict detection;
- avoiding silent last-writer-wins data loss for conflicting consequential changes;
- resuming interrupted synchronisation safely;
- integrity verification;
- reporting sync state without disclosing private values; and
- revocation of a device or access grant.

### Recovery and continuity

Eolas must not make continuity depend on one person's memorised secret, one device or one online provider account.

A future recovery design must provide a controlled mechanism for regaining access after device loss, incapacity or death while resisting unilateral unauthorised recovery.

Possible mechanisms include recovery keys, trusted contacts, multiple-party recovery or threshold secret sharing. No particular recovery mechanism is approved by this ADR. Recovery cryptography and emergency release require their own threat model and acceptance criteria before implementation.

### Provider independence

- The Clann domain model must remain independent of the synchronisation provider.
- Changing sync provider must not require remodelling household knowledge.
- A provider must not become the sole holder of canonical plaintext Clann data by architectural accident.
- Backup/export remains distinct from synchronisation: synchronisation is not itself a backup strategy.

## Conceptual architecture

```text
User / CLI / desktop / mobile
            |
            v
      Eolas domain services
            |
            v
       storage contract
            |
            v
      local encrypted store
            |
            +--------------------+
                                 |
                                 v
                         sync engine/adapter
                                 |
                                 v
                      encrypted remote/peer data
```

Identity, access control and key-management services cross the storage and synchronisation boundaries but remain separate from household/domain entities.

## Delivery approach

Implementation should proceed incrementally:

1. shared storage abstraction and local store;
2. encryption-at-rest support and key-management boundary;
3. backup/export/restore with integrity checks;
4. user identity, device identity, Clann membership and access grants;
5. trusted-device enrolment and revocation;
6. provider-neutral encrypted synchronisation;
7. remote multi-user access;
8. separately reviewed emergency/recovery access.

A later phase may combine some steps where implementation evidence shows that doing so remains testable and safe.

## Alternatives considered

### Hosted central plaintext database

Rejected as the default because it increases provider trust, operational exposure and network dependency and conflicts with local-first privacy goals.

### Store everything on one primary device

Rejected as the long-term model because it creates a continuity and availability single point of failure.

### Put the data directory in a consumer file-sync folder

Rejected as the architectural solution because generic file synchronisation does not provide Eolas-aware conflict handling, identity, access grants, revocation or reliable database semantics. A suitably encrypted file-sync adapter may be supported later under the shared synchronisation contract.

### Give every Clann member the same encryption key and full dataset

Rejected because it violates least privilege, makes selective revocation difficult and conflates Clann membership with unrestricted access.

### Make cloud synchronisation mandatory

Rejected because Eolas must remain usable offline and without dependence on an Eolas-operated service.

## Consequences

- Secure sharing becomes a first-class capability rather than an incidental filesystem choice.
- Storage, sync, identity, access control and legal authority require separate reusable concepts and tests.
- Remote-access features will be more complex than a conventional server-hosted CRUD application.
- The design supports CLI, desktop, mobile and future web interfaces without making any interface the security boundary.
- Encrypted synchronisation requires explicit key lifecycle, enrolment, revocation and recovery design.
- Conflict handling must be defined before multi-writer sync is considered production-ready.
- Backup and recovery remain independently testable requirements.
- Banking and other highly sensitive modules can rely on a shared security/access foundation rather than inventing domain-specific sharing mechanisms.

## Follow-up decisions

Before production remote synchronisation or emergency recovery is implemented, separate ADRs should settle at least:

- cryptographic key hierarchy and rotation;
- user/device enrolment and authentication;
- authorisation/access-grant evaluation;
- synchronisation conflict and merge policy;
- remote provider trust model and metadata leakage;
- recovery/emergency access and threshold policy;
- secure deletion and revoked-device behaviour.
