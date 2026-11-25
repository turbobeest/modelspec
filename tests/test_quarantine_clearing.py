"""MODEL-552: a fresh two-reader agreement clears a mismatch quarantine, within Jamie's limits.

All pages, hashes, verdicts and attempts are synthetic and built here. No page text from any
cite-only host is used.
"""

from __future__ import annotations

import copy
import json
import socket
from datetime import UTC, date, datetime

import pytest
import yaml
from decision.cited_change import REFUSALS, cited_change, cited_reading
from decision.cited_reader import ATTEMPTS_FILE
from decision.quarantine_clearing import (
    CLEARINGS_FILE,
    FIELDS,
    AttemptLog,
    clearing_epoch,
    fact_cleared,
    line,
    line_hash,
    line_problem,
    verdict_sha256,
)

from tests import test_cited_change as fact_gate
from tests import test_cited_reading as reading_gate
from tests.snapshot_records import verification


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", lambda *a: pytest.fail("Network attempted"))


# --- the gate, for a card fact -------------------------------------------------------------------

FACT_ID = f"{fact_gate.SUBJECT}#{fact_gate.FACET}"


@pytest.fixture
def data(tmp_path, monkeypatch):
    return fact_gate.Data(tmp_path / "data", monkeypatch)


def plant(root, row):
    path = root / "verification/log.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        fh.write(json.dumps(row) + "\n")
    return row


def held_mismatch(data, day="2026-09-20", value=131072, outcome="mismatch"):
    return plant(data.root, verification("fact", FACT_ID, outcome, day=day, value=value))


def seed(data, **entry):
    path = data.root / ATTEMPTS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        fh.write(json.dumps({"subject": fact_gate.SUBJECT, "facet": fact_gate.FACET,
                             "url": fact_gate.URL, **entry}) + "\n")


def run(**kw):
    args = dict(subject=fact_gate.SUBJECT, facet=fact_gate.FACET, source_id="s1",
                readers=fact_gate.pair(), request=fact_gate.serve(), clear_quarantine=True)
    args.update(kw)
    return cited_change(**args)


def refused(reason, **kw):
    out = run(**kw)
    assert out.outcome == "refused" and out.reason == reason, (out.reason, out.detail)
    assert out.record is None and reason in REFUSALS
    return out


def test_a_fresh_agreement_clears_the_one_held_mismatch_and_names_both(data):
    verdict = held_mismatch(data)
    out = run()
    assert out.changed and out.record["value"] == 262144
    [entry] = out.record["clearings"]
    assert set(entry) == set(FIELDS)
    logged = data.log()
    epoch = clearing_epoch("initial", verdict_sha256(verdict))
    assert [a["epoch"] for a in logged] == [epoch]  # read in the verdict's clearing epoch
    raw = (data.root / ATTEMPTS_FILE).read_text().splitlines()[-1]
    assert entry["epoch"] == epoch and entry["agreement"] == line_hash(raw)
    block = out.record["derivation"]["cited_change"]
    assert block["previous_epoch"] == "initial" and block["clearing_epoch"] == epoch
    assert entry["target"] == verdict["target"]
    assert entry["verdict_sha256"] == verdict_sha256(verdict)
    assert entry["verdict_date"] == "2026-09-20" and entry["value"] == 262144
    assert "SECRET-PAGE-MARKER" not in json.dumps(out.record)
    ok, attempt = line_problem(entry, verdict=verdict, subject=fact_gate.SUBJECT,
                               facet=fact_gate.FACET, ids=lambda rid: rid == FACT_ID,
                               log=AttemptLog.read(data.root / ATTEMPTS_FILE), first="initial",
                               cutoff=datetime.now(UTC).date())
    assert ok == "" and attempt == logged[-1]


def test_without_the_flag_a_quarantined_fact_is_still_refused_up_front(data):
    held_mismatch(data)
    refused("quarantined", clear_quarantine=False)
    assert not data.log()


def test_a_same_day_verdict_is_not_cleared(data):
    held_mismatch(data, day=datetime.now(UTC).date().isoformat())
    refused("clearing_not_later")
    assert not data.log()  # refused before any read


def test_an_unreachable_verdict_stays_blocked(data):
    held_mismatch(data, outcome="unreachable")
    out = refused("quarantined")
    assert "unreachable" in out.detail and not data.log()


def test_two_held_verdicts_stay_blocked(data):
    held_mismatch(data)
    held_mismatch(data, value=65536)
    refused("quarantined")
    assert not data.log()


def test_same_family_readers_are_refused_by_the_gate(data):
    held_mismatch(data)
    refused("reader_families_not_distinct", readers=fact_gate.pair(b=("codex-2", "gpt-5")))
    assert not data.log()


def test_a_disagreement_in_the_clearing_epoch_blocks(data):
    verdict = held_mismatch(data)
    seed(data, epoch=clearing_epoch("initial", verdict_sha256(verdict)), complete=True,
         agreed=False, harness=True)
    refused("prior_attempt_disagreed")


def test_a_disagreement_in_the_facts_own_epoch_blocks(data):
    held_mismatch(data)
    seed(data, epoch="initial", complete=True, agreed=False, harness=True)
    refused("prior_attempt_disagreed")


def test_an_answer_in_an_incomplete_attempt_that_differs_blocks(data):
    verdict = held_mismatch(data)
    seed(data, epoch=clearing_epoch("initial", verdict_sha256(verdict)), complete=False,
         readers=[{"reader_id": "codex", "family": "gpt-5", "version": "1", "value": 1}])
    refused("prior_attempt_disagreed")


def test_an_owner_ruled_fact_is_not_cleared_by_the_gate(data):
    held_mismatch(data)
    data.fact["derivation"] = {"owner_ruling": {"subject": fact_gate.SUBJECT}}
    data.write()
    out = refused("quarantined")
    assert "ruling" in out.detail and not data.log()


def test_a_cleared_offering_fact_writes_its_clearing_line(tmp_path, monkeypatch):
    """``scripts.cited_offering.apply`` appends the gate's line after the claim."""
    from scripts import cited_offering

    from tests import test_cited_offering as offering

    d = offering.Data(tmp_path / "data", monkeypatch)
    verdict = plant(d.root, verification("fact", offering.FACT_ID, "mismatch", day="2026-09-20",
                                         value=45))
    out = offering.retention(clear_quarantine=True)
    assert out.changed, (out.reason, out.detail)
    cited_offering.apply(out, data_dir=d.root)
    [written] = [json.loads(x) for x in (d.root / CLEARINGS_FILE).read_text().splitlines()]
    assert written == out.record["clearings"][0]
    assert written["verdict_sha256"] == verdict_sha256(verdict)
    text = d.offering_path.read_text()
    assert "clearings" not in text and "verdict_sha256" not in text  # the fact keeps no line
    assert offering.retention().reason == "quarantined"  # the log still holds it for the gate


# --- the gate, for a board reading ---------------------------------------------------------------


@pytest.fixture
def board(tmp_path, monkeypatch):
    d = reading_gate.Data(tmp_path / "data", monkeypatch)
    d.row["id"] = reading_gate.ROW_ID
    d.write()
    return d


def test_a_fresh_agreement_clears_a_readings_held_mismatch(board):
    reading_gate.plant(board, reading_gate.ROW_ID)
    out = cited_reading(subject=reading_gate.SUBJECT, benchmark_id=reading_gate.BENCH,
                        reading=reading_gate.READING, source_id="board",
                        readers=reading_gate.pair(), request=reading_gate.serve(),
                        clear_quarantine=True)
    assert out.changed and out.record["value"] == 51.2
    [entry] = out.record["clearings"]
    assert entry["target"]["kind"] == "evidence" and entry["target"]["id"] == reading_gate.ROW_ID
    assert entry["facet"] == f"benchmark:{reading_gate.BENCH}"
    assert board.log()[-1]["epoch"] == entry["epoch"] and ":clear:" in entry["epoch"]


def test_a_reading_is_still_refused_without_the_flag_and_for_an_absence(board):
    reading_gate.plant(board, reading_gate.ROW_ID)
    reading_gate.quarantined(board)
    out = cited_reading(subject=reading_gate.SUBJECT, benchmark_id=reading_gate.BENCH,
                        reading=reading_gate.READING, source_id="board",
                        readers=reading_gate.pair(value=None), request=reading_gate.serve(),
                        clear_quarantine=True)
    assert out.reason == "no_value"


def test_a_readings_unreachable_verdict_stays_blocked(board):
    reading_gate.plant(board, reading_gate.ROW_ID, "unreachable")
    out = cited_reading(subject=reading_gate.SUBJECT, benchmark_id=reading_gate.BENCH,
                        reading=reading_gate.READING, source_id="board",
                        readers=reading_gate.pair(), request=reading_gate.serve(),
                        clear_quarantine=True)
    assert out.reason == "quarantined" and not board.log()


# --- the build: the cleared value enters only through its line ------------------------------------

CITE = "https://www.perplexity.ai/pro"
MID, FACET = "lab/alpha", "model.context_window"
FID = f"{MID}#{FACET}"
PAGE, TEXT, PROMPT = "3" * 64, "a" * 64, "4" * 64
AT = "2026-10-10T09:00:00+00:00"
VALUE = 262144
TODAY = date(2026, 10, 19)


def mismatch(fid=FID, value=VALUE, day="2026-10-01"):
    return verification("fact", fid, "mismatch", day=day, value=value)


VERDICT = mismatch()
EPOCH = clearing_epoch("initial", verdict_sha256(VERDICT))


def agreement(epoch=EPOCH, *, at=AT, values=(VALUE, VALUE), families=("openai", "anthropic"),
              subject=MID, facet=FACET):
    return {"subject": subject, "facet": facet, "epoch": epoch, "url": CITE, "complete": True,
            "agreed": values[0] == values[1], "agreed_value": values[0], "harness": True,
            "page_sha256": PAGE, "text_sha256": TEXT, "prompt_sha256": PROMPT, "at": at,
            "readers": [{"reader_id": "a", "family": families[0], "version": "1",
                         "value": values[0]},
                        {"reader_id": "b", "family": families[1], "version": "1",
                         "value": values[1]}]}


def raw(attempt):
    """The attempt's line as the gate's ``log_attempt`` writes it."""
    return json.dumps(attempt, sort_keys=True, ensure_ascii=False)


def cleared_row(attempt, *, value=VALUE, subject=MID, base="initial"):
    from tests.snapshot_records import fact

    row = fact("model", subject, FACET, value, source="src-cite", outcome=None)
    row["sources"] = [{"source_id": "src-cite", "snapshot_ref": f"sha256:{attempt['page_sha256']}",
                       "retrieved_at": attempt["at"], "cited_regions": ["page"]}]
    row["derivation"] = {"cited_change": {
        "rule": "two-readers-cited-change@3", "sha256": attempt["page_sha256"],
        "text_sha256": attempt["text_sha256"], "url": attempt["url"],
        "readers": [{**r, "prompt_sha256": attempt["prompt_sha256"]} for r in attempt["readers"]],
        "previous_epoch": base, "clearing_epoch": attempt["epoch"]}}
    return row


def clearing(attempt, verdict=VERDICT, **kw):
    target = verdict["target"]
    entry = line(key=(target["kind"], target["id"], target["value_hash"]), verdict=verdict,
                 subject=attempt["subject"], facet=attempt["facet"], epoch=attempt["epoch"],
                 attempt_line=raw(attempt), value=attempt["agreed_value"],
                 at=datetime(2026, 10, 10, 10, tzinfo=UTC))
    entry.update(kw)
    return entry


def build(row, clearings, attempts, log=(VERDICT,), *, as_of=TODAY, models=None):
    from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot

    from tests.snapshot_records import SOURCES, model

    inputs = SnapshotInputs(models=models or [model(MID, facts=[row])],
                            sources={**SOURCES, "src-cite": CITE}, verifications=list(log),
                            cited_attempt_lines=[a if isinstance(a, str) else raw(a)
                                                 for a in attempts],
                            quarantine_clearings=list(clearings))
    return load_built_snapshot(build_snapshot(inputs, as_of=as_of))


def admitted(index, mid=MID):
    shown = index.fact(mid, FACET)
    return shown.state == "known" and shown.value == VALUE


def test_the_build_admits_a_cleared_fact_as_an_ordinary_cited_fact():
    attempt = agreement()
    index = build(cleared_row(attempt), [clearing(attempt)], [attempt])
    assert admitted(index)
    record = index.record(index.fact(MID, FACET).record_id)
    assert record["verification"] is None and record["citation"]["status"] == "cited"
    served = json.dumps(record)
    assert "verdict_sha256" not in served and "clearing" not in served


def test_the_build_keeps_a_cleared_value_out_without_its_line():
    attempt = agreement()
    assert not admitted(build(cleared_row(attempt), [], [attempt]))


def test_an_agreement_in_the_same_epoch_as_the_verdict_clears_nothing():
    """The Sonnet case: an agreement in the fact's own epoch, not the verdict's clearing epoch."""
    attempt = agreement("initial")
    assert not admitted(build(cleared_row(attempt), [clearing(attempt)], [attempt]))


def test_an_agreement_on_the_verdicts_day_or_earlier_clears_nothing():
    for at in ("2026-10-01T23:00:00+00:00", "2026-09-30T09:00:00+00:00"):
        attempt = agreement(at=at)
        entry = clearing(attempt, cleared_at=at)
        assert not admitted(build(cleared_row(attempt), [entry], [attempt]))


def test_same_family_readers_clear_nothing_in_the_build():
    attempt = agreement(families=("openai", "openai"))
    assert not admitted(build(cleared_row(attempt), [clearing(attempt)], [attempt]))


def test_a_disagreement_in_the_clearing_epoch_undoes_the_clearing():
    attempt = agreement()
    split = agreement(values=(VALUE, 1), at="2026-10-11T09:00:00+00:00")
    assert not admitted(build(cleared_row(attempt), [clearing(attempt)], [attempt, split]))
    in_base = agreement("initial", values=(VALUE, 1))
    assert not admitted(build(cleared_row(attempt), [clearing(attempt)], [attempt, in_base]))
    incomplete = {**agreement(), "complete": False, "agreed": None,
                  "readers": [{"reader_id": "a", "family": "openai", "version": "1", "value": 7}]}
    assert not admitted(build(cleared_row(attempt), [clearing(attempt)], [attempt, incomplete]))


@pytest.mark.parametrize("forge", [
    "extra_field", "missing_field", "other_rule", "other_verdict_hash", "other_verdict_day",
    "unknown_agreement", "other_value", "other_epoch", "other_target_hash", "cleared_later",
    "edited_attempt",
])
def test_a_forged_clearing_line_admits_nothing(forge):
    attempt = agreement()
    entry = clearing(attempt)
    attempts = [attempt]
    if forge == "extra_field":
        entry["note"] = "x"
    elif forge == "missing_field":
        del entry["cleared_at"]
    elif forge == "other_rule":
        entry["rule"] = "quarantine-clearing@2"
    elif forge == "other_verdict_hash":
        entry["verdict_sha256"] = "sha256:" + "0" * 64
    elif forge == "other_verdict_day":
        entry["verdict_date"] = "2026-09-01"
    elif forge == "unknown_agreement":
        entry["agreement"] = "sha256:" + "1" * 64
    elif forge == "other_value":
        entry["value"] = 1
    elif forge == "other_epoch":
        entry["epoch"] = clearing_epoch("initial", "sha256:" + "2" * 64)
    elif forge == "other_target_hash":
        entry["target"] = {**entry["target"], "value_hash": "sha256:" + "5" * 64}
    elif forge == "cleared_later":
        entry["cleared_at"] = "2026-10-25T09:00:00+00:00"  # after the build's day
    elif forge == "edited_attempt":
        attempts = [{**attempt, "page_sha256": "6" * 64}]  # the named attempt is gone
    assert not admitted(build(cleared_row(attempt), [entry], attempts))


def test_a_fact_whose_block_another_agreement_made_is_not_cleared():
    attempt = agreement()
    other = agreement(at="2026-10-11T09:00:00+00:00")
    other["page_sha256"] = "7" * 64
    assert not admitted(build(cleared_row(other), [clearing(attempt)], [attempt, other]))


def test_a_clearing_for_subject_a_does_not_clear_subject_b():
    from tests.snapshot_records import model

    beta = "lab/beta"
    verdict_b = mismatch(f"{beta}#{FACET}")
    attempt = agreement()  # lab/alpha's agreement and line
    row_b = cleared_row(attempt, subject=beta)
    models = [model(MID), model(beta, facts=[row_b])]
    index = build(row_b, [clearing(attempt)], [attempt], log=(VERDICT, verdict_b), models=models)
    assert not admitted(index, beta)
    # A line that names B's verdict but A's agreement is no clearing of B either.
    forged = clearing(attempt, verdict_b)
    index = build(row_b, [forged], [attempt], log=(VERDICT, verdict_b), models=models)
    assert not admitted(index, beta)


def test_a_newer_verdict_after_the_clearing_holds_again():
    attempt = agreement()
    newer = mismatch(day="2026-10-15")
    assert not admitted(build(cleared_row(attempt), [clearing(attempt)], [attempt],
                              log=(VERDICT, newer)))


def test_a_cleared_value_that_is_not_the_mismatched_one_still_needs_its_line():
    """The gate holds every value of a fact; so does the build, for a gate-written fact."""
    verdict = mismatch(value=131072)
    attempt = agreement(clearing_epoch("initial", verdict_sha256(verdict)))
    row = cleared_row(attempt)
    assert not admitted(build(row, [], [attempt], log=(verdict,)))
    assert admitted(build(row, [clearing(attempt, verdict)], [attempt], log=(verdict,)))


def test_an_unreachable_verdict_is_not_cleared_by_the_build():
    verdict = verification("fact", FID, "unreachable", day="2026-10-01", value=VALUE)
    attempt = agreement(clearing_epoch("initial", verdict_sha256(verdict)))
    entry = clearing(attempt, verdict)
    assert not admitted(build(cleared_row(attempt), [entry], [attempt], log=(verdict,)))


def test_a_ruled_fact_is_not_admitted_through_a_clearing_line():
    attempt = agreement()
    row = cleared_row(attempt)
    row["derivation"]["owner_ruling"] = {"subject": MID, "facet": FACET}
    assert not fact_cleared(row, MID, verdict=VERDICT, clearings=[clearing(attempt)],
                            log=AttemptLog([raw(attempt)]), sources={"src-cite": CITE},
                            cutoff=TODAY)
    assert not admitted(build(row, [clearing(attempt)], [attempt]))


def test_a_ruling_still_cannot_lift_a_quarantine_even_beside_a_clearing():
    """``owner_ruling.admits`` refuses a held verdict whether or not a clearing line exists."""
    from decision import owner_ruling
    from decision.snapshot import _Compiler

    ranked = _Compiler._verification_log([VERDICT])
    ruled = cleared_row(agreement())
    ruled["derivation"] = {"owner_ruling": {"subject": MID}}
    assert not owner_ruling.admits(ruled, MID, rulings=[], attempts=[], sources={},
                                   verdicts=ranked)
    from decision.cited_change import held_verdicts

    assert held_verdicts(ranked, [FID], ruled)  # the ruling path's own test still holds it


# --- the build, for a board reading ---------------------------------------------------------------

BOARD = "https://www.perplexity.ai/pro"
OLD_ID, NEW_ID = f"{MID}#bench_x#old", f"{MID}#bench_x#new"


def board_rows(score=51.2, eid=NEW_ID):
    from tests.snapshot_records import evidence

    return evidence(MID, "bench_x", score, eid=eid, outcome=None, source="src-cite",
                    source_url=BOARD)


def reading_build(row, log, clearings=(), attempts=()):
    from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot

    from tests.snapshot_records import SOURCES, model

    built = build_snapshot(SnapshotInputs(
        models=[model(MID)], evidence=[row], sources={**SOURCES, "src-cite": BOARD},
        verifications=list(log), cited_attempt_lines=[raw(a) for a in attempts],
        quarantine_clearings=list(clearings),
        benchmark_metadata={"bench_x": {"min_score": 0, "max_score": 100, "unit": "percent"}}),
        as_of=TODAY)
    return load_built_snapshot(built).evidence(MID, "bench_x")


def test_a_cleared_reading_enters_only_through_its_line():
    from decision.cited_change import reading_epoch
    from decision.model import evidence_verification_value

    filed = board_rows(46.6, OLD_ID)
    verdict = verification("evidence", OLD_ID, "mismatch", day="2026-10-01",
                           value=evidence_verification_value(filed))
    settings = {"model_id_as_evaluated": MID, "effort": None, "harness": None}
    epoch = clearing_epoch(reading_epoch(settings), verdict_sha256(verdict))
    attempt = agreement(epoch, values=(51.2, 51.2), facet="benchmark:bench_x")
    attempt["url"] = BOARD
    row = board_rows()
    row["sources"][0].update(snapshot_ref=f"sha256:{PAGE}", retrieved_at=AT)
    row["derivation"] = cleared_row(attempt, base=reading_epoch(settings))["derivation"]
    assert reading_build(row, [verdict]) == ()
    entry = clearing(attempt, verdict)
    assert reading_build(row, [verdict], [entry], [attempt])
    # The same line does not clear another setting of the reading.
    other = copy.deepcopy(row)
    other["effort"] = "low"
    assert reading_build(other, [verdict], [entry], [attempt]) == ()


def test_the_clearing_file_is_read_by_collect_repo(tmp_path):
    from decision.snapshot import SnapshotBuildError, collect_repo

    root = tmp_path / "data"
    for d in ("models", "registry", "verification", "benchmarks"):
        (root / d).mkdir(parents=True)
    (root / "registry/sources.yaml").write_text(yaml.safe_dump({"schema_version": 1,
                                                               "sources": []}))
    attempt = agreement()
    (root / ATTEMPTS_FILE).write_text(raw(attempt) + "\n")
    (root / CLEARINGS_FILE).write_text(json.dumps(clearing(attempt)) + "\n")
    inputs = collect_repo(root)
    assert len(inputs.quarantine_clearings) == 1 and inputs.cited_attempt_lines == [raw(attempt)]
    (root / CLEARINGS_FILE).write_text('{"rule": 1, "rule": 2}\n')
    with pytest.raises(SnapshotBuildError):
        collect_repo(root)


# --- review round 1 (MODEL-552) -------------------------------------------------------------------


def test_a_replay_with_recomputed_hashes_needs_the_exact_logged_line():
    attempt = agreement()
    row = cleared_row(attempt)
    respelled = json.dumps(attempt)  # the same fields, another spelling
    entry = clearing(attempt, agreement=line_hash(respelled))
    assert not admitted(build(row, [entry], [attempt]))  # the log holds the gate's spelling
    assert not admitted(build(row, [clearing(attempt)], [respelled]))  # and here the reverse
    forged = agreement(at="2026-10-12T09:00:00+00:00")  # never logged, hashes recomputed
    assert not admitted(build(cleared_row(forged), [clearing(forged)], [attempt]))
    assert admitted(build(row, [clearing(attempt)], [attempt]))  # byte-identical: admitted


def test_a_fabricated_base_epoch_is_refused():
    def case(base, extra=()):
        attempt = agreement(clearing_epoch(base, verdict_sha256(VERDICT)))
        return build(cleared_row(attempt, base=base), [clearing(attempt)], [*extra, attempt])

    assert not admitted(case("made-up"))
    assert not admitted(case("initial:reread:" + "b" * 64))
    assert not admitted(case("reread:" + "b" * 64))  # no cited change the gate made opened it
    opened = {**agreement("initial", at="2026-09-01T09:00:00+00:00"), "text_sha256": "b" * 64}
    assert admitted(case("reread:" + "b" * 64, [opened]))
    later = {**opened, "at": "2026-10-11T09:00:00+00:00"}  # opened only after the agreement
    assert not admitted(case("reread:" + "b" * 64, [later]))


def test_a_reading_base_epoch_must_be_its_own_settings():
    from decision.cited_change import reading_epoch
    from decision.quarantine_clearing import base_problem

    first = reading_epoch({"model_id_as_evaluated": "x", "effort": None, "harness": None})
    log = AttemptLog()
    at = datetime(2026, 10, 10, tzinfo=UTC)
    kw = dict(first=first, subject=MID, facet="benchmark:b", log=log, before=at)
    assert base_problem(first, **kw) is None
    assert base_problem(first + ":anything", **kw)
    assert base_problem("reading:0000000000000000", **kw)
    assert base_problem(first + ":reread:" + "c" * 64, **kw)  # no opening change logged


def test_stripping_the_cited_change_block_does_not_skip_the_hold():
    verdict = mismatch(value=131072)
    attempt = agreement(clearing_epoch("initial", verdict_sha256(verdict)))
    stripped = cleared_row(attempt)
    del stripped["derivation"]
    assert not admitted(build(stripped, [clearing(attempt, verdict)], [attempt], log=(verdict,)))
    assert not admitted(build(stripped, [], [], log=(verdict,)))
    # A value the log itself verifies is the verifier's, not a replacement: it is admitted.
    verified = verification("fact", FID, "verified", day="2026-10-02", value=VALUE)
    assert admitted(build(stripped, [], [], log=(verdict, verified)))


def test_a_ref_that_is_not_the_agreements_registered_source_clears_nothing():
    from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot

    from tests.snapshot_records import SOURCES, model

    attempt = agreement()
    row = cleared_row(attempt)
    row["sources"][0]["source_id"] = "src-other"  # the same copy hash under another page
    inputs = SnapshotInputs(models=[model(MID, facts=[row])],
                            sources={**SOURCES, "src-cite": CITE,
                                     "src-other": "https://www.perplexity.ai/enterprise"},
                            verifications=[VERDICT], cited_attempt_lines=[raw(attempt)],
                            quarantine_clearings=[clearing(attempt)])
    assert not admitted(load_built_snapshot(build_snapshot(inputs, as_of=TODAY)))


def test_a_cleared_fact_is_served_exactly_as_a_plain_cited_fact():
    from decision.owner_ruling import served_fact

    attempt = agreement()
    row = cleared_row(attempt)
    index = build(row, [clearing(attempt)], [attempt])
    plain = {k: v for k, v in row.items() if k != "derivation"}
    plain_index = build(plain, [], [], log=())
    record = index.record(index.fact(MID, FACET).record_id)
    assert record == plain_index.record(plain_index.fact(MID, FACET).record_id)
    assert served_fact(row) == plain  # the site's served form too


def test_a_decoy_sibling_does_not_divert_a_readings_verdict():
    from decision.model import evidence_verification_value

    from tests.snapshot_records import evidence

    filed = board_rows(46.6, OLD_ID)
    verdict = verification("evidence", OLD_ID, "mismatch", day="2026-10-01",
                           value=evidence_verification_value(filed))
    row = board_rows()

    def built(*others, log=(verdict,)):
        from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot

        from tests.snapshot_records import SOURCES, model

        return load_built_snapshot(build_snapshot(SnapshotInputs(
            models=[model(MID)], evidence=[row, *others],
            sources={**SOURCES, "src-cite": BOARD}, verifications=list(log),
            benchmark_metadata={"bench_x": {"min_score": 0, "max_score": 100,
                                            "unit": "percent"}}),
            as_of=TODAY)).evidence(MID, "bench_x")

    decoy = board_rows(10.0, OLD_ID)  # a cited row under the held id, other settings
    decoy["effort"] = "low"
    assert all(e.value != 51.2 for e in built(decoy))
    unverified = evidence(MID, "bench_x", 12.0, eid=OLD_ID, outcome=None, effort="low")
    assert all(e.value != 51.2 for e in built(unverified))
    # A real sibling, admitted under its own verified id, keeps its own verdicts.
    # (another measurer, so the verified row does not supersede the cited one as a duplicate)
    real = evidence(MID, "bench_x", 12.0, eid=OLD_ID, effort="low", measured_by="lab")
    assert any(e.value == 51.2 for e in built(real, log=(verdict, real["verification"])))


def test_an_agreement_on_the_filed_value_clears_an_offering_quarantine(tmp_path, monkeypatch):
    from tests import test_cited_offering as offering

    d = offering.Data(tmp_path / "data", monkeypatch)
    d.fact(value=30, state="known")
    plant(d.root, verification("fact", offering.FACT_ID, "mismatch", day="2026-09-20", value=30))
    assert offering.retention().reason == "quarantined"
    out = offering.retention(clear_quarantine=True)
    assert out.changed and out.record["value"] == 30 and len(out.record["clearings"]) == 1


def test_an_agreement_on_the_filed_score_clears_a_board_row(board):
    reading_gate.plant(board, reading_gate.ROW_ID)
    out = cited_reading(subject=reading_gate.SUBJECT, benchmark_id=reading_gate.BENCH,
                        reading=reading_gate.READING, source_id="board",
                        readers=reading_gate.pair(46.6), request=reading_gate.serve(),
                        clear_quarantine=True)
    assert out.changed and out.record["value"] == 46.6 and len(out.record["clearings"]) == 1
