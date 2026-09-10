# Refine requirement 001: Handbook foundation

Requirement: 001 — `project/requirements/features/001-handbookFoundation.md`  
Role: refine

Read the requirement and applicable repository instructions before changing
anything. Refine acceptance criteria 1–3 only; do not implement handbook
content. Preserve the web/desktop application and detailed-topic exclusions.

Resolve or turn into an explicit decision the open question about the canonical
open source format for printable handbook content. Assess the answer against
ADR-0001, ADR-0002, ADR-0004 and ADR-0008 and requirement 002. Ensure every
criterion names observable evidence for purpose, offline readability, print use
and freedom from application or vendor dependencies.

Changes may be made to:

- `project/requirements/features/001-handbookFoundation.md`
- `project/requirements/requirementsIndex.md`
- `project/adr/` only if a consequential new or superseding decision is required

Verify with:

- `pytest`
- a requirement/index status consistency review
- a criterion-to-verification mapping review
- `git diff --check`

If stakeholder choice is required, leave the requirement in `ToDo` and report
the precise decision. Do not infer approval or move it to `InProgress`.

Handoff with changed files and reasons, proposed resolution, criterion-to-
evidence mapping, commands and results, assumptions, risks and unresolved items.
