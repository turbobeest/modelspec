"""The decide command validates specs and requires a local snapshot."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from cli.modelspec import cli as cli_mod  # noqa: E402
from decision.snapshot import SnapshotInputs, build_snapshot  # noqa: E402
from tests.snapshot_records import SOURCES, evidence, model  # noqa: E402

VALID = """
spec_version: 1
where:
  - offering.price.input in [0.5, 3]
  - swe_bench_pro >= 55 @independent measured_after 2026-06-01
optimize:
  max: swe_bench_pro
"""

BUDGET_CODING = """
spec_version: 1
snapshot: latest
task_type: new_feature
capabilities: {software_engineering: required}
where:
  - model.class = text-generator
  - model.context_window >= 200000
  - offering.cost_per_task <= 0.25
optimize:
  weights: {software_engineering: 0.6, -offering.cost_per_task: 0.4}
"""


@pytest.fixture
def cached_vocabulary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    snapshot = build_snapshot(SnapshotInputs(
        models=[model("lab/a")],
        offerings=[],
        evidence=[evidence("lab/a", "swe_bench_pro", 70.0)],
        sources=SOURCES,
        benchmark_domains={"swe_bench_pro": [("software_engineering", "direct")]},
    ), gate=False, as_of=date(2026, 9, 27))
    vocabulary = {
        "vocabulary_version": 1,
        "contract_version": "1.7",
        "snapshot": snapshot.snapshot_id,
        "task_types": ["new_feature", "bug_fix"],
        "facets": [
            {"id": "model.class", "label": "Model class", "subject": "model",
             "value_type": "enum", "operators": ["=", "!=", "in", "not in", "known"],
             "known": 10, "of": 10},
            {"id": "model.context_window", "label": "Context window", "subject": "model",
             "value_type": "number",
             "operators": ["=", "!=", "<", "<=", ">", ">=", "between", "known"],
             "known": 8, "of": 10},
            {"id": "offering.cost_per_task", "label": "Cost per task",
             "subject": "offering", "value_type": "number",
             "operators": ["=", "!=", "<", "<=", ">", ">=", "between", "known"],
             "known": 6, "of": 12},
            {"id": "offering.data.retention_days", "label": "Data retention",
             "subject": "offering", "value_type": "number",
             "operators": ["=", "!=", "<", "<=", ">", ">=", "between", "known"],
             "known": 5, "of": 12},
            {"id": "offering.provider", "label": "Provider", "subject": "offering",
             "value_type": "enum", "operators": ["=", "!=", "in", "not in", "known"],
             "known": 12, "of": 12},
        ],
        "benchmarks": [
            {"id": "swe_bench_pro", "name": "SWE-bench Pro",
             "domains": [{"id": "software_engineering", "directness": "direct"}]},
            {"id": "gpqa", "name": "GPQA",
             "domains": [{"id": "reasoning", "directness": "proxy"}]},
        ],
        "domains": [
            {"id": "software_engineering", "name": "Software engineering",
             "proxy_only": False, "estimate_models": 7},
            {"id": "reasoning", "name": "Reasoning", "proxy_only": True,
             "estimate_models": 4},
        ],
        "providers": {"anthropic": "Anthropic API", "openai": "OpenAI API"},
        "coverage": {
            "as_of": "2026-09-27", "models": 10, "verified": 8,
            "classes": [{"id": "text-generator", "models": 8, "verified": 7,
                         "domains": [{"id": "software_engineering", "verified": 6}]}],
            "domains": [],
        },
    }
    cache = tmp_path / "cache"
    generation = cache / "decision" / snapshot.snapshot_id
    generation.mkdir(parents=True)
    (generation / "snapshot.json.gz").write_bytes(snapshot.to_bytes(key=None))
    (generation / "vocabulary.json").write_text(json.dumps(vocabulary))
    (cache / "decision" / "current").write_text(snapshot.snapshot_id + "\n")
    monkeypatch.setenv("MODELSPEC_CACHE", str(cache))
    return vocabulary


def _run(tmp_path: Path, text: str, *args: str):
    spec = tmp_path / "spec.yaml"
    spec.write_text(text)
    return CliRunner().invoke(cli_mod.app, ["decide", str(spec), *args])


def test_a_valid_spec_requires_a_local_snapshot(tmp_path) -> None:
    result = _run(tmp_path, VALID)
    assert result.exit_code == 1
    assert "modelspec snapshot fetch" in result.output


def test_json_reports_the_spec_hash_and_the_error_code(tmp_path) -> None:
    result = _run(tmp_path, VALID, "--json")
    assert result.exit_code == 1
    payload = json.loads(result.stderr)
    assert payload["command"] == "decide"
    assert payload["contract_version"] == "1.7"
    assert payload["spec_hash"].startswith("sha256:")
    assert payload["error"]["code"] == "snapshot_required"


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
    assert {i["field"] for i in error["issues"]} == {"offering.price.input", "swe_bench_pro"}
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


def test_unknown_facet_uses_the_registry_nearest_match(tmp_path) -> None:
    result = _run(tmp_path, VALID.replace("offering.price.input", "offering.price.inpt"))
    assert result.exit_code == 1
    assert "unknown facet 'offering.price.inpt'" in result.output
    assert "did you mean 'offering.price.input'" in result.output


def test_the_existing_commands_are_all_still_there() -> None:
    names = {cmd.name for cmd in cli_mod.app.registered_commands}
    assert {"decide", "vocab"} <= names
    groups = {group.name for group in cli_mod.app.registered_groups}
    assert {"offline", "snapshot"} <= groups


@pytest.mark.parametrize(
    "section, marker",
    [("facets", "model.context_window"), ("benchmarks", "swe_bench_pro"),
     ("domains", "software_engineering"), ("providers", "anthropic"),
     ("task-types", "new_feature"), ("coverage", "verified")],
)
def test_vocab_sections_have_human_and_json_output(
    cached_vocabulary: dict, section: str, marker: str,
) -> None:
    human = CliRunner().invoke(cli_mod.app, ["vocab", section])
    machine = CliRunner().invoke(cli_mod.app, ["vocab", section, "--json"])
    assert human.exit_code == machine.exit_code == 0
    assert marker in human.stdout
    assert marker in machine.stdout
    json.loads(machine.stdout)


def test_vocab_overview_and_filters(cached_vocabulary: dict) -> None:
    overview = CliRunner().invoke(cli_mod.app, ["vocab"])
    search = CliRunner().invoke(cli_mod.app, ["vocab", "facets", "--search", "retention"])
    domain = CliRunner().invoke(
        cli_mod.app, ["vocab", "benchmarks", "--domain", "software_engineering", "--json"]
    )
    class_ = CliRunner().invoke(
        cli_mod.app, ["vocab", "benchmarks", "--class", "text-generator", "--json"]
    )
    assert cached_vocabulary["snapshot"] in overview.stdout
    assert "next: modelspec vocab facets" in overview.stdout
    assert "offering.data.retention_days" in search.stdout
    domain_payload = json.loads(domain.stdout)
    class_payload = json.loads(class_.stdout)
    assert set(domain_payload) == {"schema_version", "command", "freshness", "result"}
    assert domain_payload["command"] == class_payload["command"] == "vocab"
    assert [row["id"] for row in domain_payload["result"]] == ["swe_bench_pro"]
    assert [row["id"] for row in class_payload["result"]] == ["swe_bench_pro"]


def test_vocab_without_a_cache_exits_three(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MODELSPEC_CACHE", str(tmp_path / "empty"))
    result = CliRunner().invoke(cli_mod.app, ["vocab"])
    assert result.exit_code == 3
    assert "modelspec snapshot fetch" in result.stderr


def test_vocab_and_check_report_the_same_corrupt_cache(
    tmp_path: Path, cached_vocabulary: dict,
) -> None:
    from cli.modelspec.snapshot import decision_vocabulary_path

    decision_vocabulary_path().write_text("not json", encoding="utf-8")
    vocab = CliRunner().invoke(cli_mod.app, ["vocab", "--json"])
    check = _run(tmp_path, BUDGET_CODING, "--check", "--json")
    assert vocab.exit_code == check.exit_code == 1
    vocab_message = json.loads(vocab.stderr)["error"]["message"]
    check_message = json.loads(check.stderr)["error"]["message"]
    assert vocab_message == check_message
    assert vocab_message.startswith("cannot read the cached decision vocabulary:")


def test_check_accepts_the_budget_coding_spec(tmp_path: Path, cached_vocabulary: dict) -> None:
    result = _run(tmp_path, BUDGET_CODING, "--check")
    assert result.exit_code == 0
    assert "ok: musts: 3, prefers: 2, snapshot: latest" in result.stdout


def test_check_suggests_a_misspelled_facet(tmp_path: Path, cached_vocabulary: dict) -> None:
    result = _run(
        tmp_path, BUDGET_CODING.replace("model.context_window", "model.context_windw"),
        "--check",
    )
    assert result.exit_code == 1
    assert "where[1]" in result.stderr
    assert "did you mean 'model.context_window'" in result.stderr


def test_check_rejects_an_unregistered_benchmark(tmp_path: Path, cached_vocabulary: dict) -> None:
    result = _run(
        tmp_path, BUDGET_CODING.replace("model.context_window >= 200000", "swe_bench_plus >= 55"),
        "--check",
    )
    assert result.exit_code == 1
    assert "unknown facet 'swe_bench_plus'" in result.stderr
    assert "swe_bench_pro" in result.stderr


def test_check_json_is_machine_readable(tmp_path: Path, cached_vocabulary: dict) -> None:
    good = _run(tmp_path, BUDGET_CODING, "--check", "--json")
    assert good.exit_code == 0
    assert json.loads(good.stdout)["ok"] is True

    bad = _run(
        tmp_path, BUDGET_CODING.replace("model.context_window", "model.context_windw"),
        "--check", "--json",
    )
    assert bad.exit_code == 1
    assert json.loads(bad.stderr)["error"]["code"] == "invalid_spec"


@pytest.mark.parametrize(
    "addition, warning",
    [
        ("capabilities: {made_up_domain: required}\n", "made_up_domain"),
        (
            "profile:\n  profile_version: 1\n  offerings:\n"
            "    - {model: lab/a, provider: made-up-provider}\n",
            "made-up-provider",
        ),
    ],
)
def test_check_accepts_advisory_vocabulary_gaps(
    tmp_path: Path, cached_vocabulary: dict, addition: str, warning: str,
) -> None:
    text = "spec_version: 1\nwhere: []\noptimize: {max: model.context_window}\n" + addition
    check = _run(tmp_path, text, "--check", "--json")
    decide = _run(tmp_path, text, "--json")
    assert check.exit_code == decide.exit_code == 0
    assert warning in check.stderr


@pytest.mark.parametrize("facet_id", ["evidence.outcome", "arena_elo_vision"])
def test_check_accepts_registered_facets_absent_from_vocabulary(
    tmp_path: Path, cached_vocabulary: dict, facet_id: str,
) -> None:
    text = (
        "spec_version: 1\nwhere: []\noptimize:\n"
        f"  max: {facet_id}\n"
    )
    check = _run(tmp_path, text, "--check", "--json")
    decide = _run(tmp_path, text, "--json")
    assert check.exit_code == decide.exit_code == 0
    assert facet_id in check.stderr


def test_check_and_decide_reject_an_unloaded_profile_with_the_same_code(
    tmp_path: Path, cached_vocabulary: dict,
) -> None:
    text = (
        "spec_version: 1\nprofile: profile:not-loaded\nwhere: []\n"
        "optimize: {max: model.context_window}\n"
    )
    check = _run(tmp_path, text, "--check", "--json")
    decide = _run(tmp_path, text, "--json")
    assert check.exit_code == decide.exit_code == 1
    assert json.loads(check.stderr)["error"]["code"] == "decision_failed"
    assert json.loads(decide.stderr)["error"]["code"] == "decision_failed"


def test_check_and_decide_agree_on_every_shipped_spec(
    tmp_path: Path, cached_vocabulary: dict,
) -> None:
    recall = sorted((REPO_ROOT / "tests" / "recall" / "specs").glob("*.yaml"))
    ui_rows = json.loads(
        (REPO_ROOT / "web" / "src" / "decide" / "__fixtures__" / "ui-specs.json")
        .read_text(encoding="utf-8")
    )
    cases = [(path.name, path.read_text(encoding="utf-8")) for path in recall]
    cases += [(row["name"], json.dumps(row["spec"])) for row in ui_rows]
    disagreements = []
    for name, text in cases:
        check = _run(tmp_path, text, "--check", "--json")
        decide = _run(tmp_path, text, "--json")
        if (check.exit_code == 0) != (decide.exit_code == 0):
            disagreements.append((name, check.exit_code, decide.exit_code))
    assert len(cases) == 223
    assert disagreements == []
