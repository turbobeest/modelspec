---
status: accepted
---
# No fixed benchmark weights; constraints filter, only evidence scores

v1 ranked models on hand-picked benchmark lists with fixed weights per use case, plus points for declared capability tiers, context length and model type. When labs moved to new benchmarks, every new model fell below the coverage floor, and old, richly documented cards kept winning; the ranking decayed silently for five months (2026-04 to 2026-09). We decided on 2026-09-24 that no ranking may depend on a fixed list of benchmarks or weights. Capability is estimated by a model fitted to all verified evidence, with learned benchmark weights and intervals (MODEL-129). Properties such as context length, model type and hardware fit are facets to filter on or tradeoffs to show, and never add to a score. Hard-coded lists of benchmarks, providers, platforms or use cases should be treated as defects.

## Considered options

- **Refresh the fixed profiles periodically** (MODEL-123's interim weights): rejected. It is the same design with a later expiry date, and on real data the declared-tier and type bonuses still put older models on top.
