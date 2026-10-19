"""Read-only generated-artifact audit for MODEL-404's main sync."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[6]
OUT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

import yaml
from api.worker import openapi
from pipeline import agent_copy
from qa.contracts import source_hashes

before = json.loads((OUT / "before.json").read_text())
rows = {}
for path, prior in before["artifacts"].items():
    data = (ROOT / path).read_bytes()
    assert b"<<<<<<<" not in data and b">>>>>>>" not in data
    digest = hashlib.sha256(data).hexdigest()
    row = {"sha256": digest, "changed_from_approved_head": digest != prior["HEAD"],
           "matches_upstream": digest == prior["MERGE_HEAD"]}
    if path in {"cli/modelspec/agent-bundle.json", "qa/fixtures/mcp-tools.json"}:
        current = json.loads(data)
        approved = json.loads(subprocess.check_output(["git", "show", before["head"] + ":" + path], cwd=ROOT))
        row["changed_semantic_keys"] = [key for key in set(current) | set(approved)
                                        if current.get(key) != approved.get(key)]
        assert set(row["changed_semantic_keys"]) <= {"source_hashes"}
        assert list(current["source_hashes"]) == sorted(current["source_hashes"])
        row["changed_source_pins"] = {key: value for key, value in current["source_hashes"].items()
                                      if approved["source_hashes"].get(key) != value}
    rows[path] = row

cli = json.loads((ROOT / "cli/modelspec/agent-bundle.json").read_text())
qa = json.loads((ROOT / "qa/fixtures/mcp-tools.json").read_text())
assert qa["source_hashes"] == source_hashes()
assert all(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
           for path, digest in cli["source_hashes"].items())
literal_pins = {
    "mcp": hashlib.sha256(agent_copy.render(agent_copy.copy()).encode()).hexdigest(),
    "guide": hashlib.sha256(agent_copy.guide()[1].encode()).hexdigest(),
    "cli_text": hashlib.sha256(json.dumps(agent_copy.cli_text(), sort_keys=True).encode()).hexdigest(),
}
pin_tests = (ROOT / "tests/test_decision_link.py").read_text()
assert all(value in pin_tests for value in literal_pins.values())
copy = json.loads((ROOT / "mcp/src/agent-copy.json").read_text())
assert "https://modelspec.dev/decide/details/" in copy["context_guide"]
assert "https://modelspec.dev/decide/details/" in (ROOT / "docs/agents.md").read_text()
assert "https://modelspec.dev/decide/details/" in cli["text"]["human_message"]

os.environ["DATA_SPLIT_ENABLED"] = "true"
flag_on = yaml.safe_load(openapi.render())
vocabulary = flag_on["paths"]["/v1/vocabulary"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
assert vocabulary["properties"]["as_of"]["type"] == "string"
assert vocabulary["properties"]["as_of"]["format"] == "date"
assert "as_of" not in vocabulary["required"]
result = {
    "approved_head": before["head"], "merged_upstream": before["merge_head"],
    "guide_version": cli["guide_version"], "regenerated_files": rows,
    "literal_catalogue_pins": literal_pins, "qa_and_cli_pins_match": True,
    "details_links_preserved": True, "optional_as_of_preserved": True,
    "vocabulary_required": vocabulary["required"],
}
(OUT / "artifacts.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps(result, indent=2, sort_keys=True))
