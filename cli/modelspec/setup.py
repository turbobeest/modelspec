"""Print or merge one MCP server entry, preserving the surrounding configuration."""

from __future__ import annotations

import difflib
import json
import os
import re
import sys
import tempfile
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import typer

from .errors import ClientError
from .guidance import BUNDLE, TEXT


def config_path(client: dict[str, Any], override: str | None) -> Path | None:
    if override:
        return Path(override).expanduser()
    path = client["path"]
    if path == "desktop":
        if sys.platform == "darwin":
            return Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
        if sys.platform == "win32":
            return (
                Path(os.environ.get("APPDATA", str(Path.home() / "AppData/Roaming")))
                / "Claude/claude_desktop_config.json"
            )
        return Path.home() / ".config/Claude/claude_desktop_config.json"
    return Path(path).expanduser() if path else None


def snippet(client: dict[str, Any]) -> str:
    value = {client["table"]: {"modelspec": client["server"]}}
    if client["format"] == "toml":
        header = f"{client['table']}.modelspec"
        lines = [f"[{header}]"]
        for key, item in client["server"].items():
            if not isinstance(item, dict):
                lines.append(f"{key} = {json.dumps(item)}")
        for key, item in client["server"].items():
            if isinstance(item, dict):
                lines.extend(["", f"[{header}.{key}]"])
                lines.extend(f"{name} = {json.dumps(content)}" for name, content in item.items())
        return "\n".join(lines) + "\n"
    return json.dumps(value, indent=2) + "\n"


def _object_spans(text: str, start: int = 0) -> tuple[dict[str, tuple[int, int]], int]:
    """Find JSON object values without reformatting any other server's bytes."""
    decoder = json.JSONDecoder()
    start += len(text[start:]) - len(text[start:].lstrip())
    if text[start] != "{":
        raise ValueError("object required")
    index = start + 1
    spans = {}
    while True:
        index += len(text[index:]) - len(text[index:].lstrip())
        if text[index] == "}":
            return spans, index
        key, index = decoder.raw_decode(text, index)
        index += len(text[index:]) - len(text[index:].lstrip())
        if text[index] != ":" or key in spans:
            raise ValueError("invalid or duplicate key")
        index += 1
        index += len(text[index:]) - len(text[index:].lstrip())
        value_start = index
        _, index = decoder.raw_decode(text, index)
        spans[key] = (value_start, index)
        index += len(text[index:]) - len(text[index:].lstrip())
        if text[index] == ",":
            index += 1
        elif text[index] != "}":
            raise ValueError("invalid JSON object")


def _insert(text: str, end: int, *, key: str, value: str, populated: bool) -> str:
    entry = ("," if populated else "") + "\n  " + json.dumps(key) + ": " + value + "\n"
    return text[:end] + entry + text[end:]


def merge(original: str, client: dict[str, Any]) -> str:
    table, server = client["table"], client["server"]
    if client["format"] == "toml":
        document = tomllib.loads(original)
        if not isinstance(document.get(table, {}), dict):
            raise ValueError("server table required")
        if document.get(table, {}).get("modelspec") == server:
            return original
        headers = list(re.finditer(r"^\s*\[([^\]\n]+)\][ \t]*(?:#[^\n]*)?$", original, re.M))
        owned = []
        for index, header in enumerate(headers):
            section = tomllib.loads(header[0])
            if "modelspec" in section.get(table, {}):
                owned.append(
                    (
                        header.start(),
                        headers[index + 1].start() if index + 1 < len(headers) else len(original),
                    )
                )
        # Inline or dotted-key definitions cannot be replaced by a table without
        # rewriting their neighbours. Leave those unusual layouts for manual setup.
        if "modelspec" in document.get(table, {}) and not owned:
            raise ValueError("inline server definition")
        updated = original
        for start, stop in reversed(owned):
            updated = updated[:start] + updated[stop:]
        updated = updated.rstrip("\n") + ("\n\n" if updated else "") + snippet(client)
        expected = {**document, table: {**document.get(table, {}), "modelspec": server}}
        if tomllib.loads(updated) != expected:
            raise ValueError("configuration changed outside modelspec")
        return updated
    text = original or "{}\n"
    document = json.loads(text)
    if not isinstance(document, dict) or (
        table in document and not isinstance(document[table], dict)
    ):
        raise ValueError("server object required")
    if document.get(table, {}).get("modelspec") == server:
        return original
    roots, end = _object_spans(text)
    if table not in roots:
        return _insert(
            text,
            end,
            key=table,
            value=json.dumps({"modelspec": server}, indent=2),
            populated=bool(roots),
        )
    servers, end = _object_spans(text, roots[table][0])
    value = json.dumps(server, indent=2)
    if "modelspec" in servers:
        start, stop = servers["modelspec"]
        return text[:start] + value + text[stop:]
    return _insert(text, end, key="modelspec", value=value, populated=bool(servers))


def _redacted(text: str) -> str:
    # Diff context is zero lines. Only a replaced ModelSpec entry can appear.
    text = re.sub(r'(Bearer\s+)(?!\$\{|<)([^"\s]+)', r"\1[redacted]", text)
    return re.sub(
        r'((?:AUTH_HEADER|API_KEY|api_key|token|password|secret)["\s]*[:=]\s*")(?!\$\{|<)[^"]*',
        r"\1[redacted]",
        text,
    )


def prepare(name: str, override: str | None) -> tuple[dict[str, Any], str]:
    if name not in BUNDLE["clients"]:
        raise ClientError("invalid_client", recovery="setup")
    client = BUNDLE["clients"][name]
    path = config_path(client, override)
    output = {
        "client": name,
        "guide_version": BUNDLE["guide_version"],
        "path": str(path) if path else None,
        "snippet": snippet(client),
        "command": client.get("command"),
        "source": client["source"],
        "guidance": TEXT["setup_note"],
        "guide": BUNDLE["urls"]["guide"],
        "next": [TEXT[client["note"]]] if "note" in client else [TEXT["setup_note"]],
    }
    return output, "\n".join(
        str(line)
        for line in (
            output["command"],
            output["snippet"],
            output["guidance"],
            *(step for step in output["next"] if step != output["guidance"]),
            output["guide"],
        )
        if line
    )


def _backup(path: Path, contents: bytes) -> Path:
    base = path.with_name(path.name + ".modelspec-bak")
    backup = base
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
    collision = 0
    while True:
        try:
            descriptor = os.open(backup, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            break
        except FileExistsError:
            suffix = f".{timestamp}" + (f".{collision}" if collision else "")
            backup = base.with_name(base.name + suffix)
            collision += 1
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(contents)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError:
        backup.unlink(missing_ok=True)
        raise
    return backup


def write(name: str, override: str | None, *, yes: bool, as_json: bool) -> dict[str, Any]:
    client = BUNDLE["clients"][name]
    path = config_path(client, override)
    if path is None:
        raise ClientError("config_path_required", recovery="setup")
    try:
        if path.is_symlink():
            raise ValueError("symlink")
        original_bytes = path.read_bytes() if path.exists() else None
        original = original_bytes.decode("utf-8") if original_bytes is not None else ""
        proposed = merge(original, client)
    except (OSError, ValueError, TypeError, IndexError):
        raise ClientError("config_unreadable", recovery="setup") from None
    if proposed == original:
        return {
            "written": False,
            "message": TEXT["setup_unchanged"].format(path=path),
            "next": [TEXT["setup_note"]],
        }
    diff = "".join(
        difflib.unified_diff(
            _redacted(original).splitlines(keepends=True),
            _redacted(proposed).splitlines(keepends=True),
            fromfile=str(path),
            tofile=str(path),
            n=0,
        )
    )
    # JSON stdout stays a single document; the reviewable diff is always on stderr.
    typer.echo(diff, err=True, nl=False)
    if not yes:
        if as_json or not sys.stdin.isatty():
            raise ClientError("confirmation_required", recovery="setup")
        if not typer.confirm(TEXT["write_prompt"], default=False, err=True):
            return {
                "written": False,
                "message": TEXT["setup_cancelled"],
                "next": [TEXT["setup_note"]],
            }
    temporary = None
    backup = None
    try:
        current = path.read_bytes() if path.exists() else None
        if current != original_bytes or path.is_symlink():
            raise ClientError("config_changed", recovery="setup")
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, name_ = tempfile.mkstemp(prefix=".modelspec-mcp-", dir=path.parent)
        temporary = Path(name_)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(proposed)
        if original_bytes is not None:
            backup = _backup(path, original_bytes)
        temporary.replace(path)
    except OSError:
        raise ClientError("config_unwritable", recovery="setup") from None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return {
        "written": True,
        "path": str(path),
        "backup": str(backup) if backup is not None else None,
        "message": TEXT["setup_written"].format(path=path)
        + (" " + TEXT["setup_backup"].format(path=backup) if backup is not None else ""),
        "next": [TEXT["setup_note"], *([TEXT[client["note"]]] if "note" in client else [])],
    }
