# 002: Privacy and security model

Priority: critical  
Owner: project maintainers

## Status

ToDo

## Outcome

As a handbook owner or trusted reader, I need clear rules for what to record
and what only to reference, so that the handbook does not create avoidable
privacy or security harm.

## Context

The public project and private household copies need an explicit boundary.
Guidance must cover classification, minimisation, safe references, access,
storage, sharing, backup and disposal without guaranteeing a storage method.

## Scope

- Public, Private, Confidential and Highly Confidential classification.
- Paper and digital safeguards, including stricter field-level classification.
- Data minimisation, controlled access, sharing, backup, recovery, retention and
  secure disposal guidance for complete and obsolete copies.
- Application-managed private digital Clann records stored outside the public
  repository beneath a platform-resolved private `eolasDataRoot`.
- Safe references to protected documents and credential stores.
- Explicitly fictional, publishable examples.

## Out of scope

- Guaranteeing the security of a chosen storage method.
- Storing or managing passwords, PINs, recovery codes or similar secrets.

## Acceptance criteria

1. Given a proposed section or field and its intended completed value, when an
   author follows the classification decision process, then they assign exactly
   one of `Public`, `Private`, `Confidential` or `Highly Confidential`, record
   the reason, and apply the stricter field classification whenever it exceeds
   the section default; uncertainty is escalated for review rather than assigned
   a less restrictive value.
2. Given the tracked repository and its generated-test fixtures, when automated
   prohibited-name and secret-pattern scans and a manual privacy review are
   performed, then no real household record, usable credential, password, PIN,
   recovery code, authentication token, private cryptographic key or realistic
   private identifier is present; every example is conspicuously fictional and
   non-usable.
3. Given the privacy guidance, when a reviewer evaluates paper and digital
   workflows, then it covers data minimisation, default storage, access,
   controlled sharing, backup, recovery, obsolete-copy handling and secure
   disposal; application-managed private digital Clann records default to
   `<eolasDataRoot>/clanns/` using the platform's private application-data
   convention, no workflow requires a vendor, and no method is described as
   risk-free or guaranteed secure.
4. Given classification metadata, when a person or tool interprets it, then the
   only accepted machine values are `public`, `private`, `confidential` and
   `highlyConfidential` in that increasing order; an unknown value is rejected,
   while a missing value is handled as `highlyConfidential` and blocked from
   sharing or export until explicitly classified.

## Dependencies and decisions

- Enables 001, 003, 004, 005 and 006.
- ADRs:
  - [003](../../adr/003-neverStorePasswords.md),
  - [004](../../adr/004-publicTemplatesPrivateData.md),
  - [005](../../adr/005-informationClassification.md).
- Superseded decision:
  [010](../../adr/010-privateClannDataLocation.md) established the initial CLI
  path beneath `~/eolas/clanns/`.
- Accepted decision:
  [011](../../adr/011-platformPrivateDataRoot.md) places application-managed
  private records beneath a platform-resolved data root and keeps hosted-server
  storage out of scope.

## Verification

- Criterion 1: classify a review set containing at least one Public, Private,
  Confidential and Highly Confidential example plus a field stricter than its
  section; record the classification and rationale and confirm no downward
  override is possible.
- Criterion 2: record the automated scan command, patterns and reviewed paths,
  then manually review every fictional fixture for conspicuous fictional labels
  and non-usable identifiers. Any real data or usable secret fails the criterion.
- Criterion 3: use a paper/digital handling matrix covering minimisation,
  storage, access, sharing, backup, recovery and disposal; verify each supported
  adapter resolves outside the repository to its platform's private data
  location and confirm every suggested method is vendor-neutral and states its
  limitations.
- Criterion 4: test all four allowed machine values, their ordering, a stricter
  field override, an unknown value and missing metadata. Unknown must be
  rejected; missing must be treated as `highlyConfidential` and prevented from
  sharing or export pending classification.
- Privacy threat review: assess accidental commit, over-collection, unauthorised
  disclosure, stale backups, insecure disposal, credential entry and unsafe
  classification fallback; record a mitigation or unresolved blocker for each.

### Refinement threat review

| Threat | Required mitigation | Remaining evidence |
| --- | --- | --- |
| Accidental commit of private data | ADR-0011 places managed records beneath a platform-resolved private root outside the repository; tracked-content scanning remains mandatory. | Verify every production adapter validates its destination and the repository scan passes. |
| Over-collection | Every field needs a stated purpose and classification; safe references are preferred to copied sensitive values. | Review the field inventory when handbook sections are implemented. |
| Unauthorised disclosure | Classification controls sharing and export decisions; guidance covers device and paper access without claiming guaranteed security. | Complete the paper/digital handling matrix and representative sharing review. |
| Stale or uncontrolled backups | Guidance must cover backup ownership, recovery testing, retention and obsolete-copy handling. | Review a representative backup and recovery scenario. |
| Insecure disposal | Guidance must cover proportionate disposal of superseded paper and digital copies. | Review representative paper and digital disposal scenarios. |
| Credential entry | ADR-0003 prohibits secret-shaped fields and requires safe references to separate authorised arrangements. | Run prohibited-field and prohibited-value scans and manually review free-text prompts. |
| Unsafe classification fallback | Unknown values are rejected; missing values fail closed as `highlyConfidential` until classified. | Add automated boundary tests when classification validation is implemented. |

## Traceability

- Implementation: pending
- Tests: pending
- Documentation: [information classification](../../../documentation/informationClassification.md), [privacy and security](../../../documentation/privacyAndSecurity.md)
- Pull request: pending
- Agent runs: 2026-07-28 — Codex, refinement role, criteria 1–4, using
  [refinement prompt](../prompt/002-privacyAndSecurityModel.md); result recorded
  in this requirement and accepted ADR-0011, which supersedes ADR-0010.

## Change history

- 2026-07-22: created as `HB-002-PrivacyAndSecurityModel.yaml`.
- 2026-07-28: migrated to permanent numeric Markdown path; outcome and evidence retained.
- 2026-07-28: refined classification, prohibited-data and handling evidence;
  recorded the maintainer-approved private data location in ADR-0010.
- 2026-07-28: superseded the fixed-path decision with ADR-0011 so desktop,
  mobile, CLI and browser interfaces use platform-resolved local storage.
