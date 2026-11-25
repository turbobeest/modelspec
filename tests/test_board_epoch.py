"""A board row's epoch includes the board's cited region (MODEL-555, Jamie 2026-11-25).

An unchanged row (no cited change) used to be read in its settings epoch alone, so one split of
its readers blocked it for good. Its epoch now names the hash of the board's cited region, from
a page the gate fetched itself. These are the bypass tests: the same page, or churn outside the
cited region, opens no epoch; a changed region opens one; bytes a caller supplies open none; a
disagreement still blocks inside its epoch.
"""

import json

import pytest
import yaml

from decision import cited_change as gate
from decision.cited_change import (
    BOARD_MARK, board_epoch, board_region_sha256, cited_reading, reading_epoch,
)
from decision.cited_reader import ATTEMPTS_FILE, sha256, text_sha256
from tests.test_cited_reading import BENCH, READING, SUBJECT, Data, offline, pair  # noqa: F401

FACET = "benchmark:" + BENCH
BASE = reading_epoch(READING)


def board(score="51.2", *, banner="", stamp="2026-11-01", script="a", rival="40.0"):
    """A synthetic board page: the score table is the cited region; the rest is page furniture."""
    return (f"<html><head><script>build={script}</script></head><body>"
            f"<div class='cookie-banner'>{banner}</div>"
            f"<p>Last updated: {stamp}</p>"
            f"<table id='rows'><tr><td>Orbit 9 Max</td><td>{score}%</td></tr>"
            f"<tr><td>Rival 1</td><td>{rival}%</td></tr></table>"
            f"<footer>{banner}</footer></body></html>").encode()


@pytest.fixture
def data(tmp_path, monkeypatch):
    return Data(tmp_path / "data", monkeypatch)


@pytest.fixture
def html_data(data):
    """The board source with an HTML recipe and a table region, as a curated board would be."""
    data.sources[0].update(normaliser="html-default",
                           cited_regions=[dict(id="rows", locator=dict(kind="css", value="table#rows"))])
    data.write()
    return data


class Board:
    """The gate's own transport, patched at the one function it calls (``_http_once``)."""

    def __init__(self, monkeypatch):
        self.page = board()
        self.calls = 0
        monkeypatch.setattr(gate, "_http_once", self)

    def __call__(self, url):
        self.calls += 1
        return 200, None, self.page


@pytest.fixture
def own(monkeypatch):
    return Board(monkeypatch)


def read(**kw):
    args = dict(subject=SUBJECT, benchmark_id=BENCH, reading=READING, source_id="board",
                readers=pair())
    args.update(kw)
    return cited_reading(**args)


def refused(reason, **kw):
    out = read(**kw)
    assert out.outcome == "refused" and out.reason == reason, (out.reason, out.detail)
    return out


def epochs(data):
    return [line["epoch"] for line in data.log()]


def serve(page):
    return lambda url: (200, None, page)


# --- the epoch ------------------------------------------------------------------------------------


def test_an_unchanged_rows_epoch_names_the_boards_cited_region(html_data, own):
    refused("readers_disagree", readers=pair(51.2, 49.0))
    [line] = html_data.log()
    region = board_region_sha256(html_data.row, "board", html_data.sources[0], own.page)
    assert line["epoch"] == f"{BASE}{BOARD_MARK}{region}" == reading_epoch(READING, board=region)
    assert line["region_sha256"] == region and len(region) == 64


def test_a_row_with_a_cited_change_keeps_its_reread_epoch():
    row = {"derivation": {"cited_change": {"text_sha256": "f" * 64}}}
    assert reading_epoch(READING, row, board="e" * 64) == f"{BASE}:reread:{'f' * 64}"


def test_re_reading_the_same_page_opens_no_new_epoch(html_data, own):
    refused("readers_disagree", readers=pair(51.2, 49.0))
    refused("prior_attempt_disagreed")
    assert len(html_data.log()) == 1


@pytest.mark.parametrize("churn", [
    dict(banner="We use cookies"), dict(stamp="2026-11-24"), dict(script="b"),
    dict(banner="Now hiring", stamp="2026-11-25", script="c"),
])
def test_churn_outside_the_cited_region_opens_no_epoch(html_data, own, churn):
    refused("readers_disagree", readers=pair(51.2, 49.0))
    own.page = board(**churn)
    assert text_sha256(own.page) != text_sha256(board()) or "script" in churn
    refused("prior_attempt_disagreed")
    assert len(html_data.log()) == 1


def test_update_times_and_script_churn_open_no_epoch_with_a_text_recipe(data, own):
    # the fixture's board source is text-default with a whole-page region
    refused("readers_disagree", readers=pair(51.2, 49.0))
    own.page = board(stamp="2026-11-25", script="zz")
    refused("prior_attempt_disagreed")
    assert len(data.log()) == 1


def test_a_changed_cited_region_opens_a_new_epoch_where_two_readers_settle_it(html_data, own):
    refused("readers_disagree", readers=pair(None, 51.2))
    own.page = board(score="53.0")
    out = read(readers=pair(53.0))
    assert out.changed and out.record["value"] == 53.0
    first, second = epochs(html_data)
    assert first != second and second.startswith(BASE + BOARD_MARK)


def test_a_change_elsewhere_in_the_region_opens_one_too(html_data, own):
    refused("readers_disagree", readers=pair(51.2, 49.0))
    own.page = board(rival="41.0")
    assert read().changed


def test_a_disagreement_still_blocks_inside_its_epoch_and_on_return(html_data, own):
    refused("readers_disagree", readers=pair(51.2, 49.0))
    own.page = board(score="53.0")
    refused("readers_disagree", readers=pair(53.0, 54.0))
    refused("prior_attempt_disagreed", readers=pair(53.0))
    own.page = board(score="51.2", banner="back again")  # the first region again
    refused("prior_attempt_disagreed")
    assert len(html_data.log()) == 2


def test_an_unreadable_region_opens_no_epoch(data, own):
    data.sources[0].pop("cited_regions")
    data.write()
    refused("readers_disagree", readers=pair(51.2, 49.0))
    assert epochs(data) == [BASE]
    own.page = board(score="53.0")
    refused("prior_attempt_disagreed")


# --- caller-supplied bytes -------------------------------------------------------------------------


def test_bytes_a_caller_supplies_cannot_open_an_epoch(html_data, own):
    refused("readers_disagree", readers=pair(51.2, 49.0))
    # a caller's transport reads in the settings epoch, where the board epoch's split counts
    refused("prior_attempt_disagreed", request=serve(board(score="53.0")))
    assert own.calls == 1 and len(html_data.log()) == 1


def test_a_caller_transport_split_still_blocks_its_own_page_once_the_gate_reads_it(html_data, own):
    refused("readers_disagree", readers=pair(51.2, 49.0), request=serve(board()))
    [line] = html_data.log()
    assert line["epoch"] == BASE and "region_sha256" in line
    refused("prior_attempt_disagreed", request=serve(board(score="53.0")))
    refused("prior_attempt_disagreed")              # the gate's own fetch of the same board
    own.page = board(score="53.0")
    assert read(readers=pair(53.0)).changed       # a changed region, fetched by the gate


def test_board_epoch_never_opens_without_a_region():
    assert board_epoch(base=BASE, lines=[], url="u", page_bytes=b"x", region=None) == BASE


# --- attempts logged before region hashes -------------------------------------------------------


def legacy(data, page, *, text=True, url="https://cursor.com/cursorbench"):
    """A split logged before region hashes (MODEL-482 era): no ``region_sha256``."""
    line = {"subject": SUBJECT, "facet": FACET, "url": url, "epoch": BASE,
            "page_sha256": sha256(page), "prompt_sha256": "0" * 64,
            "at": "2026-11-23T00:14:57+00:00", "complete": True, "harness": True,
            "agreed": False, "agreed_value": None,
            "readers": [{"reader_id": "a", "family": "anthropic", "version": "1", "value": None},
                        {"reader_id": "b", "family": "mistral", "version": "1", "value": 47.3}]}
    if text:
        line["text_sha256"] = text_sha256(page)
    path = data.root / ATTEMPTS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        fh.write(json.dumps(line) + "\n")


def link_by_block(data, page):
    """Another card's cited change on the same board: its block records the page's two hashes."""
    row = {"benchmark_id": BENCH, "model_id_as_evaluated": "Rival 1", "effort": None,
           "harness": None, "score": 40.0, "sources": [{"source_id": "board"}],
           "derivation": {"cited_change": {"url": "https://cursor.com/cursorbench",
                                           "sha256": sha256(page),
                                           "text_sha256": text_sha256(page)}}}
    card = yaml.safe_dump({"display_name": "Rival 1", "benchmarks": {"evidence": [row]}})
    (data.root / "models/acme/rival-1.md").write_text(f"---\n{card}---\n")


def test_a_legacy_split_blocks_the_page_it_read(html_data, own):
    legacy(html_data, own.page)
    refused("prior_attempt_disagreed")


def test_a_legacy_split_on_a_page_whose_text_changed_opens_a_board_epoch(html_data, own):
    legacy(html_data, board(score="47.3"))
    out = read()
    assert out.changed and epochs(html_data)[-1].startswith(BASE + BOARD_MARK)


def test_a_legacy_split_with_no_text_hash_is_named_through_a_recorded_block(html_data, own):
    old = board(score="47.3")
    legacy(html_data, old, text=False)
    refused("prior_attempt_disagreed")              # its page cannot be named: nothing opens
    link_by_block(html_data, old)
    assert read().changed                           # the block names it; the text changed


def test_a_legacy_split_named_as_this_text_still_blocks(html_data, own):
    legacy(html_data, own.page, text=False)
    link_by_block(html_data, own.page)
    own.page = own.page.replace(b"build=a", b"build=q")   # new bytes, the same visible text
    refused("prior_attempt_disagreed")


def test_a_board_epochs_split_still_blocks_when_the_row_falls_back_to_its_settings_epoch(
        html_data, own):
    refused("readers_disagree", readers=pair(51.2, 49.0))
    html_data.sources[0].pop("cited_regions")       # no region can be selected any more
    html_data.write()
    own.page = board(score="53.0")
    refused("prior_attempt_disagreed")
    assert len(html_data.log()) == 1
