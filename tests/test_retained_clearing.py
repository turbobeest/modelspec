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
              url=URL, kind="confirmation"):
    """A confirmation read as the gate logs it now, its kind in the line; ``kind=None`` is an
    older, untagged line."""
    line = {"subject": MID, "facet": FACET, "epoch": epoch, "url": url, "complete": True,
            "agreed": values[0] == values[1], "agreed_value": values[0], "harness": True,
            "page_sha256": PAGE, "text_sha256": TEXT, "prompt_sha256": PROMPT, "at": at,
            "readers": [{"reader_id": "a", "family": families[0], "version": "1",
                         "value": values[0]},
                        {"reader_id": "b", "family": families[1], "version": "1",
                         "value": values[1]}]}
    if kind is not None:
        line["kind"] = kind
    return line


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


# --- E4: a clearing from the epoch a confirmation moved the record into ---------------------------

T0 = "b" * 64  # the text hash the confirmation read; it names the record's re-read epoch
MOVED = f"reread:{T0}"
MOVED_EPOCH = clearing_epoch(MOVED, verdict_sha256(VERDICT))


def own_agreement(**kw):
    """The confirmation's own agreement: in the first epoch, on a later day than the verdict."""
    values = kw.pop("values", (VALUE, VALUE))
    text = kw.pop("text_sha256", T0)
    attempt = agreement("initial", at=kw.pop("at", "2026-10-05T09:00:00+00:00"), values=values,
                        **{k: kw.pop(k) for k in ("families", "url", "kind") if k in kw})
    attempt.update(text_sha256=text, **kw)
    return attempt


def build_moved(row, clearings, attempts, log=(VERDICT,), *, extra=(), as_of=TODAY):
    from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot

    from tests.snapshot_records import SOURCES, model

    hist = history(log)
    hist.setdefault(FID, []).extend(extra)
    inputs = SnapshotInputs(models=[model(MID, facts=[row])], sources=dict(SOURCES),
                            verifications=list(log),
                            cited_attempt_lines=[raw(a) for a in attempts],
                            clearing_history=hist, quarantine_clearings=list(clearings))
    return load_built_snapshot(build_snapshot(inputs, as_of=as_of))


def test_a_clearing_extends_the_epoch_a_confirmation_moved_the_record_into():
    own, fresh = own_agreement(), agreement(MOVED_EPOCH)
    row = confirmed_row(fresh, base=MOVED)
    assert admitted(build_moved(row, [clearing(fresh)], [own, fresh]))
    # The same clearing without the confirmation's own agreement: no move is shown.
    assert not admitted(build_moved(row, [clearing(fresh)], [fresh]))


@pytest.mark.parametrize("bypass", [
    "changed_value", "claim_changed", "earlier", "same_family", "cite_only", "incomplete",
    "disagreed", "forged_text", "forged_epoch", "record_value"])
def test_a_move_that_is_not_shown_clears_nothing(bypass):
    own, fresh, extra, row = own_agreement(), agreement(MOVED_EPOCH), [], None
    lines = None
    if bypass == "changed_value":  # the confirmation agreed on another value
        own = own_agreement(values=(131072, 131072))
    elif bypass == "claim_changed":  # a claim for another value was filed in between
        extra = [{"event": "collected", "at": "2026-10-03T09:00:00+00:00", "claim": {
            "target": {"kind": "fact", "id": FID}, "value": 131072, "field": FACET,
            "names": [MID], "sources": [], "conditions": {},
            "collector": {"agent": "a", "model_family": "family-a", "method": "read"}}}]
    elif bypass == "earlier":  # the confirmation is not on a later day than the verdict
        own = own_agreement(at="2026-10-01T23:00:00+00:00")
    elif bypass == "same_family":
        own = own_agreement(families=("openai", "openai"))
    elif bypass == "cite_only":
        own = own_agreement(url="https://www.perplexity.ai/pro")
    elif bypass == "incomplete":
        own = own_agreement(complete=False)
    elif bypass == "disagreed":  # a disagreement in the first epoch
        lines = [own, own_agreement(values=(VALUE, 131072), at="2026-10-04T09:00:00+00:00"),
                 fresh]
    elif bypass == "forged_text":  # the epoch names a text no confirmation read
        own = own_agreement(text_sha256="c" * 64)
    elif bypass == "forged_epoch":  # not a re-read epoch at all
        base = "initial:board:" + T0
        fresh = agreement(clearing_epoch(base, verdict_sha256(VERDICT)))
        row = confirmed_row(fresh, base=base)
    elif bypass == "record_value":  # the record's value is not the one the verdict held
        fresh = agreement(MOVED_EPOCH, values=(131072, 131072))
        row = confirmed_row(fresh, base=MOVED, value=131072)
    row = row or confirmed_row(fresh, base=MOVED)
    lines = lines or [own, fresh]
    index = build_moved(row, [clearing(fresh)], lines, extra=extra)
    shown = index.fact(MID, FACET)
    assert not (shown.state == "known" and shown.value == row["value"])


def test_a_claim_on_the_verdicts_own_day_is_the_epoch_tests_not_the_moves():
    # The first collection filed other values on the verdict's day; verdict_epoch (E3) decides
    # that day. Only a claim after it, up to the confirmation, can show the value changed.
    own, fresh = own_agreement(), agreement(MOVED_EPOCH)
    row = confirmed_row(fresh, base=MOVED)
    same_day = [{"event": "collected", "at": "2026-10-01T03:00:00+00:00", "claim": {
        "target": {"kind": "fact", "id": FID}, "value": None, "field": FACET, "names": [MID],
        "sources": [], "conditions": {},
        "collector": {"agent": "a", "model_family": "family-a", "method": "read"}}}]
    from decision.quarantine_clearing import confirmation_move

    kw = dict(verdict=VERDICT, value=VALUE, log=AttemptLog([raw(own)]), subject=MID, facet=FACET,
              now=datetime(2026, 10, 19, tzinfo=UTC))
    assert confirmation_move(MOVED, "initial", history=same_day, **kw)
    assert admitted(build_moved(row, [clearing(fresh)], [own, fresh]))


def test_the_move_is_one_shared_test():
    from decision.quarantine_clearing import confirmation_move

    own = own_agreement()
    log = AttemptLog([raw(own)])
    kw = dict(verdict=VERDICT, value=VALUE, log=log, subject=MID, facet=FACET,
              history=history([VERDICT])[FID], now=datetime(2026, 10, 19, tzinfo=UTC))
    assert confirmation_move(MOVED, "initial", **kw)
    assert not confirmation_move(MOVED, "reread:" + "d" * 64, **kw)  # not from the first epoch
    assert not confirmation_move("reread:" + "c" * 64, "initial", **kw)
    assert not confirmation_move(MOVED, "initial", **{**kw, "value": 131072})


def test_the_gate_clears_a_confirmation_from_the_epoch_it_moved_the_record_into(data):
    from decision.cited_change import fact_epoch
    from decision.snapshot import build_snapshot, collect_repo, load_built_snapshot
    from pipeline.load import load_models

    first = gate.run()  # the rule-16 confirmation, before any hold
    assert first.changed, (first.reason, first.detail)
    fact = filed_fact(data.fact, first.record)
    data.fact.clear()
    data.fact.update(fact)
    data.write()
    moved = fact_epoch(data.fact)
    assert moved.startswith("reread:")
    verdict = _hold(data)  # a mismatch made before it, on the same value
    out = gate.run(clear_quarantine=True)
    assert out.changed, (out.reason, out.detail)
    block = out.record["derivation"]["cited_change"]
    assert block["previous_epoch"] == moved
    assert block["clearing_epoch"] == clearing_epoch(moved, verdict_sha256(verdict))
    [entry] = out.record["clearings"]
    filed = filed_fact(data.fact, out.record)
    data.fact.clear()
    data.fact.update(filed)
    data.write()
    (data.root / CLEARINGS_FILE).write_text(json.dumps(entry, sort_keys=True) + "\n")
    (data.root / "benchmarks").mkdir(exist_ok=True)
    shown = load_built_snapshot(build_snapshot(collect_repo(data.root))).fact(
        gate.SUBJECT, gate.FACET)
    assert shown.state == "known" and sorted(shown.value) == sorted(gate.FILED)
    (card,) = load_models(data.root)
    assert [f["facet"] for f in card.cited_facts] == [gate.FACET]


# --- E4 review: four bypasses -------------------------------------------------------------------

def test_review_1_a_forged_block_cannot_borrow_an_unrelated_agreement(data):
    # The gate binds the record's block to the logged confirmation line itself (readers, page,
    # text, prompt, cited copy and source), never to the block's own rule label or text hash.
    first = gate.run()
    assert first.changed, (first.reason, first.detail)
    fact = filed_fact(data.fact, first.record)
    fact["derivation"]["cited_change"]["text_sha256"] = "e" * 64  # point at another line
    data.fact.clear()
    data.fact.update(fact)
    data.write()
    unrelated = {"subject": gate.SUBJECT, "facet": gate.FACET, "epoch": "initial",
                 "url": gate.URL, "complete": True, "agreed": True,
                 "agreed_value": list(gate.FILED), "harness": True, "page_sha256": "f" * 64,
                 "text_sha256": "e" * 64, "prompt_sha256": "1" * 64,
                 "at": datetime.now(UTC).replace(microsecond=0).isoformat(),
                 "readers": [{"reader_id": "x", "family": "openai", "version": "9",
                              "value": list(gate.FILED)},
                             {"reader_id": "y", "family": "anthropic", "version": "9",
                              "value": list(gate.FILED)}]}
    path = data.root / "verification/cited-attempts.jsonl"
    with path.open("a") as fh:
        fh.write(json.dumps(unrelated, sort_keys=True) + "\n")
    _hold(data)
    out = gate.run(clear_quarantine=True)
    assert out.outcome == "refused" and out.reason == "epoch_not_current", out.reason


@pytest.mark.parametrize("order", ["line_after", "time_after"])
def test_review_2_the_confirmation_must_be_logged_before_the_clearing_read(order):
    fresh = agreement(MOVED_EPOCH)
    row = confirmed_row(fresh, base=MOVED)
    if order == "line_after":  # logged on a later line than the clearing's agreement
        lines = [fresh, own_agreement()]
    else:  # an earlier line, but stamped after the clearing read
        lines = [own_agreement(at="2026-10-11T09:00:00+00:00"), fresh]
    assert not admitted(build_moved(row, [clearing(fresh)], lines))


@pytest.mark.parametrize("claims", ["between", "reverted"])
def test_review_3_the_value_holds_from_the_mismatch_through_the_clearing(claims):
    own, fresh = own_agreement(), agreement(MOVED_EPOCH)
    row = confirmed_row(fresh, base=MOVED)

    def filed(at, value):
        return {"event": "collected", "at": at, "claim": {
            "target": {"kind": "fact", "id": FID}, "value": value, "field": FACET,
            "names": [MID], "sources": [], "conditions": {},
            "collector": {"agent": "a", "model_family": "family-a", "method": "read"}}}

    # After the confirmation (2026-10-05) and before the clearing read (2026-10-10).
    extra = [filed("2026-10-07T09:00:00+00:00", 131072)]
    if claims == "reverted":
        extra.append(filed("2026-10-08T09:00:00+00:00", VALUE))
    assert not admitted(build_moved(row, [clearing(fresh)], [own, fresh], extra=extra))
    assert admitted(build_moved(row, [clearing(fresh)], [own, fresh]))


def test_review_4_with_no_hold_an_unrelated_clearing_line_backs_nothing():
    from decision.snapshot import _Compiler

    attempt = agreement()
    row = confirmed_row(attempt)
    other = mismatch(value=131072, day="2026-09-30")
    unrelated = clearing(agreement(clearing_epoch("initial", verdict_sha256(other)),
                                   values=(131072, 131072)), verdict=other)
    for log, clears in (((), [unrelated]), ((), [clearing(attempt)]),
                        ((other,), [unrelated])):
        verdicts = _Compiler._verification_log(list(log))
        assert confirmation_problem(row, MID, log=AttemptLog([raw(attempt)]), verdicts=verdicts,
                                    sources={"src-lab-docs": URL}, cutoff=TODAY,
                                    clearings=clears, history=history(list(log))) is not None
        assert not admitted(build(row, clears, [attempt], log))
    # Its own line, naming the verdict the log holds, still backs it.
    assert admitted(build(row, [clearing(attempt)], [attempt]))


# --- E4 review round 2: the line, not the record's label, says what it made -----------------------

@pytest.mark.parametrize("line", ["relabelled_correction", "own_fetch_unshown"])
def test_review_5_a_correction_relabelled_as_a_confirmation_moves_nothing(line):
    # A correction's agreement line (it logged the value it replaced, agreed on another, on the
    # gate's own fetch) is never a confirmation, whatever rule label the record carries.
    from decision.quarantine_clearing import line_kind

    if line == "relabelled_correction":
        own = own_agreement(filed_value=131072, own_fetch=True, region_sha256="5" * 64,
                            kind="correction")
        assert line_kind(own, FACET) == "correction"
    else:  # an older own-fetch line, untagged, with nothing to show it was admitted
        own = own_agreement(own_fetch=True, region_sha256="5" * 64, kind=None)
        assert line_kind(own, FACET) is None
    fresh = agreement(MOVED_EPOCH)
    row = confirmed_row(fresh, base=MOVED)
    assert not admitted(build_moved(row, [clearing(fresh)], [own, fresh]))
    # An own-fetch line that logged the filed value and agreed on it, with no kind, is ambiguous:
    # a correction's same-value re-read writes the same values (round 3). Only the kind the gate
    # wrote into the line makes it a confirmation.
    own = own_agreement(filed_value=VALUE, own_fetch=True, region_sha256="5" * 64, kind=None)
    assert line_kind(own, FACET) is None
    assert not admitted(build_moved(row, [clearing(fresh)], [own, fresh]))
    own = own_agreement(filed_value=VALUE, own_fetch=True, region_sha256="5" * 64,
                        kind="confirmation")
    assert line_kind(own, FACET) == "confirmation"
    assert admitted(build_moved(row, [clearing(fresh)], [own, fresh]))
    own = own_agreement(filed_value=VALUE, own_fetch=True, region_sha256="5" * 64,
                        kind="correction")  # the same values, written as a correction
    assert not admitted(build_moved(row, [clearing(fresh)], [own, fresh]))


def test_review_5_a_relabelled_correction_is_not_served_as_a_confirmation():
    from decision.quarantine_clearing import line_kind

    attempt = {**agreement("initial", values=(VALUE, VALUE), kind="correction"),
               "filed_value": 131072, "own_fetch": True, "region_sha256": "5" * 64}
    assert line_kind(attempt, FACET) == "correction"
    row = confirmed_row(attempt, cleared=False)  # labelled a rule-16 confirmation
    assert confirmation_problem(row, MID, log=AttemptLog([raw(attempt)]), verdicts={},
                                sources={"src-lab-docs": URL}, cutoff=TODAY) is not None
    assert not admitted(build(row, [], [attempt], log=()))


# --- E4 review round 4: an untagged line refuses unless the full positive test holds -------------

def _claim(at, *, value=VALUE, rule="two-readers-retained-agreement@1", copy=PAGE):
    return {"event": "collected", "at": at, "claim": {
        "target": {"kind": "fact", "id": FID}, "value": value, "field": FACET, "names": [MID],
        "sources": [{"source_id": "src-lab-docs", "snapshot_ref": f"sha256:{copy}"}],
        "conditions": {}, "collector": {"agent": "cited-change-gate",
                                        "model_family": "deterministic", "method": rule}}}


@pytest.mark.parametrize("case", ["admitted", "filed_same", "refused", "filed_differs"])
def test_untagged_lines_serve_nothing_whatever_the_queue_shows(case):
    # MODEL-491 follow-up: an older line's claim cannot be tied to its attempt, so no claim, value
    # or filed value makes an untagged line a kind. Only the kind the gate wrote into it does.
    from decision.quarantine_clearing import line_kind

    line = own_agreement(kind=None)
    if case == "filed_same":
        line["filed_value"] = VALUE
    elif case == "filed_differs":
        line["filed_value"] = 131072
    assert line_kind(line, FACET) is None
    assert line_kind({**line, "kind": "confirmation"}, FACET) == "confirmation"


def test_an_untagged_confirmation_is_not_served_even_with_an_admitting_claim():
    from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot

    from tests.snapshot_records import SOURCES, model

    def served(line, events):
        row = confirmed_row(line, cleared=False)
        inputs = SnapshotInputs(models=[model(MID, facts=[row])], sources=dict(SOURCES),
                                verifications=[], cited_attempt_lines=[raw(line)],
                                clearing_history={FID: events})
        return admitted(load_built_snapshot(build_snapshot(inputs, as_of=TODAY)))

    claim = [_claim("2026-10-10T08:59:58+00:00")]
    assert not served(agreement("initial", kind=None), claim)
    assert not served(agreement("initial", kind=None), [])
    assert served(agreement("initial"), [])  # the gate-tagged line is served


# --- E4 review round 5 ---------------------------------------------------------------------------

def test_review_7_an_untagged_line_moves_nothing_even_with_an_admitting_claim():
    # An untagged read's claim cannot be tied to its attempt, so a refused read could borrow
    # another's claim for the same value and copy. No untagged line authorizes a move.
    fresh = agreement(MOVED_EPOCH)
    row = confirmed_row(fresh, base=MOVED)
    claim = _claim("2026-10-05T08:59:58+00:00")
    untagged = own_agreement(kind=None)
    assert not admitted(build_moved(row, [clearing(fresh)], [untagged, fresh], extra=[claim]))
    assert admitted(build_moved(row, [clearing(fresh)], [own_agreement(), fresh]))


@pytest.mark.parametrize("epoch,moves", [("initial", False), ("def2", True)])
def test_review_8_the_confirmation_is_read_in_the_definition_in_force_on_its_day(epoch, moves):
    # model.context_window's def2 is in force from 2026-11-27. A confirmation read that day must
    # be in def2: an ``initial`` line logged then moves nothing (the E6 day rule). The build's
    # cutoff is never after today, so the reads are dated on that first def2 day.
    own = own_agreement(at="2026-11-27T00:10:00+00:00")
    own["epoch"] = epoch
    fresh = agreement(MOVED_EPOCH, at="2026-11-27T00:20:00+00:00")
    row = confirmed_row(fresh, base=MOVED)
    entry = clearing(fresh)
    entry["cleared_at"] = "2026-11-27T00:30:00+00:00"
    index = build_moved(row, [entry], [own, fresh], as_of=date(2026, 11, 27))
    assert admitted(index) is moves
