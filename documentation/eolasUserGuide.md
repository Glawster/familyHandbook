# Eolas User Guide

**Current CLI prototype**  
**Version covered:** current `feature/banking-core` functionality  
**Purpose:** help a family create and maintain a practical continuity record safely and simply.

## 1. What Eolas is

Eolas is a family continuity application. It is intended to help a family record the information that may be needed during an emergency, serious illness, loss of capacity, or death.

The current version is a **command-line application**. It does not yet provide a full desktop or web interface.

At present Eolas can:

- create a Clann;
- create the primary household;
- record the people in that Clann;
- record people who live in the household and Clann members who live elsewhere;
- capture structured continuity information for several areas;
- create properly structured Banking records;
- reuse existing Clann people when recording bank-account owners;
- reuse existing financial institutions where they can be identified safely;
- preview changes before saving them;
- reject password-like and other prohibited secret information;
- keep private family data outside the public source-code repository.

Banking is currently the most developed capture area. Other capture areas are still prototypes and will become fully typed modules later.

---

## 2. Important safety rules

Eolas is designed to record **knowledge about your affairs**, not the secrets used to gain access to them.

### Never enter

Do not enter:

- passwords;
- PINs;
- card security codes such as CVV or CVC;
- recovery codes;
- authenticator secrets;
- one-time codes;
- access tokens;
- private cryptographic keys;
- full payment-card numbers.

Where access arrangements matter, record **where the authorised access information is kept**, rather than copying the secret itself into Eolas.

### Application access is not legal authority

Being able to read information in Eolas does not give someone legal authority to operate a bank account, close an account, act as an attorney, act as an executor, or act for another person.

Eolas records those real-world roles separately.

---

## 3. Where Eolas stores your data

The current CLI stores Clann data beneath:

```text
~/eolas/clanns/
```

For example, a Clann called:

```text
Example Clann
```

would normally be stored under:

```text
~/eolas/clanns/example-clann/
```

The human-readable folder names are only used for organising files. New Person and Household records use opaque internal record IDs beginning with `rec_`.

A typical Clann currently looks like this:

```text
~/eolas/
└── clanns/
    └── example-clann/
        ├── clann.yaml
        ├── people/
        ├── households/
        ├── relationships/
        ├── contacts/
        ├── professionals/
        ├── documents/
        └── shared/
            └── records.yaml
```

Do not place live Clann data inside the public Eolas source-code repository.

---

## 4. Starting Eolas

If Eolas has already been installed, open a terminal and run:

```bash
eolas --help
```

The main commands currently available are:

```text
eolas clann --create
eolas capture
eolas capture banking
eolas log --show
```

---

## 5. Creating your Clann

A **Clann** is the wider group of people whose continuity information you want Eolas to help organise.

It is deliberately broader than a household. A Clann can include:

- people who live together;
- close family who live elsewhere;
- people with important continuity roles.

To create a new Clann, run:

```bash
eolas clann --create
```

Eolas opens an interactive terminal wizard.

### What the wizard asks

The wizard asks for information such as:

- the Clann name;
- the name of the primary household;
- people who currently live in that household;
- the primary person or record owner;
- Clann members who live elsewhere;
- practical household roles;
- whether each person is legally an adult.

### Controls

In the interactive screens:

- use the **arrow keys** to move through menu choices;
- press **Enter** to select;
- use `y` for yes;
- use `n` for no;
- use `q` to quit where offered;
- use `s` to skip where offered.

When the wizard is complete, Eolas shows a summary before creating the files.

If you cancel, the Clann is not created.

### Example

You might create:

```text
Clann: Example Family
Primary household: Family Home

People:
- Alex Example — householder — adult — resident
- Sam Example — partner — adult — resident
- Jamie Example — family — adult — lives elsewhere
```

Once created, these people become reusable records inside Eolas.

---

## 6. Capturing continuity information

Run:

```bash
eolas capture
```

Eolas presents a menu of the currently supported capture areas.

These currently include:

- Banking
- Credit Cards
- Mortgages
- Loans
- Investments
- Pensions
- Insurance
- Taxation
- Subscriptions
- Utilities

You can also go directly to an area. For example:

```bash
eolas capture banking
```

### Preview before save

Eolas is deliberately cautious.

A capture is normally shown as a **preview before anything is written**.

After reviewing the preview, you can choose whether to save it.

This makes it easier to spot mistakes before they become part of the Clann record.

---

## 7. Banking records

Banking is currently the first fully structured financial area.

A Banking record represents the **real-world banking relationship**, not a statement or document.

Eolas separates several things that are often confused:

```text
Financial Institution
        ↓
Banking Relationship
        ↓
Owners / interested parties
        ↓
Continuity role
        ↓
Identifiers
        ↓
Dated balance observations
        ↓
Authority references
```

### Typical information to record

During Banking capture you may be asked for information such as:

- financial institution;
- account category;
- product name;
- purpose;
- owner or owners;
- account status;
- information classification;
- date last reviewed;
- continuity role;
- account identifiers;
- balance and balance date, where supplied.

### Safe labels

Use labels that help the family understand the purpose of the account, for example:

```text
Household bills
Main current account
Emergency savings
Holiday savings
```

A label is not the bank-account number.

---

## 8. How Eolas handles account owners

Eolas tries to reuse people who are already part of the Clann.

If you enter an owner name and exactly one existing Clann Person has that exact name, Eolas reuses that Person record.

For example:

```text
Alex Example
```

may be linked directly to the existing Clann Person rather than creating another copy of Alex.

### If no person matches

If there is no matching Clann Person, Eolas currently creates a separate `Contact` record for that named external person.

### If more than one person has the same name

Eolas will not guess.

If two people have the same exact name, the capture must use an explicit record reference instead.

This avoids accidentally assigning ownership to the wrong person.

---

## 9. Joint accounts

Joint ownership is represented using multiple account parties.

For example:

```text
Household current account
Owners:
- Alex Example
- Sam Example
```

Eolas keeps ownership separate from authority.

Someone may have authority concerning an account without being an owner, and someone may own an account without another person having authority to operate it.

---

## 10. Financial institutions

Eolas keeps a Financial Institution separate from individual accounts.

The preferred model is:

```text
Example Bank
├── Household current account
├── Savings account
└── Emergency reserve account
```

rather than creating three separate copies of the bank.

If Eolas can identify exactly one existing institution with the same stored name, it can reuse that institution.

If several institutions have the same name, Eolas will not guess. An explicit reference is required.

---

## 11. Account identifiers

Eolas can represent typed banking identifiers such as:

- account number or provider account reference;
- sort code;
- IBAN;
- SWIFT/BIC;
- customer or membership number;
- building-society roll number;
- provider product reference.

These identifiers are **not** the internal Eolas record ID.

Sensitive identifiers are masked for normal display where appropriate.

For example, an identifier may appear in a masked form resembling:

```text
••••1234
```

Do not confuse an account identifier with a password, PIN, card security code, or other secret. Those must not be stored.

---

## 12. Balance information

A bank balance changes over time, so Eolas does not treat it as a permanent fact.

Instead, a balance is recorded as a dated observation.

For example:

```text
Balance: £2,350.00
As of: 2026-09-10
```

This means:

> The known balance was £2,350.00 on 10 September 2026.

It does not mean the account still contains that amount today.

If a balance is supplied, an `asOf` date/time must also be supplied.

---

## 13. Continuity roles

An account may have an important purpose in keeping the household operating.

Current Banking continuity roles include concepts such as:

- primary household operating account;
- bills account;
- salary or income receipt account;
- emergency reserve;
- savings;
- child account;
- business account;
- estate-related account;
- other.

The role describes **why the account matters to continuity**.

For example, knowing that an account is the household's main bills account may be much more useful during an emergency than simply knowing that the account exists.

---

## 14. Account status

Banking relationships can distinguish operational status from whether the Eolas record itself exists.

Examples include:

- active;
- dormant;
- restricted;
- closure pending;
- closed;
- unknown.

A closed account may still be worth retaining in Eolas for historical or continuity reasons.

---

## 15. Information classification

Eolas classifies information so that future sharing and export functions can apply appropriate controls.

The project uses:

```text
Public
Private
Confidential
Highly Confidential
```

The current generic CLI capture workflow does **not** allow Highly Confidential values to be entered through the normal capture form.

If information is especially sensitive, store only what Eolas genuinely needs and use safe references where possible.

---

## 16. Unknown information

It is acceptable not to know everything.

Where supported, Eolas distinguishes between information that is:

- known;
- unknown;
- not applicable;
- absent/not yet supplied.

Do not invent information simply to complete a form.

If you do not know something, record it as unknown when the interface allows that.

This is better than putting in a guess that another family member may later treat as fact.

---

## 17. Advanced: capture from a YAML file

The normal interactive workflow is recommended for ordinary use.

For advanced or automated entry, Banking capture can also read input from a private YAML file.

Example command:

```bash
eolas capture banking \
  --clann ~/eolas/clanns/example-clann \
  --input ~/private/bank-account.yaml \
  --label "Household bills" \
  --source "Statement reviewed 2026-09-10"
```

Without `--confirm`, Eolas previews the proposed change without saving it.

To save after validation:

```bash
eolas capture banking \
  --clann ~/eolas/clanns/example-clann \
  --input ~/private/bank-account.yaml \
  --label "Household bills" \
  --source "Statement reviewed 2026-09-10" \
  --confirm
```

Keep private input files outside the public source-code repository.

### Explicit owner references

Advanced input can use stable owner references when names would be ambiguous.

This is particularly useful if two Clann members have the same name.

### Explicit institution references

Advanced input can also identify an existing financial institution explicitly rather than relying on name matching.

This is the safest approach where provider names are duplicated or ambiguous.

---

## 18. Viewing the Eolas log

Run:

```bash
eolas log --show
```

The current CLI looks for the log at:

```text
~/eolas/eolas.log
```

If no log exists yet, Eolas reports that rather than creating one automatically.

Logs should not contain passwords, private cryptographic material, or other prohibited secrets.

---

## 19. Installing from source

For development or Linux use, Eolas can currently be installed from the repository.

The project requires Python 3.10 or later.

From the project environment:

```bash
python -m pip install -e .
```

Then verify:

```bash
eolas --help
```

The project development workflow commonly uses Conda, but an ordinary end-user installation process is still being developed.

---

## 20. macOS verification package

A macOS verification installer can currently be built from the repository.

The current package installs a self-contained terminal `eolas` command under:

```text
/usr/local/bin/eolas
```

The verification package is currently unsigned and intended for testing rather than public distribution.

After installing it, verify with:

```bash
which eolas
eolas --help
```

The installed user does not need Python, pip, Conda, Git, or the Eolas source repository to run the packaged executable.

The installer does not remove or replace existing Clann data.

---

## 21. Backing up your current data

The current CLI does not yet provide the planned full encrypted backup/synchronisation workflow.

Until that functionality is implemented, treat the entire private Eolas data directory as important family data:

```text
~/eolas/
```

Any manual backup must be protected appropriately because it may contain private or confidential family information.

Do not assume that ordinary file synchronisation is a complete Eolas backup or security solution.

Future Eolas versions are intended to provide controlled backup, restore, encryption, multi-device access and secure Clann sharing.

---

## 22. What is not implemented yet

The current version is an early but working CLI prototype.

It does **not** yet provide:

- a full desktop graphical interface;
- a web application for private Clann data;
- mobile access;
- secure multi-device synchronisation;
- production encryption/key management;
- emergency-access recovery;
- automated document import;
- PDF statement analysis;
- OCR;
- Open Banking connections;
- transaction import;
- full Direct Debit and standing-order modelling;
- executor or attorney workflows;
- final Banking reports;
- automatic institution lookup from the internet;
- fully implemented Credit Card, Mortgage, Loan, Investment, Pension, Insurance, Tax, Subscription or Utility modules.

Some of those areas appear in the capture menu because their initial capture profiles already exist, but they should still be regarded as prototypes.

---

## 23. Recommended way to use the current version

For a new Clann, the simplest workflow is:

1. Install Eolas.
2. Run `eolas clann --create`.
3. Enter the household and Clann members carefully.
4. Run `eolas capture banking`.
5. Start with the account that matters most to day-to-day household continuity.
6. Give it a clear purpose-based label.
7. Record owners and the institution.
8. Record only safe identifiers.
9. Add a balance only if you also know when that balance was valid.
10. Review the preview carefully.
11. Save only when the preview is correct.
12. Repeat for other important Banking relationships.
13. Keep the data directory protected and backed up appropriately.
14. Revisit records when circumstances change.

Do not try to complete every possible field at once. Accurate, reviewed information is more useful than a large amount of guessed information.

---

## 24. Troubleshooting

### “No Clanns exist yet”

Create one first:

```bash
eolas clann --create
```

### Eolas finds several Clanns

Interactive capture presents a choice.

For non-interactive YAML input, specify the Clann explicitly:

```bash
--clann ~/eolas/clanns/example-clann
```

### A person name is ambiguous

If two stored Clann people have the same name, Eolas refuses to guess.

Use an explicit owner reference through advanced YAML input.

### An institution name is ambiguous

Use an explicit `institutionRef` or `organisationRef` in advanced input.

### A capture is rejected because of secret information

Remove passwords, PINs, card security codes, recovery information, authentication secrets, or full payment-card numbers.

Record a safe reference to the authorised access arrangement instead.

### Balance rejected because `asOf` is missing

Add the date/time on which the balance was known to be correct.

### You are unsure about a value

Use `unknown` where supported rather than guessing.

---

## 25. Current development status

Banking Core is implemented as an active development increment, but the overall Banking requirement remains **InProgress**.

The next planned Banking work is expected to model:

- Money Movements; and
- Payment Arrangements.

These will eventually allow Eolas to describe how income arrives, how household commitments are paid, and what depends on each Banking relationship without confusing an obligation, payment instruction, expected money movement, or observed transaction.

---

## 26. Key principles to remember

The most important rules for using Eolas are simple:

> Record what your family needs to know, not the secrets needed to impersonate you.

> If you do not know something, say that it is unknown rather than guessing.

> Give accounts and services labels that explain why they matter.

> Review the preview before saving.

> Access to Eolas information does not give legal authority over the real-world asset.

> Protect the Eolas data directory as private family information.

Eolas will become more automated over time, but these principles are intended to remain the same.
