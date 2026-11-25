"""MODEL-523: remember where each source's fetch ended, and say when it moves.

A scheduled job calls ``observe`` after its fetches with the URLs each fetch
resolved through (the last one is where it ended). The record is one JSON object,
``{source_id: {final_url, final_host, first_seen, last_seen}}``, kept in a file the
job already commits. A source whose final host differs from its last record is
returned as a ``final_host_changed`` entry; the record then moves to the new host
(``first_seen`` restarts there). A run with nothing new writes nothing. Only a URL and a host are kept, never page bytes.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

# Re-exported: the helper lives with the retention rules, which the Worker bundles.
from decision.retention import ending_at_final as ending_at_final

#: The name a changed final host carries in a job's report.
FINAL_HOST_CHANGED = "final_host_changed"
#: Where the price re-read keeps the record, inside the data tree it already commits.
STATE_FILE = Path("verification") / "final-hosts.json"


def final_host(url: str) -> str:
    """The lower-case host of ``url``, without a port or trailing dot."""
    return (urlsplit(url).hostname or "").rstrip(".").lower()


def load(path: Path) -> dict[str, dict[str, str]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def observe(path: Path, finals: Mapping[str, Iterable[str]], today: date, *,
            write: bool = True) -> list[dict[str, str]]:
    """Record each source's final URL; return one entry per source whose host moved.

    ``finals`` maps a source ID to the URLs its fetch resolved through, in order.
    A source with none is left as it was. With ``write`` false nothing is written.
    """
    state = load(path)
    changes: list[dict[str, str]] = []
    dirty = False
    stamp = today.isoformat()
    for source_id in sorted(finals):
        urls = [str(u) for u in finals[source_id]]
        if not urls or not final_host(urls[-1]):
            continue
        url, host = urls[-1], final_host(urls[-1])
        old = state.get(source_id)
        if old is None or old.get("final_host") != host:
            if old is not None:
                changes.append({"source": source_id, "status": FINAL_HOST_CHANGED,
                                "old_host": str(old.get("final_host", "")), "new_host": host})
            state[source_id] = {"final_url": url, "final_host": host,
                                "first_seen": stamp, "last_seen": stamp}
            dirty = True
        elif old.get("final_url") != url:
            state[source_id] = {**old, "final_url": url, "last_seen": stamp}
            dirty = True
    # A run that sees nothing new leaves the file alone, so a quiet week commits nothing;
    # ``last_seen`` is the last day the record was written.
    if write and dirty:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return changes
