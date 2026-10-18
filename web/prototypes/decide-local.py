"""Answer prototype requests with the frozen repository's offline engine."""

from datetime import date
import importlib.util
import json
import logging
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from decision.snapshot import build_from_repo, load_built_snapshot


def main():
    # The corpus uses the same incomplete frozen catalogue with the gate off.
    # Keep its actual snapshot ID; it is not the published fixture snapshot.
    logging.basicConfig(level=logging.ERROR)
    built = build_from_repo(
        ROOT,
        premier=ROOT / "premier/slice-1.yaml",
        as_of=date(2026, 10, 4),
        gate=False,
    )
    snapshot = load_built_snapshot(built, source="PROTO-DECIDE frozen repository")
    module_spec = importlib.util.spec_from_file_location(
        "proto_decide_service", ROOT / "api/worker/src/decide_service.py"
    )
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError("Could not load the decision service")
    service = importlib.util.module_from_spec(module_spec)
    sys.modules[module_spec.name] = service
    module_spec.loader.exec_module(service)
    print(json.dumps({"ready": True, "snapshot": snapshot.snapshot_id}), flush=True)
    for line in sys.stdin:
        message = json.loads(line)
        status, body = service.decide(message["spec"], snapshot)
        print(json.dumps({"id": message["id"], "status": status, "body": body}), flush=True)


if __name__ == "__main__":
    main()
