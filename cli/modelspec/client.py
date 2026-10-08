"""Keyed, stateless HTTP. Responses live only for the current invocation."""

from __future__ import annotations

from typing import Any

import httpx

from .auth import Credential
from .errors import ClientError
from .guidance import BUNDLE, TEXT, next_steps

_transport: httpx.BaseTransport | None = None


class Client:
    def __init__(self, credential: Credential) -> None:
        self.credential = credential
        self.guide_changed = False

    def request(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        feedback: bool = False,
    ) -> httpx.Response:
        headers = {
            "User-Agent": f"modelspec-cli/{BUNDLE['cli_version']}",
            "Accept": "application/json",
        }
        if not feedback:
            headers["Authorization"] = f"Bearer {self.credential.secret}"
        try:
            with httpx.Client(
                timeout=30,
                transport=_transport,
                trust_env=False,
                follow_redirects=False,
                headers=headers,
            ) as session:
                response = session.request(
                    method, BUNDLE["urls"]["api"] + path, json=body, params=params
                )
        except (httpx.HTTPError, ValueError):
            raise ClientError(
                "network_error",
                recovery="network",
                extra_next=next_steps("upgrade") if self.guide_changed else None,
            ) from None
        version = response.headers.get("x-modelspec-guide-version")
        self.guide_changed |= bool(version and version != BUNDLE["guide_version"])
        # A broken server must not be able to echo the presented credential.
        # response.text is already decoded; encoding headers would decode it again.
        kept = [
            (name, value)
            for name, value in response.headers.multi_items()
            if name.lower() not in {"content-encoding", "content-length", "transfer-encoding"}
        ]
        response = httpx.Response(
            response.status_code,
            headers=kept,
            text=self.credential.redact(response.text),
        )
        try:
            payload = response.json()
        except ValueError:
            payload = None
        error = payload.get("error") if isinstance(payload, dict) else None
        code = str(error.get("code", "http_error")) if isinstance(error, dict) else "http_error"
        status = payload.get("status") if isinstance(payload, dict) else None
        if status is not None and not isinstance(status, str):
            raise ClientError(
                "unexpected_response",
                recovery="network",
                extra_next=next_steps("upgrade") if self.guide_changed else None,
            )
        # A 200 decision with decision_id and no error object. no_feasible, and
        # any such decision that carries coverage, exits 2 as the decision body.
        # answered or partial without coverage is an answer and exits 0.
        decision = (
            response.status_code < 300
            and isinstance(payload, dict)
            and isinstance(payload.get("decision_id"), str)
            and bool(payload["decision_id"])
            and status in {"answered", "partial", "no_feasible"}
            and not error
        )
        has_coverage = (
            isinstance(payload, dict)
            and isinstance(payload.get("coverage"), dict)
            and bool(payload["coverage"])
        )
        if decision and (status == "no_feasible" or has_coverage):
            raise ClientError(
                "no_feasible" if status == "no_feasible" else "out_of_coverage",
                recovery="coverage",
                exit_code=2,
                body=payload,
                passthrough=True,
                guide_changed=self.guide_changed,
            )
        recovery, exit_code = "spec", 1
        if response.status_code in (401, 403):
            recovery, exit_code = "key", 5
        elif response.status_code in (402, 429):
            recovery, exit_code = "credits", 6
        elif response.status_code == 426 or code in {
            "upgrade_required",
            "cli_outdated",
            "guide_outdated",
        }:
            recovery = "upgrade"
        elif not decision and (code in {
            "out_of_coverage",
            "no_match",
            "no_feasible",
            "unsupported_task",
            "capability_unavailable",
        } or status in {"no_feasible", "no_match", "out_of_coverage"} or (
            isinstance(payload, dict) and isinstance(payload.get("coverage"), dict)
            and payload["coverage"].get("kind") == "out_of_coverage"
        )):
            recovery, exit_code = "coverage", 2
        elif response.status_code >= 500:
            recovery = "network"
        if not decision and (
            response.status_code >= 300
            or error
            or status in {"refused", "no_feasible", "no_match", "out_of_coverage"}
            or recovery == "coverage"
        ):
            if not isinstance(payload, dict):
                fallback = {"key": "invalid_api_key", "upgrade": "http_error"}.get(
                    recovery, "http_error"
                )
                payload = {"error": {"code": fallback, "message": TEXT["errors"][fallback]}}
            if response.headers.get("retry-after"):
                payload = {**payload, "retry_after": response.headers["retry-after"]}
            scope = payload.get("coverage") or {}
            scope_next = [scope[key] for key in ("message", "url")
                          if isinstance(scope, dict) and isinstance(scope.get(key), str)]
            raise ClientError(
                code,
                recovery=recovery,
                exit_code=exit_code,
                body=payload,
                extra_next=scope_next + (next_steps("upgrade") if self.guide_changed else []),
            )
        if not isinstance(payload, dict):
            raise ClientError(
                "unexpected_response",
                recovery="network",
                extra_next=next_steps("upgrade") if self.guide_changed else None,
            )
        return response
