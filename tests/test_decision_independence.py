"""Two-key independence means a different model family (MODEL-140, MODEL-159).

A verifier from the collector's own model family is not a second key, whatever
its agent. The log is append-only and already holds such records, so the rule
is applied where a verification is *counted*, not where it is parsed: an old
record still loads, but a same-family ``verified`` never admits a value. A
deterministic reader has no model family and is always independent.
"""

from __future__ import annotations

import json
import urllib.request
from datetime import date

import pytest
from typer.testing import CliRunner

from decision import verify
from decision.model import Verification, VerificationActor, independent_families, model_family
from decision.snapshot import UNKNOWN, SnapshotInputs, build_snapshot, load_snapshot_bytes
from tests.snapshot_records import SOURCES, evidence, model, verification
from tests.test_decision_verify import (
    TODAY,
    _FakeLLM,
    _prose_claim,
    _repo,
    regions,  # noqa: F401 - pytest fixture
    store,  # noqa: F401 - pytest fixture
)

CLAUDE = {"agent": "claude-model-158", "model_family": "anthropic", "method": "read"}
SONNET = {"agent": "claude-cli", "model_family": "anthropic", "method": "llm-extract:sonnet"}
MISTRAL = {"agent": "ollama", "model_family": "mistral", "method": "llm-extract:mistral"}
TABLE = {"agent": "modelspec-verify", "model_family": "deterministic", "method": "table@1"}
PROSE = json.dumps([{
    "subject": "GPT-6 Sol", "value": "400,000", "unit": "tokens",
    "quoted_sentence": "It accepts up to 400,000 tokens of context.",
}])


def record(collector=CLAUDE, verifier=SONNET, outcome="verified", day="2026-09-25",
           eid="lab/alpha#terminal_bench_v4_0#55.8", score=55.8):
    v = verification("evidence", eid, outcome, day=day, value=score)
    return {**v, "collector": dict(collector), "verifier": dict(verifier)}


# --- the rule ------------------------------------------------------------------------------------


@pytest.mark.parametrize(("a", "b"), [
    ("anthropic", "anthropic"), ("claude", "anthropic"), ("gpt-5", "openai"),
    ("gemma4", "google"), ("Gemini", "gemma4"), ("qwen3", "qwen"), ("mistral", "Mistral"),
])
def test_spellings_of_one_family_are_the_same_family(a, b):
    assert model_family(a) == model_family(b)
    assert not independent_families(a, b)


@pytest.mark.parametrize(("collector", "verifier"), [
    ("anthropic", "mistral"), ("gpt-5", "anthropic"), ("gpt-5", "qwen3"), ("gpt-5", "gemma4"),
    ("anthropic", "deterministic"), ("deterministic", "deterministic"), ("gpt-5", "deterministic"),
])
def test_a_different_family_or_a_deterministic_reader_is_independent(collector, verifier):
    assert independent_families(collector, verifier)


def test_an_old_same_family_record_still_parses_but_admits_nothing():
    parsed = Verification.model_validate(record())
    assert parsed.outcome == "verified"
    assert not parsed.independent
    assert parsed.quarantined
    assert not parsed.counts


def test_a_same_family_negative_outcome_still_counts():
    # A same-family reader cannot admit a value, but its mismatch still keeps one out.
    mismatch = Verification.model_validate(record(outcome="mismatch"))
    assert mismatch.counts and mismatch.quarantined


def test_an_independent_verification_admits():
    for verifier in (MISTRAL, TABLE):
        parsed = Verification.model_validate(record(verifier=verifier))
        assert parsed.independent and parsed.counts and not parsed.quarantined


# --- admission in the snapshot -------------------------------------------------------------------


def _index(*log, inline="verified"):
    row = evidence("lab/alpha", "terminal_bench_v4_0", 55.8,
                   eid="lab/alpha#terminal_bench_v4_0#55.8", outcome=None)
    if inline:
        row["verification"] = record(outcome=inline, day="2026-09-20")
    built = build_snapshot(SnapshotInputs(
        models=[model("lab/alpha")], offerings=[], evidence=[row], sources=SOURCES,
        benchmark_domains={"terminal_bench_v4_0": [("agentic_tool_use", "direct")]},
        verifications=list(log),
    ), gate=False, as_of=date(2026, 9, 25))
    return load_snapshot_bytes(built.to_bytes(key=None), key=None)


def test_a_same_family_verification_does_not_admit_evidence():
    index = _index(record(), inline="verified")
    assert index.evidence("lab/alpha", "terminal_bench_v4_0") == ()
    assert index.excluded == {"quarantined": 1}


def test_an_independent_verification_admits_the_same_evidence():
    index = _index(record(), record(verifier=MISTRAL, day="2026-09-25"), inline=None)
    [row] = index.evidence("lab/alpha", "terminal_bench_v4_0")
    assert row.value == 55.8
    kept = index.record(row.record_id)["verification"]
    assert kept["verifier"]["model_family"] == "mistral"


def test_a_later_same_family_verification_does_not_displace_an_independent_one():
    index = _index(record(verifier=MISTRAL, day="2026-09-24"), record(day="2026-09-25"),
                   inline=None)
    [row] = index.evidence("lab/alpha", "terminal_bench_v4_0")
    assert index.record(row.record_id)["verification"]["verifier"]["model_family"] == "mistral"


def test_a_later_same_family_mismatch_still_quarantines():
    index = _index(record(verifier=MISTRAL, day="2026-09-24"),
                   record(outcome="mismatch", day="2026-09-25"), inline=None)
    assert index.evidence("lab/alpha", "terminal_bench_v4_0") == ()


def test_a_same_family_fact_verification_does_not_admit_a_fact():
    from tests.snapshot_records import fact

    f = fact("model", "lab/alpha", "model.context_window", 128000, outcome=None)
    f["verification"] = {**verification("fact", f["id"], "verified"),
                         "collector": CLAUDE, "verifier": SONNET}
    built = build_snapshot(SnapshotInputs(models=[model("lab/alpha", facts=[f])],
                                          sources=SOURCES), gate=False)
    index = load_snapshot_bytes(built.to_bytes(key=None), key=None)
    assert index.fact("lab/alpha", "model.context_window") == UNKNOWN


# --- the verification log and the verifier -------------------------------------------------------


def test_the_log_ignores_a_same_family_verified_record(tmp_path):
    log = verify.VerificationLog(tmp_path)
    log.append(Verification.model_validate(record(verifier=MISTRAL, outcome="mismatch",
                                                  day="2026-09-24")))
    log.append(Verification.model_validate(record(day="2026-09-25")))
    target = "evidence:lab/alpha#terminal_bench_v4_0#55.8"
    assert log.is_quarantined(target)
    assert log.latest()[("evidence", "lab/alpha#terminal_bench_v4_0#55.8")].outcome == "mismatch"


def test_dependent_verifications_are_reported(tmp_path):
    log = verify.VerificationLog(tmp_path)
    log.append(Verification.model_validate(record()))
    log.append(Verification.model_validate(record(eid="lab/beta#x#1", score=1.0)))
    log.append(Verification.model_validate(record(eid="lab/beta#x#1", score=1.0,
                                                  verifier=TABLE)))
    assert [(t.kind, t.id) for t in log.requarantined()] == [
        ("evidence", "lab/alpha#terminal_bench_v4_0#55.8")]


def test_the_verifier_never_asks_a_reader_from_the_collectors_family(store, regions):  # noqa: F811
    llm = _FakeLLM(PROSE, family="anthropic", agent="claude-cli")
    collector = VerificationActor(**CLAUDE)
    result = verify.verify(_prose_claim(store, collector), regions,
                           [*verify.deterministic_extractors(), llm.extractor], today=TODAY)
    assert result.outcome == "skipped"
    assert result.reason == "no_independent_extractor"
    assert llm.calls == []


def test_a_mistral_reader_verifies_a_claude_collected_value(store, regions):  # noqa: F811
    llm = _FakeLLM(PROSE)
    reader = verify.mistral_extractor(complete=llm, cache=verify.LLMCache(store.root / "llm"))
    result = verify.verify(_prose_claim(store, VerificationActor(**CLAUDE)), regions,
                           [*verify.deterministic_extractors(), reader], today=TODAY)
    assert result.outcome == "verified"
    assert result.verification.verifier == VerificationActor(
        agent="ollama", model_family="mistral",
        method="llm-extract:mistral-large:123b-instruct-2411-q4_K_M")
    assert result.verification.independent


# --- the Mistral reader --------------------------------------------------------------------------


class _Response:
    def __init__(self, body: dict) -> None:
        self.body = json.dumps(body).encode()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self) -> bytes:
        return self.body


def _ollama(monkeypatch, content: str) -> list[tuple[urllib.request.Request, float]]:
    seen = []

    def fake_urlopen(request, timeout):
        seen.append((request, timeout))
        return _Response({"model": verify.MISTRAL_MODEL,
                          "message": {"role": "assistant", "content": content}, "done": True})

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    return seen


def test_the_ollama_call_is_deterministic_json_chat(monkeypatch):
    seen = _ollama(monkeypatch, PROSE)
    reply = verify.OllamaChatCompletion()("read this")
    assert json.loads(reply)[0]["value"] == "400,000"
    request, _timeout = seen[0]
    assert request.full_url == "http://100.127.37.30:11434/api/chat"
    body = json.loads(request.data)
    assert body == {
        "model": "mistral-large:123b-instruct-2411-q4_K_M",
        "messages": [{"role": "system", "content": verify.OLLAMA_JSON_MODE},
                     {"role": "user", "content": "read this"}],
        "stream": False,
        "format": "json",
        "options": {"temperature": 0},
    }


def test_json_mode_is_told_to_wrap_the_array_it_cannot_return_bare():
    # Ollama's JSON mode emits one object; left alone, Mistral reports only the first
    # value in a region. The shared prompt is unchanged: the wrapper is a system turn.
    assert '{"values": [' in verify.OLLAMA_JSON_MODE


@pytest.mark.parametrize(("content", "rows"), [
    ('{"values": [{"subject": "A", "quoted_sentence": "q"}]}', [{"subject": "A",
                                                                 "quoted_sentence": "q"}]),
    ('{"subject": "A", "quoted_sentence": "q"}', [{"subject": "A", "quoted_sentence": "q"}]),
    ("{}", []),
    ("[]", []),
])
def test_json_mode_objects_are_read_as_the_requested_array(monkeypatch, content, rows):
    _ollama(monkeypatch, content)
    assert json.loads(verify.OllamaChatCompletion()("p")) == rows


def test_an_ollama_reply_that_is_not_json_is_left_for_the_reader_to_refuse(monkeypatch):
    _ollama(monkeypatch, "about 400k")
    assert verify.OllamaChatCompletion()("p") == "about 400k"


def test_an_unreachable_ollama_is_an_extractor_error(monkeypatch):
    def refuse(request, timeout):
        raise OSError("connection refused")

    monkeypatch.setattr(urllib.request, "urlopen", refuse)
    with pytest.raises(verify.ExtractorError, match="connection refused"):
        verify.OllamaChatCompletion()("p")


def test_the_mistral_reader_stops_at_its_call_budget(monkeypatch):
    _ollama(monkeypatch, "[]")
    complete = verify.OllamaChatCompletion(max_calls=1)
    complete("first")
    with pytest.raises(verify.LLMCallBudgetExceededError):
        complete("second")


def test_readers_do_not_share_cached_replies(tmp_path, store, regions):  # noqa: F811
    claude = _FakeLLM(PROSE)
    mistral = _FakeLLM(PROSE)
    claim = _prose_claim(store, VerificationActor(**TABLE))
    cache = tmp_path / "llm"
    verify.verify(claim, regions, [verify.claude_extractor(
        complete=claude, cache=verify.LLMCache(cache))], today=TODAY)
    verify.verify(claim, regions, [verify.mistral_extractor(
        complete=mistral, cache=verify.LLMCache(cache, namespace=verify.MISTRAL_MODEL))],
        today=TODAY)
    assert len(claude.calls) == 1 and len(mistral.calls) == 1


def test_cli_mistral_reader_uses_an_injected_extractor(tmp_path, store, monkeypatch):  # noqa: F811
    from cli.modelspec import cli as cli_mod

    monkeypatch.setenv("MODELSPEC_SOURCE_CACHE", str(store.root))
    root = _repo(tmp_path, store)
    fake = _FakeLLM(PROSE, family="mistral", agent="ollama")
    monkeypatch.setattr(verify, "mistral_extractor", lambda **kwargs: fake.extractor)
    result = CliRunner().invoke(
        cli_mod.app, ["verify", "--root", str(root), "--llm-reader", "mistral", "--json"])
    assert result.exit_code == 0, result.output
    prose = next(r for r in json.loads(result.output)["results"]
                 if "sol-prose-no-extractor" in r["target"])
    assert prose["outcome"] == "verified"
    assert prose["verifier"]["model_family"] == "mistral"


def test_cli_refuses_an_unknown_reader(tmp_path, store):  # noqa: F811
    from cli.modelspec import cli as cli_mod

    result = CliRunner().invoke(
        cli_mod.app, ["verify", "--root", str(_repo(tmp_path, store)), "--llm-reader", "gpt"])
    assert result.exit_code != 0
    assert "claude, mistral" in result.output
