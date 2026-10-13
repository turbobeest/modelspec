"""The official Claude Code marketplace and reporting skill ship together."""

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/modelspec"


def test_marketplace_resolves_the_official_plugin() -> None:
    marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    manifest = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text())
    assert marketplace == {
        "name": "modelspec",
        "description": "Official ModelSpec plugins for reporting sourced model-selection answers.",
        "owner": {"name": "Sparks & Sawdust LLC"},
        "plugins": [{"name": "modelspec", "source": "./plugins/modelspec"}],
    }
    assert (ROOT / marketplace["plugins"][0]["source"]).resolve() == PLUGIN
    assert manifest["name"] == "modelspec"
    assert manifest["version"] == "0.1.0"
    assert manifest["author"] == marketplace["owner"]
    assert manifest["homepage"] == "https://modelspec.dev"
    assert manifest["repository"] == "https://github.com/turbobeest/modelspec"
    assert manifest["license"] == "MIT"
    assert manifest["description"]
    assert "mcpServers" not in manifest
    assert not (PLUGIN / ".mcp.json").exists()


def test_reporting_skill_metadata_and_response_fields() -> None:
    skill = (PLUGIN / "skills/report-modelspec-answer/SKILL.md").read_text()
    _, frontmatter, body = skill.split("---", 2)
    metadata = yaml.safe_load(frontmatter)
    assert metadata["name"] == "report-modelspec-answer"
    assert metadata["description"].startswith(
        "Use after any ModelSpec decide, compare or rank result"
    )
    for name in ("summary_for_user", "must_mention", "next_move"):
        assert name in metadata["description"]
        assert f"`{name}`" in body
