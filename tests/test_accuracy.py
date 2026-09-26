"""The decision-engine accuracy harness reports each independent layer honestly."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from typer.testing import CliRunner

from cli.modelspec import cli as cli_mod
from decision.model import SourceRef, TargetRef, VerificationActor
from decision.sources import Source
from decision.verify import Claim, KeyValueExtractor, Queue, VerificationLog
from scripts import accuracy
from scripts.recall_run import Finding, QuestionResult


class FakeFact:
    def __init__(self, value=None, state: str = "known"):
        self.value = value
        self.state = state


class FakeEvidence:
    def __init__(
        self,
        benchmark: str,
        value: float,
        when: date,
        *,
        date_type="published",
        source_kind=None,
        source_ids=(),
        verified_at=None,
    ):
        self.benchmark_id = benchmark
        self.value = value
        self.date = when
        self.date_type = date_type
        self.source_kind = source_kind
        self.source_ids = tuple(source_ids)
        self.verified_at = verified_at
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

    def record(self, record_id):
        row = next(row for row in self._evidence if row.record_id == record_id)
        return {
            "source_kind": row.source_kind,
            "evidence_date": row.date.isoformat(),
            "date_type": row.date_type,
            "verified_at": row.verified_at.isoformat() if row.verified_at else None,
        }


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
    evidence = FakeEvidence(
        "terminal_bench_v4_0",
        70,
        date(2026, 8, 1),
        date_type="observed",
    )
    result = accuracy.check_freshness(
        FakeSnapshot(evidence=(evidence,)),
        as_of=date(2026, 9, 25),
        config=accuracy.load_config(Path("accuracy.yaml")).freshness,
    )

    assert result.status == "fail"
    assert any(row["reason"] == "stale_live_leaderboard" for row in result.details)
    assert any(row["benchmark"] == "terminal_bench_v4_0" for row in result.details)


def test_freshness_uses_when_a_live_board_was_observed_not_when_run_was_evaluated() -> None:
    evidence = FakeEvidence(
        "terminal_bench_v4_0",
        70,
        date(2026, 7, 1),
        date_type="evaluated",
        source_kind="live_leaderboard",
        verified_at=date(2026, 9, 24),
    )

    result = accuracy.check_freshness(
        FakeSnapshot(evidence=(evidence,)),
        as_of=date(2026, 9, 25),
        config=accuracy.load_config(Path("accuracy.yaml")).freshness,
    )

    assert result.status == "pass"
    assert result.counts["live_readings"] == 1
    assert result.details == []


def test_freshness_exempts_an_old_static_evaluated_result() -> None:
    evidence = FakeEvidence(
        "gpqa_diamond",
        80.3,
        date(2026, 7, 1),
        date_type="evaluated",
        source_kind="independent_evaluator",
        verified_at=date(2026, 7, 2),
    )

    result = accuracy.check_freshness(
        FakeSnapshot(evidence=(evidence,)),
        as_of=date(2026, 9, 25),
        config=accuracy.load_config(Path("accuracy.yaml")).freshness,
    )

    assert result.status == "pass"
    assert result.counts["live_readings"] == 0
    assert result.details == []


def test_freshness_uses_registered_source_volatility() -> None:
    live = Source(
        id="live-board",
        url="https://example.test/live",
        volatility="live",
    )
    static = Source(
        id="static-paper",
        url="https://example.test/paper",
    )
    old_live = FakeEvidence(
        "live_benchmark",
        70,
        date(2026, 7, 1),
        source_ids=(live.id,),
        verified_at=date(2026, 7, 1),
    )
    old_static = FakeEvidence(
        "static_benchmark",
        80,
        date(2026, 7, 1),
        source_ids=(static.id,),
        verified_at=date(2026, 7, 1),
    )

    result = accuracy.check_freshness(
        FakeSnapshot(evidence=(old_live, old_static)),
        as_of=date(2026, 9, 25),
        config=accuracy.load_config(Path("accuracy.yaml")).freshness,
        sources={live.id: live, static.id: static},
    )

    assert result.status == "fail"
    assert result.counts["live_readings"] == 1
    assert [row["benchmark"] for row in result.details] == ["live_benchmark"]
    assert result.details[0]["reason"] == "stale_live_leaderboard"


def _recall_question(
    question_id: str, verdict: str, cause: str = "engine_behavior"
) -> QuestionResult:
    return QuestionResult(
        id=question_id,
        question=f"Question {question_id}",
        verdict=verdict,
        decision=None,
        findings=(Finding(cause, verdict, "test finding"),),
    )


def test_recall_regression_fails_and_names_its_cause() -> None:
    result = accuracy.recall_ratchet(
        {"Q01": "pass", "Q02": "partial"},
        (_recall_question("Q01", "partial", "missing_data"), _recall_question("Q02", "fail")),
        gating=True,
        update_command="python scripts/accuracy.py --update-recall-baseline --date 2026-09-25",
    )

    assert result.status == "fail"
    assert result.gating is True
    assert result.counts["regressions"] == 2
    assert result.details[0]["transition"] == "pass -> partial"
    assert result.details[0]["causes"] == ["missing data"]
    assert result.details[1]["causes"] == ["engine behavior"]


def test_unrecorded_recall_improvement_fails_with_update_command() -> None:
    command = "python scripts/accuracy.py --update-recall-baseline --date 2026-09-25"
    result = accuracy.recall_ratchet(
        {"Q01": "partial"},
        (_recall_question("Q01", "pass"),),
        gating=True,
        update_command=command,
    )

    assert result.status == "fail"
    assert result.details[0]["transition"] == "partial -> pass"
    assert command in result.summary


def test_recorded_recall_improvement_passes() -> None:
    result = accuracy.recall_ratchet(
        {"Q01": "pass"},
        (_recall_question("Q01", "pass"),),
        gating=True,
        update_command="unused",
    )

    assert result.status == "pass"
    assert result.gating is True
    assert result.counts == {
        "pass": 1,
        "partial": 0,
        "fail": 0,
        "regressions": 0,
        "improvements": 0,
    }


def test_nightly_reports_recall_regressions_without_gating() -> None:
    result = accuracy.recall_ratchet(
        {"Q01": "pass"},
        (_recall_question("Q01", "fail"),),
        gating=False,
        update_command="unused",
    )

    assert result.status == "report"
    assert result.gating is False
    assert result.counts["regressions"] == 1


def test_recall_approval_guard_requires_the_label_for_spec_edits() -> None:
    changed = ["tests/recall/specs/Q01.yaml", "decision/engine.py"]

    denied = accuracy.check_recall_approval(changed, labels=[])
    allowed = accuracy.check_recall_approval(changed, labels=["recall-approved"])

    assert denied.status == "fail"
    assert denied.details == ["tests/recall/specs/Q01.yaml"]
    assert "recall-approved" in denied.summary
    assert allowed.status == "pass"


def test_recall_approval_guard_covers_answers_and_approval_record() -> None:
    changed = ["tests/recall/expected.yaml", "tests/recall/README.md"]

    result = accuracy.check_recall_approval(changed, labels=[])

    assert result.status == "fail"
    assert result.details == sorted(changed)


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
    refresh = Path(".github/workflows/leaderboard-refresh.yml").read_text()

    for path in ("decision/**", "registry/**", "models/**", "offerings/**", "verification/**"):
        assert path in pr
    assert "scripts/accuracy.py --profile pr" in pr
    assert "scripts/accuracy.py --profile nightly" in nightly
    assert (
        '"nightly": ("data_fidelity", "reference_agreement", "golden_answers")'
        in Path("scripts/accuracy.py").read_text()
    )
    assert "cron:" in nightly
    assert "issues: write" in nightly
    assert "if: failure()" in nightly
    assert "github.rest.issues.create" in nightly
    assert "--check-recall-approval" in pr
    assert "Decision accuracy" in refresh
    assert "gh run watch" in refresh
    assert refresh.index("gh run watch") < refresh.index("gh pr merge --auto --squash")
    assert "continue-on-error" not in pr + nightly
