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

## Deriving bandwidth, rather than transcribing it

Vendors rarely publish memory bandwidth directly, but they do publish the two
numbers it comes from. For a discrete card:

    bandwidth GB/s  =  bus_width_bits / 8  x  memory_data_rate_Gbps

An RTX 5090 is 512-bit GDDR7 at 28 Gbps, which is 512/8 x 28 = 1792 GB/s. That
is a derivation from two published figures rather than a number copied from a
review, and it should be preferred wherever the inputs are available. Record
both inputs so the derivation can be rechecked.

Unified-memory parts (Apple, Strix Halo) do not work this way and the figure has
to come from the vendor's own material.

## One record per commercially distinct SKU

A Hardware record is a product you can buy or rack, not a die with memory
soldered later. The old id shape (`macbook_m4_pro_64gb`) is not used.

* **Same silicon, same bandwidth, OEM RAM options** — one file. Apple SoCs list
  those options as `capacity_options_gb` and set `capacity_gb` to the published
  maximum. Fit uses that maximum. Unified parts whose vendor only publishes a
  ceiling (Snapdragon X Elite, Ryzen AI Max+ 395) store the ceiling and say so
  in notes; they do not invent an option list.
* **Distinct memory subsystems** — separate files. A100 40GB SXM and 80GB SXM
  differ in HBM generation and bandwidth. Jetson Orin/Thor modules are sold as
  separate SKUs, so each capacity is its own row (`nvidia_jetson_agx_orin_32gb`,
  `_64gb`). Consumer cards that NVIDIA names by capacity follow the same rule
  (`nvidia_rtx_3060_12gb`, `nvidia_rtx_4060_ti_16gb`).
* **A package is not a second chip.** GB10 is the SoC inside DGX Spark, not a
  sibling row. The Jetson AGX Thor Developer Kit is the T5000 module.

Groq LPU and Cerebras WSE-2 stay out: neither publishes a per-chip datasheet
with capacity and bandwidth. WSE-3 does, and is present with the SRAM caveat.

## Provenance is required

Every device carries `sources`, and `figures_are` says what kind of claim the
numbers are. Vendor specifications are vendor claims — useful, but not
independent measurement, and labelled as such. This is the same standard the
benchmark catalogue holds evidence to.

A row without `memory.bandwidth_gb_s` cannot answer the question this layer
exists to answer. Do not add one. `bandwidth_derivation` records how the
figure was obtained (bus × rate, or transcribed from a vendor table).
