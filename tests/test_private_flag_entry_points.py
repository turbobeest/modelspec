"""MODEL-491, Codex review 7: every script that consults the counting rule takes an explicit
``--private-data`` flag, off by default. With the flag off, on the public checkout, the script
hands main's rule (``private=False``) to every function that consults it; with the flag, it
hands MODEL-491's. Each case stubs the first function the flag reaches and stops there.
"""

from __future__ import annotations

import importlib
import sys
from types import SimpleNamespace

import pytest


class Reached(BaseException):
    """Stops the script once the stub has seen the flag (a BaseException, so no script's own
    ``except Exception`` catches it)."""


def _stub(seen, key="private"):
    def stub(*args, **kwargs):
        seen.append(kwargs.get(key, False))
        raise Reached

    return stub


def _drafter(seen):
    """``draft_offering`` returns a draft whose ``write`` takes the flag."""
    def draft(*args, **kwargs):
        return SimpleNamespace(write=_stub(seen))

    return draft


# (module, attribute to stub, the stub's factory, argv without the flag)
CASES = [
    ("scripts.data_trust.__main__", "load", _stub, ["data", "--data-dir", "{data}"]),
    ("scripts.price_reread", "run", _stub, []),
    ("scripts.evidence_reread", "run", _stub, ["--source-cache", "{tmp}"]),
    ("scripts.admission_drafter", "draft_packet", _stub,
     ["--data-dir", "{data}", "--model", "lab/alpha"]),
    ("scripts.offering_drafter", "draft_offering", _drafter,
     ["--data-dir", "{data}", "--model", "lab/alpha", "--write", "--cache-dir", "{tmp}"]),
    ("scripts.held_row_grandfather", "missing_hashes", _stub, ["write", "--data-dir", "{data}"]),
    ("scripts.refile_mixed_citations", "plan", _stub,
     ["--data-root", "{data}", "--policy", "{policy}", "--source-cache", "{tmp}",
      "--as-of", "2026-11-27"]),
    ("scripts.file_owner_ruling", "plan", _stub,
     ["--data-dir", "{data}", "--subject", "lab/alpha", "--facet", "model.context_window",
      "--value", "1", "--state", "known", "--ruled-by", "jamie", "--ruled-at", "2026-11-27",
      "--ticket", "MODEL-491", "--source", "src", "--basis", "counts only"]),
    ("scripts.cited_offering", "cited_change", _stub,
     ["--data-dir", "{data}", "--subject", "lab/alpha", "--facet", "model.context_window",
      "--source", "src"]),
    ("scripts.cited_reading", "run", _stub,
     ["--data-dir", "{data}", "--benchmark", "gpqa", "--source", "src"]),
    ("scripts.premier_slice1", "build", _stub, ["--data-dir", "{data}"]),
    ("scripts.accuracy", "run_profile", lambda seen: _stub(seen, "private_data"), []),
    ("scripts.recall_run", "run", _stub, []),
]


@pytest.mark.parametrize("module, attribute, factory, argv", CASES,
                         ids=[case[0].split(".")[-1].replace("__main__", "data_trust")
                              for case in CASES])
def test_the_flag_is_off_by_default_and_on_only_when_given(module, attribute, factory, argv,
                                                           tmp_path, monkeypatch):
    data = tmp_path / "data"
    for name in ("models", "benchmarks", "verification", "registry", "premier"):
        (data / name).mkdir(parents=True)
    (data / "premier" / "slice-1.yaml").write_text("models: []\n")
    from decision import retention

    script = importlib.import_module(module)
    monkeypatch.setattr(retention, "POLICY_PATH", retention.POLICY_PATH)
    argv = [a.format(data=data, tmp=tmp_path, policy=retention.POLICY_PATH) for a in argv]
    monkeypatch.delenv("MODELSPEC_DATA_DIR", raising=False)
    seen: list[bool] = []
    monkeypatch.setattr(script, attribute, factory(seen))
    if hasattr(script, "default_readers"):
        # The gate scripts build their reader CLIs before the gate runs. CI has no reader CLI and
        # never runs a paid one: use the stub readers the gate tests use.
        from tests.test_retained_agreement import pair

        monkeypatch.setattr(script, "default_readers", lambda *args, **kwargs: pair())
    for flag in ([], ["--private-data"]):
        monkeypatch.setattr(sys, "argv", [module, *argv, *flag])
        try:
            script.main() if module == "scripts.premier_slice1" else script.main([*argv, *flag])
        except Reached:
            pass
    assert seen == [False, True], seen


def test_the_gate_ranks_by_mains_rule_unless_its_caller_states_private(tmp_path):
    # A retired row that verified after a mismatch lifts the hold under main's rule, the gate's
    # default; only an explicit statement (an entry point's ``private`` argument, or
    # ``stating_private``) retires it, so the mismatch holds.
    import json

    from decision.cited_change import VERIFICATION_LOG, quarantine_rows, stating_private

    from tests.snapshot_records import verification

    fid, value = "lab/alpha#model.context_window", 128000
    mismatch = verification("fact", fid, "mismatch", day="2026-10-01", value=value)
    proof = verification("fact", fid, "verified", day="2026-10-02", value=value)
    proof["method"] = "retained-source-proof@1"
    proof["verifier"] = {**proof["verifier"], "method": "retained-source-proof@1"}
    (tmp_path / VERIFICATION_LOG).parent.mkdir(parents=True)
    (tmp_path / VERIFICATION_LOG).write_text(
        "".join(json.dumps(r) + "\n" for r in (mismatch, proof)))
    fact = {"facet": "model.context_window", "value": value, "state": "known"}
    assert quarantine_rows((fid,), fact, tmp_path) == []  # main's rule: the proof verifies
    with stating_private(True):
        assert [row["outcome"] for _key, row in quarantine_rows((fid,), fact, tmp_path)] \
            == ["mismatch"]
    assert quarantine_rows((fid,), fact, tmp_path) == []  # the statement ends with the block
