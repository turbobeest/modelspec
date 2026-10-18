"""Prepare an isolated, full frozen-catalogue, two-snapshot measurement bundle.

Run from the repository root with its installed Python environment. The real
vendor export reads only this public checkout. Two newly signed copies of its
complete snapshot receive synthetic validity dates to measure both resident
snapshots. These dates are a fixture, not an assertion about production prices.
"""

from __future__ import annotations

import base64
import copy
import gzip
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
WORKER = ROOT / "api/worker"
SCRATCH = WORKER / ".scratch-model402-round3-measurement"
KEY = b"model402-full-frozen-measurement-key"


def main() -> None:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    (SCRATCH / ".gitignore").write_text("*\n", encoding="utf-8")
    worker = SCRATCH / "worker"
    worker.mkdir(exist_ok=True)
    for name in ("pyproject.toml", "uv.lock", "pylock.toml"):
        shutil.copyfile(WORKER / name, worker / name)
    config = {
        "name": "model402-measurement-never-deploy",
        "main": "src/entry.py",
        "compatibility_date": "2026-09-01",
        "compatibility_flags": ["python_workers", "disable_python_external_sdk"],
        "rules": [{"type": "Data", "globs": [
            "registry/*.yaml", "hardware/*.yaml", "pipeline/vocab_synonyms.json",
        ], "fallthrough": True}],
    }
    (worker / "wrangler.jsonc").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("CLOUDFLARE_", "MODELSPEC_SNAPSHOT_"))}
    env["MODELSPEC_SNAPSHOT_KEY"] = KEY.decode()
    temp = SCRATCH / "tmp"
    temp.mkdir(exist_ok=True)
    env["TMPDIR"] = str(temp)
    command = [sys.executable, str(WORKER / "vendor.py"), "--out", str(worker / "src"),
               "--data-dir", str(ROOT)]
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True)
    log = Path(__file__).with_name("vendor.txt")
    log.write_text("COMMAND: " + " ".join(command) + "\n" + result.stdout + result.stderr
                   + f"\nEXIT_CODE={result.returncode}\n", encoding="utf-8")
    result.check_returncode()
    for source in (WORKER / "src").glob("*.py"):
        if source.name not in {"bundled_data.py", "tier_policy.py"}:
            shutil.copyfile(source, worker / "src" / source.name)

    sys.path.insert(0, str(ROOT))
    from decision.snapshot import Snapshot, content_hash, load_snapshot_bytes, snapshot_id_for

    bundled_path = worker / "src/bundled_data.py"
    spec = importlib.util.spec_from_file_location("model402_measured_data", bundled_path)
    bundled = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bundled)
    raw = bundled.read("/api/decision/snapshot.json.gz")
    original = json.loads(gzip.decompress(raw))["content"]
    vocabulary = json.loads(bundled.read("/api/decision/vocabulary.json"))
    today = datetime.now(UTC).date()
    boundary = today + timedelta(days=1)
    current = copy.deepcopy(original)
    current["valid_from"] = today.isoformat()
    current["valid_until"] = boundary.isoformat()
    successor = copy.deepcopy(original)
    successor["as_of"] = boundary.isoformat()
    successor["valid_from"] = boundary.isoformat()
    successor.pop("valid_until", None)
    details = []
    for name, content in (("snapshot", current), ("snapshot-successor", successor)):
        digest = content_hash(content)
        snapshot = Snapshot(content, digest, snapshot_id_for(digest))
        raw = snapshot.to_bytes(KEY, ed25519_signer=None)
        loaded = load_snapshot_bytes(raw, key=KEY, include_archive=True)
        path = f"/api/decision/{name}.json.gz"
        bundled.BLOBS[path] = base64.b64encode(gzip.compress(raw, mtime=0)).decode("ascii")
        vocabulary_copy = copy.deepcopy(vocabulary)
        vocabulary_copy["snapshot"] = loaded.snapshot_id
        vocabulary_copy.get("coverage", {})["as_of"] = content.get("as_of")
        vocabulary_name = "vocabulary" if name == "snapshot" else "vocabulary-successor"
        vocabulary_path = f"/api/decision/{vocabulary_name}.json"
        vocabulary_raw = json.dumps(vocabulary_copy).encode()
        bundled.BLOBS[vocabulary_path] = base64.b64encode(
            gzip.compress(vocabulary_raw, mtime=0)).decode("ascii")
        details.append({"path": path, "snapshot_id": loaded.snapshot_id,
                        "valid_from": content["valid_from"],
                        "valid_until": content.get("valid_until"),
                        "snapshot_gzip_bytes": len(raw),
                        "snapshot_json_bytes": len(gzip.decompress(raw)),
                        "vocabulary_json_bytes": len(vocabulary_raw),
                        "corpus_sections": len(loaded._corpus_sections),
                        "candidates_in_sections": [len(section["candidates"])
                                                   for section in loaded._corpus_sections]})
    bundled_path.write_text(
        "# Synthetic two-snapshot fixture from the full frozen public catalogue.\n"
        "import base64, gzip\nBLOBS = " + repr(bundled.BLOBS) + "\n"
        "def read(path):\n    value = BLOBS.get(path)\n"
        "    return gzip.decompress(base64.b64decode(value)) if value else None\n",
        encoding="utf-8",
    )
    # Exercise both real held objects and the handover in the existing probe.
    probe = (WORKER / "measure_memory.cjs").read_text(encoding="utf-8")
    marker = "assert len(held._corpus_sections) == 2\n"
    assert marker in probe
    probe = probe.replace(marker, marker + """holder = entry._decision_holder("https://modelspec.dev")
assert holder._bundled_successor is not None
assert holder._bundle_verified
from datetime import UTC, datetime
import decision.snapshot as snapshot_runtime
class BoundaryClock(datetime):
    @classmethod
    def now(cls, tz=None):
        return datetime.combine(holder._bundled_successor.valid_from,
                                datetime.min.time(), tzinfo=UTC)
snapshot_runtime.datetime = BoundaryClock
holder._today = lambda: holder._bundled_successor.valid_from
response = await worker.fetch(Request('POST', '/v1/decide', {
    'spec_version':1, 'snapshot':'latest', 'optimize': {'max':'gpqa_diamond'},
    'limit':1, 'explain':'none'}))
assert response.status == 200
assert holder.snapshot is holder._bundled_successor
record_peak()
""")
    probe = probe.replace("'POST /v1/decide', 'GET /v1/vocabulary'",
                          "'POST /v1/decide (current)', 'POST /v1/decide (successor)', "
                          "'GET /v1/vocabulary'")
    (SCRATCH / "measure_memory.cjs").write_text(probe, encoding="utf-8")
    source_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                capture_output=True, text=True, check=True).stdout.strip()
    source_paths = sorted({WORKER / "vendor.py", WORKER / "measure_memory.cjs",
                           WORKER / "pyproject.toml", WORKER / "uv.lock",
                           WORKER / "pylock.toml", *WORKER.glob("src/*.py"),
                           *ROOT.glob("decision/**/*.py")})
    source_hashes = {str(path.relative_to(ROOT)):
                     hashlib.sha256(path.read_bytes()).hexdigest()
                     for path in source_paths}
    source_status = subprocess.run(
        ["git", "status", "--short", "--", "api/worker", "decision"], cwd=ROOT,
        capture_output=True, text=True, check=True).stdout.splitlines()
    summary = {"fixture": "Full frozen public export; synthetic signed validity overlays",
               "source_sha": source_sha,
               "source_sha256": source_hashes,
               "source_worktree_status": source_status,
               "private_production_data_measured": False,
               "bundle_root": str(worker / "src"), "snapshots": details,
               "bundled_data_python_bytes": bundled_path.stat().st_size}
    Path(__file__).with_name("fixture.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
