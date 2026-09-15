"""The host layer (MODEL-26 phase B): offload-aware fit for a (model, device, host).

A host is the machine around an accelerator (`hosts/*.yaml`, see
docs/host-layer.md). For a discrete host, weights that do not fit in
accelerator memory can spill to system RAM. Decode is then bounded by the
slower pool, so the answer is "fits, slowly", not "does not fit".

Three fit states:

* `accelerator`: `W + A <= C_acc`, today's `fits: true`.
* `offload`: not `accelerator`, `W + A <= C_acc + C_host`, and the host is not
  unified. It carries `offload_fraction = (W + A - C_acc) / W`.
* `does_not_fit`: neither. A unified host has `C_host = 0` by definition, so
  its fit is two-state.

`W` is weights at the quant, `A = WORKING_ALLOWANCE * C_acc`, and
`C_host = host RAM - OS_RESERVE_GB`. Host RAM is the profile's
`capacity_max_gb` unless the caller states what this machine has
(`--host-ram`).

Everything here is computed, never measured. The offload formula assumes
layer-split offload with the CPU not compute-bound; see "Known wrong" in
docs/host-layer.md.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from pipeline.hardware import (
    BANDWIDTH_EFFICIENCY,
    QUANT_PREFERENCE,
    WORKING_ALLOWANCE,
    is_token_generating,
    predicted_decode_tps,
    weights_gb,
)

#: RAM held back for the OS and everything that is not model weights. One
#: constant, not a per-OS table (Jamie, 2026-09-15). `--host-ram` overrides the
#: RAM figure the reserve is taken from, not the reserve itself.
OS_RESERVE_GB = 8.0

FIT_ACCELERATOR = "accelerator"
FIT_OFFLOAD = "offload"
FIT_NONE = "does_not_fit"

BASIS_ACCELERATOR = "accelerator-roofline"
BASIS_OFFLOAD = "offload-roofline"

_SECTIONS = {
    "cpu": {"model", "cores", "threads"},
    "system_memory": {"type", "channels", "max_speed_mt_s", "capacity_max_gb",
                      "capacity_options_gb", "bandwidth_gb_s", "bandwidth_derivation"},
    "pcie": {"cpu_gen", "cpu_lanes_usable", "accelerator_link_gen", "accelerator_link_width"},
    "storage": {"class", "capacity_options_gb"},
}
_TOP = {"id", "display_name", "kind", "unified", "hardware_ref", *_SECTIONS,
        "field_sources", "figures_are", "notes"}


@dataclass(frozen=True)
class Host:
    id: str
    display_name: str
    kind: str
    unified: bool
    hardware_ref: str | None
    capacity_max_gb: float | None
    bandwidth_gb_s: float | None
    raw: dict[str, Any]


def _numeric(v: Any) -> bool:
    if isinstance(v, bool):
        return False
    if isinstance(v, (int, float)):
        return True
    return isinstance(v, list) and bool(v) and all(_numeric(x) for x in v)


def validate(raw: Any, name: str) -> None:
    """Raise ValueError when a profile breaks hosts/_schema.yaml."""
    if not isinstance(raw, dict):
        raise ValueError(f"{name}: a host profile must be a mapping")
    if set(raw) != _TOP:
        raise ValueError(f"{name}: top-level keys differ from the schema: {sorted(set(raw) ^ _TOP)}")
    if raw["kind"] not in {"platform", "system"}:
        raise ValueError(f"{name}: kind must be platform or system")
    if not isinstance(raw["unified"], bool):
        raise ValueError(f"{name}: unified is required and must be a boolean")
    for section, keys in _SECTIONS.items():
        if not isinstance(raw[section], dict) or set(raw[section]) != keys:
            raise ValueError(f"{name}: {section} keys differ from the schema")
    if raw["unified"] and (raw["system_memory"]["type"] != "unified"
                           or raw["pcie"]["accelerator_link_gen"] is not None):
        raise ValueError(f"{name}: a unified host has memory type unified and no accelerator link")
    sources = raw["field_sources"] or {}
    numeric = {f"{s}.{k}" for s in _SECTIONS for k, v in raw[s].items() if _numeric(v)}
    missing = numeric - set(sources)
    if missing:
        raise ValueError(f"{name}: unsourced numeric fields {sorted(missing)}")


def load_hosts(root: Path) -> list[Host]:
    """Read and validate hosts/*.yaml. An invalid profile is rejected, not defaulted."""
    out: list[Host] = []
    for path in sorted((root / "hosts").glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        validate(raw, path.name)
        if raw["id"] != path.stem:
            raise ValueError(f"{path.name}: id {raw['id']!r} does not match the file name")
        out.append(host_from_raw(raw))
    return out


def host_from_raw(raw: dict[str, Any]) -> Host:
    mem = raw["system_memory"]
    return Host(
        id=raw["id"], display_name=raw["display_name"], kind=raw["kind"],
        unified=bool(raw["unified"]), hardware_ref=raw.get("hardware_ref"),
        capacity_max_gb=float(mem["capacity_max_gb"]) if mem.get("capacity_max_gb") else None,
        bandwidth_gb_s=float(mem["bandwidth_gb_s"]) if mem.get("bandwidth_gb_s") else None,
        raw=raw,
    )


def host_capacity_gb(host: Host, host_ram_gb: float | None = None) -> float:
    """`C_host`: host memory available for spilled weights. 0 for a unified host."""
    if host.unified:
        return 0.0
    ram = host_ram_gb if host_ram_gb is not None else host.capacity_max_gb
    if ram is None:
        return 0.0
    return max(0.0, float(ram) - OS_RESERVE_GB)


def fit_state(weights: float, accelerator_gb: float, host_gb: float, unified: bool) -> str:
    need = weights + WORKING_ALLOWANCE * accelerator_gb
    if need <= accelerator_gb:
        return FIT_ACCELERATOR
    if not unified and need <= accelerator_gb + host_gb:
        return FIT_OFFLOAD
    return FIT_NONE


def offload_fraction(weights: float, accelerator_gb: float) -> float:
    """`f = (W + A - C_acc) / W`, clamped to [0, 1]. 0 when everything is resident."""
    if weights <= 0:
        return 0.0
    f = (weights + WORKING_ALLOWANCE * accelerator_gb - accelerator_gb) / weights
    return min(1.0, max(0.0, f))


def offload_decode_tps(accelerator_bandwidth: float, host_bandwidth: float,
                       params: float, quant: str, fraction: float) -> float:
    """`BANDWIDTH_EFFICIENCY / ((1-f)*P/B_acc + f*P/B_host)`, rounded like the roofline.

    At f = 0 this is exactly `predicted_decode_tps`: the same function answers,
    so no floating-point path can make the two disagree.
    """
    if fraction <= 0:
        return predicted_decode_tps(accelerator_bandwidth, params, quant)
    per_token = weights_gb(params, quant)
    if per_token <= 0:
        return 0.0
    seconds = (1 - fraction) * per_token / accelerator_bandwidth + fraction * per_token / host_bandwidth
    return round(BANDWIDTH_EFFICIENCY / seconds, 1)


def assess(*, total_params: float, active_params: float | None, model_type: Any,
           accelerator_gb: float, accelerator_bandwidth: float,
           host: Host, host_ram_gb: float | None = None) -> dict[str, Any]:
    """Fit state and decode prediction for one (model, device, host) triple.

    The quant chosen is the smallest that reaches the best state: for
    `accelerator` it matches `fastest_quantization`, the figure `fits` carries;
    for `offload` it spills the least, which is the fastest offload.
    Decode tps is null for a model that does not decode tokens, and for an
    offload row whose host has no published bandwidth.
    """
    host_gb = host_capacity_gb(host, host_ram_gb)
    reads = active_params or total_params
    best: tuple[str, str] | None = None
    for state in (FIT_ACCELERATOR, FIT_OFFLOAD):
        ok = [q for q in QUANT_PREFERENCE
              if fit_state(weights_gb(total_params, q), accelerator_gb, host_gb, host.unified) == state]
        if ok:
            best = (state, ok[-1])
            break
    if best is None:
        return {"fit_state": FIT_NONE, "quantization": None, "offload_fraction": None,
                "predicted_decode_tps": None, "predicted_decode_tps_basis": None}
    state, quant = best
    tokens = is_token_generating(model_type)
    if state == FIT_ACCELERATOR:
        f = 0.0
        tps = predicted_decode_tps(accelerator_bandwidth, reads, quant) if tokens else None
        basis = BASIS_ACCELERATOR
    else:
        f = round(offload_fraction(weights_gb(total_params, quant), accelerator_gb), 4)
        tps = (offload_decode_tps(accelerator_bandwidth, host.bandwidth_gb_s, reads, quant, f)
               if tokens and host.bandwidth_gb_s else None)
        basis = BASIS_OFFLOAD
    return {"fit_state": state, "quantization": quant, "offload_fraction": f,
            "predicted_decode_tps": tps,
            "predicted_decode_tps_basis": basis if tps is not None else None}


def write_export(api_dir: Path, hosts: list[Host], build_json: dict[str, Any]) -> dict[str, Any]:
    """Emit `api/hosts.json`: every profile as authored, plus the reserve used."""
    api_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "build": build_json,
        "count": len(hosts),
        "os_reserve_gb": OS_RESERVE_GB,
        "hosts": [h.raw for h in hosts],
    }
    (api_dir / "hosts.json").write_text(
        json.dumps(payload, indent=1, sort_keys=True, default=str), encoding="utf-8")
    return {"hosts": len(hosts)}


def add_to_graph(sink: Any, hosts: list[Host]) -> int:
    """`:Host` nodes and `(:Host)-[:HOSTS]->(:Hardware)` for unified hosts only.

    A discrete pairing is a query-time input, not a stored record, so discrete
    hosts get no node. Not wired into the published graph yet (see
    docs/graph-ontology.md). Returns the number of HOSTS edges.
    """
    edges = 0
    for host in hosts:
        if not host.unified:
            continue
        sink.node("Host", "id", host.id, {"id": host.id, "display_name": host.display_name,
                                          "unified": True, "kind": host.kind})
        if host.hardware_ref:
            sink.edge("Host", host.id, "HOSTS", "Hardware", host.hardware_ref, {})
            edges += 1
    return edges
