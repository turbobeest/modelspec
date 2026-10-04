"""Native web-search subscription adapters; Perplexity keeps its existing API."""

from __future__ import annotations

import json
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

from qa import tui_harness
from qa.providers import redact, redact_structure
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
    profiles = {
        name: visibility.EngineConfig(name=name, model=config["clis"][cli]["model"], key="",
                                      price_in=0, price_out=0, search_fee=0, est_call_usd=0)
        for name, cli in ENGINE_CLIS.items()
    } | {"perplexity": perplexity}
    rows, logs, api_rows = [], [], []
    now = lambda: datetime.now(timezone.utc)
    failure_reason = None
    try:
        for name, cli in ENGINE_CLIS.items():
            profile = profiles[name]
            status, reason = "complete", None
            for prompt in prompts:
                instruction = prompt["text"] + (
                    "\nUse your native web search to answer. Cite sources as Markdown links with direct URLs. "
                    "Use web and X search where available. Do not use MCP, files, shell or another provider."
                )
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
                except ValueError as exc:
                    error = f"skipped ({exc.status}: {exc})" if isinstance(exc, tui_harness.StartRefusedError) else str(exc)
                    rows.append(visibility._failed_row(profile, prompt, now(), error)
                                | {"surface": "subscription-cli"})
                    status, reason = "stopped", str(exc)
                    # No retries or API fallback on usage, auth, receipt or search-evidence failures.
                    break
                rows.append(row)
                raw_dir = out / "raw" / name
                raw_dir.mkdir(parents=True, exist_ok=True)
                (raw_dir / f"{prompt['id']}.json").write_text(json.dumps(answer.raw, indent=1))
            logs.append({"engine": name, "status": "dry-run" if dry_run else status, "reason": reason,
                         "surface": "subscription-cli"})
        name = "perplexity"
        if dry_run:
            rows.extend(visibility._failed_row(perplexity, p, now(), "Dry-run; no API calls") for p in prompts)
            logs.append({"engine": name, "status": "dry-run", "runs": 0, "surface": "api"})
        else:
            # The API exception has no CLI quiet-hours restriction. Budget, keys and retries stay unchanged.
            result = visibility.run_engine(perplexity, prompts, out=out, budget=budget,
                                           max_output_tokens=int(raw.get("max_output_tokens", 2000)),
                                           call=engines.perplexity_call, key=engines.op_read, now=now,
                                           recorded_rows=api_rows)
            result.pop("rows", None)
            logs.append({**result, "surface": "api"})
    except Exception as exc:
        # A late adapter/transport failure must not discard work or prevent private PR publication.
        failure_reason = redact(f"{type(exc).__name__}: {exc}")[:300]
        logs.append({"engine": name, "status": "stopped", "reason": failure_reason})
    finally:
        rows.extend(api_rows)
        recorded = {(row["engine"], row["prompt_id"]): row for row in rows}
        by_engine = {log["engine"]: log for log in logs}
        for engine, profile in profiles.items():
            surface = "api" if engine == "perplexity" else "subscription-cli"
            log = by_engine.get(engine)
            if log is None:
                log = {"engine": engine, "status": "skipped", "reason": failure_reason}
                logs.append(log)
            log["surface"] = surface
            log["runs"] = sum(row["engine"] == engine and "detection" in row for row in rows)
            reason = log.get("reason") or failure_reason or "engine stopped before completing the inventory"
            for prompt in prompts:
                if (engine, prompt["id"]) not in recorded:
                    recorded[engine, prompt["id"]] = visibility._failed_row(
                        profile, prompt, now(), f"skipped ({reason})"
                    ) | {"surface": surface}
        rows = [recorded[engine, prompt["id"]] for engine in profiles for prompt in prompts]
        partial = not dry_run and (failure_reason is not None or any("error" in row for row in rows))
        (out / "runs.jsonl").write_text("".join(json.dumps(redact_structure(r)) + "\n" for r in rows))
        engine_log = redact_structure({"surface": "mixed", "partial": partial, "cap_usd": budget.cap,
            "month_spend_usd": budget.spent, "engines": logs, "cli_invocations": runner.counts})
        (out / "engines.json").write_text(json.dumps(engine_log, indent=1))
        baseline_file = output / "BASELINE"
        try:
            baseline = output / baseline_file.read_text().strip() if baseline_file.exists() else None
            text = visibility.write_report(out, baseline)
            if not dry_run and not engine_log["partial"] and not baseline_file.exists():
                baseline_file.write_text(day + "\n")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            # A late report/baseline failure must still produce a report for publication.
            engine_log.update(partial=True, report_error=redact(f"{type(exc).__name__}: {exc}")[:300])
            (out / "engines.json").write_text(json.dumps(engine_log, indent=1))
            text = visibility.write_report(out)
    return text
