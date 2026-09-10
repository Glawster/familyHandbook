"""Typed banking identifier kinds and format checks.

Identifier values are never aggregate IDs. Format checks validate syntax only
and never claim that an account exists, is owned, or can receive payments.
"""

import re
from typing import Mapping, Optional

from eolas.domain.security import maskValue, secretsValidate
from eolas.domain.values import (
    Classification,
    DomainValidationError,
    Identifier,
    Provenance,
    VerificationState,
)

CURRENT_IDENTIFIER_REGISTRY_VERSION = "1"

IDENTIFIER_KIND_REGISTRY: Mapping[str, Mapping[str, str]] = {
    CURRENT_IDENTIFIER_REGISTRY_VERSION: {
        "accountNumber": "Account number or provider reference",
        "sortCode": "Domestic sort or routing code",
        "iban": "IBAN",
        "swiftBic": "SWIFT/BIC",
        "customerNumber": "Customer or membership number",
        "rollNumber": "Building-society roll number",
        "buildingSocietyReference": "Building-society reference",
        "creditCardAccountReference": "Credit-card account reference, not a PAN",
        "externalProductId": "Provider product identifier",
    }
}

_IBAN_PATTERN = re.compile(r"^[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}$")
_SORT_CODE_PATTERN = re.compile(r"^[0-9]{2}-[0-9]{2}-[0-9]{2}$")
_BIC_PATTERN = re.compile(r"^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}(?:[A-Z0-9]{3})?$")
PROHIBITED_IDENTIFIER_KINDS = {
    "password",
    "passcode",
    "pin",
    "cvv",
    "cvc",
    "pan",
    "cardNumber",
    "recoveryCode",
    "authenticatorSeed",
}


def identifierBankingCreate(
    identifier_type: str,
    value: str,
    classification: Classification,
    *,
    provenance: Optional[Provenance] = None,
    verification: VerificationState = VerificationState.UNVERIFIED,
    registry_version: str = CURRENT_IDENTIFIER_REGISTRY_VERSION,
) -> Identifier:
    """Build a masked banking identifier from a protected value."""
    identifierKindValidate(identifier_type, value, registry_version)
    secretsValidate({"identifier": value})
    masked = maskValue(value)
    if masked == value:
        masked = f"••••{value[-1:]}" if value else "••••"
    return Identifier(
        identifier_type,
        masked,
        classification,
        value,
        provenance,
        verification,
    )


def identifierKindCurrent(
    identifier_type: str, registry_version: str = CURRENT_IDENTIFIER_REGISTRY_VERSION
) -> bool:
    """Return whether the kind may drive a current banking workflow."""
    return identifierKindRegistered(identifier_type, registry_version)


def identifierKindRegistered(
    identifier_type: str, registry_version: str = CURRENT_IDENTIFIER_REGISTRY_VERSION
) -> bool:
    """Return whether the identifier kind exists in the named registry."""
    return identifier_type in IDENTIFIER_KIND_REGISTRY.get(registry_version, {})


def identifierKindValidate(
    identifier_type: str,
    value: str,
    registry_version: str = CURRENT_IDENTIFIER_REGISTRY_VERSION,
    *,
    format_check: bool = True,
) -> None:
    """Reject prohibited kinds and optionally check syntax of known formats."""
    normalised = "".join(
        character for character in identifier_type.lower() if character.isalnum()
    )
    if normalised in {item.lower() for item in PROHIBITED_IDENTIFIER_KINDS}:
        raise DomainValidationError(
            f"Prohibited banking identifier kind: {identifier_type}."
        )
    if not value.strip():
        raise DomainValidationError("A banking identifier value cannot be empty.")
    secretsValidate({"identifier": value})
    if not format_check:
        return
    if identifier_type == "iban" and not _IBAN_PATTERN.fullmatch(value):
        raise DomainValidationError(
            "IBAN format is invalid; format validity is not proof of existence."
        )
    if identifier_type == "sortCode" and not _SORT_CODE_PATTERN.fullmatch(value):
        raise DomainValidationError("Sort-code format is invalid.")
    if identifier_type == "swiftBic" and not _BIC_PATTERN.fullmatch(value):
        raise DomainValidationError("SWIFT/BIC format is invalid.")
    if identifier_type == "creditCardAccountReference":
        digits = "".join(character for character in value if character.isdigit())
        if 13 <= len(digits) <= 19:
            raise DomainValidationError(
                "A credit-card account reference must not be a full payment-card number."
            )
