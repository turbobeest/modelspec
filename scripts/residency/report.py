#!/usr/bin/env python3
"""Count and audit the residency determinations (MODEL-79).

    python3 scripts/residency/report.py counts --store /path/to/data_residency.jsonl
    python3 scripts/residency/report.py audit  --store /path/to/data_residency.jsonl
    python3 scripts/residency/report.py platforms

`--store` is always given by the caller and always points outside this
repository. Residency determinations are policy determinations and live in the
private enrichment layer; what is public is the namespace, the classification
and the three counts. Omitting `--store` is legal and reports the shape of the
work with nothing determined — which is exactly what a clone of this repository
alone can honestly say.

`audit` exits 1 when a platform that needs a determination has no record. That
is the acceptance condition the ticket states as "none left ambiguous", made
runnable, so it can be checked rather than asserted.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.residency.determination import (  # noqa: E402
    PlatformResidency,
    classify,
    counts,
    load_store,
    unrecorded,
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
    return 0


def _audit(records: list[PlatformResidency]) -> int:
    missing = unrecorded(records)
    scopes = classify(records)
    for slug in platform_slugs():
        print(f"{slug:<22} {scopes[slug].value}")
    if not missing:
        print(
            f"\nall {len(requires_determination())} platforms that need a "
            f"determination have one; {len(LOCAL_RUNTIMES)} are unbounded by "
            "construction"
        )
        return 0
    print(f"\n{len(missing)} platform(s) have no determination on record:")
    for slug in missing:
        print(f"  {slug}")
    return 1


def _platforms(_: list[PlatformResidency]) -> int:
    for slug in platform_slugs():
        kind = "unbounded" if slug in LOCAL_RUNTIMES else "needs a determination"
        print(f"{slug:<22} {kind}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("counts", "audit", "platforms"))
    parser.add_argument(
        "--store",
        type=Path,
        default=None,
        help="JSON Lines determination store, outside this repository",
    )
    args = parser.parse_args(argv)
    records = _read(args.store)
    return {"counts": _counts, "audit": _audit, "platforms": _platforms}[args.command](records)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
