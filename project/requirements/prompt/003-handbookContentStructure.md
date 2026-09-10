# Refine requirement 003: Handbook content structure

Requirement: 003 — `project/requirements/features/003-handbookContentStructure.md`  
Role: refine

Read the requirement and applicable repository instructions before changing
anything. Refine acceptance criteria 1–6 only; do not author all chapters or
design application navigation. Preserve the established handbook filenames.

Resolve or frame decisions for the form of emergency information and the
primary home of overlapping contacts. Apply ADR-0005, ADR-0007 and ADR-0008,
and treat requirements 001 and 002 as dependencies. Make the proposed inventory,
exemplar, portability, glossary, classification and domain-mapping evidence
specific enough that independent reviewers can repeat it.

Changes may be made to:

- `project/requirements/features/003-handbookContentStructure.md`
- `project/requirements/requirementsIndex.md`
- `project/adr/` only if a consequential new or superseding decision is required

Verify with `pytest`, a dependency and ADR consistency review, a complete
criterion-to-verification mapping review and `git diff --check`.

Leave the requirement in `ToDo` when stakeholder choices remain. Do not invent
chapter mappings or classify fields without recorded review evidence.

Handoff with changed files and reasons, proposed resolutions, criterion-to-
evidence mapping, commands and results, assumptions, risks and unresolved items.
