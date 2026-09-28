#!/usr/bin/env python3
"""Revoke a ModelSpec API key by its SHA-256 fingerprint."""

from __future__ import annotations

import argparse
import json
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

import access_keys  # noqa: E402

_FINGERPRINT = re.compile(r"[0-9a-f]{64}")


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
        result = subprocess.run(get_command, check=True, capture_output=True, text=True)
        record = access_keys.KeyRecord.from_json(result.stdout.strip())
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
        subprocess.run(put_command, check=True)
    except (
        OSError,
        subprocess.CalledProcessError,
        access_keys.StoredKeyError,
        OperatorKeyError,
    ) as exc:
        print(f"error: Wrangler did not revoke the key record: {exc}", file=sys.stderr)
        return 1

    print(f"Revoked API key record {args.fingerprint[:12]} in {access_binding(args.config)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
