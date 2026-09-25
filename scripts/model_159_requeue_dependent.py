#!/usr/bin/env python3
"""Requeue values only a same-family reader verified (MODEL-159).

Two keys means another model family. The log already held values whose only
``verified`` came from the collector's own family; those no longer count, so
the values are quarantined again. This prints them and requeues each one, so
``modelspec verify --changed-only --llm-reader mistral`` re-reads them with a
third family.
"""

from __future__ import annotations

from datetime import UTC, datetime

from decision.verify import DEFAULT_DIRECTORY, Queue, VerificationLog, ref_str


def main() -> None:
    targets = VerificationLog(DEFAULT_DIRECTORY).requarantined()
    print(f"re-quarantined by the family rule: {len(targets)}")
    for target in targets:
        print(f"  {ref_str(target)}  {target.value_hash}")
    Queue(DEFAULT_DIRECTORY).requeue([ref_str(t) for t in targets], at=datetime.now(UTC))


if __name__ == "__main__":
    main()
