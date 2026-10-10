"""`modelspec decide` prints a readable summary, and `--why-not` answers for one model (MODEL-180)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner

from cli.modelspec import legacy as cli_mod
from decision.snapshot import SnapshotInputs, build_snapshot
from tests.snapshot_records import SOURCES, evidence, fact, model, offering
from tests.test_decision_by_model import built_snapshot

KEY = b"cli-output-test-key"

SPEC = {
    "spec_version": 1,
    "task_type": "refactor",
    "capabilities": {"software_engineering": "required"},
    "task_tokens": {"input": 40000, "output": 4000},
    "where": ["model.class = text-generator", "model.context_window >= 100000"],
    "optimize": {"weights": {"quality": 0.78, "-offering.cost_per_task": 0.22}},
    "limit": 20,
}


@pytest.fixture(scope="module")
def snapshot_bytes() -> bytes:
    return built_snapshot().to_bytes(key=KEY)


def run(tmp_path: Path, snapshot_bytes: bytes, *args: str, spec: dict | None = None):
    snapshot_path = tmp_path / "snapshot.json.gz"
    snapshot_path.write_bytes(snapshot_bytes)
    spec_path = tmp_path / "spec.yaml"
    spec_path.write_text(json.dumps(spec or SPEC), encoding="utf-8")
    return CliRunner().invoke(
        cli_mod.app,
        ["decide", str(spec_path), "--snapshot-file", str(snapshot_path), *args],
        env={"MODELSPEC_SNAPSHOT_KEY": KEY.decode()},
    )


def test_without_json_the_command_prints_a_short_summary_not_the_decision(tmp_path, snapshot_bytes):
    result = run(tmp_path, snapshot_bytes)
    assert result.exit_code == 0, result.output
    lines = result.stdout.splitlines()
    assert len(lines) <= 25, result.stdout
    assert not result.stdout.lstrip().startswith("{")
    assert "status: partial" in result.stdout, "delta may qualify, so the answer is partial"
    assert "lab/alpha" in result.stdout and "nvidia-nim" in result.stdout
    assert "$0.112" in result.stdout
    assert "1 may qualify" in result.stdout


def test_the_summary_names_the_leaders_top_reasons(tmp_path, snapshot_bytes):
    out = run(tmp_path, snapshot_bytes).stdout
    reasons = out.split("why:", 1)[1]
    assert "quality" in reasons and "weight 0.78" in reasons


def _tied_snapshot() -> bytes:
    models = [
        model(mid, facts=[
            fact("model", mid, "model.class", "text-generator"),
            fact("model", mid, "model.lifecycle", "active"),
        ])
        for mid in ("lab/alpha", "lab/beta")
    ]
    sold = [
        offering(mid, "fireworks-ai", facts=[
            fact("offering", f"fireworks-ai/{mid}/global/standard", "offering.price.input", price,
                 source="src-pricing"),
            fact("offering", f"fireworks-ai/{mid}/global/standard", "offering.price.output", price,
                 source="src-pricing"),
        ])
        for mid, price in (("lab/alpha", 3.0), ("lab/beta", 1.0))
    ]
    rows = [
        evidence("lab/alpha", "quality", 90.0, interval=[80, 95]),
        evidence("lab/beta", "quality", 88.0, interval=[82, 93]),
    ]
    built = build_snapshot(
        SnapshotInputs(models=models, offerings=sold, evidence=rows, sources=SOURCES,
                       benchmark_domains={"quality": [("software_engineering", "direct")]}),
        gate=False,
        as_of=date(2026, 9, 28),
    )
    return built.to_bytes(key=KEY)


def test_the_summary_shows_a_tied_group_not_a_single_pick(tmp_path):
    spec = SPEC | {"where": ["model.class = text-generator"],
                   "optimize": {"max": "quality @independent"}}
    out = run(tmp_path, _tied_snapshot(), spec=spec).stdout
    assert "answer: tied, lab/alpha / lab/beta" in out
    assert "cheapest: lab/beta" in out
    assert "answer: lab/" not in out


def test_the_summary_names_the_blend_each_part_alone_and_the_thin_models(tmp_path):
    from tests.test_decision_bands import LINEUP

    models, sold, rows = [], [], []
    for mid, repo, patch, proxy, price in LINEUP:
        models.append(model(mid, facts=[
            fact("model", mid, "model.class", "text-generator"),
            fact("model", mid, "model.context_window", 200_000),
            fact("model", mid, "model.weights_openness", "closed_weights"),
            fact("model", mid, "licence.user_cap", "unbounded"),
        ]))
        oid = f"cloud/{mid}/global/standard"
        sold.append(offering(mid, "cloud", facts=[
            fact("offering", oid, "offering.price.input", price, source="src-pricing"),
            fact("offering", oid, "offering.price.output", 4 * price, source="src-pricing"),
        ]))
        rows += [evidence(mid, name, score, day="2026-09-01")
                 for name, score in (("repo_work", repo), ("patch_work", patch),
                                     ("preference_proxy", proxy)) if score is not None]
    tags = {"repo_work": [("software_engineering", "direct")],
            "patch_work": [("software_engineering", "direct")],
            "preference_proxy": [("software_engineering", "proxy")]}
    built = build_snapshot(
        SnapshotInputs(models=models, offerings=sold, evidence=rows, sources=SOURCES,
                       benchmark_domains=tags,
                       benchmark_metadata={name: {"direction": "higher_is_better"}
                                           for name in tags}),
        gate=False, as_of=date(2026, 9, 29))
    spec = SPEC | {"where": ["model.class = text-generator"], "optimize": {"weights": {
        "software_engineering": 0.6, "-offering.cost_per_task": 0.4}}}
    out = run(tmp_path, built.to_bytes(key=KEY), spec=spec).stdout

    assert "blend: 60% software_engineering, 40% -offering.cost_per_task" in out
    assert "not enough evidence yet: lab/mystery (measured on 1 benchmark, 0 direct)" in out
    assert "  software_engineering alone: lab/frontier leads" in out
    assert "  -offering.cost_per_task alone: lab/mystery" in out


def test_a_decision_with_no_feasible_model_says_what_to_relax(tmp_path, snapshot_bytes):
    spec = SPEC | {"where": ["model.class = text-generator", "model.context_window >= 900000"]}
    result = run(tmp_path, snapshot_bytes, spec=spec)
    assert result.exit_code == 0, result.output
    assert "status: no_feasible" in result.stdout
    assert "relax:" in result.stdout


def test_json_is_unchanged_by_the_summary(tmp_path, snapshot_bytes):
    body = json.loads(run(tmp_path, snapshot_bytes, "--json").stdout)
    assert body["contract_version"] == "2.16"
    assert body["results"][0]["model"] == "lab/alpha"
    assert [row["model"] for row in body["by_model"]][:2] == ["lab/alpha", "lab/beta"]


def test_why_not_an_eliminated_model_names_the_failed_must(tmp_path, snapshot_bytes):
    result = run(tmp_path, snapshot_bytes, "--why-not", "lab/gamma")
    assert result.exit_code == 0, result.output
    assert "lab/gamma was eliminated" in result.stdout
    assert "model.context_window >= 100000" in result.stdout


def test_why_not_a_may_qualify_model_names_the_unknown_facet(tmp_path, snapshot_bytes):
    out = run(tmp_path, snapshot_bytes, "--why-not", "lab/delta").stdout
    assert "may qualify" in out and "model.context_window is not known" in out


def test_why_not_a_ranked_model_says_its_rank_and_what_would_move_it(tmp_path, snapshot_bytes):
    out = run(tmp_path, snapshot_bytes, "--why-not", "lab/beta").stdout
    assert "ranked #2 of 2" in out
    assert "takes first place" in out


def test_why_not_works_at_the_default_explain_level_by_asking_for_full(tmp_path, snapshot_bytes):
    """The spec's own explain level is summary, which omits eliminated models."""
    result = run(tmp_path, snapshot_bytes, "--why-not", "lab/gamma", "--explain", "summary")
    assert "was eliminated" in result.stdout


def test_why_not_json_is_the_typed_answer(tmp_path, snapshot_bytes):
    body = json.loads(run(tmp_path, snapshot_bytes, "--why-not", "lab/gamma", "--json").stdout)
    assert body["command"] == "decide"
    answer = body["why_not"]
    assert answer["verdict"] == "eliminated" and answer["model"] == "lab/gamma"
    assert answer["failed"][0]["condition"] == "model.context_window >= 100000"


def test_why_not_an_unknown_model_says_so_and_exits_zero(tmp_path, snapshot_bytes):
    result = run(tmp_path, snapshot_bytes, "--why-not", "lab/nowhere")
    assert result.exit_code == 0
    assert "lab/nowhere is not in this decision" in result.stdout


def test_why_not_cannot_be_combined_with_compare_to(tmp_path, snapshot_bytes):
    result = run(tmp_path, snapshot_bytes, "--why-not", "lab/beta", "--compare-to", "previous",
                 "--json")
    assert result.exit_code == 1
    error = json.loads(result.stderr)["error"]
    assert error["code"] == "decision_failed" and "--compare-to" in error["message"]
