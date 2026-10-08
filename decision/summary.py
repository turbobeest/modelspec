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

_NO_ANSWER = "ModelSpec's answer is that there is no answer."
_TIE_TAIL = "and the evidence does not separate them."
_ESTIMATES = "Estimates are estimates, not measurements."
_HARDWARE = (
    "fits_hardware is an estimate, not a measured fit for a quantization or context workload."
)
_OUTSIDE = "The request is outside coverage."
_CLASS_FACET = "model.class"
_TEXT_GENERATOR = "text-generator"
_NO_CLASS = "No model class was required, so the ranking spans every class"
_NO_CLASS_MENTION = "No model.class gate was set; results span all model classes."
_COST_ONLY = "This answer is ordered by cost only; it is not a quality ranking."
_TIE_COST = "Tie-breakers are conditional; cost order is not quality order."
_QUALITY_CLAIM = "Do not claim a quality rank from this objective."
_LATENT_UNIT = "latent capability"
_COST_BASES = frozenset({
    "offering.cost_per_task",
    "offering.price.input",
    "offering.price.output",
})


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
        "caveat": len(mentions),
    }
    floors = {
        "tie": 1,
        "hard": 1,
        "prefer": 1,
        "relax": 1,
        "missing": 1,
        "caveat": len({kind for kind, _text in mentions}) or 0,
    }
    text = _compose(decision, spec, unapplied, mentions, limits)
    order = ("hard", "prefer", "relax", "missing", "tie", "caveat")
    while len(text.encode("utf-8")) > SUMMARY_BYTES:
        key = next((name for name in order if limits[name] > floors[name]), None)
        if key is None:
            break
        limits[key] -= 1
        text = _compose(decision, spec, unapplied, mentions, limits)
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
    parts = [_answer_sentence(decision, limits["tie"]), _class_sentence(decision, spec)]
    parts.extend(_why(decision, spec, unapplied, limits))
    parts.extend(_constraints(spec, unapplied, limits))
    parts.extend(_caveats(mentions, limits["caveat"]))
    return " ".join(part for part in parts if part)


def _answer_sentence(decision: Decision, tie_limit: int) -> str:
    answer = decision.answer
    if decision.status in ("partial", "no_feasible") or answer is None:
        return _NO_ANSWER
    if answer.kind == "tied":
        names = _name_list(list(answer.deterministic_order), tie_limit, more=" in answer.members")
        return f"ModelSpec's answer is a tie among {names}, {_TIE_TAIL}"
    member = answer.deterministic_order[0]
    return f"ModelSpec's answer is {member}."


def _why(
    decision: Decision, spec: Spec | None, unapplied: list[str], limits: dict[str, int],
) -> list[str]:
    if decision.status == "no_feasible":
        gates, _dont = _gates(spec, set(unapplied))
        if gates:
            listed = _bounded(gates, limits["hard"])
            exclude = f"These requirements together exclude every model: {listed}."
        else:
            exclude = "These requirements together exclude every model."
        sentences = [exclude]
        relax = _bounded(list(decision.relax), limits["relax"])
        if relax:
            sentences.append(f"Relax suggestions: {relax}. These are options, not an answer.")
        nearest = _bounded([item.relaxed for item in decision.relax_to], limits["relax"])
        if nearest:
            sentences.append(f"Nearest relaxations, not an answer: {nearest}.")
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
        noun = "model" if count == 1 else "models"
        sentences.append(f"{count} {noun} may qualify; unknown values.")
    return sentences


def _constraints(spec: Spec | None, unapplied: list[str], limits: dict[str, int]) -> list[str]:
    gates, dont_care = _gates(spec, set(unapplied))
    prefers = _prefers(spec, set(unapplied))
    sentences: list[str] = []
    if gates:
        sentences.append(f"Hard requirements: {_bounded(gates, limits['hard'])}.")
    sentences.extend(dont_care)
    if prefers:
        sentences.append(
            "Preferences that rank without excluding: "
            f"{_bounded(prefers, limits['prefer'])}."
        )
    if unapplied:
        sentences.append(f"Not applied and not enforced: {_bounded(unapplied, limits['hard'])}.")
    return sentences


def _gates(spec: Spec | None, unapplied: set[str]) -> tuple[list[str], list[str]]:
    if spec is None:
        return [], []
    gates: list[str] = []
    dont_care: list[str] = []
    phrase = f"{OPENNESS_FACET} is not required (either acceptable)."
    for condition in spec.where:
        leaves = list(_leaves(condition))
        if len(leaves) == 1 and _openness_either(leaves[0]):
            if phrase not in dont_care:
                dont_care.append(phrase)
            continue
        if any(_openness_either(leaf) for leaf in leaves) and phrase not in dont_care:
            dont_care.append(phrase)
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


def _openness_either(condition: object) -> bool:
    return (
        isinstance(condition, InSet)
        and condition.facet == OPENNESS_FACET
        and condition.in_ is not None
        and set(condition.in_) == OPENNESS_EITHER
    )


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
        items.append(("tie", f"No single winner: {count} models are tied."))
    if spec is not None and not _has_class_gate(spec):
        items.append(("class", _NO_CLASS_MENTION))
    if _cost_only(decision, spec):
        items.append(("cost", _COST_ONLY))
    if _cost_tie_break(decision):
        items.append(("tie_cost", _TIE_COST))
    for domain, benchmarks in _proxy(decision).items():
        items.append(("proxy", _proxy_sentence(domain, benchmarks)))
    for model, dimensions in _missing(decision, spec):
        items.append((
            "missing",
            f"{model} has no leaderboard data for {dimensions}; "
            "its position is estimated, not measured.",
        ))
    for requirement in unapplied:
        items.append((
            "not_applied",
            f"{requirement} was not applied; ModelSpec did not check it.",
        ))
    if decision.coverage is not None:
        message = decision.coverage.message.strip() or _OUTSIDE
        if not message.endswith("."):
            message += "."
        if len(message.encode("utf-8")) > MUST_MENTION_ITEM_BYTES:
            message = _OUTSIDE
        items.append(("coverage", message))
    qualify = len(decision.may_qualify)
    if qualify:
        noun = "model" if qualify == 1 else "models"
        items.append(("may_qualify", f"{qualify} {noun} may qualify; unknown values."))
    if decision.out_of_lineup > 0:
        count = decision.out_of_lineup
        noun = "model is" if count == 1 else "models are"
        items.append(("out_of_lineup", f"{count} active {noun} out of the lineup."))
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
        extra = f", and {rest} more" if rest else ""
        text = prefix + ", ".join(trial) + extra + suffix
        if len(text.encode("utf-8")) <= MUST_MENTION_ITEM_BYTES:
            shown.append(benchmark)
        else:
            break
    if not shown:
        return _clip_item(prefix + benchmarks[0] + suffix)
    rest = len(benchmarks) - len(shown)
    extra = f", and {rest} more" if rest else ""
    return prefix + ", ".join(shown) + extra + suffix


def _missing(decision: Decision, spec: Spec | None) -> list[tuple[str, str]]:
    dimensions = _board_dimensions(spec)
    if not dimensions:
        return []
    pairs: list[tuple[str, str]] = []
    for model in _subjects(decision):
        missing = [
            dimension for dimension in dimensions
            if _unmeasured(decision, model, dimension)
        ]
        if missing:
            pairs.append((model, _name_list(missing, 8, more=" dimensions")))
    return pairs


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
    reading = decision.reading
    claimed = reading is not None and _QUALITY_CLAIM in reading.do_not_claim
    if spec is None:
        return claimed
    bases = _objective_bases(spec)
    if not bases:
        return claimed
    return all(base in _COST_BASES for base in bases)


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
    return [*kept, ("more", f"and {dropped} more.")]


def _caveats(mentions: list[tuple[str, str]], limit: int) -> list[str]:
    if limit >= len(mentions):
        return [text for _kind, text in mentions]
    if limit <= 0:
        return []
    kept = _keep_classes(mentions, max(limit - 1, 0))
    dropped = len(mentions) - len(kept)
    sentences = [text for _kind, text in kept]
    if dropped:
        sentences.append(f"and {dropped} more.")
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
        listed += f", and {rest} more{more}"
    return listed


def _bounded(items: list[str], limit: int) -> str:
    if not items:
        return ""
    shown = items[: max(limit, 1)]
    rest = len(items) - len(shown)
    text = "; ".join(shown)
    if rest:
        text += f"; and {rest} more"
    return text


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
    ellipsis = "…".encode("utf-8")
    if max_bytes <= len(ellipsis):
        return ellipsis.decode("utf-8")
    cut = raw[: max_bytes - len(ellipsis)]
    while cut and (cut[-1] & 0xC0) == 0x80:
        cut = cut[:-1]
    clipped = cut.decode("utf-8").rstrip() + "…"
    if len(clipped.encode("utf-8")) > max_bytes:
        return clipped.encode("utf-8")[:max_bytes].decode("utf-8", errors="ignore")
    return clipped
