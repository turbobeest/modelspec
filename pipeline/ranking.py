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
    RANKING_POLICY,
    WIZARD_BENCHMARK_COVERAGE,
    _benchmark_evidence,
    _ranking_status,
    _tier_points,
    _tier_rank,
    ranking_policy,
)
from schema.graph import CollectingSink

#: Profiles offered in the wizard. All 51 are exported for the API, but a
#: dropdown of 51 is a worse experience than a short list. speech_to_text
#: currently ranks nothing (MODEL-30); offered-and-empty is worse than hiding
#: it. image_generation stays out until clip_score's range is sourced.
FEATURED_PROFILES = (
    "general", "coding", "reasoning", "chat", "agentic", "rag",
    "vision", "multilingual", "math_competition", "writing_technical",
    "summarization", "embedding", "text_to_speech",
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
    #: Benchmarks whose score came from a reviewed evidence record rather than
    #: the card's undated flat block. A ranking is only as good as the weakest
    #: evidence under it, so this is tracked per benchmark, not per model.
    verified_benchmarks: set[str] = field(default_factory=set)

    def to_json(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id, "display_name": self.display_name,
            "provider": self.provider, "model_type": self.model_type,
            "model_subtypes": self.model_subtypes,
            "benchmark_scores": self.benchmark_scores,
            "capability_tiers": self.capability_tiers,
            "cost_input": self.cost_input, "context_window": self.context_window,
            "open_weights": self.open_weights, "scores_as_of": self.scores_as_of,
            "fits": self.fits, "verified_benchmarks": sorted(self.verified_benchmarks),
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
        # Reviewed evidence takes precedence over the flat block for the same
        # benchmark: it is the same measurement, checked.
        scores = {k: float(v) for k, v in card.benchmarks.scores.items()
                  if isinstance(v, (int, float))}
        verified: set[str] = set()
        for record in card.benchmarks.evidence:
            scores[record.benchmark_id] = float(record.score)
            verified.add(record.benchmark_id)
        out.append(Candidate(
            model_id=ident.model_id,
            display_name=ident.display_name or ident.model_id,
            provider=ident.provider_display or ident.provider or "",
            model_type=ident.model_type.value if ident.model_type else None,
            model_subtypes=[s.value for s in ident.model_subtypes] if ident.model_subtypes else [],
            benchmark_scores=scores,
            verified_benchmarks=verified,
            capability_tiers=tiers.get(ident.model_id, {}),
            cost_input=card.cost.input,
            context_window=card.modalities.text.context_window,
            open_weights=bool(card.licensing.open_weights),
            scores_as_of=str(card.benchmarks.benchmark_as_of or "") or None,
            fits=fits.get(ident.model_id, {}),
        ))
    return out


def score(candidate: Candidate, profile: dict[str, Any],
          cost_weight: float | None = None,
          min_coverage: float | None = None) -> dict[str, Any]:
    """Score one candidate. Mirrors RankingEngine._score.

    `cost_weight` overrides the profile's own. Every shipped profile carries
    0.0, so price contributes nothing unless a caller asks for it — and how much
    quality someone will trade for price is a property of the person, not of the
    use case, so it belongs in the query rather than in the table. See MODEL-30.
    """
    evidence = _benchmark_evidence(candidate.benchmark_scores, profile,
                                  min_coverage=min_coverage)
    contributions = evidence["benchmark_contributions"]
    contributing_verified = len(contributions.keys() & candidate.verified_benchmarks)
    weights = profile.get("benchmark_weights", {})
    total_weight = sum(weights.values())
    verified_weight = sum(weights[b] for b in contributions if b in candidate.verified_benchmarks)
    bench = evidence["benchmark_lower_bound"]

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

    if cost_weight is None:
        cost_weight = profile.get("cost_weight", 0.0)
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

    other = cap + cost + ctx + type_bonus
    total = max(0.0, min(100.0, bench + other))
    upper = max(0.0, min(100.0, evidence["benchmark_upper_bound"] + other))
    return {
        "model_id": candidate.model_id,
        "display_name": candidate.display_name,
        "provider": candidate.provider,
        "score": round(total, 2) if evidence["rank_status"] == "ranked" else None,
        "rank": None,
        "score_lower_bound": round(total, 2),
        "score_upper_bound": round(upper, 2),
        "score_kind": RANKING_POLICY["ordering"],
        "benchmark_score": round(bench, 2),
        "capability_score": round(cap, 2),
        "cost_score": round(cost, 2),
        "context_score": round(ctx, 2),
        "type_bonus": round(type_bonus, 2),
        **evidence,
        "context_window": candidate.context_window,
        "cost_input": candidate.cost_input,
        "open_weights": candidate.open_weights,
        # A ranking is only as good as the evidence under it. Say which kind
        # rather than averaging the two into a single reassuring label.
        "evidence_basis": _basis(len(contributions), contributing_verified,
                                 evidence["benchmark_coverage"]),
        "verified_contributions": contributing_verified,
        "verified_benchmark_coverage": verified_weight / total_weight if total_weight else 0.0,
        "scores_as_of": candidate.scores_as_of,
    }


def _basis(contributing: int, verified: int, coverage: float) -> str:
    """Provenance of benchmark inputs, never a certification of the composite."""
    if not contributing:
        return "none"
    if verified == contributing:
        return "verified" if coverage >= 1.0 - 1e-12 else "partial-verified"
    if verified:
        return "mixed"
    return "unverified-legacy"


def rank(candidates: list[Candidate], profile_key: str, limit: int = 25,
         open_weights_only: bool = False, hardware_id: str | None = None,
         cost_weight: float | None = None,
         min_benchmark_coverage: float | None = None) -> list[dict[str, Any]]:
    """Return the models that can honestly be ordered for this profile.

    Unrankable models are the normal catalogue state, not an error. This
    returns the ranked shortlist, which may be empty when nothing has enough
    evidence. Use rank_report() to see withheld models and ranking_status.
    Default coverage floor is the CLI floor (0.50).
    """
    return rank_report(candidates, profile_key, limit, open_weights_only,
                       hardware_id, cost_weight,
                       min_benchmark_coverage)["ranked"]


def rank_report(candidates: list[Candidate], profile_key: str, limit: int = 25,
                open_weights_only: bool = False, hardware_id: str | None = None,
                cost_weight: float | None = None,
                min_benchmark_coverage: float | None = None) -> dict[str, Any]:
    """Rank sufficiently covered models and retain all others as unranked.

    `limit` caps the ranked shortlist only. Unranked entries are alphabetical,
    have null rank/score, and are never truncated or presented as ranked last.
    Default coverage floor is the CLI floor (0.50). Pass
    `WIZARD_BENCHMARK_COVERAGE` for the browser surface.
    """
    if limit < 0:
        raise ValueError("limit must be nonnegative")
    profile = USE_CASE_PROFILES[profile_key]
    pool = candidates
    if open_weights_only:
        pool = [c for c in pool if c.open_weights]
    if hardware_id:
        pool = [c for c in pool if hardware_id in c.fits]
    scored = [score(c, profile, cost_weight, min_benchmark_coverage) for c in pool]
    ranked = [r for r in scored if r["rank_status"] == "ranked"]
    unranked = [r for r in scored if r["rank_status"] == "unranked"]
    ranked.sort(key=lambda r: (-r["score"], r["display_name"].lower(), r["model_id"]))
    unranked.sort(key=lambda r: (r["display_name"].lower(), r["model_id"]))
    for position, result in enumerate(ranked, 1):
        result["rank"] = position
    return {
        "ranking_status": _ranking_status(ranked, unranked),
        "profile": profile_key,
        "policy": ranking_policy(min_benchmark_coverage=min_benchmark_coverage),
        "ranked_count": len(ranked), "unranked_count": len(unranked),
        "ranked": ranked[:limit], "unranked": unranked,
    }


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
        "ranking_policy": RANKING_POLICY,
    })
    dump("candidates.json", {
        "build": build_json,
        "count": len(candidates),
        "candidates": [c.to_json() for c in candidates],
    })

    precomputed = {}
    for key in FEATURED_PROFILES:
        precomputed[key] = rank_report(
            candidates, key, limit=25,
            min_benchmark_coverage=WIZARD_BENCHMARK_COVERAGE,
        )
    dump("rankings.json", {"schema_version": "2.0", "build": build_json, "rankings": precomputed})

    return {
        "candidates": len(candidates),
        "profiles": len(USE_CASE_PROFILES),
        "featured": len(FEATURED_PROFILES),
        "precomputed": {k: len(v["ranked"]) for k, v in precomputed.items()},
    }


def format_report(report: dict[str, Any]) -> str:
    """Human-readable contract shared by the report CLI and its tests."""
    policy = report['policy']
    lines = [
        f"{report['profile']}: {report['ranking_status']} ordering; "
        f"{report['ranked_count']} ranked, {report['unranked_count']} unranked.",
        "Ranked by conservative composite lower bound; observed benchmark averages "
        "do not predict missing results.",
        f"Eligibility: at least {policy['min_benchmark_coverage']:.0%} weighted benchmark coverage "
        f"and {policy['min_benchmark_count']} benchmarks (or all for a smaller profile). "
        "Bounds describe missing evidence, not statistical confidence.",
    ]
    for row in report["ranked"]:
        lines.append(
            f"{row['rank']:>3}. {row['score']:.2f}  {row['display_name']}  "
            f"coverage {row['benchmark_coverage']:.0%}, "
            f"bounds [{row['score_lower_bound']:.2f}, {row['score_upper_bound']:.2f}], "
            f"benchmark basis: {row['evidence_basis']}"
        )
    if report["unranked"]:
        lines.append("Unranked for insufficient benchmark evidence (alphabetical; not ranked low):")
        for row in report["unranked"]:
            estimate = row["benchmark_estimate"]
            observed = "none" if estimate is None else f"{estimate:.2f}/100"
            lines.append(
                f"  UNRANKED  {row['display_name']}  coverage {row['benchmark_coverage']:.0%}, "
                f"observed benchmark average {observed}, benchmark basis: {row['evidence_basis']}"
            )
    return "\n".join(lines)


def main() -> None:
    """Report CLI, usable without changes to the legacy list-only CLI."""
    import argparse
    import json
    from pathlib import Path
    from schema.card import ModelCard
    from schema.graph import derive_graph

    parser = argparse.ArgumentParser(description="Rank models with explicit incomplete evidence.")
    parser.add_argument("profile", choices=sorted(USE_CASE_PROFILES))
    parser.add_argument("--limit", type=int, default=10, help="Maximum ranked rows; all unranked models remain visible.")
    parser.add_argument("--json", action="store_true", help="Emit the version 2 ranking report.")
    args = parser.parse_args()
    if args.limit < 0:
        parser.error("--limit must be nonnegative")
    root = Path(__file__).resolve().parents[1]
    cards = [ModelCard.from_yaml_file(p) for p in sorted((root / "models").rglob("*.md"))
             if p.name != "LICENSE.md"]
    report = rank_report(build_candidates(cards, derive_graph(cards)), args.profile, args.limit)
    if args.json:
        print(json.dumps({"schema_version": "2.0", **report}, indent=2))
    else:
        print(format_report(report))


if __name__ == "__main__":
    main()
