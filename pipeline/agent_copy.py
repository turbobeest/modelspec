"""What an agent reads before it decides to call ModelSpec (MODEL-257).

    python -m pipeline.agent_copy write     # regenerate MCP copy, guide and Worker constants
    python -m pipeline.agent_copy check     # exit 1 if the committed file is stale

The compact guide, the MCP server's `instructions` and every tool description, the MCP card's tool
lines and the OpenAPI summaries for the paid endpoints all come from here. The
MCP server is TypeScript, so it reads the generated JSON rather than this
module; `tests/test_agent_copy.py` fails if that file is edited by hand or
falls behind this module, the entity registry or `api/worker/tiers.json`.

Every paid tool description says four things, in this order: the question it
answers, what it returns, that it needs a key and what it costs, and when not
to call it. Prices are read from `tiers.json`, never typed. Nothing here
mentions a payment rail that is switched off.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

from pipeline import entity, worker_flags

ROOT = Path(__file__).resolve().parents[1]
TIERS = ROOT / "api" / "worker" / "tiers.json"
OUT = ROOT / "mcp" / "src" / "agent-copy.json"
API = "https://api.modelspec.dev"
PRICING = f"{entity.SITE}/pricing/"

NULL_RULE = (
    "Null means not researched or not published, never a guess. "
    "Every sourced value on a card carries a URL and a read date. "
    "This tool returns the origin's JSON plus the origin URL; it does not invent fields."
)
GUIDE_URL = f"{entity.SITE}/agents.md"
GUIDE_OUT = ROOT / "docs" / "agents.md"
GUIDE_CONSTANTS = ROOT / "api" / "worker" / "src" / "agent_guide.py"
CLI_OUT = ROOT / "cli" / "modelspec" / "agent-bundle.json"
CLI_SCHEMA = ROOT / "cli" / "modelspec" / "spec.schema.json"
CLI_FEEDBACK_SCHEMA = ROOT / "cli" / "modelspec" / "feedback.schema.json"
INSTALL_PATHS = (
    "uvx --from modelspec-dev modelspec",
    "pipx install modelspec-dev",
    "pip install modelspec-dev",
)
PACKAGE_WARNING = "pip install modelspec is an unrelated project. Use modelspec-dev."
ACCESS = (
    "Three ways in: keyed CLI, MCP and HTTP API. "
    "Machine data access needs a ModelSpec API key; only human lookup is free. "
    "No data download or local decision cache."
)
CLI_PRIVACY = "No telemetry. The CLI never uses, sends or logs your provider API keys."
# MODEL-320. One sentence per rule. The guide, tool descriptions, OpenAPI lead,
# llms.txt and CLI help all quote this tuple.
CONDUCT_RULES = (
    "Never add a gate or constraint the user didn't state.",
    "Relax only constraints the user stated, one at a time, and say what was relaxed and why. Prefer the answer's own `relax` suggestions.",
    "A tie stays a tie. Don't promote a member by knowledge from outside the response.",
    "Cite only evidence in the response. Never add benchmark figures from memory.",
    "Tied or partial answer: report the tie and caveats, pick no member; a null answer names no pick and says what's missing.",
    'A null cost is unknown. Never show it as $0.00 or "free".',
    "One vocabulary lookup per unknown facet, then decide. Read `next` before another call.",
    "Size `task_tokens` from the user's own task, and say what you assumed. Don't copy the guide's example sizes.",
)
# MODEL-339. One sentence, quoted by the MCP instructions, the decide and rank
# tool descriptions, the guide, and CLI `modelspec help agent`. Not a conduct
# rule: those eight stay a closed list.
SUMMARY_RULE = (
    "Present `summary_for_user` to the user unchanged and keep every `must_mention` item."
)
SPEC_GUIDANCE = (
    "Call decide early with a template-based Spec; refine from reading and recovery hints. "
    "Put Musts in where: these gates exclude. Put Prefers in optimize.weights: weights rank "
    "and never exclude. Unknown values go to may_qualify. Pin snapshot for reproducibility. "
)
REPORTING_RULES = (
    " ".join(CONDUCT_RULES) + " "
    "Template weights are examples, not requirements. If the evidence basis or board does not match "
    "the task, say so: Arena web-dev evidence does not establish chat quality. "
    "p_best is the probability of ranking best under the Spec and evidence uncertainty, "
    "not the probability of matching the user's task or satisfying its requirements. "
    "Read reading when present. Present answer.kind=tied among all answer.members, including "
    "with_estate; tie-breakers are conditional. State requirements in reading.not_applied or "
    "error.issues that were not applied, including requirements removed after a rejected "
    "call. A retry does not verify them. Report estimates as estimates: fits_hardware "
    "membership is not measured fit for a specific quantization and context workload. "
    "Follow reading.do_not_claim. Never claim a rank the response does not show. "
    f"{SUMMARY_RULE} "
)
MINIMAL_SPEC = {"spec_version": 1, "optimize": {"min": "offering.cost_per_task"}}
VOCAB_NEXT = {
    "starter": "next: call decide with this; refine from reading",
    "lookup": "next: call decide using these ids; refine from reading",
    "empty": "next: retry vocab with one of the suggestions",
}


def install_markdown() -> str:
    return (ACCESS + "\n\n```sh\n" + "\n".join(INSTALL_PATHS) + "\n```\n\n" +
            PACKAGE_WARNING + f"\nGuide: {GUIDE_URL}. Pricing and keys: {PRICING}.\n")


def install_html() -> str:
    import html
    return (f"<p>{html.escape(ACCESS)}</p><pre>" +
            "\n".join(html.escape(command) for command in INSTALL_PATHS) +
            f"</pre><p>{html.escape(PACKAGE_WARNING)}</p>")


def key_procurement(root: Path = ROOT) -> str:
    variables = worker_flags.production_vars(root)
    if worker_flags.enabled(variables, "BILLING_ENABLED"):
        return (f"Buy a plan or pack at {PRICING}. "
                "Stripe hosts Checkout; claim your key at the success link.")
    return f"Use an existing key, or see {PRICING} for availability."


def cli_text(root: Path = ROOT) -> dict[str, Any]:
    """All CLI prose, including recovery and help, travels in the generated bundle."""
    return {
        "access": ACCESS,
        "privacy": CLI_PRIVACY,
        "package_warning": PACKAGE_WARNING,
        "coverage": ("Bundled public coverage summary, {as_of}: {models} catalogue cards, "
                     "{providers} catalogue providers, {benchmarks} benchmarks. {summary} "
                     "Current coverage may differ. See https://modelspec.dev/api/coverage.json."),
        "answers": ("Ask about model requirements, sourced capability evidence, cost, context, "
                    "hosting and policy constraints. Answers report ties, missing facts and reasons. "
                    + " ".join(CONDUCT_RULES) + " " + SUMMARY_RULE),
        "price": "From {low_dollars} per answer. Published range ${low_usd}–${high_usd} per answer, depending on plan, pack and explanation.",
        "procurement": (key_procurement(root) + " Checkout availability is shown on the page. "
                        "For access, volume or invoicing, contact sales@modelspec.dev. "
                        "Store a key with modelspec auth set, or set MODELSPEC_API_KEY; the environment wins."),
        "human_message": ("ModelSpec can check this model choice against your requirements and its "
                          "published evidence. The agent needs a ModelSpec API key. Answers start at "
                          "{low_dollars} at the cheapest published rate. You can provide an existing key, "
                          f"review {PRICING}, or look it up yourself on the free board at "
                          f"{entity.SITE}/decide/."),
        "orientation_next": ["Run modelspec key for access and prices.",
                             "Run modelspec setup mcp --client generic to connect an MCP client.",
                             f"Read {GUIDE_URL}; then use modelspec decide --spec FILE with a key."],
        "next_label": "Next steps:",
        "human_label": "Tell the human: {message}",
        "mcp_url": "MCP: {url}",
        "http_url": "HTTP: {url}",
        "command_help": "Run {command} --help for this command's options.",
        "links": "Guide: {guide}\nOpenAPI: {openapi}\nPricing and keys: {pricing}",
        "guide_version": "Guide version: {version}",
        "key_saved": ("Stored the ModelSpec key in {path}. POSIX uses mode 0600; "
                      "Windows uses the user-profile directory ACL. "
                      "MODELSPEC_API_KEY takes precedence."),
        "key_prompt": "ModelSpec API key",
        "write_prompt": "Apply this diff to the ModelSpec server entry?",
        "setup_note": ("Configure the MCP client's referenced environment variable or explicit "
                       "credential placeholder before launching it. A key stored by modelspec "
                       "auth set is for this CLI. Setup never copies a saved or environment key "
                       "into the config; a key value must be supplied explicitly. "
                       "Read the agent guide into the client's context."),
        "desktop_note": ("Claude Desktop uses the mcp-remote stdio bridge and needs Node.js/npx. "
                         "macOS GUI apps do not inherit your shell environment. Explicitly replace "
                         "<MODELSPEC_API_KEY> in the env block's MODELSPEC_AUTH_HEADER "
                         "with your key, "
                         "keeping the Bearer prefix and space. This stores the key in that config. "
                         "Setup writes only the placeholder and never reads your saved "
                         "or environment key."),
        "manual_note": "Replace <MODELSPEC_API_KEY> in your client's secret settings. This is a placeholder, not a credential.",
        "setup_written": "Updated only the ModelSpec server entry in {path}.",
        "setup_backup": "Backed up the original config to {path}.",
        "setup_unchanged": "The ModelSpec server entry is already configured in {path}.",
        "setup_cancelled": "The proposed change was not applied.",
        "upgrade": "Upgrade the client: uvx --refresh --from modelspec-dev modelspec; or pipx upgrade modelspec-dev; or pip install --upgrade modelspec-dev.",
        "guide_changed": "The server's guide version differs from this CLI's bundled guide. Refresh the guide and upgrade the client.",
        "errors": {
            "usage_error": "The command or options could not be read.",
            "missing_api_key": "This command needs a ModelSpec API key.",
            "invalid_api_key": "The ModelSpec key is invalid or was refused.",
            "auth_unreadable": ("The stored ModelSpec key cannot be read securely. Use a regular "
                                "file with mode 0600 on POSIX, or in your user-profile "
                                "directory on Windows."),
            "auth_unwritable": "The ModelSpec key could not be stored.",
            "invalid_spec": "The Spec failed structural validation against the bundled published schema. The server validates its meaning.",
            "spec_unreadable": "The Spec file or standard input could not be read as JSON or YAML.",
            "spec_source": "Choose exactly one of --spec FILE|- and --template ID.",
            "spec_too_large": "The Spec exceeds the API's 64 KB request limit.",
            "unknown_template": "The hosted vocabulary did not return that template's Spec.",
            "invalid_feedback": "The feedback failed the published request schema. Never include prompts, keys or personal details.",
            "invalid_vocabulary": "The vocabulary lookup options are invalid.",
            "network_error": "The hosted API could not be reached.",
            "unexpected_response": "The hosted API did not return the expected JSON object.",
            "http_error": "The hosted API refused the request.",
            "invalid_client": "Choose a supported MCP client.",
            "config_unreadable": "The MCP configuration is not a readable JSON or TOML object. No file was changed.",
            "config_unwritable": "The MCP configuration could not be written.",
            "config_changed": "The MCP configuration changed after the diff was prepared. No file was changed.",
            "config_path_required": "This client needs an explicit --config FILE for --write.",
            "confirmation_required": "Writing requires confirmation, or --yes after reviewing the diff.",
            "interrupted": "The command was interrupted.",
        },
        "recovery": {
            "key": ["Run modelspec key, then modelspec auth set or set MODELSPEC_API_KEY.", "{human_message}"],
            "credits": [f"Check your credits and available plans or packs at {PRICING}.",
                        "Honor Retry-After when present; retry once credits or the rate window allow it."],
            "coverage": ["{answers}", "{coverage}",
                         f"Read {GUIDE_URL}; tell the human which requirement could not be answered. "
                         "Do not silently drop it."],
            "network": [f"Check API health at {API}/v1/health, then retry.",
                        f"Read {GUIDE_URL} for the CLI, MCP and HTTP alternatives."],
            "upgrade": ["{upgrade}", f"Refresh {GUIDE_URL}."],
            "spec": ["Check the reported field paths against the published schema and OpenAPI.",
                     f"Read {GUIDE_URL}; use modelspec vocab with a key for a targeted lookup. "
                     "Tell the human about any requirement removed on retry."],
            "setup": ["Review the printed snippet and apply only the modelspec entry manually, "
                      "or retry modelspec setup mcp with --config FILE --write.",
                      f"Use the CLI or HTTP API with a key in the meantime: {GUIDE_URL}."],
            "usage": ["Run modelspec help agent or modelspec --help for the supported commands.",
                      f"Read {GUIDE_URL} for the next call."],
        },
        "help": {
            "root": "A keyed hosted API client. Run modelspec help agent for orientation.",
            "agent": "Orient an AI agent: coverage summary, access, setup and what to tell the human.",
            "key": "Show key procurement, published prices and a neutral message for the human.",
            "setup": "Print an MCP client configuration; --write shows a diff before confirmation.",
            "auth": "Store only a ModelSpec API key, locally. The environment takes precedence.",
            "decide": ("Send exactly your Spec to POST /v1/decide with a key. No local decision cache. "
                       + " ".join(CONDUCT_RULES)),
            "vocab": "Look up hosted vocabulary with a key; defaults to the compact starter section.",
            "feedback": "Rate an answer with a key present. Matches MCP fields; the feedback endpoint receives no Authorization header.",
            "json": "Emit JSON. Successful API bodies pass through unchanged; every failure has next steps.",
            "spec": "A JSON or YAML Spec file; - reads standard input.",
            "template": "A template ID retrieved with a key from the hosted vocabulary.",
            "client": "claude-code, claude-desktop, codex, gemini, grok, cursor or generic.",
            "config": "MCP config file. Generic clients require an explicit path to write.",
            "write": "Show the diff, then ask for confirmation before writing.",
            "yes": "Apply the displayed diff without an interactive confirmation.",
            "stdin": "Read the key from standard input instead of the hidden prompt.",
            "version": "Show the CLI and bundled guide versions.",
            "section": "A hosted vocabulary section; defaults to starter.",
            "search": "Search IDs and labels in the hosted vocabulary.",
            "id": "Return full details for this exact ID.",
            "ids": "Return full details for these IDs; repeat the option, at most 100.",
            "detail": "compact or full.",
            "offset": "Skip this many matching vocabulary rows.",
            "limit": "Compact page size, 1 to 20.",
            "rating": "reliable, unreliable, trustworthy, untrustworthy or confusing.",
            "decision_id": "The answer's decision_id, when available.",
            "note": "Optional feedback, up to 1,000 characters. No prompts, keys or personal details.",
            "trying": "Optional description, up to 300 characters, of what you were deciding.",
            "feedback_template": "Optional template ID used for that answer.",
        },
    }


def cli_clients() -> dict[str, Any]:
    """Client-native configurations, with environment references instead of secrets."""
    endpoint = entity.MCP_ENDPOINT
    return {
        "claude-code": {
            "format": "json", "path": ".mcp.json", "table": "mcpServers",
            "server": {"type": "http", "url": endpoint,
                       "headers": {"Authorization": "Bearer ${MODELSPEC_API_KEY}"}},
            "source": "https://code.claude.com/docs/en/mcp",
        },
        "claude-desktop": {
            "format": "json", "path": "desktop", "table": "mcpServers",
            "server": {"command": "npx", "args": ["-y", "mcp-remote", endpoint,
                       "--header", "Authorization:${MODELSPEC_AUTH_HEADER}"],
                       "env": {"MODELSPEC_AUTH_HEADER": "Bearer <MODELSPEC_API_KEY>"}},
            "source": "https://github.com/punkpeye/mcp-remote#custom-headers",
            "note": "desktop_note",
        },
        "codex": {
            "format": "toml", "path": "~/.codex/config.toml", "table": "mcp_servers",
            "server": {"url": endpoint, "bearer_token_env_var": "MODELSPEC_API_KEY"},
            "command": f"codex mcp add modelspec --url {endpoint} --bearer-token-env-var MODELSPEC_API_KEY",
            "source": "https://developers.openai.com/codex/mcp/",
        },
        "gemini": {
            "format": "json", "path": "~/.gemini/settings.json", "table": "mcpServers",
            "server": {"httpUrl": endpoint, "headers": {"Authorization": "Bearer ${MODELSPEC_API_KEY}"}},
            "source": "https://geminicli.com/docs/tools/mcp-server/",
        },
        "grok": {
            "format": "toml", "path": "~/.grok/config.toml", "table": "mcp_servers",
            "server": {"url": endpoint,
                       "headers": {"Authorization": "Bearer ${MODELSPEC_API_KEY}"}},
            "command": (f"grok mcp add --transport http modelspec {endpoint} "
                        "--header 'Authorization: Bearer ${MODELSPEC_API_KEY}'"),
            "source": "https://docs.x.ai/build/features/mcp-servers",
        },
        "cursor": {
            "format": "json", "path": "~/.cursor/mcp.json", "table": "mcpServers",
            "server": {"url": endpoint, "headers": {"Authorization": "Bearer ${env:MODELSPEC_API_KEY}"}},
            "source": "https://cursor.com/docs/mcp#config-interpolation",
        },
        "generic": {
            "format": "json", "path": None, "table": "mcpServers",
            "server": {"type": "http", "url": endpoint,
                       "headers": {"Authorization": "Bearer <MODELSPEC_API_KEY>"}},
            "source": GUIDE_URL, "note": "manual_note",
        },
    }


def cli_bundle(tiers: dict[str, Any] | None = None) -> dict[str, Any]:
    import tomllib

    from pipeline.load import load_benchmarks, load_catalogue, load_models
    from pipeline.pricing import procurement_data
    from pipeline.coverage import from_repo, summary
    models = load_models(ROOT)
    as_of = load_catalogue(ROOT).as_of
    coverage = from_repo(ROOT, as_of)
    return {
        "_generated": "by pipeline.agent_copy; run python -m pipeline.agent_copy write",
        "cli_version": tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"],
        "guide_version": guide(tiers)[0],
        "entity": entity.ONE_SENTENCE,
        "coverage": {"as_of": as_of.isoformat(), "models": len(models),
                     "providers": len({model.provider for model in models}),
                     "benchmarks": len(load_benchmarks(ROOT)),
                     "summary": summary(coverage), "decision": coverage},
        "urls": {"guide": GUIDE_URL, "openapi": f"{entity.SITE}/openapi.yaml",
                 "pricing": PRICING, "api": API, "mcp": entity.MCP_ENDPOINT},
        "install": list(INSTALL_PATHS),
        "pricing": procurement_data(tiers or _tiers()),
        "clients": cli_clients(),
        "text": cli_text(),
        "source_hashes": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in (Path(__file__), ROOT / "pipeline/entity.py",
                                       ROOT / "pipeline/pricing.py",
                                       ROOT / "pipeline/worker_flags.py",
                                       ROOT / worker_flags.WRANGLER_REL, TIERS,
                                       ROOT / "docs/decision-contract.schema.json", ROOT / "pyproject.toml",
                                       ROOT / "schemas/feedback-v1.schema.json")},
    }


def cli_spec_schema() -> dict[str, Any]:
    """The published request and reachable definitions only, with no engine or catalogue."""
    contract = json.loads((ROOT / "docs/decision-contract.schema.json").read_text(encoding="utf-8"))
    definitions = {}
    pending = ["DecideRequest"]
    while pending:
        name = pending.pop()
        if name in definitions:
            continue
        definition = contract["$defs"][name]
        definitions[name] = definition
        pending.extend(re.findall(r'#/\$defs/([^" ]+)', json.dumps(definition)))
    return {"$schema": contract["$schema"], "$defs": definitions, "$ref": "#/$defs/DecideRequest"}


RESPONSE_BUDGET_RULES = (
    "If a response exceeds the client context budget, retain the original outside the "
    "prompt and select answer, reading, recovery/error.issues and relevant rows for "
    "reporting. Do not treat a truncated list as complete. These token allowances are "
    "separate from ModelSpec credits and the agent vendor's token billing."
)
#: The one rule for MCP decide's bounded default (MODEL-293). The guide, the
#: MCP instructions and the decide description all quote it.
BOUNDED_MCP = (
    "MCP decide returns a bounded answer of at most 16 KB, summary included. "
    "Drill down with evidence_for. Complete rows need fields:null; "
    "explanation.fetch names what was removed and how to fetch it."
)
BOUNDED_MCP_DETAIL = (
    'With explain unset or "none": explain=none, limit=10, fields model_rank, cost_per_task, '
    "estimates, p_best. summary or full also sends contributions and evidence. "
    "omitted counts removed records; explain=none does not compute eliminations. "
    "explicit fields, including null, is sent as given. "
    "Over 16 KB the body is a trimmed notice and explanation.fetch says how to resend. "
    "decision_id is a citation, not a stored lookup. "
)


def guide_examples() -> list[dict[str, Any]]:
    """Specs come from validated templates and the registry's hardware vocabulary."""
    from decision.contract import parse_spec
    from decision.registry import default
    from decision.templates import load_templates
    registry = default()
    templates = {row["id"]: row for row in load_templates(registry=registry)}
    examples = []
    for family, template in (("Use case", "writing-balanced"),
                             ("Budget and policy", "regulated-budget"),
                             ("Own hardware", "private-self-host"),
                             ("Coding", "coding-balanced")):
        spec = deepcopy(templates[template]["spec"])
        if family == "Budget and policy":
            spec["where"].extend(condition for condition in templates["budget-coding"]["spec"]["where"]
                                 if condition.startswith("offering.cost_per_task <="))
            template += " + budget-coding"
        if family == "Own hardware":
            devices = sorted(registry.allowed_values(registry.facet("model.fits_hardware")))
            device = next((d for d in devices if "rtx_4090" in d), devices[0])
            spec["where"].append({"facet": "model.fits_hardware", "in": [device]})
            spec["access"] = "own_hardware"
            spec["estate"] = {"devices": [device]}
        parse_spec(spec, facets=registry.facet)
        examples.append({"family": family, "template": template, "spec": spec})
    return examples


def guide_body(tiers: dict[str, Any]) -> str:
    """All agent prose lives here; the published Markdown is generated, never edited."""
    from decision.contract import DEFAULT_TASK_TOKENS as default
    w = tiers["credits"]["weights"]
    text = f"""# ModelSpec agent guide

Guide version: {{version}}. Generated by `python -m pipeline.agent_copy write`.
Canonical URL: {GUIDE_URL}
Full API reference: {entity.SITE}/openapi.yaml
Coverage: {entity.SITE}/api/coverage.json

{entity.ONE_SENTENCE}

## CLI, MCP or HTTP

{ACCESS} CLI: `{INSTALL_PATHS[0]}` (or `{INSTALL_PATHS[1]}`); `pip install modelspec` is an unrelated project. `modelspec help agent --json` orients; `modelspec key` explains access. {CLI_PRIVACY}

## First call

{SPEC_GUIDANCE}
{NOT_A_ROUTER}

HTTP: POST `{API}/v1/decide` with `Content-Type: application/json`, a real
`User-Agent`, and `Authorization: Bearer <key>`. The JSON body is the Spec itself.
MCP: call `decide` with the Spec itself as arguments, with Authorization on the
MCP connection. Do not wrap it in `spec` or `task`. {key_procurement()}

Minimal valid Spec, minimizing cost without claiming a quality ranking:

```json
{json.dumps(MINIMAL_SPEC, separators=(',', ':'))}
```

`spec_version` is 1. `snapshot` defaults to latest; save the returned snapshot
and decision_id, and set snapshot to that exact ID for a reproducible retry.
Over HTTP, `explain` defaults to summary and returns full rows; full includes
every eliminated candidate and can be large. A Spec has one optimize objective: min, max, or weights.
A negative numeric weight key prefers less, for example `-offering.cost_per_task`.
Unset, cost_per_task assumes {default.input:,} input and {default.output:,} output tokens, so a small task's cost cap can exclude every model.
For boolean or enum preferences use a prefer value and weight, never a bare number.
`where` is an array. In text expressions a set is `{{a, b}}`, not `[a, b]`.
Structured example: `{{"facet":"offering.provider","in":["openai"]}}`.
`task` free text is rejected. Translate only requirements you can represent.

## Bounded answers and drill-down

{BOUNDED_MCP}

Answer, status, warnings, coverage and the top result stay. An omission is not an elimination. At `explain: none`, a missing eliminated count means eliminations were not computed. When `explanation.omitted` is set, `explanation.fetch` tells you to resend with `evidence_for` for one model, narrow `fields`, lower `limit`, or POST /v1/decide without `fields` for the complete Decision. HTTP without those controls still returns the complete Decision.

## Worked Specs

These are starting points from the registry templates, not recommendations of a
model. Keep only the gates and weights the user stated; do not silently adopt
or drop a gate or invent numeric tradeoffs. If no objective was stated,
disclose the minimal Spec's cost objective as a discovery default, not a quality
recommendation. Capabilities and weights express broad evidence, not measured
quality on the user's exact prompt. Replace the example hardware ID with the user's SKU.
"""
    for row in guide_examples():
        text += f"\n### {row['family']}\n\nTemplate: `{row['template']}`.\n\n```json\n{json.dumps(row['spec'], indent=2)}\n```\n"
    text += f"""
## Refine and report

{REPORTING_RULES}

If `reading.omitted` reports truncation, use the complete answer.members and issues
lists. These rules also apply when reading is absent: inspect answer, issues, and
result evidence directly. `may_qualify` means a required fact is unknown, not a pass.
`status=partial` is incomplete evidence. `no_match` is not a winner. No single leader
is an answer: report the tie. Do not fall back to `rank`. An undetermined policy is
not permission.

On refusal read error.issues and recovery hints, including their paths and valid
examples. Correct the specified fields and retry. Tell the user any requirement
you removed; a successful retry does not prove that removed requirement.
Use `vocab` with `{{"section":"starter"}}` for a compact first lookup, then search
or id/ids for the missing term. HTTP lookup:
`GET {API}/v1/vocabulary?section=starter` where available.
The starter response includes a ready-to-send minimal Spec and a next hint.
If a requirement is unsupported, disclose that limit instead of inventing a facet.

## Per-call token budget

These are planning allowances for agent context, not server response caps.
Token accounting uses cl100k_base when available, otherwise characters / 4.
JSON schemas also consume tokens; each tool definition can exceed its description.

| Item | Planning allowance | Credits | Use |
| --- | ---: | ---: | --- |
| Guide, stored once | <= 4,000 tokens | 0 | Load once per guide version |
| MCP initialize instructions | <= 1,000 tokens | 0 | Pointer, version, five rules |
| Each MCP description | <= 1,500 tokens | 0 | Schemas counted separately |
| Spec arguments | 1,000 tokens | 0 | Start with an example above |
| vocab starter/search | 2,000 tokens for reading | 0 | Compact, at most 20 rows per page |
| MCP decide, bounded default | <= 3,000 tokens | {w['decide.none']} | explain none, limit 10, compact rows |
| decide drill-down (evidence_for) | <= 2,000 tokens | {w['decide.none']} at explain none | One model's evidence |
| decide summary | Reserve 16,000 tokens for reading | {w['decide.summary']} | HTTP default; size depends on candidates |
| decide full | Can exceed 160,000 tokens | {w['decide.full']} | Only when eliminated-candidate detail is needed |
| rank / policy_check | Size depends on rows | {w['rank']} / {w['policy-check']} | Deprecated ranking, not a decide fallback / policy checks |
| model_info / list_use_cases | Size depends on card/profiles | 0 | One card / legacy profiles |
| feedback | 500 tokens for reading | 0 | After acting, never include secrets or a prompt |

{RESPONSE_BUDGET_RULES}

## Store once

Store this guide locally, then include its instructions in the agent's context.
A link alone does not guarantee any client fetches it. Refresh when
`x-modelspec-guide-version` changes. Every /v1/ response links here with
`Link: <{GUIDE_URL}>; rel="describedby"`. MCP initialize includes instructions
and the guide version. Local storage does not guarantee vendor prompt caching.
Do not store an API key in these files.

Claude Code, project CLAUDE.md, or the body of a manually loaded skill:

```sh
mkdir -p .agents
curl -fsS {GUIDE_URL} -o .agents/modelspec.md
cat >> CLAUDE.md <<'EOF'
When choosing models, read .agents/modelspec.md. Call decide early with a
template-based Spec; refine from reading and recovery hints.
EOF
```

Codex, project AGENTS.md:

```sh
mkdir -p .agents
curl -fsS {GUIDE_URL} -o .agents/modelspec.md
cat >> AGENTS.md <<'EOF'
When choosing models, read .agents/modelspec.md. Call decide early with a
template-based Spec; refine from reading and recovery hints.
EOF
```

Cursor, project rule file:

```sh
mkdir -p .agents .cursor/rules
curl -fsS {GUIDE_URL} -o .agents/modelspec.md
cat > .cursor/rules/modelspec.mdc <<'EOF'
---
description: ModelSpec model selection
alwaysApply: true
---
When choosing models, read .agents/modelspec.md. Call decide early with a
template-based Spec; refine from reading and recovery hints.
EOF
```

Plain MCP clients:

```sh
mkdir -p .agents
curl -fsS {GUIDE_URL} -o .agents/modelspec.md
```

The client must read initialize.result.instructions and inject that text plus
.agents/modelspec.md into its agent context once per version, alongside tools/list.
Keep the guide outside individual tool results. Reuse it for subsequent calls;
refresh if a new initialize advertises a different version. The MCP server cannot
write client files or force a client to honor instructions.
"""
    return "\n".join(line.rstrip() for line in text.split("\n"))


def guide(tiers: dict[str, Any] | None = None) -> tuple[str, str]:
    body = guide_body(tiers or _tiers())
    version = "1-" + hashlib.sha256(body.encode()).hexdigest()[:16]
    return version, body.replace("{version}", version)


def context_guide(tiers: dict[str, Any]) -> str:
    """Keep the decision/reporting rules; minify examples and omit client setup tables."""
    text = guide(tiers)[1].partition("\n## Per-call token budget\n")[0]
    text = re.sub(r"```json\n(.*?)\n```",
                  lambda match: "```json\n" + json.dumps(json.loads(match[1]), separators=(",", ":")) + "\n```",
                  text, flags=re.S)
    return text + "\n\n" + RESPONSE_BUDGET_RULES + "\n"

NOT_A_ROUTER = (
    "Not a router: call it once per job or role, not per request, then route among the "
    "models it recommends."
)


def _tiers(path: Path = TIERS) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def credit_usd_range(tiers: dict[str, Any]) -> tuple[float, float]:
    """The cheapest and dearest price of one credit across live plans and packs."""
    per_credit = [p["usd"] / p["credits"] for p in tiers["billing"]["prices"].values()
                  if not p.get("placeholder") and p.get("credits")]
    return min(per_credit), max(per_credit)


def _usd(value: float) -> str:
    from pipeline.pricing import format_usd
    return format_usd(value)


def price(weights: list[int], tiers: dict[str, Any]) -> str:
    """'Costs N credits ...' for a call, from tiers.json."""
    low, high = credit_usd_range(tiers)
    credits = " or ".join(str(w) for w in sorted(set(weights)))
    unit = "credit" if weights == [1] else "credits"
    return (f"Needs an API key (Authorization: Bearer). Costs {credits} {unit} a call; a credit "
            f"costs {_usd(low)}–{_usd(high)} depending on the plan or pack ({PRICING}).")


def copy(tiers: dict[str, Any] | None = None) -> dict[str, Any]:
    tiers = tiers or _tiers()
    w = tiers["credits"]["weights"]
    decide_price = price([w["decide.none"], w["decide.summary"], w["decide.full"]], tiers)
    tools = {
        "decide": (
            "Which models fit this job? "
            "Returns answer, ranked results, may_qualify, reading and recovery hints, "
            "decision_id and snapshot. "
            f"{REPORTING_RULES}{decide_price} {NOT_A_ROUTER} "
            f"Proxies POST {API}/v1/decide. {SPEC_GUIDANCE}"
            f"{BOUNDED_MCP} {BOUNDED_MCP_DETAIL}"
            "task free text is rejected; where is an array. "
            f"Call shape, examples, recovery and budgets: {GUIDE_URL}. {NULL_RULE}"
        ),
        "rank": (
            "Legacy v1; use decide. Deprecated: the retired fixed-benchmark "
            "ranking, whose scores lag the catalogue; newer models are often unranked. "
            "Which models rank highest for one fixed use-case profile? "
            "Returns a shortlist with evidence_basis, input provenance, not a quality "
            f"verdict. {price([w['rank']], tiers)} "
            "Don't call it as a fallback when decide names no single leader: report "
            f"decide's tie. {SUMMARY_RULE} "
            f"Proxies POST {API}/v1/rank with this tool's arguments as the JSON body. "
            f"{NULL_RULE}"
        ),
        "policy_check": (
            "Which models, on which platforms, does my policy allow? "
            "Checks a policy document (licence, origin, data handling) per model and per "
            "platform. Returns pass, fail or undetermined for each row; undetermined is not a pass. "
            f"{price([w['policy-check']], tiers)} "
            "It doesn't choose a model: use decide to choose among the ones that pass. "
            f"Proxies POST {API}/v1/policy-check with this tool's arguments as the JSON body; "
            "Authorization is forwarded. "
            f"{NULL_RULE}"
        ),
        "vocab": (
            "What can a decide spec say? "
            "Returns the decision vocabulary: valid facet ids, benchmarks, domains, providers "
            "and task types. Compact by default, with 20 rows per page and no counts. "
            "Split-mode full details exclude per-model facts and counts. "
            "Needs an API key. "
            "Use it for missing ids, not to compare models. "
            "One vocabulary lookup per unknown facet, then decide. Read `next` before another call. "
            "section=starter returns a ready-to-send minimal Spec and a next hint. "
            "Search covers every section's ids, labels, definitions and values with "
            "case- and separator-insensitive matching; a miss returns suggestions. "
            "An explicit non-starter section scopes the search. "
            "Use id or ids for row details, or detail=full for all display details. "
            "Use offset and limit to page matches across sections, including full details; "
            "an empty page ends the list. "
        ),
        "model_info": (
            "What does ModelSpec's card say about one model? "
            f"Reads {entity.SITE}/api/models/<model_id>.json (model_id is provider/slug). "
            "With data splitting, returns only the model's display name from the "
            "Worker vocabulary. Needs an API key. "
            "Not current evidence and not a ranking: use decide for that. "
            f"{NULL_RULE}"
        ),
        "list_use_cases": (
            "Which ranking profiles exist, and what is the ranking policy? "
            f"Returns {entity.SITE}/api/rank/profiles.json: the profiles, the evidence floors "
            "and the neutrality commitment. Needs an API key. "
            "Not a decision: use decide for that. "
            f"{NULL_RULE}"
        ),
        "feedback": (
            "Was a ModelSpec answer reliable? "
            "After you act on an answer, say whether it was reliable, unreliable, trustworthy, "
            f"untrustworthy or confusing, by proxying POST {API}/v1/feedback. Include the "
            "answer's decision_id. Free, no key, and no Authorization header is forwarded. "
            "Not for questions or support. Never put a prompt, a key or personal details in note. "
            'The response says status "recorded" or "not_recorded" (storage is off until the '
            "privacy statement covers it)."
        ),
    }
    card = {
        "decide": "Decide which models fit a job, with reasons and cost. Key; 1–2 credits.",
        "rank": "Deprecated fixed-profile shortlist (legacy v1); use decide. Key; 1 credit.",
        "model_info": "One model's published card. Needs an API key.",
        "list_use_cases": "Ranking profiles and the published ranking policy. Needs an API key.",
        "policy_check": "Policy pass/fail/undetermined per model and platform. Key; 5 credits.",
        "vocab": "The valid facet ids and names for a decide spec. Needs an API key.",
        "feedback": "Say whether an answer was reliable. Free, no key.",
    }
    # The OpenAPI lead for each paid or agent-facing operation: the question, what it
    # returns, the price, when not to call. openapi.py puts each operation's own
    # technical text after it.
    lead = {name: text.split(" Proxies POST")[0] for name, text in tools.items()}
    openapi = {
        "decide": {"summary": "Decide which models fit a job, and show the work.", "lead": lead["decide"]},
        "rank": {"summary": "Deprecated legacy v1: rank the catalogue for one profile. Use decide.",
                 "lead": lead["rank"]},
        "policyCheck": {"summary": "Check a policy per model and per platform.", "lead": lead["policy_check"]},
        "feedback": {"summary": "Say whether a ModelSpec answer was reliable.",
                     "lead": "Was a ModelSpec answer reliable? Rate it after you act on it, with the "
                             "decision_id. Free, no key. Not for questions or support."},
    }
    return {
        "_generated": "by pipeline/agent_copy.py (MODEL-257); edit that, then run "
                      "python -m pipeline.agent_copy write",
        "guide_version": guide(tiers)[0],
        "guide_url": GUIDE_URL,
        "context_guide": context_guide(tiers),
        "vocab": {"minimal_spec": MINIMAL_SPEC, "next": VOCAB_NEXT},
        "instructions": (
            f"{entity.ONE_SENTENCE} {entity.DISAMBIGUATION} ModelSpec guide {guide(tiers)[0]}: {GUIDE_URL}. Store once per version. "
            f"{ACCESS} CLI: {INSTALL_PATHS[0]}. {PACKAGE_WARNING} "
            "1. Call decide early and refine from reading. One vocabulary lookup per unknown facet, then decide. Read `next` before another call. "
            "2. Put Musts in where and Prefers in optimize; use vocab section=starter only for missing ids. "
            "3. Present ties as ties, including with_estate; never invent a single winner or quality rank. "
            "4. Disclose not_applied and dropped requirements after retries; unknown is not a pass. "
            "5. Follow reading.do_not_claim, label estimates and pin snapshot. "
            f"{SUMMARY_RULE} {BOUNDED_MCP}"
        ),
        "tools": tools,
        "card": card,
        "openapi": openapi,
    }


def render(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m pipeline.agent_copy")
    parser.add_argument("command", choices=("write", "check"))
    args = parser.parse_args(argv)
    version, markdown = guide()
    holding = ROOT / "site/holding/index.html"
    artifacts = {
        OUT: render(copy()),
        GUIDE_OUT: markdown,
        CLI_OUT: render(cli_bundle()),
        CLI_SCHEMA: render(cli_spec_schema()),
        CLI_FEEDBACK_SCHEMA: (ROOT / "schemas/feedback-v1.schema.json").read_text(encoding="utf-8"),
        holding: re.sub(r'(?<=<!-- modelspec-cli:start -->)\s*.*?\s*(?=<!-- modelspec-cli:end -->)',
                        "\n      " + install_html() + "\n      ", holding.read_text(encoding="utf-8"), flags=re.S),
        GUIDE_CONSTANTS: (
            '# Generated by pipeline.agent_copy; do not edit.\n'
            f'GUIDE_URL = {GUIDE_URL!r}\nGUIDE_VERSION = {version!r}\n'
            f'MINIMAL_SPEC = {MINIMAL_SPEC!r}\nVOCAB_NEXT = {VOCAB_NEXT!r}\n'
        ),
    }
    stale = False
    for path, text in artifacts.items():
        if args.command == "write":
            path.write_text(text, encoding="utf-8")
            print(f"wrote {path.relative_to(ROOT)}")
        elif not path.is_file() or path.read_text(encoding="utf-8") != text:
            print(f"{path.relative_to(ROOT)} is stale: run python -m pipeline.agent_copy write", file=sys.stderr)
            stale = True
    return int(stale)


if __name__ == "__main__":
    raise SystemExit(main())
