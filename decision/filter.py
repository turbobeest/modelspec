"""Three-valued filter (MODEL-141, design §6.2).

A condition is pass, fail or unknown for each candidate. ``all`` is Kleene AND:
a fail wins over an unknown. ``any`` is Kleene OR: a pass wins over an unknown.
``not`` swaps pass and fail and leaves unknown unknown.

The unknown policy comes from the condition, otherwise from the facets that
are unknown for that candidate. Capability moves the candidate to
``may_qualify``. A governance unknown does not pass; the elimination is
surfaced as ``unverified: may qualify``. A governance facet the candidate
already passes does not change this. A per-condition ``unknown`` override wins.
``soft`` does not change who remains. No condition adds a score.

``ids_where`` is called with ``= != < <= > >=`` and ``known``. A window is
``>=`` intersected with ``<=``. A set is an ``any`` of ``=``. An evidence
condition calls ``evidence`` and then applies its qualifiers. Retired
candidates are excluded unless the resolved spec asks for lifecycle ``retired``.

The shared snapshot protocol lives in ``decision/snapshot.py`` (MODEL-138).
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from decision.contract import (
    AllOf,
    AnyOf,
    Compare,
    EvidenceQualifiers,
    FunnelStep,
    InSet,
    Issue,
    Known,
    ModelRef,
    NotOf,
    SpecError,
    Window,
    render_condition,
)
from decision.resolve import Resolved

Leg = Literal["pass", "fail", "unknown"]
UNVERIFIED_MAY_QUALIFY = "unverified: may qualify"

# Measurers that are not the model's own lab or provider.
_INDEPENDENT = frozenset({
    "benchmark_author", "independent", "independent_evaluator", "modelspec", "outcome_protocol",
})
_PROVIDER = frozenset({"provider_self_report"})

_RETIRED_CONDITION = "model.lifecycle not in {retired}"


class _Missing:
    """The reference model has no known value, so the comparison is unknown."""


_MISSING = _Missing()


@dataclass(frozen=True)
class Bits:
    """Three disjoint bitsets over ``candidates()``. A hole is unknown."""

    passing: int = 0
    failing: int = 0
    unknown: int = 0


@dataclass(frozen=True)
class FunnelCount:
    _condition: Any
    before: int
    after: int
    may_qualify: int

    @property
    def condition(self) -> str:
        if isinstance(self._condition, str):
            return self._condition
        return render_condition(self._condition)

    def as_contract(self) -> FunnelStep:
        return FunnelStep(
            condition=self.condition, before=self.before, after=self.after,
            may_qualify=self.may_qualify,
        )


@dataclass(frozen=True)
class Elimination:
    """Why one candidate left the lineup. ``value`` is theirs, ``threshold`` is the bar."""

    candidate: str
    _condition: Any
    value: Any
    threshold: Any
    facet: str | None
    unverified: bool = False

    @property
    def condition(self) -> str:
        if isinstance(self._condition, str):
            return self._condition
        return render_condition(self._condition)

    @property
    def surface(self) -> str | None:
        if self.unverified:
            return UNVERIFIED_MAY_QUALIFY
        return None


@dataclass(frozen=True)
class MayQualify:
    """A candidate removed from the ranking because a capability value is unknown."""

    candidate: str
    unknown: tuple[str, ...]


@dataclass(frozen=True)
class SoftPenalty:
    """A soft condition, for the optimiser. It did not remove anyone."""

    condition: str
    penalty: float
    failing: tuple[str, ...]
    unknown: tuple[str, ...]


@dataclass(frozen=True)
class FilterResult:
    """Who remains after the hard conditions. There is no score here."""

    snapshot_id: str
    feasible: tuple[str, ...]
    may_qualify: tuple[MayQualify, ...]
    funnel: tuple[FunnelCount, ...]
    eliminated: tuple[Elimination, ...]
    penalties: tuple[SoftPenalty, ...]
    deprecated: tuple[str, ...]


def tri_not(leg: Leg) -> Leg:
    if leg == "pass":
        return "fail"
    if leg == "fail":
        return "pass"
    return "unknown"


def tri_and(left: Leg, right: Leg) -> Leg:
    if left == "fail" or right == "fail":
        return "fail"
    if left == "unknown" or right == "unknown":
        return "unknown"
    return "pass"


def tri_or(left: Leg, right: Leg) -> Leg:
    if left == "pass" or right == "pass":
        return "pass"
    if left == "unknown" or right == "unknown":
        return "unknown"
    return "fail"


def bit_not(bits: Bits, universe: int) -> Bits:
    return Bits(bits.failing & universe, bits.passing & universe, bits.unknown & universe)


def bit_and(left: Bits, right: Bits, universe: int) -> Bits:
    passing = left.passing & right.passing & universe
    failing = (left.failing | right.failing) & universe
    return Bits(passing, failing, universe & ~passing & ~failing)


def bit_or(left: Bits, right: Bits, universe: int) -> Bits:
    passing = (left.passing | right.passing) & universe
    failing = left.failing & right.failing & universe
    return Bits(passing, failing, universe & ~passing & ~failing)


def _as_bits(raw: Any, universe: int) -> Bits:
    passing = int(raw.passing) & universe
    failing = int(raw.failing) & universe
    unknown = int(raw.unknown) & universe
    if (passing & failing) or (passing & unknown) or (failing & unknown):
        raise ValueError("ids_where returned overlapping bitsets")
    unknown |= universe & ~passing & ~failing
    return Bits(passing, failing, unknown)


def _measurers(qualifier: str | None) -> frozenset[str] | None:
    if qualifier is None or qualifier == "any":
        return None
    if qualifier == "independent":
        return _INDEPENDENT
    if qualifier == "provider_self_report":
        return _PROVIDER
    raise ValueError(f"unknown measured_by qualifier {qualifier!r}")


def _op(op: str, left: Any, right: Any) -> bool:
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
    raise ValueError(f"unsupported op {op!r}")


def _judge(values: Sequence[Any], pred: Callable[[Any], bool]) -> Leg:
    if not values:
        return "unknown"
    saw_fail = False
    saw_unknown = False
    for value in values:
        try:
            ok = pred(value)
        except TypeError:
            saw_unknown = True
            continue
        if ok:
            return "pass"
        saw_fail = True
    if saw_unknown:
        return "unknown"
    return "fail" if saw_fail else "unknown"


def _shown(values: Sequence[Any], op: str | None) -> Any:
    ordered = [value for value in values if not isinstance(value, bool)]
    if not ordered:
        return None
    if op in ("<", "<="):
        return min(ordered)
    if op in (">", ">="):
        return max(ordered)
    if len(ordered) == 1:
        return ordered[0]
    return tuple(ordered)


def _collapse(bits: Bits, policy: str, universe: int) -> Bits:
    if policy == "pass":
        return Bits((bits.passing | bits.unknown) & universe, bits.failing & universe, 0)
    if policy == "fail":
        return Bits(bits.passing & universe, (bits.failing | bits.unknown) & universe, 0)
    return bits


def _leg_of(bits: Bits, bit: int) -> Leg:
    if bits.passing & bit:
        return "pass"
    if bits.failing & bit:
        return "fail"
    return "unknown"


def _children(cond: Any) -> tuple[Any, ...]:
    if isinstance(cond, AnyOf):
        return tuple(cond.any)
    if isinstance(cond, AllOf):
        return tuple(cond.all)
    if isinstance(cond, NotOf):
        return (cond.not_,)
    return ()


def _facet_of(cond: Any) -> str | None:
    if isinstance(cond, Known):
        return cond.known
    facet = getattr(cond, "facet", None)
    return facet if isinstance(facet, str) else None


def _is_leaf(cond: Any) -> bool:
    return isinstance(cond, Compare | Window | InSet | Known)


def _keep_row(row: Any, qualifiers: EvidenceQualifiers, measured: frozenset[str] | None) -> bool:
    if not getattr(row, "verified", False):
        return False
    if measured is not None and row.measured_by not in measured:
        return False
    if qualifiers.effort is not None and row.effort != qualifiers.effort:
        return False
    if qualifiers.harness is not None and row.harness != qualifiers.harness:
        return False
    after = qualifiers.measured_after
    if after is not None and (row.date is None or not row.date > after):
        return False
    if qualifiers.direct and getattr(row, "directness", None) != "direct":
        return False
    return True


class _Run:
    def __init__(self, resolved: Resolved, index: Any) -> None:
        self.resolved = resolved
        self.index = index
        self.facets = resolved.facets
        self.facet_cache: dict[str, Any] = {}
        self.ids = list(index.candidates())
        if len(set(self.ids)) != len(self.ids):
            raise ValueError("snapshot candidates are not unique")
        self.n = len(self.ids)
        self.universe = (1 << self.n) - 1
        self.pos = {cid: i for i, cid in enumerate(self.ids)}
        self.cache: dict[int, Bits] = {}
        self.evidence_conditions: dict[int, bool] = {}
        self.resolved_threshold: dict[int, Any] = {}
        self.penalties: list[SoftPenalty] = []
        self.path = ""
        self.lineup = 0

    def _ids_of(self, bits: int) -> tuple[str, ...]:
        ids = []
        while bits:
            bit = bits & -bits
            ids.append(self.ids[bit.bit_length() - 1])
            bits ^= bit
        return tuple(ids)

    def _life(self, cid: str) -> str:
        life = self.index.lifecycle(cid)
        if life not in ("active", "deprecated", "retired"):
            raise ValueError(f"lifecycle of {cid} is {life!r}, not active, deprecated or retired")
        return life

    def _facet(self, facet_id: str) -> Any:
        if facet_id in self.facet_cache:
            return self.facet_cache[facet_id]
        try:
            facet = self.facets(facet_id)
            self.facet_cache[facet_id] = facet
            return facet
        except KeyError:
            raise SpecError([Issue(
                None, facet_id, f"unknown facet {facet_id!r}: not in the facet registry", self.path,
            )]) from None

    def _is_evidence(self, cond: Any) -> bool:
        key = id(cond)
        if key not in self.evidence_conditions:
            facet_id = _facet_of(cond)
            self.evidence_conditions[key] = (
                getattr(cond, "qualifiers", None) is not None
                or (facet_id is not None and not isinstance(cond, Known) and (
                    self._facet(facet_id).subject == "evidence" or facet_id.startswith("evidence.")
                ))
            )
        return self.evidence_conditions[key]

    def _unknown_disposition(self, cond: Any, unk_bits: int) -> tuple[int, int, int]:
        """Split unknown bits into (treat as pass, may_qualify, unverified fail)."""
        if not unk_bits:
            return 0, 0, 0
        explicit = getattr(cond, "unknown", None)
        if explicit == "pass":
            return unk_bits, 0, 0
        if explicit == "fail" or isinstance(cond, Known):
            return 0, 0, unk_bits
        if explicit == "list":
            return 0, unk_bits, 0
        listed = failed = 0
        for cid in self._ids_of(unk_bits):
            bit = 1 << self.pos[cid]
            facets = self._unknown_facets(cond, bit)
            risks = [self._facet(facet_id).risk for facet_id in facets]
            if not risks or any(risk == "governance" for risk in risks):
                failed |= bit
            else:
                listed |= bit
        return 0, listed, failed

    def _admitted(self, cid: str, cond: Any) -> list[Any]:
        qualifiers = cond.qualifiers or EvidenceQualifiers()
        measured = _measurers(qualifiers.measured_by)
        rows = self.index.evidence(
            cid, cond.facet,
            measured_by=None if measured is None else set(measured),
            effort=qualifiers.effort,
            harness=qualifiers.harness,
            after=qualifiers.measured_after,
        )
        return [row.value for row in rows if _keep_row(row, qualifiers, measured)]

    def _reference(self, cond: Compare) -> Any:
        assert isinstance(cond.value, ModelRef)
        ref = cond.value.model
        key = id(cond)
        if key in self.resolved_threshold:
            return self.resolved_threshold[key]
        try:
            if self._is_evidence(cond):
                values = self._admitted(ref, cond)
                got: Any = _MISSING if not values else _shown(values, cond.op)
            else:
                fact = self.index.fact(ref, cond.facet)
                got = fact.value if fact.state == "known" and fact.value is not None else _MISSING
        except KeyError:
            raise SpecError([Issue(
                render_condition(cond), ref, f"model {ref} is not in the snapshot", self.path,
            )]) from None
        self.resolved_threshold[key] = got
        return got

    def _evidence_bits(self, cond: Any, op: str, arg: Any) -> Bits:
        qualifiers = cond.qualifiers or EvidenceQualifiers()
        measured = _measurers(qualifiers.measured_by)
        indexed = getattr(self.index, "evidence_where", None)
        if indexed is not None:
            return _as_bits(indexed(
                cond.facet,
                op,
                arg,
                measured_by=None if measured is None else set(measured),
                effort=qualifiers.effort,
                harness=qualifiers.harness,
                after=qualifiers.measured_after,
                direct=qualifiers.direct,
            ), self.universe)
        passing = failing = 0
        for i, cid in enumerate(self.ids):
            try:
                values = self._admitted(cid, cond)
            except KeyError:
                raise SpecError([Issue(
                    render_condition(cond), cid, f"{cid} is not in the snapshot", self.path,
                )]) from None
            if op == "between":
                low, high = arg
                leg = _judge(values, lambda value: _op(">=", value, low)
                             and _op("<=", value, high))
            else:
                leg = _judge(values, lambda value: _op(op, value, arg))
            bit = 1 << i
            if leg == "pass":
                passing |= bit
            elif leg == "fail":
                failing |= bit
        return Bits(passing, failing, self.universe & ~passing & ~failing)

    def _compare(self, cond: Compare) -> Bits:
        if isinstance(cond.value, ModelRef):
            threshold = self._reference(cond)
            if threshold is _MISSING:
                return Bits(0, 0, self.universe)
        else:
            threshold = cond.value
        if self._is_evidence(cond):
            return self._evidence_bits(cond, cond.op, threshold)
        return _as_bits(self.index.ids_where(cond.facet, cond.op, threshold), self.universe)

    def _window(self, cond: Window) -> Bits:
        low, high = cond.between
        if self._is_evidence(cond):
            return self._evidence_bits(cond, "between", (low, high))
        lo = _as_bits(self.index.ids_where(cond.facet, ">=", low), self.universe)
        hi = _as_bits(self.index.ids_where(cond.facet, "<=", high), self.universe)
        return bit_and(lo, hi, self.universe)

    def _set(self, cond: InSet) -> Bits:
        values = cond.in_ if cond.in_ is not None else cond.not_in
        if not values:
            raise ValueError("a set condition has no values")
        if self._is_evidence(cond):
            acc: Bits | None = None
            for value in values:
                bit = self._evidence_bits(cond, "=", value)
                acc = bit if acc is None else bit_or(acc, bit, self.universe)
            assert acc is not None
            bits = acc
        else:
            acc: Bits | None = None
            for value in values:
                bit = _as_bits(self.index.ids_where(cond.facet, "=", value), self.universe)
                acc = bit if acc is None else bit_or(acc, bit, self.universe)
            assert acc is not None
            bits = acc
        if cond.not_in is not None:
            bits = bit_not(bits, self.universe)
        return bits

    def _known(self, cond: Known) -> Bits:
        bits = _as_bits(self.index.ids_where(cond.known, "known", None), self.universe)
        return Bits(bits.passing, self.universe & ~bits.passing, 0)

    def _presented(self, cond: Any, raw: Bits) -> Bits:
        explicit = getattr(cond, "unknown", None)
        if explicit is None:
            return raw
        return _collapse(raw, explicit, self.universe)

    def _combine(self, children: Sequence[Any], op: Callable[[Bits, Bits, int], Bits]) -> Bits:
        parts: list[Bits] = []
        for child in children:
            if child.soft is not None:
                self._eval(child)
                continue
            parts.append(self._presented(child, self._eval(child)))
        if not parts:
            return Bits(self.universe, 0, 0)
        acc = parts[0]
        for part in parts[1:]:
            acc = op(acc, part, self.universe)
        return acc

    def _eval(self, cond: Any) -> Bits:
        key = id(cond)
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        if isinstance(cond, Compare):
            bits = self._compare(cond)
        elif isinstance(cond, Window):
            bits = self._window(cond)
        elif isinstance(cond, InSet):
            bits = self._set(cond)
        elif isinstance(cond, Known):
            bits = self._known(cond)
        elif isinstance(cond, AnyOf):
            bits = self._combine(cond.any, bit_or)
        elif isinstance(cond, AllOf):
            bits = self._combine(cond.all, bit_and)
        elif isinstance(cond, NotOf):
            child = cond.not_
            if child.soft is not None:
                self._eval(child)
                bits = Bits(self.universe, 0, 0)
            else:
                bits = bit_not(self._presented(child, self._eval(child)), self.universe)
        else:
            raise TypeError(f"not a condition: {type(cond).__name__}")
        self.cache[key] = bits
        if getattr(cond, "soft", None) is not None:
            self._record_penalty(cond, bits)
        return bits

    def _record_penalty(self, cond: Any, raw: Bits) -> None:
        lineup = self.lineup
        self.penalties.append(SoftPenalty(
            condition=render_condition(cond),
            penalty=cond.soft.penalty,
            failing=self._ids_of(raw.failing & lineup),
            unknown=self._ids_of(raw.unknown & lineup),
        ))

    def _decisive(self, cond: Any, bit: int, leg: Leg) -> Any:
        if isinstance(cond, NotOf):
            child = cond.not_
            if child.soft is not None:
                return cond
            flipped: Leg = "unknown" if leg == "unknown" else ("fail" if leg == "pass" else "pass")
            return self._decisive(child, bit, flipped)
        children = _children(cond)
        if not children:
            return cond
        for child in children:
            if child.soft is not None:
                continue
            shown = self._presented(child, self._eval(child))
            if _leg_of(shown, bit) == leg:
                return self._decisive(child, bit, leg)
        for child in children:
            if child.soft is not None:
                continue
            if self._eval(child).unknown & bit:
                return self._decisive(child, bit, "unknown")
        return cond

    def _unknown_facets(self, cond: Any, bit: int) -> list[str]:
        if isinstance(cond, NotOf):
            return self._unknown_facets(cond.not_, bit)
        children = _children(cond)
        if children:
            found: list[str] = []
            for child in children:
                if child.soft is not None:
                    continue
                if self._eval(child).unknown & bit:
                    for facet_id in self._unknown_facets(child, bit):
                        if facet_id not in found:
                            found.append(facet_id)
            return found
        facet_id = _facet_of(cond)
        return [facet_id] if facet_id else []

    def _value(self, cond: Any, cid: str) -> Any:
        if isinstance(cond, Known):
            try:
                return self.index.fact(cid, cond.known).state
            except KeyError:
                return None
        facet_id = _facet_of(cond)
        if facet_id is None:
            return None
        if self._is_evidence(cond):
            values = self._admitted(cid, cond)
            op = cond.op if isinstance(cond, Compare) else None
            return _shown(values, op) if values else None
        try:
            fact = self.index.fact(cid, facet_id)
        except KeyError:
            return None
        if fact.state != "known" or fact.value is None:
            return None
        return fact.value

    def _threshold(self, cond: Any) -> Any:
        if isinstance(cond, Compare):
            if isinstance(cond.value, ModelRef):
                got = self.resolved_threshold.get(id(cond), _MISSING)
                if got is _MISSING:
                    got = self._reference(cond)
                return None if got is _MISSING else got
            return cond.value
        if isinstance(cond, Window):
            return cond.between
        if isinstance(cond, InSet):
            return tuple(cond.in_ if cond.in_ is not None else cond.not_in or ())
        if isinstance(cond, Known):
            return "known"
        return None

    def _leaf_was_unknown(self, cond: Any, bit: int) -> bool:
        leaf = self._decisive(cond, bit, "fail")
        if not _is_leaf(leaf):
            leaf = self._decisive(cond, bit, "unknown")
        if not _is_leaf(leaf):
            return False
        return bool(self._eval(leaf).unknown & bit)

    def _cover(self, feasible: int, maybe: int, eliminated: int) -> None:
        if (feasible & maybe) or (feasible & eliminated) or (maybe & eliminated):
            raise RuntimeError("filter partition overlaps")
        if (feasible | maybe | eliminated) != self.universe:
            raise RuntimeError("filter partition does not cover the lineup")

    def run(self) -> FilterResult:
        wanted = self.resolved.spec.snapshot
        if wanted != "latest" and wanted != self.index.snapshot_id:
            raise SpecError([Issue(
                None, "snapshot",
                f"spec asks for {wanted} but the snapshot is {self.index.snapshot_id}",
                "snapshot",
            )])
        retired = 0
        for i, cid in enumerate(self.ids):
            if self._life(cid) == "retired":
                retired |= 1 << i
        eliminations: list[Elimination] = []
        if self.resolved.include_retired:
            self.lineup = self.universe
        else:
            self.lineup = self.universe & ~retired
            for cid in self._ids_of(retired):
                eliminations.append(Elimination(
                    candidate=cid, _condition=_RETIRED_CONDITION, value="retired",
                    threshold=("active", "deprecated"), facet="model.lifecycle",
                ))
        feasible = self.lineup
        maybe = 0
        eliminated = self.universe & ~self.lineup
        unknown_facets: dict[str, list[str]] = {}
        funnel: list[FunnelCount] = []
        rules = 0 if self.resolved.profile is None else len(self.resolved.profile.rules)
        self._cover(feasible, maybe, eliminated)

        for index, cond in enumerate(self.resolved.conditions):
            self.path = (f"profile.rules[{index}]" if index < rules
                         else f"where[{index - rules}]")
            before = feasible.bit_count()
            if cond.soft is not None:
                self._eval(cond)
                funnel.append(FunnelCount(cond, before, before, 0))
                continue
            raw = self._eval(cond)
            fe_pass, fe_fail, fe_unk = _split(raw, feasible)
            _mb_pass, mb_fail, mb_unk = _split(raw, maybe)
            fe_as_pass, fe_as_list, fe_as_fail = self._unknown_disposition(cond, fe_unk)
            _mb_as_pass, mb_as_list, mb_as_fail = self._unknown_disposition(cond, mb_unk)
            feasible = fe_pass | fe_as_pass
            new_maybe = fe_as_list
            drop = mb_fail | mb_as_fail
            maybe = (maybe & ~drop) | new_maybe
            new_elim = fe_fail | fe_as_fail | drop
            unverified_bits = fe_as_fail | mb_as_fail
            for cid in self._ids_of(new_maybe | mb_as_list):
                found = unknown_facets.setdefault(cid, [])
                for facet_id in self._unknown_facets(cond, 1 << self.pos[cid]):
                    if facet_id not in found:
                        found.append(facet_id)
            for cid in self._ids_of(drop):
                unknown_facets.pop(cid, None)
            for cid in self._ids_of(new_elim):
                bit = 1 << self.pos[cid]
                unverified = bool(unverified_bits & bit) or self._leaf_was_unknown(cond, bit)
                leg: Leg = "unknown" if unverified else "fail"
                leaf = self._decisive(cond, bit, leg)
                eliminations.append(Elimination(
                    candidate=cid, _condition=cond,
                    value=None if unverified else self._value(leaf, cid),
                    threshold=self._threshold(leaf),
                    facet=_facet_of(leaf),
                    unverified=unverified,
                ))
            eliminated |= new_elim
            funnel.append(FunnelCount(
                cond, before, feasible.bit_count(), new_maybe.bit_count(),
            ))
            self._cover(feasible, maybe, eliminated)

        may_qualify = tuple(
            MayQualify(cid, tuple(unknown_facets.get(cid, ())))
            for cid in self._ids_of(maybe)
        )
        deprecated = tuple(cid for cid in self.ids if self._life(cid) == "deprecated")
        return FilterResult(
            snapshot_id=self.index.snapshot_id,
            feasible=self._ids_of(feasible),
            may_qualify=may_qualify,
            funnel=tuple(funnel),
            eliminated=tuple(eliminations),
            penalties=tuple(self.penalties),
            deprecated=deprecated,
        )


def _split(raw: Bits, mask: int) -> tuple[int, int, int]:
    passing = raw.passing & mask
    failing = raw.failing & mask
    unknown = mask & ~passing & ~failing
    return passing, failing, unknown


def apply(resolved: Resolved, index: Any) -> FilterResult:
    """Filter ``index`` by the resolved conditions. The same inputs give the same result."""
    return _Run(resolved, index).run()
