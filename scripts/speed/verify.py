"""The second key for a speed fact: re-derive it from the raw run files.

This is a separate implementation of everything between a provider's stream
and a published median. It trusts no number the collector wrote per sample:
it re-reads each counted sample's raw events with its own parser, re-times
them, re-decides whether the sample counts, re-derives the vantage, the run
set and every gate, and recomputes the statistics by hand (order statistics,
interpolated quartiles, exact integer binomial tails). It shares only the
method's constants. A fact that differs gets a ``mismatch`` record, which
keeps it out of the snapshot.
"""

from __future__ import annotations

import datetime
import json
import math
from collections import Counter
from typing import Any

from decision.model import value_hash
from scripts.speed.aggregate import METRICS, evidence_sha256
from scripts.speed.method import (
    INTERVAL_LEVEL,
    MAX_FAILURE_RATE,
    MAX_WINDOW_DAYS,
    METHOD_ID,
    MIN_CONTENT_EVENTS,
    MIN_DAYS,
    MIN_SAMPLES,
    MIN_SLOTS,
    MIN_VISIBLE_TOKENS,
    REPETITIONS_PER_SLOT,
    SLOT_HOURS_UTC,
    WORKLOADS,
)

COLLECTOR = {"agent": "scripts.speed.aggregate", "model_family": "deterministic",
             "method": f"{METHOD_ID} aggregation of the slot run files"}
VERIFIER = {"agent": "scripts.speed.verify", "model_family": "deterministic",
            "method": "independent re-timing of every counted sample from its raw stream "
                      "events, with the run set, vantage, gates and statistics re-derived"}


# ── re-reading a stream ────────────────────────────────────────────────────


def _as_int(value: Any) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _read(api: str, events: list[list[Any]]) -> dict[str, Any]:
    """Content event times and the usage, straight from the payloads."""
    content: list[float] = []
    usage = {"output": 0, "reasoning": 0, "cached": 0, "thinking": 0}
    error = False
    for t, payload in events:
        if payload == "[DONE]":
            break
        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            error = True
            continue
        if not isinstance(event, dict):
            error = True
            continue
        if api == "anthropic":
            if event.get("type") == "error":
                error = True
            delta = event.get("delta") or {}
            if event.get("type") == "content_block_delta" and delta.get("type") == "text_delta" \
                    and delta.get("text"):
                content.append(t)
            if delta.get("type") == "thinking_delta":
                usage["thinking"] += 1
            if event.get("type") == "message_start":
                start = (event.get("message") or {}).get("usage") or {}
                usage["cached"] = _as_int(start.get("cache_read_input_tokens"))
            if event.get("type") == "message_delta":
                usage["output"] = _as_int((event.get("usage") or {}).get("output_tokens"))
        elif api == "gemini":
            if "error" in event:
                error = True
            parts = [p for c in event.get("candidates") or []
                     for p in (c.get("content") or {}).get("parts") or []]
            if any(p.get("text") and not p.get("thought") for p in parts):
                content.append(t)
            if any(p.get("thought") for p in parts):
                usage["thinking"] += 1
            meta = event.get("usageMetadata")
            if meta:
                usage["reasoning"] = _as_int(meta.get("thoughtsTokenCount"))
                usage["output"] = _as_int(meta.get("candidatesTokenCount")) + usage["reasoning"]
                usage["cached"] = _as_int(meta.get("cachedContentTokenCount"))
        else:
            if "error" in event:
                error = True
            deltas = [c.get("delta") or {} for c in event.get("choices") or []]
            if any(d.get("content") for d in deltas):
                content.append(t)
            if any(d.get("reasoning_content") or d.get("reasoning") for d in deltas):
                usage["thinking"] += 1
            meta = event.get("usage")
            if meta:
                usage["output"] = _as_int(meta.get("completion_tokens"))
                usage["reasoning"] = _as_int(
                    (meta.get("completion_tokens_details") or {}).get("reasoning_tokens"))
                usage["cached"] = (_as_int((meta.get("prompt_tokens_details") or {})
                                           .get("cached_tokens"))
                                   or _as_int(meta.get("prompt_cache_hit_tokens")))
    return {"content": content, "error": error, **usage}


def retime(api: str, sample: dict[str, Any]) -> dict[str, float] | None:
    """The sample's two numbers, or ``None`` when it does not count."""
    if sample["http_status"] != 200 or sample["error"]:
        return None
    read = _read(api, sample["events"])
    content = read["content"]
    visible = read["output"] - read["reasoning"]
    if (read["error"] or read["cached"] or visible < MIN_VISIBLE_TOKENS
            or len(content) < MIN_CONTENT_EVENTS or content[-1] <= content[0]):
        return None
    e = len(content)
    return {
        "ttft_ms": round(content[0] * 1000, 1),
        "throughput_tps": round(visible * (e - 1) / e / (content[-1] - content[0]), 2),
        "reasoning": read["reasoning"],
    }


# ── statistics, by hand ────────────────────────────────────────────────────


def _quantile(xs: list[float], q: float) -> float:
    position = q * (len(xs) - 1)
    low = math.floor(position)
    high = min(low + 1, len(xs) - 1)
    return xs[low] + (position - low) * (xs[high] - xs[low])


def _median(xs: list[float]) -> float:
    return (xs[(len(xs) - 1) // 2] + xs[len(xs) // 2]) / 2


def _interval(xs: list[float]) -> tuple[float, float]:
    n = len(xs)
    # Each tail may hold at most (1 - level) / 2 of 2**n outcomes.
    tail_limit = round((1 - INTERVAL_LEVEL) / 2 * 10**6)
    excluded, tail = 0, 0
    while excluded < n:
        tail += math.comb(n, excluded)
        if tail * 10**6 > tail_limit * 2**n:
            break
        excluded += 1
    if excluded == 0:
        return xs[0], xs[-1]
    return xs[excluded - 1], xs[n - excluded]


# ── the gates, re-derived ──────────────────────────────────────────────────


def _gates_hold(n: int, slots: set[str], failure_rate: float, reasoned: int,
                reasoning_off: bool) -> list[str]:
    problems = []
    dates = sorted({datetime.date.fromisoformat(s[:10]) for s in slots})
    if n < MIN_SAMPLES or len(slots) < MIN_SLOTS or len(dates) < MIN_DAYS:
        problems.append(f"too thin: n={n}, {len(slots)} slots, {len(dates)} days")
    if {int(s[11:13]) for s in slots} != set(SLOT_HOURS_UTC):
        problems.append("the slots miss a scheduled hour")
    if dates and (dates[-1] - dates[0]).days >= MAX_WINDOW_DAYS:
        problems.append("the window is too long")
    if failure_rate > MAX_FAILURE_RATE:
        problems.append(f"failure rate {failure_rate:.2f}")
    if reasoning_off and reasoned:
        problems.append(f"{reasoned} requests reasoned under an effort that claims none")
    return problems


def verify(measurement: dict[str, Any], runs: list[dict[str, Any]],
           today: datetime.date | None = None) -> list[dict[str, Any]]:
    """One verification record per fact in ``measurement``.

    ``runs`` must be every run file in the measurement's window: a run the
    measurement leaves out, or one it names that is missing, is a mismatch.
    """
    today = today or datetime.date.today()
    problems = []
    named = set(measurement["runs"]) | set(measurement["dropped_runs"])
    given = Counter(r["run_id"] for r in runs)
    if set(given) != named or any(n > 1 for n in given.values()):
        problems.append("the run files are not exactly the runs the measurement names")
    counts = Counter(r["vantage"] for r in runs)
    vantage = sorted(counts, key=lambda v: (-counts[v], v))[0] if counts else None
    if vantage != measurement["vantage"]:
        problems.append(f"the most common vantage is {vantage}, not {measurement['vantage']}")
    kept = [r for r in runs if r["vantage"] == vantage]
    if evidence_sha256(kept) != measurement["evidence_sha256"]:
        problems.append("the kept run files do not hash to evidence_sha256")
    configurations: dict[str, set[str]] = {}
    for r in runs:
        for e in r["offerings"]:
            key = json.dumps({k: e.get(k) for k in
                              ("api", "api_model", "effort", "params", "reasoning_off")},
                             sort_keys=True)
            configurations.setdefault(e["offering"], set()).add(key)
    if any(len(seen) > 1 for seen in configurations.values()):
        problems.append("an offering's model, effort or parameters changed between runs")
    expected = {w.id: w.prompt_sha256() for w in WORKLOADS}
    for r in runs:
        if r["provenance"] != measurement["provenance"] or r["method"] != METHOD_ID:
            problems.append(f"{r['run_id']} is {r['provenance']} {r['method']}")
        if {k: v["prompt_sha256"] for k, v in r["workloads"].items()} != expected:
            problems.append(f"{r['run_id']}'s prompts are not {METHOD_ID}'s")
    records = []
    for fact in measurement["facts"]:
        block = fact["measurement"]
        offering = fact["subject"]["id"]
        metric = next(m for m, (facet, _) in METRICS.items() if facet == fact["facet"])
        digits = METRICS[metric][1]
        counted, reasoned, good = 0, 0, []
        entry: dict[str, Any] = {}
        for r in kept:
            entry = next((e for e in r["offerings"] if e["offering"] == offering), entry)
            for s in r["samples"]:
                if (s["offering"] != offering or s["workload"] != block["workload"]
                        or s["warmup"] or s["sample"] >= REPETITIONS_PER_SLOT):
                    continue
                counted += 1
                read = _read(entry["api"], s["events"])
                reasoned += bool(read["reasoning"] or read["thinking"])
                timed = retime(entry["api"], s)
                if timed is not None:
                    good.append((timed, r["slot"], s["started_at"]))
        diffs = list(problems)
        if not good:
            diffs.append("no sample re-times as good")
        else:
            xs = sorted(t[metric] for t, _, _ in good)
            reasoning = _median(sorted(float(t["reasoning"]) for t, _, _ in good))
            slots = {slot for _, slot, _ in good}
            failure_rate = round(1 - len(good) / counted, 4)
            diffs += _gates_hold(len(good), slots, failure_rate, reasoned,
                                 entry.get("reasoning_off", False))
            times = sorted(t for _, _, t in good)
            again = {
                "n": len(good),
                "time_slots": len(slots),
                "days": len({s[:10] for s in slots}),
                "failure_rate": failure_rate,
                "reasoning_tokens": reasoning,
                "effort": entry.get("effort"),
                "provenance": measurement["provenance"],
                "vantage": vantage,
                "window": {"start": times[0], "end": times[-1]},
                "median": round(_median(xs), digits),
                "iqr": [round(_quantile(xs, 0.25), digits), round(_quantile(xs, 0.75), digits)],
                "interval": [round(x, digits) for x in _interval(xs)],
            }
            for key, value in again.items():
                if block.get(key) != value:
                    diffs.append(f"{key}: fact has {block.get(key)}, re-derived {value}")
            if fact["value"] != again["median"]:
                diffs.append(f"value: fact has {fact['value']}, re-derived {again['median']}")
        records.append({
            "target": {"kind": "fact", "id": fact["id"], "value_hash": value_hash(fact["value"])},
            "collector": COLLECTOR,
            "verifier": VERIFIER,
            "method": f"{METHOD_ID} re-derivation from {len(runs)} run files",
            "outcome": "mismatch" if diffs else "verified",
            "date": today.isoformat(),
            "diff": "; ".join(diffs) if diffs else None,
        })
    return records
