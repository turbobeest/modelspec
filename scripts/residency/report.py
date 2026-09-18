#!/usr/bin/env python3
"""Count and audit the residency determinations (MODEL-79).

    python3 scripts/residency/report.py counts     --store /path/to/data_residency.jsonl
    python3 scripts/residency/report.py disclosure --store /path/to/data_residency.jsonl
    python3 scripts/residency/report.py audit      --store /path/to/data_residency.jsonl
    python3 scripts/residency/report.py platforms

`--store` is always given by the caller and always points outside this
repository. Residency determinations are policy determinations and live in the
private enrichment layer; what is public is the namespace, the classification
and the three counts. Omitting `--store` is legal and reports the shape of the
work with nothing determined — which is exactly what a clone of this repository
alone can honestly say.

`disclosure` is the same 50 platforms seen from a card instead of from the
store: what each one publishes, and the tally of the three `DisclosureState`s.
Two records that look alike in `counts` — read-and-empty, and never reached —
land on different sides of it, which is the whole of MODEL-79's 2026-09-17
decision made visible.

`audit` exits 1 when a platform that needs a determination has no record, or
when a withheld platform has no paid-tier answer. That is the acceptance
condition the ticket states as "none left ambiguous", made runnable, so it can
be checked rather than asserted.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schema.enums import DisclosureState  # noqa: E402
from scripts.residency.determination import (  # noqa: E402
    PlatformResidency,
    classify,
    counts,
    disclosure_counts,
    disclosures,
    load_store,
    unreached,
    unresolved_withheld,
    unrecorded,
    withheld,
)
from scripts.residency.platforms import (  # noqa: E402
    LOCAL_RUNTIMES,
    ResidencyScope,
    platform_slugs,
    requires_determination,
)

#: One line each, so the report reads as prose rather than as an enum dump.
GLOSS = {
    ResidencyScope.DETERMINED: "region list determined, cited and dated",
    ResidencyScope.UNBOUNDED: "unbounded by construction (runs on the operator's machine)",
    ResidencyScope.UNDETERMINED: "null — no published region list was read, with reasons",
}

#: The card-facing gloss. `withheld` carries two unlike answers and says so
#: here, because a reader who takes it to mean only "held back for sale" will
#: misread 28 of them.
DISCLOSURE_GLOSS = {
    DisclosureState.WITHHELD: (
        "determined — a cited region list, or a reading that found no commitment"
    ),
    DisclosureState.UNRESEARCHED: (
        "nobody looked, or looked and could not reach it; plus the local runtimes"
    ),
    DisclosureState.PUBLISHED: "on the public card (always 0: policy determinations are not)",
}


def _read(store: Path | None) -> list[PlatformResidency]:
    return load_store(store) if store is not None else []


def _counts(records: list[PlatformResidency]) -> int:
    tally = counts(records)
    total = sum(tally.values())
    print(f"{total} platforms on Availability")
    for scope in (
        ResidencyScope.DETERMINED,
        ResidencyScope.UNBOUNDED,
        ResidencyScope.UNDETERMINED,
    ):
        print(f"  {tally[scope]:>3}  {scope.value:<13} {GLOSS[scope]}")
    missing = unrecorded(records)
    if missing:
        print(
            f"\n  of the {tally[ResidencyScope.UNDETERMINED]} null, "
            f"{len(missing)} have no record at all — never looked at, "
            "not looked at and found empty"
        )
    blocked = unreached(records)
    if blocked:
        print(
            f"\n  and {len(blocked)} were recorded as unreachable from the "
            "network the work was done on — attempted, not established:"
        )
        for slug in blocked:
            print(f"    {slug}")
    return 0


def _disclosure(records: list[PlatformResidency]) -> int:
    states = disclosures(records)
    tally = disclosure_counts(records)
    for slug in platform_slugs():
        print(f"{slug:<22} {states[slug].value}")
    print(f"\n{sum(tally.values())} platforms, as their cards read")
    for state in (
        DisclosureState.WITHHELD,
        DisclosureState.UNRESEARCHED,
        DisclosureState.PUBLISHED,
    ):
        print(f"  {tally[state]:>3}  {state.value:<13} {DISCLOSURE_GLOSS[state]}")
    blocked = set(unreached(records))
    overlap = sorted(blocked & set(withheld(records)))
    if overlap:
        # Unreachable in the type system as written; checked anyway, because
        # this is the one error the report exists to make impossible and a
        # report that prints it calmly is worse than no report.
        raise AssertionError(
            f"unreached platforms published as withheld: {overlap}. "
            "'withheld' claims a determination; nobody reached these."
        )
    if blocked:
        print(
            f"\n  {len(blocked)} of the unresearched were attempted and could "
            "not be reached; they are work, not findings"
        )
    return 0


def _audit(records: list[PlatformResidency]) -> int:
    missing = unrecorded(records)
    broken = unresolved_withheld(records)
    scopes = classify(records)
    for slug in platform_slugs():
        print(f"{slug:<22} {scopes[slug].value}")
    status = 0
    if missing:
        print(f"\n{len(missing)} platform(s) have no determination on record:")
        for slug in missing:
            print(f"  {slug}")
        status = 1
    if broken:
        print(
            f"\n{len(broken)} withheld platform(s) have no paid-tier answer "
            "(a card says withheld; the store has nothing to serve):"
        )
        for slug in broken:
            print(f"  {slug}")
        status = 1
    if status == 0:
        print(
            f"\nall {len(requires_determination())} platforms that need a "
            f"determination have one; {len(LOCAL_RUNTIMES)} are unbounded by "
            "construction"
        )
        _recheck_note(records)
    return status


def _recheck_note(records: list[PlatformResidency]) -> None:
    """Unreached platforms are outstanding work, and `audit` says so without
    failing on them. They *have* a record — somebody tried and wrote down what
    happened — so they are not the ambiguity `audit`'s exit code is about."""
    blocked = unreached(records)
    if not blocked:
        return
    print(f"\n{len(blocked)} recorded as unreachable from this network; recheck:")
    for slug in blocked:
        print(f"  {slug}")


def _platforms(_: list[PlatformResidency]) -> int:
    for slug in platform_slugs():
        kind = "unbounded" if slug in LOCAL_RUNTIMES else "needs a determination"
        print(f"{slug:<22} {kind}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("counts", "disclosure", "audit", "platforms"))
    parser.add_argument(
        "--store",
        type=Path,
        default=None,
        help="JSON Lines determination store, outside this repository",
    )
    args = parser.parse_args(argv)
    records = _read(args.store)
    commands = {
        "counts": _counts,
        "disclosure": _disclosure,
        "audit": _audit,
        "platforms": _platforms,
    }
    return commands[args.command](records)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
