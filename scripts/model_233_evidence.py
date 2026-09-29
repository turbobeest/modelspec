#!/usr/bin/env python3
"""File MODEL-233's evidence for the thin lineup models, read 2026-09-29.

The MODEL-215 coverage report found 19 lineup models with admitted evidence on
fewer than two benchmarks, and two (Claude Opus 5.5, GPT-6 Sol) whose
reasoning-and-maths claim had no admitted row. This script closes what primary
sources can close, in two passes:

1. **Registered boards.** ``refresh_leaderboards.run`` with ``add_missing``,
   scoped to the thin models. It turns the cards' legacy board rows (no ID, no
   retained copy) into claims against this week's board reading, adds a row where
   a board lists the model and the card has none, and verifies each claim with
   the deterministic extractors. ``--boards`` runs this pass.
2. **Provider self-reports.** Each ``Source`` pins a primary page this ticket
   read; ``ROWS`` lists every value taken from them, with the name the page
   publishes. ``--self-reports`` fetches each page, retains the copy (a PDF is
   retained as the layout text of the cited pages, with a provenance header),
   refuses to continue when a value is not in the cited region, registers the
   source, writes or re-points the card row, and files a claim. The collector is
   Claude, so ``modelspec verify --llm-reader mistral`` reads them: another model
   family, as MODEL-159 requires.

A value that no permitted source publishes is left out: a null beats a guess.
Every such gap is listed in ``docs/research/model-233-lineup-evidence.md``.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import io
import re
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

import pypdf
import yaml

from decision.model import SourceRef, TargetRef, VerificationActor
from decision.normalise import NORMALISERS, Locator, normalise_document, select_region
from decision.sources import USER_AGENT, CopyStore, load_sources
from decision.verify import Claim, Queue
from scripts import refresh_leaderboards
from scripts.model_143_evidence import evidence_id
from scripts.model_160_evidence import new_row_block

ROOT = Path(__file__).resolve().parents[1]
READ_DATE = "2026-09-29"
FILED_AT = datetime(2026, 9, 29, 21, tzinfo=UTC)
COLLECTOR = VerificationActor(
    agent="claude-model-233",
    model_family="anthropic",
    method="primary-source-read@2026-09-29",
)
BOARD_COLLECTOR = VerificationActor(
    agent="claude-model-233",
    model_family="anthropic",
    method="registered-board-refresh@2026-09-29",
)


@dataclass(frozen=True)
class Source:
    id: str
    url: str
    normaliser: str
    region: str
    #: ``page`` or ``table``; a table locator's value is its index on the page.
    locator: tuple[str, str] = ("page", "")
    #: A PDF is retained as the layout text of these 1-based pages.
    pdf_pages: tuple[int, ...] = ()


@dataclass(frozen=True)
class Row:
    model_id: str
    benchmark_id: str
    score: float
    published_as: str
    #: The row or column label the source prints for the benchmark.
    label: str
    source: Source
    evidence_date: str
    benchmark_version: str
    configuration: str
    effort: str | None = None
    harness: str | None = None
    unit: str = "percent"
    limitations: str = ""
    #: What the collector looks for in the region, when the label is split across it.
    needle: str | None = None
    #: Whether the source prints the unit. A bare number confirms no unit, so the
    #: claim then carries none (the card row keeps the benchmark's unit).
    printed_unit: bool = True


GEMMA_4 = Source(
    id="model-233-google-gemma-4-model-card",
    url="https://ai.google.dev/gemma/docs/core/model_card_4",
    normaliser="html-default",
    region="benchmark-results",
    locator=("table", "2"),
)
GEMMA_4_NOTE = (
    "Google's Gemma 4 model card (last updated 2026-07-30), Benchmark Results table; "
    "the page states the results are for the instruction-tuned models.")

#: Table row label -> (benchmark, version, published values by column). Left out:
#: "Tau2 (average over 3)" (over three domains or three runs is not stated),
#: "HLE with search" (hle_tools is scored with general tools, not search alone),
#: and the rows with no benchmark page (LiveCodeBench v6, Codeforces ELO,
#: OmniDocBench 1.5, MATH-Vision, CoVoST, FLEURS).
GEMMA_4_TABLE = {
    "MMLU Pro": ("mmlu_pro", "MMLU-Pro", (85.2, 82.6, 69.4, 60.0)),
    "AIME 2026 no tools": ("aime_2026", "AIME 2026, no tools", (89.2, 88.3, 42.5, 37.5)),
    "GPQA Diamond": ("gpqa_diamond", "GPQA Diamond", (84.3, 82.3, 58.6, 43.4)),
    "HLE no tools": ("hle", "Humanity's Last Exam, no tools", (19.5, 8.7, None, None)),
    "BigBench Extra Hard": ("bbeh", "BIG-Bench Extra Hard", (74.4, 64.8, 33.1, 21.9)),
    "MMMLU": ("mmmlu", "MMMLU", (88.4, 86.3, 76.6, 67.4)),
    "MRCR v2 8 needle 128k (average)": (
        "deepmind_mrcr_v2", "MRCR v2, 8 needles, up to 128K tokens, average",
        (66.4, 44.1, 25.4, 19.1)),
    "MMMU Pro": ("mmmu_pro", "MMMU-Pro", (76.9, 73.8, None, None)),
    "MedXPertQA MM": ("medxpertqa_multimodal", "MedXpertQA MM", (61.3, 58.1, None, None)),
}
#: Column order in the table. E4B and E2B are carded as ``llm-chat``, so their
#: vision rows are not taken (None above).
GEMMA_4_MODELS = (
    ("google/gemma-4-31b-it", "Gemma 4 31B"),
    ("google/gemma-4-26b-a4b-it", "Gemma 4 26B A4B"),
    ("google/gemma-4-e4b-it", "Gemma 4 E4B"),
    ("google/gemma-4-e2b-it", "Gemma 4 E2B"),
)

OPUS_5_5 = Source(
    id="model-233-anthropic-opus-5-5-system-card-table-8-1-a",
    url="https://www.anthropic.com/claude-opus-5-5-system-card",
    normaliser="text-default",
    region="table-8-1-a",
    pdf_pages=(174,),
)
OPUS_5_5_NOTE = (
    "Claude Opus 5.5 System Card (dated September 22, 2026), Table 8.1.A, Opus 5.5 column "
    "only. Adaptive thinking at {effort} effort, default sampling, averaged over five "
    "trials.")
#: (benchmark, row label, value, effort, version, needle). Terminal-Bench 4.0 is
#: reported at xhigh effort, per the table's caption. HealthBench Professional's
#: row is length-adjusted (section 8.15.2) and stays with MODEL-191's filing.
OPUS_5_5_TABLE = (
    ("swe_bench_pro", "SWE-bench Pro", 89.9, "max", "SWE-bench Pro", None),
    ("swe_bench_multilingual", "SWE-bench Multilingual", 93.9, "max",
     "SWE-bench Multilingual", None),
    ("swe_bench_multimodal", "SWE-bench Multimodal", 61.4, "max", "SWE-bench Multimodal", None),
    ("terminal_bench_v4_0", "Terminal-Bench 4.0", 66.4, "xhigh", "Terminal-Bench 4.0", None),
    ("terminal_bench_science", "Terminal-Bench-Science 0.1", 58.7, "max",
     "Terminal-Bench-Science 0.1", None),
    ("hle", "Humanity's Last Exam, no tools", 64.4, "max",
     "Humanity's Last Exam (no tools)", "No tools | 64.4"),
    ("hle_tools", "Humanity's Last Exam, with tools", 67.7, "max",
     "Humanity's Last Exam (with tools)", "With tools | 67.7"),
)

DEEPSEEK_V4_1_FLASH = Source(
    id="model-233-deepseek-v4-1-flash-model-card",
    url="https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash",
    normaliser="html-default",
    region="comparison-with-frontier-models",
    locator=("heading", "comparison-with-frontier-models-max-reasoning-effort"),
)
DEEPSEEK_NOTE = (
    "DeepSeek-V4.1-Flash model card on Hugging Face, 'Comparison with frontier models (Max "
    "reasoning effort)' table, DS-V4.1-Flash column only. The card evaluates agentic coding "
    "with the Minimal mode of DeepSeek Harness and a 1M-token context window.")
#: (benchmark, row label, value, extra configuration).
DEEPSEEK_TABLE = (
    ("hle", "HLE (Pass@1)", 36.8,
     " Full set; the card gives 39.1 on the text-only subset, not taken."),
    ("hle_tools", "HLE w/ tools (Pass@1)", 63.9, ""),
    ("terminal_bench_v2_1", "Terminal-Bench 2.1 (Pass@1)", 90.6, ""),
    ("terminal_bench_3_0", "Terminal-Bench 3.0 (Pass@1)", 30.0, ""),
    ("terminal_bench_v4_0", "Terminal-Bench 4.0 (Pass@1)", 31.2, ""),
    ("deepswe_v1_1", "DeepSWE v1.1 (Resolved)", 74.2, ""),
    ("cybergym", "CyberGym (Pass@1)", 88.1, ""),
)

QWEN_3_8_FLASH_NEXT = Source(
    id="model-233-qwen3-8-flash-next-model-card",
    url="https://huggingface.co/Qwen/Qwen3.8-Flash-Next",
    normaliser="html-default",
    region="benchmark-results-language",
    locator=("heading", "language"),
)
#: The README's last commit on Hugging Face.
QWEN_DATE = "2026-08-27"
QWEN_NOTE = (
    "Qwen3.8-Flash-Next model card on Hugging Face, Benchmark Results, Language table, "
    "Qwen3.8-Flash-Next column only.")
#: (benchmark, row label, value, extra configuration). The coding rows are left out:
#: their footnotes name a harness per row, or the best of two.
QWEN_TABLE = (
    ("gpqa_diamond", "GPQA Diamond", 91.7, ""),
    ("hle", "HLE", 35.9, " The card notes HLE is judged by GPT-4o."),
    ("ifbench", "IFBench", 81.3, ""),
)

ROWS: list[Row] = [
    Row(model_id=model_id, benchmark_id=benchmark, score=values[column],
        published_as=published, label=label, source=GEMMA_4, evidence_date="2026-07-30",
        benchmark_version=version_, configuration=GEMMA_4_NOTE)
    for label, (benchmark, version_, values) in GEMMA_4_TABLE.items()
    for column, (model_id, published) in enumerate(GEMMA_4_MODELS)
    if values[column] is not None
] + [
    Row(model_id="anthropic/claude-opus-5-5", benchmark_id=benchmark, score=score,
        published_as="Claude Opus 5.5", label=label, source=OPUS_5_5,
        evidence_date="2026-09-22", benchmark_version=version_,
        configuration=OPUS_5_5_NOTE.format(effort=effort), effort=effort, needle=needle,
        printed_unit=False)
    for benchmark, label, score, effort, version_, needle in OPUS_5_5_TABLE
] + [
    Row(model_id="deepseek/deepseek-flash", benchmark_id=benchmark, score=score,
        published_as="DS-V4.1-Flash", label=label, source=DEEPSEEK_V4_1_FLASH,
        evidence_date="2026-09-10", benchmark_version=label,
        configuration=DEEPSEEK_NOTE + extra, effort="max", printed_unit=False)
    for benchmark, label, score, extra in DEEPSEEK_TABLE
] + [
    Row(model_id="qwen/qwen3-8-flash-next", benchmark_id=benchmark, score=score,
        published_as="Qwen3.8-Flash-Next", label=label, source=QWEN_3_8_FLASH_NEXT,
        evidence_date=QWEN_DATE, benchmark_version=label,
        configuration=QWEN_NOTE + extra, printed_unit=False)
    for benchmark, label, score, extra in QWEN_TABLE
]


# --- retained copies ------------------------------------------------------------------------------


def _fetch(url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response:  # noqa: S310 - pinned URLs
        return response.read(), response.geturl()


def _pdf_copy(source: Source, body: bytes, resolved: str) -> bytes:
    reader = pypdf.PdfReader(io.BytesIO(body))
    pages = "\n\n".join(
        f"PDF page {n}\n" + "\n".join(
            re.sub(r" {2,}", " | ", line.strip())
            for line in reader.pages[n - 1].extract_text(extraction_mode="layout").splitlines())
        for n in source.pdf_pages
    )
    header = (
        f"Provenance: layout text extracted with pypdf {version('pypdf')} from page(s) "
        f"{', '.join(map(str, source.pdf_pages))} of the PDF served at {source.url}, "
        f"resolved to {resolved}, SHA-256 {hashlib.sha256(body).hexdigest()}; each run of "
        f"two or more spaces between columns is written as ' | '. Read {READ_DATE}.\n\n"
    )
    return (header + pages).encode()


def retain(source: Source, store: CopyStore) -> tuple[str, str]:
    """The copy ref and the cited region's normalised text."""
    body, resolved = _fetch(source.url)
    if source.pdf_pages:
        body = _pdf_copy(source, body, resolved)
    ref = store.put(body)
    doc = normalise_document(body, NORMALISERS[source.normaliser])
    region = select_region(doc, Locator(kind=source.locator[0], value=source.locator[1]))
    if region is None:
        raise SystemExit(f"{source.id}: cited region {source.locator} not found")
    return ref, region


def register(sources: list[Source]) -> None:
    path = ROOT / "registry" / "sources.yaml"
    text = path.read_text(encoding="utf-8")
    known = load_sources(path)
    entries = []
    for source in sources:
        if source.id in known:
            continue
        kind, value = source.locator
        entries.append(
            f"- id: {source.id}\n"
            f"  url: {source.url}\n"
            f"  fetch: http\n"
            f"  normaliser: {source.normaliser}\n"
            f"  cited_regions:\n"
            f"  - id: {source.region}\n"
            f"    locator:\n"
            f"      kind: {kind}\n"
            f"      value: '{value}'\n"
        )
    if entries:
        path.write_text(
            text.rstrip("\n") + "\n# MODEL-233: primary sources for the thin lineup models.\n"
            + "".join(entries), encoding="utf-8")
        load_sources(path)


def _number(score: float) -> str:
    return f"{score:g}" if score != int(score) else f"{int(score)}"


def check_region(row: Row, region: str) -> None:
    """The collector's own read: the row's label and value are in the cited region."""
    flat = re.sub(r"\s+", " ", region)
    for needle in (row.needle or row.label, _number(row.score)):
        if needle not in flat:
            raise SystemExit(f"{row.model_id} {row.benchmark_id}: {needle!r} "
                             f"not in {row.source.id}")


# --- cards ----------------------------------------------------------------------------------------

_BLOCK = re.compile(
    r"(?ms)^  - benchmark_id:.*?(?=^  - benchmark_id:|^  [a-z][a-z0-9_]*:|^[a-z][a-z0-9_]*:)")


@functools.cache
def card_path(model_id: str) -> Path:
    path = ROOT / "models" / f"{model_id}.md"
    if not path.is_file():
        raise SystemExit(f"no card for {model_id}")
    return path


def card_row(row: Row, ref: str) -> dict:
    record = {
        "benchmark_id": row.benchmark_id,
        "model_id_as_evaluated": row.published_as,
        "score": row.score,
        "unit": row.unit,
        "source_url": row.source.url,
        "source_kind": "provider_self_report",
        "evidence_date": row.evidence_date,
        "date_type": "published",
        "verified_at": READ_DATE,
        "benchmark_version": row.benchmark_version,
        "configuration": row.configuration,
        "limitations": row.limitations,
        "measured_by": "provider_self_report",
        "effort": row.effort,
        "harness": row.harness,
        "sources": [SourceRef(source_id=row.source.id, snapshot_ref=ref,
                              cited_regions=[row.source.region]).model_dump(mode="json")],
    }
    record["id"] = evidence_id(row.model_id, record)
    return record


def _same_value(block: dict, row: Row) -> bool:
    return (block.get("benchmark_id") == row.benchmark_id
            and abs(float(block.get("score", "nan")) - row.score) < 1e-9)


def write_rows(model_id: str, records: list[tuple[Row, dict]]) -> None:
    """Replace a card's unfiled row with the same benchmark and value; append the rest."""
    path = card_path(model_id)
    text = path.read_text(encoding="utf-8")
    pending = list(records)

    def replace(match: re.Match[str]) -> str:
        block = yaml.safe_load("evidence:\n" + match.group(0))["evidence"][0]
        for item in pending:
            row, record = item
            if _same_value(block, row) and (not block.get("id") or block["id"] == record["id"]):
                pending.remove(item)
                return new_row_block(record)
        return match.group(0)

    path.write_text(_BLOCK.sub(replace, text), encoding="utf-8")
    if pending:
        refresh_leaderboards._append_evidence(path, [record for _, record in pending])


def names(row: Row) -> tuple[str, ...]:
    front = yaml.safe_load(card_path(row.model_id).read_text(encoding="utf-8").split("---", 2)[1])
    return tuple(dict.fromkeys((row.published_as, front["display_name"],
                                row.model_id.rsplit("/", 1)[-1])))


# --- passes ---------------------------------------------------------------------------------------


def self_reports() -> None:
    store = CopyStore()
    used = list(dict.fromkeys(row.source for row in ROWS))
    copies = {source.id: retain(source, store) for source in used}
    for row in ROWS:
        check_region(row, copies[row.source.id][1])
    register(used)
    records = [(row, card_row(row, copies[row.source.id][0])) for row in ROWS]
    by_model: dict[str, list[tuple[Row, dict]]] = {}
    for row, record in records:
        by_model.setdefault(row.model_id, []).append((row, record))
    for model_id, rows in by_model.items():
        write_rows(model_id, rows)
    # Claims are filed once every card is written, so a failed write files nothing.
    queue = Queue(ROOT / "verification")
    for row, record in records:
        ref = copies[row.source.id][0]
        queue.file(Claim(
            target=TargetRef(kind="evidence", id=record["id"]),
            subject=row.model_id,
            names=names(row),
            field=row.benchmark_id,
            label=row.label,
            value=row.score,
            unit=row.unit if row.printed_unit else None,
            conditions={"effort": row.effort, "harness": row.harness, "date": None},
            collector=COLLECTOR,
            sources=(SourceRef(source_id=row.source.id, snapshot_ref=ref,
                               cited_regions=[row.source.region]),),
        ), at=FILED_AT)
    print(f"filed {len(ROWS)} self-reported values from {len(used)} sources")


#: Board rows published under a name the card does not carry, matched literally:
#: model -> {name on the board: the effort that name states}. Epoch's ``_max`` is
#: an effort suffix the verifier reads; LMArena's ``-max`` names the product row,
#: as on these cards' verified arena_webdev rows.
BOARD_NAMES: dict[str, dict[str, str | None]] = {
    "anthropic/claude-opus-5-5": {"claude-opus-5-5_max": "max"},
    "openai/gpt-6-sol": {"gpt-6-sol-max": None},
    "openai/gpt-6-luna": {"gpt-6-luna-max": None},
}


#: Board rows not added yet: model -> benchmarks. Epoch's GPQA Diamond row for
#: Claude Opus 5.5 is true and verifies, but recall question Q06's approved
#: answer requires Opus 5.5 to be flagged "may qualify" for want of that row.
#: It waits for the expected answer's re-approval (docs/recall/2026-09-29-model-233-q06.md).
BOARD_HOLD: dict[str, frozenset[str]] = {
    "anthropic/claude-opus-5-5": frozenset({"gpqa_diamond"}),
}


def _with_board_names(refresh) -> None:
    match, new = refresh._matching_new_row, refresh._new_evidence

    def matching(board, front):
        found = match(board, front)
        if found is not None:
            return found
        names = BOARD_NAMES.get(str(front.get("model_id")), {})
        hits = [row for row in board.rows if refresh._subject(row) in names]
        return hits[0] if len(hits) == 1 else None

    def evidence(*, root, model_id, front, board):
        rows, failures = new(root=root, model_id=model_id, front=front, board=board)
        held = BOARD_HOLD.get(model_id, frozenset())
        rows = [row for row in rows if row["benchmark_id"] not in held]
        for row in rows:
            effort = BOARD_NAMES.get(model_id, {}).get(row["model_id_as_evaluated"])
            if effort:
                row["effort"] = effort
        return rows, failures

    refresh._matching_new_row, refresh._new_evidence = matching, evidence


def boards(model_ids: list[str]) -> None:
    refresh_leaderboards.COLLECTOR = BOARD_COLLECTOR
    # Each board looks for a metadata template across every card: cache the parse.
    refresh_leaderboards._front = functools.cache(refresh_leaderboards._front)
    _with_board_names(refresh_leaderboards)
    report = refresh_leaderboards.run(observed_at=READ_DATE, dry_run=False,
                                      model_ids=model_ids, add_missing=True)
    print(refresh_leaderboards.render_report(report))
    print(f"added {report.added}; re-confirmed {len(report.reconfirmed)}; "
          f"changed {len(report.changes)}; quarantined {len(report.quarantined)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--boards", nargs="+", metavar="MODEL_ID")
    parser.add_argument("--self-reports", action="store_true")
    args = parser.parse_args()
    if args.boards:
        boards(args.boards)
    if args.self_reports:
        self_reports()


if __name__ == "__main__":
    main()
