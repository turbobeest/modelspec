#!/usr/bin/env python3
"""Ingest MODEL-191 Arena refinement slices for the slice-1 premier set.

The collector reads only the pinned CC BY 4.0 LMArena Hugging Face dataset.
It writes benchmark pages, appends evidence rows to existing premier cards, and
files deterministic verification claims. Re-running it is idempotent.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from decision.model import SourceRef, TargetRef, VerificationActor
from decision.sources import CopyStore, load_sources
from decision.verify import Claim, Queue
from scripts import model_160_evidence as arena
from scripts.model_143_evidence import evidence_id

ROOT = Path(__file__).resolve().parents[1]
READ_DATE = "2026-09-27"
DATASET_URL = "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset"
COLLECTOR = VerificationActor(
    agent="codex-model-191",
    model_family="openai",
    method="pinned-arena-refinement-projection@1",
)


@dataclass(frozen=True)
class Slice:
    benchmark_id: str
    name: str
    config: str
    category: str
    subcategory: str
    measures: str
    languages: tuple[str, ...]
    modalities: tuple[str, ...]
    domains: tuple[tuple[str, str], ...]


def _language(benchmark_id: str, name: str, language: str) -> Slice:
    domains = (("chat_preference", "direct"),)
    if language != "English":
        domains += (("multilingual", "proxy"),)
    return Slice(
        benchmark_id,
        f"Arena {name} (style control)",
        "text_style_control",
        name.casefold(),
        f"pairwise human preference, {name} prompts",
        f"Arena's style-controlled preference rating over prompts in {name}.",
        (language,),
        ("text",),
        domains,
    )


SLICES = (
    _language("arena_sc_english", "English", "English"),
    _language("arena_sc_chinese", "Chinese", "Chinese"),
    _language("arena_sc_japanese", "Japanese", "Japanese"),
    _language("arena_sc_korean", "Korean", "Korean"),
    _language("arena_sc_russian", "Russian", "Russian"),
    _language("arena_sc_spanish", "Spanish", "Spanish"),
    _language("arena_sc_german", "German", "German"),
    _language("arena_sc_french", "French", "French"),
    _language("arena_sc_polish", "Polish", "Polish"),
    Slice(
        "arena_sc_vision_ocr",
        "Arena Vision OCR (style control)",
        "vision_style_control",
        "ocr",
        "pairwise human preference, OCR prompts",
        "Arena's style-controlled vision preference rating over prompts classified as OCR.",
        (),
        ("text", "image"),
        (("chat_preference", "direct"), ("vision_documents", "proxy")),
    ),
    Slice(
        "arena_sc_vision_diagram",
        "Arena Vision Diagram (style control)",
        "vision_style_control",
        "diagram",
        "pairwise human preference, diagram prompts",
        "Arena's style-controlled vision preference rating over prompts classified as diagrams.",
        (),
        ("text", "image"),
        (("chat_preference", "direct"), ("vision_documents", "proxy")),
    ),
    Slice(
        "arena_sc_vision_homework",
        "Arena Vision Homework (style control)",
        "vision_style_control",
        "homework",
        "pairwise human preference, visual homework prompts",
        "Arena's style-controlled vision preference rating over prompts classified as homework.",
        (),
        ("text", "image"),
        (("chat_preference", "direct"), ("vision_documents", "proxy")),
    ),
    Slice(
        "arena_sc_document",
        "Arena Document",
        "document",
        "overall",
        "pairwise human preference, document prompts",
        "Arena's preference rating over prompts that include documents.",
        (),
        ("text", "document"),
        (("chat_preference", "direct"), ("vision_documents", "proxy")),
    ),
    Slice(
        "arena_sc_industry_software_it_services",
        "Arena Software and IT Services (style control)",
        "text_style_control",
        "industry_software_and_it_services",
        "pairwise human preference, software and IT occupation category",
        "Arena's style-controlled preference rating over software and IT services prompts.",
        (),
        ("text",),
        (("chat_preference", "direct"), ("software_engineering", "proxy")),
    ),
    Slice(
        "arena_sc_industry_entertainment_sports_media",
        "Arena Entertainment, Sports and Media (style control)",
        "text_style_control",
        "industry_entertainment_and_sports_and_media",
        "pairwise human preference, entertainment, sports and media occupation category",
        "Arena's style-controlled preference rating over entertainment, sports and media prompts.",
        (),
        ("text",),
        (("chat_preference", "direct"), ("writing", "proxy")),
    ),
    Slice(
        "arena_sc_industry_mathematical",
        "Arena Mathematical Occupations (style control)",
        "text_style_control",
        "industry_mathematical",
        "pairwise human preference, mathematical occupation category",
        "Arena's style-controlled preference rating over mathematical occupation prompts.",
        (),
        ("text",),
        (("chat_preference", "direct"), ("maths", "proxy")),
    ),
    Slice(
        "arena_sc_factuality",
        "Arena Text Factuality",
        "text_factuality",
        "overall",
        "pairwise human preference, factuality-adjusted text view",
        "Arena's overall rating in the dataset's text_factuality view.",
        (),
        ("text",),
        (("chat_preference", "direct"), ("reasoning", "proxy")),
    ),
)


def _page_front(slice_: Slice) -> dict[str, Any]:
    return {
        "id": slice_.benchmark_id,
        "name": slice_.name,
        "aliases": [],
        "page_kind": "subset",
        "category": "human-preference",
        "subcategory": slice_.subcategory,
        "status": "active",
        "summary": f"{slice_.name}: {slice_.measures}",
        "measures": slice_.measures,
        "task_format": (
            "Anonymous side-by-side battles between two models; a person votes for "
            "the better response."
        ),
        "metric": {
            "name": "Arena score (Bradley-Terry, Elo scale)",
            "direction": "higher_is_better",
            "unit": "",
            "max_score": None,
            "random_baseline": None,
            "human_baseline": None,
            "baseline_note": (
                "Open-ended scale; only differences between models on one board are meaningful."
            ),
        },
        "dataset": {
            "size": None,
            "size_note": "Live vote corpus; each row reports its vote count.",
            "url": DATASET_URL,
            "license": "CC BY 4.0",
            "languages": list(slice_.languages),
            "modalities": list(slice_.modalities),
            "splits": "latest, full",
            "public_test_set": None,
        },
        "publisher": {"org": "Arena (formerly LMArena, LMSYS)", "authors": [],
                      "url": "https://arena.ai"},
        "paper": {
            "title": "Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference",
            "arxiv": "2403.04132",
            "url": "https://arxiv.org/abs/2403.04132",
            "year": 2024,
        },
        "leaderboard_url": "https://arena.ai/leaderboard",
        "repo_url": DATASET_URL,
        "released": "",
        "last_updated": "2026-09",
        "lineage": {"family": "arena_elo", "predecessor": "", "successors": [],
                    "variants": []},
        "saturation": {
            "status": "open",
            "top_score": None,
            "as_of": "2026-09",
            "note": "A rating scale has no ceiling; overlapping intervals indicate weak separation.",
        },
        "contamination": {
            "risk": "low",
            "note": (
                "Prompts are live user submissions and votes have no fixed answer key to leak."
            ),
        },
        "harness": {"lm_eval": "", "inspect_evals": "", "helm": "",
                    "opencompass": "", "bigbench": "",
                    "other": "No offline harness; ratings come from Arena votes."},
        "tags": ["human-preference", "arena", "elo"],
        "sources": [
            {"url": DATASET_URL,
             "title": "lmarena-ai/leaderboard-dataset (CC BY 4.0)",
             "accessed": READ_DATE},
            {"url": "https://arxiv.org/abs/2403.04132",
             "title": "Chatbot Arena (arXiv)", "accessed": READ_DATE},
        ],
        "freshness": {"researched": READ_DATE,
                      "researched_by": "Codex GPT-5, MODEL-191",
                      "reviewed": "", "reviewed_by": ""},
        "domains": [
            {"id": domain, "directness": directness}
            for domain, directness in slice_.domains
        ],
    }


def write_pages(root: Path = ROOT) -> None:
    for slice_ in SLICES:
        front = yaml.safe_dump(
            _page_front(slice_), sort_keys=False, allow_unicode=True, width=100
        ).rstrip()
        body = f"""---
{front}
---

Part of the [Arena Elo](arena_elo.md) family.

## What it measures

{slice_.measures} The value measures preference, not correctness.

## Reading the numbers

The rating is a Bradley-Terry score on an Elo scale. Compare values only within this board and
the same observation. ModelSpec keeps the board's confidence interval and vote count in each
evidence row. The source observation used for this page was read on {READ_DATE}.

## Source and attribution

Values come only from the pinned [LMArena Hugging Face dataset]({DATASET_URL}), licensed CC BY
4.0. ModelSpec reads config `{slice_.config}`, category `{slice_.category}`, split `latest`, at
revision `{arena.ARENA_REVISION}`. The board states its own publication date per row.
"""
        (root / "benchmarks" / f"{slice_.benchmark_id}.md").write_text(body, encoding="utf-8")


def _cards(root: Path) -> tuple[list[str], dict[str, Path]]:
    premier = [
        row["model_id"]
        for row in yaml.safe_load((root / "premier" / "slice-1.yaml").read_text())["models"]
    ]
    return premier, {model_id: root / "models" / f"{model_id}.md" for model_id in premier}


def _copies() -> dict[str, arena.Copy]:
    registry = arena.Registry(CopyStore())
    for config in sorted({slice_.config for slice_ in SLICES}):
        url = arena.ARENA_URL.format(config=config)
        raw, raw_ref = registry.fetch(url)
        for slice_ in (item for item in SLICES if item.config == config):
            projected = arena.project_arena(
                raw,
                config,
                slice_.category,
                url=url,
                page_ref=raw_ref,
                read_date=READ_DATE,
            )
            registry.add(
                slice_.benchmark_id,
                arena.arena_source(config),
                url,
                projected,
                "rating",
            )
    return registry.copies


def _arena_names(front: dict[str, Any], model_id: str) -> list[str]:
    evidence = ((front.get("benchmarks") or {}).get("evidence") or [])
    return list(dict.fromkeys(filter(None, [
        *(row.get("model_id_as_evaluated") for row in evidence
          if str(row.get("benchmark_id", "")).startswith("arena_")),
        front.get("display_name"),
        front.get("version"),
        model_id.rsplit("/", 1)[-1],
    ])))


def _new_row(model_id: str, slice_: Slice, copy: arena.Copy, match: dict[str, Any]) -> dict:
    evidence_date = str(match["leaderboard_publish_date"])
    row = {
        "benchmark_id": slice_.benchmark_id,
        "model_id_as_evaluated": arena._subject(match),
        "score": round(float(match["rating"]), 2),
        "unit": "Arena score (Elo scale)",
        "source_url": DATASET_URL,
        "source_kind": "independent_evaluator",
        "evidence_date": evidence_date,
        "date_type": "published",
        "observed_at": READ_DATE,
        "verified_at": READ_DATE,
        "benchmark_version": (
            f"{slice_.config} / {slice_.category}, latest split, "
            f"revision {arena.ARENA_REVISION[:12]}"
        ),
        "configuration": (
            f"Pinned LMArena dataset; publication date {evidence_date}; rating "
            f"{float(match['rating']):.2f} [{float(match['rating_lower']):.2f}, "
            f"{float(match['rating_upper']):.2f}], {int(match['vote_count'])} votes, "
            f"rank {int(match['rank'])}. Observed {READ_DATE}."
        ),
        "limitations": "Crowd preference, not a checked answer. Data: LMArena, CC BY 4.0.",
        "measured_by": "independent_evaluator",
        "effort": arena._effort(match),
        "harness": None,
        "sources": [{
            "source_id": copy.source_id,
            "snapshot_ref": copy.ref,
            "cited_regions": ["rows"],
        }],
    }
    row["id"] = evidence_id(model_id, row)
    return row


def _claim(model_id: str, front: dict[str, Any], row: dict[str, Any]) -> Claim:
    names = tuple(dict.fromkeys(filter(None, (
        row["model_id_as_evaluated"], front.get("display_name"), front.get("version"),
        model_id.rsplit("/", 1)[-1],
    ))))
    return Claim(
        target=TargetRef(kind="evidence", id=row["id"]),
        subject=model_id,
        names=names,
        field=row["benchmark_id"],
        label="rating",
        value=row["score"],
        unit=row["unit"],
        conditions={"effort": row["effort"], "harness": None,
                    "date": row["evidence_date"]},
        collector=COLLECTOR,
        sources=(SourceRef(**row["sources"][0]),),
    )


def ingest(*, root: Path = ROOT, dry_run: bool = False) -> tuple[int, list[tuple[str, str]]]:
    sources = load_sources(root / "registry" / "sources.yaml")
    for config in {slice_.config for slice_ in SLICES}:
        source_id = arena.arena_source(config)
        if source_id not in sources or sources[source_id].volatility != "live":
            raise ValueError(f"{source_id}: register the Arena source as live before ingestion")

    copies = _copies()
    premier, cards = _cards(root)
    queue = Queue(root / "verification")
    filed_at = datetime.now(UTC)
    added = 0
    unmatched: list[tuple[str, str]] = []
    for model_id in premier:
        path = cards[model_id]
        text = path.read_text(encoding="utf-8")
        front = yaml.safe_load(text.split("---", 2)[1])
        evidence = ((front.get("benchmarks") or {}).get("evidence") or [])
        existing = {row["benchmark_id"] for row in evidence}
        names = _arena_names(front, model_id)
        blocks: list[str] = []
        claims: list[Claim] = []
        for slice_ in SLICES:
            if slice_.benchmark_id in existing:
                continue
            copy = copies[slice_.benchmark_id]
            match = next((arena.board_row(copy, name) for name in names
                          if arena.board_row(copy, name) is not None), None)
            if match is None:
                unmatched.append((model_id, slice_.benchmark_id))
                continue
            row = _new_row(model_id, slice_, copy, match)
            blocks.append(arena.new_row_block(row))
            claims.append(_claim(model_id, front, row))
        added += len(blocks)
        if dry_run:
            continue
        if blocks:
            arena.append_rows(path, blocks)
        for claim in claims:
            queue.file(claim, at=filed_at)
    return added, unmatched


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if not args.dry_run:
        write_pages()
    added, unmatched = ingest(dry_run=args.dry_run)
    print(f"evidence rows {'matched' if args.dry_run else 'added'}: {added}")
    print(f"unmatched model/board pairs: {len(unmatched)}")


if __name__ == "__main__":
    main()
