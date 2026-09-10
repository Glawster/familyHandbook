# Clann Eolas v0.1.0 macOS Test 1

This is an unsigned macOS verification build intended for installation and user-testing validation only.

## Release identity

- Tag: `v0.1.0-macos-test1`
- Release name: `Clann Eolas v0.1.0 macOS Test 1`
- Mark as: **Pre-release**
- Target branch: `feature/app-install`

## Asset

Upload the package produced by:

```bash
./packaging/macos/build.sh
```

Expected filename pattern:

```text
ClannEolas-0.1.0-macos-<architecture>.pkg
```

For Apple Silicon this will normally be:

```text
ClannEolas-0.1.0-macos-arm64.pkg
```

## Verification status

This package:

- is unsigned;
- is not notarised by Apple;
- is intended for verification testing only;
- installs a self-contained `eolas` executable at `/usr/local/bin/eolas`;
- does not require Python, pip, Conda, Git, or the source repository on the target Mac.

## Checksum

The build command prints the SHA-256 checksum after creating the package. Copy that value into the GitHub Release notes alongside the uploaded asset.

Example:

```text
SHA-256: <paste build output here>
```

## Tester checks

After installation, verify:

```bash
which eolas
eolas --help
eolas clann --create
```

Record the build-script environment summary with the test evidence, including macOS version/build, architecture, Python version used to build, and Xcode Command Line Tools details.

## Known limitation

The current Eolas application is terminal/curses based. This release therefore packages the working CLI rather than presenting a Finder-launched graphical `.app` bundle.
