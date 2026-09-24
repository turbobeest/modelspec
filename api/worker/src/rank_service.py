"""The rank endpoint's logic, with no Cloudflare runtime in it (MODEL-68).

`entry.py` is the Worker: it reads the request, fetches the published export and
writes the response. Everything that decides *what the answer is* lives here, so
the whole endpoint can be exercised by the repository's own test suite under
CPython, which is what makes the byte-identity proof in
`tests/test_rank_worker.py` worth anything.

Three rules this module exists to keep:

1. **The scorer is not reimplemented.** `rank_report` is imported from
   `pipeline.ranking`, the same function `modelspec offline rank --json` calls.
   `api/worker/vendor.py` puts that file in the Worker bundle byte for byte.
2. **The floors are not written down a second time.** `rank_report` is called
   with `min_benchmark_coverage=None`, which is how it reaches
   `api.ranking.engine.MIN_BENCHMARK_COVERAGE`, and the published policy block
   comes from `ranking_policy()`. There is no numeric floor anywhere in this
   package; `tests/test_rank_worker.py` asserts that.
3. **A no-match is an answer, not an empty list.** `_eliminations` re-applies
   the filters one at a time in the order `rank_report` applies them and reports
   the first one that empties the pool, so a caller is told which constraint to
   relax. It is `HTTP_NO_MATCH`, never a 200 with `[]`.

The request carries a *profile* — use case, environment, constraints. It never
carries a prompt. That is the architectural constraint recorded for the
recommender, and widening these fields toward prompt text is a contract change,
not a feature.
"""

from __future__ import annotations

from typing import Any

from api.ranking.engine import (
    CLOUD_PLATFORMS,
    LOCAL_PLATFORMS,
    PROVIDER_PLATFORMS,
    USE_CASE_PROFILES,
    ranking_policy,
)
from pipeline.ranking import Candidate, rank_report

#: Bumped only for an incompatible change to this envelope. Distinct from
#: `build.export_schema_version` (the published JSON tree) and from the CLI's
#: own `schema_version`, which this deliberately mirrors at 1.0 because the
#: ranked rows inside `result` are the same rows.
#:
#: MODEL-81 added `authoring_guide` as an always-present envelope field (the
#: recommended model's card guide, or a documented absent state). That is a
#: new field, not a widening of an existing one, so this stays 1.0 under
#: MODEL-59. `result` rows are unchanged. A bump here would also bump
#: policy-check: the two endpoints share one OpenAPI `info.version`.
#:
#: MODEL-110 added `unranked_candidates` the same way: a new always-present
#: field, not a widened one, so still 1.0.
SCHEMA_VERSION = "1.0"

#: Serving states for `authoring_guide.state`. `absent` is a state, never an
#: omitted field, an empty string, or generated text. `stale` is served as
#: stale (MODEL-65); it is never rewritten to `current`.
AUTHORING_GUIDE_STATES = ("absent", "current", "stale")
AUTHORING_GUIDE_WHYS = ("no_guide", "no_recommendation")
GUIDE_STATE_ABSENT = "absent"
GUIDE_STATE_CURRENT = "current"
GUIDE_STATE_STALE = "stale"
GUIDE_WHY_NO_GUIDE = "no_guide"
GUIDE_WHY_NO_RECOMMENDATION = "no_recommendation"

HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405
HTTP_PAYLOAD_TOO_LARGE = 413
#: A well-formed request that no model survives. Documented, and never a 200
#: with an empty list: the caller is told which constraint eliminated the pool.
HTTP_NO_MATCH = 422
HTTP_BAD_GATEWAY = 502

#: Largest request body accepted. A rank request is a few hundred bytes.
MAX_BODY_BYTES = 16 * 1024

#: Default ranked rows. `limit` caps the ranked shortlist only, exactly as it
#: does in the CLI.
DEFAULT_LIMIT = 10
MAX_LIMIT = 100

#: How the caller says where the model will run. Only the first two bind
#: anything, and they bind the one thing the published export can actually
#: answer: you can self-host only weights you can download.
HOSTING_MODES = {
    "local": {"open_weights": True,
              "means": "on the caller's own machine; requires downloadable weights"},
    "self_hosted": {"open_weights": True,
                    "means": "on infrastructure the caller runs; requires downloadable weights"},
    "managed_api": {"open_weights": False,
                    "means": "a provider or gateway API; no weights requirement"},
}

#: Runtime ids are taken from the engine's own platform tables rather than a
#: list invented here. Membership in LOCAL_PLATFORMS is the only thing that
#: binds, for the same reason as above; the rest are recorded and reported as
#: unbound, because the published export carries no runtime-level evidence and
#: a filter with nothing behind it would be a guess.
KNOWN_RUNTIMES = LOCAL_PLATFORMS | CLOUD_PLATFORMS | PROVIDER_PLATFORMS
LOCAL_RUNTIMES = LOCAL_PLATFORMS


class RequestError(ValueError):
    """A request this endpoint refuses, with the code the caller gets back."""

    def __init__(self, code: str, message: str, status: int = HTTP_BAD_REQUEST,
                 **detail: Any) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.detail = detail


# ── request parsing ──────────────────────────────────────────────────────────

def _object(value: Any, field: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise RequestError("invalid_request", f"{field} must be an object")
    return value


def _optional_str(value: Any, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise RequestError("invalid_request", f"{field} must be a non-empty string")
    return value.strip()


def _optional_bool(value: Any, field: str) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise RequestError("invalid_request", f"{field} must be true or false")
    return value


def _optional_number(value: Any, field: str) -> float | None:
    if value is None:
        return None
    # bool is an int in Python, and `true` is not a number a caller meant.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RequestError("invalid_request", f"{field} must be a number")
    return float(value)


def parse_request(payload: Any, known_hardware: set[str]) -> dict[str, Any]:
    """Validate the body and reduce it to the knobs the scorer actually has.

    Every environment and constraint field is mapped onto an argument
    `rank_report` already takes. Nothing here invents a filter: a knob the
    published export cannot answer is reported as unbound rather than guessed.
    """
    if not isinstance(payload, dict):
        raise RequestError("invalid_request", "the request body must be a JSON object")

    unknown = sorted(set(payload) - {"use_case", "environment", "constraints", "limit"})
    if unknown:
        raise RequestError(
            "invalid_request",
            "unknown top-level field(s): " + ", ".join(unknown),
            fields=unknown,
            accepted=["use_case", "environment", "constraints", "limit"],
        )

    use_case = _optional_str(payload.get("use_case"), "use_case")
    if use_case is None:
        raise RequestError("invalid_request", "use_case is required",
                           accepted=sorted(USE_CASE_PROFILES))
    if use_case not in USE_CASE_PROFILES:
        raise RequestError("unknown_use_case", f"unknown use case {use_case!r}",
                           accepted=sorted(USE_CASE_PROFILES))

    environment = _object(payload.get("environment"), "environment")
    stray_env = sorted(set(environment) - {"hardware", "hosting", "runtime"})
    if stray_env:
        raise RequestError("invalid_request",
                           "unknown environment field(s): " + ", ".join(stray_env),
                           fields=stray_env, accepted=["hardware", "hosting", "runtime"])

    constraints = _object(payload.get("constraints"), "constraints")
    accepted_constraints = {"open_weights", "max_cost_per_million_input_tokens",
                            "price_sensitivity", "include_rehosts"}
    stray_con = sorted(set(constraints) - accepted_constraints)
    if stray_con:
        raise RequestError("invalid_request",
                           "unknown constraint(s): " + ", ".join(stray_con),
                           fields=stray_con, accepted=sorted(accepted_constraints))

    hardware = _optional_str(environment.get("hardware"), "environment.hardware")
    if hardware is not None and hardware not in known_hardware:
        # The CLI refuses a typo'd device rather than answering "nothing fits
        # your GPU", because those are different answers. So does this.
        raise RequestError("unknown_hardware", f"unknown device {hardware!r}",
                           accepted=sorted(known_hardware))

    hosting = _optional_str(environment.get("hosting"), "environment.hosting")
    if hosting is not None and hosting not in HOSTING_MODES:
        raise RequestError("unknown_hosting", f"unknown hosting mode {hosting!r}",
                           accepted=sorted(HOSTING_MODES))

    runtime = _optional_str(environment.get("runtime"), "environment.runtime")
    if runtime is not None and runtime not in KNOWN_RUNTIMES:
        raise RequestError("unknown_runtime", f"unknown runtime {runtime!r}",
                           accepted=sorted(KNOWN_RUNTIMES))

    limit = payload.get("limit")
    if limit is None:
        limit = DEFAULT_LIMIT
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise RequestError("invalid_request", "limit must be an integer")
    if limit < 0:
        raise RequestError("invalid_request", "limit must be nonnegative")
    if limit > MAX_LIMIT:
        raise RequestError("invalid_request", f"limit must be at most {MAX_LIMIT}")

    price_sensitivity = _optional_number(
        constraints.get("price_sensitivity"), "constraints.price_sensitivity") or 0.0
    if not 0.0 <= price_sensitivity <= 1.0:
        raise RequestError("invalid_request",
                           "constraints.price_sensitivity must be between 0 and 1")

    max_cost = _optional_number(
        constraints.get("max_cost_per_million_input_tokens"),
        "constraints.max_cost_per_million_input_tokens")
    if max_cost is not None and max_cost < 0:
        raise RequestError("invalid_request",
                           "constraints.max_cost_per_million_input_tokens must be nonnegative")

    asked_open_weights = _optional_bool(constraints.get("open_weights"),
                                        "constraints.open_weights")
    include_rehosts = bool(_optional_bool(constraints.get("include_rehosts"),
                                          "constraints.include_rehosts"))

    # Where open_weights came from, so the response can say so rather than
    # leaving the caller to work out why their managed-API request only
    # returned downloadable models.
    open_weights_only = bool(asked_open_weights)
    open_weights_because = "constraints.open_weights" if asked_open_weights else None
    if hosting is not None and HOSTING_MODES[hosting]["open_weights"]:
        open_weights_only = True
        open_weights_because = open_weights_because or "environment.hosting"
    if runtime is not None and runtime in LOCAL_RUNTIMES:
        open_weights_only = True
        open_weights_because = open_weights_because or "environment.runtime"

    unbound = []
    if runtime is not None and runtime not in LOCAL_RUNTIMES:
        unbound.append({
            "field": "environment.runtime", "value": runtime,
            "why": "the published export carries no runtime-level evidence, so this "
                   "is recorded and not used as a filter",
        })
    if hosting == "managed_api":
        unbound.append({
            "field": "environment.hosting", "value": hosting,
            "why": "a managed API imposes no weights requirement, so this narrows nothing",
        })

    return {
        "use_case": use_case,
        "limit": limit,
        "hardware_id": hardware,
        "hosting": hosting,
        "runtime": runtime,
        "open_weights_only": open_weights_only,
        "open_weights_because": open_weights_because,
        "max_cost": max_cost,
        # `rank_report` reads the profile's own weight when this is None, and
        # every shipped profile carries 0.0. Matching the CLI exactly: it passes
        # `cost_weight=price_sensitivity or None`.
        "cost_weight": price_sensitivity or None,
        "price_sensitivity": price_sensitivity,
        "include_rehosts": include_rehosts,
        "unbound": unbound,
    }


# ── the catalogue ────────────────────────────────────────────────────────────

def candidates_from_export(export: dict[str, Any]) -> list[Candidate]:
    """Rebuild ranking records from `/api/rank/candidates.json`.

    Field for field what `cli.modelspec.offline._candidates` does with the same
    file out of the local snapshot. Both feed the same `Candidate`, which is why
    the rows that come out are the same rows.
    """
    return [
        Candidate(
            model_id=c["model_id"], display_name=c["display_name"], provider=c["provider"],
            model_type=c.get("model_type"), model_subtypes=c.get("model_subtypes") or [],
            benchmark_scores=c.get("benchmark_scores") or {},
            capability_tiers=c.get("capability_tiers") or {},
            cost_input=c.get("cost_input"), context_window=c.get("context_window"),
            open_weights=bool(c.get("open_weights")), scores_as_of=c.get("scores_as_of"),
            fits=c.get("fits") or {},
            verified_benchmarks=set(c.get("verified_benchmarks") or []),
            rehost_of=c.get("rehost_of"), release_date=c.get("release_date"),
        )
        for c in export["candidates"]
    ]


def hardware_ids(hardware_export: dict[str, Any] | None) -> set[str]:
    """Device ids from `/api/rank/hardware.json`, or none when it is absent.

    An export from before MODEL-68 has no such file. The endpoint still ranks;
    it just cannot tell a typo'd device from a device nothing fits on, so it
    refuses `environment.hardware` outright rather than silently answering the
    wrong question.
    """
    if not hardware_export:
        return set()
    return {str(d["id"]) for d in hardware_export.get("hardware", []) if d.get("id")}


# ── the answer ───────────────────────────────────────────────────────────────

def _eliminations(pool: list[Candidate], request: dict[str, Any]) -> list[dict[str, Any]]:
    """Re-apply each filter alone, in the order the ranking applies them.

    The first step whose `survivors_after` is zero is the constraint that
    eliminated the pool. Applied in the same sequence as the CLI: `--max-cost`
    narrows the pool before `rank_report`, which then drops rehosts, then
    non-open weights, then anything that does not fit the device.
    """
    steps: list[dict[str, Any]] = []
    surviving = pool

    def step(constraint: str, value: Any, keep) -> None:
        nonlocal surviving
        before = len(surviving)
        surviving = [c for c in surviving if keep(c)]
        steps.append({
            "constraint": constraint, "value": value,
            "survivors_before": before, "survivors_after": len(surviving),
        })

    if request["max_cost"] is not None:
        limit = request["max_cost"]
        step("constraints.max_cost_per_million_input_tokens", limit,
             lambda c: c.cost_input is not None and c.cost_input <= limit)
    if not request["include_rehosts"]:
        step("constraints.include_rehosts", False, lambda c: not c.rehost_of)
    if request["open_weights_only"]:
        step(request["open_weights_because"] or "constraints.open_weights", True,
             lambda c: c.open_weights)
    if request["hardware_id"]:
        device = request["hardware_id"]
        step("environment.hardware", device, lambda c: device in c.fits)
    return steps


def _no_match(report: dict[str, Any], steps: list[dict[str, Any]],
              total: int) -> dict[str, Any]:
    """Which constraint did it, and what to relax. Never a bare empty list."""
    emptied = next((s for s in steps if s["survivors_after"] == 0), None)
    policy = report["policy"]
    if emptied is not None:
        return {
            "code": "no_match",
            "ranking_status": report["ranking_status"],
            "message": (
                f"no model survives {emptied['constraint']}"
                f"={emptied['value']!r}: it took the pool from "
                f"{emptied['survivors_before']} to 0."
            ),
            "eliminated_by": emptied,
            "elimination_trace": steps,
            "relax": emptied["constraint"],
            "candidates_considered": total,
        }
    # Everything survived the filters and still nothing could be ordered. That
    # is the evidence floor, and saying "no match" without naming it would send
    # the caller off loosening constraints that were never the problem.
    survivors = steps[-1]["survivors_after"] if steps else total
    return {
        "code": "insufficient_evidence",
        "ranking_status": report["ranking_status"],
        "message": (
            f"{survivors} model(s) match the request, but none has enough benchmark "
            f"evidence for this use case to be ordered honestly: the floor is "
            f"{policy['min_benchmark_coverage']:.0%} weighted benchmark coverage and "
            f"{policy['min_benchmark_count']} benchmarks."
        ),
        "eliminated_by": {
            "constraint": "policy.min_benchmark_coverage",
            "value": policy["min_benchmark_coverage"],
            "survivors_before": survivors,
            "survivors_after": 0,
        },
        "elimination_trace": steps,
        "relax": "use_case",
        "candidates_considered": total,
    }


def _build_block(export: dict[str, Any]) -> dict[str, Any]:
    """`build.commit` and `export_schema_version` ride on every response."""
    build = export.get("build") or {}
    return {
        "commit": build.get("commit"),
        "built_at": build.get("built_at"),
        "eligibility_as_of": build.get("eligibility_as_of"),
        "export_schema_version": build.get("export_schema_version"),
    }


def _envelope(export: dict[str, Any], service_commit: str, origin: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "endpoint": "rank",
        "build": _build_block(export),
        "service_commit": service_commit,
        "export_origin": origin,
    }


def authoring_guide_block(model_id: str | None, export: dict[str, Any]) -> dict[str, Any]:
    """The recommended model's card guide, or a documented absent state.

    Reads `/api/rank/candidates.json`.`authoring_guides` (MODEL-81). Serves the
    card payload as exported — sources and `accessed` dates included. Does not
    generate claims. A stale guide is labelled `stale`, never `current`.
    """
    if not model_id:
        return {
            "state": GUIDE_STATE_ABSENT,
            "model_id": None,
            "why": GUIDE_WHY_NO_RECOMMENDATION,
            "guide": None,
        }
    guides = export.get("authoring_guides")
    raw = guides.get(model_id) if isinstance(guides, dict) else None
    if not isinstance(raw, dict):
        return {
            "state": GUIDE_STATE_ABSENT,
            "model_id": model_id,
            "why": GUIDE_WHY_NO_GUIDE,
            "guide": None,
        }
    status = raw.get("status")
    if status == GUIDE_STATE_STALE:
        state = GUIDE_STATE_STALE
    elif status == GUIDE_STATE_CURRENT:
        state = GUIDE_STATE_CURRENT
    else:
        return {
            "state": GUIDE_STATE_ABSENT,
            "model_id": model_id,
            "why": GUIDE_WHY_NO_GUIDE,
            "guide": None,
        }
    return {
        "state": state,
        "model_id": model_id,
        "why": None,
        "guide": raw,
    }


def error_response(error: RequestError, export: dict[str, Any] | None,
                   service_commit: str, origin: str) -> tuple[int, dict[str, Any]]:
    envelope = _envelope(export or {}, service_commit, origin)
    body: dict[str, Any] = {"code": error.code, "message": error.message}
    body.update(error.detail)
    return error.status, {**envelope, "error": body, "result": []}


def rank(payload: Any, export: dict[str, Any], hardware_export: dict[str, Any] | None,
         service_commit: str, origin: str) -> tuple[int, dict[str, Any]]:
    """Answer one `POST /v1/rank`. Returns the status code and the body."""
    envelope = _envelope(export, service_commit, origin)
    request = parse_request(payload, hardware_ids(hardware_export))
    pool = candidates_from_export(export)
    total = len(pool)

    narrowed = pool
    if request["max_cost"] is not None:
        # Exactly where and how the CLI applies it, before `rank_report`.
        narrowed = [c for c in narrowed
                    if c.cost_input is not None and c.cost_input <= request["max_cost"]]

    report = rank_report(
        narrowed, request["use_case"], limit=request["limit"],
        open_weights_only=request["open_weights_only"],
        hardware_id=request["hardware_id"],
        cost_weight=request["cost_weight"],
        include_rehosts=request["include_rehosts"],
    )

    common = {
        **envelope,
        "request": {
            "use_case": request["use_case"],
            "environment": {"hardware": request["hardware_id"], "hosting": request["hosting"],
                            "runtime": request["runtime"]},
            "constraints": {
                "open_weights": request["open_weights_only"],
                "max_cost_per_million_input_tokens": request["max_cost"],
                "price_sensitivity": request["price_sensitivity"],
                "include_rehosts": request["include_rehosts"],
            },
            "limit": request["limit"],
        },
        "applied": {
            "open_weights_only": request["open_weights_only"],
            "open_weights_required_by": request["open_weights_because"],
            "hardware_id": request["hardware_id"],
            "max_cost_per_million_input_tokens": request["max_cost"],
            "cost_weight": request["cost_weight"],
            "include_rehosts": request["include_rehosts"],
            "unbound": request["unbound"],
        },
        "policy": ranking_policy(),
        "profile": report["profile"],
        "ranking_status": report["ranking_status"],
        "ranked_count": report["ranked_count"],
        "unranked_count": report["unranked_count"],
        # MODEL-110: the models this ranking could not order, named. Straight
        # from `rank_report`, on a 200 and a 422 alike.
        "unranked_candidates": report["unranked_candidates"],
        "candidates_considered": total,
        "authoring_guide": authoring_guide_block(
            report["ranked"][0]["model_id"] if report["ranked"] else None, export),
    }

    if report["ranking_status"] in {"empty", "unavailable"}:
        steps = _eliminations(pool, request)
        return HTTP_NO_MATCH, {**common, "error": _no_match(report, steps, total),
                               "result": []}

    return HTTP_OK, {**common, "result": report["ranked"]}
