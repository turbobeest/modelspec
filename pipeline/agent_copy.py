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
from copy import deepcopy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from pipeline import entity

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
SPEC_GUIDANCE = (
    "Call decide early with a template-based Spec; refine from reading and recovery hints. "
    "Use vocab section=starter only when you need a facet id; use search for a targeted lookup. "
    "Put Musts in where: these gates exclude. Put Prefers in optimize.weights: weights rank "
    "and never exclude. Unknown values go to may_qualify. Pin snapshot for reproducibility. "
)
REPORTING_RULES = (
    "Read reading when present. Present answer.kind=tied as a tie among all answer.members, "
    "never a single winner; tie-breakers are conditional choices. Report a tied "
    "with_estate.answer as a tie too. State requirements in reading.not_applied or "
    "error.issues that were not applied, including requirements removed after a rejected "
    "call. A retry does not verify them. Report estimates as estimates: fits_hardware "
    "membership is not measured fit for a specific quantization and context workload. "
    "Follow reading.do_not_claim. Never claim a rank the response does not show. "
)
MINIMAL_SPEC = {"spec_version": 1, "optimize": {"min": "offering.cost_per_task"}}
#: The one rule for MCP decide's bounded default (MODEL-293). The guide, the
#: MCP instructions and the decide description all quote it.
BOUNDED_MCP = (
    "MCP decide returns a bounded answer by default; drill down with evidence_for, "
    "or ask for full rows with fields:null/explain."
)
BOUNDED_MCP_DETAIL = (
    'With explain unset or "none" it sends explain=none, limit=10 and row fields model_rank, '
    "cost_per_task, estimates and p_best, and the body says representation: bounded. The answer, "
    "reading, warnings and ties stay complete; explanation.omitted counts what was left out, "
    "including screened-out models, which are counted, not listed. To see one model's evidence, "
    "status, rank and elimination reasons, resend the same spec with its returned snapshot and "
    "evidence_for: <model id>; that stateless call stays within 2k estimated tokens. "
    "For full rows pass fields: null, or set explain to summary or full, which return full rows "
    "unless you also pass fields. Full includes every eliminated candidate and can exceed the "
    "client context budget. decision_id is a citation, not a stored lookup. "
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
    w = tiers["credits"]["weights"]
    text = f"""# ModelSpec agent guide

Guide version: {{version}}. Generated by `python -m pipeline.agent_copy write`.
Canonical URL: {GUIDE_URL}
Full API reference: {entity.SITE}/openapi.yaml

{entity.ONE_SENTENCE}

## First call

{SPEC_GUIDANCE}
{NOT_A_ROUTER}

HTTP: POST `{API}/v1/decide` with `Content-Type: application/json`, a real
`User-Agent`, and `Authorization: Bearer <key>`. The JSON body is the Spec itself.
MCP: call `decide` with the Spec itself as arguments, with Authorization on the
MCP connection. Do not wrap it in `spec` or `task`. Get a key at {PRICING}.

Minimal valid Spec, minimizing cost without claiming a quality ranking:

```json
{json.dumps(MINIMAL_SPEC, separators=(',', ':'))}
```

`spec_version` is 1. `snapshot` defaults to latest; save the returned snapshot
and decision_id, and set snapshot to that exact ID for a reproducible retry.
Over HTTP, `explain` defaults to summary and returns full rows; full includes
every eliminated candidate and can be large. A Spec has one optimize objective: min, max, or weights.
A negative numeric weight key prefers less, for example `-offering.cost_per_task`.
For boolean or enum preferences use a prefer value and weight, never a bare number.
`where` is an array. In text expressions a set is `{{a, b}}`, not `[a, b]`.
Structured example: `{{"facet":"offering.provider","in":["openai"]}}`.
`task` free text is rejected. Translate only requirements you can represent.

## Bounded answers and drill-down

{BOUNDED_MCP}

MCP `decide` with `explain` unset or `none` sends `explain: none`, `limit: 10`
and row `fields` of `model_rank`, `cost_per_task`, `estimates` and `p_best`.
The body says `representation: bounded`, `bounded_version: 1.0` and the
complete contract it projects in `projects_contract`; it has no
`contract_version`. The answer, reading, warnings and ties stay complete.
`explanation.omitted` counts what was left out, including screened-out models,
which are counted there, not listed. An omission is not an elimination or an
absent fact.

To see one model's evidence, status, rank or elimination reasons, resend the
same Spec with its returned `snapshot` plus `"evidence_for": "<lab/model>"`.
The call is stateless; `decision_id` is a citation, not a stored lookup. The
drill-down returns `model_evidence` for that model only, within 2,000 estimated
tokens, and empty `results` and `may_qualify`: report the answer from
`answer.members`. A 503 `explanation_unavailable` means the snapshot cannot
cite evidence; retry without `evidence_for`.

For full rows, pass `"fields": null`, or set `explain` to `summary` or `full`:
an explicit explain returns full rows unless you also pass `fields`. HTTP
callers get full rows unless they send `fields` or `evidence_for`.

## Worked Specs

These are starting points from the registry templates, not recommendations of a
model. Adapt their gates to the user's actual requirements; do not silently adopt
or drop a gate. Capabilities and weights express broad evidence, not measured
quality on the user's exact prompt. The hardware ID below is a registry example;
replace it with the user's SKU after a targeted lookup.
"""
    for row in guide_examples():
        text += f"\n### {row['family']}\n\nTemplate: `{row['template']}`.\n\n```json\n{json.dumps(row['spec'], indent=2)}\n```\n"
    text += f"""
## Refine and report

{REPORTING_RULES}

`reading.tied` identifies a tie; if `reading.omitted` reports truncation, use the
complete answer.members and request/error.issues lists. `reading.not_applied`
names unchecked requirements. `reading.estimates` names computed estimates.
`reading.do_not_claim` states reporting limits. These rules also apply when
reading is absent: inspect answer, issues, and result evidence directly.
`may_qualify` means a required fact is unknown, not that the model passes.
`status=partial` is incomplete evidence; `no_match` is not a winner.
Unknown policy determinations are undetermined, never permission.

On refusal read error.issues and recovery hints, including their paths and valid
examples. Correct the specified fields and retry. Tell the user any requirement
you removed; a successful retry does not prove that removed requirement.
Use `vocab` with `{{"section":"starter"}}` for a compact first lookup, then search
or id/ids for the missing term. HTTP lookup:
`GET {API}/v1/vocabulary?section=starter` where available.
Avoid paging through unrelated vocabulary before the first decide.
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
| rank / policy_check | Size depends on rows | {w['rank']} / {w['policy-check']} | Legacy ranking / policy checks |
| model_info / list_use_cases | Size depends on card/profiles | 0 | One card / legacy profiles |
| feedback | 500 tokens for reading | 0 | After acting, never include secrets or a prompt |

If a response exceeds the client context budget, retain the original outside the
prompt and select answer, reading, recovery/error.issues and relevant rows for
reporting. Do not treat a truncated list as complete. These token allowances are
separate from ModelSpec credits and the agent vendor's token billing.

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
    return text


def guide(tiers: dict[str, Any] | None = None) -> tuple[str, str]:
    body = guide_body(tiers or _tiers())
    version = "1-" + hashlib.sha256(body.encode()).hexdigest()[:16]
    return version, body.replace("{version}", version)

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
    return f"${value:.4f}".rstrip("0")


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
            f"Minimal valid Spec: {json.dumps(MINIMAL_SPEC, separators=(',', ':'))}. "
            f"{BOUNDED_MCP} {BOUNDED_MCP_DETAIL}"
            "task free text is rejected; where is an array. "
            "Report any requirement dropped on retry. "
            f"Call shape, examples, recovery and budgets: {GUIDE_URL}. {NULL_RULE}"
        ),
        "rank": (
            "Legacy v1; use decide for new work. "
            "Which models rank highest for one fixed use-case profile? "
            "Returns a shortlist for that profile with evidence_basis, which is input "
            "provenance (none, unverified-legacy, mixed, partial-verified, verified), not a "
            f"quality verdict. {price([w['rank']], tiers)} "
            "Don't call it when you can state requirements: decide takes them, rank doesn't. "
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
            "In split mode full details still exclude per-model facts and counts. Free, no key. "
            "Use it for missing ids, not to compare models. "
            "Call decide early with a template-based Spec. If you need ids, use section=starter. "
            "Use search for a case-insensitive substring of id or label, then call decide. "
            "Pass id or ids for full details of specific rows, or detail=full for all display details. "
            "Use offset and limit to page compact sections; an empty page ends the list. "
            f"{SPEC_GUIDANCE}"
        ),
        "model_info": (
            "What does ModelSpec's published card say about one model? "
            f"Reads {entity.SITE}/api/models/<model_id>.json (model_id is provider/slug). "
            "With data splitting enabled, returns only the model's display name from the "
            "Worker vocabulary. Free, no key. "
            "Not current evidence and not a ranking: use decide for that. "
            f"{NULL_RULE}"
        ),
        "list_use_cases": (
            "Which ranking profiles exist, and what is the ranking policy? "
            f"Returns {entity.SITE}/api/rank/profiles.json: the profiles, the evidence floors "
            "and the neutrality commitment, as data. Free, no key. "
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
        "rank": "Fixed-profile shortlist (legacy v1); use decide. Key; 1 credit.",
        "model_info": "One model's published card. Free, no key.",
        "list_use_cases": "Ranking profiles and the published ranking policy. Free.",
        "policy_check": "Policy pass/fail/undetermined per model and platform. Key; 5 credits.",
        "vocab": "The valid facet ids and names for a decide spec. Free.",
        "feedback": "Say whether an answer was reliable. Free, no key.",
    }
    # The OpenAPI lead for each paid or agent-facing operation: the question, what it
    # returns, the price, when not to call. openapi.py puts each operation's own
    # technical text after it.
    lead = {name: text.split(" Proxies POST")[0] for name, text in tools.items()}
    openapi = {
        "decide": {"summary": "Decide which models fit a job, and show the work.", "lead": lead["decide"]},
        "rank": {"summary": "Legacy v1: rank the catalogue for one profile. Use decide.", "lead": lead["rank"]},
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
        "instructions": (
            f"{entity.ONE_SENTENCE} {entity.DISAMBIGUATION} ModelSpec guide {guide(tiers)[0]}: {GUIDE_URL}. Store once per version. "
            "1. Call decide early with a template-based Spec; refine from reading and recovery hints. "
            "2. Put Musts in where and Prefers in optimize; use vocab section=starter only for missing ids. "
            "3. Present ties as ties, including with_estate; never invent a single winner or quality rank. "
            "4. Disclose not_applied and dropped requirements after retries; unknown is not a pass. "
            "5. Follow reading.do_not_claim, label estimates and pin snapshot. "
            f"{BOUNDED_MCP}"
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
    artifacts = {
        OUT: render(copy()),
        GUIDE_OUT: markdown,
        GUIDE_CONSTANTS: (
            '# Generated by pipeline.agent_copy; do not edit.\n'
            f'GUIDE_URL = {GUIDE_URL!r}\nGUIDE_VERSION = {version!r}\n'
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
