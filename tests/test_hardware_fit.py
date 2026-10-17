"""MODEL-287: a concrete workload is measured, estimated, or undetermined."""

from __future__ import annotations

import copy
from datetime import date

import pytest
import yaml

from decision.excluded import ExcludedSources
from decision.snapshot import SnapshotBuildError, SnapshotInputs, build_snapshot, load_built_snapshot, load_snapshot_bytes
from tests.snapshot_records import SOURCES, fact, model, verification

MODEL = "lab/hardware-model"
SKU = "fixture_gpu"
REQUEST = {"model": MODEL, "sku": SKU, "device_count": 1, "runtime": "fixture-runtime@1",
           "quantisation": "fixture-q4", "batch": 2, "context": 1024}
ALL_SOURCES = {**SOURCES, "hardware-spec": "https://hardware.example/spec",
               "run-source": "https://runtime.example/retained-run"}


def number(value, name):
    return {"value": value, "record_id": f"hardware-input:{name}", "source_ids": ["run-source"]}


def resign(row):
    row.pop("verification", None)
    row["verification"] = verification("fact", row["id"], value=copy.deepcopy(row))
    return row


def hardware_fit_record(status="estimated", **updates):
    row = {"id": "hardware-fit:fixture", "status": status, **REQUEST,
           "memory_bytes_per_device": 24_000_000_000, "observed_at": "2026-09-20",
           "source_ids": ["run-source"]}
    if status == "estimated":
        row["per_device"] = [{"weights_bytes": number(4_000_000_000, "weights"),
                              "kv_bytes_per_token": number(100_000, "kv"),
                              "runtime_headroom_bytes": number(1_000_000_000, "headroom")}]
    else:
        row.update(measured_fit=True, measured_memory_bytes=[number(5_204_800_000, "observed")])
    row.update(updates)
    return resign(row)


def fixture_snapshot(records=None, *, variants=None, verifications=(), sources=None, guard=None,
                     context=8192, known_context=True, built=False, models=None, premier=None,
                     openness="open_weights", single_device_fit=True):
    device = {"id": SKU, "memory": {"capacity_gb": 24, "bandwidth_gb_s": 500},
              "sources": [ALL_SOURCES["hardware-spec"]], "figures_are": "vendor-specification",
              "verified_at": "2026-09-20"}
    if variants:
        device["memory"]["capacity_options_gb"] = variants
    if not single_device_fit:
        device.update(single_device_fit=False, single_device_fit_reason="This SKU uses several memory pools.")
    facts = [fact("model", MODEL, "model.weights_openness", openness,
                  state="unknown" if openness is None else "known")]
    if known_context:
        facts.append(fact("model", MODEL, "model.context_window", context))
    compiled = build_snapshot(SnapshotInputs(
        models=[model(MODEL, facts=facts)] if models is None else models,
        hardware=[device], sources=sources or ALL_SOURCES,
        hardware_fit_records=[hardware_fit_record()] if records is None else records,
        verifications=verifications,
    ), gate=False, premier=premier, as_of=date(2026, 10, 10), guard=guard)
    if built:
        return compiled
    return load_built_snapshot(compiled, include_archive=False, source="hardware fit fixture")


def assess(payload=None, snapshot=None, **kwargs):
    from decision.hardware_fit import HardwareFitResponse, check

    status, body = check(REQUEST if payload is None else payload,
                         fixture_snapshot() if snapshot is None else snapshot, **kwargs)
    if status == 200:
        HardwareFitResponse.model_validate(body)
    return status, body


def test_estimated_workload_reports_literal_formula_inputs_and_never_asserts_fit():
    status, body = assess()
    assert status == 200
    assert (body["status"], body["estimated_fit"], body["margin_bytes"]) == (
        "estimated", "likely", 18_795_200_000)
    assert body["per_device"][0]["kv_cache_bytes"] == 204_800_000
    assert body["per_device"][0]["required_bytes"] == 5_204_800_000
    assert body["per_device"][0]["weights_bytes"] == number(4_000_000_000, "weights")
    assert body["assumptions"]
    assert "fits" not in body and "measured_fit" not in body
    assert {s["id"] for s in body["sources"]} == {"run-source", "hardware-spec", "src-lab-docs"}


def test_measured_requires_exact_workload_and_cites_retained_measurement():
    status, body = assess(snapshot=fixture_snapshot([hardware_fit_record("measured")]))
    assert status == 200
    assert (body["status"], body["measured_fit"], body["measurement"]["record_id"]) == (
        "measured", True, "hardware-fit:fixture")
    assert body["measurement"]["memory_bytes_per_device"] == 24_000_000_000
    _, changed = assess({**REQUEST, "batch": 1}, fixture_snapshot([hardware_fit_record("measured")]))
    assert changed["status"] == "undetermined"


@pytest.mark.parametrize("field", ["model", "sku", "device_count", "runtime", "quantisation", "batch", "context"])
def test_missing_request_input_is_undetermined(field):
    request = {k: v for k, v in REQUEST.items() if k != field}
    status, body = assess(request)
    assert status == 200 and body["status"] == "undetermined"
    assert field in {row["input"] for row in body["missing"]}


@pytest.mark.parametrize("update,missing", [({"sku": "unknown"}, "sku"),
                                          ({"model": "unknown"}, "model"),
                                          ({"quantisation": "no-source"}, "quantisation"),
                                          ({"context": 8193}, "context")])
def test_adversarial_questions_abstain(update, missing):
    status, body = assess({**REQUEST, **update})
    assert status == 200 and body["status"] == "undetermined"
    assert missing in {row["input"] for row in body["missing"]}


@pytest.mark.parametrize("update", [{"batch": True}, {"context": 1.5}, {"device_count": 0},
                                    {"memory": float("inf")}, {"memory": "24"},
                                    {"runtime": "x" * 513}, {"surprise": True}])
def test_invalid_request_types_and_unknown_fields_are_bad_requests(update):
    status, body = assess({**REQUEST, **update})
    assert status == 400 and body["error"]["code"] == "invalid_request"


def test_multi_device_estimate_uses_each_allocation_without_pooling():
    row = hardware_fit_record(device_count=2)
    row["per_device"].append({"weights_bytes": number(25_000_000_000, "weights-2"),
                              "kv_bytes_per_token": number(100_000, "kv-2"),
                              "runtime_headroom_bytes": number(1_000_000_000, "headroom-2")})
    resign(row)
    status, body = assess({**REQUEST, "device_count": 2}, fixture_snapshot([row]))
    assert status == 200
    assert (body["estimated_fit"], body["margin_bytes"]) == ("unlikely", -2_204_800_000)
    assert [device["margin_bytes"] for device in body["per_device"]] == [18_795_200_000, -2_204_800_000]


def test_memory_variants_need_override_and_measurements_match_effective_capacity():
    status, body = assess(snapshot=fixture_snapshot(variants=[16, 24]))
    assert status == 200 and body["status"] == "undetermined"
    assert "memory" in {row["input"] for row in body["missing"]}
    _, body = assess({**REQUEST, "memory": 24}, fixture_snapshot(variants=[16, 24]))
    assert (body["status"], body["margin_bytes"]) == ("estimated", 18_795_200_000)
    _, body = assess({**REQUEST, "memory": 16}, fixture_snapshot([hardware_fit_record("measured")]))
    assert body["status"] == "undetermined"


@pytest.mark.parametrize("bad", ["unknown_source", "unverified", "same_family", "mutated", "mismatch", "excluded"])
def test_untrusted_parameters_cannot_become_estimates(bad):
    row = hardware_fit_record()
    sources = dict(ALL_SOURCES)
    logged = []
    guard = None
    if bad == "unknown_source":
        row["per_device"][0]["weights_bytes"]["source_ids"] = ["missing"]
        resign(row)
    elif bad == "unverified":
        row.pop("verification")
    elif bad == "same_family":
        row["verification"]["verifier"]["model_family"] = "family-a"
    elif bad == "mutated":
        row["per_device"][0]["weights_bytes"]["value"] = 1
    elif bad == "mismatch":
        value = {k: v for k, v in row.items() if k != "verification"}
        logged = [verification("fact", row["id"], "mismatch", "2026-09-21", value=value)]
    elif bad == "excluded":
        sources["run-source"] = "https://excluded.example/run"
        guard = ExcludedSources(hosts=("excluded.example",))
    status, body = assess(snapshot=fixture_snapshot([row], sources=sources,
                                                  verifications=logged, guard=guard))
    assert status == 200 and body["status"] == "undetermined"


def test_snapshot_round_trip_retains_inputs_and_rejects_stale_snapshot():
    snapshot = fixture_snapshot()
    record = snapshot.hardware_fit_records(MODEL, SKU)[0]
    assert snapshot.record(record["id"])["verification"]["outcome"] == "verified"
    assert snapshot.record("hardware-input:weights")["value"] == 4_000_000_000
    status, body = assess(snapshot=snapshot, expected_snapshot="different")
    assert status == 409 and body["error"]["code"] == "snapshot_changed"


def test_estimate_arithmetic_overflow_abstains_without_nonfinite_numbers():
    row = hardware_fit_record()
    row["per_device"][0]["kv_bytes_per_token"]["value"] = 1e308
    resign(row)
    status, body = assess(snapshot=fixture_snapshot([row]))
    assert status == 200 and body["status"] == "undetermined"
    assert "kv_cache_bytes" in {item["input"] for item in body["missing"]}


def test_unrelated_inline_verification_cannot_admit_a_workload_record():
    row = hardware_fit_record()
    row["verification"]["target"]["id"] = "a-different-record"
    status, body = assess(snapshot=fixture_snapshot([row]))
    assert status == 200 and body["status"] == "undetermined"


def test_missing_runtime_headroom_and_missing_context_maximum_abstain():
    row = hardware_fit_record()
    del row["per_device"][0]["runtime_headroom_bytes"]
    resign(row)
    _, body = assess(snapshot=fixture_snapshot([row]))
    assert body["status"] == "undetermined"
    assert "runtime_headroom_bytes" in {item["input"] for item in body["missing"]}
    _, body = assess(snapshot=fixture_snapshot(known_context=False))
    assert body["status"] == "undetermined"
    assert "context" in {item["input"] for item in body["missing"]}


def test_conflicting_measurements_abstain_and_negative_measurement_is_measured():
    positive = hardware_fit_record("measured")
    negative = hardware_fit_record("measured", id="hardware-fit:negative", measured_fit=False,
                                   measured_memory_bytes=[number(25_000_000_000, "negative")])
    _, body = assess(snapshot=fixture_snapshot([negative]))
    assert (body["status"], body["measured_fit"]) == ("measured", False)
    _, body = assess(snapshot=fixture_snapshot([positive, negative]))
    assert body["status"] == "undetermined"
    assert "measurement" in {item["input"] for item in body["missing"]}


@pytest.mark.parametrize("conflict", ["value", "sources"])
def test_input_ids_cannot_overwrite_another_retained_input(conflict):
    first = hardware_fit_record()
    second = hardware_fit_record(id="hardware-fit:second", context=2048)
    if conflict == "value":
        second["per_device"][0]["weights_bytes"]["value"] = 1
    else:
        second["per_device"][0]["weights_bytes"]["source_ids"] = ["src-lab-docs"]
    resign(second)
    with pytest.raises(SnapshotBuildError, match="duplicate record ID hardware-input:weights"):
        fixture_snapshot([first, second])


def test_hardware_fit_survives_signed_snapshot_bytes_and_quotes_verifier():
    compiled = fixture_snapshot(built=True)
    snapshot = load_snapshot_bytes(compiled.to_bytes(key=b"hardware-test"), key=b"hardware-test")
    _, body = assess(snapshot=snapshot)
    assert (body["status"], body["margin_bytes"]) == ("estimated", 18_795_200_000)
    assert body["verification"]["verifier"]["agent"] == "verifier-b"


def test_optional_curated_file_is_collected_without_adding_any_public_data(tmp_path):
    from decision.snapshot import collect_repo

    assert collect_repo(tmp_path).hardware_fit_records == []
    fit_path = tmp_path / "hardware" / "fit" / "records.yaml"
    fit_path.parent.mkdir(parents=True)
    row = hardware_fit_record()
    fit_path.write_text(yaml.safe_dump([row]))
    assert collect_repo(tmp_path).hardware_fit_records == [row]
    fit_path.write_text("not: a list\n")
    with pytest.raises(SnapshotBuildError, match="must be a list of objects"):
        collect_repo(tmp_path)


def test_latest_logged_verification_can_admit_a_row_without_inline_verification():
    row = hardware_fit_record()
    logged = row.pop("verification")
    _, body = assess(snapshot=fixture_snapshot([row], verifications=[logged]))
    assert (body["status"], body["margin_bytes"]) == ("estimated", 18_795_200_000)


def test_hardware_fit_input_order_does_not_change_the_signed_snapshot():
    first = hardware_fit_record()
    second = hardware_fit_record(id="hardware-fit:second", context=2048)
    for name, value in second["per_device"][0].items():
        value["record_id"] = f"hardware-fit:second#{name}"
    resign(second)
    a = fixture_snapshot([first, second], built=True)
    b = fixture_snapshot([second, first], built=True)
    assert a.snapshot_id == b.snapshot_id


def test_sourced_numbers_are_shared_across_independently_verified_workloads():
    first = hardware_fit_record()
    second = hardware_fit_record(id="hardware-fit:second-workload", context=2048,
                                 observed_at="2026-09-21")
    compiled = fixture_snapshot([first, second], built=True)
    snapshot = load_snapshot_bytes(compiled.to_bytes(key=b"hardware-test"), key=b"hardware-test")
    _, original = assess(snapshot=snapshot)
    _, changed = assess({**REQUEST, "context": 2048}, snapshot)
    assert (original["status"], original["margin_bytes"]) == ("estimated", 18_795_200_000)
    assert (changed["status"], changed["margin_bytes"]) == ("estimated", 18_590_400_000)
    assert snapshot.record("hardware-input:weights") == {
        "id": "hardware-input:weights", "kind": "hardware_fit_input", "value": 4_000_000_000,
        "sources": [{"source_id": "run-source"}],
        "verified_by_records": ["hardware-fit:fixture", "hardware-fit:second-workload"],
    }
    assert original["verification"]["target"]["id"] == "hardware-fit:fixture"
    assert changed["verification"]["target"]["id"] == "hardware-fit:second-workload"
    reversed_order = fixture_snapshot([second, first], built=True)
    assert compiled.snapshot_id == reversed_order.snapshot_id


def test_shared_number_provenance_excludes_out_of_lineup_parent_records():
    first = hardware_fit_record()
    second = hardware_fit_record(id="hardware-fit:hidden", model="lab/hidden")
    compiled = fixture_snapshot([first, second], models=[model(MODEL), model("lab/hidden")],
                                premier=[MODEL], built=True)
    snapshot = load_snapshot_bytes(compiled.to_bytes(key=b"hardware-test"), key=b"hardware-test")
    _, body = assess(snapshot=snapshot)
    assert (body["status"], body["margin_bytes"]) == ("estimated", 18_795_200_000)
    assert snapshot.record("hardware-input:weights")["verified_by_records"] == ["hardware-fit:fixture"]
    assert "hardware-fit:hidden" not in compiled.content["record_table"]["rows"]
    assert [row["id"] for row in compiled.content["hardware_fit_records"]] == ["hardware-fit:fixture"]


@pytest.mark.parametrize("openness,single_pool", [("closed_weights", True), (None, True),
                                                 ("open_weights", False)])
def test_exact_measurement_does_not_depend_on_legacy_estimate_prerequisites(openness, single_pool):
    snapshot = fixture_snapshot([hardware_fit_record("measured")], openness=openness,
                                single_device_fit=single_pool)
    if openness is None:
        assert snapshot.fact(MODEL, "model.weights_openness").state == "unknown"
    status, body = assess(snapshot=snapshot)
    assert status == 200
    assert body["status"] == "measured"
    assert (body["status"], body["measured_fit"], body["measurement"]["record_id"]) == (
        "measured", True, "hardware-fit:fixture")


@pytest.mark.parametrize("openness,single_pool,missing", [("closed_weights", True, "model"),
                                                         (None, True, "model"),
                                                         ("open_weights", False, "sku")])
def test_estimates_keep_their_openness_and_single_pool_guards(openness, single_pool, missing):
    snapshot = fixture_snapshot(openness=openness, single_device_fit=single_pool)
    status, body = assess(snapshot=snapshot)
    assert status == 200 and body["status"] == "undetermined"
    assert missing in {item["input"] for item in body["missing"]}
