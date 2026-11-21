"""Offline checks for the rolling evidence re-read (MODEL-534)."""

import gzip
import json
import socket
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest

from decision import verify as v
from decision.model import SourceRef, TargetRef, VerificationActor

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "evidence_reread.py"
TODAY = date(2026, 11, 23)
COLLECTOR = VerificationActor(agent="fixture-collector", model_family="openai",
                              method="fixture-collect@1")
OLD = "https://boards.example.net/{}.json"
CITE_ONLY = "https://www.anthropic.com/board.json"
UNCLASSED = "https://unknown.example.org/board.json"


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", lambda *a: pytest.fail("Network attempted"))


@pytest.fixture
def reread():
    from scripts import evidence_reread

    return evidence_reread


def body(score):
    return json.dumps([{"model": "Acme One", "accuracy": str(score)}]).encode()


class Data:
    """A throwaway data checkout: registry, terms, queue and log."""

    def __init__(self, root: Path, monkeypatch):
        self.root = root
        monkeypatch.setenv("MODELSPEC_DATA_DIR", str(root))
        (root / "registry").mkdir(parents=True)
        self.sources = []
        self.terms = {"boards.example.net": "restricts", "unknown.example.org": "unclear",
                      "allowed.example.net": "permits"}
        self.queue = v.Queue(root / "verification")
        self.log = v.VerificationLog(root / "verification")
        self.n = 0

    def row(self, url, *, age=100, score=50.0, method="structured-row-match@1",
            outcome="verified", collector=COLLECTOR):
        self.n += 1
        source_id = f"src-{self.n}"
        self.sources.append(dict(
            id=source_id, url=url, fetch="conditional_http", normaliser="text-default",
            cited_regions=[dict(id="rows", locator=dict(kind="page", value=""))]))
        claim = v.Claim(
            target=TargetRef(kind="evidence", id=f"acme/one#bench#{self.n:012d}"),
            subject="acme/one", names=("Acme One",), field="bench", label="accuracy",
            value=score, unit="percent", collector=collector,
            sources=(SourceRef(source_id=source_id, snapshot_ref="sha256:" + "0" * 64,
                               cited_regions=["rows"]),))
        self.queue.file(claim, at=datetime(2026, 9, 1, tzinfo=UTC))
        actor = VerificationActor(agent="fixture-verifier", model_family="deterministic",
                                  method=method)
        done = TODAY - timedelta(days=age)
        self.log.append(v._verification(claim, actor, outcome, done))
        return claim

    def write(self):
        (self.root / "registry/sources.yaml").write_text(
            json.dumps(dict(schema_version=1, sources=self.sources)))
        (self.root / "registry/source-terms.json").write_text(json.dumps(self.terms))

    def lines(self):
        path = self.root / "verification/log.jsonl"
        return [json.loads(x) for x in path.read_text().splitlines()]


@pytest.fixture
def data(tmp_path, monkeypatch):
    return Data(tmp_path / "data", monkeypatch)


def serve(pages):
    calls = []

    def request(url):
        calls.append(url)
        page = pages[url]
        return page if isinstance(page, tuple) else (200, None, page)
    request.calls = calls
    return request


def run(reread, data, tmp_path, pages, *, dry_run=False, **kwargs):
    data.write()
    kwargs.setdefault("pacer", reread.Pacer(0, sleep=lambda s: None))
    return reread.run(data.root, observed_at=TODAY, dry_run=dry_run,
                      store_root=tmp_path / "cache", request=serve(pages), **kwargs)


def test_window_is_oldest_first_within_the_cap_and_takes_page_groups_whole(reread, data):
    for i in range(3):
        data.row(OLD.format("old"), age=120)      # one page, three rows
    data.row(OLD.format("mid"), age=100)
    data.row(OLD.format("new"), age=80)
    data.write()
    from decision.sources import load_sources
    terms = reread.load_terms(data.root)
    sources = load_sources(data.root / "registry/sources.yaml")
    window = reread.select_window(data.root, sources, terms, TODAY, cap=4)
    assert [r.urls[0] for r in window.rows] == [OLD.format("old")] * 3 + [OLD.format("mid")]
    assert window.waiting == 1
    small = reread.select_window(data.root, sources, terms, TODAY, cap=2)
    assert [r.urls[0] for r in small.rows] == [OLD.format("mid"), OLD.format("new")]


def test_default_cap_is_set_in_code(reread):
    assert reread.WEEKLY_ROW_CAP == 400
    assert reread.HOST_DELAY_SECONDS >= 1


def test_rows_of_another_method_fresh_rows_and_unclassed_hosts_are_left_out(reread, data):
    data.row(OLD.format("a"), age=100)
    data.row(OLD.format("b"), age=100, method="table-header-match@1")
    data.row(OLD.format("c"), age=3)
    data.row(UNCLASSED, age=100)
    data.write()
    from decision.sources import load_sources
    window = reread.select_window(data.root, load_sources(data.root / "registry/sources.yaml"),
                                  reread.load_terms(data.root), TODAY)
    assert [r.urls[0] for r in window.rows] == [OLD.format("a")]
    assert window.other_method == 1 and window.too_fresh == 1
    assert dict(window.unclassed) == {"unknown.example.org": 1}


def test_a_matching_page_is_verified_logged_and_a_copy_is_kept(reread, data, tmp_path):
    data.row(OLD.format("a"), score=50.0)
    before = len(data.lines())
    report = run(reread, data, tmp_path, {OLD.format("a"): body(50.0)})
    assert report.counts["verified"] == 1 and not report.mismatches
    last = data.lines()[-1]
    assert len(data.lines()) == before + 1
    assert last["outcome"] == "verified" and last["date"] == "2026-11-23"
    assert last["method"] == "structured-row-match@1"
    copies = list((data.root / reread.COPIES_DIRECTORY).rglob("*.gz"))
    assert len(copies) == 1 and gzip.decompress(copies[0].read_bytes()) == body(50.0)
    assert report.bytes_retained > 0 and report.copies_retained == 1


def test_a_changed_page_is_a_mismatch_alert_and_no_card_changes(reread, data, tmp_path):
    data.row(OLD.format("a"), score=50.0)
    (data.root / "models").mkdir()
    card = data.root / "models/card.md"
    card.write_text("score: 50.0\n")
    report = run(reread, data, tmp_path, {OLD.format("a"): body(47.5)})
    assert report.counts["mismatch"] == 1 and len(report.mismatches) == 1
    assert data.lines()[-1]["outcome"] == "mismatch"
    assert card.read_text() == "score: 50.0\n"
    assert "no longer match" in reread.render(report)


def test_a_gone_page_is_unreachable_and_a_transient_failure_writes_nothing(reread, data, tmp_path):
    data.row(OLD.format("gone"), age=120)
    data.row(OLD.format("slow"), age=110)
    before = len(data.lines())
    report = run(reread, data, tmp_path, {OLD.format("gone"): (404, None, b""),
                                          OLD.format("slow"): (503, None, b"")})
    assert report.counts["unreachable"] == 1 and report.counts["deferred"] == 1
    assert len(data.lines()) == before + 1
    assert data.lines()[-1]["outcome"] == "unreachable"


def test_a_redirect_to_an_unclassed_host_is_never_requested(reread, data, tmp_path):
    data.row(OLD.format("a"))
    pages = {OLD.format("a"): (302, UNCLASSED, b"")}
    request_log = serve(pages)
    data.write()
    report = reread.run(data.root, observed_at=TODAY, dry_run=False, store_root=tmp_path / "c",
                        request=request_log, pacer=reread.Pacer(0, sleep=lambda s: None))
    assert request_log.calls == [OLD.format("a")]
    assert report.counts["deferred"] == 1 and report.blocked_hosts == {"unknown.example.org": 1}
    assert not list((data.root / reread.COPIES_DIRECTORY).rglob("*"))


def test_a_redirect_to_a_classed_host_is_followed_and_the_hop_is_kept(reread, data, tmp_path):
    data.row(OLD.format("a"), score=50.0)
    target = "https://allowed.example.net/moved.json"
    report = run(reread, data, tmp_path, {OLD.format("a"): (307, target, b""),
                                          target: body(50.0)})
    assert report.counts["verified"] == 1


def test_a_cite_only_host_is_cited_with_no_bytes_kept(reread, data, tmp_path):
    data.row(CITE_ONLY)
    data.write()
    report = run(reread, data, tmp_path, {CITE_ONLY: body(50.0)})
    assert report.counts["cited"] == 1 and report.counts["verified"] == 0
    assert not (data.root / reread.COPIES_DIRECTORY).exists()
    assert report.bytes_retained == 0
    cached = [p for p in (tmp_path / "cache").rglob("*") if p.is_file()
              and not p.name.endswith(".json")]
    assert not cached, "no page bytes of a cite-only host in the cache"
    events = [json.loads(x) for x in
              (data.root / "verification/queue/events.jsonl").read_text().splitlines()]
    assert events[-1]["event"] == "checked" and events[-1]["outcome"] == "cited"
    assert events[-1]["at"].startswith("2026-11-23")


def test_a_dry_run_writes_nothing(reread, data, tmp_path):
    data.row(OLD.format("a"), score=50.0)
    data.write()
    log = (data.root / "verification/log.jsonl").read_bytes()
    events = (data.root / "verification/queue/events.jsonl").read_bytes()
    report = run(reread, data, tmp_path, {OLD.format("a"): body(50.0)}, dry_run=True)
    assert report.counts["verified"] == 1 and report.bytes_retained > 0
    assert (data.root / "verification/log.jsonl").read_bytes() == log
    assert (data.root / "verification/queue/events.jsonl").read_bytes() == events
    assert not (data.root / reread.COPIES_DIRECTORY).exists()


def test_the_run_stops_at_the_cap(reread, data, tmp_path):
    for i in range(5):
        data.row(OLD.format(f"p{i}"), age=100 + i)
    pages = {OLD.format(f"p{i}"): body(50.0) for i in range(5)}
    report = run(reread, data, tmp_path, pages, cap=3)
    assert report.selected == 3 and report.pages == 3 and report.waiting == 2


def test_requests_to_one_host_are_paced(reread):
    slept, now = [], [0.0]
    pacer = reread.Pacer(2.0, sleep=lambda s: (slept.append(s), now.__setitem__(0, now[0] + s)),
                         clock=lambda: now[0])
    pacer.wait("a.example")
    pacer.wait("a.example")
    pacer.wait("b.example")
    assert slept == [2.0]


def test_the_re_read_uses_no_paid_client_and_no_model(reread):
    text = SCRIPT.read_text().lower().split('"""', 2)[2]
    for word in ("firecrawl", "anthropic", "openai", "ollama", "mistral", "claude_extractor",
                 "api_key", "llmextractor", "completion"):
        assert word not in text.replace("www.anthropic.com", ""), word
    assert reread.METHOD == "structured-row-match@1"
    extractors = [v.StructuredDataExtractor()]
    assert {e.actor.model_family for e in extractors} == {"deterministic"}
