"""From a fit to an answer: hard filters, output states, ordering, explanation.

Order of operations, and the reason for it:

1. **Hard filters first** (independent audit, Critical 3 and High 4). The task
   fixes the class (`api/classes.py`), then feasibility: image input, minimum
   context, open weights, a price cap, a device. A model that fails any of
   these is not a candidate. Nothing about a filter reaches the score: context
   length, capability tiers and type position are not evidence of success on
   the task, so they filter or they are shown beside the answer, never added.
2. **Score** each candidate: the posterior mean and sd of the use case's
   domain mix, from the fit.
3. **State** each candidate from its evidence, not from a coverage share of a
   fixed list:
   * `ranked` — at least one independent measurement whose primary tag is
     the use case's primary domain, and posterior sd at most `SD_RANKED`;
   * `provisional` — measured in the primary domain by any source (a
     provider's own launch numbers are enough), sd at most `SD_PROVISIONAL`:
     a dated provisional comparison;
   * `insufficient` — no measurement in the primary domain: an evidence gap,
     named, never a low score.
4. **Order** by posterior mean, publish the 80% interval, and mark the
   `leading_set`: every candidate whose chance of beating the leader is at
   least `LEADER_P`. No single winner is claimed when the evidence cannot
   separate the top.
"""

from __future__ import annotations

import math
from typing import Any

from research.ranking_v2.domains import USE_CASES, primary_domain
from research.ranking_v2.model import Fit, explain

#: Proposed state thresholds, in units of the latent scale (sd of g across
#: well-measured models = 1). Jamie's call, like the floors they replace.
SD_RANKED = 0.35
SD_PROVISIONAL = 0.75
LEADER_P = 0.20
Z80 = 1.2816


def phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def eligible(card: dict[str, Any], use_case: str, *, as_of: str | None = None,
             open_weights: bool | None = None, max_cost: float | None = None,
             min_context: int | None = None, fits: dict[str, set[str]] | None = None,
             hardware: str | None = None) -> tuple[bool, str | None]:
    """Hard filters. Returns (ok, reason_if_not)."""
    spec = USE_CASES[use_case]
    if card.get("rehost_of"):
        return False, "rehost"
    if card.get("class_id") not in spec["classes"]:
        return False, f"class:{card.get('class_id')}"
    if as_of and card.get("release") and card["release"][:10] > as_of:
        return False, "not_released"
    if "image_input" in spec.get("requires", ()) and not card.get("image_input"):
        return False, "no_image_input"
    need_ctx = min_context or spec.get("min_context")
    if need_ctx and (card.get("context_window") or 0) < need_ctx:
        return False, "context_below_minimum"
    if open_weights and not card.get("open_weights"):
        return False, "not_open_weights"
    if max_cost is not None and (card.get("cost_input") is None or card["cost_input"] > max_cost):
        return False, "price_unknown_or_above_cap"
    if hardware and (fits is None or hardware not in fits.get(card["model_id"], set())):
        return False, "does_not_fit_device"
    return True, None


def state_of(fit: Fit, model_id: str, use_case: str, sd: float) -> tuple[str, str]:
    mix = USE_CASES[use_case]["mix"]
    primary = primary_domain(use_case)
    mf = fit.models.get(model_id)
    rows = mf.rows if mf else []
    in_mix = [r for r in rows if set(r.item.tags) & set(mix)]
    # The item's *first* tag must be the primary domain: Arena WebDev counts
    # toward chat in the fit, but it cannot on its own make a model `ranked`
    # for chat, because what it primarily measures is coding.
    independent_primary = [r for r in in_mix if r.item.tags[0] == primary
                           and r.obs.source_kind in ("independent_evaluator", "benchmark_author")]
    in_primary = [r for r in in_mix if primary in r.item.tags]
    if not in_primary:
        have = sorted({d for r in rows for d in r.item.tags})
        return "insufficient", (f"no measurement in {primary}"
                                + (f"; measured only in {', '.join(have)}" if have else "; no measurement at all"))
    if independent_primary and sd <= SD_RANKED:
        return "ranked", "independent evidence in the primary domain"
    if sd <= SD_PROVISIONAL:
        why = ("no independent measurement in " + primary) if not independent_primary else "interval too wide"
        return "provisional", why
    return "insufficient", "interval too wide to place"


def rank(fit: Fit, cards: dict[str, dict], use_case: str, *, as_of: str | None = None,
         limit: int = 10, explain_top: int = 0, **filters) -> dict[str, Any]:
    mix = USE_CASES[use_case]["mix"]
    rows, gaps, filtered = [], [], {}
    for mid, card in cards.items():
        ok, why = eligible(card, use_case, as_of=as_of, **filters)
        if not ok:
            filtered[why] = filtered.get(why, 0) + 1
            continue
        if mid not in fit.models:
            gaps.append({"model_id": mid, "release": card.get("release"), "state": "insufficient",
                         "reason": "no usable measurement"})
            continue
        mean, sd = fit.score(mid, mix)
        state, reason = state_of(fit, mid, use_case, sd)
        row = {"model_id": mid, "name": card.get("name"), "release": card.get("release"),
               "mean": mean, "sd": sd, "lo80": mean - Z80 * sd, "hi80": mean + Z80 * sd,
               "state": state, "reason": reason, "n_obs": len(fit.models[mid].rows)}
        (rows if state != "insufficient" else gaps).append(row)
    rows.sort(key=lambda r: (-r["mean"], r["model_id"]))
    for i, r in enumerate(rows, 1):
        r["position"] = i
    if rows:
        lead = rows[0]
        for r in rows:
            gap = lead["mean"] - r["mean"]
            spread = math.sqrt(lead["sd"] ** 2 + r["sd"] ** 2) or 1e-9
            r["p_beats_leader"] = 1.0 - phi(gap / spread) if r is not lead else 0.5
            r["leading_set"] = r is lead or r["p_beats_leader"] >= LEADER_P
    for r in rows[:explain_top]:
        r["explanation"] = explain(fit, r["model_id"], mix, top=5)
    gaps.sort(key=lambda r: (r.get("release") or ""), reverse=True)
    return {"use_case": use_case, "mix": mix, "as_of": fit.as_of, "rows": rows[:limit],
            "placed": len(rows), "ranked": sum(r["state"] == "ranked" for r in rows),
            "provisional": sum(r["state"] == "provisional" for r in rows),
            "all_rows": rows, "gaps": gaps, "filtered": filtered}


def position_of(report: dict[str, Any], model_id: str) -> tuple[int | None, str]:
    for r in report["all_rows"]:
        if r["model_id"] == model_id:
            return r["position"], r["state"]
    for r in report["gaps"]:
        if r["model_id"] == model_id:
            return None, "insufficient"
    return None, "filtered"
