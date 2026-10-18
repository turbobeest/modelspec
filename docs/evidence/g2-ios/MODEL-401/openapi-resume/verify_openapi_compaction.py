"""Prove MODEL-401 schema compaction preserves the intended public contract.

Adapted from MODEL-287/verify_openapi_compaction.py. Expand only the generator's
Shared refs. The first comparison checks the complete previously generated 2.0
document, including every annotation. The second follows MODEL-287's annotation
normalization and permits only MODEL-401's four new and four changed HardwareFit
schemas against origin/main. Every route and all other OpenAPI content must match.
"""

import argparse
import copy
from pathlib import Path
import re
import subprocess

import yaml


SHARED_REF = re.compile(r"#/components/schemas/(Shared[0-9a-f]{12})$")
SHARED_NAME = re.compile(r"Shared[0-9a-f]{12}")
NEW_SCHEMAS = {
    "HardwareFitFullEstimatedResponse",
    "HardwareFitHeadroomNotRequired",
    "HardwareFitLowerBoundDeviceEstimate",
    "HardwareFitLowerBoundEstimatedResponse",
}
CHANGED_SCHEMAS = {
    "HardwareFitEstimatedResponse",
    "HardwareFitMeasuredResponse",
    "HardwareFitRefused",
    "HardwareFitUndeterminedResponse",
}


def expand(value, spec):
    if isinstance(value, dict):
        target = SHARED_REF.fullmatch(value.get("$ref", ""))
        if target:
            assert set(value) == {"$ref"}
            return expand(spec["components"]["schemas"][target.group(1)], spec)
        return {key: expand(child, spec) for key, child in value.items()}
    if isinstance(value, list):
        return [expand(child, spec) for child in value]
    return value


def remove_annotations(schema):
    if not isinstance(schema, dict):
        return
    schema.pop("title", None)
    if schema.get("default") is None:
        schema.pop("default", None)
    for keyword in ("properties", "patternProperties", "$defs", "definitions", "dependentSchemas"):
        for child in (schema.get(keyword) or {}).values():
            remove_annotations(child)
    for keyword in ("items", "additionalProperties", "unevaluatedProperties", "unevaluatedItems",
                    "contains", "not", "if", "then", "else", "propertyNames", "additionalItems"):
        remove_annotations(schema.get(keyword))
    for keyword in ("anyOf", "oneOf", "allOf", "prefixItems"):
        for child in schema.get(keyword) or []:
            remove_annotations(child)


def expanded_document(spec):
    result = expand(spec, spec)
    result["components"]["schemas"] = {
        name: schema for name, schema in result["components"]["schemas"].items()
        if not SHARED_NAME.fullmatch(name)
    }
    return result


def normalized(spec):
    result = expanded_document(spec)
    for schema in result["components"]["schemas"].values():
        remove_annotations(schema)
    for operations in result["paths"].values():
        for operation in operations.values():
            for response in operation.get("responses", {}).values():
                for content in response.get("content", {}).values():
                    remove_annotations(content.get("schema"))
    return result


def git_file(ref):
    return subprocess.run(
        ["git", "show", f"{ref}:api/worker/openapi.yaml"],
        check=True, capture_output=True, text=True,
    ).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", default="origin/main")
    parser.add_argument("--previous-v2-ref", default="fb498b21ae503fc103b7a53b6f21fe2af55679d5")
    parser.add_argument("--after", type=Path, default=Path("api/worker/openapi.yaml"))
    args = parser.parse_args()
    base_text = git_file(args.base_ref)
    uncompacted_text = git_file(args.previous_v2_ref)
    after_text = args.after.read_text()
    base = normalized(yaml.safe_load(base_text))
    uncompacted = expanded_document(yaml.safe_load(uncompacted_text))
    expanded_after = expanded_document(yaml.safe_load(after_text))

    assert uncompacted == expanded_after, "Compaction changed the previously generated hardware-fit 2.0 document."
    print(f"All {len(expanded_after['components']['schemas'])} public component schemas and "
          f"{len(expanded_after['paths'])} paths equal the previously generated 2.0 document, "
          "including titles, descriptions, null and non-null defaults, and validation rules.")

    after = normalized(yaml.safe_load(after_text))
    before_schemas = base["components"]["schemas"]
    after_schemas = after["components"]["schemas"]
    assert after_schemas.keys() - before_schemas.keys() == NEW_SCHEMAS
    assert not before_schemas.keys() - after_schemas.keys()
    changed = {name for name in before_schemas if before_schemas[name] != after_schemas[name]}
    assert changed == CHANGED_SCHEMAS, changed
    unchanged = copy.deepcopy(after)
    for name in NEW_SCHEMAS:
        unchanged["components"]["schemas"].pop(name)
    for name in CHANGED_SCHEMAS:
        unchanged["components"]["schemas"][name] = before_schemas[name]
    assert base == unchanged, "OpenAPI content outside the eight intended HardwareFit schemas changed."
    base_sha = subprocess.run(["git", "rev-parse", args.base_ref],
                              check=True, capture_output=True, text=True).stdout.strip()
    print(f"Against {args.base_ref} ({base_sha}), only the four new and four changed HardwareFit schemas differ; "
          f"all {len(base['paths'])} paths and all other OpenAPI content are identical.")
    print(f"Size: origin/main {len(base_text.encode())}; previous 2.0 "
          f"{len(uncompacted_text.encode())}; compacted 2.0 {len(after_text.encode())} bytes.")


if __name__ == "__main__":
    main()
