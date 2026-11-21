"""A live board on a cite-only host is read in memory and cited, never kept (MODEL-482)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from scripts import accuracy
from scripts import evidence_reread
from scripts import refresh_leaderboards as refresh

URL = "https://cursor.com/cursorbench"
OBSERVED = "2026-11-21"
LAST_SEEN = "2026-10-19"
TERMS = {"cursor.com": "forbids", "example.test": "permits"}
SOURCES_YAML = f"""schema_version: 1
sources:
- id: model-160-cursorbench
  volatility: live
  url: {URL}
  fetch: http
  normaliser: text-default
  kind: benchmark_author
  cited_regions:
  - id: rows
    locator: {{kind: page, value: ''}}
"""


def page(score: str = "46.6") -> bytes:
    return (
        "<table><tr><th>#</th><th>Model</th><th>Score</th><th>Cost</th></tr>"
        f"<tr><td>1</td><td>Orbit 9 Max</td><td>{score}%</td><td>$11.95</td></tr>"
        "<tr><td>2</td><td>Rival 1</td><td>40.0%</td><td>$3.00</td></tr></table>"
    ).encode()


def served(body: bytes, calls: list[str]):
    def request(url: str):
        calls.append(url)
        if url != URL:
            raise AssertionError(f"unexpected request: {url}")
        return 200, None, body
    return request


def files_under(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*") if p.is_file()) if root.exists() else []


def test_a_cite_only_board_is_read_in_memory_with_no_bytes_kept(monkeypatch, tmp_path: Path) -> None:
    cache, scratch = tmp_path / "cache", tmp_path / "scratch"
    scratch.mkdir()
    monkeypatch.setenv("MODELSPEC_SOURCE_CACHE", str(cache))
    monkeypatch.chdir(scratch)
    body, calls = page(), []
    monkeypatch.setattr(evidence_reread, "request_once", served(body, calls))
    monkeypatch.setattr(refresh, "_fetch", lambda *_a, **_k: (_ for _ in ()).throw(OSError("off")))

    def no_put(self, *_a, **_k):
        raise AssertionError("a cite-only board must not go through the copy store")

    monkeypatch.setattr(refresh.CopyStore, "put", no_put)
    boards, failures = refresh.collect_readings(
        OBSERVED, refresh.CopyStore(cache), (), skip_arena=True, terms=TERMS)

    cursor = next(board for board in boards if board.key == "cursorbench")
    assert cursor.cite_only is True
    assert cursor.snapshot_ref == "sha256:" + hashlib.sha256(body).hexdigest()
    assert calls == [URL]
    assert files_under(cache) == [] and files_under(scratch) == [] and files_under(tmp_path) == []
    assert not any(f.benchmark == "cursorbench_4" for f in failures)


def test_a_redirect_to_a_non_retaining_host_is_not_requested(monkeypatch) -> None:
    calls: list[str] = []

    def request(url: str):
        calls.append(url)
        return 302, "https://elsewhere.test/board", b""

    with pytest.raises(ValueError, match="deferred"):
        refresh.read_in_memory(URL, TERMS, request=request)
    assert calls == [URL]  # the redirect target was never asked for


CARD = f"""---
model_id: lab/orbit
display_name: Orbit 9
version: Orbit 9
benchmarks:
  evidence:
  - benchmark_id: cursorbench_4
    model_id_as_evaluated: Orbit 9 (max)
    score: 46.6
    unit: percent
    source_url: {URL}
    source_kind: benchmark_author
    evidence_date: '{LAST_SEEN}'
    date_type: evaluated
    observed_at: '{LAST_SEEN}'
    verified_at: '{LAST_SEEN}'
    effort: max
    id: lab/orbit#cursorbench_4#old
    sources:
    - source_id: model-160-cursorbench
      snapshot_ref: sha256:{"a" * 64}
      cited_regions: [rows]
---
prose stays
"""


def run_cited(monkeypatch, tmp_path: Path, body: bytes):
    root, cache = tmp_path / "repo", tmp_path / "copies"
    (root / "models" / "lab").mkdir(parents=True)
    (root / "registry").mkdir()
    (root / "verification").mkdir()
    (root / "registry" / "sources.yaml").write_text(SOURCES_YAML, encoding="utf-8")
    card = root / "models" / "lab" / "orbit.md"
    card.write_text(CARD, encoding="utf-8")
    monkeypatch.setenv("MODELSPEC_ARENA_REVISION", "pinned")
    ref = "sha256:" + hashlib.sha256(body).hexdigest()
    projected = refresh.readers.project_cursorbench(
        body.decode(), url=URL, page_ref=f"{ref} {URL}", read_date=OBSERVED)
    board = refresh._reading_from_projection(
        key="cursorbench", source_id="model-160-cursorbench", benchmarks=("cursorbench_4",),
        source_url=URL, projected=projected, observed_at=OBSERVED, value_field="accuracy",
        store=refresh.CopyStore(cache), card_urls=(URL,), page_ref=ref, cite_only=True)
    monkeypatch.setattr(refresh, "collect_readings", lambda *_a, **_k: ([board], []))
    report = refresh.run(observed_at=OBSERVED, dry_run=False, root=root, source_cache=cache,
                         model_ids=("lab/orbit",))
    front = yaml.safe_load(card.read_text(encoding="utf-8").split("---", 2)[1])
    return report, front["benchmarks"]["evidence"][0], ref, root, cache


def test_an_unchanged_cited_row_is_dated_by_the_read_and_carries_the_page_hash(
        monkeypatch, tmp_path: Path) -> None:
    report, row, ref, root, cache = run_cited(monkeypatch, tmp_path, page())

    assert report.failures == [] and report.quarantined == []
    assert row["score"] == 46.6
    assert row["observed_at"] == OBSERVED
    source = row["sources"][0]
    assert source["snapshot_ref"] == ref and source["cited_regions"] == ["rows"]
    assert str(source["retrieved_at"]).startswith(OBSERVED)
    assert files_under(cache) == []  # no bytes and no copy record
    assert files_under(root / "verification") == []  # no claim was filed against a copy

    # The freshness check counts the dated cited read as the observation.
    snapshot = SimpleNamespace(record=lambda _rid: row)
    live, observed = accuracy._live_observation_date(
        snapshot,
        SimpleNamespace(record_id="r", date_type="evaluated", source_kind="benchmark_author",
                        source_ids=("model-160-cursorbench",), date=row["evidence_date"]),
        {"model-160-cursorbench": SimpleNamespace(volatility="live")},
    )
    assert live is True and observed.isoformat() == OBSERVED


def test_a_cited_row_whose_value_differs_is_a_mismatch_alert_never_an_overwrite(
        monkeypatch, tmp_path: Path) -> None:
    report, row, _ref, _root, _cache = run_cited(monkeypatch, tmp_path, page("41.0"))

    assert row["score"] == 46.6 and row["observed_at"] == LAST_SEEN
    assert [f.reason.split(":")[0] for f in report.quarantined] == ["mismatch"]
    assert any("mismatch" in f.reason for f in report.failures)
    assert report.changes == []
