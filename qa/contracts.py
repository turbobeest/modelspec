"""Capture public MCP definitions and schemas without importing the decision engine."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TOOL_NAMES = ("rank", "model_info", "list_use_cases", "policy_check", "decide", "vocab", "feedback")
SOURCE_PATHS = (
    "mcp/src/server.ts",
    "mcp/src/vocabulary.ts",
    "docs/decision-contract.schema.json",
    "api/worker/openapi.yaml",
)


def source_hashes() -> dict[str, str]:
    paths = list(SOURCE_PATHS)
    if (ROOT / "mcp/src/agent-copy.json").exists():
        paths.append("mcp/src/agent-copy.json")
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}


def _prose(expression: str, constants: dict[str, str]) -> str:
    tokens = re.findall(
        r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|\b(?:NULL_RULE|SPEC_GUIDANCE)\b', expression
    )
    return "".join(constants[t] if t in constants else ast.literal_eval(t) for t in tokens)


def _reachable_schema(document: dict, name: str) -> dict:
    definitions = document["$defs"]
    selected = {}
    pending = [name]
    while pending:
        key = pending.pop()
        if key in selected:
            continue
        selected[key] = definitions[key]
        pending.extend(re.findall(r'#/\$defs/([^" ]+)', json.dumps(definitions[key])))
    return {"$schema": document["$schema"], "$defs": selected, "$ref": f"#/$defs/{name}"}


def capture_tools() -> dict:
    """Mirror the seven registered inputs; pin the source hashes to detect drift."""
    source = (ROOT / "mcp/src/server.ts").read_text()
    constants = {}
    for name in ("NULL_RULE", "SPEC_GUIDANCE"):
        match = re.search(rf"const {name}\s*=\s*(.*?);\s*\n", source, re.S)
        if match:
            constants[name] = _prose(match.group(1), constants)
    copy_path = ROOT / "mcp/src/agent-copy.json"
    agent_copy = json.loads(copy_path.read_text()) if copy_path.exists() else None
    api = yaml.safe_load((ROOT / "api/worker/openapi.yaml").read_text())
    schemas = api["components"]["schemas"]

    def schema(name: str, nullable: bool) -> dict:
        value = copy.deepcopy(schemas[name])

        def convert(node):
            if isinstance(node, dict):
                is_nullable = node.pop("nullable", False)
                if nullable and is_nullable and "type" in node:
                    node["type"] = [node["type"], "null"]
                # Zod's MCP inputs advertise structural validation only. Semantic
                # bounds, required policy blocks and prose belong to OpenAPI.
                for key in ("description", "default", "required", "minLength", "minItems"):
                    node.pop(key, None)
                for child in node.values():
                    convert(child)
            elif isinstance(node, list):
                for child in node:
                    convert(child)

        convert(value)
        value["additionalProperties"] = True
        for key in ("environment", "constraints", "policy"):
            if key in value.get("properties", {}):
                # Unknown nested Zod object fields are stripped, not refused.
                value["properties"][key].pop("additionalProperties", None)
        return value

    rank = schema("RankRequest", nullable=True)
    rank["required"] = ["use_case"]
    rank["properties"]["use_case"] = {
        "type": "string",
        "description": "Ranking profile id, as published in /api/rank/profiles.json",
    }
    for key in ("hardware", "runtime"):
        rank["properties"]["environment"]["properties"][key] = {"type": ["string", "null"]}
    # Neither of these numbers is bounded by the registered MCP Zod input.
    for key in ("price_sensitivity", "max_cost_per_million_input_tokens"):
        rank["properties"]["constraints"]["properties"][key] = {"type": ["number", "null"]}
    policy = schema("PolicyCheckRequest", nullable=False)
    policy["required"] = ["policy"]
    policy["properties"]["policy"]["additionalProperties"] = True
    commercial = policy["properties"]["policy"]["properties"]["commercial_use"]
    commercial["properties"]["required"] = {"type": "boolean"}
    for block in policy["properties"]["policy"]["properties"].values():
        block.pop("additionalProperties", None)
    feedback = copy.deepcopy(schemas["FeedbackRequest"])
    feedback["properties"] = {
        k: v
        for k, v in feedback["properties"].items()
        if k in ("rating", "decision_id", "note", "trying_to_decide", "template")
    }
    feedback["required"] = ["rating"]
    for prop in feedback["properties"].values():
        prop.pop("nullable", None)
    inputs = {
        "rank": rank,
        "policy_check": policy,
        "decide": _reachable_schema(
            json.loads((ROOT / "docs/decision-contract.schema.json").read_text()), "Spec"
        ),
        "feedback": feedback,
        "model_info": {
            "type": "object",
            "properties": {
                "model_id": {"type": "string", "description": "Catalogue id, e.g. openai/gpt-5-6"}
            },
            "required": ["model_id"],
        },
        "list_use_cases": {"type": "object", "properties": {}},
        "vocab": {
            "type": "object",
            "properties": {
                "section": {
                    "type": "string",
                    "enum": [
                        "starter",
                        "facets",
                        "benchmarks",
                        "domains",
                        "providers",
                        "models",
                        "task_types",
                        "coverage",
                        "templates",
                        "refinements",
                        "estate",
                        "vendors",
                        "template_categories",
                        "template_tiers",
                    ],
                    "description": "Return only this vocabulary section; defaults to starter",
                },
                "search": {"type": "string", "description": "Case-insensitive substring over id and label or display name"},
                "id": {"type": "string", "description": "Return full details for this exact id"},
                "ids": {"type": "array", "items": {"type": "string"}, "description": "Return full details for these exact ids"},
                "detail": {"type": "string", "enum": ["compact", "full"], "description": "Full returns all display details; defaults to compact"},
                "offset": {"type": "integer", "minimum": 0, "description": "Skip this many matching rows; defaults to 0"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 20, "description": "Compact page size; defaults to 20"},
            },
        },
    }
    tools = []
    for name in TOOL_NAMES:
        match = re.search(
            rf'server\.registerTool\(\s*"{name}"\s*,\s*\{{\s*description:\s*'
            r"(.*?),\s*inputSchema:",
            source,
            re.S,
        )
        if match is None:
            raise ValueError(f"Cannot capture MCP description for {name}")
        expression = match.group(1).strip()
        if re.fullmatch(rf"agentCopy\s*\.\s*tools\s*\.\s*{name}", expression):
            if agent_copy is None:
                raise ValueError("MCP descriptions require mcp/src/agent-copy.json")
            description = agent_copy["tools"][name]
        else:
            description = _prose(expression, constants)
        tools.append(
            {
                "name": name,
                "description": description,
                "input_schema": inputs[name],
            }
        )
    return {"source_hashes": source_hashes(), "tools": tools}


if __name__ == "__main__":
    (ROOT / "qa/fixtures/mcp-tools.json").write_text(
        json.dumps(capture_tools(), indent=2, ensure_ascii=False) + "\n"
    )
