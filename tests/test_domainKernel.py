"""Conformance tests for the Phase 1 shared knowledge kernel."""

from datetime import date, datetime, timezone
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import socket
from threading import Barrier

import pytest
import yaml

from eolas.domain.entities import (
    Authority,
    AuthorityRegistration,
    AuthorityState,
    Contact,
    ContactRoute,
    ContinuityAction,
    GuidanceReference,
    Interaction,
    Organisation,
    OrganisationBrand,
    OrganisationRole,
    PartyRole,
    Person,
    RegistrationState,
)
from eolas.domain.graph import ContinuityDependency, DependencyGraph
from eolas.domain.security import classificationResolve, fieldExport, secretsValidate
from eolas.domain.storage import (
    SchemaVersionError,
    StoredRecord,
    VersionConflictError,
    WriteOperation,
    YamlRecordStore,
)
from eolas.domain.values import (
    Classification,
    DomainValidationError,
    EvidenceReference,
    Fact,
    FactState,
    Identifier,
    Jurisdiction,
    Money,
    Observation,
    ObservationStatus,
    Provenance,
    RecordIdentity,
    ReviewState,
)

NOW = datetime(2026, 9, 1, 10, 0, tzinfo=timezone.utc)
CLANN = "clann-fictional-morgan"


def _identity(kind: str, owner: str = "shared") -> RecordIdentity:
    return RecordIdentity.identityCreate(CLANN, kind, owner)


def _provenance() -> Provenance:
    return Provenance("fictionalFixture", "scenario-v1", NOW)


def _evidence() -> EvidenceReference:
    return EvidenceReference(
        "ev_fictional_notice",
        CLANN,
        "authority confirmation",
        "a" * 64,
        "evidence://immutable/fictional-notice",
        Classification.CONFIDENTIAL,
        _provenance(),
    )


def _foreignReference(kind: str = "person"):
    return RecordIdentity.identityCreate(
        "another-clann", kind, "shared"
    ).referenceCreate()


def _foreignEvidence() -> EvidenceReference:
    return EvidenceReference(
        "ev_foreign_notice",
        "another-clann",
        "foreign fixture",
        "b" * 64,
        "evidence://immutable/foreign-notice",
        Classification.CONFIDENTIAL,
        _provenance(),
    )


def testRecordIdentityIsStableOpaqueAndOwned() -> None:
    identity = _identity("organisation", "shared")

    assert identity == identity
    assert identity.record_id.startswith("rec_")
    assert "organisation" not in identity.record_id
    assert identity.owner_module == "shared"


def testRecordReferenceRejectsCrossClann() -> None:
    reference = _identity("person").referenceCreate()

    with pytest.raises(DomainValidationError, match="Cross-Clann"):
        reference.referenceValidate("another-clann")


@pytest.mark.parametrize(
    "fact",
    [
        Fact.factKnown("value"),
        Fact(FactState.UNKNOWN),
        Fact(FactState.NOT_APPLICABLE),
        Fact(FactState.ABSENT),
    ],
)
def testFactStatesAreDistinct(fact: Fact[str]) -> None:
    assert FactState(fact.state.value) is fact.state


def testFactStateDoesNotCoerceInvalidValue() -> None:
    with pytest.raises(DomainValidationError):
        Fact(FactState.UNKNOWN, "silently retained")


def testClassificationFailsClosedAndMasksWithoutUI() -> None:
    with pytest.raises(DomainValidationError, match="classification"):
        classificationResolve(None)
    with pytest.raises(DomainValidationError, match="classification"):
        classificationResolve("private")  # type: ignore[arg-type]
    assert (
        classificationResolve(Classification.PRIVATE, Classification.CONFIDENTIAL)
        is Classification.CONFIDENTIAL
    )
    assert fieldExport("FICTIONAL-REF-42", Classification.CONFIDENTIAL) == "••••F-42"


def testSharedAggregatesRejectNestedCrossClannValues() -> None:
    route = ContactRoute(
        "email",
        "fictional@example.invalid",
        "correspondence",
        Classification.PRIVATE,
        Fact(FactState.UNKNOWN),
        Provenance("fixture", "route", NOW, _foreignReference()),
    )
    with pytest.raises(DomainValidationError, match="Cross-Clann"):
        Person(
            _identity("person"),
            "Morgan Example",
            Classification.PRIVATE,
            contact_routes=(route,),
        )
    with pytest.raises(DomainValidationError, match="Cross-Clann"):
        Contact(
            _identity("contact"),
            "Riley Example",
            Classification.PRIVATE,
            represented_party=_foreignReference(),
        )
    with pytest.raises(DomainValidationError, match="same Clann"):
        Organisation(
            _identity("organisation"),
            "Example Provider",
            Classification.PRIVATE,
            brands=(OrganisationBrand("Example", evidence=(_foreignEvidence(),)),),
        )


def testContinuityAndInteractionRejectCrossClannValues() -> None:
    subject = _identity("obligation").referenceCreate()
    role = PartyRole(_identity("person").referenceCreate(), subject, "responsible")
    review = ReviewState(
        Fact(FactState.UNKNOWN),
        Fact(FactState.UNKNOWN),
        Fact(FactState.UNKNOWN),
    )
    with pytest.raises(DomainValidationError, match="Cross-Clann"):
        ContinuityAction(
            _identity("continuityAction"),
            "review",
            _foreignReference("obligation"),
            role,
            "open",
            Fact(FactState.UNKNOWN),
            (),
            (),
            Fact(FactState.UNKNOWN),
            review,
        )
    with pytest.raises(DomainValidationError, match="Cross-Clann"):
        Interaction(
            _identity("interaction"),
            NOW,
            (_foreignReference("organisation"),),
            "review",
            "Fictional summary",
            Fact(FactState.UNKNOWN),
            Fact(FactState.UNKNOWN),
            (),
            Classification.PRIVATE,
            _provenance(),
        )


def testSharedEntityCompositionsAcceptSameClannValues() -> None:
    route = ContactRoute(
        "email",
        "fictional@example.invalid",
        "correspondence",
        Classification.PRIVATE,
        Fact.factKnown(date(2026, 8, 1)),
        _provenance(),
        "Written contact preferred",
    )
    person = Person(
        _identity("person"),
        "Morgan Example",
        Classification.PRIVATE,
        contact_routes=(route,),
    )
    contact = Contact(
        _identity("contact"),
        "Riley Example",
        Classification.PRIVATE,
        represented_party=person.identity.referenceCreate(),
        contact_routes=(route,),
    )
    brand = OrganisationBrand(
        "Example Provider",
        effective_from=date(2026, 1, 1),
        evidence=(_evidence(),),
    )
    organisation = Organisation(
        _identity("organisation"),
        "Example Provider Cooperative",
        Classification.PRIVATE,
        brands=(brand,),
        contact_routes=(route,),
    )
    organisationRole = OrganisationRole(
        organisation.identity.referenceCreate(),
        "fixtureProvider",
        "fixture",
    )
    subject = _identity("obligation", "fixture").referenceCreate()
    responsibleRole = PartyRole(
        contact.identity.referenceCreate(),
        subject,
        "responsibleContact",
        provenance=_provenance(),
    )
    guidance = GuidanceReference(
        "fixture-guidance",
        Jurisdiction("GB", "ISO-3166-1", "2026"),
        "1",
        date(2026, 1, 1),
        date(2026, 8, 1),
        "fixture://guidance",
    )
    review = ReviewState(
        Fact.factKnown(date(2026, 8, 1)),
        Fact.factKnown(date(2027, 8, 1)),
        Fact.factKnown(contact.identity.referenceCreate()),
    )
    action = ContinuityAction(
        _identity("continuityAction"),
        "reviewEssentialService",
        subject,
        responsibleRole,
        "open",
        Fact(FactState.UNKNOWN),
        (guidance,),
        (_evidence(),),
        Fact(FactState.UNKNOWN),
        review,
    )
    interaction = Interaction(
        _identity("interaction"),
        NOW,
        (contact.identity.referenceCreate(), organisation.identity.referenceCreate()),
        "review",
        "Fictional provider review",
        Fact(FactState.UNKNOWN),
        Fact.factKnown(date(2026, 9, 15)),
        (_evidence(),),
        Classification.CONFIDENTIAL,
        _provenance(),
    )

    assert organisationRole.organisation == organisation.identity.referenceCreate()
    assert action.guidance == (guidance,)
    assert interaction.parties[0] == contact.identity.referenceCreate()


def testIdentifierHasTypedMaskedDisplayAndNeverBecomesIdentity() -> None:
    identifier = Identifier(
        "fictionalCustomerReference",
        "••••0042",
        Classification.CONFIDENTIAL,
        protected_value="NOT-ROUTABLE-0042",
        provenance=_provenance(),
    )

    assert identifier.identifierDisplay() == "••••0042"
    assert identifier.identifierDisplay(allow_protected=True) == "NOT-ROUTABLE-0042"
    assert not isinstance(identifier, RecordIdentity)


@pytest.mark.parametrize(
    "field",
    [
        "password",
        "passcode",
        "pin",
        "cvv",
        "securityAnswer",
        "recoveryCode",
        "mfaSecret",
        "otp",
        "accessToken",
        "privateKey",
    ],
)
def testSecretsValidateRejectsControlledSemanticAliases(field: str) -> None:
    with pytest.raises(DomainValidationError, match="Prohibited"):
        secretsValidate({field: "never-store"})


@pytest.mark.parametrize(
    "field",
    [
        "shippingAddress",
        "opinion",
        "pinningNote",
        "pensionProvider",
        "accessibilityNote",
        "capitalIncome",
    ],
)
def testSecretsValidateDoesNotRejectHarmlessSubstrings(field: str) -> None:
    secretsValidate({field: "fictional safe note"})


def testSecretsValidateRejectsFullPaymentCardNumber() -> None:
    with pytest.raises(DomainValidationError, match="payment-card"):
        secretsValidate({"notes": "4111 1111 1111 1111"})


def testProvenanceEvidenceAndObservationAreDatedAndTraceable() -> None:
    observation = Observation(
        Money(Decimal("12.34"), "GBP"),
        NOW,
        _provenance(),
        ObservationStatus.PROVIDER_CONFIRMED,
        Decimal("1"),
    )

    assert observation.as_of == NOW
    assert observation.provenance.source_reference == "scenario-v1"
    assert _evidence().checksum_sha256 == "a" * 64


@pytest.mark.parametrize(
    "locator",
    [
        "/home/person/private.pdf",
        "file:///private/evidence.pdf",
        "https://user:password@example.invalid/evidence",
        "evidence://immutable/item?token=secret",
        "evidence://immutable/../outside",
        "evidence://immutable/%2e%2e/outside",
    ],
)
def testEvidenceReferenceRejectsUnsafeLocator(locator: str) -> None:
    with pytest.raises(DomainValidationError, match="opaque evidence"):
        EvidenceReference(
            "ev_unsafe",
            CLANN,
            "unsafe locator test",
            "c" * 64,
            locator,
            Classification.CONFIDENTIAL,
            _provenance(),
        )


def testMoneyRejectsBinaryFloatingPoint() -> None:
    with pytest.raises(DomainValidationError, match="binary"):
        Money(12.34, "GBP")  # type: ignore[arg-type]


def testAuthorityAndProviderRegistrationAreSeparateStates() -> None:
    grantor = _identity("person").referenceCreate()
    actor = _identity("person").referenceCreate()
    provider = _identity("organisation").referenceCreate()
    authorityIdentity = _identity("authority")
    authority = Authority(
        authorityIdentity,
        grantor,
        actor,
        "fictionalPropertyAuthority",
        Jurisdiction("GB-SCT", "ISO-3166-2", "2026"),
        ("manageHouseholdPayments",),
        ("grantorUnavailable",),
        (),
        AuthorityState.ACTIVE,
        date(2026, 1, 1),
        None,
        (_evidence(),),
        Classification.CONFIDENTIAL,
    )
    registration = AuthorityRegistration(
        _identity("authorityRegistration"),
        authorityIdentity.referenceCreate(),
        provider,
        RegistrationState.PENDING,
        None,
        (),
        (),
        None,
        (_evidence(),),
    )

    assert authority.authorityAllows("manageHouseholdPayments", date(2026, 9, 1))
    assert registration.state is RegistrationState.PENDING


@pytest.mark.parametrize("state", [AuthorityState.EXPIRED, AuthorityState.REVOKED])
def testAuthorityExpiredRevokedOrRestrictedCannotAct(state: AuthorityState) -> None:
    authority = Authority(
        _identity("authority"),
        _identity("person").referenceCreate(),
        _identity("person").referenceCreate(),
        "fictionalTrusteeAuthority",
        Jurisdiction("GB", "ISO-3166-1", "2026"),
        ("manage",),
        (),
        ("manage",),
        state,
        date(2025, 1, 1),
        date(2026, 1, 1),
        (_evidence(),),
        Classification.CONFIDENTIAL,
    )

    assert not authority.authorityAllows("manage", date(2026, 9, 1))


def testDependencyGraphTraversesForwardReverseAndCyclesSafely() -> None:
    income = _identity("income", "pensions").referenceCreate()
    account = _identity("accountLikeFixture", "fixture").referenceCreate()
    payment = _identity("paymentLikeFixture", "fixture").referenceCreate()
    edges = (
        ContinuityDependency(
            income,
            account,
            "paidInto",
            _provenance(),
            "Pension income is paid into the household account.",
        ),
        ContinuityDependency(
            account,
            payment,
            "funds",
            _provenance(),
            "The household account funds the electricity payment.",
        ),
        ContinuityDependency(
            payment,
            account,
            "reconcilesWith",
            _provenance(),
            "The fictional payment is reconciled to the account.",
        ),
    )
    graph = DependencyGraph(CLANN, edges)

    assert graph.dependencyForward(income) == (edges[0],)
    assert graph.dependencyReverse(payment) == (edges[1],)
    paths = graph.dependencyTraverse(income)
    assert len(paths) == 3
    assert paths[1].explanation[-1] == edges[1].explanation


def testDependencyGraphRejectsCrossClannEdge() -> None:
    with pytest.raises(DomainValidationError, match="Cross-Clann"):
        ContinuityDependency(
            _identity("source").referenceCreate(),
            RecordIdentity.identityCreate(
                "other", "target", "shared"
            ).referenceCreate(),
            "dependsOn",
            _provenance(),
            "Invalid cross-boundary edge.",
        )


def testYamlStoreAtomicWritesHistoryConflictsAndClannIsolation(
    tmp_path: Path,
) -> None:
    store = YamlRecordStore(tmp_path / "kernel.yaml", CLANN)
    identity = _identity("organisation")
    first = StoredRecord(
        identity, "organisation", 1, 0, {"name": "Fictional Energy Cooperative"}
    )
    created = store.recordsCommit((WriteOperation(first, None),))[0]
    second = StoredRecord(
        identity, "organisation", 1, 0, {"name": "Fictional Energy Co-op"}
    )
    updated = store.recordsCommit((WriteOperation(second, created.record_version),))[0]

    assert updated.record_version == 2
    assert (
        store.recordHistory(identity)[0].payload["name"]
        == "Fictional Energy Cooperative"
    )
    with pytest.raises(VersionConflictError):
        store.recordsCommit((WriteOperation(second, 1),))
    wrongOwner = RecordIdentity(identity.record_id, CLANN, "organisation", "banking")
    with pytest.raises(DomainValidationError, match="owning module|ownership"):
        store.recordsCommit(
            (
                WriteOperation(
                    StoredRecord(wrongOwner, "organisation", 1, 0, {"name": "X"}),
                    updated.record_version,
                ),
            )
        )
    with pytest.raises(DomainValidationError, match="cross-Clann"):
        store.recordGet(
            RecordIdentity.identityCreate("other", "organisation", "shared")
        )

    forgedIdentity = RecordIdentity(
        identity.record_id, CLANN, "organisation", "banking"
    )
    with pytest.raises(DomainValidationError, match="history identity"):
        store.recordHistory(forgedIdentity)


def testYamlStoreSerialisesConcurrentExpectedVersionChecks(tmp_path: Path) -> None:
    path = tmp_path / "kernel.yaml"
    identity = _identity("organisation")
    barrier = Barrier(2)

    def create(label: str) -> str:
        store = YamlRecordStore(path, CLANN)
        candidate = StoredRecord(identity, "organisation", 1, 0, {"name": label})
        barrier.wait()
        try:
            store.recordsCommit((WriteOperation(candidate, None),))
            return "committed"
        except VersionConflictError:
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = tuple(executor.map(create, ("Provider A", "Provider B")))

    assert sorted(results) == ["committed", "conflict"]
    assert YamlRecordStore(path, CLANN).recordGet(identity).record_version == 1


def testYamlStoreChangeSetIsAtomicOnValidationFailure(tmp_path: Path) -> None:
    path = tmp_path / "kernel.yaml"
    store = YamlRecordStore(path, CLANN)
    safe = StoredRecord(_identity("person"), "person", 1, 0, {"name": "Morgan Example"})
    unsafe = StoredRecord(_identity("contact"), "contact", 1, 0, {"password": "never"})

    with pytest.raises(DomainValidationError):
        store.recordsCommit((WriteOperation(safe, None), WriteOperation(unsafe, None)))
    assert not path.exists()


def testYamlStoreFailsClosedForUnprotectedHighlyConfidentialValues(
    tmp_path: Path,
) -> None:
    store = YamlRecordStore(tmp_path / "kernel.yaml", CLANN)
    record = StoredRecord(
        _identity("contact"),
        "contact",
        1,
        0,
        {"classification": "highlyConfidential", "value": "sensitive"},
    )

    with pytest.raises(DomainValidationError, match="cannot protect"):
        store.recordsCommit((WriteOperation(record, None),))


def testYamlStoreRunsExplicitMigration(tmp_path: Path) -> None:
    store = YamlRecordStore(
        tmp_path / "kernel.yaml",
        CLANN,
        {("organisation", 1): lambda payload: {**payload, "status": "active"}},
    )
    identity = _identity("organisation")
    record = StoredRecord(
        identity, "organisation", 1, 0, {"name": "Fictional Provider"}
    )
    store.recordsCommit((WriteOperation(record, None),))

    migrated = store.recordMigrate(identity, 2)

    assert migrated.schema_version == 2
    assert migrated.payload["status"] == "active"
    with pytest.raises(SchemaVersionError):
        store.recordMigrate(identity, 3)


def testKernelAndStoreRequireNoNetwork(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def networkFail(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "socket", networkFail)
    identity = _identity("organisation")
    store = YamlRecordStore(tmp_path / "offline.yaml", CLANN)
    record = StoredRecord(identity, "organisation", 1, 0, {"name": "Offline Example"})

    store.recordsCommit((WriteOperation(record, None),))

    assert store.recordGet(identity).payload["name"] == "Offline Example"


def testFictionalConformanceFixtureHasTwoHouseholdsAndDependencyChain() -> None:
    fixturePath = Path("data/conformance/phaseOneFictionalScenario.yaml")
    fixture = yaml.safe_load(fixturePath.read_text(encoding="utf-8"))

    assert fixture["fictional"] is True
    assert len(fixture["households"]) >= 2
    assert len(fixture["dependencies"]) == 4
    assert any(event["type"] == "death" for event in fixture["events"])
    assert any(
        role["role"] == "fictionalAccountProvider"
        for role in fixture["organisationRoles"]
    )
    assert fixture["accountLikeRelationship"]["fullReference"] == "absent"
    secretsValidate(fixture)
