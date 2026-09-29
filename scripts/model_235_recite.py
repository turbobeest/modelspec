#!/usr/bin/env python3
"""Re-cite Claude Sonnet 5.5's direct-API prices to the plain pricing page (MODEL-235).

``collect_claude_sonnet_5_5.py`` read these five prices from a rendered copy of
platform.claude.com/docs/en/about-claude/pricing
(``model-s55-anthropic-pricing-rendered``), because the plain HTML did not list
Sonnet 5.5 yet. On 2026-09-29 the plain page (``anthropic-pricing``) does, with
the same values, so a plain fetch can re-read them every week.

The script re-points each fact to ``anthropic-pricing`` (``base-pricing`` for
standard prices, ``batch-pricing`` for batch), pinned to the copy in ``COPY``.
It files each value again as a claim and verifies it with the deterministic
readers, which log the outcome. The values do not change; the script refuses to
run if any of them fails to verify. The private-deployment fact still cites the
rendered copy.
"""

from __future__ import annotations

import re
import sys
from dataclasses import replace
from datetime import UTC, date, datetime
from pathlib import Path

from decision.model import SourceRef, VerificationActor
from decision.sources import CopyStore, load_sources
from decision.verify import Queue, StoredRegions, VerificationLog, deterministic_extractors, verify

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "offerings" / "anthropic" / "anthropic" / "claude-sonnet-5-5.yaml"
SUBJECT = "anthropic/anthropic/claude-sonnet-5-5/global/standard"
OLD_SOURCE = "model-s55-anthropic-pricing-rendered"
SOURCE = "anthropic-pricing"
#: The plain copy read on 2026-09-29.
COPY = "sha256:c0df0f1d4112d4934b9c45a360eab86006f5f6b1ac569e3b56c359c031b8a1f8"
REGIONS = {
    "input": "base-pricing", "output": "base-pricing", "cached_input": "base-pricing",
    "batch_input": "batch-pricing", "batch_output": "batch-pricing",
}
COLLECTOR = VerificationActor(agent="claude-model-235-recite", model_family="anthropic",
                              method="re-cite@2026-09-29")
AT = datetime(2026, 9, 29, 21, tzinfo=UTC)


def main() -> int:
    store = CopyStore()
    if not store.has(COPY):
        print(f"missing retained copy {COPY}", file=sys.stderr)
        return 1
    regions = StoredRegions(store, load_sources(ROOT / "registry" / "sources.yaml"))
    queue, log = Queue(ROOT / "verification"), VerificationLog(ROOT / "verification")
    filed = queue.filed()

    results = []
    for facet, region in REGIONS.items():
        target = f"{SUBJECT}#offering.price.{facet}"
        old = filed[("fact", target)]
        claim = replace(old, collector=COLLECTOR,
                        sources=(SourceRef(source_id=SOURCE, snapshot_ref=COPY,
                                           cited_regions=[region]),))
        result = verify(claim, regions, deterministic_extractors(), today=date(2026, 9, 29))
        if result.outcome != "verified" or result.verification is None:
            print(f"{target}: {result.outcome} {result.diffs}", file=sys.stderr)
            return 1
        results.append((facet, region, claim, result))

    text = FILE.read_text(encoding="utf-8")
    for facet, region, _, _ in results:
        block = re.compile(
            rf"(- id: {re.escape(SUBJECT)}#offering\.price\.{facet}\n(?:    .*\n)*?)"
            rf"    - source_id: {OLD_SOURCE}\n      snapshot_ref: sha256:[0-9a-f]{{64}}\n"
            rf"      cited_regions:\n      - [\w-]+\n")
        text, n = block.subn(
            rf"\g<1>    - source_id: {SOURCE}\n      snapshot_ref: {COPY}\n"
            rf"      cited_regions:\n      - {region}\n", text)
        if n != 1:
            print(f"{facet}: expected one source block, found {n}", file=sys.stderr)
            return 1
    FILE.write_text(text, encoding="utf-8")

    for _, _, claim, result in results:
        queue.file(claim, at=AT)
        log.append(result.verification)
        queue.checked(result, at=AT)
        print(f"{claim.target.id}: {claim.value} verified by {result.verification.method}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
