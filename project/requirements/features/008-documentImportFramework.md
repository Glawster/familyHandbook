# 008: Document Import Framework

Priority: high  
Owner: project maintainers

## Status

ToDo

## Outcome

As an Eolas user, I need to import documents into my private Clann record through
a guided, local-first workflow so that useful knowledge can be extracted,
checked and linked to existing records without retyping it or losing the source
evidence.

As an importer developer, I need stable framework contracts so that support for
a new document type can be added as a plugin without changing the ingestion,
security, evidence, audit or commit services in the core application.

## Context

Families already hold much of the information Eolas helps them organise in
statements, policies, bills, certificates, identity records and other files.
Manual transcription is slow and error-prone. Automated extraction can reduce
that burden, but documents may contain confidential information, extraction is
never perfectly reliable, and a plausible value can still refer to the wrong
person, account or organisation.

The Document Import Framework provides one controlled path from a source file
to reviewed domain knowledge. The first plugin will support bank statements,
but framework contracts must also accommodate credit-card, insurance, pension,
utility, mortgage, investment, identity, civil-registration, legal and vehicle
documents. Document-shaped input must not make the imported document format the
Eolas domain model: accepted facts map to shared domain concepts and retain a
provenance link to evidence.

This is a requirements specification, not an implementation design. Names used
for interfaces and records describe required responsibilities; a later ADR may
select concrete Python protocols, serialisation formats, libraries and
encryption mechanisms.

## Vision and principles

### Purpose and user benefits

The framework must:

- reduce repetitive data entry while keeping the user in control of every
  durable change;
- turn existing documents into useful, reviewable Eolas knowledge rather than
  treating the documents themselves as the primary model;
- retain trustworthy evidence and provenance for accepted facts;
- provide one predictable import experience across document types;
- identify uncertainty, conflicts and failures plainly instead of hiding them;
- allow a user to stop, resume or discard work without partially changing the
  Clann record; and
- let developers add document support through bounded plugins rather than
  modifying core security and storage behaviour.

### Design principles

1. **User confirmation before commitment.** Extraction is a proposal. No
   extracted value may become canonical Clann knowledge until the user has
   reviewed the proposed changes and explicitly committed them.
2. **Knowledge before documents.** Plugins map reviewed facts to the shared
   Eolas domain model. They must not create a competing model based on page
   layouts, filenames or one provider's terminology.
3. **Privacy and minimisation by default.** The framework must collect, retain
   and display only information needed for the chosen import purpose. Passwords,
   PINs, recovery codes, authentication tokens, full payment-card data and
   equivalent secrets must not be imported into ordinary Eolas records.
4. **Local and offline first.** Classification, text extraction, OCR,
   validation, review and storage must work without a network connection for
   every Phase 1 format and workflow.
5. **Evidence is distinct from knowledge.** An immutable original, its metadata
   and its checksum support provenance. Accepted structured records remain
   independently reviewable and do not silently change when extraction
   technology changes.
6. **Fail closed.** Unsupported, corrupt, ambiguous, unsafe or unclassified
   input must remain uncommitted and must produce an actionable error or review
   state.
7. **Stable core, replaceable plugins.** Plugins may recognise, extract,
   validate, present document-specific review content and propose mappings.
   Core services retain control of file access, security policy, evidence,
   transactions, entity identity, history and audit events.
8. **Explain uncertainty.** Confidence must be presented with its basis and
   must never be represented as certainty or as a substitute for validation.
9. **Accessible under stress.** Review language and controls must be clear,
   keyboard accessible and usable with assistive technology.
10. **Provider and jurisdiction neutrality.** Core contracts must not assume a
    particular bank, document issuer, country, language, currency or page
    layout.

### Privacy-first and local-first processing

- Processing must occur on the user's device by default, including OCR and all
  model inference used by Phase 1.
- No file, page image, extracted text, derived field, diagnostic sample or
  metadata may leave the device unless the user separately enables a future
  approved remote-processing capability and gives informed consent for the
  specific operation.
- The import UI must state, before any remote transfer, what will be sent, to
  whom, for what purpose, under which retention terms and what local-only
  alternative is available. Absence of consent must leave local importing
  usable.
- Source evidence, working files and import records must live beneath the
  platform-resolved private `eolasDataRoot`, outside the public repository.
- Temporary plaintext and page images must use application-controlled private
  temporary storage, have the shortest practical lifetime and be removed after
  success, cancellation or recoverable failure. Crash recovery must identify
  and clean abandoned temporary artifacts.
- Logging and telemetry must exclude document contents, extracted values,
  filenames containing personal information, full paths, account identifiers
  and thumbnails. Telemetry must be disabled by default and is not required for
  import operation.
- Missing information classification must be handled as
  `highlyConfidential`; unknown classifications must be rejected.

## Actors and terminology

- **User:** an authorised person operating Eolas for a private Clann.
- **Source document:** the file selected by the user before it is admitted to
  evidence storage.
- **Evidence object:** the retained, immutable representation of an admitted
  source document and its integrity and provenance metadata.
- **Import job:** one user-initiated batch and its aggregate progress.
- **Import item:** the processing lifecycle for one source document within a
  job.
- **Importer plugin:** a versioned component that classifies and interprets one
  or more document types through the public plugin API.
- **Candidate value:** an extracted value that has not been committed.
- **Proposed change set:** the complete set of creates, updates, links and
  evidence references offered for confirmation for one import item.
- **Committed record:** canonical Eolas knowledge created or updated by one
  atomic user-approved change set.
- **Confidence:** a calibrated indication of extraction or matching
  uncertainty; it is not proof that a value is correct.
- **Correction:** a user change to, rejection of or replacement for a candidate
  value or proposed match.

## Scope

### Phase 1 deliverables

- A generic document-import core with the contracts and lifecycle specified
  here.
- Desktop ingestion using drag and drop and a native file picker.
- Multiple-file jobs, bounded parallel processing and per-item recovery.
- PDF ingestion, including native PDF text extraction and local OCR fallback
  for image-only or insufficient-text pages.
- Secure evidence retention, integrity verification, duplicate handling,
  provenance, history and audit records.
- Classification, review, entity resolution and atomic commit workflows.
- A bank-statement importer plugin proving the public extension points.
- Fully offline operation and local processing on supported desktop platforms.
- Redaction of extracted candidate content and derived review artifacts before
  commit or export; the retained original remains immutable and separately
  access-controlled.
- Public developer documentation, plugin conformance tests and safe fictional
  fixtures.

### Future-compatible document families

The contracts must be capable of representing plugins for:

- bank, credit-card, mortgage, pension and investment statements;
- insurance policies and utility bills;
- passports, driving licences and vehicle documents;
- birth and marriage certificates; and
- wills and lasting powers of attorney.

Listing a family here does not place its importer in Phase 1.

## Functional requirements

### FR-1: Document ingestion

1. The desktop UI must accept files through drag and drop onto a clearly
   identified target and through the platform-native file picker.
2. Both entry points must support one or more files and must produce the same
   validation and processing behaviour.
3. The file picker must initially filter to the union of enabled plugins'
   supported extensions while allowing the user to inspect unsupported files
   and receive a clear rejection reason.
4. The core must inspect file signatures and parsable structure; it must not
   trust an extension or declared MIME type alone.
5. Each input must be checked for readability, non-zero content, configured
   size and page limits, supported type, malformed or truncated structure and
   cryptographic checksum before extraction.
6. Active content, embedded files, scripts, external references and macros must
   never be executed. Password-protected or encrypted input must be reported as
   requiring a supported user action or rejected without retaining a password.
7. A multi-file selection creates one import job with separately visible item
   status, progress, errors and user decisions.
8. Processing must continue for independent items when another item fails.
   Cancellation must stop uncommitted work cleanly and must not roll back items
   the user already committed.
9. The core must compute a cryptographic content checksum before admitting
   evidence. Duplicate detection must compare that checksum against retained
   evidence and current jobs, and may also show clearly labelled probable
   duplicates based on stable document attributes.
10. For an exact duplicate, the user must be able to open the earlier import
    record, skip the new item, or deliberately create a new import attempt. A
    duplicate must never create a second evidence object or duplicate domain
    records silently.
11. Files must be copied into controlled evidence storage; later modification
    or deletion of the external source file must not alter retained evidence.
12. Ingestion must prevent path traversal, symbolic-link substitution and
    time-of-check/time-of-use replacement from admitting a different file than
    the one inspected.

### FR-2: Document classification

1. The framework must ask every enabled, compatible plugin for a classification
   claim using only the read-only input supplied by the core.
2. A claim must include the plugin ID and version, proposed canonical document
   type, confidence score, confidence band and non-sensitive reason codes.
3. The core must combine claims deterministically using documented tie and
   minimum-confidence rules. It must preserve all claims for audit.
4. High-confidence unambiguous results may advance automatically to extraction.
   Low-confidence, conflicting or unsupported results must require user choice
   and must never guess silently.
5. The user must be able to override the proposed type with any enabled plugin
   compatible with the verified file type, or mark the item unsupported.
6. Manual override and its reason category must be recorded. Free-text reasons
   must be optional and treated as private data.
7. A plugin failure, timeout or invalid response must be isolated to that
   plugin. Other classifiers and other import items must remain usable.
8. A plugin must declare canonical document type identifiers from a namespaced,
   versioned registry. Display labels may be localised and must not serve as
   identifiers.

### FR-3: Extraction pipeline

1. The core pipeline must expose ordered stages for admission, text extraction,
   OCR, metadata extraction, classification, structured extraction, validation,
   entity resolution, review and commit. A plugin may participate only in its
   declared extension points.
2. Native text must be extracted from text-bearing PDFs with page boundaries
   and source coordinates retained where the extraction library supplies them.
3. Pages without sufficient usable native text must be eligible for local OCR.
   Mixed PDFs must allow OCR only on affected pages rather than duplicating all
   text.
4. OCR output must retain page association, language selection, engine name and
   version, processing settings and confidence where available.
5. Core metadata extraction must capture verified file type, byte size, page
   count, checksum and ingestion timestamp. Embedded metadata must be labelled
   as document-supplied and untrusted.
6. Structured extraction must produce typed candidate values with a stable
   field identifier, original representation, normalised representation,
   provenance locator, extractor version, validation results and confidence.
7. Candidate values may include scalar fields, repeated rows and relationships.
   The contract must support dates, money with currency, identifiers, names,
   addresses, organisations and document-specific extensible types without
   reducing all values to untyped strings.
8. Every candidate field must identify the page and, when available, bounding
   region or text span from which it was derived. Values inferred across fields
   must list their contributing evidence and be labelled as inferred.
9. Confidence scores must use a documented range and confidence bands. The UI
   must distinguish unavailable confidence from zero confidence and show
   field-level uncertainty independently of document classification confidence.
10. Plugin validation must support required fields, formats, cross-field
    consistency, arithmetic reconciliation, date ranges and document-specific
    rules. Core validation must enforce domain schema, classification,
    prohibited-secret and storage constraints.
11. Validation results must contain stable codes, severity, affected fields and
    user-safe explanations. Errors block commit; warnings require visible
    acknowledgement or correction; informational findings do not block commit.
12. Re-running extraction must create a new attempt linked to the same immutable
    evidence. It must not overwrite an earlier attempt, its user decisions or
    records already committed from it.
13. Stage input and output must be bounded and serialisable so core tests can
    replay a pipeline without Qt or the original extraction engine.

### FR-4: Bank-statement plugin

1. Phase 1 must include at least one independently registered bank-statement
   plugin supporting PDF statements with native text and scanned PDF pages.
2. The plugin must classify a bank statement without relying only on filename,
   extension or one named provider.
3. Where present, it must propose statement issuer, account holder name,
   masked account reference, statement period, opening balance, closing
   balance, currency and transaction rows containing date, description and
   amount. It may propose other fields only when they have an approved domain
   purpose and classification.
4. The plugin must never propose online-banking credentials, PINs, CVV values,
   full payment-card numbers, authentication tokens or security answers. Full
   bank account identifiers may be retained only where an approved field,
   purpose, classification and user confirmation allow it; the review UI must
   display a masked form by default.
5. Validation must check statement-period ordering, currency consistency and,
   where the statement provides sufficient information, reconciliation of
   opening balance, transactions and closing balance within declared rounding
   rules.
6. Transaction extraction must preserve source order and evidence locators.
   Page headers, carried-forward rows and duplicated OCR lines must not silently
   become transactions.
7. The plugin must map the statement to an Eolas Document evidence reference,
   an Account and relevant Person or organisation relationships. Phase 1 must
   not create a separate provider-specific bank-statement domain model.
8. Importing individual transactions into a financial ledger is out of scope.
   Transaction rows may be reviewed and retained as extraction evidence only
   to validate the statement unless a separate approved requirement defines
   their canonical use.

### FR-5: Review and confirmation

1. Each supported item must enter a review state before commit, including
   high-confidence items.
2. The review must show the original evidence beside or in direct navigation
   with the proposed type, target records, candidate values, validation results
   and confidence indicators.
3. Selecting a candidate must locate and visibly highlight its source page or
   region when provenance coordinates exist. When they do not, the UI must
   identify the source page or explain that precise highlighting is unavailable.
4. The user must be able to accept, edit, clear or reject every optional
   candidate and correct any required candidate before commit.
5. The user must be able to reject the whole item without creating or updating
   domain records. The user must choose whether already-admitted evidence is
   retained with a rejected status or securely deleted subject to retention and
   audit policy.
6. The UI must distinguish extracted text, normalised values, inferred values,
   existing canonical data and user edits. It must not use colour as the only
   indication of confidence, validity or state.
7. All edits and rejection decisions must remain reversible until commit. The
   final confirmation must summarise every proposed record creation, update,
   relationship and retained evidence object.
8. Commit must be an explicit action and atomic for one import item: either the
   complete approved change set and history are stored, or no domain change is
   stored.
9. A concurrent change to a target record after review began must prevent a
   blind overwrite and require refresh and renewed confirmation.
10. User corrections must be stored as decisions associated with the extraction
    attempt and field, including before and after values where policy permits.
    Corrections must not automatically train or alter a plugin. Any future
    learning use requires separate opt-in consent and an approved requirement.
11. The user must be able to save a draft review, close Eolas and resume it
    without re-ingesting the source, subject to configured draft retention.

### FR-6: Entity resolution

1. Plugins must propose typed roles to resolve, such as account owner, account,
   issuer organisation, insured person or address. The core entity-resolution
   service owns lookup and identity decisions.
2. Matching must consider only compatible domain entity types and may use
   normalised names, masked or approved identifiers, addresses and existing
   relationships. It must not merge entities automatically in Phase 1.
3. Each match proposal must include a confidence band and user-safe explanation
   of the attributes that agree or conflict.
4. The user must be able to link to an existing entity, search for a different
   entity, create a new entity with the minimum required fields, leave an
   optional role unresolved, or return to edit extracted data.
5. Possible duplicate entities must be shown before creation. Similarity alone
   must never expose an entity outside the active Clann or the user's authority.
6. New entity creation and updates must use the same domain validation and
   transaction boundary as manual Eolas editing.
7. A document may resolve different roles to different entities and may link to
   multiple people, accounts, organisations, properties or addresses where the
   plugin mapping declares those cardinalities.
8. Resolution decisions, rejected candidates and created entity IDs must be
   included in import history and provenance.

### FR-7: Evidence storage and lifecycle

1. The core evidence service must retain an immutable byte-for-byte original of
   every source the user chooses to keep. Plugins must not write directly to
   evidence storage.
2. Each evidence object must have a stable opaque ID, cryptographic content
   checksum with algorithm, byte size, verified media type, ingestion timestamp,
   original modification timestamp when available, and source-name metadata.
3. Source-name metadata must be treated as private, must not be required as an
   identifier and must be safely escaped wherever displayed.
4. Evidence must support encryption at rest through a documented storage
   abstraction. Phase 1 must provide an application-supported encrypted option
   or inherit encryption from a documented encrypted Clann store; the UI must
   accurately state which protection is active and must not claim that a device
   or folder is encrypted when Eolas cannot verify it.
5. Encryption keys must not be stored alongside encrypted evidence in a form
   that defeats the protection. Key creation, recovery, rotation and loss
   behaviour must be documented before encrypted evidence is enabled.
6. Opening evidence must verify its checksum. A mismatch must quarantine the
   object from normal use, block derived commits and create a non-sensitive
   integrity event without modifying the original.
7. Derived files, OCR text, thumbnails, redacted copies and extraction results
   must be separately identified, classified and linked to their evidence and
   creating engine version. They must never replace the immutable original.
8. Redaction must create a derived artifact with explicit redaction regions and
   provenance. It must not promise removal unless verification confirms the
   selected content is absent from visible layers, searchable text, metadata
   and embedded content in the output format.
9. Evidence metadata and linked facts must support append-only version history.
   A replacement document creates a new evidence object and relationship; it
   does not overwrite earlier bytes.
10. Retention and deletion must account for domain links, pending imports,
    backups and audit obligations. The UI must state what will remain before
    deletion.
11. Secure deletion must use the strongest supported platform/storage operation
    and truthfully disclose its limits on copy-on-write filesystems, SSDs,
    backups and synchronised copies. Where physical erasure cannot be assured,
    cryptographic erasure or key destruction may satisfy the policy if its
    prerequisites are met.
12. An interrupted evidence write must not expose a partial object as valid.
    Recovery must either complete an atomically staged write or remove it.

### FR-8: Import history, provenance and audit

1. The framework must keep an import job and item record even when an item is
   skipped, rejected, cancelled or fails after admission, subject to the
   minimum audit-retention policy.
2. An item history must record: stable IDs; job ID; initiation and event
   timestamps with time-zone context; evidence ID and checksum; source-name
   metadata where retained; verified file type; chosen document type;
   classifier, extractor and OCR component IDs and versions; confidence values;
   validation results; entity decisions; user corrections; acknowledgements;
   commit result; resulting record IDs; and non-sensitive errors.
3. History must record actor identity or local profile where the application
   supports multiple actors. It must never imply stronger identity assurance
   than the application provides.
4. Events must be append-only in normal operation, ordered, and attributable to
   a framework, plugin or user action. Corrections to history must append a
   superseding event rather than rewriting the earlier event.
5. A committed field must be traceable from the domain record to the import
   attempt, candidate value and evidence locator that supported it, and from an
   import item to every record it created or changed.
6. The user must be able to inspect import history by date, status, document
   type and resulting record, and open retained evidence when authorised.
7. History export must follow Eolas classification and export controls, omit
   evidence bytes unless explicitly selected, and make redactions and omissions
   apparent.
8. Deleting evidence or candidate content under retention policy must leave a
   tombstone containing only the minimum non-sensitive audit facts required to
   explain the deletion and affected records.

### FR-9: Errors, recovery and observability

1. Errors must have a stable code, lifecycle stage, severity, retryability,
   user-safe message, suggested action and an internal cause available to local
   diagnostics without document content.
2. Expected failures must include unsupported type, invalid or corrupt file,
   encrypted input, size or page limit, extraction failure, OCR failure, plugin
   timeout or crash, validation failure, evidence integrity failure, storage
   failure, conflict and user cancellation.
3. Retrying a stage must be idempotent and must not duplicate evidence, history
   events or domain records.
4. A process or application crash must leave committed items valid and
   uncommitted items recoverable or safely discardable on next start.
5. Batch progress must distinguish queued, inspecting, classifying, extracting,
   resolving, awaiting review, committing, completed, skipped, rejected,
   cancelled and failed states.
6. Application logs must use stable IDs and safe operational metadata. Raw
   document data and candidate values may appear only in an explicit,
   user-controlled diagnostic export that previews and redacts its contents.

## Architecture and public contracts

### Layer boundaries

The framework must be divided into independently testable responsibilities:

| Responsibility | Core ownership | Plugin participation |
| --- | --- | --- |
| Ingestion, signature checks and limits | Required | Declares compatible verified media types |
| Evidence and temporary storage | Required | None; opaque read-only handles only |
| Job lifecycle, scheduling and cancellation | Required | Receives bounded calls and cancellation |
| Classification arbitration | Required | Returns classification claims |
| PDF text and OCR services | Required | Requests capabilities through context |
| Structured extraction | Orchestrated by core | Returns typed candidate fields |
| Domain and security validation | Required | Adds document-specific validation |
| Entity lookup and identity | Required | Declares mapping roles and hints |
| Review shell and final confirmation | Required | Supplies schema-driven review sections and optional bounded components |
| Transactional commit | Required | Proposes mappings; cannot write directly |
| History, provenance and audit | Required | Supplies component/version and reason codes |

Core business logic and plugin contracts must have no dependency on PySide6.
Qt adapters and views orchestrate the services and render framework-defined
review models.

### Required public interfaces

The implementation must publish versioned contracts equivalent to:

- **Importer registry:** discover, enable, disable and inspect plugins; reject
  duplicate plugin IDs and incompatible API versions.
- **Importer manifest:** declare stable plugin ID, semantic version, plugin API
  range, document type IDs, verified media types, capabilities, languages,
  jurisdictions and review contribution.
- **Classifier:** accept a core-owned read-only document view and return zero or
  more typed classification claims.
- **Extractor:** accept a read-only document view, approved core extraction
  artifacts and cancellation context; return an extraction result without
  mutating domain or storage state.
- **Validator:** accept the extraction result and return stable validation
  findings without side effects.
- **Review provider:** supply a declarative, serialisable review schema and
  labels, ordering, field help, evidence navigation and validation presentation.
- **Entity mapper:** declare domain entity roles, candidate search hints,
  cardinality and proposed creates, updates and relationships.
- **Commit planner:** translate confirmed candidates and resolutions into a
  serialisable proposed change set that the core validates and commits.
- **Evidence service:** admit, open, verify, derive, retain and delete evidence
  through authorised core operations.
- **Import service:** create, resume, cancel and inspect jobs and items through
  UI-independent commands and events.
- **History service:** query immutable import attempts, decisions, provenance
  and results without exposing evidence content by default.

All public contracts must use stable identifiers, typed data-transfer models,
explicit result or error types, cancellation and timeouts where work may be
long-running, and declared compatibility rules. A minor plugin API revision
must remain backward compatible; a breaking revision must change the major API
version and produce a clear incompatibility result rather than attempting to
load the plugin.

### Required data models

At minimum, the public data model must define:

- `ImportJob`: ID, creation context, timestamps, aggregate state, item IDs and
  progress summary;
- `ImportItem`: ID, evidence or staged-source reference, lifecycle state,
  selected plugin and type, active attempt, validation summary and outcome;
- `EvidenceObject`: ID, checksum, verified media type, size, timestamps,
  classification, encryption state, retention state and derived-object links;
- `ProcessingAttempt`: ID, item ID, component identities and versions, stage
  events, claims, extraction result, validation and terminal status;
- `ClassificationClaim`: namespaced type ID, score, band, reason codes and
  plugin identity;
- `CandidateField`: stable field ID, typed original and normalised values,
  confidence, provenance locators, classification and validation findings;
- `ProvenanceLocator`: evidence ID, page and optional text span or bounded
  region, derivation inputs and engine identity;
- `ValidationFinding`: stable code, severity, field references and safe message;
- `EntityResolution`: declared role, candidates, selected or created entity,
  confidence basis and user decision;
- `UserDecision`: action, target, timestamp, actor context, optional reason code
  and permitted before/after values;
- `ProposedChangeSet`: creates, updates, relationships, evidence links, expected
  target versions and a human-readable summary; and
- `ImportEvent`: append-only event ID, item or job ID, timestamp, actor or
  component, event type and privacy-safe payload.

Persisted models must be schema-versioned. Readers must reject an unknown newer
schema safely; migrations must be explicit, transactional, reversible where
practical and recorded in history.

### Plugin isolation and governance

1. Plugins must be explicitly registered and disabled by default if unsigned,
   untrusted or incompatible under the application's distribution policy.
2. A plugin receives least-privilege access to core capabilities and a bounded
   view of one import item. It must not receive arbitrary filesystem, network,
   credential-store or unrelated Clann access through the plugin API.
3. The core must enforce time, memory, output-size and cancellation limits
   around plugin work where the selected runtime permits them. A later ADR must
   state whether third-party plugins require process isolation.
4. Plugin output is untrusted input to core schema, security and domain
   validation. Invalid fields, identifiers or mappings must be rejected.
5. A disabled or removed plugin must not make retained evidence, history or
   previously committed domain records unreadable. Reprocessing may require the
   plugin and must explain that dependency.
6. Review extensions should be declarative. Any executable custom review
   component must use an explicitly versioned, restricted interface and cannot
   bypass core confirmation, accessibility, validation or commit controls.
7. Plugin installation, enablement, disablement and version change must be
   auditable. Updating a plugin must not automatically reprocess old evidence.

## Security requirements

1. Threat modelling must cover malicious PDFs, decompression and page-count
   bombs, parser vulnerabilities, path attacks, plugin compromise, prompt or
   content injection, temporary-file exposure, log leakage, cross-Clann access,
   evidence tampering, unsafe exports, key loss and incomplete deletion.
2. Parser and OCR dependencies must be pinned and routinely reviewed for known
   vulnerabilities. Input processing must use resource limits and the strongest
   practical isolation supported by the target platform.
3. Text inside a document is data, never an instruction to the application,
   plugin, OCR engine or any future AI model. Embedded prompts, links and active
   instructions must not alter security policy or authorize tool use.
4. Every evidence and history access must be scoped to the active Clann and
   current local authorisation context.
5. Sensitive values must be masked by default in lists, notifications, recent
   items, screenshots intended for support and operating-system task previews
   where the platform permits.
6. Clipboard copying and export of confidential values must require an explicit
   action and follow Eolas classification controls.
7. No cloud AI or remote OCR may be enabled implicitly by plugin installation,
   application upgrade, unavailable local engine or poor extraction quality.
8. Security failures must fail closed without deleting the only retained
   original or exposing its contents in an error.

## Non-functional requirements

### Performance and scalability

- On the reference desktop hardware defined by the test plan, admission and
  checksum calculation for a 25 MB file must complete within 5 seconds at the
  95th percentile, excluding removable-media latency.
- A 20-page native-text PDF must reach review within 15 seconds at the 95th
  percentile; a 20-page 300-DPI scanned PDF must reach review within 120 seconds
  using the Phase 1 local OCR engine. Reference hardware, fixtures and engine
  versions must be recorded with results.
- The UI must acknowledge an import action within 200 ms, update visible
  progress at least every 500 ms during active work, and remain responsive to
  navigation and cancellation.
- A batch of 100 supported documents must complete without unbounded memory or
  thread growth. Concurrency must be configurable and bounded; queued work must
  apply backpressure.
- Evidence and history lookup by ID or exact checksum must remain usable with
  10,000 evidence objects; the performance test plan must set and verify a
  target of no more than 2 seconds for these local lookups on reference hardware.

### Accessibility and usability

- The workflow must conform to WCAG 2.2 AA for applicable desktop content and
  platform accessibility APIs.
- Every action and field must be operable by keyboard, have a programmatic name,
  role, state and error association, and preserve a logical focus order.
- Confidence, validation and import state must be expressed with text or icons
  and accessible labels, never colour alone.
- Zoom to 200 percent and supported operating-system text scaling must not hide
  actions, truncate essential values or force two-dimensional scrolling in the
  form portion of the review.
- Status announcements must not overwhelm screen-reader users; batch progress
  must provide a concise aggregate with item detail on demand.

### Cross-platform and offline operation

- Phase 1 must provide equivalent core behaviour on the Eolas-supported Linux,
  macOS and Windows versions, using platform-resolved private data and temporary
  locations.
- All required import, OCR, review, commit, history and evidence workflows must
  pass with network access disabled after application installation.
- File paths, case sensitivity, Unicode filenames, long paths and platform file
  locking must be covered by adapter tests without using the source filename as
  a trusted identifier.

### Extensibility and maintainability

- Adding a conforming new document-type plugin must require no modifications to
  core ingestion, evidence, job, history, security, entity-resolution or commit
  modules.
- Core and plugin packages must be independently testable without starting Qt.
- Public API and schema compatibility policy must be versioned, documented and
  covered by contract tests using at least the current and previous supported
  minor API versions.
- Framework services must permit replacement of PDF, OCR and encrypted-storage
  adapters through public core-owned interfaces without changing plugins that
  request the same capability.

### Reliability, auditability and data quality

- Atomic writes and transactions must prevent a crash from producing a valid-
  looking partial evidence object, history record or domain change.
- The same input, plugin version and deterministic settings must produce
  equivalent normalised output; unavoidable nondeterminism must be recorded.
- Confidence thresholds must be calibrated against labelled fictional or
  safely licensed corpora before enabling automatic classification, with false
  positive and false negative rates reported by supported document type.
- Import records and provenance must remain readable across supported upgrades
  even when the originating plugin is unavailable.

## Developer requirements

### Error handling and logging

- Public methods must return typed successes or documented failures; callers
  must not parse display text to determine behaviour.
- Plugin exceptions must be caught at the framework boundary and translated to
  stable errors while preserving a local diagnostic cause.
- Retryability must be explicit. The UI must not offer retry for policy,
  integrity or validation errors until the blocking condition changes.
- Logs must use the repository's central logging conventions and correlation
  IDs for job, item and attempt. Safe summaries must be testable with automated
  assertions that private fixture values do not appear.

### Testing strategy

The implementation must include:

- unit tests for state transitions, confidence bands, schema validation,
  duplicate policy, path validation, masking, redaction verification, matching
  and commit planning;
- contract tests run against every evidence, OCR, PDF and storage adapter;
- plugin conformance tests covering manifest compatibility, classification,
  typed extraction, validation, review schema, mappings, limits, cancellation
  and invalid or malicious output;
- golden-file extraction tests using conspicuously fictional, non-usable and
  legally distributable native and scanned PDFs, including altered layouts;
- property-based and fuzz tests for parsers, normalisers, state transitions and
  malformed plugin output;
- integration tests from ingestion through review and atomic commit, including
  duplicate, conflict, crash recovery and evidence tampering scenarios;
- security tests for malicious PDFs, active content, path traversal, archive or
  page bombs, content injection, log disclosure and cross-Clann access;
- accessibility tests plus manual keyboard and screen-reader review on each
  supported desktop platform;
- performance and soak tests using the reference workloads in this requirement;
  and
- offline tests with network access denied, proving no fallback attempts a
  remote call.

Fixtures must never contain real household data, usable credentials or
realistic identifiers. Any test requiring confidential-looking values must use
conspicuously fictional markers and document why the values cannot be used.

### Documentation

Before Phase 1 is complete, maintainers must publish:

- a user guide covering supported formats, local processing, review,
  confidence, evidence retention, redaction, deletion, backup and recovery;
- a plugin-author guide with a minimal importer, lifecycle diagram, manifest,
  API reference, typed models, compatibility policy and conformance procedure;
- security guidance and a threat model covering trust boundaries, encryption,
  keys, temporary data, plugins and remote-processing prohibition;
- data-model and migration documentation for import, evidence, provenance and
  history records;
- operator and support guidance using privacy-safe diagnostics;
- a supported-document matrix naming plugin and engine versions, languages,
  jurisdictions, file limits and known limitations; and
- release notes for every plugin or framework change that affects extraction,
  validation, compatibility, security or previously imported evidence.

## Acceptance criteria

### AC-1: Ingestion, integrity and batches

1. Given the same set of five files supplied by drag and drop and by the file
   picker, when each job is admitted, then both create five equivalent item
   records and apply identical type, size, readability and integrity checks.
2. Given a batch containing valid, empty, corrupt, unsupported and encrypted
   files, when it runs, then every item reaches the correct independent status,
   each failure has an actionable stable error, and valid items remain
   reviewable.
3. Given an admitted file whose extension disagrees with its signature, when it
   is inspected, then the verified content type governs compatibility and the
   disagreement is recorded without executing active content.
4. Given the same bytes imported twice, including through different names and
   paths, when duplicate detection runs, then the checksum identifies the
   existing evidence and no second evidence or domain record is created without
   an explicit user decision.
5. Given source replacement during admission, a symbolic link and a traversal
   filename, when each is processed, then the framework either admits exactly
   the inspected bytes into its private store or rejects the item safely.

### AC-2: Classification and plugin selection

1. Given a labelled conformance set for the bank-statement plugin, when
   classification is measured using its declared threshold, then precision and
   recall targets approved in the test plan are met and per-layout results are
   published; filename-only evidence cannot satisfy the target.
2. Given two close competing claims, no claim above threshold and one classifier
   that crashes, when arbitration runs, then the result requires manual choice,
   preserves valid claims and keeps the job running.
3. Given a manual type override, when review is resumed later, then the chosen
   plugin, original claims, override decision and reason category remain visible
   in history.

### AC-3: Extraction, OCR and validation

1. Given fictional native-text, scanned and mixed bank-statement PDFs, when the
   pipeline runs offline, then native text is used where sufficient, OCR is
   limited to affected pages, and each candidate retains its page and available
   region provenance plus engine versions.
2. Given approved golden statements representing at least three materially
   different layouts, when extracted, then all required available statement
   header fields and at least 98 percent of transaction rows are detected, at
   least 97 percent of detected transaction dates and amounts exactly match the
   labelled values, and every mismatch is exposed for review rather than
   silently committed.
3. Given balancing and non-balancing statements, when validation runs, then
   valid arithmetic passes within documented rounding rules and inconsistent
   statements produce a blocking error or acknowledged warning according to the
   plugin rule.
4. Given missing, invalid and unknown confidence values, when the result is
   validated, then missing remains visibly unavailable, out-of-range or unknown
   representations are rejected, and none is displayed as high confidence.
5. Given a document containing secret-shaped values and embedded instructions,
   when extraction runs, then instructions cannot change application behaviour
   and prohibited values are blocked from ordinary domain mappings.

### AC-4: Review and atomic commit

1. Given an extraction with high-, medium-, low- and unavailable-confidence
   fields, errors, warnings and inferred values, when review opens, then each
   state is distinguishable without colour, each value links to available
   evidence and no commit is possible while blocking errors remain.
2. Given a user edits one value, rejects another, selects an entity and creates
   one new entity, when final confirmation appears, then it lists those exact
   changes; cancelling writes none of them and confirming writes all of them in
   one transaction.
3. Given a target entity changes after review begins, when the user confirms,
   then commit is blocked by the stale expected version and requires refreshed
   review rather than overwriting the concurrent change.
4. Given a saved draft and application restart, when the user resumes, then the
   same evidence, candidates, corrections, validation and resolution state is
   restored without duplicating ingestion.

### AC-5: Entity resolution

1. Given a statement for an existing account and owner, when candidates are
   resolved, then compatible existing entities are proposed with matching and
   conflicting attributes explained and no entity is linked automatically.
2. Given two plausible accounts, no plausible account and a possible duplicate
   new entity, when reviewed, then the user can respectively choose, search,
   create or leave an optional role unresolved, and a duplicate warning appears
   before creation.
3. Given two Clanns with similar entities, when resolving an item in one Clann,
   then no candidate, count or attribute from the other Clann is returned.

### AC-6: Evidence, encryption, redaction and deletion

1. Given retained evidence, when the external source changes or is deleted,
   then the evidence opens as the original admitted bytes and its checksum still
   verifies.
2. Given a one-byte modification to retained evidence, when it is opened or
   used for reprocessing, then verification fails, the object is quarantined,
   derived commit is blocked and the error reveals no document content.
3. Given encryption is enabled, when storage is inspected outside Eolas, then
   original bytes, derived text and thumbnails are not recoverable as plaintext;
   documented key loss and recovery tests produce the specified result.
4. Given a redaction over visible text with an underlying text layer and
   metadata, when a redacted derivative is created, then automated verification
   finds the selected content in none of those locations or refuses to label
   the derivative successfully redacted.
5. Given evidence linked to committed records, pending work and a backup, when
   deletion is requested, then the UI identifies all retained consequences,
   applies the approved retention decision and reports secure-deletion limits
   without claiming guaranteed physical erasure.

### AC-7: History, provenance and recovery

1. Given completed, skipped, rejected, cancelled and failed items, when history
   is queried, then each contains the required timestamps, component versions,
   confidence, decisions and outcome appropriate to its lifecycle.
2. Given any field committed from an import, when provenance is followed, then
   the exact attempt, candidate and retained page or source locator can be found;
   reverse lookup from the import lists every affected record.
3. Given an extraction re-run with a newer plugin, when it completes, then both
   attempts and versions remain visible and earlier decisions and committed
   records are unchanged until a new change set is confirmed.
4. Given forced termination during evidence admission, review persistence and
   commit, when Eolas restarts, then each item is either wholly valid and
   resumable/committed or safely rolled back, with no duplicate record or valid-
   looking partial object.

### AC-8: Extensibility and isolation

1. Given a fictional insurance-policy plugin implemented only against the
   published API, when installed into the conformance harness, then it can
   classify, extract, validate, render schema-driven review, resolve entities
   and commit evidence-linked facts without any core source modification.
2. Given an incompatible, malformed, timed-out and crashing plugin, when each is
   loaded or invoked, then it is rejected or isolated with a stable error and
   other plugins, jobs and stored records remain usable.
3. Given a previously used plugin is disabled or removed, when history and
   committed records are opened, then they remain readable; only reprocessing
   that actually needs the plugin is unavailable and says why.

### AC-9: Security, privacy and offline operation

1. Given network access is denied and network calls are monitored, when all
   Phase 1 scenarios run, then they complete without attempted DNS, socket or
   remote-service access.
2. Given representative private fixture markers in document text, filenames,
   paths and candidate values, when normal operation and failures are logged,
   then automated scans find none of those markers in logs, telemetry or crash
   summaries.
3. Given a plugin requests unrelated files, network access, another Clann or
   direct evidence writes through framework capabilities, when invoked, then
   every request is denied and audited without disclosing whether unrelated
   data exists.
4. Given missing consent for a future remote processor, when local extraction
   fails or is low confidence, then no data leaves the device and the user is
   offered local correction, retry or cancellation.

### AC-10: Performance, accessibility and cross-platform behaviour

1. The admission, native-PDF, OCR, batch and history benchmarks meet every
   threshold in the non-functional requirements on recorded reference hardware
   in three consecutive release-candidate runs.
2. Given 100 queued documents and cancellation during active OCR, when the batch
   runs, then concurrency stays within its configured bound, the UI remains
   responsive, active work cancels within 5 seconds after the current safe
   cancellation point, and committed items remain intact.
3. Given keyboard-only operation, a supported screen reader, 200 percent zoom
   and high-contrast mode, when a user completes import, classification
   override, review, entity creation and commit, then every action, status,
   error and evidence control is perceivable and operable on Linux, macOS and
   Windows.
4. Given equivalent fixture sets on each supported desktop platform, when the
   conformance suite runs, then lifecycle, validation, checksum, domain mapping
   and history results are equivalent apart from documented platform metadata.

### AC-11: Documentation and release readiness

1. Given a developer who has not modified the core, when following the plugin
   guide, then they can build the fictional conformance plugin and pass the
   published contract suite using only public interfaces.
2. Given a Phase 1 user, when reading the user guide, then they can identify the
   supported formats, local-processing guarantee, confidence limitations,
   evidence and encryption state, redaction limits, backup implications and
   deletion consequences before relying on the feature.
3. A release candidate cannot be approved until the threat model has no
   unresolved critical or high risks, all acceptance tests pass, extraction
   accuracy and calibration results are published, and known limitations are
   present in the supported-document matrix.

## Out of scope

Phase 1 does not include:

- importers for document families other than bank statements;
- email inbox, scanner-device, camera, watched-folder, web-portal or cloud-drive
  ingestion;
- images or office-document formats except page images already contained in a
  supported PDF;
- server-side processing, cloud AI, remote OCR, cloud storage, synchronisation
  or transmission of private document content;
- automatic commitment, automatic entity merging or background extraction that
  changes canonical records without review;
- a financial ledger, transaction categorisation, spending analytics, bank-feed
  integration, Open Banking or payment initiation;
- legal, financial, tax, identity or fraud advice, authenticity guarantees or
  verification with an issuer;
- storing passwords, PINs, recovery codes, authentication tokens, full payment-
  card data or security answers;
- learning from user corrections, shared training datasets or uploading
  correction data;
- third-party plugin marketplace, remote plugin download or arbitrary
  untrusted-plugin execution;
- guaranteed physical erasure from SSDs, backups, snapshots or externally
  synchronised copies; or
- changing the shared Eolas domain model solely to mirror one document layout.

## Dependencies and decisions

### Requirements

- Requires [002](002-privacyAndSecurityModel.md) for classification, local
  private storage, minimisation, sharing, retention and disposal controls.
- Related to [007](007-legalDocumentCustodyAndAccess.md), which distinguishes
  authoritative legal-document custody from copies and references.
- Future document-specific importers should each receive a separate requirement
  and declare this framework as a dependency.

### Architecture Decision Records

- [ADR-0002](../../adr/002-offlineFirst.md): required offline operation.
- [ADR-0003](../../adr/003-neverStorePasswords.md): prohibited secret storage.
- [ADR-0004](../../adr/004-publicTemplatesPrivateData.md): separation of public
  project assets and private household data.
- [ADR-0005](../../adr/005-informationClassification.md): classification and
  fail-closed handling.
- [ADR-0006](../../adr/006-sharedDomainModel.md): shared model across interfaces.
- [ADR-0007](../../adr/007-knowledgeBeforeDocuments.md): imported documents are
  evidence for knowledge, not the organising model.
- [ADR-0008](../../adr/008-handbookAsProjection.md): imported knowledge can feed
  projections without making a projection canonical.
- [ADR-0011](../../adr/011-platformPrivateDataRoot.md): platform-resolved private
  storage and no implicit hosted storage.

### Decisions still required

Before implementation, ADRs must settle:

- plugin trust, packaging, discovery and process-isolation policy;
- PDF parser and local OCR engines, resource isolation and supported languages;
- evidence encryption, key custody, recovery, rotation and cryptographic
  erasure;
- evidence and audit retention defaults;
- confidence scale, calibration method and initial bank-statement thresholds;
  and
- exact mapping of reviewed bank-statement facts into the evolving shared
  domain schema.

## Verification

- Run the full test strategy against native, scanned, mixed, malformed,
  malicious, duplicate and encrypted fictional PDFs.
- Record benchmark hardware, operating system, dependency and plugin versions,
  fixture-set version, accuracy metrics and confidence calibration results.
- Complete privacy, security, accessibility and cross-platform reviews before
  release approval.
- Demonstrate the fictional insurance-policy conformance plugin to prove that
  core changes are unnecessary for a new document family.
- Trace every acceptance criterion to automated tests, manual evidence or a
  documented release gate in the eventual implementation plan.

## Traceability

- Implementation: shared Phase 1 import targets (typed identities, provenance, evidence references, observations and atomic command/store boundary); import framework pending
- Tests: shared-kernel, storage, security, graph and capture-adapter conformance tests implemented; domain acceptance tests pending
- Documentation: [product vision](../../../documentation/productVision.md),
  [principles](../../../documentation/principles.md),
  [domain model](../../../documentation/domainModel.md),
  [glossary](../../../documentation/glossary.md),
  [information classification](../../../documentation/informationClassification.md),
  [privacy and security](../../../documentation/privacyAndSecurity.md)
- Principles: [P-001, P-002, P-003, P-004, P-005, P-007, P-008, P-009 and
  P-010](../../../documentation/principles.md)
- Pull request: pending
- Agent runs: 2026-07-31 - Codex, initial requirements specification from the
  maintainer's Document Import Framework brief.

## Change history

- 2026-07-31: created as the Phase 1 Document Import Framework requirement,
  including the bank-statement proof plugin and generic extension contracts.
