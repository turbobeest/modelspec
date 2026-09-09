"""Model pages must show relationships without asserting things nobody checked.

The rule these tests defend: null means "not yet researched" in this schema, so
an empty section or an always-empty column is a lie — it says we looked and
found nothing.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.relations import Relations  # noqa: E402
from pipeline.render import (  # noqa: E402
    competitors_section, hardware_section, human_count, lineage_section,
    platforms_section, proper_name,
)
from schema.graph import CollectingSink  # noqa: E402


def _sink() -> CollectingSink:
    s = CollectingSink()
    for i in ("base", "child", "rival"):
        s.node("Model", "id", i, {"id": i, "display_name": i.title()})
    s.node("Platform", "id", "aws_bedrock", {"id": "aws_bedrock", "display_name": "Aws Bedrock"})
    s.node("Hardware", "id", "gpu", {"id": "gpu", "display_name": "A GPU",
                                     "memory_bandwidth_gb_s": 1000})
    s.edge("Model", "child", "DERIVED_FROM", "Model", "base", {"relation": "finetune"})
    s.edge("Model", "child", "AVAILABLE_ON", "Platform", "aws_bedrock", {})
    s.edge("Model", "child", "FITS_ON", "Hardware", "gpu",
           {"quantization": "q4", "weights_gb": 4.0, "device_memory_gb": 24,
            "predicted_decode_tps": 100.0, "fastest_predicted_decode_tps": 100.0,
            "fastest_quantization": "q4", "basis": "computed"})
    s.edge("Model", "child", "COMPETES_WITH", "Model", "rival", {"overlap_score": 0.9})
    return s


# ── the index ────────────────────────────────────────────────────────────────

def test_lineage_is_walkable_in_both_directions() -> None:
    rel = Relations(_sink())
    assert [a["id"] for a in rel.for_model("child").ancestors] == ["base"]
    assert [d["id"] for d in rel.for_model("base").descendants] == ["child"]


def test_competition_is_visible_from_both_endpoints() -> None:
    """One undirected edge, but each model must see the other."""
    rel = Relations(_sink())
    assert [c["id"] for c in rel.for_model("child").competitors] == ["rival"]
    assert [c["id"] for c in rel.for_model("rival").competitors] == ["child"]


def test_a_model_with_nothing_reports_empty() -> None:
    rel = Relations(_sink())
    assert rel.for_model("nobody-has-heard-of-this").is_empty


def test_hardware_is_ordered_fastest_first() -> None:
    s = _sink()
    s.node("Hardware", "id", "slow", {"id": "slow", "display_name": "Slow"})
    s.edge("Model", "child", "FITS_ON", "Hardware", "slow",
           {"fastest_predicted_decode_tps": 5.0, "basis": "computed"})
    order = [h["id"] for h in Relations(s).for_model("child").hardware]
    assert order[0] == "gpu"


def test_competitors_are_ordered_closest_first() -> None:
    s = _sink()
    s.node("Model", "id", "distant", {"id": "distant", "display_name": "Distant"})
    s.edge("Model", "child", "COMPETES_WITH", "Model", "distant", {"overlap_score": 0.1})
    order = [c["id"] for c in Relations(s).for_model("child").competitors]
    assert order == ["rival", "distant"]


# ── the presentation rules ───────────────────────────────────────────────────

def test_an_empty_section_is_omitted_entirely() -> None:
    """Not rendered as an empty table, which would assert we had looked."""
    rel = Relations(_sink()).for_model("rival")
    assert lineage_section(rel) == ""
    assert platforms_section(rel) == ""
    assert hardware_section(rel) == ""


def test_a_column_empty_on_every_row_is_dropped() -> None:
    """No card here carries model_id_on_platform, so that column must not appear."""
    html = platforms_section(Relations(_sink()).for_model("child"))
    assert "Platform" in html
    assert "Id on that platform" not in html


def test_a_column_with_data_is_kept() -> None:
    s = _sink()
    s.edges = [e for e in s.edges if e["type"] != "AVAILABLE_ON"]
    s.edge("Model", "child", "AVAILABLE_ON", "Platform", "aws_bedrock",
           {"model_id_on_platform": "some.model.v1"})
    html = platforms_section(Relations(s).for_model("child"))
    assert "Id on that platform" in html
    assert "some.model.v1" in html


def test_hardware_says_computed_not_measured() -> None:
    html = hardware_section(Relations(_sink()).for_model("child"))
    assert "computed" in html
    assert "Nobody has run this model" in html


def test_competitors_are_marked_derived() -> None:
    html = competitors_section(Relations(_sink()).for_model("child"))
    assert "Derived, not authored" in html


def test_lineage_reads_as_english() -> None:
    """It rendered as "is a derived from of" before the relation was handled."""
    html = lineage_section(Relations(_sink()).for_model("child"))
    assert "derived from of" not in html
    assert "finetune" in html


def test_acronyms_are_not_title_cased_into_nonsense() -> None:
    assert proper_name("aws_bedrock") == "AWS Bedrock"
    assert proper_name("gpt4all") == "GPT4All"
    assert proper_name("nvidia_nim") == "NVIDIA NIM"
    assert proper_name("some_new_platform") == "Some New Platform"


def test_parameter_counts_are_human_readable() -> None:
    assert human_count(8_000_000_000) == "8B"
    assert human_count(1_500_000_000) == "1.5B"
    assert human_count(70_000_000_000) == "70B"
    assert human_count(None) == "None"


# ── catalogue freshness and verified evidence ────────────────────────────────

def test_a_stale_catalogue_discloses_itself() -> None:
    """A complete-looking catalogue months behind is worse than a small current one."""
    from pipeline.render import freshness_notice

    class FakeModel:
        def __init__(self, released):
            self.front = {"release_date": released}

    stale = freshness_notice([FakeModel("2020-01-01")])
    assert "months ago" in stale
    assert "known gap" in stale


def test_a_current_catalogue_says_nothing() -> None:
    from datetime import date

    from pipeline.render import freshness_notice

    class FakeModel:
        def __init__(self, released):
            self.front = {"release_date": released}

    assert freshness_notice([FakeModel(date.today().isoformat())]) == ""


def test_verified_evidence_renders_apart_from_legacy_scores() -> None:
    """The two kinds of number must never be mistaken for each other."""
    from pipeline.render import evidence_section

    class FakeModel:
        front = {"benchmarks": {"evidence": [{
            "benchmark_id": "scicode", "model_id_as_evaluated": "GPT-6 Astra (max)",
            "score": 56.0, "unit": "percent", "source_url": "https://example.test/x",
            "source_kind": "independent_evaluator", "evidence_date": "2026-09-04",
            "date_type": "published", "verified_at": "2026-09-09"}]}}

    html = evidence_section(FakeModel())
    assert "Verified benchmark evidence" in html
    assert "checked against its source by a reviewer" in html
    assert "GPT-6 Astra (max)" in html, "the identifier as evaluated must be shown"
    assert "56.0%" in html


def test_no_evidence_renders_nothing() -> None:
    from pipeline.render import evidence_section

    class FakeModel:
        front = {"benchmarks": {"scores": {"humaneval": 90.0}}}

    assert evidence_section(FakeModel()) == ""


# ── the front door ───────────────────────────────────────────────────────────

def test_the_landing_page_links_to_the_site() -> None:
    """Everything was live and unreachable from modelspec.dev itself.

    The landing page predates the site and was copied into the build verbatim,
    so its only links were to GitHub. A visitor saw the same holding page as
    before and reasonably concluded nothing had shipped.
    """
    from pipeline.build import wire_landing

    html = wire_landing(
        '<nav><a href="https://github.com/turbobeest/modelspec">GitHub</a></nav>',
        {"models": 1, "providers": 1, "edges": 1, "benchmarks": 1, "fields": 1},
    )
    for route in ("/graph/", "/downselect/", "/models/", "/providers/"):
        assert f'href="{route}"' in html, f"the front door does not link to {route}"


def test_landing_statistics_come_from_the_build() -> None:
    """They were hand-written and had drifted — 750 fields against an actual 693."""
    from pipeline.build import wire_landing

    html = wire_landing(
        '<div class="stats" aria-label="x"><div><b>OLD</b>model cards</div></div></section>',
        {"models": 1225, "providers": 47, "edges": 37020, "benchmarks": 1106, "fields": 693},
    )
    assert "OLD" not in html
    assert "1,225" in html and "693" in html


def test_field_count_is_leaves_not_sections() -> None:
    """len(model_fields) is 20 sections, and would advertise "20 fields per card"."""
    import sys as _sys
    from pathlib import Path as _Path

    _sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))
    from pipeline.build import _schema_field_count
    from schema.card import ModelCard

    assert _schema_field_count(ModelCard) > 600
