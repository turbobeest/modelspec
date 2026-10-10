"""The thin modelspec-dev client. All decisions come from the hosted API."""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Callable
from importlib.resources import files
from typing import Any

import click
import typer
from jsonschema import Draft202012Validator
from typer.core import TyperCommand, TyperGroup

from . import auth, setup
from .client import Client
from .errors import ClientError, fail, guide_version_notice
from .guidance import BUNDLE, HELP, TEXT, next_steps, orientation, orientation_lines, procurement
from .spec import load_spec, validate_spec


def _json_mode(ctx: click.Context, option: bool = False) -> bool:
    return option or ctx.find_root().meta.get("json_mode", False)


def _usage(ctx: click.Context) -> None:
    fail(
        ClientError(
            "usage_error", extra_next=[TEXT["command_help"].format(command=ctx.command_path)]
        ),
        command=ctx.command_path,
        as_json=_json_mode(ctx),
    )


class RecoveryCommand(TyperCommand):
    def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
        try:
            return super().parse_args(ctx, args)
        except Exception as error:
            if getattr(error, "exit_code", None) == 2:
                _usage(ctx)
            raise

    def invoke(self, ctx: click.Context) -> Any:
        try:
            return super().invoke(ctx)
        except ClientError as error:
            fail(error, command=ctx.command_path, as_json=_json_mode(ctx))
        except (click.Abort, typer.Abort, KeyboardInterrupt, EOFError):
            fail(ClientError("interrupted"), command=ctx.command_path, as_json=_json_mode(ctx))
        except Exception as error:
            if getattr(error, "exit_code", None) == 2:
                _usage(ctx)
            raise


class RecoveryGroup(TyperGroup):
    def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
        ctx.find_root().meta["json_mode"] = _json_mode(ctx) or "--json" in args
        try:
            return super().parse_args(ctx, args)
        except Exception as error:
            if getattr(error, "exit_code", None) == 2:
                _usage(ctx)
            raise

    def resolve_command(self, ctx: click.Context, args: list[str]) -> Any:
        try:
            return super().resolve_command(ctx, args)
        except Exception as error:
            if getattr(error, "exit_code", None) == 2:
                _usage(ctx)
            raise

    def invoke(self, ctx: click.Context) -> Any:
        try:
            return super().invoke(ctx)
        except ClientError as error:
            fail(error, command=ctx.command_path, as_json=_json_mode(ctx))
        except (click.Abort, typer.Abort, KeyboardInterrupt, EOFError):
            fail(ClientError("interrupted"), command=ctx.command_path, as_json=_json_mode(ctx))


app = typer.Typer(
    name="modelspec",
    cls=RecoveryGroup,
    help=HELP["root"],
    invoke_without_command=True,
    no_args_is_help=False,
    add_completion=False,
)
help_app = typer.Typer(cls=RecoveryGroup, help=HELP["agent"], invoke_without_command=True)
setup_app = typer.Typer(cls=RecoveryGroup, help=HELP["setup"])
auth_app = typer.Typer(cls=RecoveryGroup, help=HELP["auth"])
app.add_typer(help_app, name="help")
app.add_typer(setup_app, name="setup")
app.add_typer(auth_app, name="auth")


def _orientation(ctx: click.Context, as_json: bool) -> None:
    typer.echo(
        json.dumps(orientation(), ensure_ascii=False)
        if _json_mode(ctx, as_json)
        else "\n".join(orientation_lines())
    )


@app.callback()
def root(
    ctx: typer.Context,
    as_json: bool = typer.Option(False, "--json", help=HELP["json"]),
    version: bool = typer.Option(False, "--version", help=HELP["version"]),
) -> None:
    if version:
        data = {"cli_version": BUNDLE["cli_version"], "guide_version": BUNDLE["guide_version"]}
        typer.echo(
            json.dumps(data)
            if _json_mode(ctx, as_json)
            else f"modelspec-dev {data['cli_version']}\n"
            + TEXT["guide_version"].format(version=data["guide_version"])
        )
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        _orientation(ctx, as_json)


@help_app.callback()
def help_root(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        _orientation(ctx, False)


@help_app.command("agent", cls=RecoveryCommand, help=HELP["agent"])
def help_agent(
    ctx: typer.Context, as_json: bool = typer.Option(False, "--json", help=HELP["json"])
) -> None:
    _orientation(ctx, as_json)


@app.command("key", cls=RecoveryCommand, help=HELP["key"])
def key(
    ctx: typer.Context, as_json: bool = typer.Option(False, "--json", help=HELP["json"])
) -> None:
    data = procurement()
    typer.echo(
        json.dumps(data, ensure_ascii=False)
        if _json_mode(ctx, as_json)
        else "\n".join(
            (
                data["price"],
                data["how"],
                TEXT["human_label"].format(message=data["tell_the_human"]),
                TEXT["next_label"],
                *data["next"],
            )
        )
    )


@auth_app.command("set", cls=RecoveryCommand, help=HELP["auth"])
def auth_set(
    ctx: typer.Context,
    stdin: bool = typer.Option(False, "--stdin", help=HELP["stdin"]),
    as_json: bool = typer.Option(False, "--json", help=HELP["json"]),
) -> None:
    value = (
        sys.stdin.read(4098)
        if stdin
        else typer.prompt(TEXT["key_prompt"], hide_input=True, err=True)
    )
    path = auth.store_key(value)
    message = TEXT["key_saved"].format(path=path)
    typer.echo(
        json.dumps(
            {
                "stored": True,
                "path": str(path),
                "message": message,
                "next": [TEXT["orientation_next"][-1]],
            }
        )
        if _json_mode(ctx, as_json)
        else message
    )


@setup_app.command("mcp", cls=RecoveryCommand, help=HELP["setup"])
def setup_mcp(
    ctx: typer.Context,
    client: str = typer.Option(..., "--client", help=HELP["client"]),
    config: str | None = typer.Option(None, "--config", help=HELP["config"]),
    write: bool = typer.Option(False, "--write", help=HELP["write"]),
    yes: bool = typer.Option(False, "--yes", help=HELP["yes"]),
    as_json: bool = typer.Option(False, "--json", help=HELP["json"]),
) -> None:
    data, text = setup.prepare(client, config)
    if write:
        data.update(setup.write(client, config, yes=yes, as_json=_json_mode(ctx, as_json)))
        text += "\n" + data["message"]
    typer.echo(json.dumps(data, ensure_ascii=False) if _json_mode(ctx, as_json) else text)


def _response(
    ctx: click.Context,
    client: Client,
    response: Any,
    as_json: bool,
    *,
    human_renderer: Callable[[dict[str, Any]], str] | None = None,
) -> None:
    if client.guide_changed:
        guide_version_notice(_json_mode(ctx, as_json))
    if _json_mode(ctx, as_json):
        typer.echo(response.text, nl=False)
    else:
        body = response.json()
        if human_renderer is None:
            typer.echo(json.dumps(body, indent=2, ensure_ascii=False))
            return
        try:
            text = human_renderer(body)
        except (KeyError, TypeError, AttributeError, ValueError, IndexError):
            raise ClientError("unexpected_response", recovery="network") from None
        typer.echo(text)


def _spec_body(client: Client, spec: str | None, template: str | None) -> dict[str, Any]:
    if (spec is None) == (template is None):
        raise ClientError("spec_source", recovery="spec")
    if spec is not None:
        body = load_spec(spec)
    else:
        response = client.request(
            "GET",
            "/v1/vocabulary",
            params={"section": "templates", "id": template, "detail": "full"},
        )
        try:
            rows = response.json().get("templates", [])
            if not isinstance(rows, list):
                raise ClientError("unexpected_response", recovery="network")
            row = next(
                (item for item in rows if isinstance(item, dict) and item.get("id") == template),
                None,
            )
            if row is None or not isinstance(row.get("spec"), dict):
                raise ClientError("unknown_template", recovery="spec")
            body = row["spec"]
            validate_spec(body)
        except ClientError as error:
            if client.guide_changed:
                error.next.extend(next_steps("upgrade"))
            raise
    return body


@app.command("decide", cls=RecoveryCommand, help=HELP["decide"])
def decide(
    ctx: typer.Context,
    spec: str | None = typer.Option(None, "--spec", help=HELP["spec"]),
    template: str | None = typer.Option(None, "--template", help=HELP["template"]),
    as_json: bool = typer.Option(False, "--json", help=HELP["json"]),
) -> None:
    client = Client(auth.require_key())
    body = _spec_body(client, spec, template)
    _response(ctx, client, client.request("POST", "/v1/decide", body=body), as_json)


def _comparison_value(value: dict[str, Any]) -> str:
    copy = TEXT["comparison"]
    shown = (
        copy["unknown"]
        if value.get("value") is None
        else json.dumps(value["value"], ensure_ascii=False)
    )
    if value.get("unit"):
        shown = copy["unit"].format(value=shown, unit=value["unit"])
    if value.get("interval") is not None:
        shown = copy["interval"].format(value=shown, interval=json.dumps(value["interval"]))
    if value.get("records"):
        shown = copy["records"].format(value=shown, records=", ".join(value["records"]))
    return shown


def _comparison_offering(offering: dict[str, Any]) -> str:
    copy = TEXT["comparison"]
    details = ", ".join(
        f"{name}={offering[name]}"
        for name in ("provider", "region", "tier")
        if offering.get(name) is not None
    )
    return copy["offering_ref"].format(
        model=offering.get("model", copy["unknown"]),
        details=copy["offering_details"].format(details=details) if details else "",
    )


def _comparison_text(body: dict[str, Any]) -> str:
    copy = TEXT["comparison"]
    result = body["result"]
    snapshots, status = result["snapshot"], result["status"]
    lines = [
        copy["header"].format(
            old=snapshots["old"]["id"],
            new=snapshots["new"]["id"],
            old_status=status["old"],
            new_status=status["new"],
        ),
        copy["counts"].format(**result["counts"]),
    ]
    for model in result["models"]:
        if model.get("entered"):
            kind = "entered"
        elif model.get("left"):
            kind = "departed"
        else:
            kind = "changed"
        lines.extend(["", copy["model"].format(model=model["model"], kind=copy[kind])])
        if model.get("left"):
            lines.append(
                copy["reason"].format(reason=model["left"].get("reason", copy["unknown"]))
            )
        if model.get("rank_changed"):
            lines.append(copy["rank"].format(**model["rank_changed"]))
        if model.get("may_qualify"):
            lines.append(
                copy["may_qualify"].format(**{
                    side: ", ".join(model["may_qualify"].get(side) or []) or copy["none"]
                    for side in ("old", "new")
                })
            )
        for change in model.get("values") or []:
            name = change.get("kind", copy["unknown"])
            if name == "facet":
                name = change.get("facet", name)
            elif name == "capability":
                name = copy["capability"].format(domain=change.get("domain", copy["unknown"]))
            lines.append(
                copy["value"].format(
                    name=name,
                    old=_comparison_value(change.get("old") or {}),
                    new=_comparison_value(change.get("new") or {}),
                )
            )
            offering = change.get("offering")
            if offering:
                if "old" in offering and "new" in offering:
                    lines.append(
                        copy["offering_change"].format(
                            old=_comparison_offering(offering["old"]),
                            new=_comparison_offering(offering["new"]),
                        )
                    )
                else:
                    lines.append(copy["offering"].format(offering=_comparison_offering(offering)))
    if not result["changed"]:
        lines.append(copy["unchanged"])
    return "\n".join(lines)


@app.command("compare", cls=RecoveryCommand, help=HELP["compare"])
def compare(
    ctx: typer.Context,
    spec: str | None = typer.Option(None, "--spec", help=HELP["spec"]),
    template: str | None = typer.Option(None, "--template", help=HELP["template"]),
    to: str = typer.Option(..., "--to", help=HELP["to"]),
    as_json: bool = typer.Option(False, "--json", help=HELP["json"]),
) -> None:
    client = Client(auth.require_key())
    if re.fullmatch(r"snap_[A-Za-z0-9:._-]+", to) is None:
        raise ClientError("invalid_compare_to", extra_next=[TEXT["compare_to_next"]])
    body = {"compare_to": to, "spec": _spec_body(client, spec, template)}
    _response(
        ctx,
        client,
        client.request("POST", "/v1/compare", body=body),
        as_json,
        human_renderer=_comparison_text,
    )


@app.command("vocab", cls=RecoveryCommand, help=HELP["vocab"])
def vocab(
    ctx: typer.Context,
    section: str | None = typer.Argument(None, help=HELP["section"]),
    section_option: str | None = typer.Option(None, "--section", help=HELP["section"]),
    search: str | None = typer.Option(None, "--search", help=HELP["search"]),
    id_: str | None = typer.Option(None, "--id", help=HELP["id"]),
    ids: list[str] | None = typer.Option(None, "--ids", help=HELP["ids"]),
    detail: str | None = typer.Option(None, "--detail", help=HELP["detail"]),
    offset: int | None = typer.Option(None, "--offset", help=HELP["offset"]),
    limit: int | None = typer.Option(None, "--limit", help=HELP["limit"]),
    as_json: bool = typer.Option(False, "--json", help=HELP["json"]),
) -> None:
    client = Client(auth.require_key())
    ids = [part for value in ids or [] for part in value.split(",")]
    if (
        (section is not None and section_option is not None)
        or len(ids) > 100
        or detail not in (None, "compact", "full")
        or (offset is not None and offset < 0)
        or (limit is not None and not 1 <= limit <= 20)
    ):
        raise ClientError("invalid_vocabulary", recovery="spec")
    params = {"section": section or section_option or "starter"}
    params.update(
        {
            key: value
            for key, value in (
                ("search", search),
                ("id", id_),
                ("ids", ",".join(ids) if ids else None),
                ("detail", detail),
                ("offset", offset),
                ("limit", limit),
            )
            if value is not None
        }
    )
    _response(ctx, client, client.request("GET", "/v1/vocabulary", params=params), as_json)


@app.command("feedback", cls=RecoveryCommand, help=HELP["feedback"])
def feedback(
    ctx: typer.Context,
    decision_id: str | None = typer.Argument(None, help=HELP["decision_id"]),
    rating: str = typer.Option(..., "--rating", help=HELP["rating"]),
    note: str | None = typer.Option(None, "--note", help=HELP["note"]),
    trying_to_decide: str | None = typer.Option(None, "--trying-to-decide", help=HELP["trying"]),
    template: str | None = typer.Option(None, "--template", help=HELP["feedback_template"]),
    as_json: bool = typer.Option(False, "--json", help=HELP["json"]),
) -> None:
    client = Client(auth.require_key())
    body = {"rating": rating, "client": "cli"}
    body.update(
        {
            key: value
            for key, value in (
                ("decision_id", decision_id),
                ("note", note),
                ("trying_to_decide", trying_to_decide),
                ("template", template),
            )
            if value is not None
        }
    )
    schema = json.loads(
        files(__package__).joinpath("feedback.schema.json").read_text(encoding="utf-8")
    )
    if list(Draft202012Validator(schema).iter_errors(body)):
        raise ClientError("invalid_feedback", recovery="usage")
    _response(
        ctx, client, client.request("POST", "/v1/feedback", body=body, feedback=True), as_json
    )


if __name__ == "__main__":
    app()
