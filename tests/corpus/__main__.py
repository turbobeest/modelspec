"""Run the decision spec corpus outside pytest (MODEL-203).

    python -m tests.corpus decisions --out DIR [--cache DIR]
        The Worker's answer to every case, one <case>.json each, plus the page
        vocabulary of each snapshot, for the web suite and Playwright.
    python -m tests.corpus wait-worker --origin https://api.modelspec.dev --commit SHA
        Wait up to --minutes for /v1/health to report SHA; warn, never fail.
    python -m tests.corpus live --origin https://api.modelspec.dev --out DIR
        POST the `live: true` cases to a deployed Worker and check each answer.
    python -m tests.corpus cli-matrix --modelspec PATH --work DIR
        Drive an installed `modelspec` (a clean install of the built wheel)
        against the published snapshot.

Failures print GitHub `::error::` lines and exit 1.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from tests.corpus.corpus import load_cases, payload, problems, write_decisions

#: Transient answers from a Worker mid-deploy: retried, never judged.
RETRY_STATUSES = {0, 500, 502, 503, 522, 524}
#: Cloudflare refuses urllib's default user agent.
USER_AGENT = "modelspec-corpus-smoke"


def _error(message: str) -> None:
    print(f"::error::{message}", flush=True)


def _decisions(args) -> int:
    index = write_decisions(Path(args.out), load_cases(), Path(args.cache) if args.cache else None)
    print(f"wrote {len(index['cases'])} decisions and "
          f"{len(index['vocabularies'])} vocabularies to {args.out}")
    return 0


def _post(url: str, body: bytes) -> tuple[int, bytes]:
    request = urllib.request.Request(url, data=body, method="POST", headers={
        "content-type": "application/json", "user-agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()
    except (urllib.error.URLError, TimeoutError) as exc:
        return 0, str(exc).encode()


def _wait_worker(args) -> int:
    """rank-api.yml deploys the Worker from the same push. Test the pair that
    will serve, but an older Worker is still what visitors get: warn and go on."""
    url = args.origin.rstrip("/") + "/v1/health"
    deadline = time.monotonic() + args.minutes * 60
    commit = None
    while time.monotonic() < deadline:
        try:
            request = urllib.request.Request(url, headers={"user-agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=10) as response:
                commit = json.loads(response.read()).get("service_commit")
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            commit = f"unreachable ({exc})"
        if commit == args.commit:
            print(f"the Worker is on {args.commit}")
            return 0
        time.sleep(10)
    print(f"::warning::the Worker never reported {args.commit} (last: {commit}); "
          "testing the Worker that is serving", flush=True)
    return 0


def _live(args) -> int:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    url = args.origin.rstrip("/") + "/v1/decide"
    cases = [case for case in load_cases() if case.live]
    index, failed = {"cases": [], "vocabularies": {}}, 0
    for case in cases:
        body = json.dumps(payload(case)).encode()
        for attempt in range(args.attempts):
            status, raw = _post(url, body)
            if status not in RETRY_STATUSES:
                break
            time.sleep(10 * (attempt + 1))
        try:
            answer = json.loads(raw)
        except ValueError:
            answer = {"error": f"not JSON: {raw[:200]!r}"}
        found = problems(case, status, answer)
        if found:
            failed += 1
            _error(f"POST {url} {case.id} ({case.intent}): {'; '.join(found)}")
        else:
            print(f"ok   {case.id}: HTTP {status} {answer.get('status') or ''}".rstrip())
        (out / f"{case.id}.json").write_bytes(raw)
        index["cases"].append({"id": case.id, "intent": case.intent, "snapshot": "live",
                               "http": status, "file": f"{case.id}.json"})
    (out / "index.json").write_text(json.dumps(index, indent=1) + "\n", encoding="utf-8")
    print(f"{len(cases) - failed} of {len(cases)} live cases answered as expected")
    return 1 if failed else 0


class _Matrix:
    def __init__(self, modelspec: str, work: Path):
        self.modelspec = modelspec
        self.env = os.environ | {"MODELSPEC_CACHE": str(work / "cache"), "NO_COLOR": "1",
                                 "COLUMNS": "200"}
        self.work = work
        self.failed = 0

    def run(self, *argv: str) -> subprocess.CompletedProcess:
        return subprocess.run([self.modelspec, *argv], env=self.env, capture_output=True,
                              text=True, timeout=300, check=False)

    def check(self, label: str, ok: bool, detail: str = "") -> bool:
        if ok:
            print(f"ok   {label}")
        else:
            self.failed += 1
            _error(f"modelspec {label}: {detail[:500]}")
        return ok


def _cli_matrix(args) -> int:
    work = Path(args.work)
    work.mkdir(parents=True, exist_ok=True)
    m = _Matrix(args.modelspec, work)

    fetched = m.run("snapshot", "fetch", "--json")
    decision = {}
    if m.check("snapshot fetch --json", fetched.returncode == 0, fetched.stderr):
        decision = json.loads(fetched.stdout)["result"]["decision_snapshot"]
        m.check("snapshot fetch: signature_verified", decision.get("signature_verified") is True,
                json.dumps(decision))
    if not decision.get("available"):
        _error("no decision snapshot was fetched; the rest of the matrix cannot run")
        return 1

    vocab = m.run("vocab", "--json")
    m.check("vocab --json", vocab.returncode == 0 and "result" in json.loads(vocab.stdout or "{}"),
            vocab.stderr)
    listed = m.run("vocab", "templates", "--json")
    templates = []
    if m.check("vocab templates --json", listed.returncode == 0, listed.stderr):
        templates = [row["id"] for row in json.loads(listed.stdout)["result"]]
        m.check("vocab lists templates", bool(templates), listed.stdout[:300])
    human = m.run("vocab", "templates")
    m.check("vocab templates", human.returncode == 0 and all(t in human.stdout for t in templates),
            human.stdout + human.stderr)

    top = None
    for template in templates:
        for level in ("none", "summary", "full"):
            ran = m.run("decide", "--template", template, "--explain", level, "--json")
            label = f"decide --template {template} --explain {level} --json"
            if not m.check(label, ran.returncode == 0, ran.stderr):
                continue
            answer = json.loads(ran.stdout)
            m.check(f"{label}: status", answer.get("status") in
                    ("answered", "partial", "no_feasible"), ran.stdout[:300])
            m.check(f"{label}: signature_verified", answer.get("signature_verified") is True,
                    ran.stdout[:300])
            if top is None and answer.get("results"):
                top = answer["results"][0]["offering"]["model"]

    if templates:
        readable = m.run("decide", "--template", templates[0])
        m.check("decide --template (readable summary)",
                readable.returncode == 0 and readable.stdout.startswith("status: ")
                and "--why-not MODEL_ID" in readable.stdout,
                readable.stdout + readable.stderr)
    if top is not None:
        why = m.run("decide", "--template", templates[0], "--why-not", top, "--json")
        m.check(f"decide --why-not {top} --json",
                why.returncode == 0 and "why_not" in json.loads(why.stdout or "{}"), why.stderr)
        why_text = m.run("decide", "--template", templates[0], "--why-not", top)
        m.check(f"decide --why-not {top}", why_text.returncode == 0 and why_text.stdout.strip(),
                why_text.stderr)

    ok_spec = work / "ok.yaml"
    ok_spec.write_text("spec_version: 1\noptimize: {max: software_engineering}\n", encoding="utf-8")
    checked = m.run("decide", str(ok_spec), "--check", "--json")
    m.check("decide --check (valid spec)",
            checked.returncode == 0 and json.loads(checked.stdout or "{}").get("ok") is True,
            checked.stdout + checked.stderr)
    for case in load_cases():
        if case.expect.code != "invalid_spec" or case.generated:
            continue
        spec = work / f"{case.id}.yaml"
        spec.write_text(case.spec if isinstance(case.spec, str) else json.dumps(case.spec),
                        encoding="utf-8")
        ran = m.run("decide", str(spec), "--check", "--json")
        try:
            code = json.loads(ran.stderr)["error"]["code"]
        except (ValueError, KeyError, TypeError):
            code = None
        m.check(f"decide --check {case.id}",
                ran.returncode == 1 and code in ("invalid_spec", "decision_failed"),
                f"exit {ran.returncode}, code {code}: {ran.stderr}")
    unknown = m.run("decide", "--template", "no-such-template", "--json")
    m.check("decide --template no-such-template",
            unknown.returncode == 1 and '"unknown_template"' in unknown.stderr, unknown.stderr)
    print(f"CLI matrix: {m.failed} failure(s)")
    return 1 if m.failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m tests.corpus", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    decisions = commands.add_parser("decisions")
    decisions.add_argument("--out", required=True)
    decisions.add_argument("--cache")
    live = commands.add_parser("live")
    live.add_argument("--origin", required=True)
    live.add_argument("--out", required=True)
    live.add_argument("--attempts", type=int, default=4)
    wait = commands.add_parser("wait-worker")
    wait.add_argument("--origin", required=True)
    wait.add_argument("--commit", required=True)
    wait.add_argument("--minutes", type=float, default=10)
    matrix = commands.add_parser("cli-matrix")
    matrix.add_argument("--modelspec", required=True)
    matrix.add_argument("--work", required=True)
    args = parser.parse_args(argv)
    return {"decisions": _decisions, "wait-worker": _wait_worker, "live": _live,
            "cli-matrix": _cli_matrix}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
