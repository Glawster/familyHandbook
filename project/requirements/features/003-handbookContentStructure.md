# 003: Handbook content structure

Priority: high  
Owner: project maintainers

## Status

ToDo

## Outcome

As a handbook owner or contributor, I need predictable, safe and adaptable
sections so that information is easy to find and maintain without duplication
or jurisdiction lock-in.

## Context

The eleven existing chapters need a shared structure derived from one
technology-independent domain model. Prompts should explain value, safe content
and review timing while keeping classifications visible.

## Scope

- Section taxonomy, prompt pattern, cross-references and optionality.
- A repeatable inventory mapping each existing heading and prompt to one primary
  handbook location, shared domain concepts and any duplicate appearances.
- A common section pattern covering purpose, classification, safe recording,
  prohibited content, prompts, optionality, references and review triggers.
- Jurisdiction-neutral core with separable UK-specific guidance.
- Consistent accessible headings, terminology and glossary links.
- Mapping existing chapters to primary sections and domain concepts.
- An emergency-summary projection derived from shared household knowledge.

## Out of scope

- Fully authored guidance for every topic.
- Application navigation or data-entry screens.

## Acceptance criteria

1. Given the eleven existing handbook files, when an inventory reviewer records
   every heading and prompt, then each row identifies its source path and
   heading, topic identifier, one primary handbook location, related domain
   concepts, duplicate appearances, required cross-references and disposition;
   no source heading or prompt is omitted and every duplicate has one recorded
   primary location.
2. Given one representative chapter selected after the inventory, when it is
   structured using the common section pattern, then every practical section
   states its purpose, default classification, why the information helps, what
   is safe and prohibited to record, applicable/unknown/action-required states,
   prompts, cross-references and review triggers, and passes the requirement
   002 privacy checks plus a plain-language review.
3. Given every jurisdiction-specific term, process and service found by the
   inventory, when the UK presentation layer is removed or replaced with a
   fictional jurisdiction layer, then the same canonical domain concepts,
   identifiers and relationships remain valid and no core structured-record
   schema or handbook topic ownership changes.
4. Given the inventory and representative chapter, when specialised legal,
   care, financial, technical or project terminology is reviewed, then its
   first necessary use links to one plain-language glossary definition and that
   definition identifies material jurisdiction differences; all internal links
   resolve offline and no conflicting duplicate definition exists.
5. Given the section and field inventory, when it is reviewed against ADR-0005
   and requirement 002, then every section has one recorded default
   classification with rationale, every stricter field override is explicit,
   no field weakens its section default, and missing or unknown classifications
   follow requirement 002's fail-closed behaviour.
6. Given every inventoried topic, when it is reviewed against the documented
   domain model, then it maps to at least one existing concept and relationship
   or to a uniquely identified model-gap record containing the topic, user need,
   missing concept or relationship, affected projections and reviewer decision;
   no new domain concept is inferred solely from a chapter heading.

## Dependencies and decisions

### Requirements

- Requires [001](001-handbookFoundation.md) and
  [002](002-privacyAndSecurityModel.md); enables 004, 005 and 006.

### Architecture decision records

- [005](../../adr/005-informationClassification.md) — section defaults and
  stricter field classifications remain visible in every projection.
- [007](../../adr/007-knowledgeBeforeDocuments.md) — chapter structure does not
  define the underlying household-knowledge model.
- [008](../../adr/008-handbookAsProjection.md) — handbook chapters, emergency
  summaries and annual reviews are projections of shared knowledge.
- [009](../../adr/009-markdownHandbookSource.md) — Markdown is the canonical
  source for the handbook projection, not the private knowledge model.

### Applied decisions

- Emergency information is an emergency-summary projection selected from shared
  knowledge. `handbook/02-EmergencyPlan.md` remains the established source path
  for guidance and projection rules, but must not become an independently
  maintained copy of contacts, care needs, properties or instructions.
- A contact value is maintained once as shared `Contact` knowledge, or as
  `Professional` knowledge when it represents a professional service. Chapters
  own contextual guidance and cross-references, while emergency and other
  projections select the shared value appropriate to their audience.

## Verification

- Criterion 1: compare the inventory mechanically with all headings and prompts
  from `handbook/*.md`; record total source items, mapped items, duplicates and
  dispositions, and fail if the counts do not reconcile.
- Criterion 2: use a checklist containing every common-pattern element and
  record requirement 002 privacy results, reading level or plain-language
  findings, reviewer and date for the selected representative chapter.
- Criterion 3: record all jurisdiction-specific source passages, their canonical
  concepts and replacement result; compare domain identifiers, relationships
  and structured schema before and after replacement and fail on core changes.
- Criterion 4: record each specialised term, source location, glossary anchor,
  plain-language review and jurisdiction note; run the offline internal-link
  check and fail on missing, broken or conflicting definitions.
- Criterion 5: record section default, rationale, field overrides and reviewer;
  test upward override, attempted downward override, missing metadata and an
  unknown value against requirement 002.
- Criterion 6: record topic-to-concept and relationship mappings; give every gap
  a stable inventory identifier and explicit review disposition, and fail if any
  topic has neither a mapping nor a reviewed gap.
- Dependency review: confirm requirements 001 and 002 are ready before moving
  this requirement to `InProgress`; confirm the inventory and exemplar preserve
  ADR-0005, ADR-0007, ADR-0008 and ADR-0009.

## Traceability

- Implementation: [handbook](../../../handbook/01-GettingStarted.md)
- Tests: pending
- Documentation: [domain model](../../../documentation/domainModel.md), [glossary](../../../documentation/glossary.md), [information classification](../../../documentation/informationClassification.md)
- Pull request: pending
- Agent runs: 2026-07-28 — Codex, refinement role, criteria 1–6, using
  [refinement prompt](../prompt/003-handbookContentStructure.md); result recorded
  in this requirement.

## Change history

- 2026-07-22: created as `HB-003-HandbookContentStructure.yaml`.
- 2026-07-28: migrated to permanent numeric Markdown path; outcome and evidence retained.
- 2026-07-28: refined the inventory, exemplar, portability, glossary,
  classification and domain-mapping evidence; applied ADR-0007 and ADR-0008 to
  emergency information and shared contacts.
