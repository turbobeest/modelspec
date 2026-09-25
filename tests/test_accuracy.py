"""The decision-engine accuracy harness reports each independent layer honestly."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from typer.testing import CliRunner

from cli.modelspec import cli as cli_mod
from decision.model import SourceRef, TargetRef, VerificationActor
from decision.verify import Claim, KeyValueExtractor, Queue, VerificationLog
from scripts import accuracy


class FakeFact:
    def __init__(self, value=None, state: str = "known"):
        self.value = value
        self.state = state


class FakeEvidence:
    def __init__(self, benchmark: str, value: float, when: date, *, date_type="published"):
        self.benchmark_id = benchmark
        self.value = value
        self.date = when
        self.date_type = date_type
        self.verified = True
        self.record_id = f"evidence:{benchmark}"


class FakeSnapshot:
    snapshot_id = "snap_test_accuracy"
    as_of = date(2026, 9, 25)

    def __init__(self, *, evidence=(), released=date(2026, 9, 1)):
        self._evidence = tuple(evidence)
        self._released = released

    def candidates(self):
        return ("lab/model",)

    def kind(self, candidate):
        return "model"

    def model_of(self, candidate):
        return candidate

    def lifecycle(self, candidate):
        return "active"

    def fact(self, candidate, facet):
        if facet == "model.release_date":
            return FakeFact(self._released.isoformat())
        return FakeFact(state="unknown")

    def domain_ids(self):
        return ("software_engineering",)

    def evidence_for_domain(self, candidate, domain):
        return self._evidence

    def benchmark_ids(self):
        return tuple(sorted({row.benchmark_id for row in self._evidence}))


def test_thresholds_and_budgets_live_in_one_config() -> None:
    config = accuracy.load_config(Path("accuracy.yaml"))

    assert config.freshness.lineup_evidence_grace_days == 7
    assert config.freshness.live_leaderboard_max_age_days == 30
    assert config.data_fidelity.max_firecrawl_credits == 10
    assert config.reference.top_k > 0


def test_freshness_fails_for_an_established_lineup_model_without_evidence() -> None:
    result = accuracy.check_freshness(
        FakeSnapshot(),
        as_of=date(2026, 9, 25),
        config=accuracy.load_config(Path("accuracy.yaml")).freshness,
    )

    assert result.status == "fail"
    assert result.details[0]["model"] == "lab/model"
    assert result.details[0]["reason"] == "no_verified_domain_evidence"


def test_freshness_fails_for_a_stale_live_leaderboard_reading() -> None:
    evidence = FakeEvidence("terminal_bench_v4_0", 70, date(2026, 8, 1), date_type="evaluated")
    result = accuracy.check_freshness(
        FakeSnapshot(evidence=(evidence,)),
        as_of=date(2026, 9, 25),
        config=accuracy.load_config(Path("accuracy.yaml")).freshness,
    )

    assert result.status == "fail"
    assert any(row["reason"] == "stale_live_leaderboard" for row in result.details)
    assert any(row["benchmark"] == "terminal_bench_v4_0" for row in result.details)


def test_golden_findings_are_report_only() -> None:
    result = accuracy.golden_result({"pass": 12, "partial": 3, "fail": 5})

    assert result.status == "report"
    assert result.gating is False
    assert result.counts == {"pass": 12, "partial": 3, "fail": 5}


def test_report_writes_publishable_markdown_and_json(tmp_path: Path) -> None:
    report = accuracy.AccuracyReport(
        generated_at="2026-09-25T12:00:00Z",
        profile="pr",
        snapshot="snap_test_accuracy",
        layers=(
            accuracy.LayerResult("freshness", "pass", True, "Fresh enough", {"checked": 1}),
            accuracy.LayerResult("golden_answers", "report", False, "Jamie approval pending"),
        ),
    )

    markdown, payload = accuracy.write_report(report, tmp_path)

    assert "# Decision engine accuracy" in markdown.read_text()
    assert "PASS" in markdown.read_text()
    raw = json.loads(payload.read_text())
    assert raw["status"] == "pass"
    assert raw["layers"][1]["gating"] is False


def test_modelspect_verify_accuracy_is_a_command_group(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        accuracy,
        "run_profile",
        lambda **kwargs: accuracy.AccuracyReport(
            generated_at="2026-09-25T12:00:00Z",
            profile="pr",
            snapshot="snap_test_accuracy",
            layers=(accuracy.LayerResult("freshness", "pass", True, "Fresh enough"),),
        ),
    )

    result = CliRunner().invoke(
        cli_mod.app,
        ["verify", "accuracy", "--profile", "pr", "--output-dir", str(tmp_path)],
    )

    assert result.exit_code == 0, result.output
    assert "Decision engine accuracy" in result.output
    assert (tmp_path / "accuracy.json").is_file()


class DictRegions:
    def __init__(self, text: str):
        self.region = text

    def text(self, source_id, copy_ref, region_id):
        return self.region


def _claim(target: str, field: str, value, subject: str = "lab/model") -> Claim:
    return Claim(
        target=TargetRef(kind="evidence" if field == "bench" else "fact", id=target),
        subject=subject,
        names=("Model",),
        field=field,
        label=field,
        value=value,
        collector=VerificationActor(agent="collector", model_family="gpt", method="read"),
        sources=(
            SourceRef(
                source_id="source",
                snapshot_ref="sha256:" + "a" * 64,
                cited_regions=["table"],
            ),
        ),
    )


def test_fidelity_sampling_covers_facts_evidence_and_offerings() -> None:
    claims = [
        _claim("lab/model#model.context_window", "model.context_window", 10),
        _claim("e-1", "bench", 80),
        _claim(
            "provider/lab/model/global/standard#offering.price.input",
            "offering.price.input",
            1,
            subject="provider/lab/model/global/standard",
        ),
    ]

    sampled = accuracy.sample_verified_claims(claims, size=3, seed="fixed")

    assert {accuracy.claim_category(row) for row in sampled} == {
        "fact",
        "evidence",
        "offering",
    }


def test_a_fidelity_mismatch_enters_the_existing_recrawl_queue(tmp_path: Path) -> None:
    queue = Queue(tmp_path / "verification")
    log = VerificationLog(tmp_path / "verification")
    claim = _claim("lab/model#model.context_window", "context", 10)

    result = accuracy.verify_fidelity_sample(
        [claim],
        regions=DictRegions("Model: Model\ncontext: 20"),
        extractors=[KeyValueExtractor()],
        queue=queue,
        log=log,
        today=date(2026, 9, 25),
        source_urls={"source": "https://example.test/model"},
    )

    assert result.status == "fail"
    assert result.details[0]["outcome"] == "mismatch"
    assert queue.recrawl_requests() == [(claim.target, "mismatch")]
    assert log.latest()[("fact", claim.target.id)].outcome == "mismatch"
    assert result.details[0]["source_urls"] == ["https://example.test/model"]
    assert result.details[0]["read_date"] == "2026-09-25"


def test_reference_disagreement_names_the_engine_evidence_responsible() -> None:
    config = accuracy.load_config(Path("accuracy.yaml")).reference

    comparison = accuracy.compare_rankings(
        domain="software_engineering",
        engine_basis="direct_benchmark",
        engine_benchmark="terminal_bench_v4_0",
        engine_rows=[
            {"model": "lab/a", "value": 90, "record_ids": ["e-a"]},
            {"model": "lab/b", "value": 80, "record_ids": ["e-b"]},
        ],
        reference_board="terminal-bench-4.0",
        reference_rows=[
            {"model": "lab/b", "value": 95},
            {"model": "lab/a", "value": 70},
        ],
        source_url="https://example.test/board",
        read_date=date(2026, 9, 25),
        config=config,
    )

    assert comparison["status"] == "fail"
    assert comparison["rank_correlation"] == -1.0
    assert comparison["engine_benchmark"] == "terminal_bench_v4_0"
    assert comparison["responsible_evidence"] == [
        {"model": "lab/a", "value": 90, "record_ids": ["e-a"]},
        {"model": "lab/b", "value": 80, "record_ids": ["e-b"]},
    ]
    assert comparison["source_url"] == "https://example.test/board"
    assert comparison["read_date"] == "2026-09-25"


def test_reference_correlation_is_null_when_two_ranks_cannot_be_compared() -> None:
    assert accuracy.spearman({"lab/a": 1}, {"lab/a": 1}, minimum_common=2) is None


def test_accuracy_workflows_split_pr_and_nightly_layers() -> None:
    pr = Path(".github/workflows/accuracy.yml").read_text()
    nightly = Path(".github/workflows/accuracy-nightly.yml").read_text()

    for path in ("decision/**", "registry/**", "models/**", "offerings/**", "verification/**"):
        assert path in pr
    assert "scripts/accuracy.py --profile pr" in pr
    assert "scripts/accuracy.py --profile nightly" in nightly
    assert "cron:" in nightly
    assert "issues: write" in nightly
    assert "if: failure()" in nightly
    assert "github.rest.issues.create" in nightly
    assert "continue-on-error" not in pr + nightly
