"""Tests for keyboard-focused curses controls."""

import curses
from typing import List

import pytest

from eolas.curses_ui import CursesCancelled, CursesForm, FieldChoice


class FakeWindow:
    """Minimal curses window used to drive controls with known keys."""

    def __init__(
        self,
        keys: List[int] | None = None,
        textKeys: List[str | int] | None = None,
    ) -> None:
        self.keys = list(keys or [])
        self.textKeys = list(textKeys or [])
        self.drawCalls: List[tuple[object, ...]] = []

    def addnstr(self, *args: object) -> None:
        self.drawCalls.append(args)

    def erase(self) -> None:
        return None

    def bkgd(self, *_args: object) -> None:
        return None

    def getch(self) -> int:
        return self.keys.pop(0)

    def getmaxyx(self) -> tuple[int, int]:
        return 24, 80

    def get_wch(self) -> str | int:
        return self.textKeys.pop(0)

    def keypad(self, _enabled: bool) -> None:
        return None

    def refresh(self) -> None:
        return None


@pytest.mark.parametrize(("key", "expected"), [(ord("y"), True), (ord("n"), False)])
def test_confirmationAsk_usesSingleKey(key: int, expected: bool) -> None:
    assert CursesForm(FakeWindow([key])).confirmationAsk("Continue?") is expected


def test_confirmationAsk_supportsSkipAndQuit() -> None:
    assert CursesForm(FakeWindow([ord("s")])).confirmationAsk("Continue?", default=True)
    with pytest.raises(CursesCancelled):
        CursesForm(FakeWindow([ord("q")])).confirmationAsk("Continue?")


def test_menuAsk_usesArrowsEnterAndSkip() -> None:
    choices = (FieldChoice("first", "First"), FieldChoice("second", "Second"))

    selected = CursesForm(FakeWindow([curses.KEY_DOWN, 10])).menuAsk("Choose", choices)

    assert selected == "second"
    assert CursesForm(FakeWindow([ord("s")])).menuAsk("Choose", choices) == "unknown"


def test_menuAsk_highlightsSelectedFullRowInReverseVideo() -> None:
    window = FakeWindow([10])

    CursesForm(window).menuAsk("Choose", (FieldChoice("first", "First"),))

    selectedCall = next(
        call for call in window.drawCalls if len(call) == 5 and call[0] == 4
    )
    assert selectedCall[3] == 79
    assert int(selectedCall[4]) & curses.A_REVERSE
    assert str(selectedCall[2]).endswith(" " * 73)


def test_coloursInitialize_usesRequestedTheme(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pairs: list[tuple[int, int, int]] = []
    monkeypatch.setattr(curses, "has_colors", lambda: True)
    monkeypatch.setattr(curses, "start_color", lambda: None)
    monkeypatch.setattr(curses, "init_pair", lambda *pair: pairs.append(pair))
    monkeypatch.setattr(curses, "color_pair", lambda pair: pair * 100)

    form = CursesForm(FakeWindow())

    assert pairs == [
        (1, curses.COLOR_YELLOW, curses.COLOR_BLUE),
        (2, curses.COLOR_WHITE, curses.COLOR_BLUE),
        (3, curses.COLOR_WHITE, curses.COLOR_RED),
        (4, curses.COLOR_WHITE, curses.COLOR_GREEN),
    ]
    assert form.instructionAttribute == 100
    assert form.menuAttribute == 200
    assert form.errorAttribute == 300 | curses.A_BOLD
    assert form.successAttribute == 400 | curses.A_BOLD


def test_coloursInitialize_prefersStable256ColourPalette(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pairs: list[tuple[int, int, int]] = []
    monkeypatch.setattr(curses, "has_colors", lambda: True)
    monkeypatch.setattr(curses, "start_color", lambda: None)
    monkeypatch.setattr(curses, "COLORS", 256, raising=False)
    monkeypatch.setattr(curses, "init_pair", lambda *pair: pairs.append(pair))
    monkeypatch.setattr(curses, "color_pair", lambda pair: pair * 100)

    CursesForm(FakeWindow())

    assert pairs == [
        (1, 226, 17),
        (2, 15, 17),
        (3, 15, 196),
        (4, 15, 34),
    ]


def test_textAsk_usesEnterTextAndRecognisesImmediateControlKeys() -> None:
    textKeys: List[str | int] = [*"Household bills", "\n"]
    assert CursesForm(FakeWindow(textKeys=textKeys)).textAsk("Label") == (
        "Household bills"
    )
    assert CursesForm(FakeWindow(textKeys=["s"])).textAsk("Optional") == "unknown"
    with pytest.raises(CursesCancelled):
        CursesForm(FakeWindow(textKeys=["q"])).textAsk("Optional")


def test_textAsk_supportsBackspace() -> None:
    keys: List[str | int] = [*"Billx", curses.KEY_BACKSPACE, "s", "\n"]
    assert CursesForm(FakeWindow(textKeys=keys)).textAsk("Label") == "Bills"
