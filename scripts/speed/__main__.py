"""``python -m scripts.speed``: plan, preflight, run, dry-run, aggregate, verify.

Only ``run --live`` sends a paid request, and only with ``--cap-usd``. Every
other command is free: ``preflight`` reads model lists, ``dry-run`` replays
fixtures and opens no socket.
"""

from __future__ import annotations

import argparse
import dataclasses
import gzip
import hashlib
import json
import sys
import tempfile
from collections import Counter
from datetime import UTC, datetime, timedelta
from pathlib import Path

import yaml

from scripts.speed.aggregate import aggregate
from scripts.speed.method import (
    HEADLINE_WORKLOAD,
    REPETITIONS_PER_SLOT,
    SLOT_HOURS_UTC,
    WARMUPS_PER_SLOT,
)
from scripts.speed.plan import PILOT, Plan, entry_cost, load_plan, slot_cost
from scripts.speed.providers import APIS
from scripts.speed.run import SpendRefusedError, keys_from_env, probe_vantage, run_slot
from scripts.speed.transport import FIXTURES, FixtureTransport, LiveTransport, Profile
from scripts.speed.verify import verify

#: The first simulated slot of a dry run. Fixed, so a dry run is reproducible.
DRY_RUN_START = datetime(2026, 9, 1, tzinfo=UTC)


def _plan(args: argparse.Namespace) -> Plan:
    plan = load_plan(Path(args.plan))
    if args.schedule == "baseline":
        plan = dataclasses.replace(plan, name="baseline", repetitions=REPETITIONS_PER_SLOT,
                                   warmups=WARMUPS_PER_SLOT)
    return plan


def cmd_plan(args: argparse.Namespace) -> int:
    plan = _plan(args)
    cost = slot_cost(plan)
    print(f"plan {plan.name}: {len(plan.entries)} offerings, {cost.calls} calls a slot "
          f"({plan.warmups} warm-up and {plan.repetitions} measured per workload)")
    for offering, c in entry_cost(plan).items():
        print(f"  {offering:66} {c.calls:3} calls  ~${c.expected_usd:6.2f}  "
              f"at most ${c.bound_usd:6.2f}")
    print(f"one slot: ~${cost.expected_usd:.2f} expected, at most ${cost.bound_usd:.2f}")
    if args.slots > 1:
        print(f"{args.slots} slots: ~${cost.expected_usd * args.slots:.2f} expected, "
              f"at most ${cost.bound_usd * args.slots:.2f}")
    print("keys: " + ", ".join(plan.env))
    return 0


def cmd_preflight(args: argparse.Namespace) -> int:
    """Free checks only: keys present, each pinned model listed, the vantage."""
    plan = _plan(args)
    keys = keys_from_env()
    transport = LiveTransport()
    failed = False
    for entry in plan.entries:
        api = APIS[entry.api]
        if entry.api not in keys:
            print(f"MISSING  {entry.offering}: set {api.env}")
            failed = True
            continue
        if api.models_path is None:
            print(f"UNCHECKED {entry.offering}: {api.id} has no model list; "
                  f"{entry.api_model} is confirmed by the first pilot call")
            continue
        status, body = transport.get_json(api.host, api.models_path, api.headers(keys[entry.api]))
        listed = json.dumps(body)
        if status != 200 or entry.api_model not in listed:
            print(f"FAIL     {entry.offering}: HTTP {status}; {entry.api_model} not listed")
            failed = True
        else:
            print(f"OK       {entry.offering}: {entry.api_model}")
    print(f"vantage: {probe_vantage()}")
    return 1 if failed else 0


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = (json.dumps(value, indent=1, sort_keys=True) + "\n").encode("utf-8")
    path.write_bytes(gzip.compress(text, mtime=0) if path.suffix == ".gz" else text)


def cmd_run(args: argparse.Namespace) -> int:
    if not args.live:
        print("run sends paid requests: pass --live and --cap-usd, or use dry-run",
              file=sys.stderr)
        return 2
    plan = _plan(args)
    try:
        run = run_slot(plan, LiveTransport(), cap_usd=args.cap_usd, keys=keys_from_env(),
                       vantage=probe_vantage())
    except SpendRefusedError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    out = Path(args.window) / "runs" / f"{run['run_id']}.json.gz"
    _write(out, run)
    ok = sum(s["status"] == "ok" for s in run["samples"])
    print(f"{out}: {ok} of {len(run['samples'])} requests ok, ${run['spent_usd']:.2f} spent "
          f"of a ${run['cap_usd']:.2f} cap" + (" (stopped at the cap)" if run["stopped"] else ""))
    return 0


def dry_run(plan: Plan, slots: int, out: Path) -> dict:
    """Simulate ``slots`` scheduled slots against the fixtures, then aggregate and verify."""
    raw = yaml.safe_load((FIXTURES / "profiles.yaml").read_text(encoding="utf-8"))
    transport = FixtureTransport({k: Profile(**v) for k, v in raw.items()})
    runs = []
    for i in range(slots):
        day, hour = divmod(i, len(SLOT_HOURS_UTC))
        clock = DRY_RUN_START + timedelta(days=day, hours=SLOT_HOURS_UTC[hour])
        ticks = iter(range(10**6))

        def now(clock: datetime = clock, ticks=ticks) -> datetime:
            return clock + timedelta(seconds=5 * next(ticks))

        def nonce(call, slot: int = i) -> str:
            key = f"{slot}|{call.entry.offering}|{call.workload.id}|{call.sample}|{call.warmup}"
            return hashlib.sha256(key.encode()).hexdigest()[:16]

        run = run_slot(plan, transport, cap_usd=slot_cost(plan).bound_usd,
                       keys={api: "fixture" for api in APIS}, vantage="fixture",
                       now=now, nonce=nonce)
        _write(out / "runs" / f"{run['run_id']}.json.gz", run)
        runs.append(run)
    measurement = aggregate(runs)
    verifications = verify(measurement, runs, today=DRY_RUN_START.date() + timedelta(days=4))
    _write(out / "measurement.json", measurement)
    (out / "verifications.jsonl").write_text(
        "".join(json.dumps(v, sort_keys=True) + "\n" for v in verifications), encoding="utf-8")
    return {"runs": runs, "measurement": measurement, "verifications": verifications,
            "fixture_calls": transport.calls}


def cmd_dry_run(args: argparse.Namespace) -> int:
    plan = _plan(args)
    out = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix="speed-dry-run-"))
    result = dry_run(plan, args.slots, out)
    measurement = result["measurement"]
    for row in measurement["results"]:
        if row["workload"] != HEADLINE_WORKLOAD:
            continue
        verdict = "publish" if row["publishable"] else "hold: " + "; ".join(row["reasons"])
        ttft, tps = row["ttft_ms"], row["throughput_tps"]
        print(f"  {row['offering']:66} n={row['n']:3} ttft {ttft['median']:7.0f} ms "
              f"[{ttft['interval'][0]:.0f}, {ttft['interval'][1]:.0f}]  "
              f"{tps['median']:6.1f} tok/s [{tps['interval'][0]:.1f}, "
              f"{tps['interval'][1]:.1f}]  {verdict}")
    outcomes = sorted({v["outcome"] for v in result["verifications"]})
    print(f"{result['fixture_calls']} fixture calls, no network; {len(measurement['facts'])} "
          f"facts ({measurement['provenance']}), verifications {outcomes}; written to {out}")
    return 0 if outcomes in ([], ["verified"]) else 1


def window_runs(window: Path) -> list[dict]:
    """Every run file in a window. A window is aggregated and verified whole, so
    no slot can be left out; a rerun of a slot replaces its earlier file."""
    return [json.loads(gzip.decompress(path.read_bytes()))
            for path in sorted((window / "runs").glob("*.json.gz"))]


def cmd_aggregate(args: argparse.Namespace) -> int:
    window = Path(args.window)
    measurement = aggregate(window_runs(window))
    _write(window / "measurement.json", measurement)
    held = [r for r in measurement["results"] if not r["publishable"]]
    print(f"{window}/measurement.json: {len(measurement['facts'])} facts; {len(held)} of "
          f"{len(measurement['results'])} results held by a gate")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    window = Path(args.window)
    measurement = json.loads((window / "measurement.json").read_text(encoding="utf-8"))
    records = verify(measurement, window_runs(window))
    (window / "verifications.jsonl").write_text(
        "".join(json.dumps(r, sort_keys=True) + "\n" for r in records), encoding="utf-8")
    outcomes = Counter(r["outcome"] for r in records)
    print(f"{window}/verifications.jsonl: {dict(outcomes)}")
    return 0 if set(outcomes) <= {"verified"} else 1


def _cell(summary: dict | None, digits: int) -> str:
    if summary is None:
        return "none"
    low, high = summary["interval"]
    return f"{summary['median']:.{digits}f} [{low:.{digits}f}, {high:.{digits}f}]"


def report(window: Path) -> str:
    """A window as Markdown: spend per run, then every offering and workload."""
    runs = window_runs(window)
    measurement = json.loads((window / "measurement.json").read_text(encoding="utf-8"))
    lines = ["| Run | Slot | Vantage | Requests | Spent | Cap | Stopped |",
             "|---|---|---|---|---|---|---|"]
    for r in runs:
        lines.append(f"| {r['run_id']} | {r['slot']} | {r['vantage']} | {len(r['samples'])} "
                     f"| ${r['spent_usd']:.2f} | ${r['cap_usd']:.2f} | {r['stopped'] or 'no'} |")
    lines += ["", f"Total spent: ${sum(r['spent_usd'] for r in runs):.2f}", "",
              "| Offering | Workload | Good / attempted | Failures | TTFT ms, median [95%] "
              "| Tokens/s, median [95%] | Gates |",
              "|---|---|---|---|---|---|---|"]
    for row in measurement["results"]:
        ttft, tps = row["ttft_ms"], row["throughput_tps"]
        gates = "pass" if row["publishable"] else "; ".join(row["reasons"])
        failures = ", ".join(f"{k} {v}" for k, v in row["failures"].items()) or "none"
        lines.append(f"| {row['offering']} | {row['workload']} | {row['n']} / {row['attempted']} "
                     f"| {failures} | {_cell(ttft, 0)} | {_cell(tps, 1)} | {gates} |")
    return "\n".join(lines) + "\n"


def cmd_report(args: argparse.Namespace) -> int:
    print(report(Path(args.window)), end="")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m scripts.speed", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    def with_plan(p: argparse.ArgumentParser, schedule: str) -> argparse.ArgumentParser:
        p.add_argument("--plan", default=str(PILOT))
        p.add_argument("--schedule", choices=("pilot", "baseline"), default=schedule,
                       help="pilot: the plan file's repetitions; baseline: the method's")
        return p

    p = with_plan(sub.add_parser("plan", help="calls and cost, free"), "pilot")
    p.add_argument("--slots", type=int, default=1)
    p.set_defaults(func=cmd_plan)
    p = with_plan(sub.add_parser("preflight", help="keys, model IDs and vantage, free"),
                  "pilot")
    p.set_defaults(func=cmd_preflight)
    p = with_plan(sub.add_parser("run", help="one live slot; paid"), "pilot")
    p.add_argument("--live", action="store_true")
    p.add_argument("--cap-usd", type=float, required=True)
    p.add_argument("--window", default="measurements/speed/pilot",
                   help="the window directory; the run file goes in its runs/")
    p.set_defaults(func=cmd_run)
    p = with_plan(sub.add_parser("dry-run", help="replay fixtures; free"), "baseline")
    p.add_argument("--slots", type=int, default=12)
    p.add_argument("--out")
    p.set_defaults(func=cmd_dry_run)
    p = sub.add_parser("aggregate", help="merge every run in a window into a measurement")
    p.add_argument("window")
    p.set_defaults(func=cmd_aggregate)
    p = sub.add_parser("verify", help="re-derive a window's facts from its raw runs")
    p.add_argument("window")
    p.set_defaults(func=cmd_verify)
    p = sub.add_parser("report", help="a window's spend and results as Markdown")
    p.add_argument("window")
    p.set_defaults(func=cmd_report)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
