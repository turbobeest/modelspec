#!/usr/bin/env python3
"""Register and verify the premier set's board evidence, coding first (MODEL-160).

MODEL-143 filed a first cut of the premier cards' ``benchmarks.evidence`` rows.
This pass files the rest that a deterministic reader can check: every row whose
board publishes machine-readable data.

For each board the script fetches the page or file over plain HTTP (FrontierCode
and OSWorld 2 render client-side, so Firecrawl renders them; set
``FIRECRAWL_API_KEY``), retains the fetched bytes, and retains a JSON
*projection* of it: ``{source_url, read_date,
provenance, rows}``, one row per model, holding only the board's own fields,
renamed where the deterministic reader needs a known column name. The
provenance block names the fetched copy the projection was made from. Claims
cite the projection's ``rows`` region, which ``StructuredDataExtractor`` reads.

Collectors are recorded as the agent that filed the card row (``git blame`` on
the row, then the commit's AI co-author trailer). A row this script adds, or
whose value it corrects, is collected by this script. Rows that only an LLM
reader could check (system cards, launch pages) are not filed: their
collectors are Anthropic or unknown, so ``--llm-reader claude`` is not an
independent key for them. ``--report`` lists them.

MODEL-143 mapped ``arena_elo_style_control`` and ``arena_sc_vision`` to the raw
``text`` and ``vision`` Arena configs and overwrote the card scores with those
configs' ratings. This pass re-files both against the style-control configs the
benchmarks name, restoring the ratings MODEL-123 read.

Run once, then ``modelspec verify``. Read 2026-09-25.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import subprocess
import urllib.request
import zipfile
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq
import yaml

from decision.model import SourceRef, TargetRef, VerificationActor
from decision.normalise import NORMALISERS, Locator, normalise_document, select_region
from decision.sources import CopyStore, load_sources
from decision.verify import (
    Claim,
    Queue,
    StructuredDataExtractor,
    normalise_name,
    numbers_agree,
    parse_quantity,
    split_model_cell,
)
from scripts.model_143_evidence import _set_field, evidence_id, evidence_key

ROOT = Path(__file__).resolve().parents[1]
READ_DATE = "2026-09-25"
ME = VerificationActor(
    agent="claude-model-160",
    model_family="anthropic",
    method="retained-board-projection@1",
)
USER_AGENT = "ModelSpec/1.0 (+https://modelspec.dev)"
ARENA_REVISION = "1880dbebff5ba3e2dd3865ecf6fc43539c2099db"
ARENA_URL = ("https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/"
             f"{ARENA_REVISION}/{{config}}/latest-00000-of-00001.parquet")


# --- projections ------------------------------------------------------------------------------


def document(rows: list[dict], *, url: str, page_ref: str, read_date: str | None,
             note: str) -> bytes:
    data = {
        "source_url": url,
        "read_date": read_date,
        "provenance": {"fetched_copy": page_ref, "projection": note},
        "rows": [{k: v for k, v in row.items() if v is not None} for row in rows],
    }
    # One line: the text normaliser drops lines that are only punctuation ("{", "},").
    return (json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n").encode()


def _rsc_payload(html: str) -> str:
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)</script>', html, re.S)
    return "".join(json.loads(f'"{chunk}"') for chunk in chunks)


def project_scale(html: str, variant: str = "public", *, url: str, page_ref: str,
                  read_date: str = READ_DATE) -> bytes:
    """Scale Labs leaderboard: the entries the page's React payload carries."""
    payload = _rsc_payload(html)
    start = payload.index('"variants":') + len('"variants":')
    variants, _ = json.JSONDecoder().raw_decode(payload, start)
    entries = next(v["entries"] for v in variants if v["key"] == variant)
    rows = [{
        "model": e["model"],
        "resolve_rate": e["score"],
        "ci95": e.get("confidenceInterval_upper"),
        "date": e["createdAt"][:10],
        # The page: "*Run with mini-swe-agent harness".
        "agent": "mini-swe-agent" if e["model"].endswith("*") else None,
    } for e in entries]
    return document(rows, url=url, page_ref=page_ref, read_date=read_date,
                    note=f"variants[key={variant}].entries from the page's React payload; "
                         "score as resolve_rate (the page's primary metric), createdAt as "
                         "date, agent from the page's asterisk footnote")


def project_swebench(html: str, board: str, *, url: str, page_ref: str,
                     read_date: str = READ_DATE) -> bytes:
    """swebench.com: one board of the page's ``leaderboard-data`` JSON."""
    match = re.search(r'<script type="application/json" id="leaderboard-data">(.*?)</script>',
                      html, re.S)
    boards = json.loads(match.group(1))
    results = next(b["results"] for b in boards if b["name"] == board)
    rows = [{
        "model": r["name"],
        "resolve_rate": r["resolved"],
        "date": r["date"],
        "agent": r.get("agent"),
        "reasoning_effort": r.get("reasoning_effort"),
    } for r in results]
    return document(rows, url=url, page_ref=page_ref, read_date=read_date,
                    note=f"leaderboard-data[name={board}].results; resolved as resolve_rate")


def project_arena(parquet: bytes, config: str, category: str, *, url: str, page_ref: str,
                  read_date: str = READ_DATE) -> bytes:
    """LMArena's CC BY 4.0 dataset: one category of one config."""
    table = pq.read_table(io.BytesIO(parquet)).to_pylist()
    keys = ("model_name", "rating", "rating_lower", "rating_upper", "vote_count",
            "leaderboard_publish_date")
    rows = [{k: r.get(k) for k in keys} for r in table if r["category"] == category]
    return document(rows, url=url, page_ref=page_ref, read_date=read_date,
                    note=f"config {config}, category {category}")


_CURSOR_EFFORT = re.compile(r"^(.*?)\s+(Max|Extra High|High|Medium|Low|Minimal)$")
_EFFORTS = {"max": "max", "extra high": "xhigh", "high": "high", "medium": "medium",
            "low": "low", "minimal": "minimal"}


def _table_lines(html: str, index: int = 0) -> list[list[str]]:
    rules = replace(NORMALISERS["html-default"], strip_volatile=False)
    text = select_region(normalise_document(html.encode(), rules), Locator("table", str(index)))
    return [[c.strip() for c in re.split(r" ?\| ?", line)] for line in (text or "").splitlines()]


def project_cursorbench(html: str, *, url: str, page_ref: str,
                        read_date: str = READ_DATE) -> bytes:
    """Cursor's CursorBench board: the first table, effort split off the model cell."""
    rows = []
    for cells in _table_lines(html):
        if len(cells) < 4 or not re.fullmatch(r"\d+(?:\.\d+)?\s*%", cells[2]):
            continue
        name, effort = cells[1], None
        if m := _CURSOR_EFFORT.match(name):
            name, effort = m.group(1), _EFFORTS[m.group(2).casefold()]
        rows.append({
            "model": name,
            "reasoning_effort": effort,
            "accuracy": float(cells[2].rstrip("% ")),
            "usd_per_task": float(cells[3].lstrip("$ ").replace(",", "")),
        })
    return document(rows, url=url, page_ref=page_ref, read_date=read_date,
                    note="table 0; the trailing effort word of the model cell as "
                         "reasoning_effort (Extra High = xhigh); score column as accuracy")


def project_matharena(body: bytes, *, url: str, page_ref: str,
                      read_date: str = READ_DATE) -> bytes:
    """MathArena competition table: the ``table`` HTML the JSON carries."""
    lines = _table_lines(json.loads(body)["table"])
    header = [normalise_name(re.sub(r"\(.*?\)", "", c)) for c in lines[0]]
    name_at, value_at = header.index("model name"), header.index("accuracy")
    rows = []
    for cells in lines[1:]:
        if len(cells) != len(header):
            continue
        value = re.match(r"(\d+(?:\.\d+)?)%", cells[value_at])
        name = cells[name_at]
        flagged = "⚠" in name
        rows.append({
            "model": re.sub(r"[\s⚠️]+$", "", name),
            "accuracy": float(value.group(1)) if value else None,
            "release_warning": flagged or None,
        })
    return document(rows, url=url, page_ref=page_ref, read_date=read_date,
                    note="the JSON's table field, table 0; the percentage before the CI as "
                         "accuracy; the warning glyph as release_warning")


def project_metr(body: bytes, *, url: str, page_ref: str, read_date: str = READ_DATE) -> bytes:
    """METR's Time Horizon results YAML; horizons are minutes (METR's unit)."""
    results = yaml.safe_load(body)["results"]
    rows = []
    for key, value in results.items():
        metrics = value.get("metrics") or {}
        rows.append({
            "model": key,
            "benchmark_name": value.get("benchmark_name"),
            **{name: f"{metrics[name]['estimate']} minutes"
               for name in ("p50_horizon_length", "p80_horizon_length")
               if (metrics.get(name) or {}).get("estimate") is not None},
        })
    return document(rows, url=url, page_ref=page_ref, read_date=read_date,
                    note="results.<key>.metrics.<horizon>.estimate, stated in minutes")


def project_tau(body: bytes, *, url: str, page_ref: str, read_date: str = READ_DATE) -> bytes:
    """A tau-bench leaderboard submission: its banking_knowledge pass^1."""
    s = json.loads(body)
    result = s["results"]["banking_knowledge"]
    rows = [{
        "model": s["model_name"],
        "reasoning_effort": s.get("reasoning_effort"),
        "pass_1": f"{result['pass_1']}%",
        "date": (s.get("methodology") or {}).get("evaluation_date"),
    }]
    return document(rows, url=url, page_ref=page_ref, read_date=read_date,
                    note="results.banking_knowledge.pass_1 (percent), "
                         "methodology.evaluation_date as date")


def project_mteb(body: bytes, *, url: str, page_ref: str, read_date: str = READ_DATE) -> bytes:
    """The MTEB leaderboard API: task-type scores (fractions) per model."""
    rows = [{
        "model": r["model"]["name"],
        "mean_task": r.get("meanTask"),
        "reranking": (r.get("scoresByTaskType") or {}).get("Reranking"),
        "retrieval": (r.get("scoresByTaskType") or {}).get("Retrieval"),
    } for r in json.loads(body)["rows"]]
    return document(rows, url=url, page_ref=page_ref, read_date=read_date,
                    note="rows[].model.name, meanTask and scoresByTaskType")


def project_epoch(text: str, *, url: str, page_ref: str, read_date: str = READ_DATE) -> bytes:
    """An Epoch AI benchmark CSV (Epoch's own runs, CC BY 4.0)."""
    rows = [{
        "model": r["Model version"],
        "mean_score": float(r["mean_score"]),
        "stderr": float(r["stderr"]) if r.get("stderr") else None,
        "date": (r.get("Started at") or "")[:10] or None,
    } for r in csv.DictReader(io.StringIO(text))]
    return document(rows, url=url, page_ref=page_ref, read_date=read_date,
                    note="Model version, mean_score (fraction), stderr, Started at as date")


def project_deepswe(body: bytes, *, url: str, page_ref: str,
                    read_date: str = READ_DATE) -> bytes:
    """DeepSWE's live leaderboard artifact: one row per model and reasoning effort."""
    rows = [{
        "model": r["model"],
        "reasoning_effort": r.get("reasoning_effort"),
        "agent": r.get("harness"),
        "pass_at_1": f"{r['pass_at_1']} fraction",
    } for r in json.loads(body)["rows"] if r.get("pass_at_1") is not None]
    return document(rows, url=url, page_ref=page_ref, read_date=read_date,
                    note="rows[] model, reasoning_effort, harness as agent, pass_at_1 "
                         "(a fraction, as the artifact's unit note states)")


def _js_object(text: str, start: int) -> str:
    """The JavaScript object literal that opens at ``text[start]`` (``{``)."""
    depth, quoted, i = 0, False, start
    while True:
        c = text[i]
        if quoted:
            if c == "\\":
                i += 1
            elif c == '"':
                quoted = False
        elif c == '"':
            quoted = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
        i += 1


def project_vending(chunk: str, *, url: str, page_ref: str, read_date: str = READ_DATE) -> bytes:
    """Andon Labs' Vending-Bench 2 board data: the ``vb2`` object of the page's JS chunk."""
    board = _js_object(chunk, chunk.index("{vb2:{") + len("{vb2:"))
    rows, i = [], 1
    while (m := re.compile(r'"([^"]+)":\{').search(board, i)):
        entry = _js_object(board, m.end() - 1)
        value = re.search(r"(?<![\w.])final_value:([-\d.eE+]+)", entry)
        rows.append({"model": m.group(1),
                     "money_balance": f"{value.group(1)} USD" if value else None})
        i = m.end() - 1 + len(entry)
    return document(rows, url=url, page_ref=page_ref, read_date=read_date,
                    note="the vb2 object's final_value per model (mean money balance, USD)")


def _markdown_rows(markdown: str, first_header: str) -> tuple[list[str], list[list[str]]]:
    """The markdown table whose first header cell is ``first_header``."""
    lines = [line.strip() for line in markdown.splitlines()]
    for i, line in enumerate(lines):
        cells = [c.strip() for c in line.strip("|").split("|")]
        if line.startswith("|") and cells[0] == first_header:
            body = []
            for row in lines[i + 2:]:
                if not row.startswith("|"):
                    break
                body.append([c.strip() for c in row.strip("|").split("|")])
            return cells, body
    raise ValueError(f"no table headed {first_header!r}")


_GLUED_EFFORT = re.compile(r"^(.*?)\s?(max|xhigh|high|medium|low|minimal)$")


def project_frontiercode(markdown: str, *, url: str, page_ref: str,
                         read_date: str = READ_DATE) -> bytes:
    """Cognition's FrontierCode board, rendered: the leaderboard table."""
    header, body = _markdown_rows(markdown, "#")
    at = {normalise_name(h.rstrip("▼")): i for i, h in enumerate(header)}
    rows = []
    for cells in body:
        name = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", cells[at["model"]]).strip()
        effort = None
        if m := _GLUED_EFFORT.match(name):  # the render glues the effort label to the name
            name, effort = m.group(1).strip(), m.group(2)
        rows.append({
            "model": name,
            "reasoning_effort": effort,
            "score": cells[at["score"]],
            "pass_rate": cells[at["pass rate"]],
        })
    return document(rows, url=url, page_ref=page_ref, read_date=read_date,
                    note="the rendered leaderboard table; a lowercase effort label glued to "
                         "the model cell as reasoning_effort")


def project_osworld(markdown: str, *, url: str, page_ref: str,
                    read_date: str = READ_DATE) -> bytes:
    """OSWorld 2.0's board, rendered: the model table (all releases)."""
    header, body = _markdown_rows(markdown, "Model")
    at = {normalise_name(h): i for i, h in enumerate(header)}
    rows = [{
        "model": cells[at["model"]],
        "reasoning_effort": cells[at["effort"]],
        "version": cells[at["version"]],
        "binary_reward": cells[at["binary reward"]],
        "partial_reward": cells[at["partial reward"]],
    } for cells in body]
    return document(rows, url=url, page_ref=page_ref, read_date=read_date,
                    note="the rendered model table, release filter All")


# --- boards ------------------------------------------------------------------------------------


@dataclass
class Copy:
    """One retained projection, the source it is registered under and its value key."""

    source_id: str
    url: str
    ref: str
    label: str
    rows: list[dict]
    fraction: bool = False  # the board states a fraction; cards file percent


@dataclass
class Registry:
    store: CopyStore
    sources: dict[str, dict] = field(default_factory=dict)
    copies: dict[str, Copy] = field(default_factory=dict)
    fetched: dict[str, tuple[bytes, str]] = field(default_factory=dict)
    #: Rendered pages (Firecrawl markdown), cached by URL so a rerun spends no credits.
    rendered_cache: Path | None = None

    def fetch(self, url: str) -> tuple[bytes, str]:
        if url not in self.fetched:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=180) as response:  # noqa: S310
                body = response.read()
            self.fetched[url] = (body, self.store.put(body))
        return self.fetched[url]

    def fetch_rendered(self, url: str) -> tuple[str, str]:
        """The page as Firecrawl renders it to markdown (``FIRECRAWL_API_KEY``), retained."""
        cache = self.rendered_cache and self.rendered_cache / (
            hashlib.sha256(url.encode()).hexdigest() + ".md")
        if cache and cache.is_file():
            markdown = cache.read_text(encoding="utf-8")
        else:
            request = urllib.request.Request(
                "https://api.firecrawl.dev/v2/scrape",
                data=json.dumps({"url": url, "formats": ["markdown"], "onlyMainContent": False,
                                 "waitFor": 4000}).encode(),
                headers={"Authorization": f"Bearer {os.environ['FIRECRAWL_API_KEY']}",
                         "Content-Type": "application/json"},
            )
            with urllib.request.urlopen(request, timeout=180) as response:  # noqa: S310
                markdown = json.load(response)["data"]["markdown"]
            if cache:
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_text(markdown, encoding="utf-8")
        return markdown, self.store.put(markdown.encode())

    def add(self, key: str, source_id: str, url: str, body: bytes, label: str,
            *, fraction: bool = False, fetch: str = "http") -> None:
        self.sources.setdefault(source_id, {
            "id": source_id, "url": url, "fetch": fetch, "normaliser": "text-default",
            "cited_regions": [{"id": "rows", "locator": {"kind": "page", "value": ""}}],
        })
        rows = json.loads(body)["rows"]
        self.copies[key] = Copy(source_id, url, self.store.put(body), label, rows, fraction)


SCALE_URL = "https://labs.scale.com/leaderboard/swe_bench_pro_public"
SWEBENCH_URL = "https://www.swebench.com/"
EPOCH_ZIP = "https://epoch.ai/data/benchmark_data.zip"
CURSOR_URL = "https://cursor.com/cursorbench"
MATHARENA_URL = "https://matharena.ai/competition_tables/aime--aime_2026"
METR_URL = "https://metr.org/assets/benchmark_results_1_1.yaml"
MTEB_URL = "https://mteb-leaderboard-backend.hf.space/v1/benchmarks/MTEB(eng,%20v2)/scores"
DEEPSWE_URL = "https://deepswe.datacurve.ai/artifacts/v1.1/leaderboard-live.json"
VENDING_URL = "https://andonlabs.com/evals/vending-bench-2"
FRONTIERCODE_URL = "https://cognition.com/frontiercode"
OSWORLD_URL = "https://osworld-v2.xlang.ai/"

#: Arena benchmark -> (config, category), as MODEL-123's arena_snapshot.json records it.
ARENA = {
    "arena_elo_style_control": ("text_style_control", "overall"),
    "arena_sc_business": ("text_style_control",
                          "industry_business_and_management_and_financial_operations"),
    "arena_sc_coding": ("text_style_control", "coding"),
    "arena_sc_creative_writing": ("text_style_control", "creative_writing"),
    "arena_sc_expert": ("text_style_control", "expert"),
    "arena_sc_hard_prompts": ("text_style_control", "hard_prompts"),
    "arena_sc_instruction_following": ("text_style_control", "instruction_following"),
    "arena_sc_legal": ("text_style_control", "industry_legal_and_government"),
    "arena_sc_longer_query": ("text_style_control", "longer_query"),
    "arena_sc_math": ("text_style_control", "math"),
    "arena_sc_medicine": ("text_style_control", "industry_medicine_and_healthcare"),
    "arena_sc_multi_turn": ("text_style_control", "multi_turn"),
    "arena_sc_non_english": ("text_style_control", "non_english"),
    "arena_sc_science": ("text_style_control",
                         "industry_life_and_physical_and_social_science"),
    "arena_sc_writing": ("text_style_control", "industry_writing_and_literature_and_language"),
    "arena_sc_vision": ("vision_style_control", "overall"),
    "arena_elo_overall": ("text", "overall"),
    "arena_elo_coding": ("text", "coding"),
    "arena_elo_vision": ("vision", "overall"),
}
#: Rows MODEL-143 filed against the wrong Arena config; re-filed even though they carry an ID.
REFILE = {"arena_elo_style_control", "arena_sc_vision"}


def arena_source(config: str) -> str:
    return "model-160-arena-" + config.replace("_", "-")


def build(reg: Registry, tau_urls: set[str]) -> None:
    html, ref = reg.fetch(SCALE_URL)
    reg.add("scale-pro", "model-160-scale-swe-bench-pro-public", SCALE_URL,
            project_scale(html.decode(), url=SCALE_URL, page_ref=ref), "resolve_rate")

    html, ref = reg.fetch(SWEBENCH_URL)
    for board, key in (("Verified", "swebench-verified"),
                       ("Multilingual", "swebench-multilingual")):
        reg.add(key, "model-160-swebench-leaderboard", SWEBENCH_URL,
                project_swebench(html.decode(), board, url=SWEBENCH_URL, page_ref=ref),
                "resolve_rate")

    body, ref = reg.fetch(EPOCH_ZIP)
    with zipfile.ZipFile(io.BytesIO(body)) as archive:
        for name, key, url in (
            ("swe_bench_verified.csv", "epoch-swe-bench-verified",
             "https://epoch.ai/benchmarks/swe-bench-verified"),
            ("simpleqa_verified.csv", "epoch-simpleqa-verified",
             "https://epoch.ai/benchmarks/simpleqa-verified"),
        ):
            text = archive.read(name).decode("utf-8")
            reg.add(key, f"model-160-{key}-csv", url,
                    project_epoch(text, url=url, page_ref=f"{ref} {EPOCH_ZIP}#{name}"),
                    "mean_score", fraction=True)

    for config in sorted({config for config, _ in ARENA.values()}):
        url = ARENA_URL.format(config=config)
        body, ref = reg.fetch(url)
        for benchmark, (cfg, category) in ARENA.items():
            if cfg == config:
                reg.add(f"arena:{benchmark}", arena_source(config), url,
                        project_arena(body, config, category, url=url, page_ref=ref), "rating")

    html, ref = reg.fetch(CURSOR_URL)
    reg.add("cursorbench", "model-160-cursorbench", CURSOR_URL,
            project_cursorbench(html.decode(), url=CURSOR_URL, page_ref=ref), "accuracy")

    body, ref = reg.fetch(MATHARENA_URL)
    reg.add("matharena-aime-2026", "model-160-matharena-aime-2026", MATHARENA_URL,
            project_matharena(body, url=MATHARENA_URL, page_ref=ref), "accuracy")

    body, ref = reg.fetch(METR_URL)
    for horizon in ("p50", "p80"):
        reg.add(f"metr-{horizon}", "model-160-metr-time-horizon-1-1", METR_URL,
                project_metr(body, url=METR_URL, page_ref=ref), f"{horizon}_horizon_length")

    body, ref = reg.fetch(MTEB_URL)
    reg.add("mteb-eng-v2", "model-160-mteb-eng-v2", MTEB_URL,
            project_mteb(body, url=MTEB_URL, page_ref=ref), "reranking", fraction=True)

    body, ref = reg.fetch(DEEPSWE_URL)
    reg.add("deepswe", "model-160-deepswe-v1-1", DEEPSWE_URL,
            project_deepswe(body, url=DEEPSWE_URL, page_ref=ref), "pass_at_1", fraction=True)

    # The board's table is client-side; its data ships in one of the page's JS chunks.
    page, _ = reg.fetch(VENDING_URL)
    for path in sorted(set(re.findall(r"/_app/immutable/[\w./-]+\.js", page.decode()))):
        chunk_url = "https://andonlabs.com" + path
        body, ref = reg.fetch(chunk_url)
        if b"{vb2:{" in body:
            reg.add("vending", "model-160-vending-bench-2", VENDING_URL,
                    project_vending(body.decode(), url=VENDING_URL,
                                    page_ref=f"{ref} {chunk_url}"), "money_balance")
            break

    for key, url, project in (("frontiercode", FRONTIERCODE_URL, project_frontiercode),
                              ("osworld", OSWORLD_URL, project_osworld)):
        markdown, ref = reg.fetch_rendered(url)
        label = {"frontiercode": "score", "osworld": "binary_reward"}[key]
        reg.add(key, f"model-160-{key}", url, project(markdown, url=url, page_ref=ref), label,
                fetch="rendered")

    for url in sorted(tau_urls):
        body, ref = reg.fetch(url)
        slug = re.search(r"/submissions/([^/]+)/", url).group(1)
        reg.add(f"tau:{url}", f"model-160-tau-bench-{slug.replace('_', '-')}", url,
                project_tau(body, url=url, page_ref=ref), "pass_1")


#: Benchmark -> (host the card row must cite, retained copy it is checked against).
BOARDS = {
    "swe_bench_pro": ("labs.scale.com", "scale-pro"),
    "swe_bench_verified": ("epoch.ai", "epoch-swe-bench-verified"),
    "simpleqa_verified": ("epoch.ai", "epoch-simpleqa-verified"),
    "cursorbench_4": ("cursor.com", "cursorbench"),
    "aime_2026": ("matharena.ai", "matharena-aime-2026"),
    "metr_time_horizon_50": ("metr.org", "metr-p50"),
    "metr_time_horizon_80": ("metr.org", "metr-p80"),
    "mteb_v2_reranking": ("mteb-leaderboard-backend", "mteb-eng-v2"),
    "deepswe_v1_1": ("deepswe.datacurve.ai", "deepswe"),
    "vending_bench_2": ("andonlabs.com", "vending"),
    "frontiercode_v1_1": ("cognition.com", "frontiercode"),
    "osworld_2": ("osworld-v2.xlang.ai", "osworld"),
}


def copy_for(row: Mapping[str, Any]) -> str | None:
    """The retained copy a card row is checked against, or ``None`` for no deterministic board."""
    benchmark, url = row["benchmark_id"], str(row.get("source_url") or "")
    if benchmark in ARENA and "lmarena-ai/leaderboard-dataset" in url:
        return f"arena:{benchmark}"
    if benchmark == "tau3_banking" and "sierra-tau-bench-public" in url:
        return f"tau:{url}"
    host, key = BOARDS.get(benchmark, (None, None))
    return key if host and host in url else None


#: Board-dated boards carry a date per row; the rest are dated by the day they were read.
OBSERVED = {"cursorbench", "matharena-aime-2026", "mteb-eng-v2", "deepswe", "vending",
            "frontiercode", "osworld"}


# --- matching ----------------------------------------------------------------------------------


def _subject(row: Mapping[str, Any]) -> str | None:
    normal = {normalise_name(str(k)): v for k, v in row.items()}
    return next((str(normal[k]) for k in StructuredDataExtractor._SUBJECTS if normal.get(k)),
                None)


def _effort(row: Mapping[str, Any]) -> str | None:
    subject = _subject(row) or ""
    effort = row.get("reasoning_effort")
    if effort is None:
        m = re.search(r"(?:[_\s\(\[])(minimal|low|medium|high|xhigh|max)(?:\)|\]|$)",
                      subject, re.IGNORECASE)
        effort = m.group(1) if m else None
    return str(effort).casefold() if effort else None


def board_row(copy: Copy, name: str, effort: str | None = None,
              day: str | None = None) -> dict | None:
    """The one board row published under ``name``: exact name first, then identity + effort.

    Boards that drop the "Claude" of Anthropic's names ("Fable 5.1") are tried without it.
    """
    for alias in dict.fromkeys((name, re.sub(r"^Claude[ -]", "", name))):
        exact = [r for r in copy.rows
                 if normalise_name(_subject(r) or "") == normalise_name(alias)]
        identity, named_effort = split_model_cell(alias)
        wanted = effort or named_effort
        loose = [r for r in copy.rows
                 if split_model_cell(_subject(r) or "")[0] == identity
                 and (wanted is None or _effort(r) in (None, wanted))]
        for candidates in (exact, loose):
            if day is not None and len(candidates) > 1:
                candidates = [r for r in candidates if str(r.get("date")) == day] or candidates
            if len(candidates) == 1:
                return candidates[0]
    return None


def board_value(copy: Copy, row: Mapping[str, Any], unit: str | None) -> float:
    value = row[copy.label]
    number = parse_quantity(str(value)).number if isinstance(value, str) else value
    return round(number * 100, 10) if copy.fraction and unit == "percent" else number


def agrees(card: Any, copy: Copy, row: Mapping[str, Any], unit: str | None) -> bool:
    """The card's value is the board's, to the precision either states.

    A card value more precise than the board it cites (copied from a secondary copy of
    the board) does not agree: the primary source does not state those digits.
    """
    quantity = parse_quantity(str(row[copy.label]), "fraction" if copy.fraction else None)
    if not isinstance(card, (int, float)) or quantity is None:
        return False
    written = isinstance(row[copy.label], str)  # as the page writes it, not a JSON number
    if written and not copy.fraction and _places(card) > quantity.decimals:
        return False
    return numbers_agree(card, unit if quantity.unit else None, quantity)


def _places(value: int | float) -> int:
    return 0 if isinstance(value, int) else len(repr(value).partition(".")[2])


# --- collectors --------------------------------------------------------------------------------

_TRAILER = re.compile(r"Co-Authored-By:\s*([^<\n]+?)\s*<([^>]+)>", re.I)
_FAMILY = {"anthropic.com": "anthropic", "x.ai": "xai", "openai.com": "openai"}


def _commit_collector(sha: str, cache: dict[str, VerificationActor]) -> VerificationActor:
    if set(sha) == {"0"}:  # not committed yet: a row this script added
        return ME
    if sha not in cache:
        body = subprocess.run(["git", "show", "-s", "--format=%B", sha], cwd=ROOT,
                              capture_output=True, text=True, check=True).stdout
        agents = {}
        for name, email in _TRAILER.findall(body):
            domain = email.rsplit("@", 1)[-1].replace("noreply.", "")
            if domain in _FAMILY:
                agents[re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-")] = _FAMILY[domain]
        method = f"card-row@{sha[:8]}"
        if len(set(agents.values())) == 1:
            (agent, family), = sorted(agents.items())[:1]
            cache[sha] = VerificationActor(agent=agent, model_family=family, method=method)
        else:  # no AI trailer, or co-authors from more than one family
            cache[sha] = VerificationActor(agent="unknown", model_family="unknown", method=method)
    return cache[sha]


def row_collectors(path: Path, cache: dict[str, VerificationActor]) -> list[VerificationActor]:
    """The collector of each evidence row on a card, in order, from ``git blame``."""
    blame = subprocess.run(["git", "blame", "--line-porcelain", str(path)], cwd=ROOT,
                           capture_output=True, text=True, check=True).stdout
    out, sha = [], None
    for line in blame.splitlines():
        if re.match(r"^[0-9a-f]{40} ", line):
            sha = line.split()[0]
        elif line.startswith("\t  - benchmark_id:"):
            out.append(_commit_collector(sha, cache))
    return out


# --- additions ---------------------------------------------------------------------------------

#: Premier LLMs with a published result on a coding board and no row for it on the card.
#: (model, benchmark, copy, name on the board, benchmark_version, configuration, limitations)
ADDITIONS = [
    ("google/gemini-3-1-pro-preview", "swe_bench_pro", "scale-pro", "gemini-3.1-pro (thinking)*",
     "SWE-Bench Pro, public dataset, Scale Labs leaderboard",
     "Scale Labs leaderboard entry read 2026-09-25; entry created {date}; effort thinking "
     "(the board names no level); ±{ci95} (95% CI). Harness: mini-swe-agent (the board marks "
     "mini-swe-agent runs with an asterisk).",
     "Public split only. The same page's private-split row is a different number."),
    ("anthropic/claude-opus-4-6", "swe_bench_verified", "swebench-verified", "Claude 4.6 Opus",
     "SWE-bench Verified, bash-only (mini-SWE-agent), official leaderboard",
     "Official SWE-bench leaderboard (swebench.com, the page's leaderboard-data JSON), "
     "Verified board, read 2026-09-25. Agent mini-SWE-agent; submission dated {date}; "
     "no reasoning effort stated.",
     "Bash-only comparison: one agent scaffold for every model."),
    ("anthropic/claude-opus-4-6", "swe_bench_multilingual", "swebench-multilingual",
     "Claude 4.6 Opus",
     "SWE-bench Multilingual, bash-only (mini-SWE-agent), official leaderboard",
     "Official SWE-bench leaderboard (swebench.com, the page's leaderboard-data JSON), "
     "Multilingual board, read 2026-09-25. Agent mini-SWE-agent; submission dated {date}; "
     "no reasoning effort stated.",
     "Bash-only comparison: one agent scaffold for every model."),
]
#: CursorBench names for premier models that the board lists and the card lacks.
CURSOR_ADDITIONS = {"meta/muse-spark-1-3": "Muse Spark 1.3"}


def cursor_additions(copy: Copy) -> list[tuple]:
    out = []
    for model, name in CURSOR_ADDITIONS.items():
        rows = [r for r in copy.rows if r["model"] == name]
        if not rows:
            continue
        top = min(rows, key=lambda r: list(_EFFORTS.values()).index(r["reasoning_effort"])
                  if r.get("reasoning_effort") else 99)
        effort = top.get("reasoning_effort")
        label = f"{name} ({effort})" if effort else name
        out.append((model, "cursorbench_4", "cursorbench", label, "CursorBench 4.0",
                    "Cursor's CursorBench 4.0 board read 2026-09-25; the board states no row "
                    f"date, so the reading is dated by the observation. Highest-effort row "
                    f"({effort}); ${top['usd_per_task']:.2f} a task.",
                    "Runs only in Cursor's production agent harness."))
    return out


def new_row_block(row: dict) -> str:
    lines = [f"  - benchmark_id: {row['benchmark_id']}"]
    for key, value in row.items():
        if key == "benchmark_id":
            continue
        dumped = yaml.safe_dump({key: value}, sort_keys=False, allow_unicode=True,
                                width=88).rstrip()
        lines.extend(f"    {line}" for line in dumped.splitlines())
    return "\n".join(lines) + "\n"


#: What filing a row may change. MODEL-143's ``replace_evidence`` does not rewrite ``unit``.
FILED_FIELDS = ("model_id_as_evaluated", "score", "unit", "evidence_date", "id", "measured_by",
                "effort", "harness", "sources")


def rewrite_rows(path: Path, text: str, updates: list[tuple[tuple, dict]]) -> None:
    """Rewrite the filed fields of the card's evidence rows keyed by ``evidence_key``."""
    wanted = dict(updates)

    def update(match: re.Match[str]) -> str:
        block = match.group(0).rstrip("\n")
        row = wanted.pop(evidence_key(yaml.safe_load("evidence:\n" + block)["evidence"][0]), None)
        if row is None:
            return match.group(0)
        lines = block.splitlines()
        for name in FILED_FIELDS:
            lines = _set_field(lines, name, row.get(name))
        return "\n".join(lines) + "\n"

    text = re.sub(
        r"(?ms)^  - benchmark_id:.*?(?=^  - benchmark_id:|^  [a-z][a-z0-9_]*:|^[a-z][a-z0-9_]*:)",
        update, text)
    if wanted:
        raise SystemExit(f"{path}: could not locate {len(wanted)} evidence rows")
    path.write_text(text, encoding="utf-8")


def append_rows(path: Path, blocks: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    start = text.index("\n  evidence:\n")
    end = re.compile(r"^(?:  [a-z]|[a-z])", re.M).search(text, start + len("\n  evidence:\n"))
    path.write_text(text[:end.start()] + "".join(blocks) + text[end.start():], encoding="utf-8")


# --- filing ------------------------------------------------------------------------------------


@dataclass
class Outcome:
    filed: list[tuple] = field(default_factory=list)
    score_changes: list[tuple] = field(default_factory=list)
    other_changes: list[tuple] = field(default_factory=list)
    unmatched: list[tuple] = field(default_factory=list)
    prose: list[tuple] = field(default_factory=list)


MEASURED_BY = {"benchmark_author": "benchmark_author",
               "independent_evaluator": "independent_evaluator",
               "provider_self_report": "provider_self_report"}


def fill(row: dict, copy: Copy, key: str, match: dict) -> None:
    """Set the row's qualifiers from the board row it was matched to."""
    name, subject = row.get("model_id_as_evaluated"), _subject(match)
    if not name or split_model_cell(name)[0] != split_model_cell(subject)[0]:
        row["model_id_as_evaluated"] = subject  # the name the cited board publishes
    if key in OBSERVED:
        row["evidence_date"] = READ_DATE
    elif match.get("date") or match.get("leaderboard_publish_date"):
        row["evidence_date"] = str(match.get("date") or match["leaderboard_publish_date"])
    row["effort"] = _effort(match)
    row["harness"] = "unregistered" if match.get("agent") else None
    row["measured_by"] = MEASURED_BY[row["source_kind"]]
    row["sources"] = [SourceRef(source_id=copy.source_id, snapshot_ref=copy.ref,
                                cited_regions=["rows"]).model_dump(mode="json")]


def claim_for(model_id: str, front: Mapping, row: dict, copy: Copy,
              collector: VerificationActor, key: str) -> Claim:
    names = tuple(dict.fromkeys(filter(None, (
        row["model_id_as_evaluated"], front.get("display_name"), front.get("version"),
        model_id.rsplit("/", 1)[-1],
    ))))
    return Claim(
        target=TargetRef(kind="evidence", id=row["id"]),
        subject=model_id,
        names=names,
        field=row["benchmark_id"],
        label=copy.label,
        value=row["score"],
        unit=row.get("unit"),
        conditions={"effort": row.get("effort"), "harness": row.get("harness"),
                    "date": None if key.startswith("metr") else row.get("evidence_date")},
        collector=collector,
        sources=(SourceRef(**row["sources"][0]),),
    )


def run(dry_run: bool, rendered_cache: Path | None = None) -> Outcome:
    premier = [m["model_id"] for m in
               yaml.safe_load((ROOT / "premier" / "slice-1.yaml").read_text())["models"]]
    cards: dict[str, Path] = {}
    for path in sorted((ROOT / "models").glob("*/*.md")):
        head = path.read_text(encoding="utf-8").split("---", 2)[1]
        if (mid := yaml.safe_load(head).get("model_id")) in premier:
            cards[mid] = path

    tau_urls = set()
    for path in cards.values():
        front = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
        for row in (front.get("benchmarks") or {}).get("evidence") or []:
            if row["benchmark_id"] == "tau3_banking" and not row.get("id"):
                tau_urls.add(row["source_url"])

    reg = Registry(CopyStore(), rendered_cache=rendered_cache)
    build(reg, tau_urls)
    if not dry_run:
        register(reg.sources)

    queue = Queue(ROOT / "verification")
    filed_at = datetime.now(UTC)
    blame_cache: dict[str, VerificationActor] = {}
    result = Outcome()
    additions = ADDITIONS + cursor_additions(reg.copies["cursorbench"])

    for model_id in premier:
        path = cards[model_id]
        text = path.read_text(encoding="utf-8")
        front = yaml.safe_load(text.split("---", 2)[1])
        rows = (front.get("benchmarks") or {}).get("evidence") or []
        collectors = row_collectors(path, blame_cache)
        updates, claims = [], []
        for row, collector in zip(rows, collectors, strict=True):
            refile = row["benchmark_id"] in REFILE
            if row.get("id") and not refile:
                continue
            key = copy_for(row)
            if key is None:
                why = ("prose: needs an LLM reader of another family"
                       if row.get("source_kind") == "provider_self_report"
                       else "board renders client-side; no machine-readable copy")
                result.prose.append((model_id, row["benchmark_id"], row.get("source_url"),
                                     row.get("model_id_as_evaluated"), row.get("score"),
                                     f"{collector.agent} ({collector.model_family})", why))
                continue
            copy = reg.copies[key]
            original = evidence_key(row)
            old = dict(row)
            match = board_row(copy, str(row.get("model_id_as_evaluated") or ""),
                              row.get("effort"), str(row.get("evidence_date") or "") or None)
            if match is None or match.get(copy.label) is None:
                result.unmatched.append((model_id, row["benchmark_id"],
                                         row.get("model_id_as_evaluated"), row.get("score"),
                                         copy.source_id))
                continue
            if not agrees(row["score"], copy, match, row.get("unit")):
                new = board_value(copy, match, row.get("unit"))
                if key.startswith("arena:"):
                    new = round(new, 2)
                result.score_changes.append((path.relative_to(ROOT).as_posix(),
                                             row["benchmark_id"], row["score"], new,
                                             copy.url))
                row["score"] = new
                collector = ME
            if row.get("unit") == "elo":
                row["unit"] = "Arena score (Elo scale)"
            fill(row, copy, key, match)
            for field_name in ("model_id_as_evaluated", "evidence_date", "unit"):
                if old.get(field_name) != row.get(field_name):
                    result.other_changes.append((path.relative_to(ROOT).as_posix(),
                                                 row["benchmark_id"], field_name,
                                                 old.get(field_name), row.get(field_name)))
            row["id"] = evidence_id(model_id, row)
            updates.append((original, dict(row)))
            claims.append(claim_for(model_id, front, row, copy, collector, key))

        blocks = []
        for model, benchmark, key, name, version, configuration, limitations in additions:
            copy = reg.copies[key]
            if model != model_id or any(r["benchmark_id"] == benchmark
                                        and r.get("source_url") == copy.url for r in rows):
                continue
            match = board_row(copy, name)
            if match is None:
                result.unmatched.append((model_id, benchmark, name, None, copy.source_id))
                continue
            kind = "benchmark_author"
            if key == "scale-pro":
                kind = "independent_evaluator"
            new = {
                "benchmark_id": benchmark,
                "model_id_as_evaluated": _subject(match),
                "score": board_value(copy, match, "percent"),
                "unit": "percent",
                "source_url": copy.url,
                "source_kind": kind,
                "evidence_date": None,
                "date_type": "evaluated",
                "verified_at": READ_DATE,
                "benchmark_version": version,
                "configuration": configuration.format(**{k: v for k, v in match.items()}),
                "limitations": limitations,
            }
            fill(new, copy, key, match)
            new["id"] = evidence_id(model_id, new)
            claims.append(claim_for(model_id, front, new, copy, ME, key))
            blocks.append(new_row_block(new))
            result.score_changes.append((path.relative_to(ROOT).as_posix(), benchmark, None,
                                         new["score"], copy.url))

        for claim in claims:
            result.filed.append((model_id, claim.field, claim.value, claim.collector.agent,
                                 claim.sources[0].source_id))
        if dry_run:
            continue
        if updates:
            rewrite_rows(path, text, updates)
        if blocks:
            append_rows(path, blocks)
        for claim in claims:
            queue.file(claim, at=filed_at)
    return result


def register(sources: dict[str, dict]) -> None:
    path = ROOT / "registry" / "sources.yaml"
    text = path.read_text(encoding="utf-8")
    known = load_sources(path)
    new = [s for key, s in sorted(sources.items()) if key not in known]
    if not new:
        return
    block = yaml.safe_dump(new, sort_keys=False, allow_unicode=True, width=100)
    path.write_text(
        text.rstrip("\n") + "\n# MODEL-160: board projections (JSON rows) of machine-readable "
        "boards; read 2026-09-25.\n" + block, encoding="utf-8")
    load_sources(path)


def report(result: Outcome) -> str:
    def table(header: tuple[str, ...], rows: list[tuple]) -> str:
        out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
        out += ["| " + " | ".join("" if v is None else str(v) for v in row) + " |"
                for row in rows]
        return "\n".join(out)

    return "\n\n".join([
        f"filed {len(result.filed)} claims",
        "## Score changes\n" + table(("card", "benchmark", "old", "new", "source"),
                                     result.score_changes),
        "## Other field changes\n" + table(("card", "benchmark", "field", "old", "new"),
                                           result.other_changes),
        "## No board row\n" + table(("model", "benchmark", "name", "score", "source"),
                                    result.unmatched),
        "## Not filed\n" + table(
            ("model", "benchmark", "source", "name", "score", "collector", "why"),
            result.prose),
    ])


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--dry-run", action="store_true",
                        help="Fetch and match, write nothing, print the report.")
    parser.add_argument("--report", type=Path, help="Also write the report here.")
    parser.add_argument("--rendered-cache", type=Path,
                        default=Path.home() / ".cache" / "modelspec" / "rendered",
                        help="Firecrawl renders by URL; a cached page is not fetched again.")
    args = parser.parse_args(argv)
    text = report(run(args.dry_run, args.rendered_cache))
    print(text)
    if args.report:
        args.report.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
