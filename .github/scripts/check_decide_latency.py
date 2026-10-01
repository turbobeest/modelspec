"""Warning-only deploy latency smoke over the deployed vocabulary's templates.

Initial requests are cold candidates, not proof of a fresh Cloudflare isolate.
Warm samples follow explicit warmups per template. No API key is introduced.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import subprocess
import tempfile
from pathlib import Path


def request(url, response_path, spec=None):
    command = [
        "curl",
        "-sS",
        "--max-time",
        "60",
        "-o",
        str(response_path),
        "-w",
        "%{http_code} %{time_total}",
        url,
    ]
    if spec is not None:
        command += ["-H", "content-type: application/json", "-d", json.dumps(spec)]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        return None, None, "transport failure"
    try:
        status, seconds = result.stdout.split()
        milliseconds = float(seconds) * 1000
        if status != "200":
            reason = (
                "anonymous callers require a key or are rate limited"
                if status in ("401", "403", "402", "429")
                else "endpoint unavailable"
            )
            return None, None, f"{reason} (HTTP {status})"
        body = json.loads(response_path.read_bytes())
    except (ValueError, OSError):
        return None, None, "invalid timing or JSON response"
    return body, milliseconds, None


def measure(host, count=20, warmups=5, *, vocabulary_url=None, explain="full"):
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        response_path = Path(tmp) / "response.json"
        vocabulary, _, reason = request(
            vocabulary_url or f"https://{host}/v1/vocabulary", response_path
        )
        if reason:
            return rows, f"vocabulary unavailable: {reason}"
        templates = vocabulary.get("templates") if isinstance(vocabulary, dict) else None
        if not isinstance(templates, list) or len(templates) < 8:
            return rows, "vocabulary has fewer than eight templates"
        for template in templates:
            if not isinstance(template, dict) or not isinstance(template.get("spec"), dict):
                return rows, "vocabulary contains an invalid template"
            spec = {"snapshot": "latest", "limit": 500, **template["spec"], "explain": explain}
            row = {"id": template["id"], "initial_ms": None, "warm_ms": [], "reason": None}
            for index in range(1 + warmups + count):
                body, elapsed, reason = request(f"https://{host}/v1/decide", response_path, spec)
                if reason is None and (
                    not isinstance(body, dict)
                    or not body.get("decision_id")
                    or not body.get("snapshot")
                ):
                    reason = "response is not a Decision"
                if reason:
                    row["reason"] = reason
                    break
                if index == 0:
                    row["initial_ms"] = elapsed
                elif index > warmups:
                    row["warm_ms"].append(elapsed)
            rows.append(row)
            if row["reason"] and "anonymous callers" in row["reason"]:
                return rows, row["reason"]
    return rows, None


def percentile(values, fraction):
    return sorted(values)[math.ceil(fraction * len(values)) - 1]


def report(rows, reason, warmups, count, explain):
    lines = [
        f"Decision latency smoke, explain `{explain}`. Each template has an initial request, "
        f"{warmups} excluded warmups, then {count} warm samples. Target warm p95 ≤ 500 ms.",
        "Initial requests are cold candidates; the client cannot force or identify "
        "a fresh isolate. "
        "Warm samples can still encounter a new isolate. "
        "Timings include connection setup and response transfer.",
        "",
        "| Template | Initial / cold candidate ms | Warm p50 ms | Warm p95 ms | Samples / status |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    warnings = []
    if reason:
        warnings.append(
            f"Decision latency smoke incomplete: {reason}. "
            "No API key is available to the existing smoke."
        )
    for row in rows:
        initial = "—" if row["initial_ms"] is None else f"{row['initial_ms']:.1f}"
        values = row["warm_ms"]
        if row["reason"]:
            lines.append(f"| {row['id']} | {initial} | — | — | Skipped: {row['reason']} |")
            warnings.append(f"Decision template {row['id']} skipped: {row['reason']}")
            continue
        p50, p95 = statistics.median(values), percentile(values, 0.95)
        lines.append(f"| {row['id']} | {initial} | {p50:.1f} | {p95:.1f} | {len(values)} |")
        if p95 > 500:
            warnings.append(f"Decision template {row['id']} warm p95 {p95:.1f} ms exceeds 500 ms")
    return "\n".join(lines), warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True)
    parser.add_argument("--warmups", type=int, default=5)
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--vocabulary-url")
    parser.add_argument("--explain", choices=("none", "summary", "full"), default="full")
    args = parser.parse_args()
    if args.count < 1 or args.warmups < 1:
        parser.error("count and warmups must be positive")
    rows, reason = measure(
        args.host,
        args.count,
        args.warmups,
        vocabulary_url=args.vocabulary_url,
        explain=args.explain,
    )
    summary, warnings = report(rows, reason, args.warmups, args.count, args.explain)
    print(summary)
    for warning in warnings:
        print(f"::warning::{warning}")
    if path := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(path, "a") as output:
            output.write("\n" + summary + "\n")


if __name__ == "__main__":
    main()
