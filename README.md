# clanneolas.com

An open-source, privacy-conscious project for creating a practical record of the
information a family may need during an emergency, serious illness, loss of
capacity or death.

The repository is at an early, content-first stage. It contains a draft
handbook outline, project requirements, an implemented UI-independent shared
knowledge kernel and a working command-line prototype for creating private
Clann records and capturing structured continuity information.
It does not yet contain a web or desktop application. The handbook is intended
to remain useful as human-readable and printable documents without software.

## Documentation

- [Repository layout](documentation/repositoryLayout.md)
- [Requirements management](documentation/requirementsManagement.md)
- [Testing process](documentation/testingProcess.md)
- [Release process](documentation/howToRelease.md)
- [Product vision](documentation/productVision.md)
- [Project principles](documentation/principles.md)
- [Design principles](documentation/designPrinciples.md)
- [Personas](documentation/personas/personasIndex.md)
- [Glossary](documentation/glossary.md)
- [Information classification](documentation/informationClassification.md)
- [Privacy and security](documentation/privacyAndSecurity.md)
- [Domain model](documentation/domainModel.md)
- [Financial domain implementation plan](project/financialDomainImplementationPlan.md)
- [Architecture decisions](project/adr/adrIndex.md)
- [Banking guidance](documentation/banking/bankingIndex.md)
- [Clann bootstrap wizard](documentation/clannBootstrap.md)
- [Project planning and governance](project/projectIndex.md)
- [Requirements workflow](project/requirements/requirementsIndex.md)
- [Repository assessment](project/reviews/repositoryAssessment.md)
- [Change log](documentation/changeLog.md)
- [Brand assets and guidance](brand/brandIndex.md)
- [Handbook outline](handbook/01-GettingStarted.md)

## Publishing website assets

The development repository is the source of truth for website assets. The
[`scripts/publishAssets.yml`](scripts/publishAssets.yml) manifest maps selected source folders
to folders in the separate public website repository. Each target folder is
managed as a complete mirror: files removed from its source are removed from
that target, but the publisher never changes content outside configured target
folders.

Preview a publication before applying it:

```bash
scripts/publishAssets.sh --verbose
```

Publish to the default website checkout at `~/Source/clanneolasWebsite`:

```bash
scripts/publishAssets.sh --confirm
```

Commit the published paths on the current local branch, or create a publication
branch, push it, and open a pull request:

```bash
scripts/publishAssets.sh --confirm --commit
scripts/publishAssets.sh --confirm --push
```

Both repositories must normally have clean working trees. `--force` overrides
that check; it does not broaden the folders the script may change. For a
checkout in another location, use `--destination PATH` or set
`CLANN_EOLAS_WEBSITE_REPO`. An alternative manifest can be selected with
`--manifest PATH`. The publisher requires Bash, Git, rsync, Python 3, and the
project-standard `organiseMyProjects` package providing `logUtils.sh`.

The manifest accepts this intentionally small YAML structure:

```yaml
publish:
  - source: brand/logo
    target: assets/logos
```

Source and target paths must be relative, source folders must exist, and target
folders may not overlap. `.git`, `.github`, `.vscode`, `documentation`,
`deploy`, `scripts`, `README.md`, and `LICENSE` are excluded from mapped trees
unless one is itself explicitly selected as a source mapping. Publishing is a
safe preview unless `--confirm` is supplied. `--confirm` without `--commit` or
`--push` leaves changes local and uncommitted. `--push` implies `--commit`, and
both options require `--confirm`. A publication branch and pull request are
created only when `--push` is supplied and published files changed.

Do not put real household data, passwords, PINs, recovery codes or other
secrets in this public repository. Examples must be fictional.

## Command-line tools

Create and activate the project environment, then install Eolas as an editable
package for development:

```bash
conda activate handbook
python -m pip install -e .
```

The installed `eolas` command can create a Clann and capture prototype input
records for requirements 009 through 018. Capture now uses shared typed identity
and validation, but it is not a complete implementation of those domains.
Capture commands preview changes unless
`--confirm` is supplied:

```bash
eolas clann --create
eolas capture
```

See the [Clann bootstrap and capture guide](documentation/clannBootstrap.md)
for the private-data layout and capture workflow.

## Testing

Run the complete test suite from the repository root:

```bash
pytest
```

See the [testing process](documentation/testingProcess.md) for the required
unit, integration and production-path evidence.
