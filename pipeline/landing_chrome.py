"""Shared chrome for the public pages: the brand lockup, the method header, the footer."""

from __future__ import annotations

import html

#: The lockup's scale on every page, and the one place to change it (MODEL-213).
#: It sets size and weight only; each page keeps its own wordmark font. The
#: graph explorer and the decide app are built without the pipeline, so they
#: copy it verbatim, and `tests/test_lockup.py` fails if a copy drifts.
LOCKUP_CSS = (
    ".lockup{display:inline-flex;align-items:center;gap:12px;flex:none;"
    "color:inherit;text-decoration:none}.lockup:hover{color:inherit}"
    ".lockup .mark{width:48px;height:48px;flex:none}"
    ".lockup .wordmark{font-size:30px;font-weight:400;line-height:1;letter-spacing:-.02em}"
    ".lockup .wordmark b{font-weight:700}"
    "@media (max-width:899px){.lockup{gap:10px}.lockup .mark{width:38px;height:38px}"
    ".lockup .wordmark{font-size:24px}}"
)


def logo() -> str:
    return """<svg class="mark" viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="3" fill="#0B1426" stroke="#2a3b5c"/><line x1="6.5" y1="3" x2="6.5" y2="37.5" stroke="#F2C94C" stroke-width=".9"/><line x1="3" y1="34" x2="37" y2="34" stroke="#3FB68B" stroke-width="2.2"/><path d="M11 29 16 11 21 23 26 11 31 29" fill="none" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/><g fill="#5AA9EC"><circle cx="11" cy="29" r="1.9"/><circle cx="16" cy="11" r="1.9"/><circle cx="21" cy="23" r="1.9"/><circle cx="26" cy="11" r="1.9"/><circle cx="31" cy="29" r="1.9"/></g></svg>"""


def lockup_style() -> str:
    return f"<style>{LOCKUP_CSS}</style>"


def lockup(*, href: str | None = "/") -> str:
    """The mark and the ModelSpec title as one unit. `href=None` is not a link."""
    inner = f'{logo()}<span class="wordmark"><b>Model</b>Spec</span>'
    if href is None:
        return f'<span class="lockup">{inner}</span>'
    return f'<a class="lockup" href="{href}">{inner}</a>'


def site_header(*, current: str | None = None) -> str:
    """The public-page header. `current` is the href that is this page."""
    def item(href: str, label: str, *, class_name: str = "") -> str:
        classes = f' class="{class_name}"' if class_name else ""
        mark = ' aria-current="page"' if href == current else ""
        return f'<a href="{href}"{classes}{mark}>{label}</a>'

    return (f'<header class="site-head">{lockup()}<nav>'
            f'{item("/about/", "About")}'
            f'{item("/method/", "How it decides")}'
            f'{item("/#agents", "For agents")}'
            f'{item("/pricing/", "Pricing")}'
            f'{item("/decide/details/", "Open the board", class_name="button primary")}'
            "</nav></header>")


def method_header() -> str:
    return site_header(current="/method/")


def legal_footer_links(*, base: str = "",
                       neutrality_label: str = "Neutrality commitment") -> tuple[str, ...]:
    from pipeline.legal import DOCS

    order = {"terms": 0, "privacy": 1, "neutrality": 2, "dmca": 3}
    docs = sorted(DOCS, key=lambda doc: order.get(doc.slug, len(order)))
    return tuple(
        f'<a href="{html.escape(base + doc.url_path)}">'
        f'{html.escape(neutrality_label if doc.slug == "neutrality" else doc.nav_label)}</a>'
        for doc in docs if doc.in_footer
    )


def footer(*, detail: str = "") -> str:
    return ('<footer class="site-foot"><span>© Sparks &amp; Sawdust LLC</span>'
            f'<a href="/method/">How we decide</a>{"".join(legal_footer_links())}'
            f'<a href="/brand/">Brand</a><span class="foot-detail">{detail}</span></footer>')
