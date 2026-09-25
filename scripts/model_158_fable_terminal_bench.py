#!/usr/bin/env python3
"""File Claude Fable 5.1's two Terminal-Bench 4.0 rows as claims (MODEL-158).

The rows had no ID, sources or verification, so every snapshot quarantined
them. MODEL-143's evidence script skipped the board row: its evaluated name,
"Fable 5.1 (max) with Claude Code", also matched the board's "Fable 5" row.

- 57.88 is the tbench.ai Terminal-Bench 4.0 row (Fable 5.1, Claude Code, max).
  The board is already registered as ``model-143-evidence-terminal-bench-4-0-json``
  with a retained copy that holds that row, so the claim cites that copy.
- 55.8 is section 8.6 of the Claude Fable 5.1 & Claude Mythos 5.1 System Card
  (dated September 1, 2026), a PDF. ``decision.normalise`` cannot read PDF yet,
  so the retained copy is the text of section 8.6 as ``pypdf`` extracts it from
  the PDF, with the PDF's URL and SHA-256 in a provenance header.

Run once, then ``modelspec verify --llm-reader claude``. Read 2026-09-25.
"""

from __future__ import annotations

import hashlib
import re
import urllib.request
from datetime import UTC, datetime
from importlib.metadata import version
from io import BytesIO
from pathlib import Path

import pypdf
import yaml

from decision.model import SourceRef, TargetRef, VerificationActor
from decision.sources import CopyStore, load_sources
from decision.verify import Claim, Queue
from scripts.model_143_evidence import evidence_id, evidence_key, replace_evidence

ROOT = Path(__file__).resolve().parents[1]
MODEL = "anthropic/claude-fable-5-1"
CARD = ROOT / "models" / "anthropic" / "claude-fable-5-1.md"
FILED_AT = datetime.now(UTC)
COLLECTOR = VerificationActor(
    agent="claude-model-158",
    model_family="anthropic",
    method="retained-primary-source@1",
)

BOARD_SOURCE = "model-143-evidence-terminal-bench-4-0-json"
BOARD_COPY = "sha256:660c5a0fbc79f54671c60e88cced246abad7b9b9935e1db6d63dc2fe30bb3204"
CARD_URL = "https://www.anthropic.com/claude-fable-5-1-system-card"
CARD_SOURCE = "model-158-anthropic-claude-fable-5-1-system-card"
CARD_REGION = "terminal-bench-4-0"
SECTION = re.compile(r"8\.6 Terminal-Bench 4\.0 .*?(?= 8\.7 )")


def system_card_copy(store: CopyStore) -> str:
    request = urllib.request.Request(CARD_URL, headers={"User-Agent": "ModelSpec/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:  # noqa: S310 - fixed URL
        body, resolved = response.read(), response.geturl()
    reader = pypdf.PdfReader(BytesIO(body))
    pages = (171, 172)
    text = re.sub(r"\s+", " ", " ".join(reader.pages[n - 1].extract_text() for n in pages))
    section = SECTION.search(text)
    if section is None:
        raise SystemExit("section 8.6 not found on pages 171-172")
    header = (
        f"Provenance: text extracted with pypdf {version('pypdf')} from pages "
        f"{pages[0]}-{pages[1]} (section 8.6) of the PDF served at {CARD_URL}, "
        f"resolved to {resolved}, SHA-256 {hashlib.sha256(body).hexdigest()}. "
        "Read 2026-09-25.\n\n"
    )
    return store.put((header + section.group(0).strip() + "\n").encode())


def register_card_source() -> None:
    path = ROOT / "registry" / "sources.yaml"
    text = path.read_text(encoding="utf-8")
    if f"- id: {CARD_SOURCE}\n" in text:
        return
    path.write_text(text + f"""\
# MODEL-158: the Fable 5.1 system card is a PDF, which the normaliser cannot read
# yet; its retained copy is the pypdf text of section 8.6 (Terminal-Bench 4.0).
- id: {CARD_SOURCE}
  url: {CARD_URL}
  fetch: http
  normaliser: text-default
  cited_regions:
  - id: {CARD_REGION}
    locator:
      kind: page
      value: ''
""", encoding="utf-8")
    load_sources(path)


def main() -> None:
    store = CopyStore()
    if not store.has(BOARD_COPY):
        raise SystemExit(f"retained board copy {BOARD_COPY} is missing")
    card_copy = system_card_copy(store)
    register_card_source()

    text = CARD.read_text(encoding="utf-8")
    front = yaml.safe_load(text.split("---", 2)[1])
    rows = [r for r in front["benchmarks"]["evidence"]
            if r["benchmark_id"] == "terminal_bench_v4_0" and not r.get("id")]
    by_url = {r["source_url"]: r for r in rows}
    board = by_url["https://www.tbench.ai/leaderboard/terminal-bench/4.0"]
    card = by_url[CARD_URL]

    plans = [
        # (row, evaluated name as the source writes it, measurer, source ref, label, date)
        (board, "Fable 5.1", "benchmark_author",
         SourceRef(source_id=BOARD_SOURCE, snapshot_ref=BOARD_COPY, cited_regions=["rows"]),
         "accuracy", board["evidence_date"]),
        # The section states no date, so the prose claim carries none to check.
        (card, "Claude Fable 5.1", "provider_self_report",
         SourceRef(source_id=CARD_SOURCE, snapshot_ref=card_copy, cited_regions=[CARD_REGION]),
         "Terminal-Bench 4.0", None),
    ]
    queue = Queue(ROOT / "verification")
    updates = []
    for row, evaluated, measurer, ref, label, day in plans:
        key = evidence_key(row)
        row["model_id_as_evaluated"] = evaluated
        row.update({
            "id": evidence_id(MODEL, row),
            "measured_by": measurer,
            "effort": "max",
            "harness": "unregistered",
            "sources": [ref.model_dump(mode="json")],
        })
        queue.file(Claim(
            target=TargetRef(kind="evidence", id=row["id"]),
            subject=MODEL,
            names=tuple(dict.fromkeys((evaluated, front["display_name"], "Fable 5.1"))),
            field="terminal_bench_v4_0",
            label=label,
            value=row["score"],
            unit=row["unit"],
            conditions={"effort": "max", "harness": "unregistered", "date": day},
            collector=COLLECTOR,
            sources=(ref,),
        ), at=FILED_AT)
        updates.append((key, dict(row)))
    replace_evidence(CARD, text, updates)
    print(f"filed {len(updates)} claims; system card copy {card_copy}")


if __name__ == "__main__":
    main()
