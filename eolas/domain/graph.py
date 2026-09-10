"""Cycle-safe traversal of typed cross-domain continuity dependencies."""

from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List, Optional, Set, Tuple

from eolas.domain.values import DomainValidationError, Provenance, RecordReference


@dataclass(frozen=True)
class ContinuityDependency:
    """A directed, explained dependency published by the source's owner."""

    source: RecordReference
    target: RecordReference
    dependency_type: str
    provenance: Provenance
    explanation: str
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None

    def __post_init__(self) -> None:
        self.target.referenceValidate(self.source.clann_id)
        if not self.dependency_type.strip() or not self.explanation.strip():
            raise DomainValidationError("A dependency requires a type and explanation.")

    def dependencyEffective(self, on_date: Optional[date]) -> bool:
        """Return whether the edge applies on a date, or currently if omitted."""
        if on_date is None:
            return self.effective_to is None
        return (self.effective_from is None or self.effective_from <= on_date) and (
            self.effective_to is None or self.effective_to >= on_date
        )


@dataclass(frozen=True)
class DependencyPath:
    """One explainable graph path."""

    edges: Tuple[ContinuityDependency, ...]

    @property
    def explanation(self) -> Tuple[str, ...]:
        return tuple(edge.explanation for edge in self.edges)


class DependencyGraph:
    """Clann-isolated graph service; modules retain ownership of edge meaning."""

    def __init__(
        self, clann_id: str, dependencies: Iterable[ContinuityDependency] = ()
    ):
        self.clann_id = clann_id
        self._edges: List[ContinuityDependency] = []
        for dependency in dependencies:
            self.dependencyAdd(dependency)

    def dependencyAdd(self, dependency: ContinuityDependency) -> None:
        """Add a validated edge without mutating either endpoint aggregate."""
        dependency.source.referenceValidate(self.clann_id)
        dependency.target.referenceValidate(self.clann_id)
        self._edges.append(dependency)

    def dependencyForward(
        self, source: RecordReference, on_date: Optional[date] = None
    ) -> Tuple[ContinuityDependency, ...]:
        """Return immediate outgoing dependencies."""
        source.referenceValidate(self.clann_id)
        return tuple(
            edge
            for edge in self._edges
            if edge.source == source and edge.dependencyEffective(on_date)
        )

    def dependencyReverse(
        self, target: RecordReference, on_date: Optional[date] = None
    ) -> Tuple[ContinuityDependency, ...]:
        """Return immediate incoming dependencies."""
        target.referenceValidate(self.clann_id)
        return tuple(
            edge
            for edge in self._edges
            if edge.target == target and edge.dependencyEffective(on_date)
        )

    def dependencyTraverse(
        self,
        start: RecordReference,
        *,
        reverse: bool = False,
        on_date: Optional[date] = None,
    ) -> Tuple[DependencyPath, ...]:
        """Return cycle-safe paths reachable from a reference."""
        start.referenceValidate(self.clann_id)
        paths: List[DependencyPath] = []
        stack: List[
            tuple[RecordReference, Tuple[ContinuityDependency, ...], Set[str]]
        ] = [(start, (), {start.record_id})]
        while stack:
            current, path, visited = stack.pop()
            edges = (
                self.dependencyReverse(current, on_date)
                if reverse
                else self.dependencyForward(current, on_date)
            )
            for edge in edges:
                following = edge.source if reverse else edge.target
                nextPath = (*path, edge)
                paths.append(DependencyPath(nextPath))
                if following.record_id not in visited:
                    stack.append((following, nextPath, {*visited, following.record_id}))
        return tuple(paths)
