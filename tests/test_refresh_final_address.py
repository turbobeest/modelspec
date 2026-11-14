"""A live-board read that ends on another address than the declared one fails (MODEL-493-B).

No network: a stub transport sits under the real redirect machinery.
"""

from __future__ import annotations

import ast
import gzip
import io
import json
import urllib.error
import urllib.request
import urllib.response
from email.message import Message
from pathlib import Path

import pytest

from decision.sources import CopyStore
from scripts import refresh_leaderboards as refresh
from tests.test_leaderboard_refresh import FINANCE_CARDS, FIXTURES, _finance_repo

OBSERVED = "2026-11-14"
PINNED = "a" * 40
CDN = "https://us.aws.cdn.hf.co/repos/xx/file.parquet"
TBENCH = refresh.TBENCH_URL
FINBENCH_PAGE = gzip.decompress((FIXTURES / "finbenchmark_2026-09-29.html.gz").read_bytes())


def _install(monkeypatch, table: dict[str, tuple[int, bytes | str]]):
    """Serve ``table``: url -> (200, body) or (redirect code, location). Others are unreachable."""
    calls: list[str] = []

    class Transport(urllib.request.HTTPSHandler):
        def https_open(self, request):
            calls.append(request.full_url)
            if request.full_url not in table:
                raise urllib.error.URLError(f"offline: {request.full_url}")
            code, payload = table[request.full_url]
            headers = Message()
            body = b""
            if code == 200:
                body = payload
            else:
                headers["Location"] = payload
            response = urllib.response.addinfourl(io.BytesIO(body), headers, request.full_url, code)
            response.msg = "OK" if code == 200 else "Moved"
            return response

    build_opener = urllib.request.build_opener
    monkeypatch.setattr(urllib.request, "build_opener",
                        lambda *handlers: build_opener(*handlers, Transport()))
    return calls


def _collect(tmp_path, **kwargs):
    return refresh.collect_readings(OBSERVED, CopyStore(tmp_path / "copies"), [], **kwargs)


def _failure(failures, source):
    return [row for row in failures if row.source == source]


# ── (a) a declared address that redirects fails and files nothing ───────────

def test_redirect_to_root_fails_the_board_and_files_nothing(monkeypatch, tmp_path):
    root = _finance_repo(tmp_path)
    cards = {m: (root / "models" / f"{m}.md") for m in FINANCE_CARDS}
    before = {m: p.read_bytes() for m, p in cards.items()}
    final = "https://finbenchmark.ai/other"
    _install(monkeypatch, {refresh.FINBENCH_URL: (308, final), final: (200, FINBENCH_PAGE)})

    report = refresh.run(observed_at=OBSERVED, dry_run=False, root=root,
                         source_cache=tmp_path / "copies")

    expected = f"redirected: declared {refresh.FINBENCH_URL}, final {final}"
    assert [row.reason for row in _failure(report.failures, refresh.FINBENCH_URL)] == [expected]
    assert "finbenchmark" not in report.boards
    assert report.changes == [] and report.reconfirmed == []
    assert {m: p.read_bytes() for m, p in cards.items()} == before
    assert not (root / "verification" / "log.jsonl").exists()
    assert expected in refresh.render_report(report)
    out = tmp_path / "report.json"
    refresh.write_report_json(out, report)
    listed = json.loads(out.read_text(encoding="utf-8"))["failures"]
    assert {"model_id": "*", "benchmark": "finance_benchmark_v2",
            "source": refresh.FINBENCH_URL, "reason": expected} in listed


def test_other_boards_in_the_run_are_unaffected(monkeypatch, tmp_path):
    final = "https://www.tbench.ai/leaderboard/terminal-bench/4.2"
    _install(monkeypatch, {TBENCH: (308, final), final: (200, b"<html>4.2</html>"),
                           refresh.FINBENCH_URL: (200, FINBENCH_PAGE)})
    readings, failures = _collect(tmp_path, skip_arena=True)
    assert [r.key for r in readings] == ["finbenchmark"]
    assert [row.reason for row in _failure(failures, TBENCH)] == [
        f"redirected: declared {TBENCH}, final {final}"]
    assert all(not row.reason.startswith("redirected") for row in failures
               if row.source != TBENCH)


# ── (b) no redirect: unchanged ───────────────────────────────────────────────

def test_a_read_with_no_redirect_is_unchanged(monkeypatch):
    _install(monkeypatch, {refresh.FINBENCH_URL: (200, b"body")})
    assert refresh._fetch(refresh.FINBENCH_URL) == b"body"


# ── (c) Arena ────────────────────────────────────────────────────────────────

def _pinned(config="text"):
    return refresh.readers.arena_parquet_url(config, PINNED)


def test_pinned_arena_address_ending_on_a_hf_cdn_host_is_read(monkeypatch):
    _install(monkeypatch, {_pinned(): (302, CDN), CDN: (200, b"parquet")})
    assert refresh._fetch_arena(_pinned()) == b"parquet"


@pytest.mark.parametrize("final", [
    "https://evil.example/file.parquet",
    "https://hf.co.evil.example/file.parquet",
    "https://evilhf.co/file.parquet",
    "https://huggingface.co/other/file.parquet",
])
def test_pinned_arena_address_ending_elsewhere_fails(monkeypatch, final):
    _install(monkeypatch, {_pinned(): (302, final), final: (200, b"x")})
    with pytest.raises(refresh.RedirectedRead) as error:
        refresh._fetch_arena(_pinned())
    assert (error.value.requested, error.value.final) == (_pinned(), final)


def test_unpinned_arena_address_that_redirects_fails(monkeypatch):
    unpinned = _pinned().replace(PINNED, "main")
    _install(monkeypatch, {unpinned: (302, CDN), CDN: (200, b"parquet")})
    with pytest.raises(refresh.RedirectedRead):
        refresh._fetch_arena(unpinned)


def test_the_cdn_rule_is_https_only_and_suffix_only():
    assert refresh.accept_arena_cdn(_pinned(), "https://us.aws.cdn.hf.co/x")
    assert refresh.accept_arena_cdn(_pinned(), "https://hf.co/x")
    assert not refresh.accept_arena_cdn(_pinned(), "http://us.aws.cdn.hf.co/x")
    assert not refresh.accept_arena_cdn(_pinned(), "https://us.aws.cdn.hf.co.evil.example/x")


def test_arena_collect_reports_a_foreign_final_address(monkeypatch, tmp_path):
    table = {}
    for config in sorted({c for c, _ in refresh.ARENA_BOARDS.values()}):
        url = refresh.readers.arena_parquet_url(config, PINNED)
        table[url] = (302, "https://evil.example/x")
    table["https://evil.example/x"] = (200, b"x")
    _install(monkeypatch, table)
    _, failures = _collect(tmp_path, arena_revision=PINNED)
    arena = [row for row in failures if row.benchmark.startswith("arena:")]
    assert arena and all(row.reason.startswith("redirected: declared ") for row in arena)


def test_arena_collect_accepts_the_cdn(monkeypatch, tmp_path):
    table = {CDN: (200, b"not a parquet file")}
    for config in sorted({c for c, _ in refresh.ARENA_BOARDS.values()}):
        table[refresh.readers.arena_parquet_url(config, PINNED)] = (302, CDN)
    _install(monkeypatch, table)
    _, failures = _collect(tmp_path, arena_revision=PINNED)
    assert not [row for row in failures if row.reason.startswith("redirected")]


# ── (d) Scale ────────────────────────────────────────────────────────────────

def test_scale_exact_final_address_is_read(monkeypatch):
    _install(monkeypatch, {refresh.readers.SCALE_URL: (308, refresh.SCALE_PRO_FINAL),
                           refresh.SCALE_PRO_FINAL: (200, b"page")})
    assert refresh._fetch_scale_pro(refresh.readers.SCALE_URL) == b"page"


@pytest.mark.parametrize("final", [
    "https://labs.scale.com/",
    "https://labs.scale.com/leaderboard/swe_bench_pro_commercial",
    "https://labs.scale.com/leaderboard/swe_bench_pro/",
])
def test_scale_any_other_final_address_fails(monkeypatch, final):
    _install(monkeypatch, {refresh.readers.SCALE_URL: (308, final), final: (200, b"page")})
    with pytest.raises(refresh.RedirectedRead):
        refresh._fetch_scale_pro(refresh.readers.SCALE_URL)


def test_scale_exception_does_not_cover_other_requests(monkeypatch):
    other = "https://labs.scale.com/leaderboard/humanitys_last_exam"
    _install(monkeypatch, {other: (308, refresh.SCALE_PRO_FINAL),
                           refresh.SCALE_PRO_FINAL: (200, b"page")})
    with pytest.raises(refresh.RedirectedRead):
        refresh._fetch_scale_pro(other)
    _install(monkeypatch, {refresh.readers.SCALE_URL: (308, refresh.SCALE_PRO_FINAL),
                           refresh.SCALE_PRO_FINAL: (200, b"page")})
    with pytest.raises(refresh.RedirectedRead):
        refresh._fetch(refresh.readers.SCALE_URL)


def test_scale_collect_failure_names_both_addresses(monkeypatch, tmp_path):
    final = "https://labs.scale.com/"
    _install(monkeypatch, {refresh.readers.SCALE_URL: (308, final), final: (200, b"page")})
    _, failures = _collect(tmp_path, skip_arena=True)
    assert [row.reason for row in _failure(failures, refresh.readers.SCALE_URL)] == [
        f"redirected: declared {refresh.readers.SCALE_URL}, final {final}"]


# ── (e) a cite-only final address keeps the existing refusal ─────────────────

def test_cite_only_final_address_is_refused_not_reported_as_redirected(monkeypatch, tmp_path):
    restricted = "https://docs.x.ai/models"
    _install(monkeypatch, {TBENCH: (302, restricted), restricted: (200, b"x")})
    with pytest.raises(ValueError, match="cite-only") as error:
        refresh._fetch(TBENCH)
    assert not isinstance(error.value, refresh.RedirectedRead)
    _, failures = _collect(tmp_path, skip_arena=True)
    reasons = [row.reason for row in _failure(failures, TBENCH)]
    assert len(reasons) == 1 and reasons[0].startswith("ValueError: cite-only")


# ── (f) every use of _fetch is the default or one of the two declarations ────

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
DECLARED = {"accept_arena_cdn": "_fetch_arena", "accept_scale_pro_final": "_fetch_scale_pro"}


def _files_using_fetch():
    for path in sorted(SCRIPTS.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        if path.name == "refresh_leaderboards.py":
            yield path, tree
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "scripts.refresh_leaderboards" \
                    and any(alias.name == "_fetch" for alias in node.names):
                yield path, tree
                break


class _Uses(ast.NodeVisitor):
    def __init__(self):
        self.stack: list[str] = []
        self.calls: list[tuple[str, list[str]]] = []
        self.references: list[str] = []

    def visit_FunctionDef(self, node):
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == "_fetch":
            kwargs = [ast.unparse(k.value) if k.arg == "accept_final" else f"!{k.arg}"
                      for k in node.keywords]
            self.calls.append((self.stack[-1] if self.stack else "", kwargs))
            for arg in node.args + [k.value for k in node.keywords]:
                self.visit(arg)
            return
        self.generic_visit(node)

    def visit_Name(self, node):
        if node.id == "_fetch" and isinstance(node.ctx, ast.Load):
            self.references.append(self.stack[-1] if self.stack else "")


def test_every_fetch_use_is_the_default_or_a_declared_exception():
    declared: dict[str, str] = {}
    scanned = []
    for path, tree in _files_using_fetch():
        scanned.append(path.name)
        uses = _Uses()
        uses.visit(tree)
        for function, kwargs in uses.calls:
            if kwargs:
                assert len(kwargs) == 1 and kwargs[0] in DECLARED, (path.name, function, kwargs)
                assert function == DECLARED[kwargs[0]], (path.name, function, kwargs)
                declared[kwargs[0]] = function
        if path.name == "refresh_leaderboards.py":
            # ``_fetch`` named but not called: handed to the revision resolver (in choose_arena_revision) and
            # the default reader of ``collect``.
            assert sorted(set(uses.references) - {fn for fn, _ in uses.calls}) == ["choose_arena_revision", "collect"]
            assert sum(1 for _, kwargs in uses.calls if not kwargs) == 7
    assert declared == DECLARED
    assert "refresh_leaderboards.py" in scanned and "model_233_matharena.py" in scanned
