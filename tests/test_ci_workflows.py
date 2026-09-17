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

    assert "run: python -m pytest -q" in workflow
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
    assert "check_rank_response.py ranked" in workflow
    assert "check_rank_response.py no-match" in workflow


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
        "build": {"commit": "abc", "export_schema_version": "2.0"},
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
