"""The decision-engine accuracy harness reports each independent layer honestly."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from cli.modelspec import legacy as cli_mod
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
        approved_baseline={"Q01": "partial"},
    )

    assert result.status == "pass"
    assert result.gating is True
    assert result.counts == {
        "pass": 1,
        "partial": 0,
        "fail": 0,
        "baseline_regressions": 0,
        "regressions": 0,
        "improvements": 0,
    }


def test_recall_baseline_cannot_hide_a_regression() -> None:
    result = accuracy.recall_ratchet(
        {"Q01": "fail"},
        (_recall_question("Q01", "fail"),),
        gating=True,
        update_command="unused",
        approved_baseline={"Q01": "pass"},
    )

    assert result.status == "fail"
    assert result.counts["baseline_regressions"] == 1
    assert result.details == [
        {
            "id": "Q01",
            "change": "baseline_regression",
            "transition": "pass -> fail",
            "causes": ["proposed baseline"],
        }
    ]


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


def test_recall_approval_guard_does_not_cover_ratchet_documentation() -> None:
    result = accuracy.check_recall_approval(["tests/recall/RATCHET.md"], labels=[])

    assert result.status == "pass"
    assert result.details == []


def test_report_writes_publishable_markdown_and_json(tmp_path: Path) -> None:
    report = accuracy.AccuracyReport(
        generated_at="2026-09-25T12:00:00Z",
        profile="pr",
        snapshot="snap_test_accuracy",
        layers=(
            accuracy.LayerResult("freshness", "pass", True, "Fresh enough", {"checked": 1}),
            accuracy.LayerResult(
                "frozen_image_engine_recall", "report", False, "Jamie approval pending"
            ),
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


def _fidelity(tmp_path: Path, region: str, unread=None):
    queue = Queue(tmp_path / "verification")
    log = VerificationLog(tmp_path / "verification")
    claim = _claim("lab/model#model.context_window", "context", 10)
    result = accuracy.verify_fidelity_sample(
        [claim],
        regions=DictRegions(region),
        extractors=[KeyValueExtractor()],
        queue=queue,
        log=log,
        today=date(2026, 9, 29),
        source_urls={"source": "https://example.test/model"},
        unread=unread,
    )
    return claim, result, queue, log


def test_a_value_no_reader_finds_in_a_changed_source_is_requeued_not_quarantined(
    tmp_path: Path,
) -> None:
    claim, result, queue, log = _fidelity(tmp_path, "Model: Model\nrelease: soon")

    assert result.status == "pass"
    assert result.details[0]["outcome"] == "undetermined"
    assert result.details[0]["reason"] == "source_changed"
    assert result.counts["undetermined"] == 1
    assert result.counts["verified"] == 0
    assert log.latest() == {}
    assert queue.recrawl_requests() == []
    assert queue.pending(changed_only=True) == ([], [claim.target])


def test_a_value_no_reader_finds_in_its_unchanged_source_is_undetermined_not_passed(
    tmp_path: Path,
) -> None:
    claim, result, queue, log = _fidelity(
        tmp_path,
        "Model: Model\nrelease: soon",
        {("fact", "lab/model#model.context_window"): "source_unchanged"},
    )

    assert result.details[0]["outcome"] == "undetermined"
    assert result.details[0]["reason"] == "source_unchanged"
    assert result.counts["verified"] == 0
    assert log.latest() == {}
    assert queue.pending() == ([], [])


def test_a_mismatch_only_on_an_unstated_condition_is_still_a_mismatch() -> None:
    from decision.verify import Diff, Result

    target = TargetRef(kind="evidence", id="lab/model#bench#1")
    condition = Result(target, "mismatch", diffs=(Diff("harness", "unregistered", None),))
    value = Result(target, "mismatch", diffs=(Diff("value", "92.0 percent", None),))

    assert accuracy._read_nothing(condition) is False
    assert accuracy._read_nothing(value) is True


class _Fetches:
    def __init__(self, bodies):
        self.bodies = bodies

    def fetch(self, url, *, etag=None, last_modified=None):
        from decision.sources import FetchResult

        return FetchResult("ok", 200, body=self.bodies[url], content_type="text/plain")


def test_current_copies_pin_new_copies_and_say_what_an_unread_value_is(tmp_path: Path) -> None:
    from decision.sources import CopyStore, fingerprint_bytes

    same, moved = b"context: 10\n", b"context: 10 tokens, revised\n"
    sources = {
        sid: Source(
            id=sid,
            url=f"https://example.test/{sid}",
            fetch="http",
            normaliser="text-default",
            cited_regions=[{"id": "table", "locator": {"kind": "page", "value": ""}}],
        )
        for sid in ("same", "moved")
    }

    def claim(target, source_id, snapshot_ref):
        return replace(
            _claim(target, "context", 10),
            sources=(SourceRef(source_id=source_id, snapshot_ref=snapshot_ref,
                               cited_regions=["table"]),),
        )

    batch = [
        (claim("lab/a#context", "same", fingerprint_bytes(same)), "key-value-match@1"),
        (claim("lab/b#context", "same", fingerprint_bytes(same)), "retained-source-proof@1"),
        (claim("lab/c#context", "moved", fingerprint_bytes(b"old copy")), "key-value-match@1"),
    ]
    store = CopyStore(tmp_path)

    current, unread = accuracy._current_copies(
        batch,
        sources=sources,
        store=store,
        fetcher=_Fetches({"https://example.test/same": same,
                          "https://example.test/moved": moved}),
        as_of=date(2026, 9, 29),
        nightly_methods=frozenset({"key-value-match@1"}),
    )

    assert unread == {
        ("fact", "lab/a#context"): "mismatch",
        ("fact", "lab/b#context"): "source_unchanged",
        ("fact", "lab/c#context"): "source_changed",
    }
    assert current[2].sources[0].snapshot_ref == fingerprint_bytes(moved)
    assert store.get(current[2].sources[0].snapshot_ref) == moved


def test_a_promoted_mismatch_is_queued_as_a_mismatch(tmp_path: Path) -> None:
    claim, result, queue, log = _fidelity(
        tmp_path,
        "no key value pairs here",
        {("fact", "lab/model#model.context_window"): "mismatch"},
    )

    assert result.details[0]["outcome"] == "mismatch"
    assert queue.recrawl_requests() == [(claim.target, "mismatch")]


def test_fidelity_fails_when_too_many_draws_are_undetermined() -> None:
    config = accuracy.load_config(Path("accuracy.yaml")).data_fidelity
    counts = dict.fromkeys(accuracy.FIDELITY_OUTCOMES, 0)

    ok = {**counts, "verified": 12, "undetermined": 6}
    too_many = {**counts, "verified": 12, "undetermined": 20}
    short = {**counts, "verified": 3, "undetermined": 3}

    assert accuracy.fidelity_verdict(ok, drawn=18, wanted=12, config=config)[0] == "pass"
    status, summary, share = accuracy.fidelity_verdict(
        too_many, drawn=32, wanted=12, config=config
    )
    assert (status, round(share, 3)) == ("fail", 0.625)
    assert "20 of 32 draws (62%) were undetermined" in summary
    assert accuracy.fidelity_verdict(short, drawn=6, wanted=12, config=config)[0] == "fail"


def test_a_nightly_reader_that_cannot_reread_its_own_verified_bytes_fails(
    tmp_path: Path,
) -> None:
    claim, result, queue, log = _fidelity(
        tmp_path,
        "Model: Model\nrelease: soon",
        {("fact", "lab/model#model.context_window"): "mismatch"},
    )

    assert result.status == "fail"
    assert result.details[0]["outcome"] == "mismatch"
    assert queue.recrawl_requests() == [(claim.target, "mismatch")]


def test_an_open_llm_leaderboard_projection_is_rebuilt_from_the_fetched_result() -> None:
    from decision.verify import StructuredDataExtractor, verify

    url = (
        "https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/"
        "23474373f8874f9057d23b97e5a41e911d2721c5/lab/Model/results_2024-04-16T04-20-00.json"
    )
    raw = json.dumps(
        {
            "config_general": {"model_name": "lab/Model"},
            "results": {"harness|hendrycksTest-us_foreign_policy|5": {"acc": 0.92}},
        }
    ).encode()
    claim = Claim(
        target=TargetRef(kind="evidence", id="lab/model#mmlu_us_foreign_policy#1"),
        subject="lab/model",
        names=("lab/Model",),
        field="mmlu_us_foreign_policy",
        label="mmlu_us_foreign_policy",
        value=92.0,
        unit="percent",
        collector=accuracy_collector("hf-result-projection@1"),
        sources=(SourceRef(source_id="oll", snapshot_ref="sha256:" + "a" * 64,
                           cited_regions=["rows"]),),
    )

    projected = accuracy._PROJECTIONS["hf-result-projection@1"](url, raw)

    assert json.loads(projected)["rows"][0]["mmlu_us_foreign_policy"] == "92.0%"
    result = verify(
        claim,
        DictRegions(projected.decode()),
        [StructuredDataExtractor()],
        today=date(2026, 9, 29),
    )
    assert result.outcome == "verified"


def accuracy_collector(method: str) -> VerificationActor:
    return VerificationActor(agent="openai-codex-model-118", model_family="openai", method=method)


def test_the_coverage_report_watches_the_nightly() -> None:
    targets = yaml.safe_load(Path("scripts/slo/targets.yaml").read_text())

    assert "accuracy-nightly.yml" in {row["file"] for row in targets["workflows"]}


def test_reference_disagreement_names_the_engine_evidence_responsible() -> None:
    config = accuracy.load_config(Path("accuracy.yaml")).reference

    comparison = accuracy.compare_rankings(
        domain="software_engineering",
        engine_basis="domain_capability",
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
    assert comparison["responsible_evidence"] == [
        {"model": "lab/a", "value": 90, "record_ids": ["e-a"]},
        {"model": "lab/b", "value": 80, "record_ids": ["e-b"]},
    ]
    assert comparison["source_url"] == "https://example.test/board"
    assert comparison["read_date"] == "2026-09-25"


def test_reference_boards_sharing_too_few_models_are_undetermined_not_disagreeing() -> None:
    config = accuracy.load_config(Path("accuracy.yaml")).reference

    comparison = accuracy.compare_rankings(
        domain="retrieval",
        engine_basis="domain_capability",
        engine_rows=[{"model": "lab/reranker-a"}, {"model": "lab/reranker-b"}],
        reference_board="mteb-eng-v2",
        reference_rows=[{"model": "lab/embedder-a"}, {"model": "lab/reranker-b"}],
        source_url="https://example.test/board",
        read_date=date(2026, 9, 25),
        config=config,
    )

    assert comparison["status"] == "undetermined"
    assert comparison["reason"] == "too_few_common_models"
    assert comparison["common_models"] == 1


def test_a_board_missing_the_engine_leaders_is_judged_on_the_models_it_shares() -> None:
    config = accuracy.load_config(Path("accuracy.yaml")).reference
    newest = [{"model": f"lab/new-{i}"} for i in range(5)]
    shared = [{"model": f"lab/old-{i}"} for i in range(3)]

    comparison = accuracy.compare_rankings(
        domain="software_engineering",
        engine_basis="domain_capability",
        engine_rows=newest + shared,
        reference_board="epoch-swe-bench-verified",
        reference_rows=[{"model": "lab/unrated"}, *shared],
        source_url="https://example.test/board",
        read_date=date(2026, 9, 25),
        config=config,
    )

    assert comparison["status"] == "pass"
    assert comparison["engine_top_k"] == ["lab/old-0", "lab/old-1", "lab/old-2"]
    assert comparison["rank_correlation"] == 1.0


class _Estimate:
    def __init__(self, value: float, width: float):
        self.value, self.low, self.high = value, value - width / 2, value + width / 2


class _CapabilitySnapshot(FakeSnapshot):
    estimates = {"lab/sure": _Estimate(1.0, 1.0), "lab/thin": _Estimate(2.0, 3.4)}

    def candidates(self):
        return tuple(self.estimates)

    def capability_estimate(self, candidate, domain):
        return self.estimates[candidate]

    def capability_drivers(self, candidate, domain):
        return ()


def test_engine_order_leaves_out_models_the_engine_calls_too_thin_to_rank() -> None:
    rows = accuracy._engine_domain_ranking(_CapabilitySnapshot(), "software_engineering")

    assert [row["model"] for row in rows] == ["lab/sure"]


def test_a_gate_that_decided_nothing_fails_the_report() -> None:
    report = accuracy.AccuracyReport(
        generated_at="2026-09-29T06:00:00Z",
        profile="nightly",
        snapshot=None,
        layers=(accuracy.LayerResult("reference_agreement", "undetermined", True, "none"),),
    )

    assert report.status == "fail"


def test_reference_correlation_is_null_when_two_ranks_cannot_be_compared() -> None:
    assert accuracy.spearman({"lab/a": 1}, {"lab/a": 1}, minimum_common=2) is None


def test_accuracy_workflows_split_pr_and_nightly_layers() -> None:
    pr = Path(".github/workflows/accuracy.yml").read_text()
    pr_workflow = yaml.load(pr, Loader=yaml.BaseLoader)
    pr_paths = pr_workflow["on"]["pull_request"]["paths"]
    nightly = Path(".github/workflows/accuracy-nightly.yml").read_text()
    refresh = Path(".github/private-writers/leaderboard-refresh.yml").read_text()

    for path in ("decision/**", "registry/**", "models/**", "offerings/**", "verification/**"):
        assert path in pr
    assert "scripts/accuracy.py --profile pr" in pr
    assert "scripts/accuracy.py --profile nightly" in nightly
    assert (
        '"nightly": ("data_fidelity", "reference_agreement", "frozen_image_engine_recall")'
        in Path("scripts/accuracy.py").read_text()
    )
    assert "cron:" in nightly
    assert "timeout-minutes:" in nightly
    assert "--check-recall-approval" in pr
    assert "labeled" in pr
    assert "unlabeled" in pr
    assert "pulls/${{ github.event.pull_request.number }}" in pr
    assert "github.event.pull_request.labels" not in pr
    assert "git merge-base" in pr
    assert "--approved-recall-baseline" in pr
    assert 'cp tests/recall/baseline.json' not in pr
    assert "scripts/recall_run.py" in pr_paths
    assert "check_score_only" in refresh
    assert "gh pr merge" not in refresh
    assert "continue-on-error" not in pr + nightly


def test_frozen_image_change_requires_recorded_verdict_and_changed_reason() -> None:
    kwargs = dict(gating=True, update_command="unused", approved_baseline={"Q04": "pass"})
    question = (_recall_question("Q04", "fail"),)
    reason = {"Q04": "No offering in the frozen image; private Q04 passes."}
    allowed = accuracy.recall_ratchet(
        {"Q04": "fail"}, question, frozen_image_reason=reason, **kwargs
    )
    assert allowed.status == "pass"
    assert allowed.details == [
        {
            "id": "Q04",
            "change": "frozen_image_baseline_change",
            "transition": "pass -> fail",
            "frozen_image_reason": reason["Q04"],
        }
    ]
    unchanged = accuracy.recall_ratchet(
        {"Q04": "fail"},
        question,
        frozen_image_reason=reason,
        approved_frozen_image_reason=reason,
        **kwargs,
    )
    assert unchanged.status == "fail"
    unrecorded = accuracy.recall_ratchet(
        {"Q04": "partial"}, question, frozen_image_reason=reason, **kwargs
    )
    assert unrecorded.status == "fail"
    assert unrecorded.counts["regressions"] == 1


def test_frozen_image_gate_requires_reasons_for_every_below_pass_baseline() -> None:
    result = accuracy.recall_ratchet(
        {"Q07": "partial"},
        (_recall_question("Q07", "partial"),),
        gating=True,
        update_command="unused",
        frozen_image_reason={},
    )
    assert result.status == "fail"
    assert result.details == [{"id": "Q07", "change": "missing_frozen_image_reason"}]


def test_frozen_image_reason_cannot_hide_a_removed_question() -> None:
    result = accuracy.recall_ratchet(
        {},
        (),
        gating=True,
        update_command="unused",
        approved_baseline={"Q04": "pass"},
        frozen_image_reason={"Q04": "missing frozen data"},
    )
    assert result.status == "fail"


def test_baseline_update_refuses_unexplained_drop_and_preserves_reasons(
    tmp_path, monkeypatch
) -> None:
    from types import SimpleNamespace

    import scripts.recall_run as recall

    baseline_path = tmp_path / "tests/recall/baseline.json"
    baseline_path.parent.mkdir(parents=True)
    baseline_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "as_of": "2026-09-27",
                "snapshot": "before",
                "verdicts": {"Q04": "pass"},
            }
        )
    )
    monkeypatch.setattr(
        recall,
        "run",
        lambda **kwargs: SimpleNamespace(
            snapshot_id="after", questions=(_recall_question("Q04", "fail"),)
        ),
    )
    with pytest.raises(ValueError, match="frozen_image_reason required"):
        accuracy.update_recall_baseline(root=tmp_path, snapshot_file=None, as_of=date(2026, 10, 1))
    result = accuracy.update_recall_baseline(
        root=tmp_path,
        snapshot_file=None,
        as_of=date(2026, 10, 1),
        frozen_image_reason={"Q04": "No frozen offering; private passes."},
    )
    assert result.verdicts == {"Q04": "fail"}
    assert accuracy.load_recall_baseline(baseline_path).frozen_image_reason == {
        "Q04": "No frozen offering; private passes."
    }
