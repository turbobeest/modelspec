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


def _value_of(verdict):
    """The synthetic value a fixture verdict was made for (its value hash names it)."""
    from decision.model import value_hash

    for value in (262144, 131072, 65536, 30, 45, 46.6, 51.2, None, ["lab/alpha"]):
        if value_hash(value) == verdict["target"]["value_hash"]:
            return value
    raise AssertionError("an unknown fixture value")


def events(verdict, *, method="read", sources=(), effort=None, harness=None, names=None,
           value=..., filed=None):
    """The verdict's queue trail: the claim it checked (filed the day before) and its check."""
    from datetime import timedelta

    target = {"kind": verdict["target"]["kind"], "id": verdict["target"]["id"]}
    day = date.fromisoformat(str(verdict["date"]))
    claim = {"target": target, "sources": list(sources), "names": list(names or [MID]),
             "value": _value_of(verdict) if value is ... else value, "field": FACET,
             "conditions": {"date": str(day), "effort": effort, "harness": harness},
             "collector": {"agent": "collector-a", "model_family": "family-a", "method": method}}
    return [{"event": "collected", "at": filed or f"{day - timedelta(days=1)}T09:00:00+00:00",
             "claim": claim},
            {"event": "checked", "at": f"{day}T21:00:00+00:00", "target": target,
             "outcome": verdict["outcome"]}]


def history_of(log, **kw):
    out = {}
    for verdict in log:
        if verdict["outcome"] != "verified":
            out.setdefault(verdict["target"]["id"], []).extend(events(verdict, **kw))
    return out


def plant(root, row, **kw):
    """A verdict in the log, and its trail in the queue."""
    path = root / "verification/log.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        fh.write(json.dumps(row) + "\n")
    queue = root / "verification/queue/events.jsonl"
    queue.parent.mkdir(parents=True, exist_ok=True)
    with queue.open("a") as fh:
        for event in events(row, **kw):
            fh.write(json.dumps(event) + "\n")
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
                               history=events(verdict), cutoff=datetime.now(UTC).date())
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


def board_verdict(board, outcome="mismatch", **kw):
    """A verdict on the reading's row in the log, and its claim and check in the queue."""
    row = verification("evidence", reading_gate.ROW_ID, outcome, day="2026-10-14", value=46.6)
    settings = dict(effort=reading_gate.READING["effort"], harness=reading_gate.READING["harness"],
                    names=[reading_gate.READING["model_id_as_evaluated"]])
    return plant(board.root, row, **{**settings, **kw})


@pytest.fixture
def board(tmp_path, monkeypatch):
    d = reading_gate.Data(tmp_path / "data", monkeypatch)
    d.row["id"] = reading_gate.ROW_ID
    d.write()
    return d


def test_a_fresh_agreement_clears_a_readings_held_mismatch(board):
    board_verdict(board)
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
    board_verdict(board)
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


def build(row, clearings, attempts, log=(VERDICT,), *, as_of=TODAY, models=None, history=None):
    from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot

    from tests.snapshot_records import SOURCES, model

    inputs = SnapshotInputs(models=models or [model(MID, facts=[row])],
                            sources={**SOURCES, "src-cite": CITE}, verifications=list(log),
                            cited_attempt_lines=[a if isinstance(a, str) else raw(a)
                                                 for a in attempts],
                            clearing_history=history_of(log) if history is None else history,
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
                            history=history_of([VERDICT]), cutoff=TODAY)
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


#: A board-reading claim's source: the board row's own registered source.
BOARD_SOURCE = [{"source_id": "src-cite"}]


def reading_build(row, log, clearings=(), attempts=(), history=None):
    from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot

    from tests.snapshot_records import SOURCES, model

    built = build_snapshot(SnapshotInputs(
        models=[model(MID)], evidence=[row], sources={**SOURCES, "src-cite": BOARD},
        verifications=list(log), cited_attempt_lines=[raw(a) for a in attempts],
        clearing_history=history_of(log, sources=BOARD_SOURCE) if history is None else history,
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
    # Another setting of the reading is another reading: this verdict does not hold it at all
    # (MODEL-552 follow-up), so it enters without a line, and the line is not its.
    other = copy.deepcopy(row)
    other["effort"] = "low"
    assert reading_build(other, [verdict])


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
    """The base must be the record's epoch when the verdict was made, from the claim it checked."""
    def case(base, history=None, extra=()):
        attempt = agreement(clearing_epoch(base, verdict_sha256(VERDICT)))
        return build(cleared_row(attempt, base=base), [clearing(attempt)], [*extra, attempt],
                     history=history)

    assert admitted(case("initial"))  # the claim the verdict checked was a plain collection
    assert not admitted(case("made-up"))
    assert not admitted(case("initial:reread:" + "b" * 64))
    # A re-read hash from an earlier agreement is not the record's epoch: its claim was plain.
    opened = {**agreement("initial", at="2026-09-01T09:00:00+00:00"), "text_sha256": "b" * 64,
              "page_sha256": "9" * 64}
    assert not admitted(case("reread:" + "b" * 64, extra=[opened]))
    # When the verdict checked a claim the rule-15 gate filed, the record was in that change's
    # re-read epoch, and "initial" is the fabrication.
    copy = [{"source_id": "src-cite", "snapshot_ref": "sha256:" + "9" * 64}]
    gate_claim = history_of([VERDICT], method="two-readers-cited-change@3", sources=copy)
    assert admitted(case("reread:" + "b" * 64, gate_claim, [opened]))
    assert not admitted(case("initial", gate_claim, [opened]))


def test_an_epoch_that_cannot_be_shown_clears_nothing():
    from decision.quarantine_clearing import verdict_epoch

    kw = dict(log=AttemptLog(), subject=MID, facet=FACET, first="initial")
    trail = events(VERDICT)
    assert verdict_epoch(VERDICT, history=trail, **kw) == "initial"
    assert verdict_epoch(VERDICT, history=trail[1:], **kw) is None  # no claim before the check
    assert verdict_epoch(VERDICT, history=trail[:1], **kw) is None  # no check of the verdict
    assert verdict_epoch(VERDICT, history=[], **kw) is None
    ruled = events(VERDICT, method="owner-ruling@1")
    assert verdict_epoch(VERDICT, history=ruled, **kw) is None
    gate = events(VERDICT, method="two-readers-cited-change@3")  # its copy is in no attempt
    assert verdict_epoch(VERDICT, history=gate, **kw) is None
    attempt = agreement()
    assert not admitted(build(cleared_row(attempt), [clearing(attempt)], [attempt], history={}))


def test_a_reading_claim_must_show_the_rows_settings():
    from decision.quarantine_clearing import reading_settings

    row = {"model_id_as_evaluated": "Orbit (max)", "effort": "max", "harness": None}
    same = reading_settings(row)
    assert same(events(VERDICT, effort="max", names=["Orbit (max)", "Orbit"])[0]["claim"])
    assert not same(events(VERDICT, effort="low", names=["Orbit (max)"])[0]["claim"])
    assert not same(events(VERDICT, effort="max", names=["Other"])[0]["claim"])


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
                            clearing_history=history_of([VERDICT]),
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
            clearing_history=history_of([verdict], sources=BOARD_SOURCE),
            benchmark_metadata={"bench_x": {"min_score": 0, "max_score": 100,
                                            "unit": "percent"}}),
            as_of=TODAY)).evidence(MID, "bench_x")

    assert all(e.value != 51.2 for e in built())  # the earlier id's claim was this reading

    decoy = board_rows(10.0, OLD_ID)  # a cited row under the held id, other settings
    decoy["effort"] = "low"
    assert all(e.value != 51.2 for e in built(decoy))
    unverified = evidence(MID, "bench_x", 12.0, eid=OLD_ID, outcome=None, effort="low")
    assert all(e.value != 51.2 for e in built(unverified))
    # Codex's repro: a verified sibling under the held id (another measurer, so it is not
    # superseded as a duplicate) does not take the verdict over either.
    real = evidence(MID, "bench_x", 101.0, eid=OLD_ID, effort="low", measured_by="lab")
    assert all(e.value != 51.2 for e in built(real, log=(verdict, real["verification"])))
    real_new = evidence(MID, "bench_x", 101.0, eid=f"{MID}#bench_x#real", effort="low",
                        measured_by="lab")
    assert all(e.value != 51.2 for e in built(real_new, log=(verdict, real_new["verification"])))


def test_a_cleared_row_whose_own_id_and_value_hold_the_verdict_is_admitted():
    """The verdict binds the row as it is now (same id, same score): a valid clearing admits it."""
    from decision.cited_change import reading_epoch
    from decision.model import evidence_verification_value

    row = board_rows(51.2, NEW_ID)
    row["sources"][0].update(snapshot_ref=f"sha256:{PAGE}", retrieved_at=AT)
    verdict = verification("evidence", NEW_ID, "mismatch", day="2026-10-01",
                           value=evidence_verification_value(row))
    settings = {"model_id_as_evaluated": MID, "effort": None, "harness": None}
    attempt = agreement(clearing_epoch(reading_epoch(settings), verdict_sha256(verdict)),
                        values=(51.2, 51.2), facet="benchmark:bench_x")
    attempt["url"] = BOARD
    row["derivation"] = cleared_row(attempt, base=reading_epoch(settings))["derivation"]
    assert reading_build(row, [verdict]) == ()
    assert reading_build(row, [verdict], [clearing(attempt, verdict)], [attempt])


def test_an_agreement_on_the_filed_value_clears_an_offering_quarantine(tmp_path, monkeypatch):
    from tests import test_cited_offering as offering

    d = offering.Data(tmp_path / "data", monkeypatch)
    d.fact(value=30, state="known")
    plant(d.root, verification("fact", offering.FACT_ID, "mismatch", day="2026-09-20", value=30))
    assert offering.retention().reason == "quarantined"
    out = offering.retention(clear_quarantine=True)
    assert out.changed and out.record["value"] == 30 and len(out.record["clearings"]) == 1


def test_an_agreement_on_the_filed_score_clears_a_board_row(board):
    board_verdict(board)
    out = cited_reading(subject=reading_gate.SUBJECT, benchmark_id=reading_gate.BENCH,
                        reading=reading_gate.READING, source_id="board",
                        readers=reading_gate.pair(46.6), request=reading_gate.serve(),
                        clear_quarantine=True)
    assert out.changed and out.record["value"] == 46.6 and len(out.record["clearings"]) == 1


# --- review round 3 (MODEL-552) -------------------------------------------------------------------


def test_only_the_claim_for_the_verdicts_value_supplies_the_epoch():
    """A claim for another value under the same id, even a later rule-15 one, never counts."""
    from decision.quarantine_clearing import verdict_epoch

    opened = {**agreement("initial", at="2026-09-01T09:00:00+00:00"), "text_sha256": "b" * 64,
              "page_sha256": "9" * 64}
    copy = [{"source_id": "src-cite", "snapshot_ref": "sha256:" + "9" * 64}]
    plain = events(VERDICT)  # the claim for the verdict's value, then its check
    other = events(VERDICT, method="two-readers-cited-change@3", sources=copy, value=1,
                   filed="2026-09-30T12:00:00+00:00")[0]  # another value, filed after it
    # The check names the verdict's value in its diff, so it is shown to cover the plain claim.
    check = {**plain[1], "diff": [{"field": "value", "expected": VALUE, "found": None}]}
    trail = [plain[0], other, check]
    kw = dict(log=AttemptLog([raw(opened)]), subject=MID, facet=FACET, first="initial")
    assert verdict_epoch(VERDICT, history=trail, **kw) == "initial"
    assert verdict_epoch(VERDICT, history=[other, check], **kw) is None  # only another value

    def case(base):
        attempt = agreement(clearing_epoch(base, verdict_sha256(VERDICT)))
        return build(cleared_row(attempt, base=base), [clearing(attempt)], [opened, attempt],
                     history={FID: trail})

    assert not admitted(case("reread:" + "b" * 64))
    assert admitted(case("initial"))


def test_an_opening_attempt_logged_after_the_claim_does_not_set_the_epoch():
    from decision.quarantine_clearing import verdict_epoch

    copy = [{"source_id": "src-cite", "snapshot_ref": "sha256:" + "9" * 64}]
    trail = events(VERDICT, method="two-readers-cited-change@3", sources=copy)  # filed 09-30 09:00

    def opened(at):
        return {**agreement("initial", at=at), "text_sha256": "b" * 64, "page_sha256": "9" * 64}

    def epoch(at):
        return verdict_epoch(VERDICT, history=trail, log=AttemptLog([raw(opened(at))]),
                             subject=MID, facet=FACET, first="initial")

    assert epoch("2026-09-30T09:00:00+00:00") == "reread:" + "b" * 64  # at the claim: counts
    assert epoch("2026-09-30T08:59:59+00:00") == "reread:" + "b" * 64
    assert epoch("2026-09-30T09:00:01+00:00") is None  # after the claim, before the check
    assert epoch("2026-10-02T09:00:00+00:00") is None  # after the verdict
    late = opened("2026-09-30T12:00:00+00:00")
    attempt = agreement(clearing_epoch("reread:" + "b" * 64, verdict_sha256(VERDICT)))
    index = build(cleared_row(attempt, base="reread:" + "b" * 64), [clearing(attempt)],
                  [late, attempt], history={FID: trail})
    assert not admitted(index)


# --- review round 4 (MODEL-552) -------------------------------------------------------------------


def test_a_check_after_a_newer_other_value_filing_does_not_pair_with_an_older_claim():
    """Codex round 4: a check that does not say which value it covered, after a newer filing for
    another value, is not shown to cover the older same-value claim, so it supplies nothing."""
    from decision.quarantine_clearing import verdict_epoch

    plain = events(VERDICT)
    other = events(VERDICT, value=1, filed="2026-09-30T12:00:00+00:00")[0]
    silent = plain[1]  # no value hash, no diff
    kw = dict(log=AttemptLog(), subject=MID, facet=FACET, first="initial")
    assert verdict_epoch(VERDICT, history=[plain[0], other, silent], **kw) is None
    attempt = agreement()
    index = build(cleared_row(attempt), [clearing(attempt)], [attempt],
                  history={FID: [plain[0], other, silent]})
    assert not admitted(index)
    assert verdict_epoch(VERDICT, history=[plain[0], silent], **kw) == "initial"  # adjacent


def test_a_check_is_bound_to_a_value_by_its_hash_or_its_diff():
    from decision.quarantine_clearing import check_binds, verdict_epoch

    plain = events(VERDICT)
    other = events(VERDICT, value=1, filed="2026-09-30T12:00:00+00:00")[0]
    silent = plain[1]
    kw = dict(log=AttemptLog(), subject=MID, facet=FACET, first="initial")
    assert check_binds(silent, VERDICT, FACET) is None
    names_other = {**silent, "diff": [{"field": "value", "expected": 1, "found": None}]}
    assert check_binds(names_other, VERDICT, FACET) is False
    assert verdict_epoch(VERDICT, history=[plain[0], other, names_other], **kw) is None
    names_ours = {**silent, "diff": [{"field": "value", "expected": VALUE, "found": None}]}
    assert check_binds(names_ours, VERDICT, FACET) is True
    assert verdict_epoch(VERDICT, history=[plain[0], other, names_ours], **kw) == "initial"
    hashed = {**silent, "target": {**silent["target"], "value_hash": "sha256:" + "0" * 64}}
    assert check_binds(hashed, VERDICT, FACET) is False
    own = {**silent, "target": {**silent["target"], "value_hash": VERDICT["target"]["value_hash"]}}
    assert check_binds(own, VERDICT, FACET) is True


# --- review round 5 (MODEL-552) -------------------------------------------------------------------


def test_an_older_same_day_check_is_no_fallback_for_the_newest_one():
    """Codex round 5: the newest matching check of the day follows a filing for another value
    and cannot be bound to the verdict; an earlier same-day check of the same-value claim is not
    used."""
    from decision.quarantine_clearing import verdict_epoch

    plain = events(VERDICT)  # claim 09-30 09:00, check 10-01 21:00
    early = {**plain[1], "at": "2026-10-01T08:00:00+00:00"}  # checks the same-value claim
    other = events(VERDICT, value=1, filed="2026-10-01T09:00:00+00:00")[0]
    late = plain[1]  # the newest check, after the other-value filing, says nothing
    kw = dict(log=AttemptLog(), subject=MID, facet=FACET, first="initial")
    assert verdict_epoch(VERDICT, history=[plain[0], early], **kw) == "initial"
    trail = [plain[0], early, other, late]
    assert verdict_epoch(VERDICT, history=trail, **kw) is None
    attempt = agreement()
    assert not admitted(build(cleared_row(attempt), [clearing(attempt)], [attempt],
                              history={FID: trail}))


def test_a_claim_retired_before_the_check_supplies_nothing():
    """MODEL-557 retires a claim whose data row is gone: a check after that did not cover it."""
    from decision.quarantine_clearing import verdict_epoch

    plain = events(VERDICT)
    retired = {"event": "retired", "at": "2026-10-01T08:00:00+00:00",
               "target": plain[0]["claim"]["target"], "reason": "no_data_row"}
    kw = dict(log=AttemptLog(), subject=MID, facet=FACET, first="initial")
    assert verdict_epoch(VERDICT, history=plain, **kw) == "initial"
    assert verdict_epoch(VERDICT, history=[plain[0], retired, plain[1]], **kw) is None


def test_queue_history_reads_retired_events_and_refuses_a_repeated_key(tmp_path):
    from decision.quarantine_clearing import queue_history

    path = tmp_path / "events.jsonl"
    rows = [*events(VERDICT), {"event": "retired", "at": "2026-10-02T08:00:00+00:00",
                               "target": {"kind": "fact", "id": FID}, "reason": "no_data_row"}]
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    assert [e["event"] for e in queue_history(path, {FID})[FID]] == ["collected", "checked",
                                                                     "retired"]
    path.write_text('{"event": "checked", "event": "collected", "at": "2026-10-01", '
                    f'"target": {{"kind": "fact", "id": "{FID}"}}}}\n')
    with pytest.raises(ValueError):
        queue_history(path, {FID})


# --- MODEL-552 follow-up: a verdict holds only its own reading ------------------------------------


def test_an_author_measured_row_is_not_held_by_the_providers_self_report_verdict():
    """Data#549 regression: a mismatch on a provider's self-reported row of a model and
    benchmark held the board author's own row of the same model and benchmark (another source and
    measurer). A verdict holds a row only through the row's own id, or an earlier id its queue
    claim shows was the same reading."""
    from decision.model import evidence_verification_value
    from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot

    from tests.snapshot_records import SOURCES, evidence, model

    self_id, board_id = f"{MID}#bench_x#selfreport01", f"{MID}#bench_x#boardrow0001"
    self_report = evidence(MID, "bench_x", 40.0, eid=self_id, outcome=None,
                           source="src-lab-docs", measured_by="provider_self_report")
    board = board_rows(51.2, board_id)
    board["measured_by"] = "benchmark_author"
    verdict = verification("evidence", self_id, "mismatch", day="2026-10-01",
                           value=evidence_verification_value(self_report))
    trail = {self_id: events(verdict, value=40.0, sources=[{"source_id": "src-lab-docs"}])}

    def shown(history):
        built = build_snapshot(SnapshotInputs(
            models=[model(MID)], evidence=[self_report, board],
            sources={**SOURCES, "src-cite": BOARD}, verifications=[verdict],
            clearing_history=history,
            benchmark_metadata={"bench_x": {"min_score": 0, "max_score": 100,
                                            "unit": "percent"}}),
            as_of=TODAY)
        return sorted(e.value for e in load_built_snapshot(built).evidence(MID, "bench_x"))

    assert shown(trail) == [51.2]  # the board's own row enters; the self-report stays out
    assert shown({}) == [51.2]  # with no trail at all, the verdict holds only its own row


def test_a_decoy_sibling_cannot_take_a_verdict():
    """A decoy row carrying the held earlier id (another setting) takes nothing over: the
    verdict's claim shows which reading it was on, and that reading stays held. The decoy itself
    is held by the verdict on its own id."""
    from decision.cited_change import held_rows
    from decision.model import evidence_verification_value
    from decision.quarantine_clearing import reading_holds
    from decision.snapshot import _Compiler

    filed = board_rows(46.6, OLD_ID)
    verdict = verification("evidence", OLD_ID, "mismatch", day="2026-10-01",
                           value=evidence_verification_value(filed))
    log = _Compiler._verification_log([verdict])
    history = history_of([verdict], sources=BOARD_SOURCE)
    row, decoy = board_rows(), board_rows(10.0, OLD_ID)
    decoy["effort"] = "low"
    prefix = f"{MID}#bench_x#"
    for target, own in ((row, NEW_ID), (decoy, OLD_ID)):
        candidates = held_rows(log, (own,), target, kind="evidence",
                               owns=lambda i: i.startswith(prefix))
        held = reading_holds(candidates, target, own_ids={own}, history=history)
        assert [key[1] for key, _ in held] == [OLD_ID], own
    other_reading = {**board_rows(), "effort": "low"}
    candidates = held_rows(log, (NEW_ID,), other_reading, kind="evidence",
                           owns=lambda i: i.startswith(prefix))
    assert reading_holds(candidates, other_reading, own_ids={NEW_ID}, history=history) == []
