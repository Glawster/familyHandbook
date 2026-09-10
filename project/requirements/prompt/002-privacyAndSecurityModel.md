# Refine requirement 002: Privacy and security model

Requirement: 002 — `project/requirements/features/002-privacyAndSecurityModel.md`  
Role: refine

Read the requirement and applicable repository instructions before changing
anything. Refine acceptance criteria 1–4 only; do not create private household
storage or collect sample household data. Preserve the exclusions against
security guarantees and storage of credentials or equivalent secrets.

Resolve or frame for stakeholder decision whether private copies should live
outside the repository or in a warned, ignored location. Test the proposal
against ADR-0003, ADR-0004 and ADR-0005. Define measurable verification for the
classification ordering, missing-classification default, prohibited-data scan,
and vendor-neutral paper and digital handling guidance.

Changes may be made to:

- `project/requirements/features/002-privacyAndSecurityModel.md`
- `project/requirements/requirementsIndex.md`
- `project/adr/` only if a consequential new or superseding decision is required

Verify with `pytest`, a privacy threat review, a criterion-to-verification
mapping review and `git diff --check`.

If stakeholder choice is required, leave the requirement in `ToDo`. Do not add
realistic identifiers, credentials, private data or an unapproved storage path.

Handoff with changed files and reasons, proposed resolution, criterion-to-
evidence mapping, commands and results, assumptions, risks and unresolved items.
