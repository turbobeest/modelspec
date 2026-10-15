"""Prepare a registry manifest only when the reviewed commit is deployed."""

from __future__ import annotations

import argparse
import json
import re
import urllib.request
from pathlib import Path

from mcp.scripts.check_response import check_initialize, parse_mcp


def prepare_manifest(manifest: dict, response: str, expected_version: str) -> dict:
    if not re.fullmatch(r"[0-9a-f]{40}", expected_version):
        raise ValueError("expected_version must be a full deployment commit SHA")
    parsed, problem = parse_mcp(response)
    if problem:
        raise ValueError(problem)
    problems = check_initialize(parsed, expected_version)
    if problems:
        raise ValueError("; ".join(problems))
    return {**manifest, "version": expected_version}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(Path("server.json").read_text())
    request = urllib.request.Request(
        manifest["remotes"][0]["url"],
        data=json.dumps({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26", "capabilities": {},
                "clientInfo": {"name": "modelspec-registry", "version": "1"},
            },
        }).encode(),
        headers={
            "Content-Type": "application/json", "Accept": "application/json, text/event-stream",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read().decode("utf-8")
    prepared = prepare_manifest(manifest, body, args.expected_version)
    args.output.write_text(json.dumps(prepared, indent=2) + "\n")
    print(f"Registry manifest verified against deployed MCP commit {prepared['version']}")


if __name__ == "__main__":
    main()
