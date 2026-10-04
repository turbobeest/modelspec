"""The bounded representation (1.0): opt-in HTTP projections of a complete 2.x Decision.

It is not a 2.x minor version. It omits lists every 2.x Decision carries, so it
names itself with ``representation`` and ``bounded_version`` and points at the
complete contract it projects with ``projects_contract``.
"""

from __future__ import annotations

import json

from decision import contract

ESSENTIAL_ROW_FIELDS = frozenset({"rank", "model", "offering", "warnings"})
DEFAULT_FIELDS = ("model_rank", "cost_per_task", "estimates", "p_best")
# Leave space for the MCP origin envelope and its short text summary.
DRILL_DOWN_BYTES = 7_400


def project(decision: contract.Decision, options: contract.ResponseOptions, *,
            detail: contract.ModelEvidence | None = None,
            not_applied: list[str]) -> dict:
    data = decision.model_dump(mode="json")
    kept = ("decision_id", "snapshot", "signature_verified", "spec_hash", "explain", "status",
            "answer", "warnings", "truncated", "out_of_lineup", "relax", "relax_to", "feedback")
    # A distinct representation, not a 2.x minor version: see BOUNDED_VERSION.
    body = {"representation": "bounded", "bounded_version": contract.BOUNDED_VERSION,
            "projects_contract": data["contract_version"]}
    body.update({key: data[key] for key in kept})
    fields = ESSENTIAL_ROW_FIELDS | set(options.fields or DEFAULT_FIELDS)
    body["results"] = [] if detail else [
        {key: value for key, value in row.items() if key in fields} for row in data["results"]]
    body["may_qualify"] = [] if detail else data["may_qualify"][:10]
    for key in ("reading", "coverage", "with_estate"):
        if key in data:
            body[key] = data[key]
    omitted = {key: len(data[key]) for key in (
        "by_model", "blend", "top", "near_misses", "number_origins", "sources",
        "constraint_costs", "tipping_points",
    ) if data.get(key)}
    omitted["may_qualify"] = len(data["may_qualify"]) - len(body["may_qualify"])
    if detail:
        omitted["results"] = len(data["results"])
    omitted["eliminated.models"] = len(data["eliminated"]["models"])
    omitted["eliminated.model_groups"] = len(data["eliminated"]["model_groups"])
    omitted["eliminated.funnel"] = len(data["eliminated"]["funnel"])
    if data.get("bands"):
        omitted["bands"] = sum(len(data["bands"].get(key, [])) for key in ("best", "rest", "thin"))
    if data.get("benchmark_exclusions"):
        omitted["benchmark_exclusions.estimate_changes"] = len(data["benchmark_exclusions"]["estimate_changes"])
    body["explanation"] = contract.BoundedExplanation(
        not_applied=not_applied, omitted={key: value for key, value in omitted.items() if value},
    ).model_dump(mode="json")
    if detail:
        body["model_evidence"] = detail.model_dump(mode="json")
        _bound_detail(body)
    # Validate the new representation without weakening the legacy Decision/Result types.
    return contract.BoundedDecision.model_validate(body).model_dump(mode="json", exclude_unset=True)


def _bound_detail(body: dict) -> None:
    detail = body["model_evidence"]
    omitted = body["explanation"]["omitted"]
    # Drop complete records, never trim their provenance or turn values into nulls.
    lists = [("model_evidence.contributions", detail["contributions"])]
    lists += [("model_evidence.evidence.items", group["items"]) for group in detail["evidence"]]
    while len(json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")) > DRILL_DOWN_BYTES:
        available = [(name, rows) for name, rows in lists if rows]
        if not available:
            raise contract.SpecError([contract.Issue(
                None, "evidence_for", "the reporting essentials exceed the drill-down byte budget; "
                "use a narrower structured spec", "evidence_for")])
        name, rows = max(available, key=lambda entry: len(json.dumps(entry[1][-1])))
        rows.pop()
        omitted[name] = omitted.get(name, 0) + 1
