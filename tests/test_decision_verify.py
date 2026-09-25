"""MODEL-140: two-key verification and quarantine (design §5, "Two keys").

The agent that collects a value never verifies it. These tests run the seeded
error fixture in ``tests/fixtures/verification`` end to end: every correct value
must end ``verified`` and every seeded error ``mismatch``, ``unreachable`` or
unverified, so quarantined. No network and no model call: the LLM extractor is
exercised with a fake completion.
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from decision import verify
from decision.model import (
    SourceRef,
    TargetRef,
    Verification,
    VerificationActor,
    VerificationTarget,
    value_hash,
)
from decision.sources import CopyStore, RecheckReport, SourceSnapshot, SourceState

FIXTURES = Path(__file__).parent / "fixtures" / "verification"
TODAY = date(2026, 9, 24)
NOW = datetime(2026, 9, 24, 12, tzinfo=UTC)
SPEC = yaml.safe_load((FIXTURES / "claims.yaml").read_text())
COLLECTOR = VerificationActor(**SPEC["collector"])


def _claim(entry: dict, store: CopyStore) -> verify.Claim:
    src = entry["source"]
    copy = src["copy"]
    ref = store.put((FIXTURES / copy).read_bytes()) if copy else "sha256:" + "0" * 64
    return verify.Claim(
        target=TargetRef(kind=entry.get("kind", "evidence"), id=entry["id"]),
        subject=entry["subject"],
        names=tuple(entry["names"]),
        field=entry["field"],
        label=entry.get("label"),
        value=entry["value"],
        unit=entry.get("unit"),
        conditions=entry.get("conditions", {}),
        collector=COLLECTOR,
        sources=(SourceRef(source_id=src["id"], snapshot_ref=ref, cited_regions=src["regions"]),),
    )


@pytest.fixture
def store(tmp_path) -> CopyStore:
    return CopyStore(tmp_path / "copies")


@pytest.fixture
def regions(store) -> verify.StoredRegions:
    return verify.StoredRegions(store, verify.load_sources(FIXTURES / "sources.yaml"))


@pytest.fixture
def log(tmp_path) -> verify.VerificationLog:
    return verify.VerificationLog(tmp_path / "verification")


def _seeded_run(store, regions, log, **kwargs) -> verify.RunReport:
    queue = verify.Queue(log.directory)
    for entry in SPEC["claims"]:
        queue.file(_claim(entry, store), at=NOW)
    return verify.run(queue, log, regions, verify.deterministic_extractors(), today=TODAY,
                      **kwargs)


# --- the seeded error fixture ------------------------------------------------------------------


def test_every_seeded_claim_ends_as_expected(store, regions, log) -> None:
    report = _seeded_run(store, regions, log)
    got = {r.target.id: r for r in report.results}
    assert set(got) == {e["id"] for e in SPEC["claims"]}
    for entry in SPEC["claims"]:
        result = got[entry["id"]]
        assert result.outcome == entry["expect"], (entry["id"], result)
        if "expect_diff" in entry:
            assert sorted(d.field for d in result.diffs) == sorted(entry["expect_diff"]), (
                entry["id"], result.diffs)


def test_seeded_errors_are_quarantined_and_correct_values_are_not(store, regions, log) -> None:
    _seeded_run(store, regions, log)
    for entry in SPEC["claims"]:
        target = TargetRef(kind=entry.get("kind", "evidence"), id=entry["id"])
        assert log.is_quarantined(target) is (entry["expect"] != "verified"), entry["id"]
    quarantined = {t.id for t in log.quarantined_values()}
    assert quarantined == {e["id"] for e in SPEC["claims"]
                           if e["expect"] in ("mismatch", "unreachable")}


def test_the_log_shows_collector_and_verifier_differ_on_every_record(store, regions, log) -> None:
    _seeded_run(store, regions, log)
    lines = log.path.read_text().splitlines()
    assert len(lines) == sum(e["expect"] != "skipped" for e in SPEC["claims"])
    for line in lines:
        record = Verification.model_validate_json(line)
        assert (record.collector.agent, record.collector.model_family) != (
            record.verifier.agent, record.verifier.model_family)
        assert record.method == record.verifier.method


def test_a_mismatch_records_a_structured_diff(store, regions, log) -> None:
    _seeded_run(store, regions, log)
    record = log.latest()[("evidence", "sol-max-filed-as-default")]
    assert record.outcome == "mismatch"
    assert json.loads(record.diff) == [
        {"field": "effort", "expected": "default", "found": "max"}]
    sibling = log.latest()[("evidence", "sol-copied-from-sibling")]
    diff = {d["field"]: d for d in json.loads(sibling.diff)}
    assert diff["model"] == {"field": "model", "expected": "GPT-6 Sol", "found": "GPT-6 Astra"}
    assert diff["value"]["expected"] == "58.3 percent"
    assert diff["value"]["found"] == "64.0 percent"


def test_mismatches_and_unreachables_are_requeued_for_recrawl(store, regions, log) -> None:
    _seeded_run(store, regions, log)
    recrawl = {t.id: outcome for t, outcome in verify.Queue(log.directory).recrawl_requests()}
    assert recrawl == {e["id"]: e["expect"] for e in SPEC["claims"]
                       if e["expect"] in ("mismatch", "unreachable")}


def test_a_second_run_has_nothing_left_to_do(store, regions, log) -> None:
    _seeded_run(store, regions, log)
    before = log.path.read_text()
    report = verify.run(verify.Queue(log.directory), log, regions,
                        verify.deterministic_extractors(), today=TODAY)
    # Only the skipped claim is still pending: it was never verified.
    assert [r.target.id for r in report.results] == ["sol-prose-no-extractor"]
    assert log.path.read_text() == before


# --- two keys ----------------------------------------------------------------------------------


class _FakeLLM:
    def __init__(self, reply: str, *, family: str = "claude") -> None:
        self.reply = reply
        self.calls: list[str] = []
        self.extractor = verify.LLMExtractor(
            self, agent="verify-llm", model="claude-sonnet-5", model_family=family)

    def __call__(self, prompt: str) -> str:
        self.calls.append(prompt)
        return self.reply


def _prose_claim(store, collector=COLLECTOR) -> verify.Claim:
    entry = next(e for e in SPEC["claims"] if e["id"] == "sol-prose-no-extractor")
    claim = _claim(entry, store)
    return verify.Claim(**{**claim.__dict__, "collector": collector})


def test_the_llm_extractor_verifies_prose_and_records_its_model(store, regions) -> None:
    llm = _FakeLLM(json.dumps([{"subject": "GPT-6 Sol", "value": "400,000", "unit": "tokens"}]))
    extractors = [*verify.deterministic_extractors(), llm.extractor]
    result = verify.verify(_prose_claim(store), regions, extractors, today=TODAY)
    assert result.outcome == "verified"
    assert result.verification.verifier == VerificationActor(
        agent="verify-llm", model_family="claude", method="llm-extract:claude-sonnet-5")
    assert "400,000 tokens of context" in llm.calls[0]


def test_deterministic_extractors_are_used_before_the_llm(store, regions) -> None:
    llm = _FakeLLM("[]")
    entry = next(e for e in SPEC["claims"] if e["id"] == "sol-default")
    result = verify.verify(_claim(entry, store), regions,
                           [llm.extractor, *verify.deterministic_extractors()], today=TODAY)
    assert result.outcome == "verified"
    assert result.verification.verifier.model_family == "deterministic"
    assert llm.calls == []


def test_an_unparseable_llm_reply_is_not_evidence_of_absence(store, regions) -> None:
    llm = _FakeLLM("I think it is about 400k?")
    result = verify.verify(_prose_claim(store), regions,
                           [*verify.deterministic_extractors(), llm.extractor], today=TODAY)
    assert result.outcome == "skipped"
    assert result.verification is None
    assert "extractor_error" in result.reason


def test_the_collector_never_verifies_its_own_value(store, regions) -> None:
    # The collector is the same agent and model family as the only extractor that accepts
    # prose: model validation refuses the pair, so nothing is verified.
    llm = _FakeLLM(json.dumps([{"subject": "GPT-6 Sol", "value": "400000", "unit": "tokens"}]),
                   family="grok")
    same = VerificationActor(agent="verify-llm", model_family="grok", method="anything")
    result = verify.verify(_prose_claim(store, same), regions,
                           [*verify.deterministic_extractors(), llm.extractor], today=TODAY)
    assert result.outcome == "skipped"
    assert result.reason == "no_independent_extractor"
    assert llm.calls == []


def test_same_agent_different_model_family_is_independent(store, regions) -> None:
    llm = _FakeLLM(json.dumps([{"subject": "GPT-6 Sol", "value": "400000", "unit": "tokens"}]))
    same_agent = VerificationActor(agent="verify-llm", model_family="grok", method="scrape")
    result = verify.verify(_prose_claim(store, same_agent), regions,
                           [*verify.deterministic_extractors(), llm.extractor], today=TODAY)
    assert result.outcome == "verified"


# --- comparison rules --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "hint", "number", "unit"),
    [
        ("71.2", "%", 71.2, "percent"),
        ("71.2%", None, 71.2, "percent"),
        ("400K tokens", None, 400, "k_tokens"),
        ("400,000 tokens", None, 400000, "tokens"),
        ("$2.50 / 1M tokens", None, 2.5, "usd_per_1m_tokens"),
        ("400K", "tokens", 400, "k_tokens"),
        ("n/a", None, None, None),
    ],
)
def test_quantities_parse_with_their_units(text, hint, number, unit) -> None:
    q = verify.parse_quantity(text, hint)
    if number is None:
        assert q is None
    else:
        assert (q.number, q.unit) == (number, unit)


@pytest.mark.parametrize(
    ("claimed", "unit", "found", "ok"),
    [
        (71.2, "percent", "71.2%", True),
        (71.24, "percent", "71.2%", True),   # the claim carries more digits than the source
        (71, "percent", "71.2%", True),      # the claim is the source rounded
        (71.3, "percent", "71.2%", False),
        (0.712, "fraction", "71.2%", True),
        (400000, "tokens", "400K tokens", True),
        (401000, "tokens", "400,000 tokens", False),
    ],
)
def test_the_rounding_tolerance(claimed, unit, found, ok) -> None:
    assert verify.numbers_agree(claimed, unit, verify.parse_quantity(found)) is ok


def test_the_tolerance_rule_is_recorded() -> None:
    assert "0.5" in verify.TOLERANCE_RULE


@pytest.mark.parametrize(
    ("cell", "name", "effort"),
    [
        ("GPT-6 Sol", "gpt 6 sol", None),
        ("GPT-6 Sol (max effort)", "gpt 6 sol", "max"),
        ("GPT-6 Sol [high]", "gpt 6 sol", "high"),
        ("GPT-6 Sol (thinking)", "gpt 6 sol thinking", None),
        ("GPT-6 Astra", "gpt 6 astra", None),
    ],
)
def test_model_cells_split_into_identity_and_effort(cell, name, effort) -> None:
    assert verify.split_model_cell(cell) == (name, effort)


# --- the log -----------------------------------------------------------------------------------


def _record(target_id: str, outcome: str, day: date) -> Verification:
    return Verification(
        target=VerificationTarget(kind="fact", id=target_id, value_hash=value_hash(1)),
        collector=COLLECTOR,
        verifier=VerificationActor(agent="v", model_family="deterministic", method="m"),
        method="m",
        outcome=outcome,
        date=day,
        diff='[{"field": "value"}]' if outcome == "mismatch" else None,
    )


def test_the_log_is_append_only_and_the_latest_outcome_wins(log) -> None:
    target = TargetRef(kind="fact", id="x")
    assert log.is_quarantined(target)  # never verified
    log.append(_record("x", "verified", date(2026, 9, 1)))
    assert not log.is_quarantined(target)
    log.append(_record("x", "mismatch", date(2026, 9, 1)))  # same day, later line
    assert log.is_quarantined(target)
    log.append(_record("x", "verified", date(2026, 9, 2)))
    assert not log.is_quarantined(target)
    log.append(_record("x", "unreachable", date(2026, 8, 30)))  # an older record, appended late
    assert not log.is_quarantined(target)
    assert len(log.path.read_text().splitlines()) == 4
    assert log.path.parent.name == "verification" and log.path.suffix == ".jsonl"


def test_quarantined_values_include_values_never_verified(log) -> None:
    log.append(_record("ok", "verified", TODAY))
    log.append(_record("bad", "mismatch", TODAY))
    never = TargetRef(kind="fact", id="never")
    ids = {t.id for t in log.quarantined_values([never, TargetRef(kind="fact", id="ok")])}
    assert ids == {"never"}
    assert {t.id for t in log.quarantined_values()} == {"bad"}


def test_module_level_quarantine_helpers_read_a_directory(log) -> None:
    log.append(_record("bad", "unreachable", TODAY))
    target = TargetRef(kind="fact", id="bad")
    assert verify.is_quarantined(target, directory=log.directory)
    [quarantined] = verify.quarantined_values(directory=log.directory)
    assert quarantined == VerificationTarget(
        kind="fact", id="bad", value_hash=value_hash(1)
    )


# --- triggers: change detection re-queues, --changed-only ---------------------------------------


def test_changed_regions_are_reverified_against_the_new_copy(store, regions, log) -> None:
    _seeded_run(store, regions, log)
    queue = verify.Queue(log.directory)
    # The leaderboard changed: Sol's default score is now 65.0.
    page = (FIXTURES / "leaderboard.html").read_text().replace(
        "<td>64.0</td>", "<td>65.0</td>")
    new_ref = store.put(page.encode())
    state = SourceState("seeded-leaderboard", SourceSnapshot(
        source_id="seeded-leaderboard",
        retrieved_at=NOW,
        page_fingerprint="sha256:" + "1" * 64,
        region_fingerprints={},
        copy_ref=new_ref,
    ))
    report = RecheckReport(requeue=["evidence:sol-default", "evidence:sol-max"],
                           states={"seeded-leaderboard": state})
    queue.requeue(report, at=NOW)
    later = date(2026, 9, 25)
    result = verify.run(queue, log, regions, verify.deterministic_extractors(), today=later,
                        changed_only=True)
    assert {r.target.id: r.outcome for r in result.results} == {
        "sol-default": "mismatch", "sol-max": "verified"}
    assert log.is_quarantined(TargetRef(kind="evidence", id="sol-default"))
    assert not log.is_quarantined(TargetRef(kind="evidence", id="sol-max"))


def test_changed_only_skips_new_values(store, regions, log) -> None:
    queue = verify.Queue(log.directory)
    entry = next(e for e in SPEC["claims"] if e["id"] == "sol-default")
    queue.file(_claim(entry, store), at=NOW)
    report = verify.run(queue, log, regions, verify.deterministic_extractors(), today=TODAY,
                        changed_only=True)
    assert report.results == []
    report = verify.run(queue, log, regions, verify.deterministic_extractors(), today=TODAY)
    assert [r.outcome for r in report.results] == ["verified"]


def test_a_requeued_ref_with_no_filed_claim_is_reported(log) -> None:
    queue = verify.Queue(log.directory)
    queue.requeue(RecheckReport(requeue=["fact:nobody-filed-this"]), at=NOW)
    report = verify.run(queue, log, verify.StoredRegions(CopyStore(log.directory / "c"), {}),
                        verify.deterministic_extractors(), today=TODAY)
    assert report.results == []
    assert report.unknown == [TargetRef(kind="fact", id="nobody-filed-this")]


def test_refs_parse_as_kind_and_id() -> None:
    assert verify.target_ref("fact:openai/gpt-6#context_window") == TargetRef(
        kind="fact", id="openai/gpt-6#context_window")
    with pytest.raises(ValueError):
        verify.target_ref("openai/gpt-6")


# --- the CLI -----------------------------------------------------------------------------------


def _repo(tmp_path, store) -> Path:
    root = tmp_path / "repo"
    (root / "registry").mkdir(parents=True)
    (root / "registry" / "sources.yaml").write_text((FIXTURES / "sources.yaml").read_text())
    queue = verify.Queue(root / "verification")
    for entry in SPEC["claims"]:
        queue.file(_claim(entry, store), at=NOW)
    return root


def test_cli_verifies_what_is_queued_and_prints_a_summary(tmp_path, store, monkeypatch) -> None:
    from cli.modelspec import cli as cli_mod

    monkeypatch.setenv("MODELSPEC_SOURCE_CACHE", str(store.root))
    root = _repo(tmp_path, store)
    result = CliRunner().invoke(cli_mod.app, ["verify", "--root", str(root)])
    assert result.exit_code == 0, result.output
    counts = {k: sum(e["expect"] == k for e in SPEC["claims"])
              for k in ("verified", "mismatch", "unreachable", "skipped")}
    for outcome, n in counts.items():
        assert f"{outcome}: {n}" in result.output
    assert "sol-max-filed-as-default" in result.output
    assert (root / "verification" / "log.jsonl").is_file()

    again = CliRunner().invoke(cli_mod.app, ["verify", "--root", str(root), "--changed-only",
                                             "--json"])
    assert again.exit_code == 0, again.output
    payload = json.loads(again.output)
    assert payload["changed_only"] is True
    assert payload["counts"] == {"verified": 0, "mismatch": 0, "unreachable": 0, "skipped": 0}


def test_claims_build_from_model_evidence(store, regions) -> None:
    from decision.model import Evidence

    ref = store.put((FIXTURES / "leaderboard.html").read_bytes())
    evidence = Evidence(
        id="sol-default-from-model", subject={"kind": "model", "id": "openai/gpt-6-sol"},
        benchmark_id="seeded-coding", model_id_as_evaluated="GPT-6 Sol", score=64.0,
        unit="percent", source_url="https://leaderboard.example.test/coding",
        source_kind="independent_evaluator", evidence_date="2026-08-14",
        date_type="evaluated", verified_at="2026-08-20", effort="default",
        sources=[{"source_id": "seeded-leaderboard", "snapshot_ref": ref,
                  "cited_regions": ["results"]}],
    )
    claim = verify.Claim.from_evidence(evidence, names=["GPT-6 Sol"], collector=COLLECTOR,
                                       label="Score")
    # The harness is not on the evidence, so the source's harness column is a mismatch:
    # the claim dropped a qualifier the source attaches to the value.
    result = verify.verify(claim, regions, verify.deterministic_extractors(), today=TODAY)
    assert [d.field for d in result.diffs] == ["harness"]
