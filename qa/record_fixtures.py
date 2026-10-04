"""Record local public-engine responses for CI; agent/judge turns are explicitly scripted.

This utility makes no HTTP calls and reads no keys. It is not a vendor evaluation.
    python -m qa.record_fixtures
"""

from __future__ import annotations

import gzip
import json
from datetime import date
from time import perf_counter

import yaml

from decision.contract import SpecError, parse_spec
from decision.engine import decide
from decision.registry import default
from decision.templates import load_catalogue
from decision.vocabulary import build_vocabulary
from qa.agent_harness import HERE, ROOT, load_scenarios
from scripts.recall_run import _snapshot


def main() -> None:
    registry = default()
    snapshot, gaps = _snapshot(
        root=ROOT, snapshot_file=None, report_date=date(2026, 10, 1), registry=registry
    )
    vocabulary = build_vocabulary(snapshot, registry=registry)
    templates = {t["id"]: t["spec"] for t in load_catalogue()["templates"]}
    records = []

    def record(name, arguments):
        started = perf_counter()
        if name == "vocab":
            status, body = 200, vocabulary
        else:
            try:
                spec = parse_spec(arguments, facets=registry.facet)
                body = decide(spec, snapshot, facets=registry.facet).model_dump(mode="json")
                status = 200
            except SpecError as exc:
                status = 400
                body = {
                    "error": {"code": "invalid_spec", "issues": [i.as_dict() for i in exc.issues]}
                }
        row = {
            "name": name,
            "arguments": arguments,
            "envelope": {
                "origin": "http://127.0.0.1:8787/"
                + ("v1/vocabulary" if name == "vocab" else "v1/decide"),
                "status": status,
                "body": body,
            },
            "latency_ms": (perf_counter() - started) * 1000,
        }
        records.append(row)
        return len(records) - 1

    vocab_record = record("vocab", {})
    fixtures = {}
    for s in load_scenarios():
        sid = s["id"]
        if s.get("fixture_spec"):
            spec = s["fixture_spec"]
        elif sid.startswith("recall-"):
            spec = yaml.safe_load(
                (ROOT / f"tests/recall/specs/{s['expected']['id']}.yaml").read_text()
            )
        elif s.get("template"):
            spec = templates[s["template"]]
        elif s["family"] == "F3":
            device = {
                "hardware-5090": "nvidia_rtx_5090",
                "hardware-spark": "nvidia_dgx_spark",
                "hardware-m4": "apple_m4",
                "hardware-dual-4090": "nvidia_rtx_4090",
                "hardware-h100": "nvidia_h100_sxm5_80gb",
            }.get(sid)
            if device is None:
                raise ValueError(f"{sid}: add fixture_spec for this hardware variant")
            spec = {
                "spec_version": 1,
                "where": [
                    "model.weights_openness = open_weights",
                    f"model.fits_hardware in {{{device}}}",
                ],
                "optimize": {"max": "software_engineering"},
            }
        elif s["family"] == "F4":
            constraint = s["constraints"]
            spec = templates[
                "regional-budget"
                if sid == "budget-eu"
                else "regulated-budget"
                if sid == "budget-hipaa"
                else "assistant-budget"
            ]
            spec = json.loads(json.dumps(spec))
            spec["where"].append(
                "offering.cost_per_task <= "
                + str(constraint["monthly_budget_usd"] / constraint["requests_per_month"])
            )
            spec["where"].append(
                "offering.provider in {" + ", ".join(constraint["available_apis"]) + "}"
            )
            spec["task_tokens"] = constraint["task_tokens"]
        else:
            spec = {"spec_version": 1, "task": s["prompt"], "optimize": {"max": "reasoning"}}
        spec = spec | {"explain": "summary", "limit": 5}
        try:
            spec = parse_spec(spec, facets=registry.facet).model_dump(
                mode="json", by_alias=True, exclude_defaults=True
            )
        except SpecError:
            pass
        final_record = record("decide", spec)
        response = records[final_record]["envelope"]["body"]
        # These recommendations are taken from responses, never the expected YAML.
        candidates = list(
            dict.fromkeys(r["offering"]["model"] for r in response.get("results", []))
        )
        top = candidates[:1]
        answer = response.get("answer") or {}
        if answer.get("members"):
            top = answer["members"]
        notes = "No unique quality winner is established by this scripted replay. "
        if s.get("gaps"):
            notes += " ".join(g["reason"] for g in s["gaps"]) + " "
        if "error" in response:
            top = []
            notes += "The API refused this Spec; I cannot recommend a model for all constraints. "
        final_text = notes + ("Top recommendation: " + ", ".join(top) if top else "I abstain.")
        # Judge is a fixed separate replay call. It does not claim a model judged this.
        # The conservative verdict fails scenarios with omitted policy/fit evidence.
        verdict = {
            "passed": False,
            "rationale": "Scripted fixture judge. The scripted answer does "
            "not provide enough offering-level evidence to pass the full rubric.",
            "top_models": top,
            "answer_kind": "tied" if len(top) > 1 else "single" if top else "abstain",
            "missing_capabilities": [g["reason"] for g in s.get("gaps", [])],
        }
        fixtures[sid] = {}
        for family in ("claude", "openai", "gemini"):
            indices = [vocab_record]
            if sid == "recall-q08":
                wrong = json.loads(json.dumps(spec))
                if family == "openai":
                    wrong["task_type"] = "coding"
                else:
                    wrong["where"].append("model.context_tokens >= 200000")
                indices.append(record("decide", wrong))
            indices.append(final_record)
            turns = [
                {
                    "text": "",
                    "calls": [
                        {
                            "id": f"fixture-{i}",
                            "name": records[idx]["name"],
                            "arguments": records[idx]["arguments"],
                        }
                    ],
                    "tokens_in": 2000 + i * 200,
                    "tokens_out": 100,
                }
                for i, idx in enumerate(indices)
            ]
            turns.append({"text": final_text, "calls": [], "tokens_in": 2600, "tokens_out": 150})
            fixtures[sid][family] = {
                "turns": turns,
                "record_indices": indices,
                "judge": {
                    "text": json.dumps(verdict),
                    "calls": [],
                    "tokens_in": 3000,
                    "tokens_out": 150,
                },
            }
    payload = {
        "provenance": {
            "api": "Recorded local engine responses from public repository inputs",
            "snapshot": snapshot.snapshot_id,
            "date": "2026-10-01",
            "agent_and_judge": "Scripted regression fixtures; no vendor model calls",
            "usage": "Synthetic token counts; cost is zero",
            "latency": "Recorded local engine/vocabulary durations, not network timings",
            "completeness_gaps": len(gaps),
            "generator": "python -m qa.record_fixtures",
        },
        "records": records,
        "scenarios": fixtures,
    }
    (HERE / "fixtures/replay.json.gz").write_bytes(
        gzip.compress(json.dumps(payload, ensure_ascii=False).encode(), mtime=0)
    )
    print(f"Recorded {len(records)} local responses for {len(fixtures)} scenarios")


if __name__ == "__main__":
    main()
