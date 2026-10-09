"""The bounded representation (1.1): opt-in HTTP projections of a complete 2.x Decision.

It is not a 2.x minor version. It omits lists every 2.x Decision carries, so it
names itself with ``representation`` and ``bounded_version`` and points at the
complete contract it projects with ``projects_contract``.
"""

from __future__ import annotations

import json
from collections.abc import Mapping

from decision import contract
from decision.summary import record_counts_from_capture, summarize

ESSENTIAL_ROW_FIELDS = frozenset({"rank", "model", "offering", "warnings"})
DEFAULT_FIELDS = ("model_rank", "cost_per_task", "estimates", "p_best")
# Row fields the engine fills at explain summary and full (decision/explain.py).
EXPLAIN_ROW_FIELDS = ("contributions", "evidence")
# Whole row fields the agent budget may remove. Items inside one of these stay
# intact: provenance is never cut off, and a value is never replaced with null.
HEAVY_ROW_FIELDS = ("evidence", "contributions", "estimates", "refinement_estimates", "plans")
# Evidence and contributions on a later row of a model that already has an
# earlier row. The first row of each model keeps both until the later step.
# Estimates and plans stay until that later heavy-field step.
_MEMBER_ROW_HEAVY = ("evidence", "contributions")
# Items kept per answer member before the byte budget trims further (MODEL-354).
MEMBER_EVIDENCE_ITEMS = 3
# Leave space for the MCP origin envelope and its short text summary.
DRILL_DOWN_BYTES = 7_400

# Compact UTF-8 agent budget (MODEL-334). The MCP text is
# JSON.stringify({origin, status, body}) plus decisionSummary. The body is
# capped so those two together stay within AGENT_BYTES even at the longest
# summary the MCP emits for a 61-byte model id (the longest catalogue id).
AGENT_BYTES = 16_384
MCP_ORIGIN = "https://api.modelspec.dev/v1/decide"
_ENVELOPE_PREFIX = '{"origin":"' + MCP_ORIGIN + '","status":200,"body":'
_ENVELOPE_SUFFIX = "}"
MCP_ENVELOPE_BYTES = len(_ENVELOPE_PREFIX.encode("utf-8")) + len(_ENVELOPE_SUFFIX.encode("utf-8"))
_SUMMARY_MODEL_ID = "m" * 61
_SUMMARY_SHOWN = ", ".join([_SUMMARY_MODEL_ID] * 5)
# decisionSummary's longest line: a tied drill-down, five ids, a six-digit remainder.
_SUMMARY_TEXT = (
    f"status: no_feasible; answer: tied among {_SUMMARY_SHOWN} and 999999 more in answer.members; "
    f"evidence for: {_SUMMARY_MODEL_ID} (eliminated, unranked)"
)
SUMMARY_RESERVE_BYTES = len(_SUMMARY_TEXT.encode("utf-8"))
RESPONSE_BYTES = AGENT_BYTES - MCP_ENVELOPE_BYTES - SUMMARY_RESERVE_BYTES


def row_fields_for(explain: str) -> list[str]:
    """Fields the MCP and CLI request when the caller does not pass ``fields``."""
    fields = list(DEFAULT_FIELDS)
    if explain in ("summary", "full"):
        fields.extend(EXPLAIN_ROW_FIELDS)
    return fields


def mcp_default_request(spec: dict) -> dict:
    """The request ``defaultDecideRequest`` builds. ``fields`` already on ``spec`` wins."""
    if "fields" in spec:
        fields = spec["fields"]
    elif spec.get("explain") in ("summary", "full"):
        fields = row_fields_for(str(spec.get("explain")))
    else:
        fields = list(DEFAULT_FIELDS)
    return {"explain": "none", "limit": 10, "fields": list(DEFAULT_FIELDS), **spec, "fields": fields}


def compact_bytes(body: dict) -> int:
    return _nbytes(body)


def agent_summary(body: dict) -> str:
    """Python mirror of ``decisionSummary`` in ``mcp/src/server.ts``."""
    status = body.get("status") if isinstance(body.get("status"), str) else "unknown"
    detail = body.get("model_evidence")
    if isinstance(detail, dict):
        model = detail.get("model") if isinstance(detail.get("model"), str) else "unknown"
        model_status = detail.get("status") if isinstance(detail.get("status"), str) else "unknown"
        rank = detail.get("rank")
        rank_text = f"rank {rank}" if isinstance(rank, int | float) and not isinstance(rank, bool) else "unranked"
        return (
            f"status: {status}; {_answer_summary(body.get('answer'))}; "
            f"evidence for: {model} ({model_status}, {rank_text})"
        )
    results = body.get("results") if isinstance(body.get("results"), list) else []
    models: list[str] = []
    for row in results:
        if not isinstance(row, dict):
            continue
        offering = row.get("offering")
        if isinstance(offering, dict) and isinstance(offering.get("model"), str):
            model = offering["model"]
            if model not in models:
                models.append(model)
        if len(models) == 5:
            break
    may_qualify = body.get("may_qualify")
    count = len(may_qualify) if isinstance(may_qualify, list) else 0
    shown = ", ".join(models) if models else "none"
    return f"status: {status}; top models: {shown}; may qualify: {count}"


def mcp_text_bytes(body: dict, *, status: int = 200) -> int:
    """Bytes of the MCP text: the origin envelope, plus ``decisionSummary`` on success."""
    packed = json.dumps(
        {"origin": MCP_ORIGIN, "status": status, "body": body},
        ensure_ascii=False, separators=(",", ":"),
    ).encode("utf-8")
    if status == 0 or status >= 400:
        return len(packed)
    return len(packed) + len(agent_summary(body).encode("utf-8"))


def _answer_summary(answer: object) -> str:
    if not isinstance(answer, dict) or not isinstance(answer.get("members"), list):
        return "answer: none"
    members = [model for model in answer["members"] if isinstance(model, str)]
    shown = ", ".join(members[:5])
    more = f" and {len(members) - 5} more in answer.members" if len(members) > 5 else ""
    if answer.get("kind") == "tied":
        return f"answer: tied among {shown}{more}"
    return f"answer: {shown or 'none'}"


def project(decision: contract.Decision, options: contract.ResponseOptions, *,
            detail: contract.ModelEvidence | None = None,
            not_applied: list[str],
            spec: contract.Spec | None = None,
            profiles: Mapping[str, contract.InventoryProfile] | None = None,
            feasible: int | None = None,
            member_evidence: list | None = None) -> dict:
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
    for key in ("reading", "coverage", "with_estate", "relax_task_tokens"):
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
    note = contract.BoundedExplanation.model_fields["note"].default
    body["explanation"] = {"not_applied": not_applied,
                           "omitted": {key: value for key, value in omitted.items() if value},
                           "note": note}
    if detail:
        body["model_evidence"] = detail.model_dump(mode="json")
    # Computed from the full Decision, before either budget drops records.
    # Record counts come from the same capture as member_evidence, before the
    # cap of three, so a member limit dropped from results is still counted.
    summary, mentions = summarize(
        decision, spec, not_applied=not_applied, profiles=profiles, feasible=feasible,
        record_counts=None if member_evidence is None else record_counts_from_capture(member_evidence),
    )
    body["summary_for_user"] = summary
    body["must_mention"] = mentions
    # After the summary, which is computed from the full Decision. Drill-down
    # cites one model through model_evidence and does not carry this list.
    # explain none carries the counts into the caveat and not the item list.
    if detail is None and member_evidence and decision.explain in ("summary", "full"):
        body["member_evidence"] = _bounded_member_evidence(body, member_evidence)
    if detail:
        _bound_detail(body)
    else:
        _fit_agent_budget(body)
    # Validate the new representation without weakening the legacy Decision/Result types.
    return contract.BoundedDecision.model_validate(body).model_dump(mode="json", exclude_unset=True)


def _nbytes(body: dict) -> int:
    return len(json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def _omit(body: dict, key: str) -> None:
    omitted = body["explanation"]["omitted"]
    omitted[key] = omitted.get(key, 0) + 1


def _top_model(body: dict) -> str | None:
    detail = body.get("model_evidence")
    if isinstance(detail, dict) and isinstance(detail.get("model"), str):
        return detail["model"]
    results = body.get("results") or []
    if results:
        model = _model_of(results[0])
        if model:
            return model
    members = (body.get("answer") or {}).get("members") or []
    if members and isinstance(members[0], str):
        return members[0]
    return None


def _model_of(row: dict) -> str | None:
    model = row.get("model")
    if isinstance(model, str):
        return model
    offering = row.get("offering")
    if isinstance(offering, dict) and isinstance(offering.get("model"), str):
        return offering["model"]
    return None


def _fetch_text(body: dict) -> str:
    model = _top_model(body)
    drill = f"evidence_for: {model}" if model else "evidence_for: <model>"
    return (
        "explanation.omitted counts records removed from this bounded answer. "
        f"Resend this spec with {drill} for one model's evidence; "
        "narrow fields or lower limit; "
        "or POST /v1/decide without fields for the complete Decision."
    )


def _note_fetch(body: dict) -> None:
    explanation = body["explanation"]
    if explanation["omitted"]:
        explanation["fetch"] = _fetch_text(body)
    else:
        explanation.pop("fetch", None)


def _answer_models(body: dict) -> set[str]:
    members = (body.get("answer") or {}).get("members") or []
    return {model for model in members if isinstance(model, str)}


def _heavy_field(row: dict, names: tuple[str, ...] = HEAVY_ROW_FIELDS) -> str | None:
    """The largest whole heavy field on this row, if removing it saves bytes."""
    chosen = None
    size = 2  # an empty JSON list is two bytes; smaller than that is not worth a drop
    for name in names:
        if name not in row:
            continue
        field_size = len(json.dumps(row[name], ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
        if field_size > size:
            chosen, size = name, field_size
    return chosen


def _over(body: dict) -> bool:
    """True when the body, including the fetch pointer it owes, exceeds the budget."""
    _note_fetch(body)
    return _nbytes(body) > RESPONSE_BYTES


def _drop_heavy(body: dict, row: dict, prefix: str,
                names: tuple[str, ...] = HEAVY_ROW_FIELDS) -> bool:
    name = _heavy_field(row, names)
    if name is None:
        return False
    value = row.pop(name)
    removed = len(value) if isinstance(value, list) else 1
    key = f"{prefix}.{name}"
    omitted = body["explanation"]["omitted"]
    omitted[key] = omitted.get(key, 0) + removed
    return True


def _evidence_item_key(item: dict) -> tuple:
    """Same order as ``objective_evidence_items``: weight, then direct, then id."""
    weight = item.get("estimate_weight") if isinstance(item, dict) else None
    if isinstance(weight, bool) or not isinstance(weight, (int, float)):
        weight = float("-inf")
    direct = item.get("directness") if isinstance(item, dict) else None
    record_id = item.get("record_id") if isinstance(item, dict) else None
    return (-float(weight), 0 if direct == "direct" else 1, record_id or "")


def _dump_evidence_item(item) -> dict:
    if isinstance(item, dict):
        return contract.EvidenceItem.model_validate(item).model_dump(mode="json")
    return item.model_dump(mode="json")


def _bounded_member_evidence(body: dict, captured: list) -> list[dict]:
    """One entry per answer member (the budget may later remove entries from the end). Cap items, then group by domain.

    Items are already the contribution records for that member's best row.
    Sort again so the cap keeps the highest weight, direct before proxy.
    An item with no ``requested_domain`` has no domain group to sit in. It is
    always counted in ``omitted_items`` and is never shown, even when the
    member is under the item cap.
    """
    entries = []
    omitted_total = 0
    for entry in captured:
        model_id, items = entry[0], entry[1]
        dumped = [_dump_evidence_item(item) for item in items]
        dumped.sort(key=_evidence_item_key)
        usable = []
        missing_domain = 0
        for item in dumped:
            domain = item.get("requested_domain")
            if not isinstance(domain, str) or not domain:
                missing_domain += 1
                continue
            usable.append(item)
        kept = usable[:MEMBER_EVIDENCE_ITEMS]
        omitted_items = missing_domain + (len(usable) - len(kept))
        groups: list[dict] = []
        by_domain: dict[str, dict] = {}
        for item in kept:
            domain = item["requested_domain"]
            group = by_domain.get(domain)
            if group is None:
                group = {"domain": domain, "items": []}
                by_domain[domain] = group
                groups.append(group)
            group["items"].append(item)
        entries.append({"model": model_id, "evidence": groups, "omitted_items": omitted_items})
        omitted_total += omitted_items
    if omitted_total:
        omitted = body["explanation"]["omitted"]
        omitted["member_evidence.items"] = omitted.get("member_evidence.items", 0) + omitted_total
    return entries


def _member_evidence_models(body: dict) -> set[str]:
    entries = body.get("member_evidence")
    if not isinstance(entries, list):
        return set()
    return {
        entry["model"]
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("model"), str)
    }


def _repeat_offering(results: list[dict], index: int) -> bool:
    """True when this row's model already appears in an earlier row.

    Row 0 is never a repeat. A row with no model id is never a repeat.
    """
    if index <= 0:
        return False
    model = _model_of(results[index])
    if model is None:
        return False
    return any(_model_of(earlier) == model for earlier in results[:index])


def _drop_member_row_evidence(body: dict, results: list[dict], models: set[str]) -> bool:
    """Drop evidence or contributions from the last repeat offering of a member.

    A repeat offering is a row whose model already appears in an earlier row.
    The first row of each model, and row 0, keep those fields for the later step.
    """
    if not models:
        return False
    for index in range(len(results) - 1, 0, -1):
        row = results[index]
        if _model_of(row) not in models or not _repeat_offering(results, index):
            continue
        if _drop_heavy(body, row, "results", _MEMBER_ROW_HEAVY):
            return True
    return False


def _member_item_count(entry: dict) -> int:
    total = 0
    for group in entry.get("evidence") or []:
        items = group.get("items") if isinstance(group, dict) else None
        if isinstance(items, list):
            total += len(items)
    return total


def _trim_member_item(body: dict, *, floor: int) -> bool:
    """Remove the worst item from the member who has the most, later member on a tie.

    Never removes the entry. ``floor`` is the count that member must keep.
    """
    entries = body.get("member_evidence")
    if not isinstance(entries, list):
        return False
    chosen = None
    chosen_count = floor
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        count = _member_item_count(entry)
        if count > floor and (chosen is None or count >= chosen_count):
            chosen = index
            chosen_count = count
    if chosen is None:
        return False
    entry = entries[chosen]
    worst = None
    worst_key = None
    for group_index, group in enumerate(entry.get("evidence") or []):
        if not isinstance(group, dict) or not isinstance(group.get("items"), list):
            continue
        for item_index, item in enumerate(group["items"]):
            key = _evidence_item_key(item if isinstance(item, dict) else {})
            if worst_key is None or key > worst_key:
                worst_key = key
                worst = (group_index, item_index)
    if worst is None:
        return False
    group_index, item_index = worst
    group = entry["evidence"][group_index]
    group["items"].pop(item_index)
    if not group["items"]:
        entry["evidence"].pop(group_index)
    entry["omitted_items"] = int(entry.get("omitted_items") or 0) + 1
    omitted = body["explanation"]["omitted"]
    omitted["member_evidence.items"] = omitted.get("member_evidence.items", 0) + 1
    return True


def _drop_member_entry(body: dict) -> bool:
    """Remove the last ``member_evidence`` entry and count it.

    Items still on that entry are counted under ``member_evidence.items``.
    ``answer.members`` is left unchanged. An empty list stays, so the field
    remains present when every entry was removed to fit.
    """
    entries = body.get("member_evidence")
    if not isinstance(entries, list) or not entries:
        return False
    entry = entries.pop()
    omitted = body["explanation"]["omitted"]
    omitted["member_evidence"] = omitted.get("member_evidence", 0) + 1
    if isinstance(entry, dict):
        items = _member_item_count(entry)
        if items:
            omitted["member_evidence.items"] = omitted.get("member_evidence.items", 0) + items
    return True


def _fit_agent_budget(body: dict) -> None:
    """Drop whole records until the compact body, including ``fetch``, fits.

    Order: result rows that are neither the top result nor an answer member,
    then ``evidence`` and ``contributions`` on a repeat offering (a row whose
    model already appears in an earlier row), then ``may_qualify``, then
    ``member_evidence`` items from the member with the most items down to one
    item per member, then any remaining result row except the top, then
    ``with_estate``, then ``reading`` and ``relax_task_tokens``, then one
    heavy field of the top result, then its other non-essential fields, then
    any remaining ``member_evidence`` items, then ``member_evidence`` entries
    from the end of the list. The first row of each model, and row 0, keep
    their explanation until that later heavy-field step. The top result's
    explanation is removed only after the earlier records are gone. Fields
    inside one evidence item are never trimmed. ``answer``, ``status``,
    ``warnings``, ``coverage``, ``summary_for_user``, ``must_mention`` and
    the top result's rank, model, offering and warnings stay. A heavy field
    is removed whole. Does not return a body that is still over budget: the
    essentials then raise ``SpecError``.
    """
    if not _over(body):
        return
    results: list[dict] = body["results"]
    answer_models = _answer_models(body)
    member_models = _member_evidence_models(body)

    def protected(index: int, row: dict) -> bool:
        return index == 0 or _model_of(row) in answer_models

    while _over(body):
        index = next((i for i in range(len(results) - 1, -1, -1) if not protected(i, results[i])), None)
        if index is None:
            break
        results.pop(index)
        _omit(body, "results")

    while _over(body) and _drop_member_row_evidence(body, results, member_models):
        pass

    may_qualify: list = body["may_qualify"]
    while _over(body) and may_qualify:
        may_qualify.pop()
        _omit(body, "may_qualify")

    while _over(body) and _trim_member_item(body, floor=1):
        pass

    while _over(body) and len(results) > 1:
        results.pop()
        _omit(body, "results")

    estate = body.get("with_estate")
    if isinstance(estate, dict):
        estate_results = estate.get("results")
        if isinstance(estate_results, list):
            while _over(body) and estate_results:
                estate_results.pop()
                _omit(body, "with_estate.results")
        for key in ("may_qualify", "gain"):
            rows = estate.get(key)
            if not isinstance(rows, list):
                continue
            while _over(body) and rows:
                rows.pop()
                _omit(body, f"with_estate.{key}")
        if _over(body):
            body.pop("with_estate", None)
            _omit(body, "with_estate")

    for key in ("reading", "relax_task_tokens"):
        if not _over(body):
            break
        if body.get(key) is None:
            continue
        body.pop(key)
        _omit(body, key)

    while _over(body) and results and _drop_heavy(body, results[0], "results"):
        pass

    if results:
        for name in [key for key in results[0] if key not in ESSENTIAL_ROW_FIELDS]:
            if not _over(body):
                break
            value = results[0].pop(name)
            removed = len(value) if isinstance(value, list) else 1
            key = f"results.{name}"
            omitted = body["explanation"]["omitted"]
            omitted[key] = omitted.get(key, 0) + removed

    while _over(body) and _trim_member_item(body, floor=0):
        pass

    while _over(body) and _drop_member_entry(body):
        pass

    if _over(body):
        raise contract.SpecError([contract.Issue(
            None, "fields",
            "the answer, status, warnings, coverage and top result exceed the 16 KB agent budget; "
            "narrow fields or lower limit, resend with evidence_for for one model, "
            "or POST /v1/decide without fields for the complete Decision",
            "fields")])


def _bound_detail(body: dict) -> None:
    detail = body["model_evidence"]
    omitted = body["explanation"]["omitted"]
    # Drop complete records, never trim their provenance or turn values into nulls.
    lists = [("model_evidence.contributions", detail["contributions"])]
    lists += [("model_evidence.evidence.items", group["items"]) for group in detail["evidence"]]
    while True:
        _note_fetch(body)
        if _nbytes(body) <= DRILL_DOWN_BYTES:
            return
        available = [(name, rows) for name, rows in lists if rows]
        if not available:
            raise contract.SpecError([contract.Issue(
                None, "evidence_for", "the reporting essentials exceed the drill-down byte budget; "
                "use a narrower structured spec", "evidence_for")])
        name, rows = max(available, key=lambda entry: len(json.dumps(entry[1][-1])))
        rows.pop()
        omitted[name] = omitted.get(name, 0) + 1
