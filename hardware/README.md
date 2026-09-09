# Hardware definitions

One YAML file per device. These are the machines a reader might own or rack, and
they exist so the platform can answer "what can I actually run, and how fast will
it feel" rather than only "does it fit".

## What is here, and what is not

**Here:** silicon someone can own or operate — consumer and workstation GPUs,
Apple silicon, datacentre parts that can be racked, edge modules.

**Not here:** cloud-only accelerators. Groq LPU, Cerebras WSE and Google TPU are
modelled as *Platforms*, because "does this model fit on my Groq" is not a
question anyone asks; "what does it cost per token there" is. Renting an H100 is
a Platform relationship over silicon that also has a Hardware record.

## Why bandwidth is the headline number

Inference has two phases with different bottlenecks:

* **Prefill** — reading the prompt. Compute-bound. Sets time-to-first-token.
* **Decode** — writing the answer. **Memory-bandwidth-bound.** Sets tokens/sec.

Decode reads every active weight to emit one token, so roughly:

    decode tok/s  ≈  memory_bandwidth ÷ (active_params × bytes_per_param)

For a mixture-of-experts model that is *active* parameters, not total.

Capacity and bandwidth are orthogonal, and conflating them is the most common
mistake in this space. A DGX Spark holds about four times the model an RTX 5090
does, and decodes it roughly six times slower.

## Compute figures need qualifiers

TOPS has no shared definition. The same chip is quoted at wildly different
numbers depending on precision, on whether structured sparsity is assumed, and
on dense versus peak. Store compute as a list of entries that each state their
precision and sparsity assumption, or the number is noise. `precisions_native`
is separate and matters on its own: a device without FP8 hardware gains nothing
from an FP8 quantisation.

## Provenance is required

Every device carries `sources`, and `figures_are` says what kind of claim the
numbers are. Vendor specifications are vendor claims — useful, but not
independent measurement, and labelled as such. This is the same standard the
benchmark catalogue holds evidence to.

A row without `memory.bandwidth_gb_s` cannot answer the question this layer
exists to answer. Do not add one.
