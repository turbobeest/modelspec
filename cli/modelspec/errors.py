"""One error contract for usage, local files, auth and hosted refusals."""

from __future__ import annotations

import json
from typing import Any, NoReturn

import typer

from .guidance import TEXT, next_steps


class ClientError(Exception):
    def __init__(
        self,
        code: str,
        *,
        recovery: str = "usage",
        exit_code: int = 1,
        body: dict[str, Any] | None = None,
        issues: list[dict[str, str]] | None = None,
        extra_next: list[str] | None = None,
        passthrough: bool = False,
        guide_changed: bool = False,
    ) -> None:
        self.code = code
        self.exit_code = exit_code
        self.body = body
        self.issues = issues
        self.passthrough = passthrough
        self.guide_changed = guide_changed
        self.next = [*next_steps(recovery), *(extra_next or [])]
        super().__init__(code)


def guide_version_notice(as_json: bool) -> None:
    """The stderr notice `_response` prints when the server guide moved."""
    notice = {
        "warning": {"code": "guide_version_changed", "message": TEXT["guide_changed"]},
        "next": next_steps("upgrade"),
    }
    typer.echo(
        json.dumps(notice)
        if as_json
        else "\n".join([TEXT["guide_changed"], TEXT["next_label"], *notice["next"]]),
        err=True,
    )


def fail(error: ClientError, *, command: str, as_json: bool) -> NoReturn:
    if error.passthrough and isinstance(error.body, dict):
        if error.guide_changed:
            guide_version_notice(as_json)
        if as_json:
            typer.echo(json.dumps(error.body, ensure_ascii=False))
        else:
            typer.echo(json.dumps(error.body, indent=2, ensure_ascii=False))
        raise typer.Exit(error.exit_code)
    payload = dict(error.body or {})
    payload.setdefault("schema_version", "2.0")
    payload.setdefault("command", command)
    if not isinstance(payload.get("error"), dict):
        payload["error"] = {
            "code": error.code,
            "message": TEXT["errors"].get(error.code, TEXT["errors"]["http_error"]),
        }
    if error.issues:
        payload["error"]["issues"] = error.issues
    prior = payload.get("next", [])
    if isinstance(prior, str):
        prior = [prior]
    prior_steps = (
        [step for step in prior if isinstance(step, str)] if isinstance(prior, list) else []
    )
    payload["next"] = list(dict.fromkeys([*prior_steps, *error.next]))
    if as_json:
        typer.echo(json.dumps(payload, ensure_ascii=False))
    else:
        typer.echo(payload["error"].get("message") or TEXT["errors"]["http_error"], err=True)
        for issue in error.issues or payload["error"].get("issues", []):
            typer.echo(json.dumps(issue, ensure_ascii=False), err=True)
        typer.echo(TEXT["next_label"], err=True)
        for step in payload["next"]:
            typer.echo(step, err=True)
    raise typer.Exit(error.exit_code)
