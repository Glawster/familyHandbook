"""Tests for Clann-rooted bootstrap generation."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml

import eolas.clann.service as clannService
from eolas.clann.documents import (
    clannDocumentBuild,
    householdDocumentBuild,
    personDocumentBuild,
)
from eolas.clann.manifest import CLANN_DIRECTORIES
from eolas.clann.models import ClannInput, ClannValidationError, PersonInput
from eolas.clann.service import ClannCreationError, clannCreate
from eolas.clann.slugs import slugCreate, slugsCreateUnique
from eolas.cli import cliRun

TEST_TIME = datetime(2026, 7, 25, 14, 0, tzinfo=timezone.utc)


@pytest.fixture
def clann() -> ClannInput:
    return ClannInput(
        name="River Clann",
        primary_household_name="Family Home",
        people=[
            PersonInput("Morgan River", "Morgan", "householder", True, True),
            PersonInput("Jamie River", "Jamie", "family", False),
            PersonInput(
                "Alex River",
                "Alex",
                "family",
                True,
                lives_in_primary_household=False,
            ),
        ],
    )


def _yamlLoad(path: Path) -> Dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Wilson Clann", "wilson-clann"),
        ("O'Brien", "o-brien"),
        ("Élodie Brontë", "elodie-bronte"),
        ("../../unsafe", "unsafe"),
    ],
)
def test_slugCreate(value: str, expected: str) -> None:
    assert slugCreate(value) == expected


def test_slugsCreateUnique_suffixesDuplicateNames() -> None:
    assert slugsCreateUnique(["John Smith", "John Smith"]) == [
        "john-smith",
        "john-smith-2",
    ]


def test_clannValidate_requiresPrimaryPersonAndResident() -> None:
    withoutPrimary = ClannInput(
        "Test Clann",
        "Test Home",
        [PersonInput("Alex Test", "Alex", "adult", True)],
    )
    withoutResident = ClannInput(
        "Test Clann",
        "Test Home",
        [PersonInput("Alex Test", "Alex", "adult", True, True, False)],
    )

    with pytest.raises(ClannValidationError, match="exactly one"):
        withoutPrimary.clannValidate()
    with pytest.raises(ClannValidationError, match="at least one resident"):
        withoutResident.clannValidate()


def test_documentsKeepClannAndResidenceSeparate(clann: ClannInput) -> None:
    personIds = {
        0: "person-morgan-river",
        1: "person-jamie-river",
        2: "person-alex-river",
    }
    clannDocument = clannDocumentBuild(
        clann,
        "clann-river-clann",
        "household-family-home",
        personIds,
        TEST_TIME,
    )
    householdDocument = householdDocumentBuild(
        clann,
        "clann-river-clann",
        "household-family-home",
        personIds,
        TEST_TIME,
    )
    nonResidentDocument = personDocumentBuild(
        clann.people[2],
        personIds[2],
        "clann-river-clann",
        "household-family-home",
        TEST_TIME,
    )

    assert clannDocument["schema"] == "eolas/clann/v1"
    assert len(clannDocument["people"]) == 3
    assert clannDocument["primaryHouseholdRef"] == "household-family-home"
    assert len(householdDocument["members"]) == 2
    assert householdDocument["members"][0]["status"] == "resident"
    assert nonResidentDocument["clannRef"] == "clann-river-clann"
    assert nonResidentDocument["householdMemberships"] == []


def test_clannCreate_generatesCompleteReloadableTree(
    tmp_path: Path,
    clann: ClannInput,
) -> None:
    rootPath = clannCreate(
        clann, tmp_path / "data", timestampProvider=lambda: TEST_TIME
    )

    assert rootPath == tmp_path / "data" / "clanns" / "river-clann"
    assert (rootPath / "clann.yaml").is_file()
    for directoryName in CLANN_DIRECTORIES:
        assert (rootPath / directoryName).is_dir()
    householdPath = rootPath / "households" / "family-home" / "household.yaml"
    assert householdPath.is_file()

    documents = {path: _yamlLoad(path) for path in sorted(rootPath.rglob("*.yaml"))}
    assert len(documents) == 9
    clannDocument = documents[rootPath / "clann.yaml"]
    people = {
        document["id"]: document
        for path, document in documents.items()
        if path.name == "person.yaml"
    }
    householdDocument = documents[householdPath]

    assert {entry["personRef"] for entry in clannDocument["people"]} == set(people)
    assert all(person_id.startswith("rec_") for person_id in people)
    assert householdDocument["id"].startswith("rec_")
    residentIds = {member["personRef"] for member in householdDocument["members"]}
    assert len(residentIds) == 2
    nonResident = next(
        document
        for document in people.values()
        if document["name"]["displayName"] == "Alex River"
    )
    assert nonResident["householdMemberships"] == []
    for path in documents:
        assert path.read_bytes().endswith(b"\n")
        assert "!!python" not in path.read_text(encoding="utf-8")


def test_clannCreate_writesOpaquePeopleToRecordStore(
    tmp_path: Path,
    clann: ClannInput,
) -> None:
    from eolas.clann.records import clannRecordStoreOpen
    from eolas.domain.directory import peopleLoad
    from eolas.domain.values import identityOpaque

    rootPath = clannCreate(
        clann, tmp_path / "data", timestampProvider=lambda: TEST_TIME
    )
    store = clannRecordStoreOpen(rootPath, "clann-river-clann")
    people = peopleLoad(store)

    assert len(people) == 3
    assert {person.display_name for person in people} == {
        "Morgan River",
        "Jamie River",
        "Alex River",
    }
    assert all(identityOpaque(person.identity.record_id) for person in people)
    assert all(person.identity.aggregate_type == "person" for person in people)


def test_clannCreate_rejectsExistingNonEmptyTarget(
    tmp_path: Path, clann: ClannInput
) -> None:
    targetPath = tmp_path / "clanns" / "river-clann"
    targetPath.mkdir(parents=True)
    markerPath = targetPath / "keep.txt"
    markerPath.write_text("keep", encoding="utf-8")

    with pytest.raises(ClannCreationError, match="not empty"):
        clannCreate(clann, tmp_path)

    assert markerPath.read_text(encoding="utf-8") == "keep"


def test_clannCreate_failureLeavesNoPartialClann(
    tmp_path: Path,
    clann: ClannInput,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def treeFail(rootPath: Path, *_args: object) -> None:
        (rootPath / "partial.txt").write_text("partial", encoding="utf-8")
        raise OSError("injected failure")

    monkeypatch.setattr(clannService, "_clannTreeWrite", treeFail)

    with pytest.raises(OSError, match="injected failure"):
        clannCreate(clann, tmp_path / "data")

    assert not (tmp_path / "data").exists()


def test_cliCreatesClannThroughNaturalCommand(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    capturedClann = ClannInput(
        "Example Clann",
        "Family Home",
        [PersonInput("Alex Example", "Alex", "householder", True, True)],
    )
    monkeypatch.setattr("eolas.cli.clannCapture", lambda: capturedClann)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    result = cliRun(["clann", "--create", "--confirm"])

    assert result == 0
    assert (tmp_path / "eolas/clanns/example-clann/clann.yaml").is_file()
    output = capsys.readouterr().out
    assert "Clann created:" in output
    assert "household role: householder; age: adult; residence: resident" in output


def test_cliShowsLogFile(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    logPath = tmp_path / "eolas" / "eolas.log"
    logPath.parent.mkdir()
    logPath.write_text("Eolas started\n", encoding="utf-8")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    result = cliRun(["log", "--show"])

    assert result == 0
    assert capsys.readouterr().out == "Eolas started\n"


def test_cliReportsMissingLogFile(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    result = cliRun(["log", "--show"])

    assert result == 1
    assert "No Eolas log file found:" in capsys.readouterr().out
