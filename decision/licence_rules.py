"""How to read a licence facet. Derived from the registry definitions.

Jamie has not reviewed these readings of the definitions. The sentences are
the shared rules the collector and the licence reader both apply.

The commercial-use reading follows the existing corpus and the MODEL-78
tier-1 OSI mapping (MIT and Apache = permitted). The registry wording
"attribution" is ambiguous on whether notice retention counts as a condition,
and that question is open for Jamie.

The output-training reading follows the existing corpus in treating a model
trained on outputs, which the licence makes a derivative, as restricted.
The registry definition does not settle that case, and that question is open
for Jamie.

A fine-tune with a ``base_model`` may also carry the base model's licence
terms. Today neither the rules nor the binding follow ``base_model``. KaLM's
file embeds the Gemma terms, so it reads correctly. That question is open
for Jamie.
"""

from __future__ import annotations

#: What counts as a condition on every ``licence.*`` facet.
#: A notice duty is not one.
LICENCE_CONDITION_RULE = (
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
        "The value is permitted only when the text expressly allows using the outputs "
        "to train or improve another model. "
        "The value is restricted when the text allows that only for some purposes or models, "
        "or makes a model trained on outputs a derivative subject to the licence's restrictions. "
        "The value is prohibited when the text forbids it. "
        "The value is not_disclosed when the text is silent."
    ),
}


def licence_reading_rule(facet_id: str) -> str:
    """The condition rule plus the rule for this facet. The prompt includes both."""
    return f"{LICENCE_CONDITION_RULE} {LICENCE_READING_RULES[facet_id]}"
