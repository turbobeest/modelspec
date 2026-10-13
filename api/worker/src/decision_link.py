"""Experimental signed inputs for a summary-only human view (MODEL-353)."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import secrets
import time

import access
import decide_service
import visit_token
from decision import bounded, contract

FLAG = "DECISION_LINK_ENABLED"
SECRET = "DECISION_LINK_HMAC_KEY"
LIFETIME_SECONDS = 30 * 24 * 60 * 60
MAX_CAPSULE_BYTES = 4096
MAX_TOKEN_CHARS = 5600
PRIVATE_INPUTS = ("estate", "profile", "save_as")


class LinkRefusal(ValueError):
    def __init__(self, status: int, message: str):
        self.status = status
        super().__init__(message)


def enabled(env) -> bool:
    return access.enforcement(getattr(env, FLAG, None))


def secret_for(env) -> bytes | None:
    value = str(getattr(env, SECRET, "") or "")
    return value.encode() if len(value) >= 32 else None


def attach(body: dict, inputs: dict, snapshot, env) -> None:
    """Add an optional URL only when configured and it fits the existing budget."""
    if not enabled(env) or body.get("representation") != "bounded":
        return
    key = secret_for(env)
    if key is None or not visit_token.enabled(env) or not snapshot.signature_verified \
            or any(inputs.get(name) is not None for name in PRIVATE_INPUTS):
        return
    if not getattr(env, "TURNSTILE_SECRET", None) or getattr(env, "HUMAN_GATE", None) is None \
            or not getattr(env, "VISITOR_HMAC_KEY", None) \
            or str(getattr(env, "BUILD_COMMIT", "") or "") in {"", "dev", "unknown"}:
        return
    try:
        visit_token.secret_for(env)
        visit_token.limits(env, "decide")
        visit_token.limits(env, "vocabulary")
    except (TypeError, ValueError, AttributeError):
        return
    issued = int(time.time())
    capsule = {"v": 1, "nonce": secrets.token_hex(16), "issued": issued,
               "expires": issued + LIFETIME_SECONDS,
               "snapshot": snapshot.snapshot_id, "content_hash": snapshot.content_hash,
               "service_commit": str(getattr(env, "BUILD_COMMIT", "") or "unknown"),
               "decision_id": body["decision_id"], "inputs": inputs}
    raw = json.dumps(capsule, ensure_ascii=False, separators=(",", ":")).encode()
    if len(raw) > MAX_CAPSULE_BYTES:
        return
    encoded = base64.urlsafe_b64encode(raw).decode().rstrip("=")
    signature = hmac.new(key, encoded.encode(), hashlib.sha256).hexdigest()
    url = f"https://modelspec.dev/d/{body['decision_id']}?token={encoded}.{signature}"
    candidate = {**body, "decision_url": url}
    limit = bounded.DRILL_DOWN_BYTES if inputs.get("evidence_for") is not None else bounded.RESPONSE_BYTES
    if bounded.compact_bytes(candidate) <= limit and bounded.mcp_text_bytes(candidate) <= bounded.AGENT_BYTES:
        body["decision_url"] = url


def verify(token: str, decision_id: str, key: bytes, *, now: float | None = None) -> dict:
    """Authenticate the bounded capsule before decoding or examining its expiry."""
    invalid = LinkRefusal(404, "This decision link is invalid.")
    try:
        if not isinstance(token, str) or not isinstance(decision_id, str) or len(token) > MAX_TOKEN_CHARS:
            raise invalid
        encoded, signature = token.split(".")
        if re.fullmatch(r"[A-Za-z0-9_-]+", encoded) is None \
                or re.fullmatch(r"[a-f0-9]{64}", signature) is None:
            raise invalid
        expected = hmac.new(key, encoded.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise invalid
        raw = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        if len(raw) > MAX_CAPSULE_BYTES:
            raise invalid
        capsule = json.loads(raw)
        if not isinstance(capsule, dict) or capsule.get("v") != 1 \
                or re.fullmatch(r"[a-f0-9]{32}", str(capsule.get("nonce", ""))) is None \
                or capsule.get("decision_id") != decision_id \
                or not isinstance(capsule.get("inputs"), dict) \
                or any(capsule["inputs"].get(name) is not None for name in PRIVATE_INPUTS):
            raise invalid
        issued, expires = capsule.get("issued"), capsule.get("expires")
        moment = time.time() if now is None else now
        if type(issued) is not int or type(expires) is not int \
                or expires - issued != LIFETIME_SECONDS or issued > moment:
            raise invalid
        if moment >= expires:
            raise LinkRefusal(410, "This decision link has expired.")
        return capsule
    except (ValueError, TypeError, UnicodeError) as exc:
        if isinstance(exc, LinkRefusal):
            raise
        raise invalid from None


def replay(capsule: dict, snapshot, service_commit: str) -> dict:
    """Recompute only on the identical verified data image and engine revision."""
    if not snapshot.signature_verified or capsule.get("snapshot") != snapshot.snapshot_id \
            or capsule.get("content_hash") != snapshot.content_hash \
            or capsule.get("service_commit") != service_commit:
        raise LinkRefusal(409, "The pinned snapshot or engine revision is no longer available.")
    status, body = decide_service.decide(capsule["inputs"], snapshot)
    if status != 200 or body.get("representation") != "bounded" \
            or body.get("decision_id") != capsule["decision_id"]:
        raise LinkRefusal(404, "This decision link cannot be reproduced.")
    spec = contract.parse_spec({key: value for key, value in capsule["inputs"].items()
                                if key not in ("fields", "evidence_for")}, facets=None)
    normalized = spec.model_dump(mode="json")
    applied = {key: normalized[key] for key in ("where", "optimize", "unknowns", "task_tokens")}
    if applied["task_tokens"] is None:
        applied["task_tokens"] = dict(contract.DEFAULT_TASK_TOKENS)
    not_applied = list(body["explanation"]["not_applied"])
    applied["capabilities"] = {key: value for key, value in (normalized["capabilities"] or {}).items()
                               if key not in not_applied}
    if spec.task_type is not None:
        not_applied.append("task_type")
    if spec.access is not None:
        applied["access"] = normalized["access"]
    if spec.exclude_benchmarks:
        applied["exclude_benchmarks"] = normalized["exclude_benchmarks"]
    return {"decision_id": body["decision_id"],
            "snapshot": {"id": snapshot.snapshot_id, "content_hash": snapshot.content_hash},
            "summary_for_user": body["summary_for_user"], "must_mention": body["must_mention"],
            "requirements": {"applied": applied, "not_applied": not_applied}}
