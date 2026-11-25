"""Owner-ruled facts on the rolling re-read: a changed page reopens rule 15 (MODEL-562).

An owner's ruling (``decision.owner_ruling``) settles one subject, facet and epoch whose two
readers disagreed. Inside that epoch the disagreement blocks rule 15 for good
(``prior_attempt_disagreed``), so the ruled value stands and nobody re-litigates it. A ruled
value can still go stale when the lab changes its page, so the rolling re-read
(``scripts/evidence_reread.py``) reads each page a standing ruling cites:

* While the page's visible text hashes (``decision.cited_reader.text_sha256``) as a text read
  in the ruled epoch, the page is unchanged: the ruled value is kept and no reader is asked.
* When it hashes as no text read in the ruled epoch, the page changed. The re-read records the
  hash (``RECORD_FILE``, append-only, hashes and ids only, never page text) and counts the
  fact as reopened. Rule 15 then reads the fact in a new epoch, ``reopen_epoch``, named by the
  ruled epoch and the changed text's hash, where two agreeing readers may supersede the ruling.

The epoch is derived from the page itself, never from a caller or from a log line: the gate
(``decision.cited_change._gate``) fetches the page, and ``epoch_for_page`` names the reopened
epoch only when every condition holds. The fact carries a valid ruling (exactly one ruling
line, equal to its block, that ``ruling_problem`` passes); the source read is one of the
ruling's; every attempt logged in the ruled epoch on that page recorded a text hash; and the
page's text hash is none of them. Otherwise the fact stays in its ruled epoch, where the
recorded disagreement still blocks. A page that returns to a text read in the ruled epoch
is that epoch again, and a page that returns to a text of a reopened epoch is that reopened
epoch again: a disagreement there still blocks. Attempts in the ruled epoch do not count in
a reopened one; a new text is new evidence.

A ruling never lifts a quarantine and none is lifted here. Facts that a quarantine clearing
(MODEL-552) released carry a cited-change block of their own, so they are re-read with the
other cited-change facts, in the epoch their block's text hash names.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path
from typing import Any

#: The append-only record of reopened epochs, under the data directory: one line per ruled
#: fact and changed page text, with ids and hashes only. The weekly refresh keeps
#: ``reports/evidence-reread/`` (its ``add-paths``), so the line is committed with the run.
RECORD_FILE = "reports/evidence-reread/ruled-reopenings.jsonl"
REOPEN_MARK = ":reopen:"
#: Exactly the fields of a record line.
FIELDS = ("target", "subject", "facet", "ruled_epoch", "source_id", "text_sha256", "epoch",
          "opened_on")


def reopen_epoch(ruled_epoch: str, text_sha: str) -> str:
    """The rule-15 epoch a ruled fact is read in once its page's text hashes as ``text_sha``."""
    return f"{ruled_epoch}{REOPEN_MARK}{text_sha}"


def standing_ruling(fact: Mapping[str, Any], subject: str, *, rulings: Sequence[Mapping[str, Any]],
                    attempts: Sequence[Mapping[str, Any]], sources: Mapping[str, str],
                    today: date | None = None) -> Mapping[str, Any] | None:
    """The fact's ruling line when it is valid: exactly one line for this subject, facet and the
    fact's own epoch, equal to the fact's ruling block, that ``ruling_problem`` passes."""
    from decision.owner_ruling import _exact, fact_epoch, ruling_block, ruling_problem

    block = ruling_block(fact)
    if block is None:
        return None
    key = (subject, str(fact.get("facet")), fact_epoch(fact))
    lines = [r for r in rulings if (r.get("subject"), r.get("facet"), r.get("epoch")) == key]
    if len(lines) != 1 or _exact(dict(block)) != _exact(dict(lines[0])):
        return None
    if ruling_problem(lines[0], attempts=attempts, sources=sources, today=today) is not None:
        return None
    return lines[0]


def ruled_texts(attempts: Sequence[Mapping[str, Any]], *, subject: str, facet: str, epoch: str,
                url: str) -> frozenset[str] | None:
    """The text hashes read in ``epoch`` on ``url``, from every attempt logged there, complete or
    not. ``None`` when an attempt there recorded no text hash: then a change cannot be shown."""
    out = set()
    for entry in attempts:
        if (entry.get("subject"), entry.get("facet"), entry.get("epoch"), entry.get("url")) \
                != (subject, facet, epoch, url):
            continue
        text = entry.get("text_sha256")
        if not isinstance(text, str) or len(text) != 64:
            return None
        out.add(text)
    return frozenset(out)


def epoch_for_page(fact: Mapping[str, Any], subject: str, *, source_id: str, url: str,
                   text_sha: str, rulings: Sequence[Mapping[str, Any]],
                   attempts: Sequence[Mapping[str, Any]], sources: Mapping[str, str],
                   today: date | None = None) -> str:
    """The epoch rule 15 reads a fact in, given the text hash of the page it read.

    For a fact with a standing ruling, read on one of the ruling's sources whose text hashes as
    no text read in the ruled epoch: ``reopen_epoch``. For every other fact, and whenever a
    condition fails: the fact's own epoch (``decision.cited_change.fact_epoch``)."""
    from decision.cited_change import fact_epoch

    ruled = fact_epoch(fact)
    ruling = standing_ruling(fact, subject, rulings=rulings, attempts=attempts, sources=sources,
                             today=today)
    if ruling is None or source_id not in (ruling.get("source_ids") or ()) \
            or sources.get(source_id) != url:
        return ruled
    seen = ruled_texts(attempts, subject=subject, facet=str(fact.get("facet")), epoch=ruled,
                       url=url)
    if not seen or text_sha in seen:
        return ruled
    return reopen_epoch(ruled, text_sha)


def gate_epoch(fact: Mapping[str, Any], subject: str, *, source_id: str, url: str,
               page_bytes: bytes, sources: Mapping[str, str], data_dir: str | Path) -> str:
    """``epoch_for_page`` from a data directory's ruling and attempt logs, for the gate. A log
    that cannot be read leaves the fact in its own epoch."""
    from decision.cited_change import fact_epoch
    from decision.cited_reader import ATTEMPTS_FILE, text_sha256
    from decision.owner_ruling import RULINGS_FILE, read_lines

    root = Path(data_dir)
    try:
        rulings = read_lines(root / RULINGS_FILE)
        attempts = read_lines(root / ATTEMPTS_FILE) if rulings else []
    except (OSError, ValueError):
        return fact_epoch(fact)
    if not rulings:
        return fact_epoch(fact)
    return epoch_for_page(fact, subject, source_id=source_id, url=url,
                          text_sha=text_sha256(page_bytes), rulings=rulings, attempts=attempts,
                          sources=sources)


def ruled_facts(data_dir: str | Path) -> list[dict[str, Any]]:
    """Every fact in the data directory's cards and offering files that claims an owner ruling,
    as ``{"subject", "facet", "fact"}``. The subject is the fact's location, as the build and the
    gate place it: the card's path, or the offering fact's own subject id."""
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
        for fact in facts:
            if isinstance(fact, dict) and has_ruling(fact):
                out.append({"subject": f"{path.parent.name}/{path.stem}",
                            "facet": fact.get("facet"), "fact": fact})
    for path in sorted((root / "offerings").rglob("*.yaml")):
        try:
            rows = load_yaml_unique(path.read_text("utf-8")) or []
            facts = [f for row in rows for f in row.get("facts") or []]
        except (OSError, AttributeError, TypeError, yaml.YAMLError):
            continue
        for fact in facts:
            if isinstance(fact, dict) and has_ruling(fact):
                out.append({"subject": (fact.get("subject") or {}).get("id"),
                            "facet": fact.get("facet"), "fact": fact})
    return out


def recorded(data_dir: str | Path) -> set[tuple[str, str]]:
    """``(target, epoch)`` of every line already in ``RECORD_FILE``."""
    path = Path(data_dir) / RECORD_FILE
    if not path.is_file():
        return set()
    out = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entry = json.loads(line)
            out.add((str(entry.get("target")), str(entry.get("epoch"))))
    return out


def record_line(*, subject: str, facet: str, ruled_epoch: str, source_id: str, text_sha: str,
                day: date) -> dict[str, Any]:
    """One record line: the reopened epoch of one ruled fact, from one changed page."""
    return {"target": f"{subject}#{facet}", "subject": subject, "facet": facet,
            "ruled_epoch": ruled_epoch, "source_id": source_id, "text_sha256": text_sha,
            "epoch": reopen_epoch(ruled_epoch, text_sha), "opened_on": day.isoformat()}
