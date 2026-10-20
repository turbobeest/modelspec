"""MODEL-416: a set fact's verification binds its members, never their order.

Before MODEL-416 a value hash covered the order a card filed a set in, so
filing the same members in another order gave a new hash that stepped out from
under a mismatch. A verification now records the canonical (sorted, distinct)
form, and matching still honours rows written on the old order-bound hashes.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date

import pytest
from pydantic import ValidationError

from decision import registry as reg
from decision import verify
from decision.model import (
    LEGACY_ORDERINGS_MAX_MEMBERS,
    Fact,
    SourceRef,
    TargetRef,
    VerificationActor,
    matching_value_hashes,
    value_hash,
    verification_value_hash,
)
from decision.registry import RegistryError
from tests.snapshot_records import fact, verification
from tests.test_cite_only_verification import loaded, snapshot_input
from tests.test_decision_registry import _copy, _edit, _load

FACET = "model.input_modalities"
FACT_ID = f"lab/alpha#{FACET}"
ORDER_A = ["image", "text"]
ORDER_B = ["text", "image"]

UNORDERED_FACETS = {
    "model.fits_hardware",
    "model.hardware_fit_indeterminate",
    "model.input_modalities",
    "model.languages",
    "model.output_modalities",
    "offering.harness_compatibility",
    "offering.region",
    "offering.subscription.families_covered",
    "offering.subscription.models_covered",
    "offering.subscription.surfaces",
    "origin.base_lineage",
    "origin.base_models",
    "origin.lab_jurisdiction",
    "origin.weights_hosting",
}


# --- the registry marks set semantics explicitly ---------------------------------------------


@pytest.fixture
def public_diagnostics(monkeypatch):
    """Registry copies live outside the checkout; show their loader messages."""
    monkeypatch.setattr("schema.private_data", lambda path=None: False)


def test_every_set_facet_declares_its_order_and_these_are_unordered():
    facets = reg.default().facets()
    assert {f.id for f in facets if f.value_type.unordered} == UNORDERED_FACETS
    assert {f.id for f in facets if f.value_type.kind == "set"} == UNORDERED_FACETS
    assert not any(f.value_type.unordered for f in facets if f.value_type.kind != "set")


def _set_facet(document, facet_id="model.languages"):
    return next(f for f in document["facets"] if f["id"] == facet_id)


def test_loader_refuses_a_set_facet_that_does_not_declare_its_order(tmp_path, public_diagnostics):
    root = _copy(tmp_path)
    _edit(root, "facets", lambda d: _set_facet(d)["value_type"].pop("unordered"))
    with pytest.raises(RegistryError, match="missing required field 'unordered'"):
        _load(root)


def test_loader_refuses_unordered_on_a_kind_that_is_not_a_set(tmp_path, public_diagnostics):
    root = _copy(tmp_path)
    _edit(root, "facets", lambda d: _set_facet(d, "model.context_window")["value_type"].update(
        unordered=True))
    with pytest.raises(RegistryError, match="unknown field 'unordered'"):
        _load(root)


def test_loader_refuses_an_unordered_flag_that_is_not_a_boolean(tmp_path, public_diagnostics):
    root = _copy(tmp_path)
    _edit(root, "facets", lambda d: _set_facet(d)["value_type"].update(unordered="yes"))
    with pytest.raises(RegistryError, match="unordered must be true or false"):
        _load(root)


def test_an_explicitly_ordered_set_facet_keeps_order_bound_hashes(tmp_path, public_diagnostics):
    root = _copy(tmp_path)
    _edit(root, "facets", lambda d: _set_facet(d)["value_type"].update(unordered=False))
    assert _load(root).facet("model.languages").value_type.unordered is False


# --- hashing ---------------------------------------------------------------------------------


def test_a_reorder_does_not_change_the_canonical_hash():
    models = ["openai/gpt-6-sol", "openai/gpt-6-astra", "openai/gpt-5-6-luna"]
    hashes = {verification_value_hash(order, unordered=True)
              for order in (models, sorted(models), list(reversed(models)))}
    assert hashes == {value_hash(sorted(models))}
    assert verification_value_hash(["b", "a", "b"], unordered=True) == value_hash(["a", "b"])


@pytest.mark.parametrize("value", [
    128000, 2.5, "open_weights", True, None, [8, 32], [32, 8], ["text", "image"],
    {"value": 3.0, "effective_from": "2026-10-01", "effective_until": None},
])
def test_a_value_that_is_not_an_unordered_set_hashes_as_before(value):
    assert verification_value_hash(value, unordered=False) == value_hash(value)
    assert matching_value_hashes(value, [value_hash(value)], unordered=False) == {
        value_hash(value)}


def test_an_ordered_value_does_not_match_another_order():
    assert matching_value_hashes([8, 32], [value_hash([32, 8])], unordered=False) == set()
    assert matching_value_hashes(ORDER_B, [value_hash(ORDER_A)], unordered=False) == set()


def test_a_set_matches_its_canonical_hash_and_the_legacy_hash_of_any_order():
    legacy_a, legacy_b = value_hash(ORDER_A), value_hash(ORDER_B)
    canonical = value_hash(sorted(ORDER_B))
    other = value_hash(["audio", "text"])
    assert matching_value_hashes(
        ORDER_B, [legacy_a, legacy_b, canonical, other], unordered=True,
    ) == {legacy_a, legacy_b, canonical}


def test_legacy_orders_are_found_up_to_the_member_bound():
    members = [f"lab/m{i}" for i in range(LEGACY_ORDERINGS_MAX_MEMBERS)]
    filed = list(reversed(members))
    legacy = value_hash(members[1:] + members[:1])
    assert matching_value_hashes(filed, [legacy], unordered=True) == {legacy}
    larger = [*members, "lab/m-extra"]
    assert matching_value_hashes(
        list(reversed(larger)), [value_hash(larger)], unordered=True) == set()
    assert matching_value_hashes(
        list(reversed(larger)), [value_hash(sorted(larger))], unordered=True,
    ) == {value_hash(sorted(larger))}


def _claim(field, value, subject="lab/alpha"):
    row = fact("model", subject, field, value, outcome=None)
    return verify.Claim(
        target=TargetRef(kind="fact", id=row["id"]), subject=subject, names=("Alpha",),
        field=field, value=value,
        collector=VerificationActor(agent="collector", model_family="family-a", method="read"),
        sources=(SourceRef.model_validate(row["sources"][0]),),
    )


VERIFIER = VerificationActor(agent="verifier", model_family="family-b", method="re-read")


def test_a_new_verification_of_a_set_records_the_canonical_hash():
    written = verify._verification(_claim(FACET, ORDER_B), VERIFIER, "mismatch",
                                   date(2026, 10, 19), [verify.Diff("value", "a", "b")])
    assert written.target.value_hash == value_hash(sorted(ORDER_B)) == value_hash(ORDER_A)


@pytest.mark.parametrize("field,value", [
    ("model.context_window", 128000),
    ("model.parameters_active", 3.5),
])
def test_a_new_verification_of_a_non_set_fact_is_unchanged(field, value):
    written = verify._verification(_claim(field, value), VERIFIER, "verified", date(2026, 10, 19))
    assert written.target.value_hash == value_hash(value)


# --- an inline verification on a card -------------------------------------------------------


def test_an_inline_legacy_verification_still_binds_a_reordered_card():
    row = fact("model", "lab/alpha", FACET, ORDER_B)
    row["verification"] = verification("fact", FACT_ID, value=ORDER_A)
    assert Fact.model_validate(row).verification.target.value_hash == value_hash(ORDER_A)
    row["verification"] = verification("fact", FACT_ID, value=["audio", "text"])
    with pytest.raises(ValidationError, match="value_hash does not match"):
        Fact.model_validate(row)


# --- the snapshot admits by member set ------------------------------------------------------


def _cited(modalities, log=()):
    """A cite-only card filing ``modalities``: unverified admits, a mismatch does not."""
    inputs = snapshot_input()
    for row in inputs.models[0]["facts"]:
        if row["facet"] == FACET:
            row["value"] = modalities
    return replace(inputs, verifications=list(log))


def _mismatch(value, day="2026-10-10"):
    return verification("fact", FACT_ID, "mismatch", day=day, value=value)


def test_a_cited_set_without_a_verdict_is_admitted():
    assert loaded(_cited(ORDER_B)).fact("lab/alpha", FACET).state == "known"


def test_reordering_cannot_escape_a_mismatch_on_the_legacy_hash_of_another_order():
    index = loaded(_cited(ORDER_B, [_mismatch(ORDER_A)]))
    assert index.fact("lab/alpha", FACET).state == "unknown"


def test_reordering_cannot_escape_a_mismatch_on_the_canonical_hash():
    canonical = verification("fact", FACT_ID, "mismatch", day="2026-10-10", value=ORDER_A)
    assert canonical["target"]["value_hash"] == verification_value_hash(ORDER_B, unordered=True)
    for filed in (ORDER_A, ORDER_B):
        assert loaded(_cited(filed, [canonical])).fact("lab/alpha", FACET).state == "unknown"


def test_a_mismatch_on_other_members_does_not_bind_this_set():
    index = loaded(_cited(ORDER_B, [_mismatch(["audio", "text"])]))
    assert index.fact("lab/alpha", FACET).state == "known"


def _verified_card(filed, log):
    inputs = snapshot_input(outcome="verified", url="https://lab.example.com/docs/models")
    for row in inputs.models[0]["facts"]:
        if row["facet"] == FACET:
            row["value"] = filed
            row.pop("verification")
    return replace(inputs, verifications=list(log))


@pytest.mark.parametrize("filed", [ORDER_A, ORDER_B])
def test_a_verified_set_stays_verified_in_either_order(filed):
    log = [verification("fact", FACT_ID, day="2026-10-01", value=ORDER_A)]
    index = loaded(_verified_card(filed, log))
    assert index.fact("lab/alpha", FACET).state == "known"


@pytest.mark.parametrize("filed", [ORDER_A, ORDER_B])
def test_a_later_mismatch_in_any_order_outranks_an_earlier_verified(filed):
    log = [verification("fact", FACT_ID, day="2026-10-01", value=ORDER_A),
           _mismatch(ORDER_B, day="2026-10-05")]
    assert loaded(_verified_card(filed, log)).fact("lab/alpha", FACET).state == "unknown"
