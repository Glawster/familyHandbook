"""Prepare and atomically persist structured continuity capture records."""

import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from eolas.capture.adapter import captureCommandBuild
from eolas.capture.models import CaptureInput
from eolas.clann.slugs import slugCreate
from eolas.clann.yaml_io import yamlWrite


class CaptureWriteError(RuntimeError):
    """Raised when a capture record cannot be safely written."""


TimestampProvider = Callable[[], datetime]


def capturePrepare(
    capture: CaptureInput,
    clannPath: Path,
    *,
    timestampProvider: Optional[TimestampProvider] = None,
) -> tuple[Path, Dict[str, Any]]:
    """Validate a capture and return its destination and canonical document."""
    clannPath = clannPath.expanduser().resolve()
    if not clannPath.is_dir() or not (clannPath / "clann.yaml").is_file():
        raise CaptureWriteError(f"Not an Eolas Clann directory: {clannPath}")

    provider = timestampProvider or (lambda: datetime.now().astimezone())
    timestamp = provider()
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise CaptureWriteError(
            "Timestamp provider must return a timezone-aware value."
        )

    slug = slugCreate(capture.label)
    command = captureCommandBuild(capture, _clannIdRead(clannPath), timestamp)
    targetPath = clannPath / "shared" / capture.domain / f"{slug}.yaml"
    document = {
        "schema": f"eolas/{command.schema_name}/v1",
        "schemaVersion": 1,
        "recordVersion": 1,
        "id": command.identity.record_id,
        "aggregateType": command.identity.aggregate_type,
        "ownerModule": command.identity.owner_module,
        "clannRef": command.identity.clann_id,
        "label": command.label,
        "classification": command.classification.value,
        "data": dict(command.fields),
        "metadata": {
            "source": command.provenance.source_reference,
            "sourceType": command.provenance.source_type,
            "capturedAt": timestamp.isoformat(),
            "modified": timestamp.isoformat(),
        },
    }
    return targetPath, document


def captureWrite(targetPath: Path, document: Dict[str, Any]) -> Path:
    """Atomically create a prepared record without overwriting existing data."""
    targetPath.parent.mkdir(parents=True, exist_ok=True)
    if targetPath.exists():
        raise CaptureWriteError(f"Capture record already exists: {targetPath}")

    descriptor, temporaryName = tempfile.mkstemp(
        prefix=f".{targetPath.stem}-", suffix=".yaml", dir=targetPath.parent
    )
    os.close(descriptor)
    temporaryPath = Path(temporaryName)
    try:
        yamlWrite(temporaryPath, document)
        try:
            os.link(temporaryPath, targetPath)
        except FileExistsError as error:
            raise CaptureWriteError(
                f"Capture record already exists: {targetPath}"
            ) from error
        temporaryPath.unlink()
    except BaseException:
        temporaryPath.unlink(missing_ok=True)
        raise
    return targetPath


def _clannIdRead(clannPath: Path) -> str:
    import yaml

    try:
        document = yaml.safe_load(
            (clannPath / "clann.yaml").read_text(encoding="utf-8")
        )
    except (OSError, yaml.YAMLError) as error:
        raise CaptureWriteError(f"Could not read Clann index: {error}") from error
    if not isinstance(document, dict) or not isinstance(document.get("id"), str):
        raise CaptureWriteError("Clann index does not contain a valid id.")
    return document["id"]
