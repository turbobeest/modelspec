"""The decision engine (slice 1). The contract is ``decision.contract``."""

from decision.contract import CONTRACT_VERSION, Decision, Spec, SpecError, parse_spec, spec_hash
from decision.engine import decide

__all__ = ["CONTRACT_VERSION", "Decision", "Spec", "SpecError", "decide", "parse_spec",
           "spec_hash"]
