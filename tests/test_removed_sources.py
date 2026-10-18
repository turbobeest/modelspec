"""Guard: two removed sources must not come back (MODEL-117).

Artificial Analysis's terms do not permit this project's use of its data, so
every value sourced from artificialanalysis.ai and every benchmark it owns was
removed on 2026-09-24. Zapier is treated the same way by the same decision, so
every value sourced from zapier.com and the AutomationBench benchmark were
removed with it.

This guard, ``decision/excluded.py``, and ``docs/research/source-terms-*.md``
are the only tracked files that may name either source. Other tests build
those strings at runtime. The checks cover tracked files, loaded cards and
pages, ranking tables, and the JSON export. Set ``MODELSPEC_DIST`` to a
built ``dist/`` to scan it too.
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
)
from pipeline.load import REPO_ROOT, load_benchmarks, load_catalogue, load_models

#: A document that records the MODEL-117 decision may name the sources it is
#: about. Nothing else may.
ALLOWED = (
    Path(__file__).resolve().relative_to(REPO_ROOT).as_posix(),
    "decision/excluded.py",
)
ALLOWED_GLOBS = ("docs/research/source-terms-*.md",)


def _removed_host(url: object) -> bool:
    return excluded_sources().url(url)


def _allowed(rel: str) -> bool:
    return rel in ALLOWED or any(Path(rel).match(g) for g in ALLOWED_GLOBS)


def _python_publisher(text: str) -> bool:
    import io
    import tokenize

    try:
        tokens = tokenize.generate_tokens(io.StringIO(text).readline)
        chunks = [
            token.string
            for token in tokens
            if token.type in {tokenize.STRING, tokenize.COMMENT}
        ]
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return excluded_publisher(text)
    return any(excluded_publisher(chunk) for chunk in chunks)


def _front_matter(text: str) -> tuple[str | None, str]:
    if not (text.startswith("---\n") or text.startswith("---\r\n")):
        return None, text
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "".join(lines[1:index]), "".join(lines[index + 1 :])
    return None, text


def _decoded_hit(obj: object) -> bool:
    """``excluded_in``, plus HTML entities inside string values.

    Keys are not decoded and are not rebuilt, so two keys that would look
    the same after decoding stay distinct. The legacy field key stays exempt.
    """
    import html

    from decision.excluded import each_string

    return any(excluded_publisher(html.unescape(item)) for item in each_string(obj))


def _html_publisher(text: str) -> bool:
    import html
    import json
    import re

    from pipeline.surface_lint import Page

    page = Page(text)
    if any(excluded_publisher(item) for item in (page.visible, page.title, *page.attribute_values)):
        return True
    pattern = re.compile(
        r"<script\b[^>]*type\s*=\s*[\"']application/ld\+json[\"'][^>]*>(.*?)</script>",
        re.IGNORECASE | re.DOTALL,
    )
    for blob in pattern.findall(text):
        try:
            parsed = json.loads(blob)
        except ValueError:
            if excluded_publisher(html.unescape(blob)):
                return True
            continue
        if _decoded_hit(parsed):
            return True
    return False


def _structured_publisher(path: Path, text: str) -> bool:
    """Catalogue walk. Prose is text. A mapping is parsed, and its keys are not decoded."""
    import html
    import json

    import yaml

    suffix = path.suffix.lower()
    if suffix == ".html":
        return _html_publisher(text)
    if suffix == ".json":
        try:
            parsed = json.loads(text)
        except ValueError:
            return excluded_publisher(html.unescape(text))
        return _decoded_hit(parsed)
    if suffix in {".yaml", ".yml"}:
        try:
            parsed = yaml.safe_load(text)
        except yaml.YAMLError:
            return excluded_publisher(html.unescape(text))
        if parsed is None:
            return False
        return _decoded_hit(parsed)
    if suffix == ".md":
        front, body = _front_matter(text)
        if front is not None:
            try:
                meta = yaml.safe_load(front)
            except yaml.YAMLError:
                meta = None
            if isinstance(meta, (dict, list)):
                return _decoded_hit(meta) or excluded_publisher(html.unescape(body))
        return excluded_publisher(html.unescape(text))
    return excluded_publisher(html.unescape(text))


def _publisher_hit(path: Path, text: str) -> bool:
    """Walk structured files. A source file's strings are values; its field names are not."""
    suffix = path.suffix.lower()
    structural = suffix in {".html", ".json", ".yaml", ".yml", ".md", ".py"}
    if suffix != ".html" and "&#" not in text and not excluded_publisher(text):
        return False
    if not structural:
        return excluded_publisher(text)
    if suffix == ".py":
        return _python_publisher(text)
    return _structured_publisher(path, text)


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
        if _publisher_hit(path, text):
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
    from decision.excluded import excluded_in, excluded_publisher

    assert excluded_publisher("artificial_analysis_url") is True
    assert excluded_in({"artificial_analysis_url": ""}) is False
    assert excluded_in('{"artificial_analysis_url": ""}') is True
    assert excluded_in({"value": "artificial_analysis_url"}) is True
    assert excluded_publisher("value artificial_analysis_url") is True


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


_PUBLISHER_PROBES = (
    "artificial_analysis_url: retained",
    "Artificial\nAnalysis",
    "Artificial\tAnalysis",
    "Zap\nier",
    "Zap\tier",
    "Artificial - . Analysis",
    "ArtificialAnalysisPro",
    "artificialanalysis.ai",
    "zapier.com",
)


def test_excluded_in_checks_every_string_except_the_legacy_key() -> None:
    """The key exemption is structural. Text that merely looks like the key is a value."""
    from decision.excluded import excluded_in

    assert excluded_in({"artificial_analysis_url": ""}) is False
    assert excluded_in({"artificial_analysis_url": "artificial_analysis_url: retained"}) is True
    assert excluded_in({"value": "artificial_analysis_url: retained"}) is True
    assert excluded_in("artificial_analysis_url: retained") is True
    assert excluded_in('{"artificial_analysis_url": ""}') is True
    assert excluded_in({"nested": ("ok", {"artificial_analysis_url": ""})}) is False
    for payload in _PUBLISHER_PROBES:
        assert excluded_in({"value": payload}) is True, payload
        assert excluded_in({payload: "kept"}) is True, payload


def test_guard_output_reads_serialized_values() -> None:
    import json

    from release_blog.gates import BreakdownError, guard_output

    guard_output({}, json.dumps({"artificial_analysis_url": ""}))
    guard_output({}, {"artificial_analysis_url": ""})
    for payload in _PUBLISHER_PROBES:
        with pytest.raises(BreakdownError, match="excluded source"):
            guard_output({}, {"value": payload})
        with pytest.raises(BreakdownError, match="excluded source"):
            guard_output({}, json.dumps({"value": payload}))


def test_every_separator_inside_a_json_value_is_excluded() -> None:
    import json
    from itertools import product

    from release_blog.gates import BreakdownError, guard_output

    runs = [
        "".join(parts)
        for length in range(1, 5)
        for parts in product(" \t\n-_.", repeat=length)
    ]
    assert len(runs) == 1554
    misses = []
    for left, right in (("Artificial", "Analysis"), ("Zap", "ier")):
        for sep in runs:
            for payload in (f"{left}{sep}{right}", f"Model {left}{sep}{right} name"):
                try:
                    guard_output({}, json.dumps({"value": payload}))
                except BreakdownError:
                    continue
                misses.append(payload)
    assert misses == [], f"{len(misses)} serialized values passed; first {misses[:3]!r}"


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


def test_a_snapshot_refuses_a_value_hidden_by_json_escaping() -> None:
    from decision.snapshot import SnapshotBuildError, build_snapshot
    from tests.snapshot_records import SOURCES, fact, model
    from tests.test_decision_snapshot import AS_OF, REGISTRY, inputs

    for payload in _PUBLISHER_PROBES:
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
