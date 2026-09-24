"""In-memory stand-in for the snapshot index (MODEL-138).

MODEL-138 owns ``decision/snapshot.py`` and had not merged when MODEL-141 was
written, so this module copies the protocol from the slice-1 brief. The filter
imports none of it: it calls the methods structurally. When ``decision.snapshot``
lands, this copy should be checked against it and then deleted.

``ids_where`` ops the filter sends: ``= != < <= > >=`` and ``known``. A window
is ``>=`` intersected with ``<=``. A set is an ``any`` of ``=``. Bits are over
``candidates()`` and the three legs do not overlap.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from typing import Any, Literal, Protocol


@dataclass(frozen=True)
class FactValue:
    state: Literal["known", "unknown", "not_disclosed", "requires_contract"]
    value: Any = None
    sources: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvidenceValue:
    benchmark_id: str
    version: str | None
    subcategory: str | None
    value: Any
    unit: str | None
    measured_by: str
    effort: str | None
    harness: str | None
    date: date | None
    source_ids: tuple[str, ...]
    verified: bool
    directness: str | None = None


@dataclass(frozen=True)
class Bitset3:
    passing: int
    failing: int
    unknown: int


class SnapshotIndex(Protocol):
    snapshot_id: str

    def candidates(self) -> Sequence[str]: ...

    def lifecycle(self, cid: str) -> Literal["active", "deprecated", "retired"]: ...

    def fact(self, cid: str, facet_id: str) -> FactValue: ...

    def ids_where(self, facet_id: str, op: str, arg: Any) -> Bitset3: ...

    def evidence(
        self, cid: str, benchmark_id: str, *, measured_by: set[str] | None = None,
        effort: str | None = None, harness: str | None = None, after: date | None = None,
    ) -> Sequence[EvidenceValue]: ...

    def evidence_for_domain(self, cid: str, domain_id: str) -> Sequence[EvidenceValue]: ...


def _compare(op: str, left: Any, right: Any) -> bool | None:
    try:
        if op == "=":
            return left == right
        if op == "!=":
            return left != right
        if op == "<":
            return left < right
        if op == "<=":
            return left <= right
        if op == ">":
            return left > right
        if op == ">=":
            return left >= right
    except TypeError:
        return None
    raise ValueError(f"unsupported op {op!r}")


class MemoryIndex:
    """Facts and evidence for tests.

    ``evidence`` returns every row. The filter applies the qualifiers.
    """

    def __init__(
        self,
        candidates: Sequence[str],
        facts: Mapping[tuple[str, str], FactValue],
        *,
        lifecycle: Mapping[str, str] | None = None,
        evidence: Mapping[tuple[str, str], Sequence[EvidenceValue]] | None = None,
        domain_evidence: Mapping[tuple[str, str], Sequence[EvidenceValue]] | None = None,
        extras: Sequence[str] = (),
        snapshot_id: str = "snap_test",
    ) -> None:
        self.snapshot_id = snapshot_id
        self._candidates = tuple(candidates)
        self._facts = dict(facts)
        self._lifecycle = dict(lifecycle or {})
        self._evidence = {key: tuple(rows) for key, rows in (evidence or {}).items()}
        self._domains = {key: tuple(rows) for key, rows in (domain_evidence or {}).items()}
        self._known = set(self._candidates) | set(extras)
        self.calls: list[tuple[Any, ...]] = []

    def candidates(self) -> Sequence[str]:
        return self._candidates

    def lifecycle(self, cid: str) -> Literal["active", "deprecated", "retired"]:
        if cid not in self._known:
            raise KeyError(cid)
        life = self._lifecycle.get(cid, "active")
        if life not in ("active", "deprecated", "retired"):
            raise ValueError(life)
        return life  # type: ignore[return-value]

    def fact(self, cid: str, facet_id: str) -> FactValue:
        if cid not in self._known:
            raise KeyError(cid)
        return self._facts.get((cid, facet_id), FactValue("unknown"))

    def ids_where(self, facet_id: str, op: str, arg: Any) -> Bitset3:
        self.calls.append(("ids_where", facet_id, op, arg))
        passing = failing = unknown = 0
        for i, cid in enumerate(self._candidates):
            bit = 1 << i
            fact = self.fact(cid, facet_id)
            if op == "known":
                if fact.state == "known" and fact.value is not None:
                    passing |= bit
                else:
                    failing |= bit
                continue
            if fact.state != "known" or fact.value is None:
                unknown |= bit
                continue
            result = _compare(op, fact.value, arg)
            if result is None:
                unknown |= bit
            elif result:
                passing |= bit
            else:
                failing |= bit
        return Bitset3(passing, failing, unknown)

    def evidence(
        self, cid: str, benchmark_id: str, *, measured_by: set[str] | None = None,
        effort: str | None = None, harness: str | None = None, after: date | None = None,
    ) -> Sequence[EvidenceValue]:
        self.calls.append(("evidence", cid, benchmark_id, measured_by, effort, harness, after))
        if cid not in self._known:
            raise KeyError(cid)
        return self._evidence.get((cid, benchmark_id), ())

    def evidence_for_domain(self, cid: str, domain_id: str) -> Sequence[EvidenceValue]:
        if cid not in self._known:
            raise KeyError(cid)
        return self._domains.get((cid, domain_id), ())
