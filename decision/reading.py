"""Compact reporting limits from engine outputs, never scenario-specific advice."""

from __future__ import annotations

import json
from collections.abc import Iterable

from decision.contract import Decision, Issue, Reading

HARDWARE_FIT = "model.fits_hardware"
MAX_BYTES = 600


def _compact(reading: Reading) -> Reading:
    """Cap identifier lists, with explicit counts and pointers to the complete data."""
    def size():
        return len(reading.model_dump_json().encode("utf-8"))

    if size() <= MAX_BYTES:
        return reading
    reading.do_not_claim.append(
        "Do not treat omitted lists as complete; read answer.members and request/error.issues.")
    while size() > MAX_BYTES:
        lists = {"tied": reading.tied, "not_applied": reading.not_applied}
        name = max(lists, key=lambda key: sum(len(json.dumps(v)) for v in lists[key]))
        lists[name].pop()
        reading.omitted[name] = reading.omitted.get(name, 0) + 1
    return reading


def for_decision(decision: Decision, *, hardware_fit: bool, quality_objective: bool,
                 not_applied: Iterable[str] = (), hardware_estimates: bool = False) -> Reading | None:
    tied = (list(decision.answer.members)
            if decision.answer is not None and decision.answer.kind == "tied" else [])
    estimates = []
    if hardware_fit:
        estimates.append(HARDWARE_FIT)
    if hardware_estimates:
        from decision.hardware import HARDWARE_FACETS

        estimates.extend(HARDWARE_FACETS)
    if any(row.estimates for row in decision.results):
        estimates.append("results.estimates")
    if any(row.refinement_estimates for row in decision.results):
        estimates.append("results.refinement_estimates")
    claims = []
    unapplied = list(not_applied)
    if tied:
        claims.append("Do not name a single winner among tied.")
    if decision.with_estate is not None and decision.with_estate.answer is not None and (
        decision.with_estate.answer.kind == "tied"
    ):
        claims.append("Do not name a single winner among with_estate.answer.members; that answer is tied.")
    if unapplied:
        claims.append("Do not claim not_applied requirements were evaluated.")
    if estimates:
        claims.append("Do not present estimates as measurements.")
    if hardware_fit or hardware_estimates:
        claims.append("Do not claim fit for a specific quantization or context workload.")
    if hardware_estimates:
        claims.append("Quantisation is assumed; context fit and decode speed are unmeasured.")
    if decision.results and not quality_objective:
        claims.append("Do not claim a quality rank from this objective.")
    if not claims:
        return None
    return _compact(Reading(tied=tied, not_applied=unapplied, estimates=estimates,
                            do_not_claim=claims))


def for_refusal(issues: Iterable[Issue]) -> Reading | None:
    fields = list(dict.fromkeys(issue.field or issue.path for issue in issues
                                if issue.field or issue.path))
    if not fields:
        return None
    return _compact(Reading(
        not_applied=fields,
        do_not_claim=["Do not claim rejected requirements were checked, including after retry."],
    ))
