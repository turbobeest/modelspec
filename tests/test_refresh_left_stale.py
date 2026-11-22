"""MODEL-482: a refresh run reports live rows it left stale, and the workflow fails on them."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import yaml

from scripts import refresh_leaderboards as refresh

LIVE = SimpleNamespace(volatility="live")
STATIC = SimpleNamespace(volatility="static")
REGISTERED = {"live-src": LIVE, "static-src": STATIC}
WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "private-writers" / "leaderboard-refresh.yml"


def _row(benchmark: str, source: str, observed: str, **extra) -> dict:
    return {
        "benchmark_id": benchmark, "source_url": f"https://example.test/{benchmark}",
        "model_id_as_evaluated": "M", "score": 1.0,
        "sources": [{"source_id": source}], "observed_at": observed, **extra,
    }


def _stale(rows, refreshed=frozenset(), registered=REGISTERED):
    cards = {"a/m": {"benchmarks": {"evidence": rows}}}
    return refresh.left_stale_rows(cards, set(refreshed), registered, observed_at="2026-11-22")


def test_old_live_row_is_reported():
    found = _stale([_row("b1", "live-src", "2026-10-19")])
    assert [(f.model_id, f.benchmark) for f in found] == [("a/m", "b1")]
    assert "2026-10-19" in found[0].reason


def test_edge_of_the_stale_line():
    on_line = "2026-11-01"  # 21 days
    past_line = "2026-10-31"  # 22 days
    assert _stale([_row("b1", "live-src", on_line)]) == []
    assert len(_stale([_row("b1", "live-src", past_line)])) == 1


def test_the_stale_line_reads_dates_as_the_freshness_layer_does():
    from scripts import accuracy

    row = _row("b1", "live-src", "")
    row.pop("observed_at")
    row["source_snapshot"] = {"retrieved_at": "2026-10-01"}
    row["sources"][0]["observed_at"] = "2026-11-20"
    # observed_at is read across every container before retrieved_at, so the source's
    # fresh observed_at wins over the snapshot's old retrieved_at.
    assert _stale([row]) == []
    assert accuracy._observation_metadata_date(row) == refresh.observation_metadata_date(row)


def test_rewritten_marked_static_and_arena_rows_are_not_reported():
    rewritten = _row("b1", "live-src", "2026-10-01")
    key = refresh.evidence_key(rewritten)
    assert _stale([rewritten], refreshed={("a/m", key)}) == []
    assert _stale([_row("b2", "live-src", "2026-10-01", not_published_since="2026-11-01")]) == []
    assert _stale([_row("b3", "static-src", "2026-10-01")]) == []
    arena = _row("arena_text", "live-src", "2026-10-01",
                 source_url=refresh.ARENA_DATASET_ROOT)
    assert _stale([arena]) == []


def test_observation_day_falls_back_to_source_ref_then_verified_at():
    row = _row("b1", "live-src", "")
    row.pop("observed_at")
    row["sources"][0]["retrieved_at"] = "2026-10-01T00:00:00"
    assert len(_stale([row])) == 1
    row["sources"][0].pop("retrieved_at")
    row["verified_at"] = "2026-11-20"
    assert _stale([row]) == []


def test_report_renders_and_serialises_the_stale_rows(tmp_path):
    report = refresh.RefreshReport()
    report.left_stale = _stale([_row("b1", "live-src", "2026-10-19")])
    assert "Live rows left stale" in refresh.render_report(report)
    target = tmp_path / "report.json"
    refresh.write_report_json(target, report)
    assert '"left_stale"' in target.read_text()


def test_workflow_fails_a_run_that_left_a_live_row_stale():
    steps = yaml.safe_load(WORKFLOW.read_text())["jobs"]["refresh"]["steps"]
    result = next(step for step in steps if step.get("id") == "result")
    assert "left_stale=" in result["run"]
    gate = next(step for step in steps if step.get("name") == "Fail a run that left a live row stale")
    assert gate["if"] == "inputs.dry_run != true && steps.result.outputs.left_stale != '0'"
    assert "continue-on-error" not in gate and "exit 1" in gate["run"]
    # It runs after the pull request is opened, so the written rows are not lost.
    opened = next(i for i, s in enumerate(steps) if s.get("name") == "Open the score-only pull request")
    assert steps.index(gate) > opened


def test_workflow_links_the_private_terms_register_into_the_engine():
    steps = yaml.safe_load(WORKFLOW.read_text())["jobs"]["refresh"]["steps"]
    link = next(step for step in steps if step.get("name") == "Link the private source-terms register into the engine")
    assert "data/registry/source-terms.json" in link["run"]
    assert "engine/registry/source-terms.json" in link["run"]
    # A missing register stops the job rather than leaving the engine to guess.
    assert "is missing or a symlink" in link["run"]


def _root(tmp_path: Path, terms: str | None) -> Path:
    root = tmp_path / "repo"
    (root / "models").mkdir(parents=True)
    (root / "registry").mkdir()
    (root / "verification").mkdir()
    (root / "registry" / "sources.yaml").write_text("sources: []\n")
    if terms is not None:
        (root / "registry" / "source-terms.json").write_text(terms)
    return root


import pytest


@pytest.mark.parametrize("terms", [None, "{}"])
def test_run_stops_before_any_request_without_a_terms_register(monkeypatch, tmp_path, terms):
    from scripts import evidence_reread

    monkeypatch.setattr(refresh, "load_terms", evidence_reread.load_terms)
    monkeypatch.setattr(refresh, "collect_readings", lambda *a, **k: pytest.fail("a board was read"))
    with pytest.raises(ValueError, match="source-terms register"):
        refresh.run(observed_at="2026-11-22", dry_run=True, root=_root(tmp_path, terms),
                    source_cache=tmp_path / "copies")


def _page_files(copies: Path) -> list[Path]:
    """Files in the store that hold page bytes (citation and url records are metadata)."""
    return [p for p in copies.rglob("*") if p.is_file() and p.suffix not in {".json", ".jsonl"}]


def test_a_cite_only_page_never_reaches_the_copy_store(tmp_path):
    terms = {"epoch.ai": "cite-only", "cursor.com": "forbids", "example.test": "retaining"}
    store = refresh.TermsStore(tmp_path / "copies", terms)
    body = b"page bytes"
    for url in ("https://epoch.ai/data/benchmark_data.zip", "https://cursor.com/cursorbench"):
        ref = store.put(body, source_url=url)
        assert ref == refresh.fingerprint_bytes(body)
        assert not store.has(ref)
        assert store.citations(ref)  # the citation record CopyStore.put also makes
    assert _page_files(tmp_path / "copies") == []
    assert store.has(store.put(b"retained page", source_url="https://example.test/board"))


def test_a_board_on_a_cite_only_host_is_cited_by_the_page_hash_with_no_copy(tmp_path):
    store = refresh.TermsStore(tmp_path / "copies", {"andonlabs.com": "cite-only"})
    projected = refresh.readers.document(
        [{"model": "M", "money_balance": "1 USD"}], url="https://andonlabs.com/evals/x",
        page_ref="p", read_date="2026-11-22", note="n")
    page = b"the page"
    board = refresh._reading_from_projection(
        key="vending", source_id="s", benchmarks=("vending_bench_2",),
        source_url="https://andonlabs.com/evals/x", projected=projected,
        observed_at="2026-11-22", value_field="money_balance", store=store,
        raw_ref=refresh.fingerprint_bytes(page))
    assert board.cite_only is True
    assert board.snapshot_ref == refresh.fingerprint_bytes(page)  # the page, not the projection
    assert _page_files(tmp_path / "copies") == []
    with pytest.raises(ValueError, match="page's own hash"):
        refresh._reading_from_projection(
            key="vending", source_id="s", benchmarks=("vending_bench_2",),
            source_url="https://andonlabs.com/evals/x", projected=projected,
            observed_at="2026-11-22", value_field="money_balance", store=store)


def test_the_register_is_found_under_the_data_dir_before_the_engine_root(monkeypatch, tmp_path):
    root = _root(tmp_path, None)
    data = tmp_path / "data"
    (data / "registry").mkdir(parents=True)
    (data / "registry" / "source-terms.json").write_text('{"epoch.ai": "cite-only"}')
    monkeypatch.delenv("MODELSPEC_DATA_DIR", raising=False)
    assert refresh.load_terms(root) == {}
    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(data))
    assert refresh.load_terms(root) == {"epoch.ai": "cite-only"}


def test_a_held_back_board_is_read_in_memory_with_the_data_dir_set(monkeypatch, tmp_path):
    """MODELSPEC_DATA_DIR makes ``_fetch`` refuse every held-back host; the board read must not."""
    from scripts import evidence_reread

    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(tmp_path))
    terms = {"andonlabs.com": "cite-only", "labs.scale.com": "cite-only"}
    calls: list[str] = []

    def served(url):
        calls.append(url)
        return 200, None, b"body"

    monkeypatch.setattr(evidence_reread, "request_once", served)
    monkeypatch.setattr(refresh, "_fetch", lambda *a, **k: pytest.fail("went through _fetch"))
    assert refresh._fetch_board("https://andonlabs.com/evals/vending-bench-2", terms) == b"body"
    # The one declared Scale Pro redirect is read at its declared address, never followed.
    assert refresh._fetch_board(refresh.readers.SCALE_URL, terms, scale_pro=True) == b"body"
    assert calls == ["https://andonlabs.com/evals/vending-bench-2", refresh.SCALE_PRO_FINAL]


def test_a_cite_only_read_never_requests_a_redirect_target(monkeypatch):
    calls: list[str] = []

    def redirecting(url):
        calls.append(url)
        return 301, "https://retaining.example/x", b""

    with pytest.raises(ValueError, match="not followed"):
        refresh.read_in_memory("https://epoch.ai/a", {"epoch.ai": "cite-only",
                                                      "retaining.example": "retaining"},
                               request=redirecting)
    assert calls == ["https://epoch.ai/a"]
