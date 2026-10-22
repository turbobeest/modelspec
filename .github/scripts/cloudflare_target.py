"""Point a Wrangler config at the account a deploy job targets (MODEL-441).

Wrangler prefers the config's `account_id` over CLOUDFLARE_ACCOUNT_ID, so the
job's secret alone cannot choose the account. The committed value stays, for
operators' local wrangler commands; this rewrites the CI checkout's copy in
place before a deploy and is never committed. Per-account values come from
the job's GitHub environment:

  CLOUDFLARE_ACCOUNT_ID  the account (never printed)
  CF_KV_<BINDING>        namespace id for a top-level KV binding, e.g. CF_KV_ACCESS
  CF_WORKERS_DEV         "true" or "false" for the top-level workers_dev
  CF_ROUTES              "off" deploys without the top-level routes: Workers
                         routes need an active zone, and the moved zone is
                         Pending until the move (scripts/cf_move.py attach-routes)

Unset or empty variables leave the committed value. Staging is never touched.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from pipeline.worker_flags import parse_jsonc  # noqa: E402

HEX_ID = re.compile(r"[0-9a-f]{32}")


def retarget(text: str, environ: dict[str, str]) -> tuple[str, list[str]]:
    config = parse_jsonc(text)
    changes: list[str] = []
    account = (environ.get("CLOUDFLARE_ACCOUNT_ID") or "").strip()
    if account and account != config.get("account_id"):
        if not HEX_ID.fullmatch(account):
            raise ValueError("CLOUDFLARE_ACCOUNT_ID is not a 32-hex account id")
        old = f'"account_id": "{config.get("account_id")}"'
        if text.count(old) != 1:
            raise ValueError("account_id is not written exactly once")
        text = text.replace(old, f'"account_id": "{account}"')
        changes.append("account_id")
    for binding in config.get("kv_namespaces", []):
        name = binding["binding"]
        wanted = (environ.get(f"CF_KV_{name}") or "").strip()
        if not wanted or wanted == binding["id"]:
            continue
        if not HEX_ID.fullmatch(wanted):
            raise ValueError(f"CF_KV_{name} is not a 32-hex namespace id")
        old = f'"id": "{binding["id"]}"'
        if text.count(old) != 1:
            raise ValueError(f"{name}'s namespace id is not written exactly once")
        text = text.replace(old, f'"id": "{wanted}"')
        changes.append(f"{name} namespace")
    workers_dev = (environ.get("CF_WORKERS_DEV") or "").strip().lower()
    if workers_dev:
        if workers_dev not in ("true", "false"):
            raise ValueError("CF_WORKERS_DEV must be true or false")
        current = "true" if config.get("workers_dev") else "false"
        if workers_dev != current:
            text, count = re.subn(r'^(  "workers_dev": )(true|false)', rf"\g<1>{workers_dev}",
                                  text, count=1, flags=re.MULTILINE)
            if count != 1:
                raise ValueError("no top-level workers_dev to change")
            changes.append(f"workers_dev={workers_dev}")
    routes = (environ.get("CF_ROUTES") or "").strip().lower()
    if routes:
        if routes != "off":
            raise ValueError("CF_ROUTES must be off or unset")
        if config.get("routes"):
            text, count = re.subn(r'^(  "routes": )\[\n.*?^  \]', r"\g<1>[]", text,
                                  count=1, flags=re.MULTILINE | re.DOTALL)
            if count != 1:
                raise ValueError("no top-level routes block to clear")
            changes.append("routes=off")
    after = parse_jsonc(text)
    if routes and after.get("routes"):
        raise ValueError("routes were not cleared")
    if after.get("env") != config.get("env"):
        raise ValueError("retargeting changed an environment block")
    if account and after.get("account_id") != account:
        raise ValueError("account_id was not retargeted")
    return text, changes


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: cloudflare_target.py <wrangler.jsonc>", file=sys.stderr)
        return 2
    path = Path(argv[1])
    text, changes = retarget(path.read_text(encoding="utf-8"), dict(os.environ))
    path.write_text(text, encoding="utf-8")
    print(f"{path}: " + (", ".join(changes) if changes else "committed bindings"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
