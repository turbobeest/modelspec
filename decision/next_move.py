"""Deterministic next steps for bounded answers that name no pick (MODEL-339)."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Literal

from pydantic import TypeAdapter

from decision.contract import (
    AllOf,
    AnyOf,
    Answer,
    Condition,
    Decision,
    InSet,
    InventoryProfile,
    Issue,
    MayQualify,
    NotOf,
    Reading,
    RelaxSingle,
    Spec,
    SpecError,
    Status,
    parse_spec,
    render_condition,
)
from decision.reading import HARDWARE_FIT
from decision.resolve import resolve
from decision.wording import join_names

CANDIDATE_CAP = 8
HARDWARE_CAP = 3
NEEDS_CAP = 3
NEEDS_BYTES = 600

# Approved by Jamie 2026-10-10. A wording change is a one-line edit.
ASK_USER = "Next step: which one of these requirements can change? ModelSpec will decide again with the rest kept as you set them."
ASK_USER_MULTIPLE = "Next step: which of these requirements can change? No single change admits a model, so more than one has to give."
DROP_MANY = "Drop {condition}: {n} models qualify."
DROP_ONE = "Drop {condition}: 1 model qualifies."
CHANGE = "Change {condition}."
TEST_UNMEASURED = "Next step: ModelSpec does not measure {needs}, so decide by testing {candidates} on your own work."
TEST_MISSING = "Next step: ModelSpec lacks {dimension} values for some candidates, so decide by testing {candidates} on your own work."
# Approved by Jamie 2026-10-10 (MODEL-339).
TEST_MISSING_ALL = "Next step: ModelSpec lacks {dimension} values for every model that meets your requirements, so decide by testing {candidates} on your own work."
TEST_NULL = "Next step: ModelSpec has no answer here, so decide by testing {candidates} on your own work."
TEST_CANDIDATES = "these {n} candidates"
TEST_FEWER_THAN_TWO = "the models that meet your requirements"
TASK_QUALITY = "{task} quality"
HARDWARE_NEED = "fit on {hardware} for your quantization, context length and runtime"
# Approved by Jamie 2026-10-10 (MODEL-339).
HARDWARE_MORE = "{skus} or {n} more devices"
# Approved by Jamie 2026-10-10 (MODEL-339).
HARDWARE_MORE_ONE = "{skus} or 1 more device"
NEEDS_MORE = "and {n} more"
TEST_STEPS = (
    "Collect 10 to 20 real examples of this task from your own work, each with the result you would accept.",
    "Write the pass or fail criteria before running any model.",
    "Run every candidate on the same examples with the same prompt and settings.",
    "Score each output without knowing which model produced it.",
    "Choose the candidate that passes most often. If candidates pass equally, choose on cost or on a provider you already use.",
)
HARDWARE_STEPS = (
    "Load each candidate on your hardware at the quantization, context length and runtime you plan to use.",
    "Drop any candidate that fails to load or leaves no memory headroom under your real context length.",
    "Run 10 to 20 real examples on the rest and record pass or fail and speed.",
    "Choose the candidate that passes most often at a speed you accept.",
)
TIE = "Next step: these {n} models tie on the evidence, so the choice is yours on something other than quality: a provider you already use, lower cost per task, or lower latency."
TIE_COST_ONLY = "Next step: these {n} models tie on the evidence, so the choice is yours on something other than quality: a provider you already use, or lower latency."
TIE_OPTIONS = (
    "A provider you already use: a convenience choice, not a quality choice.",
    "Lower cost per task: a cost choice, not a quality choice.",
    "Lower latency: a speed choice, not a quality choice.",
)


@dataclass(frozen=True)
class NextMoveInput:
    status: Status
    answer_kind: Literal["separated", "tied"] | None = None
    answer_members: tuple[str, ...] = ()
    may_qualify: tuple[tuple[str, tuple[str, ...]], ...] = ()
    task_type: str | None = None
    not_applied: tuple[str, ...] = ()
    fits_hardware: tuple[str, ...] = ()
    relax_single: tuple[tuple[str, int], ...] | None = None
    gates: tuple[str, ...] = ()
    feasible_models: tuple[str, ...] = ()
    objective_dimensions: tuple[str, ...] = ()
    cost_only: bool = False


def build_next_move(inp: NextMoveInput) -> dict | None:
    """Select the first applicable move. Candidate order conveys no quality order."""
    if inp.status == "answered" and inp.answer_kind == "separated":
        return None

    if inp.status == "no_feasible" and inp.relax_single is not None:
        options = [
            (DROP_ONE if admits == 1 else DROP_MANY).format(condition=condition, n=admits)
            for condition, admits in inp.relax_single
        ]
        return {
            "kind": "ask_user",
            "say": ASK_USER if options else ASK_USER_MULTIPLE,
            "options": options or [CHANGE.format(condition=condition) for condition in inp.gates],
            "steps": [],
            "candidates": [],
            "candidates_total": 0,
        }

    models = set(inp.answer_members)
    if inp.status == "partial" or inp.answer_kind is None:
        models.update(inp.feasible_models)
    if inp.status == "no_feasible":
        models.clear()
    models.update(model for model, _unknown in inp.may_qualify)
    total = len(models)
    candidates = sorted(models)[:CANDIDATE_CAP] if total >= 2 else []
    candidate_text = TEST_CANDIDATES.format(n=total) if total >= 2 else TEST_FEWER_THAN_TWO
    needs = []
    if inp.task_type is not None:
        needs.append(TASK_QUALITY.format(task=inp.task_type.replace("_", " ")))
    needs.extend(inp.not_applied)
    if inp.fits_hardware:
        # The adapter sorts distinct SKUs alphabetically before this cap.
        skus = inp.fits_hardware[:HARDWARE_CAP]
        more = len(inp.fits_hardware) - len(skus)
        hardware = (
            (HARDWARE_MORE_ONE if more == 1 else HARDWARE_MORE).format(skus=", ".join(skus), n=more)
            if more else
            join_names(skus, conjunction="or", serial_comma=False)
        )
        needs.append(HARDWARE_NEED.format(hardware=hardware))

    if inp.status == "no_feasible":
        say = _missing_values(inp.objective_dimensions, candidate_text, all_missing=True)
    elif needs:
        say = TEST_UNMEASURED.format(needs=_bounded_needs(needs), candidates=candidate_text)
    elif inp.status == "partial":
        dimensions = sorted({dimension for _model, unknown in inp.may_qualify for dimension in unknown})
        say = _missing_values(dimensions or inp.objective_dimensions, candidate_text)
    elif inp.answer_kind is None:
        say = TEST_NULL.format(candidates=candidate_text)
    else:
        return {
            "kind": "user_tiebreak",
            "say": (TIE_COST_ONLY if inp.cost_only else TIE).format(n=total),
            "options": [option for index, option in enumerate(TIE_OPTIONS) if not inp.cost_only or index != 1],
            "steps": [],
            "candidates": candidates,
            "candidates_total": total,
        }
    return {
        "kind": "decide_by_testing",
        "say": say,
        "options": [],
        "steps": list(HARDWARE_STEPS if inp.fits_hardware else TEST_STEPS),
        "candidates": candidates,
        "candidates_total": total,
    }


def _bounded_needs(needs: Iterable[str]) -> str:
    items = list(dict.fromkeys(needs))
    shown = items[:NEEDS_CAP]
    while True:
        text = " and ".join(shown)
        omitted = len(items) - len(shown)
        if omitted:
            text = (text + " " if text else "") + NEEDS_MORE.format(n=omitted)
        if len(text.encode("utf-8")) <= NEEDS_BYTES:
            return text
        if len(shown) == 1:
            raise SpecError([Issue(
                None, "fields", "the next_move needs exceed the 600-byte needs budget; "
                "use a narrower structured spec or POST /v1/decide without fields for the complete Decision",
                "fields",
            )])
        shown.pop()


def _missing_values(dimensions: Iterable[str], candidates: str, *, all_missing: bool = False) -> str:
    dimension = _bounded_needs(dimensions)
    if not dimension:
        return TEST_NULL.format(candidates=candidates)
    return (TEST_MISSING_ALL if all_missing else TEST_MISSING).format(dimension=dimension, candidates=candidates)


def applied_conditions(
    spec: Spec | None, profiles: Mapping[str, InventoryProfile] | None = None,
) -> tuple[Condition, ...]:
    """Profile rules, then the user's where list, in the engine's order."""
    if spec is None:
        return ()
    try:
        return tuple(resolve(spec, profiles=profiles).conditions)
    except SpecError:
        profile = spec.profile
        if isinstance(profile, str):
            profile = None if profiles is None else profiles.get(profile)
        rules = tuple(profile.rules) if isinstance(profile, InventoryProfile) else ()
        return rules + tuple(spec.where)


def _leaves(condition: Condition):
    if condition.soft is not None:
        return
    if isinstance(condition, AnyOf):
        for child in condition.any:
            yield from _leaves(child)
    elif isinstance(condition, AllOf):
        for child in condition.all:
            yield from _leaves(child)
    elif isinstance(condition, NotOf):
        yield from _leaves(condition.not_)
    else:
        yield condition


def _unknown_dimension_names(unknown: Iterable[str], spec: Spec | None) -> tuple[str, ...]:
    names = set(unknown)
    if "any" in names:
        names.remove("any")
        if spec is not None:
            for key in spec.optimize.weights or spec.optimize.pareto or ():
                if key.removeprefix("-").startswith("any/"):
                    names.add(key.removeprefix("-").removeprefix("any/"))
    return tuple(sorted(names))


def next_move_input_from_decision(
    decision: Decision,
    spec: Spec | None,
    *,
    not_applied: Iterable[str] = (),
    conditions: Iterable[Condition] | None = None,
    profiles: Mapping[str, InventoryProfile] | None = None,
) -> NextMoveInput:
    return _input_from_fields(
        spec, status=decision.status, answer=decision.answer, may_qualify=decision.may_qualify,
        reading=decision.reading, relax_single=decision.relax_single,
        feasible_models=(decision._feasible_models if decision._feasible_models is not None else
                         (row.model or row.offering.model for row in decision.results)),
        not_applied=not_applied, conditions=conditions, profiles=profiles,
    )


def _input_from_fields(
    spec: Spec | None, *, status: Status, answer: Answer | None,
    may_qualify: Iterable[MayQualify], reading: Reading | None, relax_single: RelaxSingle | None,
    feasible_models: Iterable[str], not_applied: Iterable[str] = (),
    conditions: Iterable[Condition] | None = None,
    profiles: Mapping[str, InventoryProfile] | None = None,
) -> NextMoveInput:
    conditions = tuple(conditions) if conditions is not None else applied_conditions(spec, profiles)
    gates = tuple(render_condition(condition) for condition in conditions if condition.soft is None)
    single = {gate.condition: gate.admits for gate in relax_single.gates} if relax_single else {}
    ordered_single = tuple((condition, single[condition]) for condition in gates if condition in single)
    # A hand-built Decision can carry a gate without a Spec. Keep its order.
    ordered_single += tuple((condition, admits) for condition, admits in single.items() if condition not in gates)
    unapplied = dict.fromkeys(not_applied)
    if reading is not None:
        unapplied.update(dict.fromkeys(reading.not_applied))
    task = spec.task_type if spec is not None else None
    for item in tuple(unapplied):
        if item.startswith("task_type = "):
            task = item.removeprefix("task_type = ")
            del unapplied[item]
    hardware = []
    for condition in conditions:
        for leaf in _leaves(condition):
            if getattr(leaf, "facet", getattr(leaf, "known", None)) != HARDWARE_FIT:
                continue
            values = (leaf.in_ or leaf.not_in) if isinstance(leaf, InSet) else [getattr(leaf, "value", "your hardware")]
            hardware.extend(str(value) for value in values)
    by_model: dict[str, set[str]] = {}
    for row in may_qualify:
        by_model.setdefault(row.model, set()).update(_unknown_dimension_names(row.unknown, spec))
    return NextMoveInput(
        status=status,
        answer_kind=None if answer is None else answer.kind,
        answer_members=() if answer is None else tuple(sorted(answer.members)),
        may_qualify=tuple((model, tuple(sorted(unknown))) for model, unknown in sorted(by_model.items())),
        task_type=task,
        not_applied=tuple(unapplied),
        fits_hardware=tuple(sorted(set(hardware))),
        relax_single=None if relax_single is None else ordered_single,
        gates=gates,
        feasible_models=tuple(sorted(set(feasible_models))),
        objective_dimensions=() if spec is None else _unknown_dimension_names(objective_names(spec), spec),
        cost_only=objective_is_cost_only(spec) if spec is not None else bool(
            reading and "Do not claim a quality rank from this objective." in reading.do_not_claim
        ),
    )


def next_move_input_from_bounded(spec_dict: dict, body_dict: dict) -> NextMoveInput:
    """Adapt retained decision fields; omitted rows cannot be reconstructed.

    Even an untrimmed serialized Decision lacks runtime-only feasible models.
    Equality with the full Decision adapter requires all feasible candidates
    to remain in results or may_qualify, without result-limit or objective
    omissions. This adapter also accepts bodies from before next_move was added.
    """
    spec = parse_spec({key: value for key, value in spec_dict.items() if key in Spec.model_fields}, facets=None)
    reading = body_dict.get("reading")
    single = body_dict.get("relax_single")
    return _input_from_fields(
        spec,
        status=TypeAdapter(Status).validate_python(body_dict["status"]),
        answer=TypeAdapter(Answer | None).validate_python(body_dict.get("answer")),
        may_qualify=(MayQualify.model_validate(row) for row in body_dict.get("may_qualify", ())),
        reading=None if reading is None else Reading.model_validate(reading),
        relax_single=None if single is None else RelaxSingle.model_validate(single),
        feasible_models=(row.get("model") or row["offering"]["model"] for row in body_dict.get("results", ())),
        not_applied=body_dict.get("explanation", {}).get("not_applied", ()),
    )


def objective_names(spec: Spec) -> list[str]:
    objective = spec.optimize
    return [name.removeprefix("-") for name in (
        [objective.max] if objective.max else [objective.min] if objective.min else
        [step.facet for step in objective.lexicographic] if objective.lexicographic else
        list(objective.weights or objective.pareto or ())
    )]


def objective_is_cost_only(spec: Spec) -> bool:
    names = objective_names(spec)
    monetary = _monetary_objectives()
    return bool(names) and all(name.removeprefix("-") in monetary for name in names)


def _monetary_objectives() -> frozenset[str]:
    """Addressable offering objectives whose registry unit is a currency."""
    from decision.registry import default

    registry = default()
    money = {
        unit.id for unit in registry.units()
        if _currency_unit(unit.id, unit.definition)
    }
    return frozenset(
        facet.id for facet in registry.facets()
        if facet.subject == "offering" and facet.addressable and facet.unit in money
        and facet.value_type.kind == "number"
    )


def _currency_unit(unit_id: str, definition: str) -> bool:
    code, separator, _rest = unit_id.partition("_")
    if not separator or len(code) != 3 or not code.isalpha():
        return False
    return any(word in definition.casefold() for word in ("dollar", "yuan", "euro", "pound", "yen", "currency"))
