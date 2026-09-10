# Clann bootstrap wizard

The bootstrap wizard creates a Clann, its primary household, and the first
people represented by Eolas.

## Run the wizard

```bash
python -m pip install -r requirements.txt
eolas clann --create
```

The curses wizard asks for the Clann name, primary household, current residents,
primary person, and any Clann people who live elsewhere. Use `y`, `n`, `q` and
`s` for decisions, arrow keys and Enter for menus, and text followed by Enter
for names and roles. Pass `--confirm` to generate after showing the summary
without the final confirmation.

Private Eolas data is always rooted at `~/eolas`. A Clann named `Example
Clann` is therefore written beneath `~/eolas/clanns/example-clann/`. Creation
is atomic and refuses to overwrite a non-empty Clann directory.

## Generated structure

```text
~/eolas/
└── clanns/
    └── example-clann/
        ├── clann.yaml
        ├── people/
        │   └── alex-example/
        │       ├── person.yaml
        │       └── identity.yaml
        ├── households/
        │   └── family-home/
        │       └── household.yaml
        ├── relationships/
        ├── contacts/
        ├── professionals/
        ├── documents/
        └── shared/
            └── records.yaml
```

Directory names remain slugs for a stable filesystem layout. New person and
household document IDs are opaque `rec_` values, not `person-alex-example`.
Those IDs are also written as `Person` aggregates in `shared/records.yaml` so
later modules can reuse them through the shared `RecordStore` port. Older Clann
directories that still use slug IDs remain readable; new Clanns do not allocate
slug identities.

`clann.yaml` indexes all people and households. Household records contain
residence memberships; person records refer to the Clann and repeat their
household memberships for convenient lookup. A person who lives elsewhere
still belongs to the Clann and can have an empty membership list until their
household is recorded.

Contacts and professionals are deliberately separate from Clann people.
Relationships are also independent of residence.

## Reuse from Python or Qt

```python
from pathlib import Path

from eolas import ClannInput, PersonInput, clannCreate

clann = ClannInput(
    name="Example Clann",
    primary_household_name="Family Home",
    people=[
        PersonInput(
            full_name="Alex Example",
            preferred_name="Alex",
            household_role="householder",
            is_adult=True,
            is_primary=True,
        )
    ],
)

createdPath = clannCreate(clann, Path.home() / "eolas")
```

The identity files contain sensitive personal-data placeholders. Store live
data in an appropriately protected location and never commit it publicly.

## Capture continuity records

Requirements 009 through 018 share an interactive curses capture command for
banking, credit cards, mortgages, loans, investments, pensions, insurance,
taxation, subscriptions and utilities:

```bash
eolas capture
eolas capture banking
```

Use `y`, `n`, `q` and `s` for immediate decisions, arrow keys and Enter for
menus, and text followed by Enter for free-form values. A skipped required fact
is recorded explicitly as `unknown`. The form collects the record label,
information source and all mandatory domain fields. Eolas automatically uses
the only Clann under `~/eolas/clanns/`, or presents a menu when more than one
exists. Running `eolas capture` also presents a menu of the available capture
domains; including a domain such as `banking` goes directly to that form. After
the preview, press `y` to save or `n` to leave the data unchanged. `--confirm`
is available to bypass this final question.

For advanced automation, put the domain fields in a private YAML file and
provide explicit context:

```bash
eolas capture banking \
  --clann ~/eolas/clanns/example-clann \
  --input ~/private/bank-account.yaml \
  --label "Household bills" \
  --source "Statement reviewed 2026-08-07"
```

The preview validates mandatory fields and shows the complete record without
writing it. Add `--confirm` to create the record atomically under
`shared/<domain>/`. Banking capture writes typed
`FinancialInstitution` and `BankingRelationship` records through the shared
Clann store at `shared/records.yaml`. If an owner name matches exactly one
Clann `Person`, that person is reused; unknown names become `Contact` records.
Existing institutions are reused when `institutionRef` is supplied, or when
exactly one stored provider has that display name. Duplicate names require
`ownerRefs` or `institutionRef` rather than silent matching. Optional payment
fields such as `obligationPurpose`, `paymentMechanism`, `movementDirection`
and `transactionAmount`/`transactionAsOf` create separate obligation,
arrangement, movement and transaction-evidence records. Other capture
domains still write one prototype YAML document per label. Run
`eolas capture --help` to see the supported domain names. Missing mandatory
fields are reported together so the input can be corrected in one pass.

Every input needs the domain's required fields plus a valid `classification`
and an ISO `lastReviewed` date. Unknown facts should be recorded explicitly as
`unknown`; they must not be silently omitted. Credential-shaped fields,
Highly Confidential content and full payment-card numbers are rejected. Use
safe references to separately managed access arrangements instead.
