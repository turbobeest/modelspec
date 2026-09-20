#!/usr/bin/env python3
"""Assert what a live `POST /v1/policy-check` response must contain (MODEL-80).

Called by the smoke test in `.github/workflows/rank-api.yml` after a deploy, and
written as a file rather than inline in the workflow for the same reason as
`check_rank_response.py`: the assertions are the contract, and a contract
belongs somewhere reviewable.

What it is actually guarding is the one way this endpoint can fail
catastrophically and quietly — an `undetermined` that a consumer can read as a
`pass`. So the checks are structural. A row that says `verdict: undetermined`
must carry **no** `passed` key, and a check that says `state: undetermined` must
carry **no** `satisfied` key. If a future change makes those keys optional
rather than exclusive, this fails the deploy.

    check_policy_response.py verdicts     BODY.json [REQUEST_PATH] [STATUS]
    check_policy_response.py undetermined BODY.json [REQUEST_PATH] [STATUS]

Reading the response is `check_rank_response.py`'s job, borrowed wholesale so
that both scripts describe an unreadable answer in the same words (MODEL-68
follow-up). Nothing here raises on a body either: a Cloudflare `error code:
522` page, an empty file and a JSON array are all things a live host really
answers, and each becomes an `::error::` line naming the status, the requested
path and the first bytes — never a traceback.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

#: `pipeline.export.EXPORT_SCHEMA_VERSION`, as the published tree reports it.
EXPORT_SCHEMA_VERSION = "3.0"

VERDICT_KEY = {"pass": "passed", "fail": "failed", "undetermined": "undetermined"}
STATE_KEY = {"satisfied": "satisfied", "violated": "violated",
             "undetermined": "undetermined"}


def _check_envelope(body: dict[str, Any]) -> list[str]:
    problems = []
    build = body.get("build") or {}
    if not build.get("commit"):
        problems.append("build.commit is missing, so the answer cannot be audited later")
    if build.get("export_schema_version") != EXPORT_SCHEMA_VERSION:
        problems.append(
            f"export_schema_version is {build.get('export_schema_version')!r}, "
            f"not {EXPORT_SCHEMA_VERSION!r}")
    if not body.get("service_commit"):
        problems.append("service_commit is missing")
    determinations = body.get("determinations")
    if not isinstance(determinations, dict):
        problems.append("the response does not say which tier answered it")
    else:
        if "included" not in determinations:
            problems.append("determinations.included is missing, so the free/paid "
                            "difference is not legible")
        if not determinations.get("included") and not determinations.get("why"):
            problems.append("a free-tier answer does not say what it could not see")
    return problems


def _check_rows(body: dict[str, Any]) -> list[str]:
    """The exclusivity that keeps `undetermined` from being read as `pass`."""
    problems = []
    for row in body.get("result") or []:
        verdict = row.get("verdict")
        if verdict not in VERDICT_KEY:
            problems.append(f"row {row.get('model_id')!r} has verdict {verdict!r}")
            continue
        expected = VERDICT_KEY[verdict]
        present = [key for key in VERDICT_KEY.values() if key in row]
        if present != [expected]:
            problems.append(
                f"row {row.get('model_id')!r} is {verdict!r} but carries {present!r}; "
                f"exactly {expected!r} must be present")
        if "platform" not in row:
            problems.append(f"row {row.get('model_id')!r} has no platform, so the "
                            "verdict is not per platform")
        for check in row.get("checks") or []:
            state = check.get("state")
            if state not in STATE_KEY:
                problems.append(f"check {check.get('constraint')!r} has state {state!r}")
                continue
            carried = [key for key in STATE_KEY.values() if key in check]
            if carried != [STATE_KEY[state]]:
                problems.append(
                    f"check {check.get('constraint')!r} is {state!r} but carries "
                    f"{carried!r}")
            if state == "violated":
                violated = check["violated"]
                if not violated.get("because"):
                    problems.append(f"a violated {check['constraint']!r} does not say why")
                source = violated.get("source")
                if source is not None and not source.get("read_on"):
                    problems.append(
                        f"a violated {check['constraint']!r} cites a source with no "
                        "read date")
    return problems


def check_verdicts(body: dict[str, Any]) -> list[str]:
    problems = _check_envelope(body) + _check_rows(body)
    summary = body.get("summary") or {}
    if not summary.get("rows"):
        problems.append("the summary reports no rows for a whole-catalogue policy")
    verdicts = summary.get("verdicts") or {}
    if set(verdicts) != {"pass", "fail", "undetermined"}:
        problems.append(f"summary.verdicts is {sorted(verdicts)!r}; all three states "
                        "must be counted, always")
    if sum(verdicts.values()) != summary.get("rows"):
        problems.append("summary.verdicts does not add up to summary.rows")
    if "provenance" not in body:
        problems.append("the response carries no provenance block")
    return problems


def check_undetermined(body: dict[str, Any]) -> list[str]:
    """`require_no_undetermined` must be a hard failure, not a soft one."""
    problems = _check_envelope(body)
    error = body.get("error") or {}
    if error.get("code") != "undetermined_present":
        problems.append(f"the 422 code is {error.get('code')!r}, "
                        "not 'undetermined_present'")
    if not error.get("undetermined_rows"):
        problems.append("the refusal does not say how many rows are undetermined")
    if not error.get("undetermined_by_constraint"):
        problems.append("the refusal does not say which constraints are undetermined")
    if body.get("result"):
        problems.append("a refused request returned rows, which makes it a soft failure")
    return problems


CHECKS = {"verdicts": check_verdicts, "undetermined": check_undetermined}

USAGE = """usage:
  check_policy_response.py {verdicts|undetermined} BODY.json [REQUEST_PATH] [STATUS]"""


def _reader():
    """`check_rank_response.py`, loaded from beside this file.

    One implementation of "what was this response, really", so a 522 on
    `/v1/policy-check` reads exactly like a 522 on `/v1/rank` in the run log.
    """
    import importlib.util

    path = Path(__file__).resolve().with_name("check_rank_response.py")
    spec = importlib.util.spec_from_file_location("modelspec_check_rank_response", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv: list[str]) -> int:
    if not 3 <= len(argv) <= 5 or argv[1] not in CHECKS:
        print(USAGE, file=sys.stderr)
        return 2
    kind, path = argv[1], argv[2]
    request_path = argv[3] if len(argv) > 3 else None
    status = argv[4] if len(argv) > 4 else None

    reader = _reader()
    body, raw, problem = reader.read_body(path)
    if problem is None and not isinstance(body, dict):
        problem = f"the body is a {type(body).__name__}, not a JSON object"
    if problem is not None:
        print(f"::error::the {kind} response could not be read: "
              + reader.describe(request_path, status, raw, problem))
        return 1

    problems = CHECKS[kind](body)
    if problems:
        print(f"::error::the deployed {kind} response is wrong "
              f"(HTTP {status or 'none'}, path {request_path or '?'}): "
              + "; ".join(problems))
        print(json.dumps(body)[:4000])
        return 1

    if kind == "verdicts":
        summary = body["summary"]
        print(f"policy-check: {summary['rows']} rows, {summary['verdicts']}, "
              f"determinations included: {body['determinations']['included']}")
    else:
        print("require_no_undetermined refused with "
              f"{body['error']['undetermined_rows']} undetermined rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
