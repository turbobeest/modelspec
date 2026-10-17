"""Compare public component schemas after expanding generated Shared refs."""

import argparse
from pathlib import Path
import re

import yaml


SHARED_REF = re.compile(r"#/components/schemas/(Shared[0-9a-f]{12})$")
SHARED_NAME = re.compile(r"Shared[0-9a-f]{12}")


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


def public_schemas(spec):
    result = {}
    for name, schema in spec["components"]["schemas"].items():
        if SHARED_NAME.fullmatch(name):
            continue
        result[name] = expand(schema, spec)
        remove_annotations(result[name])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    args = parser.parse_args()
    before = public_schemas(yaml.safe_load(args.before.read_text()))
    after = public_schemas(yaml.safe_load(args.after.read_text()))
    assert before.keys() == after.keys()
    changed = [name for name in before if before[name] != after[name]]
    assert not changed, changed
    print(f"{len(after)} public component schemas retain identical validation rules, "
          "descriptions and non-null defaults after expanding shared refs.")
    print(f"Size changed from {len(args.before.read_bytes())} to {len(args.after.read_bytes())} bytes.")


if __name__ == "__main__":
    main()
