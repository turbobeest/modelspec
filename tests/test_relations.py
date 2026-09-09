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
