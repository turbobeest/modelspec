#!/usr/bin/env python3
"""Collect MODEL-205's plans from subscription-only vendors.

An auditable one-shot collector, in the pattern of ``model_201_collect.py``.
Cursor, GitHub Copilot and Perplexity sell plans that bundle several labs'
models and serve nothing pay-per-use; ``registry/providers.yaml`` lists them
under ``subscription_vendors``. This script registers the primary pages read on
2026-09-29, writes ``offerings/subscriptions/<vendor>.yaml`` and, with
``--file``, files a verification claim for each fact it states.
``modelspec verify`` stays the only writer of outcomes.

The pages were fetched and retained before this script ran: Cursor's and
GitHub's over plain HTTP, Perplexity's (which answers plain HTTP with a
challenge) as the rendered page text. ``COPIES`` pins each source to the copy
read, and the script refuses to run when one is missing from the ``CopyStore``.

Model names become catalogue IDs only by exact display name (case and
punctuation aside). A name with no card, or only a differently named card
("Gemini 3.1 Pro" has only "Gemini 3.1 Pro Preview"), is left out: a null beats
a guess. Every omission, and every null's reason, is in
``docs/research/subscriptions/2026-09-29-vendors.md``.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from decision.model import Fact, SourceRef, SubjectRef, VerificationActor, value_hash
from decision.sources import CopyStore
from decision.verify import Claim, Queue, VerificationLog

ROOT = Path(__file__).resolve().parents[1]
READ_AT = datetime(2026, 9, 29, 14, tzinfo=UTC)
COLLECTOR = VerificationActor(
    agent="claude-model-205-collector",
    model_family="anthropic",
    method="primary-source-read@2026-09-29",
)

#: id -> (url, fetch, normaliser). Every region is the page.
SOURCES: dict[str, tuple[str, str, str]] = {
    "model-205-cursor-models-and-pricing": (
        "https://cursor.com/docs/models-and-pricing", "conditional_http", "html-default"),
    "model-205-cursor-pricing": (
        "https://cursor.com/pricing", "conditional_http", "html-default"),
    # The plan tables mark coverage with icons whose words are their aria-label.
    "model-205-github-copilot-plans": (
        "https://docs.github.com/en/copilot/get-started/plans", "conditional_http",
        "html-icon-labels"),
    "model-205-perplexity-pro": (
        "https://www.perplexity.ai/pro", "rendered", "text-default"),
    "model-205-perplexity-pro-help": (
        "https://www.perplexity.ai/help-center/en/articles/10352901-what-is-perplexity-pro",
        "rendered", "text-default"),
}

COPIES: dict[str, str] = {
    "model-205-cursor-models-and-pricing":
        "sha256:1a2f73d64bf0f7ce901f1445c42caa083fd16c107c90d96194582b3a633a07a2",
    "model-205-cursor-pricing":
        "sha256:f63d70b9ada007add6c002f1fc7efc7a1b81d138376f9acecc34117d10ac8298",
    "model-205-github-copilot-plans":
        "sha256:e2c94865bd496323ff061048b3d2993f06ad7a075aa25770ec68f5992851193d",
    # document.body.innerText after declining optional cookies and opening the
    # FAQ answer "What models do I get access to?".
    "model-205-perplexity-pro":
        "sha256:b199367eff97ae6bcfbc3e04c1a717a163fcedce3a50b2a217aef1c0fd281d8f",
    "model-205-perplexity-pro-help":
        "sha256:31df9c450daa1b858ce71ee11b116bea3b3c8ff93fc26cd38c2589475b4b8b65",
}

PRICE = "offering.subscription.price"
PERIOD = "offering.subscription.billing_period"
MODELS = "offering.subscription.models_covered"
ALLOWANCE = "offering.subscription.usage_allowance"
ACCESS = "offering.subscription.programmatic_or_agent_use"
SURFACES = "offering.subscription.surfaces"
RELATIVE_TO = "offering.subscription.allowance.relative_to"
MULTIPLIER = "offering.subscription.allowance.multiplier"
REQUIRED = (PRICE, PERIOD, MODELS, ALLOWANCE, ACCESS)
#: MODEL-200's plan facts. Those this round does not state stay ``unknown``.
PLAN_FACETS = (
    SURFACES,
    "offering.subscription.families_covered",
    "offering.subscription.coverage_quote",
    RELATIVE_TO,
    MULTIPLIER,
    "offering.subscription.allowance.window",
    "offering.subscription.allowance.tokens",
)
LABELS = {
    PRICE: "Price",
    PERIOD: "Billing period",
    MODELS: "Models covered",
    ALLOWANCE: "Usage limits",
    ACCESS: "Agent or coding tool access",
    SURFACES: "Where the plan works",
    RELATIVE_TO: "Allowance relative to",
    MULTIPLIER: "Allowance multiplier",
}


def known(value: Any, source: str) -> dict:
    return {"state": "known", "value": value, "source": source}


def undisclosed(source: str) -> dict:
    """The source was read and does not publish the value."""
    return {"state": "not_disclosed", "source": source}


def unread(source: str) -> dict:
    """The page gives the value only in another form (a monthly equivalent of an
    annual price), so the billed amount is unknown, not undisclosed."""
    return {"state": "unknown", "source": source}


CURSOR_DOCS = "model-205-cursor-models-and-pricing"
CURSOR_PAGE = "model-205-cursor-pricing"
COPILOT = "model-205-github-copilot-plans"
PPLX = "model-205-perplexity-pro"

#: "Cursor Models" (Grok 4.7, 4.6, 4.5; Composer 2.5 has no card) and the "Other
#: Models" pricing table (Gemini 3.1 Pro has only a Preview card, so it is out).
CURSOR_COVERED = sorted([
    "xai/grok-4-7", "xai/grok-4-6", "xai/grok-4-5",
    "anthropic/claude-fable-5-1", "anthropic/claude-opus-5-5", "anthropic/claude-sonnet-5-5",
    "google/gemini-3-8-flash",
    "openai/gpt-5-6-luna", "openai/gpt-5-6-sol", "openai/gpt-5-6-terra",
    "meta/muse-spark-1-3",
])
CURSOR_INDIVIDUAL = {
    MODELS: known(CURSOR_COVERED, CURSOR_DOCS),
    ALLOWANCE: known("There are two separate usage pools, each resetting with your monthly "
                     "billing cycle", CURSOR_DOCS),
    ACCESS: known("Pro, Pro Plus, and Ultra include unlimited tab completions, extended agent "
                  "usage limits on all models, access to Bugbot, and access to Cloud Agents.",
                  CURSOR_DOCS),
    SURFACES: known(["coding_tool:cursor"], CURSOR_DOCS),
}
#: No sentence ties a Teams seat to where it works, so its surfaces stay unknown.
CURSOR_TEAMS = {
    MODELS: undisclosed(CURSOR_DOCS),
    ACCESS: known("Cloud agents and automations with shared team context", CURSOR_PAGE),
}

#: GitHub's "Available models" rows, by plan column, where the cell is "Included".
#: No card: MAI-Code-1.1-Flash. Every other row has one.
_COPILOT_ALL = [
    "anthropic/claude-haiku-4-5-20251001", "anthropic/claude-sonnet-5",
    "anthropic/claude-sonnet-5-5", "google/gemini-3-5-flash", "google/gemini-3-6-flash",
    "google/gemini-3-7-flash", "google/gemini-3-8-flash", "openai/gpt-5-mini",
    "openai/gpt-5-3-codex", "openai/gpt-5-4", "openai/gpt-5-4-mini", "openai/gpt-5-6-luna",
    "openai/gpt-5-6-terra", "openai/gpt-6-luna", "xai/grok-4-5", "xai/grok-4-6", "xai/grok-4-7",
    "moonshot/kimi-k2-7-code", "moonshot/kimi-k3",
]
_COPILOT_PREMIUM = [
    "anthropic/claude-opus-4-7", "anthropic/claude-opus-4-8", "anthropic/claude-opus-5",
    "anthropic/claude-opus-5-5", "anthropic/claude-fable-5", "anthropic/claude-fable-5-1",
    "openai/gpt-5-5", "openai/gpt-5-6-sol", "openai/gpt-6-astra", "openai/gpt-6-sol",
]
COPILOT_COVERED = {
    "pro": sorted([*_COPILOT_ALL, "anthropic/claude-sonnet-4-6"]),
    "pro-plus": sorted([*_COPILOT_ALL, *_COPILOT_PREMIUM, "anthropic/claude-sonnet-4-6",
                        "openai/gpt-5-4-nano"]),
    "max": sorted([*_COPILOT_ALL, *_COPILOT_PREMIUM, "openai/gpt-5-4-nano"]),
    "business": sorted([*_COPILOT_ALL, *_COPILOT_PREMIUM]),
    "enterprise": sorted([*_COPILOT_ALL, *_COPILOT_PREMIUM]),
}
COPILOT_COMMON = {
    ACCESS: known("All plans include Copilot CLI and Copilot app.", COPILOT),
    SURFACES: known(["coding_tool:copilot-cli"], COPILOT),
}


def _copilot(plan: str, name: str, price: int, allowance: str, note: str | None = None) -> dict:
    # The page names each plan "Copilot Pro", "Copilot Pro+", ...
    return {"provider": "github-copilot", "plan": plan, "name": name, "note": note,
            "names": [name.removeprefix("GitHub ")],
            PRICE: known(price, COPILOT), PERIOD: known("monthly", COPILOT),
            MODELS: known(COPILOT_COVERED[plan], COPILOT),
            ALLOWANCE: known(allowance, COPILOT), **COPILOT_COMMON}


PLANS: list[dict[str, Any]] = [
    # ── Cursor ───────────────────────────────────────────────────────────────
    {"provider": "cursor", "plan": "pro", "name": "Cursor Pro", "names": ["Pro"],
     PRICE: known(20, CURSOR_DOCS), PERIOD: known("monthly", CURSOR_DOCS), **CURSOR_INDIVIDUAL},
    {"provider": "cursor", "plan": "pro-plus", "name": "Cursor Pro Plus", "names": ["Pro Plus", "Pro+"],
     PRICE: known(60, CURSOR_DOCS), PERIOD: known("monthly", CURSOR_DOCS), **CURSOR_INDIVIDUAL},
    {"provider": "cursor", "plan": "ultra", "name": "Cursor Ultra", "names": ["Ultra"],
     PRICE: known(200, CURSOR_DOCS), PERIOD: known("monthly", CURSOR_DOCS), **CURSOR_INDIVIDUAL},
    {"provider": "cursor", "plan": "teams-standard", "name": "Cursor Teams (Standard seat)",
     "names": ["Standard", "Teams"],
     "note": "Per user. Third-party model requests add a Cursor Token Rate of $0.25 per "
             "million tokens on Teams and Enterprise.",
     PRICE: known(40, CURSOR_DOCS), PERIOD: known("monthly", CURSOR_DOCS),
     ALLOWANCE: undisclosed(CURSOR_DOCS), **CURSOR_TEAMS},
    {"provider": "cursor", "plan": "teams-premium", "name": "Cursor Teams (Premium seat)",
     "names": ["Premium", "Teams"],
     "note": "Per user. Third-party model requests add a Cursor Token Rate of $0.25 per "
             "million tokens on Teams and Enterprise.",
     PRICE: known(120, CURSOR_DOCS), PERIOD: known("monthly", CURSOR_DOCS),
     ALLOWANCE: known("5x the Standard limits on Agent", CURSOR_DOCS),
     RELATIVE_TO: known("cursor/subscription/teams-standard", CURSOR_DOCS),
     MULTIPLIER: known(5, CURSOR_DOCS), **CURSOR_TEAMS},
    # ── GitHub Copilot ───────────────────────────────────────────────────────
    _copilot("pro", "GitHub Copilot Pro", 10,
             "Total monthly AI credits: 1,500",
             "Free for some users (verified teachers, maintainers of popular open source "
             "projects)."),
    _copilot("pro-plus", "GitHub Copilot Pro+", 39,
             "Total monthly AI credits: 7,000"),
    _copilot("max", "GitHub Copilot Max", 100,
             "Total monthly AI credits: 20,000"),
    _copilot("business", "GitHub Copilot Business", 19,
             "GitHub AI Credits per user per month: 1,900",
             "Per granted seat."),
    _copilot("enterprise", "GitHub Copilot Enterprise", 39,
             "GitHub AI Credits per user per month: 3,900",
             "Per granted seat; requires GitHub Enterprise Cloud."),
    # ── Perplexity ───────────────────────────────────────────────────────────
    {"provider": "perplexity", "plan": "pro", "name": "Perplexity Pro", "names": ["Pro"],
     "note": "The page gives only '$17 /month when billed annually', a monthly equivalent of an "
             "annual price, so the billed amount and period stay unknown. Its FAQ names GPT-5.6 "
             "Terra and Claude Sonnet 5; the help article (last modified 2026-09-03) names older "
             "models. Gemini 3.1 Pro Thinking, Grok 4.1 and Sonar 2 have no card.",
     PRICE: unread(PPLX), PERIOD: unread(PPLX),
     MODELS: known(["anthropic/claude-sonnet-5", "openai/gpt-5-6-terra"], PPLX),
     ALLOWANCE: known("4,000 bonus credits", PPLX),
     ACCESS: known("Expanded Computer access", PPLX)},
    {"provider": "perplexity", "plan": "max", "name": "Perplexity Max", "names": ["Max"],
     "note": "The page gives only '$167 /month when billed annually'; see Perplexity Pro.",
     PRICE: unread(PPLX), PERIOD: unread(PPLX),
     MODELS: undisclosed(PPLX),
     ALLOWANCE: known("10,000 monthly credits", PPLX),
     ACCESS: known("Maximum Computer usage", PPLX)},
]

HEADER = ("# MODEL-205. Primary sources read 2026-09-29; {vendor} is a subscription-only vendor\n"
          "# (registry/providers.yaml, subscription_vendors): it sells these plans and nothing\n"
          "# pay-per-use. Omissions and every null's reason:\n"
          "# docs/research/subscriptions/2026-09-29-vendors.md (scripts/model_205_collect.py).\n"
          "# unknown: not stated in the form the facet holds, or not researched this round.")


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


def build_fact(sid: str, facet: str, spec: dict | None) -> Fact:
    subject = SubjectRef(kind="offering", id=sid)
    fid = f"{sid}#{facet}"
    if spec is None:  # a MODEL-200 plan fact this round does not state
        return Fact(id=fid, subject=subject, facet=facet, state="unknown")
    ref = [SourceRef(source_id=spec["source"], snapshot_ref=COPIES[spec["source"]],
                     cited_regions=["page"])]
    if spec["state"] == "known":
        return Fact(id=fid, subject=subject, facet=facet, state="known", value=spec["value"],
                    sources=ref)
    if spec["state"] == "not_disclosed":
        return Fact(id=fid, subject=subject, facet=facet, state="not_disclosed",
                    checked_sources=[spec["source"]], sources=ref)
    return Fact(id=fid, subject=subject, facet=facet, state="unknown",
                checked_sources=[spec["source"]])


def fact_row(fact: Fact) -> dict:
    row = fact.model_dump(mode="json", exclude_none=True, exclude_defaults=True)
    row = {"id": fact.id, "subject": {"kind": "offering", "id": fact.subject.id},
           "facet": fact.facet, "state": fact.state, "value": fact.value, **row}
    order = ["id", "subject", "facet", "state", "value", "checked_sources", "sources"]
    return {k: row[k] for k in order if k in row}


def register_sources() -> None:
    path = ROOT / "registry" / "sources.yaml"
    text = path.read_text(encoding="utf-8")
    added = [{"id": sid, "url": url, "fetch": fetch, "normaliser": normaliser,
              "cited_regions": [{"id": "page", "locator": {"kind": "page", "value": ""}}]}
             for sid, (url, fetch, normaliser) in SOURCES.items()
             if f"- id: {sid}\n" not in text]
    if added:
        path.write_text(text.rstrip("\n") + "\n" + _dump(added), encoding="utf-8")


def main(file_claims: bool) -> None:
    store = CopyStore()
    missing = sorted(s for s, ref in COPIES.items() if not store.has(ref))
    if missing:
        raise SystemExit(f"retained copies missing from {store.root}: {missing}")
    register_sources()
    verified = {
        (record.target.id, record.target.value_hash)
        for record in VerificationLog(ROOT / "verification").latest().values()
        if record.outcome == "verified"
    }
    queue = Queue(ROOT / "verification")
    by_vendor: dict[str, list[str]] = {}
    filed = 0
    for spec in PLANS:
        sid = f"{spec['provider']}/subscription/{spec['plan']}"
        facts = [build_fact(sid, facet, spec.get(facet)) for facet in (*REQUIRED, *PLAN_FACETS)]
        row = {"kind": "subscription", "provider": spec["provider"], "plan": spec["plan"],
               "name": spec["name"], "facts": [fact_row(f) for f in facts]}
        lines = [f"# {spec['name']}: {spec['note']}"] if spec.get("note") else []
        by_vendor.setdefault(spec["provider"], []).append(
            "\n".join([*lines, _dump([row]).rstrip("\n")]))
        names = [spec["name"], *spec.get("names", []), spec["plan"]]
        for fact in facts:
            if not file_claims or fact.state == "unknown":
                continue
            # Idempotent: a value already verified at this ID is not filed again.
            if (fact.id, value_hash(fact.value)) in verified:
                continue
            queue.file(Claim.from_fact(fact, names=names, collector=COLLECTOR,
                                       label=LABELS[fact.facet]), at=READ_AT)
            filed += 1
    directory = ROOT / "offerings" / "subscriptions"
    for vendor, blocks in by_vendor.items():
        body = HEADER.format(vendor=vendor) + "\n" + "\n".join(blocks) + "\n"
        (directory / f"{vendor}.yaml").write_text(body, encoding="utf-8")
    print(f"wrote {len(PLANS)} plans; filed {filed} claims")


if __name__ == "__main__":
    main(file_claims="--file" in sys.argv[1:])
