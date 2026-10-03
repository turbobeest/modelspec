"""Cache hits retain the decision engine's original deterministic draws."""

from dataclasses import replace

from decision.capability import CapabilityEstimate, deterministic_probabilities


def test_estate_sized_working_set_does_not_redraw_on_the_next_call():
    from decision.capability import _probability_draws

    _probability_draws.cache_clear()
    estimates = {"a": CapabilityEstimate(1, 0, 2, .5),
                 "b": CapabilityEstimate(0, -1, 1, .5)}
    first = [deterministic_probabilities(estimates, seed_material=f"trial-{i}")
             for i in range(32)]
    misses = _probability_draws.cache_info().misses
    again = [deterministic_probabilities(estimates, seed_material=f"trial-{i}")
             for i in range(32)]
    assert again == first
    assert _probability_draws.cache_info().misses == misses


def test_probability_cache_preserves_draws_and_separates_all_inputs():
    estimates = {
        "a": CapabilityEstimate(1, 0, 2, 0.5),
        "b": CapabilityEstimate(1, 0, 2, 0.5),
        "c": CapabilityEstimate(0, 0, 0, 0),
        "d": CapabilityEstimate(-1, -1, -1, 0),
    }
    expected = {"a": (0.49609375, 1.0), "b": (0.50390625, 1.0), "c": (0.0, 1.0), "d": (0.0, 0.0)}
    first = deterministic_probabilities(estimates, seed_material="latency")
    assert first == expected
    first.clear()
    assert (
        deterministic_probabilities(
            dict(reversed(list(estimates.items()))), seed_material="latency"
        )
        == expected
    )
    assert deterministic_probabilities(estimates, seed_material="new-snapshot") == {
        "a": (0.4765625, 1.0),
        "b": (0.51953125, 1.0),
        "c": (0.00390625, 1.0),
        "d": (0.0, 0.0),
    }
    assert deterministic_probabilities(estimates, seed_material="latency", samples=128) == {
        "a": (0.4921875, 1.0),
        "b": (0.5078125, 1.0),
        "c": (0.0, 1.0),
        "d": (0.0, 0.0),
    }
    changed = estimates | {"a": replace(estimates["a"], value=5)}
    assert deterministic_probabilities(changed, seed_material="latency") == {
        "a": (1.0, 1.0),
        "b": (0.0, 1.0),
        "c": (0.0, 1.0),
        "d": (0.0, 0.0),
    }
    changed = {key: replace(value, sd=0) for key, value in estimates.items()}
    assert deterministic_probabilities(changed, seed_material="latency") == {
        "a": (1.0, 1.0),
        "b": (0.0, 1.0),
        "c": (0.0, 1.0),
        "d": (0.0, 0.0),
    }
