"""What an agent reads before it decides to call ModelSpec (MODEL-257).

    python -m pipeline.agent_copy write     # regenerate mcp/src/agent-copy.json
    python -m pipeline.agent_copy check     # exit 1 if the committed file is stale

The MCP server's `instructions` and every tool description, the MCP card's tool
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
SPEC_GUIDANCE = (
    "Read vocab first with section=starter for valid facet ids. Put Musts in where: these gates exclude. "
    "Put Prefers in optimize.weights: weights rank and never exclude. Unknown values "
    "go to may_qualify instead of being dropped. Pin snapshot for reproducibility. "
    "Example for a coding agent on a budget: "
    '{"spec_version":1,"snapshot":"latest","capabilities":{"software_engineering":"required"},'
    '"where":["model.class = text-generator","model.context_window >= 200000",'
    '"offering.cost_per_task <= 0.25"],"optimize":{"weights":'
    '{"software_engineering":0.6,"-offering.cost_per_task":0.4}}}. '
)
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
            f"{entity.ONE_SENTENCE} "
            "Returns the answer (one model, or a declared tie that names the cheapest, "
            "open-weights and best-measured members), ranked results with cost per task and "
            "uncertainty, the models screened out with the reason for each, may_qualify for "
            "missing facts, and a decision_id and snapshot so the same spec gives the same answer later. "
            "How to report: read reading when present. Present answer.kind=tied as a tie among "
            "all answer.members, never a single winner; tie-breakers are conditional choices. "
            "State requirements in reading.not_applied or error.issues that were not applied, "
            "including requirements removed after a rejected call. A retry does not verify them. "
            "Report estimates as estimates: fits_hardware membership is not measured fit for a "
            "specific quantization and context workload. Follow reading.do_not_claim. "
            "Never claim a rank the response does not show: a cost rank is not a #1 quality rank, "
            "and general capability evidence does not verify an exact prompt or thread safety. "
            f"{decide_price} {NOT_A_ROUTER} "
            f"Proxies POST {API}/v1/decide. "
            f"{SPEC_GUIDANCE}"
            "Minimal valid Spec: "
            '{"spec_version":1,"optimize":{"min":"offering.cost_per_task"}}. '
            "Common mistakes: task is free text and is rejected; translate the request "
            "into structured facets via vocab section=starter, then remove task and retry. "
            "Report to the user any requirement you dropped. "
            "where must be an array, and a text set uses {a, b}, not [a, b]; "
            'the structured form is {"facet":"offering.provider","in":["openai"]}. '
            "Boolean and enum Prefers need a prefer value and a weight, not a bare numeric weight. "
            'Use explain: "summary" (the default): 1 credit, and it carries the answer, '
            "results, by_model and may_qualify. "
            'explain: "full" (2 credits) also lists every eliminated candidate and returns about '
            "670 KB, so ask for it only to see why one model was excluded. "
            "The decision response is returned unchanged with a short summary. "
            "Authorization from the MCP client is forwarded. "
            f"{NULL_RULE}"
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
            "Call it before writing a spec, not to compare models. "
            "Call vocab section=starter first for the facets used most by the 40 template specs. "
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
        "instructions": f"{entity.ONE_SENTENCE} {entity.DISAMBIGUATION} "
                        "Start with vocab section=starter, use search, then call decide once per job or role.",
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
    text = render(copy())
    if args.command == "write":
        OUT.write_text(text, encoding="utf-8")
        print(f"wrote {OUT.relative_to(ROOT)}")
        return 0
    current = OUT.read_text(encoding="utf-8") if OUT.is_file() else ""
    if current != text:
        print(f"{OUT.relative_to(ROOT)} is stale: run python -m pipeline.agent_copy write", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
