"""Shared chrome for the public marketing pages."""

from __future__ import annotations


def logo() -> str:
    return """<svg class="mark" viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="3" fill="#0B1426" stroke="#2a3b5c"/><line x1="6.5" y1="3" x2="6.5" y2="37.5" stroke="#F2C94C" stroke-width=".9"/><line x1="3" y1="34" x2="37" y2="34" stroke="#3FB68B" stroke-width="2.2"/><path d="M11 29 16 11 21 23 26 11 31 29" fill="none" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/><g fill="#5AA9EC"><circle cx="11" cy="29" r="1.9"/><circle cx="16" cy="11" r="1.9"/><circle cx="21" cy="23" r="1.9"/><circle cx="26" cy="11" r="1.9"/><circle cx="31" cy="29" r="1.9"/></g></svg>"""


def method_header() -> str:
    return (f'<header class="site-head">{logo()}<a class="wordmark" href="/">'
            '<b>Model</b>Spec</a><nav><a href="/method/" aria-current="page">How it decides</a>'
            '<a href="/#agents">For agents</a><a href="/pricing/">Pricing</a>'
            '<a class="button primary" href="/decide/">Open the board</a></nav></header>')


def footer(*, detail: str = "") -> str:
    return ('<footer class="site-foot"><span>© Sparks and Sawdust LLC</span>'
            '<a href="/method/">How we decide</a><a href="/legal/terms/">Terms</a>'
            '<a href="/legal/privacy/">Privacy</a><a href="/legal/neutrality/">'
            f'Neutrality commitment</a><span class="foot-detail">{detail}</span></footer>')
