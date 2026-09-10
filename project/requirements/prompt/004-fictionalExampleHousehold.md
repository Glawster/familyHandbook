# Refine requirement 004: Fictional example household

Requirement: 004 — `project/requirements/features/004-fictionalExampleHousehold.md`  
Role: refine

Read the requirement and applicable repository instructions before changing
anything. Refine acceptance criteria 1–3 only; do not create the example
household. Preserve the exclusions against real, lightly anonymised or
realistically identifying information.

Propose the smallest representative scenario set that demonstrates varied
family, care, accessibility and practical needs without implying one universal
family form. Apply requirements 002 and 003 and ADR-0003, ADR-0004 and ADR-0007.
Define repeatable privacy, chapter-coverage and separation reviews, including
how conspicuous non-values will be assessed.

Changes may be made to:

- `project/requirements/features/004-fictionalExampleHousehold.md`
- `project/requirements/requirementsIndex.md`
- `project/adr/` only if a consequential new or superseding decision is required

Verify with `pytest`, a prohibited-data and re-identification risk review, a
criterion-to-verification mapping review and `git diff --check`.

Leave the requirement in `ToDo` if scenario selection needs stakeholder
agreement. Do not include usable credentials, account data or realistic private
identifiers, even as examples.

Handoff with changed files and reasons, proposed scenarios, criterion-to-
evidence mapping, commands and results, assumptions, risks and unresolved items.
