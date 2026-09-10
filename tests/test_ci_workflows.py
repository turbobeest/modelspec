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


def test_pytest_workflow_runs_the_test_command_without_masking_it() -> None:
    workflow = (WORKFLOWS / "test.yml").read_text(encoding="utf-8")

    assert "run: python -m pytest -q" in workflow
    assert "continue-on-error" not in workflow
    assert "|| true" not in workflow
    assert "2>/dev/null" not in workflow


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
