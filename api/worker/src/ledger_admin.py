"""Operator endpoints that move the credit ledger between accounts (MODEL-441).

A Durable Object cannot move between Cloudflare accounts. The ledger moves
across a short write freeze instead: the operator exports it from the old
Worker, which seals it, and imports the copy into the new Worker, whose ledger
waits in standby. Nothing here calls another Worker; the copy travels through
the operator's machine.

Every path needs `LEDGER_ADMIN_SECRET`. Without it the paths do not exist: the
Worker answers them with the same 404 as any unknown path. Runbook:
docs/ops/cloudflare-account-move.md.
"""

from __future__ import annotations

import hmac
import json
import re
from typing import Any

PREFIX = "/internal/ledger/"
#: The only holders a repair may name: an API key's ledger account.
KEY_HOLDER = re.compile(r"key:[0-9a-f]{64}")
SECRET_VAR = "LEDGER_ADMIN_SECRET"


def secret(env: Any) -> str:
    return str(getattr(env, SECRET_VAR, "") or "")


def _plain(value: Any) -> Any:
    to_py = getattr(value, "to_py", None)
    if callable(to_py):
        value = to_py()
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


def _error(status: int, code: str, message: str) -> tuple[int, dict[str, Any]]:
    return status, {"error": {"code": code, "message": message}}


def _reason(exc: Exception) -> str:
    """The last line of a Python error as it crosses RPC: the message, without
    a traceback."""
    lines = [line for line in str(exc).strip().splitlines() if line.strip()]
    return lines[-1][:300] if lines else type(exc).__name__


async def handle(env: Any, path: str, method: str, authorization: str,
                 body: str) -> tuple[int, dict[str, Any]]:
    key = secret(env)
    if not key:
        return _error(404, "not_found", f"no endpoint at {path}")
    if not hmac.compare_digest(str(authorization or ""), "Bearer " + key):
        return _error(401, "unauthorized", "admin credential missing or wrong")
    namespace = getattr(env, "CREDITS", None)
    if namespace is None:
        return _error(503, "store_not_configured", "CREDITS is not bound")
    stub = namespace.get(namespace.idFromName("ledger"))
    action = path[len(PREFIX):]

    if action == "status":
        if method != "GET":
            return _error(405, "method_not_allowed", "use GET")
        return 200, _plain(await stub.move_status())
    if action not in ("export", "import", "unseal", "transfer"):
        return _error(404, "not_found", f"no endpoint at {path}")
    if method != "POST":
        return _error(405, "method_not_allowed", "use POST")
    try:
        payload = json.loads(body or "{}")
    except ValueError:
        return _error(400, "invalid_json", "body is not JSON")
    if not isinstance(payload, dict):
        return _error(400, "invalid_request", "body must be an object")
    try:
        if action == "export":
            return 200, _plain(await stub.export_state())
        if action == "import":
            return 200, _plain(await stub.import_state(
                str(payload.get("state") or ""), str(payload.get("digest") or ""),
                str(payload.get("generation") or "")))
        if action == "transfer":
            # The repair for a key rotation that outlived its lease: the
            # balance went to a key nobody was shown (runbook, residual risks).
            src, dst = payload.get("src"), payload.get("dst")
            if not (isinstance(src, str) and isinstance(dst, str) and src != dst
                    and KEY_HOLDER.fullmatch(src) and KEY_HOLDER.fullmatch(dst)):
                return _error(400, "invalid_request",
                              "src and dst must be two different key:<64 hex> holders")
            moved = await stub.transfer(src, dst)
            return 200, {"moved": bool(_plain(moved))}
        return 200, _plain(await stub.unseal(str(payload.get("digest") or "")))
    except Exception as exc:
        return _error(409, f"{action}_refused", _reason(exc))
