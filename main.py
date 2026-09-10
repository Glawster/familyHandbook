"""Project-root launcher for the Clann Eolas application.

Keep this file deliberately small. Application behaviour belongs in the
``eolas`` package so packaging and platform launchers can share one entry point.
"""

from eolas.app import main


if __name__ == "__main__":
    raise SystemExit(main())
