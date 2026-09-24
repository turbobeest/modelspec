#!/usr/bin/env python3
"""Check evidence rows and chart fixtures a pull request adds or changes.

``--base`` is a git ref, usually ``origin/main``. The comparison is against
the merge-base of HEAD and that ref. Evidence rows are keyed on benchmark,
model as evaluated, normalised source URL, configuration, and benchmark
version. A new key is added. The same key with a different score or unit is
changed. Removed rows are counted and do not affect the exit code.

Added and changed rows are classified against ``benchmarks/_charts/*.yaml``.
A fixture is the one whose ``page_url`` equals the row's ``source_url`` after
``norm_url``. Agreement uses the chart checker's same-source comparison:
printed precision, unit, headline metric, and sibling configurations.

Exit 1 when any finding blocks. Exit 0 when the only findings are warnings
or informational, and when nothing relevant changed. Exit 2 when the base
cannot be resolved or git cannot be run. The message is on stderr.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.parse
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from schema.card import BenchmarkEvidence, ModelCard  # noqa: E402
from scripts.chart_check import (  # noqa: E402
    _explicit_dispute,
    _fmt,
    _hit,
    _metric_key,
    _reading_disputes,
    _resolution_block,
    _resolution_problems,
    _same_unit,
    _unresolved_bar,
    load_fixture,
    norm_url,
)

OUTCOMES = (
    "verified",
    "mismatch",
    "disputed",
    "no_bar",
    "no_fixture_dataset",
    "no_fixture",
)
LEVEL = {
    "verified": "ok",
    "mismatch": "blocking",
    "disputed": "blocking",
    "no_bar": "warning",
    "no_fixture_dataset": "info",
    "no_fixture": "warning, for now",
}
BLOCKING_OUTCOMES = {"mismatch", "disputed"}
WARNING_OUTCOMES = {"no_bar", "no_fixture"}
DATA_SUFFIXES = (".json", ".yaml", ".yml", ".csv", ".zip", ".parquet", ".tsv")
NOTHING = "nothing to check"


class UsageError(Exception):
    """A git or invocation failure. The process exits 2."""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check evidence rows and chart fixtures changed in a pull request."
    )
    parser.add_argument(
        "--base",
        required=True,
        help="Git ref to compare, usually origin/main. Uses the merge-base with HEAD.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root. Defaults to this checkout.",
    )
    parser.add_argument("--json", type=Path, default=None, help="Also write the JSON report here.")
    args = parser.parse_args(argv)
    root = (args.root or REPO_ROOT).resolve()
    try:
        code, markdown, report = check(root, args.base)
    except UsageError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    sys.stdout.write(markdown)
    if args.json is not None and report is not None:
        try:
            write_json(args.json, report)
        except OSError as exc:
            print(f"cannot write {args.json}: {exc}", file=sys.stderr)
            return 2
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        try:
            with open(summary, "a", encoding="utf-8") as handle:
                handle.write(markdown)
        except OSError as exc:
            print(f"cannot append {summary}: {exc}", file=sys.stderr)
            return 2
    return code


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check(root: Path, base_ref: str) -> tuple[int, str, dict[str, Any]]:
    if not root.is_dir():
        raise UsageError(f"not a directory: {root}")
    sha = merge_base(root, base_ref)
    card_changes, removed_cards, fixture_paths = changed_paths(root, sha)
    findings: list[dict[str, str]] = []
    fixtures = load_changed_and_rest(root, fixture_paths, findings)
    by_page: dict[str, list[dict[str, Any]]] = {}
    for fixture in fixtures:
        page = norm_url(str(fixture.get("page_url") or ""))
        by_page.setdefault(page, []).append(fixture)

    rows: list[dict[str, Any]] = []
    removed_rows: list[dict[str, Any]] = []
    for old, new in card_changes:
        checked, gone = diff_card(root, sha, old, new, by_page, findings)
        rows.extend(checked)
        removed_rows.extend(gone)
    for path in removed_cards:
        removed_rows.extend(removed_card_rows(root, sha, path, findings))

    for fixture in fixtures:
        rel = _rel(root, fixture)
        if rel in fixture_paths:
            findings.extend(judge_fixture(fixture, rel))

    rows.sort(
        key=lambda item: (item["card"], item["benchmark_id"], item["source_url"], item["outcome"])
    )
    findings.sort(key=lambda item: (item["file"], item["chart"], item["problem"]))
    counts = {name: 0 for name in OUTCOMES}
    for row in rows:
        counts[row["outcome"]] = counts.get(row["outcome"], 0) + 1
    blocking = sum(1 for row in rows if row["outcome"] in BLOCKING_OUTCOMES)
    blocking += sum(1 for item in findings if item["level"] == "blocking")
    warnings = sum(1 for row in rows if row["outcome"] in WARNING_OUTCOMES)
    report = {
        "base": sha,
        "requested_base": base_ref,
        "nothing_to_check": False,
        "counts": counts,
        "rows": rows,
        "removed_rows": removed_rows,
        "findings": findings,
        "fixture_files": sorted(fixture_paths),
        "blocking": blocking,
        "warnings": warnings,
    }
    relevant = bool(rows or fixture_paths or findings)
    if not relevant:
        report["nothing_to_check"] = True
        return 0, NOTHING + "\n", report
    code = 1 if blocking else 0
    return code, render_markdown(report), report


def merge_base(root: Path, base_ref: str) -> str:
    proc = git(root, "merge-base", "HEAD", base_ref)
    if proc.returncode != 0 or not proc.stdout.strip():
        detail = proc.stderr.strip() or proc.stdout.strip() or "git merge-base failed"
        raise UsageError(f"cannot resolve base {base_ref}: {detail}")
    return proc.stdout.strip().splitlines()[-1].strip()


def changed_paths(
    root: Path, sha: str
) -> tuple[list[tuple[str | None, str | None]], list[str], set[str]]:
    proc = git(
        root,
        "diff",
        "--name-status",
        "--find-renames",
        sha,
        "HEAD",
        "--",
        "models",
        "benchmarks/_charts",
    )
    if proc.returncode != 0:
        detail = proc.stderr.strip() or "git diff failed"
        raise UsageError(detail)
    cards: list[tuple[str | None, str | None]] = []
    removed_cards: list[str] = []
    fixtures: set[str] = set()
    for line in proc.stdout.splitlines():
        parsed = _split_status(line)
        if parsed is None:
            continue
        status, old, new = parsed
        head = new or old or ""
        if _is_card_path(head) or _is_card_path(old or ""):
            if status.startswith("D"):
                if old:
                    removed_cards.append(old)
            else:
                cards.append((old, new))
        if new and _is_fixture_path(new) and not status.startswith("D"):
            fixtures.add(new)
    return cards, removed_cards, fixtures


def _split_status(line: str) -> tuple[str, str | None, str | None] | None:
    parts = line.split("\t")
    if len(parts) < 2 or not parts[0]:
        return None
    status = parts[0]
    if status.startswith(("R", "C")):
        if len(parts) < 3:
            return None
        return status, parts[1], parts[2]
    if status.startswith("D"):
        return status, parts[1], None
    if status.startswith("A"):
        return status, None, parts[1]
    return status, parts[1], parts[1]


def _is_card_path(path: str) -> bool:
    return path.startswith("models/") and path.endswith(".md")


def _is_fixture_path(path: str) -> bool:
    return path.startswith("benchmarks/_charts/") and path.endswith(".yaml")


def load_changed_and_rest(
    root: Path, changed: set[str], findings: list[dict[str, str]]
) -> list[dict[str, Any]]:
    directory = root / "benchmarks" / "_charts"
    if not directory.is_dir():
        return []
    loaded = []
    for path in sorted(directory.glob("*.yaml")):
        rel = path.resolve().relative_to(root.resolve()).as_posix()
        try:
            loaded.append(load_fixture(path))
        except (OSError, ValueError, yaml.YAMLError) as exc:
            if rel in changed:
                findings.append(
                    {
                        "file": rel,
                        "chart": "",
                        "problem": f"could not read fixture: {exc}",
                        "level": "blocking",
                    }
                )
            else:
                raise UsageError(f"{rel}: {exc}") from exc
    return loaded


def diff_card(
    root: Path,
    sha: str,
    old: str | None,
    new: str | None,
    by_page: dict[str, list[dict[str, Any]]],
    findings: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    path = new or old or ""
    base_text = git_show(root, sha, old) if old else None
    head_text = git_show(root, "HEAD", new) if new else None
    base_id, base_rows, base_error = parsed_card(base_text)
    head_id, head_rows, head_error = parsed_card(head_text)
    if head_error:
        findings.append(
            {
                "file": path,
                "chart": "",
                "problem": f"could not parse card: {head_error}",
                "level": "blocking",
            }
        )
        return [], []
    if base_error:
        base_rows = {}
    model_id = head_id or base_id or ""
    found: list[dict[str, Any]] = []
    for key, row in head_rows.items():
        previous = base_rows.get(key)
        if previous is None:
            change = "added"
        elif previous.score != row.score or previous.unit != row.unit:
            change = "changed"
        else:
            continue
        outcome, chart = classify_row(row, model_id, by_page)
        found.append(row_record(path, model_id, row, change, outcome, chart, previous))
    removed = [
        removed_record(path, row) for key, row in base_rows.items() if key not in head_rows
    ]
    return found, removed


def removed_card_rows(
    root: Path, sha: str, path: str, findings: list[dict[str, str]]
) -> list[dict[str, Any]]:
    text = git_show(root, sha, path)
    _model_id, rows, error = parsed_card(text)
    if error:
        findings.append(
            {
                "file": path,
                "chart": "",
                "problem": f"could not parse card: {error}",
                "level": "blocking",
            }
        )
        return []
    return [removed_record(path, row) for row in rows.values()]


def parsed_card(
    text: str | None,
) -> tuple[str | None, dict[tuple[str, str, str, str, str], BenchmarkEvidence], str | None]:
    if text is None:
        return None, {}, None
    try:
        card = ModelCard.from_yaml_string(text)
    except Exception as exc:
        if _looks_like_card(text):
            message = str(exc).strip().splitlines()[0][:500]
            return None, {}, message
        return None, {}, None
    indexed: dict[tuple[str, str, str, str, str], BenchmarkEvidence] = {}
    for row in card.benchmarks.evidence:
        indexed[row_key(row)] = row
    return card.identity.model_id, indexed, None


def _looks_like_card(text: str) -> bool:
    return "model_id:" in text[:4000]


def row_key(row: BenchmarkEvidence) -> tuple[str, str, str, str, str]:
    return (
        row.benchmark_id,
        row.model_id_as_evaluated,
        norm_url(row.source_url),
        row.configuration,
        row.benchmark_version,
    )


def classify_row(
    row: BenchmarkEvidence,
    card_model_id: str,
    by_page: dict[str, list[dict[str, Any]]],
) -> tuple[str, dict[str, Any] | None]:
    fixtures = by_page.get(norm_url(row.source_url))
    if not fixtures:
        if machine_readable(row.source_url):
            return "no_fixture_dataset", None
        return "no_fixture", None
    clean: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    unsettled: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    for fixture in fixtures:
        for chart in fixture.get("charts") or []:
            if not isinstance(chart, dict):
                continue
            for bar in chart.get("bars") or []:
                if not isinstance(bar, dict):
                    continue
                if not _same_model(bar, card_model_id, row.model_id_as_evaluated):
                    continue
                if not _same_benchmark(bar, row.benchmark_id):
                    continue
                if _metric_key(bar):
                    continue
                item = (fixture, chart, bar)
                if _unsettled(chart, bar):
                    unsettled.append(item)
                elif bar.get("printed"):
                    clean.append(item)
    if not clean and not unsettled:
        return "no_bar", None
    held = _held_row(row)
    agreed = next((item for item in clean if _agrees(item[2], held)), None)
    if agreed is not None:
        return "verified", _describe(agreed)
    disputed_hit = next((item for item in unsettled if _agrees(item[2], held)), None)
    if disputed_hit is not None:
        return "disputed", _describe(disputed_hit)
    if clean:
        return "mismatch", _describe(_closest(clean, row.score))
    return "disputed", _describe(unsettled[0])


def _same_model(bar: dict[str, Any], card_model_id: str, evaluated: str) -> bool:
    raw = bar.get("model_id")
    if not raw:
        return False
    bar_model = str(raw)
    if card_model_id and bar_model == card_model_id:
        return True
    return bool(evaluated) and bar_model == evaluated


def _same_benchmark(bar: dict[str, Any], benchmark_id: str) -> bool:
    raw = bar.get("benchmark_id")
    if not raw:
        return False
    return str(raw) == benchmark_id


def _unsettled(chart: dict[str, Any], bar: dict[str, Any]) -> bool:
    """A disputed bar, or a resolution the checker does not accept."""
    if _unresolved_bar(bar):
        return True
    if _resolution_block(bar) is not None:
        return False
    key = (str(bar.get("model_as_labelled") or ""), str(bar.get("benchmark_id") or ""))
    return key in _reading_disputes(chart)


def _held_row(row: BenchmarkEvidence) -> dict[str, Any]:
    return {
        "score": row.score,
        "unit": row.unit,
        "source_url": row.source_url,
        "configuration": row.configuration,
    }


def _agrees(bar: dict[str, Any], held: dict[str, Any]) -> bool:
    try:
        float(bar["score"])
        float(held["score"])
    except (KeyError, TypeError, ValueError):
        return False
    same = _same_unit([held], bar.get("unit"))
    return bool(same) and _hit(bar, same) is not None


def _closest(
    items: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]], score: float
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    def distance(item: tuple[dict[str, Any], dict[str, Any], dict[str, Any]]) -> float:
        try:
            return abs(float(item[2]["score"]) - float(score))
        except (KeyError, TypeError, ValueError):
            return float("inf")

    return min(items, key=distance)


def _describe(item: tuple[dict[str, Any], dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    fixture, chart, bar = item
    try:
        score: float | None = float(bar["score"])
    except (KeyError, TypeError, ValueError):
        score = None
    return {
        "chart_score": score,
        "chart_unit": bar.get("unit") or "",
        "chart_file": fixture.get("_path") or "",
        "chart_title": chart.get("title") or "",
    }


def machine_readable(url: str) -> bool:
    """True when MODEL-111 layer 2 verifies this source without a chart fixture.

    That is a ``huggingface.co/datasets/`` path, a file name ending in a data
    suffix, or a GitHub raw file with one of those suffixes.
    """
    parsed = urllib.parse.urlparse(url.strip())
    host = parsed.netloc.casefold()
    if host.startswith("www."):
        host = host[4:]
    parts = [part for part in (parsed.path or "").split("/") if part]
    if host == "huggingface.co" and parts and parts[0].casefold() == "datasets":
        return True
    if _github_raw(host, parts) and _data_filename(parts):
        return True
    return _data_filename(parts)


def _github_raw(host: str, parts: list[str]) -> bool:
    if host == "raw.githubusercontent.com":
        return True
    return host == "github.com" and "raw" in (part.casefold() for part in parts)


def _data_filename(parts: list[str]) -> bool:
    if not parts:
        return False
    name = parts[-1].casefold()
    return any(name.endswith(suffix) for suffix in DATA_SUFFIXES)


def judge_fixture(fixture: dict[str, Any], rel: str) -> list[dict[str, str]]:
    # An unchanged fixture is not passed here, so an old single-read chart
    # does not block a pull request that leaves the file alone.
    found = []
    for chart in fixture.get("charts") or []:
        if not isinstance(chart, dict):
            continue
        title = str(chart.get("title") or "(untitled)")
        bars = [bar for bar in (chart.get("bars") or []) if isinstance(bar, dict)]
        if bars and not _two_readers(chart):
            found.append(
                {
                    "file": rel,
                    "chart": title,
                    "problem": "fewer than two distinct readers and no single_read_reason",
                    "level": "blocking",
                }
            )
        for bar in bars:
            label = str(bar.get("model_as_labelled") or "?")
            bench = str(bar.get("benchmark_id") or bar.get("benchmark_as_labelled") or "?")
            if _explicit_dispute(bar) or _reading_dispute(chart, bar):
                found.append(
                    {
                        "file": rel,
                        "chart": title,
                        "problem": f"disputed bar {label} {bench}",
                        "level": "blocking",
                    }
                )
            for problem in _resolution_problems(bar):
                found.append(
                    {
                        "file": rel,
                        "chart": title,
                        "problem": f"{label} {bench}: {problem}",
                        "level": "blocking",
                    }
                )
    return found


def _two_readers(chart: dict[str, Any]) -> bool:
    if str(chart.get("single_read_reason") or "").strip():
        return True
    readers = set()
    for reading in chart.get("readings") or []:
        if isinstance(reading, dict):
            name = str(reading.get("reader") or "").strip()
            if name:
                readers.add(name)
    return len(readers) >= 2


def _reading_dispute(chart: dict[str, Any], bar: dict[str, Any]) -> bool:
    if _resolution_block(bar) is not None:
        return False
    key = (str(bar.get("model_as_labelled") or ""), str(bar.get("benchmark_id") or ""))
    return key in _reading_disputes(chart)


def row_record(
    path: str,
    model_id: str,
    row: BenchmarkEvidence,
    change: str,
    outcome: str,
    chart: dict[str, Any] | None,
    previous: BenchmarkEvidence | None,
) -> dict[str, Any]:
    chart = chart or {}
    return {
        "change": change,
        "outcome": outcome,
        "level": LEVEL[outcome],
        "card": path,
        "model_id": model_id,
        "benchmark_id": row.benchmark_id,
        "model": row.model_id_as_evaluated,
        "source_url": row.source_url,
        "configuration": row.configuration,
        "benchmark_version": row.benchmark_version,
        "score": row.score,
        "unit": row.unit,
        "previous_score": None if previous is None else previous.score,
        "previous_unit": None if previous is None else previous.unit,
        "chart_score": chart.get("chart_score"),
        "chart_unit": chart.get("chart_unit"),
        "chart_file": _display_chart_file(chart.get("chart_file") or ""),
        "chart_title": chart.get("chart_title") or "",
    }


def removed_record(path: str, row: BenchmarkEvidence) -> dict[str, Any]:
    return {
        "card": path,
        "benchmark_id": row.benchmark_id,
        "model": row.model_id_as_evaluated,
        "source_url": row.source_url,
        "configuration": row.configuration,
        "benchmark_version": row.benchmark_version,
        "score": row.score,
        "unit": row.unit,
    }


def _display_chart_file(path: str) -> str:
    if not path:
        return ""
    marker = "benchmarks/_charts/"
    if marker in path:
        return marker + path.rsplit(marker, 1)[1]
    return Path(path).name


def render_markdown(report: dict[str, Any]) -> str:
    added = sum(1 for row in report["rows"] if row["change"] == "added")
    changed = sum(1 for row in report["rows"] if row["change"] == "changed")
    removed = len(report["removed_rows"])
    lines = [
        "## Evidence against release charts",
        "",
        f"Base `{report['base']}`. Added {added}, changed {changed}, removed {removed}.",
        "",
        "| Outcome | Count | Level |",
        "| --- | ---: | --- |",
    ]
    for name in OUTCOMES:
        lines.append(f"| {name} | {report['counts'].get(name, 0)} | {LEVEL[name]} |")
    lines.append("")
    shown = BLOCKING_OUTCOMES | WARNING_OUTCOMES
    visible = [row for row in report["rows"] if row["outcome"] in shown]
    if visible:
        lines.extend(
            [
                "| Change | Outcome | Card | Benchmark | Model | Source "
                "| Card value | Chart value |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for row in visible:
            lines.append(
                "| "
                + " | ".join(
                    [
                        _cell(row["change"]),
                        _cell(row["outcome"]),
                        _cell(row["card"]),
                        _cell(row["benchmark_id"]),
                        _cell(row["model"]),
                        _cell(row["source_url"]),
                        _cell(_value(row["score"], row["unit"])),
                        _cell(_value(row.get("chart_score"), row.get("chart_unit") or "")),
                    ]
                )
                + " |"
            )
    else:
        lines.append("No blocking or warning rows.")
    if report["fixture_files"]:
        lines.extend(["", f"Fixture files checked: {len(report['fixture_files'])}."])
    if report["findings"]:
        lines.extend(
            [
                "",
                "| File | Chart | Problem |",
                "| --- | --- | --- |",
            ]
        )
        for item in report["findings"]:
            lines.append(
                "| "
                + " | ".join([_cell(item["file"]), _cell(item["chart"]), _cell(item["problem"])])
                + " |"
            )
    lines.append("")
    return "\n".join(lines)


def _value(score: Any, unit: str) -> str:
    if score is None:
        return ""
    text = _fmt(score)
    if unit:
        return f"{text} {unit}"
    return text


def _cell(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def _rel(root: Path, fixture: dict[str, Any]) -> str:
    return Path(str(fixture.get("_path") or "")).resolve().relative_to(root.resolve()).as_posix()


def git_show(root: Path, rev: str, path: str) -> str | None:
    proc = git(root, "show", f"{rev}:{path}")
    if proc.returncode != 0:
        return None
    return proc.stdout


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        raise UsageError(f"git failed: {exc}") from exc


if __name__ == "__main__":
    raise SystemExit(main())
