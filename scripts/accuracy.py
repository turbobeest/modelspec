#!/usr/bin/env python3
"""Publishable accuracy report for the decision engine (MODEL-111 and MODEL-160).

The PR profile runs deterministic correctness, freshness, the approved recall
limit, and output parity. The nightly profile re-reads verified values, compares
domain leaders with permitted independent boards, and reports recall changes
without gating on them.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field, replace
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Literal

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "accuracy.yaml"
DEFAULT_OUTPUT = ROOT / "accuracy-report"
DEFAULT_RECALL_BASELINE = ROOT / "tests" / "recall" / "baseline.json"
PROFILES = {
    "pr": ("deterministic_correctness", "freshness", "golden_answers", "output_parity"),
    "nightly": ("data_fidelity", "reference_agreement", "golden_answers"),
}
Status = Literal["pass", "fail", "report", "undetermined"]
RecallVerdict = Literal["pass", "partial", "fail"]


@dataclass(frozen=True)
class FreshnessConfig:
    lineup_evidence_grace_days: int
    live_leaderboard_max_age_days: int


@dataclass(frozen=True)
class DataFidelityConfig:
    sample_size: int
    random_seed: str
    max_firecrawl_credits: int


@dataclass(frozen=True)
class ReferenceConfig:
    top_k: int
    minimum_rank_correlation: float
    minimum_common_models: int


@dataclass(frozen=True)
class SuiteConfig:
    test_paths: tuple[str, ...] = ()
    python_test_paths: tuple[str, ...] = ()
    web_test_paths: tuple[str, ...] = ()


@dataclass(frozen=True)
class AccuracyConfig:
    freshness: FreshnessConfig
    data_fidelity: DataFidelityConfig
    reference: ReferenceConfig
    deterministic: SuiteConfig
    parity: SuiteConfig


@dataclass(frozen=True)
class RecallBaseline:
    snapshot: str
    as_of: date
    verdicts: Mapping[str, RecallVerdict]


@dataclass(frozen=True)
class LayerResult:
    name: str
    status: Status
    gating: bool
    summary: str
    counts: Mapping[str, int] = field(default_factory=dict)
    details: Any = field(default_factory=list)
    duration_seconds: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AccuracyReport:
    generated_at: str
    profile: str
    snapshot: str | None
    layers: tuple[LayerResult, ...]

    @property
    def status(self) -> Literal["pass", "fail"]:
        return "fail" if any(row.gating and row.status == "fail" for row in self.layers) else "pass"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "generated_at": self.generated_at,
            "profile": self.profile,
            "snapshot": self.snapshot,
            "status": self.status,
            "layers": [row.to_dict() for row in self.layers],
        }


def _mapping(value: Any, where: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{where} must be a mapping")
    return value


def load_config(path: str | Path = DEFAULT_CONFIG) -> AccuracyConfig:
    path = Path(path)
    raw = _mapping(yaml.safe_load(path.read_text(encoding="utf-8")), str(path))
    if raw.get("schema_version") != 1:
        raise ValueError(f"{path}: schema_version must be 1")
    freshness = _mapping(raw.get("freshness"), "freshness")
    fidelity = _mapping(raw.get("data_fidelity"), "data_fidelity")
    reference = _mapping(raw.get("reference"), "reference")
    deterministic = _mapping(raw.get("deterministic"), "deterministic")
    parity = _mapping(raw.get("parity"), "parity")
    config = AccuracyConfig(
        FreshnessConfig(
            int(freshness["lineup_evidence_grace_days"]),
            int(freshness["live_leaderboard_max_age_days"]),
        ),
        DataFidelityConfig(
            int(fidelity["sample_size"]),
            str(fidelity["random_seed"]),
            int(fidelity["max_firecrawl_credits"]),
        ),
        ReferenceConfig(
            int(reference["top_k"]),
            float(reference["minimum_rank_correlation"]),
            int(reference["minimum_common_models"]),
        ),
        SuiteConfig(test_paths=tuple(map(str, deterministic.get("test_paths") or ()))),
        SuiteConfig(
            python_test_paths=tuple(map(str, parity.get("python_test_paths") or ())),
            web_test_paths=tuple(map(str, parity.get("web_test_paths") or ())),
        ),
    )
    if config.freshness.lineup_evidence_grace_days < 0:
        raise ValueError("freshness.lineup_evidence_grace_days must be nonnegative")
    if config.freshness.live_leaderboard_max_age_days < 1:
        raise ValueError("freshness.live_leaderboard_max_age_days must be positive")
    if not 0 <= config.data_fidelity.max_firecrawl_credits <= 10:
        raise ValueError("data_fidelity.max_firecrawl_credits must be between 0 and 10")
    if config.reference.top_k < 1 or config.reference.minimum_common_models < 2:
        raise ValueError("reference top_k must be positive and minimum_common_models at least 2")
    return config


def _day(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None


def _model_candidates(snapshot: Any) -> dict[str, list[str]]:
    result: dict[str, list[str]] = defaultdict(list)
    for candidate in snapshot.candidates():
        if snapshot.lifecycle(candidate) == "retired":
            continue
        result[snapshot.model_of(candidate)].append(candidate)
    return dict(result)


_LIVE_SOURCE_KINDS = frozenset({"live_leaderboard", "live-leaderboard", "live_board"})


def _evidence_record(snapshot: Any, row: Any) -> Mapping[str, Any]:
    record_id = getattr(row, "record_id", None)
    if record_id is None or not hasattr(snapshot, "record"):
        return {}
    try:
        record = snapshot.record(record_id)
    except (KeyError, TypeError):
        return {}
    return record if isinstance(record, Mapping) else {}


def _observation_metadata_date(record: Mapping[str, Any]) -> date | None:
    """Return a source observation date, never an evaluation/publication date."""
    containers = [record]
    source_snapshot = record.get("source_snapshot")
    if isinstance(source_snapshot, Mapping):
        containers.append(source_snapshot)
    sources = record.get("sources")
    if isinstance(sources, Sequence) and not isinstance(sources, (str, bytes)):
        containers.extend(source for source in sources if isinstance(source, Mapping))
    for key in ("observed_at", "retrieved_at"):
        for container in containers:
            if (value := _day(container.get(key))) is not None:
                return value
    return _day(record.get("verified_at"))


def _live_observation_date(
    snapshot: Any,
    row: Any,
    sources: Mapping[str, Any],
) -> tuple[bool, date | None]:
    """Classify a reading and return when the live board was observed.

    ``evaluated`` is deliberately not a live marker: it is also used for fixed
    benchmark runs. A live source kind makes the source metadata authoritative;
    an explicit ``observed`` date type means the evidence date is itself the
    observation date.
    """
    record = _evidence_record(snapshot, row)
    date_type = getattr(row, "date_type", None) or record.get("date_type")
    source_kind = getattr(row, "source_kind", None) or record.get("source_kind")
    source_ids = set(getattr(row, "source_ids", ()) or ())
    refs = record.get("sources")
    if isinstance(refs, Sequence) and not isinstance(refs, (str, bytes)):
        source_ids.update(
            str(ref["source_id"])
            for ref in refs
            if isinstance(ref, Mapping) and ref.get("source_id")
        )
    if any(getattr(sources.get(source_id), "volatility", "static") == "live"
           for source_id in source_ids):
        return True, _observation_metadata_date(record)
    if source_kind in _LIVE_SOURCE_KINDS:
        return True, _observation_metadata_date(record)
    if date_type == "observed":
        return True, _day(getattr(row, "date", None) or record.get("evidence_date"))
    return False, None


def check_freshness(
    snapshot: Any,
    *,
    as_of: date,
    config: FreshnessConfig,
    sources: Mapping[str, Any] | None = None,
) -> LayerResult:
    """Gate lineup evidence and live-leaderboard observation age."""
    if sources is None:
        from decision.sources import load_sources

        sources = load_sources(ROOT / "registry" / "sources.yaml")
    problems: list[dict[str, Any]] = []
    models = _model_candidates(snapshot)
    seen_records: set[str] = set()
    live_rows = 0
    for model_id, candidates in sorted(models.items()):
        released = _day(snapshot.fact(model_id, "model.release_date").value)
        evidence = [
            row
            for candidate in candidates
            for domain in snapshot.domain_ids()
            for row in snapshot.evidence_for_domain(candidate, domain)
            if getattr(row, "verified", False)
        ]
        if (
            released is not None
            and (as_of - released).days > config.lineup_evidence_grace_days
            and not evidence
        ):
            problems.append(
                {
                    "model": model_id,
                    "release_date": released.isoformat(),
                    "reason": "no_verified_domain_evidence",
                }
            )
        for row in evidence:
            key = row.record_id or f"{model_id}:{row.benchmark_id}:{row.date}:{row.value}"
            live, observed = _live_observation_date(snapshot, row, sources)
            if key in seen_records or not live:
                continue
            seen_records.add(key)
            live_rows += 1
            if observed is None:
                problems.append(
                    {
                        "model": model_id,
                        "benchmark": row.benchmark_id,
                        "reason": "undated_live_leaderboard",
                    }
                )
            elif (as_of - observed).days > config.live_leaderboard_max_age_days:
                problems.append(
                    {
                        "model": model_id,
                        "benchmark": row.benchmark_id,
                        "observation_date": observed.isoformat(),
                        "age_days": (as_of - observed).days,
                        "reason": "stale_live_leaderboard",
                    }
                )
    status: Status = "fail" if problems else "pass"
    return LayerResult(
        "freshness",
        status,
        True,
        f"{len(models)} lineup models and {live_rows} dated live readings checked; "
        f"{len(problems)} freshness failure(s).",
        {"lineup_models": len(models), "live_readings": live_rows, "failures": len(problems)},
        problems,
    )


_VERDICT_LEVEL = {"fail": 0, "partial": 1, "pass": 2}


def load_recall_baseline(path: str | Path = DEFAULT_RECALL_BASELINE) -> RecallBaseline:
    path = Path(path)
    raw = _mapping(json.loads(path.read_text(encoding="utf-8")), str(path))
    if raw.get("schema_version") != 1:
        raise ValueError(f"{path}: schema_version must be 1")
    verdicts = _mapping(raw.get("verdicts"), f"{path}: verdicts")
    invalid = sorted(
        question_id
        for question_id, verdict in verdicts.items()
        if not isinstance(question_id, str) or verdict not in _VERDICT_LEVEL
    )
    if invalid:
        raise ValueError(f"{path}: invalid recall verdicts for {', '.join(invalid)}")
    as_of = _day(raw.get("as_of"))
    if as_of is None:
        raise ValueError(f"{path}: as_of must be an ISO date")
    snapshot = raw.get("snapshot")
    if not isinstance(snapshot, str) or not snapshot:
        raise ValueError(f"{path}: snapshot must be a non-empty string")
    return RecallBaseline(snapshot, as_of, dict(verdicts))


def _recall_causes(question: Any) -> list[str]:
    labels = {"missing_data": "missing data", "engine_behavior": "engine behavior"}
    return sorted(
        {labels[finding.cause] for finding in question.findings if finding.severity != "pass"}
    )


def recall_ratchet(
    baseline: Mapping[str, RecallVerdict],
    questions: Sequence[Any],
    *,
    gating: bool,
    update_command: str,
) -> LayerResult:
    current = {row.id: row for row in questions}
    details: list[dict[str, Any]] = []
    regressions = improvements = 0
    for question_id in sorted(set(baseline) | set(current)):
        before = baseline.get(question_id)
        row = current.get(question_id)
        after = None if row is None else row.verdict
        if before is None or after is None:
            regressions += 1
            details.append(
                {
                    "id": question_id,
                    "change": "regression",
                    "transition": f"{before or 'missing'} -> {after or 'missing'}",
                    "causes": ["engine behavior"],
                }
            )
            continue
        delta = _VERDICT_LEVEL[after] - _VERDICT_LEVEL[before]
        if delta == 0:
            continue
        change = "improvement" if delta > 0 else "regression"
        regressions += int(delta < 0)
        improvements += int(delta > 0)
        details.append(
            {
                "id": question_id,
                "change": change,
                "transition": f"{before} -> {after}",
                "causes": _recall_causes(row),
            }
        )
    verdict_counts = {
        verdict: sum(row.verdict == verdict for row in questions)
        for verdict in ("pass", "partial", "fail")
    }
    counts = {
        **verdict_counts,
        "regressions": regressions,
        "improvements": improvements,
    }
    changed = regressions + improvements
    if changed == 0:
        return LayerResult(
            "golden_answers",
            "pass",
            gating,
            f"All {len(questions)} approved recall verdicts match the baseline.",
            counts,
            details,
        )
    messages = []
    if regressions:
        messages.append(f"{regressions} recall regression(s)")
    if improvements:
        messages.append(
            f"{improvements} unrecorded improvement(s); update the baseline with: {update_command}"
        )
    return LayerResult(
        "golden_answers",
        "fail" if gating else "report",
        gating,
        "; ".join(messages) + ".",
        counts,
        details,
    )


_RECALL_APPROVAL_PATHS = frozenset({"tests/recall/expected.yaml", "tests/recall/README.md"})


def check_recall_approval(changed_paths: Sequence[str], labels: Sequence[str]) -> LayerResult:
    protected = sorted(
        path
        for path in changed_paths
        if path in _RECALL_APPROVAL_PATHS or path.startswith("tests/recall/specs/")
    )
    approved = "recall-approved" in labels
    failed = bool(protected) and not approved
    return LayerResult(
        "recall_approval",
        "fail" if failed else "pass",
        True,
        (
            "Protected recall inputs changed without the recall-approved label. "
            "Only Jamie may apply recall-approved."
            if failed
            else "Protected recall inputs are unchanged or the recall-approved label is present."
        ),
        {"protected_files": len(protected), "approved": int(approved)},
        protected,
    )


def _run_command(name: str, command: Sequence[str], *, cwd: Path) -> LayerResult:
    started = time.monotonic()
    completed = subprocess.run(
        list(command),
        cwd=cwd,
        env={**os.environ, "PYTHONPATH": str(cwd)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    duration = time.monotonic() - started
    output = completed.stdout.strip()
    tail = output.splitlines()[-20:]
    return LayerResult(
        name,
        "pass" if completed.returncode == 0 else "fail",
        True,
        f"Command exited {completed.returncode}: {' '.join(command)}",
        {"commands": 1, "failed": int(completed.returncode != 0)},
        {"command": list(command), "output_tail": tail},
        round(duration, 3),
    )


def deterministic_correctness(root: Path, config: SuiteConfig) -> LayerResult:
    result = _run_command(
        "deterministic_correctness",
        (sys.executable, "-m", "pytest", "-q", *config.test_paths),
        cwd=root,
    )
    output = result.details.get("output_tail", [])
    pytest_summary = next(
        (line for line in reversed(output) if " passed" in line or " failed" in line),
        result.summary,
    )
    return replace(
        result,
        summary=f"Existing decision-engine suites: {pytest_summary}",
        counts={"suites": len(config.test_paths), **result.counts},
    )


def output_parity(root: Path, config: SuiteConfig) -> LayerResult:
    python_result = _run_command(
        "output_parity",
        (sys.executable, "-m", "pytest", "-q", *config.python_test_paths),
        cwd=root,
    )
    web_command = (
        "npm",
        "exec",
        "--",
        "vitest",
        "run",
        *config.web_test_paths,
    )
    web_result = _run_command("output_parity", web_command, cwd=root / "web")
    failed = python_result.status == "fail" or web_result.status == "fail"
    return LayerResult(
        "output_parity",
        "fail" if failed else "pass",
        True,
        "CLI/Worker byte parity and web-adapter spec mapping both passed."
        if not failed
        else "At least one output-parity suite failed.",
        {
            "commands": 2,
            "failed": int(python_result.status == "fail") + int(web_result.status == "fail"),
        },
        [python_result.details, web_result.details],
        round((python_result.duration_seconds or 0) + (web_result.duration_seconds or 0), 3),
    )


def _load_snapshot(root: Path, snapshot_file: Path | None, as_of: date):
    from decision.snapshot import build_from_repo, load_snapshot, load_snapshot_bytes

    if snapshot_file is not None:
        return load_snapshot(snapshot_file, key=None, include_archive=False)
    built = build_from_repo(root, premier=root / "premier" / "slice-1.yaml", as_of=as_of)
    return load_snapshot_bytes(built.to_bytes(key=None), key=None, include_archive=False)


def _recall_update_command(as_of: date) -> str:
    return (
        "PYTHONPATH=$PWD python scripts/accuracy.py --update-recall-baseline "
        f"--date {as_of.isoformat()}"
    )


def run_golden(root: Path, snapshot_file: Path | None, as_of: date, *, gating: bool) -> LayerResult:
    from scripts.recall_run import run

    with tempfile.TemporaryDirectory(prefix="modelspec-recall-") as temporary:
        result = run(
            root=root,
            snapshot_file=snapshot_file,
            output_dir=Path(temporary),
            report_date=as_of,
        )
        baseline = load_recall_baseline(root / "tests" / "recall" / "baseline.json")
        return recall_ratchet(
            baseline.verdicts,
            result.questions,
            gating=gating,
            update_command=_recall_update_command(as_of),
        )


def update_recall_baseline(
    *, root: Path, snapshot_file: Path | None, as_of: date
) -> RecallBaseline:
    from scripts.recall_run import run

    path = root / "tests" / "recall" / "baseline.json"
    with tempfile.TemporaryDirectory(prefix="modelspec-recall-baseline-") as temporary:
        result = run(
            root=root,
            snapshot_file=snapshot_file,
            output_dir=Path(temporary),
            report_date=as_of,
        )
    verdicts = {row.id: row.verdict for row in result.questions}
    if path.is_file():
        previous = load_recall_baseline(path)
        comparison = recall_ratchet(
            previous.verdicts,
            result.questions,
            gating=True,
            update_command=_recall_update_command(as_of),
        )
        regressions = [row for row in comparison.details if row["change"] == "regression"]
        if regressions:
            transitions = ", ".join(f"{row['id']} {row['transition']}" for row in regressions)
            raise ValueError(f"refusing to lower the recall baseline: {transitions}")
    payload = {
        "schema_version": 1,
        "as_of": as_of.isoformat(),
        "snapshot": result.snapshot_id,
        "generated_by": _recall_update_command(as_of),
        "verdicts": verdicts,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return RecallBaseline(result.snapshot_id, as_of, verdicts)


def claim_category(claim: Any) -> Literal["fact", "evidence", "offering"]:
    if claim.target.kind == "evidence":
        return "evidence"
    if claim.field.startswith("offering."):
        return "offering"
    return "fact"


def sample_verified_claims(claims: Sequence[Any], *, size: int, seed: str) -> list[Any]:
    """Choose a repeatable random sample, representing every available value category."""
    if size < 1:
        raise ValueError("sample size must be positive")
    rng = random.Random(seed)
    groups: dict[str, list[Any]] = defaultdict(list)
    for claim in claims:
        groups[claim_category(claim)].append(claim)
    for rows in groups.values():
        rng.shuffle(rows)
    selected: list[Any] = []
    categories = [name for name in ("fact", "evidence", "offering") if groups[name]]
    while len(selected) < min(size, len(claims)):
        progressed = False
        for name in categories:
            if groups[name] and len(selected) < size:
                selected.append(groups[name].pop())
                progressed = True
        if not progressed:
            break
    return selected


def _latest_collected_claims(path: Path) -> list[Any]:
    from decision.verify import Claim

    latest: dict[tuple[str, str], Claim] = {}
    if not path.is_file():
        return []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        if event.get("event") != "collected":
            continue
        claim = Claim.from_dict(event["claim"])
        latest[(claim.target.kind, claim.target.id)] = claim
    return list(latest.values())


def _verified_claims(root: Path) -> list[Any]:
    from decision.model import value_hash
    from decision.verify import VerificationLog

    directory = root / "verification"
    latest = VerificationLog(directory).latest()
    claims = _latest_collected_claims(directory / "queue" / "events.jsonl")
    return [
        claim
        for claim in claims
        if (record := latest.get((claim.target.kind, claim.target.id))) is not None
        and record.outcome == "verified"
        and record.target.value_hash == value_hash(claim.value)
    ]


def verify_fidelity_sample(
    claims: Sequence[Any],
    *,
    regions: Any,
    extractors: Sequence[Any],
    queue: Any,
    log: Any,
    today: date,
    source_urls: Mapping[str, str],
) -> LayerResult:
    """Re-read sampled claims and route failures through MODEL-140's recrawl queue."""
    from decision.verify import ref_str, verify

    details = []
    counts = dict.fromkeys(("verified", "mismatch", "unreachable", "skipped"), 0)
    for claim in claims:
        result = verify(claim, regions, extractors, today=today)
        counts[result.outcome] += 1
        if result.verification is not None:
            log.append(result.verification)
        if result.outcome in ("mismatch", "unreachable"):
            queue.checked(result, at=datetime.now(UTC))
        details.append(
            {
                "target": ref_str(result.target),
                "category": claim_category(claim),
                "outcome": result.outcome,
                "diff": [row.to_dict() for row in result.diffs],
                "reason": result.reason,
                "source_urls": sorted(
                    {
                        source_urls[source.source_id]
                        for source in claim.sources
                        if source.source_id in source_urls
                    }
                ),
                "read_date": today.isoformat(),
                "verifier": result.verification.verifier.model_dump()
                if result.verification is not None
                else None,
            }
        )
    failed = sum(counts[name] for name in ("mismatch", "unreachable", "skipped"))
    return LayerResult(
        "data_fidelity",
        "fail" if failed else "pass",
        True,
        f"Re-read {len(claims)} verified values from current source copies; "
        f"{failed} did not verify.",
        counts,
        details,
    )


def data_fidelity(
    root: Path,
    *,
    as_of: date,
    config: DataFidelityConfig,
    sample_size: int | None = None,
    seed: str | None = None,
    llm_reader: str | None = None,
) -> LayerResult:
    """Nightly source re-read. Plain HTTP is attempted before any paid renderer.

    Every selected source gets a plain HTTP attempt, including sources normally
    marked rendered. Firecrawl use is therefore zero and cannot exceed the
    configured ten-credit ceiling. A short eligible pool fails rather than
    silently reducing N.
    """
    from decision.excluded import excluded_sources
    from decision.sources import CopyStore, Fetcher, recheck
    from decision.verify import (
        Queue,
        StoredRegions,
        VerificationLog,
        claude_extractor,
        deterministic_extractors,
        load_sources,
        mistral_extractor,
    )

    wanted = sample_size or config.sample_size
    sources = load_sources(root / "registry" / "sources.yaml")
    excluded = excluded_sources()
    eligible = [
        claim
        for claim in _verified_claims(root)
        if claim.sources
        and all(
            source.source_id in sources
            and not excluded.url(sources[source.source_id].url)
            for source in claim.sources
        )
    ]
    sampled = sample_verified_claims(
        eligible,
        size=wanted,
        seed=f"{seed or config.random_seed}:{as_of.isoformat()}",
    )
    with tempfile.TemporaryDirectory(prefix="modelspec-accuracy-sources-") as temporary:
        store = CopyStore(Path(temporary))
        selected_ids = {source.source_id for claim in sampled for source in claim.sources}
        report = recheck(
            [
                sources[source_id].model_copy(update={"fetch": "http"})
                for source_id in sorted(selected_ids)
            ],
            {},
            (),
            fetcher=Fetcher(),
            store=store,
            now=datetime.combine(as_of, datetime.min.time(), tzinfo=UTC),
        )
        current_refs = {
            source_id: state.snapshot.copy_ref
            for source_id, state in report.states.items()
            if state.snapshot is not None
        }
        current = [
            replace(
                claim,
                sources=tuple(
                    source.model_copy(update={"snapshot_ref": current_refs[source.source_id]})
                    if source.source_id in current_refs
                    else source
                    for source in claim.sources
                ),
            )
            for claim in sampled
        ]
        extractors = deterministic_extractors()
        if llm_reader == "claude":
            extractors.append(claude_extractor())
        elif llm_reader == "mistral":
            extractors.append(mistral_extractor())
        result = verify_fidelity_sample(
            current,
            regions=StoredRegions(store, sources),
            extractors=extractors,
            queue=Queue(root / "verification"),
            log=VerificationLog(root / "verification"),
            today=as_of,
            source_urls={source_id: str(source.url) for source_id, source in sources.items()},
        )
    details = {
        "sample": result.details,
        "eligible_values": len(eligible),
        "requested_sample_size": wanted,
        "actual_sample_size": len(sampled),
        "plain_http_sources": len(selected_ids),
        "firecrawl_credits_used": 0,
        "firecrawl_credit_limit": config.max_firecrawl_credits,
    }
    if len(sampled) < wanted:
        return replace(
            result,
            status="fail",
            summary=(
                result.summary + f" Only {len(sampled)} of {wanted} eligible values were available."
            ),
            details=details,
        )
    return replace(result, details=details)


def spearman(
    left: Mapping[str, int], right: Mapping[str, int], *, minimum_common: int
) -> float | None:
    """Pearson correlation of the two rank vectors (Spearman's rho)."""
    common = sorted(set(left) & set(right))
    if len(common) < minimum_common:
        return None
    xs = [float(left[key]) for key in common]
    ys = [float(right[key]) for key in common]
    xbar, ybar = sum(xs) / len(xs), sum(ys) / len(ys)
    numerator = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys, strict=True))
    xnorm = sum((x - xbar) ** 2 for x in xs) ** 0.5
    ynorm = sum((y - ybar) ** 2 for y in ys) ** 0.5
    if xnorm == 0 or ynorm == 0:
        return None
    return round(numerator / (xnorm * ynorm), 6)


def compare_rankings(
    *,
    domain: str,
    engine_basis: str,
    engine_benchmark: str | None,
    engine_rows: Sequence[Mapping[str, Any]],
    reference_board: str,
    reference_rows: Sequence[Mapping[str, Any]],
    source_url: str,
    read_date: date,
    config: ReferenceConfig,
) -> dict[str, Any]:
    engine_rank = {str(row["model"]): i for i, row in enumerate(engine_rows, start=1)}
    reference_rank = {str(row["model"]): i for i, row in enumerate(reference_rows, start=1)}
    rho = spearman(engine_rank, reference_rank, minimum_common=config.minimum_common_models)
    engine_top = list(engine_rank)[: config.top_k]
    reference_top = list(reference_rank)[: config.top_k]
    frontier = sorted(set(engine_top) & set(reference_top))
    if not engine_rows or not reference_rows:
        status: Status = "undetermined"
    elif not frontier or (rho is not None and rho < config.minimum_rank_correlation):
        status = "fail"
    elif rho is None:
        status = "undetermined"
    else:
        status = "pass"
    return {
        "domain": domain,
        "status": status,
        "engine_basis": engine_basis,
        "engine_benchmark": engine_benchmark,
        "reference_board": reference_board,
        "rank_correlation": rho,
        "common_models": len(set(engine_rank) & set(reference_rank)),
        "known_frontier_present": bool(frontier),
        "frontier_models": frontier,
        "engine_top_k": engine_top,
        "reference_top_k": reference_top,
        "responsible_evidence": [dict(row) for row in engine_rows[: config.top_k]],
        "source_url": source_url,
        "read_date": read_date.isoformat(),
    }


def _benchmark_directions(root: Path) -> dict[str, str]:
    from pipeline.load import load_benchmarks

    return {
        card.benchmark_id: str(
            (card.front.get("metric") or {}).get("direction") or "higher_is_better"
        )
        for card in load_benchmarks(root)
    }


def _engine_domain_ranking(
    snapshot: Any, domain: str, *, root: Path
) -> tuple[str | None, list[dict]]:
    """Fallback before MODEL-129: the most-covered direct benchmark in this domain."""
    by_benchmark: dict[str, dict[str, list[Any]]] = defaultdict(lambda: defaultdict(list))
    for model, candidates in _model_candidates(snapshot).items():
        seen: set[str] = set()
        for candidate in candidates:
            for row in snapshot.evidence_for_domain(candidate, domain):
                key = row.record_id or f"{row.benchmark_id}:{row.value}:{row.date}"
                if not row.verified or row.directness != "direct" or key in seen:
                    continue
                seen.add(key)
                by_benchmark[row.benchmark_id][model].append(row)
    if not by_benchmark:
        return None, []
    benchmark = min(
        by_benchmark,
        key=lambda name: (-len(by_benchmark[name]), name),
    )
    directions = _benchmark_directions(root)
    reverse = directions.get(benchmark, "higher_is_better") == "higher_is_better"
    rows = []
    for model, evidence in by_benchmark[benchmark].items():
        ordered = sorted(evidence, key=lambda row: row.value, reverse=reverse)
        rows.append(
            {
                "model": model,
                "value": ordered[0].value,
                "record_ids": sorted({row.record_id for row in evidence if row.record_id}),
            }
        )
    rows.sort(key=lambda row: ((-row["value"] if reverse else row["value"]), row["model"]))
    return benchmark, rows


_BOARD_DOMAINS: Mapping[str, tuple[str, ...]] = {
    "software-engineering": ("software_engineering",),
    "chat-or-preference": ("chat_preference",),
    "reasoning-and-maths": ("maths", "reasoning"),
    "vision": ("vision_documents",),
    "retrieval-and-embedding": ("retrieval",),
}
_ALLOWED_BOARD_PREFIXES = (
    "arena-",
    "swe-bench",
    "terminal-bench",
    "matharena-",
    "epoch-",
    "mteb-",
)


def _reference_rows(board: Mapping[str, Any], index: Mapping[str, str]) -> list[dict[str, Any]]:
    from scripts.premier_slice1 import rank_board

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rank_board(dict(board)):
        model = index.get(row["slug"])
        if model is None or model in seen:
            continue
        seen.add(model)
        rows.append({"model": model, "value": row["score"]})
    return rows


def reference_agreement(
    snapshot: Any,
    root: Path,
    *,
    as_of: date,
    config: ReferenceConfig,
) -> LayerResult:
    """Compare every registered domain with each applicable permitted board snapshot."""
    from scripts import premier_slice1 as premier

    aliases = json.loads((root / "premier" / "inputs" / "aliases.json").read_text())
    cards = premier.load_cards()
    index = premier.match_index(cards, aliases)
    boards = [
        board
        for board in premier.leaderboards()
        if str(board["id"]).startswith(_ALLOWED_BOARD_PREFIXES)
    ]
    comparisons: list[dict[str, Any]] = []
    for domain in snapshot.domain_ids():
        benchmark, engine_rows = _engine_domain_ranking(snapshot, domain, root=root)
        applicable = [
            board for board in boards if domain in _BOARD_DOMAINS.get(board["domain"], ())
        ]
        if not applicable:
            comparisons.append(
                {
                    "domain": domain,
                    "status": "undetermined",
                    "engine_basis": "direct_benchmark",
                    "engine_benchmark": benchmark,
                    "reason": "no_permitted_independent_board",
                }
            )
            continue
        for board in applicable:
            comparisons.append(
                compare_rankings(
                    domain=domain,
                    engine_basis="direct_benchmark",
                    engine_benchmark=benchmark,
                    engine_rows=engine_rows,
                    reference_board=str(board["id"]),
                    reference_rows=_reference_rows(board, index),
                    source_url=str(board["url"]),
                    read_date=_day(premier.READ_DATE) or as_of,
                    config=config,
                )
            )
    counts = {
        status: sum(row["status"] == status for row in comparisons)
        for status in ("pass", "fail", "undetermined")
    }
    status: Status = "fail" if counts["fail"] else "pass"
    if not comparisons or counts["undetermined"] == len(comparisons):
        status = "undetermined"
    return LayerResult(
        "reference_agreement",
        status,
        True,
        f"Compared {len(snapshot.domain_ids())} domains across {len(comparisons)} "
        f"permitted board comparisons; {counts['fail']} disagreement(s).",
        counts,
        comparisons,
    )


def _markdown(report: AccuracyReport) -> str:
    lines = [
        "# Decision engine accuracy",
        "",
        f"**Overall: {report.status.upper()}**  ",
        f"Generated: {report.generated_at}  ",
        f"Profile: `{report.profile}`  ",
        f"Snapshot: `{report.snapshot or 'not used'}`",
        "",
        "| Layer | Status | Gate | Summary |",
        "| --- | --- | --- | --- |",
    ]
    for row in report.layers:
        summary = row.summary.replace("|", "\\|")
        lines.append(
            f"| {row.name.replace('_', ' ')} | {row.status.upper()} | "
            f"{'yes' if row.gating else 'no'} | {summary} |"
        )
    for row in report.layers:
        if not row.details:
            continue
        lines.extend(
            [
                "",
                f"## {row.name.replace('_', ' ').title()}",
                "",
                "```json",
                json.dumps(row.details, indent=2, sort_keys=True, default=str),
                "```",
            ]
        )
    return "\n".join(lines) + "\n"


def write_report(report: AccuracyReport, output_dir: str | Path) -> tuple[Path, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    markdown = output_dir / "accuracy.md"
    payload = output_dir / "accuracy.json"
    markdown.write_text(_markdown(report), encoding="utf-8")
    payload.write_text(
        json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return markdown, payload


def run_profile(
    *,
    root: Path = ROOT,
    config_path: Path = DEFAULT_CONFIG,
    profile: str = "pr",
    layers: Sequence[str] | None = None,
    output_dir: Path = DEFAULT_OUTPUT,
    snapshot_file: Path | None = None,
    as_of: date | None = None,
    llm_reader: str | None = None,
    sample_size: int | None = None,
    random_seed: str | None = None,
) -> AccuracyReport:
    del output_dir
    root = Path(root).resolve()
    as_of = as_of or date.today()
    config = load_config(config_path)
    selected = tuple(layers or PROFILES[profile])
    snapshot = None
    # Load the reference snapshot before fidelity can quarantine a mismatched
    # value in this run. Both nightly layers must assess the same starting state.
    if "reference_agreement" in selected:
        snapshot = _load_snapshot(root, snapshot_file, as_of)
    results: list[LayerResult] = []
    for layer in selected:
        if layer == "deterministic_correctness":
            results.append(deterministic_correctness(root, config.deterministic))
        elif layer == "freshness":
            snapshot = snapshot or _load_snapshot(root, snapshot_file, as_of)
            results.append(check_freshness(snapshot, as_of=as_of, config=config.freshness))
        elif layer == "golden_answers":
            results.append(run_golden(root, snapshot_file, as_of, gating=profile == "pr"))
        elif layer == "output_parity":
            results.append(output_parity(root, config.parity))
        elif layer == "data_fidelity":
            results.append(
                data_fidelity(
                    root,
                    as_of=as_of,
                    config=config.data_fidelity,
                    sample_size=sample_size,
                    seed=random_seed,
                    llm_reader=llm_reader,
                )
            )
        elif layer == "reference_agreement":
            snapshot = snapshot or _load_snapshot(root, snapshot_file, as_of)
            results.append(
                reference_agreement(snapshot, root, as_of=as_of, config=config.reference)
            )
        else:
            raise ValueError(f"unknown accuracy layer: {layer}")
    return AccuracyReport(
        generated_at=datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        profile=profile,
        snapshot=getattr(snapshot, "snapshot_id", None),
        layers=tuple(results),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--profile", choices=tuple(PROFILES), default="pr")
    parser.add_argument(
        "--layers", help="Comma-separated layer names instead of the profile default."
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--snapshot-file", type=Path)
    parser.add_argument("--date", type=date.fromisoformat, default=date.today())
    parser.add_argument("--llm-reader", choices=("claude", "mistral"))
    parser.add_argument("--sample-size", type=int)
    parser.add_argument("--seed")
    parser.add_argument(
        "--update-recall-baseline",
        action="store_true",
        help="Raise tests/recall/baseline.json to the current recall verdicts.",
    )
    parser.add_argument(
        "--check-recall-approval",
        action="store_true",
        help="Check protected recall paths against pull-request labels.",
    )
    parser.add_argument("--changed-files", type=Path)
    parser.add_argument("--labels-json")
    args = parser.parse_args(argv)
    if args.update_recall_baseline and args.check_recall_approval:
        parser.error("choose only one maintenance operation")
    if args.update_recall_baseline:
        try:
            baseline = update_recall_baseline(
                root=args.root.resolve(), snapshot_file=args.snapshot_file, as_of=args.date
            )
        except ValueError as exc:
            parser.error(str(exc))
        print(
            f"Updated {args.root / 'tests' / 'recall' / 'baseline.json'}: "
            f"{len(baseline.verdicts)} verdicts from {baseline.snapshot}."
        )
        return 0
    if args.check_recall_approval:
        if args.changed_files is None or args.labels_json is None:
            parser.error("--check-recall-approval requires --changed-files and --labels-json")
        changed_paths = [
            line.strip()
            for line in args.changed_files.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        try:
            labels = json.loads(args.labels_json)
        except json.JSONDecodeError as exc:
            parser.error(f"--labels-json is not valid JSON: {exc}")
        if not isinstance(labels, list) or not all(isinstance(label, str) for label in labels):
            parser.error("--labels-json must be a JSON list of strings")
        result = check_recall_approval(changed_paths, labels)
        print(result.summary)
        for path in result.details:
            print(path)
        return 1 if result.status == "fail" else 0
    report = run_profile(
        root=args.root,
        config_path=args.config,
        profile=args.profile,
        layers=tuple(filter(None, args.layers.split(","))) if args.layers else None,
        output_dir=args.output_dir,
        snapshot_file=args.snapshot_file,
        as_of=args.date,
        llm_reader=args.llm_reader,
        sample_size=args.sample_size,
        random_seed=args.seed,
    )
    markdown, payload = write_report(report, args.output_dir)
    print(markdown.read_text(encoding="utf-8"), end="")
    print(f"JSON: {payload}")
    return 1 if report.status == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
