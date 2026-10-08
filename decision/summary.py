"""Plain-language summary of one Decision (MODEL-339).

Deterministic templates only: the same Decision and Spec always produce the
same bytes. No clock, no randomness, and no model call.

``summary_for_user`` is one paragraph for the end user. ``must_mention`` is the
short list of facts a report of that answer has to carry. Both are computed
from the full Decision, before any agent-budget trim.
"""

from __future__ import annotations

from collections.abc import Iterable

from decision.contract import (
    AllOf,
    AnyOf,
    Contribution,
    Decision,
    InSet,
    Known,
    NotOf,
    Preference,
    Result,
    Spec,
    _render_value,
    render_condition,
)
from decision.reading import HARDWARE_FIT
from decision.refinements import split_dimension

SUMMARY_BYTES = 1_200
TIE_NAME_CAP = 8
MUST_MENTION_MAX = 10
MUST_MENTION_ITEM_BYTES = 200
OPENNESS_FACET = "model.weights_openness"
OPENNESS_EITHER = frozenset({"open_weights", "closed_weights"})

_NO_FEASIBLE = "ModelSpec found no model that meets every requirement, so it names no pick."
_PARTIAL = "ModelSpec's answer is incomplete, so it names no pick."
_NULL_ANSWER = "ModelSpec has no answer for this request, so it names no pick."
_TIE_TAIL = "the evidence does not separate them."
_ESTIMATES = "Some values are estimates, not measurements."
_HARDWARE = (
    "fits_hardware is an estimate, not a measured fit for a quantization or context workload."
)
_OUTSIDE = "The request is outside coverage."
_CLASS_FACET = "model.class"
_TEXT_GENERATOR = "text-generator"
_NO_CLASS = "No model class was required, so results span every class"
_COST_ONLY = "This answer is ordered by cost only; it is not a quality ranking."
_TIE_COST = "Tie-breakers are conditional; cost order is not quality order."
_QUALITY_CLAIM = "Do not claim a quality rank from this objective."
_LATENT_UNIT = "latent capability"
_NOT_CHECKED = " was not applied; ModelSpec did not check it."
_MISSING_OBJECTIVE = (
    "No model that meets the requirements has complete values for the objective "
    "({objective}), so ModelSpec cannot order them."
)
_BOARD_ONE = (
    " has no leaderboard data for {dimensions}; its position is estimated, not measured."
)
_BOARD_MANY = (
    " have no leaderboard data for {dimensions}; their positions are estimated, not measured."
)
_OPTION_TO = (
    "Relaxing {condition} to {relaxed} would admit a model; "
    "that is an option, not an answer."
)
_OPTION = "Relaxing {condition} would admit a model; that is an option, not an answer."


def summarize(
    decision: Decision,
    spec: Spec | None = None,
    *,
    not_applied: Iterable[str] = (),
) -> tuple[str, list[str]]:
    """Return ``(summary_for_user, must_mention)``."""
    unapplied = _unapplied(decision, not_applied)
    mentions = _mentions(decision, spec, unapplied)
    summary = _summary(decision, spec, unapplied, mentions)
    return summary, [text for _kind, text in mentions]


def _count(value: int) -> str:
    return f"{value:,}"


def _summary(
    decision: Decision,
    spec: Spec | None,
    unapplied: list[str],
    mentions: list[tuple[str, str]],
) -> str:
    limits = {
        "tie": TIE_NAME_CAP,
        "hard": 24,
        "prefer": 12,
        "relax": 12,
        "missing": 12,
        "caveat": 0,
    }
    floors = {
        "tie": 1,
        "hard": 1,
        "prefer": 1,
        "relax": 1,
        "missing": 1,
        "caveat": 0,
    }
    visible = _paragraph_mentions(decision, mentions)
    limits["caveat"] = len(visible)
    floors["caveat"] = len({kind for kind, _text in visible}) or 0
    text = _compose(decision, spec, unapplied, visible, limits)
    order = ("hard", "prefer", "relax", "missing", "tie", "caveat")
    while len(text.encode("utf-8")) > SUMMARY_BYTES:
        key = next((name for name in order if limits[name] > floors[name]), None)
        if key is None:
            break
        limits[key] -= 1
        text = _compose(decision, spec, unapplied, visible, limits)
    if len(text.encode("utf-8")) > SUMMARY_BYTES:
        text = _clip_paragraph(text)
    return text


def _compose(
    decision: Decision,
    spec: Spec | None,
    unapplied: list[str],
    mentions: list[tuple[str, str]],
    limits: dict[str, int],
) -> str:
    parts = [_answer_sentence(decision, limits["tie"])]
    parts.extend(_why(decision, spec, unapplied, limits))
    parts.extend(_constraints(spec, unapplied, limits))
    parts.extend(_caveats(mentions, limits["caveat"]))
    return _dedupe(parts)


def _paragraph_mentions(
    decision: Decision, mentions: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    """Caveats whose fact is not already in the answer, why, or constraints."""
    skip = {"not_applied"}
    if decision.status == "partial":
        skip.add("may_qualify")
    return [(kind, text) for kind, text in mentions if kind not in skip]


def _dedupe(parts: list[str]) -> str:
    seen: set[str] = set()
    kept: list[str] = []
    for part in parts:
        if not part or part in seen:
            continue
        seen.add(part)
        kept.append(part)
    return " ".join(kept)


def _answer_sentence(decision: Decision, tie_limit: int) -> str:
    if decision.status == "no_feasible":
        return _NO_FEASIBLE
    if decision.status == "partial":
        return _PARTIAL
    answer = decision.answer
    if answer is None:
        return _NULL_ANSWER
    if answer.kind == "tied":
        names = _name_list(list(answer.deterministic_order), tie_limit, more=" in answer.members")
        return f"ModelSpec's answer is a tie among {names}; {_TIE_TAIL}"
    member = answer.deterministic_order[0]
    return f"ModelSpec's answer is {member}."


def _why(
    decision: Decision, spec: Spec | None, unapplied: list[str], limits: dict[str, int],
) -> list[str]:
    if decision.status == "no_feasible":
        if spec is not None and _objective_values_missing(decision, spec):
            return [_MISSING_OBJECTIVE.format(objective=_objective_phrase(spec))]
        gates, _dont = _gates(spec, set(unapplied))
        if gates:
            listed = _bounded(gates, limits["hard"])
            exclude = f"These requirements together exclude every model: {listed}."
        else:
            exclude = "These requirements together exclude every model."
        sentences = [exclude]
        sentences.extend(_relaxation_options(decision, spec, limits["relax"]))
        hint = decision.relax_task_tokens
        if hint is not None:
            sentences.append(f"Task-size relaxation, not an answer: {hint.condition}.")
        return sentences
    if decision.status != "partial":
        return []
    unknowns: list[str] = []
    for row in decision.may_qualify:
        for facet in row.unknown:
            if facet not in unknowns:
                unknowns.append(facet)
    if unknowns:
        missing = f"What is missing: {_bounded(unknowns, limits['missing'])}."
    else:
        missing = "What is missing: complete objective values for some candidates."
    sentences = [missing]
    count = len(decision.may_qualify)
    if count:
        sentences.append(_qualify_sentence(count))
    return sentences


def _qualify_sentence(count: int) -> str:
    if count == 1:
        return (
            "1 more model may qualify, but ModelSpec lacks its values "
            "for these requirements."
        )
    return (
        f"{_count(count)} more models may qualify, but ModelSpec lacks their values "
        "for these requirements."
    )


def _relaxation_options(decision: Decision, spec: Spec | None, limit: int) -> list[str]:
    """One sentence per gate option. A diagnostic relax entry is not an option."""
    requirements = set(_gates(spec, set())[0])
    covered = {item.condition for item in decision.relax_to}
    options = [
        _OPTION_TO.format(condition=item.condition, relaxed=item.relaxed)
        for item in decision.relax_to
    ]
    options.extend(
        _OPTION.format(condition=condition)
        for condition in decision.relax
        if condition not in covered and condition in requirements
    )
    if not options:
        return []
    shown_count = min(len(options), max(limit, 1))
    shown = options[:shown_count]
    rest = len(options) - shown_count
    if rest:
        shown.append(f"and {_count(rest)} more.")
    return shown


def _constraints(spec: Spec | None, unapplied: list[str], limits: dict[str, int]) -> list[str]:
    gates, dont_care = _gates(spec, set(unapplied))
    prefers = _prefers(spec, set(unapplied))
    sentences: list[str] = []
    if gates:
        sentences.append(f"Requirements applied: {_bounded(gates, limits['hard'])}.")
    sentences.extend(dont_care)
    if prefers:
        sentences.append(
            "Preferences that rank without excluding: "
            f"{_bounded(prefers, limits['prefer'])}."
        )
    if unapplied:
        sentences.append(
            "Requirements not applied (ModelSpec did not check them): "
            f"{_bounded(unapplied, limits['hard'])}."
        )
    return sentences


def _gates(spec: Spec | None, unapplied: set[str]) -> tuple[list[str], list[str]]:
    if spec is None:
        return [], []
    gates: list[str] = []
    dont_care: list[str] = []
    phrase = f"{OPENNESS_FACET} is not required (either acceptable)."
    for condition in spec.where:
        if _plain_openness_either(condition):
            if phrase not in dont_care:
                dont_care.append(phrase)
            continue
        gates.append(render_condition(condition))
    for facet, level in (spec.capabilities or {}).items():
        if level == "required" and facet not in unapplied:
            gates.append(f"{facet} is required")
    return gates, dont_care


def _prefers(spec: Spec | None, unapplied: set[str]) -> list[str]:
    if spec is None:
        return []
    lines: list[str] = []
    for key, term in (spec.optimize.weights or {}).items():
        if isinstance(term, Preference):
            lines.append(f"{key} prefers {_render_value(term.prefer)}")
    for facet, level in (spec.capabilities or {}).items():
        if level == "preferred" and facet not in unapplied:
            lines.append(f"{facet} is preferred")
    return lines


def _leaves(condition: object):
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


def _plain_openness_either(condition: object) -> bool:
    """A top-level positive either-set, with nothing around it that changes the meaning."""
    if not isinstance(condition, InSet):
        return False
    return (
        condition.facet == OPENNESS_FACET
        and condition.in_ is not None
        and set(condition.in_) == OPENNESS_EITHER
        and condition.soft is None
        and condition.unknown is None
    )


def _objective_values_missing(decision: Decision, spec: Spec | None) -> bool:
    """True when ``relax`` holds an engine diagnostic, not a requirement to drop.

    A gate exclusion stores rendered conditions (``decision/relax.py``). When
    every candidate that passed the gates lacks an objective value, the engine
    stores the diagnostic instead and lists those candidates on ``may_qualify``.
    """
    if spec is None or not decision.relax or not decision.may_qualify:
        return False
    rendered = {render_condition(condition) for condition in spec.where}
    if any(item in rendered for item in decision.relax):
        return False
    objectives = set(_objective_bases(spec))
    if not objectives:
        return False
    unknowns = {name for row in decision.may_qualify for name in row.unknown}
    return bool(unknowns) and unknowns <= objectives


def _objective_phrase(spec: Spec) -> str:
    bases = _objective_bases(spec)
    if len(bases) == 1:
        return bases[0]
    return ", ".join(bases)


def _unapplied(decision: Decision, extra: Iterable[str]) -> list[str]:
    found: list[str] = []
    for item in extra:
        if item not in found:
            found.append(item)
    reading = decision.reading
    if reading is not None:
        for item in reading.not_applied:
            if item not in found:
                found.append(item)
    return found


def _mentions(
    decision: Decision, spec: Spec | None, unapplied: list[str],
) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    if _presents_tie(decision) and decision.answer is not None:
        count = len(decision.answer.members)
        items.append(("tie", f"No single winner: {_count(count)} models are tied."))
    scope = _class_sentence(decision, spec)
    if scope:
        items.append(("class", scope))
    if _cost_only(decision, spec):
        items.append(("cost", _COST_ONLY))
    if _cost_tie_break(decision):
        items.append(("tie_cost", _TIE_COST))
    for domain, benchmarks in _proxy(decision).items():
        items.append(("proxy", _proxy_sentence(domain, benchmarks)))
    for models, dimensions in _missing(decision, spec):
        items.append(("missing", _board_sentence(models, dimensions)))
    for requirement in unapplied:
        items.append(("not_applied", _not_checked(requirement)))
    if decision.coverage is not None:
        message = decision.coverage.message.strip() or _OUTSIDE
        if not message.endswith("."):
            message += "."
        if len(message.encode("utf-8")) > MUST_MENTION_ITEM_BYTES:
            message = _OUTSIDE
        items.append(("coverage", message))
    qualify = len(decision.may_qualify)
    if qualify:
        items.append(("may_qualify", _qualify_sentence(qualify)))
    if decision.out_of_lineup > 0:
        items.append(("out_of_lineup", _lineup_sentence(decision.out_of_lineup)))
    if _hardware(decision, spec):
        items.append(("hardware", _HARDWARE))
    if _estimates(decision):
        items.append(("estimates", _ESTIMATES))
    return _trim(items)


def _proxy(decision: Decision) -> dict[str, list[str]]:
    models = _subjects(decision)
    if not models:
        return {}
    wanted = set(models)
    rows = [row for row in decision.results if row.model in wanted]
    found: dict[str, set[str]] = {}
    warned = False
    for row in rows:
        if "proxy_evidence_only" in row.warnings:
            warned = True
        for group in row.evidence:
            proxy = [item for item in group.items if item.directness == "proxy"]
            direct = [item for item in group.items if item.directness == "direct"]
            if proxy and not direct:
                found.setdefault(group.domain, set()).update(item.benchmark for item in proxy)
        for contribution in row.contributions:
            evidence = contribution.evidence
            if evidence and all(item.directness == "proxy" for item in evidence):
                dimension = contribution.dimension.removeprefix("-")
                found.setdefault(dimension, set()).update(item.benchmark for item in evidence)
    if decision.bands is not None:
        for band in (decision.bands.best, decision.bands.rest, decision.bands.thin):
            for entry in band:
                if entry.model not in wanted:
                    continue
                for estimate in entry.estimates:
                    if estimate.benchmarks > 0 and estimate.direct_benchmarks == 0:
                        found.setdefault(str(estimate.dimension), set())
    if not found and warned:
        domains = [
            estimate.domain
            for row in rows if row.estimates
            for estimate in row.estimates
        ]
        for domain in domains or ["the requested task"]:
            found.setdefault(domain, set())
    return {domain: sorted(benchmarks) for domain, benchmarks in sorted(found.items())}


def _proxy_sentence(domain: str, benchmarks: list[str]) -> str:
    if not benchmarks:
        return f"The evidence for {domain} is a general proxy, not task-specific."
    prefix = f"The evidence for {domain} is a general proxy ("
    suffix = "), not task-specific."
    shown: list[str] = []
    for benchmark in benchmarks:
        trial = shown + [benchmark]
        rest = len(benchmarks) - len(trial)
        extra = f", and {_count(rest)} more" if rest else ""
        text = prefix + ", ".join(trial) + extra + suffix
        if len(text.encode("utf-8")) <= MUST_MENTION_ITEM_BYTES:
            shown.append(benchmark)
        else:
            break
    if not shown:
        return _clip_item(prefix + benchmarks[0] + suffix)
    rest = len(benchmarks) - len(shown)
    extra = f", and {_count(rest)} more" if rest else ""
    return prefix + ", ".join(shown) + extra + suffix


def _missing(decision: Decision, spec: Spec | None) -> list[tuple[list[str], list[str]]]:
    """Models that share a missing dimension set, in answer order."""
    dimensions = _board_dimensions(spec)
    if not dimensions:
        return []
    groups: dict[tuple[str, ...], list[str]] = {}
    order: list[tuple[str, ...]] = []
    for model in _subjects(decision):
        missing = tuple(
            dimension for dimension in dimensions
            if _unmeasured(decision, model, dimension)
        )
        if not missing:
            continue
        bucket = groups.get(missing)
        if bucket is None:
            groups[missing] = [model]
            order.append(missing)
        elif model not in bucket:
            bucket.append(model)
    return [(groups[key], list(key)) for key in order]


def _board_sentence(models: list[str], dimensions: list[str]) -> str:
    """One leaderboard caveat. Names that overflow 200 bytes shorten; the wording does not."""
    many = len(models) > 1
    template = _BOARD_MANY if many else _BOARD_ONE
    name_counts = range(len(models), 0, -1) if many else (1,)
    for name_count in name_counts:
        names = _name_list(models, name_count, more="")
        for dim_count in range(len(dimensions), 0, -1):
            text = names + template.format(
                dimensions=_name_list(dimensions, dim_count, more=" dimensions"),
            )
            if len(text.encode("utf-8")) <= MUST_MENTION_ITEM_BYTES:
                return text
    names = _name_list(models, 1, more="")
    dims = _name_list(dimensions, 1, more=" dimensions")
    head, _, tail = template.partition("{dimensions}")
    room = MUST_MENTION_ITEM_BYTES - len((head + tail).encode("utf-8"))
    names = _clip_to(names, max(room - len(dims.encode("utf-8")), 1))
    dims = _clip_to(dims, max(room - len(names.encode("utf-8")), 1))
    return names + head + dims + tail


def _board_dimensions(spec: Spec | None) -> list[str]:
    if spec is None:
        return []
    objective = spec.optimize
    names: list[str] = []
    if objective.max:
        names.append(objective.max)
    if objective.min:
        names.append(objective.min)
    for step in objective.lexicographic or []:
        names.append(step.facet)
    names.extend(objective.weights or {})
    names.extend(objective.pareto or [])
    dimensions: list[str] = []
    for name in names:
        base = name.removeprefix("-")
        if base.startswith(("offering.", "licence.")) or base == HARDWARE_FIT:
            continue
        if base not in dimensions:
            dimensions.append(base)
    return dimensions


def _dimension_base(dimension: str) -> str:
    return dimension.split("/")[0].split(" @")[0]


def _unmeasured(decision: Decision, model: str, dimension: str) -> bool:
    """True when this model's objective position is an estimate, latent, or null.

    A driver board attached to a latent contribution is not a measured score.
    Rows that carry neither a contribution nor an estimate for the dimension
    say nothing, so they are not reported as unmeasured.
    """
    base = _dimension_base(dimension)
    saw = False
    measured = False
    for row in decision.results:
        if row.model != model:
            continue
        states = [
            _contribution_measured(contribution)
            for contribution in row.contributions
            if _contribution_matches(contribution, dimension, base)
        ]
        if states:
            saw = True
            measured = measured or any(states)
            continue
        if _direct_board(row, dimension, base):
            saw = True
            measured = True
            continue
        if _estimate_position(row, dimension, base):
            saw = True
    return saw and not measured


def _contribution_matches(contribution: Contribution, dimension: str, base: str) -> bool:
    key = contribution.dimension.removeprefix("-")
    if contribution.refinement:
        key = f"{key}/{contribution.refinement}"
    return key == dimension or key == base


def _contribution_measured(contribution: Contribution) -> bool:
    formula = (contribution.formula or "").lower()
    if contribution.unit == _LATENT_UNIT or "estimate" in formula:
        return False
    return contribution.value is not None or contribution.raw_value is not None


def _direct_board(row: Result, dimension: str, base: str) -> bool:
    for group in row.evidence:
        matched = group.domain in (dimension, base) or any(
            item.benchmark in (dimension, base) for item in group.items
        )
        if matched and any(
            item.directness == "direct" and item.value is not None for item in group.items
        ):
            return True
    return False


def _estimate_position(row: Result, dimension: str, base: str) -> bool:
    if row.estimates and any(item.domain in (dimension, base) for item in row.estimates):
        return True
    return bool(row.refinement_estimates and any(
        item.key == dimension or item.refinement == dimension or item.domain == dimension
        for item in row.refinement_estimates
    ))


def _subjects(decision: Decision) -> list[str]:
    models: list[str] = []
    if decision.answer is not None:
        models.extend(decision.answer.deterministic_order)
    if decision.results and decision.results[0].model and decision.results[0].model not in models:
        models.append(decision.results[0].model)
    return models


def _presents_tie(decision: Decision) -> bool:
    answer = decision.answer
    return decision.status == "answered" and answer is not None and answer.kind == "tied"


def _has_class_gate(spec: Spec) -> bool:
    for condition in spec.where:
        for leaf in _leaves(condition):
            if isinstance(leaf, Known):
                if leaf.known == _CLASS_FACET:
                    return True
            elif getattr(leaf, "facet", None) == _CLASS_FACET:
                return True
    return False


def _class_sentence(decision: Decision, spec: Spec | None) -> str:
    if spec is None or _has_class_gate(spec):
        return ""
    classes = _visible_classes(decision)
    if not classes:
        return _NO_CLASS + "."
    return f"{_NO_CLASS}, including {_name_list(classes, 8, more=' classes')}."


def _lineup_sentence(count: int) -> str:
    if count == 1:
        rest = "1 active catalogue model is outside it."
    else:
        rest = f"{_count(count)} active catalogue models are outside it."
    return f"ModelSpec compared only the models in its lineup; {rest}"


def _visible_classes(decision: Decision) -> list[str]:
    order: list[str] = []
    for model in _subjects(decision):
        if model not in order:
            order.append(model)
    for row in decision.results:
        if row.model and row.model not in order:
            order.append(row.model)
    by_model: dict[str, list[str]] = {}
    for candidate in decision.top:
        found = by_model.setdefault(candidate.offering.model, [])
        for fact in candidate.facts:
            if fact.facet != _CLASS_FACET or fact.value is None:
                continue
            values = fact.value if isinstance(fact.value, list) else [fact.value]
            for value in values:
                text = str(value)
                if text and text != _TEXT_GENERATOR and text not in found:
                    found.append(text)
    classes: list[str] = []
    for model in order:
        for text in by_model.get(model, []):
            if text not in classes:
                classes.append(text)
    return classes


def _cost_only(decision: Decision, spec: Spec | None) -> bool:
    if decision.status == "no_feasible":
        return False  # nothing was ordered
    reading = decision.reading
    claimed = reading is not None and _QUALITY_CLAIM in reading.do_not_claim
    if spec is None:
        return claimed
    bases = _objective_bases(spec)
    if not bases:
        return claimed
    return all(base in _monetary_objectives() for base in bases)


def _objective_bases(spec: Spec) -> list[str]:
    objective = spec.optimize
    if objective.max:
        names = [objective.max]
    elif objective.min:
        names = [objective.min]
    elif objective.lexicographic:
        names = [step.facet for step in objective.lexicographic]
    else:
        names = list(objective.weights or objective.pareto or [])
    return [split_dimension(name.removeprefix("-"))[0] for name in names]


def _cost_tie_break(decision: Decision) -> bool:
    answer = decision.answer
    return (
        _presents_tie(decision)
        and answer is not None
        and answer.tie_breakers.cheapest is not None
    )


def _hardware(decision: Decision, spec: Spec | None) -> bool:
    reading = decision.reading
    if reading is not None and HARDWARE_FIT in reading.estimates:
        return True
    if spec is not None and spec.access is not None and spec.access.kind == "own_hardware":
        return True
    if spec is None:
        return False
    for condition in spec.where:
        if HARDWARE_FIT in render_condition(condition):
            return True
    objective = spec.optimize
    names = [objective.max, objective.min, *(objective.weights or {}), *(objective.pareto or [])]
    names.extend(step.facet for step in objective.lexicographic or [])
    return any(name and HARDWARE_FIT in name for name in names)


def _estimates(decision: Decision) -> bool:
    reading = decision.reading
    if reading is not None and any(
        name in reading.estimates for name in ("results.estimates", "results.refinement_estimates")
    ):
        return True
    return any(row.estimates or row.refinement_estimates for row in decision.results)


def _trim(items: list[tuple[str, str]]) -> list[tuple[str, str]]:
    clipped = [(kind, _clip_item(text)) for kind, text in items]
    if len(clipped) <= MUST_MENTION_MAX:
        return clipped
    kept = _keep_classes(clipped, MUST_MENTION_MAX - 1)
    dropped = len(clipped) - len(kept)
    return [*kept, ("more", f"and {_count(dropped)} more.")]


def _caveats(mentions: list[tuple[str, str]], limit: int) -> list[str]:
    if limit >= len(mentions):
        return [text for _kind, text in mentions]
    if limit <= 0:
        return []
    kept = _keep_classes(mentions, max(limit - 1, 0))
    dropped = len(mentions) - len(kept)
    sentences = [text for _kind, text in kept]
    if dropped:
        sentences.append(f"and {_count(dropped)} more.")
    return sentences


def _keep_classes(items: list[tuple[str, str]], slots: int) -> list[tuple[str, str]]:
    if slots <= 0:
        return []
    chosen: list[int] = []
    seen: set[str] = set()
    rest: list[int] = []
    for index, (kind, _text) in enumerate(items):
        if kind not in seen:
            chosen.append(index)
            seen.add(kind)
        else:
            rest.append(index)
    picked = chosen[:slots]
    for index in rest:
        if len(picked) >= slots:
            break
        picked.append(index)
    keep = set(picked)
    return [item for index, item in enumerate(items) if index in keep]


def _name_list(names: list[str], limit: int, *, more: str) -> str:
    shown = names[: max(limit, 1)]
    rest = len(names) - len(shown)
    if len(shown) == 1:
        listed = shown[0]
    elif len(shown) == 2:
        listed = f"{shown[0]} and {shown[1]}"
    else:
        listed = ", ".join(shown[:-1]) + ", and " + shown[-1]
    if rest:
        listed += f", and {_count(rest)} more{more}"
    return listed


def _bounded(items: list[str], limit: int) -> str:
    if not items:
        return ""
    shown = items[: max(limit, 1)]
    rest = len(items) - len(shown)
    text = "; ".join(shown)
    if rest:
        text += f"; and {_count(rest)} more"
    return text


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
    text = definition.casefold()
    return any(word in text for word in ("dollar", "yuan", "euro", "pound", "yen", "currency"))


def _not_checked(requirement: str) -> str:
    sentence = requirement + _NOT_CHECKED
    if len(sentence.encode("utf-8")) <= MUST_MENTION_ITEM_BYTES:
        return sentence
    room = MUST_MENTION_ITEM_BYTES - len(_NOT_CHECKED.encode("utf-8"))
    return _clip_to(requirement, room) + _NOT_CHECKED


def _clip_item(text: str) -> str:
    return _clip_to(text, MUST_MENTION_ITEM_BYTES)


def _clip_paragraph(text: str) -> str:
    """Last resort: shorten the longest sentence, keeping the no-answer line."""
    parts = text.split(". ")
    while len(". ".join(parts).encode("utf-8")) > SUMMARY_BYTES and len(parts) > 1:
        index = max(range(1, len(parts)), key=lambda i: len(parts[i].encode("utf-8")))
        shortened = _clip_to(parts[index].rstrip("."), max(40, len(parts[index].encode("utf-8")) - 80))
        if shortened == parts[index]:
            break
        parts[index] = shortened if shortened.endswith(".") else shortened
    text = ". ".join(parts)
    if len(text.encode("utf-8")) <= SUMMARY_BYTES:
        return text
    head, _, tail = text.partition(". ")
    room = SUMMARY_BYTES - len((head + ". ").encode("utf-8"))
    if room < 16 or not tail:
        return _clip_to(text, SUMMARY_BYTES)
    return head + ". " + _clip_to(tail, room)


def _clip_to(text: str, max_bytes: int) -> str:
    raw = text.encode("utf-8")
    if len(raw) <= max_bytes:
        return text
    mark = "…"
    mark_len = len(mark.encode("utf-8"))
    if max_bytes < mark_len:
        return raw[: max(max_bytes, 0)].decode("utf-8", errors="ignore")
    body = raw[: max_bytes - mark_len].decode("utf-8", errors="ignore").rstrip()
    clipped = body + mark
    encoded = clipped.encode("utf-8")
    if len(encoded) <= max_bytes:
        return clipped
    return encoded[:max_bytes].decode("utf-8", errors="ignore")
