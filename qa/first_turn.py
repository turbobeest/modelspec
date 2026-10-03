"""Offline accounting of the exact first wire request. No API keys or HTTP calls."""
from __future__ import annotations

import json

import httpx

from pipeline.agent_overhead import METHOD, tokens
from qa.providers import first_request


def breakdown(family: str, settings: dict, parts: dict[str, str], request: str,
              tools: list[dict], max_output: int) -> dict:
    payload = first_request(family, settings["model"], "".join(parts.values()), request, tools, max_output)
    # HTTPX's JSON encoder is the one used by HttpAgent.step, including UTF-8 and escaping.
    wire = httpx.Request("POST", "https://offline.invalid", json=payload).content
    native = payload.get("tools", [])
    if family == "gemini":
        native = native[0]["functionDeclarations"] if native else []
    schema_key = {"claude": "input_schema", "openai": "parameters", "gemini": "parametersJsonSchema"}[family]

    def count(value):
        return tokens(json.dumps(value, ensure_ascii=False, separators=(",", ":")))

    components = {name: count(value) if value else 0 for name, value in parts.items()}
    components.update(user_request=count(request),
                      tool_descriptions=count([t["description"] for t in native]),
                      tool_schemas=count([t[schema_key] for t in native]))
    total = tokens(wire.decode())
    # This remainder includes tool names, provider framing, and token boundary effects.
    components["protocol"] = total - sum(components.values())
    return {"method": METHOD, "components": components, "total": total, "wire_bytes": len(wire)}


def first_turn_breakdowns(config: dict, parts: dict[str, str], requests: list[str],
                          tools: list[dict], families: list[str]) -> dict:
    """Report the largest first request per family; never include prompt contents."""
    return {family: max((breakdown(family, config["agents"][family], parts, request, tools,
                                  config["max_output_tokens"]) for request in requests),
                         key=lambda row: row["total"]) for family in families}
