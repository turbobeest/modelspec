#!/usr/bin/env python3
"""Assert what a live `POST /v1/rank` response must contain (MODEL-68).

Called by the smoke test in `.github/workflows/rank-api.yml` after a deploy. It
lives in a file rather than inside the workflow so that the assertions are
reviewable, testable and identical between the two shapes of answer.

It fails loudly, prints the body it rejected, and never passes on a missing
field: the whole point of MODEL-9's scar is that a smoke test which cannot fail
is worse than none, because it reports success for a deployment nobody exercised.

    check_rank_response.py ranked body.json
    check_rank_response.py no-match body.json
"""

from __future__ import annotations

import json
import sys
from typing import Any

#: `pipeline.ranking._basis` produces exactly these. A value outside the set
#: means the deployed Worker is not running that function.
EVIDENCE_BASIS = {"none", "unverified-legacy", "mixed", "partial-verified", "verified"}

#: `pipeline.export.EXPORT_SCHEMA_VERSION`, as the published tree reports it.
EXPORT_SCHEMA_VERSION = "2.0"

#: `api.ranking.engine.MIN_BENCHMARK_COVERAGE` and `MIN_BENCHMARK_COUNT`. These
#: are product defaults and changing one needs Jamie; a deployment serving
#: anything else is a deployment to roll back, so the check is deliberately
#: literal here even though nothing in the Worker is.
MIN_BENCHMARK_COVERAGE = 0.50
MIN_BENCHMARK_COUNT = 2


def _check_envelope(body: dict[str, Any]) -> list[str]:
    problems = []
    build = body.get("build") or {}
    if not build.get("commit"):
        problems.append("build.commit is missing")
    if build.get("export_schema_version") != EXPORT_SCHEMA_VERSION:
        problems.append(
            f"export_schema_version is {build.get('export_schema_version')!r}, "
            f"not {EXPORT_SCHEMA_VERSION!r}")
    if not body.get("service_commit"):
        problems.append("service_commit is missing")
    return problems


def check_ranked(body: dict[str, Any]) -> list[str]:
    problems = _check_envelope(body)
    rows = body.get("result")
    if not isinstance(rows, list) or not rows:
        problems.append("a 200 returned no rows, which it must never do")
        rows = []
    for row in rows:
        for key in ("model_id", "score", "rank", "cost_input", "evidence_basis"):
            if key not in row:
                problems.append(f"row {row.get('model_id')!r} has no {key}")
        if row.get("evidence_basis") not in EVIDENCE_BASIS:
            problems.append(
                f"row {row.get('model_id')!r} has evidence_basis "
                f"{row.get('evidence_basis')!r}, which `_basis` never produces")
    policy = body.get("policy") or {}
    if policy.get("min_benchmark_coverage") != MIN_BENCHMARK_COVERAGE:
        problems.append(
            f"the served coverage floor is {policy.get('min_benchmark_coverage')!r}, "
            f"not {MIN_BENCHMARK_COVERAGE}")
    if policy.get("min_benchmark_count") != MIN_BENCHMARK_COUNT:
        problems.append(
            f"the served count floor is {policy.get('min_benchmark_count')!r}, "
            f"not {MIN_BENCHMARK_COUNT}")
    return problems


def check_no_match(body: dict[str, Any]) -> list[str]:
    problems = _check_envelope(body)
    if body.get("result") != []:
        problems.append("a no-match answer carried rows")
    error = body.get("error") or {}
    if not (error.get("eliminated_by") or {}).get("constraint"):
        problems.append("nothing said which constraint eliminated the pool")
    if not error.get("relax"):
        problems.append("the caller is not told what to relax")
    if not error.get("elimination_trace"):
        problems.append("there is no elimination trace to read")
    return problems


CHECKS = {"ranked": check_ranked, "no-match": check_no_match}


def main(argv: list[str]) -> int:
    if len(argv) != 3 or argv[1] not in CHECKS:
        print(f"usage: {argv[0]} {{{'|'.join(CHECKS)}}} BODY.json", file=sys.stderr)
        return 2
    kind, path = argv[1], argv[2]
    try:
        with open(path, encoding="utf-8") as handle:
            body = json.load(handle)
    except (OSError, ValueError) as exc:
        print(f"::error::the {kind} response is unreadable: {exc}")
        return 1

    problems = CHECKS[kind](body)
    if problems:
        print(f"::error::the deployed {kind} response is wrong: " + "; ".join(problems))
        print(json.dumps(body)[:4000])
        return 1

    if kind == "ranked":
        print(f"ranked {len(body['result'])} rows from build {body['build']['commit'][:12]}")
    else:
        print("no-match names " + body["error"]["eliminated_by"]["constraint"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
