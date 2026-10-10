"""How to read a licence facet. Derived from the registry definitions.

Jamie decided these readings on 2026-10-09. The collector and the licence
reader both apply them.

Keeping an MIT or Apache copyright, licence or NOTICE notice is not
attribution. Notice retention is never a condition on any ``licence.*``
facet. MIT and Apache-2.0 are permitted for commercial use and for
fine-tuning.

``licence.output_training`` is restricted or prohibited only where the
licence expressly addresses using the model's outputs, or synthetic data
or distillation from those outputs, to train or improve another model, and
limits or forbids that use. A generic modification or derivative-works
clause that never mentions outputs is not that. A silent licence is
not_disclosed. The Gemma Terms define Model Derivatives to include a model
trained on synthetic data Outputs of Gemma, or by distillation, and they
subject those models to the Terms' restrictions, so that text is restricted.
MIT, Apache-2.0, and a custom licence that only grants modification are
not_disclosed.

A fine-tune inherits its base model's licence terms where the base licence
requires it. The card field is ``base_model``. For example,
tencent/kalm-embedding-gemma3-12b-2511 has ``base_model``
google/gemma-3-12b-pt, and its LICENSE.txt embeds the Gemma terms.
"""

from __future__ import annotations

#: What counts as a condition on every ``licence.*`` facet.
#: Keeping an MIT or Apache notice is not attribution and not a condition.
LICENCE_CONDITION_RULE = (
    "Keeping an MIT or Apache copyright, licence or NOTICE notice is not "
    "attribution and not a condition. "
    "A duty to keep copyright, licence or change notices is not a condition. "
    "A condition is a display or naming duty, a separate agreement or licence, "
    "a security or other review, a user, revenue or other threshold, a territorial "
    "or field-of-use restriction, or an incorporated acceptable-use or prohibited-use policy."
)

#: One plain-language rule per licence facet, keyed by facet id.
LICENCE_READING_RULES: dict[str, str] = {
    "licence.commercial_use": (
        "The value is permitted when commercial use is granted with no condition. "
        "The value is permitted_with_conditions when it is granted subject to a condition. "
        "The value is prohibited when it is forbidden. "
        "The value is not_disclosed only when the text does not address commercial use "
        "or selling at all."
    ),
    "licence.user_cap": (
        "Record a number only when the licence requires a separate agreement or licence "
        "once a monthly-active-user threshold is exceeded. "
        "A threshold that only triggers a display, naming or attribution duty is not a cap, "
        "and neither is a revenue threshold. "
        "With no such monthly-active-user threshold the value is unbounded, "
        "because the registry definition says unbounded when the licence sets no such cap. "
        "Never use not_disclosed for user_cap when the cited region is the licence text."
    ),
    "licence.fine_tuning": (
        "An express grant to modify the model, the Software or the Work, or to create "
        "derivative works of it, covers fine-tuning. "
        "The value is permitted_with_conditions when using or distributing the result "
        "is subject to a condition, permitted when only notice retention applies, "
        "and prohibited when modification is forbidden."
    ),
    "licence.output_training": (
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
    ),
}

#: A fine-tune carries the base licence when that licence requires it.
#: The card field is ``base_model``.
BASE_MODEL_INHERITANCE_RULE = (
    "A fine-tune inherits its base model's licence terms where the base licence "
    "requires it. The card field is base_model. Inheritance applies when the base "
    "licence says derivatives, or Model Derivatives, must be distributed under its "
    "terms or remain subject to them. "
    "tencent/kalm-embedding-gemma3-12b-2511 has base_model google/gemma-3-12b-pt, "
    "and its LICENSE.txt embeds the Gemma terms."
)


def licence_reading_rule(facet_id: str) -> str:
    """The condition rule, this facet's rule, and base-model inheritance.

    The collector and the licence reader both include this text.
    """
    return (
        f"{LICENCE_CONDITION_RULE} {LICENCE_READING_RULES[facet_id]} "
        f"{BASE_MODEL_INHERITANCE_RULE}"
    )
