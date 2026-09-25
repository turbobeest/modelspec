"""Run the non-gating MODEL-146 recall report against a decision snapshot."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Literal

import yaml

from decision.contract import Decision, Spec, parse_spec
from decision.engine import decide
from decision.filter import apply
from decision.optimise import EvidenceSelector
from decision.registry import Registry
from decision.registry import default as default_registry
from decision.resolve import resolve
from decision.snapshot import (
    CompletenessError,
    Gap,
    LoadedSnapshot,
    build_from_repo,
    load_snapshot,
    load_snapshot_bytes,
)

Verdict = Literal["pass", "partial", "fail"]
Cause = Literal["missing_data", "engine_behavior"]

ROOT = Path(__file__).resolve().parents[1]
RECALL = ROOT / "tests" / "recall"
NON_GATING = "This report does not gate CI; Jamie must approve the recall set first."
_CANNOT_SEPARATE = re.compile(
    r"no unique winner|not separate|does not separate|cannot separate|"
    r"no order (?:is )?established|no .* winner|refuse to name|do not name",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Finding:
    cause: Cause
    severity: Verdict
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"cause": self.cause, "severity": self.severity, "message": self.message}


@dataclass(frozen=True)
class QuestionResult:
    id: str
    question: str
    verdict: Verdict
    decision: Decision | None
    findings: tuple[Finding, ...]
    error: str | None = None


@dataclass(frozen=True)
class RunResult:
    snapshot_id: str
    markdown_path: Path
    json_path: Path
    questions: tuple[QuestionResult, ...]
    completeness_gaps: tuple[Gap, ...] = ()


def _load_yaml(path: Path) -> Mapping[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ValueError(f"{path}: expected a YAML mapping")
    return value


def _rows_by_id(path: Path) -> dict[str, Mapping[str, Any]]:
    raw = _load_yaml(path)
    rows = raw.get("questions")
    if not isinstance(rows, list):
        raise ValueError(f"{path}: questions must be a list")
    return {str(row["id"]): row for row in rows}


def _entry_id(entry: Mapping[str, Any]) -> str | None:
    value = entry.get("model_id") or entry.get("name")
    return str(value) if isinstance(value, str) and "/" in value else None


def _models(entries: Sequence[Mapping[str, Any]]) -> set[str]:
    return {model for entry in entries if (model := _entry_id(entry)) is not None}


def _model_ids(snapshot: LoadedSnapshot) -> set[str]:
    return {snapshot.model_of(candidate) for candidate in snapshot.candidates()}


def _decision_models(decision: Decision) -> tuple[list[str], set[str]]:
    results = [result.offering.model for result in decision.results]
    flagged = {row.model for row in decision.may_qualify}
    return results, flagged


def _models_with_fact(snapshot: LoadedSnapshot, facet: str, value: Any) -> set[str]:
    models = set()
    for candidate in snapshot.candidates():
        if snapshot.kind(candidate) != "model":
            continue
        fact = snapshot.fact(candidate, facet)
        if fact.state == "known" and fact.value == value:
            models.add(candidate)
    return models


def _rule_flag_models(entries: Sequence[Mapping[str, Any]], snapshot: LoadedSnapshot) -> set[str]:
    models: set[str] = set()
    for entry in entries:
        rule = str(entry.get("rule") or "").lower()
        if "class is speech-to-text" in rule:
            models.update(_models_with_fact(snapshot, "model.class", "transcriber"))
        elif "generator whose published context length was not read" in rule:
            for model in _models_with_fact(snapshot, "model.class", "text-generator"):
                if snapshot.fact(model, "model.context_window").state != "known":
                    models.add(model)
    return models


def _raw_value(decision: Decision, rank: int) -> tuple[str, float | None, str | None]:
    result = decision.results[rank - 1]
    if not result.contributions:
        return "objective", None, None
    contribution = result.contributions[0]
    return contribution.dimension, contribution.raw_value, contribution.unit


def _top_is_tied(decision: Decision) -> bool:
    if len(decision.results) < 2:
        return False
    first = _raw_value(decision, 1)
    second = _raw_value(decision, 2)
    return first[1] is not None and first == second


def _expects_no_separation(expected: Mapping[str, Any]) -> bool:
    acceptable = expected.get("acceptable") or []
    return any(entry.get("rule") for entry in acceptable) or bool(
        _CANNOT_SEPARATE.search(str(expected.get("notes") or ""))
    )


def _direct_objective_has_a_value(
    spec: Spec, snapshot: LoadedSnapshot, acceptable: set[str], registry: Registry
) -> bool:
    """Detect the current engine losing directness on benchmark-objective reads."""
    objective = spec.optimize
    facet = objective.max or objective.min
    if facet is None:
        return False
    qualifiers = objective.qualifiers.get(facet)
    if qualifiers is None or not qualifiers.direct:
        return False
    selector = EvidenceSelector.from_qualifiers(facet, qualifiers)
    resolved = resolve(spec, facets=registry.facet)
    feasible = apply(resolved, snapshot).feasible
    for candidate in feasible:
        if snapshot.model_of(candidate) not in acceptable:
            continue
        matches = snapshot.evidence(
            candidate,
            facet,
            measured_by=None if selector.measured_by is None else set(selector.measured_by),
            effort=selector.effort,
            harness=selector.harness,
            after=selector.after,
        )
        if len(matches) == 1:
            return True
    return False


def _score(
    question: Mapping[str, Any],
    expected: Mapping[str, Any],
    spec: Spec,
    decision: Decision,
    snapshot: LoadedSnapshot,
    registry: Registry,
) -> QuestionResult:
    findings: list[Finding] = []
    results, flagged = _decision_models(decision)
    top = results[:3]
    acceptable_entries = expected.get("acceptable") or []
    acceptable = _models(acceptable_entries)
    rule_only = bool(acceptable_entries) and not acceptable

    unexpected = [model for model in top if model not in acceptable]
    if unexpected:
        findings.append(
            Finding(
                "engine_behavior",
                "fail",
                "top result(s) outside the acceptable set: " + ", ".join(unexpected),
            )
        )
    elif not top and acceptable and not rule_only:
        if _direct_objective_has_a_value(spec, snapshot, acceptable, registry):
            findings.append(
                Finding(
                    "engine_behavior",
                    "fail",
                    "a feasible acceptable model has one verified objective measurement, but "
                    "the @direct objective selector produced no result",
                )
            )
        else:
            findings.append(
                Finding(
                    "missing_data",
                    "partial",
                    "no result has a complete verified objective value; admitted evidence may "
                    "be absent, ambiguous, or quarantined",
                )
            )

    forbidden = _models(expected.get("must_never") or [])
    forbidden_results = sorted(forbidden & set(results))
    if forbidden_results:
        findings.append(
            Finding(
                "engine_behavior",
                "fail",
                "must-never-appear model(s) were ranked: " + ", ".join(forbidden_results),
            )
        )
    forbidden_flagged = sorted((forbidden & flagged) - set(results))
    if forbidden_flagged:
        findings.append(
            Finding(
                "missing_data",
                "partial",
                "must-never-appear model(s) were listed in may_qualify because a "
                "disqualifying facet is unknown or quarantined: " + ", ".join(forbidden_flagged),
            )
        )

    candidates = _model_ids(snapshot)
    must_flag_entries = expected.get("must_flag") or []
    required_flags = _models(must_flag_entries) | _rule_flag_models(must_flag_entries, snapshot)
    for model in sorted(required_flags - flagged):
        if model not in candidates:
            findings.append(
                Finding(
                    "missing_data",
                    "partial",
                    f"required may-qualify model is absent from the snapshot: {model}",
                )
            )
        elif model in results:
            findings.append(
                Finding(
                    "engine_behavior", "fail", f"{model} should be in may_qualify but was ranked"
                )
            )
        else:
            findings.append(
                Finding(
                    "engine_behavior",
                    "fail",
                    f"{model} is in the snapshot but missing from may_qualify",
                )
            )

    missing_acceptable = acceptable - candidates
    if acceptable and missing_acceptable == acceptable:
        findings.append(
            Finding(
                "missing_data",
                "partial",
                "every named acceptable model is absent from the snapshot: "
                + ", ".join(sorted(missing_acceptable)),
            )
        )

    if _expects_no_separation(expected) and top and not _top_is_tied(decision):
        findings.append(
            Finding(
                "engine_behavior",
                "fail",
                "expected evidence cannot separate a single winner, but the decision reports "
                "an ordered top result",
            )
        )

    if not findings:
        findings.append(
            Finding("engine_behavior", "pass", "all machine-checkable expectations were met")
        )
    verdict: Verdict = (
        "fail"
        if any(item.severity == "fail" for item in findings)
        else "partial"
        if any(item.severity == "partial" for item in findings)
        else "pass"
    )
    return QuestionResult(
        id=str(question["id"]),
        question=str(question["question"]).strip(),
        verdict=verdict,
        decision=decision,
        findings=tuple(findings),
    )


def _record_sources(snapshot: LoadedSnapshot, record_ids: Sequence[str]) -> list[str]:
    urls: set[str] = set()
    for record_id in record_ids:
        record = snapshot.record(record_id)
        for source in record.get("sources") or []:
            source_id = source.get("source_id") if isinstance(source, Mapping) else None
            if source_id:
                urls.add(snapshot.source_url(str(source_id)))
        source_url = record.get("source_url")
        if isinstance(source_url, str) and source_url.startswith("https://"):
            urls.add(source_url)
    return sorted(urls)


def _top_rows(decision: Decision, snapshot: LoadedSnapshot) -> list[dict[str, Any]]:
    rows = []
    for result in decision.results[:3]:
        values = []
        urls: set[str] = set()
        for contribution in result.contributions:
            value = "unknown" if contribution.raw_value is None else f"{contribution.raw_value:g}"
            if contribution.unit:
                value += f" {contribution.unit}"
            values.append(f"{contribution.dimension}: {value}")
            urls.update(_record_sources(snapshot, contribution.records))
            urls.update(item.source for item in contribution.evidence)
        rows.append(
            {
                "rank": result.rank,
                "model": result.offering.model,
                "value": "; ".join(values) or "no objective value",
                "sources": sorted(urls),
            }
        )
    return rows


def _question_payload(row: QuestionResult, snapshot: LoadedSnapshot) -> dict[str, Any]:
    decision = row.decision
    decision_payload = None
    if decision is not None:
        decision_payload = {
            "decision_id": decision.decision_id,
            "spec_hash": decision.spec_hash,
            "status": decision.status,
            "top_3": _top_rows(decision, snapshot),
            "may_qualify_count": len(decision.may_qualify),
            "may_qualify": [
                item.model_dump(mode="json", by_alias=True) for item in decision.may_qualify[:20]
            ],
            "relax": decision.relax,
            "warnings": decision.warnings,
        }
    return {
        "id": row.id,
        "question": row.question,
        "verdict": row.verdict,
        "findings": [finding.as_dict() for finding in row.findings],
        "error": row.error,
        "decision": decision_payload,
    }


def _markdown(
    *,
    report_date: date,
    snapshot: LoadedSnapshot,
    questions: Sequence[QuestionResult],
    completeness_gaps: Sequence[Gap],
) -> str:
    counts = {
        verdict: sum(row.verdict == verdict for row in questions)
        for verdict in ("pass", "partial", "fail")
    }
    missing = sum(finding.cause == "missing_data" for row in questions for finding in row.findings)
    behavior = sum(
        finding.cause == "engine_behavior" and finding.severity != "pass"
        for row in questions
        for finding in row.findings
    )
    lines = [
        f"# Recall report — {report_date.isoformat()}",
        "",
        f"Snapshot: `{snapshot.snapshot_id}` (as of {snapshot.as_of or 'not recorded'})",
        "",
        f"**{NON_GATING}**",
        "",
        "## Summary",
        "",
        f"- Pass: {counts['pass']}; partial: {counts['partial']}; fail: {counts['fail']}.",
        f"- Missing-data findings: {missing}; engine-behavior findings: {behavior}.",
        "- Snapshot exclusions: "
        + (
            ", ".join(f"{key}={value}" for key, value in sorted(snapshot.excluded.items()))
            or "none"
        )
        + ".",
        "- Missing-data findings cover absent candidates, unknown facets, and objective evidence "
        "that is absent, ambiguous, or quarantined. Engine-behavior findings cover decisions that "
        "rank an unacceptable or indeterminate winner, surface forbidden models, or fail to list "
        "an in-snapshot model under `may_qualify`.",
        "",
    ]
    if completeness_gaps:
        lines.extend(
            [
                "### Premier-set completeness gate",
                "",
                f"The gated build failed with {len(completeness_gaps)} missing guaranteed facts. "
                "The runner used an ungated build of the same repository inputs so the audit "
                "could continue.",
                "",
            ]
        )
        grouped = Counter((gap.facet, gap.reason) for gap in completeness_gaps)
        for (facet, reason), count in sorted(grouped.items()):
            lines.append(f"- {count} × `{facet}`: {reason}.")
        lines.append("- The JSON twin contains every affected model, offering, and source.")
        lines.append("")
    for row in questions:
        lines.extend([f"## {row.id} — {row.verdict}", "", row.question, ""])
        if row.error:
            lines.extend([f"Decision error: `{row.error}`", ""])
        elif row.decision is not None:
            lines.extend(
                [
                    f"Decision: `{row.decision.status}`; ID `{row.decision.decision_id}`.",
                    "",
                    "| Rank | Model | Objective value | Sources |",
                    "|---:|---|---|---|",
                ]
            )
            top_rows = _top_rows(row.decision, snapshot)
            if not top_rows:
                lines.append("| — | No ranked result | — | — |")
            for top in top_rows:
                sources = "<br>".join(f"[{url}]({url})" for url in top["sources"]) or "—"
                lines.append(f"| {top['rank']} | `{top['model']}` | {top['value']} | {sources} |")
            lines.extend(["", "Why:", ""])
        for finding in row.findings:
            label = "missing data" if finding.cause == "missing_data" else "engine behavior"
            lines.append(f"- **{label}:** {finding.message}")
        if row.decision is not None and row.decision.may_qualify:
            shown = ", ".join(
                f"`{item.model}` ({', '.join(item.unknown)})"
                for item in row.decision.may_qualify[:10]
            )
            lines.extend(["", f"May qualify: {shown}."])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _snapshot(
    *, root: Path, snapshot_file: Path | None, report_date: date, registry: Registry
) -> tuple[LoadedSnapshot, tuple[Gap, ...]]:
    if snapshot_file is not None:
        return load_snapshot(snapshot_file, key=None), ()
    gaps: tuple[Gap, ...] = ()
    try:
        built = build_from_repo(
            root,
            premier=root / "premier" / "slice-1.yaml",
            as_of=report_date,
            registry=registry,
        )
    except CompletenessError as exc:
        gaps = exc.gaps
        built = build_from_repo(
            root,
            premier=None,
            as_of=report_date,
            registry=registry,
        )
    loaded = load_snapshot_bytes(built.to_bytes(key=None), key=None, source="repository build")
    return loaded, gaps


def run(
    *,
    root: Path = ROOT,
    snapshot_file: Path | None = None,
    output_dir: Path | None = None,
    report_date: date | None = None,
) -> RunResult:
    """Run all 20 specs and write a Markdown report plus its JSON twin."""
    root = Path(root).resolve()
    report_date = report_date or date.today()
    output_dir = Path(output_dir) if output_dir is not None else root / "docs" / "recall"
    registry = default_registry()
    snapshot, completeness_gaps = _snapshot(
        root=root,
        snapshot_file=None if snapshot_file is None else Path(snapshot_file),
        report_date=report_date,
        registry=registry,
    )
    questions = _rows_by_id(root / "tests" / "recall" / "questions.yaml")
    expected = _rows_by_id(root / "tests" / "recall" / "expected.yaml")
    rows: list[QuestionResult] = []
    for question_id in sorted(questions):
        question = questions[question_id]
        try:
            raw_spec = (root / "tests" / "recall" / "specs" / f"{question_id}.yaml").read_text(
                encoding="utf-8"
            )
            spec: Spec = parse_spec(raw_spec, facets=registry.facet)
            decision = decide(spec, snapshot, facets=registry.facet)
            rows.append(
                _score(
                    question,
                    expected[question_id],
                    spec,
                    decision,
                    snapshot,
                    registry,
                )
            )
        except Exception as exc:  # One bad spec must not hide the other 19 audit results.
            rows.append(
                QuestionResult(
                    id=question_id,
                    question=str(question["question"]).strip(),
                    verdict="fail",
                    decision=None,
                    findings=(Finding("engine_behavior", "fail", "the decision did not complete"),),
                    error=f"{type(exc).__name__}: {exc}",
                )
            )

    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{report_date.isoformat()}-{snapshot.snapshot_id}"
    markdown_path = output_dir / f"{stem}.md"
    json_path = output_dir / f"{stem}.json"
    result_rows = tuple(rows)
    payload = {
        "report_date": report_date.isoformat(),
        "snapshot": snapshot.snapshot_id,
        "snapshot_as_of": snapshot.as_of.isoformat() if snapshot.as_of else None,
        "non_gating": True,
        "snapshot_excluded": snapshot.excluded,
        "premier_completeness_gaps": [
            {
                "model": gap.model,
                "subject": gap.subject,
                "facet": gap.facet,
                "reason": gap.reason,
                "sources": list(gap.sources),
            }
            for gap in completeness_gaps
        ],
        "questions": [_question_payload(row, snapshot) for row in result_rows],
    }
    markdown_path.write_text(
        _markdown(
            report_date=report_date,
            snapshot=snapshot,
            questions=result_rows,
            completeness_gaps=completeness_gaps,
        ),
        encoding="utf-8",
    )
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return RunResult(
        snapshot.snapshot_id,
        markdown_path,
        json_path,
        result_rows,
        completeness_gaps,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--snapshot-file", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--date", type=date.fromisoformat, default=date.today())
    args = parser.parse_args(argv)
    result = run(
        root=args.root,
        snapshot_file=args.snapshot_file,
        output_dir=args.output_dir,
        report_date=args.date,
    )
    counts = {
        verdict: sum(row.verdict == verdict for row in result.questions)
        for verdict in ("pass", "partial", "fail")
    }
    print(
        f"{result.snapshot_id}: {counts['pass']} pass, {counts['partial']} partial, "
        f"{counts['fail']} fail"
    )
    print(result.markdown_path)
    print(result.json_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
