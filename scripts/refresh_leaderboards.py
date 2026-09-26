#!/usr/bin/env python3
"""Refresh existing premier-set evidence from registered live boards (MODEL-124).

The refresh is deliberately narrower than a collector: it cannot add a card or
an evidence row, and it never changes identity or licence facts.  Board readers
produce one retained projection per board observation. Existing rows are
matched against that projection. Changed and confirmed values both advance
their observation metadata and pass through the normal two-key verification
queue.
"""

from __future__ import annotations

import argparse
import copy
import io
import json
import re
import tempfile
import urllib.request
import zipfile
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import yaml

from decision.excluded import excluded_sources
from decision.model import SourceRef, TargetRef, VerificationActor
from decision.sources import CopyStore, load_sources
from decision.verify import (
    Claim,
    Queue,
    StoredRegions,
    VerificationLog,
    deterministic_extractors,
)
from decision.verify import (
    run as verify_claims,
)
from scripts import model_160_evidence as readers
from scripts.model_143_evidence import evidence_id, evidence_key

ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "ModelSpec-Leaderboard-Refresh/1.0 (+https://modelspec.dev)"
ARENA_DATASET = "lmarena-ai/leaderboard-dataset"
ARENA_REVISION = readers.ARENA_REVISION
ARENA_BOARDS = {
    **readers.ARENA,
    "arena_webdev": ("webdev", "overall"),
}
COLLECTOR = VerificationActor(
    agent="codex-model-124",
    model_family="openai",
    method="weekly-live-board-refresh@1",
)


def require_allowed_source(url: str, benchmark_ids: Iterable[str] = ()) -> None:
    """Refuse excluded publishers before any network request is made."""
    excluded = excluded_sources()
    if excluded.url(url) or any(excluded.benchmark(benchmark) for benchmark in benchmark_ids):
        raise ValueError(f"excluded source refused: {url}")
    if "lmarena" in url.casefold() and ARENA_DATASET not in url:
        raise ValueError("Arena must come from the pinned Hugging Face dataset")


@dataclass(frozen=True)
class BoardReading:
    key: str
    source_id: str
    benchmark_ids: frozenset[str]
    source_url: str
    observed_at: str
    rows: tuple[Mapping[str, Any], ...]
    value_field: str
    fraction: bool = False
    snapshot_ref: str | None = None
    card_urls: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        date.fromisoformat(self.observed_at)
        require_allowed_source(self.source_url, self.benchmark_ids)
        row_dates = {str(row["observed_at"]) for row in self.rows if row.get("observed_at")}
        if row_dates and row_dates != {self.observed_at}:
            raise ValueError(
                f"{self.key}: one observation date required; got {sorted(row_dates)}"
            )


@dataclass(frozen=True)
class ScoreChange:
    card: str
    model_id: str
    model: str
    benchmark: str
    old_value: float
    new_value: float
    source: str
    observed_date: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "card": self.card,
            "model": self.model_id,
            "benchmark": self.benchmark,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "source": self.source,
            "observed_date": self.observed_date,
            "pr": "${PR_URL}",
        }


@dataclass(frozen=True)
class RowObservation:
    card: str
    model_id: str
    model: str
    benchmark: str
    old_value: float
    new_value: float
    source: str
    observed_date: str

    @property
    def changed(self) -> bool:
        return self.old_value != self.new_value

    def score_change(self) -> ScoreChange:
        return ScoreChange(**self.__dict__)


@dataclass(frozen=True)
class RowFailure:
    model_id: str
    benchmark: str
    source: str
    reason: str


@dataclass(frozen=True)
class ScoreOnlyResult:
    ok: bool
    errors: tuple[str, ...] = ()


@dataclass
class RefreshReport:
    boards: dict[str, dict[str, Any]] = field(default_factory=dict)
    changes: list[ScoreChange] = field(default_factory=list)
    reconfirmed: list[RowObservation] = field(default_factory=list)
    failures: list[RowFailure] = field(default_factory=list)
    quarantined: list[RowFailure] = field(default_factory=list)

    def board(self, key: str) -> dict[str, Any]:
        return self.boards.setdefault(
            key,
            {"models_read": 0, "models_reconfirmed": 0, "values_changed": 0,
             "failures": []},
        )


def json_board(
    *,
    key: str,
    source_id: str,
    benchmark_ids: set[str],
    source_url: str,
    body: bytes,
    observed_at: str,
    value_field: str,
    fraction: bool = False,
    snapshot_ref: str | None = None,
) -> BoardReading:
    payload = json.loads(body)
    rows = payload["rows"] if isinstance(payload, Mapping) else payload
    return BoardReading(
        key=key,
        source_id=source_id,
        benchmark_ids=frozenset(benchmark_ids),
        source_url=source_url,
        observed_at=observed_at,
        rows=tuple(rows),
        value_field=value_field,
        fraction=fraction,
        snapshot_ref=snapshot_ref,
    )


def _subject(row: Mapping[str, Any]) -> str:
    return str(next((row[key] for key in (
        "model", "model_name", "Model version", "model_display", "name"
    ) if row.get(key)), ""))


def _value(board: BoardReading, row: Mapping[str, Any], unit: str | None) -> float:
    value = row[board.value_field]
    quantity = readers.parse_quantity(str(value)) if isinstance(value, str) else None
    number = quantity.number if quantity else value
    if board.fraction and unit == "percent":
        number *= 100
    return float(number)


def _match(board: BoardReading, evidence: Mapping[str, Any]) -> Mapping[str, Any] | None:
    wanted = str(evidence.get("model_id_as_evaluated") or "")
    effort = evidence.get("effort")
    without_claude = re.sub(r"^Claude[ -]", "", wanted)
    aliases = tuple(dict.fromkeys((wanted, without_claude, f"Claude {wanted}"
                                   if without_claude == wanted else wanted)))
    candidates = [row for row in board.rows if any(
        readers.normalise_name(_subject(row)) == readers.normalise_name(alias)
        for alias in aliases
    )]
    if len(candidates) != 1:
        identity, named_effort = readers.split_model_cell(wanted)
        wanted_effort = effort or named_effort
        candidates = [
            row for row in board.rows
            if any(readers.split_model_cell(_subject(row))[0] ==
                   readers.split_model_cell(alias)[0] for alias in aliases)
            and (wanted_effort is None or readers._effort(row) in (None, wanted_effort))
        ]
    if not candidates:
        wanted_tokens = sorted(readers.normalise_name(wanted).split())
        candidates = [row for row in board.rows
                      if sorted(readers.normalise_name(_subject(row)).split()) == wanted_tokens
                      and (effort is None or readers._effort(row) in (None, effort))]
    if len(candidates) > 1:
        # Versioned boards can publish several immutable releases under one benchmark
        # name. Re-confirm the version already named by the card only when exactly one
        # source row still states its value; otherwise a null/failure beats a guess.
        agreeing = []
        for row in candidates:
            try:
                value = _value(board, row, evidence.get("unit"))
                quantity = readers.parse_quantity(str(value), evidence.get("unit"))
                if readers.numbers_agree(evidence.get("score"), evidence.get("unit"), quantity):
                    agreeing.append(row)
            except (KeyError, TypeError, ValueError):
                pass
        candidates = agreeing
    return candidates[0] if len(candidates) == 1 else None


def _plan_observations(
    model_id: str,
    card: str,
    evidence_rows: Sequence[Mapping[str, Any]],
    board: BoardReading,
) -> tuple[list[RowObservation], list[RowFailure]]:
    """Plan observations of existing rows; never add one."""
    observations: list[RowObservation] = []
    failures: list[RowFailure] = []
    for evidence in evidence_rows:
        if evidence.get("benchmark_id") not in board.benchmark_ids:
            continue
        accepted_urls = board.card_urls or frozenset({board.source_url})
        if str(evidence.get("source_url") or "") not in accepted_urls:
            continue
        match = _match(board, evidence)
        if match is None or match.get(board.value_field) is None:
            failures.append(RowFailure(
                model_id, str(evidence.get("benchmark_id")), board.source_url,
                f"no unique row for {evidence.get('model_id_as_evaluated')!r}",
            ))
            continue
        new = _value(board, match, evidence.get("unit"))
        if str(evidence.get("benchmark_id", "")).startswith("arena_"):
            new = round(new, 2)
        old = float(evidence["score"])
        if readers.numbers_agree(old, evidence.get("unit"),
                                 readers.parse_quantity(str(new), evidence.get("unit"))):
            new = old
        observations.append(RowObservation(
            card=card,
            model_id=model_id,
            model=str(evidence.get("model_id_as_evaluated")),
            benchmark=str(evidence["benchmark_id"]),
            old_value=old,
            new_value=new,
            source=board.source_url,
            observed_date=board.observed_at,
        ))
    return observations, failures


def plan_rows(
    model_id: str,
    card: str,
    evidence_rows: Sequence[Mapping[str, Any]],
    board: BoardReading,
) -> tuple[list[ScoreChange], list[RowFailure]]:
    """Plan value changes for existing rows; never add one."""
    observations, failures = _plan_observations(model_id, card, evidence_rows, board)
    return [observation.score_change() for observation in observations
            if observation.changed], failures


def _rewrite_card(path: Path, updates: list[tuple[tuple[object, ...], dict[str, Any]]]) -> None:
    wanted = dict(updates)
    text = path.read_text(encoding="utf-8")
    fields = ("score", "observed_at", "verified_at", "id", "sources")

    def update(match: re.Match[str]) -> str:
        block = match.group(0).rstrip("\n")
        row = yaml.safe_load("evidence:\n" + block)["evidence"][0]
        replacement = wanted.pop(evidence_key(row), None)
        if replacement is None:
            return match.group(0)
        lines = block.splitlines()
        for name in fields:
            lines = readers._set_field(lines, name, replacement.get(name))
        return "\n".join(lines) + "\n"

    changed = re.sub(
        r"(?ms)^  - benchmark_id:.*?"
        r"(?=^  - benchmark_id:|^  [a-z][a-z0-9_]*:|^[a-z][a-z0-9_]*:|^---$|\Z)",
        update,
        text,
    )
    if wanted:
        raise ValueError(f"{path}: could not locate {len(wanted)} changed evidence rows")
    path.write_text(changed, encoding="utf-8")


def _claim(model_id: str, front: Mapping[str, Any], row: Mapping[str, Any],
           board: BoardReading) -> Claim:
    names = tuple(dict.fromkeys(filter(None, (
        row.get("model_id_as_evaluated"), front.get("display_name"), front.get("version"),
        model_id.rsplit("/", 1)[-1],
    ))))
    source = SourceRef(source_id=board.source_id, snapshot_ref=board.snapshot_ref,
                       cited_regions=["rows"])
    return Claim(
        target=TargetRef(kind="evidence", id=str(row["id"])),
        subject=model_id,
        names=names,
        field=str(row["benchmark_id"]),
        label=board.value_field,
        value=row["score"],
        unit=row.get("unit"),
        conditions={"effort": row.get("effort"), "harness": row.get("harness"),
                    "date": row.get("evidence_date")},
        collector=COLLECTOR,
        sources=(source,),
    )


def _premier_cards(root: Path) -> dict[str, Path]:
    selected = {row["model_id"] for row in
                yaml.safe_load((root / "premier" / "slice-1.yaml").read_text())[
                    "models"
                ]}
    cards: dict[str, Path] = {}
    for path in sorted((root / "models").glob("*/*.md")):
        front = _front(path)
        if front.get("model_id") in selected:
            cards[str(front["model_id"])] = path
    missing = selected - cards.keys()
    if missing:
        raise ValueError(f"premier cards missing: {', '.join(sorted(missing))}")
    return cards


def run(*, observed_at: str, dry_run: bool, root: Path = ROOT,
        source_cache: Path | None = None) -> RefreshReport:
    date.fromisoformat(observed_at)
    cards = _premier_cards(root)
    fronts = {model: _front(path) for model, path in cards.items()}
    tau_urls = {
        str(row["source_url"])
        for front in fronts.values()
        for row in (front.get("benchmarks") or {}).get("evidence") or []
        if row.get("benchmark_id") == "tau3_banking" and row.get("source_url")
    }
    store = CopyStore(source_cache)
    boards, board_failures = collect_readings(observed_at, store, tau_urls)
    report = RefreshReport(failures=list(board_failures))
    registered = load_sources(root / "registry" / "sources.yaml")
    queue = Queue(root / "verification")
    filed_at = datetime.combine(date.fromisoformat(observed_at), datetime.min.time(), UTC)
    pending_updates: dict[Path, list[tuple[tuple[object, ...], dict[str, Any]]]] = {}
    claims: list[Claim] = []

    for board in boards:
        summary = report.board(board.key)
        if board.source_id not in registered:
            failure = RowFailure("*", ",".join(sorted(board.benchmark_ids)), board.source_url,
                                 f"source is not registered: {board.source_id}")
            report.failures.append(failure)
            summary["failures"].append(failure.reason)
            continue
        models_read: set[str] = set()
        for model_id, path in cards.items():
            rows = (fronts[model_id].get("benchmarks") or {}).get("evidence") or []
            relevant = [row for row in rows
                        if row.get("benchmark_id") in board.benchmark_ids
                        and str(row.get("source_url") or "") in
                        (board.card_urls or frozenset({board.source_url}))]
            if not relevant:
                continue
            for row in relevant:
                if _match(board, row) is not None:
                    models_read.add(model_id)
            observations, failures = _plan_observations(
                model_id, path.relative_to(root).as_posix(), relevant, board
            )
            report.failures.extend(failures)
            summary["failures"].extend(failure.reason for failure in failures)
            reconfirmed_models: set[str] = set()
            for observation in observations:
                old = next(row for row in relevant
                           if row["benchmark_id"] == observation.benchmark
                           and row.get("model_id_as_evaluated") == observation.model
                           and float(row["score"]) == observation.old_value)
                new = dict(old)
                new["score"] = observation.new_value
                new["observed_at"] = observed_at
                new["verified_at"] = observed_at
                new["sources"] = [SourceRef(
                    source_id=board.source_id,
                    snapshot_ref=board.snapshot_ref,
                    cited_regions=["rows"],
                ).model_dump(mode="json")]
                new["id"] = evidence_id(model_id, new)
                pending_updates.setdefault(path, []).append((evidence_key(old), new))
                claims.append(_claim(model_id, fronts[model_id], new, board))
                if observation.changed:
                    report.changes.append(observation.score_change())
                else:
                    report.reconfirmed.append(observation)
                    reconfirmed_models.add(model_id)
            summary["models_reconfirmed"] += len(reconfirmed_models)
        summary["models_read"] = len(models_read)
        summary["values_changed"] = sum(1 for change in report.changes
                                         if change.source == board.source_url
                                         and change.benchmark in board.benchmark_ids)

    if dry_run or not pending_updates:
        return report

    for path, updates in pending_updates.items():
        _rewrite_card(path, updates)
    # Verify only this refresh's claims. The repository queue can contain unrelated
    # collection work; processing it here would make a score refresh mutate another
    # ticket's files. The real queue receives the same collected/checked events after
    # the isolated run, while the canonical verification log is written directly.
    with tempfile.TemporaryDirectory(prefix="modelspec-refresh-verify-") as temporary:
        isolated = Queue(Path(temporary) / "verification")
        for claim in claims:
            isolated.file(claim, at=filed_at)
        verification = verify_claims(
            isolated,
            VerificationLog(root / "verification"),
            StoredRegions(store, registered),
            deterministic_extractors(),
            today=date.fromisoformat(observed_at),
        )
    for claim in claims:
        queue.file(claim, at=filed_at)
    for result in verification.results:
        queue.checked(result, at=filed_at)
    changed_ids = {claim.target.id for claim in claims}
    claims_by_id = {claim.target.id: claim for claim in claims}
    for result in verification.results:
        if result.target.id not in changed_ids or result.outcome == "verified":
            continue
        claim = claims_by_id[result.target.id]
        failure = RowFailure(
            claim.subject,
            claim.field,
            str(registered[claim.sources[0].source_id].url),
            result.reason or result.outcome,
        )
        report.quarantined.append(failure)
    return report


def render_report(report: RefreshReport) -> str:
    lines = [
        "| Board | Models read | Models re-confirmed | Values changed | Failures |",
        "|---|---:|---:|---:|---:|",
    ]
    for board, result in sorted(report.boards.items()):
        lines.append(
            f"| {board} | {result['models_read']} | {result['models_reconfirmed']} | "
            f"{result['values_changed']} | {len(result['failures'])} |"
        )
    lines.extend(["", "## Score changes", "", audit_markdown(report.changes)])
    if report.failures:
        lines.extend(["", "## Failures", "",
                      "| Model | Benchmark | Source | Why |", "|---|---|---|---|"])
        lines.extend(f"| `{row.model_id}` | `{row.benchmark}` | {row.source} | {row.reason} |"
                     for row in report.failures)
    if report.quarantined:
        lines.extend(["", "## Quarantined", "",
                      "| Model | Facet | Source | Why |", "|---|---|---|---|"])
        lines.extend(f"| `{row.model_id}` | `{row.benchmark}` | {row.source} | {row.reason} |"
                     for row in report.quarantined)
    return "\n".join(lines)


_ALLOWED_EVIDENCE_FIELDS = frozenset({
    "score", "observed_at", "verified_at", "evidence_date", "id", "sources", "verification",
})


def _files(root: Path) -> dict[str, Path]:
    return {path.relative_to(root).as_posix(): path for path in root.rglob("*") if path.is_file()}


def _front(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---", 2)[1])


def _body(path: Path) -> str:
    return path.read_text(encoding="utf-8").split("---", 2)[2]


def _without_refresh_fields(front: Mapping[str, Any]) -> dict[str, Any]:
    data = copy.deepcopy(dict(front))
    evidence = ((data.get("benchmarks") or {}).get("evidence") or [])
    for row in evidence:
        for key in _ALLOWED_EVIDENCE_FIELDS:
            row.pop(key, None)
    return data


def check_score_only(before: Path, after: Path) -> ScoreOnlyResult:
    """Mechanically prove a generated refresh did not add cards or alter identities.

    Existing evidence rows may change only their score, observation/verification
    date, ID and source-snapshot binding. Verification JSONL files may only grow.
    """
    old, new = _files(before), _files(after)
    errors: list[str] = []
    for rel in sorted(new.keys() - old.keys()):
        if rel.startswith("models/") and rel.endswith(".md"):
            errors.append(f"card created: {rel}")
        elif rel not in {"verification/log.jsonl", "verification/queue/events.jsonl"}:
            errors.append(f"file created outside refresh outputs: {rel}")
    for rel in sorted(old.keys() - new.keys()):
        errors.append(f"file deleted: {rel}")
    for rel in sorted(old.keys() & new.keys()):
        if old[rel].read_bytes() == new[rel].read_bytes():
            continue
        if rel.startswith("models/") and rel.endswith(".md"):
            before_front, after_front = _front(old[rel]), _front(new[rel])
            before_rows = ((before_front.get("benchmarks") or {}).get("evidence") or [])
            after_rows = ((after_front.get("benchmarks") or {}).get("evidence") or [])
            if len(before_rows) != len(after_rows):
                errors.append(f"evidence row count changed: {rel}")
            if _without_refresh_fields(before_front) != _without_refresh_fields(after_front):
                errors.append(f"non-score card data changed: {rel}")
            if _body(old[rel]) != _body(new[rel]):
                errors.append(f"card prose changed: {rel}")
        elif rel in {"verification/log.jsonl", "verification/queue/events.jsonl"}:
            if not new[rel].read_bytes().startswith(old[rel].read_bytes()):
                errors.append(f"append-only file rewritten: {rel}")
        else:
            errors.append(f"file changed outside refresh outputs: {rel}")
    return ScoreOnlyResult(not errors, tuple(errors))


def audit_markdown(changes: Sequence[ScoreChange]) -> str:
    lines = [
        "| Model | Benchmark | Old value | New value | Source | Observed date | PR |",
        "|---|---|---:|---:|---|---|---|",
    ]
    lines.extend(
        f"| `{c.model_id}` | `{c.benchmark}` | {c.old_value:g} | {c.new_value:g} | "
        f"[{c.source}]({c.source}) | {c.observed_date} | ${{PR_URL}} |"
        for c in changes
    )
    return "\n".join(lines)


def write_audit(path: Path, changes: Sequence[ScoreChange]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([change.to_dict() for change in changes], indent=2) + "\n",
                    encoding="utf-8")


def write_report_json(path: Path, report: RefreshReport) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "boards": report.boards,
        "changes": [change.to_dict() for change in report.changes],
        "reconfirmed": [row.__dict__ for row in report.reconfirmed],
        "failures": [row.__dict__ for row in report.failures],
        "quarantined": [row.__dict__ for row in report.quarantined],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _fetch(url: str) -> bytes:
    require_allowed_source(url)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=180) as response:  # noqa: S310 - fixed registry URLs
        return response.read()


def _reading_from_projection(
    *, key: str, source_id: str, benchmarks: Iterable[str], source_url: str,
    projected: bytes, observed_at: str, value_field: str, store: CopyStore,
    fraction: bool = False, card_urls: Iterable[str] = (),
) -> BoardReading:
    payload = json.loads(projected)
    rows = tuple({**row, "observed_at": observed_at} for row in payload["rows"])
    return BoardReading(
        key, source_id, frozenset(benchmarks), source_url, observed_at, rows,
        value_field, fraction, store.put(projected), frozenset(card_urls),
    )


def _project_tbench(html: str, *, url: str, page_ref: str, observed_at: str) -> bytes:
    payload = readers._rsc_payload(html)
    lists: list[list[dict[str, Any]]] = []
    position = 0
    while True:
        try:
            start = payload.index('"rows":', position) + len('"rows":')
        except ValueError:
            break
        value, _ = json.JSONDecoder().raw_decode(payload, start)
        if (isinstance(value, list) and value and isinstance(value[0], Mapping)
                and {"metadata", "metrics"} <= set(value[0])):
            lists.append(value)
        position = start + 1
    if len(lists) != 1:
        raise ValueError(f"Terminal-Bench: expected one leaderboard row list, got {len(lists)}")
    rows = []
    for entry in lists[0]:
        metadata, metrics = entry["metadata"], entry["metrics"]
        rows.append({
            "model": (metadata["model_display"]["label"]
                      if isinstance(metadata.get("model_display"), Mapping)
                      else metadata["model_display"]),
            "reasoning_effort": metadata.get("reasoning_effort"),
            "agent": ((metadata.get("agent_display") or {}).get("label")
                      if isinstance(metadata.get("agent_display"), Mapping)
                      else metadata.get("agent_display")),
            "accuracy": metrics["accuracy"],
            "date": metadata.get("date"),
        })
    return readers.document(rows, url=url, page_ref=page_ref, read_date=observed_at,
                            note="dehydrated leaderboard query: metadata and metrics")


def _project_frontiercode(body: bytes, *, url: str, page_ref: str,
                          observed_at: str) -> bytes:
    board = json.loads(body)["v1_1"]
    rows = []
    for model, efforts in board["data"].items():
        for effort, datasets in efforts.items():
            result = datasets.get("main")
            if not result:
                continue
            rows.append({
                "model": model,
                "reasoning_effort": None if effort == "none" else effort,
                "score": f"{result['new_score'] * 100}%",
                "pass_rate": f"{result['correct'] * 100}%",
                "agent": board.get("harness", {}).get(model),
            })
    return readers.document(rows, url=url, page_ref=page_ref, read_date=observed_at,
                            note="v1_1.data.<model>.<effort>.main from the board JSON")


def _project_osworld(body: bytes, *, url: str, page_ref: str,
                     observed_at: str) -> bytes:
    payload = json.loads(body)
    rows = [{
        "model": row["model"],
        "reasoning_effort": row.get("reasoning"),
        "version": row.get("releaseVersion"),
        "binary_reward": f"{row['binaryAccuracy']}%",
        "partial_reward": f"{row['partialScore']}%",
    } for row in payload["results"] if row.get("official")]
    return readers.document(rows, url=url, page_ref=page_ref, read_date=observed_at,
                            note="official results from official-results.json")


def _project_scale_hle(html: str, *, url: str, page_ref: str,
                       observed_at: str) -> bytes:
    payload = readers._rsc_payload(html)
    rows: list[dict[str, Any]] | None = None
    position = 0
    while True:
        try:
            start = payload.index('"entries":', position) + len('"entries":')
        except ValueError:
            break
        value, _ = json.JSONDecoder().raw_decode(payload, start)
        if isinstance(value, list) and value and {"model", "score"} <= set(value[0]):
            rows = value
            break
        position = start + 1
    if rows is None:
        raise ValueError("Scale HLE: entries not found in React payload")
    projected = [{"model": row["model"].strip(), "accuracy": row["score"]} for row in rows]
    return readers.document(projected, url=url, page_ref=page_ref, read_date=observed_at,
                            note="entries from the page's React payload; score as accuracy")


def collect_readings(observed_at: str, store: CopyStore, tau_urls: Iterable[str]) \
        -> tuple[list[BoardReading], list[RowFailure]]:
    """Fetch every terms-compatible live board used by the premier snapshot."""
    readings: list[BoardReading] = []
    failures: list[RowFailure] = []

    def collect(key: str, source_id: str, benchmarks: Iterable[str], source_url: str,
                fetch_url: str, projector: Callable[..., bytes], value_field: str,
                *, fraction: bool = False, card_urls: Iterable[str] = ()) -> None:
        try:
            require_allowed_source(fetch_url, benchmarks)
            raw = _fetch(fetch_url)
            raw_ref = store.put(raw)
            projected = projector(raw, url=source_url, page_ref=f"{raw_ref} {fetch_url}",
                                  observed_at=observed_at)
            readings.append(_reading_from_projection(
                key=key, source_id=source_id, benchmarks=benchmarks, source_url=source_url,
                projected=projected, observed_at=observed_at, value_field=value_field,
                store=store, fraction=fraction, card_urls=card_urls or (source_url,),
            ))
        except Exception as exc:  # one failed board must not hide all other board results
            failures.append(RowFailure("*", ",".join(sorted(benchmarks)), source_url,
                                       f"{type(exc).__name__}: {exc}"))

    # Arena: only the pinned CC BY 4.0 Hugging Face dataset.
    for config in sorted({config for config, _ in ARENA_BOARDS.values()}):
        fetch_url = readers.ARENA_URL.format(config=config)
        try:
            raw = _fetch(fetch_url)
            raw_ref = store.put(raw)
            for benchmark, (cfg, category) in ARENA_BOARDS.items():
                if cfg != config:
                    continue
                projected = readers.project_arena(
                    raw, config, category, url=fetch_url, page_ref=raw_ref,
                    read_date=observed_at,
                )
                readings.append(_reading_from_projection(
                    key=f"arena:{benchmark}",
                    source_id=(
                        "model-143-evidence-arena-webdev-json"
                        if config == "webdev"
                        else readers.arena_source(config)
                    ),
                    benchmarks=(benchmark,), source_url=fetch_url, projected=projected,
                    observed_at=observed_at, value_field="rating", store=store,
                    card_urls=("https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset",),
                ))
        except Exception as exc:
            failures.append(RowFailure("*", f"arena:{config}", fetch_url,
                                       f"{type(exc).__name__}: {exc}"))

    # Epoch publishes one CC BY 4.0 archive; all files in this block share one fetch.
    try:
        archive_url = readers.EPOCH_ZIP
        raw = _fetch(archive_url)
        raw_ref = store.put(raw)
        epoch = {
            "frontiermath_tiers_1_3_v2": (
                "frontiermath_tiers_1_3_v2.csv",
                "model-143-evidence-epoch-frontiermath-tiers-1-3-v2-csv",
                "https://epoch.ai/frontiermath",
            ),
            "gpqa_diamond": (
                "gpqa_diamond.csv",
                "model-143-evidence-epoch-gpqa-diamond-csv",
                "https://epoch.ai/benchmarks/gpqa-diamond",
            ),
            "swe_bench_verified": (
                "swe_bench_verified.csv",
                "model-160-epoch-swe-bench-verified-csv",
                "https://epoch.ai/benchmarks/swe-bench-verified",
            ),
            "simpleqa_verified": (
                "simpleqa_verified.csv",
                "model-160-epoch-simpleqa-verified-csv",
                "https://epoch.ai/benchmarks/simpleqa-verified",
            ),
        }
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            for benchmark, (name, source_id, page_url) in epoch.items():
                projected = readers.project_epoch(
                    archive.read(name).decode(), url=page_url,
                    page_ref=f"{raw_ref} {archive_url}#{name}", read_date=observed_at,
                )
                readings.append(_reading_from_projection(
                    key=f"epoch:{benchmark}", source_id=source_id, benchmarks=(benchmark,),
                    source_url=page_url, projected=projected, observed_at=observed_at,
                    value_field="mean_score", fraction=True, store=store,
                    card_urls=(page_url,),
                ))
    except Exception as exc:
        failures.append(RowFailure("*", "epoch", readers.EPOCH_ZIP,
                                   f"{type(exc).__name__}: {exc}"))

    collect("matharena", "model-160-matharena-aime-2026", ("aime_2026",),
            readers.MATHARENA_URL, readers.MATHARENA_URL,
            lambda body, **kw: readers.project_matharena(body, read_date=observed_at,
                                                          **{k: v for k, v in kw.items()
                                                             if k != "observed_at"}),
            "accuracy")
    try:
        raw = _fetch(readers.METR_URL)
        raw_ref = store.put(raw)
        projected = readers.project_metr(raw, url=readers.METR_URL, page_ref=raw_ref,
                                         read_date=observed_at)
        for benchmark, label in (("metr_time_horizon_50", "p50_horizon_length"),
                                 ("metr_time_horizon_80", "p80_horizon_length")):
            readings.append(_reading_from_projection(
                key=f"metr:{benchmark}", source_id="model-160-metr-time-horizon-1-1",
                benchmarks=(benchmark,), source_url=readers.METR_URL,
                projected=projected, observed_at=observed_at, value_field=label,
                store=store, card_urls=(readers.METR_URL,),
            ))
    except Exception as exc:
        failures.append(RowFailure("*", "metr", readers.METR_URL,
                                   f"{type(exc).__name__}: {exc}"))

    # MTEB needs one projection per task-type/value column and language board.
    for key, url, benchmarks in (
        ("eng", readers.MTEB_URL, ("mteb_eng_v2", "mteb_v2_reranking", "mteb_v2_retrieval")),
        (
            "multilingual",
            "https://mteb-leaderboard-backend.hf.space/v1/benchmarks/"
            "MTEB(Multilingual,%20v2)/scores",
            ("mteb_multilingual_v2",),
        ),
    ):
        try:
            raw = _fetch(url)
            raw_ref = store.put(raw)
            projected = readers.project_mteb(raw, url=url, page_ref=raw_ref,
                                             read_date=observed_at)
            for benchmark in benchmarks:
                label = {
                    "mteb_v2_reranking": "reranking",
                    "mteb_v2_retrieval": "retrieval",
                }.get(benchmark, "mean_task")
                source_id = (
                    "model-160-mteb-eng-v2"
                    if key == "eng"
                    else "model-143-evidence-mteb-multilingual-v2-json"
                )
                readings.append(_reading_from_projection(
                    key=f"mteb:{benchmark}", source_id=source_id,
                    benchmarks=(benchmark,), source_url=url, projected=projected,
                    observed_at=observed_at, value_field=label, fraction=True, store=store,
                    card_urls=(url,),
                ))
        except Exception as exc:
            failures.append(RowFailure("*", f"mteb:{key}", url, f"{type(exc).__name__}: {exc}"))

    terminal_url = "https://www.tbench.ai/leaderboard/terminal-bench/4.0"
    collect("terminal-bench", "model-143-evidence-terminal-bench-4-0-json",
            ("terminal_bench_v4_0",), terminal_url, terminal_url,
            lambda body, **kw: _project_tbench(body.decode(), **kw), "accuracy")

    frontier_data = "https://cognition.com/data/frontiercode-leaderboard/data.json"
    collect("frontiercode", "model-160-frontiercode", ("frontiercode_v1_1",),
            readers.FRONTIERCODE_URL, frontier_data, _project_frontiercode, "score",
            card_urls=(readers.FRONTIERCODE_URL,))
    osworld_data = "https://osworld-v2.xlang.ai/static/data/leaderboard/official-results.json?v=leaderboard-v21-v1"
    collect("osworld", "model-160-osworld", ("osworld_2",), readers.OSWORLD_URL,
            osworld_data, _project_osworld, "binary_reward",
            card_urls=(readers.OSWORLD_URL,))

    collect("deepswe", "model-160-deepswe-v1-1", ("deepswe_v1_1",),
            "https://deepswe.datacurve.ai/artifacts/v1.1/leaderboard-live.json",
            readers.DEEPSWE_URL,
            lambda body, **kw: readers.project_deepswe(body, read_date=observed_at,
                                                        **{k: v for k, v in kw.items()
                                                           if k != "observed_at"}),
            "pass_at_1", fraction=True, card_urls=("https://deepswe.datacurve.ai/",))

    # The remaining MODEL-160 boards already have plain-HTTP projectors.
    collect("scale-pro", "model-160-scale-swe-bench-pro-public", ("swe_bench_pro",),
            readers.SCALE_URL, readers.SCALE_URL,
            lambda body, **kw: readers.project_scale(body.decode(), read_date=observed_at,
                                                      **{k: v for k, v in kw.items()
                                                         if k != "observed_at"}),
            "resolve_rate", card_urls=(readers.SCALE_URL, "https://labs.scale.com/leaderboard/swe_bench_pro"))
    hle_url = "https://labs.scale.com/leaderboard/humanitys_last_exam"
    collect("scale-hle", "model-143-evidence-scale-hle-json", ("hle",), hle_url,
            hle_url, lambda body, **kw: _project_scale_hle(body.decode(), **kw), "accuracy")
    collect("cursorbench", "model-160-cursorbench", ("cursorbench_4",), readers.CURSOR_URL,
            readers.CURSOR_URL,
            lambda body, **kw: readers.project_cursorbench(body.decode(), read_date=observed_at,
                                                            **{k: v for k, v in kw.items()
                                                               if k != "observed_at"}),
            "accuracy")

    # SWE-bench carries two named boards in one embedded JSON document.
    try:
        raw = _fetch(readers.SWEBENCH_URL)
        raw_ref = store.put(raw)
        for board_name, benchmark in (("Verified", "swe_bench_verified"),
                                      ("Multilingual", "swe_bench_multilingual")):
            projected = readers.project_swebench(raw.decode(), board_name,
                                                 url=readers.SWEBENCH_URL,
                                                 page_ref=raw_ref, read_date=observed_at)
            readings.append(_reading_from_projection(
                key=f"swebench:{benchmark}", source_id="model-160-swebench-leaderboard",
                benchmarks=(benchmark,), source_url=readers.SWEBENCH_URL,
                projected=projected, observed_at=observed_at, value_field="resolve_rate",
                store=store, card_urls=(readers.SWEBENCH_URL,),
            ))
    except Exception as exc:
        failures.append(RowFailure("*", "swebench", readers.SWEBENCH_URL,
                                   f"{type(exc).__name__}: {exc}"))

    # Vending-Bench data lives in a JS chunk named by its HTML shell.
    try:
        page = _fetch(readers.VENDING_URL).decode()
        for chunk_path in sorted(set(re.findall(r"/_app/immutable/[\w./-]+\.js", page))):
            chunk_url = "https://andonlabs.com" + chunk_path
            raw = _fetch(chunk_url)
            if b"{vb2:{" not in raw:
                continue
            raw_ref = store.put(raw)
            projected = readers.project_vending(raw.decode(), url=readers.VENDING_URL,
                                                page_ref=f"{raw_ref} {chunk_url}",
                                                read_date=observed_at)
            readings.append(_reading_from_projection(
                key="vending", source_id="model-160-vending-bench-2",
                benchmarks=("vending_bench_2",), source_url=readers.VENDING_URL,
                projected=projected, observed_at=observed_at, value_field="money_balance",
                store=store, card_urls=(readers.VENDING_URL,),
            ))
            break
        else:
            raise ValueError("Vending-Bench data chunk not found")
    except Exception as exc:
        failures.append(RowFailure("*", "vending_bench_2", readers.VENDING_URL,
                                   f"{type(exc).__name__}: {exc}"))

    for tau_url in sorted(tau_urls):
        slug = re.search(r"/submissions/([^/]+)/", tau_url).group(1)
        collect(f"tau:{slug}", f"model-160-tau-bench-{slug.replace('_', '-')}",
                ("tau3_banking",), tau_url, tau_url,
                lambda body, **kw: readers.project_tau(body, read_date=observed_at,
                                                        **{k: v for k, v in kw.items()
                                                           if k != "observed_at"}),
                "pass_1")
    return readings, failures


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--observed-at", default=date.today().isoformat())
    parser.add_argument("--audit-json", type=Path)
    parser.add_argument("--report-json", type=Path)
    args = parser.parse_args(argv)
    # The network collector is wired below; keeping the CLI here makes the pure
    # planning and diff guard independently testable.
    report = run(observed_at=args.observed_at, dry_run=args.dry_run)
    print(render_report(report))
    if args.audit_json:
        write_audit(args.audit_json, report.changes)
    if args.report_json:
        write_report_json(args.report_json, report)


if __name__ == "__main__":
    main()
