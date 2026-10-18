"""Generate screenshot answers for exact simple-page questions, offline."""

from datetime import date
import importlib.util
import json
import logging
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))

from decision.snapshot import build_from_repo, load_built_snapshot


def main():
    logging.basicConfig(level=logging.ERROR)
    vocabulary = json.loads((ROOT / "web/src/decide/__fixtures__/live-vocabulary.json").read_text())
    templates = {row["id"]: row for row in vocabulary["templates"]}
    questions = {}
    for name, template_id in [("coding", "coding-balanced"), ("no-fit", "assistant-budget")]:
        template = templates[template_id]
        conditions = list(template["spec"]["where"])
        if name == "no-fit":
            conditions += [row["condition"] for row in templates["private-self-host"]["where"] if row["condition"].startswith(("model.weights_openness ", "licence.commercial_use "))]
        weights = template["spec"]["optimize"]["weights"]
        questions[name] = {
            "spec_version": 1,
            "snapshot": "latest",
            "capabilities": {key: "required" for key in weights if not key.startswith("-")},
            "task_tokens": template["spec"].get("task_tokens", vocabulary["default_task_tokens"]),
            "where": list(dict.fromkeys(conditions)),
            "optimize": {"weights": weights},
            "unknowns": "default",
            "explain": "full",
            "limit": 500,
        }
    built = build_from_repo(ROOT, premier=ROOT / "premier/slice-1.yaml", as_of=date(2026, 10, 4), gate=False)
    snapshot = load_built_snapshot(built, source="MODEL-404 screenshot evidence, frozen repository")
    module_spec = importlib.util.spec_from_file_location("model404_evidence_service", ROOT / "api/worker/src/decide_service.py")
    if module_spec is None or module_spec.loader is None:
        raise RuntimeError("Could not load decision service")
    service = importlib.util.module_from_spec(module_spec)
    sys.modules[module_spec.name] = service
    module_spec.loader.exec_module(service)
    out = Path(__file__).parent / ".generated"
    out.mkdir(exist_ok=True)
    manifest = {}
    for name, spec in questions.items():
        status, body = service.decide(spec, snapshot)
        if status != 200:
            raise RuntimeError(f"{name}: {status}: {body}")
        (out / f"{name}-decision.json").write_text(json.dumps({"spec": spec, "decision": body}, separators=(",", ":")) + "\n")
        manifest[name] = {"spec": spec, "snapshot": snapshot.snapshot_id, "decision_id": body["decision_id"], "status": body["status"], "answer": body.get("answer")}
        print(f"{name}: snapshot={snapshot.snapshot_id}, status={body['status']}, answer={body.get('answer', {}).get('kind') if body.get('answer') else None}")
    (out.parent / "screenshot-decisions.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
