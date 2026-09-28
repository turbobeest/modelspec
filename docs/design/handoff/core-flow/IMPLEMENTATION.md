# Decide page implementation

The new Vite entry is `web/decide.html`. It runs the fictional catalogue through
`web/src/decide/adapter/index.ts`. The existing web entry and the Python engine
are unchanged. The four original handoff files are retained verbatim in the
first commit; `support.js` is not part of the app.

Run `npm ci`, `npm run dev`, and open `/decide.html` from `web/`. Query parameters
accept `layout=canvas|table`, `theme=light|dark`, and
`simulate=loading|error`. The spec and axis round-trip through `#s=`.

The `DecisionEngine` interface is the only decision boundary. The reference
engine lives in `engine/reference.ts`, and only the adapter and its tests import
it. The UI sorts table columns and positions marks; the adapter owns selection
of offerings, ranking, frontier, winning strip, near misses, costs and questions.
`hostedEngine` is a typed, explicitly unconnected `POST /v1/decide` stub for
MODEL-151. It contains no fetch code.

## Contract mapping and differences

The adapter response passes the generated `decision-contract.schema.json`
when its separate UI explanation material is removed. That establishes its
shape, not equivalence to the future production decision engine.

1. The handoff's `task`, `tokIn`, `tokOut`, `bench`, `w` and `conds` remain the
   editable sample spec. The real contract uses `where` and `optimize`, has no
   token-count fields, and currently refuses free-text tasks. The sample's API,
   CLI and YAML tabs explicitly identify their formats as previews, not accepted
   production requests. MODEL-151 must supply the real request mapping.
2. Numeric offering statuses map to `results`, `may_qualify` and
   `eliminated.models`. A qualifier without primary evidence is unranked and
   shown as may qualify in every UI view, including Why and the table.
3. The sample treats all unknown conditions as may qualify. The real contract
   defaults governance unknowns to fail. The sample preserves its reference rule.
4. Soft misses only flag the sample result; `soft_penalty` is zero. Production
   soft conditions specify a positive penalty. No invented penalty is applied.
5. Model IDs become `lab/sample-id`. The chosen provider is retained. Sample
   offerings cover several regions and have no account tier, so the singular
   contract `region` and `tier` are null. The full region list remains in the
   UI explanation. A sample offering must not become several real offerings by
   guessing tiers or guaranteed facts.
6. Independent evidence becomes `independent`; lab evidence becomes
   `provider_self_report`. Values, units, dates, effort and source URLs are
   retained. Missing version, sub-category, count and source snapshot are null.
   Sample harness strings are not registered `name@major.minor` IDs, so contract
   harness is null and the original remains visible in the explanation. Sample
   evidence dates are represented as published, and directness as direct to
   the selected fictional benchmark, not as verified production claims.
7. Each fictional benchmark has a lowercase identifier in the evidence domain
   field. It is not a learned capability estimate or a registered real domain.
   `estimates`, `p_best` and `top3_stability` stay null. Raw reference evidence
   remains unblended. The primary benchmark contribution carries its evidence.
8. Contributions expose reference min-max normalisation, including inverted
   log cost. Conditions never contribute points. Lab fallback and soft misses
   have warning codes. The reference's handling of missing speed and prices
   remains unchanged and is confined to the fictional backend.
9. The reference funnel includes catalogue and ranked totals as UI-only steps.
   Contract funnel entries contain only conditions. The sample's `after` count
   includes unknown survivors and its may count is cumulative. Per-model
   elimination uses the first prefix at which no offering survives.
10. Constraint costs become `admits` and benchmark-unit `gain`. Unknown gain
    is an empty map, not zero. The better alternative remains in the explanation.
    Tipping bounds become individual `tipping_points`; the stable band stays in
    the explanation. The .01 sweep and fixed other-weight ratio match the sample.
11. Near misses and minimal numeric relaxation have no dedicated field in
    contract 1.0. They are `near_misses` in the UI extension. Contract `relax`
    contains a smallest condition-removal set when no ranked result exists.
    The handoff's relative condition also requires a cheaper offering; that
    extra requirement must become a separate condition in a real request.
12. `explanation`, `questions`, `frontier` and `winning_strip` are adapter-only
    display material, separate from the contract response. The contract has no
    free-form `explanation` field. Real responses must populate their declared
    fields and be adapted into this display material.
13. The displayed sample snapshot is `snap_2026-09-24_<12 hex digits>`, derived
    from sorted-key UTF-8 SHA-256 of the complete sample spec excluding editor
    IDs. Unlike the prototype's rolling hash, it includes task and benchmark,
    and survives hash restoration regardless of key order. It is not a signed
    catalogue snapshot or the canonical hash of a production contract spec.
    Warning codes make those limits explicit. The real backend owns real IDs.
14. UI weight sliders preserve the other weights' ratio without rounding the
    stored weights. Their labels show two decimals. The prototype rounds each
    stored weight independently, which can break the required sum of one.

## Accessibility and visual review

The screenshot matrix is indexed in [screens/README.md](screens/README.md).
It includes the app and the live handoff prototype at 1440 × 1000, light and
dark, canvas first and table first. Full-page captures include the Why panel,
all offerings, decision table and eliminations. Overlay captures cover every
share tab, condition editing, provenance, tooltip, loading and error states.

The prototype's original runtime is used only to capture reference screenshots.
The capture browser adds query-driven simulation to that viewer in memory,
because the viewer otherwise accepts simulation only as a component prop.
The committed reference files are not edited.

Two AA exceptions to exact colour treatment are deliberate. Small accent text
uses `--accentText` (`#006bbd` in light mode) where the handoff accent on the
page background falls below 4.5:1. The specified accent remains unchanged for
primary controls and chart data. Excluded table text uses `--muted` at full
opacity instead of reducing an entire row to 62%, which would reduce text
contrast below AA. The token-pair test checks all text surface combinations.

Handles expose values, orientation, units and arrow/Shift controls. The native
modal traps focus and restores it to its trigger. Copy reports success only
after the clipboard write succeeds. Saved alert preferences are a local preview;
no monitoring service or email delivery is claimed. Reduced-motion CSS disables
all transitions.

## Verification

From `web/`:

```sh
npm test
npm run test:browser
npm run build
npm run lint
```

The tests cover reference parity across 66 specs, literal adapter outcomes,
contract JSON Schema validation, token contrast, hash restoration, and rendered
interactions. Playwright covers pointer dragging, keyboard handles, table
selection and sorting, modal focus, clipboard, CSV, and reduced motion.

The existing v1 `DetailPanel.tsx` triggers the React hook lint rule
`set-state-in-effect`. That one pre-existing diagnostic remains visible as a
warning so `npm run lint` exits successfully without changing the component.
All new code uses the normal error rules.

The required Python command passed with 2,394 tests and 8 skips. No Python
engine, v1 rank output or `.github/` file changes in the app PR. Deployment is
a separate draft PR for Jamie to merge by hand.
