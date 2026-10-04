"""Build /decide's agent hand-off copy from the published pricing sources."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from api.ranking.engine import neutrality_commitment
from pipeline import agent_copy, pricing, worker_flags


def data(root: Path) -> dict[str, Any]:
    rates = pricing.procurement_data(pricing.load_tiers(root))
    billing_live = worker_flags.enabled(worker_flags.production_vars(root), "BILLING_ENABLED")
    commitment = neutrality_commitment()
    return {
        "summary_price_cents": f"{rates['usd_per_credit']['min'] * rates['answer_credits']['decide.summary'] * 100:.2f}",
        "full_credits": rates["answer_credits"]["decide.full"],
        "key_link": {
            "href": "/pricing/#pricing" if billing_live else "/pricing/",
            "label": "Get an API key" if billing_live else "See pricing",
            "note": "Choose a plan or pack." if billing_live else "API keys open soon.",
        },
        "mcp_clients": list(agent_copy.cli_clients()),
        "neutrality": {
            "text": "no paid placement",
            "href": commitment["neutrality_url"],
        },
    }


if __name__ == "__main__":
    print(json.dumps(data(Path(__file__).resolve().parents[1])))
