"""Which class of model a task needs — the rule (MODEL-100).

`api/classes.py` is the taxonomy; this is the decision made over it. A pure
function: a request and whatever catalogue evidence the caller has in, an
answer out. It performs no I/O, calls no model, and never raises on caller
input — a refusal is an answer here, not an exception.

**The refusal was designed first**, because the honest inventory demands it.
ModelSpec holds, per class, the facets and how many cards claim it; per card,
benchmarks that are *within-class by construction*; and across classes, **one
measurement of one task** (MODEL-99), whose own page says nothing about it
generalises. So the rule that can be applied honestly is a **filter over
facets, not a comparison**. `partial` — two or more classes survive and we
will not order them — is therefore the expected answer, not a degraded one, in
exactly the way the ranker's `unranked` is not "scored low".

Two asymmetries worth reading before the code:

* **A facet is a constraint; a term is a hint.** Facets the caller supplied are
  assertions about their own problem and they bind. Terms are our guess about
  their words, so a term match may *discover* a class but may never remove one
  the caller's own constraints admit. A guess never overrides an assertion.
* **`decides` is strict.** `emits` and `consumes` admit published adaptations —
  a text generator can be parsed into a choice, a typed state can be serialised
  into text, and MODEL-99 did both. `decides` admits none, because adapting it
  means the caller writes the decision logic themselves, which is a different
  architecture rather than a different model.

No number here orders one class above another, and MODEL-99's figures are not
served on any surface. Cost-to-correct is fitness evidence for a *task*;
`rank_score` is a within-class quality composite. `tests/test_class_fit.py`
holds the boundary in four places, including the import direction.

The reasoning is `docs/design/class-selection.md`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from api import classes as cls

#: Single source; re-exported so a caller reads one vocabulary, not two.
REFUSAL_CODES = cls.REFUSAL_CODES
EXCLUDED_REASONS = cls.EXCLUDED_REASONS

#: At most this many example ids per class, sorted. A longer list, or an
#: unsorted one, would start to read as a recommendation.
MAX_EXAMPLES = 3

_WORD = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class CatalogueEvidence:
    """What the caller knows about the catalogue, supplied rather than fetched.

    Absence and zero are different answers — MODEL-97's lesson, reapplied. A
    class missing from `card_counts` reports `unknown`; a class present with 0
    reports `empty`, which is a real and useful thing to be told.
    """

    #: class id -> number of cards
    card_counts: Mapping[str, int] = field(default_factory=dict)
    #: class id -> model ids; capped and sorted before publication
    examples: Mapping[str, Sequence[str]] = field(default_factory=dict)
    #: class id -> ranking profile keys. Omitted falls back to the derivation
    #: in `api.classes.rank_profiles_for`.
    rank_profiles: Mapping[str, Sequence[str]] = field(default_factory=dict)


def _tokens(text: str) -> tuple[set[str], str]:
    """Lowercase word tokens, and the normalised string multi-word terms match."""
    normalised = _WORD.sub(" ", text.lower()).strip()
    return set(normalised.split()), f" {normalised} "


def _matched_terms(model_class: cls.ModelClass, words: set[str], blob: str) -> list[str]:
    hits = []
    for term in model_class.terms:
        if " " in term:
            if f" {term} " in blob:
                hits.append(term)
        elif term in words:
            hits.append(term)
    return sorted(hits)


def _emits_check(model_class: cls.ModelClass, wanted: str) -> tuple[bool, dict | None]:
    if model_class.emits == wanted:
        return True, None
    for adaptation in cls.EMITS_ADAPTATIONS:
        if adaptation.from_ == model_class.emits and adaptation.to == wanted:
            return True, adaptation.to_json()
    return False, None


def _consumes_check(model_class: cls.ModelClass,
                    wanted: Sequence[str]) -> tuple[bool, list[dict]]:
    adapted: list[dict] = []
    for kind in wanted:
        if kind in model_class.consumes:
            continue
        bridge = next(
            (a for a in cls.CONSUMES_ADAPTATIONS
             if a.from_ == kind and a.to in model_class.consumes),
            None,
        )
        if bridge is None:
            return False, adapted
        adapted.append(bridge.to_json())
    return True, adapted


def _catalogue(class_id: str, evidence: CatalogueEvidence | None) -> dict[str, Any]:
    if evidence is None or class_id not in evidence.card_counts:
        return {"evidence_state": "unknown"}
    count = int(evidence.card_counts[class_id])
    examples = sorted(evidence.examples.get(class_id) or ())[:MAX_EXAMPLES]
    return {
        "card_count": count,
        "example_model_ids": examples,
        "evidence_state": "populated" if count > 0 else "empty",
    }


def _next_step(catalogue: dict[str, Any], profiles: Sequence[str]) -> str:
    state = catalogue["evidence_state"]
    if state == "unknown":
        return ("Catalogue evidence was not supplied with this request. Fetch "
                "/api/rank/class-fit.json for the per-class counts.")
    if state == "empty":
        return ("ModelSpec catalogues no model of this class today, so it "
                "cannot name one for you — look outside the catalogue.")
    if profiles:
        return (f"Rank within this class: `modelspec offline rank {profiles[0]}`"
                f" ({len(profiles)} profile(s) cover it).")
    return ("No ranking profile covers this class, so ranking stops at this "
            "class boundary. The catalogue can name the cards, not order them.")


def _answer(fit_status: str, **rest: Any) -> dict[str, Any]:
    answer: dict[str, Any] = {
        "fit_status": fit_status,
        "policy": cls.class_fit_policy(),
        "vocabulary": cls.vocabulary(),
        "matched_terms": [],
        "candidates": [],
        "excluded": [],
        "distinguishing_questions": [],
        "composition": [],
    }
    answer.update(rest)
    return answer


def _refused(code: str, message: str, **detail: Any) -> dict[str, Any]:
    refusal = {"code": code, "message": message}
    refusal.update(detail)
    return _answer("refused", refusal=refusal)


def class_fit(*, task: str | None = None,
              emits: str | None = None,
              consumes: Sequence[str] | None = None,
              decides: str | None = None,
              evidence: CatalogueEvidence | None = None) -> dict[str, Any]:
    """Candidate classes for a task, or a refusal that says what would work.

    `emits` / `consumes` / `decides` are the primary input: a caller who knows
    what their system needs gets an exact, deterministic answer with no text
    matching at all. `task` is a *term source only* — it is tokenised, matched
    against the published terms, and discarded. Only the matched terms are
    echoed; the text itself is never stored, logged or forwarded, which is what
    keeps `neutrality_commitment()`'s `stores_customer_prompts: false` an
    architectural fact rather than a promise.
    """
    for label, value in (("emits", emits), ("decides", decides)):
        vocab = cls.EMITS if label == "emits" else cls.DECIDES
        if value is not None and value not in vocab:
            return _refused(
                "unknown_facet_value",
                f"{label} must be one of the published vocabulary",
                field=label, value=value, vocabulary=cls.vocabulary(),
            )
    for kind in consumes or ():
        if kind not in cls.CONSUMES:
            return _refused(
                "unknown_facet_value",
                "consumes must be drawn from the published vocabulary",
                field="consumes", value=kind, vocabulary=cls.vocabulary(),
            )

    has_facets = bool(emits or decides or consumes)
    if not has_facets and not (task or "").strip():
        return _refused(
            "empty_request",
            "give a task description, or one of emits / consumes / decides",
            vocabulary=cls.vocabulary(),
        )

    words, blob = _tokens(task) if task else (set(), " ")
    terms_by_class = {
        model_class.id: _matched_terms(model_class, words, blob)
        for model_class in cls.CLASSES
    }
    all_matched = sorted({t for hits in terms_by_class.values() for t in hits})

    if task and not has_facets and not all_matched:
        return _refused(
            "no_term_matched",
            "no published term occurs in that description. The matcher does "
            "not paraphrase; pick a class below, or send emits / consumes / "
            "decides instead.",
            classes=[
                {"id": c.id, "emits": c.emits, "decides": c.decides,
                 "terms": list(c.terms)}
                for c in cls.CLASSES
            ],
            vocabulary=cls.vocabulary(),
        )

    candidates: list[dict[str, Any]] = []
    excluded: list[dict[str, str]] = []

    for model_class in cls.CLASSES:
        emits_adapted: dict | None = None
        consumes_adapted: list[dict] = []

        if emits is not None:
            ok, emits_adapted = _emits_check(model_class, emits)
            if not ok:
                excluded.append({"class": model_class.id,
                                 "excluded_reason": "emits_wrong_kind"})
                continue
        if decides is not None and model_class.decides != decides:
            excluded.append({"class": model_class.id,
                             "excluded_reason": "decision_shape_mismatch"})
            continue
        if consumes:
            ok, consumes_adapted = _consumes_check(model_class, consumes)
            if not ok:
                excluded.append({"class": model_class.id,
                                 "excluded_reason": "consumes_unsupported"})
                continue

        # A term is a hint, never a veto: it may only discover a class when the
        # caller supplied no constraints of their own.
        if not has_facets and not terms_by_class[model_class.id]:
            excluded.append({"class": model_class.id,
                             "excluded_reason": "not_described"})
            continue

        catalogue = _catalogue(model_class.id, evidence)
        profiles = list(
            (evidence.rank_profiles.get(model_class.id) if evidence else None)
            or cls.rank_profiles_for(model_class.id)
        )
        candidates.append({
            "class": model_class.id,
            "consumes": list(model_class.consumes),
            "emits": model_class.emits,
            "decides": model_class.decides,
            "abstains": model_class.abstains,
            "because": model_class.because,
            "model_types": list(model_class.model_types),
            "matched_terms": terms_by_class[model_class.id],
            "emits_adapted": emits_adapted,
            "consumes_adapted": consumes_adapted,
            "rank_profiles": profiles,
            "catalogue": catalogue,
            "next": _next_step(catalogue, profiles),
        })

    # `derived` and `unclassified` are never candidates, and they say why and
    # where to look instead rather than being silently absent.
    for non_class in cls.NON_CLASSES:
        excluded.append({"class": non_class, "excluded_reason": "not_a_class",
                         "resolution": cls.NON_CLASS_RESOLUTION[non_class]})

    candidates.sort(key=lambda row: row["class"])
    excluded.sort(key=lambda row: row["class"])

    if not candidates:
        return _answer("unavailable", matched_terms=all_matched, excluded=excluded)

    fit_status = "resolved" if len(candidates) == 1 else "partial"
    return _answer(
        fit_status,
        matched_terms=all_matched,
        candidates=candidates,
        excluded=excluded,
        distinguishing_questions=_questions(candidates),
        composition=_compositions(candidates),
    )


def _questions(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The facet the survivors differ on, phrased so the caller can settle it."""
    kinds = sorted({row["emits"] for row in candidates})
    found: dict[frozenset[str], cls.DistinguishingQuestion] = {}
    for index, left in enumerate(kinds):
        for right in kinds[index + 1:]:
            question = cls.QUESTION_BY_PAIR.get(frozenset({left, right}))
            if question is not None:
                found[frozenset({left, right})] = question
    return [q.to_json() for q in sorted(found.values(), key=lambda q: q.between)]


def _compositions(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Pairs that chain rather than compete. Not an ordering — see the rule."""
    chains: list[dict[str, Any]] = []
    for first in candidates:
        if not first["abstains"]:
            continue
        for second in candidates:
            if second["class"] == first["class"]:
                continue
            bridged = second["emits"] == first["emits"] or any(
                a.from_ == second["emits"] and a.to == first["emits"]
                for a in cls.EMITS_ADAPTATIONS
            )
            if not bridged:
                continue
            chains.append({
                "sequence": [first["class"], second["class"]],
                "rule": cls.COMPOSITION_RULE,
                "evidence": cls.COMPOSITION_EVIDENCE,
                "see": cls.COMPOSITION_SEE,
            })
    chains.sort(key=lambda chain: chain["sequence"])
    return chains
