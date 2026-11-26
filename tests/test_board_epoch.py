"""A board row's epoch includes the board's cited region (MODEL-555, Jamie 2026-11-25).

An unchanged row (no cited change) used to be read in its settings epoch alone, so one split of
its readers blocked it for good. Its epoch now names the row's board region, from pages the gate
fetched itself. These are the bypass tests: the same page, or churn outside the cited region,
opens no epoch; a changed region opens one; bytes a caller supplies open none; a disagreement
still blocks inside its epoch; the epoch is the row's, not the chosen source's; an attempt with
no region hash holds the row where it is; a clearing after a genuine board update is not blocked
by an older board's split, and the build agrees. Every value here is synthetic.
"""

import json
from datetime import UTC, datetime

import pytest
from decision import cited_change as gate
from decision.cited_change import (
    BOARD_MARK,
    board_epoch,
    board_region_sha256,
    cited_reading,
    reading_epoch,
)
from decision.cited_reader import ATTEMPTS_FILE, sha256, text_sha256

from tests.test_cited_reading import (  # noqa: F401
    BENCH,
    READING,
    ROW_ID,
    SUBJECT,
    URL,
    Data,
    offline,
    pair,
)

FACET = "benchmark:" + BENCH
BASE = reading_epoch(READING)
URL2 = "https://cursor.com/cursorbench/agents"


def board(score="51.2", *, banner="", stamp="2026-11-01", script="a", rival="40.0", clock="09:15",
          rotating="Try the new agent", status="Live"):
    """A synthetic board page: the score table is the cited region; the rest is page furniture,
    rotating copy and clocks."""
    return (f"<html><head><script>build={script}</script></head><body>"
            f"<div class='cookie-banner'>{banner}</div>"
            f"<div class='announcement-bar'>{rotating}</div>"
            f"<div role='status'>{status}</div>"
            f"<p>Last updated: {stamp}</p><p>Board as of {clock}</p>"
            f"<table id='rows'><tr><td>Orbit 9 Max</td><td>{score}%</td></tr>"
            f"<tr><td>Rival 1</td><td>{rival}%</td></tr></table>"
            f"<footer>{banner}</footer></body></html>").encode()


def bare(score="51.2", *, rotating="Try the new agent", clock="09:15"):
    """A board with no table: its rows are its text."""
    return (f"<html><body><div class='hero-carousel'>{rotating}</div>"
            f"<p>Refreshed {clock}</p><div>Orbit 9 Max {score}%</div>"
            f"<div>Rival 1 40.0%</div></body></html>").encode()


@pytest.fixture
def data(tmp_path, monkeypatch):
    d = Data(tmp_path / "data", monkeypatch)
    d.row["id"] = ROW_ID
    d.write()
    return d


@pytest.fixture
def html_data(data):
    """The board source with an HTML recipe and a table region, as a curated board would be."""
    table = dict(id="rows", locator=dict(kind="css", value="table#rows"))
    data.sources[0].update(normaliser="html-default", cited_regions=[table])
    data.write()
    return data


@pytest.fixture
def two(data):
    """The row cites two pages of the board's owner."""
    data.sources.append(dict(id="board2", url=URL2, kind="benchmark_author", publisher="cursor",
                             fetch="http", normaliser="text-default",
                             cited_regions=[dict(id="rows", locator=dict(kind="page", value=""))]))
    data.row["sources"].append(dict(source_id="board2", snapshot_ref="sha256:" + "0" * 64,
                                    cited_regions=["rows"]))
    data.write()
    return data


class Board:
    """The gate's own transport, patched at the one function it calls (``_http_once``)."""

    def __init__(self, monkeypatch):
        self.pages = {URL: board(), URL2: board(score="60.0")}
        self.calls = 0
        monkeypatch.setattr(gate, "_http_once", self)

    @property
    def page(self):
        return self.pages[URL]

    @page.setter
    def page(self, value):
        self.pages[URL] = value

    def __call__(self, url):
        self.calls += 1
        page = self.pages.get(url)
        return (200, None, page) if page is not None else (503, None, b"")


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


def split(**kw):
    refused("readers_disagree", readers=pair(51.2, 49.0), **kw)


def row_region(data, pages):
    parts = [[s["source_id"], board_region_sha256(data.row, s["source_id"], src, pages[src["url"]])]
             for s in sorted(data.row["sources"], key=lambda s: s["source_id"])
             for src in data.sources if src["id"] == s["source_id"]]
    return sha256(json.dumps(parts, ensure_ascii=False, separators=(",", ":")))


# --- the epoch ------------------------------------------------------------------------------------


def test_an_unchanged_rows_epoch_names_its_board_region(html_data, own):
    split()
    [line] = html_data.log()
    region = row_region(html_data, own.pages)
    assert line["epoch"] == f"{BASE}{BOARD_MARK}{region}" == reading_epoch(READING, board=region)
    assert line["region_sha256"] == region and len(region) == 64


def test_a_row_with_a_cited_change_keeps_its_reread_epoch():
    row = {"derivation": {"cited_change": {"text_sha256": "f" * 64}}}
    assert reading_epoch(READING, row, board="e" * 64) == f"{BASE}:reread:{'f' * 64}"


def test_re_reading_the_same_page_opens_no_new_epoch(html_data, own):
    split()
    refused("prior_attempt_disagreed")
    assert len(html_data.log()) == 1


CHURN = [dict(banner="We use cookies"), dict(stamp="2026-11-24"), dict(script="b"),
         dict(clock="17:42"), dict(clock="5:42 pm"), dict(rotating="Meet the new model"),
         dict(status="Updating"),
         dict(banner="Now hiring", stamp="2026-11-25", script="c", clock="23:59",
              rotating="Week 48", status="Paused")]


@pytest.mark.parametrize("churn", CHURN)
def test_churn_outside_the_cited_region_opens_no_epoch(html_data, own, churn):
    split()
    own.page = board(**churn)
    refused("prior_attempt_disagreed")
    assert len(html_data.log()) == 1


@pytest.mark.parametrize("churn", CHURN)
def test_a_whole_page_text_recipe_hashes_the_board_rows_only(data, own, churn):
    # the fixture's board source is text-default with a whole-page region
    split()
    own.page = board(**churn)
    assert text_sha256(own.page) != text_sha256(board()) or "script" in churn
    refused("prior_attempt_disagreed")
    assert len(data.log()) == 1


def test_a_tableless_html_board_is_refused_never_opened(data, own):
    own.page = bare()
    refused("page_unreadable")
    assert data.log() == []


PIPE = ("Board at {clock}\nThe leaderboard ranks models by score.\n\n"
        "| Model | Score |\n|---|---|\n| Orbit 9 Max | {score}% |\n| Rival 1 | 40.0% |\n\n"
        "{prose}\n")


def pipe(score="51.2", clock="09:15", prose="Runs use the max effort."):
    return PIPE.format(score=score, clock=clock, prose=prose).encode()


def test_a_plain_text_board_hashes_its_table_rows_never_its_prose(data, own):
    own.page = pipe()
    split()
    own.page = pipe(clock="17:42", prose="New: an agent track.")
    refused("prior_attempt_disagreed")
    own.page = pipe(score="53.0")
    assert read(readers=pair(53.0)).changed


@pytest.mark.parametrize("page", [
    b"Board at 09:15\nOrbit 9 Max 51.2%\nRival 1 40.0%\n",               # prose only
    b"| Model | Score |\n|---|---|\n",                                       # header only
    b"| Model | Score |\n|---|---|\n|  |  |\n",                             # empty body
])
def test_a_plain_text_board_without_body_rows_is_refused(data, own, page):
    own.page = page
    refused("page_unreadable")
    assert data.log() == []


@pytest.mark.parametrize("page", [
    b"<html><body><table id='rows'><tr><th>Model</th><th>Score</th></tr></table></body></html>",
    b"<html><body><table id='rows'><thead><tr><th>Model</th><th>Score</th></tr></thead>"
    b"<tbody><tr><td></td><td> </td></tr></tbody></table></body></html>",
    b"<html><body><div role='table' id='rows'><div role='row'><span role='columnheader'>Model"
    b"</span></div></div></body></html>",
])
def test_a_header_only_skeleton_is_refused(html_data, own, page):
    split()
    own.page = page
    refused("page_unreadable")
    assert len(html_data.log()) == 1


@pytest.mark.parametrize("split_markup", [
    b"<td>5<span>1.2</span>%</td>", b"<td><span>51</span><span>.2</span>%</td>",
    b"<td>\n  51.2%\n</td>", b"<td><b>51.2</b> %</td>",
])
def test_markup_that_splits_a_cell_does_not_open_an_epoch(html_data, own, split_markup):
    split()
    own.page = board().replace(b"<td>51.2%</td>", split_markup)
    assert own.page != board()
    refused("prior_attempt_disagreed")
    assert len(html_data.log()) == 1


def test_the_normalisers_own_cell_text_is_unchanged():
    from decision.normalise import NORMALISERS, normalise_document

    doc = normalise_document(b"<table><tr><td>5<span>1.2</span></td></tr></table>",
                             NORMALISERS["html-default"])
    assert doc.text == "5 1.2"


def test_a_changed_cited_region_opens_a_new_epoch_where_two_readers_settle_it(html_data, own):
    refused("readers_disagree", readers=pair(None, 51.2))
    own.page = board(score="53.0")
    out = read(readers=pair(53.0))
    assert out.changed and out.record["value"] == 53.0
    first, second = epochs(html_data)
    assert first != second and second.startswith(BASE + BOARD_MARK)


def test_a_change_elsewhere_in_the_region_opens_one_too(html_data, own):
    split()
    own.page = board(rival="41.0")
    assert read().changed


def test_a_disagreement_still_blocks_inside_its_epoch_and_on_return(html_data, own):
    split()
    own.page = board(score="53.0")
    refused("readers_disagree", readers=pair(53.0, 54.0))
    refused("prior_attempt_disagreed", readers=pair(53.0))
    own.page = board(score="51.2", banner="back again")  # the first region again
    refused("prior_attempt_disagreed")
    assert len(html_data.log()) == 2


def _miss(data, own, change):
    split()
    change()
    refused("page_unreadable")                      # no region: refused, nothing opens
    refused("page_unreadable", readers=pair(53.0))
    assert len(data.log()) == 1


def test_a_source_with_no_registered_region_is_refused(html_data, own):
    def change():
        html_data.sources[0].pop("cited_regions")
        html_data.write()
        own.page = board(score="53.0")
    _miss(html_data, own, change)


def test_a_renamed_table_id_is_refused_not_hashed_into_an_epoch(html_data, own):
    def change():
        own.page = board(score="53.0").replace(b"id='rows'", b"id='rows-v2'")
    _miss(html_data, own, change)


@pytest.mark.parametrize("placeholder", [
    b"<html><body><table id='rows'><tr><td></td><td></td></tr></table></body></html>",
    b"<html><body><table id='rows'></table><p>Loading 53.0%</p></body></html>",
    b"<html><body><div id='app'>Loading the board</div></body></html>",
])
def test_a_placeholder_is_refused_not_hashed_into_an_epoch(html_data, own, placeholder):
    def change():
        own.page = placeholder
    _miss(html_data, own, change)


def _framed(caption="Week 47", note="Scores are percentages", score="51.2"):
    return (f"<html><body><div id='board'><p>{note}</p><table id='rows'>"
            f"<caption>{caption}</caption><thead><tr><th>Model</th><th>Score</th></tr></thead>"
            f"<tbody><tr><td>Orbit 9 Max</td><td>{score}%</td></tr></tbody></table>"
            f"<p>{note}</p></div></body></html>").encode()


@pytest.mark.parametrize("locator", ["table#rows", "div#board"])
def test_only_cell_contents_are_hashed_not_captions_or_surrounding_copy(data, own, locator):
    data.sources[0].update(normaliser="html-default", cited_regions=[
        dict(id="rows", locator=dict(kind="css", value=locator))])
    data.write()
    own.page = _framed()
    split()
    own.page = _framed(caption="Week 48", note="All runs at max effort")
    refused("prior_attempt_disagreed")
    assert len(data.log()) == 1
    own.page = _framed(score="53.0")              # a body cell
    assert read(readers=pair(53.0)).changed


def test_a_changed_header_cell_opens_an_epoch(data, own):
    own.page = _framed()
    split()
    own.page = _framed().replace(b"<th>Score</th>", b"<th>Score (v2)</th>")
    assert read().changed


# --- caller-supplied bytes ------------------------------------------------------------------------


def test_bytes_a_caller_supplies_cannot_open_an_epoch(html_data, own):
    split()
    # a caller's transport reads in the settings epoch, where the board epoch's split counts
    refused("prior_attempt_disagreed", request=serve(board(score="53.0")))
    assert own.calls == 1 and len(html_data.log()) == 1


def test_a_caller_transport_attempt_records_no_region_and_holds_the_row(html_data, own):
    split(request=serve(board()))
    [line] = html_data.log()
    assert line["epoch"] == BASE and "region_sha256" not in line
    refused("prior_attempt_disagreed", request=serve(board(score="53.0")))
    refused("prior_attempt_disagreed")              # the gate's own fetch of the same board
    own.page = board(score="53.0")
    refused("prior_attempt_disagreed")              # nor a changed one: its region is unknown


def test_board_epoch_never_opens_without_a_region():
    assert board_epoch(base=BASE, lines=[], region=None) == BASE
    assert board_epoch(base=BASE, lines=[], region="x") == BASE
    assert board_epoch(base=BASE, lines=[], region="a" * 64) == f"{BASE}{BOARD_MARK}{'a' * 64}"


# --- the epoch is the row's, across its sources ---------------------------------------------------


def test_switching_sources_does_not_select_a_fresh_epoch(two, own):
    split()
    refused("prior_attempt_disagreed", source_id="board2")
    assert len(two.log()) == 1


def test_a_split_under_either_source_counts_for_the_other(two, own):
    split(source_id="board2")
    refused("prior_attempt_disagreed")
    assert len(two.log()) == 1


def test_a_change_on_any_cited_source_opens_the_rows_new_epoch(two, own):
    split()
    own.pages[URL2] = board(score="61.0")
    assert read().changed
    first, second = epochs(two)
    assert first != second


def test_an_unreadable_second_source_holds_the_row(two, own):
    split()
    del own.pages[URL2]                            # the other cited page cannot be read
    own.page = board(score="53.0")
    refused("page_unreadable")
    assert len(two.log()) == 1


@pytest.mark.parametrize("change", ["ineligible", "unregistered"])
def test_a_source_whose_eligibility_changes_holds_the_row(two, own, change):
    split()
    if change == "ineligible":
        two.sources[-1]["publisher"] = "acme"         # no longer the board owner's page
    else:
        two.sources.pop()                           # no longer in the source registry
    two.write()
    own.page = board(score="53.0")
    out = read(readers=pair(53.0))
    assert out.outcome == "refused" and out.reason in {"not_first_party", "registry_lookup_failed"}
    assert len(two.log()) == 1
    if change == "ineligible":
        two.sources[-1]["publisher"] = "cursor"       # eligible again: the same epoch as before
        two.write()
        own.page = board()
        refused("prior_attempt_disagreed")


# --- attempts logged before region hashes fail closed --------------------------------------------


def legacy(data, page, *, text=True):
    """A split logged before region hashes: no ``region_sha256``."""
    line = {"subject": SUBJECT, "facet": FACET, "url": URL, "epoch": BASE,
            "page_sha256": sha256(page), "prompt_sha256": "0" * 64,
            "at": "2026-11-02T00:00:00+00:00", "complete": True, "harness": True,
            "agreed": False, "agreed_value": None,
            "readers": [{"reader_id": "a", "family": "anthropic", "version": "1", "value": None},
                        {"reader_id": "b", "family": "mistral", "version": "1", "value": 47.3}]}
    if text:
        line["text_sha256"] = text_sha256(page)
    path = data.root / ATTEMPTS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        fh.write(json.dumps(line) + "\n")


@pytest.mark.parametrize("text", [True, False])
def test_a_legacy_split_keeps_blocking_whatever_the_board_shows(html_data, own, text):
    legacy(html_data, board(score="47.3"), text=text)
    refused("prior_attempt_disagreed")              # a changed region
    own.page = board(score="47.3", banner="x", clock="12:00")
    refused("prior_attempt_disagreed")              # a change outside it
    own.page = board(score="47.3")
    refused("prior_attempt_disagreed")              # the same page
    assert len(html_data.log()) == 1


# --- a clearing after a genuine board update ------------------------------------------------------


def _build_problem(data, entry):
    """The build's own check of a clearing line (``quarantine_clearing.line_problem``)."""
    from decision.quarantine_clearing import (
        QUEUE_FILE,
        AttemptLog,
        line_problem,
        queue_history,
        reading_settings,
    )

    verdict = json.loads((data.root / "verification/log.jsonl").read_text().splitlines()[-1])
    history = queue_history(data.root / QUEUE_FILE, {ROW_ID}).get(ROW_ID, [])
    problem, _ = line_problem(entry, verdict=verdict, subject=SUBJECT, facet=FACET,
                              ids=lambda rid: rid == ROW_ID,
                              log=AttemptLog.read(data.root / ATTEMPTS_FILE), first=BASE,
                              history=history, cutoff=datetime.now(UTC).date(),
                              settings=reading_settings({**data.row, **READING}))
    return problem


def test_an_old_boards_split_does_not_block_a_clearing_in_the_new_epoch(html_data, own):
    from tests.test_quarantine_clearing import board_verdict

    split()                                         # under the old board region
    board_verdict(html_data)                        # then the row is held
    refused("prior_attempt_disagreed", clear_quarantine=True)   # the same board: still blocked
    own.page = board(score="53.0")                  # a genuine board update
    out = read(readers=pair(53.0), clear_quarantine=True)
    assert out.changed and out.record["value"] == 53.0
    [entry] = out.record["clearings"]
    new = epochs(html_data)[-1]
    assert entry["epoch"] == new and ":clear:" in new and BOARD_MARK in new
    block = out.record["derivation"]["cited_change"]
    assert block["previous_epoch"].startswith(BASE + BOARD_MARK)
    assert _build_problem(html_data, entry) == ""   # the build agrees


def test_the_build_takes_a_board_base_only_from_an_agreement_that_read_that_region():
    from decision.quarantine_clearing import _board_base, reading_settings

    settings = reading_settings({**READING})
    region = "a" * 64
    board_base = f"{BASE}{BOARD_MARK}{region}"
    read_it = {"region_sha256": region}
    assert _board_base(board_base, BASE, BASE, settings, read_it)
    assert not _board_base(board_base, BASE, BASE, settings, {"region_sha256": "b" * 64})
    assert not _board_base(board_base, BASE, BASE, settings, {})
    assert not _board_base(board_base, BASE, BASE, None, read_it)          # not a reading
    assert not _board_base(board_base, "reread:" + "c" * 64, BASE, settings, read_it)
    assert not _board_base(f"{BASE}{BOARD_MARK}short", BASE, BASE, settings, read_it)
