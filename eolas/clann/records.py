"""Clann-scoped RecordStore adapter location.

YAML path is an adapter concern. Domain modules receive a RecordStore and must
not depend on this layout.
"""

from pathlib import Path

from eolas.domain.storage import YamlRecordStore

RECORDS_RELATIVE = Path("shared") / "records.yaml"
LEGACY_BANKING_STORE = Path("shared") / "banking" / "store.yaml"


def clannRecordStoreOpen(clannPath: Path, clann_id: str) -> YamlRecordStore:
    """Open the Clann record store, preferring the shared records file."""
    return YamlRecordStore(clannRecordStorePath(clannPath), clann_id)


def clannRecordStorePath(clannPath: Path) -> Path:
    """Return the Clann RecordStore path, with a one-way legacy fallback."""
    recordsPath = clannPath / RECORDS_RELATIVE
    legacyPath = clannPath / LEGACY_BANKING_STORE
    if recordsPath.exists() or not legacyPath.exists():
        return recordsPath
    return legacyPath
