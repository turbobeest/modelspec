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


def test_canvas_and_answers_are_right_of_facets_with_full_width_results_below():
    workspace = re.search(r"\.board-workspace\s*\{([^}]*)\}", CSS)
    assert workspace and 'grid-template-areas: "facets answer"' in workspace.group(1)
    facets = re.search(r"\.facet-list\s*\{([^}]*)\}", CSS)
    answer = re.search(r"\.board-answer\s*\{([^}]*)\}", CSS)
    assert facets and "grid-area: facets" in facets.group(1)
    assert answer and "grid-area: answer" in answer.group(1)
    assert "max-height:" not in answer.group(1)
    assert "overflow: auto" not in answer.group(1)

    results = re.search(r"\.results\s*\{([^}]*)\}", CSS)
    assert results and 'grid-template-areas: "table" "detail"' in results.group(1)
    assert "grid-template-columns: minmax(0, 1fr)" in results.group(1)
    assert "width: 100%" in results.group(1)
    table = re.search(r"\.decision-table\s*\{([^}]*)\}", CSS)
    assert table and "grid-column: 1 / -1" in table.group(1)
    assert "data-layout" not in CSS


def test_mobile_stacks_facets_before_canvas_and_answers():
    mobile = re.search(r"@media \(max-width: 1099px\)\s*\{\s*\.board-workspace\s*\{([^}]*)\}", CSS)
    assert mobile and 'grid-template-areas: "facets" "answer"' in mobile.group(1)
