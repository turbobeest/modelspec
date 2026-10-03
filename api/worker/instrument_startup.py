"""Create an isolated local timing build. Never use its config for deployment.

python api/worker/instrument_startup.py /tmp/model-283-startup
cd api/worker
node node_modules/wrangler/bin/wrangler.js dev --local --config /tmp/model-283-startup/wrangler.json \
    --var MODELSPEC_SNAPSHOT_KEY:model247-memory-fixture-key

Build a signed public fixture with vendor.py --data-dir . first. Only phase
durations reach logs; no catalogue values, requests or credentials are logged.
The local wrapper imports entry during the first request so workerd's clock
is active. This deliberately measures unsnapshotted application initialization.
It does not load a deployment-specific snapshot or measure its restore.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

WORKER = Path(__file__).resolve().parent


def instrument(destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=False)
    shutil.copytree(WORKER / "src", destination / "src", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(WORKER / "python_modules", destination / "python_modules",
                    ignore=shutil.ignore_patterns("__pycache__"))
    entry = destination / "src/entry.py"
    source = entry.read_text()
    probes = {
        "\nimport hashlib\n": '''
import time as _probe_time
_probe_started = _probe_time.perf_counter()
def _probe_mark(phase):
    global _probe_started
    now = _probe_time.perf_counter()
    print('[model-283-startup] ' + phase + ' ms=' + str(round((now - _probe_started) * 1000, 3)))
    _probe_started = now
import hashlib
''',
        "#: Files the endpoint reads.": "_probe_mark('module_imports')\n\n#: Files the endpoint reads.",
        "_decision_registry()\n": "_decision_registry()\n_probe_mark('registry')\n",
        "    del _snapshot_bytes\n": "    del _snapshot_bytes\n    _probe_mark('decision_decompress_parse_index')\n",
        "class _Fetched:\n": "_probe_mark('rank_and_vocabulary_preparation')\n\nclass _Fetched:\n",
        "        response = await self._fetch(request)\n": """        _request_started = _probe_time.perf_counter()
        response = await self._fetch(request)
        print('[model-283-startup] request ms=' + str(round((_probe_time.perf_counter() - _request_started) * 1000, 3)))
""",
    }
    for anchor, replacement in probes.items():
        if source.count(anchor) != 1:
            raise ValueError(f"instrumentation anchor changed: {anchor!r}")
        source = source.replace(anchor, replacement, 1)
    entry.write_text(source)
    (destination / "src/probe_entry.py").write_text('''from workers import WorkerEntrypoint

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        import entry
        worker = entry.Default(self.ctx, self.env)
        return await worker.fetch(request)
''')
    # No routes, account, secrets, remote bindings, or reserved flags. The
    # config is deliberately for offline dev of this independent source copy.
    config = {
        "name": "modelspec-startup-local",
        "main": "src/probe_entry.py",
        "compatibility_date": "2026-09-01",
        "compatibility_flags": ["python_workers", "disable_python_external_sdk"],
        "rules": [{"type": "Data", "globs": ["registry/*.yaml", "hardware/*.yaml"], "fallthrough": True}],
    }
    config_path = destination / "wrangler.json"
    config_path.write_text(json.dumps(config, indent=2) + "\n")
    return config_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    print(instrument(parser.parse_args().destination))
