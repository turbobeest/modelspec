"""Regression checks for the CI failure gates.

The opt-in probe is the reproducible proof that the pytest check can fail:

    MODELSPEC_CI_FAILURE_PROBE=1 .venv/bin/python -m pytest -q \
        tests/test_ci_workflows.py -k ci_failure_probe

That command must exit non-zero. The environment variable is unset during the
normal suite, so the repository never contains a permanently failing test.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = REPO_ROOT / ".github" / "workflows"


def test_ci_failure_probe() -> None:
    """Fail only when the documented probe explicitly requests it."""
    if os.environ.get("MODELSPEC_CI_FAILURE_PROBE") == "1":
        pytest.fail("intentional CI failure probe")


def _on_block(workflow_text: str) -> str:
    """The GitHub `on:` mapping, which is what decides whether a check reports."""
    after_on = workflow_text.split("\non:", 1)[1]
    return after_on.split("\njobs:", 1)[0]


def test_pytest_workflow_runs_the_test_command_without_masking_it() -> None:
    workflow = (WORKFLOWS / "test.yml").read_text(encoding="utf-8")

    assert "run: python -m pytest -q -n auto --dist loadfile" in workflow
    assert "continue-on-error" not in workflow
    assert "|| true" not in workflow
    assert "2>/dev/null" not in workflow


def test_required_check_job_names_match_branch_protection() -> None:
    """Main requires these exact check names (GitHub Actions app 15368)."""
    test_workflow = (WORKFLOWS / "test.yml").read_text(encoding="utf-8")
    deploy_workflow = (WORKFLOWS / "deploy-sites.yml").read_text(encoding="utf-8")
    assert "    name: Run pytest\n" in test_workflow
    assert "    name: Build both sites\n" in deploy_workflow


def test_required_workflows_run_on_every_pull_request() -> None:
    """A path filter on a required job leaves the check pending and deadlocks merge."""
    for name in ("test.yml", "deploy-sites.yml"):
        on_block = _on_block((WORKFLOWS / name).read_text(encoding="utf-8"))
        assert "pull_request:" in on_block, f"{name} is not triggered by pull_request"
        assert "paths:" not in on_block, f"{name} still filters pull_request by path"


def test_site_build_guards_pages_limits_before_deploy() -> None:
    workflow = (WORKFLOWS / "deploy-sites.yml").read_text(encoding="utf-8")
    assert "size +25M" in workflow
    assert "20000" in workflow
    assert "if: github.ref == 'refs/heads/main' && github.event_name != 'pull_request'" in workflow


def test_validation_workflow_checks_status_and_report_shape() -> None:
    workflow = (WORKFLOWS / "validate-cards.yml").read_text(encoding="utf-8")
    masked_validator = (
        "python scripts/validate_pr.py > validation_output.json "
        "2>validation_stderr.txt || true"
    )

    assert masked_validator not in workflow
    assert "validation_status=$?" in workflow
    assert 'VALIDATOR_STATUS="$validation_status"' in workflow
    assert 'required = {' in workflow
    assert 'report.get("mode") != "pr"' in workflow
    assert "data.get('invalid',0)" not in workflow
    assert "continue-on-error" not in workflow
    assert "2>/dev/null" not in workflow


def test_workflow_failure_masking_is_explicitly_audited() -> None:
    """Only the no-match grep count is allowed to use ``|| true``."""
    unexpected: list[str] = []
    for workflow_path in sorted(WORKFLOWS.glob("*.yml")):
        for line_number, line in enumerate(
            workflow_path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if "2>/dev/null" in line or "continue-on-error" in line:
                unexpected.append(f"{workflow_path.name}:{line_number}: {line.strip()}")
            if "|| true" in line and not (
                workflow_path.name == "daily-research.yml"
                and "grep -c '^    NEW' survey.txt" in line
            ):
                unexpected.append(f"{workflow_path.name}:{line_number}: {line.strip()}")

    assert not unexpected, "unexpected workflow failure masking:\n" + "\n".join(unexpected)


# ── the rank API deploy (MODEL-68) ───────────────────────────────────────────
#
# The scar these pin is MODEL-9's: three changes shipped without their
# container-side code ever running, because the smoke test could not tell a new
# deployment from an old instance still answering. A deploy gate that cannot
# fail is worse than no gate, so what is asserted here is that this one can.

RANK_API = WORKFLOWS / "rank-api.yml"


def test_the_rank_worker_deploys_only_from_main() -> None:
    workflow = RANK_API.read_text(encoding="utf-8")
    assert "    name: Deploy the rank Worker\n" in workflow
    assert ("if: github.event_name == 'push' && github.ref == 'refs/heads/main'"
            in workflow), "the deploy job is not fenced to pushes on main"


def test_deploy_secrets_are_not_in_scope_on_a_pull_request() -> None:
    """The bundle job runs on every PR and must never see a credential."""
    import yaml

    workflow = yaml.safe_load(RANK_API.read_text(encoding="utf-8"))
    bundle = workflow["jobs"]["bundle"]
    assert "secrets." not in yaml.safe_dump(bundle), "the PR job references a secret"
    deploy_env = workflow["jobs"]["deploy"]["env"]
    assert deploy_env["CLOUDFLARE_API_TOKEN"] == \
        "${{ secrets.CLOUDFLARE_API_MODELSPEC_TOKEN }}", (
        "the rank Worker must use its own token, not the Pages or graph one")


def test_the_bundle_is_proven_to_build_on_every_pull_request() -> None:
    """A Python Worker that does not bundle should fail on the PR, not on main."""
    workflow = RANK_API.read_text(encoding="utf-8")
    assert "deploy --dry-run" in workflow
    assert "python -m pytest -q tests/test_rank_worker.py" in workflow
    assert "vendor.py --check" in workflow


def test_the_smoke_test_asserts_the_deployed_version_is_the_one_answering() -> None:
    """`build_commit` alone cannot catch a stale instance; `service_commit` can."""
    workflow = RANK_API.read_text(encoding="utf-8")
    assert 'BUILD_COMMIT:${GITHUB_SHA}' in workflow, "the deploy does not stamp a version"
    assert 'commit=$(field service_commit)' in workflow
    assert '[ "$commit" = "${GITHUB_SHA}" ]' in workflow
    assert "never rolled onto" in workflow, "there is no named failure for a stale script"


def test_the_smoke_test_fails_loudly_rather_than_passing_silently() -> None:
    workflow = RANK_API.read_text(encoding="utf-8")
    assert "continue-on-error" not in workflow
    assert "|| true" not in workflow
    assert "2>/dev/null" not in workflow
    # `fail` annotates with ::error::, prints the body and exits non-zero. Each
    # distinct way the deploy can be wrong has to reach it with its own message.
    assert "::error::" in workflow, "failures are not annotated for the run log"
    assert workflow.count('fail "') >= 5, (
        "too few named failure cases; a smoke test that can only fail one way "
        "hides the others")
    assert "exit 1" in workflow
    # The script is invoked through `$checker`, so what is pinned is that each
    # shape of answer is still checked by the reviewable file rather than by an
    # assertion buried in the shell.
    assert 'checker=".github/scripts/check_rank_response.py"' in workflow
    for mode in ("ranked", "no-match", "not-found"):
        assert f'python3 "$checker" {mode} body.json' in workflow, \
            f"the {mode} response is no longer checked"


def test_the_smoke_test_checks_the_documented_no_match_code() -> None:
    workflow = RANK_API.read_text(encoding="utf-8")
    assert '[ "$status" != 422 ]' in workflow, "the 422 contract is not exercised live"
    assert '[ "$status" != 400 ]' in workflow, "a refused request is not exercised live"


def test_the_response_checker_rejects_an_empty_ranking() -> None:
    """The check that makes the smoke test worth running, run here too."""
    import importlib.util

    path = REPO_ROOT / ".github" / "scripts" / "check_rank_response.py"
    spec = importlib.util.spec_from_file_location("check_rank_response", path)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)

    good = {
        "build": {"commit": "abc", "export_schema_version": "3.0"},
        "service_commit": "def",
        "policy": {"min_benchmark_coverage": 0.50, "min_benchmark_count": 2},
        "result": [{"model_id": "m", "score": 1.0, "rank": 1, "cost_input": None,
                    "evidence_basis": "mixed"}],
    }
    assert checker.check_ranked(good) == []
    assert checker.check_ranked({**good, "result": []}), "an empty ranking passed"
    assert checker.check_ranked(
        {**good, "policy": {"min_benchmark_coverage": 0.25, "min_benchmark_count": 2}}), \
        "a changed floor passed"
    assert checker.check_ranked(
        {**good, "result": [{**good["result"][0], "evidence_basis": "excellent"}]}), \
        "an invented evidence_basis passed"
    assert checker.check_no_match({**good, "result": []}), "a 422 with no reason passed"


# ── the smoke test must survive a body it cannot parse ───────────────────────
#
# MODEL-68's deploy of e0265a5 went red on a Worker that was live and correct.
# The workflow read every response with an inline `json.loads`, the first thing
# it read was Cloudflare's `error code: 522` page — the route had been published
# 100 ms earlier and had not reached the edge — and the traceback under GitHub's
# default `bash -e` killed the step before the retry loop got a second turn. A
# gate that goes red on a healthy deploy is spent the same way a gate that
# cannot go red at all is: nobody reads the next one.

CHECKER = REPO_ROOT / ".github" / "scripts" / "check_rank_response.py"

#: What Cloudflare serves for a proxied host whose request matched no route.
CLOUDFLARE_522 = b"error code: 522"


def _checker():
    import importlib.util

    spec = importlib.util.spec_from_file_location("check_rank_response", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("body", [
    CLOUDFLARE_522,
    b"",
    b"   \n",
    b"<!DOCTYPE html><html><head><title>522</title></head></html>",
    b'{"service_commit": "abc"',          # truncated mid-document
    b"\xff\xfe not utf-8 at all",
    b'"a bare string"',
    b"[1, 2, 3]",
])
def test_no_response_body_can_make_the_smoke_test_raise(body: bytes, tmp_path: Path) -> None:
    """Every one of these is a thing a live host really answers."""
    checker = _checker()
    path = tmp_path / "body.json"
    path.write_bytes(body)

    parsed, raw, problem = checker.read_body(str(path))
    assert raw == body
    # A line for the run log, whatever it read, with no newline to truncate it.
    line = checker.describe("/v1/health", "522", raw, problem)
    assert "\n" not in line
    assert "HTTP 522" in line and "path /v1/health" in line


def test_a_missing_body_file_is_described_rather_than_raised(tmp_path: Path) -> None:
    checker = _checker()
    _, raw, problem = checker.read_body(str(tmp_path / "never-written.json"))
    assert problem and raw == b""
    assert "\n" not in checker.describe("/", "000", raw, problem)


def test_reading_a_field_from_an_unparseable_body_exits_zero(tmp_path: Path) -> None:
    """The poll loop reads this inside `x=$(...)`, where non-zero aborts the step."""
    import subprocess
    import sys

    path = tmp_path / "body.json"
    path.write_bytes(CLOUDFLARE_522)
    done = subprocess.run(
        [sys.executable, str(CHECKER), "field", "service_commit", str(path)],
        capture_output=True, text=True, check=False)
    assert done.returncode == 0, "an unreadable body aborted the field read"
    assert done.stdout.strip() == "", "a 522 page yielded a service_commit"
    assert "522" in done.stderr, "the run log is not told why the field is empty"


def test_an_unreadable_checked_response_is_annotated_not_traced(tmp_path: Path) -> None:
    import subprocess
    import sys

    path = tmp_path / "body.json"
    path.write_bytes(CLOUDFLARE_522)
    done = subprocess.run(
        [sys.executable, str(CHECKER), "ranked", str(path), "/v1/rank", "522"],
        capture_output=True, text=True, check=False)
    assert done.returncode == 1
    assert "Traceback" not in done.stdout + done.stderr
    assert done.stdout.startswith("::error::")
    # Status, requested path and the first bytes: enough to diagnose without
    # opening Cloudflare, and no full URL that could carry a query string.
    assert "HTTP 522" in done.stdout
    assert "path /v1/rank" in done.stdout
    assert "error code: 522" in done.stdout
    assert "https://" not in done.stdout


def test_a_failing_assertion_says_which_one_and_what_it_got(tmp_path: Path) -> None:
    import subprocess
    import sys

    path = tmp_path / "body.json"
    path.write_text('{"build": {"commit": "abc", "export_schema_version": "3.0"},'
                    ' "service_commit": "def", "result": [],'
                    ' "policy": {"min_benchmark_coverage": 0.5,'
                    ' "min_benchmark_count": 2}}', encoding="utf-8")
    done = subprocess.run(
        [sys.executable, str(CHECKER), "ranked", str(path), "/v1/rank", "200"],
        capture_output=True, text=True, check=False)
    assert done.returncode == 1
    assert "no rows" in done.stdout, "the failing assertion is not named"
    assert "HTTP 200" in done.stdout and "path /v1/rank" in done.stdout


def test_the_smoke_test_parses_no_response_body_of_its_own() -> None:
    """The parse lives in the reviewable, unit-tested script or nowhere."""
    workflow = RANK_API.read_text(encoding="utf-8")
    assert "json.loads" not in workflow, "a body is parsed inline again"
    assert "python3 -c" not in workflow, "a body is parsed inline again"
    assert 'python3 "$checker"' in workflow


def test_every_path_the_smoke_test_probes_is_one_the_route_serves() -> None:
    """A check aimed outside the route tests Cloudflare, not the Worker."""
    import re

    workflow = RANK_API.read_text(encoding="utf-8")
    probed = set(re.findall(r"^\s*probe (\S+)", workflow, re.MULTILINE))
    assert probed >= {"/", "/v1/health", "/v1/rank"}, f"too few paths probed: {probed}"

    pattern = _route_pattern()
    prefix = pattern.split("*", 1)[0].split("/", 1)[1] if "/" in pattern else ""
    for path in probed:
        assert path.lstrip("/").startswith(prefix), (
            f"the smoke test probes {path}, which the route {pattern!r} does not serve")


# ── the bare root answers, rather than 522-ing like an outage ────────────────

WRANGLER = REPO_ROOT / "api" / "worker" / "wrangler.jsonc"
WORKER_ENTRY = REPO_ROOT / "api" / "worker" / "src" / "entry.py"


def _route_pattern() -> str:
    import re

    match = re.search(r'"pattern"\s*:\s*"([^"]+)"', WRANGLER.read_text(encoding="utf-8"))
    assert match, "the Worker declares no route"
    return match.group(1)


def test_the_route_covers_the_whole_host_including_the_bare_root() -> None:
    """`api.modelspec.dev/` has no origin behind it; only the Worker can answer it."""
    assert _route_pattern() == "api.modelspec.dev/*", (
        "a narrower route leaves every path outside it answering 522, which is "
        "indistinguishable from the endpoint being down")


def test_the_worker_answers_an_unknown_path_itself() -> None:
    source = WORKER_ENTRY.read_text(encoding="utf-8")
    assert "HTTP_NOT_FOUND" in source, "unknown paths are not answered here"
    assert "ACCEPTED_ENDPOINTS = (" in source
    # Membership rather than the literal tuple: an endpoint added to the Worker
    # has to be added here too, but adding one must not fail this test for the
    # endpoints that were already right.
    for endpoint in _checker().ACCEPTED_ENDPOINTS:
        assert f'"{endpoint}"' in source, (
            f"a 404 that does not name {endpoint} is a dead end")


def test_the_worker_refuses_a_verb_on_every_endpoint_it_serves() -> None:
    """`/v1/health` answered PUT and DELETE with a 200 until this was pinned."""
    source = WORKER_ENTRY.read_text(encoding="utf-8")
    assert 'method not in ("GET", "HEAD")' in source, "/v1/health takes any verb"
    assert 'if method != "POST":' in source, "/v1/rank takes any verb"
    assert source.count("_method_not_allowed(") >= 3, (
        "not every endpoint routes its refusal through the shared 405")

    workflow = RANK_API.read_text(encoding="utf-8")
    assert '[ "$status" != 405 ]' in workflow, "no verb is refused live"


def test_the_smoke_test_exercises_the_documented_root() -> None:
    workflow = RANK_API.read_text(encoding="utf-8")
    assert '[ "$status" != 404 ]' in workflow, "the root is not exercised live"
    assert 'python3 "$checker" not-found body.json' in workflow


def test_the_not_found_check_demands_the_versioned_paths() -> None:
    checker = _checker()
    good = {"service_commit": "abc", "result": [],
            "error": {"code": "not_found", "message": "no endpoint at /",
                      "accepted": list(checker.ACCEPTED_ENDPOINTS)}}
    assert checker.check_not_found(good) == []
    assert checker.check_not_found({**good, "error": {**good["error"], "accepted": []}}), \
        "a 404 naming no endpoint passed"
    assert checker.check_not_found({**good, "service_commit": ""}), \
        "a 404 that does not say which version answered passed"
    assert checker.check_not_found({**good, "result": [{"model_id": "m"}]}), \
        "a 404 carrying rows passed"


def test_site_artifact_keeps_hidden_files() -> None:
    """upload-artifact >= 4.4 drops dotfiles unless told otherwise. The built
    sites carry /.well-known/ (api-catalog, mcp.json, agent-skills), so the
    artifact that carries dist/ to the deploy job must include hidden files,
    or those discovery documents 404 in production (MODEL-94)."""
    workflow = (WORKFLOWS / "deploy-sites.yml").read_text(encoding="utf-8")
    upload = workflow.split("actions/upload-artifact@", 1)[1].split("- uses:", 1)[0]
    assert "name: sites" in upload
    assert "include-hidden-files: true" in upload
