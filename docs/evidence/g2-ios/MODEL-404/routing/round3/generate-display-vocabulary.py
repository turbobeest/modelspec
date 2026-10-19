"""Reproduce the browser display fixture from one frozen-repository snapshot."""

from datetime import date
import hashlib
import json
import logging
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))

from api.worker.src.display_vocabulary import trim
from decision.registry import default
from decision.snapshot import build_from_repo
from pipeline.build import write_decision_vocabulary
from pipeline.load import load_models

AS_OF = date(2026, 10, 4)
FIXTURE = ROOT / "web/src/decide/__fixtures__/live-vocabulary.json"
LOCAL_KEY = b"MODEL-404 local display fixture; not a deployment key"


def main():
    logging.basicConfig(level=logging.ERROR)
    built = build_from_repo(ROOT, premier=ROOT / "premier/slice-1.yaml", as_of=AS_OF, gate=False)
    with TemporaryDirectory(prefix="display-vocabulary-", dir=Path(__file__).parent) as directory:
        snapshot_path = built.write(Path(directory) / "snapshot.json.gz", key=LOCAL_KEY, ed25519_signer=None)
        full_path = write_decision_vocabulary(ROOT, snapshot_path, key=LOCAL_KEY, ed25519_signer=None)
        full_bytes = full_path.read_bytes()
        full = json.loads(full_bytes)
    registry = default()
    values = {
        facet.id: [True, False] if facet.value_type.kind == "boolean"
        else sorted(registry.allowed_values(facet) or ())
        for facet in registry.facets() if facet.value_type.kind in {"enum", "boolean"}
    }
    model_ids = {model.model_id for model in load_models(ROOT) if model.front.get("lifecycle") != "retired"}
    display = trim(full, model_ids=model_ids, facet_values=values)
    assert display["snapshot"] == full["snapshot"]
    assert display["as_of"] == full["coverage"]["as_of"] == AS_OF.isoformat()
    assert "coverage" not in display
    encoded = (json.dumps(display, ensure_ascii=False, separators=(",", ":")) + "\n").encode()
    FIXTURE.write_bytes(encoded)
    sources = [
        "decision/snapshot.py", "decision/vocabulary.py", "pipeline/build.py",
        "api/worker/src/display_vocabulary.py", "api/worker/vendor.py", "registry/templates.yaml",
    ]
    provenance = {
        "producer": str(Path(__file__).relative_to(ROOT)),
        "producer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "inputs": "Frozen public repository; no production or private-data call",
        "snapshot_as_of": AS_OF.isoformat(),
        "snapshot": display["snapshot"],
        "vocabulary_version": display["vocabulary_version"],
        "contract_version": display["contract_version"],
        "full_vocabulary_sha256": hashlib.sha256(full_bytes).hexdigest(),
        "fixture_sha256": hashlib.sha256(encoded).hexdigest(),
        "source_hashes": {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in sources},
        "models": len(display["models"]),
        "templates": len(display["templates"]),
        "captured_decision_snapshot": json.loads((FIXTURE.parent / "live-assistant-balanced-full.json").read_text())["snapshot"],
    }
    (Path(__file__).parent / "display-vocabulary-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(json.dumps(provenance, indent=2))


if __name__ == "__main__":
    main()
