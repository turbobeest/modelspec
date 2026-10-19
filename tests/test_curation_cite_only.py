"""Curation source retention through offline watcher and export boundaries."""

from __future__ import annotations

import json
import io
import urllib.request
import urllib.response
from email.message import Message
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from scripts.curation import ci, draft, propose, watch


MARK = "CurationSourceSentinel7f3a"
NOW = "2026-10-19T12:00:00+00:00"
FORMS = {
    "xai": ("https://x.ai/pricing", ()),
    "docs": ("https://docs.x.ai/models", ()),
    "subdomain": ("https://api.docs.x.ai/pricing", ()),
    "perplexity": ("https://www.perplexity.ai/pro", ()),
    "uppercase": ("https://X.AI/pricing", ()),
    "trailing_dot": ("https://x.ai./pricing", ()),
    "port": ("https://x.ai:8443/pricing", ()),
    "redirect": ("https://example.test/start", ("https://x.ai/pricing",)),
    "control": ("https://example.test/plain", ()),
}


def benchmark(tmp_path: Path, url: str) -> Path:
    bench = tmp_path / "benchmarks"
    bench.mkdir()
    front = yaml.safe_dump({"id": "probe", "status": "active", "sources": [{"url": url}]})
    (bench / "probe.md").write_text(f"---\n{front}---\nSynthetic fixture.\n")
    return bench


def fetched(url: str, text: str, resolved_urls=(), **overrides):
    return SimpleNamespace(url=url, text=text, resolved_urls=resolved_urls,
                           status=200, etag="", last_modified="", error="",
                           truncated=False, fetcher="http", ok=True, **overrides)


def disk_hits(*roots: Path) -> list[Path]:
    return [path for root in roots for path in root.rglob("*")
            if path.is_file() and MARK.encode() in path.read_bytes()]


@pytest.mark.parametrize("form", FORMS)
def test_watch_retains_only_citation_metadata_for_restricted_origins(tmp_path, form):
    url, resolved = FORMS[form]
    bench = benchmark(tmp_path, url)
    state, reports = tmp_path / "state", tmp_path / "reports"
    bodies = iter([f"<p>{MARK} stable</p>", f"<p>{MARK} version 2.0 deprecated</p>"])

    def fetcher(source):
        return fetched(source, next(bodies), resolved)

    first = watch.watch(["probe"], state, bench_dir=bench, fetcher=fetcher,
                        js_hosts=set(), max_workers=1, now=NOW)
    second = watch.watch(["probe"], state, bench_dir=bench, fetcher=fetcher,
                         js_hosts=set(), max_workers=1, now=NOW)
    reports.mkdir()
    watch.export_source_texts(second, state, reports)
    (reports / "change_report.json").write_text(json.dumps(second))
    (reports / "change_report.md").write_text(watch.render_md(second))

    assert first["baselined"] == 1
    assert len(second["changes"]) == 1
    meta = json.loads((state / f"{watch.state_key(url)}.json").read_text())
    if form == "control":
        assert len(disk_hits(state, reports)) == 2
        assert second["changes"][0]["source_text"].endswith(".txt")
        assert second["changes"][0]["kinds"][0]["kind"] == "new_version"
        assert "status" in meta
    else:
        assert disk_hits(state, reports) == []
        assert not list(state.glob("*.txt"))
        assert not list((reports / "sources").glob("*.txt"))
        assert second["changes"][0]["kinds"] == []
        assert "source_text" not in second["changes"][0]
        assert set(meta) == {"url", "hash", "fetched_at", "resolved_urls"}
        assert meta["url"] == url and meta["fetched_at"] == NOW
        assert len(meta["hash"]) == 64
        assert set(resolved) <= set(meta["resolved_urls"])


@pytest.mark.parametrize("hops", [
    ("https://example.test/start", "https://x.ai/pricing"),
    ("https://example.test/start", "https://x.ai/pricing", "https://example.test/end"),
    ("https://example.test/start", "https://example.test/end"),
])
def test_http_fetch_records_real_urllib_redirect_chain(tmp_path, monkeypatch, hops):
    class Transport(urllib.request.HTTPSHandler):
        def https_open(self, request):
            index = hops.index(request.full_url)
            headers = Message()
            if index + 1 < len(hops):
                headers["Location"] = hops[index + 1]
                code, body = 302, b""
            else:
                code, body = 200, f"<p>{MARK}</p>".encode()
            response = urllib.response.addinfourl(io.BytesIO(body), headers, request.full_url, code)
            response.msg = "OK" if code == 200 else "Found"
            return response

    build_opener = urllib.request.build_opener
    monkeypatch.setattr(watch.urllib.request, "build_opener",
                        lambda *handlers: build_opener(*handlers, Transport()))
    monkeypatch.setattr(watch.urllib.request, "urlopen", build_opener(Transport()).open)
    result = watch.http_fetch(hops[0], retries=0)
    assert result.ok
    assert result.resolved_urls == hops

    bench = benchmark(tmp_path, hops[0])
    state = tmp_path / "state"
    watch.watch(["probe"], state, bench_dir=bench, fetcher=lambda _: result,
                js_hosts=set(), max_workers=1, now=NOW)
    if "https://x.ai/pricing" in hops:
        assert disk_hits(state) == []
    else:
        assert len(disk_hits(state)) == 1


@pytest.mark.parametrize("form", FORMS)
def test_firecrawl_watch_uses_every_reported_origin(tmp_path, monkeypatch, form):
    from scripts.benchmarks import fetch as fc

    url, resolved = FORMS[form]
    bench = benchmark(tmp_path, url)
    state = tmp_path / "state"
    host = watch.host_of(url)
    monkeypatch.setattr(fc, "resolve_key", lambda: "synthetic-key")
    monkeypatch.setattr(fc, "scrape", lambda *args, **kwargs: {
        "markdown": MARK,
        "metadata": {"sourceURL": url, "url": resolved[-1] if resolved else url},
    })
    budget = watch.FirecrawlBudget(cap=1, allow={host})
    watch.watch(["probe"], state, bench_dir=bench, fetcher=lambda _: fetched(url, "plain"),
                firecrawl=budget, js_hosts={host}, max_workers=1, now=NOW)
    assert budget.calls == 1
    assert bool(disk_hits(state)) is (form == "control")


def test_firecrawl_cannot_discard_plain_http_cite_only_redirect(tmp_path, monkeypatch):
    from scripts.benchmarks import fetch as fc

    url = "https://example.test/start"
    bench = benchmark(tmp_path, url)
    state = tmp_path / "state"
    monkeypatch.setattr(fc, "resolve_key", lambda: "synthetic-key")
    monkeypatch.setattr(fc, "scrape", lambda *args, **kwargs: {
        "markdown": MARK, "metadata": {"sourceURL": url},
    })
    budget = watch.FirecrawlBudget(cap=1, allow={"example.test"})
    watch.watch(["probe"], state, bench_dir=bench,
                fetcher=lambda _: fetched(url, "plain", ("https://x.ai/pricing",)),
                firecrawl=budget, js_hosts={"example.test"}, max_workers=1, now=NOW)
    assert disk_hits(state) == []


def report_for(changes):
    return {"axis": "benchmarks", "run_at": NOW, "pages": ["probe"], "sources_checked": 1,
            "unchanged": 0, "baselined": 0, "changes": changes, "failures": [],
            "needs_js_not_rendered": [], "firecrawl": {"cap": 0, "calls": 0, "stopped": False}}


def stale_artifacts(tmp_path, url, resolved):
    state, reports = tmp_path / "state", tmp_path / "reports"
    state.mkdir()
    (reports / "sources").mkdir(parents=True)
    key = watch.state_key(url)
    meta = {"url": url, "hash": "a" * 64, "fetched_at": NOW,
            "resolved_urls": list(resolved), "etag": MARK}
    (state / f"{key}.json").write_text(json.dumps(meta))
    (state / f"{key}.txt").write_text(MARK)
    (reports / "sources" / f"{key}.txt").write_text(MARK)
    old = report_for([{"url": url, "pages": [{"page": "probe", "role": "source"}],
                       "resolved_urls": list(resolved), "source_text": f"sources/{key}.txt",
                       "kinds": [{"kind": "new_version", "evidence": MARK}]}])
    (reports / "change_report.json").write_text(json.dumps(old))
    (reports / "change_report.md").write_text(watch.render_md(old))
    # Unrelated and unmapped historical outputs belong to other runs, not this cleanup.
    (state / "unrelated.txt").write_text("ordinary state")
    (reports / "sources" / "unmapped.txt").write_text("unmapped historical source")
    return state, reports, old


@pytest.mark.parametrize("url,resolved", [
    ("https://x.ai/pricing", ()),
    ("https://example.test/start", ("https://x.ai/pricing",)),
])
def test_export_independently_refuses_stale_cite_only_text_and_report(tmp_path, url, resolved):
    state, reports, old = stale_artifacts(tmp_path, url, resolved)
    watch.export_source_texts(old, state, reports)
    assert disk_hits(state, reports) == []
    assert old["changes"][0]["kinds"] == []
    assert "source_text" not in old["changes"][0]
    assert (state / "unrelated.txt").read_text() == "ordinary state"
    assert (reports / "sources" / "unmapped.txt").read_text() == "unmapped historical source"


@pytest.mark.parametrize("outcome", ["changed", "unchanged", "failed"])
def test_watch_repeat_preserves_cite_only_policy_and_removes_its_stale_exports(tmp_path, outcome):
    url, resolved = "https://example.test/start", ("https://x.ai/pricing",)
    bench = benchmark(tmp_path, url)
    state, reports, _ = stale_artifacts(tmp_path, url, resolved)
    if outcome == "unchanged":
        import hashlib
        meta_path = state / f"{watch.state_key(url)}.json"
        meta = json.loads(meta_path.read_text())
        meta["hash"] = hashlib.sha256(MARK.encode()).hexdigest()
        meta_path.write_text(json.dumps(meta))
    result = watch.FetchResult(url=url, status=503, error=MARK) if outcome == "failed" else fetched(url, MARK)
    report = watch.watch(["probe"], state, bench_dir=bench, fetcher=lambda _: result,
                         js_hosts=set(), max_workers=1, now=NOW)
    watch.export_source_texts(report, state, reports)
    assert disk_hits(state, reports) == []
    assert MARK not in json.dumps(report)
    assert (state / "unrelated.txt").exists()
    assert (reports / "sources" / "unmapped.txt").exists()


def test_export_ordinary_sources_preserves_prior_artifacts(tmp_path):
    url = "https://example.test/plain"
    state, reports, old = stale_artifacts(tmp_path, url, ())
    (state / "unrelated.json").write_text('["unrelated historical metadata"]')
    watch.export_source_texts(old, state, reports)
    assert len(disk_hits(state, reports)) == 5
    assert old["changes"][0]["source_text"].endswith(".txt")
    assert (state / "unrelated.json").read_text() == '["unrelated historical metadata"]'


@pytest.mark.parametrize("form", FORMS)
def test_draft_page_refuses_cite_only_sources_before_prompt_or_file_write(tmp_path, form):
    url, resolved = FORMS[form]
    page = tmp_path / "arena_elo.md"
    page.write_text((watch.ROOT / "benchmarks" / page.name).read_text())
    before = page.read_text()
    calls = []
    delegate = draft.FakeDrafter(url=url, today="2026-10-19")

    class Drafter:
        label = "offline fixture"

        def __call__(self, prompt, original):
            calls.append(prompt)
            return delegate(prompt, original)

    change = {"url": url, "resolved_urls": list(resolved),
              "kinds": [{"kind": "new_version", "evidence": MARK}]}
    result = draft.draft_page(page, change, MARK, Drafter(), today="2026-10-19",
                              out_dir=tmp_path / "drafts", apply=True)
    if form == "control":
        assert result.accepted and calls
        assert (tmp_path / "drafts" / page.name).exists()
    else:
        assert calls == []
        assert not result.accepted
        assert result.kinds == []
        assert result.errors == ["cite-only sources cannot produce retained drafts"]
        assert page.read_text() == before
        assert not (tmp_path / "drafts").exists()


@pytest.mark.parametrize("url,resolved", [
    ("https://x.ai/pricing", ()),
    ("https://example.test/start", ("https://x.ai/pricing",)),
])
def test_ci_drafter_never_reads_restored_cite_only_source_text(tmp_path, monkeypatch, url, resolved):
    source = tmp_path / "source.txt"
    source.write_text(MARK)
    change = {"url": url, "resolved_urls": list(resolved), "source_text": source.name,
              "pages": [{"page": "probe", "role": "source"}],
              "kinds": [{"kind": "new_version", "evidence": MARK}]}
    read_text = Path.read_text

    def refuse_source_read(path, *args, **kwargs):
        assert path != source, "cite-only source text must not reach the drafter"
        return read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", refuse_source_read)
    report = report_for([change])
    assert not ci.plan(report)["has_changes"]
    assert ci.draft_all(report, tmp_path, "fake", bench_dir=tmp_path / "benchmarks",
                        out_dir=tmp_path / "drafts") == []


@pytest.mark.parametrize("url,resolved", [
    ("https://x.ai/pricing", ()),
    ("https://example.test/start", ("https://x.ai/pricing",)),
])
def test_draft_cli_refuses_cite_only_before_reading_source_text(tmp_path, capsys, url, resolved):
    change = tmp_path / "change.json"
    change.write_text(json.dumps({"url": url, "resolved_urls": list(resolved), "page": "probe",
                                  "kinds": [{"kind": "new_version", "evidence": MARK}]}))
    assert draft.main(["--change", str(change), "--source-text", str(tmp_path / "absent-source.txt"),
                       "--bench-dir", str(tmp_path / "absent-benchmarks"), "--dry-run",
                       "--out-dir", str(tmp_path / "drafts")]) == 1
    assert MARK not in capsys.readouterr().out
    assert not (tmp_path / "drafts").exists()


@pytest.mark.parametrize("form", ["xai", "redirect", "control"])
def test_proposal_gate_refuses_restored_cite_only_accepted_manifests(tmp_path, form):
    url, resolved = FORMS[form]
    item = {"page": "probe", "url": url, "resolved_urls": list(resolved),
            "accepted": True, "changed": True, "draft_path": str(tmp_path / "absent-draft.md"),
            "kinds": [{"kind": "new_version", "evidence": MARK}],
            "errors": [MARK], "sources": [], "validator": "ok", "drafter": "offline fixture"}
    planned, skipped = propose.plan([item])
    out = tmp_path / "proposals.md"
    propose.write_dry_run([item], out, "2026-10-19")
    if form == "control":
        assert planned == [item] and skipped == []
        assert MARK in out.read_text()
    else:
        assert planned == [] and skipped == [item]
        assert MARK not in out.read_text()


def test_draft_cli_does_not_rewrite_cite_only_snippets_from_prior_manifest(tmp_path):
    change = tmp_path / "change.json"
    change.write_text(json.dumps({"url": "https://x.ai/pricing", "page": "probe", "kinds": []}))
    previous = {"url": "https://example.test/old", "resolved_urls": ["https://x.ai/pricing"],
                "page": "probe", "kinds": [{"kind": "new_version", "evidence": MARK}],
                "accepted": True, "changed": True, "errors": [MARK]}
    ordinary = {"url": "https://example.test/plain", "page": "other", "kinds": [], "accepted": False}
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps([previous, ordinary]))
    assert draft.main(["--change", str(change), "--source-text", str(tmp_path / "absent-source.txt"),
                       "--bench-dir", str(tmp_path / "absent-benchmarks"), "--dry-run",
                       "--manifest", str(manifest)]) == 1
    assert MARK not in manifest.read_text()
    items = json.loads(manifest.read_text())
    assert not items[0]["accepted"]
    assert items[1] == ordinary
