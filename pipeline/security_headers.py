"""Content-Security-Policy and framing headers for the modelspec.dev trees (MODEL-238).

    security_headers.block(tree)

One `/*` block for a Cloudflare Pages `_headers` file. The policy is written
from the tree it protects: every executable inline `<script>` is allowed by its
SHA-256 hash, so the policy carries no `'unsafe-inline'` for scripts and cannot
drift from the pages. JSON-LD and the JSON data islands are not executed, so
they need no entry.

Third parties, all of them: `static.cloudflareinsights.com` (the analytics
beacon script) and `cloudflareinsights.com` (where it reports), disclosed in the
privacy notice; `api.modelspec.dev` (the decide app and the pricing page call
it). Nothing else may load.
"""

from __future__ import annotations

import base64
import hashlib
import re
from pathlib import Path

API = "https://api.modelspec.dev"
BEACON_SCRIPT = "https://static.cloudflareinsights.com"
BEACON_CONNECT = "https://cloudflareinsights.com"

_INLINE = re.compile(r"<script(?![^>]*\bsrc=)([^>]*)>(.*?)</script>", re.DOTALL | re.IGNORECASE)
_TYPE = re.compile(r"""\btype\s*=\s*["']?([^"'\s>]+)""", re.IGNORECASE)
_EXECUTABLE = {"", "module", "text/javascript", "application/javascript"}


def inline_script_hashes(tree: Path) -> list[str]:
    """`'sha256-...'` sources for each executable inline script in `tree`, sorted."""
    hashes: set[str] = set()
    for page in tree.rglob("*.html"):
        for attrs, body in _INLINE.findall(page.read_text(encoding="utf-8")):
            kind = _TYPE.search(attrs)
            if (kind.group(1).lower() if kind else "") not in _EXECUTABLE:
                continue
            digest = hashlib.sha256(body.encode("utf-8")).digest()
            hashes.add(f"'sha256-{base64.b64encode(digest).decode()}'")
    return sorted(hashes)


def csp(tree: Path) -> str:
    scripts = " ".join(["'self'", *inline_script_hashes(tree), BEACON_SCRIPT])
    return "; ".join([
        "default-src 'self'",
        f"script-src {scripts}",
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data:",
        "font-src 'self'",
        f"connect-src 'self' {API} {BEACON_CONNECT}",
        "object-src 'none'",
        "base-uri 'self'",
        "form-action 'self'",
        "frame-ancestors 'none'",
    ])


def block(tree: Path) -> str:
    return (
        "/*\n"
        f"  Content-Security-Policy: {csp(tree)}\n"
        "  X-Frame-Options: DENY\n"
    )
