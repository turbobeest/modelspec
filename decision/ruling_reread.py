"""Owner-ruled facts on the rolling re-read: a changed cited region reopens rule 15 (MODEL-562).

An owner's ruling (``decision.owner_ruling``) settles one subject, facet and epoch whose two
readers disagreed. Inside that epoch the disagreement blocks rule 15 for good
(``prior_attempt_disagreed``), so the ruled value stands and nobody re-litigates it. A ruled
value can still go stale when the lab changes its page, so the rolling re-read
(``scripts/evidence_reread.py``) reads each page a standing ruling cites, with the gate's own
fetch (``decision.cited_change._fetch``: in memory, redirects off, every hop cite-only), and
compares two hashes, never page text:

* the page's visible-text hash (``decision.cited_reader.text_sha256``), against every text read
  in the ruled epoch (the attempt log records it);
* the cited-region hash (``region_sha256``): the text of each region the fact cites, selected
  by the source's own normaliser and locators (``decision.normalise``, volatile text such as
  dates and tracking stripped) and folded as rule 15 folds visible text.

A page whose visible text is one read in the ruled epoch is the ruled page: its region hash is
recorded once as the ruled baseline (``RECORD_FILE``), and nothing else happens. A page whose
visible text is new but whose region hash is the baseline changed outside what the fact cites
(a banner, a date): nothing happens. Only a region hash that differs from the baseline is a
change: the sweep appends one ``reopen`` line, and from then on rule 15 reads the fact in
``<ruled epoch>:reopen:<region hash>``, where two agreeing readers may supersede the ruling.
With no baseline (the page moved before the first sweep saw it), no change can be shown and
nothing reopens: the fact is counted ``unbaselined`` for a person.

The gate (``decision.cited_change._gate``) reads a ruled fact in a reopened epoch only when all
of these hold: the ruling stands as the build admits it (``owner_ruling.ruling_refused``); the
source is one of the ruling's; the gate fetched the page itself, with its own transport; the
page's visible text is none read in the ruled epoch; its region hash is not the baseline; and
the sweep has recorded exactly that reopened epoch for this fact and source. Otherwise the fact
stays in its ruled epoch, where the disagreement still blocks. A page back at the ruled region
is the ruled epoch again, and a disagreement inside a reopened epoch blocks that epoch. The
owner may rule again on such a disagreement (``scripts/file_owner_ruling.py`` accepts a
recorded reopened epoch); the ruling then names it (``owner_ruling.ruled_epoch``).

A ruling never lifts a quarantine and none is lifted here. Facts that a quarantine clearing
(MODEL-552) released carry a cited-change block of their own, so they are re-read with the
other cited-change facts, in the epoch their block's text hash names.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

#: The append-only record, under the data directory: ``baseline`` and ``reopen`` lines with ids
#: and hashes only. The weekly refresh keeps ``reports/evidence-reread/`` (its ``add-paths``).
RECORD_FILE = "reports/evidence-reread/ruled-reopenings.jsonl"
#: Exactly the fields of each kind of record line.
BASELINE_FIELDS = ("kind", "target", "ruled_epoch", "source_id", "region_sha256", "recorded_on")
REOPEN_FIELDS = ("kind", "target", "ruled_epoch", "source_id", "region_sha256",
                 "ruled_region_sha256", "epoch", "recorded_on")
_HEX = re.compile(r"[0-9a-f]{64}")


def reopen_epoch(ruled_epoch: str, region_sha: str) -> str:
    """The rule-15 epoch a ruled fact is read in once its cited region hashes as ``region_sha``."""
    from decision.owner_ruling import REOPEN_MARK

    return f"{ruled_epoch}{REOPEN_MARK}{region_sha}"


# --- the hashes ----------------------------------------------------------------------------------


def _fold(text: str) -> str:
    """Rule 15's fold of visible text (``decision.cited_reader.normalised_text``)."""
    import html

    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def region_sha256(fact: Mapping[str, Any], source_id: str, row: Mapping[str, Any],
                  page_bytes: bytes) -> str | None:
    """The hash of the regions of ``source_id`` the fact cites, or ``None`` when they cannot be
    selected (no registered region, an unknown normaliser or locator, content the normaliser
    refuses). A region that matches nothing hashes as absent, which is a change."""
    from decision.cited_reader import sha256
    from decision.normalise import (
        NORMALISERS, Locator, UnsupportedContentError, normalise_document, select_region,
    )

    ref = next((r for r in fact.get("sources") or () if isinstance(r, Mapping)
                and r.get("source_id") == source_id), None)
    registered = {str(r.get("id")): r for r in row.get("cited_regions") or ()
                  if isinstance(r, Mapping)}
    wanted = [str(i) for i in (ref or {}).get("cited_regions") or ()] or sorted(registered)
    rules = NORMALISERS.get(str(row.get("normaliser") or "html-default"))
    if not wanted or rules is None or any(i not in registered for i in wanted):
        return None
    try:
        doc = normalise_document(page_bytes, rules)
        parts = []
        for region_id in wanted:
            locator = registered[region_id].get("locator") or {}
            kind = str(locator.get("kind") or "page")
            kind = "heading" if kind == "heading_anchor" else kind
            text = select_region(doc, Locator(kind, str(locator.get("value") or "")))
            parts.append([region_id, None if text is None else _fold(text)])
    except (UnsupportedContentError, ValueError, TypeError):
        return None
    return sha256(json.dumps(parts, ensure_ascii=False, separators=(",", ":")))


def ruled_texts(attempts: Sequence[Mapping[str, Any]], *, subject: str, facet: str, epoch: str,
                url: str) -> frozenset[str] | None:
    """The visible-text hashes read in ``epoch`` on ``url``, from every attempt logged there,
    complete or not. ``None`` when an attempt there recorded no text hash."""
    out = set()
    for entry in attempts:
        if (entry.get("subject"), entry.get("facet"), entry.get("epoch"), entry.get("url")) \
                != (subject, facet, epoch, url):
            continue
        text = entry.get("text_sha256")
        if not isinstance(text, str) or not _HEX.fullmatch(text):
            return None
        out.add(text)
    return frozenset(out)


# --- the record ----------------------------------------------------------------------------------


@dataclass
class Records:
    """What ``RECORD_FILE`` holds: the first baseline per fact, ruled epoch and source, and every
    reopened epoch per fact."""

    baselines: dict[tuple[str, str, str], str] = field(default_factory=dict)
    reopened: dict[tuple[str, str], Mapping[str, Any]] = field(default_factory=dict)

    @classmethod
    def read(cls, data_dir: str | Path) -> Records:
        """Raises ``ValueError`` on a line that does not parse or repeats a key; a line of the
        wrong shape is ignored (it records nothing)."""
        from decision.owner_ruling import read_lines

        out = cls()
        for line in read_lines(Path(data_dir) / RECORD_FILE):
            hashes = [line.get(k) for k in ("region_sha256", "ruled_region_sha256")
                      if k in line]
            if not all(isinstance(h, str) and _HEX.fullmatch(h) for h in hashes):
                continue
            if line.get("kind") == "baseline" and set(line) == set(BASELINE_FIELDS):
                out.baselines.setdefault(
                    (str(line["target"]), str(line["ruled_epoch"]), str(line["source_id"])),
                    line["region_sha256"])
            elif line.get("kind") == "reopen" and set(line) == set(REOPEN_FIELDS) \
                    and line["epoch"] == reopen_epoch(str(line["ruled_epoch"]),
                                                      line["region_sha256"]):
                out.reopened.setdefault((str(line["target"]), str(line["epoch"])), line)
        return out


def baseline_line(*, target: str, ruled_epoch: str, source_id: str, region_sha: str,
                  day: date) -> dict[str, Any]:
    return {"kind": "baseline", "target": target, "ruled_epoch": ruled_epoch,
            "source_id": source_id, "region_sha256": region_sha, "recorded_on": day.isoformat()}


def reopen_line(*, target: str, ruled_epoch: str, source_id: str, region_sha: str,
                baseline: str, day: date) -> dict[str, Any]:
    return {"kind": "reopen", "target": target, "ruled_epoch": ruled_epoch,
            "source_id": source_id, "region_sha256": region_sha, "ruled_region_sha256": baseline,
            "epoch": reopen_epoch(ruled_epoch, region_sha), "recorded_on": day.isoformat()}


# --- the ruling ----------------------------------------------------------------------------------


def standing_ruling(fact: Mapping[str, Any], subject: str, *, inputs: Any,
                    sources: Mapping[str, str], today: date | None = None
                    ) -> Mapping[str, Any] | None:
    """The fact's ruling line when the build would admit the fact on it: the build's own test
    (``owner_ruling.ruling_refused``: one valid line for the fact's ruled epoch, the epoch's
    provenance in the attempt log, the ruling the latest claim, the fact's value, state and
    sources the ruling's, no held verdict, known by ``today``). Otherwise ``None``."""
    from decision.owner_ruling import has_ruling, ruled_epoch, ruling_refused

    if not has_ruling(fact) or ruling_refused(fact, subject, cited=True, inputs=inputs,
                                              sources=sources, as_of=today):
        return None
    key = (subject, str(fact.get("facet")), ruled_epoch(fact))
    lines = [r for r in inputs.rulings if (r.get("subject"), r.get("facet"), r.get("epoch")) == key]
    return lines[0] if len(lines) == 1 else None


@dataclass(frozen=True)
class PageStatus:
    """What one ruled page shows. ``kind``: ``current`` (the ruled page, or a change outside the
    cited region), ``baseline`` (the ruled page, its region hash not recorded yet), ``changed``
    (a new region hash, not recorded yet), ``open`` (a reopened epoch the sweep recorded),
    ``unbaselined`` (a new text and no baseline: no change can be shown), ``no_text_hash`` (an
    attempt in the ruled epoch recorded none) or ``unreadable_region``."""

    kind: str
    ruled_epoch: str
    region_sha: str | None = None
    baseline: str | None = None
    epoch: str | None = None


def page_status(fact: Mapping[str, Any], subject: str, *, source_id: str,
                row: Mapping[str, Any], page_bytes: bytes,
                attempts: Sequence[Mapping[str, Any]], records: Records) -> PageStatus:
    """The one comparison the sweep, the gate and ``reread`` make for a ruled fact's page."""
    from decision.cited_reader import text_sha256
    from decision.owner_ruling import ruled_epoch

    facet = str(fact.get("facet"))
    ruled = ruled_epoch(fact)
    target = f"{subject}#{facet}"
    seen = ruled_texts(attempts, subject=subject, facet=facet, epoch=ruled,
                       url=str(row.get("url")))
    if not seen:
        return PageStatus("no_text_hash", ruled)
    region = region_sha256(fact, source_id, row, page_bytes)
    if region is None:
        return PageStatus("unreadable_region", ruled)
    baseline = records.baselines.get((target, ruled, source_id))
    if text_sha256(page_bytes) in seen:
        return PageStatus("current" if baseline is not None else "baseline", ruled, region,
                          baseline)
    if baseline is None:
        return PageStatus("unbaselined", ruled, region)
    if region == baseline:
        return PageStatus("current", ruled, region, baseline)
    epoch = reopen_epoch(ruled, region)
    line = records.reopened.get((target, epoch))
    if line is not None and line.get("source_id") == source_id \
            and line.get("ruled_epoch") == ruled and line.get("ruled_region_sha256") == baseline:
        return PageStatus("open", ruled, region, baseline, epoch)
    return PageStatus("changed", ruled, region, baseline, epoch)


def _inputs(root: Path):
    from decision.owner_ruling import read_ruling_inputs

    return read_ruling_inputs(root)


def gate_epoch(fact: Mapping[str, Any], subject: str, *, source_id: str,
               rows: Mapping[str, Mapping[str, Any]], page_bytes: bytes, own_fetch: bool,
               data_dir: str | Path) -> str:
    """The epoch the gate reads a ruled fact in. A reopened epoch only from a page the gate
    fetched itself (``own_fetch``), for a standing ruling, on one of its sources, that the sweep
    recorded (``page_status`` is ``open``); else the ruled epoch for a standing ruling; else the
    fact's own epoch. A record or log that cannot be read leaves the fact in its own epoch."""
    from decision.cited_change import fact_epoch

    root = Path(data_dir)
    sources = {str(k): str(v.get("url")) for k, v in rows.items()
               if isinstance(v, Mapping) and v.get("url")}
    try:
        inputs = _inputs(root)
        ruling = standing_ruling(fact, subject, inputs=inputs, sources=sources)
        if ruling is None:
            return fact_epoch(fact)
        from decision.owner_ruling import ruled_epoch

        ruled = ruled_epoch(fact)
        if not own_fetch or source_id not in ruling["source_ids"]:
            return ruled
        status = page_status(fact, subject, source_id=source_id, row=rows[source_id],
                             page_bytes=page_bytes, attempts=inputs.attempts,
                             records=Records.read(root))
    except (OSError, ValueError, KeyError, TypeError):
        return fact_epoch(fact)
    return status.epoch if status.kind == "open" and status.epoch else ruled


def ruled_facts(data_dir: str | Path) -> list[dict[str, Any]]:
    """Every fact in the data directory's cards and offering files that claims an owner ruling,
    as ``{"subject", "facet"}``: the fact's location, as the build and the gate place it."""
    import yaml
    from schema.yaml_loader import load_yaml_unique

    from decision.owner_ruling import has_ruling

    root = Path(data_dir)
    out: list[dict[str, Any]] = []
    for path in sorted((root / "models").glob("*/*.md")):
        try:
            front = load_yaml_unique(path.read_text("utf-8").split("---", 2)[1])
            facts = front.get("facts") or []
        except (OSError, IndexError, AttributeError, yaml.YAMLError):
            continue
        out += [{"subject": f"{path.parent.name}/{path.stem}", "facet": f.get("facet")}
                for f in facts if isinstance(f, dict) and has_ruling(f)]
    for path in sorted((root / "offerings").rglob("*.yaml")):
        try:
            rows = load_yaml_unique(path.read_text("utf-8")) or []
            facts = [f for row in rows for f in row.get("facts") or []]
        except (OSError, AttributeError, TypeError, yaml.YAMLError):
            continue
        out += [{"subject": (f.get("subject") or {}).get("id"), "facet": f.get("facet")}
                for f in facts if isinstance(f, dict) and has_ruling(f)]
    return out
