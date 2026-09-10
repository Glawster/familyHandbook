"""Tests for requirements 009--018 CLI capture routines."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml

from eolas.capture.models import (
    CAPTURE_PROFILES,
    CaptureInput,
    CaptureValidationError,
)
from eolas.capture.service import CaptureWriteError, capturePrepare, captureWrite
from eolas.clann.models import ClannInput, PersonInput
from eolas.clann.service import clannCreate
from eolas.cli import cliRun

TEST_TIME = datetime(2026, 8, 7, 9, 30, tzinfo=timezone.utc)


@pytest.fixture
def clannPath(tmp_path: Path) -> Path:
    clann = ClannInput(
        "Example Clann",
        "Example Home",
        [PersonInput("Alex Example", "Alex", "householder", True, True)],
    )
    return clannCreate(clann, tmp_path, timestampProvider=lambda: TEST_TIME)


def _validFields(domain: str) -> Dict[str, Any]:
    fields: Dict[str, Any] = {
        field: "known" for field in CAPTURE_PROFILES[domain].required_fields
    }
    fields["classification"] = "confidential"
    fields["lastReviewed"] = "2026-08-07"
    return fields


@pytest.mark.parametrize("domain", CAPTURE_PROFILES)
def test_capturePrepare_supportsRequirements009Through018(
    clannPath: Path, domain: str
) -> None:
    capture = CaptureInput(
        domain, "Household record", _validFields(domain), "statement"
    )

    targetPath, document = capturePrepare(
        capture, clannPath, timestampProvider=lambda: TEST_TIME
    )

    assert targetPath == clannPath / "shared" / domain / "household-record.yaml"
    assert document["schema"].startswith("eolas/")
    assert document["clannRef"] == "clann-example-clann"
    assert document["metadata"]["source"] == "statement"
    firstField = CAPTURE_PROFILES[domain].required_fields[0]
    assert document["data"][firstField] == {
        "state": "known",
        "value": "known",
    }


def test_captureValidate_reportsAllMissingRequiredFields() -> None:
    capture = CaptureInput("banking", "Bills", {}, "statement")

    with pytest.raises(CaptureValidationError, match="institution.*lastReviewed"):
        capture.captureValidate()


@pytest.mark.parametrize(
    "unsafeFields",
    [
        {"password": "do-not-store"},
        {"access": {"recoveryCode": "do-not-store"}},
        {"notes": "4111 1111 1111 1111"},
    ],
)
def test_captureValidate_rejectsCredentialsAndFullCardNumbers(
    unsafeFields: Dict[str, Any],
) -> None:
    fields = _validFields("banking")
    fields.update(unsafeFields)

    with pytest.raises(CaptureValidationError, match="prohibited|Prohibited"):
        CaptureInput("banking", "Bills", fields, "statement").captureValidate()


@pytest.mark.parametrize(
    "harmlessField",
    ["shippingAddress", "opinion", "pensionProvider", "pinningNote"],
)
def test_captureValidate_allowsHarmlessSecretSubstrings(harmlessField: str) -> None:
    fields = _validFields("banking")
    fields[harmlessField] = "fictional safe value"

    CaptureInput("banking", "Bills", fields, "statement").captureValidate()


def test_captureAdapter_preservesUnknownAndNotApplicable(
    clannPath: Path,
) -> None:
    fields = _validFields("banking")
    fields["institution"] = "unknown"
    fields["accountCategory"] = "notApplicable"

    _target, document = capturePrepare(
        CaptureInput("banking", "Bills", fields, "statement"),
        clannPath,
        timestampProvider=lambda: TEST_TIME,
    )

    assert document["data"]["institution"] == {"state": "unknown"}
    assert document["data"]["accountCategory"] == {"state": "notApplicable"}


def test_captureWrite_isAtomicAndRefusesOverwrite(clannPath: Path) -> None:
    capture = CaptureInput("banking", "Bills", _validFields("banking"), "statement")
    targetPath, document = capturePrepare(
        capture, clannPath, timestampProvider=lambda: TEST_TIME
    )

    captureWrite(targetPath, document)
    with pytest.raises(CaptureWriteError, match="already exists"):
        captureWrite(targetPath, document)

    loaded = yaml.safe_load(targetPath.read_text(encoding="utf-8"))
    assert loaded == document
    assert document["id"].startswith("rec_")
    assert document["ownerModule"] == "banking"
    assert list(targetPath.parent.glob(".*.yaml")) == []


def test_cliCapture_previewsThenWritesOnlyWithConfirm(
    tmp_path: Path,
    clannPath: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    inputPath = tmp_path / "bank.yaml"
    inputPath.write_text(
        yaml.safe_dump(_validFields("banking"), sort_keys=False), encoding="utf-8"
    )
    arguments = [
        "capture",
        "banking",
        "--clann",
        str(clannPath),
        "--input",
        str(inputPath),
        "--label",
        "Household bills",
        "--source",
        "2026 statement",
    ]
    targetPath = clannPath / "shared/banking/household-bills.yaml"

    assert cliRun(arguments) == 0
    assert not targetPath.exists()
    assert "Preview complete; no files were created" in capsys.readouterr().out

    assert cliRun([*arguments, "--confirm"]) == 0
    assert targetPath.is_file()
    assert "Capture complete:" in capsys.readouterr().out


def test_cliCapture_usesCursesWhenInputIsOmitted(
    clannPath: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "eolas.cli.domainCapture",
        lambda _domain: ("Household bills", "statement", _validFields("banking")),
    )

    result = cliRun(["capture", "banking", "--clann", str(clannPath), "--confirm"])

    assert result == 0
    assert (clannPath / "shared/banking/household-bills.yaml").is_file()


def test_cliCapture_discoversOnlyClannForSimpleCommand(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dataRoot = tmp_path / "eolas"
    clann = ClannInput(
        "Example Clann",
        "Example Home",
        [PersonInput("Alex Example", "Alex", "householder", True, True)],
    )
    clannPath = clannCreate(clann, dataRoot, timestampProvider=lambda: TEST_TIME)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(
        "eolas.cli.domainCapture",
        lambda _domain: ("Household bills", "statement", _validFields("banking")),
    )

    result = cliRun(["capture", "banking", "--confirm"])

    assert result == 0
    assert (clannPath / "shared/banking/household-bills.yaml").is_file()


def test_cliCapture_usesClannMenuWhenSeveralExist(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clannsPath = tmp_path / "eolas" / "clanns"
    firstPath = clannsPath / "first"
    secondPath = clannsPath / "second"
    for path in (firstPath, secondPath):
        path.mkdir(parents=True)
        (path / "clann.yaml").write_text("id: clann-test\n", encoding="utf-8")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr("eolas.cli.clannPathCapture", lambda _paths: secondPath)
    monkeypatch.setattr(
        "eolas.cli.domainCapture",
        lambda _domain: ("Household bills", "statement", _validFields("banking")),
    )

    result = cliRun(["capture", "banking", "--confirm"])

    assert result == 0
    assert (secondPath / "shared/banking/household-bills.yaml").is_file()


def test_cliCapture_usesDomainMenuWhenDomainIsOmitted(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dataRoot = tmp_path / "eolas"
    clann = ClannInput(
        "Example Clann",
        "Example Home",
        [PersonInput("Alex Example", "Alex", "householder", True, True)],
    )
    clannPath = clannCreate(clann, dataRoot, timestampProvider=lambda: TEST_TIME)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr("eolas.cli.captureDomainCapture", lambda: "utilities")
    monkeypatch.setattr(
        "eolas.cli.domainCapture",
        lambda _domain: ("Electricity", "bill", _validFields("utilities")),
    )

    result = cliRun(["capture", "--confirm"])

    assert result == 0
    assert (clannPath / "shared/utilities/electricity.yaml").is_file()


def test_cliCapture_interactiveConfirmationSavesWithoutFlags(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dataRoot = tmp_path / "eolas"
    clann = ClannInput(
        "Example Clann",
        "Example Home",
        [PersonInput("Alex Example", "Alex", "householder", True, True)],
    )
    clannPath = clannCreate(clann, dataRoot, timestampProvider=lambda: TEST_TIME)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr("eolas.cli.captureDomainCapture", lambda: "banking")
    monkeypatch.setattr(
        "eolas.cli.domainCapture",
        lambda _domain: ("Bills", "statement", _validFields("banking")),
    )
    monkeypatch.setattr("eolas.cli.confirmationCapture", lambda *_args, **_kwargs: True)

    assert cliRun(["capture"]) == 0
    assert (clannPath / "shared/banking/bills.yaml").is_file()
