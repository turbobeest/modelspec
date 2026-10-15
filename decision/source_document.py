"""Offline source normalization supplies the pinned PDF extractor explicitly."""

from __future__ import annotations

from decision.normalise import Document, RuleSet
from decision.normalise import normalise_document as _normalise_document
from decision.pdf_text import extract_pdf


def normalise_document(body: bytes, rules: RuleSet, *, charset: str | None = None) -> Document:
    return _normalise_document(
        body,
        rules,
        charset=charset,
        pdf_extractor=extract_pdf if rules.content == "pdf" else None,
    )
