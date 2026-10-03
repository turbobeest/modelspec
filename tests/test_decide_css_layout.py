"""Layout rules the decide page cannot lose without breaking the board."""
import re
from pathlib import Path

CSS = (Path(__file__).resolve().parent.parent / "web/src/decide/decide.css").read_text()


def test_facet_controls_sit_in_the_state_column_even_without_a_known_cell():
    # 2026-10-02: the private-data vocabulary carries no facet counts, so the
    # Known cell is absent and the controls fell into the 54px Known column,
    # clipping Must and Prefer out of reach. They must pin to the last column.
    rule = re.search(r"\.facet-controls\s*\{([^}]*)\}", CSS)
    assert rule and "grid-column: -2 / -1" in rule.group(1)


def test_facets_and_narrowing_share_one_row_with_full_width_results_below():
    workspace = re.search(r"\.board-workspace\s*\{([^}]*)\}", CSS)
    assert workspace and 'grid-template-areas: "facets answer"' in workspace.group(1)
    # Jamie, 2026-10-03 (MODEL-298): the facets and narrowing cards share one
    # height, whichever is longer. The row stretches both cards.
    assert "align-items: stretch" in workspace.group(1)
    facets = re.search(r"\.facet-list\s*\{([^}]*)\}", CSS)
    answer = re.search(r"\.board-answer\s*\{([^}]*)\}", CSS)
    assert facets and "grid-area: facets" in facets.group(1)
    assert answer and "grid-area: answer" in answer.group(1)
    assert "max-height:" not in answer.group(1)
    assert "overflow: auto" not in answer.group(1)
    assert "position: sticky" not in answer.group(1)
    # Two ranked lists wrap rather than overflow the narrower answer column.
    lists = re.search(r"\.answer-lists\s*\{([^}]*)\}", CSS)
    assert lists and "repeat(auto-fit" in lists.group(1)

    results = re.search(r"\.results\s*\{([^}]*)\}", CSS)
    assert results and 'grid-template-areas: "table" "detail"' in results.group(1)
    assert "grid-template-columns: minmax(0, 1fr)" in results.group(1)
    assert "width: 100%" in results.group(1)
    table = re.search(r"\.decision-table\s*\{([^}]*)\}", CSS)
    assert table and "grid-column: 1 / -1" in table.group(1)
    assert "data-layout" not in CSS


def test_the_narrowing_column_keeps_room_for_a_ranked_row():
    # The browser test measures the overflow at 1000-1440px; this pins the
    # floor it depends on: 406px of row columns plus 56px of padding.
    workspace = re.search(r"\.board-workspace\s*\{([^}]*)\}", CSS)
    assert workspace and "grid-template-columns: minmax(0, 600px) minmax(470px, 1fr)" in workspace.group(1)
    assert "@media (max-width: 1099px) {\n  .board-workspace" not in CSS


def test_narrow_widths_stack_facets_before_the_narrowing():
    mobile = re.search(r"@media \(max-width: 999px\)\s*\{\s*\.board-workspace\s*\{([^}]*)\}", CSS)
    assert mobile and 'grid-template-areas: "facets" "answer"' in mobile.group(1)
    assert "grid-template-columns: minmax(0, 1fr);" in mobile.group(1)
