# 006: Getting Started guide

Priority: high  
Owner: project maintainers

## Status

ToDo

## Outcome

As a handbook owner or trusted helper, I need clear first steps and boundaries
so that I can begin, share, protect and maintain the handbook safely without
understanding all of it at once.

## Context

The opening chapter should provide a short route through purpose, safe setup,
trusted access and ongoing review. It must distinguish awareness, practical
help and formal legal authority, and remain useful in Markdown and on paper.

## Scope

- Purpose, audience, limitations and professional-advice boundary.
- Prioritised first steps, incomplete and not-applicable states, and follow-up actions.
- Annual and significant-change reviews.
- Trusted-person awareness, access and collaboration without implying authority.
- Paper and digital storage, controlled sharing, backup and disposal.
- Prominent do-not-store guidance and safe references to protected material.

## Out of scope

- Tailored legal, medical, financial or security advice.
- Product or vendor selection.
- Detailed household data collection or an application onboarding flow.

## Acceptance criteria

1. A first-time reader can explain the handbook's purpose and limits and choose a first section.
2. The guide links annual and significant-change review guidance to the annual review process.
3. It distinguishes awareness, trusted access and formal legal authority.
4. Paper and digital storage, sharing, backup and disposal align with the privacy model.
5. A prominent do-not-store list includes passwords, PINs, recovery codes, full payment-card security details and private cryptographic keys.
6. Sarah, David and Morgan can complete scenario walkthroughs using the guide and referenced project guidance.
7. The guide is understandable and navigable in source Markdown and a representative printed form.

## Dependencies and decisions

- Requires [001](001-handbookFoundation.md), [002](002-privacyAndSecurityModel.md) and [003](003-handbookContentStructure.md); related to 005.
- ADRs: [ADR-0001](../../adr/001-handbookBeforeSoftware.md), [ADR-0002](../../adr/002-offlineFirst.md), [ADR-0003](../../adr/003-neverStorePasswords.md), [ADR-0004](../../adr/004-publicTemplatesPrivateData.md), [ADR-0007](../../adr/007-knowledgeBeforeDocuments.md), [ADR-0008](../../adr/008-handbookAsProjection.md).
- Open questions: shortest useful first session, named review triggers and the representative print check.

## Verification

- Task-based content, link, role, glossary, privacy and prohibited-information reviews.
- Persona walkthroughs and representative accessibility/print review.

## Traceability

- Implementation: [Getting Started](../../../handbook/01-GettingStarted.md), [Annual Review](../../../handbook/11-AnnualReview.md)
- Tests: pending
- Documentation: [domain model](../../../documentation/domainModel.md), [glossary](../../../documentation/glossary.md), [privacy and security](../../../documentation/privacyAndSecurity.md), [personas](../../../documentation/personas/personasIndex.md)
- Pull request: pending
- Agent runs: None

## Change history

- 2026-07-22: created as `HB-006-GettingStartedGuide.yaml`.
- 2026-07-28: migrated to permanent numeric Markdown path; outcome and evidence retained.
