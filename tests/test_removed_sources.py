"""Guard: two removed sources must not come back (MODEL-117).

Artificial Analysis's terms do not permit this project's use of its data, so
every value sourced from artificialanalysis.ai and every benchmark it owns was
removed on 2026-09-24. Zapier is treated the same way by the same decision, so
every value sourced from zapier.com and the AutomationBench benchmark were
removed with it.

This file is the one place in the repository that names either source. The
checks cover the tracked files (cards, benchmark pages, census and eligibility
evidence, code and docs), the loaded cards and pages, the ranking tables, and
the JSON the export writes. Set ``MODELSPEC_DIST`` to a built ``dist/`` to scan
that too.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from api.ranking.engine import BENCHMARK_RANGES, USE_CASE_PROFILES, VERIFIED_ADDITIONS
from pipeline.load import REPO_ROOT, load_benchmarks, load_catalogue, load_models

#: Hosts whose values must not appear, including any subdomain.
REMOVED_HOSTS = ("artificialanalysis.ai", "zapier.com")

#: Any mention of either source, or of the benchmarks they own. "Omniscience"
#: is matched as a bare name because that evaluator's hallucination benchmark
#: was once stored with its prefix dropped. Its column labels
#: ("Non-Hallucination", "Hallucination rate") are not matched: labs publish
#: their own evaluations under those names.
REMOVED_TEXT = re.compile(
    r"artificial[\s-]?analysis|zapier|automationbench|gdpval-aa|aa-lcr|aa[\s-]intelligence[\s-]index"
    r"|omniscience",
    re.IGNORECASE,
)

#: Benchmark ids the removed sources own: `aa_*`, `*_aa`, `artificial_analysis*`,
#: `artificialanalysis_*` and `automationbench*`.
REMOVED_ID = re.compile(r"^(aa_|artificial_?analysis|automationbench)|_aa$|_aa_")

#: A document that records the MODEL-117 decision may name the sources it is
#: about. Nothing else may.
ALLOWED = (
    Path(__file__).resolve().relative_to(REPO_ROOT).as_posix(),
)
ALLOWED_GLOBS = ("docs/research/source-terms-*.md",)


def _removed_host(url: object) -> bool:
    host = (urlsplit(str(url or "").strip()).hostname or "").lower().rstrip(".")
    return any(host == h or host.endswith("." + h) for h in REMOVED_HOSTS)


def _allowed(rel: str) -> bool:
    return rel in ALLOWED or any(Path(rel).match(g) for g in ALLOWED_GLOBS)


def _tracked_files() -> list[Path]:
    try:
        out = subprocess.run(["git", "ls-files", "-z"], cwd=REPO_ROOT, check=True,
                             capture_output=True).stdout.decode("utf-8")
        return [REPO_ROOT / p for p in out.split("\0") if p]
    except (OSError, subprocess.CalledProcessError):  # pragma: no cover - no git
        return [p for p in REPO_ROOT.rglob("*")
                if p.is_file() and ".git" not in p.parts and "node_modules" not in p.parts]


def _hits(root: Path, files: list[Path]) -> list[str]:
    hits = []
    for path in files:
        rel = path.relative_to(root).as_posix()
        if _allowed(rel) or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # binary: fonts, images, compressed corpora
        match = REMOVED_TEXT.search(text)
        if match:
            line = text.count("\n", 0, match.start()) + 1
            hits.append(f"{rel}:{line}: {match.group(0)}")
    return hits


def test_no_tracked_file_names_a_removed_source() -> None:
    hits = _hits(REPO_ROOT, _tracked_files())
    assert hits == [], "\n".join(hits[:40])


def test_no_card_carries_a_removed_value() -> None:
    bad = []
    for model in load_models(REPO_ROOT):
        block = model.front.get("benchmarks") or {}
        for key in (block.get("scores") or {}):
            if REMOVED_ID.search(str(key)):
                bad.append(f"{model.model_id}: score {key}")
        for row in block.get("evidence") or []:
            if _removed_host(row.get("source_url")) or REMOVED_ID.search(str(row.get("benchmark_id"))):
                bad.append(f"{model.model_id}: evidence {row.get('benchmark_id')} {row.get('source_url')}")
        sources = model.front.get("sources") or {}
        for key, value in (sources.items() if isinstance(sources, dict) else []):
            if _removed_host(value):
                bad.append(f"{model.model_id}: sources.{key}")
    assert bad == [], "\n".join(bad[:40])


def test_no_benchmark_page_or_eligibility_result_is_a_removed_source() -> None:
    assert [b.benchmark_id for b in load_benchmarks(REPO_ROOT) if REMOVED_ID.search(b.benchmark_id)] == []
    catalogue = load_catalogue(REPO_ROOT)
    for benchmark_id, disposition in catalogue.dispositions.items():
        assert not REMOVED_ID.search(benchmark_id), benchmark_id
        for result in disposition.results:
            assert not _removed_host(result.get("source_url")), (benchmark_id, result)


def test_the_ranking_tables_carry_no_removed_id() -> None:
    keys = set(BENCHMARK_RANGES)
    keys |= {b for bs in VERIFIED_ADDITIONS.values() for b in bs}
    for profile in USE_CASE_PROFILES.values():
        keys |= set(profile.get("benchmark_weights") or {})
    assert sorted(k for k in keys if REMOVED_ID.search(k)) == []


def test_the_export_carries_no_removed_value(tmp_path: Path) -> None:
    """The JSON the build publishes, written from the real cards and pages."""
    from pipeline import export as exporter
    from pipeline import ranking
    from schema.card import ModelCard
    from schema.graph import CollectingSink

    models = load_models(REPO_ROOT)
    benchmarks = load_benchmarks(REPO_ROOT)
    catalogue = load_catalogue(REPO_ROOT)
    build = exporter.make_build(catalogue, REPO_ROOT)
    exporter.write(tmp_path / "api", models, benchmarks, catalogue, build)
    cards = [ModelCard.from_yaml_file(m.path) for m in models]
    ranking.write_export(tmp_path / "api" / "rank", cards, CollectingSink(), build.to_json())
    files = [p for p in tmp_path.rglob("*") if p.is_file()]
    assert len(files) > len(models)
    assert _hits(tmp_path, files) == []


@pytest.mark.skipif(not os.environ.get("MODELSPEC_DIST"), reason="set MODELSPEC_DIST to a built dist/")
def test_a_built_dist_carries_no_removed_value() -> None:
    root = Path(os.environ["MODELSPEC_DIST"]).resolve()
    hits = _hits(root, [p for p in root.rglob("*") if p.is_file()])
    assert hits == [], "\n".join(hits[:40])
