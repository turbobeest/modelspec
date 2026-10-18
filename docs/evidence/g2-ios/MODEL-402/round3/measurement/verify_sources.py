"""Match every measured source-file hash to the fixture's recorded commit."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]


def main() -> None:
    fixture = json.loads((HERE / "fixture.json").read_text())
    sha = fixture["source_sha"]
    rows = []
    for name, digest in fixture["source_sha256"].items():
        source = subprocess.run(["git", "show", f"{sha}:{name}"], cwd=ROOT,
                                capture_output=True, check=True).stdout
        matches = hashlib.sha256(source).hexdigest() == digest
        rows.append({"path": name, "sha256": digest, "matches_commit": matches})
    assert all(row["matches_commit"] for row in rows)
    result = {"source_sha": sha, "source_files_verified": len(rows),
              "all_match_commit": True,
              "source_worktree_status_at_export": fixture["source_worktree_status"],
              "files": rows}
    (HERE / "source-verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key != "files"},
                     indent=2))


if __name__ == "__main__":
    main()
