"""MODEL-562: owner-ruled facts on the rolling re-read; a changed page reopens rule 15.

Synthetic data only: the planted offering of ``tests.test_cited_offering`` on a cite-only host,
real disagreements and agreements through the gate with stub readers, and stub HTTP.
"""

import json
import socket
from datetime import date

import pytest
import yaml

from decision.cited_change import fact_epoch
from decision.cited_reader import text_sha256
from decision.owner_ruling import RULINGS_FILE, has_ruling
from decision.ruling_reread import (
    FIELDS, RECORD_FILE, epoch_for_page, reopen_epoch, ruled_facts, ruled_texts,
)
from scripts import cited_offering as writer
from scripts import evidence_reread as script
from tests.test_cited_offering import (
    FACT_ID, HEADER, PAGE, SUBJECT, URL, Data, pair, refused, retention, serve,
)
from tests.test_owner_ruling import RETENTION, TODAY, attempts, disagree, file, offering_fact

DAY = date(2026, 12, 1)
CHANGED = PAGE.replace(b"30 days", b"45 days")
CHURNED = PAGE.replace(b"<html>", b"<html><script>var nonce=7;</script>")
TARGET = f"{SUBJECT}#{RETENTION}"


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", lambda *a: pytest.fail("Network attempted"))


@pytest.fixture
def data(tmp_path, monkeypatch):
    return Data(tmp_path / "data", monkeypatch)


@pytest.fixture
def ruled(data):
    """A real ruling: two readers disagreed on the page, and the owner ruled 30 days."""
    disagree()
    file(data)
    assert has_ruling(offering_fact(data)) and fact_epoch(offering_fact(data)) == "initial"
    return data


def sweep(data, body, *, dry_run=False):
    """One ruled-fact re-read with ``body`` served for the ruled page."""
    request = serve({URL: body})
    report = script.Report(DAY.isoformat(), dry_run)
    script.ruled_fact_rereads(data.root, script.load_terms(data.root), report, request=request,
                              pacer=script.Pacer(0, sleep=lambda s: None), observed_at=DAY,
                              dry_run=dry_run)
    report.calls = request.calls
    return report


def records(data):
    path = data.root / RECORD_FILE
    return [json.loads(x) for x in path.read_text().splitlines()] if path.is_file() else []


def outcome(report):
    return {k: n for k, n in report.to_dict()["ruled"].items() if n}


# --- an unchanged page leaves the ruled fact alone -----------------------------------------------


def test_an_unchanged_page_keeps_the_ruled_value_and_asks_no_reader(ruled):
    before = len(attempts(ruled))
    for body in (PAGE, CHURNED):  # byte churn is no change: the text hash is compared
        report = sweep(ruled, body)
        assert report.ruled_facts_checked == 1 and outcome(report) == {"current": 1}
        assert report.calls == [URL]
    assert records(ruled) == [] and not (ruled.root / RECORD_FILE).exists()
    assert len(attempts(ruled)) == before, "no reader was asked"
    assert offering_fact(ruled)["value"] == 30


def test_a_ruling_is_never_superseded_inside_its_own_epoch(ruled):
    """Two agreeing readers on the ruled page, or on its churned bytes, change nothing."""
    before = len(attempts(ruled))
    for body in (PAGE, CHURNED):
        refused(retention(readers=pair(45), request=serve({URL: body})), "prior_attempt_disagreed")
        refused(retention(readers=pair(30), request=serve({URL: body})), "prior_attempt_disagreed")
    assert len(attempts(ruled)) == before and offering_fact(ruled)["value"] == 30
    # the re-read does not move the fact either: it records nothing for an unchanged page
    sweep(ruled, PAGE)
    refused(retention(readers=pair(45), request=serve()), "prior_attempt_disagreed")


# --- a changed page reopens the fact -------------------------------------------------------------


def test_a_changed_page_is_recorded_once_and_reopens_the_fact(ruled):
    report = sweep(ruled, CHANGED, dry_run=True)
    assert outcome(report) == {"reopened": 1} and records(ruled) == [], "a dry run writes nothing"
    report = sweep(ruled, CHANGED)
    assert outcome(report) == {"reopened": 1}
    [line] = records(ruled)
    assert set(line) == set(FIELDS)
    assert line["target"] == TARGET and line["source_id"] == "data"
    assert line["text_sha256"] == text_sha256(CHANGED)
    assert line["epoch"] == reopen_epoch("initial", text_sha256(CHANGED))
    assert line["opened_on"] == DAY.isoformat()
    # the next run sees the same epoch open: no second line
    assert outcome(sweep(ruled, CHANGED)) == {"open": 1} and len(records(ruled)) == 1
    # the ruled value stands until two readers supersede it
    assert offering_fact(ruled)["value"] == 30 and has_ruling(offering_fact(ruled))


def test_two_agreeing_readers_supersede_a_ruling_on_a_changed_page(ruled):
    out = retention(readers=pair(45), request=serve({URL: CHANGED}))
    assert out.changed, (out.reason, out.detail)
    assert attempts(ruled)[-1]["epoch"] == reopen_epoch("initial", text_sha256(CHANGED))
    writer.apply(out, data_dir=ruled.root)
    fact = offering_fact(ruled)
    assert (fact["value"], fact["state"]) == (45, "known") and not has_ruling(fact)
    # the new fact is in the epoch its own block names, which holds no attempt yet
    assert fact_epoch(fact) == "reread:" + text_sha256(CHANGED)
    assert ruled_facts(ruled.root) == []


def test_agreement_on_the_ruled_value_after_a_change_keeps_the_ruling(ruled):
    refused(retention(readers=pair(30), request=serve({URL: CHANGED})), "value_unchanged")
    assert has_ruling(offering_fact(ruled)) and offering_fact(ruled)["value"] == 30


def test_a_disagreement_in_a_reopened_epoch_blocks_it_and_only_a_new_text_reopens(ruled):
    refused(retention(readers=pair(45, 60), request=serve({URL: CHANGED})), "readers_disagree")
    refused(retention(readers=pair(45), request=serve({URL: CHANGED})), "prior_attempt_disagreed")
    # back to the ruled text: the ruled epoch, where the first disagreement blocks
    refused(retention(readers=pair(45), request=serve({URL: PAGE})), "prior_attempt_disagreed")
    assert outcome(sweep(ruled, PAGE)) == {"current": 1}
    # a third text is a new epoch
    third = PAGE.replace(b"30 days", b"60 days")
    assert outcome(sweep(ruled, third)) == {"reopened": 1}
    out = retention(readers=pair(60), request=serve({URL: third}))
    assert out.changed and out.record["value"] == 60


# --- the epoch is the page's, never a caller's ----------------------------------------------------


def _inputs(data):
    rulings = [json.loads(x) for x in (data.root / RULINGS_FILE).read_text().splitlines()]
    return dict(rulings=rulings, attempts=attempts(data), sources={s["id"]: s["url"]
                                                                  for s in data.sources})


def test_only_a_standing_ruling_on_its_own_source_with_a_new_text_reopens(ruled):
    fact, kw = offering_fact(ruled), _inputs(ruled)
    new = text_sha256(CHANGED)
    assert epoch_for_page(fact, SUBJECT, source_id="data", url=URL, text_sha=new, **kw) \
        == reopen_epoch("initial", new)
    assert epoch_for_page(fact, SUBJECT, source_id="data", url=URL, text_sha=text_sha256(PAGE),
                          **kw) == "initial"
    # another source than the ruling's, or another URL for it, stays in the ruled epoch
    other = kw["sources"]["other"]
    assert epoch_for_page(fact, SUBJECT, source_id="other", url=other, text_sha=new, **kw) \
        == "initial"
    assert epoch_for_page(fact, SUBJECT, source_id="data", url=other, text_sha=new, **kw) \
        == "initial"
    # another subject's ruling is no ruling here
    assert epoch_for_page(fact, "openai/openai/gpt-x/eu/standard", source_id="data", url=URL,
                          text_sha=new, **kw) == "initial"
    # a block that is not the ruling line, or no ruling line at all, stands nothing
    forged = {**fact, "derivation": {"owner_ruling": {**fact["derivation"]["owner_ruling"],
                                                      "value": 45}}}
    assert epoch_for_page(forged, SUBJECT, source_id="data", url=URL, text_sha=new, **kw) \
        == "initial"
    assert epoch_for_page(fact, SUBJECT, source_id="data", url=URL, text_sha=new,
                          **{**kw, "rulings": []}) == "initial"
    # a plain fact is in its own epoch whatever its page
    plain = {k: v for k, v in fact.items() if k != "derivation"}
    assert epoch_for_page(plain, SUBJECT, source_id="data", url=URL, text_sha=new, **kw) \
        == "initial"


def test_an_attempt_with_no_text_hash_shows_no_change(ruled):
    kw = _inputs(ruled)
    legacy = [{k: v for k, v in a.items() if k != "text_sha256"} for a in kw["attempts"]]
    assert ruled_texts(legacy, subject=SUBJECT, facet=RETENTION, epoch="initial", url=URL) is None
    assert epoch_for_page(offering_fact(ruled), SUBJECT, source_id="data", url=URL,
                          text_sha=text_sha256(CHANGED), **{**kw, "attempts": legacy}) == "initial"


def test_an_invalid_ruling_is_counted_and_its_page_is_not_requested(ruled):
    (ruled.root / RULINGS_FILE).write_text("")
    report = sweep(ruled, CHANGED)
    assert outcome(report) == {"invalid": 1} and report.calls == [] and records(ruled) == []


def test_an_unclassed_source_host_is_never_requested(ruled):
    for source in ruled.sources:
        if source["id"] == "data":
            source["url"] = "https://unknown.example.org/your-data"
    (ruled.root / "registry/sources.yaml").write_text(
        yaml.safe_dump({"schema_version": 1, "sources": ruled.sources}))
    report = sweep(ruled, CHANGED)
    assert outcome(report) == {"unclassed": 1} and report.calls == []
    assert report.unclassed_hosts == {"unknown.example.org": 1}


def test_a_page_that_cannot_be_read_writes_nothing(ruled):
    request = lambda url: (503, None, b"")  # noqa: E731
    report = script.Report(DAY.isoformat(), False)
    script.ruled_fact_rereads(ruled.root, {}, report, request=request,
                              pacer=script.Pacer(0, sleep=lambda s: None), observed_at=DAY,
                              dry_run=False)
    assert outcome(report) == {"deferred": 1} and records(ruled) == []


# --- the report and the cited-change path --------------------------------------------------------


def test_the_report_is_counts_only_and_unchanged_with_no_ruled_fact(data, ruled, tmp_path):
    report = script.run(ruled.root, observed_at=DAY, dry_run=True, store_root=tmp_path / "cache",
                        request=lambda url: (200, None, CHANGED),
                        pacer=script.Pacer(0, sleep=lambda s: None))
    out = report.to_dict()
    assert out["ruled_facts_checked"] == 1 and out["ruled"]["reopened"] == 1
    assert all(isinstance(n, int) for n in out["ruled"].values())
    text = json.dumps(out) + script.render(report)
    assert SUBJECT not in text and text_sha256(CHANGED) not in text and "SECRET" not in text
    assert "Owner-ruled facts (1 checked)" in script.render(report)
    assert not [p for p in (tmp_path / "cache").rglob("*") if p.is_file()], "no page bytes kept"
    plain = script.Report("x", True)
    assert "ruled" not in plain.to_dict() and "Owner-ruled" not in script.render(plain)


def test_a_ruling_in_a_reread_epoch_is_read_against_the_page_it_ruled_on(data):
    """A ruled fact keeps the cited-change block of its epoch. The cited-change re-read would
    flag it every week (the block's text is not the page's); the ruled path compares the page
    with the text the disagreeing readers read, and finds it unchanged."""
    from scripts import file_owner_ruling as filer

    writer.apply(retention(), data_dir=data.root)  # a cited change: 30, from PAGE
    epoch = fact_epoch(offering_fact(data))
    assert epoch == "reread:" + text_sha256(PAGE)
    moved = PAGE.replace(b"30 days", b"90 days")
    refused(retention(readers=pair(90, 30), request=serve({URL: moved})), "readers_disagree")
    filer.apply(filer.plan(data_dir=data.root, subject=SUBJECT, facet=RETENTION, value=90,
                           state="known", ruled_by="jamie", ruled_at=TODAY, ticket="MODEL-1",
                           source_ids=["data"],
                           basis="day counts near retention wording: 1", epoch=epoch))
    fact = offering_fact(data)
    assert has_ruling(fact) and fact_epoch(fact) == epoch
    cited = script.Report("x", True)
    script.cited_change_rereads(data.root, {}, cited, request=serve({URL: moved}),
                                pacer=script.Pacer(0, sleep=lambda s: None), observed_at=DAY)
    assert cited.cited_change_rereads == [] and not cited.by_host
    report = sweep(data, moved)
    assert outcome(report) == {"current": 1}
    refused(retention(readers=pair(90), request=serve({URL: moved})), "prior_attempt_disagreed")
    later = PAGE.replace(b"30 days", b"120 days")
    assert outcome(sweep(data, later)) == {"reopened": 1}
    assert records(data)[0]["epoch"] == reopen_epoch(epoch, text_sha256(later))
    out = retention(readers=pair(120), request=serve({URL: later}))
    assert out.changed and out.record["value"] == 120


def test_a_cleared_fact_is_re_read_in_the_epoch_its_own_block_names(data):
    """MODEL-552 clearings: the cleared record carries a cited-change block naming its
    ``clearing_epoch``. It is re-read with the cited-change facts, against its own text, and
    a change is read in ``reread:<text>``, an epoch apart from the clearing's and its base's."""
    out = retention()
    block = out.record["derivation"]["cited_change"]
    block["previous_epoch"] = "initial"
    block["clearing_epoch"] = "initial:clear:" + "c" * 64
    writer.apply(out, data_dir=data.root)
    fact = offering_fact(data)
    assert fact_epoch(fact) not in {block["previous_epoch"], block["clearing_epoch"]}

    def cited(body):
        report = script.Report("x", True)
        script.cited_change_rereads(data.root, {}, report, request=serve({URL: body}),
                                    pacer=script.Pacer(0, sleep=lambda s: None),
                                    observed_at=date.today().replace(year=date.today().year + 1))
        return report

    assert cited(PAGE).cited_change_rereads == [] and cited(PAGE).cleared_facts_checked == 1
    assert cited(CHANGED).cited_change_rereads == [FACT_ID]
    assert cited(CHANGED).to_dict()["cleared_facts_checked"] == 1


def test_the_offering_file_keeps_its_header(ruled):
    sweep(ruled, CHANGED)
    assert ruled.offering_path.read_text().startswith(HEADER)
