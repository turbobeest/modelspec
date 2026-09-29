"""Merge slot runs into one measurement, gate it, and write the offering facts.

Every offering and workload gets a result row, published or not, with the
reasons it missed a gate. Only the headline workload's rows that pass every
gate become facts; the facts are unverified until ``verify.py`` recomputes
them from the same run files.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import asdict
from datetime import date
from typing import Any

from scripts.speed.method import (
    HEADLINE_WORKLOAD,
    MAX_FAILURE_RATE,
    MAX_WINDOW_DAYS,
    METHOD_ID,
    METHOD_URL,
    MIN_DAYS,
    MIN_SAMPLES,
    MIN_SLOTS,
    REPETITIONS_PER_SLOT,
    SLOT_HOURS_UTC,
    WORKLOAD_IDS,
    WORKLOADS,
    summarise,
)

MEASUREMENT_FORMAT = "modelspec.speed-measurement"
#: The registry source every speed fact cites. It is registered when the first
#: live measurement is promoted; its snapshot ref is the run files' hash.
SOURCE_ID = "modelspec-speed-v1"
#: Sample field -> (facet, decimal places the fact keeps).
METRICS = {
    "ttft_ms": ("offering.speed.time_to_first_token", 0),
    "throughput_tps": ("offering.speed.throughput", 1),
}


class AggregateError(ValueError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def evidence_sha256(runs: list[dict[str, Any]]) -> str:
    ordered = sorted(runs, key=lambda r: r["run_id"])
    return "sha256:" + hashlib.sha256(canonical(ordered)).hexdigest()


def sample_key(run: dict[str, Any], sample: dict[str, Any]) -> tuple[Any, ...]:
    return (run["slot"], sample["offering"], sample["workload"], sample["sample"],
            sample["warmup"])


def settings_of(entry: dict[str, Any]) -> dict[str, Any]:
    """What a number depends on besides the method: the model, its effort, its parameters."""
    return {k: entry.get(k) for k in ("api", "api_model", "effort", "params", "reasoning_off")}


def _check(runs: list[dict[str, Any]]) -> str:
    if not runs:
        raise AggregateError("no runs to aggregate")
    ids = Counter(r["run_id"] for r in runs)
    keys = Counter(sample_key(r, s) for r in runs for s in r["samples"])
    repeated = sorted(i for i, n in ids.items() if n > 1)
    if repeated or any(n > 1 for n in keys.values()):
        raise AggregateError(f"a run or a sample appears twice ({repeated or 'same slot'}); "
                             "a sample counts once")
    settings: dict[str, set[bytes]] = {}
    for r in runs:
        for e in r["offerings"]:
            settings.setdefault(e["offering"], set()).add(canonical(settings_of(e)))
    drifted = sorted(o for o, seen in settings.items() if len(seen) > 1)
    if drifted:
        raise AggregateError(f"settings changed between runs for {drifted}; "
                             "a window measures one configuration")
    provenance = {r["provenance"] for r in runs}
    if len(provenance) != 1:
        raise AggregateError(f"runs mix provenance {sorted(provenance)}")
    expected = {w.id: w.prompt_sha256() for w in WORKLOADS}
    for r in runs:
        if r["method"] != METHOD_ID:
            raise AggregateError(f"{r['run_id']} used {r['method']}, not {METHOD_ID}")
        hashes = {k: v["prompt_sha256"] for k, v in r["workloads"].items()}
        if hashes != expected:
            raise AggregateError(f"{r['run_id']}'s prompts differ from {METHOD_ID}'s")
    return provenance.pop()


def _gate(n: int, slots: set[str], failure_rate: float, reasoned: int,
          reasoning_off: bool) -> list[str]:
    reasons = []
    days = sorted({slot[:10] for slot in slots})
    hours = {int(slot[11:13]) for slot in slots}
    if n < MIN_SAMPLES:
        reasons.append(f"{n} good samples; the gate is {MIN_SAMPLES}")
    if len(slots) < MIN_SLOTS:
        reasons.append(f"{len(slots)} time slots; the gate is {MIN_SLOTS}")
    if hours != set(SLOT_HOURS_UTC):
        reasons.append(f"slots cover {len(hours)} of the {len(SLOT_HOURS_UTC)} scheduled hours")
    if len(days) < MIN_DAYS:
        reasons.append(f"{len(days)} days; the gate is {MIN_DAYS}")
    if days and (date.fromisoformat(days[-1]) - date.fromisoformat(days[0])).days \
            >= MAX_WINDOW_DAYS:
        reasons.append(f"the slots span {MAX_WINDOW_DAYS} days or more")
    if failure_rate > MAX_FAILURE_RATE:
        reasons.append(f"{failure_rate:.0%} of requests failed; the gate is "
                       f"{MAX_FAILURE_RATE:.0%}")
    if reasoning_off and reasoned:
        reasons.append(f"the effort claims no reasoning, but {reasoned} counted requests "
                       "reasoned")
    return reasons


def vantage_of(runs: list[dict[str, Any]]) -> str:
    """The most common vantage; a tie goes to the first name, not to file order."""
    counts = Counter(r["vantage"] for r in runs)
    return min(counts, key=lambda v: (-counts[v], v))


def aggregate(runs: list[dict[str, Any]]) -> dict[str, Any]:
    provenance = _check(runs)
    vantage = vantage_of(runs)
    kept = sorted((r for r in runs if r["vantage"] == vantage), key=lambda r: r["slot"])
    entries = {e["offering"]: e for r in kept for e in r["offerings"]}
    rows: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for r in kept:
        for s in r["samples"]:
            # Repetitions past speed-v1's per-slot count are outside the method.
            if not s["warmup"] and s["sample"] < REPETITIONS_PER_SLOT:
                rows.setdefault((s["offering"], s["workload"]), []).append(s | {"slot": r["slot"]})
    results = []
    for (offering, workload_id), samples in sorted(
            rows.items(), key=lambda kv: (kv[0][0], WORKLOAD_IDS.index(kv[0][1]))):
        ok = [s for s in samples if s["status"] == "ok"]
        slots = {s["slot"] for s in ok}
        failure_rate = 1 - len(ok) / len(samples)
        reasoning = summarise([s["reasoning_tokens"] for s in ok]).median if ok else None
        reasoned = sum(1 for s in samples if s["reasoning_tokens"] or s["reasoning_events"])
        entry = entries[offering]
        reasons = _gate(len(ok), slots, failure_rate, reasoned, entry.get("reasoning_off", False))
        times = sorted(s["started_at"] for s in ok)
        results.append({
            "offering": offering,
            "workload": workload_id,
            "effort": entry["effort"],
            "attempted": len(samples),
            "n": len(ok),
            "failures": dict(sorted(Counter(s["status"] for s in samples
                                            if s["status"] != "ok").items())),
            "failure_rate": round(failure_rate, 4),
            "time_slots": len(slots),
            "days": len({slot[:10] for slot in slots}),
            "reasoning_tokens": reasoning,
            "window": {"start": times[0], "end": times[-1]} if times else None,
            "publishable": not reasons,
            "reasons": reasons,
            **{m: asdict(summarise([s[m] for s in ok])) if ok else None for m in METRICS},
        })
    body: dict[str, Any] = {
        "format": MEASUREMENT_FORMAT,
        "method": METHOD_ID,
        "method_url": METHOD_URL,
        "provenance": provenance,
        "vantage": vantage,
        "runs": sorted(r["run_id"] for r in kept),
        "dropped_runs": sorted(r["run_id"] for r in runs if r["vantage"] != vantage),
        "evidence_sha256": evidence_sha256(kept),
        "results": results,
    }
    ends = [r["window"]["end"] for r in results if r["window"]]
    stamp = max(ends)[:10] if ends else "empty"
    body["measurement_id"] = (
        f"{METHOD_ID}-{stamp}-{hashlib.sha256(canonical(body)).hexdigest()[:12]}")
    body["facts"] = facts(body)
    return body


def measurement_block(body: dict[str, Any], result: dict[str, Any], metric: str
                      ) -> dict[str, Any]:
    digits = METRICS[metric][1]
    summary = result[metric]
    return {
        "measured_by": "ModelSpec",
        "method": body["method"],
        "method_url": body["method_url"],
        "workload": result["workload"],
        "effort": result["effort"],
        "reasoning_tokens": result["reasoning_tokens"],
        "provenance": body["provenance"],
        "run_id": body["measurement_id"],
        "vantage": body["vantage"],
        "n": summary["n"],
        "time_slots": result["time_slots"],
        "days": result["days"],
        "failure_rate": result["failure_rate"],
        "median": round(summary["median"], digits),
        "iqr": [round(x, digits) for x in summary["iqr"]],
        "interval": [round(x, digits) for x in summary["interval"]],
        "window": result["window"],
    }


def facts(body: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for result in body["results"]:
        if result["workload"] != HEADLINE_WORKLOAD or not result["publishable"]:
            continue
        offering = result["offering"]
        for metric, (facet, _) in METRICS.items():
            block = measurement_block(body, result, metric)
            out.append({
                "id": f"{offering}#{facet}",
                "subject": {"kind": "offering", "id": offering},
                "facet": facet,
                "value": block["median"],
                "state": "known",
                "sources": [{"source_id": SOURCE_ID, "snapshot_ref": body["evidence_sha256"],
                             "cited_regions": [f"{offering}/{result['workload']}"]}],
                "measurement": block,
            })
    return out
