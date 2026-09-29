#!/usr/bin/env python3
"""Collect MODEL-201's subscription-plan facts (research round 2).

An auditable one-shot collector, like ``model_143_collect.py``. It registers the
primary pages read on 2026-09-29, writes the plan records in
``offerings/subscriptions/``, and files a verification claim for every fact it
adds or changes. ``modelspec verify`` stays the only writer of outcomes.

The pages were fetched and retained before this script ran (plain HTTP, or
Firecrawl markdown for pages that render client-side); ``COPIES`` pins each
source to the retained copy that was read. The script refuses to run when a
copy is missing from the local ``CopyStore``.

Verbatim coverage wording, surfaces and allowance evidence, and every null's
reason are in ``docs/research/subscriptions/2026-09-29.md``.
"""

from __future__ import annotations

import textwrap
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from decision.model import Fact, SourceRef, SubjectRef, VerificationActor, value_hash
from decision.sources import CopyStore
from decision.verify import Claim, Queue, VerificationLog

ROOT = Path(__file__).resolve().parents[1]
READ_AT = datetime(2026, 9, 29, 11, tzinfo=UTC)
COLLECTOR = VerificationActor(
    agent="claude-model-201-collector",
    model_family="anthropic",
    method="primary-source-read@2026-09-29",
)

#: New registrations: id -> (url, fetch, normaliser). Every region is the page.
SOURCES: dict[str, tuple[str, str, str]] = {
    "model-201-anthropic-max-plan": (
        "https://support.claude.com/en/articles/11049741-what-is-the-max-plan",
        "conditional_http", "html-default"),
    "model-201-anthropic-team-plan": (
        "https://support.claude.com/en/articles/9266767-what-is-the-team-plan",
        "conditional_http", "html-default"),
    "model-201-anthropic-enterprise-plan": (
        "https://support.claude.com/en/articles/9797531-what-is-the-enterprise-plan",
        "conditional_http", "html-default"),
    "model-201-openai-pricing": (
        "https://chatgpt.com/pricing/", "conditional_http", "html-default"),
    "model-201-openai-go": (
        "https://help.openai.com/en/articles/11989085-what-is-chatgpt-go",
        "rendered", "html-default"),
    "model-201-openai-codex-pricing": (
        "https://learn.chatgpt.com/docs/pricing", "conditional_http", "html-default"),
    "model-201-openai-business": (
        "https://help.openai.com/en/articles/8792828-chatgpt-business-overview",
        "rendered", "html-default"),
    "model-201-gemini-subscriptions": (
        "https://gemini.google/subscriptions/", "conditional_http", "html-default"),
    "model-201-grok-supergrok": (
        "https://grok.com/supergrok", "rendered", "text-default"),
    "model-201-xai-business": (
        "https://x.ai/grok/business", "rendered", "text-default"),
    "model-201-mistral-pricing": (
        "https://mistral.ai/pricing/", "conditional_http", "html-default"),
    "model-201-zai-subscribe": (
        "https://z.ai/subscribe", "rendered", "text-default"),
    "model-201-zai-devpack": (
        "https://docs.z.ai/devpack/overview", "conditional_http", "html-default"),
    "model-201-minimax-token-plan": (
        "https://platform.minimax.io/docs/token-plan/intro", "conditional_http",
        "html-default"),
    "model-201-alibaba-coding-plan": (
        "https://www.alibabacloud.com/help/en/model-studio/coding-plan",
        "conditional_http", "html-default"),
}

#: The retained copy read for each source, new or re-read.
COPIES: dict[str, str] = {
    "model-201-anthropic-max-plan":
        "sha256:f7b1d12e92fa6e5cb36ca3d7746f7ed288fcec24388e2ceef1c160a380bd86cb",
    "model-201-anthropic-team-plan":
        "sha256:88754473faef64796823131c86f30d6707e035c5338be7c8b11fbc692c92b920",
    "model-201-anthropic-enterprise-plan":
        "sha256:a7b332d9e3fdd81af82e70c9c24d06b270555d4376967577391a6fbd00527805",
    "model-201-openai-pricing":
        "sha256:66190ff220d3e83e341fdee5d875fc06166966c2e3d70661615c7ee870aa9f6b",
    "model-201-openai-go":
        "sha256:e1785024ee3907168bbce92247d0eafb3b34488541f1bf86157a7cae35d9bda5",
    "model-201-openai-codex-pricing":
        "sha256:9801cda32403ba3adfa7ec28ff34d45dab8b68228ae91945db7bc39b68f7fc56",
    "model-201-openai-business":
        "sha256:f25bcc5803ce6faddb6b0d6fdbd056bf7b887feb925c15f720e3b9b33445907a",
    "model-201-gemini-subscriptions":
        "sha256:ef310f79a211f38de82a05b18cc96aea326bb022fdef1829efe29172718f3a54",
    "model-201-grok-supergrok":
        "sha256:e3b66f22dc28fdd435f16fb2f9ecf943981d09003f620efbeee0f310d164f6bf",
    "model-201-xai-business":
        "sha256:4229887c1ce257e1c78412c3d0cf1011248565a7f04d76e02ac9699d93056a72",
    "model-201-mistral-pricing":
        "sha256:8bf7fcab035a0c50f564ff5ce5c5b925912b335f880b5e8f80c695652a79f121",
    "model-201-zai-subscribe":
        "sha256:7c28afd8b8729fccc25dc314b16174572b82add95de8c5a4aa4d84bf827c4b77",
    "model-201-zai-devpack":
        "sha256:1eab0aa0d83b34e7170c3350b1e9b38ba51fc197dcc258795475b39b0abaa952",
    "model-201-minimax-token-plan":
        "sha256:afd01792fed84deccc30029de5d3030c0883b28c36176908df38f988e15b8afa",
    "model-201-alibaba-coding-plan":
        "sha256:448994e29950b133d818855ed649a212ec2c147dc21160d4ebf4de54c4b5afdf",
    # MODEL-173 registrations, re-read 2026-09-29.
    "model-173-google-ai-plans":
        "sha256:7cf6d7992c5522395ac6d5bf80077873593224f09a052a358a2d3c259a73749f",
    "model-173-google-gemini-limits":
        "sha256:a0d0ea7cf0609428c67c4fc468d959c84d36c9662b22f2aadbbfe428758a36a3",
    "model-173-xai-consumer-pricing":
        "sha256:6fa0677fdddfe3963d6134a243f72cb8949a7df8539b200353b2c65ba508df14",
}

PRICE = "offering.subscription.price"
PERIOD = "offering.subscription.billing_period"
MODELS = "offering.subscription.models_covered"
ALLOWANCE = "offering.subscription.usage_allowance"
ACCESS = "offering.subscription.programmatic_or_agent_use"
FACETS = (PRICE, PERIOD, MODELS, ALLOWANCE, ACCESS)
#: MODEL-200's plan facts, kept in this order after the five above.
PLAN_FACETS = (
    "offering.subscription.surfaces",
    "offering.subscription.families_covered",
    "offering.subscription.coverage_quote",
    "offering.subscription.allowance.relative_to",
    "offering.subscription.allowance.multiplier",
    "offering.subscription.allowance.window",
    "offering.subscription.allowance.tokens",
)

LABELS = {
    PRICE: "Price",
    PERIOD: "Billing period",
    MODELS: "Models covered",
    ALLOWANCE: "Usage limits",
    ACCESS: "Agent or coding tool access",
}
#: A price claim carries no unit: the verifier then takes the unit the source
#: states ("$200 per month"), as MODEL-173's re-filed price claims do. A claimed
#: ``usd_per_billing_period`` is a unit no page writes, so it never confirms.
UNITS: dict[str, str] = {}


def known(value: Any, source: str, region: str = "page") -> dict:
    return {"state": "known", "value": value, "source": source, "region": region}


def undisclosed(source: str, region: str = "page") -> dict:
    """The source was read and does not publish the value."""
    return {"state": "not_disclosed", "source": source, "region": region}


def unread(source: str) -> dict:
    """The value may be published, but the retained copy does not show it (e.g. a
    price drawn client-side as an animation). Unknown, not a claim about the page."""
    return {"state": "unknown", "source": source}


KEEP = {"state": "keep"}

OPENAI_CHAT = [
    "openai/gpt-6-astra", "openai/gpt-6-sol", "openai/gpt-6-luna",
    "openai/gpt-5-6-sol", "openai/gpt-5-6-terra", "openai/gpt-5-6-luna",
]

#: Each plan: provider, plan, name, extra published names, and one spec per facet.
#: ``KEEP`` leaves an existing MODEL-173 fact as it is.
PLANS: list[dict[str, Any]] = [
    # ── Anthropic ────────────────────────────────────────────────────────────
    {"provider": "anthropic", "plan": "max-20x", "name": "Claude Max 20x",
     "names": ["Max 20x"],
     "note": "Price from the Max plan article; the pricing page says only 'From $100'.",
     PRICE: known(200, "model-201-anthropic-max-plan")},
    {"provider": "anthropic", "plan": "team-standard", "name": "Claude Team (Standard seat)",
     "names": ["Standard seats", "Team plan"],
     "note": "Per member; a Team plan needs at least two members. $20 per member per "
             "month when billed annually.",
     PRICE: known(25, "model-201-anthropic-team-plan"),
     PERIOD: known("monthly", "model-201-anthropic-team-plan"),
     MODELS: undisclosed("model-201-anthropic-team-plan"),
     ALLOWANCE: known("1.25x the Pro plan's per-session usage allowance",
                      "model-201-anthropic-team-plan"),
     ACCESS: known("Access to Claude Code to delegate coding tasks from concept to "
                   "completion directly from your terminal.",
                   "model-201-anthropic-team-plan")},
    {"provider": "anthropic", "plan": "team-premium", "name": "Claude Team (Premium seat)",
     "names": ["Premium seats", "Team plan"],
     "note": "Per member; $100 per member per month when billed annually.",
     PRICE: known(125, "model-201-anthropic-team-plan"),
     PERIOD: known("monthly", "model-201-anthropic-team-plan"),
     MODELS: undisclosed("model-201-anthropic-team-plan"),
     ALLOWANCE: known("6.25x the Pro plan's per-session usage allowance",
                      "model-201-anthropic-team-plan"),
     ACCESS: known("Access to Claude Code to delegate coding tasks from concept to "
                   "completion directly from your terminal.",
                   "model-201-anthropic-team-plan")},
    {"provider": "anthropic", "plan": "enterprise", "name": "Claude Enterprise",
     "names": ["Enterprise plan"],
     "note": "Seat fee covers access only; all usage is billed at standard API rates. "
             "The help article states no seat price.",
     PRICE: undisclosed("model-201-anthropic-enterprise-plan"),
     PERIOD: known("annual", "model-201-anthropic-enterprise-plan"),
     MODELS: undisclosed("model-201-anthropic-enterprise-plan"),
     ALLOWANCE: known("There are no per-seat usage limits and no included token allowance.",
                      "model-201-anthropic-enterprise-plan"),
     ACCESS: known("The seat fee gives each user access to Claude on web, desktop, and "
                   "mobile, plus Claude Code and Cowork.",
                   "model-201-anthropic-enterprise-plan")},
    # ── OpenAI ───────────────────────────────────────────────────────────────
    {"provider": "openai", "plan": "go", "name": "ChatGPT Go", "names": ["Go"],
     "note": "Models covered are the pricing page's Go column; GPT-5.6 Terra is "
             "'Limited access in Work and Codex on desktop'.",
     PRICE: known(8, "model-201-openai-codex-pricing"),
     PERIOD: known("monthly", "model-201-openai-go"),
     MODELS: known(["openai/gpt-5-6-luna", "openai/gpt-5-6-terra"],
                   "model-201-openai-pricing"),
     ALLOWANCE: undisclosed("model-201-openai-go"),
     ACCESS: known("Use Codex for lightweight coding tasks.",
                   "model-201-openai-codex-pricing")},
    {"provider": "openai", "plan": "plus", "name": "ChatGPT Plus", "names": ["Plus"],
     "note": "GPT-5 Thinking Mini is also listed; it has no catalogue ID.",
     MODELS: known(OPENAI_CHAT, "model-201-openai-pricing")},
    {"provider": "openai", "plan": "pro-5x", "name": "ChatGPT Pro 5x",
     "names": ["Pro $100", "Pro"],
     "note": "GPT-5.6 Sol Pro and GPT-5 Thinking Mini are also listed; neither has a "
             "catalogue ID.",
     PERIOD: known("monthly", "model-201-openai-codex-pricing"),
     MODELS: known(OPENAI_CHAT, "model-201-openai-pricing")},
    {"provider": "openai", "plan": "pro-20x", "name": "ChatGPT Pro 20x",
     "names": ["Pro $200", "Pro 20X", "Pro"],
     "note": "New sign-ups and upgrades paused since 2026-09-10; existing subscriptions "
             "renew. GPT-5.6 Sol Pro and GPT-5 Thinking Mini have no catalogue ID.",
     PERIOD: known("monthly", "model-201-openai-codex-pricing"),
     MODELS: known(OPENAI_CHAT, "model-201-openai-pricing")},
    {"provider": "openai", "plan": "business-standard",
     "name": "ChatGPT Business (Standard seat)", "names": ["Standard seat"],
     "note": "Per user; at least two seats. $20 per user per month billed annually.",
     PRICE: known(25, "model-201-openai-business"),
     PERIOD: known("monthly", "model-201-openai-business"),
     MODELS: undisclosed("model-201-openai-business"),
     ALLOWANCE: undisclosed("model-201-openai-business"),
     ACCESS: known("ChatGPT, ChatGPT Work, and Codex", "model-201-openai-business")},
    {"provider": "openai", "plan": "business-premium",
     "name": "ChatGPT Business (Premium seat)", "names": ["Premium seat"],
     "note": "Per user; $100 per user per month billed annually.",
     PRICE: known(125, "model-201-openai-business"),
     PERIOD: known("monthly", "model-201-openai-business"),
     MODELS: undisclosed("model-201-openai-business"),
     ALLOWANCE: known("5x more usage than Standard seats, no 5-hour usage limit",
                      "model-201-openai-business"),
     ACCESS: known("ChatGPT, ChatGPT Work, and Codex with higher usage limits",
                   "model-201-openai-business")},
    # ── Google ───────────────────────────────────────────────────────────────
    {"provider": "google-gemini-api", "plan": "ai-plus", "name": "Google AI Plus",
     "names": ["AI Plus"],
     "note": "US price from gemini.google/subscriptions; one.google.com draws it "
             "client-side.",
     PRICE: known(4.99, "model-201-gemini-subscriptions")},
    {"provider": "google-gemini-api", "plan": "ai-pro", "name": "Google AI Pro",
     "names": ["AI Pro"],
     PRICE: known(19.99, "model-201-gemini-subscriptions")},
    {"provider": "google-gemini-api", "plan": "ai-ultra-5x", "name": "Google AI Ultra 5x",
     "names": ["Ultra 5x"],
     "note": "Replaces ai-ultra: Google now sells Ultra as two priced tiers.",
     PRICE: known(99.99, "model-201-gemini-subscriptions"),
     PERIOD: known("monthly", "model-201-gemini-subscriptions"),
     MODELS: undisclosed("model-173-google-ai-plans"),
     ALLOWANCE: known("5x higher usage limits vs. AI Pro", "model-201-gemini-subscriptions"),
     ACCESS: known("Higher Google AI Studio, Google Antigravity, and Jules limits",
                   "model-173-google-ai-plans", "comparison")},
    {"provider": "google-gemini-api", "plan": "ai-ultra-20x", "name": "Google AI Ultra 20x",
     "names": ["Ultra 20x"],
     PRICE: known(199.99, "model-201-gemini-subscriptions"),
     PERIOD: known("monthly", "model-201-gemini-subscriptions"),
     MODELS: undisclosed("model-173-google-ai-plans"),
     ALLOWANCE: known("20x higher usage limits vs. AI Pro", "model-201-gemini-subscriptions"),
     ACCESS: known("Highest Google AI Studio, Google Antigravity, and Jules limits",
                   "model-173-google-ai-plans", "comparison")},
    # ── xAI ──────────────────────────────────────────────────────────────────
    {"provider": "xai", "plan": "supergrok", "name": "SuperGrok",
     "note": "Re-read 2026-09-29: the plan card still names Grok 4.6, not 4.7.",
     MODELS: known(["xai/grok-4-6"], "model-173-xai-consumer-pricing")},
    {"provider": "xai", "plan": "supergrok-plus", "name": "SuperGrok Plus",
     "note": "Re-read 2026-09-29: inherits SuperGrok's Grok 4.6.",
     MODELS: known(["xai/grok-4-6"], "model-173-xai-consumer-pricing")},
    {"provider": "xai", "plan": "supergrok-lite", "name": "SuperGrok Lite",
     "note": "Prices on grok.com/supergrok are drawn as digit animations; no copy "
             "shows them, so price and period are unknown, not undisclosed.",
     PRICE: unread("model-201-grok-supergrok"),
     PERIOD: unread("model-201-grok-supergrok"),
     MODELS: undisclosed("model-201-grok-supergrok"),
     ALLOWANCE: known("2x longer conversations in Chat", "model-201-grok-supergrok"),
     ACCESS: undisclosed("model-201-grok-supergrok")},
    {"provider": "xai", "plan": "supergrok-heavy", "name": "SuperGrok Heavy",
     "note": "Price drawn as a digit animation, as for Lite. Includes X Premium+.",
     PRICE: unread("model-201-grok-supergrok"),
     PERIOD: unread("model-201-grok-supergrok"),
     MODELS: undisclosed("model-201-grok-supergrok"),
     ALLOWANCE: known("Highest usage at the fastest speed", "model-201-grok-supergrok"),
     ACCESS: undisclosed("model-201-grok-supergrok")},
    {"provider": "xai", "plan": "business", "name": "Grok Business", "names": ["Business"],
     "note": "Per user.",
     PRICE: known(30, "model-201-xai-business"),
     PERIOD: known("monthly", "model-201-xai-business"),
     MODELS: known(["xai/grok-4-6"], "model-201-xai-business"),
     ALLOWANCE: known("Increased rate limits", "model-201-xai-business"),
     ACCESS: known("Grok Build", "model-201-xai-business")},
    # ── Mistral ──────────────────────────────────────────────────────────────
    {"provider": "mistral", "plan": "pro", "name": "Mistral Pro", "names": ["Pro"],
     "note": "Le Chat is now presented as Vibe on the pricing page.",
     PRICE: known(14.99, "model-201-mistral-pricing"),
     PERIOD: known("monthly", "model-201-mistral-pricing"),
     MODELS: undisclosed("model-201-mistral-pricing"),
     ALLOWANCE: known("More messages and web searches.", "model-201-mistral-pricing"),
     ACCESS: known("All-day coding in the CLI, IDE, or on web.",
                   "model-201-mistral-pricing")},
    {"provider": "mistral", "plan": "team", "name": "Mistral Team", "names": ["Team"],
     "note": "Per user.",
     PRICE: known(24.99, "model-201-mistral-pricing"),
     PERIOD: known("monthly", "model-201-mistral-pricing"),
     MODELS: undisclosed("model-201-mistral-pricing"),
     ALLOWANCE: undisclosed("model-201-mistral-pricing"),
     ACCESS: undisclosed("model-201-mistral-pricing")},
    # ── Z.ai ─────────────────────────────────────────────────────────────────
    *[
        {"provider": "zai", "plan": f"glm-coding-{tier.lower()}",
         "name": f"GLM Coding Plan {tier}", "names": [tier],
         "note": "Monthly list price; the page defaults to the discounted yearly rate.",
         PRICE: known(price, "model-201-zai-subscribe"),
         PERIOD: known("monthly", "model-201-zai-subscribe"),
         MODELS: known(["zhipu/glm-5-3", "zhipu/glm-5-3-flash"], "model-201-zai-devpack"),
         ALLOWANCE: known(allowance, "model-201-zai-subscribe"),
         ACCESS: known("The plan can be applied to coding tools such as Claude Code, "
                       "Cline, and OpenCode", "model-201-zai-devpack")}
        for tier, price, allowance in (
            ("Lite", 18, "10,000 Credits / week"),
            ("Pro", 80, "6× Lite usage"),
            ("Max", 168, "14× Lite usage"),
        )
    ],
    # ── MiniMax ──────────────────────────────────────────────────────────────
    *[
        {"provider": "minimax", "plan": f"token-{tier.lower()}",
         "name": f"MiniMax Token Plan {tier}", "names": [tier],
         "note": "The Token Plan replaced MiniMax's Coding Plan. Coverage names families "
                 "('M3 / M2.7'), not model IDs.",
         PRICE: known(price, "model-201-minimax-token-plan"),
         PERIOD: known("monthly", "model-201-minimax-token-plan"),
         MODELS: undisclosed("model-201-minimax-token-plan"),
         ALLOWANCE: known("5-hour rolling and weekly windows", "model-201-minimax-token-plan"),
         ACCESS: known("OpenClaw, Claude Code, Cursor, TRAE, Hermes Agent",
                       "model-201-minimax-token-plan")}
        for tier, price in (("Plus", 22), ("Max", 55), ("Ultra", 132))
    ],
    # ── Alibaba Cloud Model Studio ───────────────────────────────────────────
    {"provider": "alibaba-model-studio", "plan": "coding-pro", "name": "Coding Plan Pro",
     "names": ["Pro"],
     "note": "qwen3-max-2026-01-23 is also supported; it has no catalogue ID. "
             "Slots are limited.",
     PRICE: known(50, "model-201-alibaba-coding-plan"),
     PERIOD: known("monthly", "model-201-alibaba-coding-plan"),
     MODELS: known([
         "qwen/qwen3-7-plus", "qwen/qwen3-6-plus", "moonshot/kimi-k2-5", "zhipu/glm-5",
         "minimax/minimax-m2-5", "qwen/qwen3-5-plus", "qwen/qwen3-coder-next",
         "qwen/qwen3-coder-plus", "zhipu/glm-4-7",
     ], "model-201-alibaba-coding-plan"),
     ALLOWANCE: known("Up to 6,000 requests per 5 hours Up to 45,000 requests per week "
                      "Up to 90,000 requests per month", "model-201-alibaba-coding-plan"),
     ACCESS: known("This plan is for interactive use in programming tools such as Claude "
                   "Code, Qoder, Qoder CN, and OpenClaw.", "model-201-alibaba-coding-plan")},
]

#: Plans withdrawn from the catalogue, with why.
REMOVED = {
    "google-gemini-api/subscription/ai-ultra":
        "split into ai-ultra-5x and ai-ultra-20x, which Google prices separately",
}

HEADERS = {
    "anthropic": "MODEL-173 (read 2026-09-28), MODEL-200's plan facts, and MODEL-201\n"
                 "# (read 2026-09-29).",
    "google-gemini-api": "MODEL-173 (read 2026-09-28), MODEL-200's plan facts, and MODEL-201\n"
                 "# (read 2026-09-29).",
    "openai": "MODEL-173 (read 2026-09-28), MODEL-200's plan facts, and MODEL-201\n"
                 "# (read 2026-09-29).",
    "xai": "MODEL-173 (read 2026-09-28), MODEL-200's plan facts, and MODEL-201\n"
                 "# (read 2026-09-29).",
    "mistral": "MODEL-201. Primary sources read 2026-09-29.",
    "zai": "MODEL-201. Primary sources read 2026-09-29.",
    "minimax": "MODEL-201. Primary sources read 2026-09-29.",
    "alibaba-model-studio": "MODEL-201. Primary sources read 2026-09-29.",
}


class _Dumper(yaml.SafeDumper):
    """The repository's style: leaf mappings and lists inline, no anchors."""

    def ignore_aliases(self, data: Any) -> bool:
        return True


def _leaf(items) -> bool:
    return all(not isinstance(v, (dict, list)) for v in items)


_Dumper.add_representer(dict, lambda d, data: d.represent_mapping(
    "tag:yaml.org,2002:map", data.items(), flow_style=_leaf(data.values()) or None))
_Dumper.add_representer(list, lambda d, data: d.represent_sequence(
    "tag:yaml.org,2002:seq", data, flow_style=bool(data) and _leaf(data) or None))


def _dump(data: Any) -> str:
    return yaml.dump(data, Dumper=_Dumper, sort_keys=False, allow_unicode=True, width=100)


def plan_id(spec: dict) -> str:
    return f"{spec['provider']}/subscription/{spec['plan']}"


def source_ref(source: str, region: str) -> SourceRef:
    return SourceRef(source_id=source, snapshot_ref=COPIES[source], cited_regions=[region])


def build_fact(sid: str, facet: str, spec: dict) -> Fact:
    subject = SubjectRef(kind="offering", id=sid)
    fid = f"{sid}#{facet}"
    if spec["state"] == "known":
        return Fact(id=fid, subject=subject, facet=facet, state="known", value=spec["value"],
                    sources=[source_ref(spec["source"], spec["region"])])
    if spec["state"] == "not_disclosed":
        return Fact(id=fid, subject=subject, facet=facet, state="not_disclosed",
                    checked_sources=[spec["source"]],
                    sources=[source_ref(spec["source"], spec["region"])])
    return Fact(id=fid, subject=subject, facet=facet, state="unknown",
                checked_sources=[spec["source"]])


def fact_row(fact: Fact) -> dict:
    row = fact.model_dump(mode="json", exclude_none=True, exclude_defaults=True)
    row = {"id": fact.id, "subject": {"kind": "offering", "id": fact.subject.id},
           "facet": fact.facet, "state": fact.state, "value": fact.value, **{
               k: v for k, v in row.items()
               if k not in {"id", "subject", "facet", "state", "value"}}}
    order = ["id", "subject", "facet", "state", "value", "checked_sources", "sources"]
    return {k: row[k] for k in order if k in row}


def dump_file(provider: str, rows: list[dict], notes: dict[str, str]) -> str:
    out = [f"# {HEADERS[provider]}",
           "# Verbatim wording, surfaces and every null's reason:",
           "# docs/research/subscriptions/2026-09-29.md (scripts/model_201_collect.py).",
           "# Unknown means the retained copy does not show the value; not_disclosed",
           "# means the page was read and does not publish it."]
    for row in rows:
        sid = f"{row['provider']}/subscription/{row['plan']}"
        if sid in notes:
            out.extend(textwrap.wrap(f"{row['name']}: {notes[sid]}", width=86,
                                     initial_indent="# ", subsequent_indent="#   "))
        body = _dump([row])
        out.append(body.rstrip("\n"))
    return "\n".join(out) + "\n"


def register_sources() -> None:
    path = ROOT / "registry" / "sources.yaml"
    text = path.read_text(encoding="utf-8")
    added = []
    for sid, (url, fetch, normaliser) in SOURCES.items():
        if f"- id: {sid}\n" in text:
            continue
        added.append({"id": sid, "url": url, "fetch": fetch, "normaliser": normaliser,
                      "cited_regions": [{"id": "page", "locator": {"kind": "page", "value": ""}}]})
    if added:
        block = _dump(added)
        path.write_text(text.rstrip("\n") + "\n" + block, encoding="utf-8")


def main(dry_run: bool = False) -> None:
    """Write the records; file claims unless ``dry_run`` (validate first: the queue is
    append-only)."""
    store = CopyStore()
    missing = sorted(s for s, ref in COPIES.items() if not store.has(ref))
    if missing:
        raise SystemExit(f"retained copies missing from {store.root}: {missing}")
    register_sources()

    queue = Queue(ROOT / "verification")
    verified = {
        (record.target.id, record.target.value_hash)
        for record in VerificationLog(ROOT / "verification").latest().values()
        if record.outcome == "verified"
    }
    notes: dict[str, str] = {}
    filed = 0
    by_provider: dict[str, list[dict]] = {}
    directory = ROOT / "offerings" / "subscriptions"
    for path in sorted(directory.glob("*.yaml")):
        rows = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        by_provider[path.stem] = [
            r for r in rows if f"{r['provider']}/subscription/{r['plan']}" not in REMOVED
        ]

    for rows in by_provider.values():
        for row in rows:
            order = {f: i for i, f in enumerate((*FACETS, *PLAN_FACETS))}
            row["facts"].sort(key=lambda fact: order.get(fact["facet"], len(order)))

    for spec in PLANS:
        sid = plan_id(spec)
        rows = by_provider.setdefault(spec["provider"], [])
        row = next((r for r in rows if r["plan"] == spec["plan"]), None)
        if row is None:
            row = {"kind": "subscription", "provider": spec["provider"], "plan": spec["plan"],
                   "name": spec["name"], "facts": []}
            rows.append(row)
        if spec.get("note"):
            notes[sid] = spec["note"]
        existing = {f["facet"]: f for f in row["facts"]}
        names = [spec["name"], *spec.get("names", []), spec["plan"]]
        for facet in FACETS:
            fs = spec.get(facet, KEEP if facet in existing else None)
            if fs is None:
                raise SystemExit(f"{sid}: no value or KEEP for {facet}")
            if fs["state"] == "keep":
                continue
            fact = build_fact(sid, facet, fs)
            existing[facet] = fact_row(fact)
            # Idempotent: a value already verified at this ID is not filed again.
            if (fact.state != "unknown" and not dry_run
                    and (fact.id, value_hash(fact.value)) not in verified):
                queue.file(
                    Claim.from_fact(fact, names=names, collector=COLLECTOR,
                                    unit=UNITS.get(facet), label=LABELS[facet]),
                    at=READ_AT,
                )
                filed += 1
        row["facts"] = [existing[f] for f in FACETS] + [
            fact for facet, fact in existing.items() if facet not in FACETS]

    for provider, rows in by_provider.items():
        (directory / f"{provider}.yaml").write_text(
            dump_file(provider, rows, notes), encoding="utf-8")
    print(f"filed {filed} claims for {len(PLANS)} plans")


if __name__ == "__main__":
    import sys

    main(dry_run="--dry-run" in sys.argv[1:])
