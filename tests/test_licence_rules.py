"""Jamie's licence readings of 2026-10-09 (MODEL-345)."""

from __future__ import annotations

import hashlib

from decision.licence_rules import (
    BASE_MODEL_INHERITANCE_RULE,
    LICENCE_CONDITION_RULE,
    LICENCE_READING_RULES,
    licence_reading_rule,
)
from decision.model import SourceRef, TargetRef, VerificationActor
from decision.verify import LICENCE_PROMPT, Claim, _licence_prompt

_NOTICE = (
    "Keeping an MIT or Apache copyright, licence or NOTICE notice is not "
    "attribution and not a condition."
)
_OLD_DERIVATIVE = (
    "makes a model trained on outputs a derivative subject to the licence's restrictions"
)


def test_notice_retention_is_not_attribution_on_every_facet() -> None:
    assert _NOTICE in LICENCE_CONDITION_RULE
    assert "notices is not a condition" in LICENCE_CONDITION_RULE
    for facet_id in LICENCE_READING_RULES:
        rule = licence_reading_rule(facet_id)
        assert _NOTICE in rule
        assert BASE_MODEL_INHERITANCE_RULE in rule


def test_output_training_does_not_treat_a_plain_derivative_clause_as_restricted() -> None:
    rule = LICENCE_READING_RULES["licence.output_training"]
    assert _OLD_DERIVATIVE not in rule
    assert _OLD_DERIVATIVE not in licence_reading_rule("licence.output_training")
    assert rule == (
        "This facet is about using the model's outputs to train or improve another model. "
        "A grant to fine-tune or modify this model says nothing about it. "
        "The value is restricted or prohibited only where the text expressly addresses "
        "using the model's outputs, or synthetic data or distillation from those outputs, "
        "to train or improve another model, and limits or forbids that use. "
        "A generic modification or derivative-works clause that never mentions outputs, "
        "synthetic data or distillation is not that, and the value is not_disclosed. "
        "The Gemma Terms define Model Derivatives to include a model trained on synthetic "
        "data Outputs of Gemma, or by distillation, and they subject those models to the "
        "Terms' restrictions. That text is restricted. "
        "MIT, Apache-2.0, and a custom licence that only grants modification are not_disclosed. "
        "The value is permitted only when the text expressly allows using the outputs "
        "to train or improve another model. "
        "The value is prohibited when the text expressly forbids it. "
        "The value is not_disclosed when the text is silent."
    )


def test_inheritance_is_part_of_every_reading_rule() -> None:
    assert BASE_MODEL_INHERITANCE_RULE == (
        "A fine-tune inherits its base model's licence terms where the base licence "
        "requires it. The card field is base_model. Inheritance applies when the base "
        "licence says derivatives, or Model Derivatives, must be distributed under its "
        "terms or remain subject to them. "
        "tencent/kalm-embedding-gemma3-12b-2511 has base_model google/gemma-3-12b-pt, "
        "and its LICENSE.txt embeds the Gemma terms."
    )
    for facet_id in (
        "licence.commercial_use",
        "licence.user_cap",
        "licence.fine_tuning",
        "licence.output_training",
    ):
        assert licence_reading_rule(facet_id).endswith(BASE_MODEL_INHERITANCE_RULE)


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
    assert "The card field is base_model." in bound
    material = f"{LICENCE_PROMPT}\n{bound}"
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]
    changed = hashlib.sha256(f"{material}\nRULE-CHANGED".encode("utf-8")).hexdigest()[:16]
    assert digest != changed
