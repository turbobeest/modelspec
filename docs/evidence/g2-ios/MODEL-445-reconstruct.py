"""Reconstruct selected watcher observations from public issue metadata only."""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from release_signals.watch import load_registry
from scripts.triage_release_discoveries import _signal

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--issues", type=Path, required=True)
parser.add_argument("--out", type=Path, required=True)
parser.add_argument("--timezone", default="UTC")
args = parser.parse_args()
zone = ZoneInfo(args.timezone)
issues = json.loads(args.issues.read_text())
sources = {source.id: source for source in load_registry().sources}
observations = []
selected = []
for issue in issues:
    day = datetime.fromisoformat(issue["createdAt"].replace("Z", "+00:00")).astimezone(zone).date()
    if not "2026-10-21" <= day.isoformat() < "2026-11-05":
        continue
    selected.append(issue)
    signal = _signal(issue["body"])
    refs = re.findall(r"^- `([^`]+)`: `([^`]+)` at (\S+)$", issue["body"], re.MULTILINE)
    if not refs:
        url = urlsplit(signal.first_seen_url)
        matches = [source for source in sources.values() if (
            source.url == signal.first_seen_url or
            source.kind == "openrouter" and url.hostname == "openrouter.ai" or
            source.kind == "huggingface" and url.hostname == "huggingface.co"
            and parse_qs(urlsplit(source.url).query)["author"][0].casefold()
            == url.path.strip("/").split("/")[0].casefold()
        )]
        if len(matches) != 1:
            raise ValueError(f"issue #{issue['number']} has no unique source")
        refs = [(matches[0].id, signal.model_name, signal.first_seen_url)]
    for index, (source_id, name, url) in enumerate(refs):
        source = sources[source_id]
        observations.append({
            "source_id": source_id, "source_key": f"issue:{issue['number']}:{index}",
            "model_name": name, "provider": source.provider or signal.provider,
            "url": url, "created": None, "issue_url": issue["url"],
        })
report = {
    "observed_at": max(_signal(issue["body"]).timestamp for issue in selected),
    "provenance": "Public issue metadata; source creation dates and missing observations unknown.",
    "window": {"start": "2026-10-21", "end_exclusive": "2026-11-05", "timezone": args.timezone},
    "issue_count": len(selected), "observations": observations,
}
args.out.write_text(json.dumps(report, indent=2) + "\n")
print(f"{len(selected)} issues, {len(observations)} observations, {args.timezone}")
