"""P(best) and top-three stability are computed from the estimates alone, and cached."""

from dataclasses import replace

from decision.capability import CapabilityEstimate, deterministic_probabilities


def test_estate_sized_working_set_does_not_recompute_on_the_next_call():
    from decision.capability import _probabilities

    _probabilities.cache_clear()
    trials = [{"a": CapabilityEstimate(1 + i / 100, 0, 2, .5),
               "b": CapabilityEstimate(0, -1, 1, .5)} for i in range(32)]
    first = [deterministic_probabilities(estimates) for estimates in trials]
    misses = _probabilities.cache_info().misses
    again = [deterministic_probabilities(estimates) for estimates in trials]
    assert again == first
    assert _probabilities.cache_info().misses == misses


def test_probabilities_depend_on_the_estimates_alone():
    estimates = {
        "a": CapabilityEstimate(1, 0, 2, 0.5),
        "b": CapabilityEstimate(1, 0, 2, 0.5),
        "c": CapabilityEstimate(0, 0, 0, 0),
        "d": CapabilityEstimate(-1, -1, -1, 0),
    }
    expected = {
        "a": (0.4999, 0.9999), "b": (0.4999, 0.9999), "c": (0.0005, 1.0), "d": (0.0, 0.0001),
    }
    first = deterministic_probabilities(estimates)
    assert first == expected
    first.clear()
    assert deterministic_probabilities(dict(reversed(list(estimates.items())))) == expected
    changed = estimates | {"a": replace(estimates["a"], value=5)}
    assert deterministic_probabilities(changed) == {
        "a": (1.0, 1.0),
        "b": (0.0, 0.9999),
        "c": (0.0, 1.0),
        "d": (0.0, 0.0),
    }


def test_exact_scores_tie_to_the_lower_model_id():
    estimates = {
        "a": CapabilityEstimate(1, 0, 2, 0),
        "b": CapabilityEstimate(1, 0, 2, 0),
        "c": CapabilityEstimate(0, 0, 0, 0),
        "d": CapabilityEstimate(-1, -1, -1, 0),
    }
    assert deterministic_probabilities(estimates) == {
        "a": (1.0, 1.0),
        "b": (0.0, 1.0),
        "c": (0.0, 1.0),
        "d": (0.0, 0.0),
    }


def test_two_models_match_the_closed_form():
    # P(x >= y) for N(0.3, 1) against N(0, 1) is Phi(0.3 / sqrt(2)) = 0.58400.
    assert deterministic_probabilities({
        "x": CapabilityEstimate(0.3, 0, 0, 1),
        "y": CapabilityEstimate(0, 0, 0, 1),
    }) == {"x": (0.584, 1.0), "y": (0.416, 1.0)}
