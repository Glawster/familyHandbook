# macOS Packaging

This directory contains the first macOS installation routine for Clann Eolas.

## Current scope

Eolas is currently a terminal/curses application. The verification package therefore installs a self-contained `eolas` executable rather than presenting a Finder-launched `.app` bundle that would have no usable terminal attached.

The package is intended for verification testing while the desktop UI is still under development.

## Build

Build on macOS from any working directory:

```bash
./packaging/macos/build.sh
```

The build routine:

1. verifies it is running on macOS;
2. requires Python 3 and Apple's `pkgbuild` utility;
3. creates an isolated build virtual environment under `.build/macos`;
4. installs Clann Eolas and PyInstaller into that environment;
5. builds a self-contained `eolas` executable;
6. stages the executable at `/usr/local/bin/eolas`;
7. creates a macOS installer package under `dist/`; and
8. prints the SHA-256 checksum of the resulting package.

The generated filename includes the project version and build architecture, for example:

```text
ClannEolas-0.1.0-macos-arm64.pkg
```

## Verification install

Open the generated `.pkg` in Finder and follow the standard macOS Installer prompts, or install from Terminal:

```bash
sudo installer -pkg dist/ClannEolas-0.1.0-macos-arm64.pkg -target /
```

After installation, verify:

```bash
which eolas
eolas --help
```

The installed user does not need Python, pip, Conda, Git, the source repository, or the build environment.

## User data

The installer only installs the application executable. Existing Eolas family data beneath the user's home directory is not included in the package and must not be deleted during installation or upgrade.

Uninstalling the executable is deliberately separate from removing user data.

## Signing and public distribution

The package produced by this routine is unsigned and is intended for internal verification only. A public macOS release will also require Developer ID signing and Apple notarisation.

## Future desktop application

When the Eolas graphical desktop UI is available, the same package-owned `eolas.app` entry point can be redirected to that UI. macOS packaging can then produce a standard `Clann Eolas.app` bundle and distribution image/package without moving application logic back into platform-specific installer code.
