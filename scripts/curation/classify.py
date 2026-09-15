"""Conservative change classifier for the curation watcher (MODEL-10).

Maps a raw source change to the ticket's change kinds. Every kind needs textual
evidence that is new in this reading (present in the new text, absent from the
old). Anything else is `changed_unclassified`. It never guesses.

Kinds: new_version, leaderboard_dead, source_gone, deprecation, licence_change,
test_set_release, paper_revision, leaderboard_movement, changed_unclassified.
`saturation_crossing` and `dataset_change` are ticket kinds that part 1 does not
detect automatically: they need reading numbers and splits, which is the drafter's job.
"""
from __future__ import annotations

import difflib
import re

GONE_CODES = (404, 410)

_VERSION = re.compile(r"\b(?:v|version\s*)(\d+(?:\.\d+){0,2})\b", re.I)
_SUCCESSOR = re.compile(r"\b(successor|superseded by|replaced by|introducing \S+ (?:v?\d|pro|2|3))\b", re.I)
_DEPRECATION = re.compile(
    r"\b(deprecated|deprecation|retired|no longer (?:maintained|updated|supported)|"
    r"sunset(?:ting)?|this (?:repository|project|leaderboard) (?:is|has been) archived|archived)\b", re.I)
_LICENCE = re.compile(
    r"\b(MIT|Apache[- ]2\.0|BSD-[23]-Clause|GPL-[23]\.0|LGPL|AGPL|MPL-2\.0|"
    r"CC[- ]BY(?:[- ](?:SA|NC|ND))*(?:[- ]\d\.\d)?|CC0|ODC-BY|OpenRAIL\S*|Llama \d+ Community)\b", re.I)
_TEST_SET = re.compile(
    r"\b((?:private|hidden|held[- ]out|new) test[- ]set|test set (?:is )?(?:now )?released|"
    r"releas\w+ (?:of )?the test (?:set|split)|test split (?:is )?(?:now )?(?:public|available))\b", re.I)
_ARXIV_VER = re.compile(r"\barXiv:\s*\d{4}\.\d{4,5}v(\d+)|\[v(\d+)\]|\(v(\d+)\)", re.I)


def added_lines(old: str, new: str) -> list[str]:
    return [ln[2:] for ln in difflib.ndiff(old.splitlines(), new.splitlines()) if ln.startswith("+ ")]


def _norm_licence(s: str) -> str:
    return re.sub(r"[\s-]+", "-", s.upper())


def _arxiv_max(text: str) -> int:
    nums = [int(g) for m in _ARXIV_VER.finditer(text) for g in m.groups() if g]
    return max(nums, default=0)


def classify(*, url: str, roles: list[str], old: str, new: str,
             status: int | None, prev_status: int | None = None) -> list[dict]:
    """Return [{kind, evidence}]. An empty `new` with a failure status is a fetch failure."""
    if status in GONE_CODES:
        kind = "leaderboard_dead" if "leaderboard" in roles else "source_gone"
        return [{"kind": kind, "evidence": f"HTTP {status}"}]
    if status is None or not (200 <= status < 300):
        return [{"kind": "fetch_failed", "evidence": f"status {status}"}]

    added = added_lines(old, new)
    added_text = "\n".join(added)
    kinds: list[dict] = []

    old_versions = {m.group(1) for m in _VERSION.finditer(old)}
    new_versions = [m.group(0) for m in _VERSION.finditer(added_text) if m.group(1) not in old_versions]
    if new_versions:
        kinds.append({"kind": "new_version", "evidence": f"new version string {new_versions[0]!r}"})
    elif (m := _SUCCESSOR.search(added_text)) and not _SUCCESSOR.search(old):
        kinds.append({"kind": "new_version", "evidence": f"successor wording {m.group(0)!r}"})

    if (m := _DEPRECATION.search(added_text)) and not _DEPRECATION.search(old):
        kinds.append({"kind": "deprecation", "evidence": f"{m.group(0)!r} appeared"})

    old_lic = {_norm_licence(x.group(0)) for x in _LICENCE.finditer(old)}
    new_lic = {_norm_licence(x.group(0)) for x in _LICENCE.finditer(new)}
    if old_lic and new_lic and old_lic != new_lic:
        kinds.append({"kind": "licence_change",
                      "evidence": f"licence tokens {sorted(old_lic)} -> {sorted(new_lic)}"})

    if (m := _TEST_SET.search(added_text)) and not _TEST_SET.search(old):
        kinds.append({"kind": "test_set_release", "evidence": f"{m.group(0)!r} appeared"})

    if "arxiv.org" in url or "paper" in roles:
        ov, nv = _arxiv_max(old), _arxiv_max(new)
        if ov and nv > ov:
            kinds.append({"kind": "paper_revision", "evidence": f"arXiv v{ov} -> v{nv}"})

    if not kinds and "leaderboard" in roles:
        kinds.append({"kind": "leaderboard_movement",
                      "evidence": f"leaderboard content changed ({len(added)} added lines)"})
    if not kinds:
        kinds.append({"kind": "changed_unclassified", "evidence": f"{len(added)} added lines"})
    return kinds
