"""MODEL-146 step 4: an independent reviewer grades the 20 recall decisions.

The reviewer is Mistral Large on the local ollama server (spark-15), a model
family distinct from the builders (OpenAI GPT via Codex and Anthropic Claude).
It grades each decision's answer, explanation and sources as right, defensible
or wrong, in the independent audit's format, and says why.

usage: python independent_review.py <recall-report.json> <out.md>
"""

from __future__ import annotations

import json
import sys
import time
import urllib.request

OLLAMA = "http://100.127.37.30:11434/api/chat"
MODEL = "mistral-large:123b-instruct-2411-q4_K_M"

RUBRIC = """You are an independent reviewer auditing a model-selection engine.
For one question you get: the question as a developer asked it, the
constraints, and the engine's decision (ranked results with their measured
values and sources, models that "may qualify" because a fact is unknown, and
eliminations). Grade three things, each as exactly one of right, defensible,
wrong:

- answer: are the top results a sound answer to the question under its
  constraints, as of September 2026? "defensible" if reasonable people could
  pick them; "wrong" if a clearly better or required model is missing, or a
  result violates a constraint.
- explanation: does the decision's evidence actually support the ranking?
- sources: are the cited sources primary or independent, and do they fit?

Be strict and concrete. An empty result is "wrong" for answer unless the
constraints truly admit nothing. Do not invent facts about models; if you are
unsure whether a model exists or what it scores, say so and grade
"defensible" rather than "wrong".

Reply with JSON only:
{"answer": "...", "explanation": "...", "sources": "...", "why": "<= 80 words"}
"""


def slim(decision: dict) -> dict:
    """Keep what a reviewer needs from the recall report's decision summary."""
    return {
        "status": decision.get("status"),
        "top_3": decision.get("top_3") or [],
        "may_qualify_count": decision.get("may_qualify_count"),
        "may_qualify": [
            {"model": m.get("model"), "unknown": m.get("unknown")}
            for m in (decision.get("may_qualify") or [])[:8]
        ],
        "relax": decision.get("relax"),
        "warnings": decision.get("warnings"),
        "out_of_lineup": decision.get("out_of_lineup"),
    }


def grade(question: dict) -> dict:
    prompt = json.dumps({
        "id": question["id"],
        "question": question.get("question"),
        "constraints": CONSTRAINTS.get(question["id"]),
        "decision": slim(question.get("decision") or {}),
        "error": question.get("error"),
    }, ensure_ascii=False)
    body = json.dumps({
        "model": MODEL,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0},
        "messages": [{"role": "system", "content": RUBRIC},
                     {"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(OLLAMA, data=body,
                                 headers={"content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as resp:
        content = json.load(resp)["message"]["content"]
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"answer": "unparsed", "explanation": "unparsed",
                "sources": "unparsed", "why": content[:300]}


CONSTRAINTS: dict = {}


def main() -> None:
    import yaml  # the repo venv has it
    report = json.load(open(sys.argv[1]))
    for q in yaml.safe_load(open("tests/recall/questions.yaml"))["questions"]:
        CONSTRAINTS[q["id"]] = q.get("constraints")
    rows = []
    for q in report["questions"]:
        t0 = time.time()
        g = grade(q)
        rows.append((q["id"], q.get("verdict"), g, time.time() - t0))
        print(q["id"], g.get("answer"), g.get("explanation"), g.get("sources"),
              f"{rows[-1][3]:.0f}s", flush=True)
    counts = {k: {} for k in ("answer", "explanation", "sources")}
    for _, _, g, _ in rows:
        for k in counts:
            counts[k][g.get(k)] = counts[k].get(g.get(k), 0) + 1
    with open(sys.argv[2], "w") as out:
        out.write("# Independent review of the 20 recall decisions (MODEL-146 step 4)\n\n")
        out.write(f"Reviewer: `{MODEL}` on local ollama, a family distinct from the "
                  "builders (OpenAI GPT via Codex, Anthropic Claude). Temperature 0.\n\n")
        out.write(f"Recall report reviewed: `{sys.argv[1].split('/')[-1]}`, "
                  f"snapshot `{report.get('snapshot')}`.\n\n")
        out.write("| Grade | Answer | Explanation | Sources |\n|---|---:|---:|---:|\n")
        for label in ("right", "defensible", "wrong", "unparsed"):
            out.write(f"| {label} | " + " | ".join(
                str(counts[k].get(label, 0)) for k in ("answer", "explanation", "sources")) + " |\n")
        out.write("\n| Q | Recall verdict | Answer | Explanation | Sources | Why |\n"
                  "|---|---|---|---|---|---|\n")
        for qid, verdict, g, _ in rows:
            why = str(g.get("why", "")).replace("|", "/").replace("\n", " ")
            out.write(f"| {qid} | {verdict} | {g.get('answer')} | {g.get('explanation')} "
                      f"| {g.get('sources')} | {why} |\n")
    print("wrote", sys.argv[2])


if __name__ == "__main__":
    main()
