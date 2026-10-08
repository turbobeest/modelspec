"""MODEL-345 collector names the reading rule on every licence value."""

from __future__ import annotations

from decision.licence_rules import LICENCE_READING_RULES
from scripts.model_345_collect import FACETS, READINGS


def test_every_collector_value_names_the_rule_it_applied() -> None:
    assert set(LICENCE_READING_RULES) == set(FACETS)
    for model_id, row in READINGS.items():
        for facet in FACETS:
            reading = row["facets"][facet]
            assert reading["rule"] == facet, (model_id, facet)
            assert reading["rule"] in LICENCE_READING_RULES
