"""Guard: two removed sources must not come back (MODEL-117).

Artificial Analysis's terms do not permit this project's use of its data, so
every value sourced from artificialanalysis.ai and every benchmark it owns was
removed on 2026-09-24. Zapier is treated the same way by the same decision, so
every value sourced from zapier.com and the AutomationBench benchmark were
removed with it.

This guard, ``decision/excluded.py``, and the platform draft tests are the
only files that name either source. The checks cover tracked files, loaded
cards and pages, ranking tables,
and the JSON export. Set ``MODELSPEC_DIST`` to a built ``dist/`` to scan it too.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from api.ranking.engine import BENCHMARK_RANGES, USE_CASE_PROFILES, VERIFIED_ADDITIONS
from decision.excluded import (
    REMOVED_HOSTS,  # noqa: F401 - part of this guard's public test surface
    REMOVED_ID,
    REMOVED_TEXT,
    excluded_publisher,
    excluded_sources,
    without_legacy_source_keys,
)
from pipeline.load import REPO_ROOT, load_benchmarks, load_catalogue, load_models

#: A document that records the MODEL-117 decision may name the sources it is
#: about. Nothing else may.
ALLOWED = (
    Path(__file__).resolve().relative_to(REPO_ROOT).as_posix(),
    "decision/excluded.py",
    # The draft tests name both publishers in order to prove the drafts omit them.
    "tests/test_release_blog_platforms.py",
)
ALLOWED_GLOBS = ("docs/research/source-terms-*.md",)


def _removed_host(url: object) -> bool:
    return excluded_sources().url(url)


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
        visible = without_legacy_source_keys(text)
        if excluded_publisher(visible):
            hits.append(f"{rel}: excluded publisher")
            continue
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


@pytest.mark.parametrize(
    "text",
    [
        "Artificial Analysis",
        "Artificial  Analysis",
        "artificial-analysis",
        "artificial--analysis",
        "artificial_analysis",
        "artificial.analysis",
        "Artificial - Analysis",
        "ARTIFICIAL...ANALYSIS",
        "Zapier",
        "zapier",
        "Zap-ier",
        "zap_ier",
        "zap.ier",
        "Zap ier",
        "Z a p i e r",
    ],
)
def test_excluded_publishers_match_across_separators(text: str) -> None:
    assert excluded_publisher(text), text


def test_a_sentence_about_lighting_is_not_an_excluded_publisher() -> None:
    assert excluded_publisher("The artificial lighting analysis is separate.") is False


def test_the_legacy_source_field_key_is_not_a_publisher_name() -> None:
    assert REMOVED_TEXT.search("artificial_analysis_url: ''") is None


def test_mixed_separators_collapse_before_the_publisher_check() -> None:
    from decision.excluded import excluded_publisher

    assert excluded_publisher("Artificial - . Analysis")
    assert excluded_publisher("The artificial lighting analysis is separate.") is False


def test_a_glued_publisher_name_and_its_domains_are_excluded() -> None:
    from decision.excluded import excluded_publisher

    assert excluded_publisher("ArtificialAnalysisPro")
    assert excluded_publisher("artificialanalysis.ai")
    assert excluded_publisher("https://www.artificialanalysis.ai/models/x")
    assert excluded_publisher("zapier.com")
    assert excluded_publisher("https://zapier.com/apps")


def test_the_legacy_field_key_is_exempt_and_the_same_spelling_as_a_value_is_not() -> None:
    from decision.excluded import excluded_publisher, without_legacy_source_keys

    assert excluded_publisher("artificial_analysis_url") is True
    assert excluded_publisher(without_legacy_source_keys("artificial_analysis_url: ''")) is False
    assert (
        excluded_publisher(without_legacy_source_keys('{"artificial_analysis_url": ""}')) is False
    )
    assert excluded_publisher(without_legacy_source_keys("value artificial_analysis_url")) is True


@pytest.mark.parametrize(
    "text",
    [
        "Artificial - . Analysis",
        "Model Artificial - . Analysis",
        "ArtificialAnalysisPro",
        "artificialanalysis.ai",
        "zapier.com",
        "Zap - . ier",
    ],
)
def test_guard_output_and_lexicon_reject_collapsed_publishers(text: str) -> None:
    from pipeline.surface_lint import lexicon
    from release_blog.gates import BreakdownError, guard_output

    with pytest.raises(BreakdownError, match="excluded source"):
        guard_output({}, text)
    findings = [
        item
        for item in lexicon({"llms.txt": text}, {}, {})
        if item.check == "lexicon.removed-source"
    ]
    assert findings, text


def test_a_snapshot_refuses_a_fact_value_that_names_a_publisher() -> None:
    from decision.snapshot import SnapshotBuildError, build_snapshot
    from tests.snapshot_records import SOURCES, fact, model
    from tests.test_decision_snapshot import AS_OF, REGISTRY, inputs

    for payload in (
        "Artificial - . Analysis",
        "Model Artificial - . Analysis",
        "ArtificialAnalysisPro",
        "artificialanalysis.ai",
        "zapier.com",
    ):
        facts = [fact("model", "lab/alpha", "model.weights_openness", payload)]
        with pytest.raises(SnapshotBuildError, match="excluded source"):
            build_snapshot(
                inputs(
                    models=[model("lab/alpha", facts=facts)],
                    offerings=[],
                    evidence=[],
                    sources=SOURCES,
                ),
                registry=REGISTRY,
                as_of=AS_OF,
                guard=excluded_sources(),
            )


@pytest.mark.skipif(not os.environ.get("MODELSPEC_DIST"), reason="set MODELSPEC_DIST to a built dist/")
def test_a_built_dist_carries_no_removed_value() -> None:
    root = Path(os.environ["MODELSPEC_DIST"]).resolve()
    hits = _hits(root, [p for p in root.rglob("*") if p.is_file()])
    assert hits == [], "\n".join(hits[:40])
