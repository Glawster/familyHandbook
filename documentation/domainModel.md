# Domain model

The domain model describes the real-world concepts clanneolas.com organises and
how they relate. It is not a database schema, file format, API design or
application architecture.

## Mission

**clanneolas.com provides a shared language for organising the practical
knowledge families need before, during and after life's unexpected events.**

The model gives handbook chapters, emergency summaries, fictional examples,
printed output and any future software a shared language. Each output is a
projection: it selects and presents relevant parts of the same model for a
particular person and situation.

The project's keystone architectural test is:

> **Am I modelling knowledge, or am I modelling a document?**

See [ADR 007: Knowledge before documents](../project/adr/007-knowledgeBeforeDocuments.md).

The handbook is the first foundational projection, not the domain model or the
source of truth. [ADR 008](../project/adr/008-handbookAsProjection.md)
defines the relationship used for future content and interface design:

```text
Knowledge → Projection → User Experience
```

## Model principles

- Model family life, not the current folder structure or a future interface.
- A household is a planning context, not necessarily a family, couple or shared
  address.
- Record only what has a clear purpose.
- References to protected information are often safer than copies.
- Every information-bearing concept can carry a classification and review
  information.
- Jurisdiction-specific terms extend the model; they do not define its core.
- The model remains understandable and useful on paper.

## Core concepts

```text
Household
├── People
├── Properties
├── Documents
├── Assets
├── Accounts
├── Contacts
├── Instructions
├── Wishes
└── Reviews
```

These branches are navigation aids, not isolated containers. A document can
relate to a person, property, asset or account. A contact can support several
people or responsibilities. A review can cover the whole household or selected
items.

The relationship diagram is maintained as
[Mermaid source](domainModel.mmd).

## Concepts and Instances

The domain model describes concepts.

Individual households create instances of those concepts.

Fictional example:

Concept:
Person

Instance: Example Person A

## Household

The context whose practical knowledge is being organised. A household may be
one person, people who live together, or people who coordinate responsibilities
across different homes.

Candidate information:

- display name or neutral label;
- people associated with the household;
- important locations;
- review schedule;
- trusted-reader arrangements; and
- jurisdiction profiles used by relevant guidance.

A household label should not require a legal family name or precise address.

## Person

An individual who belongs to, depends on, supports or has a responsibility in
relation to the household.

Candidate information:

- name or preferred label;
- relationship to the household or another person;
- safe contact references;
- care or medical information needed for a stated purpose;
- roles and responsibilities;
- related documents;
- emergency contacts; and
- wishes relevant to that person.

Relationships must support households that are not based on marriage, biology
or one address. Medical details are `Confidential` by default; a public template
must never contain real values.

## Property

A home, building, land, vehicle or other place-related responsibility the
household may need to operate, protect or maintain.

Candidate information:

- descriptive label rather than an unnecessary precise address;
- relationship to the household, such as home, rented property or storage;
- utilities and maintenance responsibilities;
- access and safety instructions;
- related contacts, documents, accounts and assets; and
- review information.

Security-system details, key locations and precise access instructions may be
`Confidential`. Codes and PINs are `Highly Confidential` and must not be stored
in ordinary handbook content.

## Document

A record that exists elsewhere and may be needed as evidence, authority or
guidance. The handbook normally stores a reference to it, not the document
itself.

Candidate information:

- title or descriptive label;
- document type;
- safe location reference;
- classification;
- owner or responsible person;
- related people, properties, assets or accounts;
- issuer or relevant contact;
- effective or expiry date, when useful;
- last reviewed date; and
- action needed.

Examples include a will, insurance policy, power of attorney, tenancy agreement
or care plan. A location reference must be only as precise as authorised readers
need.

## Asset

Something of practical or financial value that the household may need to
identify, protect, maintain or deal with.

Candidate information:

- descriptive label and category;
- owner or interested people;
- location reference;
- related documents, accounts, properties and contacts;
- maintenance or action information; and
- classification and review date.

The model does not require a full inventory or valuation. Include detail only
when it supports a defined handbook need.

## Account

A relationship with an organisation or service that may require attention. It
is not a container for credentials.

Candidate information:

- provider or organisation;
- purpose and account category;
- safe reference or masked identifier, only when needed;
- responsible people;
- related assets, properties, documents and contacts;
- actions that may be needed; and
- classification and review date.

Passwords, PINs, recovery codes, full payment-card details and equivalent
secrets are never account attributes in ordinary handbook content.

## Contact

A person, organisation, team or professional service that may need to be
contacted or may be able to help.

Candidate information:

- name or organisation label;
- role or reason for contact;
- preferred contact method;
- availability or escalation guidance;
- people, properties, documents, accounts or wishes supported; and
- classification and review date.

Contact does not imply legal authority. Roles such as attorney, executor and
next of kin must retain the distinctions in the [glossary](glossary.md).

## Instruction

Practical knowledge about how, when or why to do something for the household.
An instruction can support a person, property, account, asset, document or wish
without belonging exclusively to one handbook chapter.

Candidate information:

- title and purpose;
- steps or guidance;
- circumstances or trigger;
- responsible person or role;
- related concepts and contacts;
- classification;
- last reviewed date; and
- follow-up action.

Instructions must distinguish practical guidance from legal, medical or
financial advice. They must not contain passwords, PINs, recovery codes or
other Highly Confidential values.

## Wish

A preference, request or intention a person wants trusted readers to understand.
A wish is not automatically legally binding and must not be presented as a
substitute for a formal document.

Candidate information:

- subject and plain-language description;
- person expressing the wish;
- people who should know;
- related documents and contacts;
- whether professional or formal action is needed;
- classification; and
- review date.

## Review

Evidence that household information, selected concepts or references were
checked at a point in time.

Candidate information:

- review date;
- scope or items reviewed;
- responsible role or person;
- changes identified;
- follow-up actions and target dates; and
- next review trigger or date.

A review records that something was checked; it does not silently overwrite the
history of a requirement, ADR or legal document.

## Shared supporting concepts

The first model may also need small supporting concepts rather than repeating
free text:

- **Role:** a responsibility or authority held by a person or contact, such as
  carer, executor or attorney.
- **Relationship:** how two concepts are connected, with wording that does not
  assume a particular family structure.
- **Location reference:** a safe description of where an item or protected
  record can be found.
- **Action:** something that needs to be done, by whom and when.
- **Classification:** the handling level defined by the
  [information classification model](informationClassification.md).
- **Review information:** when an item was checked and when or why it should be
  checked again.

These are conceptual tools, not commitments to software classes or database
tables.

## Projections

```text
                         ┌───────────────────┐
                         │ Shared domain     │
                         │ model             │
                         └─────────┬─────────┘
             ┌────────────────────┼────────────────────┐
             │                    │                    │
     ┌───────▼────────┐   ┌───────▼────────┐   ┌──────▼─────────┐
     │ Handbook       │   │ Emergency      │   │ Annual review  │
     │ chapters       │   │ summary        │   │ checklist      │
     └────────────────┘   └────────────────┘   └────────────────┘
             │                    │                    │
     ┌───────▼────────┐   ┌───────▼────────┐   ┌──────▼─────────┐
     │ Printed        │   │ Fictional      │   │ Future         │
     │ handbook       │   │ example        │   │ software       │
     └────────────────┘   └────────────────┘   └────────────────┘
```

For example, an emergency summary may project urgent contacts, care needs,
property access guidance and document references. It should not create separate
copies that can drift away from the same concepts in the full handbook.

## Boundaries and open questions

This first model intentionally does not settle:

- which concepts become standalone records versus embedded content;
- the canonical YAML, Markdown or other source format;
- identifiers and versioning for private household records;
- whether organisations need a separate concept from contacts;
- how shared or conflicting wishes are represented;
- how jurisdiction-specific extensions are packaged; or
- how future software stores, queries or synchronises information.

Those choices require evidence, requirements and ADRs. They must not be inferred
from the illustrative candidate information in this document.
## Implemented shared-domain foundation

The Phase 1 knowledge kernel now implements the common concepts beneath future
domain modules. It is deliberately independent of CLI, curses, Qt and concrete
storage. The canonical boundary is a set of typed domain values, commands and
services; YAML is only the current local adapter.

Every new aggregate has an opaque `RecordIdentity` containing its Clann and one
owner module. Typed `RecordReference` values cross aggregate/module boundaries
without transferring ownership and reject cross-Clann use. Names, slugs,
filenames and external identifiers are never canonical identity. Prototype
Clann bootstrap records retain their earlier readable IDs pending migration.

Availability is explicit through `Fact`: `known`, `unknown`, `notApplicable`
and `absent` are distinct and are never silently coerced. Temporal facts use an
`Observation` with an `asOf` time, provenance, confirmation status and optional
confidence. `Identifier`, `Money`, `Schedule`, `Jurisdiction`, `ReviewState`,
`EvidenceReference` and `Provenance` are reusable value compositions.

The shared party model distinguishes `Person`, lightweight `Contact`, legal
`Organisation`, familiar `OrganisationBrand`, dated contact routes and domain-
owned provider roles. `PartyRole` does not imply ownership or authority.
`Authority` describes scope and legal/practical state; provider-specific
`AuthorityRegistration` separately describes operational recognition.

`ContinuityDependency` is a typed directed reference between records. The
shared graph service validates Clann scope and performs forward, reverse and
cycle-safe traversal with human-readable explanations. Modules own the meaning
of edge types they publish and retain ownership of their aggregates.

Persistence uses a versioned `RecordStore` port with atomic change sets,
expected-version conflicts, append-only prior versions and explicit migrations.
The implemented YAML adapter demonstrates the contract but its document shape
is not a domain schema.

The existing generic capture profiles remain prototype input support for
requirements 009–018. They now translate into typed commands and shared
validation, but they are not the completed Banking or other domain models.
