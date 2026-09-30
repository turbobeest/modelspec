#!/usr/bin/env python3
"""File MathArena BrokenArXiv and ArXivMath evidence for the lineup (MODEL-233).

The premier set's reasoning-and-maths clause cites MathArena's expected-performance
board. MathArena now marks its final-answer and proof competitions deprecated, and
current frontier models appear only on its research-maths boards, BrokenArXiv and
ArXivMath. This script reads the Overall table of each, the boards
``refresh_leaderboards.MATHARENA_BOARDS`` registers for the weekly refresh.

For each board it fetches the table over plain HTTP, retains the fetched bytes and
the projection ``project_matharena`` makes of them, and registers the source. For
each lineup model in ``ROWS`` it appends one evidence row per board to the card and
files a claim citing the projection's ``rows`` region. The claim binds the score
and MathArena's release warning (``contamination_warning``) together, as the
snapshot does. ``StructuredDataExtractor`` reads it, so a deterministic reader is
the second key: run ``modelspec verify`` next.

A card that already carries a row for the board is left alone, so a second run
files nothing. Read 2026-09-29.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import yaml

from decision.model import SourceRef, TargetRef, VerificationActor, evidence_verification_value
from decision.sources import CopyStore, load_sources
from decision.verify import Claim, Queue, normalise_name
from scripts import model_160_evidence as readers
from scripts.model_143_evidence import evidence_id
from scripts.refresh_leaderboards import MATHARENA_BOARDS, _fetch

ROOT = Path(__file__).resolve().parents[1]
READ_DATE = "2026-09-29"
FILED_AT = datetime(2026, 9, 29, 23, tzinfo=UTC)
COLLECTOR = VerificationActor(
    agent="claude-model-233",
    model_family="anthropic",
    method="matharena-board-read@2026-09-29",
)

#: Lineup model -> the one row MathArena publishes for it, the highest effort run.
#: Not filed: Qwen3.8-Max (MathArena ran the 2026-08-02 release; the lineup card is
#: the 0902 snapshot) and Kimi K3 (Think) (a thinking variant is another identity).
ROWS = (
    ("anthropic/claude-opus-5-5", "Claude-Opus-5.5 (high)"),
    ("openai/gpt-6-sol", "GPT-6 Sol (max)"),
    ("openai/gpt-6-astra", "GPT-6 Astra (max)"),
    ("anthropic/claude-fable-5-1", "Claude-Fable-5.1 (low)"),
    ("xai/grok-4-7", "Grok 4.7 (xhigh)"),
    ("deepseek/deepseek-flash", "DeepSeek-V4.1-Flash (Max)"),
    ("meta/muse-spark-1-3", "Muse Spark 1.3"),
    ("google/gemini-3-8-flash", "Gemini 3.8 Flash"),
)

VERSION = {"brokenarxiv": "BrokenArXiv, MathArena Overall table",
           "arxivmath": "ArXivMath, MathArena Overall table"}


def card_path(model_id: str) -> Path:
    return ROOT / "models" / f"{model_id}.md"


def evidence_row(model_id: str, benchmark: str, url: str, source: SourceRef,
                 match: dict) -> dict:
    effort = readers._effort(match)
    row = {
        "benchmark_id": benchmark,
        "model_id_as_evaluated": match["model"],
        "score": match["accuracy"],
        "unit": "percent",
        "source_url": url,
        "source_kind": "benchmark_author",
        "evidence_date": READ_DATE,
        "date_type": "evaluated",
        "verified_at": READ_DATE,
        "benchmark_version": VERSION[benchmark],
        "configuration": (
            f"MathArena competition table read {READ_DATE}; the table states no run date, "
            "so the reading is dated by the observation. Accuracy averaged over four runs "
            f"per problem. Effort {effort or 'not stated'}, as the model cell names it."),
        "limitations": (
            "Overall pools MathArena's monthly editions, so it moves when an edition is "
            "added."
            + (" MathArena warns the model was released after the problems were."
               if match.get("release_warning") else "")),
        "measured_by": "benchmark_author",
        "effort": effort,
        "harness": None,
        "sources": [source.model_dump(mode="json")],
        "quality_flags": ["contamination_warning"] if match.get("release_warning") else None,
        "observed_at": READ_DATE,
    }
    row = {k: v for k, v in row.items() if k != "quality_flags" or v}
    row["id"] = evidence_id(model_id, row)
    return row


def claim_for(model_id: str, front: dict, row: dict) -> Claim:
    names = tuple(dict.fromkeys(filter(None, (
        row["model_id_as_evaluated"], front.get("display_name"), front.get("version"),
        model_id.rsplit("/", 1)[-1],
    ))))
    return Claim(
        target=TargetRef(kind="evidence", id=row["id"]),
        subject=model_id,
        names=names,
        field=row["benchmark_id"],
        label="accuracy",
        value=evidence_verification_value(row),
        unit=row["unit"],
        conditions={"effort": row["effort"], "harness": None, "date": row["evidence_date"]},
        collector=COLLECTOR,
        sources=(SourceRef(**row["sources"][0]),),
    )


def register(sources: list[dict]) -> None:
    path = ROOT / "registry" / "sources.yaml"
    known = load_sources(path)
    new = [s for s in sources if s["id"] not in known]
    if not new:
        return
    block = yaml.safe_dump(new, sort_keys=False, allow_unicode=True, width=100)
    text = path.read_text(encoding="utf-8").rstrip("\n")
    path.write_text(text + "\n# MODEL-233: MathArena research-maths boards (projections); "
                    f"read {READ_DATE}.\n" + block, encoding="utf-8")
    load_sources(path)


def run(dry_run: bool) -> list[tuple]:
    store = CopyStore()
    boards, registrations = {}, []
    for benchmark, (source_id, url) in MATHARENA_BOARDS.items():
        raw = _fetch(url)
        projected = readers.project_matharena(raw, url=url, page_ref=f"{store.put(raw)} {url}",
                                              read_date=READ_DATE)
        source = SourceRef(source_id=source_id, snapshot_ref=store.put(projected),
                           cited_regions=["rows"])
        boards[benchmark] = (url, source, json.loads(projected)["rows"])
        registrations.append({
            "id": source_id, "volatility": "live", "url": url, "fetch": "http",
            "normaliser": "text-default",
            "cited_regions": [{"id": "rows", "locator": {"kind": "page", "value": ""}}],
        })
    if not dry_run:
        register(registrations)

    queue = Queue(ROOT / "verification")
    report = []
    for model_id, name in ROWS:
        path = card_path(model_id)
        text = path.read_text(encoding="utf-8")
        front = yaml.safe_load(text.split("---", 2)[1])
        existing = (front.get("benchmarks") or {}).get("evidence") or []
        blocks, claims = [], []
        for benchmark, (url, source, rows) in boards.items():
            if any(r.get("benchmark_id") == benchmark and r.get("source_url") == url
                   for r in existing):
                report.append((model_id, benchmark, name, None, "already on the card"))
                continue
            matches = [r for r in rows
                       if normalise_name(r["model"]) == normalise_name(name)]
            if len(matches) != 1 or matches[0].get("accuracy") is None:
                report.append((model_id, benchmark, name, None, "no unique scored row"))
                continue
            row = evidence_row(model_id, benchmark, url, source, matches[0])
            blocks.append(readers.new_row_block(row))
            claims.append(claim_for(model_id, front, row))
            report.append((model_id, benchmark, name, row["score"],
                           ",".join(row.get("quality_flags", [])) or "filed"))
        if dry_run or not blocks:
            continue
        readers.append_rows(path, blocks)
        for claim in claims:
            queue.file(claim, at=FILED_AT)
    return report


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--dry-run", action="store_true",
                        help="Fetch and match, write nothing, print what would be filed.")
    args = parser.parse_args(argv)
    for row in run(args.dry_run):
        print(" | ".join("" if v is None else str(v) for v in row))


if __name__ == "__main__":
    main()
