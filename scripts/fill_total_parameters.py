#!/usr/bin/env python3
"""Deprecated. Parameter counts come from Hub safetensors, not names.

The previous implementation filled `total_parameters` from the filename
(`Mixtral-8x7B` → 7B). That is how the catalogue emitted FITS_ON edges for
hardware that cannot hold the weights. Run `scripts/fetch_total_parameters.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.fetch_total_parameters import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
