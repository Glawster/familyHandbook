"""Store-backed lookup of shared party and organisation aggregates."""

from typing import Tuple

from eolas.domain.codec import (
    CONTACT_SCHEMA,
    ORGANISATION_SCHEMA,
    PERSON_SCHEMA,
    contactDecode,
    organisationDecode,
    personDecode,
)
from eolas.domain.entities import Contact, Organisation, Person
from eolas.domain.storage import RecordNotFoundError, RecordStore
from eolas.domain.values import DomainValidationError, RecordIdentity


def contactLoad(store: RecordStore, identity: RecordIdentity) -> Contact:
    """Load a Contact by identity."""
    return contactDecode(store.recordGet(identity))


def contactsLoad(store: RecordStore) -> Tuple[Contact, ...]:
    """Return current Contact aggregates in the store."""
    return tuple(
        contactDecode(record)
        for record in store.recordsList(aggregate_type="contact", owner_module="shared")
        if record.schema_name == CONTACT_SCHEMA
    )


def organisationLoad(store: RecordStore, identity: RecordIdentity) -> Organisation:
    """Load an Organisation by identity."""
    return organisationDecode(store.recordGet(identity))


def organisationsLoad(store: RecordStore) -> Tuple[Organisation, ...]:
    """Return current Organisation aggregates in the store."""
    return tuple(
        organisationDecode(record)
        for record in store.recordsList(
            aggregate_type="organisation", owner_module="shared"
        )
        if record.schema_name == ORGANISATION_SCHEMA
    )


def partyLoad(store: RecordStore, identity: RecordIdentity) -> Person | Contact:
    """Load a Person or Contact; reject other aggregate types."""
    if identity.aggregate_type == "person":
        return personLoad(store, identity)
    if identity.aggregate_type == "contact":
        return contactLoad(store, identity)
    raise DomainValidationError("An account party must reference a Person or Contact.")


def partyLoadById(
    store: RecordStore, clann_id: str, record_id: str
) -> Person | Contact:
    """Resolve a party from an explicit record ID without guessing type."""
    for aggregate_type, loader in (
        ("person", personLoad),
        ("contact", contactLoad),
    ):
        identity = RecordIdentity(record_id, clann_id, aggregate_type, "shared")
        try:
            return loader(store, identity)
        except (KeyError, RecordNotFoundError, DomainValidationError):
            continue
    raise DomainValidationError(f"Unknown party reference: {record_id}.")


def personLoad(store: RecordStore, identity: RecordIdentity) -> Person:
    """Load a Person by identity."""
    return personDecode(store.recordGet(identity))


def peopleLoad(store: RecordStore) -> Tuple[Person, ...]:
    """Return current Person aggregates in the store."""
    return tuple(
        personDecode(record)
        for record in store.recordsList(aggregate_type="person", owner_module="shared")
        if record.schema_name == PERSON_SCHEMA
    )


def peopleNamed(store: RecordStore, display_name: str) -> Tuple[Person, ...]:
    """Return People whose display name matches exactly."""
    return tuple(
        person for person in peopleLoad(store) if person.display_name == display_name
    )
