# Live leaderboard harvest (AA + LM Arena)

2026-09-10. Attachments went through `scripts/attach_evidence.py` and
`LEDGER_TO_CARD` only. No git writes. Firecrawl JSON/query/highlight was not
used.

## Credits

| | |
| --- | ---: |
| Opening remainingCredits | **5569** |
| Spent | **0** |
| Closing remainingCredits | **5569** |
| Guard hit | no |
| Task budget | 300 |
| CLI default budget | 20 |

Fetcher: plain HTTP GET of the two census URLs (0 Firecrawl credits). Both
pages are Next.js apps whose HTML already contains the flight payloads with
per-model scores. Caching that HTML under
`benchmarks/_census/ranking_evidence/raw/` (plus `.meta.json` with
`fetched_at`) is enough to finish later for free via `--no-fetch`.

Firecrawl markdown scrape is wired (`scripts/benchmarks/fetch.py --budget N`,
`--firecrawl` on the harvest script) and **aborts in code** when spend since
the opening `https://api.firecrawl.dev/v2/team/credit-usage` snapshot reaches
the budget. JSON / query / highlight formats are refused unless
`--allow-expensive-formats` is set. Those formats were not necessary here:
the expensive 5× path is how a previous pair burned ~920 credits.

## Cards moved from unrankable to rankable

`fetch_manifest.json` progress.tiers.unrankable (no flat scores and no
evidence):

| | cards |
| --- | ---: |
| Before | **667** |
| After | **601** |
| Moved | **66** |

167 cards received new evidence rows (plus 4 already carrying this evidence).
Most of those 167 already had some other score; the unrankable gap only
clears when a card goes from *none* to *any*. 66 cards made that jump.

Harvest extracted 2260 scored cells (2060 AA ranked components + 200 Arena
style-control overall). 590 of those had an explicit `LEDGER_TO_CARD` entry
and were attached. Absence stays absent.

## Ranked keys taken

From `USE_CASE_PROFILES` after `_apply_verified_additions()` (78 keys). Taken
only when the column identity was exact:

| source | column / snapshot | ranked key | unit |
| --- | --- | --- | --- |
| AA | `gpqa` (methodology: GPQA Diamond, 448 questions) | `gpqa_diamond` | percent |
| AA | `scicode` | `scicode` | percent |
| AA | `lcr` | `aa_lcr` | percent |
| AA | `gdpvalNormalized` | `gdpval_aa` | percent |
| AA | `critpt` | `critpt` | percent |
| LM Arena | `text-overall-style_control` | `arena_elo_style_control` | elo |

AA 0–1 fractions were stored as percent. Arena ratings were stored as Elo.

## Date-contract decision

Implemented, not relitigated.

A static published result (paper, model card, blog) still requires a stated
day. Inferring that day from retrieval is the failure mode the old census
rule guards against, and it remains a refusal.

A live leaderboard row has no publication date. It has a standing that
changes. The measurement *is* “this model’s standing on that board on that
date.” `date_type: evaluated`, `source_kind: independent_evaluator`,
`evidence_date` = the date the page was fetched. Cached parses reuse
`.meta.json` `fetched_at`, not the parse-pass day.

Prefer a stated snapshot / as-of / last-updated when one exists. Neither
page stated a day, so both used the observation date **2026-09-10**.

`BENCHMARK_WRITE_RULE` in `scripts/build_manifest.py` (and the regenerated
`fetch_manifest.json`) now states this published-vs-live distinction
explicitly.

## Mapping

`LEDGER_TO_CARD` was extended with 212 explicit unique matches. Attach never
infers a name. `(max)` is treated as the boards’ canonical product row, the
same judgement already recorded for `GPT-6 Astra (max)`. `(high)` / `(low)` /
`(medium)` / `(xhigh)` / thinking / non-reasoning are refused.

## Refusals (by cause)

### AA field is not a ranked key (13)

An AA index is not a raw benchmark. Wrong variants are not folded into a
nearby ranked id.

- `intelligenceIndex` — composite Intelligence Index
- `mmmuPro` — MMMU-Pro ≠ `mmmu`
- `terminalbenchV21` / `terminalbenchV40` / `terminalbenchHard` — not `terminal_bench` (v1.0)
- `tau2` / `tauBanking` — not original `tau_bench`
- `hle` — not ranked
- `ifbench` — not `ifeval`
- `omniscience` / `analystAgent` / `apexAgents` / `itbenchSre` — not ranked

### Arena snapshot is not the ranked Elo variant (10)

Arena Elo overall is not a category Elo. Style-control overall is not raw
overall. Only `text-overall-style_control` was taken (`arena_elo_style_control`).

- `webdev-overall-raw` (127) — not `arena_elo_coding`
- `vision-overall-style_control` (148) — style-control vision ≠ `arena_elo_vision`
- `document-overall-raw` (39)
- `text_to_image-overall-raw` (78)
- `image_edit-overall-raw` (55)
- `image_to_webdev-overall-raw` (44)
- `search-overall-raw` (34)
- `text_to_video-overall-raw` (48)
- `image_to_video-overall-raw` (47)
- `video_to_video-overall-raw` (10)

### Effort / serving variant (307 unique names, 864 scored cells)

Row is not the base product. Examples: `Claude Opus 5 (high)`,
`GPT-6 Astra (high)`, `GPT-5.6 Sol (low)`, `DeepSeek V4 Pro (Non-reasoning)`,
`Claude Fable 5.1 (xhigh with fallback)`. Full list:
`leaderboard_refusals.json` → `refusals.effort_variant`.

### Ambiguous name (13 unique)

More than one card, or an unqualified name with an Instruct/IT sibling.

- `Devstral 2` — `mistral/devstral-2512`, `mistral/devstral-latest`
- `GLM-5.2 (max)` / `glm-5.2-max` — `mistral/zai-glm-5-2`, `qwen/glm-5-2`
- `Gemma 3 270M`, `Gemma 4 31B` — base vs IT
- `Llama 3.1 405B` / `70B` / `8B`, `Llama 3.2 1B` / `3B` — base vs Instruct (and duplicate orgs)
- `Qwen3 0.6B` — `qwen/qwen3-0-6b`, `unsloth/qwen3-0-6b`
- `gpt-5.1`, `gpt-5.2` — more than one card

### No unique exact card (284 unique names, 768 scored cells)

No card, or the evaluator name does not uniquely match a display_name / slug.
Examples: `Claude 3.5 Sonnet (Oct)`, `Gemini 3 Flash`, `MiMo-V2.5-Pro`,
`Qwen3.5 Omni Plus`, `Grok 4.20 0309`. Full list:
`leaderboard_refusals.json` → `refusals.unmapped_name`.

## How to replay for free

```
.venv/bin/python scripts/fetch_ranking_leaderboards.py --no-fetch --dry-run
.venv/bin/python scripts/attach_evidence.py --dry-run
```

Cached pages:

- `raw/artificialanalysis-ai-leaderboards-models.html` (+ `.meta.json`, fetched_at 2026-09-10)
- `raw/lmarena-ai-leaderboard.html` (+ `.meta.json`, fetched_at 2026-09-10)
