"""MODEL-135: ``modelspec decide`` parses and validates a spec, then says the engine is not built.

Until MODEL-141/142/145 land, a valid spec exits 1 with "engine not yet
built"; an invalid one exits 1 naming the condition, field and reason. No
existing command changes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from cli.modelspec import cli as cli_mod  # noqa: E402
from cli.modelspec import decide_cmd  # noqa: E402

VALID = """
spec_version: 1
where:
  - input_price in [0.5, 3]
  - swe_bench_pro >= 55 @independent measured_after 2026-06-01
optimize:
  max: swe_bench_pro
"""


@pytest.fixture(autouse=True)
def no_registry(monkeypatch):
    """Structure-only validation, so these tests do not depend on MODEL-133's data."""
    monkeypatch.setattr(decide_cmd, "_facet_lookup", lambda: (None, "stubbed out in tests"))


def _run(tmp_path: Path, text: str, *args: str):
    spec = tmp_path / "spec.yaml"
    spec.write_text(text)
    return CliRunner().invoke(cli_mod.app, ["decide", str(spec), *args])


def test_a_valid_spec_reports_that_the_engine_is_not_built(tmp_path) -> None:
    result = _run(tmp_path, VALID)
    assert result.exit_code == 1
    assert "engine not yet built" in result.output
    assert "sha256:" in result.output


def test_json_reports_the_spec_hash_and_the_error_code(tmp_path) -> None:
    result = _run(tmp_path, VALID, "--json")
    assert result.exit_code == 1
    payload = json.loads(result.stderr)
    assert payload["command"] == "decide"
    assert payload["contract_version"] == "1.0"
    assert payload["spec_hash"].startswith("sha256:")
    assert payload["error"]["code"] == "engine_not_built"


def test_an_invalid_spec_names_condition_field_and_reason(tmp_path) -> None:
    bad = VALID.replace("@independent", "@independnt")
    result = _run(tmp_path, bad)
    assert result.exit_code == 1
    assert "swe_bench_pro >= 55 @independnt measured_after 2026-06-01" in result.output
    assert "field swe_bench_pro" in result.output
    assert "unknown qualifier @independnt" in result.output
    assert "engine not yet built" not in result.output


def test_json_lists_every_issue(tmp_path) -> None:
    bad = VALID.replace("@independent", "@independnt").replace("[0.5, 3]", "[3, 0.5]")
    result = _run(tmp_path, bad, "--json")
    assert result.exit_code == 1
    error = json.loads(result.stderr)["error"]
    assert error["code"] == "invalid_spec"
    assert [i["path"] for i in error["issues"]] == ["where[0]", "where[1]"]
    assert {i["field"] for i in error["issues"]} == {"input_price", "swe_bench_pro"}
    assert all(i["condition"] and i["reason"] for i in error["issues"])


def test_explain_overrides_the_spec(tmp_path) -> None:
    ok = _run(tmp_path, VALID, "--explain", "full", "--json")
    assert json.loads(ok.stderr)["explain"] == "full"
    bad = _run(tmp_path, VALID, "--explain", "verbose")
    assert bad.exit_code == 1
    assert "explain" in bad.output


def test_free_text_task_is_refused(tmp_path) -> None:
    result = _run(tmp_path, VALID + "task: refactor the parser\n")
    assert result.exit_code == 1
    assert "not yet in slice 1" in result.output


def test_a_missing_file_is_a_usage_error(tmp_path) -> None:
    result = CliRunner().invoke(cli_mod.app, ["decide", str(tmp_path / "nope.yaml")])
    assert result.exit_code == 1
    assert "nope.yaml" in result.output


def test_a_missing_registry_is_said_not_skipped(tmp_path) -> None:
    result = _run(tmp_path, VALID)
    assert "facet IDs were not checked" in result.output


def test_the_existing_commands_are_all_still_there() -> None:
    names = {cmd.name for cmd in cli_mod.app.registered_commands}
    assert "decide" in names
    groups = {group.name for group in cli_mod.app.registered_groups}
    assert {"offline", "snapshot"} <= groups
