"""Write the `alert` issue body for a failing accuracy nightly (MODEL-335).

The orchestrator's heartbeat reads open issues labelled `alert`. A red run in
Actions alone notifies no one, and the coverage report's bundled breach issue
(MODEL-215) stays open for unrelated reasons. The workflow opens one `alert`
issue for a failing nightly, comments on it each further failing night, and
closes it on the next green run. This module only writes the text. The
workflow makes the `gh` calls.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

TITLE = "Accuracy nightly failed"
LABEL = "alert"


def _failing_values(layer: Mapping[str, Any]) -> list[str]:
    details = layer.get("details")
    sample = details.get("sample", []) if isinstance(details, Mapping) else []
    return [
        f"- `{row['target']}`: {row['outcome']}"
        + (f" ({row['reason']})" if row.get("reason") else "")
        + "".join(f"\n  - {url}" for url in row.get("source_urls", []))
        for row in sample
        if row.get("outcome") in ("mismatch", "unreachable")
    ]


def body(report: Mapping[str, Any] | None, run_url: str) -> str:
    """The issue text: which gating layers failed and which values did not verify.

    A missing report (the script crashed before writing one) is still an alert.
    """
    if report is None:
        return f"The nightly wrote no report: it failed before or during the run.\n\nRun: {run_url}\n"
    lines = [
        f"Snapshot `{report.get('snapshot')}`, generated {report.get('generated_at')}.",
        "",
        "| Layer | Status | Gate | Summary |",
        "| --- | --- | --- | --- |",
    ]
    failing: list[str] = []
    for layer in report.get("layers", []):
        lines.append(
            f"| {layer['name']} | {layer['status']} | {'yes' if layer['gating'] else 'no'} "
            f"| {layer['summary']} |"
        )
        if layer["gating"] and layer["status"] != "pass":
            failing.extend(_failing_values(layer))
    if failing:
        lines += ["", "Values that did not verify:", "", *failing]
    lines += ["", f"Run: {run_url}"]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--run-url", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    report = json.loads(args.report.read_text(encoding="utf-8")) if args.report.exists() else None
    args.output.write_text(body(report, args.run_url), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
