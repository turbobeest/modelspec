"""Rank models against a use-case profile, without a database.

`api/ranking/engine.py` holds the profiles, the benchmark normalisation ranges
and the scoring constants. That module imports cleanly with no FalkorDB
dependency, so this reuses its tables and helpers directly rather than
transcribing them — a transcribed copy of 51 profiles and 170 benchmark ranges
would drift on the first edit.

What is reimplemented here is only the scoring itself, against a model built
from a card rather than from a Cypher row. The formulas follow
`RankingEngine._score` exactly: benchmarks to 40 points, capabilities to 20,
cost and context scaled by the profile's weights, a type-match bonus to 15.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from api.ranking.engine import (
    BENCHMARK_RANGES,
    USE_CASE_PROFILES,
    _normalize_benchmark,
    _tier_points,
    _tier_rank,
)
from schema.graph import CollectingSink

#: Profiles offered in the wizard. All 51 are exported for the API, but a
#: dropdown of 51 is a worse experience than one of 12, and these cover the
#: questions people actually arrive with.
FEATURED_PROFILES = (
    "general", "coding", "reasoning", "chat", "agentic", "rag",
    "vision", "multilingual", "math_competition", "writing_technical",
    "summarization", "embedding",
)


@dataclass
class Candidate:
    model_id: str
    display_name: str
    provider: str
    model_type: str | None
    model_subtypes: list[str] = field(default_factory=list)
    benchmark_scores: dict[str, float] = field(default_factory=dict)
    capability_tiers: dict[str, str] = field(default_factory=dict)
    cost_input: float | None = None
    context_window: int | None = None
    open_weights: bool = False
    scores_as_of: str | None = None
    fits: dict[str, float] = field(default_factory=dict)  # hardware id -> predicted tok/s

    def to_json(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id, "display_name": self.display_name,
            "provider": self.provider, "model_type": self.model_type,
            "model_subtypes": self.model_subtypes,
            "benchmark_scores": self.benchmark_scores,
            "capability_tiers": self.capability_tiers,
            "cost_input": self.cost_input, "context_window": self.context_window,
            "open_weights": self.open_weights, "scores_as_of": self.scores_as_of,
            "fits": self.fits,
        }


def build_candidates(cards: list[Any], sink: CollectingSink) -> list[Candidate]:
    """One ranking record per card, with capability tiers and hardware fit attached."""
    tiers: dict[str, dict[str, str]] = {}
    fits: dict[str, dict[str, float]] = {}
    for edge in sink.edges:
        if edge["type"] == "HAS_CAPABILITY":
            props = edge.get("props") or {}
            if props.get("tier"):
                tiers.setdefault(edge["from"], {})[edge["to"]] = str(props["tier"])
        elif edge["type"] == "FITS_ON":
            props = edge.get("props") or {}
            tps = props.get("fastest_predicted_decode_tps")
            if tps:
                fits.setdefault(edge["from"], {})[edge["to"]] = float(tps)

    out = []
    for card in cards:
        ident = card.identity
        out.append(Candidate(
            model_id=ident.model_id,
            display_name=ident.display_name or ident.model_id,
            provider=ident.provider_display or ident.provider or "",
            model_type=ident.model_type.value if ident.model_type else None,
            model_subtypes=[s.value for s in ident.model_subtypes] if ident.model_subtypes else [],
            benchmark_scores={k: float(v) for k, v in card.benchmarks.scores.items()
                              if isinstance(v, (int, float))},
            capability_tiers=tiers.get(ident.model_id, {}),
            cost_input=card.cost.input,
            context_window=card.modalities.text.context_window,
            open_weights=bool(card.licensing.open_weights),
            scores_as_of=str(card.benchmarks.benchmark_as_of or "") or None,
            fits=fits.get(ident.model_id, {}),
        ))
    return out


def score(candidate: Candidate, profile: dict[str, Any]) -> dict[str, Any]:
    """Score one candidate. Mirrors RankingEngine._score."""
    bench_weights = profile.get("benchmark_weights", {})
    bench_raw = 0.0
    contributions: dict[str, float] = {}
    for bench_id, weight in bench_weights.items():
        raw = candidate.benchmark_scores.get(bench_id)
        if raw is None:
            continue
        contribution = _normalize_benchmark(bench_id, raw) * weight
        bench_raw += contribution
        contributions[bench_id] = round(contribution, 2)
    bench = bench_raw * 0.40

    cap_weights = profile.get("capability_weights", {})
    total_cap_weight = sum(cap_weights.values()) if cap_weights else 1.0
    cap_raw = 0.0
    for name, weight in cap_weights.items():
        tier = candidate.capability_tiers.get(name)
        if tier:
            cap_raw += _tier_points(tier) * (weight / total_cap_weight)
        else:
            subs = [t for cid, t in candidate.capability_tiers.items()
                    if cid.startswith(f"{name}:")]
            if subs:
                best = min(subs, key=_tier_rank)
                cap_raw += _tier_points(best) * 0.7 * (weight / total_cap_weight)
    cap = cap_raw * 2.0

    cost_weight = profile.get("cost_weight", 0.10)
    cost_raw = 0.0
    if candidate.cost_input is not None:
        if candidate.cost_input == 0:
            cost_raw = 10.0
        else:
            clamped = max(candidate.cost_input, 0.10)
            cost_raw = max(0.0, min(9.5, 9.0 + 2.0 * math.log10(0.10 / clamped)))
    cost = cost_raw * cost_weight * 10

    ctx_weight = profile.get("context_weight", 0.10)
    ctx_raw = 0.0
    if candidate.context_window and candidate.context_window > 0:
        ctx_raw = min(10.0, max(0.0, (math.log10(candidate.context_window) - 3.5) * 3.0))
    ctx = ctx_raw * ctx_weight * 10

    preferred = profile.get("preferred_types", [])
    type_bonus = 0.0
    if candidate.model_type:
        best_idx = None
        for t in [candidate.model_type] + candidate.model_subtypes:
            if t in preferred:
                idx = preferred.index(t)
                best_idx = idx if best_idx is None else min(best_idx, idx)
        if best_idx is not None:
            type_bonus = max(5.0, 15.0 - best_idx * 3.0)

    total = max(0.0, min(100.0, bench + cap + cost + ctx + type_bonus))
    return {
        "model_id": candidate.model_id,
        "display_name": candidate.display_name,
        "provider": candidate.provider,
        "score": round(total, 2),
        "benchmark_score": round(bench, 2),
        "capability_score": round(cap, 2),
        "cost_score": round(cost, 2),
        "context_score": round(ctx, 2),
        "type_bonus": round(type_bonus, 2),
        "benchmark_contributions": contributions,
        "context_window": candidate.context_window,
        "cost_input": candidate.cost_input,
        "open_weights": candidate.open_weights,
        # Every benchmark contribution comes from a card score that carries one
        # date per card and no per-score source. The ranking is only as good as
        # that, and must say so.
        "evidence_basis": "unverified-legacy" if contributions else "none",
        "scores_as_of": candidate.scores_as_of,
    }


def rank(candidates: list[Candidate], profile_key: str, limit: int = 25,
         open_weights_only: bool = False, hardware_id: str | None = None) -> list[dict[str, Any]]:
    profile = USE_CASE_PROFILES[profile_key]
    pool = candidates
    if open_weights_only:
        pool = [c for c in pool if c.open_weights]
    if hardware_id:
        pool = [c for c in pool if hardware_id in c.fits]
    scored = [score(c, profile) for c in pool]
    scored.sort(key=lambda r: (-r["score"], r["display_name"].lower()))
    return scored[:limit]


def write_export(out_dir: Any, cards: list[Any], sink: CollectingSink,
                 build_json: dict[str, Any]) -> dict[str, Any]:
    """Emit the tables the browser needs, plus precomputed rankings."""
    import json
    from pathlib import Path

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    def dump(rel: str, payload: Any) -> None:
        path = out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, sort_keys=True, default=str), encoding="utf-8")

    candidates = build_candidates(cards, sink)
    dump("profiles.json", {
        "build": build_json,
        "featured": list(FEATURED_PROFILES),
        "profiles": USE_CASE_PROFILES,
        "benchmark_ranges": {k: list(v) for k, v in BENCHMARK_RANGES.items()},
    })
    dump("candidates.json", {
        "build": build_json,
        "count": len(candidates),
        "candidates": [c.to_json() for c in candidates],
    })

    precomputed = {}
    for key in FEATURED_PROFILES:
        precomputed[key] = rank(candidates, key, limit=25)
    dump("rankings.json", {"build": build_json, "rankings": precomputed})

    return {
        "candidates": len(candidates),
        "profiles": len(USE_CASE_PROFILES),
        "featured": len(FEATURED_PROFILES),
        "precomputed": {k: len(v) for k, v in precomputed.items()},
    }
