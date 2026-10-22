"""Reviewed PDF source bindings. Adding a template requires a source-terms decision.

No production template is approved yet. A template pins the entire source and
extraction before interpreting a fixed line, including its ownership context.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from decision.normalise import fingerprint


@dataclass(frozen=True)
class PdfTemplate:
    source_url: str
    retention_terms_url: str
    copy_ref: str
    extraction_ref: str
    subject: str
    model_name: str
    field: str
    source_kind: str
    value_line: int
    value_pattern: str
    unit: str

    def __post_init__(self):
        if not self.retention_terms_url.startswith("https://"):
            raise ValueError("PDF template needs the reviewed retention-terms URL")
        if any(not re.fullmatch(r"sha256:[0-9a-f]{64}", value)
               for value in (self.copy_ref, self.extraction_ref)):
            raise ValueError("PDF template needs exact source and extraction hashes")
        if self.value_line < 0 or "value" not in re.compile(self.value_pattern).groupindex:
            raise ValueError("PDF template needs a fixed line and named value capture")


APPROVED_TEMPLATES: tuple[PdfTemplate, ...] = ()


def retention_approved(source_url: str, copy_ref: str) -> bool:
    return any(template.source_url == source_url and template.copy_ref == copy_ref
               for template in APPROVED_TEMPLATES)


def verify_pdf(claim, regions, *, today):
    """Exclusive PDF dispatch, with no generic reader or LLM fallback."""
    from decision.model import VerificationActor
    from decision.verify import (
        DETERMINISTIC,
        Reading,
        Result,
        _independent,
        _verification,
        compare,
    )

    actor = VerificationActor(agent="modelspec-verify", model_family=DETERMINISTIC,
                              method="pdf-reviewed-template@1")
    if not _independent(claim, actor, today):
        return Result(claim.target, "skipped", reason="no_independent_extractor")
    for source in claim.sources:
        registered = regions.sources.get(source.source_id)
        if registered is None or registered.normaliser != "pdf-pypdf-6.19.0-v1":
            continue
        for template in APPROVED_TEMPLATES:
            if (
                template.source_url != str(registered.url)
                or template.copy_ref != source.snapshot_ref
                or template.subject != claim.subject
                or template.field != claim.field
                or template.source_kind != registered.kind
            ):
                continue
            for region_id in source.cited_regions:
                text = regions.text(source.source_id, source.snapshot_ref, region_id)
                if text is None or fingerprint(text) != template.extraction_ref:
                    continue
                lines = text.splitlines()
                if template.value_line >= len(lines):
                    continue
                match = re.fullmatch(template.value_pattern, lines[template.value_line])
                if match is None:
                    continue
                readings = [Reading(template.model_name, match["value"], template.unit)]
                diffs = compare(claim, readings)
                outcome = "mismatch" if diffs else "verified"
                return Result(claim.target, outcome,
                              _verification(claim, actor, outcome, today, diffs), tuple(diffs))
    return Result(claim.target, "skipped", reason="pdf_template_not_approved")
