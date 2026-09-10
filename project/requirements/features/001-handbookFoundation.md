# 001: Handbook foundation

Priority: critical  
Owner: Andy Wilson

## Status

ToDo

## Outcome

As a household member, I need to understand the handbook's purpose, limits and
safe use before adding information, so that I can begin without depending on an
application or needing to understand Markdown or file manipulation.

## Context

The handbook needs a trustworthy, application-independent foundation. It must
distinguish reusable public guidance from a private completed handbook and make
clear that it is not legal, medical or financial advice.

## Scope

- Purpose, audience, usage, storage, maintenance and limitations.
- Human-readable source and a practical print-oriented structure.
- Direct human editing and tool-assisted creation or maintenance of the same
  Markdown source through automation, web, mobile, desktop or CLI interfaces.
- Tool-assisted projection from structured private household records, currently
  stored as YAML beneath `~/eolas/clanns/`, into human-readable Markdown without
  requiring users to understand either file format.
- Guided interfaces that hide Markdown syntax, file paths and file operations
  from ordinary users while preserving direct editing as an expert or fallback
  capability.
- Safe first steps and links to privacy guidance.

## Out of scope

- A web or desktop application.
- Detailed content for every handbook topic.

## Acceptance criteria

1. Given only the Getting Started section, when a first-time reader reviews it,
   then they can locate an explicit statement of the handbook's purpose,
   intended audience and limitations, and an ordered set of safe first steps
   covering creation, storage, sharing, review and disposal.
2. Given a fresh local checkout with no network connection, when a reviewer
   opens the canonical handbook source and follows its essential references,
   then the content remains readable in a text editor and all essential
   references resolve locally; when the same source is rendered through the
   documented local print path, it produces a representative A4 PDF or paper
   copy with no clipped text and with headings, safety warnings and
   classification labels still visible.
3. Given a review of the foundation source and its instructions, when required
   dependencies are inventoried, then no step needed to read, maintain or print
   the handbook requires an application, network connection, vendor account or
   subscription; any optional service is labelled optional and has an offline,
   vendor-neutral alternative. When optional automation, web, mobile, desktop
   or CLI tooling creates or updates a handbook, it reads and writes the same
   documented Markdown source without introducing a proprietary canonical copy;
   the user completes the workflow without needing to understand Markdown
   syntax, YAML syntax, storage layout or file operations. Where the workflow
   captures structured household knowledge, the interface updates the shared
   structured records and regenerates or updates the Markdown projection rather
   than maintaining an unrelated duplicate value.

## Dependencies and decisions

### Requirements

- Requires [002](002-privacyAndSecurityModel.md).
- Enables 003, 004, 005 and 006.
- Remaining dependency: requirement 002 must be ready before this requirement
  can move to `InProgress`.

### Architecture Decision Records

- [001](../../adr/001-handbookBeforeSoftware.md) — Handbook before software
- [002](../../adr/002-offlineFirst.md) — Offline first
- [004](../../adr/004-publicTemplatesPrivateData.md) — Public templates, private data
- [008](../../adr/008-handbookAsProjection.md) — Handbook as projection
- [009](../../adr/009-markdownHandbookSource.md) — **Accepted**: UTF-8 Markdown as canonical source for the handbook projection; PDF and paper are derived experiences; household knowledge model is independent of document format.

## Verification

- Criterion 1: a content-review checklist records the exact heading or passage
  covering purpose, audience, limitations, creation, storage, sharing, review
  and disposal; any missing item fails the criterion.
- Criterion 2: an offline link check records all essential local references,
  and a representative A4 print review records the renderer and command used,
  page size, absence of clipped text, and visibility of headings, warnings and
  classification labels.
- Criterion 3: a dependency inventory records every required tool, account,
  service and network dependency; any required application, vendor account,
  subscription or connection fails the criterion. Optional services must have
  a documented offline, vendor-neutral alternative. Interface review confirms
  that automation, web, mobile, desktop and CLI workflows use shared core file
  operations against the documented Markdown source and do not create a second
  proprietary source of truth. A representative user walkthrough confirms that
  creating and updating content requires no manual Markdown editing, path entry
  or direct file manipulation. An integration review confirms that structured
  values are written once to the private YAML record and consistently projected
  into Markdown, with no independently maintained duplicate value.

## Traceability

- Implementation: [Getting Started](../../../handbook/01-GettingStarted.md)
- Tests: pending
- Documentation: [product vision](../../../documentation/productVision.md)
- Pull request: pending
- Agent runs: 2026-07-28 — Codex, refinement role, criteria 1–3, using
  [refinement prompt](../prompt/001-handbookFoundation.md); result recorded in
  this requirement and proposed ADR-0009.

## Change history

- 2026-07-22: created as `HB-001-HandbookFoundation.yaml`.
- 2026-07-28: migrated to permanent numeric Markdown path; outcome and evidence retained.
- 2026-07-28: refined criteria and verification evidence; proposed Markdown as
  the canonical handbook-projection source through ADR-0009.
- 2026-07-28: clarified that optional automation and web, mobile, desktop or
  CLI interfaces manipulate the same human-editable Markdown source.
- 2026-07-28: clarified that ordinary users are not expected to understand or
  directly manipulate Markdown files.
- 2026-07-28: distinguished private structured YAML records from the Markdown
  handbook projection and required tooling to hide both formats from users.
- 2026-07-28: project maintainer accepted ADR-0009; requirement remains `ToDo`
  pending requirement 002 and readiness review.
