#!/usr/bin/env python3
"""Evaluate Jev in four non-generative ModelSpec jobs (MODEL-112).

The labelled inputs live in ``tests/fixtures/jev_*.yaml``. ``--plan`` makes no
network calls. ``--run`` calls pinned Jev and the same gpt-5-mini baseline used
by ``scripts/eval_cost_to_correct.py``. The output is JSONL: one paid answer per
row followed by a summary. Re-analysis needs no key and spends nothing.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import yaml

from decision.registry import default as default_registry
from decision.sources import CopyStore, load_sources
from decision.verify import Claim, StoredRegions
from scripts.attribution import TypeSafeJudge, load_config

ROOT = Path(__file__).resolve().parents[2]
TASK_LABELS = ROOT / "tests/fixtures/jev_task_routing.yaml"
JUDGMENT_LABELS = ROOT / "tests/fixtures/jev_judgment_labels.yaml"
VOCABULARY = ROOT / "web/src/decide/__fixtures__/vocabulary.json"
FIXTURE_URL = (
    "https://github.com/turbobeest/modelspec/blob/main/"
    "tests/fixtures/verification/leaderboard.html"
)
JEV_PRICE = 0.042 / 1_000_000
JEV_PRICE_SOURCE = "https://docs.typesafe.ai/models"
JEV_DOCS_READ_DATE = "2026-09-25"
BASELINE_MODEL = "openai/gpt-5-mini"
ACT = 0.90
FLAG = 0.60
NO_MATCH = "no_match"


@dataclass(frozen=True)
class Case:
    id: str
    candidate: str
    state: dict[str, Any]
    questions: dict[str, Any]
    expected: dict[str, Any]
    source_url: str
    source_read_date: str


@dataclass(frozen=True)
class Arm:
    name: str
    model: str
    input_price: float
    output_price: float
    price_source: str
    price_read_utc: str

    def cost(self, input_tokens: int, output_tokens: int) -> float:
        return input_tokens * self.input_price + output_tokens * self.output_price


def confidence_band(confidence: float, *, no_match: bool = False) -> str:
    """The binding act / flag / null policy. Arithmetic stays in code."""
    if no_match or confidence < FLAG:
        return "null"
    return "act" if confidence >= ACT else "flag"


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, round(q * (len(ordered) - 1)))]


def normalise_answer(answer: dict[str, Any]) -> Any:
    if answer.get("type") == "choice":
        return str(answer.get("choice"))
    if answer.get("type") == "noul":
        return bool(float(answer.get("noul", 0.0)) >= 0.5)
    raise ValueError("answer is neither Choice nor Noul")


def score_answers(
    body: dict[str, Any], expected: dict[str, Any]
) -> tuple[bool, float, bool, dict[str, Any]]:
    answers = body.get("answers")
    if not isinstance(answers, dict):
        raise ValueError("missing answers")
    values: dict[str, Any] = {}
    confidences: list[float] = []
    chose_no_match = False
    for question_id, wanted in expected.items():
        raw = answers.get(question_id)
        if not isinstance(raw, dict):
            raise ValueError(f"missing answer {question_id}")
        value = normalise_answer(raw)
        values[question_id] = value
        if raw.get("type") == "choice":
            probabilities = raw.get("probabilities") or {}
            if value not in probabilities:
                raise ValueError(f"choice {value!r} lacks a probability")
            confidences.append(float(raw.get("confidence", probabilities[value])))
            chose_no_match = chose_no_match or value == NO_MATCH
        else:
            probability = float(raw.get("noul", 0.0))
            confidences.append(max(probability, 1.0 - probability))
        if type(value) is not type(wanted):  # bool must not compare equal to 0/1
            raise ValueError(f"answer type differs for {question_id}")
    return values == expected, min(confidences, default=0.0), chose_no_match, values


def choice(question: str, options: list[str], descriptions: dict[str, str] | None = None) -> dict:
    descriptions = descriptions or {}
    return {
        "type": "choice",
        "instructions": question,
        "criteria": {option: descriptions.get(option) for option in options},
    }


def task_cases() -> list[Case]:
    labels = yaml.safe_load(TASK_LABELS.read_text(encoding="utf-8"))
    registry = default_registry()
    registered_domains = registry.domains()
    domains = [row.id for row in registered_domains] + [NO_MATCH]
    domain_descriptions = {
        row.id: {"name": row.name, "definition": row.definition} for row in registered_domains
    }
    domain_descriptions[NO_MATCH] = "No registered domain fits the task text."
    class_facet = registry.facet("model.class")
    classes = sorted(registry.allowed_values(class_facet) or ()) + [NO_MATCH]
    class_descriptions = {
        class_id: class_facet.value_label(class_id) or class_id for class_id in classes
    }
    class_descriptions[NO_MATCH] = "The task text does not establish a model class."
    condition_text = {
        "context_200k": "The task requires at least 200,000 tokens of context.",
        "open_weights": "The task requires open weights or local/self-hosted use.",
        "commercial_use": "The task explicitly requires commercial-use rights.",
        "low_latency": "The task explicitly requires low latency or interactive response.",
    }
    cases = []
    for row in labels["cases"]:
        expected = {"domain": row["domain"], "class": row["class"]}
        questions = {
            "domain": choice(
                "Which one registered capability domain does this task primarily require? "
                "Choose no_match when none fits. Judge only the task text.",
                domains,
                domain_descriptions,
            ),
            "class": choice(
                "Which model class does the task require? Choose no_match when the text is "
                "insufficient. Judge what the model consumes, emits, or decides.",
                classes,
                class_descriptions,
            ),
        }
        wanted = set(row.get("conditions") or [])
        for condition, instructions in condition_text.items():
            question_id = f"condition_{condition}"
            questions[question_id] = {
                "type": "noul",
                "instructions": instructions + " Do not infer an unstated requirement.",
                "criteria": {"true": "Explicitly required", "false": "Not explicitly required"},
            }
            expected[question_id] = condition in wanted
        cases.append(
            Case(
                row["id"],
                "task_routing",
                {"task": row["text"]},
                questions,
                expected,
                "https://github.com/turbobeest/modelspec/blob/main/tests/recall/questions.yaml",
                labels["read_date"],
            )
        )
    return cases


def fixture_region() -> str:
    return (ROOT / "tests/fixtures/verification/leaderboard.html").read_text(encoding="utf-8")


def evidence_attribution_cases(labels: dict[str, Any]) -> list[Case]:
    group = labels["attribution"]
    cases = []
    for row in group["cases"]:
        proposed = {k: v for k, v in row.items() if k not in ("id", "expected")}
        proposed.setdefault("benchmark", group["benchmark"])
        proposed.setdefault("benchmark_version", group["benchmark_version"])
        cases.append(
            Case(
                row["id"],
                "evidence_attribution",
                {
                    "registered_source": {
                        "benchmark": group["benchmark"],
                        "version": group["benchmark_version"],
                    },
                    "proposed_evidence": proposed,
                    "cited_region": fixture_region(),
                },
                {
                    "attribution": choice(
                        "Does the cited region support this exact number for this model variant, "
                        "benchmark version, effort, harness, and unit? Select no_match if any "
                        "identity or condition is absent or differs.",
                        ["belongs", NO_MATCH],
                    )
                },
                {"attribution": row["expected"]},
                FIXTURE_URL,
                labels["read_date"],
            )
        )
    return cases


def _claims_and_latest() -> tuple[dict[str, dict], dict[str, dict]]:
    claims: dict[str, dict] = {}
    queue = ROOT / "verification/queue/events.jsonl"
    for line in queue.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if claim := row.get("claim"):
            target = claim["target"]
            claims[f"{target['kind']}:{target['id']}"] = claim
    latest: dict[str, dict] = {}
    for line in (ROOT / "verification/log.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        target = row["target"]
        key = f"{target['kind']}:{target['id']}"
        old = latest.get(key)
        if old is None or row["date"] >= old["date"]:
            latest[key] = row
    return claims, latest


def second_key_cases(labels: dict[str, Any]) -> list[Case]:
    claims, latest = _claims_and_latest()
    sources = load_sources(ROOT / "registry/sources.yaml")
    regions = StoredRegions(CopyStore(), sources)
    cases = []
    for row in labels["second_key"]["cases"]:
        claim_data = claims[row["target"]]
        claim = Claim.from_dict(claim_data)
        cited = []
        urls = []
        for source_ref in claim.sources:
            source = sources[source_ref.source_id]
            urls.append(str(source.url))
            for region_id in source_ref.cited_regions:
                text = regions.text(source_ref.source_id, source_ref.snapshot_ref, region_id)
                if text:
                    cited.append(
                        {"source_id": source_ref.source_id, "region": region_id, "text": text}
                    )
        verification = latest[row["target"]]
        if not verification["method"].startswith("llm-extract:"):
            raise ValueError(f"{row['target']} was not checked by a prose reader")
        cases.append(
            Case(
                row["id"],
                "second_key",
                {"filed_claim": claim.to_dict(), "cited_regions": cited},
                {
                    "verification": choice(
                        "Do the cited regions independently support the filed claim for the exact "
                        "subject, value, unit, and conditions? Choose no_match if any part differs "
                        "or the source does not establish it.",
                        ["supported", NO_MATCH],
                    )
                },
                {"verification": row["expected"]},
                urls[0],
                verification["date"],
            )
        )
    return cases


def explanation_cases(labels: dict[str, Any]) -> list[Case]:
    cases = []
    for row in labels["explanation"]["cases"]:
        evidence = {
            "model": row["evidence_model"],
            "benchmark": "seeded-coding",
            "version": "2026-08-14",
            "effort": row["evidence_effort"],
            "harness": "codex-cli@1.4",
            "value": row["evidence_value"],
            "unit": "percent",
            "source": FIXTURE_URL,
            "date_read": labels["read_date"],
        }
        cases.append(
            Case(
                row["id"],
                "explanation_check",
                {
                    "why_sentence": row["sentence"],
                    "evidence_row": evidence,
                    "cited_region": fixture_region(),
                },
                {
                    "support": choice(
                        "Is every factual assertion in why_sentence supported by the evidence row "
                        "and its cited region? Choose no_match for contradiction, missing support, "
                        "or a claim that exceeds the row.",
                        ["supported", NO_MATCH],
                    )
                },
                {"support": row["expected"]},
                FIXTURE_URL,
                labels["read_date"],
            )
        )
    return cases


def all_cases() -> list[Case]:
    labels = yaml.safe_load(JUDGMENT_LABELS.read_text(encoding="utf-8"))
    return [
        *task_cases(),
        *evidence_attribution_cases(labels),
        *second_key_cases(labels),
        *explanation_cases(labels),
    ]


def parse_real_task_baseline(cases: list[Case]) -> list[dict[str, Any]]:
    tasks = [c for c in cases if c.candidate == "task_routing"]
    payload = {
        "vocabulary": str(VOCABULARY),
        "tasks": [{"id": c.id, "text": c.state["task"]} for c in tasks],
    }
    scratch = Path(
        "/private/tmp/claude-501/-Users-terbeest-dev-modelspec/"
        "6b307b20-b183-41a5-91e6-14f65d035cbc/scratchpad/slice1/112"
    )
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as temporary:
        input_path = Path(temporary) / "task-input.json"
        output_path = Path(temporary) / "task-output.json"
        input_path.write_text(json.dumps(payload), encoding="utf-8")
        env = os.environ.copy()
        env["MODELSPEC_JEV_TASK_INPUT"] = str(input_path)
        env["MODELSPEC_JEV_TASK_OUTPUT"] = str(output_path)
        subprocess.run(
            [
                str(ROOT / "web/node_modules/.bin/vitest"),
                "run",
                "src/decide/__tests__/research-task-parser.test.ts",
            ],
            cwd=ROOT / "web",
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )
        parsed_rows = json.loads(output_path.read_text(encoding="utf-8"))
    parsed = {row["id"]: row for row in parsed_rows}
    rows = []
    for case in tasks:
        found = parsed[case.id]
        actual = {
            "domain": found["domain"],
            "class": found["class"],
            **{
                key: key.removeprefix("condition_") in found["conditions"]
                for key in case.expected
                if key.startswith("condition_")
            },
        }
        rows.append(
            {
                "record": "item",
                "candidate": case.candidate,
                "arm": "parseRealTask",
                "case_id": case.id,
                "correct": actual == case.expected,
                "expected": case.expected,
                "actual": actual,
                "latency_ms": found["latency_ms"],
                "tokens_in": 0,
                "tokens_out": 0,
                "cost_usd": 0.0,
                "band": "act",
                "source_url": case.source_url,
                "source_read_date": case.source_read_date,
            }
        )
    return rows


def llm_body(case: Case, model: str) -> dict[str, Any]:
    payload = json.dumps({"state": case.state, "questions": case.questions}, sort_keys=True)
    return {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Judge only the supplied state. Do not supply facts from memory.",
            },
            {
                "role": "user",
                "content": payload
                + "\n\nReturn one JSON object: {\"answers\": {question_id: "
                + "{\"choice\": option} or {\"noul\": number}}}. "
                + "Use exactly the question IDs and criteria keys supplied.",
            },
        ],
        "max_tokens": 4000,
    }


def parse_llm(data: dict[str, Any], case: Case) -> dict[str, Any]:
    choices = data.get("choices") or []
    text = str(((choices[0] if choices else {}).get("message") or {}).get("content") or "")
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("baseline returned no JSON object")
    raw = json.loads(text[start : end + 1])
    if not isinstance(raw, dict) or not isinstance(raw.get("answers"), dict):
        raise ValueError("baseline JSON is not an object")
    answers = {}
    for question_id, question in case.questions.items():
        found = raw["answers"].get(question_id)
        if not isinstance(found, dict):
            raise ValueError(f"baseline omitted {question_id}")
        if question["type"] == "choice":
            selected = found.get("choice")
            if not isinstance(selected, str):
                raise ValueError(f"baseline omitted the choice for {question_id}")
            answers[question_id] = {
                "type": "choice",
                "choice": selected,
                "probabilities": {selected: 1.0},
                "confidence": 0.0,
            }
        else:
            answers[question_id] = {"type": "noul", "noul": float(found["noul"])}
    return {"answers": answers}


def baseline_prices(base_url: str, api_key: str) -> Arm:
    read = datetime.now(UTC).isoformat(timespec="seconds")
    response = httpx.get(
        base_url.rstrip("/") + "/models",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=60,
    )
    response.raise_for_status()
    model = next(row for row in response.json()["data"] if row["id"] == BASELINE_MODEL)
    pricing = model["pricing"]
    return Arm(
        "gpt-5-mini",
        BASELINE_MODEL,
        float(pricing["prompt"]),
        float(pricing["completion"]),
        base_url.rstrip("/") + "/models",
        read,
    )


def summarise(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(row["candidate"], row["arm"])].append(row)
    output = []
    for (candidate, arm), group in sorted(groups.items()):
        correct = sum(bool(row["correct"]) for row in group)
        cost = sum(float(row["cost_usd"]) for row in group)
        output.append(
            {
                "candidate": candidate,
                "arm": arm,
                "n": len(group),
                "correct": correct,
                "accuracy": round(correct / len(group), 4),
                "p50_latency_ms": round(percentile([row["latency_ms"] for row in group], 0.5), 1),
                "p95_latency_ms": round(percentile([row["latency_ms"] for row in group], 0.95), 1),
                "total_cost_usd": round(cost, 6),
                "cost_per_1000_correct_usd": round(cost / correct * 1000, 4) if correct else None,
                "bands": dict(Counter(row["band"] for row in group)),
                "failures": dict(Counter(row.get("failure") or "none" for row in group)),
            }
        )
    return output


def run(args: argparse.Namespace) -> None:
    cases = all_cases()
    if args.candidates:
        selected = {value.strip() for value in args.candidates.split(",") if value.strip()}
        known = {case.candidate for case in cases}
        if unknown := selected - known:
            raise SystemExit(f"unknown candidates: {', '.join(sorted(unknown))}")
        cases = [case for case in cases if case.candidate in selected]
    parser_rows = parse_real_task_baseline(cases)
    if args.plan:
        plan = {
            "cases": dict(Counter(c.candidate for c in cases)),
            "paid_calls": len(cases) * 2,
        }
        print(json.dumps(plan, indent=2))
        return
    jev_key = os.environ.get("TYPESAFE_API_KEY", "").strip()
    text_key = os.environ.get("TEXT_MODEL_API_KEY", "").strip()
    base_url = os.environ.get("TEXT_MODEL_BASE_URL", "https://openrouter.ai/api/v1").strip()
    if not jev_key or not text_key:
        raise SystemExit("TYPESAFE_API_KEY and TEXT_MODEL_API_KEY must be set")
    if args.max_usd <= 0 or args.max_usd > 5:
        raise SystemExit("--max-usd must be greater than 0 and no more than 5")
    config = load_config()
    judge = TypeSafeJudge(jev_key, config)
    baseline = baseline_prices(base_url, text_key)
    jev = Arm(
        "jev",
        config.model,
        JEV_PRICE,
        0.0,
        JEV_PRICE_SOURCE,
        datetime.now(UTC).isoformat(timespec="seconds"),
    )
    estimated_chars = sum(
        len(json.dumps({"state": case.state, "questions": case.questions}))
        for case in cases
    )
    projection = estimated_chars / 4 * (jev.input_price + baseline.input_price)
    projection += len(cases) * 4000 * baseline.output_price
    if projection > args.max_usd:
        raise SystemExit(
            f"projected ${projection:.4f} exceeds cap ${args.max_usd:.2f}; nothing called"
        )
    lock = threading.Lock()
    spent = 0.0
    paid_rows: list[dict[str, Any]] = []
    client = httpx.Client(base_url=base_url, timeout=180)

    def ask(case: Case, arm: Arm) -> None:
        nonlocal spent
        reserve = arm.cost(
            len(json.dumps(case.state)) // 2 + len(json.dumps(case.questions)) // 2,
            4000,
        )
        with lock:
            if spent + reserve > args.max_usd:
                raise RuntimeError("hard spend cap reached before call")
        started = time.perf_counter()
        failure = None
        body: dict[str, Any] = {}
        input_tokens = output_tokens = 0
        provider_cost = None
        try:
            if arm.name == "jev":
                body = judge.evaluate(case.state, case.questions)
                usage = body.get("usage") or {}
                input_tokens = int(usage.get("input_tokens") or 0)
                output_tokens = int(usage.get("output_tokens") or 0)
            else:
                response = client.post(
                    "/chat/completions",
                    json=llm_body(case, arm.model),
                    headers={"Authorization": f"Bearer {text_key}"},
                )
                response.raise_for_status()
                data = response.json()
                body = parse_llm(data, case)
                usage = data.get("usage") or {}
                input_tokens = int(usage.get("prompt_tokens") or 0)
                output_tokens = int(usage.get("completion_tokens") or 0)
                provider_cost = usage.get("cost")
            correct, confidence, no_match, actual = score_answers(body, case.expected)
            band = confidence_band(confidence, no_match=no_match) if arm.name == "jev" else "act"
        except Exception as exc:  # paid malformed and API failures count as wrong
            correct, confidence, actual, band = False, 0.0, {}, "null"
            failure = type(exc).__name__
        latency = (time.perf_counter() - started) * 1000
        cost = arm.cost(input_tokens, output_tokens)
        row = {
            "record": "item",
            "candidate": case.candidate,
            "arm": arm.name,
            "model": arm.model,
            "case_id": case.id,
            "correct": correct,
            "expected": case.expected,
            "actual": actual,
            "confidence": confidence,
            "band": band,
            "failure": failure,
            "latency_ms": round(latency, 1),
            "tokens_in": input_tokens,
            "tokens_out": output_tokens,
            "cost_usd": cost,
            "provider_reported_cost_usd": provider_cost,
            "source_url": case.source_url,
            "source_read_date": case.source_read_date,
        }
        with lock:
            spent += cost
            if spent > args.max_usd:
                raise RuntimeError("provider usage exceeded the hard spend cap")
            paid_rows.append(row)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(ask, case, arm) for arm in (jev, baseline) for case in cases]
        for future in futures:
            future.result()
    rows = parser_rows + sorted(
        paid_rows, key=lambda row: (row["arm"], row["candidate"], row["case_id"])
    )
    summary = {
        "record": "summary",
        "ticket": "MODEL-112",
        "read_date": JEV_DOCS_READ_DATE,
        "started_and_finished_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "thresholds": {"act": ACT, "flag": FLAG, "null": f"below {FLAG} or no_match"},
        "max_usd": args.max_usd,
        "spent_usd": round(spent, 6),
        "prices": [jev.__dict__, baseline.__dict__],
        "results": summarise(rows),
    }
    with args.out.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
        handle.write(json.dumps(summary, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2))


def analyse(path: Path) -> None:
    rows = []
    summary = None
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("record") == "item":
            rows.append(row)
        else:
            summary = row
    print(json.dumps({"stored": summary, "recomputed": summarise(rows)}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", action="store_true")
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--analyse", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--max-usd", type=float, default=4.5)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--candidates", help="comma-separated candidate names; default is all")
    args = parser.parse_args()
    if args.analyse:
        analyse(args.analyse)
        return
    if args.run and args.out is None:
        parser.error("--run requires --out")
    run(args)


if __name__ == "__main__":
    main()
