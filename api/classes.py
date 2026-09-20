"""What class of model a problem needs — the taxonomy (MODEL-100).

`ModelType` is a good publishing field and a bad selection axis. Its 35 values
sit on four axes at once: modality (`image-generation`), role (`reward-model`,
`router`), lineage (`distilled`, `merged`, `quantized-variant`) and domain
(`medical`, `legal`). A builder cannot choose on that — `quantized-variant` and
`llm-chat` are not alternatives, one is a provenance relation to the other.

So this module is a **view over `ModelType`, never a replacement for it**. The
enum stays exactly as published; MODEL-98 has just paid a major version for it.
Nothing here is written on a card, so nothing can drift per card — the same
call `schema/applicability.py` made one commit ago, for the same reason.

The axis is **what a model consumes, what it emits, and what decision it makes
on the caller's behalf**. `decides` does the real work, because it is the facet
that changes the caller's own code: prose a person reads, a permutation of
items you supplied, a label from a taxonomy the model defines, a value from a
set *you* defined, a preference between two outputs, or an action taken.

A class is **derived**, not hand-listed: `CLASS_BY_PAIR[(emits, decides)]`.
That pair is injective, checked at import and again by a test, so the mapping
is a function a sceptic can evaluate rather than a matter of taste.

Two deliberate properties:

* **Keyed on the enum's string values**, never on `ModelType` itself. The
  module therefore imports nothing the Cloudflare Worker's Python bundle does
  not already carry — `api/ranking/engine.py` is in it and `schema/` is not —
  so it can be vendored unchanged the day `POST /v1/class-fit` is built
  (`api/worker/vendor.py`). `tests/test_class_fit.py` holds the key set equal
  to `{t.value for t in ModelType}`, so a new enum member is a red test on the
  commit that adds it — which is where the argument about its class belongs.
* **`api/ranking/engine.py` never imports this module.** The dependency runs
  one way only, and a test enforces it. Cost-to-correct (MODEL-99) is fitness
  evidence for a *task*; `rank_score` is a within-class quality composite. If
  the scorer could see this package, a measurement of one task could lift a
  model in a ranking of another, invisibly.

The reasoning is `docs/design/class-selection.md`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# `neutrality_commitment` is *called*, never transcribed, so the published
# terms keep their single source and `tests/test_legal.py` stays the one place
# prose and JSON are held together. `USE_CASE_PROFILES` is read to derive which
# ranking profiles cover a class, rather than hand-listing them here. This is
# the only import from the repository, and it points at a module the Worker
# bundle already carries.
from api.ranking.engine import USE_CASE_PROFILES, neutrality_commitment

# ── the vocabularies, published ─────────────────────────────────────────────

#: Input kinds a task can have. Not modalities: `structured_state` is the
#: typed state a decision model is handed, and `item_list` is the candidate
#: set a reranker orders.
CONSUMES: tuple[str, ...] = (
    "text", "image", "audio", "video", "page_image", "structured_state",
    "numeric_series", "model_output", "item_list", "observations",
)

#: What comes out. `open_text` is generated language a person or a parser
#: reads; `choice` is a value from a set the caller defined; `label` is a value
#: from a taxonomy the model defines. Those three are different products.
EMITS: tuple[str, ...] = (
    "open_text", "media", "transcript", "vector", "ordering", "label",
    "choice", "preference_score", "action", "series", "world_state",
    "annotation",
)

#: The decision the model makes on the caller's behalf — the facet that decides
#: what the caller's code looks like afterwards.
DECIDES: tuple[str, ...] = (
    "nothing", "what_order", "which_of_a_fixed_set",
    "which_of_a_caller_defined_set", "how_good", "what_to_do_next",
)

#: Every refusal the rule can produce. Published, and `api/class_fit.py` reads
#: this tuple rather than repeating it.
REFUSAL_CODES: tuple[str, ...] = (
    "empty_request", "no_term_matched", "unknown_facet_value",
)

#: Why a class is not a candidate. A closed set: an exclusion without a reason
#: is a guess wearing a verdict's clothes.
EXCLUDED_REASONS: tuple[str, ...] = (
    "emits_wrong_kind", "consumes_unsupported", "decision_shape_mismatch",
    # The task description used none of this class's terms. Only ever reached
    # when the caller supplied no facets of their own: a term is a hint and may
    # discover a class, but it may never remove one a constraint admits.
    "not_described",
    "not_a_class",
)


@dataclass(frozen=True)
class Adaptation:
    """One published way an input or an output can be made to fit.

    Adaptations are the reason a text generator can answer a decision question
    at all, and they are deliberately few: each one is a claim that a caller
    can bridge two facet values in practice, and each one here is a claim
    MODEL-99 actually made and measured.
    """

    from_: str
    to: str
    how: str

    def to_json(self) -> dict[str, str]:
        return {"from": self.from_, "to": self.to, "how": self.how}


#: Inputs that can be made to fit. Exactly one today.
CONSUMES_ADAPTATIONS: tuple[Adaptation, ...] = (
    Adaptation(
        "structured_state", "text",
        "serialised as JSON — MODEL-99 handed the LLM arms the decision "
        "model's own state and questions verbatim",
    ),
)

#: Outputs that can be made to fit. Exactly one today, and it carries its own
#: caveat: MODEL-99 scored a truncated or unparseable reply as a *wrong*
#: answer, not a missing one, because dropping them would flatter the arm that
#: produces them.
EMITS_ADAPTATIONS: tuple[Adaptation, ...] = (
    Adaptation(
        "open_text", "choice",
        "parsed out of generated text; a malformed, truncated or refused "
        "answer is a wrong answer, not a missing one",
    ),
)


@dataclass(frozen=True)
class ModelClass:
    """One class: its facets, the `ModelType` values that derive to it, and why."""

    id: str
    consumes: tuple[str, ...]
    emits: str
    decides: str
    #: Whether this class has an "I cannot tell" output state. The precondition
    #: for a cascade (see `COMPOSITION_RULE`), not a quality judgement.
    abstains: bool
    #: Why this `(emits, decides)` pair is its own class, in the words a
    #: reviewer needs. Not published per class to sell it; published so it can
    #: be argued with.
    because: str
    #: Words a task description might use. The weakest part of this design, and
    #: the part published loudest for exactly that reason.
    terms: tuple[str, ...]
    #: The `ModelType` values that derive to this class.
    model_types: tuple[str, ...]
    #: A domain narrows the pool *inside* a class; it never names one.
    domains: dict[str, str] = field(default_factory=dict)


CLASSES: tuple[ModelClass, ...] = (
    ModelClass(
        id="actor",
        consumes=("text", "image", "observations"),
        emits="action", decides="what_to_do_next", abstains=False,
        because=(
            "it acts. Everything else hands the caller material or a verdict "
            "and stops; this one changes the world, so the caller's code is an "
            "executor rather than a reader"
        ),
        terms=("agent", "agentic", "act", "action", "tool", "tools", "browse",
               "automate", "robot", "robotics", "control", "execute"),
        model_types=("agent-model", "robotics"),
    ),
    ModelClass(
        id="analyser",
        consumes=("text", "image", "video"),
        emits="annotation", decides="which_of_a_fixed_set", abstains=False,
        because=(
            "it labels the *parts* of its input — tokens, spans, regions, "
            "depth — rather than the whole of it, so the caller gets a "
            "structure over the input, not a verdict about it"
        ),
        terms=("detect", "detection", "segment", "segmentation", "bounding box",
               "depth", "named entity", "token classification", "annotate",
               "keypoint", "fill mask"),
        model_types=("vision-encoder", "text-encoder"),
    ),
    ModelClass(
        id="decider",
        consumes=("text", "structured_state"),
        emits="choice", decides="which_of_a_caller_defined_set", abstains=True,
        because=(
            "the answer set is defined by the caller at request time. That is "
            "the sentence `schema/enums.py` already writes for `decision-model`"
            " — a safety classifier has a fixed harm taxonomy, these labels do "
            "not — promoted from a docstring to the axis"
        ),
        terms=("decide", "decision", "classify", "classification", "choose",
               "route", "routing", "triage", "judge", "judgement", "judgment",
               "verdict", "determine", "attribute", "attribution", "calibrated",
               "probability", "abstain"),
        model_types=("decision-model", "router"),
    ),
    ModelClass(
        id="forecaster",
        consumes=("numeric_series",),
        emits="series", decides="nothing", abstains=False,
        because="no tokens go in and none come out; the unit is a number over time",
        terms=("forecast", "forecasting", "time series", "timeseries",
               "seasonality", "demand", "horizon"),
        model_types=("time-series",),
    ),
    ModelClass(
        id="labeller",
        consumes=("text", "image"),
        emits="label", decides="which_of_a_fixed_set", abstains=True,
        because=(
            "the taxonomy belongs to the model, not the caller. You get the "
            "categories it was trained on and no others, which is a different "
            "product from one that answers your questions"
        ),
        terms=("moderate", "moderation", "safety", "toxicity", "toxic",
               "harmful", "abuse", "spam", "guardrail", "classify",
               "classification", "flag"),
        model_types=("safety-classifier",),
    ),
    ModelClass(
        id="media-generator",
        consumes=("text", "image", "audio"),
        emits="media", decides="nothing", abstains=False,
        because="the artefact is pixels or samples, so nothing downstream parses it",
        terms=("image", "picture", "illustration", "render", "photo", "video",
               "speech", "voice", "music", "synthesise", "synthesize", "inpaint"),
        model_types=("image-generation", "image-editing", "video-generation",
                     "audio-tts", "audio-music"),
    ),
    ModelClass(
        id="orderer",
        consumes=("text", "item_list"),
        emits="ordering", decides="what_order", abstains=False,
        because=(
            "it is handed the candidates and returns a permutation of them. It "
            "invents nothing and chooses nothing; it only sorts"
        ),
        terms=("rerank", "reranking", "reorder", "relevance", "shortlist",
               "ordering", "sort"),
        model_types=("reranker",),
    ),
    ModelClass(
        id="scorer",
        consumes=("text", "model_output"),
        emits="preference_score", decides="how_good", abstains=False,
        because=(
            "its subject is another model's output, for training or selection. "
            "It answers 'how good is this answer', never 'what is the answer'"
        ),
        terms=("reward", "preference", "rlhf", "best of n", "rate the output",
               "score the output"),
        model_types=("reward-model",),
    ),
    ModelClass(
        id="simulator",
        consumes=("observations",),
        emits="world_state", decides="nothing", abstains=False,
        because="it predicts what happens next in an environment, not what to say about it",
        terms=("simulate", "simulation", "world model", "dynamics", "rollout",
               "environment"),
        model_types=("world-model",),
    ),
    ModelClass(
        id="text-generator",
        consumes=("text", "image", "audio"),
        emits="open_text", decides="nothing", abstains=False,
        because=(
            "it produces open-ended language and decides nothing: the caller "
            "reads it, or parses it and decides. This is the class every other "
            "catalogue already ranks, and the one MODEL-100 exists to stop "
            "assuming"
        ),
        terms=("write", "writing", "summarise", "summarize", "summary", "draft",
               "explain", "chat", "conversation", "prose", "essay", "reply",
               "translate", "rewrite", "compose", "reason", "code", "coding"),
        model_types=("llm-chat", "llm-reasoning", "llm-code", "llm-base", "vlm",
                     "medical", "legal", "financial", "audio-realtime"),
        domains={"medical": "medical", "legal": "legal", "financial": "financial"},
    ),
    ModelClass(
        id="transcriber",
        consumes=("audio", "page_image"),
        emits="transcript", decides="nothing", abstains=False,
        because=(
            "the output is a faithful rendering of the input in another form. "
            "A generator may add or reorganise; this one may not, and that is "
            "the whole difference to the caller"
        ),
        terms=("transcribe", "transcript", "transcription", "ocr", "dictation",
               "subtitle", "caption", "speech to text"),
        model_types=("audio-asr", "document-ocr"),
    ),
    ModelClass(
        id="vectoriser",
        consumes=("text", "image"),
        emits="vector", decides="nothing", abstains=False,
        because=(
            "the output is a reusable representation the caller stores and "
            "compares, not an answer about any one input"
        ),
        terms=("embed", "embedding", "embeddings", "vector", "similarity",
               "semantic search", "nearest neighbour", "nearest neighbor",
               "retrieval", "index"),
        model_types=("embedding-text", "embedding-multimodal", "embedding-code"),
    ),
)


#: `ModelType` values that name **no class**, and why.
#:
#: Lineage answers "where did these weights come from", not "what does this
#: do". A distilled model is a smaller instance of its base model's class, not
#: an alternative to it. `miscellaneous` disqualifies itself by its own
#: definition — "for models no specific type describes honestly".
NON_CLASSES: dict[str, tuple[str, ...]] = {
    "derived": ("adapter", "quantized-variant", "distilled", "merged"),
    "unclassified": ("miscellaneous",),
}

#: What a caller does instead. Named, because "we cannot place this" without a
#: next step is a dead end rather than a refusal.
NON_CLASS_RESOLUTION: dict[str, str] = {
    "derived": (
        "this value records a lineage relation, not a capability. Follow "
        "`lineage.base_model` on the card and take that model's class."
    ),
    "unclassified": (
        "`miscellaneous` is the catalogue's own admission that no type "
        "describes the model honestly. There is nothing to derive from it."
    ),
}


def _build_class_by_pair() -> dict[tuple[str, str], str]:
    """`(emits, decides) -> class id`, and prove it is a function."""
    table: dict[tuple[str, str], str] = {}
    for model_class in CLASSES:
        key = (model_class.emits, model_class.decides)
        if key in table:
            raise ValueError(
                f"{model_class.id} and {table[key]} share the pair {key}: the "
                "class derivation would stop being a function"
            )
        table[key] = model_class.id
    return table


#: The derivation, printed. A class is looked up from its facets; it is never
#: assigned by hand.
CLASS_BY_PAIR: dict[tuple[str, str], str] = _build_class_by_pair()

CLASS_BY_ID: dict[str, ModelClass] = {c.id: c for c in CLASSES}


def _build_placement() -> dict[str, str]:
    placed: dict[str, str] = {}
    for model_class in CLASSES:
        for value in model_class.model_types:
            placed[value] = model_class.id
    for non_class, values in NON_CLASSES.items():
        for value in values:
            placed[value] = non_class
    return placed


#: `model_type` value -> class id, or one of the `NON_CLASSES` keys.
MODEL_TYPE_PLACEMENT: dict[str, str] = _build_placement()


def class_for_model_type(value: str | None) -> str | None:
    """The class id for a `model_type`, or None when it names no class."""
    placed = MODEL_TYPE_PLACEMENT.get(value or "")
    return placed if placed in CLASS_BY_ID else None


def non_class_for_model_type(value: str | None) -> str | None:
    """`derived`, `unclassified`, or None when the value does name a class."""
    placed = MODEL_TYPE_PLACEMENT.get(value or "")
    return placed if placed in NON_CLASSES else None


def rank_profiles_for(class_id: str) -> list[str]:
    """Ranking profiles that cover a class, **derived** from `preferred_types`.

    Not a hand list, so it cannot drift from the profiles. For `decider` it is
    empty today, which is the true and useful statement that ranking stops at
    that class boundary.
    """
    model_class = CLASS_BY_ID.get(class_id)
    if model_class is None:
        return []
    wanted = set(model_class.model_types)
    return sorted(
        key for key, profile in USE_CASE_PROFILES.items()
        if wanted & set(profile.get("preferred_types") or ())
    )


# ── the questions a `partial` answer hands back ─────────────────────────────
#
# Published, not generated. When two classes both survive, the facet they
# differ on is the thing the caller has to settle, and phrasing it is the
# difference between "I cannot tell you" and work somebody can do.

@dataclass(frozen=True)
class DistinguishingQuestion:
    between: tuple[str, str]
    ask: str

    def to_json(self) -> dict[str, Any]:
        return {"between": list(self.between), "ask": self.ask}


DISTINGUISHING_QUESTIONS: tuple[DistinguishingQuestion, ...] = (
    DistinguishingQuestion(
        ("choice", "open_text"),
        "Does your code branch on the answer, or does a person read it? A "
        "value your code switches on wants a decider; prose a person reads "
        "wants a text-generator. If you would parse the prose into a value, "
        "you want a decider and are considering paying an LLM to be one.",
    ),
    DistinguishingQuestion(
        ("choice", "label"),
        "Is the set of answers fixed by the model, or defined by you per "
        "request? A fixed taxonomy — harm categories, sentiment — is a "
        "labeller. Your own options, changing per call, need a decider.",
    ),
    DistinguishingQuestion(
        ("ordering", "vector"),
        "Do you need a reusable representation you store and compare later, "
        "or one ordering of items you already hold? Storing it is a "
        "vectoriser; ordering it now is an orderer. Retrieval usually wants "
        "both, in that order.",
    ),
    DistinguishingQuestion(
        ("action", "open_text"),
        "Does the model hand your code text to act on, or take the action "
        "itself? If your code owns the loop you want a text-generator and a "
        "harness, not an actor.",
    ),
    DistinguishingQuestion(
        ("open_text", "transcript"),
        "Must the output be a faithful rendering of the input, or may it add, "
        "omit and reorganise? A transcriber may not; a generator may, and "
        "will.",
    ),
    DistinguishingQuestion(
        ("annotation", "label"),
        "Do you need one answer about the whole input, or a structure over "
        "its parts? Whole-input is a labeller; spans, boxes and masks are an "
        "analyser.",
    ),
)

QUESTION_BY_PAIR: dict[frozenset[str], DistinguishingQuestion] = {
    frozenset(q.between): q for q in DISTINGUISHING_QUESTIONS
}


#: When two candidate classes do not compete but chain. Published as the rule,
#: because "both, in this order" is a legitimate answer and has to be
#: distinguishable from an ordering, which it is not: neither class is placed
#: above the other.
COMPOSITION_RULE = (
    "When a candidate class has an 'I cannot tell' output state (`abstains`) "
    "and another candidate decides the same shape from the same inputs, the "
    "pair is named as a sequence — the abstaining class first, the other on "
    "its abstentions. This is not an ordering: neither class is better, and "
    "no number is attached to either."
)

#: The one measured case, cited as a document. Its figures are deliberately
#: not served: a number printed beside a class name is a score whatever the
#: key is called, and that page's own "what this does not show" forbids
#: generalising one task to another.
COMPOSITION_EVIDENCE = "one measured task"
COMPOSITION_SEE = (
    "https://github.com/turbobeest/modelspec/blob/main/"
    "docs/research/cost-to-correct-attribution.md"
)


#: What the term matcher cannot do. In the published rule, not only in the
#: design document, so a caller reads it beside the answer it shaped.
CANNOT: tuple[str, ...] = (
    "paraphrase: a task described in other words than the published terms is refused",
    "negation: 'it must not write anything' matches the writing terms",
    "any language other than English",
    "constraints of volume, latency or budget, which are not in the words",
    "choosing a model — that is ranking, and it runs within one class",
)


def class_fit_policy() -> dict[str, Any]:
    """The decision rule, as data a sceptic can read and re-run.

    `ranking_policy()` publishes the floors and `neutrality_commitment()`
    publishes the honest-broker promise, both keyless and both beside the
    answer they shaped. This ships the same way, and carries the commitment by
    calling it rather than copying its strings.
    """
    return {
        "version": "class-fit-v1",
        "basis": "model_type",
        "axis": ["consumes", "emits", "decides"],
        "derivation": "class = CLASS_BY_PAIR[(emits, decides)]",
        "orders_classes": False,
        "cross_class_scores": "never",
        "task_matching": (
            "exact token match over the published terms; no model call, so the "
            "same request always returns the same answer"
        ),
        "request_text": (
            "matched and discarded. Only the matched terms are echoed; the "
            "text is never stored, logged or forwarded"
        ),
        "cannot": list(CANNOT),
        "refuses_when": [
            {"code": "empty_request",
             "meaning": "no task description and no facet was given"},
            {"code": "no_term_matched",
             "meaning": "a task description was given and no published term occurs in it"},
            {"code": "unknown_facet_value",
             "meaning": "a facet value outside the published vocabulary"},
        ],
        "fit_statuses": ["resolved", "partial", "unavailable", "refused"],
        "excluded_reasons": list(EXCLUDED_REASONS),
        "adaptations": {
            "consumes": [a.to_json() for a in CONSUMES_ADAPTATIONS],
            "emits": [a.to_json() for a in EMITS_ADAPTATIONS],
        },
        "strict_facet": (
            "decides — it admits no adaptation, because adapting it means the "
            "caller writes the decision logic themselves, which is a different "
            "architecture rather than a different model"
        ),
        "composition_rule": COMPOSITION_RULE,
        "non_classes": {key: NON_CLASS_RESOLUTION[key] for key in NON_CLASSES},
        # Additive under the contract's own rule, and called rather than
        # transcribed so the published terms keep one source.
        "neutrality": neutrality_commitment(),
    }


def vocabulary() -> dict[str, list[str]]:
    """The three facet vocabularies, published with every answer."""
    return {"consumes": list(CONSUMES), "emits": list(EMITS), "decides": list(DECIDES)}
