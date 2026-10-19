"""Check generated pins and the display fixture after the #819 merge."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[7]
OUT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

import yaml
from api.worker import openapi
from pipeline import agent_copy
from qa.contracts import source_hashes


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


paths = [
    "docs/agents.md", "mcp/src/agent-copy.json", "cli/modelspec/agent-bundle.json",
    "api/worker/src/agent_guide.py", "api/worker/openapi.yaml", "qa/fixtures/mcp-tools.json",
]
cli = json.loads((ROOT / paths[2]).read_text())
qa = json.loads((ROOT / paths[-1]).read_text())
literal_pins = {
    "mcp": hashlib.sha256(agent_copy.render(agent_copy.copy()).encode()).hexdigest(),
    "guide": hashlib.sha256(agent_copy.guide()[1].encode()).hexdigest(),
    "cli_text": hashlib.sha256(json.dumps(agent_copy.cli_text(), sort_keys=True).encode()).hexdigest(),
}
test = (ROOT / "tests/test_decision_link.py").read_text()
result = {
    "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "merged_upstream": "34c6dbef95371cff728a7a28aba33dcffe3e50e3",
    "guide_version": cli["guide_version"],
    "artifact_hashes": {path: sha(path) for path in paths},
    "literal_pins": literal_pins,
    "literal_pins_match": all(value in test for value in literal_pins.values()),
    "qa_pins_match": qa["source_hashes"] == source_hashes(),
    "cli_pins_match": all(sha(path) == expected for path, expected in cli["source_hashes"].items()),
}
assert result["literal_pins_match"] and result["qa_pins_match"] and result["cli_pins_match"]
assert "decision_snapshot:" not in (ROOT / "api/worker/openapi.yaml").read_text()
(OUT / "generated-pins.json").write_text(json.dumps(result, indent=2) + "\n")
(OUT.parent / "generated-pins.json").write_text(json.dumps(result, indent=2) + "\n")

os.environ["DATA_SPLIT_ENABLED"] = "true"
flag_on = openapi.render()
operation = yaml.safe_load(flag_on)["paths"]["/v1/vocabulary"]["get"]
schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
assert schema["properties"]["as_of"]["format"] == "date"
assert "as_of" not in schema["required"]
proof = {
    "render_sha256": hashlib.sha256(flag_on.encode()).hexdigest(),
    "as_of": schema["properties"]["as_of"], "required": schema["required"],
    "description": operation["description"],
}
(OUT / "flag-on-openapi-proof.json").write_text(json.dumps(proof, indent=2) + "\n")
(OUT.parent / "flag-on-openapi-proof.json").write_text(json.dumps(proof, indent=2) + "\n")

before = json.loads((OUT / "pre819-display-vocabulary-provenance.json").read_text())
after = json.loads((OUT.parent / "display-vocabulary-provenance.json").read_text())
fixture = json.loads((ROOT / "web/src/decide/__fixtures__/live-vocabulary.json").read_text())
assert sha("web/src/decide/__fixtures__/live-vocabulary.json") == after["fixture_sha256"]
assert fixture["as_of"] == after["snapshot_as_of"] == "2026-10-04"
assert "coverage" not in fixture
comparison = {
    "merged_upstream": result["merged_upstream"],
    "fixture_bytes_unchanged": before["fixture_sha256"] == after["fixture_sha256"],
    "full_vocabulary_bytes_unchanged": before["full_vocabulary_sha256"] == after["full_vocabulary_sha256"],
    "snapshot_unchanged": before["snapshot"] == after["snapshot"],
    "date_unchanged": before["snapshot_as_of"] == after["snapshot_as_of"],
    "snapshot": after["snapshot"], "as_of": after["snapshot_as_of"],
    "fixture_sha256": after["fixture_sha256"],
    "models": len(fixture["models"]), "templates": len(fixture["templates"]),
    "available_templates": sum(row.get("available", True) for row in fixture["templates"]),
    "changed_producer_inputs": [path for path, value in after["source_hashes"].items()
                                if before["source_hashes"].get(path) != value],
}
(OUT / "fixture-comparison.json").write_text(json.dumps(comparison, indent=2) + "\n")
print(json.dumps({"pins": result, "fixture": comparison}, indent=2))
