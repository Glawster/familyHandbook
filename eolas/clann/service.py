"""Atomic Clann creation service."""

import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Optional

from eolas.clann.documents import (
    clannDocumentBuild,
    householdDocumentBuild,
    identityDocumentBuild,
    personDocumentBuild,
)
from eolas.clann.manifest import CLANN_DIRECTORIES, PERSON_SECTIONS
from eolas.clann.models import ClannInput
from eolas.clann.records import RECORDS_RELATIVE
from eolas.clann.slugs import slugCreate, slugsCreateUnique
from eolas.clann.yaml_io import yamlWrite
from eolas.domain.codec import personEncode
from eolas.domain.entities import Person
from eolas.domain.storage import WriteOperation, YamlRecordStore
from eolas.domain.values import Classification, RecordIdentity


class ClannCreationError(RuntimeError):
    """Raised when a Clann cannot be safely created."""


TimestampProvider = Callable[[], datetime]


def clannCreate(
    clann: ClannInput,
    outputDirectory: Path,
    *,
    timestampProvider: Optional[TimestampProvider] = None,
) -> Path:
    """Validate and atomically create ``clanns/<slug>`` under a data root."""

    clann.clannValidate()
    outputDirectory = outputDirectory.expanduser().resolve()
    if outputDirectory.exists() and not outputDirectory.is_dir():
        raise ClannCreationError(f"Output path is not a directory: {outputDirectory}")

    clannsPath = outputDirectory / "clanns"
    clannsPath.mkdir(parents=True, exist_ok=True)
    clannSlug = slugCreate(clann.name)
    targetPath = clannsPath / clannSlug
    if targetPath.exists() and any(targetPath.iterdir()):
        raise ClannCreationError(
            f"Target directory already exists and is not empty: {targetPath}. "
            "Choose a different Clann name or output directory."
        )

    provider = timestampProvider or (lambda: datetime.now().astimezone())
    timestamp = provider()
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ClannCreationError(
            "Timestamp provider must return a timezone-aware value."
        )

    personSlugs = slugsCreateUnique(person.full_name for person in clann.people)
    clannId = f"clann-{clannSlug}"
    householdSlug = slugCreate(clann.primary_household_name)
    householdId = RecordIdentity.identityCreate(
        clannId, "household", "shared"
    ).record_id
    personIds: Dict[int, str] = {
        index: RecordIdentity.identityCreate(clannId, "person", "shared").record_id
        for index in range(len(clann.people))
    }

    temporaryPath = Path(tempfile.mkdtemp(prefix=f".{clannSlug}-", dir=clannsPath))
    try:
        _clannTreeWrite(
            temporaryPath,
            clann,
            clannId,
            householdId,
            householdSlug,
            personSlugs,
            personIds,
            timestamp,
        )
        if targetPath.exists():
            targetPath.rmdir()
        temporaryPath.rename(targetPath)
    except BaseException:
        if temporaryPath.exists():
            shutil.rmtree(temporaryPath)
        if clannsPath.exists() and not any(clannsPath.iterdir()):
            clannsPath.rmdir()
        if outputDirectory.exists() and not any(outputDirectory.iterdir()):
            outputDirectory.rmdir()
        raise

    return targetPath


def _clannTreeWrite(
    rootPath: Path,
    clann: ClannInput,
    clannId: str,
    householdId: str,
    householdSlug: str,
    personSlugs: list[str],
    personIds: Dict[int, str],
    timestamp: datetime,
) -> None:
    """Build all content beneath an isolated temporary root."""

    for directoryName in CLANN_DIRECTORIES:
        (rootPath / directoryName).mkdir()

    yamlWrite(
        rootPath / "clann.yaml",
        clannDocumentBuild(clann, clannId, householdId, personIds, timestamp),
    )

    householdPath = rootPath / "households" / householdSlug
    householdPath.mkdir()
    yamlWrite(
        householdPath / "household.yaml",
        householdDocumentBuild(clann, clannId, householdId, personIds, timestamp),
    )

    for index, person in enumerate(clann.people):
        personPath = rootPath / "people" / personSlugs[index]
        personPath.mkdir()
        personId = personIds[index]
        yamlWrite(
            personPath / "person.yaml",
            personDocumentBuild(person, personId, clannId, householdId, timestamp),
        )
        yamlWrite(
            personPath / PERSON_SECTIONS["identity"]["filename"],
            identityDocumentBuild(person, personId, timestamp),
        )

    _peopleStoreWrite(rootPath, clann, clannId, personIds)


def _peopleStoreWrite(
    rootPath: Path,
    clann: ClannInput,
    clannId: str,
    personIds: Dict[int, str],
) -> None:
    """Persist Person aggregates through the shared RecordStore port."""
    store = YamlRecordStore(rootPath / RECORDS_RELATIVE, clannId)
    operations = tuple(
        WriteOperation(
            personEncode(
                Person(
                    RecordIdentity(personIds[index], clannId, "person", "shared"),
                    person.full_name.strip(),
                    Classification.PRIVATE,
                )
            ),
            None,
        )
        for index, person in enumerate(clann.people)
    )
    store.recordsCommit(operations)
