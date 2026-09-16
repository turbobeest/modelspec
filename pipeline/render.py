"""Render the export into static pages for modelspec.dev and benchgraph.dev.

Design rules this module enforces, rather than leaves to the author:

* A benchmark's models-covered table is generated from the cards. It is never
  authored on the page.
* Nothing is presented as current unless the eligibility report says so. Pages
  outside the active set state their standing and why, in the spec's own terms.
* Every score shows its date and its attribution. A number without a date is
  worse than no number, because it invites a comparison that is not supported.
"""

from __future__ import annotations

import html
import math
import posixpath
import re
from collections.abc import Collection, Iterable
from datetime import date
from pathlib import Path
from typing import Any

from pipeline.export import Build
from pipeline.hardware import Device
from pipeline.load import Benchmark, Catalogue, Model
#: The evidence-basis vocabulary lives in the ranking engine. A page that spelled
#: its own labels out would drift from the CLI on the first edit.
from pipeline.ranking import _basis

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" '
         'href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/'
         'css2?family=Archivo:wght@400;500;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">')

CSS = """
:root{--ground:#07080a;--surface:#0d1014;--raise:#13171d;--line:#1a1f26;--rule:#13171d;
--ink:#e6eaf0;--body:#c3cad4;--mute:#9aa4b2;--dim:#767f8d;
--good:#4ade80;--warn:#f5b342;--bad:#f87171;--off:#767f8d;--alias:#a78bfa;
--accent:#f5b342;--gutter:46px}
[data-site="benchgraph"]{--accent:#38bdf8}
*{box-sizing:border-box}
html{color-scheme:dark}
body{margin:0;background:var(--ground);color:var(--ink);
font-family:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
font-size:14px;line-height:1.55;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none;border-bottom:1px solid var(--line)}
a:hover{border-bottom-color:var(--accent)}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
.wrap{max-width:1220px;margin:0 auto;padding:0 24px}
nav{display:flex;align-items:center;justify-content:space-between;padding:16px 0;
border-bottom:1px solid var(--line);margin-bottom:26px;flex-wrap:wrap;gap:12px}
nav .brand{font-family:"Archivo",ui-sans-serif,system-ui,sans-serif;font-weight:700;font-size:16px;
letter-spacing:-.02em;color:var(--ink);border-bottom:0}
nav .brand:hover{color:var(--accent)}
nav .links{display:flex;gap:20px;font-size:12px;letter-spacing:.06em;flex-wrap:wrap}
nav .links a{color:var(--dim);border-bottom:0;text-transform:uppercase}
nav .links a:hover{color:var(--accent)}
.sans,.card,.prose{font-family:"Archivo",ui-sans-serif,system-ui,"Helvetica Neue",Arial,sans-serif}
h1{font-family:"Archivo",ui-sans-serif,system-ui,"Helvetica Neue",Arial,sans-serif;font-weight:700;
font-size:46px;line-height:1.05;letter-spacing:-.035em;margin:0 0 12px;overflow-wrap:break-word}
h2{font-family:"Archivo",ui-sans-serif,system-ui,"Helvetica Neue",Arial,sans-serif;font-weight:500;
font-size:13px;text-transform:uppercase;letter-spacing:.12em;color:var(--mute);
border-bottom:1px solid var(--line);padding-bottom:8px;margin:38px 0 14px;
position:relative;counter-increment:sec}
h2::before{content:counter(sec,decimal-leading-zero);position:absolute;
left:calc(-1 * var(--gutter));top:2px;width:var(--gutter);
font-family:"JetBrains Mono",ui-monospace,monospace;font-size:10px;letter-spacing:.14em;
color:var(--dim);text-transform:uppercase}
h3{font-family:"Archivo",ui-sans-serif,system-ui,"Helvetica Neue",Arial,sans-serif;font-weight:700;
font-size:16px;letter-spacing:-.01em;margin:22px 0 6px}
p{font-family:"Archivo",ui-sans-serif,system-ui,"Helvetica Neue",Arial,sans-serif;font-size:16px;
line-height:1.65;color:var(--body);max-width:68ch;text-wrap:pretty;margin:0 0 12px}
li{font-family:"Archivo",ui-sans-serif,system-ui,"Helvetica Neue",Arial,sans-serif;font-size:16px;
line-height:1.65;color:var(--body)}
.page{counter-reset:sec;padding-left:var(--gutter)}
.lab{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:10px;letter-spacing:.14em;
color:var(--dim);text-transform:uppercase}
.lede{color:var(--body);font-size:16px}
.meta{color:var(--dim);font-size:12px;font-family:"JetBrains Mono",ui-monospace,monospace;
max-width:none}
code,.mono{font-family:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px}
table{width:100%;border-collapse:collapse;margin:8px 0 18px;font-size:13px}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--rule);vertical-align:top;
overflow-wrap:break-word}
th{font-family:"JetBrains Mono",ui-monospace,monospace;font-weight:400;font-size:10px;
letter-spacing:.14em;color:var(--dim);text-transform:uppercase;border-bottom:1px solid var(--line)}
td.num{text-align:right;font-family:"JetBrains Mono",ui-monospace,monospace}
td.grouphead{background:var(--surface);border-bottom:1px solid var(--line)}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.panel{background:var(--surface);border:1px solid var(--line);padding:14px 16px;margin:14px 0}
.panel table{margin:0}
.pill{display:inline-block;font-family:"JetBrains Mono",ui-monospace,monospace;font-size:10px;
letter-spacing:.1em;text-transform:uppercase;padding:3px 9px;border:1px solid var(--line);
color:var(--mute);margin-right:6px}
.pill::before{margin-right:6px}
.pill.active{color:var(--good);border:1px solid var(--good);background:#102a1c}
.pill.active::before{content:"✓"}
.pill.unverified{color:var(--warn);border:1px solid var(--warn);background:none}
.pill.unverified::before{content:"!"}
.pill.alias{color:var(--alias);border:1px dashed var(--alias);background:none}
.pill.alias::before{content:"→"}
.pill.unassessed{color:var(--off);border:1px dotted var(--off);background:none}
.pill.unassessed::before{content:"?"}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px}
.card{background:var(--surface);border:1px solid var(--line);padding:13px 15px}
.card a{border-bottom:0;font-weight:700;font-size:16px;color:var(--ink)}
.card a:hover{color:var(--accent)}
.card .sub{color:var(--dim);font-size:12px;margin-top:3px;
font-family:"JetBrains Mono",ui-monospace,monospace}
ul.cols{columns:3;column-gap:26px;padding-left:18px}
ul.cols li{font-size:14px}
footer{margin:56px 0 34px;padding-top:18px;border-top:1px solid var(--line)}
footer p{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12px;color:var(--dim);
max-width:none;margin:0 0 6px}
.notice{border-left:3px solid var(--warn);padding:11px 15px;background:var(--surface);
margin:14px 0;font-size:15px;color:var(--body);max-width:68ch;
font-family:"Archivo",ui-sans-serif,system-ui,"Helvetica Neue",Arial,sans-serif}
.notice.ok{border-left-color:var(--good)}
.notice.derived{border-left-color:var(--warn)}
.notice.derived::before{content:"Derived";font-family:"JetBrains Mono",ui-monospace,monospace;
font-size:10px;letter-spacing:.14em;color:var(--warn);text-transform:uppercase;margin-right:12px}
.stats{display:grid;border-top:1px solid var(--line);border-bottom:1px solid var(--line);
margin:22px 0 30px}
.stats .cell{padding:16px 18px;min-width:0}
.stats .cell+.cell{border-left:1px solid var(--line)}
.stats .lab{display:block;margin-bottom:7px}
.stats .val{font-family:"Archivo",ui-sans-serif,system-ui,"Helvetica Neue",Arial,sans-serif;
font-size:20px;font-weight:700;letter-spacing:-.03em;overflow-wrap:break-word}
.stats .val.long{font-size:16px;font-weight:500}
.basis-verified{color:var(--good)}
.basis-unverified-legacy{color:var(--warn)}
.basis-mixed,.basis-partial-verified{color:var(--accent)}
.basis-none{color:var(--mute)}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 4px}
.chain{display:flex;align-items:stretch;border:1px solid var(--line);background:var(--surface);
padding:18px 0;margin:0 0 24px}
.chain-col{flex:1 1 0;min-width:0;padding:0 18px;display:flex;flex-direction:column;gap:8px}
.chain-col+.chain-col{border-left:1px solid var(--line)}
.chain-col.self{justify-content:center}
.chain-card{border:1px solid var(--line);padding:10px 13px;font-size:15px;
font-family:"Archivo",ui-sans-serif,system-ui,sans-serif}
.chain-card.self{border-color:var(--accent)}
.chain-card a{border-bottom:0;color:var(--ink);
font-family:"Archivo",ui-sans-serif,system-ui,sans-serif;font-size:15px}
.chain-card a:hover{color:var(--accent)}
.chain-card .lab{display:block;margin-top:4px;color:var(--accent)}
.chain-card.self .lab{color:var(--dim)}
.chain-name{font-family:"Archivo",ui-sans-serif,system-ui,sans-serif;font-size:15px;font-weight:700}
.bar{display:flex;align-items:center;gap:10px}
.bar .track{flex:0 0 150px;width:150px;height:8px;background:var(--raise)}
.bar .fill{display:block;height:8px;background:var(--accent)}
.bar .val{flex:0 0 auto;min-width:52px;text-align:right;
font-family:"JetBrains Mono",ui-monospace,monospace}
.bar.flex .track{flex:1 1 auto;width:auto}
.hw{display:flex;flex-direction:column}
.hw>.scroll{order:-1}
.showall{margin-top:12px}
.showall summary{display:inline-block;cursor:pointer;list-style:none;
font-family:"JetBrains Mono",ui-monospace,monospace;font-size:11px;letter-spacing:.1em;
text-transform:uppercase;color:var(--accent);border:1px solid var(--line);padding:7px 14px}
.showall summary::-webkit-details-marker{display:none}
.showall summary:hover{border-color:var(--accent)}
.showall .when-open{display:none}
.showall[open] .when-open{display:inline}
.showall[open] .when-closed{display:none}
.showall+.scroll tr.more{display:none}
.showall[open]+.scroll tr.more{display:table-row}
.gaps{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 14px}
.gap{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:10px;letter-spacing:.14em;
text-transform:uppercase;border:1px dashed var(--line);color:var(--mute);padding:4px 11px}
.complete{display:flex;align-items:center;gap:14px;margin:0 0 14px;max-width:68ch}
.complete .track{flex:1 1 auto;height:6px;background:var(--raise)}
.complete .fill{display:block;height:6px;background:var(--accent)}
@media(max-width:800px){
.page{padding-left:0}
h2::before{position:static;display:block;width:auto;margin-bottom:6px}
h1{font-size:30px}
ul.cols{columns:1}
.grid{grid-template-columns:1fr}
.stats{grid-template-columns:1fr!important}
.stats .cell+.cell{border-left:0;border-top:1px solid var(--line)}
.chain{flex-direction:column;gap:16px}
.chain-col+.chain-col{border-left:0;border-top:1px solid var(--line);padding-top:16px}
.bar .track{flex:0 0 90px;width:90px}
}
"""


def format_weight_size(gb: Any) -> str:
    """Render a stored weight size in GB for a model page. Display only.

    Values of 1 GB and above print to exactly two decimals ("3.62 GB"), the
    page format before MODEL-47. Values below 1 GB print in MB to three
    significant figures ("616 MB", "1.23 MB"), so a sub-10M-parameter model
    never reads as "0.0 GB" and a non-zero size never reads as "0 MB".
    """
    if gb is None:
        return ""
    try:
        value = float(gb)
    except (TypeError, ValueError):
        return f"{gb} GB"
    if abs(value) >= 1:
        return f"{value:.2f} GB"
    mb = value * 1000.0
    if mb == 0:
        return "0 MB"
    mb = float(f"{mb:.3g}")  # round first so 9.996 prints "10.0", not "10.00"
    decimals = max(0, 2 - math.floor(math.log10(abs(mb))))
    return f"{mb:.{decimals}f} MB"


def format_score(value: Any, unit: Any) -> str:
    """Render a score with its unit readably.

    The evidence records store units as words ("percent"), which must not be
    concatenated straight onto the number.
    """
    if value is None:
        return "\u2014"
    unit = (str(unit or "")).strip()
    if unit == "percent":
        return f"{value}%"
    return f"{value} {unit}".strip()


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def shell(*, title: str, description: str, canonical: str, body: str, build: Build,
          site: str, nav_links: Iterable[tuple[str, str]], robots: str = "index, follow") -> str:
    links = "".join(f'<a href="{esc(h)}">{esc(t)}</a>' for t, h in nav_links)
    return f"""<!doctype html>
<html lang="en" data-site="{esc(site.lower())}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(canonical)}">
<meta name="robots" content="{esc(robots)}">
<meta name="theme-color" content="#07080a">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(canonical)}">
<meta name="generator" content="modelspec-pipeline {esc(build.commit[:12])}">
{FONTS}
<style>{CSS}</style></head>
<body><div class="wrap">
<nav><a class="brand" href="/">{esc(site)}</a><div class="links">{links}</div></nav>
<main class="page">
{body}
</main>
<footer>
<p>Built {esc(build.built_at)} from commit <span class="mono">{esc(build.commit[:12])}</span>.
Eligibility as of {esc(build.as_of.isoformat())}.</p>
<p><a href="https://github.com/turbobeest/modelspec">Source and data on GitHub</a> &middot;
Data <span class="mono">CC BY-SA</span>, code <span class="mono">MIT</span>.</p>
</footer></div></body></html>
"""


#: `.title()` turns aws_bedrock into "Aws Bedrock" and gpt4all into "Gpt4All".
#: Acronyms and brand casing have to be spelled out; anything absent falls back
#: to title case, which is right for the plain ones.
PROPER_NAMES = {
    "aws_bedrock": "AWS Bedrock", "azure_ai_foundry": "Azure AI Foundry",
    "google_vertex_ai": "Google Vertex AI", "nvidia_nim": "NVIDIA NIM",
    "ibm_watsonx": "IBM watsonx", "gpt4all": "GPT4All", "lm_studio": "LM Studio",
    "openrouter": "OpenRouter", "together_ai": "Together AI",
    "fireworks_ai": "Fireworks AI", "deepinfra": "DeepInfra",
    "huggingface": "Hugging Face", "sambanova": "SambaNova",
    "github_copilot": "GitHub Copilot", "chatgpt": "ChatGPT",
    "claude_ai": "Claude.ai", "grok_xai": "Grok (xAI)", "gemini_app": "Gemini",
    "deepseek": "DeepSeek", "ai21_labs": "AI21 Labs", "jan_ai": "Jan",
    "mlx_community": "MLX Community", "open_webui": "Open WebUI",
    "modelscope": "ModelScope", "kaggle_models": "Kaggle Models",
    "mistral_plateforme": "Mistral La Plateforme", "zhipu_glm": "Zhipu GLM",
    "qwen_alibaba": "Qwen (Alibaba)", "baidu_ernie": "Baidu ERNIE",
    "bytedance_doubao": "ByteDance Doubao", "tencent_hunyuan": "Tencent Hunyuan",
    "moonshot_kimi": "Moonshot Kimi", "zero_one_ai": "01.AI",
    "tii_falcon": "TII Falcon", "upstage_solar": "Upstage Solar",
    "samsung_gauss": "Samsung Gauss", "copilot_microsoft": "Microsoft Copilot",
    "meta_ai": "Meta AI", "snowflake_cortex": "Snowflake Cortex",
    "stability_ai": "Stability AI", "poe": "Poe", "raycast": "Raycast",
}


def proper_name(node_id: str, fallback: str = "") -> str:
    if node_id in PROPER_NAMES:
        return PROPER_NAMES[node_id]
    return fallback or node_id.replace("_", " ").title()


def human_count(value: Any) -> str:
    """8000000000 is unreadable; 8B is the number a person means."""
    try:
        n = float(value)
    except (TypeError, ValueError):
        return esc(value)
    for limit, suffix in ((1e12, "T"), (1e9, "B"), (1e6, "M")):
        if n >= limit:
            trimmed = f"{n / limit:.1f}".rstrip("0").rstrip(".")
            return f"{trimmed}{suffix}"
    return f"{n:,.0f}"


MS_NAV = [("Downselect", "/downselect/"), ("Graph", "/graph/"), ("Models", "/models/"), ("Providers", "/providers/"), ("Benchmarks", "https://benchgraph.dev/benchmarks/"), ("API", "/api/index.json")]
BG_NAV = [("Catalogue", "/benchmarks/"), ("Models", "https://modelspec.dev/models/"),
          ("Graph", "https://modelspec.dev/graph/"), ("API", "/api/catalogue.json")]


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# ── modelspec.dev ────────────────────────────────────────────────────────────

def _section(title: str, body: str, lede: str = "") -> str:
    """Render a section, or nothing at all.

    A section with no rows is omitted rather than rendered as an empty shell.
    Null in this schema means "not yet researched", and an empty table asserts
    the opposite — that we looked and there was nothing.
    """
    if not body:
        return ""
    return f"<h2>{esc(title)}</h2>" + (f'<p class="lede">{lede}</p>' if lede else "") + body


def _table(headers: list[str], rows: list[str]) -> str:
    if not rows:
        return ""
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    return ('<div class="scroll"><table><thead><tr>' + head +
            "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>")


def looks_like_hf_repo(model_id: str) -> bool:
    """A Hub repo id is `org/name`. Card ids look the same, so this is not identity."""
    if model_id.count("/") != 1 or "://" in model_id or model_id.startswith("/"):
        return False
    org, name = model_id.split("/")
    return bool(org) and bool(name)


def model_anchor(model_id: str, name: str, pages: Collection[str] | None = None) -> str:
    """Link to a card page the build produces, never to a 404.

    Lineage fields store Hugging Face repo ids. Those are not card ids.
    `/m/{hf-id}/` is a page this pipeline does not emit.
    """
    label = esc(name)
    if pages is None or model_id in pages:
        return f'<a href="/m/{esc(model_id)}/">{label}</a>'
    if looks_like_hf_repo(model_id):
        return (
            f'<a href="https://huggingface.co/{esc(model_id)}" '
            f'rel="nofollow noopener">{label}</a>'
        )
    return label


def lineage_section(relations: Any, pages: Collection[str] | None = None,
                    display_name: str = "") -> str:
    """This model between what it came from and what came from it.

    The relation word is written lowercase and uppercased by `.lab`, so the
    markup keeps the word the graph actually stored.
    """
    if not (relations.ancestors or relations.descendants):
        return ""

    def card(entry: dict[str, Any], suffix: str) -> str:
        relation = str(entry.get("relation") or "").strip()
        label = (f'<span class="lab">{esc(relation)}{suffix}</span>' if relation else "")
        return ('<div class="chain-card">'
                + model_anchor(str(entry["id"]), str(entry["name"]), pages)
                + label + "</div>")

    columns = []
    if relations.ancestors:
        columns.append('<div class="chain-col"><span class="lab">Descended from</span>'
                       + "".join(card(e, " of") for e in relations.ancestors) + "</div>")
    columns.append(
        '<div class="chain-col self"><div class="chain-card self">'
        + (f'<span class="chain-name">{esc(display_name)}</span>' if display_name else "")
        + '<span class="lab">This model</span></div></div>')
    if relations.descendants:
        columns.append('<div class="chain-col"><span class="lab">Is the base of</span>'
                       + "".join(card(e, "") for e in relations.descendants) + "</div>")

    return _section("Lineage", '<div class="chain">' + "".join(columns) + "</div>")


def platforms_section(relations: Any) -> str:
    """Only render columns that carry data on at least one row.

    An always-empty column is the table equivalent of an empty section: it
    asserts we looked and found nothing, when in fact nobody has researched it.
    """
    entries = relations.platforms
    if not entries:
        return ""
    any_ids = any(e.get("model_id_on_platform") for e in entries)
    any_flags = any(e.get("fine_tuning") or e.get("gated") for e in entries)

    rows = []
    for entry in entries:
        cells = [f'<td>{esc(proper_name(str(entry["id"]), ""))}</td>']
        if any_ids:
            cells.append(f'<td class="mono">{esc(entry.get("model_id_on_platform") or "")}</td>')
        if any_flags:
            flags = []
            if entry.get("fine_tuning"):
                flags.append("fine-tuning")
            if entry.get("gated"):
                flags.append("gated")
            cells.append("<td>" + " ".join(
                '<span class="pill">' + esc(f) + "</span>" for f in flags) + "</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")

    headers = ["Platform"]
    if any_ids:
        headers.append("Id on that platform")
    if any_flags:
        headers.append("")
    return _section("Where it runs", _table(headers, rows),
                    "Taken from the card's availability section.")


def _decode_cell(value: Any) -> str:
    """'n/a' for a non-token model (or missing data), never blank or 0."""
    if value is None:
        return "n/a"
    return f"~{esc(value)}"


#: Biggest iron first. A class this pipeline has not seen sorts after all of
#: these rather than silently taking a position among them.
DEVICE_CLASS_ORDER = ("datacentre", "workstation", "consumer", "edge", "integrated")

#: Enough rows to see the shape of the curve. The rest are one click away.
HARDWARE_ROWS_SHOWN = 8


def _uniform(rows: list[dict[str, Any]], key: str) -> tuple[bool, Any]:
    """Whether every row carries the same value for `key`, and what that value is."""
    values = [r.get(key) for r in rows]
    first = values[0] if values else None
    return all(v == first for v in values), first


def _decode_bar(value: Any, peak: float) -> str:
    """The decode rate as a bar against the fastest device on this page."""
    width = 0.0
    if value is not None and peak > 0:
        width = max(0.0, min(100.0, float(value) / peak * 100.0))
    return ('<div class="bar"><span class="track">'
            f'<span class="fill" style="width:{width:.1f}%"></span></span>'
            f'<span class="val">{_decode_cell(value)}</span></div>')


def _hardware_groups(entries: list[dict[str, Any]],
                     devices: dict[str, Device] | None) -> list[tuple[str, list[dict[str, Any]]]]:
    """Rows by device class, or one unnamed group when any row cannot be placed.

    A partial grouping would have to invent a class for the rows it could not
    look up, so one unknown id drops the whole table back to flat.
    """
    if devices is None or not all(e.get("id") in devices for e in entries):
        return [("", entries)]
    buckets: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        buckets.setdefault(devices[entry["id"]].device_class, []).append(entry)
    rank = {name: i for i, name in enumerate(DEVICE_CLASS_ORDER)}
    return [(name, buckets[name])
            for name in sorted(buckets, key=lambda c: (rank.get(c, len(rank)), c))]


def hardware_section(relations: Any, devices: dict[str, Device] | None = None) -> str:
    entries = list(relations.hardware)
    if not entries:
        return ""

    # A value identical on every row is a fact about the model, not about the
    # devices, so it belongs in the sentence rather than repeated down a column.
    same_quant, quant = _uniform(entries, "quantization")
    same_weights, weights = _uniform(entries, "weights_gb")
    same_fastest_quant, fastest_quant = _uniform(entries, "fastest_quantization")

    hoisted = []
    if same_quant and quant is not None:
        hoisted.append(f'Every device here runs it at <span class="mono">{esc(quant)}</span>.')
    if same_weights and weights is not None:
        hoisted.append('The weights are <span class="mono">'
                       f'{esc(format_weight_size(weights))}</span> on all of them.')
    if same_fastest_quant and fastest_quant is not None:
        hoisted.append('The fastest quantisation that fits is <span class="mono">'
                       f'{esc(fastest_quant)}</span> everywhere.')
    lede = ("Ordered by predicted speed. Bandwidth sets decode rate; memory decides whether "
            "it runs at all." + ("" if not hoisted else " " + " ".join(hoisted)))

    headers = ["Device", "Memory", "Bandwidth"]
    if not same_quant:
        headers.append("Best quality")
    if not same_weights:
        headers.append("Weights")
    headers += ["tok/s", "Fastest"]
    if not same_fastest_quant:
        headers.append("Fastest at")

    peak = max((float(e["predicted_decode_tps"]) for e in entries
                if e.get("predicted_decode_tps") is not None), default=0.0)

    rows: list[str] = []
    shown = 0
    for name, group in _hardware_groups(entries, devices):
        if name:
            more = ' class="more"' if shown >= HARDWARE_ROWS_SHOWN else ""
            plural = "s" if len(group) != 1 else ""
            rows.append(f'<tr{more}><td class="grouphead" colspan="{len(headers)}">'
                        f'<span class="lab">{esc(name)} &middot; {len(group)} '
                        f'device{plural}</span></td></tr>')
        for entry in group:
            device = entry.get("device") or {}
            cells = [f'<td>{esc(entry["name"])}</td>',
                     f'<td class="num">{esc(entry.get("device_memory_gb"))} GB</td>',
                     f'<td class="num">{esc(device.get("memory_bandwidth_gb_s"))} GB/s</td>']
            if not same_quant:
                cells.append(f'<td class="mono">{esc(entry.get("quantization") or "")}</td>')
            if not same_weights:
                cells.append('<td class="num">'
                             f'{esc(format_weight_size(entry.get("weights_gb")))}</td>')
            cells.append(f'<td>{_decode_bar(entry.get("predicted_decode_tps"), peak)}</td>')
            cells.append('<td class="num">'
                         f'{_decode_cell(entry.get("fastest_predicted_decode_tps"))}</td>')
            if not same_fastest_quant:
                cells.append('<td class="mono">'
                             f'{esc(entry.get("fastest_quantization") or "")}</td>')
            more = ' class="more"' if shown >= HARDWARE_ROWS_SHOWN else ""
            rows.append(f"<tr{more}>" + "".join(cells) + "</tr>")
            shown += 1

    control = ""
    if shown > HARDWARE_ROWS_SHOWN:
        control = ('<details class="showall"><summary>'
                   f'<span class="when-closed">Show all {shown} devices</span>'
                   '<span class="when-open">Show fewer</span></summary></details>')

    moe = any(e.get("moe_prediction_is_conservative") for e in relations.hardware)
    caveat = (" This is a mixture-of-experts model and no card carries active-parameter "
              "counts, so these predictions use total parameters and understate the real "
              "speed." if moe else "")
    note = ('<div class="notice derived">Every figure here is <strong>computed</strong>, not measured. '
            'Fit is weights at each quantisation against device memory, with a 25% allowance '
            'for the KV cache, activations and the OS. Decode rate is the memory-bandwidth '
            'roofline at 70% efficiency. Nobody has run this model on these devices.'
            + esc(caveat) + '</div>')
    # `.showall + .scroll` can only reach rows that follow the control, so the
    # control is emitted first and flex `order` puts it back under the table.
    return _section("What it fits on",
                    note + f'<div class="hw">{control}{_table(headers, rows)}</div>', lede)


def capability_chips(relations: Any) -> str:
    """The capability pills alone, for the page header."""
    return " ".join(
        f'<span class="pill">{esc(str(e["name"]))}'
        + (f' &middot; {esc(e["tier"])}' if e.get("tier") else "") + "</span>"
        for e in relations.capabilities)


def competitors_section(relations: Any, pages: Collection[str] | None = None) -> str:
    entries = relations.competitors[:12]
    if not entries:
        return ""
    cards = []
    for entry in entries:
        score = entry.get("overlap_score")
        width = 0.0 if score is None else max(0.0, min(100.0, float(score) * 100.0))
        cards.append(
            '<div class="card">'
            + model_anchor(str(entry["id"]), str(entry["name"]), pages)
            + '<div class="bar flex"><span class="track"><span class="fill" '
            f'style="width:{width:.1f}%"></span></span>'
            f'<span class="val">{esc("" if score is None else score)}</span></div></div>')
    note = ('<div class="notice derived">Derived, not authored. Two models compete if they share a '
            'type, sit within 3x on parameters, and report at least one benchmark in common; '
            'the score is the overlap of their capability sets. The shared-benchmark test '
            'rests on card scores that carry one date per card and no per-score source.</div>')
    return _section("What competes with it",
                    note + f'<div class="grid">{"".join(cards)}</div>')


def evidence_section(model: Model) -> str:
    """Per-score evidence: the reviewed kind, with a source and a date each."""
    block = model.front.get("benchmarks") or {}
    records = block.get("evidence") if isinstance(block, dict) else None
    if not records:
        return ""
    rows = []
    for rec in records:
        kind = str(rec.get("source_kind") or "")
        rows.append(
            f'<tr><td>{esc(rec.get("benchmark_id"))}</td>'
            f'<td>{esc(rec.get("model_id_as_evaluated"))}</td>'
            f'<td class="num">{esc(format_score(rec.get("score"), rec.get("unit")))}</td>'
            f'<td>{esc(rec.get("evidence_date"))} '
            f'<span class="pill">{esc(rec.get("date_type"))}</span></td>'
            f'<td><span class="pill">{esc(kind.replace("_", " "))}</span></td>'
            f'<td><a href="{esc(rec.get("source_url"))}" rel="nofollow noopener">source</a></td></tr>')
    note = ('<div class="notice ok">Each row was checked against its source by a reviewer, '
            'and carries the model identifier as actually evaluated — which is not always the '
            'same as this card\'s.</div>')
    return _section("Verified benchmark evidence",
                    note + _table(["Benchmark", "Evaluated as", "Score", "Evidence date",
                                   "Source kind", ""], rows))


GUIDE_SECTIONS = (
    ("prompt_shape", "Prompt shape"),
    ("system_message", "System message"),
    ("reasoning_and_tools", "Reasoning and tools"),
    ("formatting", "Formatting"),
    ("failure_modes", "Failure modes"),
    ("retry_advice", "Retry advice"),
)


def authoring_guide_section(front: dict[str, Any]) -> str:
    """The card's dated, sourced authoring guide, or nothing when it has none.

    Styling reuses existing classes so unguided pages stay byte-identical:
    ``current`` wears the ``active`` pill, ``stale`` the ``unverified`` pill
    plus a ``notice``.
    """
    guide = front.get("authoring_guide")
    if not isinstance(guide, dict):
        return ""
    applies = guide.get("applies_to") if isinstance(guide.get("applies_to"), dict) else {}
    status = str(guide.get("status") or "")
    stale = status == "stale"
    pill = "unverified" if stale else "active"
    header = (f'<p><span class="pill {pill}">{esc(status or "unknown")}</span> '
              f'reviewed {esc(guide.get("as_of"))} &middot; applies to '
              f'<span class="mono">{esc(applies.get("version"))}</span></p>')
    if stale:
        header += ('<div class="notice">This guide was written for an earlier version '
                   'and needs re-review.</div>')
    sections = guide.get("sections") if isinstance(guide.get("sections"), dict) else {}
    parts = []
    for key, label in GUIDE_SECTIONS:
        claims = sections.get(key) or []
        items = []
        for claim in claims:
            if not isinstance(claim, dict):
                continue
            sources = [
                f'{_safe_link(s.get("url"), s.get("title"))} '
                f'<small>{esc(s.get("accessed"))} &middot; {esc(s.get("kind"))}</small>'
                for s in (claim.get("sources") or []) if isinstance(s, dict)]
            items.append(f'<li>{esc(claim.get("text"))}'
                         + (f'<br><small>Sources:</small> {"; ".join(sources)}' if sources else "")
                         + "</li>")
        if items:
            parts.append(f"<h3>{esc(label)}</h3><ul>{''.join(items)}</ul>")
    return _section("Authoring guide", header + "".join(parts),
                    "How to prompt this model, per its provider's guidance. Every claim is sourced and dated.")


def _dig(front: Any, *keys: str) -> Any:
    """Nested lookup that survives a missing or non-dict intermediate."""
    node = front
    for key in keys:
        if not isinstance(node, dict):
            return None
        node = node.get(key)
    return node


#: Per-token prices only. The per-million and per-hour fields answer a different
#: question and their presence would not mean this model's tokens are priced.
COST_PER_TOKEN_FIELDS = ("input", "output", "reasoning", "cache_read", "cache_write",
                         "batch_input", "batch_output")


def _has_token_price(front: Any) -> bool:
    cost = _dig(front, "cost")
    return isinstance(cost, dict) and any(
        cost.get(field) is not None for field in COST_PER_TOKEN_FIELDS)


#: Every fact this page knows how to show, and how to tell whether the card has
#: it. A registry rather than a run of conditionals, because the footer's whole
#: claim is that the list is complete and the same one every page is measured
#: against. `open_weights` is false-is-present: a card that says "closed" has
#: been researched.
PAGE_FACTS: tuple[tuple[str, Any], ...] = (
    ("Parameters", lambda f, r, m: _dig(f, "architecture", "total_parameters") is not None),
    ("Release date", lambda f, r, m: bool(f.get("release_date"))),
    ("Last updated", lambda f, r, m: bool(f.get("last_updated"))),
    ("Family", lambda f, r, m: bool(f.get("family"))),
    ("Status", lambda f, r, m: bool(f.get("status"))),
    ("Open weights", lambda f, r, m: _dig(f, "licensing", "open_weights") is not None),
    ("Licence", lambda f, r, m: bool(_dig(f, "licensing", "license_type"))),
    ("Context window", lambda f, r, m: _dig(f, "modalities", "text", "context_window") is not None),
    ("Pricing", lambda f, r, m: _has_token_price(f)),
    ("Training cutoff", lambda f, r, m: bool(_dig(f, "lineage", "training_data_cutoff"))),
    ("Lineage", lambda f, r, m: r is not None and bool(r.ancestors or r.descendants)),
    ("Capabilities", lambda f, r, m: r is not None and bool(r.capabilities)),
    ("Platform availability", lambda f, r, m: r is not None and bool(r.platforms)),
    ("Hardware fit", lambda f, r, m: r is not None and bool(r.hardware)),
    ("Benchmark scores", lambda f, r, m: bool(m)),
)


def unresearched_section(front: dict[str, Any], relations: Any, scores: Any) -> str:
    """Name the gaps once, with the page's own denominator.

    `ModelCard.card_completeness` is not used here. Measured across all 1,339
    cards it spans 10.0%-21.3%, so it separates nothing, and it costs 20s per
    build. What a reader wants is which of the things this page could show are
    missing.
    """
    absent = [label for label, present in PAGE_FACTS
              if not present(front if isinstance(front, dict) else {}, relations, scores)]
    if not absent:
        return ""
    have, total = len(PAGE_FACTS) - len(absent), len(PAGE_FACTS)
    bar = (f'<div class="complete"><span class="lab">{have} of the {total} facts this page '
           'can show</span><span class="track"><span class="fill" '
           f'style="width:{have / total * 100:.1f}%"></span></span></div>')
    chips = "".join(f'<span class="gap">{esc(label)}</span>' for label in absent)
    return _section(
        "Not yet researched", bar + f'<div class="gaps">{chips}</div>',
        "A section with nothing to say does not render at all, so this is the one place the "
        "page names its gaps. Remember that null in this schema means nobody has looked, not "
        "that the model lacks the property.")


#: Past this many characters a value reads as a phrase rather than a figure, and
#: the display size that flatters "34.4B" breaks "partial-verified" across lines.
STAT_LONG_VALUE = 10


def _card_evidence_basis(model: Model) -> str | None:
    """Provenance of this card's own scores, in the ranking engine's vocabulary.

    A card with no scores has nothing to characterise, and "none" would read as
    a verdict on the model rather than on an empty input set.
    """
    contributing = len(model.scores)
    if not contributing:
        return None
    records = _dig(model.front, "benchmarks", "evidence")
    verified_ids = {str(r.get("benchmark_id")) for r in records
                    if isinstance(r, dict)} if isinstance(records, list) else set()
    verified = sum(1 for key in model.scores if str(key) in verified_ids)
    return _basis(contributing, verified, verified / contributing)


def stat_strip(model: Model) -> str:
    """The card's headline figures, only the ones it actually carries.

    The column count follows the cells that survive, so a thin card gets a
    short strip rather than a row of blanks asserting we looked.
    """
    front = model.front
    parameters = _dig(front, "architecture", "total_parameters")
    open_weights = _dig(front, "licensing", "open_weights")
    basis = _card_evidence_basis(model)
    cells = [
        ("Parameters", human_count(parameters) if parameters else None, ""),
        ("Type", front.get("model_type"), ""),
        ("Released", front.get("release_date"), ""),
        ("Open weights", None if open_weights is None else ("yes" if open_weights else "no"), ""),
        ("Evidence basis", basis, f" basis-{basis}" if basis else ""),
    ]
    rendered = [(label, str(value), extra) for label, value, extra in cells
                if value not in (None, "", [])]
    if not rendered:
        return ""
    body = "".join(
        f'<div class="cell"><span class="lab">{esc(label)}</span>'
        f'<div class="val{" long" if len(value) > STAT_LONG_VALUE else ""}{extra}">'
        f"{esc(value)}</div></div>"
        for label, value, extra in rendered)
    return (f'<div class="stats" style="grid-template-columns:repeat({len(rendered)},'
            f'minmax(0,1fr))">{body}</div>')


def model_page(model: Model, build: Build, benchmarks: dict[str, Benchmark],
               catalogue: Catalogue, relations: Any = None,
               pages: Collection[str] | None = None,
               devices: dict[str, Device] | None = None) -> str:
    front = model.front
    scores = model.scores
    as_of = model.scores_as_of
    rows = []
    for key, value in sorted(scores.items(), key=lambda kv: kv[0]):
        bench = benchmarks.get(key)
        name = esc(bench.name) if bench else esc(key)
        link = f'<a href="https://benchgraph.dev/b/{esc(key)}/">{name}</a>' if bench else name
        disposition = catalogue.for_benchmark(key).status
        rows.append(
            f'<tr><td>{link}</td><td><span class="pill {esc(disposition)}">{esc(disposition)}</span></td>'
            f'<td class="num">{esc(value)}</td></tr>'
        )

    stale = ('<div class="notice">These scores carry one collection date for the whole card '
             f'({esc(as_of)}) and a source list rather than a source per score, so they cannot be '
             'attributed individually. They are shown as reported and are not verified evidence. '
             'Benchmark pages carry the reviewed, dated evidence where it exists.</div>') if scores else ""

    rel = relations
    chips = ""
    sections = ""
    if rel is not None:
        pills = capability_chips(rel)
        chips = f'<div class="chips">{pills}</div>' if pills else ""
        sections = (lineage_section(rel, pages, model.display_name)
                    + hardware_section(rel, devices) + platforms_section(rel)
                    + competitors_section(rel, pages))

    body = f"""
<h1>{esc(model.display_name)}</h1>
<p class="meta">{esc(model.provider_display)} &middot; <span class="mono">{esc(model.model_id)}</span></p>
{chips}
{stat_strip(model)}
{sections}{authoring_guide_section(front)}
{evidence_section(model)}
<h2>Reported benchmark scores</h2>
{stale if scores else '<p class="lede">This card reports no benchmark scores yet.</p>'}
<div class="scroll"><table>
<thead><tr><th>Benchmark</th><th>Catalogue standing</th><th>Score</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
{unresearched_section(front, rel, scores)}
<h2>Data</h2>
<p><a href="/api/models/{esc(model.model_id)}.json">This card as JSON</a> &middot;
<a href="/graph/">See it in the graph</a> &middot;
<a href="https://github.com/turbobeest/modelspec/blob/main/{esc(model.path.relative_to(model.path.parents[2]))}">Edit on GitHub</a></p>
"""
    return shell(
        title=f"{model.display_name} — ModelSpec",
        description=f"{model.display_name} by {model.provider_display}: benchmark scores, lineage, platforms and hardware fit, with the date on every number.",
        canonical=f"https://modelspec.dev/m/{model.model_id}/",
        body=body, build=build, site="ModelSpec", nav_links=MS_NAV,
    )


def catalogue_freshness(models: list[Model], build: Build | None = None) -> dict[str, Any]:
    """How current the catalogue itself is.

    Individual scores disclose their age. The catalogue as a whole did not, and
    a visitor had no way to tell whether the data stopped months ago. A
    complete-looking catalogue that is behind is more misleading than a small
    current one, because its completeness is what makes it look trustworthy.

    Eligibility `as_of` and the build commit are the dates the build actually
    knows. Newest release is a secondary signal that the corpus has a hole.
    """
    dates = sorted(
        str(m.front.get("release_date"))
        for m in models
        if m.front.get("release_date")
    )
    info: dict[str, Any] = {
        "newest_release": dates[-1] if dates else None,
        "models": len(models),
    }
    if build is not None:
        info["eligibility_as_of"] = build.as_of.isoformat()
        info["commit"] = build.commit
        info["built_at"] = build.built_at
    return info


def freshness_notice(models: list[Model], build: Build | None = None) -> str:
    """Disclose how current the catalogue is, and the hole when there is one.

    Without a build, a current corpus is silent — nothing to warn about. With
    a build, eligibility date and commit are always shown, because a reader
    otherwise cannot tell whether the data is from this week or last spring.
    """
    info = catalogue_freshness(models, build)
    parts: list[str] = []
    if build is not None:
        parts.append(
            '<p class="meta">Catalogue eligibility as of '
            f'<strong>{esc(info["eligibility_as_of"])}</strong>'
            f' · built from <span class="mono">{esc(build.commit[:12])}</span></p>'
        )
    newest = info.get("newest_release")
    if newest:
        try:
            newest_d = date.fromisoformat(str(newest))
        except ValueError:
            newest_d = None
        if newest_d is not None:
            days = (date.today() - newest_d).days
            if days >= 45:
                parts.append(
                    '<div class="notice">The newest model in this catalogue was released on '
                    f'<strong>{esc(newest)}</strong>, about {days // 30} months ago. '
                    'Anything released since is missing, so a "best model" answer here excludes it. '
                    'This is a known gap, not a claim that nothing newer exists.</div>'
                )
    return "".join(parts)


def models_index(models: list[Model], build: Build) -> str:
    by_provider: dict[str, list[Model]] = {}
    for model in models:
        by_provider.setdefault(model.provider_display, []).append(model)
    blocks = []
    for provider in sorted(by_provider, key=str.lower):
        items = "".join(
            f'<li><a href="/m/{esc(m.model_id)}/">{esc(m.display_name)}</a></li>'
            for m in sorted(by_provider[provider], key=lambda m: m.display_name.lower())
        )
        blocks.append(f'<h3>{esc(provider)}</h3><ul class="cols">{items}</ul>')
    body = (f'<h1>Every model</h1><p class="lede">{len(models)} cards across '
            f'{len(by_provider)} providers.</p>' + freshness_notice(models, build)
            + "".join(blocks))
    return shell(title="Every model — ModelSpec",
                 description=f"All {len(models)} model cards in ModelSpec, by provider.",
                 canonical="https://modelspec.dev/models/", body=body, build=build,
                 site="ModelSpec", nav_links=MS_NAV)


def providers_index(models: list[Model], build: Build) -> str:
    counts: dict[str, tuple[str, int]] = {}
    for model in models:
        name, count = counts.get(model.provider, (model.provider_display, 0))
        counts[model.provider] = (name, count + 1)
    cards = "".join(
        f'<div class="card"><a href="/p/{esc(slug)}/">{esc(name)}</a>'
        f'<div class="sub">{count} model{"s" if count != 1 else ""}</div></div>'
        for slug, (name, count) in sorted(counts.items(), key=lambda kv: kv[1][0].lower())
    )
    body = (f'<h1>Providers</h1><p class="lede">{len(counts)} organisations publishing '
            f'{len(models)} models.</p>' + freshness_notice(models, build)
            + f'<div class="grid">{cards}</div>')
    return shell(title="Providers — ModelSpec", description=f"{len(counts)} model providers in ModelSpec.",
                 canonical="https://modelspec.dev/providers/", body=body, build=build,
                 site="ModelSpec", nav_links=MS_NAV)


def provider_page(slug: str, models: list[Model], build: Build) -> str:
    display = models[0].provider_display
    rows = "".join(
        f'<tr><td><a href="/m/{esc(m.model_id)}/">{esc(m.display_name)}</a></td>'
        f'<td>{esc(m.front.get("model_type") or "")}</td>'
        f'<td>{esc(m.front.get("release_date") or "")}</td>'
        f'<td class="num">{len(m.scores)}</td></tr>'
        for m in sorted(models, key=lambda m: m.display_name.lower())
    )
    body = (f'<h1>{esc(display)}</h1><p class="lede">{len(models)} models.</p>'
            '<div class="scroll"><table><thead><tr><th>Model</th><th>Type</th><th>Released</th>'
            f'<th>Scores</th></tr></thead><tbody>{rows}</tbody></table></div>')
    return shell(title=f"{display} models — ModelSpec",
                 description=f"Every {display} model in ModelSpec, with release dates and benchmark coverage.",
                 canonical=f"https://modelspec.dev/p/{slug}/", body=body, build=build,
                 site="ModelSpec", nav_links=MS_NAV)


# ── benchgraph.dev ───────────────────────────────────────────────────────────

DISPOSITION_BLURB = {
    "active": "This benchmark is in the default catalogue: its identity, protocol, current model "
              "coverage and dated results were verified by a reviewer who opened the sources.",
    "unverified": "This page is not in the default catalogue. Evidence required by the catalogue "
                  "contract is missing or was not approved by a reviewer. That is a statement about "
                  "the evidence we hold, not a claim that the benchmark is stale or illegitimate.",
    "historical": "This benchmark is established, but its qualifying comparison evidence has expired "
                  "or it is too saturated to separate current models. Its history is preserved here.",
    "alias": "This is an alternate identifier for another benchmark, not a separate benchmark.",
    "unassessed": "This page is a discovery lead. Nobody has yet assessed it against the catalogue "
                  "contract, so it carries no disposition. Absence of evidence here is not evidence "
                  "of staleness.",
}


def _safe_link(url: Any, label: Any) -> str:
    """Link only http(s) URLs; anything else renders as escaped plain text."""
    u = str(url or "").strip()
    text = str(label or "").strip() or u
    if u.lower().startswith(("http://", "https://")):
        return f'<a href="{esc(u)}" rel="nofollow noopener">{esc(text)}</a>'
    return esc(text)


GITHUB_BLOB = "https://github.com/turbobeest/modelspec/blob/main/"
_SIBLING_PAGE = re.compile(r"^([a-z0-9][a-z0-9_]{1,80})\.md$")
_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
_INLINE = re.compile(r"`([^`]+)`|\[([^\]]+)\]\(([^)\s]*)\)")
_STRONG = re.compile(r"\*\*(\S(?:.*?\S)?)\*\*")
_EM = re.compile(r"(?<![\w*])\*(\S(?:.*?\S)?)\*(?![\w*])|(?<![\w])_(\S(?:.*?\S)?)_(?![\w])")
_HEADING = re.compile(r"^(#{1,6})(?:\s+(.*?)\s*#*)?\s*$")
_BULLET = re.compile(r"^\s*[-*+]\s+(.*)$")
_NUMBERED = re.compile(r"^\s*\d+[.)]\s+(.*)$")


def _body_href(url: str) -> str | None:
    """Resolve a body link to an absolute http(s) URL, or None to render plain text.

    Absolute http(s) passes through. A sibling benchmark page (`mmlu.md`) links to
    its benchgraph page. Any other repo-relative path resolves against benchmarks/
    to the file on GitHub, the same base as "Edit on GitHub". Other schemes,
    protocol-relative URLs, bare fragments and paths escaping the repo do not link.
    """
    u = url.strip()
    if u.lower().startswith(("http://", "https://")):
        return u
    if not u or u.startswith(("#", "/", "\\")) or _SCHEME.match(u):
        return None
    path, _, frag = u.partition("#")
    sibling = _SIBLING_PAGE.match(path)
    if sibling:
        return f"https://benchgraph.dev/b/{sibling.group(1)}/"
    resolved = posixpath.normpath(posixpath.join("benchmarks", path))
    if not path or resolved.startswith("..") or "\\" in resolved:
        return None
    return GITHUB_BLOB + resolved + (f"#{frag}" if frag else "")


def _emphasis(escaped: str) -> str:
    escaped = _STRONG.sub(r"<strong>\1</strong>", escaped)
    return _EM.sub(lambda m: f"<em>{m.group(1) or m.group(2)}</em>", escaped)


def _inline(text: str) -> str:
    """Escape one run of Markdown text, allowing only code spans, links and emphasis."""
    out: list[str] = []
    pos = 0
    for m in _INLINE.finditer(text):
        out.append(_emphasis(esc(text[pos:m.start()])))
        if m.group(1) is not None:
            out.append(f"<code>{esc(m.group(1))}</code>")
        else:
            href = _body_href(m.group(3))
            out.append(_safe_link(href, m.group(2)) if href else esc(m.group(2)))
        pos = m.end()
    out.append(_emphasis(esc(text[pos:])))
    return "".join(out)


def _norm_heading(text: str) -> str:
    """Case-insensitive, whitespace-collapsed, trailing punctuation stripped."""
    return re.sub(r"\s+", " ", text).strip().rstrip(".:;,!?").strip().lower()


def _body_headings(text: str) -> set[str]:
    """Normalised headings in a body, ignoring lines inside fenced code."""
    out: set[str] = set()
    fenced = False
    for line in (text or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            fenced = not fenced
            continue
        m = None if fenced else _HEADING.match(stripped)
        if m and m.group(2):
            out.add(_norm_heading(m.group(2)))
    return out


def render_markdown_body(text: str) -> str:
    """A minimal, escape-everything Markdown renderer for benchmark page bodies.

    Supports headings, paragraphs, bullet and numbered lists, fenced code, inline
    code, emphasis and links. Authored HTML is always escaped, never passed through.
    Page headings start at h2 because the page title is the h1.
    """
    blocks: list[str] = []
    para: list[str] = []
    items: list[str] = []
    kind = ""
    lines = (text or "").splitlines()

    def flush() -> None:
        nonlocal kind
        if para:
            blocks.append(f"<p>{_inline(' '.join(para))}</p>")
            para.clear()
        if items:
            tag = "ol" if kind == "ol" else "ul"
            blocks.append(f"<{tag}>" + "".join(f"<li>{_inline(i)}</li>" for i in items) + f"</{tag}>")
            items.clear()
        kind = ""

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("```"):
            flush()
            code: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            blocks.append(f"<pre><code>{esc(chr(10).join(code))}</code></pre>")
            i += 1
            continue
        heading = _HEADING.match(stripped)
        bullet = _BULLET.match(line)
        numbered = None if bullet else _NUMBERED.match(line)
        if not stripped:
            flush()
        elif heading:
            flush()
            if heading.group(2):
                level = 2 if len(heading.group(1)) <= 2 else 3
                blocks.append(f"<h{level}>{_inline(heading.group(2))}</h{level}>")
        elif bullet or numbered:
            want = "ul" if bullet else "ol"
            if para or (items and kind != want):
                flush()
            kind = want
            items.append((bullet or numbered).group(1))
        elif items and line[:1] in (" ", "\t"):
            items[-1] += " " + stripped
        else:
            if items:
                flush()
            para.append(stripped)
        i += 1
    flush()
    return "".join(blocks)


def benchmark_links_section(front: dict[str, Any]) -> str:
    """Leaderboard, paper, repo and dated sources for a benchmark page.

    Empty or unset fields render nothing, and so does a section with no rows.
    """
    links: list[str] = []
    lb = str(front.get("leaderboard_url") or "").strip()
    if lb:
        links.append(f"<li>Leaderboard: {_safe_link(lb, lb)}</li>")
    paper = front.get("paper")
    if isinstance(paper, dict):
        title = str(paper.get("title") or "").strip()
        url = str(paper.get("url") or "").strip()
        arxiv = str(paper.get("arxiv") or "").strip()
        if not url and arxiv:
            url = f"https://arxiv.org/abs/{arxiv}"
        if title or url:
            extra = f" (arXiv {esc(arxiv)})" if arxiv else ""
            links.append(f"<li>Paper: {_safe_link(url, title or url)}{extra}</li>")
    repo = str(front.get("repo_url") or "").strip()
    if repo:
        links.append(f"<li>Repository: {_safe_link(repo, repo)}</li>")
    out = _section("Links", f"<ul>{''.join(links)}</ul>" if links else "")

    items: list[str] = []
    sources = front.get("sources")
    for src in sources if isinstance(sources, list) else []:
        if not isinstance(src, dict):
            continue
        url = str(src.get("url") or "").strip()
        title = str(src.get("title") or "").strip()
        if not (url or title):
            continue
        accessed = str(src.get("accessed") or "").strip()
        date_note = f' <span class="meta">read {esc(accessed)}</span>' if accessed else ""
        items.append(f"<li>{_safe_link(url, title or url)}{date_note}</li>")
    return out + _section("Sources", f"<ul>{''.join(items)}</ul>" if items else "",
                          lede="Where each fact on this page came from, and when it was read.")


def benchmark_page(bench: Benchmark, build: Build, catalogue: Catalogue,
                   covered: list[dict[str, Any]]) -> str:
    disposition = catalogue.for_benchmark(bench.benchmark_id)
    status = disposition.status
    blurb = DISPOSITION_BLURB.get(status, DISPOSITION_BLURB["unassessed"])
    notice_class = "notice ok" if status == "active" else "notice"
    reasons = ""
    if disposition.reasons:
        items = "".join(f"<li>{esc(r)}</li>" for r in disposition.reasons)
        reasons = f"<p style='margin-top:8px'>Recorded reasons:</p><ul>{items}</ul>"

    alias_note = ""
    if status == "alias" and disposition.canonical_id != bench.benchmark_id:
        alias_note = (f'<p>Canonical page: <a href="/b/{esc(disposition.canonical_id)}/">'
                      f'{esc(disposition.canonical_id)}</a></p>')

    verified = ""
    if disposition.results:
        rows = "".join(
            f'<tr><td>{esc(r.get("model_id"))}</td>'
            f'<td class="num">{esc(format_score(r.get("score"), r.get("unit")))}</td>'
            f'<td>{esc(r.get("evidence_date"))} '
            f'<span class="pill">{esc(r.get("date_type"))}</span></td>'
            f'<td>{esc(r.get("source_kind"))}</td>'
            f'<td><a href="{esc(r.get("source_url"))}" rel="nofollow noopener">source</a></td></tr>'
            for r in disposition.results
        )
        verified = ('<h2>Verified results</h2><p class="lede">Each row was checked against its '
                    'source by a reviewer.</p><div class="scroll"><table><thead><tr><th>Model</th>'
                    '<th>Score</th><th>Evidence date</th><th>Source kind</th><th>Link</th></tr>'
                    f'</thead><tbody>{rows}</tbody></table></div>')

    covered_block = '<p class="lede">No model card in ModelSpec reports this benchmark yet.</p>'
    if covered:
        rows = "".join(
            f'<tr><td><a href="https://modelspec.dev/m/{esc(c["model_id"])}/">{esc(c["display_name"])}</a></td>'
            f'<td>{esc(c["provider_display"])}</td><td class="num">{esc(c["score"])}</td>'
            f'<td>{esc(c.get("as_of") or "undated")}</td></tr>'
            for c in covered[:200]
        )
        more = (f'<p class="meta">Showing the top 200 of {len(covered)}.</p>'
                if len(covered) > 200 else "")
        covered_block = (
            '<div class="notice">These figures come from the model cards, which carry one '
            'collection date per card and no per-score attribution. They are shown as reported, '
            'not as verified evidence.</div>'
            '<div class="scroll"><table><thead><tr><th>Model</th><th>Provider</th><th>Score</th>'
            f'<th>Card as of</th></tr></thead><tbody>{rows}</tbody></table></div>{more}')

    front = bench.front
    facts = [("Category", front.get("category")), ("Subcategory", front.get("subcategory")),
             ("Page status", front.get("status"))]
    metric = front.get("metric")
    if isinstance(metric, dict):
        facts += [("Metric", metric.get("name")), ("Direction", metric.get("direction")),
                  ("Unit", metric.get("unit")), ("Baseline note", metric.get("baseline_note"))]
    dataset = front.get("dataset")
    if isinstance(dataset, dict):
        facts += [("Dataset size", dataset.get("size")), ("Dataset size note", dataset.get("size_note")),
                  ("Dataset licence", dataset.get("license"))]
    for key, label in (("saturation", "Saturation note"), ("contamination", "Contamination note")):
        block = front.get(key)
        if isinstance(block, dict):
            facts.append((label, block.get("note")))
    publisher = front.get("publisher")
    if isinstance(publisher, dict):
        facts.append(("Publisher", publisher.get("org")))
    fact_rows = "".join(f"<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>"
                        for k, v in facts if v is not None and str(v).strip() not in ("", "[]"))

    measures = str(front.get("measures") or "").strip()
    task = str(front.get("task_format") or "").strip()
    aliases = (f'<p class="meta">Also known as: {esc(", ".join(bench.aliases))}</p>'
               if bench.aliases else "")

    prose = render_markdown_body(bench.body)
    body_headings = _body_headings(bench.body) if prose else set()
    if _norm_heading("What it measures") in body_headings:
        measures = ""
    if _norm_heading("Task format") in body_headings:
        task = ""

    body = f"""
<h1>{esc(bench.name)}</h1>
<p class="lede">{esc(bench.summary)}</p>
{aliases}
<p><span class="pill {esc(status)}">{esc(status)}</span></p>
<div class="{notice_class}">{esc(blurb)}{reasons}{alias_note}</div>
<div class="panel"><table>{fact_rows}</table></div>
{f'<h2>What it measures</h2><p>{esc(measures)}</p>' if measures else ''}
{f'<h2>Task format</h2><p>{esc(task)}</p>' if task else ''}
{f'<div class="prose">{prose}</div>' if prose else ''}
{verified}
{benchmark_links_section(front)}
<h2>Models reporting this benchmark</h2>
{covered_block}
<h2>Data</h2>
<p><a href="/api/benchmarks/{esc(bench.benchmark_id)}.json">This page as JSON</a> &middot;
<a href="https://github.com/turbobeest/modelspec/blob/main/benchmarks/{esc(bench.path.name)}">Edit on GitHub</a></p>
"""
    return shell(
        title=f"{bench.name} — benchgraph",
        description=(bench.summary[:180] or f"{bench.name}: what it measures, who publishes it, and which models report it."),
        canonical=f"https://benchgraph.dev/b/{bench.benchmark_id}/",
        body=body, build=build, site="benchgraph", nav_links=BG_NAV,
        robots="index, follow" if status in {"active", "unverified", "historical"} else "index, follow",
    )


def catalogue_page(benchmarks: list[Benchmark], catalogue: Catalogue, build: Build,
                   coverage: dict[str, list[dict[str, Any]]]) -> str:
    groups: dict[str, list[Benchmark]] = {}
    for bench in benchmarks:
        groups.setdefault(catalogue.for_benchmark(bench.benchmark_id).status, []).append(bench)

    def table(items: list[Benchmark]) -> str:
        rows = "".join(
            f'<tr><td><a href="/b/{esc(b.benchmark_id)}/">{esc(b.name)}</a></td>'
            f'<td class="mono">{esc(b.benchmark_id)}</td>'
            f'<td>{esc(b.category)}</td>'
            f'<td class="num">{len(coverage.get(b.benchmark_id, []))}</td></tr>'
            for b in sorted(items, key=lambda b: b.name.lower())
        )
        return ('<div class="scroll"><table><thead><tr><th>Benchmark</th><th>ID</th>'
                '<th>Category</th>'
                f'<th>Models reporting</th></tr></thead><tbody>{rows}</tbody></table></div>')

    active = groups.get("active", [])
    sections = [
        f'<h2>Active catalogue <span class="pill active">{len(active)}</span></h2>',
        '<p class="lede">Verified against the catalogue contract as of '
        f'{esc(catalogue.as_of.isoformat())}. These are the only benchmarks presented as current.</p>',
        table(active) if active else '<p class="lede">The active set is empty for this build date.</p>',
    ]
    for status, heading, blurb in [
        ("historical", "Historical", "Established benchmarks whose qualifying evidence has expired, or which are too saturated to separate current models."),
        ("unverified", "Unverified", "Assessed, but missing evidence the contract requires, or not yet approved by a reviewer. Not a claim of staleness."),
        ("alias", "Aliases", "Alternate identifiers that resolve to a canonical benchmark."),
        ("unassessed", "Unassessed discovery leads", "Pages nobody has yet assessed against the contract. Reported separately from evaluated dispositions, as the spec requires."),
    ]:
        items = groups.get(status, [])
        if not items:
            continue
        sections += [f'<h2>{heading} <span class="pill {status}">{len(items)}</span></h2>',
                     f'<p class="lede">{blurb}</p>', table(items)]

    body = (f'<h1>The benchmark catalogue</h1><p class="lede">{len(benchmarks)} pages. '
            f'{len(active)} hold active eligibility as of {esc(catalogue.as_of.isoformat())}.</p>'
            + "".join(sections))
    return shell(title="Benchmark catalogue — benchgraph",
                 description=f"{len(benchmarks)} AI benchmark pages, partitioned by whether their evidence supports presenting them as current.",
                 canonical="https://benchgraph.dev/benchmarks/", body=body, build=build,
                 site="benchgraph", nav_links=BG_NAV)


# ── shared furniture ─────────────────────────────────────────────────────────

def sitemap(base: str, paths: Iterable[str], today: date) -> str:
    """Pretty-print so a large catalogue cannot become one 100k+ line.

    Search Console read the 100,405-byte one-line benchgraph sitemap and
    refused the 143,458-byte one-line modelspec sitemap as "could not be
    read". Both were well-formed. A single line over 128 KiB is the
    difference that matches; one URL per line stays far under that.
    """
    lastmod = today.isoformat()
    entries = "\n".join(
        f"<url><loc>{esc(base + p)}</loc><lastmod>{lastmod}</lastmod></url>"
        for p in paths
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n"
        "</urlset>\n"
    )


def not_found(site: str, build: Build, nav: list[tuple[str, str]], home: str) -> str:
    body = ('<h1>Not found</h1><p class="lede">There is no page at this address.</p>'
            f'<p><a href="{esc(home)}">Back to {esc(site)}</a></p>')
    return shell(title=f"Not found — {site}", description="No page at this address.",
                 canonical=home, body=body, build=build, site=site, nav_links=nav,
                 robots="noindex, follow")
