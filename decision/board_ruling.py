"""The owner's ruling on a benchmark board reading whose rule-15 readers disagreed (MODEL-569).

A board reading (one evidence row of a benchmark, read by the board-reading gate,
``decision.cited_change.cited_reading``) is keyed in the attempt log by the card's subject, the
facet ``benchmark:<id>`` and the row's epoch: its settings epoch (``reading:<hash>``), a board
epoch of it that names the row's cited board region (``<settings>:board:<region>``, MODEL-555),
or, once the row carries a cited change, that change's re-read epoch. A complete attempt whose two
readers disagreed blocks that epoch for good, and the row has no registered fact facet, so the
fact filer's path (``decision.owner_ruling``, MODEL-551) did not reach it. This module extends it
with the same limits:

* a ruling is one line of ``verification/owner-rulings.jsonl`` with exactly
  ``owner_ruling.FIELDS``; ``ruling_problem`` checks it as for a fact (owner, ticket, basis of
  counts and field names, day, resolved disagreements, cite-only sources the resolved attempts
  read), and the value is a board score: ``known``, a number in the board's range;
* the epoch is one of the row's (``epoch_problem``): its settings or re-read epoch, a board epoch
  of it whose region every resolved attempt logged, or a reopened epoch that extends a standing
  ruling's (``<ruled epoch>:reopen:<region>``) whose region differs from that ruling's baseline;
* the epoch is current (``stale_problem``): no attempt at the reading logged after the resolved
  disagreement is in another epoch, other than a reopened epoch that extends the ruling's; and an
  agreement there on another score means the ruling no longer stands;
* nothing holds the row: the verdicts ``quarantine_clearing.reading_held`` finds (its own id, and
  queue-proven earlier ids, MODEL-552 follow-up) are the caller's ``held``; a ruling names no
  verdict, so it releases none and refuses a held row;
* the row's score is exactly the ruling's value and each of the ruling's sources is cited at the
  copy its resolved attempt read.

``row_problem`` is the one test: the filer (``scripts/file_owner_ruling.py``), the gate (whether a
ruled row's ruling stands) and the build (``decision.snapshot`` and ``pipeline.load``) all call it.

On the re-read, by MODEL-562's rule for facts: a ruled row is read in its ruled epoch, where the
disagreement still blocks. The sweep (``scripts.evidence_reread.ruled_reading_rereads``) reads the
board with the gate's own fetch and, when the row's board region (``row_region_sha256``) is not
the region the resolved attempts logged (the baseline, never read from the record), records one
``reopen`` line (``ruling_reread.RECORD_FILE``). Only then, and only from its own fetch, does the
gate read the row in ``<ruled epoch>:reopen:<region>``. A ruling stops standing only through an
agreement on another score there (``superseding_epoch``): any other attempt under its epoch is
ignored. A row whose ruling stopped standing is read only in that reopened epoch, never from
caller bytes; one whose ruling does not stand at all is not read. The board-owner check
(``owner_problem``: the source is the benchmark owner's own ``benchmark_author`` page) is part
of ``row_problem``, so the filer, the gate and the build all apply it.
"""

from __future__ import annotations

import math
import re
from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

_HEX = re.compile(r"[0-9a-f]{64}")
BENCHMARK_AUTHOR = "benchmark_author"


# --- the board owner's page (the gate's ``_check_board_source``, shared) --------------------------


@dataclass(frozen=True)
class BoardRegistry:
    """What the board-owner check reads: the source registry rows (``url``, ``kind``,
    ``publisher``), the publishers' registered URLs (providers, subscription vendors, labs) and
    each benchmark page's ``owner_id``. The gate builds it from its own lookup; the build and the
    site read it from the data checkout (``read``)."""

    sources: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    publishers: Mapping[str, str] = field(default_factory=dict)
    owners: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def read(cls, root: str | Path) -> BoardRegistry:
        """Raises ``OSError``, ``ValueError``, ``KeyError`` or ``TypeError`` on a registry that
        cannot be read; a caller fails closed."""
        import yaml
        from schema.yaml_loader import load_yaml_unique

        root = Path(root)
        rows = yaml.safe_load((root / "registry" / "sources.yaml").read_text("utf-8"))["sources"]
        owners: dict[str, Any] = {}
        for page in sorted((root / "benchmarks").glob("*.md")):
            try:
                front = load_yaml_unique(page.read_text("utf-8").split("---", 2)[1])
            except (IndexError, yaml.YAMLError):
                continue
            if isinstance(front, dict):
                owners[page.stem] = front.get("owner_id")  # as the gate opens the page
        return cls({str(r["id"]): dict(r) for r in rows if isinstance(r, dict)},
                   read_publishers(root), owners)


def read_publishers(root: str | Path) -> dict[str, str]:
    """Publisher id -> registered URL, as the board gate reads them (``reading_lookup``)."""
    import yaml

    root = Path(root)
    publishers: dict[str, str] = {}
    providers = yaml.safe_load((root / "registry" / "providers.yaml").read_text("utf-8"))
    for group in ("providers", "subscription_vendors"):
        for entry in providers.get(group) or []:
            publishers[entry["id"]] = str(entry.get("url") or "")
    for entry in yaml.safe_load((root / "registry" / "labs.yaml").read_text("utf-8"))["labs"]:
        publishers.setdefault(entry["id"], str(entry.get("url") or ""))
    return publishers


def _host(url: Any) -> str | None:
    from urllib.parse import urlsplit

    try:
        host = (urlsplit(str(url)).hostname or "").lower().rstrip(".")
    except ValueError:
        return None
    return host.removeprefix("www.") or None


def owner_problem(registry: BoardRegistry | None, benchmark_id: str,
                  source_id: str) -> tuple[str, str] | None:
    """``(gate reason, detail)`` unless the source is the benchmark owner's own page: a
    ``benchmark_author`` source whose recorded publisher is a registered publisher, is the
    benchmark page's ``owner_id``, and is registered on the source's host. The one check the
    gate, the filer and the build make. No registry fails closed."""
    if registry is None:
        return "not_first_party", "no board registry is known"
    row = registry.sources.get(source_id)
    if row is None or not row.get("url"):
        return "not_first_party", "the source is not in the source registry"
    if row.get("kind") != BENCHMARK_AUTHOR:
        return "source_kind_not_permitted", f"{row.get('kind')} is not {BENCHMARK_AUTHOR}"
    publisher = row.get("publisher")
    registered = registry.publishers.get(publisher) if isinstance(publisher, str) else None
    if not publisher or not registered:
        return "not_first_party", \
            "the source registry records no publisher, or one the registries do not know"
    owner = registry.owners.get(benchmark_id)
    if not isinstance(owner, str) or not owner:
        return "not_first_party", "the benchmark page records no owner"
    if publisher != owner:
        return "not_first_party", "the source's publisher is not the benchmark's owner"
    host = _host(row["url"])
    if host is None or _host(registered) != host:
        return "not_first_party", "the owner's registry host is not the source's host"
    return None


def is_board_facet(facet: Any) -> bool:
    from decision.cited_change import BENCHMARK_PREFIX

    return isinstance(facet, str) and facet.startswith(BENCHMARK_PREFIX) \
        and len(facet) > len(BENCHMARK_PREFIX)


def board_facet(row: Mapping[str, Any]) -> str:
    from decision.cited_change import BENCHMARK_PREFIX

    return BENCHMARK_PREFIX + str(row.get("benchmark_id"))


def value_problem(ruling: Mapping[str, Any], max_score: Any = None) -> tuple[str, str] | None:
    """A board ruling states a score: ``known``, a number (not a boolean), finite, at least 0 and
    at most the board's ``max_score`` when it has one (as the gate refuses a reading outside it)."""
    if ruling.get("state") != "known":
        return "value_invalid", "a board ruling states a score (state known)"
    value = ruling.get("value")
    if isinstance(value, bool) or not isinstance(value, (int, float)) \
            or not math.isfinite(float(value)) or value < 0:
        return "value_invalid", "a board score is a finite number of at least 0"
    if isinstance(max_score, (int, float)) and not isinstance(max_score, bool) \
            and value > max_score:
        return "value_invalid", "the score is outside the board's range"
    return None


def row_base(row: Mapping[str, Any]) -> str:
    """The row's own epoch before any board region: its settings epoch, or the re-read epoch its
    cited-change block names (``cited_change.reading_epoch``)."""
    from decision.cited_change import READING_KEYS, reading_epoch

    return reading_epoch({k: row.get(k) for k in READING_KEYS}, row)


def _has_block(row: Mapping[str, Any]) -> bool:
    from decision.cited_change import cited_change_block

    return cited_change_block(row) is not None


def split_epoch(epoch: Any, row: Mapping[str, Any]) -> tuple[str, list[str]] | None:
    """``(core, reopened regions)`` when ``epoch`` is one of the row's: the core is the row's base
    epoch or, for a row with no cited change, a board epoch of it; then zero or more
    ``:reopen:<region>``. ``None`` for any other epoch."""
    from decision.cited_change import BOARD_MARK
    from decision.owner_ruling import REOPEN_MARK

    base = row_base(row)
    if not isinstance(epoch, str) or not epoch.startswith(base):
        return None
    rest, core = epoch[len(base):], base
    if rest.startswith(BOARD_MARK):
        region = rest[len(BOARD_MARK):len(BOARD_MARK) + 64]
        if _has_block(row) or not _HEX.fullmatch(region):
            return None
        core, rest = base + BOARD_MARK + region, rest[len(BOARD_MARK) + 64:]
    regions = []
    while rest:
        if not rest.startswith(REOPEN_MARK):
            return None
        region = rest[len(REOPEN_MARK):len(REOPEN_MARK) + 64]
        if not _HEX.fullmatch(region):
            return None
        regions.append(region)
        rest = rest[len(REOPEN_MARK) + 64:]
    return core, regions


def named_region(epoch: str, row: Mapping[str, Any]) -> str | None:
    """The region the epoch names last (a reopened region, else the board epoch's), or ``None``."""
    from decision.cited_change import is_board_epoch

    parsed = split_epoch(epoch, row)
    if parsed is None:
        return None
    core, regions = parsed
    return regions[-1] if regions else is_board_epoch(core, row_base(row))


def baseline(ruling: Mapping[str, Any], attempts: Sequence[Mapping[str, Any]]) -> str | None:
    """The ruled board region: the one ``board_region_sha256`` every resolved attempt logged.
    ``None`` (no change can be shown, nothing reopens) when one logged none or two differ."""
    from decision.owner_ruling import resolved_attempts

    found = {a.get("board_region_sha256") for a in resolved_attempts(ruling, attempts).values()}
    if len(found) != 1:
        return None
    region = found.pop()
    return region if isinstance(region, str) and _HEX.fullmatch(region) else None


def target(ruling: Mapping[str, Any]) -> str:
    """The reopen record's target for a board ruling: ``<subject>#<facet>`` (its epoch names the
    reading's settings), as a fact's is ``<subject>#<facet>`` (``ruling_reread.RECORD_FILE``)."""
    return f"{ruling.get('subject')}#{ruling.get('facet')}"


def recorded_reopen(ruling: Mapping[str, Any], attempts: Sequence[Mapping[str, Any]],
                    region: Any, reopened: Collection[tuple[str, str]]) -> str | None:
    """``<ruled epoch>:reopen:<region>`` when it is a reopened epoch of this ruling the gate may
    read in: ``region`` is a region hash, the ruling has a baseline and ``region`` is not it, and
    the sweep recorded exactly that epoch for the ruling's target (MODEL-562's rule for facts).
    Otherwise ``None``."""
    from decision.ruling_reread import reopen_epoch

    known = baseline(ruling, attempts)
    if not isinstance(region, str) or not _HEX.fullmatch(region) or known is None \
            or region == known:
        return None
    epoch = reopen_epoch(str(ruling["epoch"]), region)
    return epoch if (target(ruling), epoch) in reopened else None


def gate_epoch(ruling: Mapping[str, Any], attempts: Sequence[Mapping[str, Any]],
               region: str | None, reopened: Collection[tuple[str, str]] = frozenset()) -> str:
    """The epoch the gate reads a standing ruled row in: the ruled epoch, or the recorded
    reopened epoch (``recorded_reopen``) that ``region`` (the row's board region from pages the
    gate fetched itself) names. Anything else keeps the ruled epoch, where the disagreement
    blocks."""
    return recorded_reopen(ruling, attempts, region, reopened) or str(ruling["epoch"])


def superseding_epoch(ruling: Mapping[str, Any], attempts: Sequence[Mapping[str, Any]],
                      reopened: Collection[tuple[str, str]]) -> str | None:
    """The reopened epoch in which the ruling was superseded, or ``None`` while it stands. Only
    a complete, agreed harness attempt counts, logged after the ruling's resolved attempts, in a
    reopened epoch of the ruling that the sweep recorded (``recorded_reopen``) and whose logged
    ``board_region_sha256`` is the region that epoch names, on another score than the ruling's.
    Any other attempt under the ruling's epoch is ignored: a forged line cannot withhold a row."""
    from decision.cited_reader import canonical
    from decision.owner_ruling import REOPEN_MARK, _at, attempt_id, resolved_attempts

    epoch, facet = str(ruling["epoch"]), str(ruling["facet"])
    wanted = set(resolved_attempts(ruling, attempts))
    resolved = [(_at(a), i) for i, a in enumerate(attempts) if attempt_id(a) in wanted]
    if not resolved or any(t is None for t, _ in resolved):
        return None
    last = max(resolved)
    prefix = epoch + REOPEN_MARK
    for index, entry in enumerate(attempts):
        logged = entry.get("epoch")
        if (entry.get("subject"), entry.get("facet")) != (ruling.get("subject"), facet) \
                or not isinstance(logged, str) or not logged.startswith(prefix):
            continue
        region = logged[len(prefix):]
        at = _at(entry)
        if at is None or (at, index) <= last or entry.get("board_region_sha256") != region \
                or recorded_reopen(ruling, attempts, region, reopened) != logged:
            continue
        if entry.get("complete") is True and entry.get("agreed") is True \
                and entry.get("harness") is True and entry.get("agreed_value") is not None \
                and canonical(entry.get("agreed_value"), facet) \
                != canonical(ruling["value"], facet):
            return logged
    return None


def _key(line: Mapping[str, Any]) -> tuple[Any, Any, Any]:
    return line.get("subject"), line.get("facet"), line.get("epoch")


def epoch_problem(ruling: Mapping[str, Any], *, row: Mapping[str, Any], subject: str,
                  rulings: Sequence[Mapping[str, Any]], attempts: Sequence[Mapping[str, Any]],
                  sources: Mapping[str, str], max_score: Any = None, today: date | None = None,
                  reopened: Collection[tuple[str, str]] = frozenset(),
                  _depth: int = 0) -> tuple[str, str] | None:
    """Why the ruling's epoch is not one of this row's that the gate made, else ``None``. A board
    or reopened epoch is the gate's only when every resolved attempt logged the region it names;
    a reopened epoch also extends exactly one valid ruling whose baseline is another region, and
    the sweep recorded it (``recorded_reopen``, as for facts)."""
    from decision.owner_ruling import REOPEN_MARK, resolved_attempts, ruling_problem

    parsed = split_epoch(ruling.get("epoch"), row)
    if parsed is None or _depth > 64:
        return "epoch_not_current", "the ruling's epoch is not one of this reading's"
    _, regions = parsed
    named = named_region(str(ruling["epoch"]), row)
    if named is not None and any(a.get("board_region_sha256") != named
                                 for a in resolved_attempts(ruling, attempts).values()):
        return "epoch_not_current", "a resolved attempt did not log the region its epoch names"
    if not regions:
        return None
    prior_epoch = str(ruling["epoch"])[:-len(REOPEN_MARK + regions[-1])]
    prior = [r for r in rulings if _key(r) == (subject, ruling.get("facet"), prior_epoch)]
    if len(prior) != 1:
        return "epoch_not_current", "a reopened epoch extends no single ruling"
    if ruling_problem(prior[0], attempts=attempts, sources=sources, today=today,
                      max_score=max_score) is not None \
            or epoch_problem(prior[0], row=row, subject=subject, rulings=rulings,
                             attempts=attempts, sources=sources, max_score=max_score,
                             today=today, reopened=reopened, _depth=_depth + 1) is not None:
        return "epoch_not_current", "the ruling a reopened epoch extends is not valid"
    known = baseline(prior[0], attempts)
    if known is None or known == regions[-1]:
        return "epoch_not_current", "the reopened region is not a change from the ruled region"
    if recorded_reopen(prior[0], attempts, regions[-1], reopened) != ruling["epoch"]:
        return "epoch_not_current", "the sweep recorded no such reopened epoch"
    return None


def stale_problem(ruling: Mapping[str, Any], *, row: Mapping[str, Any], subject: str,
                  attempts: Sequence[Mapping[str, Any]]) -> tuple[str, str] | None:
    """The filer's test that the ruling's epoch is the reading's current one, else ``None``.
    Every attempt at the reading (its subject, facet and an epoch of its base) logged after the
    latest resolved attempt counts: one in another epoch means the reading moved on (a changed
    board region opened a new epoch), unless it is a reopened epoch of the ruling's, the re-read;
    and an agreement there on another score means there is nothing left to rule. Once a ruling
    is filed, only ``superseding_epoch`` ends it."""
    from decision.cited_reader import canonical
    from decision.owner_ruling import REOPEN_MARK, _at, attempt_id, resolved_attempts

    epoch, facet = str(ruling["epoch"]), str(ruling["facet"])
    wanted = set(resolved_attempts(ruling, attempts))
    resolved = [(i, _at(a)) for i, a in enumerate(attempts) if attempt_id(a) in wanted]
    if not resolved or any(t is None for _, t in resolved):
        return "no_disagreement", "a resolved attempt has no zoned time"
    # The latest resolved attempt by time, a later line on a tie (the log is append-only).
    last = max((t, i) for i, t in resolved)
    base = row_base(row)
    for index, entry in enumerate(attempts):
        logged = entry.get("epoch")
        if (entry.get("subject"), entry.get("facet")) != (subject, facet) \
                or not isinstance(logged, str) or not logged.startswith(base) or logged == epoch:
            continue
        at = _at(entry)
        if at is None:
            return "epoch_not_current", "an attempt at this reading has no zoned time"
        if (at, index) <= last:
            continue
        if not logged.startswith(epoch + REOPEN_MARK):
            return "epoch_not_current", "a later attempt read this reading in another epoch"
        if entry.get("complete") is True and entry.get("agreed") is True \
                and entry.get("harness") is True and entry.get("agreed_value") is not None \
                and canonical(entry.get("agreed_value"), facet) \
                != canonical(ruling["value"], facet):
            return "epoch_not_current", "a later agreement in a reopened epoch read another score"
    return None


def ruling_line(row: Mapping[str, Any], subject: str,
                rulings: Sequence[Mapping[str, Any]]) -> Mapping[str, Any] | None:
    """The one ruling line for the row's block's key, or ``None``."""
    from decision.owner_ruling import ruling_block

    block = ruling_block(row)
    if block is None:
        return None
    lines = [r for r in rulings if _key(r) == (subject, board_facet(row), block.get("epoch"))]
    return lines[0] if len(lines) == 1 else None


def row_problem(row: Mapping[str, Any], subject: str, *, rulings: Sequence[Mapping[str, Any]],
                attempts: Sequence[Mapping[str, Any]], sources: Mapping[str, str],
                max_score: Any = None, held: Sequence[Any] = (), today: date | None = None,
                registry: BoardRegistry | None = None,
                reopened: Collection[tuple[str, str]] = frozenset()
                ) -> tuple[str, str] | None:
    """``(reason, detail)`` when a board row that carries ``derivation.owner_ruling`` does not
    stand on a valid ruling, else ``None``. ``subject`` is the row's owner as the gate and the
    build place it (the attempt log's subject), ``held`` the verdicts that hold the row
    (``quarantine_clearing.reading_held``), ``today`` the last day the caller may know,
    ``registry`` the board-owner registries (``owner_problem``: none fails closed) and
    ``reopened`` the ``(target, epoch)`` pairs the sweep recorded
    (``ruling_reread.Records``). Details carry counts and field names only."""
    from decision.owner_ruling import (
        _exact,
        _same_instant,
        ruling_block,
        ruling_problem,
        source_copies,
    )

    block = ruling_block(row)
    if block is None:
        return "malformed", "the row carries no ruling block"
    stored = (row.get("subject") or {}).get("id") if isinstance(row.get("subject"), Mapping) \
        else None
    if stored is not None and stored != subject:
        return "malformed", "the row names another subject"
    ruling = ruling_line(row, subject, rulings)
    if ruling is None:
        return "malformed", "no single ruling line is filed for this reading and epoch"
    if _exact(dict(block)) != _exact(dict(ruling)):
        return "malformed", "the row's ruling block is not the filed line"
    problem = ruling_problem(ruling, attempts=attempts, sources=sources, today=today,
                             max_score=max_score) \
        or epoch_problem(ruling, row=row, subject=subject, rulings=rulings, attempts=attempts,
                         sources=sources, max_score=max_score, today=today, reopened=reopened)
    if problem is not None:
        return problem
    for source_id in ruling["source_ids"]:
        owned = owner_problem(registry, str(row.get("benchmark_id")), str(source_id))
        if owned is not None:
            return "not_cited", f"a ruling source is not the board owner's page ({owned[0]})"
    if superseding_epoch(ruling, attempts, reopened) is not None:
        return "epoch_not_current", "an agreement in a recorded reopened epoch superseded it"
    if held:
        return "quarantined", f"{len(held)} verdict(s) hold this reading; a ruling lifts none"
    if _exact(row.get("score")) != _exact(ruling["value"]) \
            or row.get("not_published_since") not in (None, ""):
        return "value_invalid", "the row's score is not the ruling's value"
    copies = source_copies(ruling, attempts, sources)
    refs = {str(r.get("source_id")): r for r in row.get("sources") or ()
            if isinstance(r, Mapping)}
    if set(copies) != set(ruling["source_ids"]):
        return "source_mismatch", "a ruling source has no copy a resolved attempt read"
    for source_id, (snapshot, at) in copies.items():
        ref = refs.get(source_id)
        if ref is None or ref.get("snapshot_ref") != snapshot \
                or not _same_instant(ref.get("retrieved_at"), at):
            return "source_mismatch", "the row does not cite a ruling source at its read copy"
    return None


def row_refused(row: Mapping[str, Any], subject: str, *, cited: bool,
                rulings: Sequence[Mapping[str, Any]], attempts: Sequence[Mapping[str, Any]],
                sources: Mapping[str, str], max_score: Any = None, held: Sequence[Any] = (),
                as_of: date | None = None, registry: BoardRegistry | None = None,
                reopened: Collection[tuple[str, str]] = frozenset()) -> bool:
    """The build's test for a board row: one that claims a ruling is refused (withheld) when it
    is not cited or its ruling does not stand at the cutoff (``owner_ruling.ruling_cutoff``). A
    row that claims no ruling is never refused here."""
    from decision.owner_ruling import has_ruling, ruling_cutoff

    if not has_ruling(row):
        return False
    return not cited or row_problem(row, subject, rulings=rulings, attempts=attempts,
                                    sources=sources, max_score=max_score, held=held,
                                    today=ruling_cutoff(as_of), registry=registry,
                                    reopened=reopened) is not None
