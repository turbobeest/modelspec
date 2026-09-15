# The host layer (MODEL-26)

Status: **phase B implemented** (`pipeline/hosts.py`, `offline fit --host`). Jamie
accepted decisions 1-6 below as recommended on 2026-09-15; agentic latency moved
to MODEL-57. The contract is documented in `docs/cli-contract.md` under "Hosts
and offload".

## Why

`pipeline/hardware.py` answers two questions per (model, device): does it fit in
accelerator memory (`fits`), and what is the roofline decode speed
(`bandwidth x 0.70 / bytes read per token`). Both are right for a model that
sits entirely in accelerator memory. Decode there is bandwidth-bound, and the
host CPU barely matters.

The host decides the answer in four places:

1. **Offload.** Layers that do not fit spill to system RAM. Decode is then
   limited by *system memory* bandwidth. The answer becomes "fits, slowly",
   not "does not fit".
2. **CPU-only inference.** It is the same case, with every layer on the host.
3. **Agentic wall-clock.** Tool execution, I/O and API waits. See the deferral
   below.
4. **Orchestration overhead.** Tokenisation, sampling and scheduling. It is
   small next to decode, so it is not modelled.

## The model

```
Host ──HOSTS──▶ Hardware          (discrete: host and accelerator are separate records)
Host(unified: true, hardware_ref) (unified: one silicon, one memory pool)
```

- **Discrete.** A `Host` (`hosts/*.yaml`) plus a `Hardware` (`hardware/*.yaml`)
  make a *pairing*. The pairing is a query-time input (`--host X --device Y`),
  not a stored record. Any host can pair with any PCIe device, and storing the
  cross product would be data with no source.
- **Unified** (Apple silicon, Strix Halo, DGX Spark). `unified: true`. The host's
  `system_memory` describes the one shared pool, and `hardware_ref` points at the
  same silicon's Hardware record. There is no offload tier, because the pool is
  already the accelerator's memory. Fit is two-state, and
  `pcie.accelerator_link_gen` is null. This matches `hardware.memory.unified_with_host`.
  The test enforces that a unified host has `type: unified` and no accelerator link.
- The graph keeps Hardware as it is. Phase B adds a `Host` node label and a
  `(:Host)-[:HOSTS]->(:Hardware)` edge, for unified hosts only. For discrete hosts
  the pairing lives in the query, and `docs/graph-ontology.md` is updated then.

## Minimal fields (each changes an answer)

| Field | Changes |
|---|---|
| `unified` | whether an offload tier exists at all |
| `system_memory.bandwidth_gb_s` | decode speed of offloaded layers (the dominant term) |
| `system_memory.channels`, `max_speed_mt_s` | derive bandwidth when a vendor does not publish it. The DIMM population changes the rated speed (9950X: DDR5-5600 at 2 DIMMs, DDR5-3600 at 4). |
| `system_memory.capacity_max_gb` / `capacity_options_gb` | whether the spill fits at all (the `does_not_fit` boundary) |
| `cpu.cores`, `threads` | CPU-only prefill (compute-bound). Recorded, but no formula uses them in phase B. |
| `pcie.cpu_gen`, `accelerator_link_gen`, `accelerator_link_width` | the cost of *not* keeping experts/layers resident (see "known wrong"); load time. The link is min(CPU, slot, device). |
| `storage.class` | cold-load time and mmap paging. Recorded only. |
| `field_sources` | provenance: every non-null number cites a page, read date and quote |

Deliberately absent: motherboard, cooling, PSU, NUMA topology, OS, and RAM timings.
None of them moves a fit state, and they only nudge decode.

## Fit states

Phase B replaces the boolean with an additive `fit_state`. `fits` stays, with
unchanged meaning (`fit_state == "accelerator"`).

Let `W` = weights at the chosen quant (`weights_gb`), `A` = the existing
`WORKING_ALLOWANCE` overhead, `C_acc` = accelerator capacity, and `C_host` =
host memory available for weights (`capacity_max_gb` minus a stated OS reserve,
proposed 8 GB, or the user's `--host-ram`).

- `accelerator`: `W + A <= C_acc`. This is today's `fits: true`.
- `offload`: not `accelerator`, and `W + A <= C_acc + C_host`, and the host is not
  unified. It carries `offload_fraction = (W + A - C_acc) / W` and a predicted
  decode speed with its formula stated.
- `does_not_fit`: neither of the above. For a unified host, `C_host` is 0 by
  definition.
- `cpu_only` (`C_acc` = 0, no accelerator) is the `offload` formula with `f = 1`.

## Offload decode formula

A token reads the resident fraction from accelerator memory and the spilled
fraction from system memory, in sequence. Per-token time adds:

```
t_token = ( (1-f)·P / B_acc  +  f·P / B_host ) / BANDWIDTH_EFFICIENCY
tps     = BANDWIDTH_EFFICIENCY / ( (1-f)·P/B_acc + f·P/B_host )
```

Here `P` = GB read per token (active params x quant bytes, as in
`predicted_decode_tps`), `f` = `offload_fraction`, `B_acc` = device
bandwidth, and `B_host` = `system_memory.bandwidth_gb_s`. When `f = 0` it reduces
exactly to today's roofline. Example: at f = 0.5, with B_acc = 1792 (RTX 5090)
and B_host = 89.6 (9950X), tps ≈ 0.7 / (P · (0.00028 + 0.00558)). The host term
is ~95% of the time, so the GPU barely matters. That is the point the ticket makes.

Assumptions: layer-split offload (llama.cpp `-ngl` style), where offloaded
layers also *compute* on the CPU. The formula assumes the CPU is not the
bottleneck for those layers. The PCIe transfer per token is only the hidden state,
which is negligible. The 0.70 efficiency applies to both pools.

Known wrong:
- **CPU compute-bound layers.** Few cores or no AVX-512/AMX makes the host slower
  than its bandwidth predicts. The formula overstates.
- **MoE expert offload** (experts on host, attention on GPU). `f` should use the
  *active* expert bytes, not the total, and the right `P` split is per-tensor.
  Phase B uses the active-param split, and labels it an estimate.
- **Weights streamed over PCIe** (some runtimes compute offloaded layers on the
  GPU). There the bound is the PCIe bandwidth, not B_host. Not modelled.
- **Prefill.** It is compute-bound and not covered at all.
- **KV cache** placement is ignored. With the cache on the host, long context degrades further.
- Rated DIMM speed is not the running speed (XMP/EXPO, 4-DIMM derating).

## Additive to CLI contract 1.0

Phase B only *adds* fields, and `schema_version` stays `"1.0"`:
- Fit rows gain `fit_state`, `offload_fraction`, `host_id`, and
  `predicted_decode_tps_basis` (`accelerator-roofline` | `offload-roofline`).
- `fits` keeps its meaning. A consumer that reads only `fits` sees no change.
- Without `--host`, output is byte-identical to today, because no row has
  `fit_state: offload`.
- `hosts.json` is a new export file. `build.export_schema_version` stays `1.0`
  (additive).

## Phase B file plan

- `pipeline/hosts.py` (new): `load_hosts`, `Host` dataclass, `fit_state`, `offload_decode_tps`.
- `pipeline/hardware.py`: call `fit_state`, and add fields to rows (after PR #59).
- `pipeline/export.py` / `pipeline/build.py`: emit `api/hosts.json`.
- `cli/modelspec/offline.py`: `fit --host ID [--host-ram GB] [--include-offload]`.
- `docs/cli-contract.md`: document the new fields and flags.
- `docs/graph-ontology.md`, `schema/graph.py`: the `Host` label and `HOSTS` edge (unified only).
- `tests/test_hosts.py` (extend), and `tests/test_hardware.py` (f=0 reduces to roofline).
- `pipeline/render.py` / web3d wizard: the offload badge. Optional, and a later ticket.

## Agentic latency: deferred

**Deferred.** Wall-clock in an agent loop is `Σ(prefill + decode) + Σ(tool
execution + I/O + API waits)`. The second sum depends on the *task and harness*,
not the machine. The same host runs a `grep` tool in 10 ms and a test suite in
10 minutes. A number invented here would be a synthetic benchmark with no
source. That breaks "a null beats a guess".

The honest home is **benchgraph**: an agentic wall-clock benchmark (for example a
fixed task suite timed end to end on a stated host+device+runtime), ingested
under the eligibility contract like any other benchmark, with evidence dating.
The host layer contributes the *keys* such a benchmark result must carry
(`host_id`, `hardware_id`), so results can join. It does not contribute the number.

## Not modelled

Prefill/TTFT, and CPU instruction sets (AVX-512, AMX). Multi-GPU pairings and
tensor parallel, PCIe bifurcation, and NVMe/mmap paging speed. Thermal throttling of
hosts, and NUMA. OS memory reserve beyond the one constant. Runtime differences
(llama.cpp versus vLLM offload). KV-cache offload. Power and cost.

## Decisions for Jamie

1. **Do offload rows appear in default `offline fit`?** Recommend **no**. Keep
   them behind `--include-offload`, which requires `--host`. The default
   output then stays byte-identical, and nobody reads "fits" where it runs at 3 tok/s.
2. **Does an offload row rank?** Recommend **no** in phase B. Rank on
   `accelerator` only, and show offload as a separate annotated tier.
3. **Default OS reserve for `C_host`.** Recommend a fixed 8 GB with
   `--host-ram` to override. There is no per-OS table.
4. **Agentic latency.** Recommend the deferral to a benchgraph benchmark ticket.
5. **Host catalogue scope.** Recommend platforms (CPU+memory spec) and unified
   systems only, not motherboards or builds. At most about 10 profiles, added when a
   DPF question needs one.
6. **Rated or derated DIMM speed** for bandwidth. Recommend the 2-DIMM rated
   speed, with the 4-DIMM figure in `bandwidth_derivation`.
