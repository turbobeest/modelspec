"""Provider-facing schemas; the captured MCP schemas remain the execution contract."""

from __future__ import annotations

import json

# Non-strict Claude/OpenAI tools accept JSON Schema constraints. Gemini's
# parametersJsonSchema uses JSON values, but we send a conservative subset of
# the documented Schema vocabulary to avoid backend-specific keyword handling.
JSON_KEYWORDS = {
    "type",
    "description",
    "properties",
    "required",
    "items",
    "enum",
    "anyOf",
    "oneOf",
    "allOf",
    "not",
    "additionalProperties",
    "patternProperties",
    "prefixItems",
    "minimum",
    "maximum",
    "exclusiveMinimum",
    "exclusiveMaximum",
    "multipleOf",
    "minLength",
    "maxLength",
    "pattern",
    "format",
    "minItems",
    "maxItems",
    "uniqueItems",
    "minProperties",
    "maxProperties",
}
GEMINI_KEYWORDS = {
    "type",
    "description",
    "properties",
    "required",
    "items",
    "enum",
    "anyOf",
    "minimum",
    "maximum",
    "minLength",
    "maxLength",
    "pattern",
    "format",
    "minItems",
    "maxItems",
    "minProperties",
    "maxProperties",
}


def provider_schema(schema: dict, family: str) -> dict:
    """Show each local definition once, retaining other uses as named instructions.

    Repeated and recursive references become typed values pointing to the first
    named definition in this tool. This presentation schema guides the agent;
    LiveTools validates the complete original schema, including nested rules.
    """
    allowed = GEMINI_KEYWORDS if family == "gemini" else JSON_KEYWORDS

    def describe(node, text):
        node["description"] = " ".join(filter(None, (node.get("description"), text)))

    def resolve(ref):
        if not ref.startswith("#/"):
            raise ValueError("Tool schemas require local JSON pointers")
        target = schema
        for token in ref[2:].split("/"):
            target = target[token.replace("~1", "/").replace("~0", "~")]
        return target

    seen_refs = set()

    def convert(node):
        if not isinstance(node, dict):
            return node  # Boolean schemas and scalar keyword values.
        while "$ref" in node:
            ref = node["$ref"]
            target = resolve(ref)
            name = ref.rsplit("/", 1)[-1]
            if ref in seen_refs:
                result = {"type": target["type"]} if "type" in target else {}
                describe(result, f"Use the {name} definition.")
                siblings = convert({k: v for k, v in node.items() if k != "$ref"})
                describe(result, siblings.pop("description", ""))
                result.update(siblings)
                return result
            seen_refs.add(ref)
            node = target | {k: v for k, v in node.items() if k != "$ref"}
            node = node | {"description": f"{name} definition. " + node.get("description", "")}
        result, notes = {}, []
        for key, value in node.items():
            if key in ("$schema", "$defs", "definitions", "title", "$id"):
                continue
            if key in ("properties", "patternProperties"):
                value = {name: convert(child) for name, child in value.items()}
            elif key in ("items", "additionalProperties", "not"):
                value = convert(value)
            elif key in ("anyOf", "oneOf", "allOf", "prefixItems"):
                value = [convert(child) for child in value]
            if key == "const":
                result["enum"] = [value]
                if "type" not in node:
                    result["type"] = (
                        "null"
                        if value is None
                        else "boolean"
                        if isinstance(value, bool)
                        else "integer"
                        if isinstance(value, int)
                        else "number"
                        if isinstance(value, float)
                        else "string"
                        if isinstance(value, str)
                        else "object"
                        if isinstance(value, dict)
                        else "array"
                    )
            elif key == "type" and isinstance(value, list):
                result["anyOf"] = [{"type": t} for t in value]
            elif family == "gemini" and key == "oneOf":
                result["anyOf"] = value
                notes.append("Exactly one of the anyOf alternatives must match.")
            elif key in allowed:
                result[key] = value
            else:
                notes.append(f"{key}: {json.dumps(value, separators=(',', ':'))}.")
        for note in notes:
            describe(result, note)
        return result

    result = convert(schema)
    if result.get("type") != "object" or any(k in result for k in ("anyOf", "oneOf", "allOf")):
        raise ValueError("Tool input schemas must have a single object root")
    return result
