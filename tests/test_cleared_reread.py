"""MODEL-566: a quarantine-cleared fact can be re-read by two readers in the epochs after its
clearing.

A verdict a valid clearing line released (MODEL-552) no longer holds the fact once it is past the
clearing epoch: the gate reads a changed page in the epoch the cleared block names, and the build
admits the block a later agreement made there. A forged or byte-mismatched line, a line for
another value or subject, a newer verdict, a read of the clearing's own page, and an owner-ruled
fact all stay held, in the gate and in the build.

All pages, hashes, verdicts and attempts are synthetic and built here. No page text from any
cite-only host is used.
"""

from __future__ import annotations

import json
import socket
from datetime import UTC, datetime

import pytest
import yaml
from decision.cited_change import CitedChange, cited_reading, reread, reread_reading
from decision.cited_reader import ATTEMPTS_FILE
from decision.quarantine_clearing import (
    CLEARINGS_FILE,
    QUEUE_FILE,
    AttemptLog,
    append,
    clearing_epoch,
    fact_released,
    later_agreements,
    queue_history,
    read_clearings,
    reread_epoch,
    verdict_sha256,
)
from scripts import cited_offering as writer
from scripts.cited_reading import rewritten_row

from tests import test_cited_offering as offering
from tests import test_cited_reading as reading_gate
from tests.snapshot_records import verification
from tests.test_quarantine_clearing import (
    AT,
    EPOCH,
    FACET,
    MID,
    PAGE,
    TEXT,
    TODAY,
    VALUE,
    VERDICT,
    agreement,
    board_rows,
    build,
    cleared_row,
    clearing,
    mismatch,
    plant,
    raw,
    reading_build,
)


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", lambda *a: pytest.fail("Network attempted"))


#: What the gate's own transport serves (``decision.cited_change._http_once``, stubbed): a
#: released verdict is re-read only on a page the gate fetched itself.
PAGES: dict[str, bytes] = {}


@pytest.fixture(autouse=True)
def web(monkeypatch):
    import decision.cited_change as gate_module

    PAGES.clear()
    PAGES.update({offering.URL: offering.PAGE, reading_gate.URL: reading_gate.PAGE})
    monkeypatch.setattr(gate_module, "_http_once", lambda url: (200, None, PAGES[url]))


# --- the gate: a cleared offering fact, through the real gate and writer -------------------------

MOVED = offering.PAGE.replace(b"30 days", b"46 days")
MOVED_AGAIN = offering.PAGE.replace(b"30 days", b"60 days")


@pytest.fixture
def cleared(tmp_path, monkeypatch):
    """A held mismatch (on 45), cleared by a fresh agreement on 30; the record and its line
    written by the real writer."""
    d = offering.Data(tmp_path / "data", monkeypatch)
    plant(d.root, verification("fact", offering.FACT_ID, "mismatch", day="2026-09-20", value=45))
    out = offering.retention(clear_quarantine=True)
    assert out.changed and out.record["clearings"], (out.reason, out.detail)
    writer.apply(out, data_dir=d.root)
    assert len(read_clearings(d.root / CLEARINGS_FILE)) == 1
    return d


def filed(d):
    rows = yaml.safe_load(d.offering_path.read_text())
    return next(f for r in rows for f in r["facts"] if f["id"] == offering.FACT_ID)


def edit(d, change):
    """Change the filed fact in place (``change(fact)``), keeping every other line's data."""
    rows = yaml.safe_load(d.offering_path.read_text())
    change(next(f for r in rows for f in r["facts"] if f["id"] == offering.FACT_ID))
    d.offering_path.write_text(yaml.safe_dump(rows, sort_keys=False))


def again(page=MOVED, value=46):
    """A re-read through the gate's own fetch of ``page``."""
    PAGES[offering.URL] = page
    return reread(filed_of_subject(), source_id="data", readers=offering.pair(value))


def filed_of_subject():
    return {"subject": offering.SUBJECT, "facet": "offering.data.retention"}


def released_now(d) -> bool:
    """The build's own predicate over the gate-written files."""
    verdict = json.loads((d.root / "verification/log.jsonl").read_text().splitlines()[0])
    return fact_released(filed(d), offering.SUBJECT, verdict=verdict,
                         clearings=read_clearings(d.root / CLEARINGS_FILE),
                         log=AttemptLog.read(d.root / ATTEMPTS_FILE),
                         sources={s["id"]: s["url"] for s in d.sources},
                         history=queue_history(d.root / QUEUE_FILE, {offering.FACT_ID}),
                         cutoff=datetime.now(UTC).date())


def rewrite_line(d, path, change):
    lines = (d.root / path).read_text().splitlines()
    (d.root / path).write_text("\n".join(change(lines)) + "\n")


def test_a_released_verdict_lets_two_readers_re_read_a_changed_page(cleared):
    d = cleared
    block = filed(d)["derivation"]["cited_change"]
    assert released_now(d)  # the build admits the cleared block
    out = again()
    assert out.outcome == "changed" and out.record["value"] == 46, (out.reason, out.detail)
    assert d.log()[-1]["epoch"] == f"{block['clearing_epoch']}:reread:{block['text_sha256']}"
    assert "clearing_epoch" not in out.record["derivation"]["cited_change"]
    assert "SECRET-PAGE-MARKER" not in json.dumps(out.record)
    # Written, the later block is admitted by the build too, and is re-read in its own epoch.
    writer.apply(CitedChange("cited_change", None, "", out.record), data_dir=d.root)
    assert filed(d)["value"] == 46 and released_now(d)
    assert again(MOVED, 46).outcome == "current"
    hop = again(MOVED_AGAIN, 60)
    assert hop.outcome == "changed" and hop.record["value"] == 60, (hop.reason, hop.detail)


def test_the_clearing_is_not_re_litigated_on_its_own_page(cleared):
    d = cleared
    before = len(d.log())
    assert again(offering.PAGE).outcome == "current"
    for kw in ({}, {"clear_quarantine": True}, {"readers": offering.pair(46)}):
        out = offering.retention(request=None, **kw)
        assert out.outcome == "refused" and out.reason == "quarantined", (out.reason, kw)
        assert "re-litigated" in out.detail
    assert len(d.log()) == before  # refused before any reader was asked


def test_a_released_fact_is_re_read_only_on_the_gates_own_fetch(cleared):
    """Bytes or a transport a caller supplies never re-read a released fact (review 1)."""
    d = cleared
    before = len(d.log())
    out = reread(filed_of_subject(), source_id="data", readers=offering.pair(46),
                 request=offering.serve({offering.URL: MOVED}))
    assert out.reason == "quarantined" and "fetched itself" in out.detail
    for kw in ({}, {"clear_quarantine": True}):
        out = offering.retention(request=offering.serve({offering.URL: MOVED}),
                                 readers=offering.pair(46), **kw)
        assert out.reason == "quarantined" and "fetched itself" in out.detail
    assert len(d.log()) == before


@pytest.mark.parametrize("forge", ["verdict_hash", "agreement", "value", "subject", "facet",
                                   "epoch", "respelled_attempt"])
def test_a_forged_or_byte_mismatched_clearing_holds_the_re_read(cleared, forge):
    d = cleared

    def forged(lines):
        entry = json.loads(lines[0])
        if forge == "verdict_hash":
            entry["verdict_sha256"] = "sha256:" + "0" * 64
        elif forge == "agreement":
            entry["agreement"] = "sha256:" + "1" * 64
        elif forge == "value":
            entry["value"] = 46
        elif forge == "subject":
            entry["subject"] = "openai/openai/gpt-x/global/other"
        elif forge == "facet":
            entry["facet"] = "offering.data.training"
        elif forge == "epoch":
            entry["epoch"] = clearing_epoch("initial", "sha256:" + "2" * 64)
        return [json.dumps(entry, sort_keys=True)]

    if forge == "respelled_attempt":  # the same fields in another spelling: another line hash
        rewrite_line(d, ATTEMPTS_FILE, lambda lines: [
            json.dumps(json.loads(x), sort_keys=True, separators=(",", ":")) for x in lines])
    else:
        rewrite_line(d, CLEARINGS_FILE, forged)
    assert not released_now(d)
    out = again()
    assert out.outcome == "flagged" and out.reason == "quarantined", (out.reason, out.detail)


def test_a_fact_filed_with_another_value_than_the_clearing_stays_held(cleared):
    d = cleared
    edit(d, lambda f: f.update(value=46))
    assert not released_now(d)
    assert again().reason == "quarantined"


@pytest.mark.parametrize("value,outcome", [(30, "mismatch"), (45, "mismatch"),
                                           (30, "unreachable")])
def test_a_newer_verdict_after_the_clearing_holds_the_fact_again(cleared, value, outcome):
    d = cleared
    today = datetime.now(UTC).date().isoformat()
    plant(d.root, verification("fact", offering.FACT_ID, outcome, day=today, value=value))
    out = again()
    assert out.outcome == "flagged" and out.reason == "quarantined", (out.reason, out.detail)


def test_an_owner_ruled_fact_is_not_released(cleared):
    d = cleared
    edit(d, lambda f: f["derivation"].update(owner_ruling={"subject": offering.SUBJECT}))
    assert not released_now(d)
    out = offering.retention(request=offering.serve({offering.URL: MOVED}),
                             readers=offering.pair(46))
    assert out.outcome == "refused" and out.reason == "quarantined"


def test_without_a_clearing_line_the_re_read_is_still_held(cleared):
    (cleared.root / CLEARINGS_FILE).write_text("")
    assert again().reason == "quarantined"


# --- the gate: a cleared board reading -----------------------------------------------------------

BOARD_MOVED = reading_gate.PAGE.replace(b"51.2%", b"53.0%")


def test_a_cleared_reading_is_re_read_on_a_changed_board(tmp_path, monkeypatch):
    board = reading_gate.Data(tmp_path / "data", monkeypatch)
    board.row["id"] = reading_gate.ROW_ID
    board.write()
    row = verification("evidence", reading_gate.ROW_ID, "mismatch", day="2026-10-14", value=46.6)
    plant(board.root, row, effort=reading_gate.READING["effort"],
          harness=reading_gate.READING["harness"],
          names=[reading_gate.READING["model_id_as_evaluated"]])
    kw = dict(subject=reading_gate.SUBJECT, benchmark_id=reading_gate.BENCH,
              reading=reading_gate.READING, source_id="board")
    out = cited_reading(**kw, readers=reading_gate.pair(), request=reading_gate.serve(),
                        clear_quarantine=True)
    assert out.changed and out.record["clearings"], (out.reason, out.detail)
    board.row = rewritten_row(reading_gate.SUBJECT, board.row, out)
    board.write()
    append(out.record["clearings"], board.root)
    same = cited_reading(**kw, readers=reading_gate.pair())
    assert same.reason == "quarantined" and "re-litigated" in same.detail
    theirs = reread_reading(**kw, readers=reading_gate.pair(53.0),
                            request=reading_gate.serve(BOARD_MOVED))
    assert theirs.reason == "quarantined" and "fetched itself" in theirs.detail
    PAGES[reading_gate.URL] = BOARD_MOVED
    moved = reread_reading(**kw, readers=reading_gate.pair(53.0))
    assert moved.outcome == "changed" and moved.record["value"] == 53.0, (moved.reason,
                                                                          moved.detail)
    (board.root / CLEARINGS_FILE).write_text("")  # no line: the verdict holds again
    PAGES[reading_gate.URL] = BOARD_MOVED.replace(b"53.0", b"54.0")
    held = reread_reading(**kw, readers=reading_gate.pair(53.0))
    assert held.outcome == "flagged" and held.reason == "quarantined"


# --- the build: the block a later agreement made after the clearing epoch -------------------------

LATER_TEXT, LATER_PAGE, LATER_AT = "b" * 64, "5" * 64, "2026-10-12T09:00:00+00:00"
#: The epoch the cleared record is re-read in: its clearing epoch, with the text it read.
AFTER = f"{EPOCH}:reread:{TEXT}"


def later(epoch=None, *, at=LATER_AT, values=(131072, 131072), text=LATER_TEXT,
          page=LATER_PAGE, families=("openai", "anthropic"), **kw):
    """An agreement in an epoch after the clearing's: by default the cleared record's own."""
    entry = agreement(epoch or AFTER, at=at, values=values,
                      families=families, **kw)
    return {**entry, "text_sha256": text, "page_sha256": page}


def later_row(attempt, value=None, subject=MID):
    row = cleared_row(attempt, value=attempt["agreed_value"] if value is None else value,
                      subject=subject)
    block = row["derivation"]["cited_change"]
    del block["previous_epoch"], block["clearing_epoch"]
    return row


def shows(index, value, mid=MID):
    fact = index.fact(mid, FACET)
    return fact.state == "known" and fact.value == value


def test_the_build_admits_a_block_a_later_agreement_made_after_the_clearing():
    first = agreement()
    link = later()
    index = build(later_row(link), [clearing(first)], [first, link])
    assert shows(index, 131072)
    record = index.record(index.fact(MID, FACET).record_id)
    assert record["verification"] is None and record["citation"]["status"] == "cited"
    # and the next epoch: an agreement on the page that link read opens it
    hop = later(reread_epoch("initial", LATER_TEXT), at="2026-10-14T09:00:00+00:00",
                values=(65536, 65536), text="c" * 64, page="6" * 64)
    assert shows(build(later_row(hop), [clearing(first)], [first, link, hop]), 65536)
    log = AttemptLog([raw(first), raw(link), raw(hop)])
    assert {e["epoch"] for e, _ in later_agreements(log, clearing(first), log.entries[0],
                                                    subject=MID, facet=FACET, first="initial",
                                                    cutoff=TODAY)} \
        == {AFTER, reread_epoch("initial", LATER_TEXT)}


def test_the_later_block_needs_a_valid_clearing_line():
    first, link = agreement(), later()
    row = later_row(link)
    assert not shows(build(row, [], [first, link]), 131072)
    forged = clearing(first, verdict_sha256="sha256:" + "0" * 64)
    assert not shows(build(row, [forged], [first, link]), 131072)
    other_value = clearing(first, value=65536)
    assert not shows(build(row, [other_value], [first, link]), 131072)
    respelled = json.dumps(first)  # byte-mismatched: the named line is not in the log
    assert not shows(build(row, [clearing(first)], [respelled, link]), 131072)


@pytest.mark.parametrize("epoch", [EPOCH, "initial", "reread:" + "9" * 64, "reread:" + TEXT,
                                   "made-up:reread:" + TEXT])
def test_an_agreement_outside_the_epochs_after_the_clearing_releases_nothing(epoch):
    """The clearing epoch itself (no re-litigation), its base, an unrelated re-read epoch, the
    plain re-read epoch of the clearing's page (not under the clearing epoch) and a
    reading-shaped epoch are not after the clearing."""
    first = agreement()
    link = later(epoch)
    assert not shows(build(later_row(link), [clearing(first)], [first, link]), 131072)


def test_an_agreement_not_after_the_clearing_agreement_releases_nothing():
    first = agreement()
    earlier = later(at="2026-10-09T09:00:00+00:00")  # a later line, an earlier time
    assert not shows(build(later_row(earlier), [clearing(first)], [first, earlier]), 131072)
    # Ordered by the clearing line's ``cleared_at`` (10:00), not its agreement's time (09:00).
    before_line = later(at="2026-10-10T09:30:00+00:00")
    assert not shows(build(later_row(before_line), [clearing(first)], [first, before_line]),
                     131072)
    at_line = later(at="2026-10-10T10:00:00+00:00")
    assert not shows(build(later_row(at_line), [clearing(first)], [at_line, first]), 131072)
    assert shows(build(later_row(at_line), [clearing(first)], [first, at_line]), 131072)
    past_cutoff = later(at="2026-10-25T09:00:00+00:00")  # after the build's day
    assert not shows(build(later_row(past_cutoff), [clearing(first)], [first, past_cutoff]),
                     131072)


def test_a_disagreement_or_one_family_in_the_later_epoch_releases_nothing():
    first, link = agreement(), later()
    split = later(at="2026-10-13T09:00:00+00:00", values=(131072, 1))
    assert not shows(build(later_row(link), [clearing(first)], [first, link, split]), 131072)
    other = later(at="2026-10-13T09:00:00+00:00", values=(65536, 65536))
    assert not shows(build(later_row(link), [clearing(first)], [first, link, other]), 131072)
    same = later(families=("openai", "openai"))
    assert not shows(build(later_row(same), [clearing(first)], [first, same]), 131072)


def test_the_later_block_must_be_the_one_the_agreement_made():
    first, link = agreement(), later()
    row = later_row(link)
    row["derivation"]["cited_change"]["sha256"] = "7" * 64
    assert not shows(build(row, [clearing(first)], [first, link]), 131072)
    assert not shows(build(later_row(link, value=65536), [clearing(first)], [first, link]), 65536)


def test_a_newer_verdict_after_the_clearing_holds_the_later_block():
    first, link = agreement(), later()
    row = later_row(link)
    for newer in (mismatch(value=131072, day="2026-10-15"), mismatch(day="2026-10-15"),
                  verification("fact", f"{MID}#{FACET}", "unreachable", day="2026-10-15",
                               value=131072)):
        assert not shows(build(row, [clearing(first)], [first, link], log=(VERDICT, newer)),
                         131072)


def test_a_clearing_for_subject_a_does_not_release_subject_b():
    from tests.snapshot_records import model

    beta = "lab/beta"
    verdict_b = mismatch(f"{beta}#{FACET}")
    first, link = agreement(), later()
    row_b = later_row(link, subject=beta)
    models = [model(MID), model(beta, facts=[row_b])]
    index = build(row_b, [clearing(first)], [first, link], log=(VERDICT, verdict_b),
                  models=models)
    assert not shows(index, 131072, beta)


def test_an_owner_ruled_later_block_is_not_released():
    first, link = agreement(), later()
    row = later_row(link)
    row["derivation"]["owner_ruling"] = {"subject": MID, "facet": FACET}
    assert not shows(build(row, [clearing(first)], [first, link]), 131072)


def test_a_later_reading_block_is_admitted_in_the_readings_own_epochs():
    from decision.cited_change import reading_epoch
    from decision.model import evidence_verification_value

    from tests.test_quarantine_clearing import NEW_ID, OLD_ID

    filed_row = board_rows(46.6, OLD_ID)
    verdict = verification("evidence", OLD_ID, "mismatch", day="2026-10-01",
                           value=evidence_verification_value(filed_row))
    settings = {"model_id_as_evaluated": MID, "effort": None, "harness": None}
    first = agreement(clearing_epoch(reading_epoch(settings), verdict_sha256(verdict)),
                      values=(51.2, 51.2), facet="benchmark:bench_x")
    first["url"] = "https://www.perplexity.ai/pro"

    def row_for(link):
        row = board_rows(53.0, NEW_ID)
        row["sources"][0].update(snapshot_ref=f"sha256:{link['page_sha256']}", retrieved_at=AT)
        row["derivation"] = later_row(link)["derivation"]
        return row

    def link_in(epoch):
        entry = later(epoch, values=(53.0, 53.0), facet="benchmark:bench_x")
        entry["url"] = first["url"]
        return entry

    good = link_in(f"{first['epoch']}:reread:{TEXT}")
    assert reading_build(row_for(good), [verdict], [clearing(first, verdict)], [first, good])
    assert reading_build(row_for(good), [verdict], [], [first, good]) == ()
    for epoch in (reread_epoch("initial", TEXT), reread_epoch(reading_epoch(settings), TEXT)):
        wrong = link_in(epoch)
        assert reading_build(row_for(wrong), [verdict], [clearing(first, verdict)],
                             [first, wrong]) == ()
    own = link_in(first["epoch"])
    assert reading_build(row_for(own), [verdict], [clearing(first, verdict)], [first, own]) == ()


def test_the_cleared_block_itself_is_still_admitted():
    """MODEL-552's own path is unchanged."""
    first = agreement()
    assert shows(build(cleared_row(first), [clearing(first)], [first]), VALUE)


# --- cleared twice: the latest valid clearing is followed -----------------------------------------


class Clock:
    """The gate's and the harness's clock, set by the test (``datetime.now`` only)."""

    def __init__(self, monkeypatch):
        import decision.cited_change as gate_module
        import decision.cited_reader as reader_module

        self.at = datetime(2026, 10, 1, 9, tzinfo=UTC)
        clock = self

        class Fixed(datetime):
            @classmethod
            def now(cls, tz=None):
                at = cls.fromisoformat(clock.at.isoformat())
                return at if tz is not None else at.replace(tzinfo=None)

        for module in (gate_module, reader_module):
            monkeypatch.setattr(module, "datetime", Fixed)


def checked(d, verdict, at):
    """A verdict and only its check in the queue: the claim it checked is the writer's last."""
    log = d.root / "verification/log.jsonl"
    with log.open("a") as fh:
        fh.write(json.dumps(verdict) + "\n")
    with (d.root / QUEUE_FILE).open("a") as fh:
        fh.write(json.dumps({"event": "checked", "at": at, "target": {
            "kind": "fact", "id": offering.FACT_ID}, "outcome": verdict["outcome"]}) + "\n")
    return verdict


def released_all(d) -> bool:
    """Every held verdict released, by the build's own predicate over the gate-written files."""
    from decision.cited_change import quarantine_rows

    held = [row for _, row in quarantine_rows([offering.FACT_ID], filed(d), d.root)]
    common = dict(clearings=read_clearings(d.root / CLEARINGS_FILE),
                  log=AttemptLog.read(d.root / ATTEMPTS_FILE),
                  sources={s["id"]: s["url"] for s in d.sources},
                  history=queue_history(d.root / QUEUE_FILE, {offering.FACT_ID}),
                  cutoff=datetime(2026, 12, 31).date(), held=held)
    return bool(held) and all(fact_released(filed(d), offering.SUBJECT, verdict=row, **common)
                              for row in held)


@pytest.fixture
def twice(tmp_path, monkeypatch):
    """Cleared on 1 October (a mismatch on 45); a new mismatch on the cleared value, checked on
    5 October against the writer's claim; cleared again on 8 October, on the same page."""
    clock = Clock(monkeypatch)
    d = offering.Data(tmp_path / "data", monkeypatch)
    plant(d.root, verification("fact", offering.FACT_ID, "mismatch", day="2026-09-20", value=45))
    first = offering.retention(clear_quarantine=True)
    assert first.changed, (first.reason, first.detail)
    writer.apply(first, data_dir=d.root)
    checked(d, verification("fact", offering.FACT_ID, "mismatch", day="2026-10-05", value=30),
            "2026-10-05T21:00:00+00:00")
    clock.at = datetime(2026, 10, 8, 9, tzinfo=UTC)
    assert offering.retention().reason == "quarantined"  # the new verdict holds
    assert not released_all(d)
    second = offering.retention(clear_quarantine=True)
    assert second.changed, (second.reason, second.detail)
    writer.apply(second, data_dir=d.root)
    assert len(read_clearings(d.root / CLEARINGS_FILE)) == 2
    return d, clock


def test_a_fact_cleared_twice_is_served_and_re_read(twice):
    """The verdict between the two clearings is the one the second clears; the first verdict is
    released through it. Gate and build agree, and a later page change is read again."""
    d, clock = twice
    assert released_all(d)  # the build releases both: the first through the second clearing
    assert "re-litigated" in offering.retention(request=None).detail  # not on its own page
    clock.at = datetime(2026, 10, 20, 9, tzinfo=UTC)
    out = again()
    assert out.outcome == "changed" and out.record["value"] == 46, (out.reason, out.detail)
    writer.apply(CitedChange("cited_change", None, "", out.record), data_dir=d.root)
    assert released_all(d)


def test_a_verdict_between_the_two_clearings_that_no_line_names_holds(twice):
    d, clock = twice
    checked(d, verification("fact", offering.FACT_ID, "mismatch", day="2026-10-06", value=65536),
            "2026-10-06T21:00:00+00:00")
    assert not released_all(d)
    clock.at = datetime(2026, 10, 20, 9, tzinfo=UTC)
    assert again().reason == "quarantined"


def test_a_verdict_newer_than_the_latest_clearing_holds(twice):
    d, clock = twice
    checked(d, verification("fact", offering.FACT_ID, "mismatch", day="2026-10-09", value=30),
            "2026-10-09T21:00:00+00:00")
    clock.at = datetime(2026, 10, 20, 9, tzinfo=UTC)
    assert not released_all(d) and again().reason == "quarantined"


def test_without_the_first_line_the_second_clearing_does_not_release_the_first_verdict(twice):
    d, clock = twice
    rewrite_line(d, CLEARINGS_FILE, lambda lines: lines[1:])
    clock.at = datetime(2026, 10, 20, 9, tzinfo=UTC)
    assert not released_all(d) and again().reason == "quarantined"


# the build, synthetic: v1 cleared by C1 (A1), v2 on the cleared value cleared by C2 (A2)

V1 = mismatch(value=131072)
#: The epoch the record the first clearing made is re-read in.
AFTER1 = f"{clearing_epoch('initial', verdict_sha256(V1))}:reread:{TEXT}"
SECOND_TEXT, SECOND_PAGE, SECOND_AT = "d" * 64, "8" * 64, "2026-10-14T09:00:00+00:00"


def second_verdict(day="2026-10-12", value=VALUE):
    return mismatch(value=value, day=day)


def twice_build(row, *, clearings=None, extra_log=(), attempts=None, v2=None):
    from tests.test_quarantine_clearing import events

    v2 = v2 or second_verdict()
    a1 = agreement(clearing_epoch("initial", verdict_sha256(V1)))
    a2 = {**agreement(clearing_epoch(AFTER1, verdict_sha256(v2)),
                      at=SECOND_AT), "page_sha256": SECOND_PAGE, "text_sha256": SECOND_TEXT}
    lines = [clearing(a1, V1), clearing(a2, v2, cleared_at="2026-10-14T10:00:00+00:00")]
    history = {f"{MID}#{FACET}": [
        *events(V1),
        *events(v2, method="two-readers-cited-change@3",
                sources=[{"source_id": "src-cite", "snapshot_ref": f"sha256:{PAGE}"}])]}
    for extra in extra_log:
        history[f"{MID}#{FACET}"] += events(extra)
    return build(row(a1, a2) if callable(row) else row,
                 lines if clearings is None else clearings(lines),
                 [a1, a2] if attempts is None else attempts(a1, a2),
                 log=(V1, v2, *extra_log), history=history)


def second_row(a1, a2):
    return cleared_row(a2, base=AFTER1)


def test_the_build_serves_a_fact_cleared_twice():
    assert shows(twice_build(second_row), VALUE)


def test_the_build_needs_both_lines_for_a_fact_cleared_twice():
    assert not shows(twice_build(second_row, clearings=lambda lines: lines[1:]), VALUE)
    assert not shows(twice_build(second_row, clearings=lambda lines: lines[:1]), VALUE)
    def forged(lines):
        return [lines[0], {**lines[1], "verdict_sha256": "sha256:" + "0" * 64}]

    assert not shows(twice_build(second_row, clearings=forged), VALUE)


def test_a_second_clearing_logged_before_the_first_releases_nothing():
    assert not shows(twice_build(second_row, attempts=lambda a1, a2: [a2, a1]), VALUE)


def test_the_build_holds_a_verdict_between_or_after_the_clearings_that_no_line_names():
    between = mismatch(value=65536, day="2026-10-13")
    assert not shows(twice_build(second_row, extra_log=(between,)), VALUE)
    newer = mismatch(value=65536, day="2026-10-16")
    assert not shows(twice_build(second_row, extra_log=(newer,)), VALUE)
    again_v2 = second_verdict(day="2026-10-16")  # a newer verdict on the cleared value itself
    assert not shows(twice_build(second_row, extra_log=(again_v2,)), VALUE)


def test_a_re_read_after_the_second_clearing_is_served():
    link = later(f"{clearing_epoch(AFTER1, verdict_sha256(second_verdict()))}:reread:"
                 f"{SECOND_TEXT}", at="2026-10-16T09:00:00+00:00",
                 values=(65536, 65536), text="e" * 64, page="9" * 64)
    index = twice_build(lambda a1, a2: later_row(link), attempts=lambda a1, a2: [a1, a2, link])
    assert shows(index, 65536)


# --- adversarial review round 1 (MODEL-566) -------------------------------------------------------


def test_a_re_read_of_the_same_page_in_the_descendant_epoch_releases_nothing():
    """The descendant epoch's name is predictable; a read logged there of the clearing's own
    page (its text hash, or its cited region when both logged one) is no link (finding 1)."""
    first = agreement()
    same_text = later(text=TEXT)
    assert not shows(build(later_row(same_text), [clearing(first)], [first, same_text]), 131072)
    regioned = {**first, "region_sha256": "f" * 64}
    same_region = {**later(), "region_sha256": "f" * 64}
    assert not shows(build(later_row(same_region), [clearing(regioned)],
                           [regioned, same_region]), 131072)
    moved_region = {**later(), "region_sha256": "e" * 64}
    assert shows(build(later_row(moved_region), [clearing(regioned)], [regioned, moved_region]),
                 131072)


def test_only_the_latest_valid_clearing_of_a_verdict_counts():
    """An older clearing's block, and a block descending from it, is not admitted once a later
    valid clearing of the same verdict exists (finding 3)."""
    older = agreement()
    newer = {**agreement(at="2026-10-11T09:00:00+00:00"), "page_sha256": "7" * 64,
             "text_sha256": "c" * 64}
    lines = [clearing(older), clearing(newer, cleared_at="2026-10-11T10:00:00+00:00")]
    logged = [older, newer]
    assert shows(build(cleared_row(newer), lines, logged), VALUE)
    assert not shows(build(cleared_row(older), lines, logged), VALUE)
    assert shows(build(cleared_row(older), lines[:1], logged), VALUE)  # alone, it still counts
    link = later(at="2026-10-12T09:00:00+00:00")  # after the older clearing only
    assert not shows(build(later_row(link), lines, [*logged, link]), 131072)
    assert shows(build(later_row(link), lines[:1], [*logged, link]), 131072)


def test_a_verdicts_epoch_comes_only_from_the_records_own_agreement():
    """Never another setting's attempt on the same board copy, and never a clearing-shaped
    attempt no line names (finding 4)."""
    from decision.cited_change import reading_epoch
    from decision.quarantine_clearing import epoch_after, line_hash, verdict_epoch

    from tests.test_quarantine_clearing import events

    ours = reading_epoch({"model_id_as_evaluated": MID, "effort": None, "harness": None})
    theirs = reading_epoch({"model_id_as_evaluated": MID, "effort": "low", "harness": None})
    verdict = mismatch(day="2026-10-12")
    trail = events(verdict, method="two-readers-cited-change@3",
                   sources=[{"source_id": "src-cite", "snapshot_ref": f"sha256:{PAGE}"}])
    kw = dict(history=trail, subject=MID, facet=FACET, first=ours)
    other = agreement(f"{theirs}:reread:{'1' * 64}")
    assert verdict_epoch(verdict, log=AttemptLog([raw(other)]), **kw) is None
    own = agreement(ours)
    assert verdict_epoch(verdict, log=AttemptLog([raw(own)]), **kw) == f"{ours}:reread:{TEXT}"
    shaped = agreement(clearing_epoch("initial", "sha256:" + "2" * 64))
    fact_kw = {**kw, "first": "initial"}
    assert verdict_epoch(verdict, log=AttemptLog([raw(shaped)]), **fact_kw) is None
    named = [{"subject": MID, "facet": FACET, "epoch": shaped["epoch"],
              "agreement": line_hash(raw(shaped))}]
    assert verdict_epoch(verdict, log=AttemptLog([raw(shaped)]), clearings=named,
                         **fact_kw) == epoch_after("initial", shaped)
    wrong = [{**named[0], "agreement": "sha256:" + "3" * 64}]
    assert verdict_epoch(verdict, log=AttemptLog([raw(shaped)]), clearings=wrong,
                         **fact_kw) is None


def test_a_conflicting_incomplete_answer_blocks_a_readings_re_read(tmp_path, monkeypatch):
    """The reading gate counts an answer inside an incomplete attempt in the released row's
    epoch, as the build does (finding 5)."""
    from decision.cited_change import reading_epoch

    board = reading_gate.Data(tmp_path / "data", monkeypatch)
    board.row["id"] = reading_gate.ROW_ID
    board.write()
    plant(board.root, verification("evidence", reading_gate.ROW_ID, "mismatch",
                                   day="2026-10-14", value=46.6),
          effort=reading_gate.READING["effort"], harness=reading_gate.READING["harness"],
          names=[reading_gate.READING["model_id_as_evaluated"]])
    kw = dict(subject=reading_gate.SUBJECT, benchmark_id=reading_gate.BENCH,
              reading=reading_gate.READING, source_id="board")
    out = cited_reading(**kw, readers=reading_gate.pair(), request=reading_gate.serve(),
                        clear_quarantine=True)
    assert out.changed, (out.reason, out.detail)
    board.row = rewritten_row(reading_gate.SUBJECT, board.row, out)
    board.write()
    append(out.record["clearings"], board.root)
    epoch = reading_epoch(reading_gate.READING, board.row)
    with (board.root / ATTEMPTS_FILE).open("a") as fh:
        fh.write(json.dumps({"subject": reading_gate.SUBJECT,
                             "facet": f"benchmark:{reading_gate.BENCH}", "epoch": epoch,
                             "complete": False, "harness": True, "readers": [
                                 {"reader_id": "claude", "family": "anthropic", "version": "1",
                                  "value": 12.5}]}) + "\n")
    PAGES[reading_gate.URL] = BOARD_MOVED
    held = reread_reading(**kw, readers=reading_gate.pair(53.0))
    assert held.outcome == "flagged" and held.reason == "prior_attempt_disagreed", held


# --- adversarial review round 2 (MODEL-566) -------------------------------------------------------


def test_a_same_page_attempt_on_another_value_never_supplies_the_epoch():
    """The agreement that set the record's epoch must be on the claim's value (finding 1)."""
    from decision.quarantine_clearing import verdict_epoch

    from tests.test_quarantine_clearing import events

    verdict = mismatch(day="2026-10-12")
    trail = events(verdict, method="two-readers-cited-change@3",
                   sources=[{"source_id": "src-cite", "snapshot_ref": f"sha256:{PAGE}"}])
    kw = dict(history=trail, subject=MID, facet=FACET, first="initial")
    other = agreement("initial", values=(65536, 65536))
    assert verdict_epoch(verdict, log=AttemptLog([raw(other)]), **kw) is None
    same = agreement("initial")
    assert verdict_epoch(verdict, log=AttemptLog([raw(other), raw(same)]), **kw) \
        == reread_epoch("initial", TEXT)


def test_every_opener_of_an_epoch_counts():
    """Two agreements open the same epoch (the same page text, other cited regions); a read
    there that only the second makes valid is still a link (finding 2)."""
    first = {**agreement(), "region_sha256": "1" * 64}
    one = {**later(at="2026-10-12T09:00:00+00:00"), "region_sha256": "2" * 64}
    two = {**later(at="2026-10-12T10:00:00+00:00"), "region_sha256": "3" * 64}
    read = {**later(reread_epoch("initial", LATER_TEXT), at="2026-10-13T09:00:00+00:00",
                    values=(65536, 65536), text="c" * 64, page="6" * 64),
            "region_sha256": "2" * 64}  # the region ``one`` read: no move against it
    logged = [first, one, two, read]
    assert shows(build(later_row(read), [clearing(first)], logged), 65536)
    assert not shows(build(later_row(read), [clearing(first)], [first, one, read]), 65536)


def test_the_gate_takes_its_opener_from_the_releasing_chain():
    """Only the chain's own agreements that open the epoch are compared, never another
    attempt on the same page in another epoch or source (finding 3)."""
    from decision.cited_change import _relitigates
    from decision.cited_reader import text_sha256
    from decision.quarantine_clearing import epoch_after, openers

    page = b"<html><body>a synthetic page, long enough to read</body></html>"
    opener = {**later(), "text_sha256": "0" * 64, "region_sha256": "1" * 64}
    # The same page read in a clearing epoch opens another epoch: it is no opener of this one.
    decoy = {**opener, "epoch": clearing_epoch("initial", "sha256:" + "4" * 64),
             "region_sha256": "2" * 64}
    epoch = epoch_after("initial", opener)
    assert openers([opener, decoy], "initial", epoch) == [opener]
    kw = dict(own_fetch=True, first="initial", epoch=epoch)
    assert _relitigates([[opener]], page, region="1" * 64, **kw).reason == "quarantined"
    assert _relitigates([[opener]], page, region="2" * 64, **kw) is None
    same_text = {**opener, "text_sha256": text_sha256(page)}
    assert _relitigates([[same_text]], page, region="9" * 64, **kw).reason == "quarantined"
    assert _relitigates([[opener]], page, region="2" * 64, own_fetch=False, first="initial",
                        epoch=epoch).reason == "quarantined"


def seed_epoch(root, subject, facet, epoch, **entry):
    with (root / ATTEMPTS_FILE).open("a") as fh:
        fh.write(json.dumps({"subject": subject, "facet": facet, "epoch": epoch,
                             "harness": True, "at": "2026-11-01T09:00:00+00:00", **entry},
                            sort_keys=True) + "\n")


SILENT = {"complete": True, "agreed": True, "agreed_value": None, "readers": [
    {"reader_id": "codex", "family": "openai", "version": "1", "value": None},
    {"reader_id": "claude", "family": "anthropic", "version": "1", "value": None}]}


@pytest.mark.parametrize("seeded", ["nothing", "silence", "incomplete", "other_value"])
def test_the_gate_and_the_build_agree_on_a_re_read(cleared, seeded):
    """Parity (round 2): on the same logs, the gate accepts a re-read exactly when the build
    walks it as a link after the clearing. A complete agreement on silence then a value, an
    incomplete answer and an agreement on another value are refused by both (finding 4)."""
    from decision.cited_change import fact_epoch

    d = cleared
    epoch = fact_epoch(filed(d))
    facet = "offering.data.retention"
    if seeded == "silence":
        seed_epoch(d.root, offering.SUBJECT, facet, epoch, **SILENT)
    elif seeded == "incomplete":
        seed_epoch(d.root, offering.SUBJECT, facet, epoch, complete=False, readers=[
            {"reader_id": "codex", "family": "openai", "version": "1", "value": 12}])
    elif seeded == "other_value":
        seed_epoch(d.root, offering.SUBJECT, facet, epoch, **{
            **SILENT, "agreed_value": 12,
            "readers": [{**r, "value": 12} for r in SILENT["readers"]]})
    before = len(d.log())
    out = again()
    log = AttemptLog.read(d.root / ATTEMPTS_FILE)
    [entry] = read_clearings(d.root / CLEARINGS_FILE)
    agreed = next(e for e in log.entries if e["epoch"] == entry["epoch"])
    walked = later_agreements(log, entry, agreed, subject=offering.SUBJECT, facet=facet,
                              first="initial", cutoff=datetime.now(UTC).date())
    gate_read = log.entries[-1] if len(log.entries) > before else None
    in_build = gate_read is not None and any(n == gate_read for n, _ in walked)
    assert (out.outcome == "changed") is in_build, (seeded, out.reason, out.detail)
    assert (out.outcome == "changed") is (seeded == "nothing")


def test_an_absence_then_a_score_refuses_a_readings_re_read(tmp_path, monkeypatch):
    """The board gate refuses a released row's re-read on a value after an agreed absence in
    its epoch, as the build does (finding 4)."""
    from decision.cited_change import reading_epoch

    board = reading_gate.Data(tmp_path / "data", monkeypatch)
    board.row["id"] = reading_gate.ROW_ID
    board.write()
    plant(board.root, verification("evidence", reading_gate.ROW_ID, "mismatch",
                                   day="2026-10-14", value=46.6),
          effort=reading_gate.READING["effort"], harness=reading_gate.READING["harness"],
          names=[reading_gate.READING["model_id_as_evaluated"]])
    kw = dict(subject=reading_gate.SUBJECT, benchmark_id=reading_gate.BENCH,
              reading=reading_gate.READING, source_id="board")
    out = cited_reading(**kw, readers=reading_gate.pair(), request=reading_gate.serve(),
                        clear_quarantine=True)
    assert out.changed, (out.reason, out.detail)
    board.row = rewritten_row(reading_gate.SUBJECT, board.row, out)
    board.write()
    append(out.record["clearings"], board.root)
    seed_epoch(board.root, reading_gate.SUBJECT, f"benchmark:{reading_gate.BENCH}",
               reading_epoch(reading_gate.READING, board.row), **SILENT)
    PAGES[reading_gate.URL] = BOARD_MOVED
    held = reread_reading(**kw, readers=reading_gate.pair(53.0))
    assert held.outcome == "flagged" and held.reason == "prior_attempt_disagreed", held
