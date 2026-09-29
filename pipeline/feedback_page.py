"""The feedback page and the Feedback control on every page (MODEL-221).

`write` publishes `/feedback/`: the form, how an agent sends feedback, what is
kept, and "What you told us / what we changed" from `docs/feedback/changes.yaml`.
It also copies the control's script and stylesheet to `/feedback-assets/`.

`inject` adds the control to one HTML page: the stylesheet in `<head>`, and a
link to `/feedback/` before `</body>` that `feedback.js` turns into a button
opening the form. Without JavaScript it stays a link, so the control works
everywhere. `inject_tree` runs it over every page of a built tree; the decide
app carries its own React copy of the control and is built separately.
"""

from __future__ import annotations

import html
import shutil
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from pipeline import brand, landing_chrome

PAGE_PATH = Path("feedback/index.html")
ASSET_DIR = "feedback-assets"
CHANGES = Path("docs/feedback/changes.yaml")
ENDPOINT = "https://api.modelspec.dev/v1/feedback"
SCHEMA = "https://modelspec.dev/api/feedback/v1.schema.json"
SCHEMA_PATH = Path("api/feedback/v1.schema.json")
DOCS = "https://github.com/turbobeest/modelspec/blob/main/docs/feedback-api.md"
MARKER = "data-feedback-launch"

HEAD = f'<link rel="stylesheet" href="/{ASSET_DIR}/feedback.css">'
BODY = (f'<a class="ms-fb-launch" href="/feedback/" {MARKER}>Feedback</a>'
        f'<script src="/{ASSET_DIR}/feedback.js" defer></script>')


def inject(page: str) -> str:
    """The page with the Feedback control. Idempotent; a page without a body is unchanged."""
    if MARKER in page or "</body>" not in page:
        return page
    if "</head>" in page:
        page = page.replace("</head>", HEAD + "</head>", 1)
    head, _, tail = page.rpartition("</body>")
    return head + BODY + "</body>" + tail


def inject_tree(tree: Path) -> int:
    """Add the control to every HTML page under `tree`. Returns how many changed."""
    changed = 0
    for path in sorted(Path(tree).rglob("*.html")):
        if ASSET_DIR in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        updated = inject(text)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed += 1
    return changed


def load_changes(root: Path) -> list[dict[str, Any]]:
    data = yaml.safe_load((Path(root) / CHANGES).read_text(encoding="utf-8")) or {}
    rows = data.get("changes") or []
    for row in rows:
        missing = {"date", "told", "changed"} - set(row)
        if missing:
            raise ValueError(f"{CHANGES}: an entry is missing {sorted(missing)}")
        if not isinstance(row["date"], date):
            raise ValueError(f"{CHANGES}: date must be YYYY-MM-DD, got {row['date']!r}")
    return sorted(rows, key=lambda row: row["date"], reverse=True)


def _changes_html(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ("<p>Nothing yet. Feedback storage is not switched on, so there is no "
                "feedback to act on. Each change made because of what you tell us will be "
                "listed here, with its date and what shipped.</p>")
    items = []
    for row in rows:
        link = (f' <a href="{html.escape(row["link"])}">What shipped</a>'
                if row.get("link") else "")
        items.append(
            f'<li><time datetime="{row["date"].isoformat()}">{row["date"].isoformat()}</time>'
            f'<p><b>You told us:</b> {html.escape(row["told"])}</p>'
            f'<p><b>We changed:</b> {html.escape(row["changed"])}{link}</p></li>')
    return f'<ol class="fb-changes">{"".join(items)}</ol>'


def page(rows: list[dict[str, Any]]) -> str:
    curl = html.escape(
        f"curl -X POST {ENDPOINT} -H 'content-type: application/json' "
        "-d '{\"rating\": \"unreliable\", \"client\": \"agent\", "
        "\"decision_id\": \"dec_…\", \"note\": \"What went wrong\"}'")
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Feedback · ModelSpec</title><meta name="description" content="Tell ModelSpec whether an answer was reliable, unreliable, trustworthy, untrustworthy or confusing. People and agents, no account and no key."><link rel="canonical" href="https://modelspec.dev/feedback/">{brand.head_links()}{brand.social_meta("Feedback · ModelSpec", path="/feedback/")}<link rel="stylesheet" href="/landing-assets/landing.css"><link rel="stylesheet" href="/{ASSET_DIR}/page.css">{landing_chrome.lockup_style()}</head><body><header class="site-head">{landing_chrome.lockup()}<nav><a href="/method/">How it decides</a><a href="/pricing/">Pricing</a><a class="button primary" href="/decide/">Open the board</a></nav></header><main class="fb-page">
<section><h1>Tell us what you think.</h1><p>Was an answer reliable or unreliable? Did the evidence look trustworthy? Was something confusing? Pick one. The two text boxes are optional.</p><div data-feedback-inline data-question="What did you think of ModelSpec?"><p>This form needs JavaScript. Agents and scripts can use the API below.</p></div></section>
<section id="agents"><h2>For agents</h2><p>Send one rating after you act on an answer. No key. Include the <code>decision_id</code> when the feedback is about a decision; every decision names this endpoint in its <code>feedback</code> block.</p><ul><li>Endpoint: <code>POST {ENDPOINT}</code></li><li>Request schema: <a href="{SCHEMA}"><code>{SCHEMA}</code></a></li><li>Ratings: <code>reliable</code>, <code>unreliable</code>, <code>trustworthy</code>, <code>untrustworthy</code>, <code>confusing</code>. Client: <code>agent</code>, <code>cli</code>, <code>mcp</code> or <code>page</code>.</li><li>CLI: <code>modelspec feedback DECISION_ID --rating unreliable --note "…"</code></li><li>MCP: the <code>feedback</code> tool on <code>https://api.modelspec.dev/mcp</code></li><li>Reference: <a href="{DOCS}">docs/feedback-api.md</a> and operation <code>feedback</code> in <a href="/openapi.yaml">openapi.yaml</a></li></ul><pre><code>{curl}</code></pre></section>
<section id="privacy"><h2>What we keep</h2><p><b>Feedback storage is switched off.</b> Until it is switched on, what you send is checked and answered, and nothing of it is kept. Before it is switched on, the <a href="/legal/privacy/">privacy statement</a> will say exactly what is kept, for how long, and how to delete it.</p><p>Whatever happens, feedback needs no account and no key, and your address is never stored with it. Please don&#39;t include prompts, keys or personal details in the text boxes.</p></section>
<section id="changes"><h2>What you told us, and what we changed</h2>{_changes_html(rows)}</section>
</main>{landing_chrome.footer(detail="Feedback storage is switched off.")}</body></html>
'''


PAGE_CSS = """.fb-page{max-width:760px;margin:0 auto;padding:32px 16px 96px}
.fb-page h1{font-size:clamp(32px,5vw,44px);line-height:1.1;margin:0 0 12px}
.fb-page h2{margin:40px 0 8px}
.fb-page section p,.fb-page li{max-width:68ch}
.fb-page pre{overflow-x:auto;padding:12px;border:1px solid #34496e;border-radius:3px;background:#111d33;white-space:pre-wrap;word-break:break-word}
.fb-page code{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:.92em;overflow-wrap:anywhere}
.fb-page a{color:#5aa9ec}
.fb-page [data-feedback-inline]{margin-top:16px;padding:16px;border:1px solid #34496e;border-radius:3px;background:#111d33}
.fb-changes{list-style:none;padding:0}.fb-changes li{padding:12px 0;border-top:1px solid #223452}
.fb-changes time{color:#c7d1e0;font-family:"JetBrains Mono",ui-monospace,monospace}
"""


def write(tree: Path, root: Path) -> dict[str, Any]:
    """Publish `/feedback/`, its assets, and the request schema under `/api/`."""
    tree, root = Path(tree), Path(root)
    rows = load_changes(root)
    out = tree / PAGE_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    # Its inline form needs the control script, whatever runs after this.
    out.write_text(inject(page(rows)), encoding="utf-8")
    assets = tree / ASSET_DIR
    assets.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).parent / "feedback_assets"
    for name in ("feedback.js", "feedback.css"):
        shutil.copy2(source / name, assets / name)
    (assets / "page.css").write_text(PAGE_CSS, encoding="utf-8")
    schema = tree / SCHEMA_PATH
    schema.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / "schemas" / "feedback-v1.schema.json", schema)
    return {"path": "/feedback/", "sitemap_paths": ["/feedback/"], "changes": len(rows)}
