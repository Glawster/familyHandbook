"""Application entry point shared by source and packaged launchers."""

from eolas.cli import main as cliMain


def main() -> int:
    """Run the currently available Eolas user interface.

    Eolas is presently a terminal/curses application. Keeping this indirection
    means future desktop packaging can switch to a graphical application entry
    point without making platform installers depend on repository-root code.
    """

    return cliMain()
