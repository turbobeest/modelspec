"""Answer-engine visibility runs (MODEL-256): monthly, on low-cost models, for now.

    python -m scripts.aeo.visibility run --inventory PROMPTS --config ENGINES --out RUNS_DIR
    python -m scripts.aeo.visibility report RUN_DIR [--baseline BASELINE_DIR]

``run`` sends every prompt in the inventory (MODEL-254) to every engine in the
private config, stores each answer verbatim with what it cited and searched,
and writes ``report.md`` and ``summary.json`` beside the runs. ``--dry-run``
prints the plan and the cost estimate and calls nothing.

**Where it runs.** The operator's machine. Never this repository's CI: the
repository and its Actions logs are public, and the inventory, the answers and
the report are not. The config, the inventory and the output all live in the
private business repository.

**Money.** The config sets a monthly cap. Before each engine starts, the run
adds the month's recorded spend to that engine's estimate and refuses the engine
if the sum would cross the cap; after every call it stops once the cap is
reached. Spend is what the engine reported where it reports cost (Perplexity),
otherwise tokens and searches priced from the config.

**What the numbers are.** ``surface=api``, labelled on every row. Detection is
heuristic and says so: a mention of OpenAI's Model Spec, the CNCF ModelPack or
the PyPI package is never counted as ModelSpec. Accuracy of the description is
left for a human or a judge to mark (``accurate: null``).
"""

from __future__ import annotations

import argparse
import json
import re
import time
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Mapping
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import httpx
import yaml

from scripts.aeo import engines, inventory
from scripts.aeo.engines import Answer, EngineUnavailable

SURFACE = "api"

# ── detection ────────────────────────────────────────────────────────────────

_OURS_DOMAIN = "modelspec.dev"
_ONE_WORD = re.compile(r"\bmodelspec\b(?!\.dev)", re.I)
_SELECTION = re.compile(r"select|choos|decid|benchmark|alternatives|rank|downselect|which model", re.I)
_OTHER_ENTITIES = {
    "openai-model-spec": re.compile(r"openai[^.\n]{0,80}\bmodel[ -]?spec\b|\bmodel[ -]?spec\b[^.\n]{0,80}openai|model-spec\.openai\.com", re.I),
    "pypi-modelspec": re.compile(r"neuroml|pypi\.org/project/modelspec|pip install modelspec", re.I),
    "cncf-modelpack": re.compile(r"modelpack", re.I),
}
_RECOMMEND = re.compile(r"recommend|\buse\b|\btry\b|consider|check out|tool such as|tools like", re.I)


@dataclass(frozen=True)
class Detection:
    mentioned: bool
    cited: bool
    cited_top3: bool
    recommended: bool
    disambiguated: bool
    confused_with: tuple[str, ...]
    accurate: bool | None = None  # judged later, never guessed here


def _sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]


def detect(text: str, citation_domains: list[str]) -> Detection:
    """Heuristic: is this answer about modelspec.dev, and in what role?"""
    cited_positions = [i for i, d in enumerate(citation_domains) if d == _OURS_DOMAIN or d.endswith("." + _OURS_DOMAIN)]
    cited = bool(cited_positions)
    named_by_domain = _OURS_DOMAIN in text.lower()
    named_by_word = any(_SELECTION.search(s) for s in _sentences(text) if _ONE_WORD.search(s))
    confused = tuple(name for name, pattern in _OTHER_ENTITIES.items() if pattern.search(text))
    mentioned = named_by_domain or cited or (named_by_word and "pypi-modelspec" not in confused)
    recommended = mentioned and any(
        (_OURS_DOMAIN in s.lower() or _ONE_WORD.search(s)) and _RECOMMEND.search(s) for s in _sentences(text))
    return Detection(mentioned=mentioned, cited=cited, cited_top3=any(p < 3 for p in cited_positions),
                     recommended=recommended, disambiguated=mentioned, confused_with=confused)


def succeeded(goal: str, d: Detection) -> bool:
    return {"cited": d.cited, "mentioned": d.mentioned, "recommended": d.recommended,
            "disambiguated": d.disambiguated}[goal]


# ── config and money ─────────────────────────────────────────────────────────

@dataclass(frozen=True)
class EngineConfig:
    name: str
    model: str
    key: str  # an op:// reference, never a key
    price_in: float  # USD per million input tokens
    price_out: float  # USD per million output tokens
    search_fee: float  # USD per search
    est_call_usd: float  # budget estimate per call, before any are made


@dataclass(frozen=True)
class Config:
    monthly_cap_usd: float
    max_output_tokens: int
    engines: tuple[EngineConfig, ...]


def load_config(path: Path) -> Config:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    rows = tuple(EngineConfig(name=name, **spec) for name, spec in raw["engines"].items())
    unknown = [e.name for e in rows if e.name not in engines.CALLS]
    if unknown:
        raise ValueError(f"unknown engines in {path}: {unknown}")
    if any(not e.key.startswith("op://") for e in rows):
        raise ValueError("engine keys must be op:// references; a literal key never goes in the config")
    return Config(monthly_cap_usd=float(raw["monthly_cap_usd"]),
                  max_output_tokens=int(raw.get("max_output_tokens", 2000)), engines=rows)


def call_cost(engine: EngineConfig, answer: Answer) -> float:
    if answer.reported_cost_usd is not None:
        return float(answer.reported_cost_usd)
    return (answer.input_tokens * engine.price_in + answer.output_tokens * engine.price_out) / 1e6 \
        + answer.searches * engine.search_fee


def month_spend(runs_root: Path, month: str) -> float:
    total = 0.0
    for path in Path(runs_root).glob("*/runs.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row.get("collected_at", "").startswith(month):
                total += row.get("cost_usd", 0.0)
    return total


# ── running ──────────────────────────────────────────────────────────────────

Caller = Callable[[str, str, str, int], Answer]


def _with_retries(call: Caller, *args: Any, attempts: int = 3) -> Answer:
    for attempt in range(attempts):
        try:
            return call(*args)
        except (httpx.TransportError, httpx.HTTPStatusError) as exc:
            status = getattr(getattr(exc, "response", None), "status_code", 0)
            if attempt == attempts - 1 or (status and status < 500):
                raise
            time.sleep(5 * (attempt + 1))
    raise AssertionError("unreachable")


@dataclass
class Budget:
    cap: float
    spent: float

    def allows(self, more: float) -> bool:
        return self.spent + more <= self.cap


def run_engine(engine: EngineConfig, prompts: list[Mapping[str, Any]], *, out: Path, budget: Budget,
               max_output_tokens: int, call: Caller, key: Callable[[str], str],
               now: Callable[[], datetime]) -> dict[str, Any]:
    """Every prompt on one engine. Returns what happened, for the run log."""
    estimate = engine.est_call_usd * len(prompts)
    if not budget.allows(estimate):
        return {"engine": engine.name, "status": "skipped",
                "reason": f"budget: ${budget.spent:.2f} spent + ${estimate:.2f} estimate > ${budget.cap:.2f} cap"}
    try:
        secret = key(engine.key)
    except EngineUnavailable as exc:
        return {"engine": engine.name, "status": "skipped", "reason": str(exc)}
    done, rows = 0, []
    raw_dir = out / "raw" / engine.name
    raw_dir.mkdir(parents=True, exist_ok=True)
    for prompt in prompts:
        if budget.spent >= budget.cap:
            return {"engine": engine.name, "status": "stopped", "reason": "monthly cap reached", "runs": done,
                    "rows": rows}
        try:
            answer = _with_retries(call, engine.model, secret, prompt["text"], max_output_tokens)
        except EngineUnavailable as exc:
            return {"engine": engine.name, "status": "unavailable", "reason": str(exc), "runs": done, "rows": rows}
        except httpx.HTTPError as exc:
            rows.append(_failed_row(engine, prompt, now(), f"{type(exc).__name__}: {exc}"[:300]))
            continue
        cost = call_cost(engine, answer)
        budget.spent += cost
        (raw_dir / f"{prompt['id']}.json").write_text(json.dumps(answer.raw, indent=1), encoding="utf-8")
        rows.append(_row(engine, prompt, answer, cost, now()))
        done += 1
    return {"engine": engine.name, "status": "complete", "runs": done, "rows": rows}


def _row(engine: EngineConfig, prompt: Mapping[str, Any], answer: Answer, cost: float,
         at: datetime) -> dict[str, Any]:
    detection = detect(answer.text, [c.domain for c in answer.citations])
    return {
        "prompt_id": prompt["id"], "cluster": prompt["cluster"], "success_goal": prompt["success"],
        "engine": engine.name, "surface": SURFACE, "model_version": answer.model_version or engine.model,
        "collected_at": at.isoformat(), "answer_text": answer.text,
        "citations": [asdict(c) for c in answer.citations], "fanout_queries": answer.fanout_queries,
        "searched": answer.searched,
        "usage": {"input_tokens": answer.input_tokens, "output_tokens": answer.output_tokens,
                  "searches": answer.searches},
        "cost_usd": round(cost, 6), "detection": asdict(detection),
        "success": succeeded(prompt["success"], detection), "raw_blob_ref": f"raw/{engine.name}/{prompt['id']}.json",
    }


def _failed_row(engine: EngineConfig, prompt: Mapping[str, Any], at: datetime, error: str) -> dict[str, Any]:
    return {"prompt_id": prompt["id"], "cluster": prompt["cluster"], "success_goal": prompt["success"],
            "engine": engine.name, "surface": SURFACE, "model_version": engine.model,
            "collected_at": at.isoformat(), "error": error, "cost_usd": 0.0}


def run(prompts: list[Mapping[str, Any]], config: Config, *, runs_root: Path, today: date,
        calls: Mapping[str, Caller] = engines.CALLS, key: Callable[[str], str] = engines.op_read,
        now: Callable[[], datetime] = lambda: datetime.now(UTC)) -> Path:
    out = Path(runs_root) / today.isoformat()
    out.mkdir(parents=True, exist_ok=True)
    budget = Budget(cap=config.monthly_cap_usd, spent=month_spend(runs_root, today.strftime("%Y-%m")))
    # Engines run side by side; the budget is checked between calls, so the cap
    # can be overshot by at most one call per engine in flight.
    with ThreadPoolExecutor(max_workers=len(config.engines)) as pool:
        results = list(pool.map(lambda e: run_engine(
            e, prompts, out=out, budget=budget, max_output_tokens=config.max_output_tokens,
            call=calls[e.name], key=key, now=now), config.engines))
    with (out / "runs.jsonl").open("a", encoding="utf-8") as handle:
        for result in results:
            for row in result.pop("rows", []):
                handle.write(json.dumps(row) + "\n")
    (out / "engines.json").write_text(json.dumps(
        {"surface": SURFACE, "cap_usd": budget.cap, "month_spend_usd": round(budget.spent, 4),
         "engines": results}, indent=1), encoding="utf-8")
    return out


# ── scoring and the report ───────────────────────────────────────────────────

def _rate(rows: list[Mapping[str, Any]], key: Callable[[Mapping[str, Any]], bool]) -> float | None:
    return round(sum(1 for r in rows if key(r)) / len(rows), 3) if rows else None


def summarise(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    rows = list(rows)
    answered = [r for r in rows if "detection" in r]
    cells: dict[str, dict[str, Any]] = {}
    grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for r in answered:
        grouped[(r["cluster"], r["engine"])].append(r)
    for (cluster, engine), group in sorted(grouped.items()):
        cell = {
            "n": len(group),
            "success": _rate(group, lambda r: r["success"]),
            "mentioned": _rate(group, lambda r: r["detection"]["mentioned"]),
            "cited": _rate(group, lambda r: r["detection"]["cited"]),
            "recommended": _rate(group, lambda r: r["detection"]["recommended"]),
            "searched": _rate(group, lambda r: r["searched"]),
        }
        if cluster == "constrained":
            cell["cited_top3"] = _rate(group, lambda r: r["detection"]["cited_top3"])
        if cluster == "disambiguation":
            cell["disambiguation_failure"] = _rate(group, lambda r: not r["detection"]["disambiguated"])
        cells[f"{cluster}/{engine}"] = cell
    domains: dict[str, list[tuple[str, int]]] = {}
    for cluster in sorted({r["cluster"] for r in answered}):
        counter = Counter(c["domain"] for r in answered if r["cluster"] == cluster for c in r["citations"])
        domains[cluster] = counter.most_common(20)
    confused = Counter(name for r in answered for name in r["detection"]["confused_with"])
    return {"surface": SURFACE, "answers": len(answered),
            "errors": sum(1 for r in rows if "error" in r),
            "cost_usd": round(sum(r.get("cost_usd", 0.0) for r in answered), 4),
            "cells": cells, "top_cited_domains": domains, "confused_with": dict(confused)}


def _fmt(value: float | None) -> str:
    return "–" if value is None else f"{value:.0%}"


def render(summary: Mapping[str, Any], *, run_date: str, engines_log: Mapping[str, Any],
           baseline: Mapping[str, Any] | None = None) -> str:
    lines = [f"# Answer-engine visibility, {run_date}", "",
             "**Surface: API** (each engine's own web-search API). These are not the consumer apps "
             "buyers see; read them as a trend, not as what a buyer saw. Detection is heuristic, and "
             "description accuracy is not judged yet.", "",
             f"Answers: {summary['answers']}. Cost: ${summary['cost_usd']:.2f} "
             f"(month to date ${engines_log.get('month_spend_usd', 0):.2f} of ${engines_log.get('cap_usd', 0):.2f}).", ""]
    for e in engines_log.get("engines", []):
        if e["status"] != "complete":
            lines.append(f"- **{e['engine']}: {e['status']}**: {e.get('reason', '')}")
    lines += ["", "| Cluster / engine | n | Goal met | Mentioned | Cited | Recommended | Searched | Extra |",
              "|---|---|---|---|---|---|---|---|"]
    for key, cell in summary["cells"].items():
        extra = ""
        if "cited_top3" in cell:
            extra = f"top-3 cited {_fmt(cell['cited_top3'])}"
        if "disambiguation_failure" in cell:
            extra = f"disambiguation failure {_fmt(cell['disambiguation_failure'])}"
        delta = ""
        if baseline and key in baseline.get("cells", {}) and cell["success"] is not None:
            before = baseline["cells"][key]["success"]
            if before is not None:
                delta = f" ({(cell['success'] - before) * 100:+.0f} pts)"
        lines.append(f"| {key} | {cell['n']} | {_fmt(cell['success'])}{delta} | {_fmt(cell['mentioned'])} | "
                     f"{_fmt(cell['cited'])} | {_fmt(cell['recommended'])} | {_fmt(cell['searched'])} | {extra} |")
    if summary["confused_with"]:
        lines += ["", "Answers that named a different entity: " +
                  ", ".join(f"{k} {v}" for k, v in sorted(summary["confused_with"].items()))]
    lines += ["", "## Most-cited domains by cluster", ""]
    for cluster, pairs in summary["top_cited_domains"].items():
        lines.append(f"- **{cluster}:** " + ", ".join(f"{d} ({n})" for d, n in pairs))
    return "\n".join(lines) + "\n"


def write_report(run_dir: Path, baseline_dir: Path | None = None) -> str:
    rows = [json.loads(line) for line in (run_dir / "runs.jsonl").read_text(encoding="utf-8").splitlines()]
    summary = summarise(rows)
    baseline = json.loads((baseline_dir / "summary.json").read_text(encoding="utf-8")) if baseline_dir else None
    engines_log = json.loads((run_dir / "engines.json").read_text(encoding="utf-8"))
    text = render(summary, run_date=run_dir.name, engines_log=engines_log, baseline=baseline)
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    (run_dir / "report.md").write_text(text, encoding="utf-8")
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m scripts.aeo.visibility")
    sub = parser.add_subparsers(dest="command", required=True)
    go = sub.add_parser("run")
    go.add_argument("--inventory", type=Path, required=True)
    go.add_argument("--config", type=Path, required=True)
    go.add_argument("--out", type=Path, required=True, help="the runs directory; a dated subdirectory is made")
    go.add_argument("--baseline", type=Path)
    go.add_argument("--dry-run", action="store_true")
    rep = sub.add_parser("report")
    rep.add_argument("run_dir", type=Path)
    rep.add_argument("--baseline", type=Path)
    args = parser.parse_args(argv)

    if args.command == "report":
        print(write_report(args.run_dir, args.baseline))
        return 0
    prompts = inventory.load(args.inventory)
    config = load_config(args.config)
    today = date.today()
    spent = month_spend(args.out, today.strftime("%Y-%m"))
    estimate = sum(e.est_call_usd for e in config.engines) * len(prompts)
    print(f"{len(prompts)} prompts x {len(config.engines)} engines; estimate ${estimate:.2f}; "
          f"month to date ${spent:.2f} of ${config.monthly_cap_usd:.2f}")
    if args.dry_run:
        return 0
    out = run(prompts, config, runs_root=args.out, today=today)
    print(write_report(out, args.baseline))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
