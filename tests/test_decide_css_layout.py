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
