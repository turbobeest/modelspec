"""Reproduce MODEL-402 size and Pyodide probes without Cloudflare credentials.

Run with the repository Python environment. Only the full frozen public
checkout is exported. No command deploys or uploads a Worker.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SCRATCH = ROOT / "api/worker/.scratch-model402-measurement"
WORKER = SCRATCH / "worker"
NODE_BIN = "/Users/terbeest/.nvm/versions/node/v22.22.3/bin"
BOOTSTRAP_UV = "/Users/terbeest/.local/bin/uv"
UV = str(SCRATCH / "uv-tool/bin/uv")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepared", action="store_true",
                        help="Reuse an existing prepared fixture after a tooling retry.")
    args = parser.parse_args()
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("CLOUDFLARE_", "MODELSPEC_SNAPSHOT_"))}
    env.update(PATH=str(SCRATCH / "uv-tool/bin") + ":" + NODE_BIN + ":"
               + env.get("PATH", ""), WRANGLER_SEND_METRICS="false",
               MODELSPEC_SNAPSHOT_KEY="model402-full-frozen-measurement-key")
    previous = HERE / "commands.json"
    commands = json.loads(previous.read_text()) if args.prepared and previous.exists() else []

    def run(name: str, args: list[str], cwd: Path = ROOT, *, required: bool = True):
        print(f"Running {name}", flush=True)
        result = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True)
        output = result.stdout + result.stderr
        (HERE / f"{name}.txt").write_text(
            f"CWD: {cwd}\nCOMMAND: {shlex.join(args)}\n" + output
            + f"\nEXIT_CODE={result.returncode}\n", encoding="utf-8")
        commands.append({"name": name, "command": args, "cwd": str(cwd),
                         "exit_code": result.returncode})
        (HERE / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
        print(f"{name}: exit {result.returncode}", flush=True)
        if required:
            result.check_returncode()
        return result, output

    if not args.prepared:
        run("prepare", [sys.executable, str(HERE / "prepare_bundle.py")])
    if not Path(UV).exists():
        run("uv-tool-venv", [BOOTSTRAP_UV, "venv", str(SCRATCH / "uv-tool"),
                             "--python", "3.13"])
    run("uv-tool-install", [BOOTSTRAP_UV, "pip", "install", "--python",
                            str(SCRATCH / "uv-tool/bin/python"), "uv==0.12.19"])
    run("uv-version", [UV, "--version"])
    run("node-version", [NODE_BIN + "/node", "--version"])
    run("npm-version", [NODE_BIN + "/npm", "--version"])
    run("python-version", [sys.executable, "--version"])
    run("uv-sync", [UV, "sync", "--project", str(WORKER), "--frozen", "--python", "3.13"])
    run("npm-worker", [NODE_BIN + "/npm", "install", "--prefix", str(WORKER),
                       "--no-save", "wrangler@4.139.0"])
    run("npm-memory", [NODE_BIN + "/npm", "install", "--prefix", str(SCRATCH / "memory"),
                       "--no-save", "pyodide@0.28.3"])
    env["NODE_PATH"] = str(SCRATCH / "memory/node_modules")
    # Download package wheels in a separate process. Keep the measurement's
    # Node runtime free of retained download buffers and HTTP/TLS caches.
    run("pyodide-cache", [NODE_BIN + "/node", "-e", """
const path = require('node:path');
const { loadPyodide } = require('pyodide');
const root = path.dirname(require.resolve('pyodide'));
loadPyodide({indexURL: root + '/',
  packageBaseUrl: 'https://cdn.jsdelivr.net/pyodide/v0.28.3/full/',
  packageCacheDir: path.join(root, 'packages')})
  .then(py => py.loadPackage(['pydantic', 'pyyaml']))
  .catch(error => { console.error(error.name); process.exitCode = 1; });
"""])
    run("worker-tools", [str(WORKER / ".venv/bin/python"), "-c",
                         "import sys; from importlib.metadata import version; "
                         "print(sys.version); print('workers-py', version('workers-py')); "
                         "print('workers-runtime-sdk', version('workers-runtime-sdk'))"])
    _, dry_run = run("worker-dry-run", [UV, "run", "--project", ".", "pywrangler", "deploy",
                                       "--dry-run", "--outdir", str(SCRATCH / "upload")], WORKER)
    upload = re.search(r"Total Upload:.*?(\d+\.\d+) KiB / gzip: (\d+\.\d+) KiB", dry_run)
    assert upload, "Wrangler did not report an upload size"
    run("bundle-imports", [sys.executable, str(ROOT / "api/worker/bundle_check.py"),
                           str(SCRATCH / "upload")])
    memory_result, memory_output = run(
        "memory", [NODE_BIN + "/node", "--expose-gc", str(SCRATCH / "measure_memory.cjs"),
                   str(WORKER / "src")], required=False)
    memory_json = [line for line in memory_output.splitlines() if line.startswith('{"runtime"')]
    manifest = [{"path": str(path.relative_to(SCRATCH / "upload")),
                 "bytes": path.stat().st_size,
                 "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                for path in sorted((SCRATCH / "upload").rglob("*")) if path.is_file()]
    (HERE / "upload-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    raw_kib, gzip_kib = map(float, upload.groups())
    summary = {
        "fixture": "Full frozen public catalogue; synthetic signed validity overlays",
        "private_production_data_measured": False,
        "wrangler_total_upload_kib": raw_kib,
        "wrangler_gzip_upload_kib": gzip_kib,
        "worker_upload_bytes_exact_from_artifacts": sum(
            row["bytes"] for row in manifest if row["path"] != "README.md"),
        "worker_uncompressed_limit_mib": 64,
        "uncompressed_limit_used_percent": raw_kib / (64 * 1024) * 100,
        "gzip_below_historical_10_mib_limit": gzip_kib < 10 * 1024,
        "memory_exit_code": memory_result.returncode,
        "memory": json.loads(memory_json[-1]) if memory_json else None,
    }
    cold = HERE / "memory-cold-download.json"
    if cold.exists():
        summary["earlier_cold_download_probe"] = json.loads(cold.read_text())
    (HERE / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
