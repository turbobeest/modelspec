#!/usr/bin/env python3
"""File the MODEL-191 existing-row audit against retained primary sources.

Fourteen rows have text that an independent reader can check. The Gemini 3.8
Flash PDF publishes its results table as an image, so its two rows remain
quarantined rather than passing through an invented transcription.
"""

from __future__ import annotations

import hashlib
import re
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from importlib.metadata import version
from io import BytesIO
from pathlib import Path

import pypdf
import yaml

from decision.model import SourceRef, TargetRef, VerificationActor
from decision.normalise import NORMALISERS, normalise_document
from decision.sources import CopyStore, load_sources
from decision.verify import Claim, Queue
from scripts.model_143_evidence import evidence_id, evidence_key, replace_evidence

ROOT = Path(__file__).resolve().parents[1]
READ_DATE = "2026-09-27"
USER_AGENT = "ModelSpec/1.0 (+https://modelspec.dev)"
COLLECTOR = VerificationActor(
    agent="codex-model-191",
    model_family="openai",
    method="retained-primary-source@1",
)


@dataclass(frozen=True)
class SourcePlan:
    source_id: str
    url: str
    pages: tuple[int, ...] = ()
    html_url: str | None = None


@dataclass(frozen=True)
class ClaimPlan:
    model_id: str
    benchmark_id: str
    source: str
    label: str
    effort: str | None


SOURCES = {
    "opus": SourcePlan(
        "model-191-anthropic-opus-5-5-system-card",
        "https://www.anthropic.com/claude-opus-5-5-system-card",
        (174, 184, 185, 213, 214),
    ),
    "fable": SourcePlan(
        "model-191-anthropic-fable-5-1-system-card",
        "https://www.anthropic.com/claude-fable-5-1-system-card",
        (167, 177, 196, 197, 198, 199),
    ),
    "openai": SourcePlan(
        "model-191-openai-gpt-6-astra",
        "https://openai.com/index/gpt-6-astra/",
    ),
    "deepseek": SourcePlan(
        "model-191-deepseek-v4-pro-paper",
        "https://arxiv.org/abs/2606.19348",
        html_url="https://arxiv.org/html/2606.19348",
    ),
}

CLAIMS = (
    ClaimPlan("anthropic/claude-opus-5-5", "swe_bench_multimodal", "opus",
              "SWE-bench Multimodal", "max"),
    ClaimPlan("anthropic/claude-opus-5-5", "terminal_bench_science", "opus",
              "Terminal-Bench Science 0.1", "max"),
    ClaimPlan("anthropic/claude-opus-5-5", "hle_tools", "opus",
              "Humanity's Last Exam (with tools)", "max"),
    ClaimPlan("anthropic/claude-opus-5-5", "healthbench_professional", "opus",
              "HealthBench Professional", "max"),
    ClaimPlan("anthropic/claude-fable-5-1", "swe_bench_multimodal", "fable",
              "SWE-bench Multimodal", "max"),
    ClaimPlan("anthropic/claude-fable-5-1", "terminal_bench_science", "fable",
              "Terminal-Bench Science 0.1", "max"),
    ClaimPlan("anthropic/claude-fable-5-1", "arc_agi_2", "fable", "ARC-AGI-2", "max"),
    ClaimPlan("anthropic/claude-fable-5-1", "healthbench_professional", "opus",
              "HealthBench Professional", "max"),
    ClaimPlan("anthropic/claude-opus-5", "healthbench_professional", "opus",
              "HealthBench Professional", "max"),
    ClaimPlan("openai/gpt-6-astra", "terminal_bench_science", "openai",
              "Terminal-Bench Science 0.1", None),
    ClaimPlan("openai/gpt-6-astra", "browsecomp", "openai", "BrowseComp", None),
    ClaimPlan("openai/gpt-6-astra", "hle_tools", "openai",
              "Humanity's Last Exam (w/ tools)", None),
    ClaimPlan("openai/gpt-6-astra", "arc_agi_2", "openai", "ARC-AGI-2", None),
    ClaimPlan("deepseek/deepseek-v4-pro", "mmlu_pro", "deepseek", "MMLU-Pro", "max"),
)


def _fetch(url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=180) as response:  # noqa: S310
        return response.read(), response.geturl()


def _pdf_excerpt(plan: SourcePlan, body: bytes, resolved: str) -> bytes:
    reader = pypdf.PdfReader(BytesIO(body))
    text = "\n\n".join(
        f"PDF page {page}\n{reader.pages[page - 1].extract_text() or ''}"
        for page in plan.pages
    )
    header = (
        f"Provenance: text extracted with pypdf {version('pypdf')} from pages "
        f"{', '.join(map(str, plan.pages))} of the PDF served at {plan.url}, resolved "
        f"to {resolved}, SHA-256 {hashlib.sha256(body).hexdigest()}. Read {READ_DATE}.\n\n"
    )
    return (header + re.sub(r"[ \t]+", " ", text)).encode()


def _source_copy(plan: SourcePlan, store: CopyStore) -> str:
    body, resolved = _fetch(plan.html_url or plan.url)
    if plan.pages:
        retained = _pdf_excerpt(plan, body, resolved)
    else:
        text = normalise_document(body, NORMALISERS["html-default"]).text
        if plan.source_id.endswith("deepseek-v4-pro-paper"):
            start = text.index("Table 6: Comparison between DeepSeek-V4-Pro-Max")
            end = text.index("Reasoning.", start)
            text = text[start:end]
        retained = (
            f"Provenance: HTML fetched from {resolved}, SHA-256 "
            f"{hashlib.sha256(body).hexdigest()}. Read {READ_DATE}.\n\n{text}\n"
        ).encode()
    return store.put(retained)


def _register_sources() -> None:
    path = ROOT / "registry" / "sources.yaml"
    text = path.read_text(encoding="utf-8")
    known = load_sources(path)
    additions = []
    for plan in SOURCES.values():
        if plan.source_id in known:
            continue
        additions.append({
            "id": plan.source_id,
            "url": plan.url,
            "fetch": "http",
            "normaliser": "text-default",
            "cited_regions": [{"id": "evidence", "locator": {"kind": "page", "value": ""}}],
        })
    if additions:
        block = yaml.safe_dump(additions, sort_keys=False, allow_unicode=True, width=100)
        path.write_text(
            text.rstrip() + "\n# MODEL-191: retained primary-source regions for existing lineup rows; "
            f"read {READ_DATE}.\n" + block,
            encoding="utf-8",
        )
    load_sources(path)


def main() -> None:
    _register_sources()
    store = CopyStore()
    copies = {key: _source_copy(plan, store) for key, plan in SOURCES.items()}
    queue = Queue(ROOT / "verification")
    filed_at = datetime.now(UTC)
    by_model: dict[str, list[ClaimPlan]] = {}
    for plan in CLAIMS:
        by_model.setdefault(plan.model_id, []).append(plan)

    filed = 0
    for model_id, plans in by_model.items():
        path = ROOT / "models" / f"{model_id}.md"
        text = path.read_text(encoding="utf-8")
        front = yaml.safe_load(text.split("---", 2)[1])
        rows = ((front.get("benchmarks") or {}).get("evidence") or [])
        updates = []
        for plan in plans:
            matches = [row for row in rows if row["benchmark_id"] == plan.benchmark_id
                       and not row.get("id")]
            if len(matches) != 1:
                raise SystemExit(
                    f"{model_id} {plan.benchmark_id}: expected one unfiled row, got {len(matches)}"
                )
            row = matches[0]
            original = evidence_key(row)
            source = SOURCES[plan.source]
            ref = SourceRef(
                source_id=source.source_id,
                snapshot_ref=copies[plan.source],
                cited_regions=["evidence"],
            )
            row.update({
                "id": evidence_id(model_id, row),
                "measured_by": "provider_self_report",
                "effort": plan.effort,
                "harness": None,
                "sources": [ref.model_dump(mode="json")],
            })
            names = tuple(dict.fromkeys(filter(None, (
                row.get("model_id_as_evaluated"), front.get("display_name"),
                front.get("version"), model_id.rsplit("/", 1)[-1],
            ))))
            queue.file(Claim(
                target=TargetRef(kind="evidence", id=row["id"]),
                subject=model_id,
                names=names,
                field=plan.benchmark_id,
                label=plan.label,
                value=row["score"],
                unit=row.get("unit"),
                conditions={"effort": plan.effort, "harness": None, "date": None},
                collector=COLLECTOR,
                sources=(ref,),
            ), at=filed_at)
            updates.append((original, dict(row)))
            filed += 1
        replace_evidence(path, text, updates)
    print(f"filed {filed} existing-row claims; 2 Gemini image-table rows remain quarantined")


if __name__ == "__main__":
    main()
