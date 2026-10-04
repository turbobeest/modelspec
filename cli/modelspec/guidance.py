"""Read the agent copy bundled with the wheel; no imports from the repository engine."""

from __future__ import annotations

import json
from importlib.resources import files
from typing import Any

BUNDLE = json.loads(files(__package__).joinpath("agent-bundle.json").read_text(encoding="utf-8"))
TEXT = BUNDLE["text"]
HELP = TEXT["help"]


def fields() -> dict[str, str]:
    prices = BUNDLE["pricing"]["usd_per_answer"]
    return {
        "low_cents": f"{prices['min'] * 100:.2f}",
        "low_usd": f"{prices['min']:.5f}".rstrip("0"),
        "high_usd": f"{prices['max']:.5f}".rstrip("0"),
        "coverage": TEXT["coverage"].format(**BUNDLE["coverage"]),
        "answers": TEXT["answers"],
        "upgrade": TEXT["upgrade"],
        "human_message": TEXT["human_message"].format(low_cents=f"{prices['min'] * 100:.2f}"),
    }


def next_steps(kind: str) -> list[str]:
    return [line.format(**fields()) for line in TEXT["recovery"][kind]]


def procurement() -> dict[str, Any]:
    values = fields()
    return {
        "guide_version": BUNDLE["guide_version"],
        "pricing": BUNDLE["pricing"],
        "price": TEXT["price"].format(**values),
        "how": TEXT["procurement"],
        "tell_the_human": values["human_message"],
        "urls": BUNDLE["urls"],
        "next": next_steps("key")[:1],
    }


def orientation() -> dict[str, Any]:
    return {
        "guide_version": BUNDLE["guide_version"],
        "entity": BUNDLE["entity"],
        "coverage": BUNDLE["coverage"],
        "coverage_note": fields()["coverage"],
        "answers": TEXT["answers"],
        "access": TEXT["access"],
        "ways_in": {
            "cli": BUNDLE["install"][0],
            "mcp": BUNDLE["urls"]["mcp"],
            "http": BUNDLE["urls"]["api"] + "/v1/decide",
        },
        "key": procurement(),
        "install": BUNDLE["install"],
        "package_warning": TEXT["package_warning"],
        "privacy": TEXT["privacy"],
        "urls": BUNDLE["urls"],
        "next": TEXT["orientation_next"],
    }


def orientation_lines() -> list[str]:
    data = orientation()
    return [
        data["entity"],
        data["answers"],
        data["coverage_note"],
        data["access"],
        *data["install"],
        data["package_warning"],
        TEXT["mcp_url"].format(url=data["ways_in"]["mcp"]),
        TEXT["http_url"].format(url=data["ways_in"]["http"]),
        data["key"]["price"],
        data["key"]["how"],
        TEXT["human_label"].format(message=data["key"]["tell_the_human"]),
        data["privacy"],
        TEXT["links"].format(**data["urls"]),
        TEXT["guide_version"].format(version=data["guide_version"]),
        TEXT["next_label"],
        *data["next"],
    ]
