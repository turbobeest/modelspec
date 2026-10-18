"""Verify the granted QA capture and reviewed-copy changes against origin/main."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path

from pipeline import agent_copy

ROOT = Path(__file__).resolve().parents[5]


def base_json(path: str):
    result = subprocess.run(
        ["git", "show", f"origin/main:{path}"], cwd=ROOT,
        text=True, capture_output=True, check=True,
    )
    return json.loads(result.stdout)


def main():
    base = base_json("mcp/src/agent-copy.json")
    current = agent_copy.copy()
    assert json.loads((ROOT / "mcp/src/agent-copy.json").read_text()) == current
    expected = copy.deepcopy(base)
    expected["tools"]["hardware_fit"] = current["tools"]["hardware_fit"]
    assert expected == current, "Copy changed outside tools.hardware_fit"
    old_hash = hashlib.sha256(agent_copy.render(base).encode()).hexdigest()
    new_hash = hashlib.sha256(agent_copy.render(current).encode()).hexdigest()
    assert old_hash == "faa19be299fb233c78d366f2fed67897f45b87d89d2bad40f96faa2f6f3841b7"
    pin = (ROOT / "tests/test_decision_link.py").read_text()
    assert new_hash in pin and old_hash not in pin

    old_capture = base_json("qa/fixtures/mcp-tools.json")
    capture = json.loads((ROOT / "qa/fixtures/mcp-tools.json").read_text())
    expected_capture = copy.deepcopy(old_capture)
    expected_capture["source_hashes"] = capture["source_hashes"]
    changed_tools = []
    for index, (old, new) in enumerate(zip(old_capture["tools"], capture["tools"], strict=True)):
        assert old["name"] == new["name"]
        if old != new:
            changed_tools.append(old["name"])
            assert old["name"] == "hardware_fit"
            assert new["description"] == current["tools"]["hardware_fit"]
            expected_tool = {**old, "description": new["description"]}
            assert expected_tool == new, "Hardware-fit input schema changed"
            expected_capture["tools"][index] = new
    assert changed_tools == ["hardware_fit"]
    assert expected_capture == capture
    assert old_capture["source_hashes"].keys() == capture["source_hashes"].keys()
    changed_hashes = sorted(
        name for name, value in capture["source_hashes"].items()
        if old_capture["source_hashes"][name] != value
    )
    assert changed_hashes == ["api/worker/openapi.yaml", "mcp/src/agent-copy.json"]
    print(json.dumps({
        "changed_tool_entries": changed_tools,
        "changed_source_hash_metadata": changed_hashes,
        "old_reviewed_copy_hash": old_hash,
        "new_reviewed_copy_hash": new_hash,
        "other_copy_fields_and_tool_inputs": "unchanged",
    }, indent=2))


if __name__ == "__main__":
    main()
