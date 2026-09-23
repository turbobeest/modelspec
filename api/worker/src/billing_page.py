"""The page a browser lands on after Stripe Checkout (MODEL-105).

Stripe sends the buyer to `GET /v1/billing/claim?session_id=…`. That answer is
JSON, and an agent keeps getting exactly that JSON. A person in a browser gets
this page instead: the same facts from the same `billing.claim` outcome, and
the key shown once with a plain instruction to copy it now.

Static HTML: no JavaScript, nothing fetched from anywhere, every value escaped.
The key is written into the page and nowhere else; nothing here logs.
"""

from __future__ import annotations

from html import escape
from typing import Any

SITE = "https://modelspec.dev/"
DOCS = "https://modelspec.dev/docs/api"

#: Sent with the page. It holds a secret, so it may load nothing, be framed by
#: nothing, and leak no referrer when the buyer follows a link off it.
HEADERS = {
    "content-security-policy": (
        "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; "
        "form-action 'none'; frame-ancestors 'none'"),
    "referrer-policy": "no-referrer",
    "x-robots-tag": "noindex",
}

_STYLE = (
    ":root{color-scheme:dark light}"
    "body{margin:0;background:#07080a;color:#e6e8eb;"
    "font:16px/1.6 system-ui,-apple-system,Segoe UI,sans-serif}"
    "main{max-width:640px;margin:0 auto;padding:40px 16px}"
    "h1{font-size:24px;margin:0 0 16px}"
    "a{color:#f5b342}"
    "code,.key{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}"
    ".key{display:block;padding:14px;margin:8px 0 12px;background:#13171d;"
    "border:1px solid #f5b342;word-break:break-all;user-select:all;font-size:15px}"
    ".warn{color:#f5b342;font-weight:700}"
    "dl{display:grid;grid-template-columns:max-content 1fr;gap:4px 16px}"
    "dt{color:#9aa3ad}dd{margin:0}"
)


def prefers_html(accept: str | None) -> bool:
    """True only when `Accept` names `text/html` above JSON.

    A browser sends `text/html,…,*/*;q=0.8`. `curl` sends `*/*`, an agent sends
    `application/json` or nothing: all of those keep the JSON. A tie is JSON.
    """
    if not accept:
        return False
    html_q: float | None = None
    json_q: float | None = None
    app_any: float | None = None
    any_any: float | None = None
    for part in accept.split(","):
        pieces = [piece.strip() for piece in part.split(";")]
        media = pieces[0].lower()
        q = 1.0
        for param in pieces[1:]:
            if param.lower().startswith("q="):
                try:
                    q = float(param[2:])
                except ValueError:
                    q = 0.0
        if media == "text/html":
            html_q = q
        elif media == "application/json":
            json_q = q
        elif media == "application/*":
            app_any = q
        elif media == "*/*":
            any_any = q
    if html_q is None or html_q <= 0:
        return False
    for rival in (json_q, app_any, any_any):
        if rival is not None:
            return html_q > rival
    return True


def _e(value: Any) -> str:
    return escape(str(value if value is not None else ""), quote=True)


def _page(title: str, body: str, *, refresh: int | None = None) -> str:
    meta = f'<meta http-equiv="refresh" content="{int(refresh)}">' if refresh else ""
    return (
        "<!doctype html>\n"
        '<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<meta name="robots" content="noindex">'
        f"{meta}<title>{_e(title)} — ModelSpec</title>"
        f"<style>{_STYLE}</style></head>"
        f"<body><main><h1>{_e(title)}</h1>{body}"
        f'<p><a href="{SITE}">Back to modelspec.dev</a> · '
        f'<a href="{DOCS}">API docs</a></p>'
        "</main></body></html>\n"
    )


def _purchase(body: dict[str, Any]) -> str:
    credits = body.get("credits")
    credits_text = f"{credits:,}" if isinstance(credits, int) else _e(credits)
    rows = [
        ("Bought", _e(body.get("plan") or body.get("kind") or "")),
        ("Credits", credits_text),
        ("Tier", _e(body.get("tier") or "")),
        ("Key id", f"<code>{_e(body.get('key_id') or '')}</code>"),
    ]
    listing = "".join(f"<dt>{label}</dt><dd>{value}</dd>" for label, value in rows)
    return (f"<dl>{listing}</dl>"
            f"<p>{_e(body.get('what_you_bought') or '')}</p>")


_USE = (
    "<h2>Using it</h2>"
    "<p>Send the key on every API request as the header "
    "<code>Authorization: Bearer &lt;key&gt;</code>. "
    f'The endpoints and examples are in the <a href="{DOCS}">API docs</a>.</p>'
)


def claim_page(status: int, body: dict[str, Any]) -> str:
    """The HTML for one `billing.claim` outcome: success or refusal."""
    error = body.get("error") if isinstance(body.get("error"), dict) else None
    if error is None and body.get("key"):
        return _page("Payment received: your API key", (
            f"{_purchase(body)}"
            '<p class="warn">Copy it now. It will not be shown again: ModelSpec '
            "keeps no copy of it, and reloading this page will not reveal it.</p>"
            f'<code class="key">{_e(body["key"])}</code>'
            f"{_USE}"))
    if error is None:
        return _page("Payment received", (
            f"{_purchase(body)}"
            f"<p>{_e(body.get('message') or '')}. No new key was issued: "
            "keep using the key you already hold.</p>"
            f"{_USE}"))
    code = str(error.get("code") or "")
    message = _e(error.get("message") or "")
    if code == "claim_not_ready":
        return _page("Payment received: key not ready yet", (
            f"<p>{message}.</p>"
            "<p>This page will reload itself in a few seconds. "
            "If it does not, reload it.</p>"), refresh=5)
    if code == "claim_consumed":
        return _page("This key was already shown", (
            f"<p>{message}</p>"
            "<p>A key is shown once. If you still hold it, you can rotate it "
            "with <code>POST /v1/billing/rotate</code>.</p>"))
    return _page("This purchase could not be claimed", (
        f"<p>{message}</p>"
        f"<p>HTTP {int(status)} · <code>{_e(code)}</code></p>"))
