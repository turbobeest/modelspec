"""Extractable guides teach the method with a dated, engine-computed example."""

from collections import Counter
from datetime import date
import json
from pathlib import Path
import re
import socket

import pytest

from decision import registry, snapshot
from decision.contract import DEFAULT_TASK_TOKENS, parse_spec
from decision.engine import decide
from decision.excluded import REMOVED_TEXT
from decision.templates import load_catalogue
from pipeline import build, entity, live, surface_lint
from tests.snapshot_records import SOURCES, evidence, fact, model, offering

ROOT = Path(__file__).resolve().parents[1]
CHOOSE = "/guides/how-to-choose-an-ai-model/"
COMPARE = "/guides/analysis-of-alternatives-vs-model-router-vs-hard-coded-model/"
PATHS = ("/guides/", CHOOSE, COMPARE)
DAY = date(2026, 9, 23)


def _image(price: float, *, additional_models: int = 0, excluded_models: int = 0):
    models, offerings, measurements = [], [], []
    candidates = [("alpha", "text-generator", price),
                  ("beta", "text-generator", 0.5),
                  ("costly", "text-generator", 10),
                  ("image", "image-generator", 0.5)]
    candidates.extend((f"extra-{index:02}", "text-generator", 0.5)
                      for index in range(additional_models))
    candidates.extend((f"excluded-{index:03}", "text-generator", 10)
                      for index in range(excluded_models))
    for name, kind, rate in candidates:
        mid = "lab/" + name
        models.append(model(mid, facts=[
            fact("model", mid, "model.class", kind),
            fact("model", mid, "model.lifecycle", "active"),
            fact("model", mid, "model.context_window", 256000),
        ]))
        oid = f"lab/{mid}/global/standard"
        offerings.append(offering(mid, "lab", facts=[
            fact("offering", oid, "offering.price.input", rate, source="src-pricing"),
            fact("offering", oid, "offering.price.output", 1, source="src-pricing"),
        ]))
        for benchmark in ("swe_bench_verified", "swe_bench_pro", "terminal_bench"):
            measurements.append(evidence(mid, benchmark, 70 if name in ("alpha", "beta") else 40))
    return snapshot.build_snapshot(snapshot.SnapshotInputs(
        models=models, offerings=offerings, evidence=measurements, sources=SOURCES,
        benchmark_domains={key: [("software_engineering", "direct")] for key in
                           ("swe_bench_verified", "swe_bench_pro", "terminal_bench")},
        benchmark_metadata={key: {"unit": "percent"} for key in
                            ("swe_bench_verified", "swe_bench_pro", "terminal_bench")},
    ), gate=False, as_of=DAY)


@pytest.fixture
def image_root(tmp_path, monkeypatch):
    root = tmp_path / "public"
    root.mkdir()
    (root / "data-image.json").write_text(json.dumps({"as_of": DAY.isoformat()}))
    (root / "registry").symlink_to(ROOT / "registry", target_is_directory=True)
    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(tmp_path / "private-must-not-be-read"))
    monkeypatch.setattr(socket, "create_connection", lambda *a, **kw: pytest.fail("Network access"))
    return root


def _expected(built):
    facets = registry.load(ROOT / "registry", repo_root=ROOT).facet
    template = next(t for t in load_catalogue()["templates"] if t["id"] == "budget-coding")
    spec = parse_spec(template["spec"], facets=facets)
    decision = decide(spec, snapshot.load_built_snapshot(built, include_archive=True), facets=facets)
    return template, spec, decision.model_dump(mode="json")


def _exclusions(built):
    facets = registry.load(ROOT / "registry", repo_root=ROOT).facet
    template = next(t for t in load_catalogue()["templates"] if t["id"] == "budget-coding")
    spec = parse_spec({**template["spec"], "explain": "full"}, facets=facets)
    decision = decide(spec, snapshot.load_built_snapshot(built, include_archive=True), facets=facets)
    return decision.model_dump(mode="json")["eliminated"]["models"]


def _write_pages(tree, public_root):
    from pipeline import guides

    with build.public_use_case_image(public_root) as (catalogue, decisions, as_of, image, reg):
        template = next(t for t in catalogue["templates"] if t["id"] == "budget-coding")
        exclusions = build.use_case_exclusions(template, image, reg)
        build.write_use_case_pages(tree, public_root, examples=(catalogue, decisions, as_of),
                                   exclusions={template["id"]: exclusions})
        return guides.write_examples(tree, catalogue, decisions, as_of, image, reg,
                                     exclusions=exclusions)


def _rows(raw, table_id):
    match = re.search(rf'<table\b[^>]*id="{table_id}"[^>]*>(.*?)</table>', raw, re.S)
    assert match, f"Missing {table_id} table"
    return [[surface_lint.Page(cell).visible for cell in re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>', row, re.S)]
            for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>', match[1], re.S)]


@pytest.fixture
def rendered(tmp_path, monkeypatch, image_root):
    built = _image(0.5)
    monkeypatch.setattr(snapshot, "build_from_repo", lambda *a, **kw: built)
    tree = tmp_path / "site"
    result = _write_pages(tree, image_root)
    pages = {path: (tree / path.lstrip("/") / "index.html").read_text() for path in PATHS}
    return tree, result, pages, _expected(built)


def test_swapping_public_image_changes_engine_numbers_and_exclusions(tmp_path, monkeypatch, image_root):
    from pipeline import guides

    rendered_rows = []
    for index, price in enumerate((0.5, 2.0)):
        built = _image(price)
        monkeypatch.setattr(snapshot, "build_from_repo", lambda *a, **kw: built)
        tree = tmp_path / str(index)
        guides.write(tree, image_root)
        raw = (tree / CHOOSE.lstrip("/") / "index.html").read_text()
        _, spec, decision = _expected(built)
        page = surface_lint.Page(raw)
        rows = _rows(raw, "example-results")[1:]
        entries = [entry for band in ("best", "rest", "thin") for entry in decision["bands"][band]]
        assert entries
        expected = [[surface_lint.Page(build._use_case_value(entry[field])).visible
                     for field in ("score", "score_interval", "p_best", "cost_per_task")]
                    for entry in entries]
        assert [row[2:] for row in rows] == expected
        assert decision["snapshot"] in page.visible
        assert decision["decision_id"] in page.visible
        assert decision["bands"]["basis"] in page.visible
        tokens = spec.task_tokens or DEFAULT_TASK_TOKENS
        assert f"{tokens.input} input tokens" in page.visible
        assert f"{tokens.output} output tokens" in page.visible
        reasons = _exclusions(built)
        counts = {row[0]: int(row[1]) for row in _rows(raw, "example-exclusion-counts")[1:]}
        assert counts == Counter(reason["condition"] for reason in reasons)
        excluded = _rows(raw, "example-excluded")[1:]
        assert len(excluded) == min(10, len(reasons))
        for row, reason in zip(excluded, reasons[:10], strict=True):
            assert row[2] == reason["condition"]
            assert row[3] == surface_lint.Page(build._use_case_value(reason["value"])).visible
        rendered_rows.append((rows, counts))
    assert rendered_rows[0][0] != rendered_rows[1][0]
    assert sum(rendered_rows[1][1].values()) > sum(rendered_rows[0][1].values())


@pytest.mark.parametrize("identifier", ["dec_", "snap_"])
def test_guide_and_linked_use_case_have_same_identifiers(rendered, identifier):
    tree, _, pages, _ = rendered
    use_case = (tree / "use-cases/coding/budget-coding/index.html").read_text()
    pattern = rf"{identifier}[a-z0-9]+"
    guide_ids = set(re.findall(pattern, surface_lint.Page(pages[CHOOSE]).visible))
    use_case_ids = set(re.findall(pattern, surface_lint.Page(use_case).visible))
    assert len(guide_ids) == len(use_case_ids) == 1
    assert guide_ids == use_case_ids


def test_guide_and_linked_use_case_have_same_scores_probability_and_cost(rendered):
    tree, _, pages, _ = rendered
    use_case = (tree / "use-cases/coding/budget-coding/index.html").read_text()
    use_case_rows = [
        [surface_lint.Page(cell).visible for cell in re.findall(r'<td\b[^>]*>(.*?)</td>', row, re.S)]
        for table in re.findall(r'<table\b[^>]*>(.*?)</table>', use_case, re.S)
        if '<th>P(best)</th>' in table
        for body in re.findall(r'<tbody>(.*?)</tbody>', table, re.S)
        for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>', body, re.S)
    ]
    assert use_case_rows
    assert [row[2:] for row in _rows(pages[CHOOSE], "example-results")[1:]] == [
        row[1:5] for row in use_case_rows
    ]


def test_large_screened_out_list_stays_a_short_explainer(tmp_path, monkeypatch, image_root):
    from pipeline import guides

    built = _image(0.5, excluded_models=400)
    monkeypatch.setattr(snapshot, "build_from_repo", lambda *a, **kw: built)
    guides.write(tmp_path / "site", image_root)
    raw = (tmp_path / "site" / CHOOSE.lstrip("/") / "index.html").read_text()
    page = surface_lint.Page(raw)
    reasons = _exclusions(built)
    assert len(reasons) > 400
    assert len(page.visible.split()) <= 3000
    assert 1 <= len(_rows(raw, "example-excluded")[1:]) <= 15
    counts = {row[0]: int(row[1]) for row in _rows(raw, "example-exclusion-counts")[1:]}
    assert counts == Counter(reason["condition"] for reason in reasons)
    assert "/use-cases/coding/budget-coding/#screened-out" in page.links


def test_guide_links_to_full_screened_out_list_on_use_case(rendered):
    tree, _, pages, _ = rendered
    use_case = (tree / "use-cases/coding/budget-coding/index.html").read_text()
    reasons = _exclusions(_image(0.5))
    assert 'id="screened-out"' in use_case
    assert len(_rows(use_case, "use-case-excluded")[1:]) == len(reasons)
    assert "/use-cases/coding/budget-coding/#screened-out" in surface_lint.Page(pages[CHOOSE]).links


def test_example_has_exact_public_image_label_tie_rules_and_template_link(rendered):
    _, _, pages, (template, _, decision) = rendered
    page = surface_lint.Page(pages[CHOOSE])
    label = f"Worked example as of {DAY.isoformat()}, from the public data image."
    assert label in page.visible
    assert label in surface_lint.Page(build.use_case_page(template, decision, DAY)).visible
    assert "delayed" in page.visible.lower()
    assert "/decide/?template=budget-coding" in page.links
    assert "/use-cases/coding/budget-coding/" in page.links
    assert "Tie-breakers describe members of the tie" in page.visible
    assert "They do not establish a winner" in page.visible
    assert "USD" in page.visible and "Unavailable" in page.visible
    assert "engine-selected offering" in page.visible
    assert "screened out" in page.visible.lower()


def test_guide_keeps_every_band_model_when_results_are_truncated(tmp_path, monkeypatch, image_root):
    from pipeline import guides

    built = _image(0.5, additional_models=23)
    _, _, decision = _expected(built)
    entries = [entry for band in ("best", "rest", "thin") for entry in decision["bands"][band]]
    assert decision["truncated"]["models"] > 0
    assert len(entries) > len(decision["results"])
    monkeypatch.setattr(snapshot, "build_from_repo", lambda *a, **kw: built)
    guides.write(tmp_path / "site", image_root)
    raw = (tmp_path / "site" / CHOOSE.lstrip("/") / "index.html").read_text()
    rows = _rows(raw, "example-results")[1:]
    assert len(rows) == len(entries)
    assert len({row[0] for row in rows}) == len(entries)
    assert all(row[0].startswith("Alternative ") for row in rows)
    assert [row[2:] for row in rows] == [
        [surface_lint.Page(build._use_case_value(entry[field])).visible
         for field in ("score", "score_interval", "p_best", "cost_per_task")]
        for entry in entries
    ]
    assert all(entry["model"] not in raw for entry in entries)


def test_guides_compare_categories_without_product_names(rendered):
    _, _, pages, (_, _, decision) = rendered
    excluded = _exclusions(_image(0.5))
    denylist = ["".join(parts).casefold() for parts in (
        ("Open", "Router"), ("Lite", "LLM"), ("Port", "key"), ("Not ", "Diamond"),
        ("Route", "LLM"), ("Chat", "GPT"), ("Clau", "de"), ("Gemi", "ni"),
    )]
    for raw in pages.values():
        assert not REMOVED_TEXT.search(raw)
        assert not any(name in raw.casefold() for name in denylist)
        assert all(row["model"] not in raw for row in decision["by_model"])
        assert all(row["model"] not in raw for row in excluded)
        assert not re.search(r"affiliate|sponsored", raw, re.I)
    rows = _rows(pages[COMPARE], "category-comparison")
    assert rows[0] == ["Question", "Analysis of alternatives", "Model router", "Hard-coded model"]
    assert len(rows) == 9
    assert all(len(row) == 4 for row in rows)
    page = surface_lint.Page(pages[COMPARE])
    assert "A router is the better tool for per-request routing on live traffic" in page.visible
    assert "A hard-coded model is the better tool when one model already fits and change is costly" in page.visible


def test_guides_have_dated_sitemap_entries_and_visible_structured_data(rendered):
    _, result, pages, _ = rendered
    assert set(result["sitemap_paths"]) == set(PATHS)
    assert result["sitemap_dates"] == {path: DAY.isoformat() for path in PATHS}
    sitemap = build.r.sitemap(entity.SITE, result["sitemap_paths"], DAY,
                              lastmods=result["sitemap_dates"])
    assert dict(surface_lint.sitemap_entries(sitemap)) == {
        entity.SITE + path: DAY.isoformat() for path in PATHS
    }
    for path in (CHOOSE, COMPARE):
        page = surface_lint.Page(pages[path])
        nodes = [node for block in page.ld for node in surface_lint.objects(json.loads(block))]
        article = next(node for node in nodes if node.get("@type") == "Article")
        assert article["headline"] in page.visible
        assert article["dateModified"] == DAY.isoformat()
        assert article["dateModified"] in page.visible
        assert article["url"] == entity.SITE + path
        assert not surface_lint.structured_data({path.lstrip("/") + "index.html": pages[path]})
        terms = [node for node in nodes if node.get("@type") == "DefinedTerm"]
        assert len(terms) == (1 if path == CHOOSE else 0)
        for term in terms:
            assert term["name"] == "analysis of alternatives for AI models"
            assert term["description"] in page.visible


def test_defined_term_describes_deciding_model_fit_and_showing_work(rendered):
    _, _, pages, _ = rendered
    page = surface_lint.Page(pages[CHOOSE])
    terms = [node for block in page.ld for node in surface_lint.objects(json.loads(block))
             if node.get("@type") == "DefinedTerm"]
    assert len(terms) == 1
    assert "decides which models fit a job and shows its work" in terms[0]["description"]


def test_guides_are_readable_and_linked_without_client_javascript(rendered, monkeypatch):
    tree, _, pages, _ = rendered
    monkeypatch.setattr(live, "PAGES", PATHS)
    assert live.thin_pages(tree) == []
    for path, raw in pages.items():
        page = surface_lint.Page(raw)
        assert page.first_paragraph.startswith(entity.ONE_SENTENCE)
        assert f'<link rel="canonical" href="{entity.SITE}{path}">' in raw
        assert "noindex" not in page.meta.get("robots", "")
        assert set(("/method/", "/about/", "/use-cases/", "/compare/")) <= set(page.links)
        assert re.search(r'<meta name="viewport"', raw)
        assert not re.search(r'<script(?![^>]*application/ld\+json)', raw)
    assert set((CHOOSE, COMPARE)) <= set(surface_lint.Page(pages["/guides/"]).links)


def test_guide_without_supported_answer_keeps_the_limit_visible(tmp_path):
    from pipeline import guides

    reg = registry.load(ROOT / "registry", repo_root=ROOT)
    built = snapshot.build_snapshot(snapshot.SnapshotInputs(models=[], sources=SOURCES), as_of=DAY, gate=False)
    catalogue = load_catalogue()
    image = snapshot.load_built_snapshot(built)
    decisions = [decide(parse_spec(template["spec"], facets=reg.facet), image,
                        facets=reg.facet).model_dump(mode="json")
                 for template in catalogue["templates"]]
    guides.write_examples(tmp_path, catalogue, decisions, DAY, image, reg)
    page = surface_lint.Page((tmp_path / CHOOSE.lstrip("/") / "index.html").read_text())
    assert "No recommendation" in page.visible
    assert "noindex" not in page.meta.get("robots", "")
    assert "Unavailable" in page.visible or "No candidates" in page.visible
