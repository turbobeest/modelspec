"""Words a breakdown never uses (standard §5).

A breakdown describes evidence. It does not grade a lab's honesty, intent or
marketing, and it uses no superlative the evidence does not support. The
renderer refuses its own output if any of these appear, and ticket 2's
renderer applies the same list to human commentary.
"""

from __future__ import annotations

import re

#: Each pattern is a word stem or phrase, matched case-insensitively on word
#: boundaries. "best" is not here: it is ModelSpec's band name.
REFUSED = (
    r"inflat\w*",
    r"overstat\w*",
    r"understat\w*",
    r"mislead\w*",
    r"cherry[\s-]?pick\w*",
    r"hype[ds]?",
    r"exaggerat\w*",
    r"dishonest\w*",
    r"fudg\w*",
    r"padd(?:ed|ing)",
    r"sandbag\w*",
    r"spin",
    r"gam(?:ed|ing) the",
    r"number one",
    r"no\.\s?1",
    r"#1",
    r"world'?s best",
    r"crush\w*",
    r"destroy\w*",
    r"dominat\w*",
    r"disappoint\w*",
    r"impressive\w*",
    r"stunning\w*",
    r"massive\w*",
    r"huge",
    r"blows? away",
    r"beats?",
    r"falls? short",
)
_REFUSED = re.compile(
    r"(?<![\w#])(?:" + "|".join(REFUSED) + r")(?!\w)", re.IGNORECASE
)


def refused_words(text: str) -> list[str]:
    """Every refused word or phrase in ``text``, in order."""
    return [match.group(0) for match in _REFUSED.finditer(text)]
