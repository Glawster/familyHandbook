# Requirements

Next available number: 020

This directory is the source of truth for specific outcomes clanneolas.com
intends to deliver and why. Requirements can govern handbook content, project
processes or future software. They describe outcomes and constraints before
implementation and must distinguish current behaviour from planned work.

## ToDo

- [001 — Handbook foundation](features/001-handbookFoundation.md) (legacy ID: HB-001)
- [002 — Privacy and security model](features/002-privacyAndSecurityModel.md) (legacy ID: HB-002)
- [003 — Handbook content structure](features/003-handbookContentStructure.md) (legacy ID: HB-003)
- [004 — Fictional example household](features/004-fictionalExampleHousehold.md) (legacy ID: HB-004)
- [005 — Annual review process](features/005-annualReviewProcess.md) (legacy ID: HB-005)
- [006 — Getting Started guide](features/006-gettingStartedGuide.md) (legacy ID: HB-006)
- [007 — Legal document custody and access](features/007-legalDocumentCustodyAndAccess.md) (legacy ID: APP-001)
- [008 — Document Import Framework](features/008-documentImportFramework.md)
- [019 — Secure Clann access and synchronisation](features/019-secureClannAccessAndSync.md)

## InProgress

- [009 — Banking module](features/009-bankingModule.md) — Banking Core aggregates, identifiers, parties, roles, balances and typed capture implemented; money movements, payment arrangements, workflows and projections remain
- [010 — Credit cards](features/010-creditCards.md) — shared Phase 1 kernel and CLI input adapter implemented; full domain workflows and projections remain
- [011 — Mortgages](features/011-mortgages.md) — shared Phase 1 kernel and CLI input adapter implemented; full domain workflows and projections remain
- [012 — Loans and other borrowing](features/012-loans.md) — shared Phase 1 kernel and CLI input adapter implemented; full domain workflows and projections remain
- [013 — Investments](features/013-investments.md) — shared Phase 1 kernel and CLI input adapter implemented; full domain workflows and projections remain
- [014 — Pensions](features/014-pensions.md) — shared Phase 1 kernel and CLI input adapter implemented; full domain workflows and projections remain
- [015 — Insurance](features/015-insurance.md) — shared Phase 1 kernel and CLI input adapter implemented; full domain workflows and projections remain
- [016 — Taxation](features/016-taxation.md) — shared Phase 1 kernel and CLI input adapter implemented; full domain workflows and projections remain
- [017 — Subscriptions and recurring services](features/017-subscriptions.md) — shared Phase 1 kernel and CLI input adapter implemented; full domain workflows and projections remain
- [018 — Utilities and essential household services](features/018-utilities.md) — shared Phase 1 kernel and CLI input adapter implemented; full domain workflows and projections remain

## Completed

None.

## Repository-specific guidance

This index follows the managed
[requirements process](../../documentation/requirementsManagement.md). The six
existing `HB` records were assigned permanent numeric paths during the 2026-07-28
migration. Their former IDs remain in each record and in this index so older
links and history can be interpreted.

All requirements remain under `features/` when their status changes. Do not
move completed or retired records. Allocate the next number here and update it
in the same change that creates a requirement.

## Directory layout

- `../project.yaml` defines the shared purpose, scope, principles, risks and
  milestones for the wider project.
- `../../documentation/principles.md` explains the north-star principles referenced by
  stable ID from each requirement.
- `features/` contains all requirements at every lifecycle stage.
- `prompt/` contains flat durable prompts matched to requirements by filename;
  reusable adapters live in `prompt/adapters/`.
- `../adr/` contains architecture decision records (ADRs) that affect multiple
  requirements.
- `templates/requirement.md` is copied when proposing a requirement.
- `../reviews/` contains point-in-time assessments and reviews.

## Naming conventions

- Markdown filenames generally use camelCase, except `README.md` and
  records whose stable identifier is deliberately exposed in the filename.
- Requirement filenames use `ddd-conciseCamelCaseName.md`. Numbers are
  repository-wide, permanent and never reused.
- ADR files use `ddd-shortName.md`, for example `005-canonicalFormat.md`.
  Their repository-wide numeric identifiers are permanent and never reused.
- Dates use ISO 8601 `YYYY-MM-DD` format.
- Requirements use normative words deliberately: **must** is mandatory,
  **should** is the expected default, and **may** is optional.

## Priority and status

Priorities are `critical`, `high`, `medium` or `low`. `critical` is reserved
for safety, privacy or foundational work that blocks responsible progress.

The index and each record use `ToDo`, `InProgress` or `Completed`. A completed
entry may also state a disposition such as retired, rejected or superseded.

## Review expectations

Reviewers should look for duplicate requirements, contradictions, accidental
UK or vendor coupling, private data, inaccessible language and claims that get
ahead of implementation. A feature without a credible benefit to at least one
documented persona is not ready for approval. Reviewers must also test the
outcome against every linked principle rather than treating principle IDs as
labels. Changes to project principles require explicit review and normally an
ADR. Feature requirements should link both to the
project principles they satisfy and to the relevant handbook, documentation,
tests or future code paths.

Presentation requirements are legitimate when they concern matters such as
readability, navigation, accessibility or print layout. They must describe a
projection of shared knowledge rather than introduce a competing source of
truth.

No requirement file contains private household data. Fictional examples must
be clearly labelled, safe to publish and free of usable credentials or
realistic identifiers.

## Prompt index

<!-- OMP-PROMPT-INDEX-BEGIN -->
- [001-handbookFoundation](prompt/001-handbookFoundation.md)
- [002-privacyAndSecurityModel](prompt/002-privacyAndSecurityModel.md)
- [003-handbookContentStructure](prompt/003-handbookContentStructure.md)
- [004-fictionalExampleHousehold](prompt/004-fictionalExampleHousehold.md)
- [005-annualReviewProcess](prompt/005-annualReviewProcess.md)
- [006-gettingStartedGuide](prompt/006-gettingStartedGuide.md)
- [007-legalDocumentCustodyAndAccess](prompt/007-legalDocumentCustodyAndAccess.md)
<!-- OMP-PROMPT-INDEX-END -->
