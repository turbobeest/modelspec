"""Vendor private data and run the real Worker memory probe in both periods."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

KEY = "model437-round2-private-proof-throwaway-key"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--node", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True,
                        help="npm prefix containing node_modules/pyodide@0.28.3")
    args = parser.parse_args()
    code, output = args.code.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    runtime = args.runtime.resolve()
    metadata = json.loads((runtime / "node_modules/pyodide/package.json").read_text())
    if metadata["version"] != "0.28.3":
        raise ValueError("the probe requires Pyodide 0.28.3")
    env = dict(os.environ, MODELSPEC_SNAPSHOT_KEY=KEY, MODELSPEC_REQUIRE_DATA_DIR="1",
               DATA_SPLIT_ENABLED="false", PYTHONPATH=str(code),
               NODE_PATH=str(runtime / "node_modules"))
    env.pop("MODELSPEC_SOURCE_CACHE", None)
    env.pop("MODELSPEC_SNAPSHOT_ED25519_KEY", None)
    bundle = output / "bundle"
    with (output / "vendor.private.log").open("w") as log:
        subprocess.run([sys.executable, str(code / "api/worker/vendor.py"),
                        "--data-dir", str(args.data_dir.resolve()), "--out", str(bundle)],
                       cwd=code, env=env, stdout=log, stderr=log, check=True)
    for source in (code / "api/worker/src").glob("*.py"):
        if source.name not in {"bundled_data.py", "tier_policy.py"}:
            shutil.copy2(source, bundle / source.name)
    results = {}
    for period in ("current", "successor"):
        command = [str(args.node.resolve()), "--expose-gc",
                   str(code / "api/worker/measure_memory.cjs"), str(bundle),
                   "--limit-mib", "115", "--output", str(output / (period + ".public.json"))]
        if period == "successor":
            command.append("--successor")
        with (output / (period + ".log")).open("w") as log:
            result = subprocess.run(command, cwd=code, env=env, stdout=log, stderr=log)
        results[period] = result.returncode
        print(f"{period} memory probe exit {result.returncode}", flush=True)
    return int(any(results.values()))


if __name__ == "__main__":
    raise SystemExit(main())
