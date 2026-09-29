"""Which capability domains a model's class can be measured on (MODEL-97).

A domain with no estimate is one of two claims. *Unknown*: nobody has measured
it yet, and a re-check may. *Inapplicable*: the class cannot answer the
question at all, so there is nothing to measure. Printing both as "not
measured yet" asserts gaps that can never close.

As in ``schema/applicability.py``, a rule depends only on the class, read from
what the class consumes and emits in ``api/classes.py``, never on another fact.
The one fact-based case is kept apart as ``not_offered``: a model whose
*verified* ``model.input_modalities`` excludes images cannot be measured on
images, and the post cites that fact rather than calling the class unable.
"""

from __future__ import annotations

from api.classes import CLASS_BY_ID

#: Domains whose definition is about the text a model writes.
_OPEN_TEXT = frozenset({
    "software_engineering", "engineering_stem", "maths", "reasoning", "legal",
    "medical", "finance", "writing", "marketing_seo", "multilingual", "chat_preference",
})
_IMAGE_INPUTS = frozenset({"image", "page_image"})


def inapplicable_reason(domain_id: str, class_id: str) -> str | None:
    """Why ``class_id`` cannot be measured on ``domain_id``, or ``None`` when it can.

    An unregistered class is never called inapplicable: that would assert
    there is nothing to know about a class nobody has described.
    """
    cls = CLASS_BY_ID.get(class_id)
    if cls is None:
        return None
    if domain_id == "retrieval":
        if cls.emits in ("vector", "ordering"):
            return None
        return ("retrieval is graded on an embedding or reranking model's ranking, "
                "and this class is neither")
    if domain_id == "vision_documents":
        if _IMAGE_INPUTS & set(cls.consumes):
            return None
        return "this class takes no image input"
    if domain_id == "agentic_tool_use":
        if cls.emits in ("open_text", "action"):
            return None
        return "this class neither writes text nor acts"
    if domain_id in _OPEN_TEXT:
        if cls.emits == "open_text":
            return None
        return "this class writes no open text"
    return None


def not_offered_reason(domain_id: str, input_modalities: object) -> str | None:
    """Why a verified ``model.input_modalities`` value rules a domain out, or ``None``."""
    if domain_id != "vision_documents" or not isinstance(input_modalities, list | tuple):
        return None
    if _IMAGE_INPUTS & set(input_modalities):
        return None
    return "its verified input modalities do not include images"
