"""MODEL-491 E4: a MODEL-552 clearing may release a non-cited rule-16 confirmation.

A confirmation (``two-readers-retained-agreement@1``) on a page whose host retains copies is held
by a mismatch on its value. A fresh two-reader agreement on the filed value, read in that
verdict's clearing epoch on a later day, with its clearing line, releases it; the build and the
site loader serve it as cited through ``retained_correction.confirmation_problem`` with the line
counted, and the gate asks the same test of the record it files. Bypass tests in the MODEL-552
style. Every page, hash, verdict and attempt is synthetic.
"""

from __future__ import annotations

import copy
import json
import socket
from datetime import UTC, date, datetime, timedelta

import pytest
from decision.cited_change import RETAINED_RULE
from decision.quarantine_clearing import (
    CLEARINGS_FILE,
    AttemptLog,
    clearing_epoch,
    line,
    verdict_sha256,
)
from decision.retained_correction import RULE, confirmation_problem, filed_fact

from tests import test_retained_agreement as gate
from tests.snapshot_records import verification


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", lambda *a: pytest.fail("Network attempted"))


# --- the build and the site loader ----------------------------------------------------------------

MID, FACET = "lab/alpha", "model.context_window"
FID = f"{MID}#{FACET}"
URL = "https://lab.example.com/docs/models"  # src-lab-docs: a host that retains copies
PAGE, TEXT, PROMPT = "3" * 64, "a" * 64, "4" * 64
AT = "2026-10-10T09:00:00+00:00"
VALUE = 262144
TODAY = date(2026, 10, 19)


def mismatch(value=VALUE, day="2026-10-01", outcome="mismatch"):
    return verification("fact", FID, outcome, day=day, value=value)


VERDICT = mismatch()
EPOCH = clearing_epoch("initial", verdict_sha256(VERDICT))


def agreement(epoch=EPOCH, *, at=AT, values=(VALUE, VALUE), families=("openai", "anthropic"),
              url=URL):
    return {"subject": MID, "facet": FACET, "epoch": epoch, "url": url, "complete": True,
            "agreed": values[0] == values[1], "agreed_value": values[0], "harness": True,
            "page_sha256": PAGE, "text_sha256": TEXT, "prompt_sha256": PROMPT, "at": at,
            "readers": [{"reader_id": "a", "family": families[0], "version": "1",
                         "value": values[0]},
                        {"reader_id": "b", "family": families[1], "version": "1",
                         "value": values[1]}]}


def raw(attempt):
    return json.dumps(attempt, sort_keys=True, ensure_ascii=False)


def confirmed_row(attempt, *, value=VALUE, rule=RETAINED_RULE, base="initial", cleared=True):
    from tests.snapshot_records import fact

    row = fact("model", MID, FACET, value, source="src-lab-docs", outcome=None)
    row["sources"] = [{"source_id": "src-lab-docs",
                       "snapshot_ref": f"sha256:{attempt['page_sha256']}",
                       "retrieved_at": attempt["at"], "cited_regions": ["page"]}]
    block = {"rule": rule, "sha256": attempt["page_sha256"], "text_sha256": attempt["text_sha256"],
             "url": attempt["url"], "previous_value": value,
             "readers": [{**r, "prompt_sha256": attempt["prompt_sha256"]}
                         for r in attempt["readers"]]}
    if cleared:
        block.update(previous_epoch=base, clearing_epoch=attempt["epoch"])
    row["derivation"] = {"cited_change": block}
    return row


def clearing(attempt, verdict=VERDICT, **kw):
    target = verdict["target"]
    entry = line(key=(target["kind"], target["id"], target["value_hash"]), verdict=verdict,
                 subject=MID, facet=FACET, epoch=attempt["epoch"], attempt_line=raw(attempt),
                 value=attempt["agreed_value"], at=datetime(2026, 10, 10, 10, tzinfo=UTC))
    entry.update(kw)
    return entry


def events(verdict, value=VALUE):
    target = {"kind": "fact", "id": verdict["target"]["id"]}
    day = date.fromisoformat(str(verdict["date"]))
    claim = {"target": target, "sources": [], "names": [MID], "value": value, "field": FACET,
             "conditions": {"date": str(day), "effort": None, "harness": None},
             "collector": {"agent": "collector-a", "model_family": "family-a", "method": "read"}}
    return [{"event": "collected", "at": f"{day - timedelta(days=1)}T09:00:00+00:00",
             "claim": claim},
            {"event": "checked", "at": f"{day}T21:00:00+00:00", "target": target,
             "outcome": verdict["outcome"]}]


def history(log):
    out = {}
    for verdict in log:
        if verdict["outcome"] != "verified":
            out.setdefault(verdict["target"]["id"], []).extend(events(verdict))
    return out


def build(row, clearings, attempts, log=(VERDICT,), *, as_of=TODAY):
    from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot

    from tests.snapshot_records import SOURCES, model

    inputs = SnapshotInputs(models=[model(MID, facts=[row])], sources=dict(SOURCES),
                            verifications=list(log),
                            cited_attempt_lines=[raw(a) for a in attempts],
                            clearing_history=history(log),
                            quarantine_clearings=list(clearings))
    return load_built_snapshot(build_snapshot(inputs, as_of=as_of))


def admitted(index):
    shown = index.fact(MID, FACET)
    return shown.state == "known" and shown.value == VALUE


def test_a_cleared_confirmation_is_served_as_cited():
    attempt = agreement()
    index = build(confirmed_row(attempt), [clearing(attempt)], [attempt])
    assert admitted(index)
    record = index.record(index.fact(MID, FACET).record_id)
    assert record["verification"] is None and record["citation"]["status"] == "cited"


def test_without_the_clearing_a_held_confirmation_stays_out():
    attempt = agreement()
    assert not admitted(build(confirmed_row(attempt), [], [attempt]))
    plain = agreement("initial")  # an agreement in the verdict's own epoch, no clearing
    assert not admitted(build(confirmed_row(plain, cleared=False), [], [plain]))


@pytest.mark.parametrize("bypass", [
    "same_epoch", "verdict_day", "same_family", "disagreed", "two_held", "unreachable",
    "other_verdict", "other_value", "cite_only", "correction", "licence", "ruled", "no_queue",
    "no_block_epoch", "after_cutoff"])
def test_a_clearing_that_fails_releases_nothing(bypass):
    attempt, log, lines, as_of = agreement(), [VERDICT], None, TODAY
    row = None
    clears = None
    if bypass == "same_epoch":  # read in the verdict's own epoch, not its clearing epoch
        attempt = agreement("initial")
    elif bypass == "verdict_day":
        attempt = agreement(at="2026-10-01T23:00:00+00:00")
    elif bypass == "same_family":
        attempt = agreement(families=("openai", "openai"))
    elif bypass == "disagreed":
        lines = [agreement(values=(VALUE, 131072), at="2026-10-09T09:00:00+00:00"), attempt]
    elif bypass == "two_held":  # a clearing clears one verdict
        log = [VERDICT, mismatch(value=131072, day="2026-10-02")]
    elif bypass == "unreachable":
        log = [mismatch(outcome="unreachable")]
    elif bypass == "other_verdict":
        clears = [clearing(attempt, verdict=mismatch(day="2026-09-30"))]
    elif bypass == "other_value":  # the agreement is on another value than the filed one
        attempt = agreement(values=(131072, 131072))
        row = confirmed_row(attempt)
    elif bypass == "cite_only":  # a cite-only page takes rule 15, not this path
        attempt = agreement(url="https://www.perplexity.ai/pro")
    elif bypass == "correction":  # a correction is never cleared
        row = confirmed_row(attempt, rule=RULE)
    elif bypass == "no_block_epoch":  # the block does not name its clearing epoch
        row = confirmed_row(attempt, cleared=False)
    elif bypass == "after_cutoff":
        as_of = date(2026, 10, 9)
    row = row or confirmed_row(attempt)
    if bypass == "licence":
        row["facet"] = "licence.user_cap"
    elif bypass == "ruled":
        row["derivation"]["owner_ruling"] = {"rule": "owner-ruling@1"}
    clears = clears if clears is not None else [clearing(attempt)]
    lines = lines or [attempt]
    hist = {} if bypass == "no_queue" else history(log)
    verdicts = __import__("decision.snapshot", fromlist=["_Compiler"])._Compiler \
        ._verification_log(log)
    assert confirmation_problem(row, MID, log=AttemptLog([raw(a) for a in lines]),
                                verdicts=verdicts, sources={"src-lab-docs": URL},
                                cutoff=as_of, clearings=clears, history=hist) is not None
    if bypass in {"licence", "no_queue"}:
        return  # the build's own inputs carry the queue; a licence row is checked above
    assert not admitted(build(row, clears, lines, log, as_of=as_of))


def test_the_site_loader_takes_the_builds_decision():
    from pipeline.load import _confirmed_citation

    attempt = agreement()
    row = confirmed_row(attempt)
    verdicts = __import__("decision.snapshot", fromlist=["_Compiler"])._Compiler \
        ._verification_log([VERDICT])
    inputs = (AttemptLog([raw(attempt)]), verdicts, TODAY)
    sources = {"src-lab-docs": URL}
    assert _confirmed_citation(row, MID, inputs, sources, TODAY,
                               ([clearing(attempt)], history([VERDICT]))) is not None
    assert _confirmed_citation(row, MID, inputs, sources, TODAY, ([], {})) is None
    assert _confirmed_citation(row, MID, inputs, sources, TODAY) is None


# --- the gate -------------------------------------------------------------------------------------

GATE_ID = f"{gate.SUBJECT}#{gate.FACET}"


@pytest.fixture
def data(tmp_path, monkeypatch):
    return gate.Data(tmp_path / "data", monkeypatch)


def _hold(data, *, value=None, day="2026-09-20", outcome="mismatch"):
    verdict = verification("fact", GATE_ID, outcome, day=day,
                           value=list(gate.FILED) if value is None else value)
    data.log_rows = [verdict]
    data.write()
    target = {"kind": "fact", "id": GATE_ID}
    claim = {"target": target, "sources": [], "names": [gate.SUBJECT],
             "value": list(gate.FILED) if value is None else value, "field": gate.FACET,
             "conditions": {"date": day, "effort": None, "harness": None},
             "collector": {"agent": "collector-a", "model_family": "family-a", "method": "read"}}
    queue = data.root / "verification/queue/events.jsonl"
    queue.parent.mkdir(parents=True, exist_ok=True)
    before = (date.fromisoformat(day) - timedelta(days=1)).isoformat()
    queue.write_text(
        json.dumps({"event": "collected", "at": f"{before}T09:00:00+00:00", "claim": claim})
        + "\n" + json.dumps({"event": "checked", "at": f"{day}T21:00:00+00:00",
                             "target": target, "outcome": outcome}) + "\n")
    return verdict


def test_the_gate_clears_a_held_confirmation_and_the_build_serves_it(data):
    from decision.snapshot import build_snapshot, collect_repo, load_built_snapshot
    from pipeline.load import load_models

    verdict = _hold(data)
    out = gate.run(clear_quarantine=True)
    assert out.changed, (out.reason, out.detail)
    block = out.record["derivation"]["cited_change"]
    epoch = clearing_epoch("initial", verdict_sha256(verdict))
    assert block["rule"] == RETAINED_RULE and block["clearing_epoch"] == epoch
    assert block["previous_epoch"] == "initial"
    [entry] = out.record["clearings"]
    assert entry["verdict_sha256"] == verdict_sha256(verdict)
    assert data.attempts()[-1]["epoch"] == epoch
    # File the record and its line as a writer does; the build and the site serve it as cited.
    fact = filed_fact(data.fact, out.record)
    data.fact.clear()
    data.fact.update(fact)
    data.write()
    (data.root / CLEARINGS_FILE).write_text(json.dumps(entry, sort_keys=True) + "\n")
    (data.root / "benchmarks").mkdir(exist_ok=True)
    index = load_built_snapshot(build_snapshot(collect_repo(data.root)))
    shown = index.fact(gate.SUBJECT, gate.FACET)
    assert shown.state == "known" and sorted(shown.value) == sorted(gate.FILED)
    assert index.record(shown.record_id)["citation"]["status"] == "cited"
    (card,) = load_models(data.root)
    assert [f["facet"] for f in card.cited_facts] == [gate.FACET]
    # Without its clearing line, the same card is held again on both.
    (data.root / CLEARINGS_FILE).write_text("")
    index = load_built_snapshot(build_snapshot(collect_repo(data.root)))
    assert index.fact(gate.SUBJECT, gate.FACET).state != "known"
    (card,) = load_models(data.root)
    assert card.cited_facts == []


def test_the_gate_clears_no_correction_and_no_other_value(data):
    _hold(data)
    # With ``correct`` no clearing is made: E2 reads past a mismatch on the filed value, and a
    # confirmation of that value is refused after the read; no clearing line is ever written.
    out = gate.run(clear_quarantine=True, correct=True)
    assert out.outcome == "refused" and out.reason == "quarantined" and out.record is None


def test_a_clearing_on_a_retaining_page_confirms_the_filed_value_only(data):
    _hold(data)
    out = gate.run(clear_quarantine=True, readers=gate.pair(["text"]))
    assert out.outcome == "refused" and out.reason == "value_differs"


def test_without_the_flag_a_held_confirmation_is_still_refused(data):
    _hold(data)
    request = gate.serve()
    out = gate.run(request=request)
    assert out.outcome == "refused" and out.reason == "quarantined" and request.calls == []


def test_an_unreachable_or_same_day_verdict_is_not_cleared_on_a_retaining_page(data):
    _hold(data, outcome="unreachable")
    out = gate.run(clear_quarantine=True)
    assert out.outcome == "refused" and out.reason == "quarantined"
    today = datetime.now(UTC).date().isoformat()
    _hold(data, day=today)
    out = gate.run(clear_quarantine=True)
    assert out.outcome == "refused" and out.reason in {"clearing_not_later", "quarantined"}


def test_a_forged_cleared_block_admits_nothing():
    attempt = agreement()
    row = confirmed_row(attempt)
    forged = copy.deepcopy(row)
    forged["derivation"]["cited_change"]["readers"][1]["family"] = "google"
    assert not admitted(build(forged, [clearing(attempt)], [attempt]))
    assert admitted(build(row, [clearing(attempt)], [attempt]))
