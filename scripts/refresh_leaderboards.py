#!/usr/bin/env python3
"""Refresh evidence from registered live boards (MODEL-124 and MODEL-113).

The weekly premier-set refresh updates existing evidence rows. In latest
mode, when a stored Arena revision is not the revision just read, every
catalogue card with a row on that benchmark is refreshed too, up to
``ARENA_ROWS_PER_RUN`` Arena rows. A release-signal
run may also add evidence to an explicitly selected existing card when one
registered board row matches exactly and the board has an unambiguous metadata
template. The refresh never adds a card or changes identity or licence facts.
The Arena revision is one setting. An explicit ``arena_latest`` argument
wins. Otherwise ``MODELSPEC_ARENA_REVISION`` is ``pinned`` when unset or
empty, or ``latest``. Any other value is an error that names the variable.
``--arena-latest`` requests ``latest``.
Board readers produce one retained projection per board observation. New,
changed and confirmed evidence passes through the normal two-key verification
queue.
"""

from __future__ import annotations

import argparse
import copy
import io
import json
import os
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
from decision.model import (
    SourceRef,
    TargetRef,
    VerificationActor,
    evidence_verification_value,
)
from decision.sources import CopyStore, load_sources
from decision.units import unit_id
from decision.verify import (
    Claim,
    Queue,
    StoredRegions,
    VerificationLog,
    deterministic_extractors,
    numbers_agree,
    parse_quantity,
    reading_effort,
    split_model_cell,
    structured_name_effort,
)
from decision.verify import (
    run as verify_claims,
)
from scripts import model_160_evidence as readers
from scripts.model_143_evidence import evidence_id, evidence_key, measured_by

#: A configuration cites the day the board was read as the standalone word ``read``
#: and a date. A hyphenated word such as ``re-read`` is not that citation.
_READ_DATE = re.compile(r"(?<![\w-])read \d{4}-\d{2}-\d{2}\b")
#: The same citation in a folded YAML scalar, where the date can sit on the next line.
_READ_DATE_FOLDED = re.compile(
    r"(?<![\w-])read(?:[ \t]+|[ \t]*\n[ \t]+)(\d{4}-\d{2}-\d{2})\b"
)
#: Projector columns that are the row's own measurement or publish date.
_SOURCE_DATE_KEYS = ("date", "leaderboard_publish_date", "started_at", "Started at", "release_date")
#: Card vocabulary for a row dated by the observation. The decision contract
#: publishes this value as ``observed``.
OBSERVATION_DATE_TYPE = "evaluated"

ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "ModelSpec-Leaderboard-Refresh/1.0 (+https://modelspec.dev)"
ARENA_DATASET = "lmarena-ai/leaderboard-dataset"
ARENA_DATASET_ROOT = "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset"
ARENA_REVISION = readers.ARENA_REVISION
#: Arena evidence rows written in one run. Premier cards are written first.
#: Rows past this wait for the next run.
ARENA_ROWS_PER_RUN = 1200
#: Unit ``StructuredDataExtractor`` assigns to a rating column. A card unit on
#: another dimension cannot be refreshed: the guard refuses a unit edit, and the
#: verifier would record a mismatch.
_ARENA_RATING_UNIT = "Arena score (Elo scale)"
ARENA_BOARDS = {
    **readers.ARENA,
    "arena_webdev": ("webdev", "overall"),
}
MTEB_API = "https://mteb-leaderboard-backend.hf.space/v1/benchmarks/{}/scores"
#: (key, board URL, registered source, {benchmark id: projected column}, stored unit). A task-type
#: column is the board's own mean over that type's tasks; the board publishes it only
#: for a model scored on every one of them (MODEL-242).
MTEB_BOARDS = (
    ("eng", readers.MTEB_URL, "model-160-mteb-eng-v2",
     {"mteb_eng_v2": "mean_task", "mteb_v2_reranking": "reranking",
      "mteb_v2_retrieval": "retrieval"}, "percent"),
    ("multilingual", MTEB_API.format("MTEB(Multilingual,%20v2)"),
     "model-143-evidence-mteb-multilingual-v2-json",
     {"mteb_multilingual_v2": "mean_task", "mteb_multilingual_v2_reranking": "reranking"},
     "percent"),
    ("cmn", MTEB_API.format("MTEB(cmn,%20v1)"), "model-242-mteb-cmn-v1-json",
     {"mteb_cmn_v1_reranking": "reranking"}, "percent"),
    ("followir", MTEB_API.format("FollowIR"), "model-242-mteb-followir-json",
     {"followir": "mean_task"}, "p-MRR (x100)"),
)
MTEB_ROW = {"unit": "percent", "source_kind": "benchmark_author"}
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
    #: ``unit`` and ``source_kind`` for a row the board adds. A board that declares
    #: them can seed a benchmark no card carries yet; otherwise a card row is the template.
    row_template: Mapping[str, str] | None = None

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
    evidence_date: str
    #: ``source_publishes_row_date`` on the card row's source URL.
    source_dated: bool = False
    #: The matched dataset row's reading. Empty until ``_plan_observations`` fills it.
    reading_interval: tuple[float, float] | None = None
    reading_n: int | None = None
    reading_effort: str | None = None
    reading_publish_date: str | None = None
    reading_revision: str = ""
    reading_checked: bool = False
    reading_rank: int | None = None

    @property
    def changed(self) -> bool:
        return self.old_value != self.new_value

    def score_change(self) -> ScoreChange:
        return ScoreChange(
            card=self.card,
            model_id=self.model_id,
            model=self.model,
            benchmark=self.benchmark,
            old_value=self.old_value,
            new_value=self.new_value,
            source=self.source,
            observed_date=self.observed_date,
        )


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
    added: int = 0
    #: Arena rows past ``ARENA_ROWS_PER_RUN`` in this run.
    arena_rows_left: int = 0
    arena_revision: str = ""
    arena_revision_fallback: str | None = None
    arena_revision_latest: bool = False

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
    if board.fraction and unit_id(unit) in {"percent", "p-mrr (x100)"}:
        number *= 100
    return float(number)


def _iso_day(value: object) -> str:
    if hasattr(value, "isoformat"):
        return value.isoformat()[:10]
    return str(value or "").split("T", 1)[0]


def _source_measurement_date(row: Mapping[str, Any]) -> str | None:
    """The projector row's own measurement or publish day, when it has one."""
    for key in _SOURCE_DATE_KEYS:
        if value := row.get(key):
            return str(value).split("T", 1)[0]
    return None


def _evidence_date(board: BoardReading, row: Mapping[str, Any]) -> str:
    """Use the row's measurement date, or the live board's observation date."""
    return _source_measurement_date(row) or board.observed_at


def observation_dated(
    evidence_date: object, observed_at: object, *, source_dated: bool = False,
) -> bool:
    """True when the evidence day is the observation and the projector publishes no row date.

    ``source_dated`` is ``source_publishes_row_date`` for the row's source URL.
    A dated projector stays a measurement, including when this row's date is
    missing and when the measurement day is the observation day.
    """
    if source_dated:
        return False
    evidence, observed = _iso_day(evidence_date), _iso_day(observed_at)
    return bool(evidence) and evidence == observed


def source_publishes_row_date(source_url: str) -> bool:
    """True when this source URL's projector publishes a per-row date.

    The live writer, ``align_observation_cards`` and ``check_score_only`` all
    call this. The URL is the whole rule. A missing date on the projected row
    does not change it: Epoch sets ``date`` to ``None`` for an empty
    ``Started at``, and ``document`` drops that key. An unknown URL is dated.
    Only ``_OBSERVATION_SOURCE_URLS`` publish no per-row date.
    """
    return source_url not in _OBSERVATION_SOURCE_URLS


def align_observation_dating(row: Mapping[str, Any]) -> dict[str, Any]:
    """Make configuration text and date_type match an observation-dated row.

    ``source_publishes_row_date`` on the row's source URL decides. A dated
    projector stays as written, including when its date value is missing.
    An observation source whose evidence day is the observation day gets
    ``read <that date>`` and date_type ``evaluated``. The citation is the
    standalone word ``read``. ``re-read`` stays as written.
    """
    updated = dict(row)
    if not observation_dated(
        updated.get("evidence_date"),
        updated.get("observed_at"),
        source_dated=source_publishes_row_date(str(updated.get("source_url") or "")),
    ):
        return updated
    day = _iso_day(updated.get("evidence_date"))
    configuration = updated.get("configuration")
    if isinstance(configuration, str) and configuration:
        updated["configuration"] = _READ_DATE.sub(f"read {day}", configuration)
    if updated.get("date_type") == "published":
        updated["date_type"] = OBSERVATION_DATE_TYPE
    return updated


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


def _numbers_close(claimed: float, found: object) -> bool:
    quantity = parse_quantity(str(found))
    return quantity is not None and numbers_agree(float(claimed), None, quantity)


def _matched_interval(
    row: Mapping[str, Any], score: float,
) -> tuple[tuple[float, float] | None, str | None]:
    """Rounded rating bounds that contain ``score``, or a reason not to write."""
    lower, upper = row.get("rating_lower"), row.get("rating_upper")
    if lower is None and upper is None:
        return None, None
    if lower is None or upper is None:
        return None, "matched row states only one side of the interval"
    lo, hi = round(float(lower), 2), round(float(upper), 2)
    if score < lo:
        lo = round(float(score), 2)
    if score > hi:
        hi = round(float(score), 2)
    if lo > hi or not (lo <= score <= hi):
        return None, "matched interval does not contain the score"
    if not _numbers_close(lo, lower) or not _numbers_close(hi, upper):
        return None, "matched interval does not contain the score"
    return (lo, hi), None


def _matched_rank(row: Mapping[str, Any]) -> int | None:
    value = row.get("rank")
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not number.is_integer():
        return None
    return int(number)


def _matched_votes(row: Mapping[str, Any]) -> int | None:
    value = row.get("vote_count")
    if value is None:
        value = row.get("n")
    if value is None:
        return None
    return int(value)


def _verifier_names(
    model_id: str, front: Mapping[str, Any], evidence: Mapping[str, Any],
) -> tuple[str, ...]:
    """The names ``_claim`` gives the verifier for this evidence row."""
    return tuple(dict.fromkeys(filter(None, (
        evidence.get("model_id_as_evaluated"), front.get("display_name"), front.get("version"),
        model_id.rsplit("/", 1)[-1],
    ))))


def _verifier_owns(subject: str, names: Sequence[str]) -> bool:
    """Whether the verifier treats ``subject`` as this card's own row."""
    identity = split_model_cell(subject.replace("+", " plus "))[0]
    if not identity:
        return False
    return any(
        identity == split_model_cell(str(name).replace("+", " plus "))[0] for name in names
    )


def _dataset_effort(row: Mapping[str, Any]) -> str | None:
    column = row.get("reasoning_effort")
    if column is None:
        column = row.get("effort")
    return reading_effort(_subject(row), column)


def effort_named_on_card(model_id_as_evaluated: str) -> str | None:
    """Effort named by the card id, counting a hyphen as a space.

    The verifier's pattern does not treat a hyphen as a separator, so
    ``example-model-high`` names nothing until the hyphens become spaces.
    This is the only value a null effort may become.
    """
    text = str(model_id_as_evaluated or "")
    found = structured_name_effort(text)
    if found is None:
        found = structured_name_effort(text.replace("-", " "))
    if found is None:
        return None
    return reading_effort("", found)


_REVISION_QUOTE = re.compile(r"(?i)\brevision\s+([0-9a-f]{7,40})\b")
_PUBLISH_QUOTE = re.compile(
    r"(?i)\b(?:publication date|leaderboard_publish_date)\s+(\d{4}-\d{2}-\d{2})\b"
)
_OBSERVED_QUOTE = re.compile(r"(?i)\bObserved\s+(\d{4}-\d{2}-\d{2})\b")
_RATING_QUOTE = re.compile(r"(?i)\brating\s+(-?\d+(?:\.\d+)?)")
_BRACKET_QUOTE = re.compile(r"\[\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\]")
_CI_QUOTE = re.compile(
    r"(?i)\b(?:ci|interval)\s+(-?\d+(?:\.\d+)?)\s*[-–]\s*(-?\d+(?:\.\d+)?)"
)
_VOTES_QUOTE = re.compile(r"(?i)(?<!\w)(-?\d+(?:\.\d+)?)\s+votes\b")
_RANK_QUOTE = re.compile(r"(?i)\brank\s+(\d+)\b")
_EFFORT_QUOTE = re.compile(
    r"(?i)(\(effort:\s*)(minimal|low|medium|high|xhigh|max)\b"
)
_NUMBER_TOKEN = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?(?![\w.])")


def _format_like(literal: str, value: float) -> str:
    if "." in literal:
        return f"{value:.{len(literal.split('.', 1)[1])}f}"
    rounded = round(value)
    if abs(value - rounded) < 1e-9:
        return str(int(rounded))
    return f"{value:.2f}"


def _retell_reading(
    text: object,
    *,
    old_score: float,
    new_score: float,
    old_interval: object,
    new_interval: tuple[float, float] | None,
    old_n: object,
    new_n: int | None,
    old_dates: tuple[str, ...],
    new_publish: str | None,
    new_observed: str,
    new_revision: str,
    new_effort: str | None,
    new_rank: int | None = None,
) -> str | None:
    """Rewrite quoted publish date, rating, interval, votes, rank and revision.

    Returns None when a labeled quote cannot be replaced without leaving the
    previous reading in the sentence. A sentence that quotes none of those
    is returned unchanged. A quoted rank with no replacement rank is refused.
    """
    if not isinstance(text, str) or not text:
        return text if isinstance(text, str) else ""
    unsafe = False
    quoted_score = False
    quoted_interval = False
    quoted_votes = False
    quoted_rank = False
    quoted_publish = False
    quoted_revision = False
    old_rank_number: float | None = None
    old_hex = ""
    loose_numbers: list[float] = []

    def rating(match: re.Match[str]) -> str:
        nonlocal unsafe, quoted_score
        literal = match.group(1)
        if not _numbers_close(old_score, literal):
            unsafe = True
            return match.group(0)
        quoted_score = True
        return match.group(0).replace(literal, _format_like(literal, new_score), 1)

    def bounds(match: re.Match[str]) -> str:
        nonlocal unsafe, quoted_interval
        left, right = match.group(1), match.group(2)
        if new_interval is None:
            unsafe = True
            return match.group(0)
        if old_interval is None:
            # The interval is quoted in the sentence and absent from the field.
            # Rewrite it only when the quote contains the score it belongs to.
            low, high = float(left), float(right)
            if low > high or not (low <= float(old_score) <= high):
                unsafe = True
                return match.group(0)
            loose_numbers.extend((low, high))
        else:
            low, high = old_interval
            if not _numbers_close(float(low), left) or not _numbers_close(float(high), right):
                unsafe = True
                return match.group(0)
        quoted_interval = True
        rewritten = match.group(0).replace(left, _format_like(left, new_interval[0]), 1)
        return rewritten.replace(right, _format_like(right, new_interval[1]), 1)

    def votes(match: re.Match[str]) -> str:
        nonlocal unsafe, quoted_votes
        literal = match.group(1)
        if new_n is None:
            unsafe = True
            return match.group(0)
        if old_n is not None and not _numbers_close(float(old_n), literal):
            unsafe = True
            return match.group(0)
        if old_n is None:
            loose_numbers.append(float(literal))
        quoted_votes = True
        return match.group(0).replace(literal, _format_like(literal, float(new_n)), 1)

    def rank(match: re.Match[str]) -> str:
        nonlocal unsafe, quoted_rank, old_rank_number
        literal = match.group(1)
        if new_rank is None:
            unsafe = True
            return match.group(0)
        quoted_rank = True
        old_rank_number = float(literal)
        return match.group(0).replace(literal, str(int(new_rank)), 1)

    def published(match: re.Match[str]) -> str:
        nonlocal unsafe, quoted_publish
        if not new_publish:
            unsafe = True
            return match.group(0)
        quoted_publish = True
        return match.group(0).replace(match.group(1), new_publish, 1)

    def observed(match: re.Match[str]) -> str:
        return match.group(0).replace(match.group(1), new_observed, 1)

    hexes = {item.lower() for item in _REVISION_QUOTE.findall(text)}
    if len(hexes) > 1:
        return None
    vote_quotes = {float(value) for value in _VOTES_QUOTE.findall(text)}
    if len(vote_quotes) > 1:
        return None
    bracket_quotes = {(float(low), float(high)) for low, high in _BRACKET_QUOTE.findall(text)}
    if len(bracket_quotes) > 1:
        return None
    rank_quotes = {int(value) for value in _RANK_QUOTE.findall(text)}
    if len(rank_quotes) > 1:
        return None
    if hexes:
        old_hex = next(iter(hexes))
        if not new_revision:
            return None
        quoted_revision = True
        if not new_revision.lower().startswith(old_hex):
            shortened = new_revision.lower()[:len(old_hex)]

            def revision(match: re.Match[str]) -> str:
                return match.group(0).replace(match.group(1), shortened, 1)

            text = _REVISION_QUOTE.sub(revision, text)

    text = _RATING_QUOTE.sub(rating, text)
    text = _BRACKET_QUOTE.sub(bounds, text)
    text = _CI_QUOTE.sub(bounds, text)
    text = _VOTES_QUOTE.sub(votes, text)
    text = _RANK_QUOTE.sub(rank, text)
    text = _PUBLISH_QUOTE.sub(published, text)
    text = _OBSERVED_QUOTE.sub(observed, text)
    if new_effort and _EFFORT_QUOTE.search(text):
        found_levels = {match.group(2).casefold() for match in _EFFORT_QUOTE.finditer(text)}
        if len(found_levels) > 1:
            return None
        text = _EFFORT_QUOTE.sub(lambda match: f"{match.group(1)}{new_effort}", text)
    if unsafe:
        return None
    if quoted_score or quoted_interval or quoted_votes or quoted_rank:
        watched: list[float] = []
        if quoted_score:
            watched.append(float(old_score))
        if quoted_interval and old_interval is not None:
            watched.extend(float(item) for item in old_interval)
        if quoted_votes and old_n is not None:
            watched.append(float(old_n))
        if quoted_rank and old_rank_number is not None:
            watched.append(old_rank_number)
        watched.extend(loose_numbers)
        fresh = [float(new_score)]
        if new_interval is not None:
            fresh.extend(new_interval)
        if new_n is not None:
            fresh.append(float(new_n))
        if quoted_rank and new_rank is not None:
            fresh.append(float(new_rank))
        for token in _NUMBER_TOKEN.findall(text):
            value = float(token)
            stale = any(_numbers_close(old, value) for old in watched)
            current = any(_numbers_close(item, value) for item in fresh)
            if stale and not current:
                return None
    if quoted_publish:
        allowed = {day for day in (new_publish, new_observed) if day}
        for day in old_dates:
            if day and day not in allowed and day in text:
                return None
    if quoted_revision and old_hex and old_hex in text:
        if not new_revision.lower().startswith(old_hex):
            return None
    return text


def _copy_matched_reading(
    old: Mapping[str, Any], observation: RowObservation, *, observed_at: str,
) -> tuple[dict[str, Any] | None, str | None]:
    """Copy the matched reading onto ``old``. None when that would contradict it."""
    new = dict(old)
    if not observation.reading_checked:
        new["score"] = observation.new_value
        return new, None
    current = None if old.get("effort") in (None, "") else reading_effort("", old.get("effort"))
    dataset = observation.reading_effort
    named = effort_named_on_card(str(old.get("model_id_as_evaluated") or ""))
    if dataset is None:
        if current is not None:
            return None, "matched effort contradicts the card"
        written_effort = None
    elif current is None:
        if dataset != named:
            return None, "matched effort is not the effort named on model_id_as_evaluated"
        written_effort = dataset
    elif current == dataset:
        written_effort = current
    else:
        return None, "matched effort contradicts the card"
    if old.get("interval") is not None and observation.reading_interval is None:
        return None, "matched row does not state the interval this row quotes"
    if old.get("n") is not None and observation.reading_n is None:
        return None, "matched row does not state the vote count this row quotes"
    if _RANK_QUOTE.search(str(old.get("configuration") or "")) and observation.reading_rank is None:
        return None, "configuration quotes a rank the matched row does not state"
    new["score"] = observation.new_value
    if observation.reading_interval is not None:
        new["interval"] = [observation.reading_interval[0], observation.reading_interval[1]]
    if observation.reading_n is not None:
        new["n"] = observation.reading_n
    if written_effort != current:
        new["effort"] = written_effort
    old_dates = tuple(dict.fromkeys(filter(None, (
        _iso_day(old.get("evidence_date")), _iso_day(old.get("observed_at")),
    ))))
    told = _retell_reading(
        old.get("configuration") or "",
        old_score=float(old.get("score")),
        new_score=float(observation.new_value),
        old_interval=old.get("interval"),
        new_interval=observation.reading_interval,
        old_n=old.get("n"),
        new_n=observation.reading_n,
        old_dates=old_dates,
        new_publish=observation.reading_publish_date,
        new_observed=_iso_day(observed_at),
        new_revision=observation.reading_revision,
        new_effort=written_effort,
        new_rank=observation.reading_rank,
    )
    if told is None:
        return None, "configuration still quotes the previous reading"
    version = _retell_reading(
        old.get("benchmark_version") or "",
        old_score=float(old.get("score")),
        new_score=float(observation.new_value),
        old_interval=old.get("interval"),
        new_interval=observation.reading_interval,
        old_n=old.get("n"),
        new_n=observation.reading_n,
        old_dates=old_dates,
        new_publish=observation.reading_publish_date,
        new_observed=_iso_day(observed_at),
        new_revision=observation.reading_revision,
        new_effort=written_effort,
        new_rank=observation.reading_rank,
    )
    if version is None:
        return None, "benchmark_version still quotes the previous reading"
    if told != (old.get("configuration") or ""):
        new["configuration"] = told
    if version != (old.get("benchmark_version") or ""):
        new["benchmark_version"] = version
    return new, None


def _plan_observations(
    model_id: str,
    card: str,
    evidence_rows: Sequence[Mapping[str, Any]],
    board: BoardReading,
    *,
    revision: str = "",
    front: Mapping[str, Any] | None = None,
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
        arena = str(evidence.get("benchmark_id", "")).startswith("arena_")
        if arena and front is not None:
            names = _verifier_names(model_id, front, evidence)
            if not _verifier_owns(_subject(match), names):
                failures.append(RowFailure(
                    model_id, str(evidence.get("benchmark_id")), board.source_url,
                    "matched row is not a row the verifier reads",
                ))
                continue
        raw = _value(board, match, evidence.get("unit"))
        old = float(evidence["score"])
        if arena:
            found = readers.parse_quantity(str(match.get(board.value_field)), _ARENA_RATING_UNIT)
            rounded = round(raw, 2)
            if found is not None and readers.numbers_agree(old, evidence.get("unit"), found):
                new = old
            elif found is not None and readers.numbers_agree(rounded, evidence.get("unit"), found):
                new = rounded
            else:
                failures.append(RowFailure(
                    model_id, str(evidence.get("benchmark_id")), board.source_url,
                    "matched rating does not agree in the card's unit",
                ))
                continue
        else:
            new = raw
            if readers.numbers_agree(old, evidence.get("unit"),
                                     readers.parse_quantity(str(new), evidence.get("unit"))):
                new = old
        interval, interval_reason = _matched_interval(match, new)
        if interval_reason:
            failures.append(RowFailure(
                model_id, str(evidence.get("benchmark_id")), board.source_url,
                interval_reason,
            ))
            continue
        source_date = _source_measurement_date(match)
        cited = _cited_shas(board.source_url)
        arena_board = board.key.startswith("arena:")
        # The Arena revision belongs to Arena boards. Another board keeps a
        # commit its own URL cites, and otherwise none.
        board_revision = (cited[-1] if cited else revision) if arena_board else (cited[-1] if cited else "")
        observations.append(RowObservation(
            card=card,
            model_id=model_id,
            model=str(evidence.get("model_id_as_evaluated")),
            benchmark=str(evidence["benchmark_id"]),
            old_value=old,
            new_value=new,
            source=board.source_url,
            observed_date=board.observed_at,
            evidence_date=source_date or board.observed_at,
            source_dated=source_publishes_row_date(str(evidence.get("source_url") or "")),
            reading_interval=interval if arena_board else None,
            reading_n=_matched_votes(match) if arena_board else None,
            reading_effort=_dataset_effort(match) if arena_board else None,
            reading_publish_date=source_date if arena_board else None,
            reading_revision=board_revision,
            reading_checked=arena_board,
            reading_rank=_matched_rank(match) if arena_board else None,
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


def _replace_folded_read_date(text: str, day: str) -> str:
    """Replace the date in ``read <date>``, including when YAML folded it onto the next line."""
    return _READ_DATE_FOLDED.sub(lambda match: match.group(0).replace(match.group(1), day, 1), text)


def _patch_configuration_read_date(lines: list[str], day: str) -> list[str]:
    """Replace ``read YYYY-MM-DD`` inside the configuration field, and nowhere else."""
    start = next((i for i, line in enumerate(lines) if line.startswith("    configuration:")), None)
    if start is None:
        return lines
    end = start + 1
    while end < len(lines) and not re.match(r"^    [a-z][a-z0-9_]*:", lines[end]):
        end += 1
    chunk = _replace_folded_read_date("\n".join(lines[start:end]), day)
    return [*lines[:start], *chunk.split("\n"), *lines[end:]]


def _rewrite_card(
    path: Path,
    updates: list[tuple[tuple[object, ...], dict[str, Any]]],
    *,
    fields: Sequence[str] | None = None,
) -> None:
    from schema.benchmark_values import validate_card_rows

    validate_card_rows(path, [row for _, row in updates])
    wanted = dict(updates)
    text = path.read_text(encoding="utf-8")
    always = ("score", "evidence_date", "observed_at", "verified_at", "id", "sources")

    def update(match: re.Match[str]) -> str:
        block = match.group(0).rstrip("\n")
        row = yaml.safe_load("evidence:\n" + block)["evidence"][0]
        replacement = wanted.pop(evidence_key(row), None)
        if replacement is None:
            return match.group(0)
        lines = block.splitlines()
        if fields is None:
            names = [
                name for name in (
                    *always, "date_type", "configuration", "interval", "n",
                    "effort", "benchmark_version",
                )
                if name in always or replacement.get(name) != row.get(name)
            ]
        else:
            names = [name for name in fields if replacement.get(name) != row.get(name)]
        day = _iso_day(replacement.get("evidence_date"))
        old_configuration, new_configuration = row.get("configuration"), replacement.get("configuration")
        patch_read_date = (
            "configuration" in names
            and isinstance(old_configuration, str)
            and isinstance(new_configuration, str)
            and _READ_DATE.sub(f"read {day}", old_configuration) == new_configuration
        )
        if patch_read_date:
            names = [name for name in names if name != "configuration"]
        for name in names:
            lines = readers._set_field(lines, name, replacement.get(name))
        if patch_read_date:
            lines = _patch_configuration_read_date(lines, day)
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


def align_observation_cards(root: Path) -> list[str]:
    """Rewrite stored rows whose source URL is an observation projector.

    Returns the card paths that changed, relative to ``root``. Classification
    is ``source_publishes_row_date``. A dated projector is left alone, including
    when its evidence day is already the observation day and when its date
    value is missing.
    """
    changed: list[str] = []
    for path in sorted((root / "models").glob("*/*.md")):
        front = _front(path)
        rows = ((front.get("benchmarks") or {}).get("evidence") or [])
        updates = []
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            aligned = align_observation_dating(row)
            if (
                aligned.get("configuration") != row.get("configuration")
                or aligned.get("date_type") != row.get("date_type")
            ):
                updates.append((evidence_key(row), aligned))
        if not updates:
            continue
        before = path.read_text(encoding="utf-8")
        _rewrite_card(path, updates, fields=("date_type", "configuration"))
        if path.read_text(encoding="utf-8") == before:
            raise ValueError(f"{path}: observation alignment matched no text")
        written = {
            evidence_key(row): row
            for row in ((_front(path).get("benchmarks") or {}).get("evidence") or [])
            if isinstance(row, Mapping)
        }
        for key, aligned in updates:
            row = written.get(key)
            if row is None or (
                row.get("configuration") != aligned.get("configuration")
                or row.get("date_type") != aligned.get("date_type")
            ):
                raise ValueError(f"{path}: observation alignment did not stick")
        changed.append(path.relative_to(root).as_posix())
    return changed


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
        # The value the snapshot checks: with interval, n or quality flags, all of them.
        value=evidence_verification_value(row),
        unit=row.get("unit"),
        conditions={"effort": row.get("effort"), "harness": row.get("harness"),
                    "date": row.get("evidence_date")},
        collector=COLLECTOR,
        sources=(source,),
    )


def _matching_new_row(board: BoardReading, front: Mapping[str, Any]) -> Mapping[str, Any] | None:
    aliases = {
        readers.normalise_name(str(value))
        for value in (
            front.get("display_name"), front.get("version"), front.get("model_id"),
            str(front.get("model_id") or "").rsplit("/", 1)[-1],
        )
        if value
    }
    matches = []
    for row in board.rows:
        identity, _ = readers.split_model_cell(_subject(row))
        if identity in aliases:
            matches.append(row)
    return matches[0] if len(matches) == 1 else None


def _evidence_template(
    root: Path, board: BoardReading, benchmark_id: str,
) -> Mapping[str, Any] | None:
    if board.row_template is not None:
        return {**board.row_template, "source_url": board.source_url}
    allowed_urls = board.card_urls or frozenset({board.source_url})
    templates = []
    for path in sorted((root / "models").glob("*/*.md")):
        front = _front(path)
        for row in (front.get("benchmarks") or {}).get("evidence") or []:
            if row.get("benchmark_id") == benchmark_id \
                    and str(row.get("source_url") or "") in allowed_urls:
                templates.append(row)
    signatures = {
        (row.get("unit"), row.get("source_kind"))
        for row in templates
    }
    if len(signatures) != 1:
        return None
    return templates[0]


def _new_evidence(
    *, root: Path, model_id: str, front: Mapping[str, Any], board: BoardReading,
) -> tuple[list[dict[str, Any]], list[RowFailure]]:
    matched = _matching_new_row(board, front)
    if matched is None or matched.get(board.value_field) is None:
        return [], []
    rows: list[dict[str, Any]] = []
    failures: list[RowFailure] = []
    for benchmark_id in sorted(board.benchmark_ids):
        template = _evidence_template(root, board, benchmark_id)
        if template is None:
            failures.append(RowFailure(
                model_id, benchmark_id, board.source_url,
                "no unambiguous evidence metadata template for this registered board",
            ))
            continue
        row = {
            "benchmark_id": benchmark_id,
            "model_id_as_evaluated": _subject(matched),
            "score": _value(board, matched, str(template["unit"])),
            "unit": template["unit"],
            "source_url": template["source_url"],
            "source_kind": template["source_kind"],
            "evidence_date": _evidence_date(board, matched),
            "date_type": "evaluated",
            "observed_at": board.observed_at,
            "verified_at": board.observed_at,
            "benchmark_version": "",
            "configuration": "",
            "limitations": "",
            "measured_by": measured_by(template),
            "effort": None,
            "harness": None,
            "sources": [SourceRef(
                source_id=board.source_id,
                snapshot_ref=board.snapshot_ref,
                cited_regions=["rows"],
            ).model_dump(mode="json")],
        }
        row["id"] = evidence_id(model_id, row)
        rows.append(row)
    return rows, failures


def _append_evidence(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    from schema.benchmark_values import validate_card_rows

    validate_card_rows(path, rows)
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    # Append to the block list as text, so the rest of the card is untouched.
    front, blocks = parts[1], "".join(readers.new_row_block(dict(row)) for row in rows)
    head, empty = "\n  evidence:\n  - ", "\n  evidence: []\n"
    if head in front or empty in front:
        if head in front:
            start = front.index(head) + len(head)
            after = re.compile(r"^(?:  [a-z]|[a-z])", re.M).search(front, start)
            end = after.start() if after else len(front)
            front = front[:end] + blocks + front[end:]
        else:
            front = front.replace(empty, "\n  evidence:\n" + blocks, 1)
        path.write_text("---".join((parts[0], front, parts[2])), encoding="utf-8")
        return
    front = yaml.safe_load(parts[1]) or {}
    benchmarks = dict(front.get("benchmarks") or {})
    evidence = list(benchmarks.get("evidence") or [])
    evidence.extend(dict(row) for row in rows)
    benchmarks["evidence"] = evidence
    front["benchmarks"] = benchmarks
    path.write_text(
        "---\n" + yaml.dump(front, sort_keys=False, allow_unicode=True) + "---" + parts[2],
        encoding="utf-8",
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


def _selected_cards(root: Path, model_ids: Iterable[str] | None) -> dict[str, Path]:
    """Load the premier set by default, or an explicit release-signal scope."""
    if model_ids is None:
        return _premier_cards(root)
    selected = set(model_ids)
    cards: dict[str, Path] = {}
    for path in sorted((root / "models").glob("*/*.md")):
        model_id = str(_front(path).get("model_id") or "")
        if model_id in selected:
            cards[model_id] = path
    missing = selected - cards.keys()
    if missing:
        raise ValueError(f"selected cards missing: {', '.join(sorted(missing))}")
    return cards


ARENA_REVISION_ENV = "MODELSPEC_ARENA_REVISION"
_SHA_IN_URL = re.compile(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])")
_SHA_PATH = re.compile(r"/(?:resolve|tree|blob)/([0-9a-f]{7,40})(?![0-9a-f])")


def arena_revision_setting(explicit: bool | None = None) -> bool:
    """True when this run reads the dataset head.

    An explicit argument wins. Otherwise ``MODELSPEC_ARENA_REVISION`` is
    ``pinned`` (also the default when unset or empty) or ``latest``.
    """
    if explicit is not None:
        return explicit
    raw = os.environ.get(ARENA_REVISION_ENV)
    if raw is None or raw == "":
        return False
    if raw == "pinned":
        return False
    if raw == "latest":
        return True
    raise ValueError(
        f"{ARENA_REVISION_ENV} must be 'pinned' or 'latest', got {raw!r}"
    )


def _cited_shas(url: str) -> list[str]:
    """Commit SHAs a registry URL names.

    A 40-character hex string counts anywhere in the URL. A hex path segment
    of 7 to 40 characters counts after ``/resolve/``, ``/tree/``, or
    ``/blob/``. ``resolve/main`` and a URL with no revision name none.
    """
    lowered = str(url).lower()
    found: list[str] = []
    for sha in (*_SHA_IN_URL.findall(lowered), *_SHA_PATH.findall(lowered)):
        if sha not in found:
            found.append(sha)
    return found


def _sha_agrees(cited: str, revision: str) -> bool:
    """True when one SHA is the other, or the shorter one is its prefix."""
    short, longer = (cited, revision) if len(cited) <= len(revision) else (revision, cited)
    return longer.startswith(short)


def _moving_arena_benchmarks(root: Path, revision: str) -> set[str]:
    """Arena benchmarks whose stored rows cite a revision other than ``revision``."""
    moving: set[str] = set()
    for path in sorted((root / "models").glob("*/*.md")):
        front = _front(path)
        for row in (front.get("benchmarks") or {}).get("evidence") or []:
            if not isinstance(row, Mapping):
                continue
            benchmark = str(row.get("benchmark_id") or "")
            if not benchmark.startswith("arena_"):
                continue
            quoted = f"{row.get('benchmark_version') or ''}\n{row.get('configuration') or ''}"
            for cited in _REVISION_QUOTE.findall(quoted):
                if not _sha_agrees(cited.lower(), revision.lower()):
                    moving.add(benchmark)
    return moving


def _cards_on_benchmarks(root: Path, benchmarks: set[str], skip: set[str]) -> dict[str, Path]:
    """Catalogue cards, other than ``skip``, that have a row on ``benchmarks``."""
    found: dict[str, Path] = {}
    if not benchmarks:
        return found
    for path in sorted((root / "models").glob("*/*.md")):
        front = _front(path)
        model_id = str(front.get("model_id") or "")
        if not model_id or model_id in skip:
            continue
        rows = (front.get("benchmarks") or {}).get("evidence") or []
        if any(
            str(row.get("benchmark_id") or "") in benchmarks
            for row in rows if isinstance(row, Mapping)
        ):
            found[model_id] = path
    return found


def registry_revision_conflict(registered: Mapping[str, Any], boards: Sequence[BoardReading],
                              revision: str) -> list[str]:
    """Arena source ids whose registry URL names a commit other than ``revision``.

    An abbreviated SHA matches by prefix. A URL with no commit SHA, including
    ``resolve/main`` and the dataset root, is not a conflict. The caller
    writes no Arena rows when this list is not empty. Both revision modes
    call it.
    """
    conflict: list[str] = []
    wanted = revision.lower()
    source_ids = sorted({board.source_id for board in boards if board.key.startswith("arena:")})
    for source_id in source_ids:
        source = registered.get(source_id)
        if source is None:
            continue
        shas = _cited_shas(str(source.url))
        if any(not _sha_agrees(sha, wanted) for sha in shas):
            conflict.append(source_id)
    return conflict


def choose_arena_revision(latest: bool) -> readers.ArenaRevision:
    """The pinned Arena revision, unless ``latest`` asks the dataset API.

    A failed lookup keeps the pin. The returned fallback text is the report line.
    """
    if not latest:
        return readers.ArenaRevision(sha=readers.ARENA_REVISION)
    chosen = readers.resolve_arena_revision(_fetch)
    if not readers.valid_arena_revision(chosen.sha):
        return readers.ArenaRevision(
            sha=readers.ARENA_REVISION,
            fallback=chosen.fallback or "resolved sha failed validation",
        )
    return chosen


def run(*, observed_at: str, dry_run: bool, root: Path = ROOT,
        source_cache: Path | None = None,
        model_ids: Iterable[str] | None = None,
        add_missing: bool = False,
        arena_latest: bool | None = None) -> RefreshReport:
    date.fromisoformat(observed_at)
    latest = arena_revision_setting(arena_latest)
    chosen = choose_arena_revision(latest)
    premier = _selected_cards(root, model_ids)
    extras: dict[str, Path] = {}
    # Latest mode, and only the weekly path (no explicit model_ids), refreshes
    # every card on an Arena benchmark whose stored revision is not the one
    # just read. Pinned mode stays on the premier set. An explicit selection
    # stays on those cards.
    if model_ids is None and latest and chosen.fallback is None:
        moving = _moving_arena_benchmarks(root, chosen.sha)
        if moving:
            extras = _cards_on_benchmarks(root, moving, set(premier))
    cards = {**premier, **extras}
    card_groups = [premier, extras] if extras else [premier]
    fronts = {model: _front(path) for model, path in cards.items()}
    tau_urls = {
        str(row["source_url"])
        for front in fronts.values()
        for row in (front.get("benchmarks") or {}).get("evidence") or []
        if row.get("benchmark_id") == "tau3_banking" and row.get("source_url")
    }
    store = CopyStore(source_cache)
    # Latest mode writes Arena rows only when the head resolved and every
    # config was read there. A resolver failure, or any failed head fetch,
    # writes none. The pin stays per config.
    complete = (
        latest and chosen.fallback is None and chosen.sha != readers.ARENA_REVISION
    )
    boards, board_failures = collect_readings(
        observed_at, store, tau_urls, chosen.sha, arena_complete=complete,
        skip_arena=latest and chosen.fallback is not None,
    )
    failures = list(board_failures)
    if chosen.fallback:
        failures.insert(0, RowFailure(
            "*", "arena", readers.ARENA_DATASET_API,
            f"resolver fallback: {chosen.fallback}",
        ))
    config_fallback = next(
        (row.reason for row in failures if row.reason.startswith("config fallback:")),
        None,
    )
    effective = chosen.sha
    report_fallback = chosen.fallback or config_fallback
    report = RefreshReport(
        failures=failures,
        arena_revision=effective,
        arena_revision_fallback=report_fallback,
        arena_revision_latest=latest and report_fallback is None,
    )
    registered = load_sources(root / "registry" / "sources.yaml")
    conflict = registry_revision_conflict(registered, boards, effective)
    if conflict:
        report.failures.append(RowFailure(
            "*",
            "arena",
            readers.ARENA_DATASET_API,
            "the registry cites a different revision: " + ", ".join(conflict),
        ))
        boards = [board for board in boards if not board.key.startswith("arena:")]
    queue = Queue(root / "verification")
    filed_at = datetime.combine(date.fromisoformat(observed_at), datetime.min.time(), UTC)
    pending_updates: dict[Path, list[tuple[tuple[object, ...], dict[str, Any]]]] = {}
    pending_additions: dict[Path, list[dict[str, Any]]] = {}
    claims: list[Claim] = []

    arena_written = 0
    unregistered: set[str] = set()
    for group in card_groups:
        # Catalogue expansion exists to move Arena boards. A non-premier card
        # keeps every other row as stored.
        expanded = extras and group is extras
        for board in boards:
            if expanded and not board.key.startswith("arena:"):
                continue
            summary = report.board(board.key)
            if board.source_id not in registered:
                if board.key not in unregistered:
                    unregistered.add(board.key)
                    failure = RowFailure(
                        "*", ",".join(sorted(board.benchmark_ids)), board.source_url,
                        f"source is not registered: {board.source_id}",
                    )
                    report.failures.append(failure)
                    summary["failures"].append(failure.reason)
                continue
            models_read: set[str] = set()
            reconfirmed_models: set[str] = set()
            for model_id, path in group.items():
                rows = (fronts[model_id].get("benchmarks") or {}).get("evidence") or []
                relevant = [row for row in rows
                            if row.get("benchmark_id") in board.benchmark_ids
                            and str(row.get("source_url") or "") in
                            (board.card_urls or frozenset({board.source_url}))]
                if not relevant:
                    if add_missing:
                        additions, failures = _new_evidence(
                            root=root, model_id=model_id, front=fronts[model_id], board=board,
                        )
                        report.failures.extend(failures)
                        summary["failures"].extend(failure.reason for failure in failures)
                        if additions:
                            models_read.add(model_id)
                            pending_additions.setdefault(path, []).extend(additions)
                            claims.extend(
                                _claim(model_id, fronts[model_id], row, board) for row in additions
                            )
                            report.added += len(additions)
                    continue
                for row in relevant:
                    if _match(board, row) is not None:
                        models_read.add(model_id)
                observations, failures = _plan_observations(
                    model_id, path.relative_to(root).as_posix(), relevant, board,
                    revision=effective, front=fronts[model_id],
                )
                report.failures.extend(failures)
                summary["failures"].extend(failure.reason for failure in failures)
                for observation in observations:
                    arena_row = str(observation.benchmark).startswith("arena_")
                    if arena_row and arena_written >= ARENA_ROWS_PER_RUN:
                        report.arena_rows_left += 1
                        continue
                    old = next(row for row in relevant
                               if row["benchmark_id"] == observation.benchmark
                               and row.get("model_id_as_evaluated") == observation.model
                               and float(row["score"]) == observation.old_value)
                    new, reason = _copy_matched_reading(old, observation, observed_at=observed_at)
                    if new is None:
                        failure = RowFailure(
                            model_id, observation.benchmark, board.source_url,
                            reason or "reading was not rewritten",
                        )
                        report.failures.append(failure)
                        summary["failures"].append(failure.reason)
                        continue
                    new["evidence_date"] = observation.evidence_date
                    new["observed_at"] = observed_at
                    new["verified_at"] = observed_at
                    new = align_observation_dating(new)
                    new["sources"] = [SourceRef(
                        source_id=board.source_id,
                        snapshot_ref=board.snapshot_ref,
                        cited_regions=["rows"],
                    ).model_dump(mode="json")]
                    new["id"] = evidence_id(model_id, new)
                    if arena_row:
                        arena_written += 1
                    pending_updates.setdefault(path, []).append((evidence_key(old), new))
                    claims.append(_claim(model_id, fronts[model_id], new, board))
                    if observation.changed:
                        report.changes.append(observation.score_change())
                    else:
                        report.reconfirmed.append(observation)
                        reconfirmed_models.add(model_id)
            summary["models_reconfirmed"] += len(reconfirmed_models)
            summary["models_read"] += len(models_read)
            summary["values_changed"] = sum(
                1 for change in report.changes
                if change.source == board.source_url
                and change.benchmark in board.benchmark_ids
            )

    if dry_run or (not pending_updates and not pending_additions):
        return report

    for path, additions in pending_additions.items():
        _append_evidence(path, additions)
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


def _unwritten_arena_reason(report: RefreshReport) -> str | None:
    """The failure that means this run wrote no Arena rows."""
    for row in report.failures:
        if (
            row.reason.startswith("resolver fallback:")
            or row.reason.startswith("config fallback:")
            or "registry cites a different revision" in row.reason
        ):
            return row.reason
    return None


def render_report(report: RefreshReport) -> str:
    lines: list[str] = []
    if report.arena_revision:
        withheld = _unwritten_arena_reason(report)
        if withheld:
            lines.extend([
                f"Arena revision: {report.arena_revision} read, no rows written: {withheld}",
                "",
            ])
        else:
            if report.arena_revision_fallback:
                status = f"fallback to the pinned default: {report.arena_revision_fallback}"
            elif report.arena_revision_latest:
                status = "Hugging Face dataset sha"
            else:
                status = "pinned default"
            lines.extend([f"Arena revision: {report.arena_revision} ({status})", ""])
    if report.arena_rows_left:
        lines.extend([
            f"Arena rows left for the next run: {report.arena_rows_left}",
            "",
        ])
    lines.extend([
        "| Board | Models read | Models re-confirmed | Values changed | Failures |",
        "|---|---:|---:|---:|---:|",
    ])
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


#: GitHub rejects a pull request body at 65,536 characters. Stay under that.
_PR_BODY_LIMIT = 60_000
_PR_URL_TOKEN = "${PR_URL}"
#: Longest modelspec-data pull request URL this fitter reserves space for.
_PR_URL_BUDGET = len("https://github.com/turbobeest/modelspec-data/pull/9999999999")
_REPORT_ARTIFACT = "leaderboard-refresh-report"


def _measured_length(text: str, pr_url_budget: int) -> int:
    """Length after each ``${PR_URL}`` grows to ``pr_url_budget`` characters."""
    growth = max(0, pr_url_budget - len(_PR_URL_TOKEN))
    return len(text) + text.count(_PR_URL_TOKEN) * growth


def _omitted_change_rows(count: int) -> str:
    if count == 1:
        subject = "1 change row was left out"
    else:
        subject = f"{count} change rows were left out"
    return (
        f"{subject}. The full report is in the run's {_REPORT_ARTIFACT} artifact."
    )


def _opening_line(lines: list[str]) -> str:
    for line in lines:
        if not line.strip():
            continue
        if line.startswith(("Arena revision:", "|", "#")):
            return ""
        return line
    return ""


def _markdown_table(lines: list[str], header_prefix: str) -> list[str]:
    for index, line in enumerate(lines):
        if not line.startswith(header_prefix):
            continue
        table = [line]
        cursor = index + 1
        while cursor < len(lines) and lines[cursor].startswith("|"):
            table.append(lines[cursor])
            cursor += 1
        return table
    return []


def _table_in_section(lines: list[str], heading: str) -> list[str]:
    try:
        start = lines.index(heading)
    except ValueError:
        return []
    table: list[str] = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        if line.startswith("|"):
            table.append(line)
    return table


def _change_table(lines: list[str]) -> tuple[list[str], list[str]]:
    table = _table_in_section(lines, "## Score changes")
    if len(table) < 2:
        return table, []
    return table[:2], table[2:]


def _truncate_pull_request_body(body: str, limit: int, pr_url_budget: int) -> str:
    lines = body.splitlines()
    opening = _opening_line(lines)
    arena = next((line for line in lines if line.startswith("Arena revision:")), "")
    arena_left = next((line for line in lines if line.startswith("Arena rows left")), "")
    board = _markdown_table(lines, "| Board |")
    failures = _table_in_section(lines, "## Failures")
    change_header, change_rows = _change_table(lines)

    def assemble(rows: list[str], omitted: int) -> str:
        parts: list[str] = []
        if opening:
            parts.append(opening)
        if arena:
            parts.extend(["", arena] if parts else [arena])
        if arena_left:
            parts.extend(["", arena_left] if parts else [arena_left])
        if board:
            parts.extend(["", *board] if parts else list(board))
        if failures:
            block = ["## Failures", "", *failures]
            parts.extend(["", *block] if parts else block)
        if rows:
            block = ["## Score changes", "", *change_header, *rows]
            parts.extend(["", *block] if parts else block)
        if omitted:
            note = _omitted_change_rows(omitted)
            parts.extend(["", note] if parts else [note])
        return "\n".join(parts) + "\n"

    kept: list[str] = []
    for row in change_rows:
        trial = kept + [row]
        candidate = assemble(trial, len(change_rows) - len(trial))
        if _measured_length(candidate, pr_url_budget) <= limit:
            kept = trial
        else:
            break
    return assemble(kept, len(change_rows) - len(kept))


def fit_pull_request_body(
    body: str, *, limit: int = _PR_BODY_LIMIT, pr_url_budget: int = _PR_URL_BUDGET,
) -> str:
    """Return ``body`` when it fits in ``limit`` characters.

    Each ``${PR_URL}`` is measured as ``pr_url_budget`` characters, so filling
    in the pull request URL cannot push a fitted body over the limit. A body
    that does not fit keeps the opening line, the Arena revision line, the
    per-board table and the failures table in full, then as many score-change
    rows as fit. The cut is on a row boundary. One line says how many change
    rows were left out and that the full report is in the run's
    ``leaderboard-refresh-report`` artifact.
    """
    if _measured_length(body, pr_url_budget) <= limit:
        return body
    return _truncate_pull_request_body(body, limit, pr_url_budget)


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


_REFRESH_SIGNATURE = frozenset({
    "score", "observed_at", "verified_at", "evidence_date", "id", "sources",
})


def _reading_refreshed(before: Mapping[str, Any], after: Mapping[str, Any]) -> bool:
    """True when this run rewrote the score-bearing reading."""
    return any(before.get(key) != after.get(key) for key in _REFRESH_SIGNATURE)


def _arena_dataset_root_url(url: object) -> bool:
    return str(url or "").rstrip("/") == ARENA_DATASET_ROOT


def _arena_reading_row(row: Mapping[str, Any]) -> bool:
    return (
        str(row.get("benchmark_id") or "").startswith("arena_")
        and _arena_dataset_root_url(row.get("source_url"))
    )


_MASK_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_MASK_HEX = re.compile(r"(?i)\b[0-9a-f]{7,40}\b")
_MASK_NUMBER = re.compile(r"-?\d+(?:\.\d+)?")


def _mask_quoted_figures(text: str) -> str:
    """Dates, then hex strings, then numbers, so only the wording remains."""
    masked = _MASK_DATE.sub("0", text)
    masked = _MASK_HEX.sub("0", masked)
    return _MASK_NUMBER.sub("0", masked)


def _verifier_named_effort(model_id_as_evaluated: object) -> str | None:
    """The canonical effort ``split_model_cell`` reads on this model id."""
    text = str(model_id_as_evaluated or "")
    found = structured_name_effort(text)
    if found is not None:
        return split_model_cell(f"({found})")[1]
    return split_model_cell(text)[1]


def _arena_effort_refresh_allowed(before: Mapping[str, Any], after: Mapping[str, Any]) -> bool:
    """Null or empty effort may become the canonical level, and nothing else."""
    if before.get("model_id_as_evaluated") != after.get("model_id_as_evaluated"):
        return False
    old, new = before.get("effort"), after.get("effort")
    if old == new:
        return True
    if old not in (None, ""):
        return False
    named = _verifier_named_effort(before.get("model_id_as_evaluated"))
    return named is not None and new == named


def _row_allows_refresh(before: Mapping[str, Any], after: Mapping[str, Any]) -> bool:
    """A refresh may change score, dates, id and the source snapshot.

    On a refreshed Arena dataset-root row, ``interval`` and ``n`` may change.
    ``configuration`` may change only when the two strings match after dates,
    hex strings and numbers are masked. ``effort`` may change only from null
    or empty to the canonical level the unchanged ``model_id_as_evaluated``
    names. ``benchmark_version`` never changes. On every other row, when
    ``source_publishes_row_date`` is false and the new evidence day is the
    observation, a row may replace the standalone word ``read`` plus a date
    in the configuration, and change date_type from ``published`` to
    ``evaluated``. ``re-read`` is not that citation. A dated projector keeps
    both fields, including when this row's date value is missing. An unknown
    source URL does too.
    """
    refreshed = _reading_refreshed(before, after)
    old, new = dict(before), dict(after)
    for key in _ALLOWED_EVIDENCE_FIELDS:
        old.pop(key, None)
        new.pop(key, None)
    if refreshed and _arena_reading_row(before) and _arena_reading_row(after):
        for key in ("interval", "n"):
            old.pop(key, None)
            new.pop(key, None)
        if _mask_quoted_figures(str(before.get("configuration") or "")) == _mask_quoted_figures(
            str(after.get("configuration") or ""),
        ):
            old.pop("configuration", None)
            new.pop("configuration", None)
        if _arena_effort_refresh_allowed(before, after):
            old.pop("effort", None)
            new.pop("effort", None)
    dated_by_source = source_publishes_row_date(str(before.get("source_url") or ""))
    if old.get("configuration") != new.get("configuration"):
        if not observation_dated(
            after.get("evidence_date"), after.get("observed_at"), source_dated=dated_by_source,
        ):
            return False
        expected = _READ_DATE.sub(
            f"read {_iso_day(after.get('evidence_date'))}",
            str(old.get("configuration") or ""),
        )
        if expected != str(new.get("configuration") or ""):
            return False
        old.pop("configuration", None)
        new.pop("configuration", None)
    if old.get("date_type") != new.get("date_type"):
        if not (
            observation_dated(
                after.get("evidence_date"), after.get("observed_at"), source_dated=dated_by_source,
            )
            and old.get("date_type") == "published"
            and new.get("date_type") == OBSERVATION_DATE_TYPE
        ):
            return False
        old.pop("date_type", None)
        new.pop("date_type", None)
    return old == new


def _fronts_match_after_refresh(
    before_front: Mapping[str, Any], after_front: Mapping[str, Any],
) -> bool:
    before, after = copy.deepcopy(dict(before_front)), copy.deepcopy(dict(after_front))
    before_rows = list(((before.get("benchmarks") or {}).get("evidence") or []))
    after_rows = list(((after.get("benchmarks") or {}).get("evidence") or []))
    if len(before_rows) != len(after_rows):
        return False
    if any(not _row_allows_refresh(old, new) for old, new in zip(before_rows, after_rows)):
        return False
    for front in (before, after):
        benchmarks = front.get("benchmarks")
        if isinstance(benchmarks, dict):
            benchmarks["evidence"] = []
    return before == after


def check_score_only(before: Path, after: Path) -> ScoreOnlyResult:
    """Mechanically prove a generated refresh did not add cards or alter identities.

    Existing evidence rows may change their score, observation/verification
    date, ID and source-snapshot binding. A refreshed Arena dataset-root row
    may also change its interval and vote count, a configuration whose wording
    is unchanged once dates, hex strings and numbers are masked, and its
    effort from null to the canonical level its model id names.
    ``benchmark_version`` stays. A row whose source URL is an observation
    projector, dated by the observation, may also make its configuration's
    standalone ``read <date>`` and date_type match that date.
    A ``re-read`` phrase is not that edit. A dated projector keeps both fields,
    including when its date value is missing and when the stored evidence day
    already equals ``observed_at``. Verification JSONL files may only grow.
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
            elif not _fronts_match_after_refresh(before_front, after_front):
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
        "arena_revision": report.arena_revision,
        "arena_revision_fallback": report.arena_revision_fallback,
        "arena_revision_latest": report.arena_revision_latest,
        "arena_rows_left": report.arena_rows_left,
        "boards": report.boards,
        "changes": [change.to_dict() for change in report.changes],
        "reconfirmed": [row.__dict__ for row in report.reconfirmed],
        "failures": [row.__dict__ for row in report.failures],
        "quarantined": [row.__dict__ for row in report.quarantined],
        "added": report.added,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _fetch(url: str) -> bytes:
    from decision.retention import open_retained_source

    require_allowed_source(url)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with open_retained_source(request, timeout=180) as response:
        return response.read()


def _reading_from_projection(
    *, key: str, source_id: str, benchmarks: Iterable[str], source_url: str,
    projected: bytes, observed_at: str, value_field: str, store: CopyStore,
    fraction: bool = False, card_urls: Iterable[str] = (),
    row_template: Mapping[str, str] | None = None,
) -> BoardReading:
    payload = json.loads(projected)
    rows = tuple({**row, "observed_at": observed_at} for row in payload["rows"])
    return BoardReading(
        key, source_id, frozenset(benchmarks), source_url, observed_at, rows,
        value_field, fraction, store.put(projected, source_url=source_url), frozenset(card_urls), row_template,
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


#: MathArena's research-maths boards, the Overall table of each (MODEL-233). The
#: site marks its final-answer and proof competitions deprecated; these still run.
MATHARENA_BOARDS = {
    "brokenarxiv": ("model-233-matharena-brokenarxiv",
                    "https://matharena.ai/competition_tables/overall--brokenarxiv"),
    "arxivmath": ("model-233-matharena-arxivmath",
                  "https://matharena.ai/competition_tables/overall--arxivmath"),
}
#: AIME 2025 uses ``project_matharena``. That projector's row has no date column.
MATHARENA_AIME_2025_URL = "https://matharena.ai/competition_tables/aime--aime_2025"
HLE_URL = "https://labs.scale.com/leaderboard/humanitys_last_exam"
DEEPSWE_CARD_URL = "https://deepswe.datacurve.ai/"
#: Card source URLs whose refresher projector puts none of ``_SOURCE_DATE_KEYS``
#: on a row. ``source_publishes_row_date`` is membership in this set. A blank
#: date that ``document`` drops does not move the URL into this set: an empty
#: Epoch ``Started at`` stays a dated projector. Read from each
#: projector's row dict: ``project_metr``, ``project_mteb``,
#: ``project_matharena``, ``project_cursorbench``, ``project_deepswe``,
#: ``project_vending``, ``project_frontiercode`` and ``_project_frontiercode``,
#: ``project_osworld`` and ``_project_osworld``, ``_project_scale_hle``.
#: Arena, Epoch, Terminal-Bench, Scale SWE-bench Pro, Finance Benchmark,
#: SWE-bench and tau-bench each emit ``date`` or ``leaderboard_publish_date``.
_OBSERVATION_SOURCE_URLS = frozenset({
    readers.METR_URL,
    *(board[1] for board in MTEB_BOARDS),
    readers.MATHARENA_URL,
    MATHARENA_AIME_2025_URL,
    *(url for _, url in MATHARENA_BOARDS.values()),
    readers.CURSOR_URL,
    readers.DEEPSWE_URL,
    DEEPSWE_CARD_URL,
    readers.VENDING_URL,
    readers.FRONTIERCODE_URL,
    readers.OSWORLD_URL,
    HLE_URL,
})


FINBENCH_URL = "https://finbenchmark.ai/"


def _project_finbenchmark(html: str, *, url: str, page_ref: str,
                          observed_at: str) -> bytes:
    """Finance Benchmark v2 rows from the page's React payload (MODEL-232).

    The page carries one ``rows`` list of run records. Only ``task_set_version``
    v2 rows are kept: v2.1 and v3 results are different task sets, not newer v2
    readings. ``pass_at_1`` is a fraction on the page and percent on the cards.
    """
    payload = readers._rsc_payload(html)
    lists: list[list[Mapping[str, Any]]] = []
    position = 0
    while True:
        try:
            start = payload.index('"rows":', position) + len('"rows":')
        except ValueError:
            break
        value, _ = json.JSONDecoder().raw_decode(payload, start)
        if (isinstance(value, list) and value and isinstance(value[0], Mapping)
                and {"model_name", "provider", "task_set_version", "pass_at_1"} <= set(value[0])):
            lists.append(value)
        position = start + 1
    if len(lists) != 1:
        raise ValueError(f"Finance Benchmark: expected one run-record list, got {len(lists)}")
    rows = [{
        "model": f"{row['provider']}/{row['model_name']}",
        "pass_at_1": round(float(row["pass_at_1"]) * 100, 4),
        "date": str(row["completed_at"]).split("T", 1)[0],
        "harness": f"finance-benchmark {row['harness_version']}",
        "task_set_version": row["task_set_version"],
    } for row in lists[0] if row["task_set_version"] == "v2" and row["pass_at_1"] is not None]
    if not rows:
        raise ValueError("Finance Benchmark: no v2 rows in the run-record list")
    return readers.document(rows, url=url, page_ref=page_ref, read_date=observed_at,
                            note="task_set_version v2 rows from the page's React payload; "
                                 "provider/model_name as model; pass_at_1 as percent; "
                                 "harness_version as the finance-benchmark harness")


def collect_readings(observed_at: str, store: CopyStore, tau_urls: Iterable[str],
                     arena_revision: str | None = None, *,
                     arena_complete: bool = False,
                     skip_arena: bool = False,
                     ) -> tuple[list[BoardReading], list[RowFailure]]:
    """Fetch every terms-compatible live board used by the premier snapshot.

    ``arena_revision`` selects the Arena dataset commit. An absent or invalid
    value keeps the pinned revision. The value is checked again before any URL
    is built. ``arena_complete`` requires every Arena config at that revision.
    When one of those fetches fails or the config is missing, this run writes
    no Arena rows and one failure names the gap. It does not read the pin
    instead. ``skip_arena`` writes no Arena rows; the caller reports why.
    Pinned mode still writes each config it could read.
    """
    readings: list[BoardReading] = []
    failures: list[RowFailure] = []
    revision = arena_revision or readers.ARENA_REVISION
    if not readers.valid_arena_revision(revision):
        revision = readers.ARENA_REVISION

    def collect(key: str, source_id: str, benchmarks: Iterable[str], source_url: str,
                fetch_url: str, projector: Callable[..., bytes], value_field: str,
                *, fraction: bool = False, card_urls: Iterable[str] = ()) -> None:
        try:
            require_allowed_source(fetch_url, benchmarks)
            raw = _fetch(fetch_url)
            raw_ref = store.put(raw, source_url=fetch_url)
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

    # Arena: the CC BY 4.0 Hugging Face dataset, at one revision for every config.
    def arena_source_id(config: str) -> str:
        if config == "webdev":
            return "model-143-evidence-arena-webdev-json"
        return readers.arena_source(config)

    def fetch_arena(at: str) -> tuple[dict[str, tuple[bytes, str, str]], list[RowFailure]]:
        kept: dict[str, tuple[bytes, str, str]] = {}
        missed: list[RowFailure] = []
        for config in sorted({config for config, _ in ARENA_BOARDS.values()}):
            fetch_url = readers.arena_parquet_url(config, at)
            try:
                raw = _fetch(fetch_url)
                raw_ref = store.put(raw, source_url=fetch_url)
            except Exception as exc:
                missed.append(RowFailure(
                    "*", f"arena:{config}", fetch_url, f"{type(exc).__name__}: {exc}",
                ))
                continue
            kept[config] = (raw, raw_ref, fetch_url)
        return kept, missed

    def project_arena(kept: dict[str, tuple[bytes, str, str]]) \
            -> tuple[list[BoardReading], list[RowFailure]]:
        produced: list[BoardReading] = []
        missed: list[RowFailure] = []
        for config, (raw, raw_ref, fetch_url) in kept.items():
            produced_here: list[BoardReading] = []
            error: RowFailure | None = None
            for benchmark, (cfg, category) in ARENA_BOARDS.items():
                if cfg != config:
                    continue
                try:
                    projected = readers.project_arena(
                        raw, config, category, url=fetch_url, page_ref=raw_ref,
                        read_date=observed_at,
                    )
                    produced_here.append(_reading_from_projection(
                        key=f"arena:{benchmark}",
                        source_id=arena_source_id(config),
                        benchmarks=(benchmark,), source_url=fetch_url, projected=projected,
                        observed_at=observed_at, value_field="rating", store=store,
                        card_urls=("https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset",),
                    ))
                except Exception as exc:
                    error = RowFailure(
                        "*", f"arena:{config}", fetch_url, f"{type(exc).__name__}: {exc}",
                    )
                    break
            if error is None:
                produced.extend(produced_here)
            else:
                missed.append(error)
        return produced, missed

    if not skip_arena:
        kept, missed = fetch_arena(revision)
        if arena_complete and missed:
            missing = ", ".join(sorted(
                row.benchmark.removeprefix("arena:") for row in missed
            ))
            detail = "; ".join(row.reason for row in missed)
            failures.append(RowFailure(
                "*", "arena", readers.ARENA_DATASET_API,
                f"config fallback: revision {revision} is missing {missing}; "
                f"no Arena rows written ({detail})",
            ))
        else:
            produced, project_errors = project_arena(kept)
            readings.extend(produced)
            failures.extend(missed)
            failures.extend(project_errors)

    # Epoch publishes one CC BY 4.0 archive; all files in this block share one fetch.
    try:
        archive_url = readers.EPOCH_ZIP
        raw = _fetch(archive_url)
        raw_ref = store.put(raw, source_url=archive_url)
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

    # MathArena: MIT-licensed code, CC BY-SA 4.0 datasets; the site asks only to be
    # cited (checked 2026-09-29). Its index marks retired competitions, and a row's
    # `deprecated` flag must come from the same reading as its score.
    matharena = {
        "matharena": ("model-160-matharena-aime-2026", "aime_2026", readers.MATHARENA_URL),
        **{f"matharena:{benchmark}": (source_id, benchmark, url)
           for benchmark, (source_id, url) in MATHARENA_BOARDS.items()},
    }
    try:
        index = _fetch(readers.MATHARENA_INDEX)
        index_ref = store.put(index, source_url=readers.MATHARENA_INDEX)
    except Exception as exc:
        failures.append(RowFailure("*", "matharena", readers.MATHARENA_INDEX,
                                   f"{type(exc).__name__}: {exc}"))
    else:
        for key, (source_id, benchmark, url) in matharena.items():
            def project(body: bytes, *, url: str, page_ref: str, observed_at: str,
                        competition: str = url.rsplit("/", 1)[1]) -> bytes:
                return readers.project_matharena(
                    body, url=url, read_date=observed_at,
                    page_ref=f"{page_ref}; index {index_ref} {readers.MATHARENA_INDEX}",
                    deprecated=readers.matharena_deprecated(index.decode(), competition))
            collect(key, source_id, (benchmark,), url, url, project, "accuracy")
    try:
        raw = _fetch(readers.METR_URL)
        raw_ref = store.put(raw, source_url=readers.METR_URL)
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

    for key, url, source_id, columns, unit in MTEB_BOARDS:
        try:
            raw = _fetch(url)
            raw_ref = store.put(raw, source_url=url)
            projected = readers.project_mteb(raw, url=url, page_ref=raw_ref,
                                             read_date=observed_at)
            for benchmark, label in columns.items():
                readings.append(_reading_from_projection(
                    key=f"mteb:{benchmark}", source_id=source_id,
                    benchmarks=(benchmark,), source_url=url, projected=projected,
                    observed_at=observed_at, value_field=label, fraction=True, store=store,
                    card_urls=(url,), row_template={**MTEB_ROW, "unit": unit},
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
            readers.DEEPSWE_URL, readers.DEEPSWE_URL,
            lambda body, **kw: readers.project_deepswe(body, read_date=observed_at,
                                                        **{k: v for k, v in kw.items()
                                                           if k != "observed_at"}),
            "pass_at_1", fraction=True, card_urls=(DEEPSWE_CARD_URL,))

    # The remaining MODEL-160 boards already have plain-HTTP projectors.
    collect("scale-pro", "model-160-scale-swe-bench-pro-public", ("swe_bench_pro",),
            readers.SCALE_URL, readers.SCALE_URL,
            lambda body, **kw: readers.project_scale(body.decode(), read_date=observed_at,
                                                      **{k: v for k, v in kw.items()
                                                         if k != "observed_at"}),
            "resolve_rate", card_urls=(readers.SCALE_URL, "https://labs.scale.com/leaderboard/swe_bench_pro"))
    collect("scale-hle", "model-143-evidence-scale-hle-json", ("hle",), HLE_URL,
            HLE_URL, lambda body, **kw: _project_scale_hle(body.decode(), **kw), "accuracy")
    collect("cursorbench", "model-160-cursorbench", ("cursorbench_4",), readers.CURSOR_URL,
            readers.CURSOR_URL,
            lambda body, **kw: readers.project_cursorbench(body.decode(), read_date=observed_at,
                                                            **{k: v for k, v in kw.items()
                                                               if k != "observed_at"}),
            "accuracy")
    # MIT-licensed repository; the site asks only to be cited (checked 2026-09-29).
    collect("finbenchmark", "model-192-finance-benchmark-v2", ("finance_benchmark_v2",),
            FINBENCH_URL, FINBENCH_URL,
            lambda body, **kw: _project_finbenchmark(body.decode(), **kw), "pass_at_1")

    # SWE-bench carries two named boards in one embedded JSON document.
    try:
        raw = _fetch(readers.SWEBENCH_URL)
        raw_ref = store.put(raw, source_url=readers.SWEBENCH_URL)
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
            raw_ref = store.put(raw, source_url=chunk_url)
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
    parser.add_argument(
        "--arena-latest",
        action="store_true",
        help="Read Arena at the current Hugging Face dataset revision. "
             "A failure keeps the pinned revision and says so in the report.",
    )
    args = parser.parse_args(argv)
    # The network collector is wired below; keeping the CLI here makes the pure
    # planning and diff guard independently testable.
    report = run(observed_at=args.observed_at, dry_run=args.dry_run,
                 arena_latest=True if args.arena_latest else None)
    print(render_report(report))
    if args.audit_json:
        write_audit(args.audit_json, report.changes)
    if args.report_json:
        write_report_json(args.report_json, report)


if __name__ == "__main__":
    main()
