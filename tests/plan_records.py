"""The MODEL-200 test catalogue: Claude models, plans with and without sourced
coverage, a metered rival, and self-hostable models.

Shared by ``tests/test_decision_plans.py`` and the golden file it checks
``access``-less decisions against (``tests/fixtures/model-200-no-access.json``).
"""

from __future__ import annotations

from decision.snapshot import SnapshotInputs
from tests.snapshot_records import SOURCES, fact, model, offering, subscription

CONTEXT = "model.context_window"
OPUS = "anthropic/claude-opus-5-5"
SONNET = "anthropic/claude-sonnet-5"
OLD_OPUS = "anthropic/claude-opus-3"
MAX = "anthropic/subscription/max-20x"
PRO = "anthropic/subscription/pro"
PLUS = "openai/subscription/plus"
CLAUDE_SURFACES = ["chat_app", "coding_tool:claude-code", "desktop_app", "mobile_app"]


def _model(mid, context, *, lifecycle="active", openness="closed_weights", fits=None):
    facts = [fact("model", mid, CONTEXT, context),
             fact("model", mid, "model.weights_openness", openness)]
    if fits is not None:
        facts.append(fact("model", mid, "model.fits_hardware", fits))
    return model(mid, lifecycle=lifecycle, facts=facts)


def _offering(mid, provider, price):
    row = offering(mid, provider, price=price)
    oid = f"{provider}/{mid}/global/standard"
    row["facts"].append(fact("offering", oid, "offering.price.output", price, source="src-pricing"))
    return row


def _plan(provider, plan, *, price, covered=None, families=None, quote=None, surfaces=None,
          relative_to=None, multiplier=None):
    sid = f"{provider}/subscription/{plan}"
    row = subscription(provider, plan)

    def put(facet, value):
        facet = "offering.subscription." + facet
        row["facts"] = [f for f in row["facts"] if f["facet"] != facet]
        if value == "not_disclosed":
            row["facts"].append(fact("offering", sid, facet, None, state="not_disclosed",
                                     source="src-pricing"))
        elif value is not None:
            row["facts"].append(fact("offering", sid, facet, value, source="src-pricing"))

    put("price", price)
    put("models_covered", covered or "not_disclosed")
    put("families_covered", families)
    put("coverage_quote", quote)
    put("surfaces", surfaces)
    put("allowance.relative_to", relative_to)
    put("allowance.multiplier", multiplier)
    row["name"] = {"max-20x": "Claude Max 20x", "pro": "Claude Pro", "plus": "ChatGPT Plus",
                   "team-api": "Team API"}.get(plan, plan)
    return row


def inputs(*, max_coverage: bool = True) -> SnapshotInputs:
    """``max_coverage=False`` is today's Max 20x: its coverage is not disclosed."""
    models = [
        _model(OPUS, 200_000),
        _model(SONNET, 200_000),
        _model(OLD_OPUS, 400_000, lifecycle="retired"),
        _model("other/huge", 500_000),
        _model("acme/tiny", 50_000, openness="open_weights", fits=["apple_m3_max"]),
        _model("acme/unfit", 60_000, openness="open_weights"),
        _model("acme/closed", 70_000),
    ]
    offerings = [
        _offering(OPUS, "anthropic", 15.0),
        _offering(SONNET, "anthropic", 3.0),
        _offering(OPUS, "aws-bedrock", 18.0),
        _offering("other/huge", "openai", 30.0),
    ]
    subscriptions = [
        _plan("anthropic", "max-20x", price=200, surfaces=CLAUDE_SURFACES,
              families=["anthropic/claude-opus", "anthropic/claude-sonnet"] if max_coverage else None,
              quote="Opus and Sonnet models" if max_coverage else None,
              relative_to=PRO, multiplier=20),
        _plan("anthropic", "pro", price=20, surfaces=CLAUDE_SURFACES,
              families=["anthropic/claude-sonnet"] if max_coverage else None,
              quote="Sonnet models" if max_coverage else None),
        _plan("anthropic", "team-api", price="not_disclosed", surfaces=["api"],
              covered=[SONNET]),
        _plan("openai", "plus", price=20),
    ]
    return SnapshotInputs(models=models, offerings=offerings, sources=SOURCES,
                          subscriptions=subscriptions)


#: Specs without ``access``, whose decisions must not change (MODEL-200).
NO_ACCESS_SPECS = [
    {"spec_version": 1, "optimize": {"max": CONTEXT}, "explain": "none"},
    {"spec_version": 1, "optimize": {"max": CONTEXT}, "explain": "summary"},
    {"spec_version": 1, "optimize": {"min": "offering.cost_per_task"}, "explain": "none"},
    {"spec_version": 1, "optimize": {"max": CONTEXT}, "explain": "none",
     "estate": {"plans": [MAX]}},
    {"spec_version": 1, "optimize": {"max": CONTEXT}, "explain": "none",
     "estate": {"plans": [MAX, PLUS], "providers": ["openai"], "devices": ["apple_m3_max"]}},
    {"spec_version": 1, "optimize": {"max": CONTEXT}, "explain": "none",
     "estate": {"plans": [MAX], "exhausted": [MAX], "providers": ["anthropic"]}},
]
