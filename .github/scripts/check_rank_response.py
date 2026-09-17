#!/usr/bin/env python3
"""Read a live rank-API response, and say what it actually was (MODEL-68).

Called by the smoke test in `.github/workflows/rank-api.yml` after a deploy. It
lives in a file rather than inside the workflow so that the assertions are
reviewable, testable and identical between the shapes of answer.

It fails loudly, prints the body it rejected, and never passes on a missing
field: the whole point of MODEL-9's scar is that a smoke test which cannot fail
is worse than none, because it reports success for a deployment nobody exercised.

The second scar is this file's own. MODEL-68's deploy of `e0265a5` went red on a
Worker that was live and correct, because the workflow parsed every response
inline with `json.loads` and the first one it read was Cloudflare's `error code:
522` page — the route had been published 100 ms earlier and had not reached the
edge yet. A `JSONDecodeError` traceback under `bash -e` killed the step before
the retry loop got a second turn. So *nothing here raises on a body*: an
unreadable response is a described fact (status, requested path, first bytes),
which the caller then decides is either worth retrying or worth failing on.

    check_rank_response.py ranked BODY.json [REQUEST_PATH] [STATUS]
    check_rank_response.py no-match BODY.json [REQUEST_PATH] [STATUS]
    check_rank_response.py not-found BODY.json [REQUEST_PATH] [STATUS]
    check_rank_response.py field NAME BODY.json      # always exits 0
    check_rank_response.py digest REQUEST_PATH STATUS BODY.json
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

#: The versioned endpoints a 404 has to name. Same list as `api/worker/src/entry.py`.
ACCEPTED_ENDPOINTS = ("POST /v1/rank", "GET /v1/health")

#: How much of a body to quote. Enough to recognise a Cloudflare error page, an
#: HTML redirect or a truncated JSON document; short enough for one `::error::`
#: line, which GitHub renders only up to the first newline anyway.
SNIPPET_BYTES = 200


# ── reading a response without ever raising on it ────────────────────────────

def read_body(path: str) -> tuple[Any, bytes, str | None]:
    """Return ``(parsed, raw, problem)``.

    ``problem`` is None only when ``raw`` parsed as JSON. Nothing here raises:
    an unreachable host, an empty file and Cloudflare's `error code: 522` page
    are all ordinary answers that the caller has to be able to describe.
    """
    try:
        with open(path, "rb") as handle:
            raw = handle.read()
    except OSError as exc:
        return None, b"", f"the body file could not be read: {exc}"
    text = raw.decode("utf-8", "replace").strip()
    if not text:
        return None, raw, "the body is empty"
    try:
        return json.loads(text), raw, None
    except ValueError as exc:
        return None, raw, f"the body is not JSON ({exc})"


def snippet(raw: bytes) -> str:
    """The first bytes of a body, collapsed onto one annotation-safe line."""
    if not raw:
        return "<empty>"
    text = " ".join(raw[:SNIPPET_BYTES].decode("utf-8", "replace").split())
    if len(raw) > SNIPPET_BYTES:
        text += f" ... (+{len(raw) - SNIPPET_BYTES} more bytes)"
    return text or "<whitespace only>"


def describe(request_path: str | None, status: str | None, raw: bytes,
             problem: str | None = None) -> str:
    """What the last response was, in one line.

    The requested *path* rather than the full URL: the host is in the workflow's
    env and a query string is not, so this stays safe to paste into a public run
    log no matter what a future check appends to a request.
    """
    parts = [f"HTTP {status or 'none'}", f"path {request_path or '?'}",
             f"{len(raw)} bytes"]
    if problem:
        parts.append(problem)
    parts.append(f"body starts: {snippet(raw)}")
    return "; ".join(parts)


# ── what each shape of answer must contain ───────────────────────────────────

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


def check_not_found(body: dict[str, Any]) -> list[str]:
    """An unrouted path is an answer too.

    No `build` here on purpose: a 404 must not cost a subrequest to the export
    just to tell a crawler where the endpoints are. What it owes the caller is
    the version answering and the versioned paths that do exist.
    """
    problems = []
    if not body.get("service_commit"):
        problems.append("service_commit is missing")
    error = body.get("error") or {}
    if error.get("code") != "not_found":
        problems.append(f"the error code is {error.get('code')!r}, not 'not_found'")
    accepted = error.get("accepted") or []
    for endpoint in ACCEPTED_ENDPOINTS:
        if endpoint not in accepted:
            problems.append(f"the 404 does not name {endpoint}")
    if body.get("result") != []:
        problems.append("a 404 carried rows")
    return problems


CHECKS = {"ranked": check_ranked, "no-match": check_no_match,
          "not-found": check_not_found}

USAGE = """usage:
  check_rank_response.py {ranked|no-match|not-found} BODY.json [REQUEST_PATH] [STATUS]
  check_rank_response.py field NAME BODY.json
  check_rank_response.py digest REQUEST_PATH STATUS BODY.json"""


def _run_check(kind: str, path: str, request_path: str | None,
               status: str | None) -> int:
    body, raw, problem = read_body(path)
    if problem is not None:
        print(f"::error::the {kind} response could not be read: "
              + describe(request_path, status, raw, problem))
        return 1
    if not isinstance(body, dict):
        print(f"::error::the {kind} response is not a JSON object: "
              + describe(request_path, status, raw, f"it is a {type(body).__name__}"))
        return 1

    problems = CHECKS[kind](body)
    if problems:
        print(f"::error::the deployed {kind} response is wrong "
              f"(HTTP {status or 'none'}, path {request_path or '?'}): "
              + "; ".join(problems))
        print(json.dumps(body)[:4000])
        return 1

    if kind == "ranked":
        print(f"ranked {len(body['result'])} rows from build {body['build']['commit'][:12]}")
    elif kind == "no-match":
        print("no-match names " + body["error"]["eliminated_by"]["constraint"])
    else:
        print("not-found names " + ", ".join(body["error"]["accepted"]))
    return 0


def _field(name: str, path: str) -> int:
    """One top-level field, or an empty line. Always exits 0.

    The poll loop reads this inside ``x=$(...)`` under ``bash -e``, so a
    non-zero exit here would abort the step rather than let it retry — which is
    precisely how a healthy deploy was reported as a failure.
    """
    body, raw, problem = read_body(path)
    if problem is not None or not isinstance(body, dict):
        print(f"note: {name} is unknown because {problem or 'the body is not an object'}"
              f"; body starts: {snippet(raw)}", file=sys.stderr)
        print("")
        return 0
    value = body.get(name)
    print("" if value is None else value)
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(USAGE, file=sys.stderr)
        return 2
    mode = argv[1]

    if mode == "field":
        if len(argv) != 4:
            print(USAGE, file=sys.stderr)
            return 2
        return _field(argv[2], argv[3])

    if mode == "digest":
        if len(argv) != 5:
            print(USAGE, file=sys.stderr)
            return 2
        request_path, status, path = argv[2], argv[3], argv[4]
        _, raw, problem = read_body(path)
        print(describe(request_path, status, raw, problem))
        return 0

    if mode not in CHECKS or not 3 <= len(argv) <= 5:
        print(USAGE, file=sys.stderr)
        return 2
    return _run_check(mode, argv[2],
                      argv[3] if len(argv) > 3 else None,
                      argv[4] if len(argv) > 4 else None)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
