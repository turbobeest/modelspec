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
printed precision, unit, headline metric, and sibling configurations. The
outcome is ``verified`` when the agreeing bar names two or more readers in
``confirmed_by``. Fewer than two is ``verified_single_read``, a warning.

A fixture the pull request adds or changes is judged per bar. An added or
changed bar needs two distinct ``confirmed_by`` readers, or a non-empty
``single_read_reason`` on the bar or on its chart. A removed bar is
informational. ``disputed`` and an invalid ``resolution`` still block.

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
from collections.abc import Callable
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
    "verified_single_read",
    "mismatch",
    "disputed",
    "no_bar",
    "no_fixture_dataset",
    "no_fixture",
)
LEVEL = {
    "verified": "ok",
    "verified_single_read": "warning",
    "mismatch": "blocking",
    "disputed": "blocking",
    "no_bar": "warning",
    "no_fixture_dataset": "info",
    "no_fixture": "warning, for now",
}
BLOCKING_OUTCOMES = {"mismatch", "disputed"}
WARNING_OUTCOMES = {"verified_single_read", "no_bar", "no_fixture"}
DATA_SUFFIXES = (".json", ".yaml", ".yml", ".csv", ".zip", ".parquet", ".tsv")
NOTHING = "nothing to check"
READER_ROW_LIMIT = 50
KeyFunc = Callable[[dict[str, Any]], Any]


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
    card_changes, removed_cards, fixture_changes = changed_paths(root, sha)
    findings: list[dict[str, str]] = []
    changed_heads = {head for head, _base in fixture_changes if head}
    fixtures = load_changed_and_rest(root, changed_heads, findings)
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

    by_rel = {_rel(root, fixture): fixture for fixture in fixtures}
    for head_path, base_path in fixture_changes:
        rel = head_path or base_path
        base_data, base_error = _base_fixture(root, sha, base_path or None)
        if base_error:
            findings.append(_finding(rel, "", base_error, "blocking", "fixture"))
        if head_path:
            fixture = by_rel.get(head_path)
            if fixture is None:
                continue
        else:
            fixture = {"charts": []}
        findings.extend(judge_fixture(fixture, rel, base_data))

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
        "fixture_files": sorted({head or base for head, base in fixture_changes}),
        "blocking": blocking,
        "warnings": warnings,
    }
    relevant = bool(rows or fixture_changes or findings)
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
) -> tuple[list[tuple[str | None, str | None]], list[str], list[tuple[str, str]]]:
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
    # (head path, base path). An empty string means that side has no file.
    fixtures: list[tuple[str, str]] = []
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
        if status.startswith("D"):
            if old and _is_fixture_path(old):
                fixtures.append(("", old))
        elif new and _is_fixture_path(new):
            fixtures.append((new, old or ""))
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
    agreed = [item for item in clean if _agrees(item[2], held)]
    if agreed:
        confirmed = [item for item in agreed if _distinct_confirmers(item[2]) >= 2]
        if confirmed:
            return "verified", _describe(confirmed[0])
        return "verified_single_read", _describe(agreed[0])
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


def judge_fixture(
    fixture: dict[str, Any], rel: str, base: dict[str, Any] | None
) -> list[dict[str, str]]:
    # An unchanged fixture is not passed here. An unchanged bar inside a
    # changed fixture is not judged for readers either.
    found: list[dict[str, str]] = []
    chart_pairs = _pair_by_key(_charts(base), _charts(fixture), _chart_key)
    for base_chart, head_chart in chart_pairs:
        if head_chart is None:
            title = _chart_label(base_chart or {})
            for bar in _bars(base_chart):
                found.append(_removed_finding(rel, title, bar))
            continue
        title = _chart_label(head_chart)
        for base_bar, head_bar in _pair_by_key(_bars(base_chart), _bars(head_chart), _bar_key):
            if head_bar is None:
                found.append(_removed_finding(rel, title, base_bar or {}))
                continue
            if base_bar is None or _bar_changed(base_bar, head_bar):
                if _reader_gap(head_chart, head_bar):
                    found.append(
                        _finding(
                            rel,
                            title,
                            f"{_bar_name(head_bar)}: fewer than two distinct readers "
                            "and no single_read_reason",
                            "blocking",
                            "readers",
                        )
                    )
            found.extend(_dispute_findings(rel, title, head_chart, head_bar))
    return found


def _base_fixture(
    root: Path, sha: str, path: str | None
) -> tuple[dict[str, Any] | None, str | None]:
    if not path:
        return None, None
    text = git_show(root, sha, path)
    if text is None:
        return None, "could not read base fixture"
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        return None, f"could not read base fixture: {exc}"
    if not isinstance(data, dict):
        return None, "could not read base fixture"
    return data, None


def _charts(fixture: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not fixture:
        return []
    return [chart for chart in (fixture.get("charts") or []) if isinstance(chart, dict)]


def _bars(chart: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not chart:
        return []
    return [bar for bar in (chart.get("bars") or []) if isinstance(bar, dict)]


def _chart_key(chart: dict[str, Any]) -> str:
    return str(chart.get("title") or "")


def _chart_label(chart: dict[str, Any]) -> str:
    return str(chart.get("title") or "(untitled)")


def _bar_key(bar: dict[str, Any]) -> tuple[str, str, str, str]:
    benchmark = bar.get("benchmark_id")
    if benchmark is None or str(benchmark).strip() == "":
        benchmark = bar.get("benchmark_as_labelled")
    return (
        str(bar.get("model_as_labelled") or ""),
        str(benchmark or ""),
        str(bar.get("metric") or ""),
        str(bar.get("configuration") or ""),
    )


def _pair_by_key(
    base_items: list[dict[str, Any]],
    head_items: list[dict[str, Any]],
    key_fn: KeyFunc,
) -> list[tuple[dict[str, Any] | None, dict[str, Any] | None]]:
    """Pair items that share a unique key. A repeated key pairs in list order."""
    base_groups = _group(base_items, key_fn)
    head_groups = _group(head_items, key_fn)
    colliding = {
        key
        for key, group in base_groups.items()
        if len(group) > 1 or len(head_groups.get(key, [])) > 1
    }
    colliding.update(key for key, group in head_groups.items() if len(group) > 1)
    pairs: list[tuple[dict[str, Any] | None, dict[str, Any] | None]] = []
    for key, head_group in head_groups.items():
        if key in colliding:
            continue
        base_group = base_groups.get(key, [])
        if base_group:
            pairs.append((base_group[0], head_group[0]))
        else:
            pairs.append((None, head_group[0]))
    for key, base_group in base_groups.items():
        if key in colliding or key in head_groups:
            continue
        pairs.append((base_group[0], None))
    seen: set[Any] = set()
    for item in head_items + base_items:
        key = key_fn(item)
        if key not in colliding or key in seen:
            continue
        seen.add(key)
        base_group = base_groups.get(key, [])
        head_group = head_groups.get(key, [])
        width = max(len(base_group), len(head_group))
        for index in range(width):
            base_item = base_group[index] if index < len(base_group) else None
            head_item = head_group[index] if index < len(head_group) else None
            pairs.append((base_item, head_item))
    return pairs


def _group(items: list[dict[str, Any]], key_fn: KeyFunc) -> dict[Any, list[dict[str, Any]]]:
    groups: dict[Any, list[dict[str, Any]]] = {}
    for item in items:
        groups.setdefault(key_fn(item), []).append(item)
    return groups


def _bar_changed(base: dict[str, Any], head: dict[str, Any]) -> bool:
    return _bar_signature(base) != _bar_signature(head)


def _bar_signature(bar: dict[str, Any]) -> tuple[Any, ...]:
    return (
        _score_value(bar.get("score")),
        _field_text(bar.get("unit")),
        _field_text(bar.get("model_as_labelled")),
        _field_text(bar.get("benchmark_as_labelled")),
        _field_text(bar.get("model_id")),
        _field_text(bar.get("benchmark_id")),
        _field_text(bar.get("metric")),
        _field_text(bar.get("configuration")),
        _field_text(bar.get("role")),
        _confirmed_names(bar),
    )


def _score_value(score: Any) -> tuple[str, float | str]:
    if isinstance(score, bool) or score is None:
        return ("", "")
    if isinstance(score, (int, float)):
        return ("n", float(score))
    return ("s", str(score))


def _field_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _confirmed_names(bar: dict[str, Any]) -> tuple[str, ...]:
    raw = bar.get("confirmed_by")
    if raw is None:
        return ()
    if not isinstance(raw, list):
        return ("",)
    names = []
    for item in raw:
        if isinstance(item, str) and item.strip():
            names.append(item.strip())
        else:
            names.append("")
    return tuple(names)


def _distinct_confirmers(bar: dict[str, Any]) -> int:
    return len({name for name in _confirmed_names(bar) if name})


def _reader_gap(chart: dict[str, Any], bar: dict[str, Any]) -> bool:
    if _distinct_confirmers(bar) >= 2:
        return False
    if str(bar.get("single_read_reason") or "").strip():
        return False
    if str(chart.get("single_read_reason") or "").strip():
        return False
    return True


def _bar_name(bar: dict[str, Any]) -> str:
    label = str(bar.get("model_as_labelled") or "?")
    bench = str(bar.get("benchmark_id") or bar.get("benchmark_as_labelled") or "?")
    metric = str(bar.get("metric") or "").strip()
    config = " ".join(str(bar.get("configuration") or "").split())
    name = f"{label} {bench}"
    if metric:
        name = f"{name} {metric}"
    if config:
        if len(config) > 80:
            config = config[:77] + "..."
        name = f"{name} ({config})"
    return name


def _removed_finding(file: str, chart: str, bar: dict[str, Any]) -> dict[str, str]:
    return _finding(file, chart, f"removed bar {_bar_name(bar)}", "info", "removed")


def _dispute_findings(
    file: str, chart_title: str, chart: dict[str, Any], bar: dict[str, Any]
) -> list[dict[str, str]]:
    found = []
    label = str(bar.get("model_as_labelled") or "?")
    bench = str(bar.get("benchmark_id") or bar.get("benchmark_as_labelled") or "?")
    if _explicit_dispute(bar) or _reading_dispute(chart, bar):
        found.append(
            _finding(file, chart_title, f"disputed bar {label} {bench}", "blocking", "disputed")
        )
    for problem in _resolution_problems(bar):
        found.append(
            _finding(file, chart_title, f"{label} {bench}: {problem}", "blocking", "resolution")
        )
    return found


def _finding(file: str, chart: str, problem: str, level: str, kind: str) -> dict[str, str]:
    return {"file": file, "chart": chart, "problem": problem, "level": level, "kind": kind}


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
    findings = report["findings"]
    reader = [item for item in findings if item.get("kind") == "readers"]
    removed = [item for item in findings if item.get("kind") == "removed"]
    other = [item for item in findings if item.get("kind") not in {"readers", "removed"}]
    if reader or removed:
        lines.extend(_render_bar_findings(reader, removed))
    if other:
        lines.extend(["", *_render_finding_table(other)])
    lines.append("")
    return "\n".join(lines)


def _render_bar_findings(reader: list[dict[str, str]], removed: list[dict[str, str]]) -> list[str]:
    reader_counts = _chart_counts(reader)
    removed_counts = _chart_counts(removed)
    lines = [
        "",
        "### Changed bars",
        "",
        f"Blocking bars: {len(reader)}. Removed bars: {len(removed)}.",
        "",
        "| Fixture | Chart | Blocking bars | Removed bars |",
        "| --- | --- | ---: | ---: |",
    ]
    for key in sorted(set(reader_counts) | set(removed_counts)):
        file, chart = key
        lines.append(
            "| "
            + " | ".join(
                [
                    _cell(file),
                    _cell(chart),
                    str(reader_counts.get(key, 0)),
                    str(removed_counts.get(key, 0)),
                ]
            )
            + " |"
        )
    lines.extend(_render_capped_rows(reader, "Blocking bars", READER_ROW_LIMIT))
    lines.extend(_render_capped_rows(removed, "Removed bars", READER_ROW_LIMIT))
    return lines


def _chart_counts(items: list[dict[str, str]]) -> dict[tuple[str, str], int]:
    counts: dict[tuple[str, str], int] = {}
    for item in items:
        key = (item["file"], item["chart"])
        counts[key] = counts.get(key, 0) + 1
    return counts


def _render_capped_rows(items: list[dict[str, str]], label: str, limit: int) -> list[str]:
    if not items:
        return []
    shown = items[:limit]
    lines = ["", f"{label}, {len(shown)} of {len(items)}.", "", *_render_finding_table(shown)]
    hidden = len(items) - limit
    if hidden > 0:
        name = label.lower()
        if hidden == 1:
            note = f"1 further {name[:-1]} is omitted."
        else:
            note = f"{hidden} further {name} are omitted."
        lines.extend(["", f"{note} The table above has the count for each chart."])
    return lines


def _render_finding_table(items: list[dict[str, str]]) -> list[str]:
    lines = ["| Fixture | Chart | Problem |", "| --- | --- | --- |"]
    for item in items:
        lines.append(
            "| "
            + " | ".join([_cell(item["file"]), _cell(item["chart"]), _cell(item["problem"])])
            + " |"
        )
    return lines


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
