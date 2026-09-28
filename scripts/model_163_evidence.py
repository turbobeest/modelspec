#!/usr/bin/env python3
"""File a focused verified-evidence set for MODEL-163 lineup additions."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

import yaml

from decision.model import SourceRef, TargetRef, VerificationActor
from decision.sources import CopyStore, load_sources
from decision.verify import Claim, Queue, StructuredDataExtractor, normalise_name
from scripts.model_143_evidence import (
    _set_field,
    canonical_snapshot,
    evidence_id,
    evidence_key,
    measured_by,
    source_date,
    source_id,
    source_row,
    source_url,
    verified_score,
)

ROOT = Path(__file__).resolve().parents[1]
FILED_AT = datetime(2026, 9, 26, 18, tzinfo=UTC)
COLLECTOR = VerificationActor(
    agent="openai-codex-model-163",
    model_family="gpt-5",
    method="retained-primary-board-snapshot@1",
)

# One directly relevant, exact-identity result is enough to admit each model.
SELECTED = {
    "bytedance/seed1-5-embedding": ("mteb_eng_v2", "mteb-eng-v2.json", "mean_task"),
    "google/gemini-2-5-flash": ("arena_elo_style_control", "arena-text.json", "rating"),
    "google/gemma-4-31b-it": ("gpqa_diamond", "epoch-gpqa_diamond.csv", "mean_score"),
    "microsoft/phi-4": ("arena_elo_style_control", "arena-text.json", "rating"),
    "qwen/qwen3-embedding-8b": ("mteb_eng_v2", "mteb-eng-v2.json", "mean_task"),
}
ARENA_STYLE_REF = SourceRef(
    source_id="model-160-arena-text-style-control",
    snapshot_ref="sha256:4662065250a8ba456c98963d631fa259b3f2c305e33d948af0f8907e71c23550",
    cited_regions=["rows"],
)


def frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---", 2)[1]), text


def replace_evidence(path: Path, text: str, original: tuple, row: dict) -> None:
    fields = (
        "model_id_as_evaluated", "score", "unit", "source_url", "evidence_date", "id",
        "measured_by", "effort", "harness", "sources",
    )

    found = False

    def update(match: re.Match[str]) -> str:
        nonlocal found
        block = match.group(0).rstrip("\n")
        parsed = yaml.safe_load("evidence:\n" + block)["evidence"][0]
        if evidence_key(parsed) != original:
            return match.group(0)
        found = True
        lines = block.splitlines()
        for field in fields:
            lines = _set_field(lines, field, row.get(field))
        return "\n".join(lines) + "\n"

    replaced = re.sub(
        r"(?ms)^  - benchmark_id:.*?(?=^  - benchmark_id:|^  [a-z][a-z0-9_]*:|^[a-z][a-z0-9_]*:)",
        update,
        text,
    )
    if not found:
        raise SystemExit(f"{path}: selected evidence row was not found")
    path.write_text(replaced, encoding="utf-8")


def main() -> None:
    inputs = ROOT / "premier" / "inputs"
    store = CopyStore()
    snapshots: dict[str, str] = {}
    for filename in sorted({row[1] for row in SELECTED.values()}):
        labels = {row[2] for row in SELECTED.values() if row[1] == filename}
        snapshots[filename] = store.put(canonical_snapshot(inputs / filename, labels))

    registered = load_sources(ROOT / "registry" / "sources.yaml")
    queue = Queue(ROOT / "verification")
    filed = 0
    for model_id, (benchmark, filename, label) in sorted(SELECTED.items()):
        path = ROOT / "models" / f"{model_id}.md"
        card, text = frontmatter(path)
        rows = (card.get("benchmarks") or {}).get("evidence") or []
        candidates = [row for row in rows if row.get("benchmark_id") == benchmark]
        if len(candidates) > 1:
            expected_url = source_url(inputs / filename)
            candidates = [row for row in candidates if row.get("source_url") == expected_url]
        if len(candidates) != 1:
            raise SystemExit(f"{model_id}: expected one {benchmark} row, got {len(candidates)}")
        row = dict(candidates[0])
        original = evidence_key(row)
        ref = ARENA_STYLE_REF if filename == "arena-text.json" else SourceRef(
            source_id=source_id(filename), snapshot_ref=snapshots[filename],
            cited_regions=["rows"],
        )
        if filename == "arena-text.json":
            source_rows = StructuredDataExtractor._rows(
                store.get(ref.snapshot_ref).decode("utf-8")
            ) or []
            expected = normalise_name(str(row.get("model_id_as_evaluated") or ""))
            exact = []
            for source_candidate in source_rows:
                candidate_normal = {
                    normalise_name(str(key)): value
                    for key, value in source_candidate.items()
                }
                candidate_subject = next((
                    candidate_normal.get(key) for key in StructuredDataExtractor._SUBJECTS
                    if candidate_normal.get(key)
                ), None)
                if candidate_subject and normalise_name(str(candidate_subject)) == expected:
                    exact.append(source_candidate)
            matched = exact[0] if len(exact) == 1 else None
        else:
            matched = source_row(filename, row)
        if matched is None:
            raise SystemExit(f"{model_id}: no exact retained row in {filename}")
        normal = {normalise_name(str(key)): value for key, value in matched.items()}
        subject = next(normal[key] for key in StructuredDataExtractor._SUBJECTS if normal.get(key))
        row["model_id_as_evaluated"] = str(subject)
        row["score"] = verified_score(row["score"], matched, label, row.get("unit"))
        if filename == "arena-text.json":
            row["unit"] = "Arena score (Elo scale)"
        row["source_url"] = source_url(inputs / filename)
        if observed := source_date(matched):
            row["evidence_date"] = observed
        row["id"] = evidence_id(model_id, row)
        row["measured_by"] = measured_by(row)
        effort_match = re.search(r"_(minimal|low|medium|high|xhigh|max)$", str(subject))
        row["effort"] = effort_match.group(1) if effort_match else None
        row["harness"] = None
        if ref.source_id not in registered:
            raise SystemExit(f"unregistered retained source: {ref.source_id}")
        row["sources"] = [ref.model_dump(mode="json")]
        replace_evidence(path, text, original, row)
        names = tuple(dict.fromkeys(filter(None, (
            row["model_id_as_evaluated"], card.get("display_name"), card.get("version"),
            model_id.rsplit("/", 1)[-1],
        ))))
        queue.file(Claim(
            target=TargetRef(kind="evidence", id=row["id"]),
            subject=model_id,
            names=names,
            field=benchmark,
            label=label,
            value=row["score"],
            unit=row.get("unit"),
            conditions={"effort": row["effort"], "harness": None,
                        "date": row.get("evidence_date")},
            collector=COLLECTOR,
            sources=(ref,),
        ), at=FILED_AT)
        filed += 1

    # V4.1 Flash is not yet an exact-identity row on the retained Arena board.
    # Its provider card publishes a structured GPQA-Diamond table, so admit
    # that self-report without pretending the older V4 Flash row is V4.1.
    model_id = "deepseek/deepseek-flash"
    path = ROOT / "models" / f"{model_id}.md"
    card, text = frontmatter(path)
    candidates = [
        row for row in (card.get("benchmarks") or {}).get("evidence") or []
        if row.get("benchmark_id") == "gpqa_diamond"
    ]
    if len(candidates) != 1:
        raise SystemExit(f"{model_id}: expected one provider GPQA row")
    row = dict(candidates[0])
    original = evidence_key(row)
    fact_ref = SourceRef.model_validate(card["facts"][0]["sources"][0])
    source_text = store.get(fact_ref.snapshot_ref).decode("utf-8")
    expected_row = "| GPQA Diamond (Pass@1) | 93.4 | **94.1** | 92.9 | 88.1 | 92.4 | 89.9 | 90.9 |"
    if expected_row not in source_text:
        raise SystemExit("DeepSeek provider table no longer contains the cited GPQA row")
    projection_ref = store.put(
        b"model | GPQA-Diamond | date\nDeepSeek-V4.1-Flash | 90.9% | 2026-09-10\n"
    )
    evidence_ref = SourceRef(
        source_id=fact_ref.source_id,
        snapshot_ref=projection_ref,
        cited_regions=fact_ref.cited_regions,
    )
    row["source_url"] = str(registered[fact_ref.source_id].url)
    row["id"] = evidence_id(model_id, row)
    row["measured_by"] = "provider_self_report"
    row["effort"] = None
    row["harness"] = None
    row["sources"] = [evidence_ref.model_dump(mode="json")]
    replace_evidence(path, text, original, row)
    queue.file(Claim(
        target=TargetRef(kind="evidence", id=row["id"]),
        subject=model_id,
        names=("DeepSeek-V4.1-Flash", "DeepSeek V4.1 Flash", "deepseek-flash"),
        field="gpqa_diamond",
        label="GPQA-Diamond",
        value=row["score"],
        unit=row.get("unit"),
        conditions={"effort": None, "harness": None, "date": row.get("evidence_date")},
        collector=COLLECTOR,
        sources=(evidence_ref,),
    ), at=FILED_AT)
    filed += 1
    print(f"filed {filed} focused evidence rows from retained primary snapshots")


if __name__ == "__main__":
    main()
