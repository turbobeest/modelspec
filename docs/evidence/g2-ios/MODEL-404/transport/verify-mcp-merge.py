"""Read-only checks for preserved main hardware-fit artifacts after the merge."""

import json
import runpy
import subprocess
from pathlib import Path

MAIN = "0cf4080a72d354295c434206257d089d26b50ed6"


def committed(path):
    return subprocess.check_output(["git", "show", f"{MAIN}:{path}"])


for path in (
    "decision/hardware_fit.py",
    "decision/snapshot.py",
    "mcp/test/__snapshots__/server.test.ts.snap",
    "mcp/test/fixtures/generate-hardware-fit.py",
    "mcp/test/fixtures/hardware-fit.json",
    "mcp/test/hardware-fit.test.ts",
):
    assert Path(path).read_bytes() == committed(path), path
    print(f"Identical to {MAIN[:8]}: {path}")

copy = json.loads(Path("mcp/src/agent-copy.json").read_text())
main_copy = json.loads(committed("mcp/src/agent-copy.json"))
assert copy["tools"] == main_copy["tools"]
assert "basis lower_bound for unlikely only" in copy["tools"]["hardware_fit"]
assert "Missing headroom cannot establish likely" in copy["tools"]["hardware_fit"]
assert "Full board: https://modelspec.dev/decide/details/." in copy["context_guide"]
print("All MCP tool descriptions match main; hardware-fit 2.0 wording retained.")
print("Merged context guide links the full board to /decide/details/.")

saved = json.loads(Path("mcp/test/fixtures/hardware-fit.json").read_text())
generated = runpy.run_path("mcp/test/fixtures/generate-hardware-fit.py")["assessments"]()
assert generated == saved
assert {case["body"]["hardware_fit_version"] for case in saved["cases"]} == {"2.0"}
assert {case["basis"] for case in saved["cases"]} == {"full", "lower_bound"}
print("In-memory Python assessment regeneration matches both saved 2.0 cases.")
