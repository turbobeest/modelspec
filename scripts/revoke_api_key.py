#!/usr/bin/env python3
"""Revoke a ModelSpec API key by its SHA-256 fingerprint."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

SCRIPTS_ROOT = Path(__file__).resolve().parent
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from api_key_operator import (  # noqa: E402
    DEFAULT_WRANGLER_CONFIG,
    WORKER_SRC,
    OperatorKeyError,
    access_binding,
    wrangler_target,
)

if str(WORKER_SRC) not in sys.path:
    sys.path.insert(0, str(WORKER_SRC))

import access_config  # noqa: E402
import access_keys  # noqa: E402

_FINGERPRINT = re.compile(r"[0-9a-f]{64}")
# token_urlsafe(24) is 32 characters. 16 avoids redacting short words after the prefix.
_SECRET_BODY = r"[A-Za-z0-9_\-]{16,}"


def _wrangler_env() -> dict[str, str]:
    # Wrangler asks about metrics when it sees a terminal, then exits non-zero
    # when that prompt cannot be shown. These two variables skip the prompt.
    # Closed stdin means a captured run is not a terminal.
    env = dict(os.environ)
    env["CI"] = "1"
    env["WRANGLER_SEND_METRICS"] = "false"
    return env


def _secret_pattern() -> re.Pattern[str]:
    policy = access_config.load_policy()
    prefixes = [
        re.escape(prefix) for prefix in (policy.live_prefix, policy.sandbox_prefix) if prefix
    ]
    return re.compile(f"(?:{'|'.join(prefixes)}){_SECRET_BODY}")


def _json_object_end(text: str, start: int) -> int | None:
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index + 1
    return None


def _looks_like_stored_key(blob: str) -> bool:
    try:
        data = json.loads(blob)
    except ValueError:
        return False
    return (
        isinstance(data, dict)
        and isinstance(data.get("key_id"), str)
        and isinstance(data.get("tier"), str)
        and data["tier"] != ""
    )


def _redact(text: str) -> str:
    """Remove live secrets and stored key records from text Wrangler printed."""
    redacted = _secret_pattern().sub("[redacted]", text)
    pieces: list[str] = []
    index = 0
    while index < len(redacted):
        start = redacted.find("{", index)
        if start < 0:
            pieces.append(redacted[index:])
            break
        end = _json_object_end(redacted, start)
        if end is not None and _looks_like_stored_key(redacted[start:end]):
            pieces.append(redacted[index:start])
            pieces.append("[redacted]")
            index = end
            continue
        pieces.append(redacted[index : start + 1])
        index = start + 1
    return "".join(pieces)


def _run_wrangler(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        env=_wrangler_env(),
        check=False,
    )
    if result.returncode != 0:
        stderr = _redact(result.stderr or "").strip()
        detail = f"wrangler exited {result.returncode}"
        if stderr:
            detail = f"{detail}: {stderr}"
        raise OperatorKeyError(detail)
    return result


def _commands(fingerprint: str, config: Path) -> tuple[list[str], str]:
    name = access_keys.storage_name_from_fingerprint(fingerprint)
    get = ["npx", "wrangler", "kv", "key", "get", name, *wrangler_target(config)]
    return get, name


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "fingerprint", help="full SHA-256 fingerprint printed when the key was issued"
    )
    parser.add_argument(
        "--config", type=Path, default=DEFAULT_WRANGLER_CONFIG, help="Wrangler config path"
    )
    parser.add_argument("--put", action="store_true", help="mark the remote KV record inactive")
    args = parser.parse_args(argv)

    if _FINGERPRINT.fullmatch(args.fingerprint) is None:
        print(
            "error: fingerprint must contain 64 lowercase hexadecimal characters",
            file=sys.stderr,
        )
        return 2
    try:
        get_command, name = _commands(args.fingerprint, args.config)
    except OperatorKeyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not args.put:
        print("Wrangler lookup command:")
        print("  " + shlex.join(get_command))
        print("Re-run this script with --put to mark the record inactive.")
        return 0

    try:
        fetched = _run_wrangler(get_command)
        record = access_keys.KeyRecord.from_json(fetched.stdout.strip())
        if record.key_id != args.fingerprint[: access_keys.KEY_ID_LENGTH]:
            raise OperatorKeyError(
                f"stored key id {record.key_id!r} does not match fingerprint "
                f"{args.fingerprint[:12]!r}"
            )
        value = json.dumps(replace(record, active=False).to_json())
        put_command = [
            "npx",
            "wrangler",
            "kv",
            "key",
            "put",
            name,
            "--value",
            value,
            *wrangler_target(args.config),
        ]
        _run_wrangler(put_command)
    except (
        OSError,
        subprocess.CalledProcessError,
        access_keys.StoredKeyError,
        OperatorKeyError,
    ) as exc:
        print(
            f"error: Wrangler did not revoke the key record: {_redact(str(exc))}",
            file=sys.stderr,
        )
        return 1

    print(f"Revoked API key record {args.fingerprint[:12]} in {access_binding(args.config)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
