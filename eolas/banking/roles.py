"""Versioned banking continuity-role registry.

Unknown role identifiers are preserved for compatibility. They cannot drive a
current workflow until they exist in the active registry version.
"""

from typing import Mapping

CURRENT_REGISTRY_VERSION = "1"

CONTINUITY_ROLE_REGISTRY: Mapping[str, Mapping[str, str]] = {
    CURRENT_REGISTRY_VERSION: {
        "primaryHouseholdOperatingAccount": "Primary household operating account",
        "primaryHouseholdBills": "Primary household bills account",
        "emergencyReserve": "Emergency reserve",
        "personalSpending": "Personal spending",
        "salaryReceipt": "Salary or income receipt account",
        "pensionReceipt": "Pension receipt account",
        "rentalPropertyOperations": "Rental property operations",
        "taxReserve": "Tax reserve",
        "childSavings": "Child or junior savings",
        "childAccount": "Child account",
        "savings": "Savings",
        "businessOperations": "Business operations",
        "estateAdministration": "Estate-related administration",
        "other": "Other continuity purpose",
    }
}

PRIMARY_OPERATING_ROLE = "primaryHouseholdOperatingAccount"


def roleCurrent(role_id: str, registry_version: str = CURRENT_REGISTRY_VERSION) -> bool:
    """Return whether a role may drive current banking workflows."""
    return roleRegistered(role_id, registry_version)


def roleLabel(role_id: str, registry_version: str = CURRENT_REGISTRY_VERSION) -> str:
    """Return the registered label, or a compatibility placeholder."""
    return CONTINUITY_ROLE_REGISTRY.get(registry_version, {}).get(
        role_id, f"unregistered:{role_id}"
    )


def roleRegistered(
    role_id: str, registry_version: str = CURRENT_REGISTRY_VERSION
) -> bool:
    """Return whether the role exists in the named registry version."""
    return role_id in CONTINUITY_ROLE_REGISTRY.get(registry_version, {})
