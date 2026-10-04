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


def test_the_answer_and_its_chart_split_twelve_columns_six_each():
    # MODEL-325: answer first, chart beside it, on the same 12 columns as the
    # template tiles, so the split lands on the gutter between tiles 3 and 4.
    region = re.search(r"\.answer-region\s*\{([^}]*)\}", CSS)
    assert region and "grid-template-columns: repeat(12, minmax(0, 1fr))" in region.group(1)
    assert "column-gap: var(--gutter)" in region.group(1)
    answer_column = re.search(r"\.answer-column\s*\{([^}]*)\}", CSS)
    chart_column = re.search(r"\.chart-column\s*\{([^}]*)\}", CSS)
    assert answer_column and "grid-column: 1 / span 6" in answer_column.group(1)
    assert chart_column and "grid-column: 7 / -1" in chart_column.group(1)
    tiles = re.search(r"\.template-shortcuts\s*\{([^}]*)\}", CSS)
    assert tiles and "repeat(6, minmax(0, 1fr))" in tiles.group(1) and "gap: var(--gutter)" in tiles.group(1)
    # The answer card grows with its rows; it never scrolls inside itself.
    answer = re.search(r"\.board-answer\s*\{([^}]*)\}", CSS)
    assert answer
    assert "max-height:" not in answer.group(1)
    assert "overflow: auto" not in answer.group(1)
    assert "position: sticky" not in answer.group(1)
    # Two ranked lists wrap rather than overflow the answer column.
    lists = re.search(r"\.answer-lists\s*\{([^}]*)\}", CSS)
    assert lists and "repeat(auto-fit" in lists.group(1)

    results = re.search(r"\.results\s*\{([^}]*)\}", CSS)
    assert results and 'grid-template-areas: "table" "detail"' in results.group(1)
    assert "grid-template-columns: minmax(0, 1fr)" in results.group(1)
    assert "width: 100%" in results.group(1)
    table = re.search(r"\.decision-table\s*\{([^}]*)\}", CSS)
    assert table and "grid-column: 1 / -1" in table.group(1)
    assert "data-layout" not in CSS


def test_one_gutter_one_gap_one_padding_one_radius():
    # MODEL-325 D1-D6: every spacing between panels and tiles reads these tokens.
    tokens = re.search(r"\.decide-app\s*\{([^}]*--gutter[^}]*)\}", CSS)
    assert tokens
    for token in ("--gutter: 16px;", "--gap: 16px;", "--pad: 20px;", "--radius: 0;"):
        assert token in tokens.group(1)
    panel = re.search(r"\.decide-app \.panel\s*\{([^}]*)\}", CSS)
    assert panel and "padding: var(--pad)" in panel.group(1) and "border: 1px solid var(--line)" in panel.group(1)
    assert "border-top: 2px" not in CSS
    assert not re.search(r"border-radius: [23]px", CSS)


def test_narrow_widths_stack_the_chart_under_the_answer():
    narrow = re.search(r"@media \(max-width: 1099px\)\s*\{\s*\.answer-region\s*\{([^}]*)\}", CSS)
    assert narrow and "flex-direction: column" in narrow.group(1)
    assert ".mobile-answer-bar" not in CSS
