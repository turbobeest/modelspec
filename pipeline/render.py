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
from collections.abc import Collection, Iterable
from datetime import date
from pathlib import Path
from typing import Any

from pipeline.export import Build
from pipeline.load import Benchmark, Catalogue, Model

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" '
         'href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/'
         'css2?family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">')

CSS = """
:root{--ink:#f3f4f6;--mute:#9aa3b2;--dim:#5b6472;--ground:#000;--panel:#0b0e14;
--line:#1f2430;--amber:#f5b342;--good:#34d399;--warn:#fbbf24;--off:#6b7280}
*{box-sizing:border-box}
html{color-scheme:dark}
body{margin:0;background:var(--ground);color:var(--ink);
font-family:"Space Grotesk",ui-sans-serif,system-ui,"Helvetica Neue",Arial,sans-serif;
font-size:17px;line-height:1.6;-webkit-font-smoothing:antialiased}
a{color:var(--ink);text-decoration:underline;text-decoration-color:var(--dim);text-underline-offset:3px}
a:hover{text-decoration-color:var(--amber)}
:focus-visible{outline:2px solid var(--amber);outline-offset:3px;border-radius:4px}
.wrap{max-width:1100px;margin:0 auto;padding:0 24px}
nav{display:flex;align-items:center;justify-content:space-between;padding:22px 0 8px;
border-bottom:1px solid var(--line);margin-bottom:28px;flex-wrap:wrap;gap:12px}
nav .brand{font-weight:700;font-size:18px;letter-spacing:-.02em;text-decoration:none}
nav .links{display:flex;gap:20px;font-size:15px;flex-wrap:wrap}
nav .links a{color:var(--mute);text-decoration:none}
nav .links a:hover{color:var(--ink)}
h1{font-size:34px;line-height:1.2;letter-spacing:-.02em;margin:0 0 6px}
h2{font-size:21px;margin:34px 0 10px;letter-spacing:-.01em}
h3{font-size:17px;margin:22px 0 6px}
p{margin:0 0 12px}
.lede{color:var(--mute);font-size:18px;margin-bottom:18px}
.meta{color:var(--dim);font-size:14px;font-family:"JetBrains Mono",ui-monospace,monospace}
code,.mono{font-family:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace;font-size:14px}
table{width:100%;border-collapse:collapse;margin:10px 0 18px;font-size:15px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--mute);font-weight:500;font-size:13px;text-transform:uppercase;letter-spacing:.04em}
td.num{text-align:right;font-family:"JetBrains Mono",ui-monospace,monospace}
.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin:14px 0}
.pill{display:inline-block;font-size:12px;padding:2px 9px;border-radius:999px;
border:1px solid var(--line);color:var(--mute);margin-right:6px;font-family:"JetBrains Mono",ui-monospace,monospace}
.pill.active{color:var(--good);border-color:#14532d}
.pill.unverified{color:var(--warn);border-color:#422006}
.pill.alias{color:var(--mute)}
.pill.unassessed{color:var(--off)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:13px 15px}
.card a{text-decoration:none;font-weight:700}
.card .sub{color:var(--dim);font-size:13px;margin-top:3px}
ul.cols{columns:3;column-gap:26px;padding-left:18px}
@media(max-width:800px){ul.cols{columns:1}h1{font-size:27px}}
footer{margin:56px 0 34px;padding-top:18px;border-top:1px solid var(--line);color:var(--dim);font-size:14px}
.notice{border-left:3px solid var(--warn);padding:10px 14px;background:#0f0c04;margin:14px 0;font-size:15px}
.notice.ok{border-left-color:var(--good);background:#04120c}
"""


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
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(canonical)}">
<meta name="robots" content="{esc(robots)}">
<meta name="theme-color" content="#000000">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(canonical)}">
<meta name="generator" content="modelspec-pipeline {esc(build.commit[:12])}">
{FONTS}
<style>{CSS}</style></head>
<body><div class="wrap">
<nav><a class="brand" href="/">{esc(site)}</a><div class="links">{links}</div></nav>
{body}
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


def lineage_section(relations: Any, pages: Collection[str] | None = None) -> str:
    rows = []
    for entry in relations.ancestors:
        relation = str(entry.get("relation") or "").strip()
        phrase = f"Is a <strong>{esc(relation)}</strong> of" if relation else "Derived from"
        rows.append(f'<tr><td>{phrase}</td>'
                    f'<td>{model_anchor(str(entry["id"]), str(entry["name"]), pages)}</td></tr>')
    for entry in relations.descendants:
        relation = str(entry.get("relation") or "").strip()
        phrase = (f"Is the base of this <strong>{esc(relation)}</strong>"
                  if relation else "Is the base of")
        rows.append(f'<tr><td>{phrase}</td>'
                    f'<td>{model_anchor(str(entry["id"]), str(entry["name"]), pages)}</td></tr>')
    return _section("Lineage", _table(["Relationship", "Model"], rows))


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


def hardware_section(relations: Any) -> str:
    rows = []
    for entry in relations.hardware:
        device = entry.get("device") or {}
        bandwidth = device.get("memory_bandwidth_gb_s")
        rows.append(
            f'<tr><td>{esc(entry["name"])}</td>'
            f'<td class="num">{esc(entry.get("device_memory_gb"))} GB</td>'
            f'<td class="num">{esc(bandwidth)} GB/s</td>'
            f'<td>{esc(entry.get("quantization"))}</td>'
            f'<td class="num">{esc(entry.get("weights_gb"))} GB</td>'
            f'<td class="num">~{esc(entry.get("predicted_decode_tps"))}</td>'
            f'<td class="num">~{esc(entry.get("fastest_predicted_decode_tps"))} '
            f'<span class="mono" style="color:var(--dim)">{esc(entry.get("fastest_quantization"))}</span></td></tr>')
    if not rows:
        return ""
    moe = any(e.get("moe_prediction_is_conservative") for e in relations.hardware)
    caveat = (" This is a mixture-of-experts model and no card carries active-parameter "
              "counts, so these predictions use total parameters and understate the real "
              "speed." if moe else "")
    note = ('<div class="notice">Every figure here is <strong>computed</strong>, not measured. '
            'Fit is weights at each quantisation against device memory, with a 25% allowance '
            'for the KV cache, activations and the OS. Decode rate is the memory-bandwidth '
            'roofline at 70% efficiency. Nobody has run this model on these devices.'
            + esc(caveat) + '</div>')
    return _section(
        "What it fits on",
        note + _table(["Device", "Memory", "Bandwidth", "Best quality",
                       "Weights", "tok/s", "Fastest"], rows),
        "Ordered by predicted speed. Bandwidth sets decode rate; memory decides whether it runs at all.")


def capabilities_section(relations: Any) -> str:
    if not relations.capabilities:
        return ""
    pills = " ".join(
        f'<span class="pill">{esc(str(e["name"]))}'
        + (f' &middot; {esc(e["tier"])}' if e.get("tier") else "") + "</span>"
        for e in relations.capabilities)
    return _section("Capabilities", f"<p>{pills}</p>")


def competitors_section(relations: Any, pages: Collection[str] | None = None) -> str:
    rows = []
    for entry in relations.competitors[:12]:
        rows.append(
            f'<tr><td>{model_anchor(str(entry["id"]), str(entry["name"]), pages)}</td>'
            f'<td class="num">{esc(entry.get("overlap_score"))}</td>'
            f'<td>{esc(entry.get("computed_date"))}</td></tr>')
    if not rows:
        return ""
    note = ('<div class="notice">Derived, not authored. Two models compete if they share a '
            'type, sit within 3x on parameters, and report at least one benchmark in common; '
            'the score is the overlap of their capability sets. The shared-benchmark test '
            'rests on card scores that carry one date per card and no per-score source.</div>')
    return _section("What competes with it",
                    note + _table(["Model", "Capability overlap", "Derived"], rows))


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


def model_page(model: Model, build: Build, benchmarks: dict[str, Benchmark],
               catalogue: Catalogue, relations: Any = None,
               pages: Collection[str] | None = None) -> str:
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

    identity = [
        ("Provider", model.provider_display),
        ("Family", front.get("family")),
        ("Type", front.get("model_type")),
        ("Status", front.get("status")),
        ("Released", front.get("release_date")),
        ("Updated", front.get("last_updated")),
        ("Parameters", human_count(front["architecture"]["total_parameters"])
         if isinstance(front.get("architecture"), dict)
         and front["architecture"].get("total_parameters") else None),
        ("Open weights", ("yes" if front["licensing"].get("open_weights") else None)
         if isinstance(front.get("licensing"), dict) else None),
    ]
    id_rows = "".join(
        f"<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in identity if v not in (None, "", [])
    )

    rel = relations
    sections = ""
    if rel is not None:
        sections = (lineage_section(rel, pages) + capabilities_section(rel)
                    + hardware_section(rel) + platforms_section(rel)
                    + competitors_section(rel, pages))

    unresearched = ""
    if rel is not None and rel.is_empty:
        unresearched = ('<div class="notice">Nothing beyond the card\'s own fields has been '
                        'researched for this model yet — no lineage, platforms, capabilities or '
                        'hardware fit. That is a gap in the data, not a statement about the '
                        'model.</div>')

    body = f"""
<h1>{esc(model.display_name)}</h1>
<p class="lede">{esc(model.provider_display)} &middot; <span class="mono">{esc(model.model_id)}</span></p>
<div class="panel"><table>{id_rows}</table></div>
{unresearched}
{sections}
{evidence_section(model)}
<h2>Reported benchmark scores</h2>
{stale if scores else '<p class="lede">This card reports no benchmark scores yet.</p>'}
<div class="scroll"><table>
<thead><tr><th>Benchmark</th><th>Catalogue standing</th><th>Score</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
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
                  ("Unit", metric.get("unit"))]
    dataset = front.get("dataset")
    if isinstance(dataset, dict):
        facts += [("Dataset size", dataset.get("size")), ("Dataset licence", dataset.get("license"))]
    publisher = front.get("publisher")
    if isinstance(publisher, dict):
        facts.append(("Publisher", publisher.get("org")))
    fact_rows = "".join(f"<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>"
                        for k, v in facts if v not in (None, "", []))

    measures = str(front.get("measures") or "").strip()
    task = str(front.get("task_format") or "").strip()
    aliases = (f'<p class="meta">Also known as: {esc(", ".join(bench.aliases))}</p>'
               if bench.aliases else "")

    body = f"""
<h1>{esc(bench.name)}</h1>
<p class="lede">{esc(bench.summary)}</p>
{aliases}
<p><span class="pill {esc(status)}">{esc(status)}</span></p>
<div class="{notice_class}">{esc(blurb)}{reasons}{alias_note}</div>
<div class="panel"><table>{fact_rows}</table></div>
{f'<h2>What it measures</h2><p>{esc(measures)}</p>' if measures else ''}
{f'<h2>Task format</h2><p>{esc(task)}</p>' if task else ''}
{verified}
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
    urls = "".join(
        f"<url><loc>{esc(base + p)}</loc><lastmod>{today.isoformat()}</lastmod></url>"
        for p in paths
    )
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')


def not_found(site: str, build: Build, nav: list[tuple[str, str]], home: str) -> str:
    body = ('<h1>Not found</h1><p class="lede">There is no page at this address.</p>'
            f'<p><a href="{esc(home)}">Back to {esc(site)}</a></p>')
    return shell(title=f"Not found — {site}", description="No page at this address.",
                 canonical=home, body=body, build=build, site=site, nav_links=nav,
                 robots="noindex, follow")
