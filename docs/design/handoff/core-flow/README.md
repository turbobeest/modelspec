# Handoff: ModelSpec core decision flow

## Overview
ModelSpec is a neutral decision engine that tells people which AI model, and which provider offering, to use for a task under their constraints, and why. This package covers the **core flow** on desktop in light and dark modes: arrive → state needs (task parse, chips, add condition) → watch the field narrow (funnel, next questions) → see the answer (trade-off canvas + shortlist + may-qualify) → understand why (contribution bars, evidence with provenance, condition checks, constraint cost, near misses, tipping point, why-not, offerings) → change their mind (every control live) → share or act (permalink, API/CLI/YAML, alerts, procurement export).

There are two layouts of the same engine, switchable in the header:
- **Canvas first** (default): canvas + shortlist on top, then the why panel, then the table.
- **Table first**: the table is the hero, with the canvas as a smaller lens on the right.

Not in this package yet: mobile, the model page, the launch report, social cards, the flow map, and the design-system sheet.

## About the design files
These files are **design references built in HTML**. They are prototypes showing the intended look and behaviour, not production code to copy. Recreate them in the target codebase's environment (React, Vue, etc.) using its own patterns. If there is no codebase yet, pick a suitable framework (React + TypeScript with SVG or Canvas charts is a good fit).

`modelspec-data.js` holds two things:
1. The **fictional sample catalogue**: 25 models, 6 labs, 60 offerings. It must stay labelled as fictional.
2. A **reference decision engine**: `evaluate`, `suggestions`, `parseTask`, `relaxValue`. Treat it as a behavioural spec for the real API. It is plain ES module JS, readable on its own, and is the most precise description of the logic.

`*.dc.html` files are "Design Components": HTML templates with `{{ }}` holes plus a logic class. `support.js` is the runtime that renders them; you don't need to port it. To view a prototype, serve the folder over HTTP (e.g. `npx serve`) and open `ModelSpec.dc.html`.

## Fidelity
**High fidelity.** Colours, type, spacing, states and interactions are final for this pass. Recreate them precisely.

## Screens / views

### Global header (sticky, 56px)
- Background `--surface`, 1px bottom border `--line`, padding `0 24px`, gap 14px.
- **Logo**: 28×28 SVG (viewBox 32). Navy rounded square (rx 3) with the axes drawn in `#8fa3c2` at 1.2px. A cursive "M" drawn as a line-chart stroke (white, 1.7px, round caps and joins) runs across the axes, with 5 dots (r 1.5, `#5aa9ec`) at the M's turning points. The exact path is in the file.
- **Wordmark**: "Model" in 17px weight 600, then "Spec" in weight 300, letter-spacing -0.02em.
- **Badge** "Fictional sample data": mono 11.5px, `--warn` text on `--warnSoft`, padding 3px 8px, radius 2px.
- **Right side**:
  - Snapshot ID in mono 12px `--muted`, hidden below 1100px wide.
  - Segmented control "Canvas first | Table first": active is `--ink` background with `--surface` text.
  - "Dark mode / Light mode" toggle.
  - Primary button "Share or act": `--accent` background, `--accentInk` text, 13px weight 600, padding 7px 14px.
- All header controls use `white-space: nowrap`.

### 01 Arrive
- Centred column, max-width 1000px, padding `80px 24px 72px`, vertical gap 40px.
- **Label** "Model decision engine": mono 11.5px `--muted`.
- **H1** "Which AI model fits your task, under your constraints, and why.": 52px, weight 300, line-height 1.04, letter-spacing -0.035em, max-width 860px, `text-wrap: balance`.
- **Lede**: 17px `--muted`, max-width 660px. The model and offering counts are live.
- **Task box**:
  - `--surface`, 1px `--line2` border, radius 2px, padding 18px.
  - Mono label "Describe your task".
  - Borderless textarea, 22px.
  - Footer row (top rule `--line`): the hint "A small classifier turns this into conditions you can see and edit. There is no chat." and the primary button "Find models ↵". Enter submits; Shift+Enter adds a new line.
- **Templates**: grid `repeat(auto-fit, minmax(260px, 1fr))`, gap 12px. Each card is a button:
  - Name 16px weight 600.
  - Task 13px `--muted`.
  - Mini chips 11.5px on `--surface2`.
  - Footer with the live "N qualify" (22px weight 300) and "+ M may qualify" in `--warn`.
  - Hover: border turns `--accent`.
- **Link** "start from constraints": opens the work view with only "Type: LLM" and "Offered now" set, and the add-condition search open.

### 02 Decide (work view)
Max-width 1640px, padding `18px 24px 72px`, vertical gap 14px. Every panel is `--surface` with a 1px `--line` border, a **2px `--ink` top rule**, and radius 0. Panel labels are mono 11.5px `--muted` in sentence case.

**Spec panel**
- **Task input**: 18px, bottom border only.
- **Tokens per task**: two number inputs, in and out. Every $ per task figure is derived from these, visibly.
- **Rank by**: three range sliders, step 0.05: the primary benchmark, $ per task, and tok/s. The weights always renormalise to sum to 1. Each shows its value to 2 decimals.
- **Chips**:
  - Label, then meta in 11px `--muted` ("soft · from task · −N removed"), then a × remove button.
  - Chips parsed from the task use an `--accentSoft` background. Soft chips have a `--warn` border. The chip being edited has an `--accent` border.
- **+ add condition**: dashed button. It opens a search box that filters facets by keyword (e.g. "residency"). Enter adds the first match, then opens its editor.
- **Parse trace**: "Read from your task: “large” → context ≥ 200K …".
- **Condition editor** (inline panel with an `--accent` border):
  - A numeric value with its real unit.
  - Require/Exclude, a region, or Independent only/Any source, where relevant.
  - Hard/Soft. Soft keeps failing models, flags them, and adds no points.
  - Remove and Done.
- **Parse loading**: three grey skeleton chips and "Reading your task…" for about 420 ms.

**Narrowing panel** (auto-fit, min 400px) and **next questions panel**
- **Funnel**: a grid of steps. Each step has:
  - the count, 30px weight 300;
  - a 6px bar: the confirmed share in `--ink2`, then the "may" share in `--warn` at 55% opacity;
  - the condition label and "−N" removed.
  - The last step, "Ranked on evidence", is in `--accent`. Bar widths animate over 0.45s with `cubic-bezier(.2,.7,.2,1)`.
- **Next questions**: sorted by how many models each would remove. Each option shows its result, e.g. "→ 5 + 1 may". "Doesn't matter" dismisses the question.

**Trade-off canvas**
- **Axes**: user-selectable x (all in real units):
  - $ per task, log scale
  - input $ per 1M tokens, log
  - time to first token in ms, log
  - output tokens/s, linear
  - context length in tokens, log

  y is any benchmark valid for the model type, in that benchmark's own unit.
- **Plot height**: 460px (300px in table-first layout). There's a 52px y-label gutter and a 30px x-tick row; tick labels are mono 10.5px.
- **Marker encoding** (colour is never the only cue):
  - Qualifies, independent: filled `--accent`, 13px.
  - Qualifies, lab-reported only: `--surface` fill with a 2px `--accent` ring.
  - May qualify: 2px dashed `--warn` ring.
  - Excluded: 8px `--faint` at 45% opacity.
  - Selected: 16px, with a double ring `0 0 0 3px surface, 0 0 0 5px ink`.
  - Intervals: 2px vertical bars at 45% opacity.
- **Frontier**: 2px `--ink` line through the Pareto set of qualifying models (cheaper and better).
- **Direct labels**, 12px weight 600, on frontier, shortlist, selected and may-qualify points. There's a simple vertical collision offset of 15px steps, and labels flip to the left when a point is past 72% of the width.
- **Draggable constraint handles**, both `role="slider"` and keyboard operable (arrow keys, Shift for bigger steps):
  - The x cap or minimum is a vertical `--accent` line with a label such as "≤ $0.10".
  - The benchmark floor is a horizontal line with a label such as "CodeBench Pro ≥ 45.0% · independent".
  - The infeasible side is shaded `--surface2` at 75%.
  - With no condition set, the handle sits ghosted at 50% at the edge with "Drag to set a cap".
  - Dragging creates or updates the matching condition. Values snap: $ to 2 significant figures, ms to 10, tok/s to 5, context to standard sizes, benchmark to 0.5 (0.005 for nDCG).
- **Winning strip** (26px): "Best {benchmark} you can get at each {axis} cap". Segments are labelled with the model name, and the current #1's segments use `--accentSoft`.
- **Tooltip on hover or focus**: name, lab and offering, y value ± interval with its provenance, x value, and status with the reason.
- **"Not plotted"** line: lists models that are unknown on the chosen axis.
- **Nothing qualifies**: a centred overlay card listing the top 3 near misses, each with a "Relax to …" button.

**Shortlist** (400px column; 420px in table-first)
- **Cards**:
  - Best overall for your weights
  - Best value (most benchmark per $)
  - Cheapest that clears your bar
  - Best open weights

  If the same model fills two roles, the later card says "same as …". A card with no qualifying model says so plainly.
- **Card layout**:
  - The role in mono `--accent`.
  - Name 17px weight 600.
  - "lab · via provider".
  - A 3-column metric row: benchmark ± interval with provenance, $ per task, output tok/s.
  - A `--warnSoft` note when relevant: not separable, ranked on a lab-reported score, or outside a soft preference.
  - The selected card has an `--accent` border.
- **May qualify panel**: 1px dashed `--warn` border. Each row gives the reason it's unknown, e.g. "Unknown: no independent CodeBench Pro yet; lab reports 64.0%", with a "Provisional" tag where it applies.

**Decision table**
- **Sorting**: click a column header to sort; `aria-sort` is set on the headers.
- **Columns**: #, Model · lab, Offering, benchmark ± interval with ● ind. or ○ lab, $ per task, In $/1M, Out $/1M, First token, Tok/s, Context, Weights, Status · reason.
- **Rows**: excluded rows show at 62% opacity and can be toggled off. The selected row uses an `--accentSoft` background.
- **"Eliminations by condition"**: models grouped by the condition that first removed them.

### 03 Why panel (selected model)
- **Header**:
  - Name 24px weight 600.
  - "lab · released date (N days ago)".
  - Outline badges: type, weights and licence, Provisional (`--warn`), Retired (`--bad`).
  - Status on the right: "Qualifies · #k of N", "May qualify" or "Excluded", with the reason.
- **Banners**, when they apply:
  - Provisional, dashed `--warn`: "Released N days ago. X lab-reported scores, Y independent. Speed not yet measured. Scheduled updates at +1, +7 and +30 days."
  - Retired, in the live archive.
  - "Evidence too thin to separate these", with both intervals.
- **Three columns** (auto-fit, min 320px):
  1. **Contribution bars**:
     - Each is a 10px track: the outline is the weight set, the fill is the share of it earned.
     - Each is labelled with the real value and the qualifying field's range.
     - There's an explicit note that conditions never add points.
     - **Tipping point**: text such as "X stays #1 while the $ per task weight is between a and b. Above b, Y takes #1." A band marks the stable range, and a live slider sets the cost weight.
  2. **Evidence rows**:
     - Benchmark, value ± interval or "no interval", then unit · effort · harness · date.
     - A provenance button: "Independent" (neutral) or "Lab-reported" (`--warn` on `--warnSoft`). It opens a popover with value, measured by, effort, harness, date and source URL.
     - Then facts, and "What the lab didn't report".
  3. **Condition checks** for the chosen offering:
     - Each condition gets ✓ pass, ? unknown, ~ soft miss or ✕ fail, with an aria label and the reason.
     - "What each condition costs you": points of the benchmark lost, as a 4px bar, plus a note on the best model you'd get without it.
     - Near misses with "Relax" buttons.
     - A "Why not…" select that explains any model.
- **Offerings table**: every provider for the model with regions, in and out $/1M, $ per task, TTFT, tok/s, retention, and the result against the conditions. The offering used for ranking is highlighted. Above the table, the $ per task formula is printed in mono.

### 04 Share or act (modal)
- **Overlay**: `rgba(11,20,38,.45)`. The dialog is 860px max, radius 3px. Escape and a click outside both close it.
- **Tabs**:
  - **Permalink**: the spec base64-encoded in the hash.
  - **API call**: curl with a JSON spec.
  - **CLI**.
  - **Spec YAML**.
  - **Save and alert**: three checkboxes (a new model beats this pick; this pick's terms change; retirement), then "Save and watch".
  - **Procurement review**: a clause table giving Yes/No/Unknown with evidence and sources, plus "Download CSV".
- The code tabs use mono 12.5px on `--surface2` with a Copy button.

## Interactions & behaviour
- **No page reloads.** Every change to the spec re-evaluates straight away. Points, intervals, handles, funnel bars and contribution bars animate `left/top/width/height` over 0.55s with `cubic-bezier(.2,.7,.2,1)`.
- **`prefers-reduced-motion`** turns every transition off.
- **Spec in the URL.** The spec is written to `location.hash` (`#s=<base64 JSON>`) on every change and restored on load.
- **Snapshot ID** is deterministic from the spec: `snap_2026-09-24_<hash>`.
- **Selection.** Clicking a canvas point, card, may-qualify row or table row selects that model and drives the why panel. The default selection is the #1, or failing that the first may-qualify model.
- **Escape** closes the modal, popover, add-condition search and editor.
- **Responsive.** Below 1200px wide the results grid collapses to a single column. The header hides the snapshot ID below 1100px. Mobile is not designed yet.
- **Simulated states** (props or tweaks): `simulate: loading` shows skeletons with "Loading snapshot … · 25 models, 60 offerings". `simulate: error` shows an alert, "Couldn't load snapshot …", with Retry, and hides results rather than showing stale ones.
- **Layout and theme** can also be forced with `?layout=table` and `?theme=dark`.

## Engine rules (see `modelspec-data.js`)
- **Offering statuses.** Each condition tests to pass (1), unknown (0) or fail (−1) per offering. An offering fails if any hard condition fails, is unknown if it has any unknowns, and passes otherwise. A soft condition's fails are flagged, not excluded.
- **Model status and chosen offering.** A model takes the best status among its offerings. The chosen offering is the one with fewest fails, then fewest soft misses, then the cheapest (or the fastest if the speed weight is above the cost weight).
- **Funnel.** A model "drops at" the first condition prefix where none of its offerings survives.
- **Ranking** runs only over qualifying models that have a primary-benchmark result. Qualifying models without one go to may-qualify as unranked. The score is a weighted sum of min-max normalised values: the benchmark (independent value preferred, lab value used and flagged if that's all there is), the log of $ per task inverted, and tok/s (unknown counts as 0). **Conditions never add points.**
- **Frontier**: the Pareto set on the chosen x axis versus the benchmark.
- **Not separable**: the difference between two models is less than the combined interval (√(ci₁² + ci₂²)) and their costs are within 2×.
- **Constraint cost**: re-evaluate without each condition and compare the best benchmark value.
- **Near miss**: an excluded model where one of its offerings fails exactly one condition. `relaxValue` gives the minimal change that would let it in.
- **Tipping point**: sweep the cost weight from 0 to 1 in steps of 0.01, keeping the other weights' ratio, and find where #1 changes.
- **Next questions**: candidate facets not yet set, each option re-evaluated, sorted by the most models removed.
- **Task parse**: a deterministic keyword classifier, standing in for the small classifier model. It returns conditions, weights, a primary benchmark and a trace.

## State
`view` (arrive or work) · `spec` {task, tokIn, tokOut, bench, w{cap,cost,speed}, conds[]} · `xAxis` · `sel` · `edit` (condition id) · `addOpen`/`addQ` · `dismissed[]` · `sortK`/`sortDir` · `showExcl` · `hover` · `prov` (popover) · `share`/`shareTab` · `alerts{}` · `theme` · `layout`.

Condition shapes:
- `{f:'type', v}`
- `{f:'active'}`
- `{f:'ctx', min}`
- `{f:'open', v:true|false}`
- `{f:'commercial'}`
- `{f:'bench', b, min, indep}`
- `{f:'task$', max}`
- `{f:'in$', max}`
- `{f:'resid', v:'EU'|'US'|'UK'}`
- `{f:'ret0'}`
- `{f:'ttft', max}`
- `{f:'tps', min}`
- `{f:'origin', ex:[]}`
- `{f:'rel', ref, b}`

Every shape also accepts `soft` and `from` (parsed from the task).

## Design tokens
The base is the attached design system, a Fluent-like palette. Font: Segoe UI Variable Text / Segoe UI / system-ui. Mono: Cascadia Code / Cascadia Mono / Consolas. **Tabular figures everywhere** (`font-variant-numeric: tabular-nums`).

| Token | Light | Dark |
|---|---|---|
| --bg | #faf9f8 | #0B1426 |
| --surface | #ffffff | #111d33 |
| --surface2 | #f3f2f1 | #18284a |
| --line | #edebe9 | #223452 |
| --line2 | #d2d0ce | #34496e |
| --ink | #201f1e | #f3f2f1 |
| --ink2 | #323130 | #e1dfdd |
| --muted | #605e5c | #a9b4c8 |
| --faint | #a19f9d | #6f7f9b |
| --accent | #0078d4 | #5aa9ec |
| --accentInk | #ffffff | #0B1426 |
| --accentSoft | #deecf9 | #15365a |
| --warn | #7a4a00 | #f4c95d |
| --warnSoft | #fff4ce | #3a3117 |
| --bad | #a4262c | #f28b94 |
| --badSoft | #fde7e9 | #3d1e24 |
| --good | #0b6a0b | #7fd07a |
| --navy | #0B1426 | #1d3a66 |
| --shadow | 0 10px 32px rgba(11,20,38,.16) | 0 10px 32px rgba(0,0,0,.5) |

- **Type scale**:
  - 52 (H1, 300)
  - 30 (funnel readouts, 300)
  - 24 (model name, 600)
  - 22 (task input on arrive)
  - 18 (task input in work view)
  - 17 (card name, lede)
  - 15 and 14 (body)
  - 13 and 12.5 (secondary)
  - 11.5 (mono labels)
  - 10.5 (mono ticks)
- **Radius**: 2px on controls and cards, 0 on panels (with the 2px ink top rule), 3px on the modal and logo, 50% on chart markers only.
- **Spacing**: gaps of 4, 6, 8, 10, 12, 14, 16 and 24. Panel padding is 14–18px and page gutters are 24px.
- **Colour use**: one accent (`--accent`) for qualifying data, handles and primary actions. `--warn` is reserved for may-qualify, provisional and lab-reported. There's no categorical palette and no brand-favouring colour.

## Assets
There are no raster assets. The logo is inline SVG (in the header of `ModelSpec.dc.html`). All model, lab, benchmark and provider names are fictional.

## Files
- `ModelSpec.dc.html`: the full core-flow prototype. The template holds the markup and inline styles; the logic class holds view-model derivation, drag handling and share formats.
- `ModelSpec Options.dc.html`: canvas-first and table-first, side by side.
- `modelspec-data.js`: the fictional catalogue and the reference decision engine.
- `support.js`: runtime for viewing the `.dc.html` files only; don't port it.
