"""Offload-aware fit (MODEL-26 phase B): fit states, the offload formula, and `fit --host`."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from cli.modelspec import offline
from pipeline import hosts as H
from pipeline.hardware import (
    BANDWIDTH_EFFICIENCY, QUANT_PREFERENCE, WORKING_ALLOWANCE, predicted_decode_tps, weights_gb,
)

ROOT = Path(__file__).resolve().parent.parent
#: Hosts present before any later additions; a deletion must fail the tests.
ORIGINAL_HOSTS = {"amd_ryzen_9_9950x_am5", "apple_mac_studio_m5_max"}


def _host_ids_on_disk() -> set[str]:
    return {p.stem for p in (ROOT / "hosts").glob("*.yaml") if p.name != "_schema.yaml"}


def _host(unified: bool = False, ram: float | None = 64.0, bandwidth: float | None = 100.0,
          hid: str = "synthetic_host") -> H.Host:
    return H.Host(id=hid, display_name=hid, kind="platform", unified=unified, hardware_ref=None,
                  capacity_max_gb=ram, bandwidth_gb_s=bandwidth, raw={"id": hid})


# ── loading ─────────────────────────────────────────────────────────────────

def test_hosts_load_and_validate():
    hosts = {h.id: h for h in H.load_hosts(ROOT)}
    assert set(hosts) == _host_ids_on_disk()
    assert ORIGINAL_HOSTS <= set(hosts)
    assert hosts["amd_ryzen_9_9950x_am5"].bandwidth_gb_s == 89.6  # 2-DIMM rated, as-is
    assert hosts["apple_mac_studio_m5_max"].unified


def test_invalid_host_profile_is_rejected():
    raw = dict(H.load_hosts(ROOT)[0].raw)
    raw["field_sources"] = {}
    with pytest.raises(ValueError, match="unsourced"):
        H.validate(raw, "x.yaml")


# ── fit states on a synthetic device and host ───────────────────────────────

def test_three_fit_states():
    acc = 24.0  # usable 18 GB after the working allowance
    host = _host(ram=64.0)  # C_host = 56 GB
    c_host = H.host_capacity_gb(host)
    assert c_host == 64.0 - H.OS_RESERVE_GB
    assert H.fit_state(10.0, acc, c_host, False) == H.FIT_ACCELERATOR
    assert H.fit_state(40.0, acc, c_host, False) == H.FIT_OFFLOAD
    assert H.fit_state(100.0, acc, c_host, False) == H.FIT_NONE
    f = H.offload_fraction(40.0, acc)
    assert f == pytest.approx((40.0 + WORKING_ALLOWANCE * acc - acc) / 40.0)


def test_host_ram_override_moves_the_boundary():
    host = _host(ram=256.0)
    assert H.host_capacity_gb(host, host_ram_gb=16.0) == 8.0
    # W + A = 40 + 6 = 46 GB; 24 + 8 = 32 GB is not enough, 24 + 248 is.
    assert H.fit_state(40.0, 24.0, H.host_capacity_gb(host, 16.0), False) == H.FIT_NONE
    assert H.fit_state(40.0, 24.0, H.host_capacity_gb(host), False) == H.FIT_OFFLOAD


def test_unified_host_has_no_offload():
    host = _host(unified=True, ram=128.0)
    assert H.host_capacity_gb(host) == 0.0
    assert H.fit_state(40.0, 24.0, H.host_capacity_gb(host), True) == H.FIT_NONE
    a = H.assess(total_params=70e9, active_params=None, model_type="llm-chat",
                 accelerator_gb=24.0, accelerator_bandwidth=1000.0, host=host)
    assert a["fit_state"] == H.FIT_NONE


# ── the formula ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("bandwidth", [89.6, 273.0, 546.0, 1792.0])
@pytest.mark.parametrize("params", [6e5, 3.2e9, 8e9, 70e9])
@pytest.mark.parametrize("quant", QUANT_PREFERENCE)
def test_f_zero_is_exactly_todays_roofline(bandwidth, params, quant):
    assert H.offload_decode_tps(bandwidth, 50.0, params, quant, 0.0) == \
        predicted_decode_tps(bandwidth, params, quant)
    # And the unshortcut formula agrees to the rounding.
    per = weights_gb(params, quant)
    raw = BANDWIDTH_EFFICIENCY / (per / bandwidth + 0.0 * per / 50.0)
    assert round(raw, 1) == predicted_decode_tps(bandwidth, params, quant)


def test_offload_formula_matches_the_design_doc():
    p, q, f = 70e9, "q4", 0.5
    per = weights_gb(p, q)
    expected = round(BANDWIDTH_EFFICIENCY / ((1 - f) * per / 1792 + f * per / 89.6), 1)
    assert H.offload_decode_tps(1792, 89.6, p, q, f) == expected
    assert expected < predicted_decode_tps(1792, p, q)


def test_offload_tps_is_null_for_non_token_models():
    host = _host(ram=256.0)
    kwargs = dict(total_params=40e9, active_params=None, accelerator_gb=16.0,
                  accelerator_bandwidth=500.0, host=host)
    chat = H.assess(model_type="llm-chat", **kwargs)
    enc = H.assess(model_type="vision-encoder", **kwargs)
    assert chat["fit_state"] == enc["fit_state"] == H.FIT_OFFLOAD
    assert chat["predicted_decode_tps"] is not None
    assert chat["predicted_decode_tps_basis"] == H.BASIS_OFFLOAD
    assert enc["predicted_decode_tps"] is None
    assert enc["predicted_decode_tps_basis"] is None


# ── export ──────────────────────────────────────────────────────────────────

def test_hosts_json_is_exported(tmp_path):
    counts = H.write_export(tmp_path, H.load_hosts(ROOT), {"commit": "abc"})
    payload = json.loads((tmp_path / "hosts.json").read_text())
    on_disk = _host_ids_on_disk()
    assert counts == {"hosts": len(on_disk)} and payload["count"] == len(on_disk)
    assert payload["os_reserve_gb"] == H.OS_RESERVE_GB
    assert {h["id"] for h in payload["hosts"]} == on_disk
    assert ORIGINAL_HOSTS <= on_disk


def test_build_writes_hosts_json():
    assert "host_layer.write_export(" in (ROOT / "pipeline" / "build.py").read_text()


def test_graph_host_node_only_for_unified():
    from schema.graph import CollectingSink
    sink = CollectingSink()
    unified = H.Host(id="u", display_name="u", kind="system", unified=True,
                     hardware_ref="apple_m4_max", capacity_max_gb=64, bandwidth_gb_s=546, raw={})
    assert H.add_to_graph(sink, [unified, _host()]) == 1
    assert [e["type"] for e in sink.edges] == ["HOSTS"]


# ── the CLI ─────────────────────────────────────────────────────────────────

#: Captured from the pre-MODEL-26-phase-B CLI (origin/main e09e009) on this fixture.
GOLDEN_HUMAN = ("  ~   40.0 tok/s  Chat Model\n       n/a tok/s  Vision Encoder\n\n"
                "predicted from memory bandwidth, not measured; n/a means the weights fit "
                "but the model does not decode tokens\n")
GOLDEN_JSON = ('{"schema_version": "1.0", "command": "fit", "freshness": {}, "result": '
               '[{"model_id": "a/chat", "display_name": "Chat Model", "predicted_decode_tps": '
               '40.0, "prediction_basis": "computed, not measured"}, {"model_id": "b/vision", '
               '"display_name": "Vision Encoder", "predicted_decode_tps": null, '
               '"prediction_basis": "computed, not measured"}]}')


def _fixture(directory: Path, with_hosts: bool = True) -> None:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_cli_snapshot_fixtures", Path(__file__).with_name("test_cli_snapshot.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module._write_fit_fixture(directory)
    path = directory / "snapshot.json"
    payload = json.loads(path.read_text())
    cands = payload["data"]["candidates"]["candidates"]
    for c in cands:
        c["total_parameters"] = 1e9
    base = dict(cands[0])
    # gpu: 24 GB, 1000 GB/s. 40B at q4 = 20 GB + 6 GB allowance > 24 GB: offload.
    cands.append(dict(base, model_id="c/big", display_name="Big Chat", model_type="llm-chat",
                      fits={}, total_parameters=40e9, active_parameters=None))
    cands.append(dict(base, model_id="d/bigenc", display_name="Big Encoder",
                      model_type="vision-encoder", fits={}, total_parameters=40e9))
    cands.append(dict(base, model_id="e/huge", display_name="Huge", model_type="llm-chat",
                      fits={}, total_parameters=2e12))
    if with_hosts:
        payload["data"]["hosts"] = {"hosts": [h.raw for h in H.load_hosts(ROOT)]}
    path.write_text(json.dumps(payload))


def _invoke(cache: Path, args: list[str], monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MODELSPEC_CACHE", str(cache))
    return CliRunner().invoke(offline.app, args)


def test_fit_without_host_is_byte_identical(tmp_path, monkeypatch):
    _fixture(tmp_path)
    human = _invoke(tmp_path, ["fit", "gpu"], monkeypatch)
    assert human.exit_code == 0 and human.stdout == GOLDEN_HUMAN
    raw = _invoke(tmp_path, ["fit", "gpu", "--json"], monkeypatch)
    data = json.loads(raw.stdout)
    data["freshness"] = {}
    assert json.dumps(data) == GOLDEN_JSON


def test_include_offload_requires_host(tmp_path, monkeypatch):
    _fixture(tmp_path)
    for args in (["fit", "gpu", "--include-offload"], ["fit", "gpu", "--host-ram", "64"]):
        r = _invoke(tmp_path, args, monkeypatch)
        assert r.exit_code == offline.EXIT_ERROR
        assert "requires --host" in r.stderr


def test_unknown_host_is_an_error(tmp_path, monkeypatch):
    _fixture(tmp_path)
    r = _invoke(tmp_path, ["fit", "gpu", "--host", "nope", "--json"], monkeypatch)
    assert r.exit_code == offline.EXIT_ERROR
    assert "unknown host" in json.loads(r.stderr)["error"]["message"]


def test_snapshot_without_hosts_is_an_error(tmp_path, monkeypatch):
    _fixture(tmp_path, with_hosts=False)
    r = _invoke(tmp_path, ["fit", "gpu", "--host", "amd_ryzen_9_9950x_am5"], monkeypatch)
    assert r.exit_code == offline.EXIT_ERROR and "no host profiles" in r.stderr


def test_offload_tier_follows_accelerator_rows(tmp_path, monkeypatch):
    _fixture(tmp_path)
    r = _invoke(tmp_path, ["fit", "gpu", "--host", "amd_ryzen_9_9950x_am5",
                           "--include-offload", "--json"], monkeypatch)
    assert r.exit_code == 0, r.stderr
    rows = json.loads(r.stdout)["result"]
    states = [x["fit_state"] for x in rows]
    assert states == ["accelerator", "accelerator", "offload", "offload"]
    assert [x["model_id"] for x in rows] == ["a/chat", "b/vision", "c/big", "d/bigenc"]
    assert all(x["host_id"] == "amd_ryzen_9_9950x_am5" for x in rows)
    assert rows[0]["predicted_decode_tps_basis"] == "accelerator-roofline"
    assert rows[2]["predicted_decode_tps_basis"] == "offload-roofline"
    assert 0 < rows[2]["offload_fraction"] < 1
    assert rows[3]["predicted_decode_tps"] is None  # non-token
    human = _invoke(tmp_path, ["fit", "gpu", "--host", "amd_ryzen_9_9950x_am5",
                               "--include-offload"], monkeypatch).stdout
    assert human.index("Vision Encoder") < human.index("offload tier") < human.index("Big Chat")


def test_host_without_include_offload_adds_fields_only(tmp_path, monkeypatch):
    _fixture(tmp_path)
    r = _invoke(tmp_path, ["fit", "gpu", "--host", "amd_ryzen_9_9950x_am5", "--json"], monkeypatch)
    rows = json.loads(r.stdout)["result"]
    assert [x["fit_state"] for x in rows] == ["accelerator", "accelerator"]
    assert rows[0]["offload_fraction"] == 0.0


def test_unified_host_shows_no_offload_tier(tmp_path, monkeypatch):
    _fixture(tmp_path)
    r = _invoke(tmp_path, ["fit", "gpu", "--host", "apple_mac_studio_m5_max",
                           "--include-offload", "--json"], monkeypatch)
    assert {x["fit_state"] for x in json.loads(r.stdout)["result"]} == {"accelerator"}


def test_host_ram_can_remove_the_offload_tier(tmp_path, monkeypatch):
    _fixture(tmp_path)
    r = _invoke(tmp_path, ["fit", "gpu", "--host", "amd_ryzen_9_9950x_am5",
                           "--include-offload", "--host-ram", "8", "--json"], monkeypatch)
    assert "offload" not in {x["fit_state"] for x in json.loads(r.stdout)["result"]}
