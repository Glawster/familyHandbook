# Information classification

Information classification helps authors and households decide what is safe to
publish, what belongs only in a private handbook and what should not be copied
into ordinary handbook content at all.

The classification describes the likely harm if information is disclosed to
the wrong person. It does not guarantee that a storage method is secure.

## Core rules

- Every handbook section must declare a default classification.
- A field or content block may declare a stricter classification than its
  section, but never a less restrictive one without explicit review.
- When several classifications apply, use the most restrictive.
- Classification labels must remain visible in human-readable and printed
  output, not only in software metadata.
- Future software may use the labels for warnings, filtering or export rules,
  but the classification model must work without software.
- Classification is based on completed household content. A blank public
  template can describe a `Private` field without making the template itself
  private.

## Levels

### Public

Information intentionally safe for anyone to read or redistribute, such as
reusable guidance, blank templates and clearly fictional reviewed examples.

It may be committed to the public repository, but must still respect copyright,
consent and the project's fictional-example rules.

### Private

Ordinary household information intended for household members or trusted
people, where disclosure would be intrusive or inconvenient but is unlikely on
its own to enable serious harm.

Examples include household routines, non-sensitive contact preferences and
maintenance schedules. It must not be committed to the public repository and
should be shared only with people who have a practical need for it.

### Confidential

Sensitive information whose disclosure could cause meaningful distress,
discrimination, financial loss, identity misuse or a significant invasion of
privacy.

Examples include health and care details, financial relationships, legal
arrangements, final wishes, security-system details and precise references to
protected documents.

Apply tighter access than for ordinary private information. Include only what
has a clear purpose, prefer safe references where possible, and consider paper
copies, backups and obsolete versions.

### Highly Confidential

Information whose disclosure could directly enable account takeover, theft,
identity fraud, circumvention of security or other severe harm.

Examples include passwords, PINs, authentication or recovery codes,
password-manager master credentials, private cryptographic keys and complete
payment-card security details.

Highly Confidential values must not be stored in ordinary handbook content.
The handbook may record that a separate authorised access arrangement exists
and give a safe, proportionate reference to it. Never include these values in
public templates, fictional examples, logs, exports or tests.

The shared knowledge model distinguishes classification from prohibition. Some
future knowledge may legitimately be Highly Confidential and may be retained
only by a storage adapter that explicitly provides the required protection and
by export policies that fail closed. Credentials, authentication material,
security answers, recovery/one-time codes and complete payment-card numbers are
prohibited regardless of storage capability. The current handbook and YAML
capture adapter do not store Highly Confidential values.

## Section labels

Until a canonical machine-readable handbook format is chosen, section authors
should display the classification near the title:

```text
Classification: Private
```

Future structured formats must use stable lowercase values:

```yaml
classification: private
```

The allowed values are `public`, `private`, `confidential` and
`highlyConfidential`. Tooling must reject unknown values rather than silently
treating them as less restrictive.

## Choosing a classification

Classify the completed content, not the blank prompt:

1. Is it intentionally publishable? Use `Public`.
2. Would it expose household information? Use at least `Private`.
3. Could disclosure cause meaningful personal, financial, legal, health or
   security harm? Use at least `Confidential`.
4. Could the value directly unlock, authenticate or defeat protection? It is
   `Highly Confidential` and must be kept out of ordinary handbook content.

If uncertain, choose the stricter level and request review.
