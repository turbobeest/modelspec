"""Probability prose chooses its article from the displayed percentage."""

import pytest

from pipeline.comparison_pages import comparison_page
from pipeline.surface_lint import Page
from tests.test_comparison_probability_trace import DAY, comparison, separate  # noqa: F401


@pytest.mark.parametrize("probability,phrase", [
    (0.0766, "an 8%"),
    (0.105, "an 11%"),
    (0.175, "an 18%"),
    (0.795, "an 80%"),
    (0.805, "an 81%"),
    (0.885, "an 89%"),
    (0.895, "a 90%"),
    (0.63671875, "a 64%"),
    (0.3852, "a 39%"),
    (0.0099, "an under 1%"),
])
def test_probability_articles_follow_the_rendered_number(comparison, probability, phrase):
    decision = comparison[1]
    decision["bands"]["best"][0]["p_best"] = probability
    decision["bands"]["best"][1]["p_beats_leader"] = probability
    separate(decision)

    visible = Page(comparison_page(*comparison, DAY)).visible

    assert f"with {phrase} chance of being the best model" in visible
    assert f"lab/a-challenger has {phrase} chance of matching or beating" in visible
