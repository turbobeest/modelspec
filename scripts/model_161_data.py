#!/usr/bin/env python3
"""Collect the in-lineup MODEL-161 data fixes from primary sources.

The collector retains deterministic JSON projections, updates only slice-1
cards, and files every changed value for ``modelspec verify``. Read 2026-09-26.
"""

from __future__ import annotations

import json
import re
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from decision.model import SourceRef, TargetRef, VerificationActor
from decision.sources import CopyStore, load_sources
from decision.verify import Claim, Queue
from pipeline.hardware import WORKING_ALLOWANCE, fitting_quants, weights_gb
from scripts.model_143_evidence import _set_field
from scripts.model_160_evidence import (
    ARENA_REVISION,
    ARENA_URL,
    MATHARENA_URL,
    board_row,
    document,
    project_arena,
    project_matharena,
)

ROOT = Path(__file__).resolve().parents[1]
READ_DATE = "2026-09-26"
ME = VerificationActor(
    agent="codex-model-161",
    model_family="openai",
    method="retained-primary-source-projection@1",
)
USER_AGENT = "ModelSpec/1.0 (+https://modelspec.dev)"

MATHARENA_INDEX = "https://matharena.ai/"
MTEB_ENG = "https://mteb-leaderboard-backend.hf.space/v1/benchmarks/MTEB(eng,%20v2)/scores"
MTEB_MULTI = (
    "https://mteb-leaderboard-backend.hf.space/v1/benchmarks/"
    "MTEB(Multilingual,%20v2)/scores"
)
NVIDIA_4090 = "https://www.nvidia.com/en-us/geforce/graphics-cards/40-series/rtx-4090/"
QWEN_API = "https://huggingface.co/api/models/Qwen/Qwen3.8-Flash-Next"

VECTORISERS = {
    "jcorners/ingot-8b-r3": (
        "JCorners/Ingot-8B-R3",
        "https://huggingface.co/api/models/JCorners/Ingot-8B-R3",
        MTEB_ENG,
    ),
    "kingsoft/qzhou-embedding": (
        "Kingsoft-LLM/QZhou-Embedding",
        "https://huggingface.co/api/models/Kingsoft-LLM/QZhou-Embedding",
        MTEB_ENG,
    ),
    "microsoft/harrier-oss-v1-27b": (
        "microsoft/harrier-oss-v1-27b",
        "https://huggingface.co/api/models/microsoft/harrier-oss-v1-27b",
        MTEB_MULTI,
    ),
}


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=180) as response:  # noqa: S310
        return response.read()


def projection(url: str, rows: list[dict[str, Any]], provenance: dict[str, Any]) -> bytes:
    return (
        json.dumps(
            {"source_url": url, "read_date": READ_DATE, "provenance": provenance, "rows": rows},
            ensure_ascii=False,
            separators=(",", ":"),
        )
        + "\n"
    ).encode()


def retain(store: CopyStore, body: bytes) -> str:
    return store.put(body)


def source(source_id: str, url: str) -> dict[str, Any]:
    return {
        "id": source_id,
        "url": url,
        "fetch": "http",
        "normaliser": "text-default",
        "cited_regions": [{"id": "rows", "locator": {"kind": "page", "value": ""}}],
    }


def register(rows: list[dict[str, Any]]) -> None:
    path = ROOT / "registry" / "sources.yaml"
    known = load_sources(path)
    additions = [row for row in rows if row["id"] not in known]
    if not additions:
        return
    text = path.read_text(encoding="utf-8").rstrip("\n")
    block = yaml.safe_dump(additions, sort_keys=False, allow_unicode=True, width=100)
    path.write_text(
        text + "\n# MODEL-161: in-lineup recall data, read 2026-09-26.\n" + block,
        encoding="utf-8",
    )
    load_sources(path)


def card_path(model_id: str) -> Path:
    lab, model = model_id.split("/", 1)
    return ROOT / "models" / lab / f"{model}.md"


def front(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])


def evidence_blocks(text: str):
    return list(re.finditer(
        r"(?ms)^  - benchmark_id:.*?(?=^  - benchmark_id:|^  [a-z][a-z0-9_]*:|^[a-z][a-z0-9_]*:)",
        text,
    ))


def update_evidence(path: Path, benchmark: str, transform) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    changed: list[dict[str, Any]] = []

    def replace(match: re.Match[str]) -> str:
        block = match.group(0).rstrip("\n")
        row = yaml.safe_load("evidence:\n" + block)["evidence"][0]
        if row["benchmark_id"] != benchmark:
            return match.group(0)
        updated = transform(dict(row))
        if updated == row:
            return match.group(0)
        lines = block.splitlines()
        for key in (
            "evidence_date", "verified_at", "configuration", "interval", "n",
            "quality_flags", "sources",
        ):
            if key in updated:
                lines = _set_field(lines, key, updated[key])
        changed.append(updated)
        return "\n".join(lines) + "\n"

    updated_text = re.sub(
        r"(?ms)^  - benchmark_id:.*?(?=^  - benchmark_id:|^  [a-z][a-z0-9_]*:|^[a-z][a-z0-9_]*:)",
        replace,
        text,
    )
    if changed:
        updated_text = re.sub(r"(?m)^card_updated:.*$", f"card_updated: '{READ_DATE}'", updated_text)
        path.write_text(updated_text, encoding="utf-8")
    return changed


def append_fact(path: Path, fact: dict[str, Any]) -> None:
    data = front(path)
    if any(row["facet"] == fact["facet"] for row in data.get("facts") or []):
        return
    text = path.read_text(encoding="utf-8")
    marker = "card_schema_version:"
    at = text.index(marker)
    dumped = yaml.safe_dump([fact], sort_keys=False, allow_unicode=True, width=100).rstrip()
    block = "\n".join(line[2:] if line.startswith("- ") else line for line in dumped.splitlines())
    # Restore the list marker only on the first line.
    lines = block.splitlines()
    lines[0] = "- " + lines[0]
    updated = text[:at] + "\n".join(lines) + "\n" + text[at:]
    updated = re.sub(r"(?m)^card_updated:.*$", f"card_updated: '{READ_DATE}'", updated)
    path.write_text(updated, encoding="utf-8")


def update_fact_sources(path: Path, fact_id: str, sources: list[dict[str, Any]]) -> None:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"(?ms)^- id: {re.escape(fact_id)}\n.*?(?=^- (?:id|facet):|^card_schema_version:)"
    )
    match = pattern.search(text)
    if match is None:
        raise RuntimeError(f"missing fact {fact_id} in {path}")
    block = match.group(0).rstrip("\n")
    start = block.find("\n  sources:")
    if start < 0:
        raise RuntimeError(f"missing sources for {fact_id} in {path}")
    dumped = yaml.safe_dump({"sources": sources}, sort_keys=False, allow_unicode=True).rstrip()
    replacement = "\n" + "\n".join(f"  {line}" for line in dumped.splitlines())
    updated_block = block[:start] + replacement
    if updated_block != block:
        path.write_text(
            text[:match.start()] + updated_block + "\n" + text[match.end():],
            encoding="utf-8",
        )


def names(model_id: str, row: dict[str, Any], data: dict[str, Any]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(filter(None, (
        row.get("model_id_as_evaluated"), data.get("display_name"), model_id.rsplit("/", 1)[-1]
    ))))


def evidence_claim(model_id: str, row: dict[str, Any]) -> Claim:
    data = front(card_path(model_id))
    return Claim(
        target=TargetRef(kind="evidence", id=row["id"]),
        subject=model_id,
        names=names(model_id, row, data),
        field=row["benchmark_id"],
        label="rating" if row["benchmark_id"] == "arena_elo_overall" else "accuracy",
        value=row["score"],
        unit=row.get("unit"),
        conditions={
            "effort": row.get("effort"),
            "harness": row.get("harness"),
            "date": row.get("evidence_date"),
        },
        collector=ME,
        sources=tuple(SourceRef(**ref) for ref in row["sources"]),
    )


def fact_claim(
    model_id: str,
    fact: dict[str, Any],
    *,
    label: str,
    unit: str | None = None,
    names_extra: tuple[str, ...] = (),
) -> Claim:
    data = front(card_path(model_id))
    return Claim(
        target=TargetRef(kind="fact", id=fact["id"]),
        subject=model_id,
        names=tuple(dict.fromkeys((
            data["display_name"], model_id.rsplit("/", 1)[-1], *names_extra,
        ))),
        field=fact["facet"],
        label=label,
        value=fact["value"],
        unit=unit,
        collector=ME,
        sources=tuple(SourceRef(**ref) for ref in fact["sources"]),
    )


def main() -> None:
    store = CopyStore()
    queue = Queue(ROOT / "verification")
    filed_at = datetime.now(UTC)
    registrations: list[dict[str, Any]] = []
    claims: list[Claim] = []

    premier = {
        row["model_id"]
        for row in yaml.safe_load((ROOT / "premier" / "slice-1.yaml").read_text())["models"]
    }

    # Arena rating intervals and vote counts.
    arena_url = ARENA_URL.format(config="text")
    arena_raw = fetch(arena_url)
    raw_ref = retain(store, arena_raw)
    arena_body = project_arena(
        arena_raw,
        "text",
        "overall",
        url=arena_url,
        page_ref=raw_ref,
        read_date=READ_DATE,
    )
    arena_ref = retain(store, arena_body)
    # MODEL-160 already registered this exact pinned parquet. Reuse that
    # source identity and retain a richer projection with its intervals.
    arena_source = "model-160-arena-text"
    arena_rows = json.loads(arena_body)["rows"]
    for model_id in sorted(premier):
        path = card_path(model_id)
        if not path.is_file():
            continue

        def arena_update(row, model_id=model_id):
            match = board_row(
                type("Copy", (), {"rows": arena_rows})(),
                str(row.get("model_id_as_evaluated") or ""),
                row.get("effort"),
                row.get("evidence_date"),
            )
            if match is None:
                return row
            row["interval"] = [round(float(match["rating_lower"]), 2),
                               round(float(match["rating_upper"]), 2)]
            row["n"] = int(match["vote_count"])
            row["sources"] = [{
                "source_id": arena_source,
                "snapshot_ref": arena_ref,
                "cited_regions": ["rows"],
            }]
            return row

        for row in update_evidence(path, "arena_elo_overall", arena_update):
            claims.append(evidence_claim(model_id, row))

    # MathArena benchmark deprecation and row contamination warnings.
    index_html = fetch(MATHARENA_INDEX).decode()
    if not re.search(
        r'is-deprecated[^>]+data-competition-id="aime--aime_2026"|'
        r'data-competition-id="aime--aime_2026"[^>]+is-deprecated',
        index_html,
    ):
        raise RuntimeError("MathArena no longer marks AIME 2026 deprecated")
    table_raw = fetch(MATHARENA_URL)
    table_ref_raw = retain(store, table_raw)
    table_body = project_matharena(
        table_raw, url=MATHARENA_URL, page_ref=table_ref_raw, read_date=READ_DATE
    )
    table_ref = retain(store, table_body)
    table_source = "model-161-matharena-aime-2026"
    registrations.append(source(table_source, MATHARENA_URL))
    table_rows = json.loads(table_body)["rows"]
    quality_body = projection(
        MATHARENA_INDEX,
        [{"model": "AIME 2026", "deprecated": True}],
        {"selector": 'button[data-competition-id="aime--aime_2026"].is-deprecated'},
    )
    quality_ref = retain(store, quality_body)
    quality_source = "model-161-matharena-aime-2026-quality"
    registrations.append(source(quality_source, MATHARENA_INDEX))
    for model_id in sorted(premier):
        path = card_path(model_id)
        if not path.is_file():
            continue

        def math_update(row):
            match = board_row(
                type("Copy", (), {"rows": table_rows})(),
                str(row.get("model_id_as_evaluated") or ""),
                row.get("effort"),
            )
            flags = ["deprecated"]
            if match and match.get("release_warning"):
                flags.append("contamination_warning")
            row["evidence_date"] = READ_DATE
            row["verified_at"] = READ_DATE
            row["configuration"] = str(row.get("configuration") or "").replace(
                "2026-09-24", READ_DATE
            )
            row["quality_flags"] = flags
            row["sources"] = [
                {"source_id": table_source, "snapshot_ref": table_ref, "cited_regions": ["rows"]},
                {"source_id": quality_source, "snapshot_ref": quality_ref,
                 "cited_regions": ["rows"]},
            ]
            return row

        for row in update_evidence(path, "aime_2026", math_update):
            claims.append(evidence_claim(model_id, row))

    # English-language facts from model-card metadata and MTEB metadata.
    mteb_cache = {url: json.loads(fetch(url)) for url in (MTEB_ENG, MTEB_MULTI)}
    for model_id, (published_name, api_url, mteb_url) in VECTORISERS.items():
        api = json.loads(fetch(api_url))
        api_languages = api.get("cardData", {}).get("language") or []
        mteb_row = next(row for row in mteb_cache[mteb_url]["rows"]
                        if row["model"]["name"].casefold() == published_name.casefold())
        mteb_languages = mteb_row["model"].get("languages") or []
        if "en" not in api_languages or not any(
            str(value).casefold() == "english" for value in mteb_languages
        ):
            raise RuntimeError(f"{model_id}: primary sources do not both state English")
        slug = model_id.replace("/", "-")
        api_source = f"model-161-{slug}-model-card"
        mteb_source = f"model-161-{slug}-mteb"
        api_ref = retain(store, projection(
            api_url,
            [{"model": published_name, "languages": "en"}],
            {"cardData.language": api_languages},
        ))
        mteb_ref = retain(store, projection(
            mteb_url,
            [{"model": published_name, "languages": "en"}],
            {"rows[].model.languages": mteb_languages},
        ))
        registrations.extend([source(api_source, api_url), source(mteb_source, mteb_url)])
        fact = {
            "id": f"{model_id}#model.languages",
            "subject": {"kind": "model", "id": model_id},
            "facet": "model.languages",
            "value": ["en"],
            "state": "known",
            "sources": [
                {"source_id": api_source, "snapshot_ref": api_ref, "cited_regions": ["rows"]},
                {"source_id": mteb_source, "snapshot_ref": mteb_ref, "cited_regions": ["rows"]},
            ],
        }
        append_fact(card_path(model_id), fact)
        claims.append(fact_claim(
            model_id, fact, label="languages", names_extra=(published_name,),
        ))

    # Qwen parameter count and the deterministic RTX 4090 fit estimate.
    qwen = json.loads(fetch(QWEN_API))
    params = int(qwen["safetensors"]["total"])
    capacity_gb = 24.0
    nvidia_html = fetch(NVIDIA_4090).decode(errors="replace")
    if not re.search(r"24\s*GB", nvidia_html, re.IGNORECASE):
        raise RuntimeError("NVIDIA RTX 4090 page no longer discloses 24 GB")
    nvidia_body = projection(
        NVIDIA_4090,
        [{"model": "NVIDIA GeForce RTX 4090", "memory": "24 GB"}],
        {"selector": "RTX 4090 specifications; Standard Memory Config"},
    )
    nvidia_ref = retain(store, nvidia_body)
    nvidia_source = "model-161-nvidia-rtx-4090-memory"
    registrations.append(source(nvidia_source, NVIDIA_4090))
    quants = fitting_quants(params, capacity_gb)
    if quants:
        raise RuntimeError(f"Qwen unexpectedly fits the RTX 4090 at {quants}")
    fit_body = projection(
        QWEN_API,
        [{
            "model": "Qwen3.8-Flash-Next",
            "parameters_total": f"{params} parameters",
            "fits_hardware": "none",
            "nvidia_rtx_4090_capacity_gb": capacity_gb,
            "usable_capacity_gb": capacity_gb * (1 - WORKING_ALLOWANCE),
            "q4_weights_gb": weights_gb(params, "q4"),
        }],
        {
            "safetensors.total": params,
            "hardware_source": NVIDIA_4090,
            "formula": "pipeline.hardware.fitting_quants",
            "working_allowance": WORKING_ALLOWANCE,
        },
    )
    fit_ref = retain(store, fit_body)
    fit_source = "model-161-qwen3-8-flash-next-rtx-4090-fit"
    registrations.append(source(fit_source, QWEN_API))
    parameter_fact = {
        "id": "qwen/qwen3-8-flash-next#model.parameters_total",
        "subject": {"kind": "model", "id": "qwen/qwen3-8-flash-next"},
        "facet": "model.parameters_total",
        "value": params,
        "state": "known",
        "sources": [{"source_id": fit_source, "snapshot_ref": fit_ref,
                     "cited_regions": ["rows"]}],
    }
    fit_fact = {
        "id": "qwen/qwen3-8-flash-next#model.fits_hardware",
        "subject": {"kind": "model", "id": "qwen/qwen3-8-flash-next"},
        "facet": "model.fits_hardware",
        "value": [],
        "state": "known",
        "sources": [{"source_id": fit_source, "snapshot_ref": fit_ref,
                     "cited_regions": ["rows"]},
                    {"source_id": nvidia_source, "snapshot_ref": nvidia_ref,
                     "cited_regions": ["rows"]}],
    }
    qwen_path = card_path("qwen/qwen3-8-flash-next")
    append_fact(qwen_path, parameter_fact)
    append_fact(qwen_path, fit_fact)
    update_fact_sources(qwen_path, fit_fact["id"], fit_fact["sources"])
    claims.extend([
        fact_claim("qwen/qwen3-8-flash-next", parameter_fact,
                   label="parameters_total", unit="parameters"),
        fact_claim("qwen/qwen3-8-flash-next", fit_fact, label="fits_hardware"),
    ])

    register(registrations)
    for claim in claims:
        queue.file(claim, at=filed_at)
    print(f"filed {len(claims)} claims from {len(registrations)} registered sources")


if __name__ == "__main__":
    main()
