"""Translate presentation-shaped capture input into typed domain commands."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping

from eolas.capture.models import CAPTURE_PROFILES, CaptureInput
from eolas.domain.security import classificationResolve, secretsValidate
from eolas.domain.values import Classification, FactState, Provenance, RecordIdentity


@dataclass(frozen=True)
class CaptureRecordCommand:
    """Typed command accepted from CLI, curses or YAML input adapters."""

    identity: RecordIdentity
    domain: str
    schema_name: str
    label: str
    fields: Mapping[str, Any]
    classification: Classification
    provenance: Provenance

    def commandValidate(self) -> None:
        """Apply shared security policy at the domain boundary."""
        classificationResolve(self.classification)
        secretsValidate(self.fields)


def captureCommandBuild(
    capture: CaptureInput, clann_id: str, captured_at: datetime
) -> CaptureRecordCommand:
    """Validate loose adapter input and produce a typed, Clann-owned command."""
    capture.captureValidate()
    profile = CAPTURE_PROFILES[capture.domain]
    command = CaptureRecordCommand(
        RecordIdentity.identityCreate(clann_id, profile.schema_name, capture.domain),
        capture.domain,
        profile.schema_name,
        capture.label.strip(),
        {name: _factEncode(value) for name, value in capture.fields.items()},
        Classification(str(capture.fields["classification"])),
        Provenance("manualCapture", capture.source.strip(), captured_at),
    )
    command.commandValidate()
    return command


def _factEncode(value: Any) -> Mapping[str, Any]:
    """Encode adapter values without conflating unknown, inapplicable or absent."""
    if value is None:
        return {"state": FactState.ABSENT.value}
    if value == FactState.UNKNOWN.value:
        return {"state": FactState.UNKNOWN.value}
    if value == FactState.NOT_APPLICABLE.value:
        return {"state": FactState.NOT_APPLICABLE.value}
    return {"state": FactState.KNOWN.value, "value": value}
