"""YAML document builders for the initial Clann structure."""

from datetime import datetime
from typing import Any, Dict, Mapping

from eolas.clann.manifest import PERSON_SECTIONS
from eolas.clann.models import ClannInput, PersonInput
from eolas.clann.names import nameParse


def clannDocumentBuild(
    clann: ClannInput,
    clannId: str,
    householdId: str,
    personIds: Mapping[int, str],
    timestamp: datetime,
) -> Dict[str, Any]:
    """Build the Clann index document."""

    primaryIndex = next(
        index for index, person in enumerate(clann.people) if person.is_primary
    )
    timestampValue = timestamp.isoformat()
    return {
        "schema": "eolas/clann/v1",
        "id": clannId,
        "name": clann.name.strip(),
        "primaryPersonRef": personIds[primaryIndex],
        "primaryHouseholdRef": householdId,
        "people": [
            {"personRef": personIds[index]} for index in range(len(clann.people))
        ],
        "households": [{"householdRef": householdId}],
        "metadata": {
            "status": "active",
            "created": timestampValue,
            "modified": timestampValue,
            "lastReviewed": None,
            "nextReview": None,
        },
    }


def householdDocumentBuild(
    clann: ClannInput,
    clannId: str,
    householdId: str,
    personIds: Mapping[int, str],
    timestamp: datetime,
) -> Dict[str, Any]:
    """Build the primary household document."""

    timestampValue = timestamp.isoformat()
    return {
        "schema": "eolas/household/v1",
        "id": householdId,
        "clannRef": clannId,
        "name": clann.primary_household_name.strip(),
        "members": [
            {
                "personRef": personIds[index],
                "role": person.household_role.strip(),
                "status": "resident",
            }
            for index, person in enumerate(clann.people)
            if person.lives_in_primary_household
        ],
        "addressRef": None,
        "metadata": {
            "status": "active",
            "created": timestampValue,
            "modified": timestampValue,
            "lastReviewed": None,
            "nextReview": None,
        },
    }


def personDocumentBuild(
    person: PersonInput,
    personId: str,
    clannId: str,
    householdId: str,
    timestamp: datetime,
) -> Dict[str, Any]:
    """Build a Clann-scoped person index document."""

    timestampValue = timestamp.isoformat()
    memberships = []
    if person.lives_in_primary_household:
        memberships.append(
            {
                "householdRef": householdId,
                "role": person.household_role.strip(),
                "status": "resident",
            }
        )
    return {
        "schema": "eolas/person/v1",
        "id": personId,
        "clannRef": clannId,
        "name": {
            "displayName": person.full_name.strip(),
            "preferredName": person.preferred_name.strip(),
        },
        "isAdult": person.is_adult,
        "isPrimary": person.is_primary,
        "householdMemberships": memberships,
        "sections": {
            name: section["filename"] for name, section in PERSON_SECTIONS.items()
        },
        "metadata": {
            "status": "active",
            "created": timestampValue,
            "modified": timestampValue,
            "lastReviewed": None,
            "nextReview": None,
        },
    }


def identityDocumentBuild(
    person: PersonInput,
    personId: str,
    timestamp: datetime,
) -> Dict[str, Any]:
    """Build the initial identity document for a person."""

    parsedName = nameParse(person.full_name)
    timestampValue = timestamp.isoformat()
    return {
        "schema": PERSON_SECTIONS["identity"]["schema"],
        "personRef": personId,
        "personal": {
            "title": None,
            "firstName": parsedName.first_name,
            "middleNames": parsedName.middle_names,
            "lastName": parsedName.last_name,
            "preferredName": person.preferred_name.strip(),
            "previousNames": [],
            "dateOfBirth": None,
            "placeOfBirth": {
                "townOrCity": None,
                "countyOrRegion": None,
                "country": None,
            },
            "nationality": [],
            "maritalStatus": None,
        },
        "identifiers": {
            "nationalInsuranceNumber": None,
            "nhsNumber": None,
        },
        "documents": {
            "passportRef": None,
            "drivingLicenceRef": None,
            "birthCertificateRef": None,
            "marriageCertificateRef": None,
            "willRef": None,
            "lastingPowerOfAttorneyRefs": [],
        },
        "medicalSummary": {
            "bloodGroup": None,
            "allergiesKnown": None,
        },
        "photograph": {"fileRef": None},
        "notes": None,
        "metadata": {
            "status": "draft",
            "created": timestampValue,
            "modified": timestampValue,
            "lastVerified": None,
            "nextReview": None,
        },
    }
