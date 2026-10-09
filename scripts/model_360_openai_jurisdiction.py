#!/usr/bin/env python3
"""Record OpenAI's parent jurisdiction from the Delaware AG release (MODEL-360).

The training entity is OpenAI OpCo, LLC, read from the existing terms source.
The parent is OpenAI, Inc. (now OpenAI Foundation). The Delaware Attorney
General's release of 2025-10-28 states that OpenAI, Inc. was incorporated as
a Delaware nonprofit corporation in 2015. OpenAI's structure page says that
nonprofit is now the OpenAI Foundation.

The script sets ``kind`` on the 23 existing ``lab-jurisdiction-*`` sources,
adds ``lab-jurisdiction-openai-foundation``, and rewrites only the ``openai``
lab. A second run writes the same bytes and files no claim.

``--claims`` files the openai claim with ``Queue.file``. It does not write
``verification/log.jsonl``. File once: a second ``--claims`` appends another
collected event.

Run with the code worktree on ``PYTHONPATH`` or pass ``--code`` (inserted first).
``--fetch`` is the directory that holds ``delaware-ag-openai.html``.

    python scripts/model_360_openai_jurisdiction.py \\
        --code <code worktree> --data <data worktree> --fetch <fetch dir>
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

READ_DATE = "2026-10-09"
FILED_AT = datetime(2026, 10, 9, tzinfo=UTC)
FETCH_NAME = "delaware-ag-openai.html"
FOUNDATION_ID = "lab-jurisdiction-openai-foundation"
FOUNDATION_URL = (
    "https://news.delaware.gov/2025/10/28/"
    "ag-jennings-completes-review-of-openai-recapitalization/"
)
EXCERPT = "OpenAI, Inc. was incorporated as a Delaware nonprofit corporation in 2015"
NOTE = (
    "The global terms name OpenAI OpCo, LLC, a Delaware company. "
    "The Delaware Attorney General's release of 2025-10-28 states OpenAI, Inc. "
    "was incorporated as a Delaware nonprofit corporation in 2015. "
    "OpenAI's structure page (https://openai.com/our-structure/) says that, "
    "with the structure announced on 2025-10-28, the nonprofit is now the "
    "OpenAI Foundation and the for-profit is OpenAI Group PBC, which the "
    "Foundation controls."
)
OFFICIAL_REGISTRY = (
    "lab-jurisdiction-cerebras",
    "lab-jurisdiction-google-alphabet",
    "lab-jurisdiction-google-llc",
    "lab-jurisdiction-jina-elastic",
    "lab-jurisdiction-meta",
    "lab-jurisdiction-microsoft",
    "lab-jurisdiction-nvidia",
    "lab-jurisdiction-qwen",
    "lab-jurisdiction-tencent",
)
PROVIDER_TERMS = (
    "lab-jurisdiction-annamodels",
    "lab-jurisdiction-bytedance",
    "lab-jurisdiction-deepseek",
    "lab-jurisdiction-jcorners",
    "lab-jurisdiction-jina",
    "lab-jurisdiction-kingsoft",
    "lab-jurisdiction-minimax",
    "lab-jurisdiction-moonshot",
    "lab-jurisdiction-openai",
    "lab-jurisdiction-querit",
    "lab-jurisdiction-typesafe",
    "lab-jurisdiction-xai",
    "lab-jurisdiction-zhipu",
)
LAB_DOCUMENTATION = ("lab-jurisdiction-anthropic",)
LAB_SOURCE = re.compile(
    r"(?ms)^- id: (?P<id>lab-jurisdiction-\S+)\n.*?(?=^- id: |\Z)"
)
OPENAI_LAB = re.compile(r"(?ms)^- id: openai\n.*?(?=^- id: |\Z)")
TERMS_REF = re.compile(
    r"(?m)^    - source_id: lab-jurisdiction-openai\n"
    r"      snapshot_ref: (sha256:[0-9a-f]{64})\n"
)
KIND_LINE = re.compile(r"(?m)^  kind:.*\n")
NORMALISER_LINE = re.compile(r"(?m)^(  normaliser: \S+\n)")


def kind_mapping() -> dict[str, str]:
    rows = (
        *tuple((source_id, "official_registry") for source_id in OFFICIAL_REGISTRY),
        *tuple((source_id, "provider_terms") for source_id in PROVIDER_TERMS),
        *tuple((source_id, "lab_documentation") for source_id in LAB_DOCUMENTATION),
    )
    mapping = dict(rows)
    if len(mapping) != len(rows) or len(mapping) != 23:
        raise SystemExit(f"kind mapping has {len(mapping)} ids, expected 23")
    return mapping


def yaml_scalar(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def atomic_write(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def write_if_changed(path: Path, text: str) -> bool:
    if path.read_text(encoding="utf-8") == text:
        return False
    atomic_write(path, text)
    return True


def with_kind(block: str, kind: str) -> str:
    source_id = block.split("\n", 1)[0]
    if KIND_LINE.search(block):
        return KIND_LINE.sub(f"  kind: {kind}\n", block, count=1)
    if NORMALISER_LINE.search(block) is None:
        raise SystemExit(f"{source_id}: no normaliser line to attach kind to")
    return NORMALISER_LINE.sub(rf"\1  kind: {kind}\n", block, count=1)


def set_kinds(text: str, mapping: dict[str, str]) -> str:
    seen: set[str] = set()
    pieces: list[str] = []
    last = 0
    for match in LAB_SOURCE.finditer(text):
        source_id = match.group("id")
        seen.add(source_id)
        pieces.append(text[last:match.start()])
        if source_id == FOUNDATION_ID:
            pieces.append(match.group(0))
        elif source_id not in mapping:
            raise SystemExit(f"{source_id}: not in the kind mapping")
        else:
            pieces.append(with_kind(match.group(0), mapping[source_id]))
        last = match.end()
    pieces.append(text[last:])
    missing = sorted(source_id for source_id in mapping if source_id not in seen)
    if missing:
        raise SystemExit("missing lab-jurisdiction sources: " + ", ".join(missing))
    updated = "".join(pieces)
    if LAB_SOURCE.sub("", text) != LAB_SOURCE.sub("", updated):
        raise SystemExit("sources.yaml changed outside lab-jurisdiction sources")
    return updated


def foundation_block() -> str:
    return (
        f"- id: {FOUNDATION_ID}\n"
        f"  url: {yaml_scalar(FOUNDATION_URL)}\n"
        "  volatility: static\n"
        "  fetch: http\n"
        "  normaliser: html-default\n"
        "  kind: official_registry\n"
        "  cited_regions:\n"
        "  - id: incorporation\n"
        "    locator:\n"
        "      kind: page\n"
        f"      value: {yaml_scalar('::excerpt=' + EXCERPT)}\n"
    )


def upsert_foundation(text: str) -> str:
    block = foundation_block()
    match = re.search(
        rf"(?ms)^- id: {re.escape(FOUNDATION_ID)}\n.*?(?=^- id: |\Z)",
        text,
    )
    if match:
        if match.group(0) == block:
            return text
        return text[:match.start()] + block + text[match.end():]
    if text and not text.endswith("\n"):
        text += "\n"
    return text + block


def openai_block(terms_ref: str, parent_ref: str) -> str:
    return (
        "- id: openai\n"
        f"  entity: {yaml_scalar('OpenAI OpCo, LLC')}\n"
        "  entity_code: US\n"
        f"  parent_entity: {yaml_scalar('OpenAI, Inc. (now OpenAI Foundation)')}\n"
        "  parent_code: US\n"
        f"  note: {yaml_scalar(NOTE)}\n"
        f"  read_date: '{READ_DATE}'\n"
        "  jurisdiction:\n"
        "    state: known\n"
        "    value:\n"
        "    - US\n"
        "    sources:\n"
        "    - source_id: lab-jurisdiction-openai\n"
        f"      snapshot_ref: {terms_ref}\n"
        "      cited_regions:\n"
        "      - incorporation\n"
        "      party: entity\n"
        f"    - source_id: {FOUNDATION_ID}\n"
        f"      snapshot_ref: {parent_ref}\n"
        "      cited_regions:\n"
        "      - incorporation\n"
        "      party: parent\n"
    )


def rewrite_openai(text: str, parent_ref: str) -> str:
    match = OPENAI_LAB.search(text)
    if match is None:
        raise SystemExit("labs.yaml: no openai lab")
    ref = TERMS_REF.search(match.group(0))
    if ref is None:
        raise SystemExit("labs.yaml: openai terms source has no snapshot_ref")
    block = openai_block(ref.group(1), parent_ref)
    if match.group(0) == block:
        updated = text
    else:
        updated = text[:match.start()] + block + text[match.end():]
    if OPENAI_LAB.sub("", text) != OPENAI_LAB.sub("", updated):
        raise SystemExit("labs.yaml changed outside the openai lab")
    return updated


def confirm_region(body: bytes) -> None:
    from dataclasses import replace

    from decision.normalise import NORMALISERS, Locator, normalise_document, select_region
    from decision.verify import jurisdiction_codes

    rules = replace(NORMALISERS["html-default"], strip_volatile=False)
    doc = normalise_document(body, rules)
    text = select_region(doc, Locator("page", "::excerpt=" + EXCERPT))
    if text is None or not text.strip():
        raise SystemExit("openai foundation region is empty")
    codes = jurisdiction_codes(text)
    if codes != frozenset({"US"}):
        raise SystemExit(f"openai foundation region reads {sorted(codes)}, expected US")


def file_claims(data: Path) -> int:
    from decision.labs import FACET, load_labs
    from decision.model import SourceRef, TargetRef, VerificationActor
    from decision.verify import Claim, Queue

    labs_now = load_labs(data)
    lab = labs_now["openai"]
    if lab.state != "known" or lab.entity is None:
        raise SystemExit("openai is not a known lab")
    fact = lab.fact()
    claim = Claim(
        target=TargetRef(kind="fact", id=fact["id"]),
        subject=f"lab:{lab.id}",
        names=(lab.entity,),
        field=FACET,
        value=fact["value"],
        collector=VerificationActor(agent="grok", model_family="grok", method="lab-registry@1"),
        sources=tuple(SourceRef.model_validate(source) for source in fact["sources"]),
    )
    Queue(data / "verification").file(claim, at=FILED_AT)
    return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code", type=Path, required=True, help="ModelSpec code worktree")
    parser.add_argument("--data", type=Path, required=True, help="modelspec-data worktree")
    parser.add_argument("--fetch", type=Path, required=True,
                        help=f"Directory that holds {FETCH_NAME}")
    parser.add_argument("--claims", action="store_true",
                        help="File the openai claim after writing the registry")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    code = args.code.resolve()
    data = args.data.resolve()
    fetch = args.fetch.resolve()
    sys.path.insert(0, str(code))
    from decision.labs import check_lab_copies, load_labs
    from decision.sources import CopyStore, load_sources

    if not (code / "decision" / "labs.py").is_file():
        raise SystemExit(f"--code is not the ModelSpec tree: {code}")
    sources_path = data / "registry" / "sources.yaml"
    labs_path = data / "registry" / "labs.yaml"
    if not sources_path.is_file() or not labs_path.is_file():
        raise SystemExit(f"--data has no registry: {data}")
    page = fetch / FETCH_NAME
    if not page.is_file():
        raise SystemExit(f"missing fetch file: {page}")
    body = page.read_bytes()
    confirm_region(body)
    mapping = kind_mapping()
    sources_text = upsert_foundation(set_kinds(sources_path.read_text(encoding="utf-8"), mapping))
    store = CopyStore()
    parent_ref = store.put(body)
    labs_text = rewrite_openai(labs_path.read_text(encoding="utf-8"), parent_ref)
    sources_changed = write_if_changed(sources_path, sources_text)
    labs_changed = write_if_changed(labs_path, labs_text)
    load_sources(sources_path)
    loaded = load_labs(data)
    check_lab_copies(data, loaded, store)
    openai = loaded["openai"]
    print(f"copy store: {store.root}")
    print(
        f"openai: {openai.state} {list(openai.value or [])} "
        f"entity={openai.entity} parent={openai.parent_entity}"
    )
    print("openai sources: " + ", ".join(source["source_id"] for source in openai.sources))
    print(f"foundation ref: {parent_ref}")
    print(f"sources written: {sources_changed}")
    print(f"labs written: {labs_changed}")
    print(f"xai: {loaded['xai'].state}")
    if args.claims:
        print(f"claims filed: {file_claims(data)}")


if __name__ == "__main__":
    main()
