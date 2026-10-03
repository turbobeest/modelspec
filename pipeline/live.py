"""The live modelspec.dev tree: the decide composition production serves.

    python -m pipeline.live build --src dist-v1 --web web/dist --out dist

`pipeline.build` writes the full v1 tree, which `pipeline.holding` derives the
holding tree from. This module derives the live tree from the same build plus
the decide app (`web/dist`). `.github/workflows/deploy-sites.yml` deploys it to
the Pages preview branch `internal` always, and to production when
`SITE_MODE=live`.

**An allowlist.** A page the v1 build still generates (model, provider and
benchmark pages, the wizard) is absent here unless this module
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
import html
import os
import subprocess
import re
import shutil
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

from pipeline import (agent_ready, brand, entity, landing, landing_chrome, public_data, security_headers,
                      social_cards, structured_data)

BASE = "https://modelspec.dev"

#: Copied whole from the v1 build.
KEEP_DIRS = (
    "api", "legal", ".well-known", "method", landing.ASSET_DIR, "pricing",
    "pricing-assets", "fonts",
    # MODEL-221: the feedback page, and the control every page loads.
    "feedback", "feedback-assets",
    # MODEL-299: the press and brand kit.
    "brand",
)
#: Copied from the v1 build. The discovery files are what MODEL-214 restored.
KEEP_FILES = (
    "index.html", "openapi.yaml",
    "llms.txt", "index.md", "auth.md", "agents.md",
    *brand.FILES,
)
#: The public pages, in sitemap order.
PAGES = (
    "/", "/method/", "/decide/", "/pricing/", "/feedback/", "/brand/",
    "/legal/terms/", "/legal/privacy/", "/legal/neutrality/",
)
#: Files an agent is pointed at. Every modelspec.dev link in them must resolve.
DISCOVERY = (
    "llms.txt", "index.md", "auth.md", "agents.md", "robots.txt", "sitemap.xml",
    ".well-known/api-catalog", ".well-known/mcp.json",
    ".well-known/agent-skills/index.json", ".well-known/agent-skills/modelspec/SKILL.md",
)

#: The v1 site's URLs. Each answered 404 with the decide app for a body until
#: these rules (MODEL-238). Never a rule on /api/*.
LEGACY = (
    "/downselect", "/models", "/providers", "/benchmarks",
    "/m/*", "/p/*", "/b/*",
)
#: Retired by MODEL-251: the 3D graph explorer and the catalogue digest.
#: Old links land on the home page and on llms.txt instead of a 404.
RETIRED = (
    "/graph  /  301\n",
    "/graph/  /  301\n",
    "/graph/*  /  301\n",
    "/llms-full.txt  /llms.txt  301\n",
)
REDIRECTS = "/landing/  /  301\n" + "".join(
    f"{rule}{suffix}  /decide/  301\n"
    for rule in LEGACY
    for suffix in (("",) if rule.endswith("*") else ("", "/"))
) + "".join(RETIRED)
#: The one robots.txt (MODEL-253): agent_ready's, with the Content-Signal line.
#: Until then this module wrote a plain copy last, and production served it.
ROBOTS = agent_ready.robots_txt(BASE)
REPO_ROOT = Path(__file__).resolve().parents[1]
#: What each public page is made from, for its sitemap <lastmod>: the date of the
#: last commit that touched any of these, not the build time. A build that
#: changes nothing must not make every page look fresh.
PAGE_SOURCES = {
    "/": ("pipeline/landing.py", "pipeline/landing_chrome.py", "pipeline/entity.py", "models"),
    "/method/": ("pipeline/method.py", "pipeline/entity.py"),
    "/decide/": ("web/decide.html", "web/src/decide", "pipeline/live.py"),
    "/pricing/": ("pipeline/pricing.py", "api/worker/tiers.json"),
    "/feedback/": ("pipeline/feedback_page.py",),
    "/legal/terms/": ("docs/legal/terms-of-service.md",),
    "/legal/privacy/": ("docs/legal/privacy.md",),
    "/legal/neutrality/": ("docs/legal/neutrality.md",),
}
#: A page an answer engine can quote has a heading and real text without
#: running any JavaScript (MODEL-253).
MIN_WORDS = 80
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


def lastmod(path: str, root: Path = REPO_ROOT, today: date | None = None) -> str:
    """The last commit date of the page's sources; the build date if git can't say."""
    sources = [s for s in PAGE_SOURCES[path] if (root / s).exists()]
    out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", *sources], cwd=root,
                         capture_output=True, text=True, check=False)
    stamp = out.stdout.strip()
    return stamp if out.returncode == 0 and stamp else (today or date.today()).isoformat()


def sitemap(dates: dict[str, str] | None = None) -> str:
    dates = dates if dates is not None else {path: lastmod(path) for path in PAGES}
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{BASE}{path}</loc><lastmod>{dates[path]}</lastmod></url>\n"
                  for path in PAGES)
        + "</urlset>\n"
    )


def decide_capsule() -> str:
    """What /decide/ says before its JavaScript runs (MODEL-253).

    The board is a JavaScript app behind a human gate, so a crawler used to get
    an empty `<div id="root">`. This is the page's own description, in the
    page, for readers and retrievers alike; the app replaces it when it
    mounts. It holds no model data: answers stay on the board and the API.
    """
    e = lambda text: html.escape(text, quote=False)  # noqa: E731
    return (
        '<main class="capsule"><h1>Decide which AI model fits your job</h1>'
        f"<p>{e(entity.ONE_SENTENCE)}</p>"
        "<p>The decision board puts every requirement in front of you. Mark each one "
        "<b>Must</b> (a hard gate: a model that fails it is excluded, with the reason), "
        "<b>Prefer</b> (a weight that orders the models that pass) or "
        "<b>Doesn't matter</b>. The board then shows which models qualify, which were "
        "screened out and why, what each costs per task, and how sure the evidence is. "
        "When the evidence can't separate two models, it says so instead of inventing a "
        "winner.</p>"
        "<p>The board is free for people and rate-limited by a human check; it runs in "
        "your browser and needs JavaScript. Agents and software use the hosted API "
        "(<code>POST https://api.modelspec.dev/v1/decide</code>) or the MCP server with "
        'an API key: see <a href="/pricing/">pricing</a> and <a href="/auth.md">API access</a>.</p>'
        f"<p>{e(entity.DISAMBIGUATION)} "
        '<a href="/method/">How ModelSpec decides</a>.</p></main>'
    )


_TAGS = re.compile(r"<[^>]+>")
_INVISIBLE = re.compile(r"<(script|style|noscript|svg|template)\b.*?</\1>", re.S | re.I)


def visible_words(page: str) -> int:
    """Words a reader sees in the page body with JavaScript off."""
    body = re.split(r"<body\b[^>]*>", page, maxsplit=1)[-1]
    return len(html.unescape(_TAGS.sub(" ", _INVISIBLE.sub(" ", body))).split())


def thin_pages(tree: Path) -> list[str]:
    """Each sitemap page that answers a crawler with no heading or too few words."""
    failed = []
    for path in PAGES:
        page = (tree / path.lstrip("/") / "index.html").read_text(encoding="utf-8")
        words = visible_words(page)
        if not re.search(r"<h1[\s>]", page):
            failed.append(f"{path}: no <h1> without JavaScript")
        if words < MIN_WORDS:
            failed.append(f"{path}: {words} words without JavaScript; need {MIN_WORDS}")
    return failed


def not_found() -> str:
    """The 404 page: noindex, no canonical, and the three ways back in."""
    from pipeline import holding
    links = "".join(f'<a href="{href}">{label}</a>' for href, label in
                    (("/", "Home"), ("/decide/", "Decide"), ("/method/", "Method")))
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        '<meta name="robots" content="noindex"><title>Page not found · ModelSpec</title>\n'
        + brand.head_links() +
        f"<style>{holding._STYLE}nav a{{margin:0 .75rem}}</style></head>\n"
        f"<body><header>{landing_chrome.lockup()}</header><main><h1>Page not found</h1>"
        f"<p>Nothing is published at this address.</p><nav>{links}</nav></main></body></html>\n"
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
    decide = (web / "decide.html").read_text(encoding="utf-8")
    if decide.count('<div id="root"></div>') != 1:
        raise ValueError("web/dist/decide.html must hold exactly one empty <div id=\"root\">")
    (tree / "decide" / "index.html").write_text(
        decide.replace('<div id="root"></div>', f'<div id="root">{decide_capsule()}</div>'), encoding="utf-8")
    (tree / "404.html").write_text(not_found(), encoding="utf-8")
    shutil.copytree(web / "assets", tree / "assets",
                    ignore=shutil.ignore_patterns("main-*"))
    redirects = (public_data.REDIRECTS if public_data.enabled() else "") + REDIRECTS
    (tree / "_redirects").write_text(redirects, encoding="utf-8")
    (tree / "robots.txt").write_text(ROBOTS, encoding="utf-8")
    (tree / "sitemap.xml").write_text(sitemap(), encoding="utf-8")
    structured_data.inject(tree)
    headers = (real / "_headers").read_text(encoding="utf-8")
    headers = headers.rstrip("\n") + "\n" + HEADERS
    if public_data.enabled():
        headers = public_data.cache_headers(headers)
    (tree / "_headers").write_text(
        security_headers.add_to(headers, tree), encoding="utf-8")
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


#: What the deployed origin must answer beyond 200. The api-catalog type and
#: the Link header were both lost once by a `_headers` that replaced the build's.
EXPECTED_TYPES = {"/.well-known/api-catalog": "application/linkset+json"}
EXPECTED_LINKS = ('rel="describedby"', 'rel="api-catalog"', 'rel="sitemap"')
#: Written only on main (MAIN_ONLY), so the build cannot check it; production can.
DEPLOYED_ONLY = ("/api/decision/vocabulary.json",)


def smoke(origin: str, fetch=None) -> list[str]:
    """Each way the deployed `origin` fails to serve discovery as built."""
    def get(url: str) -> tuple[int, dict[str, str], bytes]:
        request = urllib.request.Request(url, headers={"User-Agent": "modelspec-smoke"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.status, {k.lower(): v for k, v in response.headers.items()}, response.read()
        except urllib.error.HTTPError as error:
            return error.code, {}, b""

    fetch = fetch or get
    failed: list[str] = []
    deployed = () if os.environ.get("DATA_SPLIT_ENABLED") == "true" else DEPLOYED_ONLY
    for path in (*(f"/{rel}" for rel in DISCOVERY), "/openapi.yaml", *PAGES, *deployed):
        status, headers, body = fetch(origin.rstrip("/") + path)
        if status != 200 or not body:
            failed.append(f"{path}: {status}")
            continue
        expected = EXPECTED_TYPES.get(path)
        if expected and not headers.get("content-type", "").startswith(expected):
            failed.append(f"{path}: Content-Type {headers.get('content-type')!r}, not {expected}")
        if path == "/":
            link = headers.get("link", "")
            failed.extend(f"/: Link header lacks {rel}" for rel in EXPECTED_LINKS if rel not in link)
    return failed


def crawler_probe(origin: str, fetch=None) -> list[str]:
    """Each (crawler, path) the deployed `origin` refuses (MODEL-253).

    A WAF rule that blocks "AI bots" as one group removes the search and fetch
    crawlers along with training ones, and answer engines then stop citing the
    site. This asks for every sitemap page and robots.txt as each named crawler.
    """
    def get(url: str, agent: str) -> int:
        request = urllib.request.Request(url, headers={"User-Agent": f"Mozilla/5.0 (compatible; {agent}; +https://modelspec.dev)"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.status
        except urllib.error.HTTPError as error:
            return error.code
        except urllib.error.URLError:
            return 0

    fetch = fetch or get
    agents = [agent for _, group in agent_ready.CRAWLERS for agent in group]
    return [f"{agent} {path}: {status}"
            for agent in agents for path in ("/robots.txt", *PAGES)
            if (status := fetch(origin.rstrip("/") + path, agent)) != 200]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    sub = parser.add_subparsers(dest="command", required=True)
    make = sub.add_parser("build", help="derive the live trees from a real build")
    make.add_argument("--src", default="dist-v1", help="the real build (default: dist-v1)")
    make.add_argument("--web", default="web/dist", help="the decide app build (default: web/dist)")
    make.add_argument("--out", default="dist", help="output (default: dist)")
    check = sub.add_parser("smoke", help="fetch every discovery file from a deployed origin")
    check.add_argument("--origin", required=True, help="for example https://modelspec.dev")
    probe = sub.add_parser("crawler-probe", help="fetch every page as each named AI crawler")
    probe.add_argument("--origin", required=True, help="for example https://modelspec.dev")
    args = parser.parse_args(argv)

    if args.command == "crawler-probe":
        refused = crawler_probe(args.origin)
        for line in refused:
            print(f"::error::{args.origin}: {line}", file=sys.stderr)
        if not refused:
            print(f"{args.origin}: every named crawler gets 200 on robots.txt and every sitemap page")
        return 1 if refused else 0

    if args.command == "smoke":
        failed = smoke(args.origin)
        for line in failed:
            print(f"::error::{args.origin}{line}", file=sys.stderr)
        if not failed:
            print(f"{args.origin}: every discovery file and page answers as built")
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
    thin = thin_pages(out / "modelspec")
    if thin:
        print("error: pages an answer engine can't read without JavaScript:", file=sys.stderr)
        for line in thin:
            print(f"  {line}", file=sys.stderr)
        return 3
    count = sum(1 for p in (out / "modelspec").rglob("*") if p.is_file())
    print(f"modelspec: {count} files; discovery links resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
