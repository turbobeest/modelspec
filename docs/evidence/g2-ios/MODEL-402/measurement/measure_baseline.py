"""Compare the same complete frozen bundle with its successor blobs omitted."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import shlex
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SCRATCH = ROOT / "api/worker/.scratch-model402-measurement"
WORKER = SCRATCH / "worker"
NODE_BIN = "/Users/terbeest/.nvm/versions/node/v22.22.3/bin"
UV = str(SCRATCH / "uv-tool/bin/uv")


def main() -> None:
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("CLOUDFLARE_", "MODELSPEC_SNAPSHOT_"))}
    env.update(PATH=str(SCRATCH / "uv-tool/bin") + ":" + NODE_BIN + ":"
               + env.get("PATH", ""), WRANGLER_SEND_METRICS="false",
               MODELSPEC_SNAPSHOT_KEY="model402-full-frozen-measurement-key",
               NODE_PATH=str(SCRATCH / "memory/node_modules"))
    path = WORKER / "src/bundled_data.py"
    saved = path.read_bytes()
    spec = importlib.util.spec_from_file_location("model402_baseline_data", path)
    bundled = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bundled)
    for key in ("/api/decision/snapshot-successor.json.gz",
                "/api/decision/vocabulary-successor.json"):
        assert key in bundled.BLOBS
        del bundled.BLOBS[key]

    def run(name, args, cwd=ROOT):
        result = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True)
        output = result.stdout + result.stderr
        (HERE / f"{name}.txt").write_text(
            f"CWD: {cwd}\nCOMMAND: {shlex.join(args)}\n" + output
            + f"\nEXIT_CODE={result.returncode}\n", encoding="utf-8")
        return result, output

    try:
        path.write_text("import base64, gzip\nBLOBS = " + repr(bundled.BLOBS) + "\n"
                        "def read(path):\n    value = BLOBS.get(path)\n"
                        "    return gzip.decompress(base64.b64decode(value)) if value else None\n")
        baseline_data_bytes = path.stat().st_size
        dry_result, dry_output = run(
            "baseline-worker-dry-run", [UV, "run", "--project", ".", "pywrangler", "deploy",
                                        "--dry-run", "--outdir", str(SCRATCH / "upload-baseline")],
            WORKER)
        dry_result.check_returncode()
        upload = re.search(r"Total Upload:.*?(\d+\.\d+) KiB / gzip: (\d+\.\d+) KiB", dry_output)
        assert upload
        memory_result, memory_output = run(
            "baseline-memory", [NODE_BIN + "/node", "--expose-gc",
                                str(ROOT / "api/worker/measure_memory.cjs"), str(WORKER / "src")])
        memory_json = [line for line in memory_output.splitlines()
                       if line.startswith('{"runtime"')]
        summary = {
            "fixture": "Same full frozen bundle; only successor snapshot/vocabulary omitted",
            "source_sha": json.loads((HERE / "fixture.json").read_text())["source_sha"],
            "baseline_bundled_data_python_bytes": baseline_data_bytes,
            "wrangler_total_upload_kib": float(upload[1]),
            "wrangler_gzip_upload_kib": float(upload[2]),
            "memory_exit_code": memory_result.returncode,
            "memory": json.loads(memory_json[-1]) if memory_json else None,
        }
        (HERE / "baseline-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        print(json.dumps(summary, indent=2))
    finally:
        path.write_bytes(saved)


if __name__ == "__main__":
    main()
