"""Read-only local reproduction of template decisions with supported routes."""

import json

from decision.contract import parse_spec
from decision.engine import decide
from decision.templates import load_templates
from tests.corpus.corpus import load, snapshot_bytes

snapshot = load(snapshot_bytes("repo"))
templates = {template["id"]: template["spec"] for template in load_templates()}
for name in (
    "assistant-balanced", "coding-balanced", "writing-balanced", "long-documents",
    "high-volume-balanced",
):
    base = dict(templates[name]) | {
        "explain": "summary",
        "task_tokens": templates[name].get("task_tokens", {"input": 40000, "output": 4000}),
    }
    for access in (None, "chat_app", "coding_tool", "own_software", "own_hardware"):
        request = base | ({"access": access} if access else {})
        answer = decide(parse_spec(request, facets=None), snapshot)
        print(json.dumps({
            "template": name,
            "access": access,
            "status": answer.status,
            "members": answer.answer.members if answer.answer else None,
            "relax": answer.relax,
            "relax_single": answer.relax_single.model_dump() if answer.relax_single else None,
        }), flush=True)
