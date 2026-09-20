"""Which questions a model's *class* can answer at all (MODEL-97).

A `null` in this schema has always meant "not yet researched" — somebody should
go and look. For a catalogue of one class that reading is nearly always right.
For a catalogue of several it is sometimes a lie: a model that emits no text has
no maximum output-token count to research, and publishing that `null` with the
same meaning as an unresearched one asserts a gap that can never be closed.

**Applicability is derived from `model_type`, never written on a card.** There
is no per-card list to fall out of date, nothing to round-trip through
`ModelCard.to_yaml()`, and no way for one card to disagree with its own class.
The table here is reviewed once instead of 1,339 times, and
`tests/test_class_and_null_semantics.py` fails if a path in it stops naming a
real schema field.

Two rules the table obeys, and the second is the important one:

1. A rule names the classes for which a field **is** applicable. A card whose
   class is not among them has nothing to research there.
2. **A rule may depend only on the class.** Not on another card field. The
   tempting rule — "hardware profiles are inapplicable when `open_weights` is
   false" — is refused, because `licensing.open_weights` is `bool = False` with
   no null state: an unresearched card is indistinguishable from a genuinely
   closed one, so the rule would manufacture "there is nothing to know" across
   the catalogue. That is MODEL-77's `data_residency: []` mistake repainted.

What this file deliberately does **not** call inapplicable: architecture.
A closed model still *has* layers and parameters; nobody has published them.
That is unknown, possibly unobtainable, and much nearer `withheld` than
"meaningless". Calling it inapplicable would assert there is nothing to know
and quietly excuse the catalogue from ever asking.

The section-level counterpart of this table is `__applicable_model_types__` on
the nested models in `schema/card.py`, which predates it. `schema.card
.inapplicable_paths` evaluates both and is the single entry point consumers use.
"""

from __future__ import annotations

from dataclasses import dataclass

from .enums import ModelType


def model_types(*keys: str) -> frozenset[ModelType]:
    """Resolve ModelType members by exact value or hyphen-prefix (``'llm-'``)."""
    found: set[ModelType] = set()
    for key in keys:
        if key.endswith("-"):
            matched = [t for t in ModelType if t.value.startswith(key)]
            if not matched:
                raise ValueError(f"no ModelType starts with {key!r}")
            found.update(matched)
        else:
            found.add(ModelType(key))
    return frozenset(found)


#: Classes that emit text tokens, so an output-token limit, a token stream and
#: an output tok/s are questions they can answer.
#:
#: Same membership as `pipeline.hardware.TOKEN_GENERATING_MODEL_TYPES`, which
#: answers the neighbouring question "does it decode tokens, so is a tok/s
#: prediction honest" (MODEL-53). Two names because they are two questions;
#: a test holds them equal so neither drifts, and that test is where a future
#: divergence gets argued rather than discovered.
TEXT_WRITING_MODEL_TYPES: frozenset[ModelType] = model_types(
    "llm-", "vlm", "medical", "legal", "financial", "agent-model", "router",
    "adapter", "quantized-variant", "distilled", "merged",
)

#: Classes that take text *in*, so an input-token limit and a context window
#: are questions they can answer. A decision model reads supplied state, so it
#: is here; it writes no text, so it is not above.
TEXT_READING_MODEL_TYPES: frozenset[ModelType] = TEXT_WRITING_MODEL_TYPES | model_types(
    "text-encoder", "document-ocr", "reranker", "embedding-", "decision-model",
    "reward-model", "safety-classifier",
)


@dataclass(frozen=True)
class FieldRule:
    """One field, the classes it applies to, and why it applies to no others."""

    #: Dotted path from the `ModelCard` root. Held to a real field by a test.
    path: str
    #: What a reader is told the page cannot show.
    label: str
    #: The classes for which this field is a real question.
    applies_to: frozenset[ModelType]
    #: The sentence a page or a reviewer needs. Not published per field; it is
    #: the reason the rule survives review.
    because: str


FIELD_RULES: tuple[FieldRule, ...] = (
    FieldRule("modalities.text.max_output_tokens", "Max output tokens",
              TEXT_WRITING_MODEL_TYPES, "this class emits no text"),
    FieldRule("modalities.text.streaming", "Token streaming",
              TEXT_WRITING_MODEL_TYPES, "this class emits no token stream"),
    FieldRule("modalities.text.fill_in_middle", "Fill-in-the-middle",
              TEXT_WRITING_MODEL_TYPES, "this class emits no text"),
    FieldRule("inference_performance.api_tps_output", "API output tok/s",
              TEXT_WRITING_MODEL_TYPES, "this class has no output token stream"),
    FieldRule("modalities.text.max_input_tokens", "Max input tokens",
              TEXT_READING_MODEL_TYPES, "this class takes no text input"),
    FieldRule("modalities.text.context_window", "Context window",
              TEXT_READING_MODEL_TYPES, "this class takes no text input"),
)

#: Human labels for the *sections* `__applicable_model_types__` gates. Used
#: when a page or a report has to name a subtree rather than a field.
SECTION_LABELS: dict[str, str] = {
    "capabilities": "Generative capabilities",
    "modalities.text": "Text modality",
    "modalities.vision": "Vision",
    "modalities.audio": "Audio",
    "modalities.video": "Video",
    "modalities.document": "Documents",
    "modalities.image_generation": "Image generation",
    "modalities.embeddings": "Embeddings",
    "modalities.reranking": "Reranking",
}

_FIELD_LABELS: dict[str, str] = {rule.path: rule.label for rule in FIELD_RULES}


def label_for(path: str) -> str:
    """A reader's name for a dotted path; the path itself when none is set."""
    return _FIELD_LABELS.get(path) or SECTION_LABELS.get(path) or path


def reason_for(path: str) -> str | None:
    """Why this path does not apply, for the rules that state one."""
    for rule in FIELD_RULES:
        if rule.path == path:
            return rule.because
    return None
