"""MODEL-569: the owner may rule on a benchmark board reading whose two readers disagreed.

The same limits as a fact's ruling (MODEL-551): only past a complete recorded disagreement in the
row's current epoch (a board epoch names the row's board region, MODEL-555), by the owner, on a
counts-only basis; the build admits the row only through a valid ruling line, by the same helper
the filer and the gate use (``decision.board_ruling.row_problem``). A ruled row goes on the
re-read: a changed board region reopens it, an unchanged one keeps the ruled value. A ruling never
lifts a hold. These are the bypass tests. Every page, value, hash and attempt is synthetic.
"""

from __future__ import annotations

import copy
import json
from datetime import UTC, datetime

import pytest
import yaml
from decision import board_ruling
from decision.cited_change import BOARD_MARK, reading_epoch
from decision.cited_reader import ATTEMPTS_FILE
from decision.owner_ruling import RULINGS_FILE, attempt_id
from scripts import file_owner_ruling as filer

from tests.test_board_epoch import (  # noqa: F401
    BASE,
    FACET,
    READING,
    ROW_ID,
    SUBJECT,
    URL,
    Board,
    board,
    data,
    html_data,
    offline,
    own,
    pair,
    read,
    refused,
    row_region,
)

TODAY = datetime.now(UTC).date().isoformat()
BASIS = "2 readers split on 1 row; 1 attempt resolved"


def split(**kw):
    out = read(readers=pair(51.2, 49.0), **kw)
    assert out.outcome == "refused" and out.reason == "readers_disagree", (out.reason, out.detail)


def board_epoch_of(d, own):
    return f"{BASE}{BOARD_MARK}{row_region(d, own.pages)}"


def args(d, **kw):
    out = dict(data_dir=d.root, subject=SUBJECT, facet=FACET, value=49.0, state="known",
               ruled_by="jamie", ruled_at=TODAY, ticket="MODEL-569", source_ids=["board"],
               basis=BASIS, reading=dict(READING))
    out.update(kw)
    return out


def file(d, **kw):
    result = filer.plan(**args(d, **kw))
    filer.apply(result)
    return result


def refuses(d, reason, **kw):
    with pytest.raises(filer.Refused) as caught:
        filer.plan(**args(d, **kw))
    assert caught.value.reason == reason, (caught.value.reason, caught.value.detail)
    return caught.value


def card_row(d):
    text = (d.root / "models/acme/orbit-9.md").read_text()
    front = yaml.safe_load(text.split("---", 2)[1])
    [row] = front["benchmarks"]["evidence"]
    return row


def rulings(d):
    path = d.root / RULINGS_FILE
    return [json.loads(x) for x in path.read_text().splitlines()] if path.is_file() else []


@pytest.fixture
def split_row(html_data, own):
    """A board row whose two readers split in its board epoch, read by the gate itself."""
    html_data.row.update(unit="percent", source_url=URL)
    html_data.bench["metric"]["unit"] = "percent"
    html_data.write()
    split()
    return html_data


def ruled(d, own):
    epoch = board_epoch_of(d, own)
    file(d, epoch=epoch)
    return epoch


# --- the filer ------------------------------------------------------------------------------------


def test_a_split_board_row_is_ruled_and_the_row_carries_the_line(split_row, own):
    epoch = ruled(split_row, own)
    [line] = rulings(split_row)
    assert line["epoch"] == epoch and line["facet"] == FACET and line["value"] == 49.0
    assert line["resolves"] == [attempt_id(a) for a in split_row.log()]
    row = card_row(split_row)
    assert row["score"] == 49.0 and row["derivation"]["owner_ruling"] == line
    [attempt] = split_row.log()
    [ref] = row["sources"]
    assert ref["snapshot_ref"] == f"sha256:{attempt['page_sha256']}"
    assert ref["retrieved_at"] == attempt["at"] and row["id"] != ROW_ID
    # Nothing is filed on the queue, and the attempt log is untouched.
    assert len(split_row.log()) == 1
    assert not (split_row.root / "verification/queue/events.jsonl").exists()


def test_the_dry_run_cli_writes_nothing_and_prints_counts_only(split_row, own, capsys):
    before = (split_row.root / "models/acme/orbit-9.md").read_text()
    code = filer.main(["--data-dir", str(split_row.root), "--subject", SUBJECT, "--facet", FACET,
                       "--epoch", board_epoch_of(split_row, own), "--value", "49.0",
                       "--state", "known", "--ruled-by", "jamie", "--ruled-at", TODAY,
                       "--ticket", "MODEL-569", "--source", "board", "--basis", BASIS,
                       "--reading", json.dumps(READING)])
    out = json.loads(capsys.readouterr().out)
    assert code == 0 and out["outcome"] == "planned" and out["ruling_line"] is True
    assert (split_row.root / "models/acme/orbit-9.md").read_text() == before
    assert rulings(split_row) == [] and "Orbit 9 Max" not in json.dumps(out)


def test_no_disagreement_is_refused(html_data, own):
    assert read(readers=pair(51.2)).changed  # an agreement, not a split
    refuses(html_data, "no_disagreement", epoch=board_epoch_of(html_data, own))


def test_an_incomplete_or_seeded_split_is_not_a_disagreement(split_row, own):
    path = split_row.root / ATTEMPTS_FILE
    [line] = split_row.log()
    for change in ({"harness": False}, {"complete": False}, {"prompt_sha256": None}):
        path.write_text(json.dumps({**line, **change}) + "\n")
        refuses(split_row, "no_disagreement", epoch=line["epoch"])


@pytest.mark.parametrize("who", ["claude", "Jamie", "", "orchestrator"])
def test_a_non_owner_is_refused(split_row, own, who):
    refuses(split_row, "not_owner", epoch=board_epoch_of(split_row, own), ruled_by=who)


@pytest.mark.parametrize("kw", [dict(basis="see https://cursor.com/x"), dict(basis="a\nb"),
                                dict(basis="x" * 401), dict(basis=" ")])
def test_the_basis_is_counts_only(split_row, own, kw):
    refuses(split_row, "basis_invalid", epoch=board_epoch_of(split_row, own), **kw)


@pytest.mark.parametrize("kw", [dict(value="49.0"), dict(value=True), dict(value=-1),
                                dict(value=101), dict(value=None, state="not_disclosed"),
                                dict(state="unknown")])
def test_a_board_ruling_states_a_score_in_the_boards_range(split_row, own, kw):
    refuses(split_row, "value_invalid", epoch=board_epoch_of(split_row, own), **kw)


def test_another_rows_epoch_or_the_settings_epoch_is_refused(split_row, own):
    refuses(split_row, "no_disagreement", epoch=BASE)                  # the split is not there
    other = dict(READING, effort="low")
    refuses(split_row, "registry_lookup_failed", epoch=board_epoch_of(split_row, own),
            reading=other)                                             # no such row
    refuses(split_row, "no_disagreement", epoch=f"{BASE}{BOARD_MARK}{'e' * 64}")


def test_a_stale_epoch_is_refused(split_row, own):
    epoch = board_epoch_of(split_row, own)
    own.page = board(score="53.0")              # the board's cited region changed
    assert read(readers=pair(53.0)).changed is True  # a later agreement, in a new board epoch
    refuses(split_row, "epoch_not_current", epoch=epoch)


def test_a_later_split_in_a_new_board_epoch_makes_the_older_one_stale(split_row, own):
    old = board_epoch_of(split_row, own)
    own.page = board(score="53.0")
    split()
    new = board_epoch_of(split_row, own)
    assert new != old
    refuses(split_row, "epoch_not_current", epoch=old)
    file(split_row, epoch=new, value=53.0)


def test_a_held_reading_is_refused_and_a_ruling_lifts_no_hold(split_row, own):
    from decision.model import evidence_verification_value

    from tests.snapshot_records import verification

    row = card_row(split_row)
    row["id"] = ROW_ID
    verdict = verification("evidence", ROW_ID, "mismatch", day="2026-10-01",
                           value=evidence_verification_value(row))
    path = split_row.root / "verification/log.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(verdict) + "\n")
    refuses(split_row, "quarantined", epoch=board_epoch_of(split_row, own))
    assert rulings(split_row) == []


def test_a_duplicate_ruling_is_refused_and_a_stopped_write_finishes(split_row, own, monkeypatch):
    epoch = board_epoch_of(split_row, own)
    result = filer.plan(**args(split_row, epoch=epoch))
    monkeypatch.setattr(filer, "write_atomic", lambda *a: (_ for _ in ()).throw(OSError("stop")))
    with pytest.raises(OSError):
        filer.apply(result)
    assert len(rulings(split_row)) == 1 and card_row(split_row)["score"] == 46.6
    monkeypatch.undo()
    file(split_row, epoch=epoch)                 # the rerun finishes the write
    assert len(rulings(split_row)) == 1 and card_row(split_row)["score"] == 49.0
    refuses(split_row, "duplicate_ruling", epoch=epoch)
    refuses(split_row, "duplicate_ruling", epoch=epoch, value=50.0)


def test_a_source_the_row_does_not_cite_or_another_owners_is_refused(split_row, own):
    refuses(split_row, "source_mismatch", epoch=board_epoch_of(split_row, own),
            source_ids=["hf"])


# --- the gate and the re-read ---------------------------------------------------------------------


def test_after_a_ruling_the_same_board_still_blocks(split_row, own):
    ruled(split_row, own)
    own.page = board(banner="We use cookies", clock="17:42")   # churn outside the cited region
    refused("prior_attempt_disagreed", readers=pair(51.2))
    assert len(split_row.log()) == 1 and card_row(split_row)["score"] == 49.0


def test_a_caller_transport_never_reopens_a_ruled_row(split_row, own):
    ruled(split_row, own)
    page = board(score="53.0")
    refused("prior_attempt_disagreed", readers=pair(53.0), request=lambda url: (200, None, page))


def test_a_changed_board_region_reopens_the_ruled_row(split_row, own):
    epoch = ruled(split_row, own)
    own.page = board(score="53.0")
    out = read(readers=pair(53.0))
    assert out.changed and out.record["value"] == 53.0
    last = split_row.log()[-1]
    region = row_region(split_row, own.pages)
    assert last["epoch"] == f"{epoch}:reopen:{region}" and last["board_region_sha256"] == region


def test_a_split_in_the_reopened_epoch_blocks_and_may_be_ruled_again(split_row, own):
    epoch = ruled(split_row, own)
    own.page = board(score="53.0")
    split()
    reopened = split_row.log()[-1]["epoch"]
    assert reopened.startswith(epoch + ":reopen:")
    refused("prior_attempt_disagreed", readers=pair(53.0))
    # The first ruling still stands while the reopened split waits: the row is admitted.
    assert board_ruling.stale_problem(card_row(split_row)["derivation"]["owner_ruling"],
                                      row=card_row(split_row), subject=SUBJECT,
                                      attempts=split_row.log()) is None
    file(split_row, epoch=reopened, value=53.0)
    assert card_row(split_row)["derivation"]["owner_ruling"]["epoch"] == reopened
    own.page = board(score="53.0", clock="23:59")
    refused("prior_attempt_disagreed", readers=pair(53.0))


def test_a_ruled_row_cannot_be_cleared(split_row, own):
    from decision.cited_change import _clearing_target

    ruled(split_row, own)
    refusal, target = _clearing_target([(("evidence", "x", "y"), {"outcome": "mismatch"})],
                                       card_row(split_row), datetime.now(UTC), allowed=True,
                                       kind="evidence")
    assert refusal.reason == "quarantined" and target is None


def test_reread_reading_keeps_the_ruled_value_until_the_region_changes(split_row, own):
    from decision.cited_change import reread_reading

    ruled(split_row, own)
    common = dict(subject=SUBJECT, benchmark_id=FACET.split(":", 1)[1], reading=READING,
                  source_id="board")
    assert reread_reading(readers=pair(49.0), **common).outcome == "current"
    own.page = board(score="53.0")
    out = reread_reading(readers=pair(53.0), **common)
    assert out.outcome == "changed" and out.record["value"] == 53.0


def test_the_sweep_lists_a_ruled_reading_whose_region_changed(split_row, own):
    from scripts import evidence_reread as sweep

    ruled(split_row, own)
    terms = {"cursor.com": "cite-only"}
    report = sweep.Report(observed_at=TODAY, dry_run=True, cap=0)
    sweep.ruled_reading_rereads(split_row.root, terms, report, pacer=sweep.Pacer(0))
    assert report.ruled_readings == {"current": 1} and report.cited_change_rereads == []
    own.page = board(score="53.0")
    report = sweep.Report(observed_at=TODAY, dry_run=True, cap=0)
    sweep.ruled_reading_rereads(split_row.root, terms, report, pacer=sweep.Pacer(0))
    assert report.ruled_readings == {"changed": 1} and len(report.cited_change_rereads) == 1
    assert report.to_dict()["ruled_readings"]["changed"] == 1
    assert card_row(split_row)["score"] == 49.0      # the sweep changes no card


# --- the build ------------------------------------------------------------------------------------

MID, BENCH = "lab/alpha", "bench_x"
BFACET = f"benchmark:{BENCH}"
BOARD = "https://www.perplexity.ai/pro"
SETTINGS = {"model_id_as_evaluated": MID, "effort": None, "harness": None}
REGION, PAGE, TEXT, PROMPT = "c" * 64, "3" * 64, "a" * 64, "4" * 64
AT = "2026-10-10T09:00:00+00:00"
EPOCH = f"{reading_epoch(SETTINGS)}{BOARD_MARK}{REGION}"
BUILD_DAY = datetime(2026, 10, 19).date()


def attempt(epoch=EPOCH, *, values=(51.2, 49.0), at=AT, region=REGION, subject=MID):
    entry = {"subject": subject, "facet": BFACET, "epoch": epoch, "url": BOARD, "complete": True,
             "agreed": values[0] == values[1],
             "agreed_value": values[0] if values[0] == values[1] else None, "harness": True,
             "page_sha256": PAGE, "text_sha256": TEXT, "prompt_sha256": PROMPT, "at": at,
             "readers": [{"reader_id": "a", "family": "openai", "version": "1",
                          "value": values[0]},
                         {"reader_id": "b", "family": "anthropic", "version": "1",
                          "value": values[1]}]}
    if region is not None:
        entry["board_region_sha256"] = region
    return entry


def ruling(split_attempt, **kw):
    line = {"subject": MID, "facet": BFACET, "epoch": split_attempt["epoch"], "value": 49.0,
            "state": "known", "ruled_by": "jamie", "ruled_at": "2026-10-11",
            "ticket": "MODEL-569", "source_ids": ["src-cite"],
            "resolves": [attempt_id(split_attempt)], "basis": BASIS}
    line.update(kw)
    return line


def ruled_evidence(line, *, score=None, eid=f"{MID}#{BENCH}#ruled", at=AT):
    from tests.snapshot_records import evidence

    row = evidence(MID, BENCH, line["value"] if score is None else score, eid=eid, outcome=None,
                   source="src-cite", source_url=BOARD)
    row["sources"][0].update(snapshot_ref=f"sha256:{PAGE}", retrieved_at=at)
    row["derivation"] = {"owner_ruling": copy.deepcopy(line)}
    return row


def build(row, lines, attempts, log=(), as_of=BUILD_DAY):
    from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot

    from tests.snapshot_records import SOURCES, model

    built = build_snapshot(SnapshotInputs(
        models=[model(MID)], evidence=[row], sources={**SOURCES, "src-cite": BOARD},
        verifications=list(log), owner_rulings=list(lines), cited_attempts=list(attempts),
        benchmark_metadata={BENCH: {"min_score": 0, "max_score": 100, "unit": "percent"}}),
        as_of=as_of)
    return load_built_snapshot(built).evidence(MID, BENCH)


def scores(index):
    return [row.value for row in index]


def test_the_build_admits_a_ruled_row_on_its_line():
    split_attempt = attempt()
    line = ruling(split_attempt)
    assert scores(build(ruled_evidence(line), [line], [split_attempt])) == [49.0]


def bypasses():
    split_attempt = attempt()
    line = ruling(split_attempt)
    row = ruled_evidence(line)
    other_split = attempt(subject="lab/beta")
    yield "no line", row, [], [split_attempt]
    yield "forged line", row, [{**line, "ruled_by": "claude"}], [split_attempt]
    forged = ruled_evidence({**line, "value": 60.0})
    yield "block not the line", forged, [line], [split_attempt]
    yield "another value", ruled_evidence(line, score=60.0), [line], [split_attempt]
    other = ruling(other_split, subject="lab/beta")
    yield "another row's line", ruled_evidence(other), [other], [other_split]
    agreed = attempt(values=(49.0, 49.0))
    yield "no disagreement", ruled_evidence(ruling(agreed)), [ruling(agreed)], [agreed]
    yield "unlogged attempt", row, [line], []
    settings_split = attempt(reading_epoch(SETTINGS), region=None)
    yield "another epoch", row, [line], [settings_split]
    later = attempt(f"{reading_epoch(SETTINGS)}{BOARD_MARK}{'d' * 64}", values=(53.0, 53.0),
                    at="2026-10-12T09:00:00+00:00", region="d" * 64)
    yield "stale epoch", row, [line], [split_attempt, later]
    wrong_region = attempt(region="d" * 64)
    yield "region not the epoch's", ruled_evidence(ruling(wrong_region)), \
        [ruling(wrong_region)], [wrong_region]
    yield "future ruling", ruled_evidence(ruling(split_attempt, ruled_at="2026-10-20")), \
        [ruling(split_attempt, ruled_at="2026-10-20")], [split_attempt]
    moved = copy.deepcopy(row)
    moved["sources"][0]["snapshot_ref"] = "sha256:" + "5" * 64
    yield "another copy", moved, [line], [split_attempt]
    other_settings = copy.deepcopy(row)
    other_settings["effort"] = "low"
    yield "another setting", other_settings, [line], [split_attempt]
    reopened = attempt(f"{EPOCH}:reopen:{'d' * 64}", values=(53.0, 53.0),
                       at="2026-10-12T09:00:00+00:00", region="d" * 64)
    yield "superseded in a reopened epoch", row, [line], [split_attempt, reopened]


@pytest.mark.parametrize("case", list(bypasses()), ids=lambda c: c[0] if isinstance(c, tuple)
                         else None)
def test_the_build_keeps_out_a_ruled_row_whose_ruling_does_not_stand(case):
    _, row, lines, attempts = case
    assert build(row, lines, attempts) == ()
    # Kept out by the ruling test itself, the one the filer and the gate use.
    assert board_ruling.row_problem(row, MID, rulings=lines, attempts=attempts,
                                    sources={"src-cite": BOARD}, max_score=100,
                                    today=BUILD_DAY) is not None


def test_a_ruled_row_never_silently_drops_a_hold_on_its_earlier_id():
    """A ruled row's id changes with its score. A failed verdict on the id it had stays a
    ``held_row_missing`` refusal of the whole build; the ruling releases no verdict."""
    from decision.model import evidence_verification_value
    from decision.snapshot import SnapshotBuildError, SnapshotInputs, build_snapshot

    from tests.snapshot_records import SOURCES, model, verification

    split_attempt = attempt()
    line = ruling(split_attempt)
    old = ruled_evidence(line, score=46.6, eid=f"{MID}#{BENCH}#old")
    verdict = verification("evidence", old["id"], "mismatch", day="2026-10-01",
                           value=evidence_verification_value(old))
    inputs = SnapshotInputs(
        models=[model(MID)], evidence=[ruled_evidence(line)],
        sources={**SOURCES, "src-cite": BOARD}, verifications=[verdict], owner_rulings=[line],
        cited_attempts=[split_attempt], check_held_rows=True,
        benchmark_metadata={BENCH: {"min_score": 0, "max_score": 100, "unit": "percent"}})
    with pytest.raises(SnapshotBuildError, match="held_row_missing"):
        build_snapshot(inputs, as_of=BUILD_DAY)


def test_without_the_block_the_hand_edited_score_is_an_ordinary_row():
    """The ruling check is what keeps a forged block out: the same row with no block enters."""
    split_attempt = attempt()
    row = ruled_evidence({**ruling(split_attempt), "ruled_by": "claude"})
    assert build(row, [], [split_attempt]) == ()
    del row["derivation"]
    assert scores(build(row, [], [split_attempt])) == [49.0]


def test_the_build_keeps_out_a_held_ruled_row_and_never_drops_the_hold():
    from decision.model import evidence_verification_value

    from tests.snapshot_records import verification

    split_attempt = attempt()
    line = ruling(split_attempt)
    row = ruled_evidence(line)
    verdict = verification("evidence", row["id"], "mismatch", day="2026-10-01",
                           value=evidence_verification_value(row))
    assert build(row, [line], [split_attempt], log=[verdict]) == ()


def test_the_build_admits_a_second_ruling_only_in_a_reopened_epoch_of_a_valid_one():
    split_attempt = attempt()
    first = ruling(split_attempt)
    reopened_split = attempt(f"{EPOCH}:reopen:{'d' * 64}", values=(53.0, 52.0),
                             at="2026-10-12T09:00:00+00:00", region="d" * 64)
    second = ruling(reopened_split, value=53.0, ruled_at="2026-10-13")
    attempts = [split_attempt, reopened_split]
    later = "2026-10-12T09:00:00+00:00"
    assert scores(build(ruled_evidence(second, at=later), [first, second], attempts)) == [53.0]
    assert build(ruled_evidence(second, at=later), [second], attempts) == ()  # extends no ruling
    same = attempt(f"{EPOCH}:reopen:{REGION}", values=(53.0, 52.0),
                   at="2026-10-12T09:00:00+00:00", region=REGION)
    back = ruling(same, value=53.0, ruled_at="2026-10-13")
    assert build(ruled_evidence(back, at=later), [first, back],
                 [split_attempt, same]) == ()                                  # no change
    # Meanwhile the first ruling still stands: a split in its reopened epoch supersedes nothing.
    assert scores(build(ruled_evidence(first), [first], attempts)) == [49.0]


def test_the_build_and_the_filer_decide_with_one_helper():
    split_attempt = attempt()
    line = ruling(split_attempt)
    row = ruled_evidence(line)
    sources = {"src-cite": BOARD}
    assert board_ruling.row_problem(row, MID, rulings=[line], attempts=[split_attempt],
                                    sources=sources, max_score=100) is None
    assert board_ruling.row_problem(row, MID, rulings=[line], attempts=[split_attempt],
                                    sources=sources, max_score=40)[0] == "value_invalid"
    assert board_ruling.row_problem(row, MID, rulings=[line], attempts=[split_attempt],
                                    sources=sources, held=[object()])[0] == "quarantined"


def test_the_site_withholds_a_ruled_row_that_does_not_stand(split_row, own, monkeypatch):
    from decision.owner_ruling import read_ruling_inputs
    from pipeline.load import _ruled_row_withheld

    ruled(split_row, own)
    row = card_row(split_row)
    inputs = read_ruling_inputs(split_row.root)
    sources = {s["id"]: s["url"] for s in split_row.sources}
    assert not _ruled_row_withheld(split_row.root, row, SUBJECT, inputs, sources, None, None)
    forged = {**row, "score": 60.0}
    assert _ruled_row_withheld(split_row.root, forged, SUBJECT, inputs, sources, None, None)
