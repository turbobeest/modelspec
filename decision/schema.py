"""Write docs/decision-contract.schema.json from the contract types.

    python -m decision.schema
"""

from __future__ import annotations

from pathlib import Path

from decision.contract import render_json_schema

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "docs" / "decision-contract.schema.json"


def main() -> None:
    SCHEMA_PATH.write_text(render_json_schema())
    print(f"wrote {SCHEMA_PATH}")


if __name__ == "__main__":
    main()
