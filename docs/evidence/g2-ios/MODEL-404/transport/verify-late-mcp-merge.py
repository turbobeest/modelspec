"""Read-only MCP source and link inventory checks after the second main merge."""

import json
import subprocess
from pathlib import Path

MAIN = "b4a7074f37a3ba940bd86db9d1e2459a25fd40af"
files = subprocess.check_output([
    "git", "ls-tree", "-r", "--name-only", MAIN, "mcp", "server.json",
], text=True).splitlines()

for name in files:
    if name == "mcp/src/agent-copy.json":
        continue
    original = subprocess.check_output(["git", "show", f"{MAIN}:{name}"])
    assert Path(name).read_bytes() == original, name
print(f"{len(files) - 1} MCP/registry files match integrated main {MAIN[:8]} byte for byte.")
print("This includes runtime authorization, origin handling, server-card discovery, tests, snapshots and configuration.")

copy = json.loads(Path("mcp/src/agent-copy.json").read_text())
original_copy = json.loads(subprocess.check_output([
    "git", "show", f"{MAIN}:mcp/src/agent-copy.json",
]))
changed = sorted(key for key in copy if copy[key] != original_copy[key])
assert changed == ["context_guide", "guide_version", "instructions"]
assert copy["tools"] == original_copy["tools"]
assert "Full board: https://modelspec.dev/decide/details/." in copy["context_guide"]
assert "https://modelspec.dev/decide/" not in json.dumps(copy).replace(
    "https://modelspec.dev/decide/details/", "",
)
print("Only MODEL-404 guide/version/instructions differ from main; tool descriptions are unchanged.")
print("The MCP full-board link remains /decide/details/.")

readme = Path("README.md").read_text()
assert "[decide](https://modelspec.dev/decide/)" in readme
assert "[decision board](https://modelspec.dev/decide/details/)" in readme
assert "/decide/" not in Path("server.json").read_text()
assert "/decide/" not in Path("mcp/README.md").read_text()
print("General human lookup remains /decide/; explicit board lookup remains /decide/details/.")
print("Registry metadata and new discovery documentation introduce no decide-page link requiring relocation.")
