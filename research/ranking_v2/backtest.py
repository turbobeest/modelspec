"""Validation for ranking v2 (MODEL-129): the four gates, both data views.

    .venv/bin/python -m research.ranking_v2.backtest all          # everything
    .venv/bin/python -m research.ranking_v2.backtest heldout
    .venv/bin/python -m research.ranking_v2.backtest replay
    .venv/bin/python -m research.ranking_v2.backtest face
    .venv/bin/python -m research.ranking_v2.backtest truth [--report PATH]
    .venv/bin/python -m research.ranking_v2.backtest saturation

Two data views, as the ticket asks:

* `sourced` — evidence rows (after the MODEL-117 purge) plus the Arena dataset;
* `flat`    — the same, plus the undated flat `benchmarks.scores` blocks, with
  sibling copies quarantined.

Results land in `research/ranking_v2/results/` as JSON and Markdown. Every run
is deterministic: fixed seeds, fixed as-of date, committed Arena snapshot.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import math
import os
import statistics
import time
from pathlib import Path
from typing import Any

from research.ranking_v2 import baselines
from research.ranking_v2 import evidence as ev
from research.ranking_v2.domains import USE_CASES
from research.ranking_v2.model import Fit, fit as fit_v2, item_information, mask_cells
from research.ranking_v2.rank import position_of, rank

AS_OF = "2026-09-24"
VIEWS = ("sourced", "flat")
RESULTS = Path(__file__).resolve().parent / "results"
SEEDS = (1, 2, 3, 4, 5)
HOLDOUT = 0.15
#: A held-out cell is scored only if its item keeps this many training models.
MIN_TRAIN_MODELS = 5

#: 2026 flagships for the replay: each lab's headline releases, by card id.
FLAGSHIPS = (
    "anthropic/claude-opus-4-6", "anthropic/claude-sonnet-4-6", "google/gemini-3-1-pro-preview",
    "openai/gpt-5-4", "meta/muse-spark", "zhipu/glm-5-1", "anthropic/claude-opus-4-7",
    "moonshot/kimi-k2-6", "openai/gpt-5-5", "google/gemini-3-5-flash", "qwen/qwen3-7-max",
    "anthropic/claude-opus-4-8", "minimax/minimax-m3", "anthropic/claude-fable-5",
    "zhipu/glm-5-2", "anthropic/claude-sonnet-5", "xai/grok-4-5", "openai/gpt-5-6-sol",
    "moonshot/kimi-k3", "anthropic/claude-opus-5", "qwen/qwen3-8-max", "deepseek/deepseek-v4-pro",
    "xai/grok-4-6", "google/gemini-3-7-flash", "zhipu/glm-5-3", "anthropic/claude-fable-5-1",
    "google/gemini-3-8-flash", "openai/gpt-6-astra", "deepseek/deepseek-flash", "xai/grok-4-7",
    "anthropic/claude-opus-5-5", "openai/gpt-6-sol",
)
REPLAY_USE_CASES = ("coding", "reasoning", "chat")
V1_PROFILE = {"coding": "coding", "reasoning": "reasoning", "chat": "chat", "agentic": "agentic",
              "vision": "vision", "general": "general", "math": "math_competition",
              "rag_generator": "rag", "research_assistant": "research_assistant",
              "embedding": "embedding"}


# ── data ────────────────────────────────────────────────────────────────────


class Data:
    def __init__(self) -> None:
        cache = os.environ.get("RANKING_V2_CARD_CACHE")
        if cache and Path(cache).exists():
            self.cards = json.loads(Path(cache).read_text())
        else:
            self.cards = ev.load_cards()
            if cache:
                Path(cache).write_text(json.dumps(self.cards, default=str))
        self.by_id = {c["model_id"]: c for c in self.cards}
        self.pages = ev.load_pages()
        self.arena = ev.load_arena()
        self.quarantine = ev.quarantine_flat(self.cards)
        self._v1 = None

    def obs(self, as_of: str, view: str) -> ev.Build:
        return ev.observations(self.cards, self.pages, self.arena, as_of,
                               include_flat=(view == "flat"), quarantine=self.quarantine)

    # ── v1, faithfully: the repository's own scorer, fed the same dated data ──
    def v1_base(self):
        if self._v1 is None:
            from pipeline.ranking import build_candidates
            from schema.card import ModelCard
            from schema.graph import derive_graph
            root = ev.ROOT
            cards = [ModelCard.from_yaml_file(p) for p in sorted((root / "models").rglob("*.md"))
                     if p.name != "LICENSE.md"]
            from pipeline import hardware
            # The same derivation `pipeline/build.py` runs, so device fits exist.
            devices = hardware.load_devices(root)
            derived = derive_graph(cards, hardware.device_classes(devices))
            hardware.compute(derived, cards, devices)
            self._v1 = build_candidates(cards, derived)
        return self._v1

    def v1_candidates(self, as_of: str, view: str, purge: bool = True):
        out = []
        for c in self.v1_base():
            rc = self.by_id[c.model_id]
            if c.release_date and c.release_date[:10] > as_of:
                continue
            scores: dict[str, float] = {}
            verified: set[str] = set()
            if view == "flat" and (ev._iso(rc["flat_as_of"]) or "2024-01-01") <= as_of:
                scores = {k: v for k, v in rc["flat"].items() if not (purge and ev.excluded(k))}
            for e in rc["evidence"]:
                if e["evidence_date"] > as_of or (purge and ev.excluded(e["benchmark_id"], e["source_url"])):
                    continue
                scores[e["benchmark_id"]] = float(e["score"])
                verified.add(e["benchmark_id"])
            out.append(dataclasses.replace(c, benchmark_scores=scores, verified_benchmarks=verified))
        return out

    def fits(self) -> dict[str, set[str]]:
        return {c.model_id: set(c.fits) for c in self.v1_base()}


def v1_rank(data: Data, as_of: str, view: str, use_case: str, purge: bool = True,
            **kw) -> dict[str, Any]:
    from pipeline.ranking import rank_report
    return rank_report(data.v1_candidates(as_of, view, purge), V1_PROFILE[use_case], limit=10_000, **kw)


def v1_position(report: dict[str, Any], model_id: str) -> tuple[int | None, str]:
    for r in report["ranked"]:
        if r["model_id"] == model_id:
            return r["rank"], "ranked"
    for r in report["unranked"]:
        if r["model_id"] == model_id:
            return None, f"unranked ({r['benchmark_coverage']:.0%} coverage)"
    return None, "absent"


def _write(name: str, payload: Any, md: str | None = None) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / f"{name}.json").write_text(json.dumps(payload, indent=1, default=str, sort_keys=True) + "\n")
    if md is not None:
        (RESULTS / f"{name}.md").write_text(md.rstrip() + "\n")


# ── 1. held-out prediction ───────────────────────────────────────────────────


def heldout(data: Data) -> dict[str, Any]:
    methods = ("item_mean", "model_mean", "lowrank_k1", "lowrank_k2", "lowrank_k3",
               "v2_general_only", "v2")
    out: dict[str, Any] = {}
    for view in VIEWS:
        build = data.obs(AS_OF, view)
        # Hold out only cells of items that can be fitted at all.
        per_seed = []
        for seed in SEEDS:
            train, test = mask_cells(build.obs, HOLDOUT, seed)
            st = baselines.Standardiser(train)
            preds: dict[str, Any] = {
                "item_mean": baselines.item_mean(train),
                "model_mean": baselines.model_mean(train),
                "lowrank_k1": baselines.lowrank(train, 1),
                "lowrank_k2": baselines.lowrank(train, 2),
                "lowrank_k3": baselines.lowrank(train, 3),
            }
            f_g = fit_v2(train, data.pages, AS_OF, use_domains=False)
            f_full = fit_v2(train, data.pages, AS_OF)
            kinds = {(o.model_id, o.item): o.source_kind for o in test}
            preds["v2_general_only"] = lambda m, i, f=f_g: f.predict(m, i, kinds.get((m, i), ""))
            preds["v2"] = lambda m, i, f=f_full: f.predict(m, i, kinds.get((m, i), ""))
            cells = []
            n_train: dict[str, int] = {}
            for o in train:
                n_train[o.item] = n_train.get(o.item, 0) + 1
            for o in test:
                it = f_full.items.get(o.item)
                if it is None or it.status not in ("free", "borrowed") or o.model_id not in f_full.models:
                    continue
                if n_train.get(o.item, 0) < MIN_TRAIN_MODELS:
                    continue
                sd = st.raw_sd.get(o.item)
                if o.link == "pct":
                    # A 3-model item can have a 0.8 pp spread; errors are
                    # scaled by at least 5 pp so one such cell cannot dominate.
                    sd = max(sd or 0.0, 5.0)
                if o.link == "log":
                    y = math.log(o.value)
                else:
                    y = o.value
                row = {"item": o.item, "model": o.model_id, "link": o.link, "domain": it.tags[0],
                       "arena": o.live, "source_kind": o.source_kind}
                ok = True
                for mth in methods:
                    p = preds[mth](o.model_id, o.item)
                    if p is None:
                        ok = False
                        break
                    if o.link == "log":
                        p = math.log(max(p, 1e-6))
                        scale = math.sqrt(statistics.pvariance(
                            [math.log(x.value) for x in train if x.item == o.item]) or 1.0)
                    else:
                        scale = sd or 1.0
                    row[mth] = (p - y) / scale
                    if o.link == "pct":
                        row[mth + "_pp"] = p - y
                if ok:
                    # Calibration: is the observed value inside v2's 80%
                    # predictive interval?
                    psd = f_full.predict_sd(o.model_id, o.item)
                    if psd:
                        err = row["v2_pp"] if o.link == "pct" else row["v2"] * scale
                        row["v2_z"] = err / psd
                    cells.append(row)
            per_seed.append(cells)
        out[view] = {"seeds": list(SEEDS), "cells": per_seed,
                     "summary": _heldout_summary(per_seed, methods)}
    _write("heldout", {v: out[v]["summary"] for v in out}, _heldout_md(out, methods))
    return out


def _heldout_summary(per_seed: list[list[dict]], methods) -> dict[str, Any]:
    groups: dict[str, list] = {}
    for cells in per_seed:
        for c in cells:
            for g in ("all", "domain:" + c["domain"], "arena" if c["arena"] else "benchmarks"):
                groups.setdefault(g, []).append(c)
    summ = {}
    for g, cs in sorted(groups.items()):
        entry = {"cells": len(cs) / len(per_seed)}
        zs = [c["v2_z"] for c in cs if "v2_z" in c]
        if zs:
            entry["v2_cover80"] = sum(abs(z) <= 1.2816 for z in zs) / len(zs)
        for m in methods:
            errs = [c[m] for c in cs]
            entry[m] = math.sqrt(sum(e * e for e in errs) / len(errs))
            pp = [abs(c[m + "_pp"]) for c in cs if m + "_pp" in c]
            if pp:
                entry[m + "_mae_pp"] = sum(pp) / len(pp)
        summ[g] = entry
    return summ


def _heldout_md(out, methods) -> str:
    lines = [f"# Held-out prediction ({int(HOLDOUT * 100)}% of cells, {len(SEEDS)} seeds, as of {AS_OF})", "",
             "RMSE in units of each item's training standard deviation (lower is better).",
             "`pp` is the mean absolute error in percentage points on bounded-percentage cells.", ""]
    for view, res in out.items():
        s = res["summary"]
        lines += [f"## View: {view}", "",
                  "| cells | group | " + " | ".join(methods) + " | v2 MAE pp | item-mean MAE pp | v2 80% coverage |",
                  "|---:|---|" + "---:|" * len(methods) + "---:|---:|---:|"]
        for g, e in s.items():
            lines.append(f"| {e['cells']:.0f} | {g} | " + " | ".join(f"{e[m]:.3f}" for m in methods)
                         + f" | {e.get('v2_mae_pp', float('nan')):.2f} | {e.get('item_mean_mae_pp', float('nan')):.2f}"
                         + f" | {e.get('v2_cover80', float('nan')):.0%} |")
        lines.append("")
    return "\n".join(lines)


# ── 2. historical replay ─────────────────────────────────────────────────────


def replay(data: Data) -> dict[str, Any]:
    cutoffs: dict[str, str] = {}
    for mid in FLAGSHIPS:
        rel = data.by_id[mid]["release"][:10]
        cutoffs[mid] = min(ev.plus_days(rel, 7), AS_OF)
    today = {view: fit_v2(data.obs(AS_OF, view).obs, data.pages, AS_OF) for view in VIEWS}
    fits: dict[tuple[str, str], Fit] = {}
    rows = []
    for mid in FLAGSHIPS:
        t = cutoffs[mid]
        for view in VIEWS:
            if (t, view) not in fits:
                fits[(t, view)] = fit_v2(data.obs(t, view).obs, data.pages, t)
            f = fits[(t, view)]
            for uc in REPLAY_USE_CASES:
                rep = rank(f, data.by_id, uc, as_of=t)
                pos, state = position_of(rep, mid)
                # Where today's evidence puts it, among the same release-week pool.
                pool = {m for m in data.by_id
                        if (data.by_id[m]["release"] or "0000")[:10] <= t}
                rep_now = rank(today[view], {m: data.by_id[m] for m in pool}, uc, as_of=AS_OF)
                pos_now, state_now = position_of(rep_now, mid)
                v1 = v1_rank(data, t, view, uc)
                v1_pos, v1_state = v1_position(v1, mid)
                rows.append({"model_id": mid, "cutoff": t, "view": view, "use_case": uc,
                             "v2_position": pos, "v2_state": state, "v2_placed": rep["placed"],
                             "v2_today_position": pos_now, "v2_today_state": state_now,
                             "v1_position": v1_pos, "v1_state": v1_state,
                             "v1_ranked": v1["ranked_count"]})
            print("replay", mid, t, view, flush=True)
    _write("replay", rows, _replay_md(rows))
    return {"rows": rows}


def _replay_md(rows: list[dict]) -> str:
    lines = ["# Historical replay: each 2026 flagship at release + 7 days", "",
             "Only evidence dated on or before the cutoff; Arena read from the newest snapshot on or",
             "before it. `today` is the flagship's position among the same release-week pool under",
             "today's evidence. v1 is `pipeline.ranking.rank_report` at the CLI floor, fed the",
             "same dated, purged data.", ""]
    for view in VIEWS:
        vr = [r for r in rows if r["view"] == view]
        lines += [f"## View: {view}", ""]
        for uc in REPLAY_USE_CASES:
            ur = [r for r in vr if r["use_case"] == uc]
            placed = [r for r in ur if r["v2_position"] is not None]
            ranked = [r for r in ur if r["v2_state"] == "ranked"]
            v1r = [r for r in ur if r["v1_position"] is not None]
            # Agreement with today's evidence means something only when today
            # has had time to add evidence: flagships 30+ days before the as-of.
            old = [r for r in placed if r["v2_today_position"] is not None
                   and ev.days_between(r["cutoff"], AS_OF) >= 30]
            errs = [abs(r["v2_position"] - r["v2_today_position"]) for r in old]
            within3 = sum(e <= 3 for e in errs)
            lines.append(f"- **{uc}**: v2 placed {len(placed)}/{len(ur)} ({len(ranked)} ranked, "
                         f"{len(placed) - len(ranked)} provisional); v1 ranked {len(v1r)}/{len(ur)}. "
                         f"For the {len(old)} placed flagships with 30+ days of later evidence, median "
                         f"|release-week position − today's position| = "
                         f"{statistics.median(errs) if errs else float('nan'):.1f}, "
                         f"{within3}/{len(old)} within 3 places.")
        lines += ["", "| flagship | cutoff | use case | v2 at +7d | v2 today | v1 at +7d |",
                  "|---|---|---|---|---|---|"]
        for r in vr:
            v2 = f"#{r['v2_position']} of {r['v2_placed']} ({r['v2_state']})" if r["v2_position"] else r["v2_state"]
            now = f"#{r['v2_today_position']} ({r['v2_today_state']})" if r["v2_today_position"] else r["v2_today_state"]
            v1 = f"#{r['v1_position']} of {r['v1_ranked']}" if r["v1_position"] else r["v1_state"]
            lines.append(f"| {r['model_id']} | {r['cutoff']} | {r['use_case']} | {v2} | {now} | {v1} |")
        lines.append("")
    return "\n".join(lines)


# ── 3. face validity ─────────────────────────────────────────────────────────

FACE_USE_CASES = ("coding", "reasoning", "chat", "agentic", "vision")


def face(data: Data) -> dict[str, Any]:
    out: dict[str, Any] = {}
    md = [f"# Face validity: top 10 as of {AS_OF}", ""]
    for view in VIEWS:
        build = data.obs(AS_OF, view)
        t0 = time.time()
        f = fit_v2(build.obs, data.pages, AS_OF)
        fit_s = time.time() - t0
        gs = [mf.value("g") for mf in f.models.values() if len(mf.rows) >= 3]
        g_sd = statistics.pstdev(gs) if len(gs) > 1 else float("nan")
        md += [f"## View: {view}", "",
               f"{ev.summarise(build.obs)}", "",
               f"Scale: sd of g over the {len(gs)} models with 3+ observations is {g_sd:.2f} "
               "latent units (the unit every threshold and U below is in).", "",
               f"Fit: {fit_s:.1f} s, {len(f.history)} sweeps. Source-kind offsets (latent units, "
               f"± se): " + ", ".join(f"{k} {v:+.2f} ± {f.offset_se[k]:.2f}" for k, v in f.offsets.items()),
               "", "Domain sd (learned): " + ", ".join(f"{d} {s:.2f}" for d, s in f.sigma.items()), "",
               "Items: " + json.dumps(_count(it.status for it in f.items.values())), ""]
        out[view] = {"summary": ev.summarise(build.obs), "dropped": build.dropped,
                     "offsets": f.offsets, "offset_se": f.offset_se, "sigma": f.sigma,
                     "items": {i.id: {"status": i.status, "lam": i.lam, "beta": i.beta,
                                      "tau": math.sqrt(i.tau2), "n": i.n_models, "anchor": i.n_anchor,
                                      "tags": i.tags} for i in f.items.values()},
                     "use_cases": {}}
        for uc in FACE_USE_CASES:
            t1 = time.time()
            rep = rank(f, data.by_id, uc, as_of=AS_OF, explain_top=5)
            score_ms = (time.time() - t1) * 1000
            v1 = v1_rank(data, AS_OF, view, uc)
            v1_prod = v1_rank(data, AS_OF, "flat", uc, purge=False) if view == "flat" else None
            out[view]["use_cases"][uc] = {"v2": rep["rows"], "placed": rep["placed"],
                                          "ranked": rep["ranked"], "provisional": rep["provisional"],
                                          "gaps_newest": rep["gaps"][:10],
                                          "v1": [r["model_id"] for r in v1["ranked"][:10]],
                                          "v1_production": [r["model_id"] for r in v1_prod["ranked"][:10]] if v1_prod else None,
                                          "score_ms": score_ms}
            md += [f"### {uc} ({view})", "",
                   f"Mix {USE_CASES[uc]['mix']}. Placed {rep['placed']} ({rep['ranked']} ranked, "
                   f"{rep['provisional']} provisional); scoring every candidate took {score_ms:.0f} ms.", "",
                   "| # | v2 | U (80% interval) | state | lead set | v1 (purged) |" +
                   (" v1 (production data) |" if v1_prod else ""),
                   "|---:|---|---|---|---|---|" + ("---|" if v1_prod else "")]
            v1_ids = [r["model_id"] for r in v1["ranked"][:10]]
            v1p = [r["model_id"] for r in v1_prod["ranked"][:10]] if v1_prod else None
            for i in range(10):
                r = rep["rows"][i] if i < len(rep["rows"]) else None
                cell = (f"{r['model_id']} ({r['release'][:7]}) | {r['mean']:.2f} ({r['lo80']:.2f}, {r['hi80']:.2f}) | "
                        f"{r['state']} | {'yes' if r.get('leading_set') else ''}") if r else " | | | "
                line = f"| {i + 1} | {cell} | {v1_ids[i] if i < len(v1_ids) else ''} |"
                if v1p is not None:
                    line += f" {v1p[i] if i < len(v1p) else ''} |"
                md.append(line)
            md += ["", "Why, for the top 3 (the five measurements carrying the most weight):", ""]
            for r in rep["rows"][:3]:
                md.append(f"- **{r['model_id']}** — U {r['mean']:.2f} ± {r['sd']:.2f}, {r['state']} ({r['reason']}):")
                for x in r.get("explanation", []):
                    unit = {"pct": "%", "lin": "", "log": " min"}[x["unit"]]
                    md.append(f"  - {x['item']} = {x['value']:.4g}{unit} ({x['source_kind']}, {x['date']}"
                              f"{', ' + x['as_evaluated'] if x['as_evaluated'] else ''}"
                              f"{', ' + x['version'] if x['version'] else ''}) → implies {x['implied_ability']:+.2f}"
                              f" ± {x['implied_sd']:.2f}, weight {x['weight_share']:.0%}; {x['source_url']}")
            if rep["gaps"]:
                md += ["", "Newest candidates with an evidence gap (not ranked low, not ranked): "
                       + "; ".join(f"{g['model_id']} ({g.get('release', '')[:10]}): {g['reason']}"
                                   for g in rep["gaps"][:5]), ""]
            md.append("")
    _write("face_validity", out, "\n".join(md))
    return out


def _count(xs) -> dict[str, int]:
    out: dict[str, int] = {}
    for x in xs:
        out[x] = out.get(x, 0) + 1
    return out


# ── 4. ground truth (independent audit) ──────────────────────────────────────

QUESTIONS: dict[str, dict[str, Any]] = {
    "Q01": {"use_case": "coding", "ref": ["anthropic/claude-opus-5-5", "openai/gpt-6-astra", "anthropic/claude-fable-5-1"]},
    "Q02": {"use_case": "agentic", "ref": ["anthropic/claude-opus-5-5", "openai/gpt-6-astra", "anthropic/claude-fable-5-1"]},
    "Q03": {"use_case": "coding", "ref": ["anthropic/claude-opus-5-5", "openai/gpt-6-astra", "anthropic/claude-opus-4-6"]},
    "Q04": {"use_case": "general", "ref": ["anthropic/claude-fable-5-1", "anthropic/claude-opus-5", "anthropic/claude-opus-4-6"]},
    "Q05": {"use_case": "chat", "ref": ["anthropic/claude-fable-5-1", "anthropic/claude-opus-5", "anthropic/claude-opus-4-6"]},
    "Q06": {"use_case": "reasoning", "ref": ["openai/gpt-6-astra", "google/gemini-3-8-flash", "google/gemini-3-7-flash"]},
    "Q07": {"use_case": "math", "ref": ["openai/gpt-6-astra", "anthropic/claude-fable-5", "anthropic/claude-fable-5-1"]},
    "Q08": {"use_case": "rag_generator", "filters": {"min_context": 200_000},
            "ref": ["anthropic/claude-opus-5-5", "openai/gpt-6-astra", "google/gemini-3-8-flash"]},
    "Q09": {"use_case": "rag_generator",
            "ref": ["anthropic/claude-opus-5-5", "openai/gpt-6-astra", "google/gemini-3-8-flash"]},
    "Q10": {"use_case": "general", "filters": {"max_cost": 0.2},
            "ref": ["openai/gpt-6-luna", "openai/gpt-4-1-nano", "openai/gpt-5-6-luna"]},
    "Q11": {"use_case": "chat", "filters": {"max_cost": 0.5},
            "ref": ["openai/gpt-6-luna", "openai/gpt-4-1-mini", "openai/gpt-4-1-nano"]},
    "Q12": {"use_case": "coding", "filters": {"open_weights": True},
            "ref": ["deepseek/deepseek-flash", "qwen/qwen3-8-flash-next", "cerebras/qwen-3-8-27b"]},
    "Q13": {"use_case": "reasoning", "filters": {"open_weights": True},
            "ref": ["deepseek/deepseek-flash", "qwen/qwen3-8-flash-next", "cerebras/qwen-3-8-27b"]},
    "Q14": {"use_case": "vision", "ref": ["anthropic/claude-fable-5", "anthropic/claude-fable-5-1", "anthropic/claude-opus-5"]},
    "Q15": {"use_case": "embedding", "ref": [None, None, "qwen/qwen3-embedding-8b"]},
    "Q16": {"use_case": "embedding", "filters": {"open_weights": True},
            "ref": [None, "tencent/kalm-embedding-gemma3-12b-2511", "qwen/qwen3-embedding-8b"]},
    "Q17": {"use_case": "coding", "filters": {"hardware": "nvidia_rtx_4090", "open_weights": True},
            "ref": ["cerebras/qwen-3-8-27b", "google/gemma-4-31b-it", "google/gemma-4-26b-a4b-it"]},
    "Q18": {"use_case": "chat", "filters": {"hardware": "apple_m4", "open_weights": True},
            "ref": ["google/gemma-4-e4b-it", "google/gemma-4-e2b-it", "google/gemma-4-26b-a4b-it"]},
    "Q19": {"use_case": "research_assistant", "ref": ["openai/gpt-6-astra", "anthropic/claude-opus-5-5", "anthropic/claude-fable-5-1"]},
    "Q20": {"use_case": None, "ref": []},
}
AUDIT_DIR = Path("/private/tmp/claude-501/-Users-terbeest-dev-modelspec/"
                 "6b307b20-b183-41a5-91e6-14f65d035cbc/scratchpad/independent-audit")


def truth(data: Data, audit_dir: Path = AUDIT_DIR) -> dict[str, Any] | None:
    if not (audit_dir / "REPORT.md").exists():
        print("independent audit report not found; skipping", audit_dir)
        return None
    judgments = {j["id"]: j for j in json.loads((audit_dir / "question-judgments.json").read_text())}
    questions = {q["id"]: q for q in json.loads((audit_dir / "questions.json").read_text())}
    fits_map = data.fits()
    out: dict[str, Any] = {}
    md = ["# Ground truth: the independent audit's 20 questions", "",
          "Reference top three and judgments from the independent audit (2026-09-24). v1 top three",
          "are the live answers the audit recorded. `hits` counts v2's top three (ranked and",
          "provisional rows, by posterior mean) that appear in the audit's reference three.", ""]
    for view in VIEWS:
        f = fit_v2(data.obs(AS_OF, view).obs, data.pages, AS_OF)
        md += [f"## View: {view}", "",
               "| Q | question | v1 (audit) | v1 hits | v2 top three (state) | v2 hits | v2 #1 in ref | audit reference |",
               "|---|---|---|---:|---|---:|---|---|"]
        tot = {"v1_hits": 0, "v2_hits": 0, "v2_top1": 0, "answerable": 0}
        rows = []
        for qid, spec in QUESTIONS.items():
            q = questions[qid]
            resp = q.get("response") or {}
            v1_top = [r.get("model_id") for r in (resp.get("result") or [])][:3]
            ref = [r for r in spec["ref"] if r]
            v1_hits = len(set(v1_top) & set(ref))
            if spec["use_case"] is None:
                v2_top, v2_desc = [], "abstains: no speech evidence in the model (evidence gap)"
            else:
                filt = dict(spec.get("filters", {}))
                if "hardware" in filt:
                    filt["fits"] = fits_map
                rep = rank(f, data.by_id, spec["use_case"], as_of=AS_OF, **filt)
                v2_top = [r["model_id"] for r in rep["rows"][:3]]
                v2_desc = "; ".join(f"{r['model_id']} ({r['state']})" for r in rep["rows"][:3]) or \
                    f"abstains: evidence gap ({len(rep['gaps'])} eligible, none measured)"
            v2_hits = len(set(v2_top) & set(ref))
            top1 = bool(v2_top) and v2_top[0] in ref
            tot["v1_hits"] += v1_hits
            tot["v2_hits"] += v2_hits
            tot["v2_top1"] += top1
            tot["answerable"] += bool(ref)
            rows.append({"id": qid, "question": q["question"], "v1_top3": v1_top, "v1_hits": v1_hits,
                         "v2_top3": v2_top, "v2": v2_desc, "v2_hits": v2_hits, "v2_top1_in_ref": top1,
                         "reference": spec["ref"], "audit_judgment_v1": judgments[qid]["judgment"]})
            md.append(f"| {qid} | {q['question'][:70]} | {', '.join(x or '' for x in v1_top)} "
                      f"({judgments[qid]['judgment']}) | {v1_hits} | {v2_desc} | {v2_hits} | "
                      f"{'yes' if top1 else 'no'} | {judgments[qid]['reference'][:90]} |")
        md += ["", f"Totals over {tot['answerable']} questions with a reference: v1 hits "
               f"{tot['v1_hits']}/{3 * tot['answerable']}, v2 hits {tot['v2_hits']}/{3 * tot['answerable']}, "
               f"v2 #1 in the reference three {tot['v2_top1']}/{tot['answerable']}.", ""]
        out[view] = {"rows": rows, "totals": tot}
    _write("ground_truth", out, "\n".join(md))
    return out


# ── saturation ───────────────────────────────────────────────────────────────


def saturation(data: Data) -> dict[str, Any]:
    """Information an item carries at the median model vs. at the frontier."""
    out = {}
    md = ["# Saturation: Fisher information per observation, median vs. frontier", "",
          "theta is the item's own domain blend. `median` and `frontier` are the 50th and 97th",
          "percentiles of that blend over the models observed on the item. A saturated",
          "benchmark keeps information at the median and loses it at the frontier.", ""]
    for view in VIEWS:
        f = fit_v2(data.obs(AS_OF, view).obs, data.pages, AS_OF)
        rows = []
        for it in f.items.values():
            if it.status not in ("free", "borrowed") or it.link != "pct" or it.n_models < 8:
                continue
            thetas = sorted(mf.value("g") + sum(mf.value(d) for d in it.tags) / len(it.tags)
                            for mf in f.models.values())
            med = thetas[len(thetas) // 2]
            front = thetas[int(0.97 * (len(thetas) - 1))]
            i_med, i_front = item_information(f, it.id, med), item_information(f, it.id, front)
            top = max(r.obs.value for mf in f.models.values() for r in mf.rows if r.item is it)
            rows.append({"item": it.id, "n": it.n_models, "lambda": it.lam, "tau_pp": 100 * math.sqrt(it.tau2),
                         "info_median": i_med, "info_frontier": i_front,
                         "frontier_share": i_front / i_med if i_med else float("nan"), "top": top})
        rows.sort(key=lambda r: r["frontier_share"])
        out[view] = rows
        md += [f"## View: {view}", "",
               "| item | models | best observed | lambda | tau (pp) | info at median | info at frontier | frontier / median |",
               "|---|---:|---:|---:|---:|---:|---:|---:|"]
        for r in rows:
            md.append(f"| {r['item']} | {r['n']} | {r['top']:.1f} | {r['lambda']:.2f} | {r['tau_pp']:.1f} | {r['info_median']:.2f} | "
                      f"{r['info_frontier']:.2f} | {r['frontier_share']:.2f} |")
        md.append("")
    _write("saturation", out, "\n".join(md))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="ranking v2 backtests")
    ap.add_argument("what", choices=["all", "heldout", "replay", "face", "truth", "saturation"])
    ap.add_argument("--report", type=Path, default=AUDIT_DIR)
    args = ap.parse_args()
    data = Data()
    steps = ["face", "saturation", "truth", "heldout", "replay"] if args.what == "all" else [args.what]
    for s in steps:
        t0 = time.time()
        if s == "truth":
            truth(data, args.report)
        else:
            globals()[s](data)
        print(f"{s}: {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
