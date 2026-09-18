#!/usr/bin/env python3
"""Read a live MCP response without raising on Cloudflare error pages.

MODEL-68's deploy of e0265a5 went red on a healthy Worker because inline
json.loads hit a 522 HTML page and aborted the retry loop. Nothing here
raises on a body.

    check_response.py field NAME BODY
    check_response.py digest PATH STATUS BODY
    check_response.py initialize BODY
    check_response.py tools-list BODY
"""

from __future__ import annotations

import json
import sys
from typing import Any

EXPECTED_TOOLS = ("rank", "model_info", "list_use_cases", "policy_check")
SNIPPET_BYTES = 200


def read_body(path: str) -> tuple[Any, bytes, str | None]:
    try:
        with open(path, "rb") as handle:
            raw = handle.read()
    except OSError as exc:
        return None, b"", f"the body file could not be read: {exc}"
    text = raw.decode("utf-8", "replace").strip()
    if not text:
        return None, raw, "the body is empty"
    parsed, problem = parse_mcp(text)
    return parsed, raw, problem


def parse_mcp(text: str) -> tuple[Any, str | None]:
    if text.startswith("{") or text.startswith("["):
        try:
            return json.loads(text), None
        except ValueError as exc:
            return None, f"the body is not JSON ({exc})"
    datas: list[Any] = []
    for line in text.splitlines():
        if not line.startswith("data:"):
            continue
        payload = line[5:].strip()
        if not payload or payload == "[DONE]":
            continue
        try:
            datas.append(json.loads(payload))
        except ValueError:
            continue
    if not datas:
        return None, "the body is not JSON and has no SSE data frames"
    if len(datas) == 1:
        return datas[0], None
    return datas, None


def snippet(raw: bytes) -> str:
    piece = raw[:SNIPPET_BYTES].decode("utf-8", "replace").replace("\n", " ")
    return piece


def describe(path: str, status: str, raw: bytes, problem: str | None) -> str:
    extra = f"; {problem}" if problem else ""
    return f"HTTP {status} path {path} body {snippet(raw)!r}{extra}"


def rpc_result(parsed: Any) -> dict[str, Any] | None:
    if not isinstance(parsed, dict):
        return None
    result = parsed.get("result")
    return result if isinstance(result, dict) else None


def check_initialize(parsed: Any, expected_version: str) -> list[str]:
    problems: list[str] = []
    result = rpc_result(parsed)
    if result is None:
        return ["initialize did not return a JSON-RPC result object"]
    info = result.get("serverInfo")
    if not isinstance(info, dict):
        return ["initialize result has no serverInfo"]
    version = info.get("version")
    if version != expected_version:
        problems.append(
            f"serverInfo.version is {version!r}, want {expected_version!r}"
        )
    if info.get("name") != "modelspec":
        problems.append(f"serverInfo.name is {info.get('name')!r}, want 'modelspec'")
    return problems


def check_tools_list(parsed: Any) -> list[str]:
    result = rpc_result(parsed)
    if result is None:
        return ["tools/list did not return a JSON-RPC result object"]
    tools = result.get("tools")
    if not isinstance(tools, list):
        return ["tools/list result.tools is not a list"]
    names = [row.get("name") for row in tools if isinstance(row, dict)]
    missing = [name for name in EXPECTED_TOOLS if name not in names]
    problems: list[str] = []
    if missing:
        problems.append(f"missing tools: {missing}; saw {names}")
    if len(tools) != 4:
        problems.append(f"expected 4 tools, got {len(tools)}")
    for row in tools:
        if not isinstance(row, dict):
            problems.append("a tools/list entry is not an object")
            continue
        schema = row.get("inputSchema") or row.get("input_schema")
        if not isinstance(schema, dict):
            problems.append(f"tool {row.get('name')!r} has no input schema")
        elif schema.get("type") not in (None, "object"):
            problems.append(
                f"tool {row.get('name')!r} input schema type is {schema.get('type')!r}"
            )
    return problems


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: check_response.py <field|digest|initialize|tools-list> ...",
              file=sys.stderr)
        return 2
    command = argv[1]
    if command == "field":
        _, _, name, path = argv[0], argv[1], argv[2], argv[3]
        parsed, raw, problem = read_body(path)
        if problem:
            print(problem, file=sys.stderr)
            return 0
        result = rpc_result(parsed) or {}
        info = result.get("serverInfo") if isinstance(result.get("serverInfo"), dict) else {}
        if name == "version":
            print(info.get("version") or "")
        else:
            value = result.get(name)
            print("" if value is None else value)
        return 0
    if command == "digest":
        _, _, path, status, body = argv[0], argv[1], argv[2], argv[3], argv[4]
        parsed, raw, problem = read_body(body)
        print(describe(path, status, raw, problem))
        return 0
    if command == "initialize":
        path, expected = argv[2], argv[3]
        parsed, raw, problem = read_body(path)
        if problem:
            print(problem, file=sys.stderr)
            return 1
        issues = check_initialize(parsed, expected)
        if issues:
            print("; ".join(issues), file=sys.stderr)
            return 1
        return 0
    if command == "tools-list":
        parsed, raw, problem = read_body(argv[2])
        if problem:
            print(problem, file=sys.stderr)
            return 1
        issues = check_tools_list(parsed)
        if issues:
            print("; ".join(issues), file=sys.stderr)
            return 1
        return 0
    print(f"unknown command {command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
