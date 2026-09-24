"""The decision engine (slice 1; design: `docs/design/decision-engine.md`). The contract is ``decision.contract``.

A new package beside v1. Nothing here is imported by `api/ranking/` or
`pipeline/ranking.py`, and nothing here changes `/v1/rank`.
"""

from decision.contract import CONTRACT_VERSION, Decision, Spec, SpecError, parse_spec, spec_hash
from decision.engine import decide

__all__ = ["CONTRACT_VERSION", "Decision", "Spec", "SpecError", "decide", "parse_spec",
           "spec_hash"]
