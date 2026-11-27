"""What the gate logged that can show why a fact stays held (MODEL-491).

Once ``retained-source-proof@1`` stops counting, a fact that no honest read can verify stays held,
and the private data lists it with its reason. This module holds the evidence such a listing
rests on. It is hold evidence only: nothing here serves a value or moves a record, and
``quarantine_clearing.line_kind`` (the kinds that move or serve) knows none of it.

- **A tagged read.** ``read_page`` writes the gate's ``kind`` into every fact read it logs, under
  the line's hash: ``split`` (the two readers disagreed), ``silent`` (both agreed the page states
  nothing) or ``refused`` (a reader gave no usable answer). ``hold_kind`` returns ``split`` or
  ``silent`` for such a line.
- **A legacy read.** Before the gate wrote those tags, it logged the same reads untagged. An
  untagged line counts the same way only if it lies in the attempt log's pinned legacy prefix:
  the log's first bytes as they stood in the private data before the gate wrote these tags,
  pinned here by byte length and sha256 (``LEGACY_ATTEMPTS``). The append-only guard keeps that
  prefix unchanged. A line appended after it needs the real tag, and if one byte of the prefix
  differs, no line is legacy.
- **A refusal before any read.** When the gate refuses a fact before reading it, it appends one
  tagged line to its own log (``REFUSALS_FILE``) with the fact, its value hash, the refusal
  reason and the fact's epoch. That line is not a read: no attempt reader sees it, so it is never
  a retry or a disagreement.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any

#: ``verification/cited-attempts.jsonl`` in the private data as it stood before the gate wrote
#: these tags: its byte length and the sha256 of those bytes. A count and a digest only.
LEGACY_ATTEMPTS = (318087,
                   "84fa41926889833e06be732a346d307da0f4550280fc9d6479a322d5ba58bae7")

HOLD_KINDS = ("split", "silent")
REFUSALS_FILE = "verification/cited-refusals.jsonl"
REFUSAL_RULE = "gate-refusal@1"
REFUSAL_FIELDS = ("at", "epoch", "fact_id", "facet", "kind", "reason", "rule", "source_id",
                  "subject", "value_hash")


def legacy_count(lines: Sequence[str], pinned: tuple[int, str] = LEGACY_ATTEMPTS) -> int:
    """How many leading lines of the attempt log (``AttemptLog.lines``, each a line without its
    newline) are its pinned legacy prefix, byte for byte: ``0`` unless the log's first lines,
    each followed by a newline, are exactly the pinned bytes."""
    length, digest = pinned
    size, digest_now = 0, hashlib.sha256()
    for n, raw in enumerate(lines):
        chunk = raw.encode("utf-8") + b"\n"
        size += len(chunk)
        if size > length:
            return 0
        digest_now.update(chunk)
        if size == length:
            return n + 1 if digest_now.hexdigest() == digest else 0
    return 0


def hold_kind(log: Any, raw: str, *, pinned: tuple[int, str] = LEGACY_ATTEMPTS) -> str | None:
    """``split`` or ``silent`` when the attempt line ``raw`` (a line of ``log``, an
    ``AttemptLog``) shows that hold, else ``None``. A tagged line shows what its tag says. An
    untagged line shows it only inside the legacy prefix, by its own fields: a complete harness
    attempt whose readers disagreed, or agreed the page states nothing."""
    from decision.owner_ruling import loads

    if raw not in log.lines:
        return None
    entry = loads(raw)
    if not isinstance(entry, Mapping):
        return None
    if "kind" in entry:
        return entry["kind"] if entry["kind"] in HOLD_KINDS else None
    if raw not in log.lines[:legacy_count(log.lines, pinned)]:
        return None
    if entry.get("complete") is not True or entry.get("harness") is not True:
        return None
    if entry.get("agreed") is False:
        return "split"
    if entry.get("agreed") is True and entry.get("agreed_value") is None:
        return "silent"
    return None


def refusal_line(*, subject: str, facet: str, value_hash: str, reason: str, epoch: str,
                 source_id: str, at: datetime) -> dict[str, Any]:
    """The line the gate appends when it refuses a fact before reading it."""
    return {"at": at.replace(microsecond=0).isoformat(), "epoch": epoch,
            "fact_id": f"{subject}#{facet}", "facet": facet, "kind": "refusal", "reason": reason,
            "rule": REFUSAL_RULE, "source_id": source_id, "subject": subject,
            "value_hash": value_hash}


def refusals_path(data_dir: str | Path | None = None) -> Path | None:
    root = data_dir or os.environ.get("MODELSPEC_DATA_DIR", "").strip()
    return Path(root) / REFUSALS_FILE if root else None


def log_refusal(entry: Mapping[str, Any], *, data_dir: str | Path | None = None) -> None:
    """Append one refusal line. The log is append-only, like the attempt log."""
    path = refusals_path(data_dir)
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(dict(entry), sort_keys=True, ensure_ascii=False) + "\n")


def read_refusals(path: Path) -> list[str]:
    """The refusal log's raw lines (no blank ones), for a listing to name by hash."""
    if not path.is_file():
        return []
    return [raw for raw in path.read_text(encoding="utf-8").split("\n") if raw.strip()]
