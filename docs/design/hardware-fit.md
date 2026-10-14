# Hardware-fit closeout

MODEL-348 closes on the decisions below. The implemented estimates are
specified under "Architecture and hardware estimates (MODEL-348)" in
[the decision contract](../decision-contract.md#architecture-and-hardware-estimates-model-348),
contract 2.17. This note adds no facet, changes no contract field, and
gives architecture and hardware no ranking weight.

## Quantisation and precision

`fitting_quants` in `pipeline/hardware.py` keeps every quantisation whose
resident weights fit in usable memory, best quality first. The order is
`bf16`, `fp16`, `fp8`, `int8`, `q6`, `q5`, `q4`, at 2, 2, 1, 1, 0.75,
0.625 and 0.5 bytes per parameter. The engine uses the first entry.
Selection compares unrounded weight memory with usable memory. Each
estimate reports that quantisation. When none fits, `quantisation` is
null and `unknown_reason` says why.

There is no caller-selected precision facet. The estimate already states
the precision it assumed. A caller override would be a new input. The
current facets are `hardware.weights_gb` and `hardware.decode_tps_estimate`.

A future caller-selected precision is acceptable when a spec can name one
of those seven values, both estimates use it when the weights fit usable
memory, and either estimate is unknown with a reason when they do not.
The choice must not enter `rank_score`. Widening an existing contract
field to carry it follows MODEL-59.

## Resident memory

`hardware.weights_gb` is resident weights from total parameters.
`WORKING_ALLOWANCE` is 0.25, so usable memory is 75 percent of device
capacity. The formula does not add a device-dependent working set on top
of the weights.

There is no total-workload memory facet. A workload total needs context
length, batch size, KV cache and activations. The decision snapshot does
not carry those inputs. A second memory number taken only from the same
25 percent allowance would present fixed headroom as a measured workload.

## KV cache and context fit

Deferred. The decision snapshot has no layer or head geometry, so the
estimate places KV cache inside the 25 percent allowance. The contract
states that this does not establish a context length or a
workload-specific fit.

`pipeline/hardware.py` can compute KV bytes per token from card geometry
when layer count, KV heads and head dimension are present. The decision
snapshot does not expose that geometry, and the decision estimate does
not call that calculator.

A future context-fit estimate is acceptable when the snapshot admits
verified geometry facts, the formula states KV bytes for a named context
length, and the estimate says whether that context fits in the allowance,
with input records and sources. Until those facts are in the snapshot,
context fit stays unestablished.

## Architecture

`model.architecture`, `model.parameters_total` and `model.parameters_active`
are facts. `model.experts_total` and `model.experts_per_token` are facts
when the registry defines them. Ordinary Must and Prefer conditions can
filter them. They have no default ranking weight, including in
`rank_score`. MODEL-100 forbids a number that orders one class above
another, and these facts do not supply one. An unknown hard condition
stays `may_qualify`. Missing active parameters never fall back to total
parameters. That refusal holds for a dense model too.

## CUDA and runtime

Deferred. Runtime is not a compatibility gate.

`fitting_quants` admits a quantisation the device does not accelerate
natively. The fit gate is memory. `precisions_native` can inform a
prediction. It does not reject a fit. The decision-engine catalogue also
leaves exact download artifacts, including a specific quantised file,
out of scope.

A future runtime gate is acceptable when the snapshot has a verified
fact for the constraint being gated, such as a CUDA compute capability
or a named runtime, and a registered facet applies the existing unknown
policy. The gate must not change `rank_score`. Until those facts exist,
CUDA and runtime do not decide fit.

## Unchanged

This closeout adds no registry facet. The two hardware estimate facets
remain `hardware.weights_gb` and `hardware.decode_tps_estimate`. The
decision contract stays 2.17. The bounded representation stays at its
current version, 1.3, and this note does not change it. Ranking floors
are unchanged.
