"""Prove the deliberate guide change before refreshing fixed byte hashes."""

import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import types
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from pipeline import agent_copy, worker_flags  # noqa: E402

BASE = "0afd269c0e2e4dbb86dd073f4b8669437470fb07"
OUT = Path(__file__).resolve().parent
POINTER = "Orchestrator system prompt and worked Spec: https://modelspec.dev/orchestrators/.\n"


def at_base(path):
    return subprocess.run(
        ["git", "show", f"{BASE}:{path}"], cwd=ROOT,
        capture_output=True, check=True, text=True,
    ).stdout


base = types.ModuleType("pipeline.agent_copy_at_base")
base.__file__ = str(ROOT / "pipeline/agent_copy.py")
exec(compile(at_base("pipeline/agent_copy.py"), base.__file__, "exec"), base.__dict__)
flags = {**worker_flags.production_vars(ROOT), "DECISION_LINK_ENABLED": "false"}
with patch.object(worker_flags, "production_vars", return_value=flags):
    old_version, old_guide = base.guide()
    new_version, new_guide = agent_copy.guide()
    old_copy, new_copy = base.render(base.copy()), agent_copy.render(agent_copy.copy())
    old_cli = json.dumps(base.cli_text(), sort_keys=True)
    new_cli = json.dumps(agent_copy.cli_text(), sort_keys=True)

assert old_guide == at_base("docs/agents.md")
assert old_copy == at_base("mcp/src/agent-copy.json")
assert new_guide == (ROOT / "docs/agents.md").read_text()
assert new_copy == (ROOT / "mcp/src/agent-copy.json").read_text()
assert new_guide.count(POINTER) == 1
assert new_guide.replace(POINTER, "").replace(new_version, old_version) == old_guide
old_data, new_data = json.loads(old_copy), json.loads(new_copy)
assert {key for key in new_data if new_data[key] != old_data[key]} == {
    "guide_version", "context_guide", "instructions",
}
assert new_data["context_guide"].count(POINTER) == 1
new_data["context_guide"] = new_data["context_guide"].replace(POINTER, "")
assert agent_copy.render(new_data).replace(new_version, old_version) == old_copy
assert new_cli == old_cli

test_source = (ROOT / "tests/test_decision_link.py").read_text()
for previous, current in ((old_copy, new_copy), (old_guide, new_guide)):
    test_source = test_source.replace(
        hashlib.sha256(current.encode()).hexdigest(),
        hashlib.sha256(previous.encode()).hexdigest(),
    )
assert test_source == at_base("tests/test_decision_link.py")

diff = "".join(difflib.unified_diff(
    old_guide.splitlines(keepends=True), new_guide.splitlines(keepends=True),
    fromfile="base/docs/agents.md", tofile="current/docs/agents.md",
))
(OUT / "flag-off-guide.diff").write_text(diff)
results = {
    "base": BASE,
    "flag": "DECISION_LINK_ENABLED=false",
    "old_guide_version": old_version,
    "new_guide_version": new_version,
    "guide": {"old": hashlib.sha256(old_guide.encode()).hexdigest(),
              "new": hashlib.sha256(new_guide.encode()).hexdigest()},
    "mcp_copy": {"old": hashlib.sha256(old_copy.encode()).hexdigest(),
                 "new": hashlib.sha256(new_copy.encode()).hexdigest()},
    "cli_text": {"old": hashlib.sha256(old_cli.encode()).hexdigest(),
                 "new": hashlib.sha256(new_cli.encode()).hexdigest()},
    "guide_only_adds_pointer_and_derived_version": True,
    "mcp_copy_only_adds_context_pointer_and_derived_versions": True,
    "cli_text_byte_identical": True,
    "test_source_only_refreshes_two_fixed_hashes": True,
}
(OUT / "flag-off-hashes.json").write_text(json.dumps(results, indent=2) + "\n")
print(diff)
print(json.dumps(results, indent=2))
