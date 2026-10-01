"""Warning-only deploy latency smoke. Uses the existing smoke's anonymous path.

BUILD_COMMIT identifies a deployment, it is not an authentication credential.
If anonymous decisions require a key or a snapshot is unavailable, report a
skip in the summary. Never print response rows or introduce a secret.
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

SPEC = {
    "spec_version": 1,
    "snapshot": "latest",
    "where": ["model.class = text-generator", "model.lifecycle = active"],
    "optimize": {"weights": {"software_engineering": 1}},
    "explain": "full",
    "limit": 500,
}


def measure(host, count=20):
    timings = []
    with tempfile.TemporaryDirectory() as tmp:
        response_path = Path(tmp) / "response.json"
        for i in range(count + 1):
            # curl's total includes connection setup and reading the whole body.
            result = subprocess.run(
                [
                    "curl",
                    "-sS",
                    "--max-time",
                    "60",
                    "-o",
                    str(response_path),
                    "-w",
                    "%{http_code} %{time_total}",
                    f"https://{host}/v1/decide",
                    "-H",
                    "content-type: application/json",
                    "-d",
                    json.dumps(SPEC),
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode:
                return None, "transport failure"
            status, seconds = result.stdout.split()
            if status != "200":
                reason = (
                    "anonymous callers require a key or are rate limited"
                    if status in ("401", "403", "402", "429")
                    else "decision unavailable"
                )
                return None, f"{reason} (HTTP {status})"
            try:
                body = json.loads(response_path.read_bytes())
            except ValueError:
                return None, "invalid JSON response"
            if (
                not isinstance(body, dict)
                or not body.get("decision_id")
                or not body.get("snapshot")
            ):
                return None, "response is not a Decision"
            if i:  # First request warms the isolate and is excluded.
                timings.append(float(seconds) * 1000)
    return timings, None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True)
    args = parser.parse_args()
    timings, reason = measure(args.host)
    if reason:
        summary = (
            f"Decision latency smoke skipped: {reason}. "
            "No API key is available to the existing smoke."
        )
        print(f"::warning::{summary}")
    else:
        p50 = statistics.median(timings)
        p95 = sorted(timings)[math.ceil(0.95 * len(timings)) - 1]
        summary = (
            f"Decision latency, {len(timings)} warm POST calls: "
            f"p50 {p50:.1f} ms; p95 {p95:.1f} ms. Target p95 ≤ 500 ms."
        )
        print(summary)
        if p95 > 500:
            print(f"::warning::Decision p95 {p95:.1f} ms exceeds 500 ms")
    if path := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(path, "a") as output:
            output.write("\n" + summary + "\n")


if __name__ == "__main__":
    main()
