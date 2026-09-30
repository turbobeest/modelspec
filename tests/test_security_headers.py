"""The Content-Security-Policy builder (MODEL-238). Tree-level checks live in test_holding."""

from __future__ import annotations

import base64
import hashlib
from pathlib import Path

from pipeline import security_headers


def _tree(tmp_path: Path) -> Path:
    tree = tmp_path / "modelspec"
    tree.mkdir()
    (tree / "index.html").write_text(
        "<html><head><script>var a=1</script>"
        '<script type="application/ld+json">{"a":1}</script></head></html>')
    (tree / "sub").mkdir()
    (tree / "sub" / "index.html").write_text(
        '<script type="module">import "/x.js"</script><script src="/y.js"></script>')
    return tree


def _hash(body: str) -> str:
    return "'sha256-" + base64.b64encode(hashlib.sha256(body.encode()).digest()).decode() + "'"


def test_only_executable_inline_scripts_are_hashed(tmp_path: Path) -> None:
    assert security_headers.inline_script_hashes(_tree(tmp_path)) == sorted(
        [_hash("var a=1"), _hash('import "/x.js"')])


def test_the_policy_allows_exactly_the_named_origins(tmp_path: Path) -> None:
    policy = dict(part.split(" ", 1) for part in security_headers.csp(_tree(tmp_path)).split("; "))

    assert policy["connect-src"] == "'self' https://api.modelspec.dev https://cloudflareinsights.com"
    assert policy["frame-ancestors"] == "'none'"
    assert policy["object-src"] == "'none'"
    assert policy["script-src"].endswith("https://static.cloudflareinsights.com")
    assert "'unsafe-eval'" not in policy["script-src"]
    assert "'unsafe-inline'" not in policy["script-src"]


def test_the_block_sets_the_policy_and_denies_framing(tmp_path: Path) -> None:
    block = security_headers.block(_tree(tmp_path))

    assert block.startswith("/*\n  Content-Security-Policy: default-src 'self'; ")
    assert block.endswith("  X-Frame-Options: DENY\n")

