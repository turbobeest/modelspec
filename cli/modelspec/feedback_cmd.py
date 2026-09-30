"""``modelspec feedback``: tell ModelSpec whether an answer held up (MODEL-221).

Sends one rating to ``POST https://api.modelspec.dev/v1/feedback``. No key is
needed and none is sent: this command never reads ``MODELSPEC_API_KEY``. The
body is printed before it is sent, and ``--dry-run`` prints it without sending.
"""

from __future__ import annotations

import json
from typing import Any, Optional

import typer

from . import outcome

EXIT_ERROR = 1
ENDPOINT = "https://api.modelspec.dev/v1/feedback"
RATINGS = ("reliable", "unreliable", "trustworthy", "untrustworthy", "confusing")
TIMEOUT_SECONDS = 15.0

#: Tests replace this with an `httpx.MockTransport`; `None` is the network.
_transport: Any = None


def _fail(code: str, message: str, as_json: bool) -> None:
    if as_json:
        typer.echo(json.dumps({"command": "feedback",
                               "error": {"code": code, "message": message}}, indent=2), err=True)
    else:
        typer.echo(f"error: {message}", err=True)
    raise typer.Exit(EXIT_ERROR)


def feedback(
    decision_id: Optional[str] = typer.Argument(
        None, help="The decision_id of the answer this is about (dec_…). Optional."),
    rating: str = typer.Option(
        ..., "--rating", "-r",
        help="One of: reliable, unreliable, trustworthy, untrustworthy, confusing."),
    note: Optional[str] = typer.Option(
        None, "--note", "-m",
        help="Optional. What was wrong or right. Never a prompt, a key or personal details."),
    trying_to_decide: Optional[str] = typer.Option(
        None, "--trying-to-decide", help="Optional. What you were trying to decide."),
    template: Optional[str] = typer.Option(
        None, "--template", help="Optional. The decision template you used."),
    endpoint: str = typer.Option(
        ENDPOINT, "--endpoint", help="Where to send it. Change it only to test a local Worker."),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Print the exact body and send nothing."),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Rate an answer: reliable, unreliable, trustworthy, untrustworthy or confusing. No key.

    Send one after you act on an answer, with its decision_id.

    Example: modelspec feedback dec_3f9a1c2b7d4e --rating unreliable --note "no EU region"
    """
    if rating not in RATINGS:
        _fail("invalid_request", f"--rating must be one of {', '.join(RATINGS)}", as_json)
    body: dict[str, Any] = {"rating": rating, "client": "cli"}
    for name, value in (("decision_id", decision_id), ("note", note),
                        ("trying_to_decide", trying_to_decide), ("template", template)):
        if value is not None and value.strip():
            body[name] = value.strip()

    if dry_run:
        typer.echo(json.dumps({"command": "feedback", "dry_run": True, "endpoint": endpoint,
                               "body": body}, indent=2))
        return
    if not as_json:
        typer.echo(f"Sending to {endpoint}: {json.dumps(body)}", err=True)

    import httpx

    version = outcome.cli_version() or "dev"
    try:
        with httpx.Client(timeout=TIMEOUT_SECONDS, transport=_transport, follow_redirects=False,
                          headers={"user-agent": f"modelspec-cli/{version}"}) as client:
            response = client.post(endpoint, json=body)
    except httpx.HTTPError as exc:
        _fail("origin_unreachable", f"could not reach {endpoint}: {type(exc).__name__}", as_json)
    try:
        payload = response.json()
    except ValueError:
        _fail("unexpected_response", f"{endpoint} answered HTTP {response.status_code} "
                                     "with a body that is not JSON", as_json)
    if response.status_code >= 400:
        error = payload.get("error") if isinstance(payload, dict) else None
        code = error.get("code") if isinstance(error, dict) else "unexpected_response"
        message = error.get("message") if isinstance(error, dict) else f"HTTP {response.status_code}"
        _fail(str(code), str(message), as_json)

    if as_json:
        typer.echo(json.dumps({"command": "feedback", "result": payload}, indent=2))
        return
    if payload.get("status") == "recorded":
        typer.echo("Thank you. Your feedback was recorded.")
        typer.echo(f"Receipt (keep it to delete this later): {payload.get('receipt')}")
    else:
        typer.echo(payload.get("message") or "Thank you. Nothing was kept.")
    if payload.get("redacted"):
        typer.echo("Removed before storage: " + ", ".join(payload["redacted"]))
