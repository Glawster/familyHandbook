"""Typed inputs for creating a Clann and its primary household."""

from dataclasses import dataclass
from typing import List


class ClannValidationError(ValueError):
    """Raised when Clann bootstrap input is invalid."""


@dataclass(frozen=True)
class PersonInput:
    """A person represented by the Clann."""

    full_name: str
    preferred_name: str
    household_role: str
    is_adult: bool
    is_primary: bool = False
    lives_in_primary_household: bool = True

    def personValidate(self) -> None:
        if not self.full_name.strip():
            raise ClannValidationError("Person full name cannot be empty.")
        if not self.preferred_name.strip():
            raise ClannValidationError("Preferred name cannot be empty.")
        if not self.household_role.strip():
            raise ClannValidationError("Household role cannot be empty.")


@dataclass(frozen=True)
class ClannInput:
    """Validated information needed to bootstrap a Clann."""

    name: str
    primary_household_name: str
    people: List[PersonInput]

    def clannValidate(self) -> None:
        if not self.name.strip():
            raise ClannValidationError("Clann name cannot be empty.")
        if not self.primary_household_name.strip():
            raise ClannValidationError("Primary household name cannot be empty.")
        if not self.people:
            raise ClannValidationError("A Clann must contain at least one person.")

        for person in self.people:
            person.personValidate()

        if sum(person.is_primary for person in self.people) != 1:
            raise ClannValidationError("A Clann must have exactly one primary person.")
        if not any(person.lives_in_primary_household for person in self.people):
            raise ClannValidationError(
                "The primary household must have at least one resident."
            )
