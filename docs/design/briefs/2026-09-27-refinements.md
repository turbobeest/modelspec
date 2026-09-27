# Design brief: refinements on the facet board

**Ticket:** MODEL-188 (UI) with engine and data sub-issues. **From:** Jamie's
design session, 2026-09-27. **Builds on:**
[`2026-09-27-facet-board.md`](2026-09-27-facet-board.md). **Evidence:**
[`../../research/refinements/evidence-2026-09-27.md`](../../research/refinements/evidence-2026-09-27.md),
a survey of all 1,133 benchmark pages and 7,055 evidence rows on 1,366 model
cards.

## The idea

Choosing a broad domain is the first cut. Once a person sets **Software
engineering** to Must or Prefer, finer criteria appear under it: Python or
Rust, bug fix or new feature, agentic repo work or a terminal agent. The same
goes for writing (creative or technical), legal (contracts or case law),
finance, medical and the other domains.

The person still chooses everything, so the rule of no interpretation holds.
Refinements are a third level that opens only inside a domain the person has
switched on, so the first screen stays scannable.

Jamie asked for this from first principles rather than one example, so the
taxonomy below comes from the detail our benchmark data actually holds.

## What the evidence supports (from the survey)

**129 candidate refinements:** 35 live now, 30 need tagging or ingestion, 60
need research, and 4 have no benchmark at all.

- **Live now** (at least 2 lineup models with evidence). The strongest are:
  - agentic repo-level coding: 6 direct benchmarks, 22 of 25 text generators;
  - research-level maths: 17;
  - new feature / build from a brief: 16;
  - long-horizon business operation: 16;
  - code quality / mergeability: 13;
  - bug fix: 10;
  - terminal agent: 9;
  - competition maths: 9;
  - customer support under policy: 9;
  - Python: 7 (SWE-bench Verified is Python-only).
  Arena preference slices are also live, labelled as preference.
- **Tagging or ingestion only:** the evidence exists but isn't wired in.
  - Arena publishes 9 natural-language categories (17–22 lineup models each), vision OCR, diagram and homework slices, a document board and factuality. We don't ingest them.
  - Three snapshot benchmarks could be tagged `finance: proxy` today.
  - `simpleqa_verified` (factuality, 17 models) has no domain tag.
- **Needs research:** programming languages beyond Python (Rust, Java, Go, C++, TypeScript), legal sub-areas, long context, and web research agents. No verified per-language score exists on any lineup card.
- **No benchmark at all:** test writing, reviewing someone else's code, fixing a security vulnerability, and SEO.

The data plumbing already exists and is unused. Evidence rows have a
`subcategory` field that the engine already reads, and no row sets it.
Per-language scores can go on existing benchmark ids as sub-category rows.

## Taxonomy: four kinds of refinement

Every refinement has a parent (a domain, or "any" for cross-domain axes), a
kind, a definition, and the benchmarks that measure it, each tagged
direct or proxy.

| Kind | What it narrows | Examples |
| --- | --- | --- |
| **Language** | the programming or natural language of the work | Python, Rust, TypeScript, SQL, CUDA; Chinese, Spanish, Japanese |
| **Task** | what the model is asked to do | bug fix, new feature, refactor, review, test writing, migration; contract review, case-law research; financial analysis |
| **Mode** | how it works | agentic in a repo, terminal agent, in-IDE, single function, competitive programming; long-horizon; browsing |
| **Material** | what it works on | web front-end, scientific code, data/ML, security/CTF; charts, OCR and documents, screenshots; long documents |

Two cross-domain axes attach to "any" rather than to a domain: **natural
language of the task** and **input length** (context actually used, which is
different from the context-window facet).

## How a refinement behaves

1. **It's an estimate, nested in its domain.** "Software engineering in Rust" is
   the software-engineering estimate plus a Rust-specific adjustment, learned
   from Rust-tagged evidence. With little Rust evidence, the adjustment shrinks
   toward zero and the interval widens. The model then falls back to its
   general coding estimate, visibly less certain. This keeps Jamie's rule of
   never locking in benchmarks: no single Rust benchmark decides; every
   Rust-tagged result contributes.
2. **Three states, like facets.**
   - **Prefer:** the refinement's weight is carved out of its parent domain's
     weight. The person splits "Software engineering 0.6" into "general 0.3 ·
     Rust 0.3" with one slider.
   - **Must** is a floor on the refinement estimate. It's offered only when the
     refinement is live.
   - **Doesn't matter** is the default.
3. **Honest states for evidence**, shown on every refinement row:
   - **Live:** at least 2 lineup models still in the running have evidence.
     Prefer and Must are enabled. The row shows "measured on 7 of 25".
   - **Thin:** exactly 1 model has evidence. Prefer is allowed, with a warning
     that the order rests on one model. Must is disabled.
   - **Not yet measured:** benchmarks exist, but no lineup model has scores
     (needs tagging or research). The row is listed and greyed out, with the
     reason and a link to what would measure it.
   - **No benchmark:** nothing measures it anywhere. The row is listed,
     greyed out: "No public benchmark measures test writing yet".
   Models without refinement evidence are never dropped. They're ranked on
   their parent-domain estimate with the wider interval, labelled "no Rust
   evidence — estimated from general coding".
4. **Preference-only evidence is labelled.** A refinement measured only by
   Arena (human preference) says "preference, not correctness" wherever it
   appears, as proxy evidence does today.
5. **Suggestions without interpretation.** When a domain opens, its refinements
   are listed in order of evidence strength (live first). Nothing is
   preselected.

## On the board

- Under an active domain row, a **Refine** control expands a compact list
  grouped by kind: Language · Task · Mode · Material. Each row has the three
  states, its evidence badge (Live / Thin / Not yet measured / No benchmark)
  and "measured on n of N".
- The answer column explains each refinement's effect: "Ranking on Software
  engineering (Rust 0.3 · general 0.3) · Cost 0.4". Models without Rust
  evidence show the fallback label.
- The canvas (MODEL-184) can put any live refinement on an axis, for example
  "SWE: Rust × Cost".
- Templates can set refinements. Candidates: "Rust systems work" and
  "front-end web", once live.

## For agents (CLI / API / MCP)

- Refinements are vocabulary entries (`modelspec vocab refinements --domain
  software_engineering`), each with its evidence state and coverage.
- In a spec they are capability keys in the same namespace: `optimize.weights:
  {software_engineering: 0.3, "software_engineering/rust": 0.3,
  -offering.cost_per_task: 0.4}`. The naming is up to the engine ticket; it's
  an additive contract change.

## Work, split by lane

| Ticket | Lane | What |
| --- | --- | --- |
| Refinement registry + tagging | mothership (data) | registry of refinements (id, parent, kind, definition); benchmark tags per refinement, direct or proxy; published in the vocabulary with coverage and evidence state |
| Nested estimate | mothership (engine) | the refinement estimate as the domain estimate plus a partially pooled adjustment; intervals widen without evidence; refinement keys in `optimize.weights`; contract minor bump |
| Quick-win ingestion | mothership (data) | the Arena language, vision (OCR, diagram, homework), document, industry and factuality slices, 17–22 models each; `finance: proxy` tags on three snapshot benchmarks; verify the lineup rows already on cards (`healthbench_professional` and others) |
| Research | mothership (research) | per-language coding scores as `subcategory` rows (SWE-bench Multilingual, Multi-SWE-bench, Aider Polyglot, MultiPL-E); direct finance and legal benchmarks for lineup models |
| Board UI | this lane (MODEL-188) | the Refine control, evidence badges, weight carving, fallback labels, the canvas axis; built after Jamie approves the board, and rendering whatever the vocabulary publishes |

## Out of scope

- Inferring refinements from anything a person types.
- Inventing a score for a refinement nobody measures. "No benchmark" is a
  finding in its own right, and it tells research where to go.
