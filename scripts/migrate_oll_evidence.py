#!/usr/bin/env python3
"""Move exact Open LLM Leaderboard flat values to per-value evidence.

The collector reads the leaderboard's pinned Hugging Face dataset revisions,
requires an exact Hugging Face repository identity, and only migrates a card
value when a published result file states the same value at the card's written
precision. Values without that proof remain in ``benchmarks.scores``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from statistics import mean
from typing import Any

import yaml

from decision.model import SourceRef, TargetRef, VerificationActor, value_hash
from decision.sources import CopyStore, load_sources
from decision.verify import Claim, Queue, VerificationLog
from scripts.model_143_evidence import evidence_id

ROOT = Path(__file__).resolve().parents[1]
READ_DATE = date(2026, 9, 25)
USER_AGENT = "ModelSpec/1.0 (+https://modelspec.dev)"
COLLECTOR = VerificationActor(
    agent="openai-codex-model-118",
    model_family="openai",
    method="hf-result-projection@1",
)
DATASETS = {
    "v1": ("open-llm-leaderboard-old/results", "23474373f8874f9057d23b97e5a41e911d2721c5"),
    "v2": ("open-llm-leaderboard/results", "aa81ecc38fdc5708254b833923368970efdf5ef5"),
}

V1_METRICS = {
    "arc_challenge": ("harness|arc:challenge|25", "acc_norm"),
    "gsm8k": ("harness|gsm8k|5", "acc"),
    "hellaswag": ("harness|hellaswag|10", "acc_norm"),
    "truthfulqa": ("harness|truthfulqa:mc|0", "mc2"),
    "winogrande": ("harness|winogrande|5", "acc"),
}


def _percent(value: Any) -> float:
    return 100.0 * float(value)


def extract_v1_scores(result: dict[str, Any], path: str) -> tuple[str, date, dict[str, float]]:
    """Return the evaluated identity, date and OLL v1 metrics from one result file."""
    identity = str((result.get("config_general") or {}).get("model_name") or "")
    match = re.search(r"/results_(\d{4}-\d{2}-\d{2})T", "/" + path)
    if not identity or match is None:
        raise ValueError(f"not an OLL v1 result file: {path}")
    rows = result.get("results") or {}
    scores: dict[str, float] = {}
    for benchmark_id, (task, metric) in V1_METRICS.items():
        if metric in (rows.get(task) or {}):
            scores[benchmark_id] = _percent(rows[task][metric])
    prefix = "harness|hendrycksTest-"
    for task, metrics in rows.items():
        if task.startswith(prefix) and "|" in task[len(prefix):] and "acc" in metrics:
            subject = task[len(prefix):].split("|", 1)[0]
            scores[f"mmlu_{subject}"] = _percent(metrics["acc"])
    return identity, date.fromisoformat(match.group(1)), scores


def extract_v2_scores(result: dict[str, Any], path: str) -> tuple[str, date, dict[str, float]]:
    """Return the evaluated identity, date and canonical OLL v2 metrics."""
    model_args = str((result.get("config") or {}).get("model_args") or "")
    match = re.search(r"(?:^|,)pretrained=([^,]+)", model_args)
    if match is None or result.get("date") is None:
        raise ValueError(f"not an OLL v2 result file: {path}")
    identity = match.group(1)
    evaluated = datetime.fromtimestamp(float(result["date"]), UTC).date()
    rows = result.get("results") or {}

    def values(prefix: str, metric: str) -> list[float]:
        return [float(row[metric]) for task, row in rows.items()
                if task.startswith(prefix) and metric in row]

    scores: dict[str, float] = {}
    strict = rows.get("leaderboard_ifeval") or {}
    if all(key in strict for key in (
        "prompt_level_strict_acc,none", "inst_level_strict_acc,none"
    )):
        scores["ifeval"] = _percent(mean([
            strict["prompt_level_strict_acc,none"],
            strict["inst_level_strict_acc,none"],
        ]))
    for benchmark_id, prefix in (("bbh", "leaderboard_bbh_"),
                                 ("musr", "leaderboard_musr_")):
        found = values(prefix, "acc_norm,none")
        if found:
            scores[benchmark_id] = _percent(mean(found))
    direct = {
        "math_lvl5": ("leaderboard_math_hard", "exact_match,none"),
        "gpqa_pooled": ("leaderboard_gpqa", "acc_norm,none"),
        "mmlu_pro": ("leaderboard_mmlu_pro", "acc,none"),
    }
    for benchmark_id, (task, metric) in direct.items():
        if metric in (rows.get(task) or {}):
            scores[benchmark_id] = _percent(rows[task][metric])
    return identity, evaluated, scores


@dataclass(frozen=True)
class PublishedResult:
    version: str
    path: str
    source_url: str
    source_id: str
    identity: str
    evaluated: date
    scores: dict[str, float]
    snapshot_ref: str


@dataclass
class Change:
    card: str
    model_id: str
    benchmark_id: str
    legacy_value: float
    status: str = "unverified-legacy"
    reason: str = "no exact published value"
    published_value: float | None = None
    evidence_date: str = ""
    source_url: str = ""
    evidence_id: str = ""
    row: dict[str, Any] | None = None
    claim: Claim | None = None

    def audit_row(self) -> dict[str, Any]:
        return {
            "card": self.card,
            "model_id": self.model_id,
            "benchmark_id": self.benchmark_id,
            "legacy_value": self.legacy_value,
            "status": self.status,
            "reason": self.reason,
            "published_value": "" if self.published_value is None else self.published_value,
            "evidence_date": self.evidence_date,
            "source_url": self.source_url,
            "evidence_id": self.evidence_id,
        }


@dataclass
class Plan:
    changes: list[Change] = field(default_factory=list)
    sources: dict[str, dict[str, Any]] = field(default_factory=dict)


def _get(url: str, cache: Path) -> bytes:
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / (hashlib.sha256(url.encode()).hexdigest() + ".json")
    if path.is_file():
        return path.read_bytes()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=180) as response:  # noqa: S310
        body = response.read()
    path.write_bytes(body)
    return body


def _metadata(version: str, cache: Path) -> tuple[str, list[str]]:
    repository, revision = DATASETS[version]
    body = _get(f"https://huggingface.co/api/datasets/{repository}", cache)
    data = json.loads(body)
    if data.get("sha") != revision:
        raise RuntimeError(f"{repository} moved: expected {revision}, found {data.get('sha')}")
    return repository, [item["rfilename"] for item in data.get("siblings") or []]


def _hf_identity(front: dict[str, Any]) -> str | None:
    url = str((front.get("sources") or {}).get("huggingface_url") or "").rstrip("/")
    marker = "huggingface.co/"
    return url.split(marker, 1)[1] if marker in url and "/" in url.split(marker, 1)[1] else None


def _agrees(card: float, published: float) -> bool:
    places = len(str(card).partition(".")[2]) if isinstance(card, float) else 0
    return abs(float(card) - published) <= (0.5 * 10 ** -places) + 1e-12


def _projection(identity: str, evaluated: date, scores: dict[str, float], *,
                source_url: str, raw_ref: str) -> bytes:
    row = {"model": identity, "date": evaluated.isoformat(),
           **{key: f"{value}%" for key, value in scores.items()}}
    payload = {
        "source_url": source_url,
        "read_date": READ_DATE.isoformat(),
        "provenance": {
            "fetched_copy": raw_ref,
            "projection": "OLL result metrics converted from fractions to percent; aggregates are arithmetic means of the published subtasks",
        },
        "rows": [row],
    }
    return (json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n").encode()


def _published(version: str, path: str, repository: str, revision: str,
               cache: Path, store: CopyStore) -> PublishedResult:
    source_url = f"https://huggingface.co/datasets/{repository}/resolve/{revision}/{path}"
    raw = _get(source_url, cache)
    raw_ref = store.put(raw)
    data = json.loads(raw)
    identity, evaluated, scores = (
        extract_v1_scores(data, path) if version == "v1" else extract_v2_scores(data, path)
    )
    projection = _projection(identity, evaluated, scores, source_url=source_url, raw_ref=raw_ref)
    source_id = f"oll-{version}-{hashlib.sha256(path.encode()).hexdigest()[:12]}"
    return PublishedResult(version, path, source_url, source_id, identity, evaluated, scores,
                           store.put(projection))


def _result_paths(version: str, identity: str, siblings: list[str]) -> list[str]:
    prefix = identity.rstrip("/") + "/results_"
    return sorted(path for path in siblings if path.startswith(prefix) and path.endswith(".json"))


def _load_cards() -> list[tuple[Path, dict[str, Any]]]:
    cards = []
    for path in sorted((ROOT / "models").glob("*/*.md")):
        text = path.read_text(encoding="utf-8")
        if "open-llm-leaderboard" not in text:
            continue
        cards.append((path, yaml.safe_load(text.split("---", 2)[1])))
    return cards


def _candidate_jobs(cards: list[tuple[Path, dict[str, Any]]], cache: Path
                    ) -> tuple[dict[str, tuple[str, str, list[str]]], list[tuple[str, str]]]:
    metadata = {}
    jobs = []
    for version in DATASETS:
        repository, siblings = _metadata(version, cache)
        revision = DATASETS[version][1]
        metadata[version] = (repository, revision, siblings)
    for _, front in cards:
        source = str((front.get("benchmarks") or {}).get("benchmark_source") or "")
        identity = _hf_identity(front)
        if not identity:
            continue
        for version in DATASETS:
            if f"open-llm-leaderboard-{version}" in source:
                jobs.extend((version, path) for path in _result_paths(version, identity,
                            metadata[version][2]))
    return metadata, sorted(set(jobs))


def build_plan(cache: Path) -> Plan:
    cards = _load_cards()
    metadata, jobs = _candidate_jobs(cards, cache)
    store = CopyStore()

    def fetch(job: tuple[str, str]) -> PublishedResult | None:
        version, path = job
        repository, revision, _ = metadata[version]
        try:
            return _published(version, path, repository, revision, cache, store)
        except ValueError:
            # Early v1 files without a dated filename cannot supply the exact
            # evaluation date this migration requires.
            return None

    with ThreadPoolExecutor(max_workers=12) as pool:
        published = [result for result in pool.map(fetch, jobs) if result is not None]
    by_identity: dict[tuple[str, str], list[PublishedResult]] = {}
    for result in published:
        by_identity.setdefault((result.version, result.identity.casefold()), []).append(result)

    plan = Plan()
    for path, front in cards:
        block = front.get("benchmarks") or {}
        flat = block.get("scores") or {}
        existing = {row.get("benchmark_id") for row in block.get("evidence") or []}
        marker = str(block.get("benchmark_source") or "")
        identity = _hf_identity(front)
        model_id = str(front.get("model_id") or "")
        versions = [version for version in DATASETS
                    if f"open-llm-leaderboard-{version}" in marker]
        owned = set(V1_METRICS) | {f"mmlu_{name}" for name in _MMLU_SUBJECTS}
        if "v2" in versions:
            owned |= set(V2_KEYS)
        if "v1" not in versions:
            owned -= set(V1_METRICS) | {f"mmlu_{name}" for name in _MMLU_SUBJECTS}
        for benchmark_id in sorted(set(flat) & owned):
            change = Change(path.relative_to(ROOT).as_posix(), model_id, benchmark_id,
                            float(flat[benchmark_id]))
            plan.changes.append(change)
            if benchmark_id in existing:
                change.reason = "an evidence row already owns this benchmark"
                continue
            if not identity:
                change.reason = "card has no exact Hugging Face repository identity"
                continue
            version = "v2" if benchmark_id in V2_KEYS else "v1"
            results = by_identity.get((version, identity.casefold()), [])
            matches = [result for result in results
                       if benchmark_id in result.scores
                       and _agrees(change.legacy_value, result.scores[benchmark_id])]
            if not matches:
                change.reason = "no result file for the exact model states this value"
                continue
            chosen = max(matches, key=lambda result: (result.evaluated, result.path))
            row = {
                "benchmark_id": benchmark_id,
                "model_id_as_evaluated": chosen.identity,
                "score": change.legacy_value,
                "unit": "percent",
                "source_url": chosen.source_url,
                "source_kind": "benchmark_author",
                "evidence_date": chosen.evaluated.isoformat(),
                "date_type": "evaluated",
                "verified_at": READ_DATE.isoformat(),
                "benchmark_version": f"Open LLM Leaderboard {version}",
                "configuration": "Published per-model result; leaderboard metric converted from fraction to percent.",
                "limitations": "Static leaderboard result. The source file identifies the evaluated repository and run date.",
                "measured_by": "benchmark_author",
                "sources": [{
                    "source_id": chosen.source_id,
                    "snapshot_ref": chosen.snapshot_ref,
                    "cited_regions": ["rows"],
                }],
            }
            row["id"] = evidence_id(model_id, row)
            source_ref = SourceRef.model_validate(row["sources"][0])
            names = tuple(dict.fromkeys(filter(None, (
                chosen.identity, front.get("display_name"), model_id.rsplit("/", 1)[-1],
            ))))
            claim = Claim(
                target=TargetRef(kind="evidence", id=row["id"]),
                subject=model_id,
                names=names,
                field=benchmark_id,
                label=benchmark_id,
                value=row["score"],
                unit="percent",
                conditions={"effort": None, "harness": None,
                            "date": chosen.evaluated.isoformat()},
                collector=COLLECTOR,
                sources=(source_ref,),
            )
            change.reason = "awaiting modelspec verify"
            change.published_value = chosen.scores[benchmark_id]
            change.evidence_date = chosen.evaluated.isoformat()
            change.source_url = chosen.source_url
            change.evidence_id = row["id"]
            change.row = row
            change.claim = claim
            plan.sources[chosen.source_id] = {
                "id": chosen.source_id,
                "url": chosen.source_url,
                "fetch": "conditional_http",
                "normaliser": "text-default",
                "cited_regions": [{"id": "rows", "locator": {"kind": "page", "value": ""}}],
            }
    return plan


_MMLU_SUBJECTS = (
    "abstract_algebra anatomy astronomy business_ethics clinical_knowledge college_biology "
    "college_chemistry college_computer_science college_mathematics college_medicine "
    "college_physics computer_security conceptual_physics econometrics electrical_engineering "
    "elementary_mathematics formal_logic global_facts high_school_biology "
    "high_school_chemistry high_school_computer_science high_school_european_history "
    "high_school_geography high_school_government_and_politics high_school_macroeconomics "
    "high_school_mathematics high_school_microeconomics high_school_physics "
    "high_school_psychology high_school_statistics high_school_us_history "
    "high_school_world_history human_aging human_sexuality international_law jurisprudence "
    "logical_fallacies machine_learning management marketing medical_genetics miscellaneous "
    "moral_disputes moral_scenarios nutrition philosophy prehistory professional_accounting "
    "professional_law professional_medicine professional_psychology public_relations "
    "security_studies sociology us_foreign_policy virology world_religions"
).split()
V2_KEYS = ("ifeval", "bbh", "math_lvl5", "gpqa_pooled", "musr", "mmlu_pro")


def register_sources(plan: Plan) -> None:
    path = ROOT / "registry" / "sources.yaml"
    known = load_sources(path)
    new = [source for key, source in sorted(plan.sources.items()) if key not in known]
    if not new:
        return
    block = yaml.safe_dump(new, sort_keys=False, allow_unicode=True, width=100)
    with path.open("a", encoding="utf-8") as handle:
        handle.write("\n# MODEL-118: pinned Open LLM Leaderboard result files; read 2026-09-25.\n")
        handle.write(block)
    load_sources(path)


def collect(plan: Plan) -> None:
    register_sources(plan)
    queue = Queue(ROOT / "verification")
    now = datetime.now(UTC)
    for change in plan.changes:
        if change.claim is not None:
            queue.file(change.claim, at=now)


def _row_block(row: dict[str, Any]) -> str:
    dumped = yaml.safe_dump([row], sort_keys=False, allow_unicode=True, width=100).rstrip()
    return "\n".join("  " + line for line in dumped.splitlines()) + "\n"


def _apply_card(path: Path, changes: list[Change]) -> None:
    text = path.read_text(encoding="utf-8")
    for change in changes:
        pattern = re.compile(rf"(?m)^    {re.escape(change.benchmark_id)}:\s*[^\n]+\n")
        text, count = pattern.subn("", text, count=1)
        if count != 1:
            raise RuntimeError(f"{change.card}: could not remove {change.benchmark_id}")
    text = re.sub(r"(?m)^  scores:\n(?=  [a-z_]+:)", "  scores: {}\n", text)
    blocks = "".join(_row_block(change.row or {}) for change in changes)
    if re.search(r"(?m)^  evidence: \[\]\n", text):
        text = re.sub(r"(?m)^  evidence: \[\]\n", "  evidence:\n" + blocks, text, count=1)
    elif not re.search(r"(?m)^  evidence:\s*$", text):
        text = re.sub(r"(?m)^(  benchmark_source:)", "  evidence:\n" + blocks + r"\1",
                      text, count=1)
    else:
        text = re.sub(r"(?m)^  evidence:\s*$",
                      lambda match: match.group(0) + "\n" + blocks.rstrip("\n"),
                      text, count=1)
    path.write_text(text, encoding="utf-8")


def apply_verified(plan: Plan) -> None:
    latest = VerificationLog(ROOT / "verification").latest()
    by_card: dict[str, list[Change]] = {}
    for change in plan.changes:
        if change.row is None:
            continue
        record = latest.get(("evidence", change.evidence_id))
        if record is None or record.outcome != "verified" \
                or record.target.value_hash != value_hash(change.legacy_value):
            change.status = "quarantined"
            change.reason = record.outcome if record is not None else "not verified"
            continue
        change.row["verified_at"] = record.date.isoformat()
        change.status = "migrated"
        change.reason = "verified by modelspec verify"
        by_card.setdefault(change.card, []).append(change)
    for card, changes in by_card.items():
        _apply_card(ROOT / card, changes)


def write_audit(plan: Plan, path: Path) -> None:
    fields = list(plan.changes[0].audit_row()) if plan.changes else [
        "card", "model_id", "benchmark_id", "legacy_value", "status", "reason",
        "published_value", "evidence_date", "source_url", "evidence_id",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(change.audit_row() for change in plan.changes)


def summary(plan: Plan) -> str:
    statuses = Counter(change.status for change in plan.changes)
    benchmarks = Counter((change.benchmark_id, change.status) for change in plan.changes)
    lines = [f"{sum(statuses.values())} OLL flat values: " +
             ", ".join(f"{key}={value}" for key, value in sorted(statuses.items()))]
    lines.extend(f"{benchmark}: {status}={count}"
                 for (benchmark, status), count in sorted(benchmarks.items()))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("phase", choices=("collect", "apply", "dry-run"))
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--audit", type=Path,
                        default=ROOT / "docs/audits/model-118-oll-migration.csv")
    args = parser.parse_args(argv)
    plan = build_plan(args.cache_dir)
    if args.phase == "collect":
        collect(plan)
    elif args.phase == "apply":
        apply_verified(plan)
    write_audit(plan, args.audit)
    print(summary(plan))


if __name__ == "__main__":
    main()
