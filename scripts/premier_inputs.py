"""The board inputs of the lineup scripts are cite-only and are not kept.

The hosts behind ``premier/inputs`` forbid kept copies, so a missing input is
expected. The scripts stop with exit 2 and one message before any other work.
There is no reader here by design: the board is re-read in memory at
regeneration time.
"""

from __future__ import annotations

import sys
from collections.abc import Iterable
from pathlib import Path

EXIT_CITE_ONLY = 2


def require_inputs(directory: Path, names: Iterable[str]) -> None:
    """Exit 2 with one message if any named input file is missing."""
    for name in sorted(set(names)):
        if not (Path(directory) / name).is_file():
            sys.stderr.write(
                f"premier input {name} is cite-only: "
                "re-read the board in memory at regeneration time\n"
            )
            raise SystemExit(EXIT_CITE_ONLY)
