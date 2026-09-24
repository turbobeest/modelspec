"""Runs a spec against a snapshot.

``decision.resolve`` and ``decision.filter`` are the first two stages
(MODEL-141). Optimise and explain land in MODEL-142 and MODEL-145, so
``decide`` stays unimplemented until those stages exist.
"""

from __future__ import annotations

from typing import Any

from decision.contract import Decision, Spec


def decide(spec: Spec, snapshot: Any) -> Decision:
    raise NotImplementedError("engine lands in MODEL-141/142/145")
