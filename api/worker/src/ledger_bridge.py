"""The credit ledger's bridge between two Cloudflare accounts (MODEL-441).

A Durable Object cannot move between accounts. The ledger moves by handoff
instead: the old account's object is sealed and copied into the new
account's object over HTTPS, and every later call the old Worker receives is
forwarded here by `credits.DurableLedger`. There is one live ledger at every
moment, so no balance is lost or counted twice while the zone moves.

Every path needs `LEDGER_BRIDGE_SECRET`. Without it the paths do not exist:
the Worker answers them with the same 404 as any unknown path. Runbook:
docs/ops/cloudflare-account-move.md.
"""

from __future__ import annotations

import hmac
import json
from typing import Any

import credits

PREFIX = "/internal/ledger/"

#: The ledger operations a forwarded call may name: CreditsObject's own RPC
#: methods, never the handoff methods.
CALLABLE = frozenset({
    "credit", "set_monthly", "clear_monthly", "transfer", "reserve", "commit",
    "take_read", "release_read", "keep_read", "meter_identifier",
    "note_unreported", "open_backlog", "ack_backlog", "note_uncertain",
    "list_uncertain", "ack_uncertain", "age_uncertain", "open_meter_events",
    "unreconcile_uncertain", "release", "has_read_funding", "balance", "seen",
    "expect", "payment", "refund", "hold", "end_hold",
})


def secret(env: Any) -> str:
    return str(getattr(env, credits.LEDGER_BRIDGE_SECRET_VAR, "") or "")


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


async def handle(env: Any, path: str, method: str, authorization: str,
                 body: str, *, post: Any = None) -> tuple[int, dict[str, Any]]:
    key = secret(env)
    if not key:
        return _error(404, "not_found", f"no endpoint at {path}")
    if not hmac.compare_digest(str(authorization or ""), "Bearer " + key):
        return _error(401, "unauthorized", "bridge credential missing or wrong")
    namespace = getattr(env, "CREDITS", None)
    if namespace is None:
        return _error(503, "store_not_configured", "CREDITS is not bound")
    stub = namespace.get(namespace.idFromName("ledger"))
    action = path[len(PREFIX):]

    if action == "status":
        if method != "GET":
            return _error(405, "method_not_allowed", "use GET")
        return 200, _plain(await stub.handoff_status())
    if method != "POST":
        return _error(405, "method_not_allowed", "use POST")
    try:
        payload = json.loads(body or "{}")
    except ValueError:
        return _error(400, "invalid_json", "body is not JSON")
    if not isinstance(payload, dict):
        return _error(400, "invalid_request", "body must be an object")

    if action == "call":
        name = payload.get("method")
        args = payload.get("args")
        if name not in CALLABLE or not isinstance(args, list):
            return _error(400, "invalid_request", "unknown ledger method or bad args")
        ledger = credits.DurableLedger(namespace, key, post=post)
        try:
            result = await ledger._call(name, *args)
        except credits.LedgerUnavailable as exc:
            return _error(503, "ledger_unavailable", str(exc))
        return 200, {"result": _plain(result)}

    if action == "import":
        try:
            status = await stub.import_state(str(payload.get("state") or ""),
                                             str(payload.get("digest") or ""))
        except Exception as exc:
            return _error(409, "import_refused", _reason(exc))
        return 200, _plain(status)

    if action == "handoff":
        return await _handoff(stub, key, str(payload.get("target") or ""), post)

    return _error(404, "not_found", f"no endpoint at {path}")


async def _handoff(stub: Any, key: str, target: str,
                   post: Any) -> tuple[int, dict[str, Any]]:
    """Seal, copy, record. The import's outcome decides the seal: refused
    means unseal and keep serving here; unknown (no answer) means stay sealed,
    because the copy may have landed, and re-running finishes the job."""
    target = target.rstrip("/")
    if not target.startswith("https://"):
        return _error(400, "invalid_request", "target must be an https:// origin")
    if post is None:
        from x402_facilitator import worker_post as post
    current = _plain(await stub.handoff_status())
    if current.get("moved_to") == target:
        return 200, current
    try:
        sealed = _plain(await stub.begin_handoff(target))
    except Exception as exc:
        return _error(409, "handoff_refused", _reason(exc))
    try:
        status, answer = await post(
            target + PREFIX + "import",
            {"state": sealed["state"], "digest": sealed["digest"]},
            {"authorization": "Bearer " + key, "content-type": "application/json"})
    except Exception as exc:
        return _error(502, "import_unknown",
                      f"no answer from the target ({type(exc).__name__}); "
                      "the ledger stays sealed; re-run the handoff")
    if status == 200 and answer.get("digest") == sealed["digest"]:
        return 200, _plain(await stub.finish_handoff(target, sealed["digest"]))
    if 400 <= status < 500:
        await stub.abort_handoff()
        return _error(409, "import_refused",
                      f"the target refused the copy (HTTP {status}); the ledger is unsealed")
    return _error(502, "import_unknown",
                  f"the target answered HTTP {status}; the ledger stays sealed; re-run the handoff")


def _reason(exc: Exception) -> str:
    """The last line of a Python error as it crosses RPC: the message, without
    a traceback."""
    lines = [line for line in str(exc).strip().splitlines() if line.strip()]
    return lines[-1][:300] if lines else type(exc).__name__
