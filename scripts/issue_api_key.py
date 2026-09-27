#!/usr/bin/env python3
"""Issue a live ModelSpec API key directly into the Worker's KV namespace."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
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


@dataclass(frozen=True)
class IssuedKey:
    """The one-time secret and the non-secret KV material derived from it."""

    secret: str
    fingerprint: str
    name: str
    value: str
    created_at: str


def build_key(
    *,
    owner: str,
    label: str = "",
    tier: str = "free",
    secret: str | None = None,
    now: datetime | None = None,
) -> IssuedKey:
    """Build the same secret and record that `access_keys.issue` stores."""
    policy = access_config.load_policy()
    policy.tier(tier)
    key = secret or access_keys.mint(policy)
    created_at = (now or datetime.now(UTC)).isoformat().replace("+00:00", "Z")
    record = access_keys.KeyRecord(
        key_id=access_keys.key_id(key),
        tier=tier,
        owner=owner,
        created_at=created_at,
        active=True,
        label=label,
    )
    return IssuedKey(
        secret=key,
        fingerprint=access_keys.fingerprint(key),
        name=access_keys.storage_name(key),
        value=json.dumps(record.to_json()),
        created_at=created_at,
    )


def put_command(
    issued: IssuedKey,
    config: Path = DEFAULT_WRANGLER_CONFIG,
    environment: str | None = None,
) -> list[str]:
    """Build the Wrangler command that writes the non-secret record."""
    environment_args = ["--env", environment] if environment else []
    return [
        "npx",
        "wrangler",
        "kv",
        "key",
        "put",
        issued.name,
        "--value",
        issued.value,
        *environment_args,
        *wrangler_target(config),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", required=True, help="operator label for the key owner")
    parser.add_argument("--label", default="", help="optional purpose shown in the KV record")
    parser.add_argument("--tier", default="free", help="tier from api/worker/tiers.json")
    parser.add_argument(
        "--config", type=Path, default=DEFAULT_WRANGLER_CONFIG, help="Wrangler config path"
    )
    parser.add_argument("--env", help="Wrangler environment, for example staging")
    parser.add_argument("--put", action="store_true", help="write the record to remote Workers KV")
    args = parser.parse_args(argv)

    try:
        issued = build_key(owner=args.owner, label=args.label, tier=args.tier)
        command = put_command(issued, args.config, args.env)
    except (access_config.PolicyError, OperatorKeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"API key: {issued.secret}")
    print("Store it in 1Password now. This key will not be shown again.")
    print(f"Fingerprint: {issued.fingerprint}")
    print(f"KV name: {issued.name}")
    print(f"KV value: {issued.value}")
    print("Wrangler command:")
    print("  " + shlex.join(command))

    if not args.put:
        return 0
    try:
        subprocess.run(command, check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"error: Wrangler did not store the key record: {exc}", file=sys.stderr)
        return 1
    print(f"Stored API key record {issued.fingerprint[:12]} in {access_binding(args.config)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
