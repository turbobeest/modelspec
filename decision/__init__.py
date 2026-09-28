"""The decision engine (slice 1; design: `docs/design/decision-engine.md`). The contract is ``decision.contract``.

A new package beside v1. Nothing here is imported by `api/ranking/` or
`pipeline/ranking.py`, and nothing here changes `/v1/rank`.
"""

from decision.contract import CONTRACT_VERSION, Decision, Spec, SpecError, parse_spec, spec_hash
from decision.engine import decide
from decision.filter import apply
from decision.resolve import resolve

__all__ = ["CONTRACT_VERSION", "Decision", "Spec", "SpecError", "apply", "decide", "parse_spec",
           "resolve", "spec_hash"]
