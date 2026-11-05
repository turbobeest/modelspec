#!/usr/bin/env python3
"""Review an exported discovery issue list; contact GitHub only with --apply.

Dry-run is the default. Apply paces and caps every gh invocation, comments with
the decision reason, and closes noise or marks possible releases for review.
Pass a private catalogue explicitly to check for carded releases.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from release_signals.contract import ReleaseSignal, SignalError  # noqa: E402
from release_signals.watch import load_catalogue  # noqa: E402
from scripts.release_watch_filter import (  # noqa: E402
    canonical_release, card_identity, catalogue_identities, rejection_reason,
)

CLASSIFICATIONS = ("duplicate", "superseded", "real", "noise")
JSON_FENCE = re.compile(r"^```json[ \t]*\r?\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
SAMPLE_LIMIT = 5
DISCOVERY_LABEL = "release-discovery"
REVIEW_LABEL = "release-review"
OPEN_ISSUE_LIMIT = 1000


def _signal(body: str) -> ReleaseSignal:
    blocks = JSON_FENCE.findall(body)
    if len(blocks) != 1:
        raise SignalError("expected exactly one JSON signal block")
    try:
        value = json.loads(blocks[0])
    except json.JSONDecodeError as exc:
        raise SignalError("signal block is not valid JSON") from exc
    try:
        return ReleaseSignal.parse(value, discovered=True)
    except ValueError as exc:
        raise SignalError(str(exc)) from exc


def _read_issues(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError("issues input must be a JSON array")
    numbers: set[int] = set()
    for row in value:
        if not isinstance(row, dict):
            raise ValueError("each issue must be a JSON object")
        number = row.get("number")
        if type(number) is not int or number <= 0 or number in numbers:
            raise ValueError("issue numbers must be unique positive integers")
        numbers.add(number)
        for key in ("title", "url", "createdAt", "body"):
            if not isinstance(row.get(key), str):
                raise ValueError(f"issue #{number} must have a string {key}")
        try:
            created = datetime.fromisoformat(row["createdAt"].replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"issue #{number} has an invalid createdAt") from exc
        if created.tzinfo is None:
            raise ValueError(f"issue #{number} createdAt must have a UTC offset")
    return value


def triage(issues: list[dict[str, Any]], *, catalogue_root: Path | None = None) -> dict:
    carded: set[tuple[str, str]] = set()
    if catalogue_root is not None:
        if not (catalogue_root / "models").is_dir():
            raise ValueError("catalogue root must contain a models directory")
        catalogue = load_catalogue(catalogue_root)
        carded = catalogue_identities(catalogue)

    chosen: dict[tuple[str, str], int] = {}
    rows = []
    ordered = sorted(issues, key=lambda row: (
        datetime.fromisoformat(row["createdAt"].replace("Z", "+00:00")), row["number"],
    ))
    for issue in ordered:
        row = {key: issue[key] for key in ("number", "title", "url", "createdAt")}
        row.update(classification="real", reason="", canonical_id=None, duplicate_of=None)
        try:
            signal = _signal(issue["body"])
        except SignalError as exc:
            row["reason"] = f"Manual review: {exc}; retained as a possible release."
            rows.append(row)
            continue

        identity = card_identity(signal.provider, signal.model_name)
        row["canonical_id"] = ":".join(canonical_release(signal.provider, signal.model_name))
        rejected = rejection_reason(
            signal.provider, signal.model_name, source_url=signal.first_seen_url,
        )
        if rejected:
            row.update(classification="noise", reason=rejected)
        elif identity in chosen:
            row.update(
                classification="duplicate",
                reason="Another open issue represents the same canonical release.",
                duplicate_of=chosen[identity],
            )
        else:
            chosen[identity] = issue["number"]
            if identity in carded:
                row.update(
                    classification="superseded",
                    reason="An exact canonical release or alias is already carded.",
                )
            else:
                row["reason"] = "Distinct possible model release; keep for review."
        rows.append(row)

    for row in rows:
        category = row["classification"]
        row["decision"] = "relabel" if category == "real" else "close"
        row["rule"] = {
            "real": "manual-review" if row["canonical_id"] is None else "possible-release",
            "duplicate": "duplicate-release", "superseded": "already-carded",
            "noise": row["reason"],
        }[category]
    counted = Counter(row["classification"] for row in rows)
    return {
        "schema_version": 1,
        "dry_run": True,
        "catalogue_checked": catalogue_root is not None,
        "counts": {category: counted[category] for category in CLASSIFICATIONS},
        "issues": rows,
        "samples": {
            category: [
                row for row in rows if row["classification"] == category
            ][:SAMPLE_LIMIT]
            for category in CLASSIFICATIONS
        },
    }


def markdown(report: dict) -> str:
    dry_run = report["dry_run"]
    lines = [
        "# Release discovery triage: " + ("DRY RUN" if dry_run else "APPLY"),
        "",
        "No issues were closed or labeled. Review this report before applying any changes."
        if dry_run else "Apply results are recorded per issue below.",
        "",
        "| Classification | Count |",
        "| --- | ---: |",
        *[f"| {category} | {report['counts'][category]} |" for category in CLASSIFICATIONS],
        "",
        f"Catalogue checked: {'yes' if report['catalogue_checked'] else 'no'}.",
        "Superseded means an exact release or alias is already carded; newer versions "
        "do not supersede older ones automatically.",
    ]
    if not dry_run:
        applied = report["apply"]
        lines.extend([
            "", f"GitHub calls: {applied['calls_used']}/{applied['max_calls']}.",
            f"Call budget exhausted: {'yes' if applied['budget_exhausted'] else 'no'}.",
        ])
        if applied["error"]:
            lines.append(f"Apply stopped: {applied['error']}")
    lines.extend([
        "", "| Issue | Title | Decision | Classification | Rule / reason | Apply status |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    def cell(value: str) -> str:
        return " ".join(value.split()).replace("|", "\\|")

    for row in report["issues"]:
        detail = row["reason"]
        if row["duplicate_of"] is not None:
            detail += f" Keep #{row['duplicate_of']}."
        lines.append(
            f"| [#{row['number']}]({row['url']}) | {cell(row['title'])} | "
            f"{row['decision']} | {row['classification']} | {cell(row['rule'])}: "
            f"{cell(detail)} | {row.get('apply_status', 'dry-run')} |"
        )
    return "\n".join(lines) + "\n"


def apply(report: dict, issues: list[dict], *, repo: str, max_calls: int) -> None:
    """Apply a local plan with a fresh state check before each issue's writes."""
    if max_calls < 1:
        raise ValueError("--max-calls must be positive")
    report["dry_run"] = False
    result = {"calls_used": 0, "max_calls": max_calls, "budget_exhausted": False, "error": None}
    report["apply"] = result
    originals = {issue["number"]: issue for issue in issues}
    last_call: float | None = None
    review_label_ready = False
    verified: set[int] = set()
    changed: set[int] = set()

    class BudgetExhausted(Exception):
        pass

    def reserve(calls: int) -> None:
        if result["calls_used"] + calls > max_calls:
            raise BudgetExhausted

    def gh(*args: str) -> str:
        nonlocal last_call
        reserve(1)
        if last_call is not None:
            time.sleep(max(0.0, 1.0 - (time.monotonic() - last_call)))
        last_call = time.monotonic()
        result["calls_used"] += 1
        done = subprocess.run(
            ["gh", *args, "--repo", repo], capture_output=True, text=True,
            stdin=subprocess.DEVNULL, timeout=60, check=False,
        )
        if done.returncode:
            raise RuntimeError(f"gh {' '.join(args[:2])} failed: {done.stderr.strip()}")
        return done.stdout

    for row in report["issues"]:
        row["apply_status"] = "pending"
    if not report["issues"]:
        return
    try:
        opened = json.loads(gh(
            "issue", "list", "--label", DISCOVERY_LABEL, "--state", "open",
            "--limit", str(OPEN_ISSUE_LIMIT), "--json", "number,labels",
        ))
        if not isinstance(opened, list) or not all(
            isinstance(issue, dict) and type(issue.get("number")) is int
            and isinstance(issue.get("labels"), list)
            and all(isinstance(label, dict) and isinstance(label.get("name"), str)
                    for label in issue["labels"])
            for issue in opened
        ):
            raise ValueError("GitHub returned an invalid open discovery list")
        if len(opened) >= OPEN_ISSUE_LIMIT:
            raise ValueError("Open discovery listing reached its limit; no issues were changed")
        open_labels = {
            issue["number"]: {label["name"] for label in issue["labels"]} for issue in opened
        }
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
        result["error"] = str(exc)
        return

    for row in report["issues"]:
        number = str(row["number"])
        if row["number"] not in open_labels:
            row["apply_status"] = "skipped_not_open_discovery"
            continue
        if row["decision"] == "relabel" and REVIEW_LABEL in open_labels[row["number"]]:
            row["apply_status"] = "skipped_reviewed"
            continue
        try:
            state = json.loads(gh("issue", "view", number, "--json", "state,labels,comments,title,body"))
            if not isinstance(state, dict) or state.get("state") not in {"OPEN", "CLOSED"}:
                raise ValueError(f"issue #{number} returned an invalid state")
            if state["state"] == "CLOSED":
                row["apply_status"] = "skipped_closed"
                continue
            labels, comments = state.get("labels"), state.get("comments")
            if not isinstance(labels, list) or not all(
                isinstance(label, dict) and isinstance(label.get("name"), str) for label in labels
            ) or not isinstance(comments, list) or not all(
                isinstance(comment, dict) and isinstance(comment.get("body"), str) for comment in comments
            ):
                raise ValueError(f"issue #{number} returned invalid labels or comments")
            names = {label["name"] for label in labels}
            if DISCOVERY_LABEL not in names:
                row["apply_status"] = "skipped_label_removed"
                continue
            original = originals[row["number"]]
            if any(state.get(field) != original[field] for field in ("body", "title")):
                row["apply_status"] = "skipped_changed"
                changed.add(row["number"])
                continue
            verified.add(row["number"])
            if row["decision"] == "relabel" and REVIEW_LABEL in names:
                row["apply_status"] = "skipped_reviewed"
                continue
            anchor = row["duplicate_of"]
            if anchor is not None and anchor not in verified and anchor not in changed:
                anchor_state = json.loads(gh("issue", "view", str(anchor), "--json", "title,body"))
                if not isinstance(anchor_state, dict):
                    raise ValueError(f"issue #{anchor} returned an invalid duplicate anchor")
                if any(anchor_state.get(field) != originals[anchor][field] for field in ("body", "title")):
                    changed.add(anchor)
                else:
                    verified.add(anchor)
            if anchor in changed:
                row["apply_status"] = "skipped_changed_anchor"
                continue
            reason = " ".join(row["reason"].split())
            if row["duplicate_of"] is not None:
                reason += f" Keep #{row['duplicate_of']}."
            comment = f"Release discovery triage: {row['decision']} ({row['classification']}); {reason}"
            needs_comment = not any(item["body"] == comment for item in comments)
            writes = 1 + int(needs_comment)
            if row["decision"] == "relabel" and not review_label_ready:
                reserve(writes + 1)
                labels = json.loads(gh("label", "list", "--search", REVIEW_LABEL, "--limit", "100", "--json", "name"))
                if not isinstance(labels, list) or not all(
                    isinstance(label, dict) and isinstance(label.get("name"), str) for label in labels
                ):
                    raise ValueError("GitHub returned an invalid label list")
                if not any(label["name"] == REVIEW_LABEL for label in labels):
                    reserve(writes + 1)
                    gh("label", "create", REVIEW_LABEL, "--color", "FBCA04",
                       "--description", "Possible model release retained after discovery triage")
                review_label_ready = True
            reserve(writes)
            if needs_comment:
                gh("issue", "comment", number, "--body", comment)
            if row["decision"] == "close":
                gh("issue", "close", number, "--reason", "not planned")
                row["apply_status"] = "closed"
            else:
                gh("issue", "edit", number, "--add-label", REVIEW_LABEL)
                row["apply_status"] = "relabeled"
        except BudgetExhausted:
            result["budget_exhausted"] = True
            row["apply_status"] = "pending_budget"
            break
        except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
            result["error"] = str(exc)
            row["apply_status"] = "failed"
            break


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--issues", type=Path, required=True, help="Local gh issue list JSON export",
    )
    parser.add_argument("--catalogue-root", type=Path, help="Optional local private catalogue")
    parser.add_argument("--report", type=Path, help="Write the full JSON report")
    parser.add_argument("--summary", type=Path, help="Write counts and every decision as Markdown")
    parser.add_argument("--apply", action="store_true", help="Apply decisions to GitHub with one-second call spacing")
    parser.add_argument("--repo", default="turbobeest/modelspec", help="GitHub owner/repository for apply")
    parser.add_argument("--max-calls", type=int, default=10, help="Maximum total gh calls, including reads (default: 10)")
    args = parser.parse_args(argv)
    if args.max_calls < 1:
        parser.error("--max-calls must be positive")
    paths = [
        path.resolve() for path in (args.issues, args.report, args.summary) if path is not None
    ]
    if len(paths) != len(set(paths)):
        parser.error("--issues, --report and --summary must name different files")
    if args.catalogue_root is not None:
        catalogue_root = args.catalogue_root.resolve()
        if any(
            path.resolve().is_relative_to(catalogue_root)
            for path in (args.report, args.summary) if path is not None
        ):
            parser.error("reports must be outside the private catalogue")
    try:
        issues = _read_issues(args.issues)
        report = triage(issues, catalogue_root=args.catalogue_root)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if args.apply:
        for issue in issues:
            expected = f"https://github.com/{args.repo}/issues/{issue['number']}"
            if issue["url"].rstrip("/").casefold() != expected.casefold():
                parser.error(f"issue #{issue['number']} URL does not match --repo {args.repo}")
        apply(report, issues, repo=args.repo, max_calls=args.max_calls)
    summary = markdown(report)
    if args.report is not None:
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.summary is not None:
        args.summary.write_text(summary, encoding="utf-8")
    print(summary, end="")
    applied = report.get("apply", {})
    return 1 if applied.get("error") or applied.get("budget_exhausted") else 0


if __name__ == "__main__":
    raise SystemExit(main())
