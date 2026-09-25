"""Holding mode: the product pages dark, the data still up (Jamie, 2026-09-24).

    python -m pipeline.holding build --src dist --out dist-holding
    python -m pipeline.holding mode        # prints `live` or `holding`

`pipeline.build` always builds the real site. This module derives the modelspec
holding tree from it, and copies `dist/benchgraph` unchanged.
`.github/workflows/deploy-sites.yml` decides which tree goes to production:

* `SITE_MODE` holding (unset, empty, or anything but the exact string `live`):
  the real modelspec site goes to the Pages preview branch `internal`, for
  testing, and the modelspec holding tree goes to `main`, which serves
  modelspec.dev. benchgraph.dev gets the same `_redirects` file either way.
* `SITE_MODE=live`: the real modelspec site goes to production as well.
  benchgraph.dev still gets that same `_redirects` file.

A missing variable therefore fails closed: no merge can bring the old site back
by accident.

What the modelspec holding tree is, and why:

* **Copied, not rebuilt.** `/api/**`, `/legal/**` and `openapi.yaml` are copied
  byte for byte from the real build, so what the CLI (`modelspec snapshot
  fetch`), DPF, the rank Worker and the MCP server read is exactly what the
  real site would publish. The legal pages stay reachable because Stripe's
  account review and past purchasers rely on them.
* **An allowlist.** Nothing else of the real build is kept but the fonts the
  legal pages load and the favicons. A page added to the real site later is
  dark in holding mode without anyone remembering to add it here.
* **A 404, not a redirect.** Every other path (model and benchmark pages, the
  wizard, the explorer, /pricing, llms.txt, the Markdown twins, .well-known)
  is absent, and Pages answers a missing path with `404.html`, which is the
  holding page. A `_redirects` splat on this host would also catch `/api/*`,
  because Pages applies redirects before it looks for a file.
* **No Pages Function.** No `_worker.js`, `functions/` or `_routes.json`, so no
  code runs in front of the files and nothing negotiates Markdown.
* **noindex, still crawlable.** `X-Robots-Tag: noindex` on every response and a
  robots meta tag on the page, with no `Link` header advertising llms.txt or a
  sitemap. robots.txt allows everything, since a crawler barred from a page
  never reads its noindex, and names no sitemap.

benchgraph.dev (MODEL-126) is not a holding tree. `pipeline.build` publishes
one `_redirects` file there, and this module copies those bytes into
`dist-holding/benchgraph`. A holding page on that host would publish no
`/api/`, so `benchgraph.dev/api/*` would stop answering. The redirect sends
pages to modelspec.dev's holding 404, and `/api/*` to the `/api/**` this
module copies onto modelspec.dev.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

MODE_ENV = "SITE_MODE"
LIVE = "live"
HOLDING = "holding"

SITES = {"modelspec": "ModelSpec"}

#: What is copied from the real build, byte for byte. Directories whole.
#: modelspec only. benchgraph.dev is one redirect file, copied unchanged.
KEEP_DIRS = {"modelspec": ("api", "legal", "fonts")}
KEEP_FILES = ("openapi.yaml", "favicon.ico", "favicon-64.png", "apple-touch-icon.png",
              "icon-512.png", "icon.svg")
#: What this module writes itself.
WRITTEN = ("index.html", "404.html", "_headers", "robots.txt")

LINE = "{site} is in preparation. Check back soon."
OPERATOR = "Sparks and Sawdust LLC"
#: modelspec.dev only: benchgraph.dev has no legal pages of its own.
LEGAL_LINKS = (("Terms", "/legal/terms/"), ("Privacy", "/legal/privacy/"))

HEADERS = (
    "/*\n"
    "  X-Robots-Tag: noindex\n"
    "  X-Content-Type-Options: nosniff\n"
    "  Strict-Transport-Security: max-age=63072000; includeSubDomains; preload\n"
    "/openapi.yaml\n"
    "  Content-Type: application/yaml\n"
    "/favicon.ico\n"
    "  Content-Type: image/x-icon\n"
)

ROBOTS = "User-agent: *\nAllow: /\n"

_STYLE = (
    ":root{--bg:#fafaf8;--fg:#1b1b19;--mute:#6b6b66}"
    "@media (prefers-color-scheme:dark){:root{--bg:#141413;--fg:#ecebe6;--mute:#9a9992}}\n"
    "body{margin:0;min-height:100vh;display:grid;place-items:center;background:var(--bg);"
    "color:var(--fg);font:16px/1.5 system-ui,-apple-system,sans-serif;padding:0 16px}\n"
    "main{max-width:32rem;text-align:center}h1{font-size:1.75rem;margin:0 0 .5rem}"
    "p{margin:.25rem 0;color:var(--mute)}a{color:inherit}.l{margin-top:2rem;font-size:.85rem}"
)


def resolve_mode(raw: str | None) -> str:
    """`live` only for the exact string `live`. Anything else is holding."""
    return LIVE if raw == LIVE else HOLDING


def page(site: str) -> str:
    """The holding page: the name, one line, and the operator. No numbers.

    The same bytes are `/` (200) and `404.html` (every other path, 404). No
    canonical, since no URL showing this should be indexed.
    """
    line = LINE.format(site=site)
    footer = ""
    if site == SITES["modelspec"]:
        footer = '<p class="l">' + " · ".join(
            f'<a href="{href}">{label}</a>' for label, href in LEGAL_LINKS) + "</p>"
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        f'<meta name="robots" content="noindex"><title>{site}</title>'
        '<link rel="icon" href="/favicon.ico">\n'
        f"<style>{_STYLE}</style></head>\n"
        f"<body><main><h1>{site}</h1><p>{line}</p>{footer}"
        f'<p class="l">© {OPERATOR}</p></main></body></html>\n'
    )


def require_benchgraph_redirect(real: Path) -> None:
    """Fail unless `real` is the one `_redirects` file with the two rules.

    benchgraph.dev has no pages and no `/api/` of its own. Anything else in
    this directory means the build and the redirect contract have drifted.
    """
    if not real.is_dir():
        raise FileNotFoundError(f"{real} is missing; run pipeline.build first")
    entries = sorted(path.relative_to(real).as_posix() for path in real.rglob("*"))
    redirect = real / "_redirects"
    if entries != ["_redirects"] or not redirect.is_file():
        raise ValueError(f"{real} must be exactly _redirects, found {entries}")
    from pipeline.build import BENCHGRAPH_REDIRECTS
    text = redirect.read_text(encoding="utf-8")
    if text != BENCHGRAPH_REDIRECTS:
        raise ValueError(f"{redirect} is not the two benchgraph redirect rules")


def build(src: Path, out: Path) -> dict[str, list[str]]:
    """Write the modelspec holding tree under `out`, and copy the benchgraph redirect."""
    require_benchgraph_redirect(src / "benchgraph")
    if out.exists():
        shutil.rmtree(out)
    kept: dict[str, list[str]] = {}
    for name, site in SITES.items():
        real, tree = src / name, out / name
        if not (real / "index.html").is_file():
            raise FileNotFoundError(f"{real} is not a built site; run pipeline.build first")
        tree.mkdir(parents=True)
        kept[name] = []
        for rel in KEEP_DIRS[name]:
            if not (real / rel).is_dir():
                raise FileNotFoundError(f"{real / rel} is missing; it must stay published")
            shutil.copytree(real / rel, tree / rel)
            kept[name].append(rel + "/")
        for rel in KEEP_FILES:
            if (real / rel).is_file():
                shutil.copy2(real / rel, tree / rel)
                kept[name].append(rel)
        html = page(site)
        (tree / "index.html").write_text(html, encoding="utf-8")
        (tree / "404.html").write_text(html, encoding="utf-8")
        (tree / "_headers").write_text(HEADERS, encoding="utf-8")
        (tree / "robots.txt").write_text(ROBOTS, encoding="utf-8")
    shutil.copytree(src / "benchgraph", out / "benchgraph")
    return kept


def violations(tree: Path, name: str) -> list[str]:
    """What a holding tree must not contain. Empty means it is dark."""
    bad: list[str] = []
    for path in sorted(tree.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(tree).as_posix()
        top = rel.split("/", 1)[0]
        if "/" in rel:
            if top not in KEEP_DIRS[name]:
                bad.append(f"{rel}: outside the kept directories")
            elif (top == "api" and path.suffix != ".json"
                  and rel != "api/decision/snapshot.json.gz"):
                bad.append(f"{rel}: /api/ holds JSON only")
            elif top == "legal" and path.name != "index.html":
                bad.append(f"{rel}: /legal/ holds its pages only")
            elif top == "fonts" and path.suffix not in {".woff2", ".txt"}:
                bad.append(f"{rel}: /fonts/ holds faces and their licences only")
        elif rel not in KEEP_FILES and rel not in WRITTEN:
            bad.append(f"{rel}: not a holding file")
    for rel in ("index.html", "404.html"):
        if not (tree / rel).is_file() or 'content="noindex"' not in (tree / rel).read_text(
                encoding="utf-8"):
            bad.append(f"{rel}: missing, or not noindex")
    headers = (tree / "_headers").read_text(encoding="utf-8") if (tree / "_headers").is_file() else ""
    if "X-Robots-Tag: noindex" not in headers or "Link:" in headers:
        bad.append("_headers: must noindex everything and advertise nothing")
    if "Sitemap" in ((tree / "robots.txt").read_text(encoding="utf-8")
                     if (tree / "robots.txt").is_file() else "Sitemap"):
        bad.append("robots.txt: missing, or names a sitemap")
    return bad


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    sub = parser.add_subparsers(dest="command", required=True)
    make = sub.add_parser("build", help="derive the holding trees from a real build")
    make.add_argument("--src", default="dist", help="the real build (default: dist)")
    make.add_argument("--out", default="dist-holding", help="output (default: dist-holding)")
    sub.add_parser("mode", help=f"print the site mode that ${MODE_ENV} resolves to")
    args = parser.parse_args(argv)

    if args.command == "mode":
        print(resolve_mode(os.environ.get(MODE_ENV)))
        return 0
    src, out = Path(args.src).resolve(), Path(args.out).resolve()
    kept = build(src, out)
    for name in SITES:
        bad = violations(out / name, name)
        if bad:
            print(f"error: the {name} holding tree is not dark:", file=sys.stderr)
            for line in bad[:20]:
                print(f"  {line}", file=sys.stderr)
            return 2
    for name, items in kept.items():
        print(f"{name}: kept {', '.join(items)}; wrote {', '.join(WRITTEN)}")
    print("benchgraph: copied _redirects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
