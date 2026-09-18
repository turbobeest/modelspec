"""How much of the corpus has a `commercial_use` answer, counted from the cards.

The remaining count is a published number (MODEL-78), and it is deliberately
computed from the public cards rather than from the enrichment store. Anyone
can run this against a clone and get the same figure; a count that only the
holder of the determinations could produce would be a claim about the product
made by the product.

The three states it separates are the three MODEL-77 made expressible:

* `unspecified` — nobody has looked. This is the remaining tail.
* `withheld`   — determined, held in the enrichment layer. Answered, not here.
* a determination with a citation — determined and published in the open.

Run it with `python -m scripts.policy.coverage` from the repository root.
"""

from __future__ import annotations

import pathlib
import sys
from collections import Counter

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from schema.enums import UsePermission  # noqa: E402

DETERMINED = {
    UsePermission.ALLOWED.value,
    UsePermission.RESTRICTED.value,
    UsePermission.PROHIBITED.value,
    UsePermission.WITHHELD.value,
}


def card_states(models_dir: pathlib.Path | None = None) -> Counter:
    """`commercial_use` across every card, counted by value."""
    models_dir = models_dir or REPO_ROOT / "models"
    counts: Counter = Counter()
    for path in sorted(models_dir.rglob("*.md")):
        if path.name == "LICENSE.md":
            continue
        data = yaml.safe_load(path.read_text().split("---", 2)[1])
        value = (data.get("licensing") or {}).get("commercial_use")
        counts[str(value)] += 1
    return counts


def report(models_dir: pathlib.Path | None = None) -> str:
    counts = card_states(models_dir)
    total = sum(counts.values())
    answered = sum(n for value, n in counts.items() if value in DETERMINED)
    remaining = total - answered
    lines = [
        f"cards                {total}",
        f"commercial_use known {answered} ({answered / total:.1%})" if total else "",
        f"still unresearched   {remaining}",
        "",
        "by value:",
    ]
    lines += [f"  {value:14s} {n}" for value, n in counts.most_common()]
    return "\n".join(line for line in lines if line != "" or True)


if __name__ == "__main__":
    print(report())
