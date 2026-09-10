"""Central security, classification, masking and export policy."""

import re
from enum import Enum
from typing import Any, Mapping

from eolas.domain.values import Classification, DomainValidationError


class ProhibitedSemantic(str, Enum):
    """Semantic values Eolas must never persist."""

    PASSWORD = "password"
    PASSCODE = "passcode"
    PIN = "pin"
    CARD_SECURITY_CODE = "cardSecurityCode"
    SECURITY_ANSWER = "securityAnswer"
    RECOVERY_CODE = "recoveryCode"
    AUTHENTICATOR_SEED = "authenticatorSeed"
    ONE_TIME_CODE = "oneTimeCode"
    ACCESS_TOKEN = "accessToken"
    SIGNING_MATERIAL = "signingMaterial"


_ALIASES = {
    "password": ProhibitedSemantic.PASSWORD,
    "passwd": ProhibitedSemantic.PASSWORD,
    "passcode": ProhibitedSemantic.PASSCODE,
    "pin": ProhibitedSemantic.PIN,
    "pincode": ProhibitedSemantic.PIN,
    "cvv": ProhibitedSemantic.CARD_SECURITY_CODE,
    "cvc": ProhibitedSemantic.CARD_SECURITY_CODE,
    "cardsecuritycode": ProhibitedSemantic.CARD_SECURITY_CODE,
    "securityanswer": ProhibitedSemantic.SECURITY_ANSWER,
    "recoverycode": ProhibitedSemantic.RECOVERY_CODE,
    "backupcode": ProhibitedSemantic.RECOVERY_CODE,
    "authenticatorseed": ProhibitedSemantic.AUTHENTICATOR_SEED,
    "mfasecret": ProhibitedSemantic.AUTHENTICATOR_SEED,
    "totpseed": ProhibitedSemantic.AUTHENTICATOR_SEED,
    "seedphrase": ProhibitedSemantic.AUTHENTICATOR_SEED,
    "onetimecode": ProhibitedSemantic.ONE_TIME_CODE,
    "otp": ProhibitedSemantic.ONE_TIME_CODE,
    "sessiontoken": ProhibitedSemantic.ACCESS_TOKEN,
    "accesstoken": ProhibitedSemantic.ACCESS_TOKEN,
    "privatekey": ProhibitedSemantic.SIGNING_MATERIAL,
    "signingkey": ProhibitedSemantic.SIGNING_MATERIAL,
    "signingsecret": ProhibitedSemantic.SIGNING_MATERIAL,
    "gatewaycredential": ProhibitedSemantic.SIGNING_MATERIAL,
}


def classificationResolve(
    record_default: Classification | None,
    field_override: Classification | None = None,
) -> Classification:
    """Resolve explicit handling classifications without a permissive default."""
    if not isinstance(record_default, Classification):
        raise DomainValidationError("A valid classification is required.")
    if field_override is not None and not isinstance(field_override, Classification):
        raise DomainValidationError("A field classification must be valid.")
    return record_default.classificationCombine(field_override)


def fieldExport(
    value: str, classification: Classification, *, privileged: bool = False
) -> str:
    """Apply UI-independent masking policy to exported fields."""
    if classification.rank >= Classification.CONFIDENTIAL.rank and not privileged:
        return maskValue(value)
    return value


def maskValue(value: str, visible: int = 4) -> str:
    """Mask a value while retaining a short recognition suffix."""
    if not value:
        return ""
    suffix = value[-visible:] if len(value) > visible else value[-1:]
    return f"••••{suffix}"


def secretsValidate(value: Any, path: str = "fields") -> None:
    """Reject controlled secret semantics and complete payment-card numbers."""
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalised = _nameNormalise(key)
            if normalised in _ALIASES:
                raise DomainValidationError(
                    f"Prohibited credential field at {path}.{key}."
                )
            secretsValidate(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            secretsValidate(child, f"{path}[{index}]")
    elif isinstance(value, str) and _cardNumberLooksComplete(value):
        raise DomainValidationError(
            f"Full payment-card number at {path} is prohibited."
        )


def _cardNumberLooksComplete(value: str) -> bool:
    if not re.fullmatch(r"[0-9 -]+", value):
        return False
    digits = "".join(character for character in value if character.isdigit())
    if not 13 <= len(digits) <= 19:
        return False
    checksum = 0
    parity = len(digits) % 2
    for index, character in enumerate(digits):
        number = int(character)
        if index % 2 == parity:
            number = number * 2 - 9 if number > 4 else number * 2
        checksum += number
    return checksum % 10 == 0


def _nameNormalise(value: object) -> str:
    return "".join(character for character in str(value).lower() if character.isalnum())
