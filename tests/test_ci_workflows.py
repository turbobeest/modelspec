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

    assert "python -m pytest -q -n auto --dist loadfile" in workflow
    assert "continue-on-error" not in workflow
    assert "|| true" not in workflow
    assert "2>/dev/null" not in workflow


def test_pytest_workflow_validates_every_github_workflow() -> None:
    workflow = (WORKFLOWS / "test.yml").read_text(encoding="utf-8")

    assert "rhysd/actionlint:1.7.7" in workflow
    assert "-shellcheck=" in workflow
    assert " -color" in workflow


def test_required_check_job_names_match_branch_protection() -> None:
    """Main requires these exact check names (GitHub Actions app 15368)."""
    test_workflow = (WORKFLOWS / "test.yml").read_text(encoding="utf-8")
    deploy_workflow = (WORKFLOWS / "deploy-sites.yml").read_text(encoding="utf-8")
    assert "    name: Run pytest\n" in test_workflow
    assert "    name: Build both sites\n" in deploy_workflow


def test_pytest_aggregator_preserves_the_required_check_contract() -> None:
    import yaml

    workflow = yaml.safe_load((WORKFLOWS / "test.yml").read_text(encoding="utf-8"))
    jobs = workflow["jobs"]
    required = jobs["required-pytest"]
    assert [job.get("name") for job in jobs.values()].count("Run pytest") == 1
    assert required["name"] == "Run pytest"
    assert required["needs"] == ["pytest-shards", "pytest-perf-and-collection", "package-smoke"]
    assert required["if"] == "always()"
    assert "pip install" not in yaml.safe_dump(required)
    gate = required["steps"][0]
    assert gate["name"] == "Require pytest jobs to succeed"
    assert gate["if"] == "always()"
    assert gate["env"]["SHARD_RESULT"] == "${{ needs.pytest-shards.result }}"
    assert gate["env"]["PERF_RESULT"] == \
        "${{ needs.pytest-perf-and-collection.result }}"
    assert gate["env"]["PACKAGE_RESULT"] == "${{ needs.package-smoke.result }}"
    assert 'test "$SHARD_RESULT" = success' in gate["run"]
    assert 'test "$PERF_RESULT" = success' in gate["run"]
    assert 'test "$PACKAGE_RESULT" = success' in gate["run"]


def test_pytest_matrix_matches_the_file_splitter() -> None:
    import yaml

    from scripts.pytest_shards import DEFAULT_SHARD_COUNT

    workflow_text = (WORKFLOWS / "test.yml").read_text(encoding="utf-8")
    workflow = yaml.safe_load(workflow_text)
    matrix = workflow["jobs"]["pytest-shards"]["strategy"]["matrix"]["include"]
    assert len(matrix) == DEFAULT_SHARD_COUNT
    assert [entry["index"] for entry in matrix] == list(range(DEFAULT_SHARD_COUNT))
    assert [entry["label"] for entry in matrix] == [f"{i}/{DEFAULT_SHARD_COUNT}"
                                                     for i in range(1, 5)]
    assert f"--shard-count {DEFAULT_SHARD_COUNT}" in workflow_text
    assert "--shard-index ${{ matrix.index }}" in workflow_text
    assert 'pytest -q -n auto --dist loadfile -m "not perf"' in workflow_text
    assert "--junitxml=shard-${{ matrix.index }}-junit.xml" in workflow_text
    shard_steps = workflow["jobs"]["pytest-shards"]["steps"]
    timing_upload = next(step for step in shard_steps
                         if step.get("name") == "Upload test timings")
    assert timing_upload["if"] == "always()"
    assert timing_upload["with"]["name"] == "pytest-shard-${{ matrix.index }}-junit"
    assert timing_upload["with"]["path"] == "shard-${{ matrix.index }}-junit.xml"
    assert (REPO_ROOT / "tests" / "shard_durations.json").is_file()


def test_timing_tests_run_serially_exactly_once() -> None:
    import yaml

    workflow_text = (WORKFLOWS / "test.yml").read_text(encoding="utf-8")
    workflow = yaml.safe_load(workflow_text)
    perf_job = workflow["jobs"]["pytest-perf-and-collection"]
    perf_command = "python -m pytest -q -p no:xdist -m perf"
    assert workflow_text.count("name: Run timing tests serially") == 1
    assert workflow_text.count(perf_command) == 1
    assert any(step.get("run") == perf_command for step in perf_job["steps"])


def test_file_splitter_uses_pytest_default_patterns_from_the_repo_root(tmp_path: Path) -> None:
    from scripts.pytest_shards import test_files

    expected = {
        tmp_path / "tests" / "feature_test.py",
        tmp_path / "integration" / "test_feature.py",
    }
    for path in expected:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")

    assert set(test_files(tmp_path)) == expected


def test_file_splitter_excludes_pytest_ignored_directories(tmp_path: Path) -> None:
    from scripts.pytest_shards import test_files

    included = tmp_path / "test_included.py"
    included.write_text("", encoding="utf-8")
    for directory in (tmp_path / "node_modules", tmp_path / ".venv"):
        directory.mkdir()
        (directory / "test_excluded.py").write_text("", encoding="utf-8")
    virtualenv = tmp_path / "custom-environment"
    virtualenv.mkdir()
    (virtualenv / "pyvenv.cfg").write_text("", encoding="utf-8")
    (virtualenv / "test_excluded.py").write_text("", encoding="utf-8")

    assert test_files(tmp_path) == [included]


def test_file_splitter_honors_pyproject_discovery_options(tmp_path: Path) -> None:
    from scripts.pytest_shards import test_files

    (tmp_path / "pyproject.toml").write_text(
        """[tool.pytest.ini_options]
python_files = ["checks/check_*.py"]
testpaths = ["checks"]
norecursedirs = ["generated"]
""",
        encoding="utf-8",
    )
    expected = tmp_path / "checks" / "check_feature.py"
    expected.parent.mkdir()
    expected.write_text("", encoding="utf-8")
    (tmp_path / "test_outside.py").write_text("", encoding="utf-8")
    generated = tmp_path / "checks" / "generated"
    generated.mkdir()
    (generated / "check_excluded.py").write_text("", encoding="utf-8")

    assert test_files(tmp_path) == [expected]


def test_file_splitter_assigns_discovered_set_once(tmp_path: Path) -> None:
    from scripts.pytest_shards import DEFAULT_SHARD_COUNT, partition_files, test_files

    files = []
    for relative in ("test_one.py", "suite/two_test.py", "suite/test_three.py"):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(relative, encoding="utf-8")
        files.append(path)

    discovered = test_files(tmp_path)
    assigned = [
        path
        for shard in partition_files(discovered, DEFAULT_SHARD_COUNT)
        for path in shard
    ]
    assert len(assigned) == len(set(assigned))
    assert set(assigned) == set(discovered) == set(files)


def test_duration_lpt_beats_size_packing(tmp_path: Path) -> None:
    from scripts.pytest_shards import partition_files

    durations_by_size = [8.0, 1.0, 7.0, 2.0, 6.0, 3.0]
    files = []
    durations = {}
    for index, (size, duration) in enumerate(
        zip(range(60, 0, -10), durations_by_size, strict=True)
    ):
        path = tmp_path / f"test_{index}.py"
        path.write_text("x" * size, encoding="utf-8")
        files.append(path)
        durations[path.name] = duration

    duration_shards = partition_files(files, 2, root=tmp_path, durations=durations)
    size_shards = partition_files(
        files,
        2,
        root=tmp_path,
        durations={path.name: float(path.stat().st_size) for path in files},
    )

    def longest(shards: list[list[Path]]) -> float:
        return max(sum(durations[path.name] for path in shard) for shard in shards)

    assert longest(duration_shards) == 14.0
    assert longest(size_shards) == 16.0


def test_file_missing_from_durations_is_still_assigned(tmp_path: Path) -> None:
    from scripts.pytest_shards import partition_files

    known = tmp_path / "test_known.py"
    unknown = tmp_path / "test_new.py"
    known.write_text("known", encoding="utf-8")
    unknown.write_text("new", encoding="utf-8")

    assigned = partition_files(
        [known, unknown], 2, root=tmp_path, durations={known.name: 2.0}
    )

    assert {path for shard in assigned for path in shard} == {known, unknown}


def test_junit_refresh_sums_testcases_by_file(tmp_path: Path) -> None:
    from scripts.refresh_shard_durations import durations_from_junit

    test_file = tmp_path / "tests" / "test_feature.py"
    test_file.parent.mkdir()
    test_file.write_text("", encoding="utf-8")
    xml_file = tmp_path / "shard.xml"
    xml_file.write_text(
        """<testsuites><testsuite>
<testcase classname="tests.test_feature" name="test_one" time="1.25" />
<testcase classname="tests.test_feature.TestGroup" name="test_two" time="2.5" />
</testsuite></testsuites>
""",
        encoding="utf-8",
    )

    assert durations_from_junit([xml_file], tmp_path) == {
        "tests/test_feature.py": 3.75
    }


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


def test_staging_rank_worker_deploy_is_manual_and_targets_only_staging() -> None:
    import yaml

    workflow = yaml.safe_load(RANK_API.read_text(encoding="utf-8"))
    staging = workflow["jobs"]["deploy-staging"]
    assert staging["if"] == "github.event_name == 'workflow_dispatch' && (vars.DATA_SPLIT_ENABLED != 'true' || github.ref == 'refs/heads/main')"
    assert staging["needs"] == "bundle"
    staging_text = yaml.safe_dump(staging)
    assert "vendor.py" in staging_text
    assert "uv sync --project api/worker --frozen" in staging_text
    assert "pywrangler deploy --env staging" in staging_text

    production_text = yaml.safe_dump(workflow["jobs"]["deploy"])
    assert "--env staging" not in production_text


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


def test_the_worker_bundle_resolves_python_dependencies() -> None:
    workflow = RANK_API.read_text(encoding="utf-8")
    assert "astral-sh/setup-uv@" in workflow
    assert "uv sync --project api/worker --frozen" in workflow
    assert "uv run --project . pywrangler deploy --dry-run" in workflow


def test_deploy_syncs_the_snapshot_verification_secret() -> None:
    import yaml

    workflow = yaml.safe_load(RANK_API.read_text(encoding="utf-8"))
    bundle = workflow["jobs"]["bundle"]
    deploy = workflow["jobs"]["deploy"]
    assert "MODELSPEC_SNAPSHOT_KEY" not in yaml.safe_dump(bundle)
    assert deploy["env"]["MODELSPEC_SNAPSHOT_KEY"] == \
        "${{ secrets.MODELSPEC_SNAPSHOT_KEY }}"
    deploy_text = yaml.safe_dump(deploy)
    assert "pywrangler secret put MODELSPEC_SNAPSHOT_KEY" in deploy_text
    sync = next(step["run"] for step in deploy["steps"]
                if step.get("name") == "Sync the decision snapshot verification key")
    missing_key = sync.split("else", 1)[0]
    assert "::warning::" in missing_key
    assert "exit 1" not in missing_key


def test_deploy_accepts_a_decision_or_the_documented_no_snapshot_response() -> None:
    workflow = RANK_API.read_text(encoding="utf-8")
    decide = workflow.index("probe /v1/decide")
    openapi = workflow.index("python3 api/worker/openapi.py --probe")
    assert decide < openapi
    between = workflow[decide:openapi]
    assert 'snapshot=$(field snapshot)' in between
    assert 'error=$(field error)' in between
    assert '[ "$status" = 503 ] && [ "$error" = "no_snapshot" ]' in between
    assert "signed decision snapshot was not ready" not in between


def test_site_build_only_publishes_a_complete_signed_decision_snapshot() -> None:
    workflow = (WORKFLOWS / "deploy-sites.yml").read_text(encoding="utf-8")
    assert "github.event_name != 'pull_request' && secrets.MODELSPEC_SNAPSHOT_KEY" in workflow
    assert "--decision-snapshot-if-ready" in workflow
    assert 'if [ "$GITHUB_EVENT_NAME" != "pull_request" ]' in workflow
    assert "::error::MODELSPEC_SNAPSHOT_KEY is not configured" not in workflow


def test_site_build_reads_the_ed25519_private_key_from_the_repo_secret() -> None:
    import yaml

    workflow = yaml.safe_load((WORKFLOWS / "deploy-sites.yml").read_text(encoding="utf-8"))
    build = workflow["jobs"]["build"]
    step = next(row for row in build["steps"] if row.get("name") == "Build")

    assert step["env"]["MODELSPEC_SNAPSHOT_ED25519_KEY"] == (
        "${{ github.event_name != 'pull_request' && "
        "secrets.MODELSPEC_SNAPSHOT_ED25519_KEY || '' }}"
    )
    install = next(row for row in build["steps"] if row.get("name") == "Install dependencies")
    assert "cryptography" in install["run"]


def test_rank_smoke_failure_rolls_back_before_the_job_fails() -> None:
    workflow = RANK_API.read_text(encoding="utf-8")
    assert "wrangler rollback --message" in workflow
    assert "fail_rank()" in workflow
    rank_checks = workflow[
        workflow.index("# 3. A ranking") : workflow.index("# 7. The policy-check endpoint")
    ]
    assert rank_checks.count("fail_rank ") >= 5


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
