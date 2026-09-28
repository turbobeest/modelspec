"""MODEL-160: board projections re-read by the deterministic verifier.

Each retained copy is a JSON projection of a fetched board. These tests feed a
projection to the real verifier, so a projection the readers cannot confirm
fails here and not on a live claim.
"""

from __future__ import annotations

import io
import json
from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest
import yaml

from decision.model import SourceRef, TargetRef, VerificationActor
from decision.normalise import NORMALISERS, normalise_document
from decision.verify import Claim, StructuredDataExtractor, compare
from scripts import model_160_evidence as m160

ROOT = Path(__file__).resolve().parents[1]
COLLECTOR = VerificationActor(agent="test-collector", model_family="test", method="test")
REF = SourceRef(source_id="s", snapshot_ref="sha256:" + "0" * 64, cited_regions=["rows"])


def claim(value, *, names, label, unit="percent", effort=None, harness=None, day=None):
    return Claim(
        target=TargetRef(kind="evidence", id="x"), subject="lab/model", names=names,
        field="bench", label=label, value=value, unit=unit,
        conditions={"effort": effort, "harness": harness, "date": day},
        collector=COLLECTOR, sources=(REF,),
    )


def diffs(body: bytes, c: Claim):
    """Read ``body`` as ``StoredRegions`` serves a ``text-default`` copy's page region."""
    reader = StructuredDataExtractor()
    text = normalise_document(body, replace(NORMALISERS["text-default"],
                                            strip_volatile=False)).text
    assert reader.accepts(text)
    return compare(c, reader.extract(c, text))


def rsc_page(variants: list[dict]) -> str:
    payload = '1a:["$","div",null,{"children":["$","$L1c",null,{"variants":' \
        + json.dumps(variants) + '}]}]\n'
    return ("<html><body><script>self.__next_f.push([1," + json.dumps(payload)
            + "])</script></body></html>")


def test_scale_projection_keeps_the_public_variant_and_marks_the_harness() -> None:
    entry = {"model": "gpt-5.4 (xHigh)*", "score": 59.1, "confidenceInterval_upper": 3.56,
             "createdAt": "2026-04-08T17:04:48.000Z"}
    page = rsc_page([
        {"key": "public", "label": "Public", "entries": [entry]},
        {"key": "private", "label": "Private",
         "entries": [{**entry, "model": "gpt-5.4(xHigh)*", "score": 43.4}]},
    ])
    body = m160.project_scale(page, url="https://example.test", page_ref="sha256:x")
    rows = json.loads(body)["rows"]
    assert rows == [{"model": "gpt-5.4 (xHigh)*", "resolve_rate": 59.1, "ci95": 3.56,
                     "date": "2026-04-08", "agent": "mini-swe-agent"}]
    ok = claim(59.1, names=("gpt-5.4 (xHigh)*",), label="resolve_rate", effort="xhigh",
               harness="unregistered", day="2026-04-08")
    assert diffs(body, ok) == []
    private = claim(43.4, names=("gpt-5.4 (xHigh)*",), label="resolve_rate", effort="xhigh",
                    harness="unregistered", day="2026-04-08")
    assert diffs(body, private)


def test_swebench_projection_reads_one_board_and_its_agent() -> None:
    boards = [
        {"name": "Verified", "results": [
            {"name": "Claude 4.6 Opus", "agent": "mini-SWE-agent", "date": "2026-02-17",
             "resolved": 75.6, "reasoning_effort": None, "per_instance_details": {"a": 1}}]},
        {"name": "Multilingual", "results": [
            {"name": "Claude 4.6 Opus", "agent": "mini-SWE-agent", "date": "2026-02-13",
             "resolved": 72.0, "reasoning_effort": None}]},
    ]
    page = ('<script type="application/json" id="leaderboard-data">'
            + json.dumps(boards) + "</script>")
    body = m160.project_swebench(page, "Verified", url="https://example.test",
                                 page_ref="sha256:x")
    ok = claim(75.6, names=("Claude 4.6 Opus",), label="resolve_rate",
               harness="unregistered", day="2026-02-17")
    assert diffs(body, ok) == []
    assert diffs(body, claim(72.0, names=("Claude 4.6 Opus",), label="resolve_rate",
                             harness="unregistered", day="2026-02-17"))


def test_arena_projection_is_one_category_of_one_config() -> None:
    pa = pytest.importorskip("pyarrow")
    pq = pytest.importorskip("pyarrow.parquet")
    table = pa.Table.from_pylist([
        {"model_name": "claude-fable-5", "rating": 1505.6827, "category": "overall",
         "leaderboard_publish_date": "2026-09-13", "vote_count": 30057.0},
        {"model_name": "claude-fable-5", "rating": 1552.3912, "category": "coding",
         "leaderboard_publish_date": "2026-09-13", "vote_count": 9000.0},
    ])
    buffer = io.BytesIO()
    pq.write_table(table, buffer)
    body = m160.project_arena(buffer.getvalue(), "text_style_control", "overall",
                              url="https://example.test", page_ref="sha256:x")
    names = ("claude-fable-5",)
    unit = "Arena score (Elo scale)"
    assert diffs(body, claim(1505.68, names=names, label="rating", unit=unit,
                             day="2026-09-13")) == []
    assert diffs(body, claim(1552.39, names=names, label="rating", unit=unit,
                             day="2026-09-13"))


def test_cursorbench_projection_splits_the_effort_off_the_name() -> None:
    page = ("<table><tr><th>#</th><th>Model</th><th></th><th></th></tr>"
            "<tr><td>1</td><td>Opus 5.5 Max</td><td>57.8 %</td><td>$ 13.43</td></tr>"
            "<tr><td>2</td><td>Grok 4.7 Extra High</td><td>46.3 %</td><td>$ 6.01</td></tr>"
            "</table>")
    body = m160.project_cursorbench(page, url="https://example.test", page_ref="sha256:x",
                                    read_date="2026-09-25")
    rows = json.loads(body)["rows"]
    assert rows[1] == {"model": "Grok 4.7", "reasoning_effort": "xhigh", "accuracy": 46.3,
                       "usd_per_task": 6.01}
    ok = claim(57.8, names=("Opus 5.5 (max)",), label="accuracy", effort="max",
               day="2026-09-25")
    assert diffs(body, ok) == []


def test_matharena_projection_parses_the_accuracy_cell() -> None:
    table = ("<table><thead><tr><th>Rank</th><th>Model Name</th><th>Provider</th>"
             "<th>Accuracy (± 95% CI)</th></tr></thead><tbody>"
             "<tr><td>3</td><td>GPT-5.4 (xhigh) ⚠️</td><td>OpenAI</td>"
             "<td>99.17% ± 1.63%</td></tr></tbody></table>")
    body = m160.project_matharena(json.dumps({"table": table}).encode(),
                                  url="https://example.test", page_ref="sha256:x",
                                  read_date="2026-09-25")
    ok = claim(99.17, names=("GPT-5.4 (xhigh)",), label="accuracy", effort="xhigh",
               day="2026-09-25")
    assert diffs(body, ok) == []


def test_metr_projection_states_minutes() -> None:
    document = {"results": {"gpt_5_4": {
        "release_date": date(2026, 3, 5),
        "metrics": {"p50_horizon_length": {"estimate": 341.735276},
                    "p80_horizon_length": {"estimate": 80.1}}}}}
    body = m160.project_metr(yaml.safe_dump(document).encode(),
                             url="https://example.test", page_ref="sha256:x",
                             read_date="2026-09-25")
    ok = claim(341.735276, names=("gpt_5_4",), label="p50_horizon_length",
               unit="minutes")
    assert diffs(body, ok) == []
    assert diffs(body, claim(341.735276, names=("gpt_5_4",), label="p50_horizon_length",
                             unit="hours"))


def test_tau_projection_reads_pass_1_with_effort_and_date() -> None:
    submission = {"model_name": "GPT-5.4", "reasoning_effort": "xhigh",
                  "results": {"banking_knowledge": {"pass_1": 39.43}},
                  "methodology": {"evaluation_date": "2026-05-06"}}
    body = m160.project_tau(json.dumps(submission).encode(), url="https://example.test",
                            page_ref="sha256:x")
    ok = claim(39.43, names=("GPT-5.4 (xhigh)",), label="pass_1", effort="xhigh",
               day="2026-05-06")
    assert diffs(body, ok) == []


def test_deepswe_projection_keeps_every_effort_level() -> None:
    artifact = {"generated_at": "2026-09-22T06:27:15+00:00", "rows": [
        {"model": "gpt-6-astra", "harness": "mini-swe-agent", "reasoning_effort": "xhigh",
         "pass_at_1": 0.7411504424778761},
        {"model": "gpt-6-astra", "harness": "mini-swe-agent", "reasoning_effort": "max",
         "pass_at_1": 0.7323008849557522},
    ]}
    body = m160.project_deepswe(json.dumps(artifact).encode(), url="https://example.test",
                                page_ref="sha256:x", read_date="2026-09-25")
    ok = claim(73.23, names=("gpt-6-astra (max)",), label="pass_at_1", effort="max",
               harness="unregistered", day="2026-09-25")
    assert diffs(body, ok) == []
    assert diffs(body, claim(74.12, names=("gpt-6-astra (max)",), label="pass_at_1",
                             effort="max", harness="unregistered", day="2026-09-25"))


def test_vending_projection_reads_only_the_vb2_object() -> None:
    chunk = ('const q=[1,2],m={vb2:{"Claude Opus 4.6":{num_epochs:5,num_final_values:5,'
             'time_series:[500,510.5],final_value:8017.594,final_value_std:3056.7},'
             '"Claude Fable 5 - Max":{num_epochs:5,time_series:[],final_value:4966.64}},'
             '"arena-x":{"Claude Opus 4.6":{num_epochs:5,final_value:5062.33}}};')
    body = m160.project_vending(chunk, url="https://example.test", page_ref="sha256:x",
                                read_date="2026-09-25")
    rows = json.loads(body)["rows"]
    assert [r["model"] for r in rows] == ["Claude Opus 4.6", "Claude Fable 5 - Max"]
    ok = claim(8017.59, names=("Claude Opus 4.6",), label="money_balance", unit="USD",
               day="2026-09-25")
    assert diffs(body, ok) == []
    assert diffs(body, claim(5062.33, names=("Claude Opus 4.6",), label="money_balance",
                             unit="USD", day="2026-09-25"))


FRONTIERCODE_MD = """\
| # | Model | Score▼ | Pass rate▼ | Flag rate▼ | Cost / rollout▼ | Output tokens▼ |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | Fable 5.1medium | 50.9% | 55.5% | 0.0% | $3.28 | 26.1k |
| 6 | [SWE-2](https://cognition.com/blog/swe-2) max | 50.0% | 55.5% | — | $1.18 | 72.8k |
| 12 | Kimi K3 | 44.2% | 48.9% | 0.2% | $3.82 | 53.6k |
| 40 | Mistral 3.5 Medium | 8.0% | 9.0% | 0.6% | $1.35 | 22.5k |
"""


def test_frontiercode_projection_splits_the_glued_effort() -> None:
    body = m160.project_frontiercode(FRONTIERCODE_MD, url="https://example.test",
                                     page_ref="sha256:x", read_date="2026-09-25")
    rows = json.loads(body)["rows"]
    assert [(r["model"], r.get("reasoning_effort")) for r in rows] == [
        ("Fable 5.1", "medium"), ("SWE-2", "max"), ("Kimi K3", None),
        ("Mistral 3.5 Medium", None)]
    ok = claim(50.9, names=("Fable 5.1",), label="score", effort="medium", day="2026-09-25")
    assert diffs(body, ok) == []


def test_osworld_projection_reads_binary_reward_per_effort() -> None:
    table = """\
| Model | Effort | Version | X metric | Binary reward | Partial reward |
| --- | --- | --- | --- | --- | --- |
| Claude Opus 5 | max | v2026.08.08 | 103K | 31.4% | 68.3% |
| Claude Opus 5 | xhigh | v2026.08.08 | 73.1K | 30.2% | 67.7% |
"""
    body = m160.project_osworld(table, url="https://example.test", page_ref="sha256:x",
                                read_date="2026-09-25")
    ok = claim(31.4, names=("Claude Opus 5 (max)",), label="binary_reward", effort="max",
               day="2026-09-25")
    assert diffs(body, ok) == []
    assert diffs(body, claim(30.2, names=("Claude Opus 5 (max)",), label="binary_reward",
                             effort="max", day="2026-09-25"))


@pytest.fixture(scope="module")
def premier_evidence() -> list[dict]:
    rows = []
    for entry in yaml.safe_load((ROOT / "premier" / "slice-1.yaml").read_text())["models"]:
        provider, name = entry["model_id"].split("/", 1)
        text = (ROOT / "models" / provider / f"{name}.md").read_text(encoding="utf-8")
        front = yaml.safe_load(text.split("---", 2)[1])
        rows += (front.get("benchmarks") or {}).get("evidence") or []
    return rows


@pytest.mark.parametrize(("benchmark", "source"), [
    ("arena_elo_style_control", "model-160-arena-text-style-control"),
    ("arena_sc_vision", "model-160-arena-vision-style-control"),
    ("arena_elo_overall", "model-160-arena-text"),
    ("arena_elo_vision", "model-160-arena-vision"),
])
def test_arena_rows_cite_the_config_their_benchmark_names(premier_evidence, benchmark,
                                                           source) -> None:
    """MODEL-143 verified style-control rows against the raw ``text`` config."""
    cited = {ref["source_id"] for row in premier_evidence
             if row["benchmark_id"] == benchmark for ref in row.get("sources") or []}
    assert cited == {source}


def test_arena_rows_state_the_unit_the_reader_confirms(premier_evidence) -> None:
    """A filed row's card unit is the unit its claim was verified in."""
    units = {row["unit"] for row in premier_evidence
             if row["benchmark_id"].startswith("arena_") and row.get("sources")}
    assert units == {"Arena score (Elo scale)"}
