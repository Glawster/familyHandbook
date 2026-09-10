"""Persistence port and a local YAML adapter for versioned domain records."""

import copy
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Optional, Protocol, Tuple

import yaml
from filelock import FileLock

from eolas.domain.security import secretsValidate
from eolas.domain.values import DomainValidationError, RecordIdentity


class RecordNotFoundError(KeyError):
    """Raised when a requested aggregate is not present."""


class VersionConflictError(RuntimeError):
    """Raised when optimistic expected-version validation fails."""


class SchemaVersionError(RuntimeError):
    """Raised when persisted schema cannot be explicitly migrated."""


@dataclass(frozen=True)
class StoredRecord:
    """Persistence-neutral aggregate payload plus concurrency metadata."""

    identity: RecordIdentity
    schema_name: str
    schema_version: int
    record_version: int
    payload: Mapping[str, Any]


@dataclass(frozen=True)
class WriteOperation:
    """One create/update in an atomic change set."""

    record: StoredRecord
    expected_version: Optional[int]


class RecordStore(Protocol):
    """Canonical persistence abstraction used by domain services."""

    def recordsCommit(
        self, operations: Iterable[WriteOperation]
    ) -> Tuple[StoredRecord, ...]: ...

    def recordGet(self, identity: RecordIdentity) -> StoredRecord: ...

    def recordHistory(self, identity: RecordIdentity) -> Tuple[StoredRecord, ...]: ...


Migration = Callable[[Mapping[str, Any]], Mapping[str, Any]]


class YamlRecordStore:
    """Offline Clann-isolated YAML adapter; YAML is not the domain contract."""

    STORE_SCHEMA_VERSION = 1

    def __init__(
        self,
        path: Path,
        clann_id: str,
        migrations: Optional[Mapping[tuple[str, int], Migration]] = None,
        *,
        supports_highly_confidential: bool = False,
    ) -> None:
        self.path = path.expanduser().resolve()
        self.lock = FileLock(f"{self.path}.lock")
        self.clann_id = clann_id
        self.migrations = dict(migrations or {})
        self.supports_highly_confidential = supports_highly_confidential

    def recordGet(self, identity: RecordIdentity) -> StoredRecord:
        """Read a current record under the adapter's Clann boundary."""
        self._identityValidate(identity)
        state = self._stateLoad()
        raw = state["records"].get(identity.record_id)
        if raw is None:
            raise RecordNotFoundError(identity.record_id)
        record = self._recordDecode(raw)
        if record.identity != identity:
            raise DomainValidationError(
                "Record identity type or ownership does not match."
            )
        return record

    def recordHistory(self, identity: RecordIdentity) -> Tuple[StoredRecord, ...]:
        """Return append-only prior versions, excluding current state."""
        self._identityValidate(identity)
        state = self._stateLoad()
        history = tuple(
            self._recordDecode(raw)
            for raw in state["history"]
            if raw["identity"]["recordId"] == identity.record_id
        )
        if any(record.identity != identity for record in history):
            raise DomainValidationError(
                "Record history identity type or ownership does not match."
            )
        return history

    def recordsCommit(
        self, operations: Iterable[WriteOperation]
    ) -> Tuple[StoredRecord, ...]:
        """Atomically create/update a validated set with optimistic conflicts."""
        operationList = list(operations)
        if not operationList:
            return ()
        if len({item.record.identity.record_id for item in operationList}) != len(
            operationList
        ):
            raise DomainValidationError(
                "A change set cannot write one aggregate twice."
            )
        # Hold one cross-process lock across the complete optimistic transaction.
        # Atomic replacement protects the file itself; this lock prevents two
        # writers from both validating against the same stale snapshot.
        with self.lock:
            state = self._stateLoad()
            committed = []
            for operation in operationList:
                record = operation.record
                self._identityValidate(record.identity)
                secretsValidate(record.payload)
                if (
                    not self.supports_highly_confidential
                    and _highClassificationContains(record.payload)
                ):
                    raise DomainValidationError(
                        "This storage adapter cannot protect Highly Confidential values."
                    )
                current = state["records"].get(record.identity.record_id)
                if (
                    current is not None
                    and self._recordDecode(current).identity != record.identity
                ):
                    raise DomainValidationError(
                        "Only the owning module may update an aggregate."
                    )
                currentVersion = (
                    None if current is None else int(current["recordVersion"])
                )
                if currentVersion != operation.expected_version:
                    raise VersionConflictError(
                        f"Expected version {operation.expected_version}; "
                        f"found {currentVersion}."
                    )
                nextRecord = StoredRecord(
                    record.identity,
                    record.schema_name,
                    record.schema_version,
                    1 if currentVersion is None else currentVersion + 1,
                    copy.deepcopy(dict(record.payload)),
                )
                if current is not None:
                    state["history"].append(copy.deepcopy(current))
                state["records"][record.identity.record_id] = self._recordEncode(
                    nextRecord
                )
                committed.append(nextRecord)
            self._stateWrite(state)
            return tuple(committed)

    def recordMigrate(
        self, identity: RecordIdentity, target_version: int
    ) -> StoredRecord:
        """Apply every registered schema migration explicitly and atomically."""
        current = self.recordGet(identity)
        if target_version == current.schema_version:
            return current
        payload = dict(current.payload)
        version = current.schema_version
        while version < target_version:
            migration = self.migrations.get((current.schema_name, version))
            if migration is None:
                raise SchemaVersionError(
                    f"No migration for {current.schema_name} v{version} to v{version + 1}."
                )
            payload = dict(migration(payload))
            version += 1
        if version != target_version:
            raise SchemaVersionError("Schema downgrades are not supported.")
        candidate = StoredRecord(
            current.identity, current.schema_name, version, 0, payload
        )
        return self.recordsCommit((WriteOperation(candidate, current.record_version),))[
            0
        ]

    def _identityValidate(self, identity: RecordIdentity) -> None:
        if identity.clann_id != self.clann_id:
            raise DomainValidationError(
                "Record store rejected a cross-Clann operation."
            )

    def _recordDecode(self, raw: Mapping[str, Any]) -> StoredRecord:
        identityRaw = raw["identity"]
        identity = RecordIdentity(
            identityRaw["recordId"],
            identityRaw["clannId"],
            identityRaw["aggregateType"],
            identityRaw["ownerModule"],
        )
        self._identityValidate(identity)
        return StoredRecord(
            identity,
            str(raw["schemaName"]),
            int(raw["schemaVersion"]),
            int(raw["recordVersion"]),
            copy.deepcopy(raw["payload"]),
        )

    def _recordEncode(self, record: StoredRecord) -> Dict[str, Any]:
        return {
            "identity": {
                "recordId": record.identity.record_id,
                "clannId": record.identity.clann_id,
                "aggregateType": record.identity.aggregate_type,
                "ownerModule": record.identity.owner_module,
            },
            "schemaName": record.schema_name,
            "schemaVersion": record.schema_version,
            "recordVersion": record.record_version,
            "payload": copy.deepcopy(dict(record.payload)),
        }

    def _stateLoad(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {
                "storeSchemaVersion": self.STORE_SCHEMA_VERSION,
                "clannId": self.clann_id,
                "records": {},
                "history": [],
            }
        try:
            loaded = yaml.safe_load(self.path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as error:
            raise SchemaVersionError(f"Could not read record store: {error}") from error
        if (
            not isinstance(loaded, dict)
            or loaded.get("storeSchemaVersion") != self.STORE_SCHEMA_VERSION
        ):
            raise SchemaVersionError("Unsupported or missing store schema version.")
        if loaded.get("clannId") != self.clann_id:
            raise DomainValidationError("Record store belongs to another Clann.")
        if not isinstance(loaded.get("records"), dict) or not isinstance(
            loaded.get("history"), list
        ):
            raise SchemaVersionError("Record store structure is invalid.")
        return loaded

    def _stateWrite(self, state: Mapping[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporaryName = tempfile.mkstemp(
            prefix=f".{self.path.stem}-", suffix=self.path.suffix, dir=self.path.parent
        )
        temporaryPath = Path(temporaryName)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                yaml.safe_dump(dict(state), stream, allow_unicode=True, sort_keys=False)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporaryPath, self.path)
        except BaseException:
            temporaryPath.unlink(missing_ok=True)
            raise


def _highClassificationContains(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(
            (str(key).lower() == "classification" and child == "highlyConfidential")
            or _highClassificationContains(child)
            for key, child in value.items()
        )
    if isinstance(value, (list, tuple)):
        return any(_highClassificationContains(child) for child in value)
    return False
