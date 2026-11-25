"""MODEL-562: owner-ruled facts on the rolling re-read; a changed cited region reopens rule 15.

Synthetic data only: the planted offering of ``tests.test_cited_offering`` on a cite-only host,
its source given an HTML normaliser and one CSS-located region, real disagreements and
agreements through the gate with stub readers, and stub HTTP.
"""

import json
import socket
from datetime import date

import pytest
import yaml

from decision import cited_change as gate_module
from decision.cited_change import _gate, cited_change, fact_epoch, reread
from decision.cited_reader import text_sha256
from decision.owner_ruling import RULINGS_FILE, has_ruling, ruled_epoch
from decision.ruling_reread import (
    BASELINE_FIELDS, RECORD_FILE, REOPEN_FIELDS, Records, region_sha256, reopen_epoch, ruled_facts,
)
from scripts import cited_offering as writer
from scripts import evidence_reread as script
from scripts import file_owner_ruling as filer
from tests.test_cited_offering import FACT_ID, HEADER, SUBJECT, URL, Data, pair, refused, serve
from tests.test_owner_ruling import RETENTION, args, attempts, offering_fact

DAY = date(2026, 12, 1)
TARGET = f"{SUBJECT}#{RETENTION}"
FILLER = " ".join(f"Section {i} describes how the service handles requests." for i in range(30))


def page(days=30, banner="Updated 1 November", nonce=""):
    return (f"<html><body><p class='banner'>{banner}</p><p>{FILLER}</p>"
            f"<script>var n='{nonce}';</script>"
            f"<p id='retention'>Abuse monitoring logs are kept for up to {days} days.</p>"
            "<p>SECRET-PAGE-MARKER</p></body></html>").encode()


RULED = page()
CHURNED = page(nonce="7")  # byte churn: the visible text is the ruled page's
BANNER = page(banner="Spring offer: read the new guide")  # visible text moved, the region did not
CHANGED = page(45)


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", lambda *a: pytest.fail("Network attempted"))


class Web:
    """The gate's own transport (``decision.cited_change._http_once``), stubbed."""

    def __init__(self, monkeypatch):
        self.pages, self.calls = {URL: RULED}, []
        monkeypatch.setattr(gate_module, "_http_once", self)

    def __call__(self, url):
        self.calls.append(url)
        got = self.pages[url]
        return got if isinstance(got, tuple) else (200, None, got)


@pytest.fixture
def web(monkeypatch):
    return Web(monkeypatch)


@pytest.fixture
def data(tmp_path, monkeypatch):
    data = Data(tmp_path / "data", monkeypatch)
    source = next(s for s in data.sources if s["id"] == "data")
    source["normaliser"] = "html-default"
    source["cited_regions"] = [
        {"id": "retention", "locator": {"kind": "css", "value": "#retention"}}]
    data.write()
    return data


def own(readers, **kw):
    """The gate on the retention fact, fetching the page itself."""
    return cited_change(subject=SUBJECT, facet=RETENTION, source_id="data", readers=readers, **kw)


def rule(data, **kw):
    result = filer.plan(data_dir=data.root, **args(**kw))
    filer.apply(result)


@pytest.fixture
def ruled(data, web):
    """A real ruling: two readers disagreed on the ruled page, and the owner ruled 30 days."""
    refused(own(pair(30, "unbounded")), "readers_disagree")
    rule(data)
    fact = offering_fact(data)
    assert has_ruling(fact) and fact_epoch(fact) == "initial"
    assert fact["sources"][0]["cited_regions"] == ["retention"]
    return data


def sweep(data, body, web, *, dry_run=False):
    """One ruled-fact re-read, through the gate's own transport, with ``body`` served."""
    web.pages[URL] = body
    report = script.Report(DAY.isoformat(), dry_run)
    script.ruled_fact_rereads(data.root, script.load_terms(data.root), report,
                              pacer=script.Pacer(0, sleep=lambda s: None), observed_at=DAY,
                              dry_run=dry_run)
    return report


def records(data):
    path = data.root / RECORD_FILE
    return [json.loads(x) for x in path.read_text().splitlines()] if path.is_file() else []


def outcome(report):
    return {k: n for k, n in report.to_dict()["ruled"].items() if n}


def served(web, body):
    web.pages[URL] = body
    return body


def epochs(data):
    return [a["epoch"] for a in attempts(data)]


def region(data, body):
    fact = offering_fact(data)
    row = next(s for s in data.sources if s["id"] == "data")
    return region_sha256(fact, "data", row, body)


# --- an unchanged page, or a change outside the cited region, leaves the fact alone -----------


def test_the_ruled_page_records_its_baseline_once_and_asks_no_reader(ruled, web):
    before = len(attempts(ruled))
    assert outcome(sweep(ruled, RULED, web)) == {"baselined": 1}
    [line] = records(ruled)
    assert set(line) == set(BASELINE_FIELDS) and line["kind"] == "baseline"
    assert line["region_sha256"] == region(ruled, RULED) and line["target"] == TARGET
    for body in (RULED, CHURNED):
        assert outcome(sweep(ruled, body, web)) == {"current": 1}
    assert len(records(ruled)) == 1 and len(attempts(ruled)) == before, "no reader was asked"
    assert offering_fact(ruled)["value"] == 30


def test_unrelated_visible_text_churn_opens_no_epoch(ruled, web):
    sweep(ruled, RULED, web)
    assert text_sha256(BANNER) != text_sha256(RULED)
    assert region(ruled, BANNER) == region(ruled, RULED)
    assert outcome(sweep(ruled, BANNER, web)) == {"current": 1}
    assert [r["kind"] for r in records(ruled)] == ["baseline"]
    served(web, BANNER)
    refused(own(pair(45)), "prior_attempt_disagreed")
    assert set(epochs(ruled)) == {"initial"}


def test_a_new_text_with_no_baseline_shows_no_change(ruled, web):
    assert outcome(sweep(ruled, CHANGED, web)) == {"unbaselined": 1} and records(ruled) == []
    refused(own(pair(45)), "prior_attempt_disagreed")


def test_a_ruling_is_never_superseded_inside_its_own_epoch(ruled, web):
    sweep(ruled, RULED, web)
    before = len(attempts(ruled))
    for body in (RULED, CHURNED, BANNER):
        served(web, body)
        refused(own(pair(45)), "prior_attempt_disagreed")
        refused(own(pair(30)), "prior_attempt_disagreed")
    assert len(attempts(ruled)) == before and offering_fact(ruled)["value"] == 30


# --- a changed cited region reopens the fact -----------------------------------------------------


def test_a_changed_region_is_recorded_once(ruled, web):
    sweep(ruled, RULED, web)
    assert outcome(sweep(ruled, CHANGED, web, dry_run=True)) == {"reopened": 1}
    assert len(records(ruled)) == 1, "a dry run writes nothing"
    assert outcome(sweep(ruled, CHANGED, web)) == {"reopened": 1}
    baseline, line = records(ruled)
    assert set(line) == set(REOPEN_FIELDS) and line["kind"] == "reopen"
    assert line["region_sha256"] == region(ruled, CHANGED)
    assert line["ruled_region_sha256"] == baseline["region_sha256"]
    assert line["epoch"] == reopen_epoch("initial", region(ruled, CHANGED))
    assert outcome(sweep(ruled, CHANGED, web)) == {"open": 1} and len(records(ruled)) == 2
    assert offering_fact(ruled)["value"] == 30 and has_ruling(offering_fact(ruled))


def test_the_gate_reopens_only_an_epoch_the_sweep_recorded(ruled, web):
    sweep(ruled, RULED, web)
    served(web, CHANGED)
    refused(own(pair(45)), "prior_attempt_disagreed")  # changed, but not recorded yet
    sweep(ruled, CHANGED, web)
    out = own(pair(45))
    assert out.changed, (out.reason, out.detail)
    assert epochs(ruled)[-1] == reopen_epoch("initial", region(ruled, CHANGED))
    writer.apply(out, data_dir=ruled.root)
    fact = offering_fact(ruled)
    assert (fact["value"], fact["state"]) == (45, "known") and not has_ruling(fact)
    assert fact_epoch(fact) == "reread:" + text_sha256(CHANGED)
    assert ruled_facts(ruled.root) == []


def test_caller_bytes_never_mint_a_reopened_epoch(ruled, web):
    sweep(ruled, RULED, web)
    sweep(ruled, CHANGED, web)
    refused(own(pair(45), request=serve({URL: CHANGED})), "prior_attempt_disagreed")
    refused(_gate(subject=SUBJECT, facet=RETENTION, source_id="data", readers=pair(45),
                  request=None, allow_unchanged=False, page=(CHANGED, ())),
            "prior_attempt_disagreed")
    assert set(epochs(ruled)) == {"initial"}


def test_a_forged_record_line_reopens_nothing(ruled, web):
    sweep(ruled, RULED, web)
    path = ruled.root / RECORD_FILE
    baseline = records(ruled)[0]
    forged = {"kind": "reopen", "target": TARGET, "ruled_epoch": "initial", "source_id": "data",
              "region_sha256": baseline["region_sha256"],
              "ruled_region_sha256": baseline["region_sha256"],
              "epoch": reopen_epoch("initial", baseline["region_sha256"]),
              "recorded_on": DAY.isoformat()}
    path.write_text(path.read_text() + json.dumps(forged) + "\n")
    for body in (RULED, BANNER):  # the ruled region, whatever a line says
        served(web, body)
        refused(own(pair(45)), "prior_attempt_disagreed")


@pytest.mark.parametrize("tamper", ["ruling_value", "fact_value", "no_ruling_line"])
def test_a_tampered_ruling_cannot_reopen(ruled, web, tamper):
    sweep(ruled, RULED, web)
    sweep(ruled, CHANGED, web)
    path = ruled.root / RULINGS_FILE
    if tamper == "ruling_value":
        [line] = [json.loads(x) for x in path.read_text().splitlines()]
        path.write_text(json.dumps({**line, "value": 45}) + "\n")
    elif tamper == "fact_value":
        ruled.fact(value=45, derivation=offering_fact(ruled)["derivation"],
                   sources=offering_fact(ruled)["sources"])
    else:
        path.write_text("")
    served(web, CHANGED)
    refused(own(pair(45)), "prior_attempt_disagreed")
    assert outcome(sweep(ruled, CHANGED, web))["invalid"] == 1


def test_a_disagreement_in_a_reopened_epoch_blocks_it_and_the_owner_may_rule_there(ruled, web):
    from decision.owner_ruling import admits, latest_ruling_claims

    sweep(ruled, RULED, web)
    sweep(ruled, CHANGED, web)
    reopened = reopen_epoch("initial", region(ruled, CHANGED))
    refused(own(pair(45, 60)), "readers_disagree")
    refused(own(pair(45)), "prior_attempt_disagreed")
    rule(ruled, value=45, epoch=reopened)
    fact = offering_fact(ruled)
    assert fact["derivation"]["owner_ruling"]["epoch"] == reopened
    assert ruled_epoch(fact) == reopened and fact["value"] == 45
    lines = [json.loads(x) for x in (ruled.root / RULINGS_FILE).read_text().splitlines()]
    assert admits(fact, SUBJECT, rulings=lines, attempts=attempts(ruled),
                  sources={s["id"]: s["url"] for s in ruled.sources},
                  claims=latest_ruling_claims(ruled.root / "verification/queue/events.jsonl"))
    # the second ruling's epoch now holds the disagreement: no supersession inside it
    refused(own(pair(60)), "prior_attempt_disagreed")
    # and its ruled page is the changed one: a baseline is recorded for the new epoch
    assert outcome(sweep(ruled, CHANGED, web)) == {"baselined": 1}


def test_the_filer_refuses_an_unrecorded_reopened_epoch_with_a_logged_disagreement(ruled, web):
    from decision.cited_change import lookup
    from decision.cited_reader import read_page

    epoch = reopen_epoch("initial", "e" * 64)
    found = lookup(SUBJECT, RETENTION)
    # a real harness disagreement logged in an epoch the sweep never recorded
    read_page(subject=SUBJECT, url=URL, facet_id=RETENTION, subject_name=found.subject_name,
              page_bytes=CHANGED, readers=pair(45, 60), epoch=epoch, definition=found.definition)
    assert epochs(ruled)[-1] == epoch
    with pytest.raises(filer.Refused) as caught:
        rule(ruled, value=45, epoch=epoch)
    assert caught.value.reason == "epoch_not_current"


# --- reread() and the sweep read a ruled page as the gate does ------------------------------------


def test_reread_of_a_ruled_page_back_at_the_text_before_the_ruling_is_not_current(data, web):
    """The fact had a cited change on page A (30); the page moved to B, the readers disagreed in
    A's epoch, and the owner ruled. Back at A, the kept block's text matches, but A is not the
    ruled page: ``reread`` does not call it current."""
    out = own(pair(30))
    writer.apply(out, data_dir=data.root)
    base = fact_epoch(offering_fact(data))
    moved = served(web, page(90))
    refused(own(pair(90, 30)), "readers_disagree")
    rule(data, value=90, epoch=base)
    fact = offering_fact(data) | {"subject": SUBJECT}
    assert fact_epoch(fact) == base
    served(web, moved)
    assert reread(fact, source_id="data", readers=pair(90)).outcome == "current"
    served(web, RULED)  # back at page A
    first = reread(fact, source_id="data", readers=pair(30))
    assert first.outcome == "flagged" and first.reason == "prior_attempt_disagreed"
    # once the sweep has the ruled baseline and records the change, reread reopens it
    sweep(data, moved, web)
    sweep(data, RULED, web)
    again = reread(fact, source_id="data", readers=pair(30))
    assert again.outcome == "changed" and again.record["value"] == 30
    # the old cited-change re-read no longer lists the ruled fact
    report = script.Report("x", True)
    script.cited_change_rereads(data.root, {}, report, request=serve({URL: RULED}),
                                pacer=script.Pacer(0, sleep=lambda s: None), observed_at=DAY)
    assert report.cited_change_rereads == []


def test_the_sweep_and_the_gate_hash_the_same_bytes_behind_a_redirect(ruled, web):
    """Both read with the gate's fetch: a cite-only redirect is followed by both, and the
    epoch the sweep records is the epoch the gate reads in."""
    moved = "https://developers.openai.com/api/docs/guides/your-data-v2"
    sweep(ruled, RULED, web)
    web.pages[moved] = CHANGED
    sweep(ruled, (302, moved, b""), web)
    [_, line] = records(ruled)
    out = own(pair(45))
    assert out.changed and epochs(ruled)[-1] == line["epoch"]


def test_a_redirect_to_a_retaining_host_is_refused_by_both(ruled, web):
    sweep(ruled, RULED, web)
    web.pages["https://huggingface.co/x"] = CHANGED
    report = sweep(ruled, (302, "https://huggingface.co/x", b""), web)
    assert outcome(report) == {"blocked": 1} and "https://huggingface.co/x" not in web.calls
    refused(own(pair(45)), "redirect_to_retaining_host")


# --- the rest of the sweep ----------------------------------------------------------------------


def test_an_unclassed_source_host_is_never_requested(ruled, web):
    for source in ruled.sources:
        if source["id"] == "data":
            source["url"] = "https://unknown.example.org/your-data"
    (ruled.root / "registry/sources.yaml").write_text(
        yaml.safe_dump({"schema_version": 1, "sources": ruled.sources}))
    web.calls.clear()
    report = sweep(ruled, CHANGED, web)
    assert outcome(report) == {"unclassed": 1} and web.calls == []
    assert report.unclassed_hosts == {"unknown.example.org": 1}


def test_a_page_that_cannot_be_read_writes_nothing(ruled, web):
    assert outcome(sweep(ruled, (503, None, b""), web)) == {"deferred": 1}
    assert records(ruled) == []


def test_the_report_is_counts_only_and_unchanged_with_no_ruled_fact(ruled, web, tmp_path):
    sweep(ruled, RULED, web)
    web.pages[URL] = CHANGED
    report = script.run(ruled.root, observed_at=DAY, dry_run=True, store_root=tmp_path / "cache",
                        pacer=script.Pacer(0, sleep=lambda s: None))
    out = report.to_dict()
    assert out["ruled_facts_checked"] == 1 and out["ruled"]["reopened"] == 1
    assert all(isinstance(n, int) for n in out["ruled"].values())
    text = json.dumps(out) + script.render(report)
    assert SUBJECT not in text and region(ruled, CHANGED) not in text and "SECRET" not in text
    assert "Owner-ruled facts (1 checked)" in script.render(report)
    assert not [p for p in (tmp_path / "cache").rglob("*") if p.is_file()], "no page bytes kept"
    plain = script.Report("x", True)
    assert "ruled" not in plain.to_dict() and "Owner-ruled" not in script.render(plain)


def test_a_ruled_epoch_is_rule_15s_or_a_reopened_one_that_extends_it(ruled):
    fact = offering_fact(ruled)
    block = fact["derivation"]["owner_ruling"]

    def with_epoch(epoch):
        return {**fact, "derivation": {"owner_ruling": {**block, "epoch": epoch}}}

    assert ruled_epoch(fact) == "initial"
    ok = reopen_epoch("initial", "a" * 64)
    assert ruled_epoch(with_epoch(ok)) == ok
    assert ruled_epoch(with_epoch(reopen_epoch(ok, "b" * 64))) == reopen_epoch(ok, "b" * 64)
    for bad in ("reread:" + "a" * 64, "initial:reopen:xyz", "other:reopen:" + "a" * 64,
                ok + "!"):
        assert ruled_epoch(with_epoch(bad)) == "initial"
    assert Records.read(ruled.root).reopened == {}


def test_a_cleared_fact_is_re_read_in_the_epoch_its_own_block_names(data, web):
    """MODEL-552 clearings: the cleared record carries a cited-change block naming its
    ``clearing_epoch``. It is re-read with the cited-change facts, against its own text, and
    a change is read in ``reread:<text>``, an epoch apart from the clearing's and its base's."""
    out = own(pair(30))
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

    assert cited(RULED).cited_change_rereads == [] and cited(RULED).cleared_facts_checked == 1
    assert cited(CHANGED).cited_change_rereads == [FACT_ID]
    assert cited(CHANGED).to_dict()["cleared_facts_checked"] == 1


def test_the_offering_file_keeps_its_header(ruled, web):
    sweep(ruled, CHANGED, web)
    assert ruled.offering_path.read_text().startswith(HEADER)
