"""Test helper: pin a test's whole attempt log as its legacy prefix (MODEL-491).

The ruling tests build their own attempt logs, with untagged and seeded splits written as the
gate wrote them before it tagged them. ``pin_whole_log`` treats each such log as the pinned
legacy prefix, so those tests keep checking what they check. The prefix rule itself is tested
in ``tests/test_gate_line_tags.py``.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


def pin_whole_log(monkeypatch) -> None:
    import decision.hold_evidence as he

    def read_legacy(root, path="verification/cited-attempts.jsonl"):
        file = Path(root) / path
        if not file.is_file():
            return ()
        data = file.read_bytes()
        return he.legacy_lines(path, data, {path: (len(data), hashlib.sha256(data).hexdigest())})

    monkeypatch.setattr(he, "read_legacy", read_legacy)
