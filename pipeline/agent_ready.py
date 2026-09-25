"""Agent-readiness files for the modelspec.dev tree (MODEL-94).

Called once from `pipeline.build.main` after the pages exist. Adds robots
Content-Signals, favicon.ico, Markdown twins, well-known discovery documents,
JSON-LD, llms-full.txt, and the Pages Function that serves Markdown for
`Accept: text/markdown`. Does not restructure the build.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any, Iterable

from pipeline import brand
from pipeline.export import Build
from pipeline.load import Benchmark, Catalogue, Model, REPO_ROOT

#: Cap for /llms-full.txt. Cloudflare Pages refuses a file over 25 MiB;
#: this is well under that and still fits a typical context window.
LLMS_FULL_CAP = 1_048_576

MS_BASE = "https://modelspec.dev"
RANK_API = "https://api.modelspec.dev/v1/rank"
POLICY_API = "https://api.modelspec.dev/v1/policy-check"
HEALTH_API = "https://api.modelspec.dev/v1/health"
MCP_ENDPOINT = "https://api.modelspec.dev/mcp"
API_DOCS = "https://github.com/turbobeest/modelspec/blob/main/docs/api.md"
POLICY_DOCS = (
    "https://github.com/turbobeest/modelspec/blob/main/docs/api-policy-check.md"
)
MCP_DOCS = "https://github.com/turbobeest/modelspec/blob/main/mcp/README.md"
OPENAPI_URL = f"{MS_BASE}/openapi.yaml"
RFC_9727_PROFILE = "https://www.rfc-editor.org/info/rfc9727"
CONTENT_SIGNALS = "https://contentsignals.org/"
CONTENT_SIGNALS_BLOG = "https://blog.cloudflare.com/content-signals-policy/"
# Agent Skills Discovery RFC v0.2.0 (Cloudflare / agentskills.io). Ticket
# example `/.well-known/skills/` is the older elithrar draft; the current
# index is `/.well-known/agent-skills/index.json`.
SKILLS_SCHEMA = "https://schemas.agentskills.io/discovery/0.2.0/schema.json"
# Agent Readiness (agent-ready.dev) still fetches `/.well-known/mcp.json`
# against this registry schema. SEP-2127's later draft prefers an AI Catalog
# plus `<mcp-url>/server-card` and omits primitives; the ticket wants this
# well-known path and the four tools listed, so they stay.
MCP_SCHEMA = (
    "https://static.modelcontextprotocol.io/schemas/2025-10-17/server.schema.json"
)
MCP_NAME = "dev.modelspec/catalogue"
MCP_NAME_PATTERN = r"^[a-zA-Z0-9.-]+/[a-zA-Z0-9._-]+$"
MCP_DESCRIPTION_MAX = 100
MCP_TOOLS = ("rank", "model_info", "list_use_cases", "policy_check")
_BYTES_WIDTH = 8
PAGES_FILE_LIMIT = 20_000
PAGES_ROUTES = {
    "version": 1,
    "include": ["/*"],
    "exclude": [
        "/api/*",
        "/fonts/*",
        "/graph/vendor/*",
        "/functions/*",
        "/*.png",
        "/*.jpg",
        "/*.jpeg",
        "/*.gif",
        "/*.svg",
        "/*.webp",
        "/*.ico",
        "/*.css",
        "/*.js",
        "/*.mjs",
        "/*.woff",
        "/*.woff2",
        "/*.json",
        "/*.xml",
        "/*.yaml",
        "/*.yml",
        "/*.map",
    ],
}

COST_PER_TOKEN_FIELDS = (
    "input", "output", "reasoning", "cache_read", "cache_write",
    "batch_input", "batch_output",
)

_SKIP_MD_EXT = re.compile(
    r"\.(json|xml|txt|png|jpe?g|gif|svg|webp|ico|css|js|mjs|woff2?|ya?ml|map|html)$",
    re.I,
)
_WRANGLER_FLAG = re.compile(r'"([A-Z0-9_]+)"\s*:\s*"([^"]*)"')


def _dig(front: Any, *keys: str) -> Any:
    node = front
    for key in keys:
        if not isinstance(node, dict):
            return None
        node = node.get(key)
    return node


def _json(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def _script_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True).replace("<", "\\u003c")


def _insert_head(html: str, snippet: str) -> str:
    needle = "</head>"
    idx = html.lower().find(needle)
    if idx == -1 or snippet in html:
        return html
    return html[:idx] + snippet + html[idx:]


def _flag_off(value: str | None) -> bool:
    return (value or "").strip().lower() in {"false", "0", "no", "off", ""}


def wrangler_vars(root: Path) -> dict[str, str]:
    path = root / "api" / "worker" / "wrangler.jsonc"
    if not path.is_file():
        return {}
    return dict(_WRANGLER_FLAG.findall(path.read_text(encoding="utf-8")))


def robots_txt(base: str) -> str:
    """robots.txt with Content Signals.

    Syntax: https://contentsignals.org/ (Cloudflare's publisher AI-use
    preferences; also https://blog.cloudflare.com/content-signals-policy/).
    search / ai-input / ai-train are independent yes|no signals; they do
    not replace Allow/Disallow. Agent Readiness looks for this directive.

    ``ai-train=yes`` is a deliberate choice, confirmed by Jamie on 2026-09-23:
    the catalogue is meant to end up in models' knowledge, so training on it is
    permitted, not merely tolerated. It cannot be withdrawn for anything
    already crawled, which is why it is recorded here rather than left as a
    default. Changing it is his decision.
    """
    return (
        f"# Content-Signal syntax: {CONTENT_SIGNALS}\n"
        f"# (Cloudflare's implementation of publisher AI-use preferences;\n"
        f"#  also {CONTENT_SIGNALS_BLOG}).\n"
        f"# search / ai-input / ai-train are independent yes|no signals for\n"
        f"# how fetched content may be used; they do not replace Allow/Disallow.\n"
        f"User-agent: *\n"
        f"Content-Signal: search=yes, ai-input=yes, ai-train=yes\n"
        f"Allow: /\n"
        f"\n"
        f"Sitemap: {base}/sitemap.xml\n"
    )


def wants_markdown(accept: str | None) -> bool:
    if not accept:
        return False
    for part in accept.split(","):
        bits = [b.strip() for b in part.strip().split(";")]
        if (bits[0] if bits else "").lower() != "text/markdown":
            continue
        q = 1.0
        for param in bits[1:]:
            if param.lower().startswith("q="):
                try:
                    q = float(param[2:])
                except ValueError:
                    q = 0.0
        if q > 0:
            return True
    return False


def markdown_asset_path(pathname: str) -> str | None:
    if not pathname or ".." in pathname:
        return None
    path = pathname.split("?", 1)[0].split("#", 1)[0]
    if path.startswith("/api/") or path == "/api":
        return None
    if path.startswith("/fonts/") or path.startswith("/.well-known/"):
        return None
    if path.endswith(".md"):
        return path
    if _SKIP_MD_EXT.search(path):
        return None
    if path in {"/", ""}:
        return "/index.md"
    if path.endswith("/"):
        return f"{path}index.md"
    return f"{path}/index.md"


def _fmt(value: Any) -> str:
    if value is None or value == "":
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _token_price(front: dict[str, Any]) -> str | None:
    cost = _dig(front, "cost")
    if not isinstance(cost, dict):
        return None
    parts = []
    for field in COST_PER_TOKEN_FIELDS:
        value = cost.get(field)
        if value is not None:
            parts.append(f"{field}={value}")
    return ",".join(parts) if parts else None


def _source_line(label: str, block: Any) -> str | None:
    if isinstance(block, str) and block.strip().startswith("http"):
        return f"- {label}: {block.strip()}"
    if not isinstance(block, dict):
        return None
    url = str(block.get("url") or "").strip()
    if not url:
        return None
    read = str(block.get("read_on") or block.get("accessed") or "").strip()
    kind = str(block.get("kind") or "").strip()
    extra = " ".join(p for p in (kind, read) if p)
    return f"- {label}: {url}" + (f" ({extra})" if extra else "")


def model_facts(model: Model) -> dict[str, Any]:
    front = model.front if isinstance(model.front, dict) else {}
    return {
        "id": model.model_id,
        "name": model.display_name,
        "provider": model.provider,
        "type": front.get("model_type"),
        "context": _dig(front, "modalities", "text", "context_window"),
        "pricing": _token_price(front),
        "licence": _dig(front, "licensing", "license_type"),
        "commercial_use": _dig(front, "licensing", "commercial_use"),
        "url": f"{MS_BASE}/m/{model.model_id}/",
    }


def model_markdown(model: Model) -> str:
    facts = model_facts(model)
    front = model.front if isinstance(model.front, dict) else {}
    lines = [
        f"# {model.display_name}",
        "",
        f"- id: {facts['id']}",
        f"- name: {facts['name']}",
        f"- provider: {_fmt(facts['provider'])}",
        f"- provider_display: {_fmt(model.provider_display)}",
        f"- type: {_fmt(facts['type'])}",
        f"- context: {_fmt(facts['context'])}",
        f"- pricing: {_fmt(facts['pricing'])}",
        f"- licence: {_fmt(facts['licence'])}",
        f"- commercial_use: {_fmt(facts['commercial_use'])}",
        f"- open_weights: {_fmt(_dig(front, 'licensing', 'open_weights'))}",
        f"- release_date: {_fmt(front.get('release_date'))}",
        f"- page: {facts['url']}",
        f"- json: {MS_BASE}/api/models/{model.model_id}.json",
        "",
        "Null means not researched or not published, never a guess.",
        "",
        "## Provenance",
    ]
    try:
        rel = model.path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        rel = model.path.as_posix()
    lines.append(f"- card: https://github.com/turbobeest/modelspec/blob/main/{rel}")
    if model.scores_source:
        lines.append(f"- scores_source: {model.scores_source}")
    if model.scores_as_of:
        lines.append(f"- scores_as_of: {model.scores_as_of}")
    lic_url = _dig(front, "licensing", "license_url")
    if lic_url:
        lines.append(f"- licence_url: {lic_url}")
    src = _source_line("commercial_use", _dig(front, "licensing", "commercial_use_source"))
    if src:
        lines.append(src)
    sources = front.get("sources")
    if isinstance(sources, dict):
        for key, value in sources.items():
            if key.startswith("last_scraped") or not value:
                continue
            read = sources.get(f"last_scraped_{key.removesuffix('_url')}") or ""
            lines.append(f"- {key}: {value}" + (f" (read {read})" if read else ""))
    evidence = _dig(front, "benchmarks", "evidence")
    if isinstance(evidence, list):
        for row in evidence:
            if not isinstance(row, dict):
                continue
            line = _source_line(str(row.get("benchmark_id") or "evidence"), row)
            if line:
                lines.append(line)
    lines += ["", "## Reported scores"]
    if model.scores:
        for key, value in sorted(model.scores.items()):
            lines.append(f"- {key}: {value}")
    else:
        lines.append("null")
    lines.append("")
    return "\n".join(lines)


def provider_markdown(slug: str, models: list[Model]) -> str:
    display = models[0].provider_display if models else slug
    lines = [
        f"# {display}",
        "",
        f"- provider: {slug}",
        f"- models: {len(models)}",
        f"- page: {MS_BASE}/p/{slug}/",
        "",
        "Null means not researched or not published, never a guess.",
        "",
        "## Models",
    ]
    for model in sorted(models, key=lambda m: m.display_name.lower()):
        front = model.front if isinstance(model.front, dict) else {}
        lines.append(
            f"- {model.model_id}: {model.display_name} "
            f"(type: {_fmt(front.get('model_type'))}, "
            f"released: {_fmt(front.get('release_date'))})"
        )
    lines.append("")
    return "\n".join(lines)


def benchmark_markdown(bench: Benchmark, catalogue: Catalogue) -> str:
    from pipeline.render import benchmark_facts

    disposition = catalogue.for_benchmark(bench.benchmark_id)
    lines = [
        f"# {bench.name}",
        "",
        f"- id: {bench.benchmark_id}",
        f"- name: {bench.name}",
        f"- summary: {_fmt(bench.summary or None)}",
        f"- catalogue_status: {disposition.status}",
        f"- page: {MS_BASE}/b/{bench.benchmark_id}/",
        "",
        "Null means not researched or not published, never a guess.",
        "",
        "## Facts",
    ]
    facts = benchmark_facts(bench.front if isinstance(bench.front, dict) else {})
    if facts:
        for label, value in facts:
            lines.append(f"- {label}: {value}")
    else:
        lines.append("null")
    lines += ["", "## Provenance"]
    try:
        rel = bench.path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        rel = bench.path.as_posix()
    lines.append(f"- page_source: https://github.com/turbobeest/modelspec/blob/main/{rel}")
    sources = bench.front.get("sources") if isinstance(bench.front, dict) else None
    found = False
    if isinstance(sources, list):
        for src in sources:
            line = _source_line("source", src)
            if line:
                lines.append(line)
                found = True
    if not found:
        lines.append("- sources: null")
    paper = bench.front.get("paper") if isinstance(bench.front, dict) else None
    paper_line = _source_line("paper", paper) if paper else None
    if paper_line:
        lines.append(paper_line)
    lines.append("")
    return "\n".join(lines)


def modelspec_landing_markdown(models: list[Model], benchmarks: list[Benchmark],
                               build: Build) -> str:
    providers = {m.provider for m in models}
    return (
        f"# ModelSpec\n\n"
        f"> {MS_BASE}\n\n"
        f"Open catalogue of AI models. Null means not researched.\n\n"
        f"- models: {len(models)}\n"
        f"- providers: {len(providers)}\n"
        f"- benchmarks: {len(benchmarks)}\n"
        f"- built: {build.built_at}\n"
        f"- commit: {build.commit}\n"
        f"- eligibility_as_of: {build.as_of.isoformat()}\n"
        f"- html: {MS_BASE}/\n"
        f"- json: {MS_BASE}/api/index.json\n"
        f"- rank: {RANK_API}\n"
        f"- policy-check: {POLICY_API}\n"
        # MODEL-100. The whole class-fit rule as static data, no key: which
        # *class* of model a problem needs, before ranking within one.
        f"- class-fit: {MS_BASE}/api/rank/class-fit.json\n"
        f"- mcp: {MCP_ENDPOINT}\n"
        f"- openapi: {OPENAPI_URL}\n"
        f"- auth: {MS_BASE}/auth.md\n"
        f"- llms: {MS_BASE}/llms.txt\n"
        f"- llms-full: {MS_BASE}/llms-full.txt\n"
        f"\n"
        f"Use class-fit first if you have not decided what *kind* of model the "
        f"problem needs; it names candidate classes and refuses to order them. "
        f"Use rank to shortlist a model for a use case. Use policy-check to "
        f"test a licence/origin/residency/commercial-use policy. "
        f"evidence_basis is input provenance, not a quality verdict.\n"
    )


def model_jsonld(model: Model) -> dict[str, Any]:
    """SoftwareApplication from card fields that exist. No ratings."""
    front = model.front if isinstance(model.front, dict) else {}
    data: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": model.display_name,
        "identifier": model.model_id,
        "url": f"{MS_BASE}/m/{model.model_id}/",
    }
    if model.provider_display:
        data["provider"] = {"@type": "Organization", "name": model.provider_display}
    released = front.get("release_date")
    if released:
        data["datePublished"] = str(released)
    model_type = front.get("model_type")
    if model_type:
        data["applicationSubCategory"] = str(model_type)
    license_url = _dig(front, "licensing", "license_url")
    license_type = _dig(front, "licensing", "license_type")
    if license_url:
        data["license"] = str(license_url)
    elif license_type:
        data["license"] = str(license_type)
    return data


def benchmark_jsonld(bench: Benchmark, catalogue: Catalogue) -> dict[str, Any]:
    data: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": bench.name,
        "identifier": bench.benchmark_id,
        "url": f"{MS_BASE}/b/{bench.benchmark_id}/",
    }
    if bench.summary:
        data["description"] = bench.summary
    status = catalogue.for_benchmark(bench.benchmark_id).status
    data["creativeWorkStatus"] = status
    category = bench.front.get("category") if isinstance(bench.front, dict) else None
    if category:
        data["keywords"] = str(category)
    return data


def modelspec_landing_jsonld(models: list[Model], benchmarks: list[Benchmark]) -> list[dict[str, Any]]:
    return [
        {
            "@context": "https://schema.org",
            "@type": "Dataset",
            "name": "ModelSpec catalogue",
            "url": f"{MS_BASE}/",
            "description": (
                f"{len(models)} model cards and {len(benchmarks)} benchmark pages. "
                "Null means not researched."
            ),
            "license": "https://creativecommons.org/licenses/by-sa/4.0/",
            "creator": {"@type": "Organization", "name": "Sparks and Sawdust LLC"},
            "isAccessibleForFree": True,
            "distribution": [
                {"@type": "DataDownload", "contentUrl": f"{MS_BASE}/api/index.json",
                 "encodingFormat": "application/json"},
                {"@type": "DataDownload", "contentUrl": f"{MS_BASE}/llms-full.txt",
                 "encodingFormat": "text/plain"},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "WebAPI",
            "name": "ModelSpec Rank API",
            "url": RANK_API,
            "documentation": API_DOCS,
            "provider": {"@type": "Organization", "name": "Sparks and Sawdust LLC"},
        },
        {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": "ModelSpec MCP server",
            "url": MCP_ENDPOINT,
            "applicationCategory": "DeveloperApplication",
            "codeRepository": "https://github.com/turbobeest/modelspec",
        },
    ]


def api_catalog() -> dict[str, Any]:
    """RFC 9727 linkset (application/linkset+json)."""
    def entry(anchor: str, doc: str, doc_type: str = "text/html") -> dict[str, Any]:
        item: dict[str, Any] = {
            "anchor": anchor,
            "service-desc": [{"href": OPENAPI_URL, "type": "application/yaml"}],
            "service-doc": [{"href": doc, "type": doc_type}],
        }
        if anchor == RANK_API:
            item["status"] = [{"href": HEALTH_API, "type": "application/json"}]
        return item
    return {
        "linkset": [
            entry(RANK_API, API_DOCS),
            entry(POLICY_API, POLICY_DOCS),
            entry(MCP_ENDPOINT, MCP_DOCS),
        ]
    }


def mcp_card() -> dict[str, Any]:
    """SEP-2127 / Agent Readiness card at /.well-known/mcp.json.

    Schema (2025-10-17): name, description (<=100 chars), version, remotes.
    `tools` is extra; draft-07 additionalProperties default to true, and the
    ticket requires the four MCP tools named here.
    """
    description = (
        "Rank models, inspect cards, list use cases, and check policy."
    )
    if len(description) > MCP_DESCRIPTION_MAX:
        raise ValueError("MCP description exceeds schema maxLength 100")
    return {
        "$schema": MCP_SCHEMA,
        "name": MCP_NAME,
        "title": "ModelSpec",
        "description": description,
        "version": "1.0.0",
        "websiteUrl": MS_BASE,
        "repository": {
            "url": "https://github.com/turbobeest/modelspec",
            "source": "github",
        },
        "remotes": [{"type": "streamable-http", "url": MCP_ENDPOINT}],
        "tools": [
            {"name": "rank",
             "description": "POST /v1/rank. Shortlist models for a use case."},
            {"name": "model_info",
             "description": "GET a model card as JSON from the public export."},
            {"name": "list_use_cases",
             "description": "GET /api/rank/profiles.json ranking profiles."},
            {"name": "policy_check",
             "description": "POST /v1/policy-check. pass/fail/undetermined."},
        ],
    }


def skill_markdown() -> str:
    from api.ranking.engine import (
        HONEST_BROKER_RULE,
        NEUTRALITY_PLEDGE,
        neutrality_commitment,
    )

    n = neutrality_commitment()
    return (
        "---\n"
        "name: modelspec\n"
        "description: >\n"
        "  Use ModelSpec when choosing, switching, or checking an AI model.\n"
        "  Call rank for a shortlist, policy-check for licence/origin/residency\n"
        "  /commercial-use, and the MCP server for the same tools. Null means\n"
        "  not researched. evidence_basis is provenance, not quality.\n"
        "---\n"
        "\n"
        "# ModelSpec\n"
        "\n"
        "Catalogue of AI models and benchmarks at https://modelspec.dev. "
        "The rank Worker is https://api.modelspec.dev. "
        "Null on a card means not researched or not published, never a guess. "
        "Every sourced value carries a URL and a read date.\n"
        "\n"
        "## When to call what\n"
        "\n"
        "- **rank** (`POST https://api.modelspec.dev/v1/rank`) — shortlist "
        "models for a use case, hardware, hosting and constraints. Required "
        "field: `use_case`. No prompt. Free; no key required while "
        "`ACCESS_ENFORCED` is off.\n"
        "- **policy-check** (`POST https://api.modelspec.dev/v1/policy-check`) "
        "— pass / fail / undetermined per model and per platform against a "
        "caller's licence, origin, residency and commercial-use policy. Use "
        "this when the question is compliance, not quality. Without a paid "
        "key it answers from the public export; undetermined is not a pass.\n"
        "- **MCP** (`https://api.modelspec.dev/mcp`) — Streamable HTTP. Tools: "
        + ", ".join(MCP_TOOLS)
        + ". Same origins as the HTTP API. No key.\n"
        "- Do not call rank to answer a policy question, and do not treat a "
        "rank score as a licence determination.\n"
        "\n"
        "## evidence_basis\n"
        "\n"
        "Per ranked row: `none`, `unverified-legacy`, `mixed`, "
        "`partial-verified`, `verified`. This is input provenance of the "
        "scores that contributed, not a quality certificate. `verified` "
        "means the contributing scores have dated sources, not that the "
        "model is good.\n"
        "\n"
        "## Neutrality\n"
        "\n"
        f"{HONEST_BROKER_RULE}\n"
        "\n"
        f"{NEUTRALITY_PLEDGE}\n"
        "\n"
        f"Operator: {n['operator']}. Machine-readable commitment: "
        f"{MS_BASE}/api/rank/profiles.json (`neutrality`). "
        f"Terms: {n['terms_url']}. Privacy: {n['privacy_url']}.\n"
        "\n"
        "## Discovery\n"
        "\n"
        f"- OpenAPI: {OPENAPI_URL}\n"
        f"- API catalog (RFC 9727): {MS_BASE}/.well-known/api-catalog\n"
        f"- MCP card (SEP-2127): {MS_BASE}/.well-known/mcp.json\n"
        f"- Auth: {MS_BASE}/auth.md\n"
        f"- llms.txt: {MS_BASE}/llms.txt\n"
        f"- Markdown: send `Accept: text/markdown` or fetch `<page>/index.md`\n"
    )


def skills_index(skill_bytes: bytes, url: str, description: str) -> dict[str, Any]:
    digest = "sha256:" + hashlib.sha256(skill_bytes).hexdigest()
    return {
        "$schema": SKILLS_SCHEMA,
        "skills": [
            {
                "name": "modelspec",
                "type": "skill-md",
                "description": description,
                "url": url,
                "digest": digest,
            }
        ],
    }


def skill_description() -> str:
    return (
        "Use ModelSpec when choosing, switching, or checking an AI model. "
        "Call rank for a shortlist, policy-check for licence/origin/residency"
        "/commercial-use, and the MCP server for the same tools. Null means "
        "not researched. evidence_basis is provenance, not quality."
    )


def auth_markdown(root: Path) -> str:
    flags = wrangler_vars(root)
    access_off = _flag_off(flags.get("ACCESS_ENFORCED"))
    billing_off = _flag_off(flags.get("BILLING_ENABLED"))
    x402_off = _flag_off(flags.get("X402_ENABLED"))
    lines = [
        # Cloudflare Agent Readiness expects the document to open with an
        # "Auth.md" heading; it reported the old title as missing it.
        "# Auth.md",
        "",
        "How an agent gets access to ModelSpec.",
        "",
        "The rank and policy-check APIs live at `https://api.modelspec.dev`. "
        "Present a key with `Authorization: Bearer <key>` or `X-API-Key`. "
        "A key is never read from the query string.",
        "",
        "## What is live",
        "",
    ]
    if access_off:
        lines.append(
            "**No key is required.** `ACCESS_ENFORCED` in the Worker is off. "
            "A request without a key is served as the free tier, unmetered. "
            "A request that presents a key is checked: unknown and revoked "
            "keys are refused rather than ignored."
        )
    else:
        lines.append(
            "**A key is required.** `ACCESS_ENFORCED` is on. A request "
            "without a key is `401 missing_api_key`."
        )
    lines += [
        "",
        "### Free tier (no key)",
        "",
        "- `POST /v1/rank` — live catalogue, no signup.",
        "- `POST /v1/policy-check` — live catalogue public fields. "
        "Checks that need the private determination store stay "
        "`undetermined` with `why: tier`. That is not a pass.",
        "- `GET /v1/health` — deploy pin.",
        "- MCP `https://api.modelspec.dev/mcp` — the four tools, no key.",
        "",
        "### Sandbox (`test_` keys)",
        "",
        "Any key beginning `test_` is unlimited and is answered from the "
        "sandbox. No signup, no key store, no published export. Rank only; "
        "`POST /v1/policy-check` with a `test_` key is `400 sandbox_not_available`. "
        "Rows are synthetic, from the real scorer, not live catalogue data.",
        "",
        "## What is not live",
        "",
    ]
    if billing_off:
        lines.append(
            "**Billing is not live.** `BILLING_ENABLED` is off. "
            "`POST /v1/billing/checkout` returns `503 billing_not_enabled`, "
            "so there is no paid key you can buy today. A key bought "
            "earlier keeps working and keeps its credits; claim and "
            "rotation still answer for it."
        )
    else:
        lines.append(
            "Billing is enabled. See `/pricing` and `docs/billing.md`."
        )
    if x402_off:
        lines.append("")
        lines.append(
            "**x402 prepaid credits are not live.** `X402_ENABLED` is off."
        )
    lines += [
        "",
        "OpenAPI: " + OPENAPI_URL,
        "Human docs: " + API_DOCS,
        "",
    ]
    return "\n".join(lines)


def _catalogue_digest(title: str, blocks: Iterable[str], *, cap: int,
                      unit: str) -> tuple[str, dict[str, int]]:
    """Single-file digest. Header states cap_bytes and the final byte count."""
    zeros = "0" * _BYTES_WIDTH
    header = f"# {title}\n# cap_bytes: {cap}\n# bytes: {zeros}\n"
    reserve = 180
    budget = cap - len(header.encode("utf-8")) - reserve
    kept: list[str] = []
    used = 0
    included = 0
    omitted = 0
    block_list = list(blocks)
    for i, block in enumerate(block_list):
        size = len(block.encode("utf-8"))
        if used + size > budget:
            omitted = len(block_list) - i
            break
        kept.append(block)
        used += size
        included += 1
    note = (
        f"# truncated: {omitted} {unit} omitted (cap {cap} bytes)\n"
        if omitted else ""
    )
    body = (header + note + "\n".join(kept)).rstrip() + "\n"
    encoded = body.encode("utf-8")
    if len(encoded) > cap:
        body = encoded[: max(cap - 1, 0)].decode("utf-8", errors="ignore")
        if not body.endswith("\n"):
            body = body[: max(len(body) - 1, 0)] + "\n"
    size = len(body.encode("utf-8"))
    body = body.replace(f"# bytes: {zeros}", f"# bytes: {size:0{_BYTES_WIDTH}d}", 1)
    size = len(body.encode("utf-8"))
    return body, {"bytes": size, "cap": cap, "included": included, "omitted": omitted}


def _model_blocks(models: Iterable[Model]) -> list[str]:
    blocks = []
    for model in models:
        facts = model_facts(model)
        blocks.append(
            f"## {facts['id']}\n"
            f"name: {facts['name']}\n"
            f"provider: {_fmt(facts['provider'])}\n"
            f"type: {_fmt(facts['type'])}\n"
            f"context: {_fmt(facts['context'])}\n"
            f"pricing: {_fmt(facts['pricing'])}\n"
            f"licence: {_fmt(facts['licence'])}\n"
            f"commercial_use: {_fmt(facts['commercial_use'])}\n"
            f"url: {facts['url']}\n"
        )
    return blocks


def _benchmark_blocks(benchmarks: Iterable[Benchmark], catalogue: Catalogue) -> list[str]:
    blocks = []
    for bench in benchmarks:
        status = catalogue.for_benchmark(bench.benchmark_id).status
        category = bench.front.get("category") if isinstance(bench.front, dict) else None
        blocks.append(
            f"## {bench.benchmark_id}\n"
            f"name: {bench.name}\n"
            f"category: {_fmt(category)}\n"
            f"status: {status}\n"
            f"url: {MS_BASE}/b/{bench.benchmark_id}/\n"
        )
    return blocks


def llms_full_models(models: Iterable[Model], *, cap: int = LLMS_FULL_CAP) -> tuple[str, dict[str, int]]:
    return _catalogue_digest("ModelSpec catalogue digest", _model_blocks(models), cap=cap, unit="models")


def llms_full_benchmarks(benchmarks: Iterable[Benchmark], catalogue: Catalogue,
                         *, cap: int = LLMS_FULL_CAP) -> tuple[str, dict[str, int]]:
    return _catalogue_digest(
        "Benchmark catalogue digest", _benchmark_blocks(benchmarks, catalogue),
        cap=cap, unit="benchmarks")


def llms_full(models: Iterable[Model], benchmarks: Iterable[Benchmark], catalogue: Catalogue,
              *, cap: int = LLMS_FULL_CAP) -> tuple[str, dict[str, int]]:
    """One digest: model cards, then benchmark pages, under the same cap."""
    blocks = _model_blocks(models) + _benchmark_blocks(benchmarks, catalogue)
    return _catalogue_digest("ModelSpec catalogue digest", blocks, cap=cap, unit="records")


def _write_favicon(tree: Path) -> int:
    brand.write_icons(tree)
    return (tree / "favicon.ico").stat().st_size


def _copy_functions(root: Path, tree: Path) -> None:
    src = root / "site" / "functions"
    if not src.is_dir():
        return
    dest = tree / "functions"
    dest.mkdir(parents=True, exist_ok=True)
    middleware = src / "_middleware.js"
    worker = src / "_worker.js"
    if middleware.is_file():
        shutil.copy2(middleware, dest / "_middleware.js")
    if worker.is_file():
        shutil.copy2(worker, tree / "_worker.js")
    (tree / "_routes.json").write_text(
        json.dumps(PAGES_ROUTES, indent=2) + "\n", encoding="utf-8")


def _head_for(md_href: str, json_ld: list[dict[str, Any]] | dict[str, Any] | None = None) -> str:
    parts = [
        f'<link rel="alternate" type="text/markdown" href="{md_href}">\n',
        '<link rel="icon" href="/favicon.ico">\n',
    ]
    payloads = json_ld if isinstance(json_ld, list) else ([json_ld] if json_ld else [])
    for payload in payloads:
        parts.append(
            f'<script type="application/ld+json">{_script_json(payload)}</script>\n'
        )
    return "".join(parts)


def _write_md(path: Path, text: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = text if text.endswith("\n") else text + "\n"
    path.write_text(data, encoding="utf-8")
    return len(data.encode("utf-8"))


def ship(*, root: Path, ms: Path, models: list[Model],
         benchmarks: list[Benchmark], catalogue: Catalogue, build: Build,
         by_provider: dict[str, list[Model]]) -> dict[str, Any]:
    """Write every MODEL-94 artifact into the modelspec.dev tree."""
    ms_fav = _write_favicon(ms)
    _copy_functions(root, ms)

    (ms / "robots.txt").write_text(robots_txt(MS_BASE), encoding="utf-8")

    openapi_src = root / "api" / "worker" / "openapi.yaml"
    if openapi_src.is_file():
        shutil.copy2(openapi_src, ms / "openapi.yaml")

    well = ms / ".well-known"
    well.mkdir(parents=True, exist_ok=True)
    (well / "api-catalog").write_text(_json(api_catalog()), encoding="utf-8")
    (well / "mcp.json").write_text(_json(mcp_card()), encoding="utf-8")

    skill_text = skill_markdown()
    skill_bytes = skill_text.encode("utf-8")
    skill_dir = well / "agent-skills" / "modelspec"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_bytes(skill_bytes)
    index = skills_index(
        skill_bytes,
        "/.well-known/agent-skills/modelspec/SKILL.md",
        skill_description(),
    )
    (well / "agent-skills" / "index.json").write_text(_json(index), encoding="utf-8")
    (ms / "auth.md").write_text(auth_markdown(root), encoding="utf-8")

    md_count = 0
    md_count += 1 if _write_md(ms / "index.md", modelspec_landing_markdown(models, benchmarks, build)) else 0
    for model in models:
        _write_md(ms / "m" / model.model_id / "index.md", model_markdown(model))
        md_count += 1
    for slug, group in by_provider.items():
        _write_md(ms / "p" / slug / "index.md", provider_markdown(slug, group))
        md_count += 1
    for bench in benchmarks:
        _write_md(ms / "b" / bench.benchmark_id / "index.md",
                  benchmark_markdown(bench, catalogue))
        md_count += 1

    ms_index = ms / "index.html"
    if ms_index.is_file():
        ms_index.write_text(
            _insert_head(ms_index.read_text(encoding="utf-8"),
                         _head_for("/index.md", modelspec_landing_jsonld(models, benchmarks))),
            encoding="utf-8")
    for model in models:
        page = ms / "m" / model.model_id / "index.html"
        if page.is_file():
            page.write_text(
                _insert_head(page.read_text(encoding="utf-8"),
                             _head_for(f"/m/{model.model_id}/index.md", model_jsonld(model))),
                encoding="utf-8")
    for slug in by_provider:
        page = ms / "p" / slug / "index.html"
        if page.is_file():
            page.write_text(
                _insert_head(page.read_text(encoding="utf-8"),
                             _head_for(f"/p/{slug}/index.md")),
                encoding="utf-8")
    for bench in benchmarks:
        page = ms / "b" / bench.benchmark_id / "index.html"
        if page.is_file():
            page.write_text(
                _insert_head(page.read_text(encoding="utf-8"),
                             _head_for(f"/b/{bench.benchmark_id}/index.md",
                                       benchmark_jsonld(bench, catalogue))),
                encoding="utf-8")

    full, full_stats = llms_full(models, benchmarks, catalogue)
    (ms / "llms-full.txt").write_text(full, encoding="utf-8")

    extra = (
        f"- Catalogue digest: {MS_BASE}/llms-full.txt\n"
        f"- Auth: {MS_BASE}/auth.md\n"
        f"- MCP card: {MS_BASE}/.well-known/mcp.json\n"
    )
    llms = ms / "llms.txt"
    if llms.is_file():
        text = llms.read_text(encoding="utf-8")
        if extra.strip() not in text:
            llms.write_text(text.rstrip() + "\n" + extra, encoding="utf-8")

    return {
        "markdown_pages": md_count,
        "favicon_bytes": ms_fav,
        "llms_full": full_stats,
        "skill_bytes": len(skill_bytes),
        "openapi_published": (ms / "openapi.yaml").is_file(),
    }
