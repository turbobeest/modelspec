# Round 3 objective source selection

Base: `53fde1fd302da4fd050758d42a4c5ead8bd7a593`. The root executor committed the correction in `09bbb4203e00fb99a72379c11801885a3f6dae7f`. This evidence covers REV-814 finding 2; the root executor owns browser and final broader verification.

`SimpleAnswer` now uses `simple/source.ts` to select its single source line. The selection rule is:

1. Read capability terms from `decision.blend` using `estimated: true`. Select the unique term with the largest positive share. Cost and other exact dimensions do not compete with capability terms. Equal largest capability shares have no single faithful source, so they use the fallback.
2. Consider only `answer.members`. For each member, use its best ranked offering's contribution for the selected signed dimension and refinement. The contract's member-evidence definition identifies this offering as the basis of the member's objective position. Another route's evidence can reflect a different harness or effort and is not substituted.
3. Identify the best offering from ranked `by_model.offerings`, with the lowest-ranked retained result as the fallback when that older optional model view is unavailable. Read matching contribution evidence from `results`, or from `top` when the best offering's result was cut by the limit. A nonzero global truncation count does not by itself remove a valid source. Domain evidence groups cannot replace objective contribution evidence.
4. Require enough contribution evidence to compare every verdict member. Missing estimate weights or missing member contributions use the fallback. Repeated nonempty contributions for the same offering must agree on record ID, estimate weight, directness, benchmark, date, and source URL. Evidence order does not matter; conflicting metadata uses the fallback.
5. Pool those member records and apply `decision/explain.py::_evidence_priority`: highest estimate weight, direct before proxy, then record ID. Record IDs use Unicode code-point order to match Python rather than locale or UTF-16 ordering. Equal priorities across members use model ID in the same order. Within one member, equal priorities that name different sources remain ambiguous and use the fallback.
6. Display the selected benchmark's vocabulary name and the evidence item's own date and URL. If its benchmark name is absent, use the fallback. Dates and URLs are required and validated by the existing decision schema; no date, benchmark, or URL is fabricated.

The fallback is exactly `Sources and dates: see the full evidence`. The existing primary evidence link remains available.

The unchanged assistant fixture still shows `Source: Arena WebDev (Code Arena), 2026-09-23.` Reordering results, member order, contributions, or evidence does not change it. A separated answer cannot borrow evidence from an unrelated result. The rendered regressions also cover cost-heavy blends, direct/proxy priority, Unicode record ordering, refinement dimensions, usable retained top evidence, unrelated truncation, missing metadata, and conflicting repeated offering data.

The existing asynchronous verdict-focus assertion is unchanged. No engine, schema, backend, browser fixture, generated artifact, or gate implementation was changed for this finding. No full Python suite, deployment, paid request, commit, push, or GitHub mutation was run by this worker. Browser tests are owned by the gates worker.

Commands, direct exit codes, and compact failure excerpts are in [results.txt](results.txt). The full web-unit run recorded there preceded the final duplicate-offering correction; the final correction was verified with all four simple-page suites and TypeScript checking. The root executor owns the final broader verification.
