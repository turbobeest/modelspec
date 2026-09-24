"""Runs a spec against a snapshot. The stages land in MODEL-141, MODEL-142 and MODEL-145."""

from __future__ import annotations

from typing import Any

from decision.contract import Decision, Spec


def decide(spec: Spec, snapshot: Any) -> Decision:
    raise NotImplementedError("engine lands in MODEL-141/142/145")
