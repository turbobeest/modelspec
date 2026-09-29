"""The live modelspec.dev tree: the decide composition production serves.

    python -m pipeline.live build --src dist-v1 --web web/dist --out dist

`pipeline.build` writes the full v1 tree, which `pipeline.holding` derives the
holding tree from. This module derives the live tree from the same build plus
the decide app (`web/dist`). `.github/workflows/deploy-sites.yml` deploys it to
the Pages preview branch `internal` always, and to production when
`SITE_MODE=live`.

**An allowlist.** A page the v1 build still generates (model, provider and
benchmark pages, the wizard, the explorer) is absent here unless this module
names it, so it cannot reappear merely by being generated.

**Discovery is checked, not trusted.** This allowlist used to be `cp` lines in
the workflow. They left out llms.txt, llms-full.txt, index.md and auth.md, so
from the 2026-09-25 flip modelspec.dev answered 404 for all four while
llms.txt, the landing page's `rel="alternate"` link, the MCP card and the
agent skill all pointed at them (MODEL-214). `dead_links` now fails the build
when any file an agent is told to read, or any published page, names a
modelspec.dev path this tree does not publish, and `smoke` fetches each discovery file from the deployed
origin after every deploy.

    python -m pipeline.live smoke --origin https://modelspec.dev
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

from pipeline import brand, landing, social_cards

BASE = "https://modelspec.dev"

#: Copied whole from the v1 build.
KEEP_DIRS = (
    "api", "legal", ".well-known", "method", landing.ASSET_DIR, "pricing",
    "pricing-assets", "fonts", "graph",
)
#: Copied from the v1 build. The discovery files are what MODEL-214 restored.
KEEP_FILES = (
    "index.html", "openapi.yaml",
    "llms.txt", "llms-full.txt", "index.md", "auth.md",
    *brand.FILES,
)
#: The public pages, in sitemap order.
PAGES = (
    "/", "/method/", "/decide/", "/graph/", "/pricing/",
    "/legal/terms/", "/legal/privacy/", "/legal/neutrality/",
)
#: Files an agent is pointed at. Every modelspec.dev link in them must resolve.
DISCOVERY = (
    "llms.txt", "llms-full.txt", "index.md", "auth.md", "robots.txt", "sitemap.xml",
    ".well-known/api-catalog", ".well-known/mcp.json",
    ".well-known/agent-skills/index.json", ".well-known/agent-skills/modelspec/SKILL.md",
)

REDIRECTS = "/landing/  /  301\n"
ROBOTS = f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n"
#: Appended to the v1 build's `_headers` (site/holding/_headers), which carries
#: the discovery `Link` header and the content types of llms.txt, the Markdown
#: twins, the api-catalog and openapi.yaml.
HEADERS = (
    "/api/*\n"
    "  Access-Control-Allow-Origin: *\n"
    "/assets/*\n"
    "  Cache-Control: public, max-age=31536000, immutable\n"
)

_LINK = re.compile(re.escape(BASE) + r"(/[^\s\"'<>)`\]]*)?")
#: A link on a published page, root-relative or absolute on BASE. `//host` is
#: not one. Prose that merely names a URL is not a link.
_HREF = re.compile(r'(?:href|src|content)="(?:' + re.escape(BASE) + r')?(/(?!/)[^"]*)"')
#: Written only by a build on main: the social cards need Chromium
#: (MODELSPEC_RENDER_SOCIAL_CARDS) and the decision snapshot needs the signing
#: keys. A pull request's tree lacks them. The workflow checks the cards exist
#: before it deploys, and the post-deploy smoke reads the snapshot.
MAIN_ONLY = (*(f"/{name}" for name in social_cards.card_filenames()), "/api/decision/")


def sitemap() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{BASE}{path}</loc></url>\n" for path in PAGES)
        + "</urlset>\n"
    )


def build(src: Path, web: Path, out: Path) -> None:
    """Write the live modelspec and benchgraph trees under `out`."""
    real = src / "modelspec"
    if out.exists():
        shutil.rmtree(out)
    tree = out / "modelspec"
    tree.mkdir(parents=True)
    for rel in KEEP_DIRS:
        shutil.copytree(real / rel, tree / rel)
    for rel in KEEP_FILES:
        shutil.copy2(real / rel, tree / rel)
    # Rendered in CI only (MODELSPEC_RENDER_SOCIAL_CARDS); the workflow checks
    # every one is present before it deploys.
    for rel in social_cards.card_filenames():
        if (real / rel).is_file():
            shutil.copy2(real / rel, tree / rel)
    (tree / "decide").mkdir()
    shutil.copy2(web / "decide.html", tree / "decide" / "index.html")
    shutil.copy2(web / "decide.html", tree / "404.html")
    shutil.copytree(web / "assets", tree / "assets",
                    ignore=shutil.ignore_patterns("main-*"))
    (tree / "_redirects").write_text(REDIRECTS, encoding="utf-8")
    (tree / "robots.txt").write_text(ROBOTS, encoding="utf-8")
    (tree / "sitemap.xml").write_text(sitemap(), encoding="utf-8")
    headers = (real / "_headers").read_text(encoding="utf-8")
    (tree / "_headers").write_text(headers.rstrip("\n") + "\n" + HEADERS, encoding="utf-8")
    (out / "benchgraph").mkdir()
    shutil.copy2(src / "benchgraph" / "_redirects", out / "benchgraph" / "_redirects")


def resolves(tree: Path, path: str) -> bool:
    """Whether Pages serves `path` from `tree` as a file rather than the 404."""
    path = path.split("#", 1)[0].split("?", 1)[0] or "/"
    target = tree / path.lstrip("/")
    if path.endswith("/"):
        return (target / "index.html").is_file()
    return target.is_file() or (target / "index.html").is_file()


def dead_links(tree: Path) -> list[str]:
    """Each `file: path` where a discovery file or a published page names a
    modelspec.dev path `tree` lacks."""
    dead: list[str] = []
    for rel in DISCOVERY:
        doc = tree / rel
        if not doc.is_file():
            dead.append(f"{rel}: missing")
            continue
        text = doc.read_text(encoding="utf-8")
        paths = {m.group(1) or "/" for m in _LINK.finditer(text)}
        dead.extend(f"{rel}: {path}" for path in sorted(paths)
                    if "<" not in path and not resolves(tree, path.rstrip(".,;:")))
    headers = tree / "_headers"
    for path in re.findall(r"<(/[^>]*)>", headers.read_text(encoding="utf-8")
                           if headers.is_file() else ""):
        if not resolves(tree, path):
            dead.append(f"_headers: {path}")
    for page in PAGES:
        rel = page.lstrip("/") + "index.html"
        if not (tree / rel).is_file():
            dead.append(f"{rel}: missing")
            continue
        html = (tree / rel).read_text(encoding="utf-8")
        paths = {m.group(1) for m in _HREF.finditer(html)}
        dead.extend(f"{rel}: {path}" for path in sorted(paths)
                    if not resolves(tree, path) and not path.startswith(MAIN_ONLY))
    return dead


def smoke(origin: str, fetch=None) -> list[str]:
    """Each discovery path or page the deployed `origin` does not serve with 200."""
    def get(url: str) -> tuple[int, bytes]:
        request = urllib.request.Request(url, headers={"User-Agent": "modelspec-smoke"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as error:
            return error.code, b""

    fetch = fetch or get
    failed: list[str] = []
    for path in (*(f"/{rel}" for rel in DISCOVERY), "/openapi.yaml", *PAGES):
        status, body = fetch(origin.rstrip("/") + path)
        if status != 200 or not body:
            failed.append(f"{path}: {status}")
    return failed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    sub = parser.add_subparsers(dest="command", required=True)
    make = sub.add_parser("build", help="derive the live trees from a real build")
    make.add_argument("--src", default="dist-v1", help="the real build (default: dist-v1)")
    make.add_argument("--web", default="web/dist", help="the decide app build (default: web/dist)")
    make.add_argument("--out", default="dist", help="output (default: dist)")
    check = sub.add_parser("smoke", help="fetch every discovery file from a deployed origin")
    check.add_argument("--origin", required=True, help="for example https://modelspec.dev")
    args = parser.parse_args(argv)

    if args.command == "smoke":
        failed = smoke(args.origin)
        for line in failed:
            print(f"::error::{args.origin}{line}", file=sys.stderr)
        if not failed:
            print(f"{args.origin}: every discovery file and page answers 200")
        return 1 if failed else 0

    out = Path(args.out).resolve()
    build(Path(args.src).resolve(), Path(args.web).resolve(), out)
    dead = dead_links(out / "modelspec")
    if dead:
        print(f"error: {len(dead)} discovery links do not resolve in the live tree:",
              file=sys.stderr)
        for line in dead[:20]:
            print(f"  {line}", file=sys.stderr)
        return 2
    count = sum(1 for p in (out / "modelspec").rglob("*") if p.is_file())
    print(f"modelspec: {count} files; discovery links resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
