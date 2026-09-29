"""Render ``breakdown.json`` as a Markdown draft post and SVG charts (MODEL-224).

The renderer adds no fact. Every number it prints comes from a ``Cited`` in
the breakdown and carries a footnote naming the fact ID behind it: the
snapshot record, or the computation with its inputs and decision.
``untraced_numbers`` checks the output for any number without one, and
``render`` refuses to return a post that has one, or that uses a refused word.
"""

from __future__ import annotations

import math
import re
from collections.abc import Iterable, Mapping, Sequence
from html import escape
from typing import Any

from release_blog import wording
from release_blog.model import Breakdown, Cited
from release_blog.tone import refused_words

SNAPSHOT_FILE = "https://modelspec.dev/api/decision/snapshots/{id}.json.gz"
STANDARD_URL = "https://modelspec.dev/blog/standard/"
NEUTRALITY_URL = "https://modelspec.dev/legal/neutrality/"
TIER_ORDER = ("best", "balanced", "budget", "fastest", "private")
BAND_WORDS = {"best": "leading band", "rest": "ranked, outside the leading band",
              "thin": "thin evidence", None: "not ranked"}
MEASURED_BY = {
    "benchmark_author": "the benchmark's authors",
    "independent_evaluator": "an independent evaluator",
    "modelspec": "ModelSpec",
    "outcome_protocol": "ModelSpec's outcome protocol",
}
COMPUTED = {
    "capability.estimate": "the capability model's estimate, fitted from every admitted "
                           "benchmark reading",
    "decision.p_best": "P(best) from the decision",
    "decision.top3_stability": "top-three stability from the decision",
    "decision.model_rank": "the model's place among the decision's ranked models",
    "decision.bands.best": "the number of models in the decision's best band",
    "decision.ranked_models": "the number of models the decision ranked",
    "decision.compare": "the comparison of the two decisions",
    "offering.cost_per_task": "list price for one task: (input price × input tokens + "
                              "output price × output tokens) ÷ 1,000,000",
    "plan.monthly": "the plan's annual price ÷ 12",
    "plan.break_even_tasks_per_month": "the plan's monthly price ÷ one task's pay-per-use cost",
    "difference": "the independent reading minus the lab's figure",
    "snapshot.held_back": "the count of this model's records the snapshot held back, by "
                          "reason (`content.held_back`)",
}


# ── footnotes and numbers ──────────────────────────────────────────────────


class Footnotes:
    """One footnote per fact, numbered in order of first use."""

    def __init__(self, breakdown: Breakdown):
        self.b = breakdown
        self.keys: dict[str, int] = {}
        self.notes: list[str] = []

    def _key(self, cited: Cited) -> str:
        return "|".join([cited.record_id or "", cited.computed or "", cited.decision_id or "",
                         ",".join(cited.records), repr(cited.value), repr(cited.low),
                         repr(cited.high)])

    def _text(self, cited: Cited) -> str:
        after = self.b.generated_from.after.snapshot_id
        urls = ", ".join(f"<{self.b.sources[s]}>" for s in cited.source_ids)
        if cited.record_id is not None:
            where = f" Source: {urls}." if urls else ""
            return (f"Fact `{cited.record_id}` in snapshot `{after}`, verified "
                    f"{cited.read_date.isoformat()}.{where}")
        parts = [f"Computed: {COMPUTED.get(cited.computed or '', cited.computed)} "
                 f"(`{cited.computed}`), from snapshot `{after}`."]
        if cited.records:
            parts.append("Records: " + ", ".join(f"`{r}`" for r in cited.records) + ".")
        if cited.decision_id:
            parts.append(f"Decision `{cited.decision_id}`.")
        if urls:
            parts.append(f"Sources: {urls}.")
        return " ".join(parts)

    def ref(self, cited: Cited) -> str:
        key = self._key(cited)
        if key not in self.keys:
            self.keys[key] = len(self.notes) + 1
            self.notes.append(self._text(cited))
        return f"[^{self.keys[key]}]"

    def note(self, text: str) -> str:
        """A footnote that explains a spec input, such as a task size."""
        if text not in self.keys:
            self.keys[text] = len(self.notes) + 1
            self.notes.append(text)
        return f"[^{self.keys[text]}]"

    def block(self) -> str:
        return "\n".join(f"[^{i}]: {text}" for i, text in enumerate(self.notes, 1))


def _number(value: float, unit: str | None) -> str:
    if unit == "USD":
        text = f"{value:,.4f}".rstrip("0")
        whole, _, cents = text.partition(".")
        return f"${whole}.{cents.ljust(2, '0')}"
    if unit == "USD per month":
        return f"${value:,.2f}"
    if unit == "usd_per_1m_tokens":
        return f"${value:,.2f}"
    if unit == "probability":
        return f"{value * 100:.1f}%"
    if unit == "percent":
        return f"{value:g}%"
    if unit == "capability estimate":
        return f"{value:.2f}"
    if unit in ("models", "place", "items", "records"):
        return f"{value:,.0f}"
    if unit == "tasks per month":
        return f"{value:,.1f}"
    return f"{value:g}"


UNIT_WORDS = {"usd_per_1m_tokens": "per million tokens", "tokens_per_second": "tokens a second",
              "ms": "ms", "seconds": "s"}


def _fmt(notes: Footnotes, cited: Cited | None, *, unit_words: bool = False) -> str:
    if cited is None:
        return "unknown"
    text = _number(cited.value, cited.unit) + notes.ref(cited)
    if unit_words and cited.unit in UNIT_WORDS:
        text += " " + UNIT_WORDS[cited.unit]
    return text


def _estimate(notes: Footnotes, cited: Cited | None) -> str:
    if cited is None:
        return "unknown"
    ref = notes.ref(cited)
    return (f"{cited.value:.2f}{ref} (interval {cited.low:.2f}{ref} "
            f"to {cited.high:.2f}{ref})")


def _code(text: str) -> str:
    return f"`{text}`"


def _cell(text: str | None) -> str:
    return (text or "—").replace("|", "\\|").replace("\n", " ")


def _table(head: Sequence[str], rows: Iterable[Sequence[str]]) -> str:
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    lines += ["| " + " | ".join(_cell(c) for c in row) + " |" for row in rows]
    return "\n".join(lines)


# ── the guard ──────────────────────────────────────────────────────────────

_DEFINITION = re.compile(r"^\[\^\d+\]:.*$", re.MULTILINE)
_CODE = re.compile(r"`[^`]*`")
_LINK_TARGET = re.compile(r"\]\([^)]*\)|<https?://[^>]*>|https?://\S+")
_ISO_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_NUMBER = re.compile(r"(?<![\w.^])[$]?\d[\d,]*(?:\.\d+)?%?")


def untraced_numbers(markdown: str, allowed: Iterable[str] = ()) -> list[str]:
    """Every number in ``markdown`` not immediately followed by a footnote marker.

    Footnote definitions, code spans (IDs), link targets, ISO dates (read and
    due dates) and the ``allowed`` strings (the model's name) are skipped.
    """
    text = _DEFINITION.sub("", markdown)
    text = _CODE.sub("", text)
    text = _LINK_TARGET.sub("", text)
    text = _ISO_DATE.sub("", text)
    for phrase in sorted(allowed, key=len, reverse=True):
        text = text.replace(phrase, "")
    return [m.group(0) for m in _NUMBER.finditer(text)
            if not text.startswith("[^", m.end())]


# ── charts ────────────────────────────────────────────────────────────────

_LIGHT = {"bg": "#fcfcfb", "ink": "#0b0b0b", "ink2": "#52514e", "rule": "#e4e3dd",
          "s1": "#2a78d6", "s2": "#eb6834", "muted": "#9a9993"}
_DARK = {"bg": "#1a1a19", "ink": "#ffffff", "ink2": "#c3c2b7", "rule": "#3a3936",
         "s1": "#3987e5", "s2": "#d95926", "muted": "#77766f"}


def _rules(c: Mapping[str, str]) -> str:
    return (f".bg{{fill:{c['bg']}}}.f-s1{{fill:{c['s1']}}}.f-s2{{fill:{c['s2']}}}"
            f".f-muted{{fill:{c['muted']}}}.k-s1{{stroke:{c['s1']}}}"
            f".k-muted{{stroke:{c['muted']}}}.k-rule{{stroke:{c['rule']}}}"
            f".ring{{stroke:{c['bg']}}}text{{fill:{c['ink2']}}}.t,.v{{fill:{c['ink']}}}"
            f"text.m{{fill:{c['muted']}}}")


_STYLE = "\n".join([
    "<style>",
    "text{font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Arial,sans-serif;"
    "font-size:12px}.t{font-size:14px;font-weight:600}",
    _rules(_LIGHT),
    "@media (prefers-color-scheme: dark){" + _rules(_DARK) + "}",
    "</style>",
])


def _svg(width: int, height: int, title: str, body: list[str]) -> str:
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">',
        _STYLE,
        f'<rect class="bg" width="{width}" height="{height}"/>',
        f'<text class="t" x="16" y="24">{escape(title)}</text>',
        *body, "</svg>", ""])


def _bar(x: float, y: float, w: float, h: float, fill: str, tip: str) -> str:
    w = max(w, 2.0)
    return (f'<rect class="f-{fill}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" '
            f'height="{h:.1f}" rx="4"><title>{escape(tip)}</title></rect>')


def claims_chart(b: Breakdown) -> str | None:
    rows = b.claims_vs_evidence.claims
    if not rows:
        return None
    values = [r.claim.value for r in rows] + [x.value.value for r in rows for x in r.readings]
    units = {r.claim.unit for r in rows}
    top = max(values) if units == {"percent"} else max(values) * 1.1
    top = 100.0 if units == {"percent"} else top
    left, width, bar = 200, 420, 14
    y, body = 64, [
        f'<rect class="f-s2" x="{left}" y="38" width="10" height="10" rx="2"/>'
        f'<text x="{left + 16}" y="47">Lab-reported</text>',
        f'<rect class="f-s1" x="{left + 120}" y="38" width="10" height="10" rx="2"/>'
        f'<text x="{left + 136}" y="47">Independent reading</text>',
    ]
    for row in rows:
        body.append(f'<text class="v" x="16" y="{y + 11}">{escape(row.benchmark)}</text>')
        label = f"{_number(row.claim.value, row.claim.unit)} lab-reported"
        body.append(_bar(left, y, width * row.claim.value / top, bar, "s2", label))
        body.append(f'<text x="{left + width * row.claim.value / top + 6:.1f}" '
                    f'y="{y + 11}">{escape(_number(row.claim.value, row.claim.unit))}</text>')
        y += bar + 2
        if not row.readings:
            body.append(f'<text class="m" x="{left}" y="{y + 11}">no independent reading '
                        "yet</text>")
            y += bar + 2
        for reading in row.readings:
            v = reading.value
            body.append(_bar(left, y, width * v.value / top, bar, "s1",
                             f"{_number(v.value, v.unit)} {reading.measured_by}"))
            body.append(f'<text x="{left + width * v.value / top + 6:.1f}" y="{y + 11}">'
                        f"{escape(_number(v.value, v.unit))}</text>")
            y += bar + 2
        y += 12
    return _svg(680, y + 8, "Lab-reported and independent readings", body)


def standing_chart(b: Breakdown) -> str | None:
    if not b.standing:
        return None
    rows: list[tuple[str, str, Cited, bool]] = []
    for s in b.standing:
        seen = {b.model.id}
        rows.append((s.domain.name, b.model.id, s.estimate, True))
        for leader in s.leaders:
            if leader.model in seen or leader.estimate is None:
                continue
            seen.add(leader.model)
            rows.append((s.domain.name, leader.model, leader.estimate, False))
    lo = min(r[2].low or r[2].value for r in rows)
    hi = max(r[2].high or r[2].value for r in rows)
    pad = (hi - lo) * 0.05 or 1.0
    lo, hi = lo - pad, hi + pad
    left, width = 260, 380

    def x(v: float) -> float:
        return left + width * (v - lo) / (hi - lo)

    body, y, domain = [], 44, None
    for name, model, est, own in rows:
        if name != domain:
            domain = name
            y += 14
            body.append(f'<text class="t" x="16" y="{y + 10}">{escape(name)}</text>')
            y += 30
        colour = "s1" if own else "muted"
        tip = (f"{model}: {est.value:.2f} (interval {est.low:.2f} to {est.high:.2f})")
        body.append(f'<text class="{"v" if own else ""}" x="24" y="{y + 4}">'
                    f"{escape(model)}</text>")
        body.append(f'<line x1="{x(est.low or est.value):.1f}" y1="{y}" '
                    f'x2="{x(est.high or est.value):.1f}" y2="{y}" class="k-{colour}" '
                    f'stroke-width="2" stroke-linecap="round"><title>{escape(tip)}</title></line>')
        body.append(f'<circle class="f-{colour} ring" cx="{x(est.value):.1f}" cy="{y}" r="5" '
                    f'stroke-width="2"><title>{escape(tip)}</title>'
                    "</circle>")
        y += 22
    axis = [f'<line x1="{left}" y1="{y}" x2="{left + width}" y2="{y}" class="k-rule"/>']
    for tick in range(math.ceil(lo), math.floor(hi) + 1):
        axis.append(f'<line x1="{x(tick):.1f}" y1="44" x2="{x(tick):.1f}" y2="{y}" '
                    'class="k-rule"/>')
        axis.append(f'<text x="{x(tick):.1f}" y="{y + 16}" text-anchor="middle">{tick}</text>')
    axis.append(f'<text x="{left + width / 2:.1f}" y="{y + 32}" text-anchor="middle">'
                "Capability estimate (latent scale); bars are eighty-percent intervals</text>")
    return _svg(680, y + 44, "Capability estimates, with intervals", [*axis, *body])


def cost_chart(b: Breakdown) -> str | None:
    rows = [o for o in b.cost.offerings
            if o.task.basis == "contract_default" and o.cost_per_task is not None]
    if not rows:
        return None
    top = max(o.cost_per_task.value for o in rows) * 1.15  # type: ignore[union-attr]
    left, width, y, body = 300, 300, 44, []
    for o in rows:
        v = o.cost_per_task.value  # type: ignore[union-attr]
        label = f"{o.provider} · {o.region} · {o.tier}"
        body.append(f'<text class="v" x="16" y="{y + 11}">{escape(label)}</text>')
        tip = f"{o.offering}: {_number(v, 'USD')}"
        body.append(_bar(left, y, width * v / top, 14, "s1", tip))
        body.append(f'<text x="{left + width * v / top + 6:.1f}" y="{y + 11}">'
                    f"{escape(_number(v, 'USD'))}</text>")
        y += 24
    return _svg(680, y + 8, "Cost per task, list price", body)


def charts(b: Breakdown) -> dict[str, str]:
    """``{file name: SVG}`` for every chart the breakdown supports."""
    made = {"claims.svg": claims_chart(b), "standing.svg": standing_chart(b),
            "cost.svg": cost_chart(b)}
    return {name: svg for name, svg in made.items() if svg is not None}


# ── the post ──────────────────────────────────────────────────────────────


def _setup(setup: Any) -> str:
    parts = [f"version {setup.version}" if setup.version else None,
             f"harness {setup.harness}" if setup.harness else None,
             f"effort {setup.effort}" if setup.effort else None,
             f"sub-category {setup.subcategory}" if setup.subcategory else None]
    text = "; ".join(p for p in parts if p) or "not stated"
    return _code(text) if any(ch.isdigit() for ch in text) else text


def _claims(b: Breakdown, n: Footnotes, chart: bool) -> list[str]:
    out = ["## Claims and evidence"]
    rows = b.claims_vs_evidence.claims
    if not rows:
        out.append("ModelSpec holds no lab-reported figure for this model that has passed "
                   "the second key.")
    else:
        out.append("Lab-reported figures are quoted from the lab's own page. Independent "
                   "readings are shown beside them, and a difference is given only for a "
                   "like-for-like setup.")
        table = []
        for row in rows:
            lab = _fmt(n, row.claim)
            if not row.readings:
                table.append([_code(row.benchmark), lab, "none yet", "—", _setup(row.setup),
                              wording.NO_READING])
            for r in row.readings:
                sentence = wording.difference(r.comparability, differs_in=r.differs_in)
                if r.difference is not None and r.difference.value != 0:
                    size = _number(abs(r.difference.value), r.difference.unit).rstrip("%")
                    sentence = wording.difference(
                        "same_setup", size=size + n.ref(r.difference),
                        direction="higher" if r.difference.value > 0 else "lower",
                        unit=r.difference.unit)
                elif r.difference is not None:
                    sentence = wording.difference("same_setup") + n.ref(r.difference)
                table.append([_code(row.benchmark), lab, _fmt(n, r.value),
                              MEASURED_BY.get(r.measured_by, r.measured_by),
                              _setup(r.setup), sentence])
        out.append(_table(["Benchmark", "Lab-reported", "Independent reading", "Measured by",
                           "Setup", "Comparison"], table))
        notes = [f"- {_code(row.benchmark)}, lab figure: {row.limitations}" for row in rows
                 if row.limitations and not any(ch.isdigit() for ch in row.limitations)]
        if notes:
            out.append("Limitations the records state, verbatim:\n\n" + "\n".join(notes))
        if chart:
            out.append("![Lab-reported and independent readings](charts/claims.svg)")
    out.append("### Not in the announcement")
    unreported = b.claims_vs_evidence.unreported
    if unreported:
        out.append(_table(["Benchmark", "Independent reading", "Measured by", "Setup"], [
            [_code(u.benchmark), _fmt(n, u.reading), MEASURED_BY.get(u.measured_by,
                                                                     u.measured_by),
             _setup(u.setup)] for u in unreported]))
    else:
        out.append("No independent reading in this model's estimated domains is missing "
                   "from the lab's figures.")
    return out


def _standing(b: Breakdown, n: Footnotes, chart: bool) -> list[str]:
    out = ["## Where it lands"]
    if not b.standing:
        out.append("The model has no capability estimate in any domain yet.")
        return out
    out.append("Each estimate comes from ModelSpec's capability model, fitted from every "
               "admitted benchmark reading, never from one benchmark. Intervals are "
               "eighty-percent intervals. P(best) is the share of draws from the fitted "
               "model in which a model scores highest in that domain: a statement about "
               "the evidence, not a forecast.")
    for s in b.standing:
        others = rank = ranked = None
        if s.band == "best" and s.band_size.value > 1:
            others = f"{s.band_size.value - 1:,.0f}" + n.ref(s.band_size)
        if s.band in ("rest", "thin"):
            # Footnotes number in reading order: the thin sentence names the
            # ranked count before the place, the rest sentence the other way.
            def place() -> str:
                return "unknown" if s.rank is None else _fmt(n, s.rank)

            if s.band == "thin":
                ranked, rank = _fmt(n, s.ranked_models), place()
            else:
                rank = place()
                ranked = _fmt(n, s.ranked_models)
        name = s.domain.name[:1].lower() + s.domain.name[1:]
        sentence = wording.standing(domain=name, band=s.band, others=others, rank=rank,
                                    ranked=ranked, single=s.band_size.value == 2)
        detail = f"Its estimate is {_estimate(n, s.estimate)}"
        if s.p_best is not None:
            detail += f", with P(best) {_fmt(n, s.p_best)}"
        if s.top3_stability is not None:
            detail += f" and top-three stability {_fmt(n, s.top3_stability)}"
        out.append(f"**{s.domain.name}.** {sentence} {detail}. It rests on "
                   f"{', '.join(_code(d.benchmark) for d in s.drivers) or 'no named record'} "
                   f"(decision {_code(s.decision)}).")
        out.append(_table(["Leading-band model", "Estimate", "P(best)"], [
            [_code(leader.model) + (" (this model)" if leader.model == b.model.id else ""),
             _estimate(n, leader.estimate), _fmt(n, leader.p_best)]
            for leader in s.leaders]))
    if chart:
        out.append("![Capability estimates, with intervals](charts/standing.svg)")
    out.append("### Decision templates it changes")
    tc = b.template_changes
    out.append(wording.template_intro(tc.unavailable, bool(tc.changes)))
    if tc.changes:
        ordered = sorted(tc.changes, key=lambda c: (
            TIER_ORDER.index(c.template.tier) if c.template.tier in TIER_ORDER else 99,
            c.template.category, c.template.id))
        out.append(_table(["Template", "Tier", "Model's band before", "Model's band after",
                           "Left the leading band"], [
            [f"{c.template.name} ({_code(c.template.id)})", c.template.tier,
             BAND_WORDS[c.band_before], BAND_WORDS[c.band_after],
             ", ".join(_code(m) for m in c.displaced) or "none"]
            for c in ordered]))
    return out


def _cost(b: Breakdown, n: Footnotes, chart: bool) -> list[str]:
    out = ["## Cost and access", "### Cost per task"]
    rows = b.cost.offerings
    if not rows:
        out.append("ModelSpec holds no priced offering of this model.")
    for basis in dict.fromkeys(o.task.basis for o in rows):
        group = [o for o in rows if o.task.basis == basis]
        task = group[0].task
        why = ("the decision contract's default task (`DEFAULT_TASK_TOKENS`)"
               if basis == "contract_default" else f"the task size template `{basis}` sets")
        ref = n.note(f"Task size: {why}.")
        out.append(f"At a task of {task.input:,}{ref} input tokens and "
                   f"{task.output:,}{ref} output tokens:")
        out.append(_table(["Offering", "Input price", "Output price", "Cost per task"], [
            [_code(o.offering), _fmt(n, o.price_input, unit_words=True),
             _fmt(n, o.price_output, unit_words=True), _fmt(n, o.cost_per_task)]
            for o in group]))
    if chart and rows:
        out.append("![Cost per task, list price](charts/cost.svg)")
    out.append("### Plans")
    covering = [p for p in b.cost.plans if p.covers is True]
    unknown = [p for p in b.cost.plans if p.covers == "unknown"]
    not_covering = [p for p in b.cost.plans if p.covers is False]
    if covering:
        out.append("Plans whose own pages cover this model. The break-even is how many "
                   "tasks a month make the plan cheaper than paying per use, for a coding "
                   "tool; it is blank when the plan reaches the model directly rather than "
                   "through a pay-per-use offering.")
        out.append(_table(["Plan", "Monthly price", "Break-even (tasks a month)",
                           "Coverage statement"], [
            [f"{p.plan['name']} ({_code(p.plan['id'])})", _fmt(n, p.monthly),
             "—" if p.break_even is None else _fmt(n, p.break_even),
             _coverage(n, p)]
            for p in covering]))
    if unknown:
        out.append("Coverage not yet verified, so these are neither counted as covering "
                   "nor as not covering: " + ", ".join(_code(p.plan["id"]) for p in unknown)
                   + ".")
    if not_covering:
        out.append("Verified not to cover this model: "
                   + ", ".join(_code(p.plan["id"]) for p in not_covering) + ".")
    if not b.cost.plans:
        out.append("ModelSpec tracks no subscription plan in this snapshot.")
    out.append("Links to providers and plans go to their own pages. No link carries a "
               "referral, affiliate or tracking parameter.")
    return out


def _coverage(n: Footnotes, plan: Any) -> str:
    """How the plan covers the model; its page's own words go in a footnote."""
    text = (plan.rule or "").replace("offering.subscription.models_covered",
                                     "`offering.subscription.models_covered`")
    if plan.quote and plan.quote_record:
        quote = " ".join(plan.quote.split()).replace("`", "'")
        text += n.note(f"Coverage statement, verbatim from fact `{plan.quote_record}`: "
                       f"`{quote}`")
    return text


def _hardware(b: Breakdown) -> list[str]:
    out = ["## Hardware fit"]
    hw = b.hardware
    if hw is None:
        out.append("The model's weights are not published as open weights in this snapshot, "
                   "so there is no hardware section.")
        return out
    if hw.fits:
        out.append("Verified to fit: " + ", ".join(_code(d) for d in hw.fits)
                   + f" (fact {_code(hw.fits_record or '')}).")
    else:
        out.append("No verified hardware fit yet.")
    if hw.indeterminate:
        out.append("Fit not yet determinable on: " + ", ".join(_code(d) for d in hw.indeterminate)
                   + ".")
    out.append("Predicted speeds are not verified facts, so they are not shown.")
    return out


def _gaps(b: Breakdown, n: Footnotes) -> list[str]:
    g = b.not_yet_measured
    out = ["## Not measured yet"]
    held = None
    if g.held_back:
        held = ", ".join(f"{reason.replace('_', ' ')}: {_fmt(n, count)}"
                         for reason, count in g.held_back.items())
    items = [wording.held_back(g.held_back, held)]
    if g.claims_without_reading:
        items.append("Lab figures with no independent reading yet: "
                     + ", ".join(_code(x) for x in g.claims_without_reading) + ".")
    if g.domains_without_estimate:
        items.append("Domains with no estimate yet: "
                     + ", ".join(_code(x) for x in g.domains_without_estimate) + ".")
    if g.unknown_facets:
        items.append("Guaranteed facts still unknown: " + ", ".join(
            f"{_code(u.facet)} ({', '.join(_code(s) for s in u.subjects)})"
            for u in g.unknown_facets) + ".")
    else:
        items.append("Every fact ModelSpec guarantees for this model is known or verified "
                     "as not disclosed.")
    unmeasured = [s.offering for s in g.speed
                  if s.time_to_first_token == "unknown" and s.throughput == "unknown"]
    if unmeasured:
        items.append("Speed not yet measured under method `speed-v1` for: "
                     + ", ".join(_code(x) for x in unmeasured) + ".")
    measured = [s for s in g.speed if s.offering not in unmeasured]
    out.append("\n".join(f"- {item}" for item in items))
    if measured:
        out.append(_table(["Offering", "Time to first token", "Throughput"], [
            [_code(s.offering),
             "unknown" if s.time_to_first_token == "unknown"
             else _fmt(n, s.time_to_first_token, unit_words=True),
             "unknown" if s.throughput == "unknown" else _fmt(n, s.throughput, unit_words=True)]
            for s in measured]))
    out.append("### Re-check schedule")
    words = {1: "One day", 7: "Seven days", 30: "Thirty days"}
    out.append(f"First published {b.recheck.first_published.isoformat()}. ModelSpec looks "
               "again on these dates. A re-check that changes anything becomes a new, dated "
               "revision that shows what changed; one that changes nothing adds no revision.")
    out.append(_table(["After", "Due"], [
        [words.get(row["day"], "Later"), row["due"]] for row in b.recheck.schedule]))
    return out


def _provenance(b: Breakdown) -> list[str]:
    g = b.generated_from
    after = g.after
    out = ["## Sources and decisions",
           f"- Snapshot: {_code(after.snapshot_id)}, as of "
           f"{after.as_of.isoformat() if after.as_of else 'unknown'}, content hash "
           f"{_code(after.content_hash)}, signed with Ed25519 key {_code(after.key_id)}. "
           f"File: <{SNAPSHOT_FILE.format(id=after.snapshot_id)}>."]
    if g.before is not None:
        out[-1] += (f"\n- Compared with snapshot {_code(g.before.snapshot_id)}, as of "
                    f"{g.before.as_of.isoformat() if g.before.as_of else 'unknown'}, "
                    f"the last one without this model. File: "
                    f"<{SNAPSHOT_FILE.format(id=g.before.snapshot_id)}>.")
    out[-1] += (f"\n- Accuracy: the {_code(g.accuracy.profile)} profile passed for "
                f"{_code(g.accuracy.snapshot)}.\n- Generator: {_code(g.generator.package)} "
                f"{_code(g.generator.version)}. Every number in this post is in "
                "`breakdown.json` beside it, with its record or computation.")
    out.append("Every decision this post relies on. Re-running a spec against its snapshot "
               "gives the same decision ID.")
    out.append(_table(["Purpose", "Decision", "Snapshot", "Spec hash"], [
        [_code(d.purpose), _code(d.decision_id), _code(d.snapshot_id), _code(d.spec_hash)]
        for d in b.decisions]))
    out.append("Sources cited:\n\n" + "\n".join(
        f"- {_code(sid)}: <{url}>" for sid, url in sorted(b.sources.items())))
    out.append(f"{b.disclosures.neutrality} See <{NEUTRALITY_URL}>. This post follows the "
               f"release breakdown standard: <{STANDARD_URL}>.")
    return out


def render(b: Breakdown) -> tuple[str, dict[str, str]]:
    """The Markdown draft and its charts, ``(post, {file name: svg})``."""
    n = Footnotes(b)
    made = charts(b)
    after = b.generated_from.after
    lead = [f"# {b.headline.text}",
            f"*Draft release breakdown of {b.model.name} ({_code(b.model.id)}), revision "
            f"{_code(str(b.revision))}. Every number comes from signed snapshot "
            f"{_code(after.snapshot_id)} and links to its fact. Not published: a draft "
            "never renders on the site until Jamie approves it.*"]
    if b.disclosures.supplier:
        lead.append(f"> **Disclosure.** {b.disclosures.supplier}")
    if b.disclosures.early_access:
        lead.append(f"> **Early access.** {b.disclosures.early_access}")
    body = [
        *lead,
        *_claims(b, n, "claims.svg" in made),
        *_standing(b, n, "standing.svg" in made),
        *_cost(b, n, "cost.svg" in made),
        *_hardware(b),
        *_gaps(b, n),
        *_provenance(b),
    ]
    if b.changes_since_r1:
        body.append("## Changes since the first revision\n\n" + "\n".join(
            f"- {_code(c['pointer'])}" for c in b.changes_since_r1))
    post = "\n\n".join(body) + "\n\n" + n.block() + "\n"
    # Names are labels, not figures: the model's own and the plans'.
    names = [b.model.name, *(p.plan["name"] for p in b.cost.plans)]
    stray = untraced_numbers(post, allowed=names)
    if stray:
        raise ValueError(f"numbers without a footnote in the post: {stray}")
    text = _DEFINITION.sub("", post)
    orphans = [i for i in range(1, len(n.notes) + 1) if f"[^{i}]" not in text]
    if orphans:
        raise ValueError(f"footnotes nothing in the post refers to: {orphans}")
    words = refused_words(post)
    if words:
        raise ValueError(f"refused words in the post: {words}")
    return post, made


def write(b: Breakdown, out: Any) -> Mapping[str, Any]:
    """Write ``post.md`` at ``out`` and its charts in ``charts/`` beside it."""
    from pathlib import Path

    out = Path(out)
    post, made = render(b)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(post, encoding="utf-8")
    written = {"post": str(out), "charts": []}
    if made:
        folder = out.parent / "charts"
        folder.mkdir(exist_ok=True)
        for name, svg in made.items():
            (folder / name).write_text(svg, encoding="utf-8")
            written["charts"].append(str(folder / name))
    return written
