"""Native web-search subscription adapters; Perplexity keeps its existing API."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

from qa import tui_harness
from qa.providers import redact_structure
from qa.subscription_jobs import preview, require_ready
from qa.tui_providers import CLIS, SEARCH_TOOLS
from scripts.aeo import engines, inventory, visibility

ENGINE_CLIS = {"openai": "codex", "anthropic": "claude", "gemini": "gemini", "xai": "grok"}


def engine_config(path: Path, config: dict, *, dry_run=False):
    raw = yaml.safe_load(path.read_text())
    if set(raw["engines"]) != set(ENGINE_CLIS) | {"perplexity"}:
        raise ValueError("Configure the four subscription engines and Perplexity")
    for name, cli in ENGINE_CLIS.items():
        row = raw["engines"][name]
        if not dry_run and (row.get("transport") != "subscription" or row.get("cli") != cli or "key" in row):
            raise ValueError(f"{name}: requires subscription transport and no API key reference")
        if not dry_run and row["model"] != config["clis"][cli]["model"]:
            raise ValueError(f"{name}: model must match the doctor-certified CLI profile")
    perplexity = visibility.EngineConfig(name="perplexity", **raw["engines"]["perplexity"])
    if not perplexity.key.startswith("op://"):
        raise ValueError("Perplexity requires its existing 1Password reference")
    return raw, perplexity


def answer_from_execution(cli, execution):
    parsed = execution.transcript
    calls = [c for c in parsed.other_tool_calls if c["name"] in SEARCH_TOOLS[cli]]
    searches = [c for c in calls if c["name"] not in {"WebFetch", "web_fetch"}
                and c.get("result_observed") is True and not c.get("result", {}).get("isError")]
    if not searches:
        raise ValueError("CLI did not provide native web-search evidence")
    queries = [str(c["arguments"].get("query", c["arguments"].get("search_query", "")))
               for c in searches if isinstance(c["arguments"], dict)]
    # Native Markdown citations retain direct URLs; no second paid extraction call.
    urls = re.findall(r"https?://[^\s<>\]\)\"]+", parsed.final_answer)
    return engines.Answer(
        text=parsed.final_answer, model_version=parsed.model or "",
        citations=engines._citations([(u.rstrip(".,;"), "") for u in urls]),
        fanout_queries=[q for q in queries if q], searched=True,
        input_tokens=parsed.tokens_in or 0, output_tokens=parsed.tokens_out or 0,
        searches=len(searches), reported_cost_usd=0.0,
        raw=redact_structure({"transport": "subscription-cli", "cli": cli,
                              "search_calls": calls, "answer": parsed.final_answer,
                              "usage": parsed.usage, "reported_cost_usd": parsed.cost_usd}),
    )


def run(inventory_path, engine_path, output, state, config, day, *, dry_run=False):
    raw, perplexity = engine_config(engine_path, config, dry_run=dry_run)
    prompts = inventory.load(inventory_path)
    ready = {} if dry_run else require_ready(config, list(CLIS), state)
    runner = tui_harness.Runner(config, state, ready)
    out = output / day
    out.mkdir(parents=True, exist_ok=True)
    budget = visibility.Budget(float(raw["monthly_cap_usd"]), visibility.month_spend(output, day[:7]))
    rows, logs = [], []
    now = lambda: datetime.now(timezone.utc)
    for name, cli in ENGINE_CLIS.items():
        profile = visibility.EngineConfig(name=name, model=config["clis"][cli]["model"], key="",
                                          price_in=0, price_out=0, search_fee=0, est_call_usd=0)
        status, reason, count = "complete", None, 0
        for prompt in prompts:
            instruction = prompt["text"] + (
                "\nUse your native web search to answer. Cite sources as Markdown links with direct URLs. "
                "Use web and X search where available. Do not use MCP, files, shell or another provider."
            )
            import tempfile
            try:
                with tempfile.TemporaryDirectory(prefix=f"aeo-{cli}-", dir=state) as d:
                    if dry_run:
                        preview(cli, config, Path(d), instruction, purpose="search")
                        rows.append(visibility._failed_row(profile, prompt, now(), "Dry-run; no searches")
                                    | {"surface": "subscription-cli"})
                        continue
                    execution = runner.invoke(cli, instruction, "agent", workspace=Path(d), purpose="search")
                if execution.status != "completed":
                    raise ValueError(execution.error or execution.status)
                answer = answer_from_execution(cli, execution)
                row = visibility._row(profile, prompt, answer, 0.0, now())
                row["surface"] = "subscription-cli"
                row["usage_unknown"] = execution.transcript.tokens_in is None
                raw_dir = out / "raw" / name
                raw_dir.mkdir(parents=True, exist_ok=True)
                (raw_dir / f"{prompt['id']}.json").write_text(json.dumps(answer.raw, indent=1))
                rows.append(row)
                count += 1
            except (ValueError, tui_harness.StartRefusedError) as exc:
                rows.append(visibility._failed_row(profile, prompt, now(), str(exc))
                            | {"surface": "subscription-cli"})
                status, reason = "stopped", str(exc)
                # No retries or API fallback on usage, auth, receipt or search-evidence failures.
                break
        logs.append({"engine": name, "status": "dry-run" if dry_run else status, "reason": reason,
                     "runs": count, "surface": "subscription-cli"})
    if dry_run:
        rows.extend(visibility._failed_row(perplexity, p, now(), "Dry-run; no API calls") for p in prompts)
        logs.append({"engine": "perplexity", "status": "dry-run", "runs": 0, "surface": "api"})
    else:
        # This is the sole API-billed exception; its adapter, budget, keys and retries are unchanged.
        tui_harness.quiet_hours_guard(config.get("_quiet_hours", False), False)
        result = visibility.run_engine(perplexity, prompts, out=out, budget=budget,
                                       max_output_tokens=int(raw.get("max_output_tokens", 2000)),
                                       call=engines.perplexity_call, key=engines.op_read, now=now)
        rows.extend(result.pop("rows", []))
        logs.append({**result, "surface": "api"})
    (out / "runs.jsonl").write_text("".join(json.dumps(redact_structure(r)) + "\n" for r in rows))
    (out / "engines.json").write_text(json.dumps({"surface": "mixed", "cap_usd": budget.cap,
        "month_spend_usd": budget.spent, "engines": logs, "cli_invocations": runner.counts}, indent=1))
    baseline_file = output / "BASELINE"
    baseline = output / baseline_file.read_text().strip() if baseline_file.exists() else None
    text = visibility.write_report(out, baseline)
    if not dry_run and baseline is None:
        baseline_file.write_text(day + "\n")
    return text
