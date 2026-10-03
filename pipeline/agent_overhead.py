"""Reproducible prompt-size accounting: python -m pipeline.agent_overhead [--baseline REV]."""
from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
try:
    import tiktoken
except ImportError:
    ENCODER = None
else:
    ENCODER = tiktoken.get_encoding("cl100k_base")
METHOD = "cl100k_base" if ENCODER else "ceil(characters / 4)"


def tokens(text: str) -> int:
    return len(ENCODER.encode(text)) if ENCODER else math.ceil(len(text) / 4)


def measure(openapi: str, tools: list[dict]) -> dict:
    spec = yaml.safe_load(openapi)
    dump = lambda value: yaml.safe_dump(value, sort_keys=False, allow_unicode=True)
    return {
        "method": METHOD,
        "openapi_bytes": len(openapi.encode()),
        "openapi_tokens": tokens(openapi),
        "paths": {name: tokens(dump(value)) for name, value in spec["paths"].items()},
        "components": {name: tokens(dump(value)) for name, value in spec["components"]["schemas"].items()},
        "tools": {t["name"]: {"definition": tokens(json.dumps(t, ensure_ascii=False)),
                              "description": tokens(t["description"])} for t in tools},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", nargs="?", const="origin/main", help="Read artifacts at this git revision, default origin/main")
    parser.add_argument("--mcp-tools", type=Path, help="Actual tools/list JSON captured by the MCP overhead test")
    args = parser.parse_args()

    def read(path):
        if args.baseline:
            return subprocess.check_output(["git", "show", f"{args.baseline}:{path}"], cwd=ROOT).decode()
        return (ROOT / path).read_text()

    # qa.contracts mirrors tools/list. The starting server advertised the entire
    # contract in decide.$defs, while its fixture captured only reachable defs.
    tools = (json.loads(args.mcp_tools.read_text()) if args.mcp_tools else
             json.loads(read("qa/fixtures/mcp-tools.json"))["tools"])
    if args.baseline and not args.mcp_tools:
        contract = json.loads(read("docs/decision-contract.schema.json"))
        next(t for t in tools if t["name"] == "decide")["input_schema"]["$defs"] = contract["$defs"]
    print(json.dumps(measure(read("api/worker/openapi.yaml"), tools), indent=2))


def comparison_markdown(before: dict, after: dict) -> str:
    """PR tables from measured artifacts; sections count standalone YAML, not slices."""
    lines = [
        f"Token method: {after['method']}. OpenAPI totals count the complete file. "
        "Path and schema rows count each value serialized as standalone YAML, so they "
        "do not sum to the total. MCP rows count actual SDK tools/list definitions "
        "serialized as JSON, including their schemas. No live agent or paid call is involved.",
        "", "| Artifact | Before | After |", "| --- | ---: | ---: |",
        f"| OpenAPI bytes | {before['openapi_bytes']:,} | {after['openapi_bytes']:,} |",
        f"| OpenAPI tokens | {before['openapi_tokens']:,} | {after['openapi_tokens']:,} |",
        f"| MCP definitions, summed per tool | {sum(t['definition'] for t in before['tools'].values()):,} | "
        f"{sum(t['definition'] for t in after['tools'].values()):,} |",
        "", "| MCP tool | Definition before | Definition after | Description before | Description after |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for name, row in after['tools'].items():
        old = before['tools'][name]
        lines.append(f"| `{name}` | {old['definition']:,} | {row['definition']:,} | {old['description']:,} | {row['description']:,} |")
    for key, label in (('paths', 'OpenAPI path'), ('components', 'OpenAPI schema component')):
        lines += ['', f'| {label} | Tokens before | Tokens after |', '| --- | ---: | ---: |']
        for name in sorted(before[key].keys() | after[key].keys()):
            lines.append(f"| `{name}` | {before[key].get(name, 0):,} | {after[key].get(name, 0):,} |")
    return '\n'.join(lines) + '\n'


if __name__ == "__main__":
    main()
