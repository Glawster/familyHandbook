# Refine requirement 005: Annual review process

Requirement: 005 — `project/requirements/features/005-annualReviewProcess.md`  
Role: refine

Read the requirement and applicable repository instructions before changing
anything. Refine acceptance criteria 1–3 only; do not write the final checklist
or add software reminders. Preserve offline, vendor-neutral use and the
exclusion against recording secrets during review.

Propose a bounded set of significant life events that should trigger immediate
review and distinguish them from the annual cycle. Apply requirements 001–003
and ADR-0002, ADR-0003, ADR-0007 and ADR-0008. Make coverage, obsolete-copy
handling and fictional walkthrough evidence independently repeatable.

Changes may be made to:

- `project/requirements/features/005-annualReviewProcess.md`
- `project/requirements/requirementsIndex.md`
- `project/adr/` only if a consequential new or superseding decision is required

Verify with `pytest`, handbook-topic coverage review, privacy review, a complete
criterion-to-verification mapping review and `git diff --check`.

Leave the requirement in `ToDo` if event selection requires stakeholder
agreement. Do not infer automated reminders or vendor services into scope.

Handoff with changed files and reasons, proposed event triggers, criterion-to-
evidence mapping, commands and results, assumptions, risks and unresolved items.
