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
    TEXT,
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
    return reread(filed_of_subject(), source_id="data", readers=offering.pair(value),
                  request=offering.serve({offering.URL: page}))


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
    assert d.log()[-1]["epoch"] == reread_epoch("initial", block["text_sha256"])
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
        out = offering.retention(**kw)
        assert out.outcome == "refused" and out.reason == "quarantined", (out.reason, kw)
        assert "re-litigated" in out.detail
    assert len(d.log()) == before  # refused before any reader was asked


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
    same = cited_reading(**kw, readers=reading_gate.pair(), request=reading_gate.serve())
    assert same.reason == "quarantined" and "re-litigated" in same.detail
    moved = reread_reading(**kw, readers=reading_gate.pair(53.0),
                           request=reading_gate.serve(BOARD_MOVED))
    assert moved.outcome == "changed" and moved.record["value"] == 53.0, (moved.reason,
                                                                          moved.detail)
    (board.root / CLEARINGS_FILE).write_text("")  # no line: the verdict holds again
    held = reread_reading(**kw, readers=reading_gate.pair(53.0),
                          request=reading_gate.serve(BOARD_MOVED.replace(b"53.0", b"54.0")))
    assert held.outcome == "flagged" and held.reason == "quarantined"


# --- the build: the block a later agreement made after the clearing epoch -------------------------

LATER_TEXT, LATER_PAGE, LATER_AT = "b" * 64, "5" * 64, "2026-10-12T09:00:00+00:00"


def later(epoch=None, *, at=LATER_AT, values=(131072, 131072), text=LATER_TEXT,
          page=LATER_PAGE, families=("openai", "anthropic"), **kw):
    """An agreement in an epoch after the clearing's: by default the cleared record's own."""
    entry = agreement(epoch or reread_epoch("initial", TEXT), at=at, values=values,
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
    assert {e["epoch"] for e in later_agreements(log, log.entries[0], subject=MID, facet=FACET,
                                                 first="initial")} \
        == {reread_epoch("initial", TEXT), reread_epoch("initial", LATER_TEXT)}


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


@pytest.mark.parametrize("epoch", [EPOCH, "initial", "reread:" + "9" * 64,
                                   "made-up:reread:" + TEXT])
def test_an_agreement_outside_the_epochs_after_the_clearing_releases_nothing(epoch):
    """The clearing epoch itself (no re-litigation), its base, an unrelated re-read epoch and a
    reading-shaped epoch are not after the clearing."""
    first = agreement()
    link = later(epoch)
    assert not shows(build(later_row(link), [clearing(first)], [first, link]), 131072)


def test_an_agreement_not_after_the_clearing_agreement_releases_nothing():
    first = agreement()
    earlier = later(at="2026-10-09T09:00:00+00:00")  # a later line, an earlier time
    assert not shows(build(later_row(earlier), [clearing(first)], [first, earlier]), 131072)
    same_time = later(at=AT)
    assert not shows(build(later_row(same_time), [clearing(first)], [same_time, first]), 131072)
    assert shows(build(later_row(same_time), [clearing(first)], [first, same_time]), 131072)


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

    good = link_in(reread_epoch(reading_epoch(settings), TEXT))
    assert reading_build(row_for(good), [verdict], [clearing(first, verdict)], [first, good])
    assert reading_build(row_for(good), [verdict], [], [first, good]) == ()
    fact_shaped = link_in(reread_epoch("initial", TEXT))
    assert reading_build(row_for(fact_shaped), [verdict], [clearing(first, verdict)],
                         [first, fact_shaped]) == ()
    own = link_in(first["epoch"])
    assert reading_build(row_for(own), [verdict], [clearing(first, verdict)], [first, own]) == ()


def test_the_cleared_block_itself_is_still_admitted():
    """MODEL-552's own path is unchanged."""
    first = agreement()
    assert shows(build(cleared_row(first), [clearing(first)], [first]), VALUE)
