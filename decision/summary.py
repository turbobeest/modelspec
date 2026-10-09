"""Plain-language summary of one Decision (MODEL-339).

Deterministic templates only: the same Decision and Spec always produce the
same bytes. No clock, no randomness, and no model call.

``summary_for_user`` is one paragraph for the end user. ``must_mention`` is the
short list of facts a report of that answer has to carry, and it also names
claims the answer does not support (MODEL-351). Both are computed from the
full Decision, before any agent-budget trim.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from decision.contract import (
    AllOf,
    AnyOf,
    Contribution,
    Decision,
    InSet,
    InventoryProfile,
    Known,
    NotOf,
    Preference,
    Result,
    Spec,
    SpecError,
    _render_value,
    render_condition,
)
from decision.optimise import OBJECTIVE_GAP_PREFIX, OPTIMISER_DIAGNOSTICS
from decision.reading import HARDWARE_FIT
from decision.refinements import split_dimension
from decision.resolve import resolve

SUMMARY_BYTES = 1_200
TIE_NAME_CAP = 8
MUST_MENTION_MAX = 10
MUST_MENTION_ITEM_BYTES = 200
_BOARD_DIMENSION_CAP = 8
OPENNESS_FACET = "model.weights_openness"
OPENNESS_EITHER = frozenset({"open_weights", "closed_weights"})

_NO_FEASIBLE = "ModelSpec found no model that meets every requirement, so it names no pick."
_PARTIAL = "ModelSpec's answer is incomplete, so it names no pick."
_NULL_ANSWER = "ModelSpec has no answer for this request, so it names no pick."
_TIE_TAIL = "the evidence does not separate them."
_ESTIMATES = "Some values are estimates, not measurements."
_HARDWARE_TAIL = (
    " is an estimate; fit for a specific quantization, context length "
    "or runtime headroom is not established."
)
_HARDWARE = "fits_hardware" + _HARDWARE_TAIL
_HARDWARE_NOT_REQUIRED = (
    "model.fits_hardware was not required, so no model is established to fit the target hardware."
)
_PARTIAL_NO_FIT = (
    "No model is established as the best fit: "
    "some candidates lack values ModelSpec needs."
)
_PARTIAL_HEAD = "No model is established as the best fit: "
_TIE_NOT_A_PICK = " are tied; this is not a recommendation of any one of them."
_UNCHECKED = "ModelSpec checked only the stated requirements; other needs were not checked."
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
# Approved by Jamie 2026-10-08 23:22 ET. A wording change is a one-line edit.
_COUNT_ONE_NOT_PROXY = "1 record, not a proxy"
_COUNT_ONE_PROXY = "1 record, a proxy"
_COUNT_NONE_PROXIES = "{records} records, none of them proxies"
_COUNT_ALL_PROXIES = "{records} records, all of them proxies"
_COUNT_ONE_OF_THEM_A_PROXY = "{records} records, 1 of them a proxy"
_COUNT_SOME_PROXIES = "{records} records, {proxies} of them proxies"
_ESTIMATED_POSITION = "{model}'s position on {dimension} is estimated from {detail}."
_OPTION_TO = (
    "Relaxing {condition} to {relaxed} would admit a model; "
    "that is an option, not an answer."
)
_OPTION = "Relaxing {condition} would admit a model; that is an option, not an answer."
_OPTION_TOGETHER = (
    "Relaxing {conditions} together would admit a model; that is an option, not an answer."
)
_SINGLE_GATE = (
    "Removing only {condition} would let {n} models qualify; "
    "every other requirement stays as you set it."
)
_SINGLE_GATE_ONE = (
    "Removing only {condition} would let 1 model qualify; "
    "every other requirement stays as you set it."
)
_NO_SINGLE_GATE = (
    "No single requirement is the blocker: removing any one of them "
    "on its own still leaves no model."
)


def summarize(
    decision: Decision,
    spec: Spec | None = None,
    *,
    not_applied: Iterable[str] = (),
    profiles: Mapping[str, InventoryProfile] | None = None,
    feasible: int | None = None,
    record_counts: Mapping[str, Mapping[str, tuple[int, int]]] | None = None,
    proxy_benchmarks: Mapping[str, Iterable[str]] | None = None,
) -> tuple[str, list[str]]:
    """Return ``(summary_for_user, must_mention)``.

    ``feasible`` is how many candidates the gates left for the optimiser.
    ``None`` reads that from the funnel. An empty funnel is not evidence
    that the gates excluded everyone.

    ``record_counts`` maps a model to a dimension to ``(records, proxy records)``
    behind that objective position. The engine passes the capture that also
    feeds ``member_evidence``, before the cap of three, for every model
    ``_subjects`` names. ``None`` counts the records already on the Decision's
    contributions.

    ``proxy_benchmarks`` maps a dimension to the benchmark names on an
    all-proxy contribution. Explain none does not attach that evidence to
    the Decision, so a proxy sentence the bands already selected would
    otherwise omit the names. Names already on the Decision are left as they
    are.
    """
    unapplied = _unapplied(decision, not_applied)
    if spec is not None and spec.task_type is not None:
        task = f"task_type = {spec.task_type}"
        if task not in unapplied:
            unapplied.append(task)
    conditions = _applied_conditions(spec, profiles)
    mentions = _mentions(
        decision, spec, unapplied, conditions, record_counts, proxy_benchmarks,
    )
    summary = _summary(
        decision, spec, unapplied, mentions, conditions, feasible=feasible,
    )
    return summary, [text for _kind, text in mentions]


def _applied_conditions(
    spec: Spec | None, profiles: Mapping[str, InventoryProfile] | None,
) -> tuple:
    """The condition list the engine filters on: profile rules, then ``where``.

    ``resolve`` is that list. A hand-built spec the registry rejects still
    uses the same order, so a summary of it does not drop the profile rules.
    """
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


def _count(value: int) -> str:
    return f"{value:,}"


def _summary(
    decision: Decision,
    spec: Spec | None,
    unapplied: list[str],
    mentions: list[tuple[str, str]],
    conditions: tuple,
    *,
    feasible: int | None = None,
) -> str:
    limits = {
        "single": 12,
        "tie": TIE_NAME_CAP,
        "applied": 24,
        "hard": 24,
        "prefer": 12,
        "relax": 12,
        "missing": 12,
        "caveat": 0,
    }
    floors = {
        "single": 1,
        "tie": 1,
        "applied": 1,
        "hard": 1,
        "prefer": 1,
        "relax": 1,
        "missing": 1,
        "caveat": 0,
    }
    visible = _paragraph_mentions(decision, mentions)
    limits["caveat"] = len(visible)
    floors["caveat"] = len({kind for kind, _text in visible}) or 0
    # None lists every condition in the joint relaxation. Shorten that list
    # only after the other lists are at their floors, so the fixed ending stays.
    joint_limit: int | None = None
    # One gate sentence plus the full requirement lists can sit just over the
    # cap. The joint option yields first: a gate sentence already names a
    # removal that admits a model (MODEL-356).
    omit_joint = False
    text = _compose(
        decision, spec, unapplied, visible, limits, conditions, joint_limit, feasible,
        omit_joint=omit_joint,
    )
    # On no_feasible "Requirements applied" repeats the exclude list, so the
    # repeat shortens before the list that explains the empty answer (MODEL-351).
    order = ("single", "applied", "hard", "prefer", "relax", "missing", "tie", "caveat")
    while len(text.encode("utf-8")) > SUMMARY_BYTES:
        key = next((name for name in order if limits[name] > floors[name]), None)
        single = decision.relax_single
        if (
            key == "hard"
            and not omit_joint
            and single is not None
            and single.gates
            and _joint_conditions(decision, conditions)
        ):
            omit_joint = True
        elif key is not None:
            limits[key] -= 1
        else:
            count = len(_joint_conditions(decision, conditions))
            current = count if joint_limit is None else joint_limit
            if count <= 1 or current <= 1 or omit_joint:
                break
            joint_limit = current - 1
        text = _compose(
            decision, spec, unapplied, visible, limits, conditions, joint_limit, feasible,
            omit_joint=omit_joint,
        )
    if len(text.encode("utf-8")) > SUMMARY_BYTES:
        text = _clip_paragraph(text)
    return text


def _compose(
    decision: Decision,
    spec: Spec | None,
    unapplied: list[str],
    mentions: list[tuple[str, str]],
    limits: dict[str, int],
    conditions: tuple,
    joint_limit: int | None = None,
    feasible: int | None = None,
    *,
    omit_joint: bool = False,
) -> str:
    parts = [_answer_sentence(decision, limits["tie"])]
    parts.extend(_why(
        decision, spec, unapplied, limits, conditions, joint_limit, feasible,
        omit_joint=omit_joint,
    ))
    parts.extend(_constraints(spec, unapplied, limits, conditions))
    parts.extend(_caveats(mentions, limits["caveat"]))
    return _dedupe(parts)


def _paragraph_mentions(
    decision: Decision, mentions: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    """Caveats whose fact is not already in the answer, why, or constraints."""
    skip = {"not_applied", "partial"}
    if decision.status == "partial":
        # A partial answer's tie keeps its named must_mention text (MODEL-351):
        # the answer sentence names no members for "These N models" to refer to.
        skip.add("may_qualify")
    visible: list[tuple[str, str]] = []
    for kind, text in mentions:
        if kind in skip:
            continue
        if kind == "tie" and decision.status == "answered" and decision.answer is not None:
            count = _count(len(decision.answer.members))
            text = (
                f"These {count} models are tied; "
                "this is not a recommendation of any one of them."
            )
        visible.append((kind, text))
    return visible


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
    decision: Decision,
    spec: Spec | None,
    unapplied: list[str],
    limits: dict[str, int],
    conditions: tuple,
    joint_limit: int | None = None,
    feasible: int | None = None,
    *,
    omit_joint: bool = False,
) -> list[str]:
    if decision.status == "no_feasible":
        # A diagnostic from optimise([]) is an objective failure only when the
        # gates left candidates. Otherwise it is the engine's placeholder for
        # a lineup the gates already emptied.
        if _optimiser_diagnostic(decision) and _gates_left_candidates(decision, feasible):
            objective = _objective_name(decision, spec)
            if objective:
                return [_MISSING_OBJECTIVE.format(objective=objective)]
        gates, _dont = _gates(spec, set(unapplied), conditions)
        if gates:
            listed = _bounded(gates, limits["hard"])
            exclude = f"These requirements together exclude every model: {listed}."
        else:
            exclude = "These requirements together exclude every model."
        sentences = [exclude]
        sentences.extend(
            _relaxation_options(
                decision, conditions, limits["relax"], joint_limit, omit_joint=omit_joint,
            )
        )
        sentences.extend(_single_gate_sentences(decision, limits["single"]))
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


def _optimiser_diagnostic(decision: Decision) -> bool:
    """True when ``relax`` carries a reason ``optimise`` returns for ``no_feasible``.

    The engine rewrites that reason, once the gates left candidates, into a
    sentence that names the objective. That sentence is the same failure.
    """
    return any(
        item in OPTIMISER_DIAGNOSTICS or item.startswith(OBJECTIVE_GAP_PREFIX)
        for item in decision.relax
    )


def _gates_left_candidates(decision: Decision, feasible: int | None = None) -> bool:
    """Whether the optimiser received any candidate.

    ``feasible`` is ``len(FilterResult.feasible)``, the tuple ``run_optimise``
    passes to ``optimise`` after profile rules and ``where``. ``explain``
    ``none`` does not record the funnel. An empty funnel is not evidence
    that the gates excluded everyone.
    """
    if feasible is not None:
        return feasible > 0
    funnel = decision.eliminated.funnel
    if not funnel:
        return True
    return funnel[-1].after > 0


def _objective_name(decision: Decision, spec: Spec | None) -> str | None:
    """The objective to name in the missing-values sentence.

    The sentence has no form without that name. A spec supplies it. Without a
    spec, the only names the decision carries are the unknown facets on
    ``may_qualify``.
    """
    if spec is not None:
        return _objective_phrase(spec) or None
    names: list[str] = []
    for row in decision.may_qualify:
        for facet in row.unknown:
            if facet not in names:
                names.append(facet)
    if not names:
        return None
    if len(names) == 1:
        return names[0]
    return ", ".join(names)


def _joint_conditions(decision: Decision, conditions: tuple) -> list[str]:
    """``relax`` entries that are applied gates and have no ``relax_to`` item."""
    requirements = set(_condition_gates(conditions)[0])
    covered = {item.condition for item in decision.relax_to}
    return [
        condition for condition in decision.relax
        if condition not in covered and condition in requirements
    ]


def _single_gate_sentences(decision: Decision, limit: int) -> list[str]:
    """Gates whose removal alone admits models, in the order ``relax_single`` gives.

    ``limit`` is this paragraph's own cap for these sentences. The trim lowers
    it to 1 before any requirement list loses an item, and no further, so the
    first gate stays. The none sentence is emitted only when removing every
    relaxable gate together still admits a model and ``question_admits`` is
    false.
    """
    single = decision.relax_single
    if single is None:
        return []
    if single.status == "none":
        if single.together_admits > 0 and not single.question_admits:
            return [_NO_SINGLE_GATE]
        return []
    return [
        _single_gate_sentence(gate.condition, gate.admits)
        for gate in single.gates[:limit]
    ]


def _single_gate_sentence(condition: str, admits: int) -> str:
    if admits == 1:
        return _SINGLE_GATE_ONE.format(condition=condition)
    return _SINGLE_GATE.format(condition=condition, n=_count(admits))


def _relaxation_options(
    decision: Decision, conditions: tuple, limit: int, joint_limit: int | None = None,
    *,
    omit_joint: bool = False,
) -> list[str]:
    """``relax_to`` items are each enough. Uncovered ``relax`` entries are one set.

    ``limit`` caps how many ``relax_to`` sentences are written out. Further
    items are counted inside the last of those sentences, so each sentence
    keeps its ending. The joint option stays while any ``relax_to`` sentence
    stays, unless the paragraph has already kept a single-gate sentence and
    still does not fit.
    """
    items = list(decision.relax_to)
    uncovered = [] if omit_joint else _joint_conditions(decision, conditions)
    joint = _joint_option(uncovered, joint_limit) if uncovered else None
    if not items and joint is None:
        return []
    budget = max(limit, 1)
    if joint is None:
        return _relax_to_sentences(items, budget)
    return [*_relax_to_sentences(items, min(len(items), budget)), joint]


def _relax_to_sentences(items: list, take: int) -> list[str]:
    if take <= 0 or not items:
        return []
    shown = items[:take]
    extra = len(items) - len(shown)
    sentences = [
        _OPTION_TO.format(condition=item.condition, relaxed=item.relaxed)
        for item in shown
    ]
    if extra:
        last = shown[-1]
        relaxed = f"{last.relaxed}, and {_count(extra)} more"
        sentences[-1] = _OPTION_TO.format(condition=last.condition, relaxed=relaxed)
    return sentences


def _joint_option(conditions: list[str], limit: int | None = None) -> str:
    if len(conditions) == 1:
        return _OPTION.format(condition=conditions[0])
    cap = len(conditions) if limit is None else max(limit, 1)
    listed = _name_list(conditions, cap, more="")
    return _OPTION_TOGETHER.format(conditions=listed)


def _constraints(
    spec: Spec | None, unapplied: list[str], limits: dict[str, int], conditions: tuple,
) -> list[str]:
    gates, dont_care = _gates(spec, set(unapplied), conditions)
    prefers = _prefers(spec, set(unapplied))
    sentences: list[str] = []
    if gates:
        sentences.append(f"Requirements applied: {_bounded(gates, limits['applied'])}.")
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


def _gates(
    spec: Spec | None, unapplied: set[str], conditions: tuple,
) -> tuple[list[str], list[str]]:
    if spec is None:
        return [], []
    gates, dont_care = _condition_gates(conditions)
    for facet, level in (spec.capabilities or {}).items():
        if level == "required" and facet not in unapplied:
            gates.append(f"{facet} is required")
    return gates, dont_care


def _condition_gates(conditions: tuple) -> tuple[list[str], list[str]]:
    gates: list[str] = []
    dont_care: list[str] = []
    phrase = f"{OPENNESS_FACET} is not required (either acceptable)."
    for condition in conditions:
        if _plain_openness_either(condition):
            if phrase not in dont_care:
                dont_care.append(phrase)
            continue
        gates.append(render_condition(condition))
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
    decision: Decision,
    spec: Spec | None,
    unapplied: list[str],
    conditions: tuple,
    record_counts: Mapping[str, Mapping[str, tuple[int, int]]] | None = None,
    proxy_benchmarks: Mapping[str, Iterable[str]] | None = None,
) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    tie = _tie_item(decision)
    if tie:
        items.append(("tie", tie))
    partial = _partial_item(decision)
    if partial:
        items.append(("partial", partial))
    scope = _class_sentence(decision, spec, conditions)
    if scope:
        items.append(("class", scope))
    if _cost_only(decision, spec):
        items.append(("cost", _COST_ONLY))
    if _cost_tie_break(decision):
        items.append(("tie_cost", _TIE_COST))
    for domain, benchmarks in _proxy(decision, proxy_benchmarks).items():
        items.append(("proxy", _proxy_sentence(domain, benchmarks)))
    for models, dimensions, records, proxies in _missing(decision, spec, record_counts):
        items.append(("missing", _board_sentence(
            models, dimensions, records=records, proxies=proxies,
        )))
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
    # A partial answer's own item already names the models that may qualify.
    if qualify and decision.status != "partial":
        items.append(("may_qualify", _qualify_sentence(qualify)))
    if decision.out_of_lineup > 0:
        items.append(("out_of_lineup", _lineup_sentence(decision.out_of_lineup)))
    if _hardware(decision, spec, conditions):
        items.append(("hardware", _hardware_item(spec, conditions)))
    if _estimates(decision):
        items.append(("estimates", _ESTIMATES))
    if spec is not None:
        items.append(("unchecked", _UNCHECKED))
    return _trim(items)


def _proxy(
    decision: Decision,
    proxy_benchmarks: Mapping[str, Iterable[str]] | None = None,
) -> dict[str, list[str]]:
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
    # Explain none keeps the bands, which name the domain and not the
    # benchmarks. The capture loaded the same all-proxy contribution evidence
    # the summary reads. Fill only a domain that has no names yet, so a
    # sentence that already names its benchmarks stays word for word.
    if proxy_benchmarks:
        for domain, names in proxy_benchmarks.items():
            slot = found.get(domain)
            if slot is not None and not slot:
                slot.update(name for name in names if isinstance(name, str) and name)
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


def _missing(
    decision: Decision,
    spec: Spec | None,
    record_counts: Mapping[str, Mapping[str, tuple[int, int]]] | None,
) -> list[tuple[list[str], list[str], int, int]]:
    """One ``(model, dimension)`` when that position was estimated from records.

    N=0 keeps the no-leaderboard sentence: models that share one set of
    unmeasured dimensions share one item, placed where the first of them
    appears. Order follows the answer, then the objective's dimensions.
    """
    dimensions = _board_dimensions(spec)
    if not dimensions:
        return []
    items: list[tuple[list[str], list[str], int, int]] = []
    zero_at: dict[tuple[str, ...], int] = {}
    for model in _subjects(decision):
        missing = [
            dimension for dimension in dimensions
            if _unmeasured(decision, model, dimension)
        ]
        if not missing:
            continue
        by_count: dict[tuple[int, int], list[str]] = {}
        count_order: list[tuple[int, int]] = []
        for dimension in missing:
            pair = _record_pair(decision, model, dimension, record_counts)
            bucket = by_count.get(pair)
            if bucket is None:
                by_count[pair] = [dimension]
                count_order.append(pair)
            else:
                bucket.append(dimension)
        for records, proxies in count_order:
            dims = by_count[(records, proxies)]
            if records <= 0:
                key = tuple(dims)
                slot = zero_at.get(key)
                if slot is None:
                    zero_at[key] = len(items)
                    items.append(([model], list(dims), 0, 0))
                elif model not in items[slot][0]:
                    items[slot][0].append(model)
                continue
            for dimension in dims:
                items.append(([model], [dimension], records, proxies))
    return items


def record_counts_from_capture(captured) -> dict[str, dict[str, tuple[int, int]]]:
    """Per-model dimension counts carried beside a member-evidence capture."""
    found: dict[str, dict[str, tuple[int, int]]] = {}
    for entry in captured:
        counts = entry[2] if len(entry) > 2 else None
        if isinstance(counts, dict):
            found[entry[0]] = {
                dimension: (int(pair[0]), int(pair[1]))
                for dimension, pair in counts.items()
            }
    return found


def proxy_benchmarks_from_capture(captured) -> dict[str, list[str]]:
    """Benchmark names on all-proxy contributions, unioned across the capture.

    The fourth element of a capture row is that map for one model. A row
    without it contributes no names. Order is the sorted union, which is the
    order ``_proxy`` already uses for names it read off the Decision.
    """
    found: dict[str, set[str]] = {}
    for entry in captured:
        names = entry[3] if len(entry) > 3 else None
        if not isinstance(names, dict):
            continue
        for dimension, benchmarks in names.items():
            if not isinstance(dimension, str) or not dimension:
                continue
            slot = found.setdefault(dimension, set())
            for benchmark in benchmarks:
                if isinstance(benchmark, str) and benchmark:
                    slot.add(benchmark)
    return {dimension: sorted(benchmarks) for dimension, benchmarks in sorted(found.items())}


def _record_pair(
    decision: Decision,
    model: str,
    dimension: str,
    record_counts: Mapping[str, Mapping[str, tuple[int, int]]] | None,
) -> tuple[int, int]:
    if record_counts is not None and model in record_counts:
        found = record_counts[model]
        if dimension in found:
            return _pair(found[dimension])
        base = _dimension_base(dimension)
        if base in found:
            return _pair(found[base])
        return (0, 0)
    return _decision_record_counts(decision, model, dimension)


def _pair(value) -> tuple[int, int]:
    records, proxies = value
    return int(records), int(proxies)


def _decision_record_counts(decision: Decision, model: str, dimension: str) -> tuple[int, int]:
    """Records on this model's unmeasured contribution for one dimension.

    The same items ``contributions`` stores. A result row wins over ``top``.
    """
    from decision.explain import tally_evidence_records

    base = _dimension_base(dimension)
    rows = [row for row in decision.results if _row_model(row) == model]
    if not rows:
        rows = [row for row in decision.top if _row_model(row) == model]
    items = []
    for row in rows:
        for contribution in row.contributions:
            if not _contribution_matches(contribution, dimension, base):
                continue
            if _contribution_measured(contribution):
                continue
            items.extend(contribution.evidence)
    return tally_evidence_records(items)


def _estimate_detail(records: int, proxies: int) -> str:
    if records == 1 and proxies <= 0:
        return _COUNT_ONE_NOT_PROXY
    if records == 1 and proxies == 1:
        return _COUNT_ONE_PROXY
    shown = _count(records)
    if proxies <= 0:
        return _COUNT_NONE_PROXIES.format(records=shown)
    if proxies == records:
        return _COUNT_ALL_PROXIES.format(records=shown)
    if proxies == 1:
        return _COUNT_ONE_OF_THEM_A_PROXY.format(records=shown)
    return _COUNT_SOME_PROXIES.format(records=shown, proxies=_count(proxies))


def _board_affixes(many_models: bool) -> tuple[str, str]:
    template = _BOARD_MANY if many_models else _BOARD_ONE
    head, _, tail = template.partition("{dimensions}")
    return head, tail


def _estimated_position_sentence(model: str, dimension: str, records: int, proxies: int) -> str:
    """One approved sentence. A name that overflows 200 bytes shortens; the wording does not."""
    detail = _estimate_detail(records, proxies)
    text = _ESTIMATED_POSITION.format(model=model, dimension=dimension, detail=detail)
    if len(text.encode("utf-8")) <= MUST_MENTION_ITEM_BYTES:
        return text
    tail = f" is estimated from {detail}."
    head = "'s position on "
    room = MUST_MENTION_ITEM_BYTES - len((head + tail).encode("utf-8"))
    model_text = _clip_to(model, max(room - len(dimension.encode("utf-8")), 1))
    dimension_text = _clip_to(dimension, max(room - len(model_text.encode("utf-8")), 1))
    return model_text + head + dimension_text + tail


def _board_sentence(
    models: list[str], dimensions: list[str], *, records: int = 0, proxies: int = 0,
) -> str:
    """One leaderboard caveat. Names that overflow 200 bytes shorten; the wording does not."""
    if records > 0:
        return _estimated_position_sentence(models[0], dimensions[0], records, proxies)
    many = len(models) > 1
    head, tail = _board_affixes(many)
    # A 200-byte item never holds more than a handful of ids, so the search
    # starts from small caps: the cost stays bounded however large the tie or
    # objective is.
    name_counts = range(min(len(models), TIE_NAME_CAP), 0, -1) if many else (1,)
    for name_count in name_counts:
        names = _name_list(models, name_count, more="")
        for dim_count in range(min(len(dimensions), _BOARD_DIMENSION_CAP), 0, -1):
            text = names + head + _name_list(dimensions, dim_count, more=" dimensions") + tail
            if len(text.encode("utf-8")) <= MUST_MENTION_ITEM_BYTES:
                return text
    names = _name_list(models, 1, more="")
    dims = _name_list(dimensions, 1, more=" dimensions")
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
    ``limit`` drops members from ``results``. Their contributions stay on
    ``top`` when explain is full, and a capability estimate stays on ``bands``
    for every ranked model. A measured contribution is never overridden by a
    band. A row that carries neither a contribution nor an estimate says
    nothing, so it is not reported as unmeasured.
    """
    base = _dimension_base(dimension)
    covered = _measurement(decision.results, model, dimension, base, estimates=True)
    if covered is None:
        covered = _measurement(decision.top, model, dimension, base, estimates=False)
    if covered is True:
        return False
    if covered is False:
        return True
    return _band_unmeasured(decision, model, dimension, base)


def _measurement(rows, model: str, dimension: str, base: str, *, estimates: bool) -> bool | None:
    """True when measured, False when not, None when no row speaks for the dimension."""
    verdict: bool | None = None
    for row in rows:
        if _row_model(row) != model:
            continue
        state = _position_state(row.contributions, row.evidence, dimension, base)
        if state is None and estimates and _estimate_position(row, dimension, base):
            state = False
        if state is True:
            return True
        if state is False:
            verdict = False
    return verdict


def _row_model(row) -> str | None:
    model = getattr(row, "model", None)
    if model:
        return model
    offering = getattr(row, "offering", None)
    return None if offering is None else offering.model


def _position_state(contributions, evidence, dimension: str, base: str) -> bool | None:
    states = [
        _contribution_measured(contribution)
        for contribution in contributions
        if _contribution_matches(contribution, dimension, base)
    ]
    if states:
        return any(states)
    if _direct_board(evidence, dimension, base):
        return True
    return None


def _band_unmeasured(decision: Decision, model: str, dimension: str, base: str) -> bool:
    bands = decision.bands
    if bands is None:
        return False
    for entry in (*bands.best, *bands.rest, *bands.thin):
        if entry.model != model:
            continue
        for estimate in entry.estimates:
            key = estimate.dimension.removeprefix("-")
            if key == dimension or key == base:
                return True
    return False


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


def _direct_board(evidence, dimension: str, base: str) -> bool:
    for group in evidence:
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


def _tie_item(decision: Decision) -> str:
    answer = decision.answer
    if answer is None or answer.kind != "tied" or decision.status not in ("answered", "partial"):
        return ""
    names = list(answer.deterministic_order)
    for count in range(min(len(names), TIE_NAME_CAP), 0, -1):
        text = _name_list(names, count, more=" in answer.members") + _TIE_NOT_A_PICK
        if len(text.encode("utf-8")) <= MUST_MENTION_ITEM_BYTES:
            return text
    return _clip_item(_name_list(names, 1, more=" in answer.members") + _TIE_NOT_A_PICK)


def _partial_item(decision: Decision) -> str:
    if decision.status != "partial":
        return ""
    facets: list[str] = []
    models: list[str] = []
    unknown_sets: list[frozenset[str]] = []
    for row in decision.may_qualify:
        if row.model not in models:
            models.append(row.model)
        for facet in row.unknown:
            if facet not in facets:
                facets.append(facet)
        unknown_sets.append(frozenset(row.unknown))
    if not facets or not models:
        return _PARTIAL_NO_FIT
    return _partial_sentence(facets, models, len(set(unknown_sets)) == 1)


def _partial_sentence(facets: list[str], models: list[str], same: bool) -> str:
    verb = "is" if len(facets) == 1 else "are"
    scope = "unknown for" if same else "unknown for one or more of"

    def render(facet_limit: int, model_limit: int, facet_more: str) -> str:
        facet_list = _name_list(facets, facet_limit, more=facet_more)
        model_list = _name_list(models, model_limit, more=" in may_qualify")
        return f"{_PARTIAL_HEAD}{facet_list} {verb} {scope} {model_list}."

    for count in range(min(len(models), TIE_NAME_CAP), 0, -1):
        text = render(len(facets), count, "")
        if len(text.encode("utf-8")) <= MUST_MENTION_ITEM_BYTES:
            return text
    for count in range(min(len(facets), TIE_NAME_CAP), 0, -1):
        text = render(count, 1, " facets")
        if len(text.encode("utf-8")) <= MUST_MENTION_ITEM_BYTES:
            return text
    return _clip_item(render(1, 1, " facets"))


def _presents_tie(decision: Decision) -> bool:
    answer = decision.answer
    return decision.status == "answered" and answer is not None and answer.kind == "tied"


def _has_class_gate(conditions: tuple) -> bool:
    for condition in conditions:
        for leaf in _leaves(condition):
            if isinstance(leaf, Known):
                if leaf.known == _CLASS_FACET:
                    return True
            elif getattr(leaf, "facet", None) == _CLASS_FACET:
                return True
    return False


def _class_sentence(decision: Decision, spec: Spec | None, conditions: tuple) -> str:
    if spec is None or _has_class_gate(conditions):
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


def _hardware_item(spec: Spec | None, conditions: tuple) -> str:
    gates = _hardware_gates(conditions)
    if not gates and _own_hardware_without_fit(spec):
        return _HARDWARE_NOT_REQUIRED
    if len(gates) != 1:
        # Several gates are already listed under "Requirements applied".
        return _HARDWARE
    gate = gates[0]
    sentence = gate + _HARDWARE_TAIL
    if len(sentence.encode("utf-8")) <= MUST_MENTION_ITEM_BYTES:
        return sentence
    room = MUST_MENTION_ITEM_BYTES - len(_HARDWARE_TAIL.encode("utf-8"))
    return _clip_to(gate, room) + _HARDWARE_TAIL


def _own_hardware_without_fit(spec: Spec | None) -> bool:
    """Own hardware was asked for, but neither a gate nor the estate names a device."""
    if spec is None or spec.access is None or spec.access.kind != "own_hardware":
        return False
    return spec.estate is None or not spec.estate.devices


def _hardware_gates(conditions: tuple) -> list[str]:
    """Profile rules and ``where`` conditions that name fits_hardware."""
    gates: list[str] = []
    for condition in conditions:
        rendered = render_condition(condition)
        if HARDWARE_FIT in rendered:
            gates.append(rendered)
    return gates


def _hardware(decision: Decision, spec: Spec | None, conditions: tuple = ()) -> bool:
    reading = decision.reading
    if reading is not None and HARDWARE_FIT in reading.estimates:
        return True
    if spec is not None and spec.access is not None and spec.access.kind == "own_hardware":
        return True
    if spec is None:
        return False
    if _hardware_gates(conditions or tuple(spec.where)):
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
