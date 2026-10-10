"""The Worker gets its tier table from the bundle, not a text var.

Cloudflare caps a Worker text var at 5.1 kB (code 10054). Pricing v2 took the
compact tier table past that, so `TIER_POLICY` as a `--var` failed every
deploy of f1bfbdbc. `vendor.py` now embeds the table as `tier_policy.py`.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKER = REPO_ROOT / "api" / "worker"
for path in (str(REPO_ROOT), str(WORKER / "src")):
    if path not in sys.path:
        sys.path.insert(0, path)

import access_config  # noqa: E402

#: Cloudflare's limit is 5.1 kB. Anything passed as a --var keeps this headroom.
TEXT_VAR_HEADROOM_BYTES = 4800


def _vendor():
    spec = importlib.util.spec_from_file_location("vendor_under_test", WORKER / "vendor.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _workflows() -> dict[str, str]:
    return {p.name: p.read_text(encoding="utf-8")
            for p in (REPO_ROOT / ".github" / "workflows").glob("*.yml")}


def test_the_bundle_embeds_the_committed_tier_table(tmp_path):
    _vendor().write_tier_policy(tmp_path)
    namespace: dict = {}
    exec((tmp_path / "tier_policy.py").read_text(encoding="utf-8"), namespace)
    committed = json.loads((WORKER / "tiers.json").read_text(encoding="utf-8"))
    assert json.loads(namespace["TEXT"]) == committed
    assert access_config.policy_from_json(namespace["TEXT"]).to_json() == \
        access_config.load_policy(path=WORKER / "tiers.json").to_json()


def test_the_isolate_reads_the_bundled_table_when_no_file_is_reachable(monkeypatch, tmp_path):
    table = json.loads((WORKER / "tiers.json").read_text(encoding="utf-8"))
    table["tiers"]["free"]["daily_limit"] = 7
    monkeypatch.setattr(access_config, "DEFAULT_POLICY_PATH", tmp_path / "absent.json")
    monkeypatch.setitem(sys.modules, "tier_policy",
                        types.SimpleNamespace(TEXT=json.dumps(table)))
    policy = access_config.load_policy(types.SimpleNamespace())
    assert policy.tier("free").daily_limit == 7


def test_no_bundle_and_no_file_still_refuses(monkeypatch, tmp_path):
    monkeypatch.setattr(access_config, "DEFAULT_POLICY_PATH", tmp_path / "absent.json")
    monkeypatch.setitem(sys.modules, "tier_policy", None)
    try:
        access_config.load_policy(types.SimpleNamespace())
    except access_config.PolicyError as exc:
        assert "no tier table" in str(exc)
    else:
        raise AssertionError("a missing table must refuse")


def test_an_explicit_path_never_falls_back_to_the_bundle(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "tier_policy",
                        types.SimpleNamespace(TEXT=(WORKER / "tiers.json").read_text()))
    try:
        access_config.load_policy(path=tmp_path / "absent.json")
    except access_config.PolicyError:
        pass
    else:
        raise AssertionError("an explicit path that is missing must refuse")


def test_no_deploy_passes_the_tier_table_as_a_text_var():
    for name, text in _workflows().items():
        assert "TIER_POLICY:" not in text, name


def test_every_text_var_built_from_a_repo_file_keeps_headroom():
    """A `--var NAME:$(jq -c . FILE)` must stay under 4.8 kB, short of the 5.1 kB cap."""
    pattern = re.compile(r'--var "(\w+):\$\(jq -c \. ([\w./-]+)\)"')
    for name, text in _workflows().items():
        for var, rel in pattern.findall(text):
            source = WORKER / rel
            if not source.is_file():
                source = REPO_ROOT / rel
            compact = json.dumps(json.loads(source.read_text(encoding="utf-8")),
                                 separators=(",", ":"), ensure_ascii=False)
            assert len(compact.encode("utf-8")) < TEXT_VAR_HEADROOM_BYTES, (name, var)
