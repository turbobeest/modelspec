"""The sandbox: a real ranking of models that do not exist (MODEL-69).

A `test_` key is answered from this module and nothing else. No key store, no
published export, no network — the short-circuit happens in `access.serve`
before either is reached, and `tests/test_api_access.py` proves it by handing
the gateway a key store and a data loader that fail the test if they are called.

What makes the answer trustworthy as an integration target is that it is not a
hand-written fixture. The rows come out of `pipeline.ranking.rank_report` — the
same function the live endpoint and `modelspec offline rank --json` call — run
over a fixed set of synthetic candidates defined below. Every field a live row
has, a sandbox row has, with the same types, because the same code produced
both. A field added to the scorer appears here on the next deploy without
anybody remembering to update a fixture.

The values are deliberately unmistakable. The models are called
`sandbox/fixture-*`, the provider is "ModelSpec Sandbox", and `scores_as_of` is
a fixed date. Nobody can mistake this for the catalogue, and `"sandbox": true`
rides on the response so a program does not have to.
"""

from __future__ import annotations

from typing import Any

from api.ranking.engine import BENCHMARK_RANGES, USE_CASE_PROFILES, ranking_policy
from pipeline.ranking import Candidate, rank_report

#: Marked on every sandbox response. A caller that ignores it and ships these
#: rows has at least been told.
SANDBOX_MARKER = "sandbox"

#: Fixed, so two sandbox calls a week apart return the same thing.
SCORES_AS_OF = "2026-01-01"

DEFAULT_USE_CASE = "general"
#: Ranked rows returned when the request does not ask for a number. A page
#: size, not a rate limit.
DEFAULT_ROW_COUNT = 10

#: The synthetic catalogue: a strong managed model, a strong open-weights
#: model, a cheap small one, and one with thin evidence so a caller sees what
#: `unranked` and a real `evidence_basis` look like before they pay for either.
_FIXTURES: tuple[dict[str, Any], ...] = (
    {"model_id": "sandbox/fixture-flagship", "display_name": "Sandbox Flagship",
     "quality": 0.95, "coverage": 1.0, "verified": True, "cost_input": 3.0,
     "context_window": 200_000, "open_weights": False,
     "model_type": "llm-reasoning", "tier": "tier-1"},
    {"model_id": "sandbox/fixture-open", "display_name": "Sandbox Open 70B",
     "quality": 0.82, "coverage": 1.0, "verified": True, "cost_input": 0.6,
     "context_window": 128_000, "open_weights": True,
     "model_type": "llm-chat", "tier": "tier-1"},
    {"model_id": "sandbox/fixture-small", "display_name": "Sandbox Small 8B",
     "quality": 0.55, "coverage": 0.75, "verified": False, "cost_input": 0.05,
     "context_window": 32_000, "open_weights": True,
     "model_type": "llm-chat", "tier": "tier-2"},
    {"model_id": "sandbox/fixture-unrated", "display_name": "Sandbox Unrated",
     "quality": 0.40, "coverage": 0.0, "verified": False, "cost_input": None,
     "context_window": 8_000, "open_weights": True,
     "model_type": "llm-chat", "tier": "tier-3"},
)

_PROVIDER = "ModelSpec Sandbox"


def _benchmark_value(benchmark: str, quality: float) -> float:
    """A plausible score for a benchmark, `quality` of the way up its range."""
    low, high = BENCHMARK_RANGES.get(benchmark, (0.0, 100.0))
    return round(low + (high - low) * quality, 1)


def _candidates(use_case: str) -> list[Candidate]:
    """Synthetic candidates carrying the benchmarks this profile weighs.

    Scores are generated for the profile's own benchmarks so the sandbox
    answers every use case the live endpoint does, rather than only the ones
    somebody happened to write a fixture for.
    """
    profile = USE_CASE_PROFILES[use_case]
    weighted = [b for b, w in profile.get("benchmark_weights", {}).items() if w > 0]
    capabilities = list(profile.get("capability_weights", {}))

    out: list[Candidate] = []
    for spec in _FIXTURES:
        covered = weighted[:max(0, round(len(weighted) * float(spec["coverage"])))]
        scores = {b: _benchmark_value(b, float(spec["quality"])) for b in covered}
        out.append(Candidate(
            model_id=str(spec["model_id"]),
            display_name=str(spec["display_name"]),
            provider=_PROVIDER,
            model_type=str(spec["model_type"]),
            model_subtypes=[],
            benchmark_scores=scores,
            capability_tiers={name: str(spec["tier"]) for name in capabilities},
            cost_input=spec["cost_input"],
            context_window=int(spec["context_window"]),
            open_weights=bool(spec["open_weights"]),
            scores_as_of=SCORES_AS_OF,
            fits={},
            verified_benchmarks=set(covered) if spec["verified"] else set(),
        ))
    return out


def request_from_payload(payload: Any) -> dict[str, Any]:
    """A tolerant reading of a request body.

    Used when the caller has not already parsed the request. The Worker should
    pass the live parser's output instead, so that a body the live endpoint
    would refuse is refused in the sandbox too — see `docs/api-access.md`.
    """
    body = payload if isinstance(payload, dict) else {}
    use_case = body.get("use_case")
    if not isinstance(use_case, str) or use_case not in USE_CASE_PROFILES:
        use_case = DEFAULT_USE_CASE
    limit = body.get("limit")
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        limit = DEFAULT_ROW_COUNT
    constraints = body.get("constraints") if isinstance(body.get("constraints"), dict) else {}
    return {
        "use_case": use_case,
        "limit": limit,
        "open_weights_only": bool(constraints.get("open_weights")),
        "include_rehosts": bool(constraints.get("include_rehosts")),
        "hardware_id": None,
        "hosting": None,
        "runtime": None,
        "max_cost": None,
        "price_sensitivity": None,
        "cost_weight": None,
        "open_weights_because": None,
        "unbound": [],
    }


def rank_response(request: dict[str, Any], *, envelope: dict[str, Any],
                  policy: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    """A sandbox answer to one rank request.

    `envelope` is the live envelope — pass the one the live handler builds, so
    the two responses cannot drift apart in the fields that identify a build.
    Built from an empty export, it carries null build fields, which is honest:
    no export was read.
    """
    use_case = request.get("use_case") or DEFAULT_USE_CASE
    pool = _candidates(use_case)
    report = rank_report(
        pool, use_case, limit=int(request.get("limit") or DEFAULT_ROW_COUNT),
        open_weights_only=bool(request.get("open_weights_only")),
        hardware_id=None,
        cost_weight=request.get("cost_weight"),
        include_rehosts=bool(request.get("include_rehosts")),
    )
    body = {
        **envelope,
        SANDBOX_MARKER: True,
        "request": {
            "use_case": use_case,
            "environment": {"hardware": request.get("hardware_id"),
                            "hosting": request.get("hosting"),
                            "runtime": request.get("runtime")},
            "constraints": {
                "open_weights": bool(request.get("open_weights_only")),
                "max_cost_per_million_input_tokens": request.get("max_cost"),
                "price_sensitivity": request.get("price_sensitivity"),
                "include_rehosts": bool(request.get("include_rehosts")),
            },
            "limit": int(request.get("limit") or DEFAULT_ROW_COUNT),
        },
        "applied": {
            "open_weights_only": bool(request.get("open_weights_only")),
            "open_weights_required_by": request.get("open_weights_because"),
            "hardware_id": None,
            "max_cost_per_million_input_tokens": request.get("max_cost"),
            "cost_weight": request.get("cost_weight"),
            "include_rehosts": bool(request.get("include_rehosts")),
            "unbound": list(request.get("unbound") or []),
        },
        "policy": policy if policy is not None else ranking_policy(),
        "profile": report["profile"],
        "ranking_status": report["ranking_status"],
        "ranked_count": report["ranked_count"],
        "unranked_count": report["unranked_count"],
        "candidates_considered": len(pool),
        "result": report["ranked"],
    }
    return 200, body
