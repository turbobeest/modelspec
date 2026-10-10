"""Jamie's licence readings of 2026-10-09 (MODEL-345)."""

from __future__ import annotations

import hashlib

import decision.licence_rules as licence_rules
from decision.licence_rules import (
    LICENCE_CONDITION_RULE,
    LICENCE_READING_RULES,
    licence_reading_rule,
)
from decision.model import SourceRef, TargetRef, VerificationActor
from decision.verify import LICENCE_PROMPT, Claim, _licence_prompt

_NOTICE = (
    "Keeping a copyright, licence, NOTICE or change notice is not attribution "
    "and not a condition."
)
_COMPETING_MODEL = (
    "The value is restricted when the text expressly allows or forbids it only "
    "for some purposes or models, for example not for a competing model, or makes "
    "a model trained on outputs a derivative subject to the licence's restrictions. "
    "The value is prohibited when the text expressly forbids it for every purpose."
)
_OUTPUT_DERIVATIVE = (
    "A licence that defines a model trained on its outputs, on synthetic data from "
    "them, or by distillation from them as a derivative subject to its restrictions "
    "is restricted."
)


def test_notice_retention_is_not_attribution_on_every_facet() -> None:
    assert _NOTICE in LICENCE_CONDITION_RULE
    assert "MIT" not in LICENCE_CONDITION_RULE
    assert "Apache" not in LICENCE_CONDITION_RULE
    for facet_id in LICENCE_READING_RULES:
        rule = licence_reading_rule(facet_id)
        assert _NOTICE in rule
        assert "base_model" not in rule
        assert "Gemma" not in rule
        assert "MIT" not in rule
        assert "Apache" not in rule


def test_output_training_keeps_a_competing_model_limit_restricted() -> None:
    rule = LICENCE_READING_RULES["licence.output_training"]
    assert _COMPETING_MODEL in rule
    assert _COMPETING_MODEL in licence_reading_rule("licence.output_training")


def test_output_training_does_not_treat_a_plain_derivative_clause_as_restricted() -> None:
    rule = LICENCE_READING_RULES["licence.output_training"]
    assert "generic modification or derivative-works clause" in rule
    assert rule == (
        "This facet is about using the model's outputs to train or improve another model. "
        "A grant to fine-tune or modify this model says nothing about it. "
        "The value is restricted or prohibited only where the text expressly addresses "
        "using the model's outputs, or synthetic data or distillation from those outputs, "
        "to train or improve another model, and limits or forbids that use. "
        "A generic modification or derivative-works clause that never mentions outputs, "
        "synthetic data or distillation is not that, and the value is not_disclosed. "
        f"{_OUTPUT_DERIVATIVE} "
        "The value is permitted only when the text expressly allows using the outputs "
        "to train or improve another model. "
        "The value is restricted when the text expressly allows or forbids it only for some "
        "purposes or models, for example not for a competing model, or makes a model trained "
        "on outputs a derivative subject to the licence's restrictions. "
        "The value is prohibited when the text expressly forbids it for every purpose. "
        "The value is not_disclosed when the text is silent."
    )


def test_the_reader_rule_leaves_inheritance_to_the_binding_code() -> None:
    """The reader only sees licence text. The KaLM example stays in the module doc."""
    for facet_id in (
        "licence.commercial_use",
        "licence.user_cap",
        "licence.fine_tuning",
        "licence.output_training",
    ):
        rule = licence_reading_rule(facet_id)
        assert "inherit" not in rule.casefold()
        assert "tencent/" not in rule
    assert "tencent/kalm-embedding-gemma3-12b-2511" in licence_rules.__doc__
    assert "google/gemma-3-12b-pt" in licence_rules.__doc__


def test_the_licence_reader_hashes_the_rule_text() -> None:
    """The cache key is the prompt template plus the filled rule, definition and values."""
    claim = Claim(
        target=TargetRef(kind="fact", id="lab/nimbus-3#licence.output_training"),
        subject="lab/nimbus-3",
        names=("Nimbus 3",),
        field="licence.output_training",
        value=None,
        collector=VerificationActor(agent="claude-cli", model_family="anthropic", method="collect"),
        sources=(SourceRef(
            source_id="nimbus-licence",
            snapshot_ref="sha256:" + "a" * 64,
            cited_regions=["page"],
        ),),
    )
    _prompt, bound = _licence_prompt(claim, "Permission is hereby granted.")
    assert _NOTICE in bound
    assert "not_disclosed when the text is silent" in bound
    assert _OUTPUT_DERIVATIVE in bound
    assert "base_model" not in bound
    assert "Gemma" not in bound
    assert "MIT" not in bound
    assert "Apache" not in bound
    material = f"{LICENCE_PROMPT}\n{bound}"
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]
    changed = hashlib.sha256(f"{material}\nRULE-CHANGED".encode("utf-8")).hexdigest()[:16]
    assert digest != changed
