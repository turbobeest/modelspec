# Downselect UX research (MODEL-147, phase 1)

*Research and prototypes only. No production code. Written 2026-09-24.*
*Vocabulary: `CONTEXT.md` on the `design/decision-engine` branch. Design: `docs/design/decision-engine.md` §6, §7 and §11 (slice 5).*
*Prototypes: [`prototypes/`](prototypes/). Comparison and recommendation: [`prototype-comparison.md`](prototype-comparison.md).*

## The job

A person arrives with a task and some rules, some of which they haven't stated yet. They leave with a **decision** they trust enough to act on, and with a link that reproduces it. The page has to do three things that today's model pickers don't:

1. **Filter honestly.** Constraints eliminate. Unknown values are shown, not dropped (design §3, principles 1–3).
2. **Rank with visible uncertainty.** Intervals, P(best) and plausible rank take the place of a false-precision score.
3. **Explain.** It says why #1 won, why each other model didn't, what each constraint costs, and at what point #1 would change.

The same components have to draw the launch report and the social cards, because every chart in a post is a saved spec that deep-links back to this page (MODEL-114, design §11).

All four prototypes run on one toy engine whose output follows the decision response in the DPF integration spec §7: `results` with `p_best`, `top3`, `contributions`, `may_qualify`, the `eliminated` funnel and models, `constraint_costs`, `tipping_points`, a `decision_id` and a `snapshot`. When `decision/contract.py` lands (MODEL-135), each page swaps `MS.decide` for the real call, and nothing in the UI changes shape.

---

## Principles

**P1. The count is the heartbeat.** Every control shows, before and after it's used, how many offerings survive. Chips show the count left after that condition, toggles show their delta (`EU only −12`), and the "+ add condition" menu previews the result (`Zero retention: yes (→ 9)`). Baymard found that showing each option's match count builds confidence before a click, that real-time updating is expected, and that 28% of sites give no overview of applied filters, which disoriented users in testing [2][3].

**P2. Unknown is a third state, and it's visible.** A capability unknown is listed as "may qualify", hatched in the funnel and dashed in the scatter. A governance unknown counts as not satisfied, and the reason says "not documented". No view drops a row silently. That rule is the product's core promise (design §6.2), and the UI is where a user checks it.

**P3. Uncertainty in frequencies, not decimals.** Show P(best) as "best in 62 of 100 resamples" in a 10×10 icon array, and rank as a plausible range (`#1–5`). Frequency framing, quantile dotplots and hypothetical outcome plots beat density plots and bare error bars for untrained readers [10][11]. Icon arrays help people with low numeracy [28]. Arena moved to reporting a rank spread for the same reason [17].

**P4. Show the interval that matches the question.** An interval around an estimate of capability is inferential uncertainty. Readers shown confidence intervals over-estimate effects compared with readers shown prediction intervals [12]. Label ours as "estimate interval" and never as "range of results you'll get". Avoid hard-edged bands around a moving line: the hurricane "cone of uncertainty" is read as the storm growing [13]. The prototypes use thin whiskers and a HOPs toggle instead.

**P5. Every number is one click from its evidence.** Contributions break the score into dimensions. Each dimension names its normalisation (`coding 68–82, cost $0.013–$0.30, lower is better`), and each estimate leads to its evidence rows. People given "why" and "why not" explanations understood a system better and trusted it more [14].

**P6. Why not X is a first-class query, not a tooltip.** It is one sentence of one of four kinds: eliminated on a named condition with the value; a near miss with the gap (`8% over the budget`); may qualify with the unknown facet; or ranked lower, with the dimension it lost on and the one it gained on.

**P7. Show the tipping point instead of hiding it.** "Coding weight 60%: #1 changes below 30% → Ossify Coder 2." Prototype B draws this as a **winner band**, a strip showing who is #1 at every setting of the trade-off slider. One glance shows how robust the answer is. This is explorable explanation applied to a decision [16].

**P8. Two levels of disclosure, plus the raw spec.** Presets, then chips and "+ add condition", then the raw spec text. NN/g warns that more than two levels of disclosure lose people [1], so the raw spec is a separate *mode* (a tab or a `<details>`) and not a third nested level. It is the same text an agent sends, parsed with loud errors (`unknown facet “colour”`).

**P9. Plain language becomes editable chips, and the mapping is shown.** Echo the words that were read (`Read as: “Refactor…cheap…EU…never train”`) and turn each phrase into a chip the user can correct. Atlassian's structured queries convert only the parts of a sentence that map deterministically to filters and treat the rest as a query [5]. Linear's AI filter produces ordinary filters that live in the URL [6]. The resolver must never apply an invisible condition.

**P10. A decision is a URL.** The spec plus the snapshot ID live in the fragment (`#spec=…`), so the link reproduces the decision (design §3, principle 8). Every prototype reads the others' links, the launch report links into all three, and each social card carries one.

**P11. Motion explains change, never decorates.** Animate what changed: a point crossing the budget line, a funnel bar shrinking. Keep transitions short. Heer and Robertson found animated transitions improve graphical perception, and recommend durations around one second [15]. Everything honours `prefers-reduced-motion` [26], and the HOPs animation is opt-in.

**P12. Pop comes from emphasis, not colour count.** One accent (amber) marks the winner or the report's subject; everything else is neutral. Label the winner and the frontier directly, and leave the other points unlabelled [23][24]. Categorical colour appears only in contribution bars (up to five dimensions, in the reference palette order), always with a legend. Non-text marks meet 3:1 contrast in both themes [25].

---

## Patterns, by question

### Faceted search done well
- A persistent applied-filter bar at the top, as chips with × and the count after each [2].
- Counts on options *before* they're chosen [3], and dynamic facets that hide options that would give zero results [4]. We deliberately *show* zero-result options with their count instead of hiding them, because "nothing qualifies with SOC 2 in AP" is itself an answer.
- Facets grouped by risk direction. Governance facets carry a distinct border and the note "documented, never compliant" (design §5).

### Multi-criteria decisions
- **LineUp** (InfoVis 2013 best paper): table columns as bars, a stacked "why it scores" column, and interactive weights with instant re-ranking [7]. Prototype C is LineUp adapted for three-valued filtering.
- **ValueCharts**: exposes the linear model's weights and each alternative's per-objective contribution [8]. That is our `contributions` block.
- **Choice overload** is weaker than folklore says. A meta-analysis of 50 experiments found a mean effect near zero with high variance [9]. The lesson is to show many options once they're well organised, grouped as ranked, may qualify and eliminated, rather than hiding options.

### Pareto frontier
- A scatter of capability estimate against cost per task (log scale, cheaper on the left), with the non-dominated set joined by a dashed line.
- Draggable limits (a vertical budget line and a horizontal capability floor) with a tinted feasible zone. Points that leave the zone fade to hollow; points within 15% of a limit get a warning ring and a "near miss, 8% off" label.
- One axis only. Speed and governance are toggles or filters, not a second y-axis.
- We considered parallel coordinates for more than two dimensions, and left them out of the prototypes. They reward experts and lose a general audience; the decision table covers the high-dimension case better.

### What-if and tipping points
- Relaxation costs: "Dropping ‘Region in EU’ lets 8 more in, and Tern T-3 would win (+3 coding, +$0.001/task)". This is `constraint_costs` from design §6.5.
- The winner band (B), tipping sentences (A, C), and a clarifying question when two options are close (A: "It's close… which matters more?").

### Showing uncertainty people read correctly
- Icon array for P(best), rank spread in place of a single rank, and whiskers for estimate intervals.
- HOPs: B's "uncertainty as motion" toggle cycles through 40 resamples of the estimates, so points jitter in proportion to their uncertainty [11]. A wide-interval new model visibly jumps around; a well-evidenced one sits still.
- Provisional badges on anything released in the last 7 days, and "deprecated" warnings (design §4.1).

### Explaining eliminations
- A funnel of counts after each condition, in order, with the "may qualify" share hatched.
- Eliminated rows grouped and collapsed by default, each with its reason and near misses flagged, and expandable into a diff against #1.

### Progressive disclosure and the language box
- A: text box → echoed reading → chips → an optional raw spec in `<details>`.
- C: presets → condition builder rows (facet, operator, value, unknown policy) → a raw spec tab.
- The unknown policy is editable per condition, and each default is shown as text ("unknown: fail (default)").

---

## Today's leaderboards and model pickers: what they do and what they get wrong

| What they do | What misleads | What's missing (and our answer) |
|---|---|---|
| **Preference arenas** rank by pairwise votes, now with a rank spread and a style-controlled view [17]. | Undisclosed private testing and best-of-N submission inflate some providers' scores. Closed models get more battles [18]. The number-one spot is often a statistical tie. | Constraints, cost and governance. We show rank spread and P(best) as first-class, and record who measured each result. |
| **Static benchmark leaderboards**: the Open LLM Leaderboard ran 2 years and evaluated over 13,000 models before it was retired in March 2025 [19]. | Saturated or contaminated benchmarks keep ranking models after they stop separating them. Its maintainers said it could encourage "hill climbing irrelevant directions" [19]. Secondary sources report contamination and self-reported scaffold results at the top of popular coding boards (not checked against primary sources; treat as a lead) [22]. | No fixed benchmark list (ADR 0002). Evidence is dated, qualified by who measured it and at what effort, and shown per domain. |
| **Independent benchmarking hubs** run evaluations themselves with documented settings, show ±1 SE intervals and publish CC BY data [20]. | Little, apart from coverage: they answer "how good?" and not "which one for me?" | They're a source, not a competitor. We credit them and show their provenance as `measured_by: independent`. |
| **Usage rankings** rank by tokens routed through one gateway [21]. | Popularity reads as quality. They count one gateway's public traffic, not the market. | Keep usage out of the score. At most, show it as a clearly labelled facet. |
| **Pickers and comparison tables** list every model with columns and sort. | A sort treated as a recommendation; one "overall" score; missing values blank or zero; no dates; the lab's own numbers shown as fact. | Everything in this document: honest filtering, unknowns, intervals, provenance, explanation, reproducible links. |

The common failures are single composite scores with false precision, unknowns shown as blanks or zeros, no evidence date, lab claims mixed silently with independent runs, sorting presented as deciding, and no way to state your own constraints.

---

## Charts that pop and stay honest

- **One accent.** The winner or subject is amber; the frontier is ink; everything else is neutral grey. Eliminated points are hollow and faded, not deleted, so the user sees what the rules removed.
- **Direct labels,** selectively: the winner, the frontier and near misses. Never a number on every point [23][24].
- **Themes.** Light and dark are defined as tokens on `:root`, with dark under `prefers-color-scheme` and a `data-theme` override that works on any element. The social cards use this to render dark or light independently of the page.
- **Accessibility.** Every SVG has `role="img"` and a summary `aria-label`. Status is never shown by colour alone: "?" plus the text "not documented", "near miss" as a word. Sliders mirror every drag handle for keyboard use. Marks meet 3:1 contrast [25]. Reduced motion is honoured [26].
- **Motion.** Short transitions on the funnel bars and on dot positions, and HOPs only on request.
- **A watermark in every chart** ("FICTIONAL SAMPLE DATA" in the prototypes). In production it becomes the snapshot ID and date, so a screenshot is still traceable.

### Social card sizes (read 2026-09-24; all from secondary guides, so re-check against the platforms' own help pages before launch)

| Network | Use | Size | Notes |
|---|---|---|---|
| X | Link card (`summary_large_image`) | 1200×628 (≈2:1) | X's stated ratio is 2:1; 1200×628 is the Open Graph convention that also works [27a][27b] |
| X | In-feed image | 1200×675 (16:9) | used for the prototype card [27c] |
| LinkedIn | Link share | 1200×627 (1.91:1) | [27d] |
| Instagram | Portrait feed post | 1080×1350 (4:5) | Profile grid crops to about 3:4; keep text within a central safe zone about 1012 px wide [27e] |

---

## The launch report

Design §11 sets its contents. The mock shows this order:

1. **Hero:** name, lab, release date, a *provisional* badge, the permalink (`/launch/<model>/<release date>`), and an update timeline (+1, +7, +30 days, then the normal re-check cycle). Four stat tiles: coding estimate with interval, P(best) for a reference spec, cheapest offering's cost per task, and independent runs against lab claims.
2. **Claims against independent evidence:** a dumbbell chart (hollow = lab claim, filled = independent), with "no independent run yet" and "lab did not report" written out.
3. **Standing per domain:** interval strips against the five closest competitors, one small multiple per domain. The strips are unblended, matching slice 1.
4. **Trade-offs:** the frontier scatter with the subject highlighted, and a link that opens it in the trade-off canvas with the same spec.
5. **What the lab didn't report,** and **what's still unknown:** the unknown facets, with the policy each triggers.
6. **Social cards:** views of sections 2–4 at each network's size. Each has an honest headline ("…but its interval is wide"), the caveat in the caption, a spec link, and the snapshot or watermark.

A headline must never state more than the interval supports. Card copy should be generated from the decision (P(best), interval, evidence counts) rather than written by hand, so it can't drift from the data.

## Shareable spec URLs

- Put the spec as base64url JSON in the fragment: `#spec=…&view=canvas|table|launch`. The fragment never reaches a server and needs no store, which fits the static Pages path. It includes the snapshot ID, so the decision reproduces.
- For production, add a short, human-readable path that resolves to the same spec: `modelspec.dev/d/<hash>`, as the cards show. It needs a small immutable store, which is a keyed-layer decision for Jamie, or a hash-only static manifest built at export.
- Every view accepts every other view's link. A post links to B, a reader switches to C, and the spec carries over, as the prototypes' nav already does.

---

## Anti-patterns to reject

- A single "overall score" with decimals.
- Blank or zero standing in for unknown.
- Sorting a column and calling it a recommendation. C labels sorting as "view only; ranking unchanged".
- Colour by rank, so survivors repaint when a filter changes. Colour follows the entity.
- Two y-scales on one chart.
- Hiding eliminated options entirely. Fade them and give the reason.
- Hard-edged uncertainty bands [13].
- A resolver that applies conditions the user can't see or edit.
- Wizards more than two levels deep [1].
- Social copy written by hand and disconnected from the decision.
- Naming or sourcing an excluded source anywhere (`tests/test_removed_sources.py`).

---

## References

All were read or searched on **2026-09-24**. "(summary)" means the claim rests on a search-result summary of the page, not a full reading. Check those before quoting them in public.

1. Nielsen, J. "Progressive Disclosure." NN/g, 2006-12-03. https://www.nngroup.com/articles/progressive-disclosure/
2. Baymard Institute. "Filtering UX: Display ‘Applied Filters’ in an Overview." https://baymard.com/blog/how-to-design-applied-filters (summary)
3. Baymard Institute. "What Is an Ecommerce Filter? UI Best Practices." https://baymard.com/blog/ecommerce-filter-ui (summary)
4. Nielsen Norman Group. "Ecommerce UX: Search, including Faceted Search" (report). https://www.nngroup.com/reports/ecommerce-ux-search-including-faceted-search/ (summary)
5. Atlassian. "Structured Queries: Enhancing Search with Natural Language and Filters," 2026-05-13. https://www.atlassian.com/blog/company-news/enhancing-search-with-natural-language-and-filters
6. Linear. "Filters" (docs). https://linear.app/docs/filters
7. Gratzl, S., Lex, A., Gehlenborg, N., Pfister, H., Streit, M. "LineUp: Visual Analysis of Multi-Attribute Rankings." IEEE TVCG 19(12), 2013. https://vdl.sci.utah.edu/publications/2013_infovis_lineup/
8. Carenini, G., Loyd, J. "ValueCharts." AVI 2004. https://www.cs.ubc.ca/group/iui/VALUECHARTS/ (summary)
9. Scheibehenne, B., Greifeneder, R., Todd, P. M. "Can There Ever Be Too Many Options? A Meta-Analytic Review of Choice Overload." J. Consumer Research 37(3), 2010. https://academic.oup.com/jcr/article-abstract/37/3/409/1827647
10. Padilla, L., Kay, M., Hullman, J. "Uncertainty Visualization." 2022. http://space.ucmerced.edu/Downloads/publications/Uncertainty_Visualization_Padilla_Kay_Hullman_2022.pdf (summary)
11. Hullman, J. et al. "Hypothetical Outcome Plots Help Untrained Observers Judge Trends…" https://users.eecs.northwestern.edu/~jhullman/hops_jobs_pfs.pdf (summary)
12. Hofman, J., Goldstein, D., Hullman, J. "How Visualizing Inferential Uncertainty Can Mislead Readers About Treatment Effects in Scientific Results." CHI 2020. https://dl.acm.org/doi/10.1145/3313831.3376454
13. Ruginski, I. et al. "Non-expert interpretations of hurricane forecast uncertainty visualizations." 2016. https://escholarship.org/uc/item/96s9t7g5 (summary)
14. Lim, B. Y., Dey, A. K., Avrahami, D. "Why and Why Not Explanations Improve the Intelligibility of Context-Aware Intelligent Systems." CHI 2009. https://dl.acm.org/doi/10.1145/1518701.1519023 (summary)
15. Heer, J., Robertson, G. "Animated Transitions in Statistical Data Graphics." InfoVis 2007. https://idl.cs.washington.edu/files/2007-AnimatedTransitions-InfoVis.pdf (summary)
16. "Explorable explanation" (on Victor, B., "Explorable Explanations," 2011). https://en.wikipedia.org/wiki/Explorable_explanation (summary)
17. Arena. "Ranking method," published 2025-11-14, updated 2026-02-28. https://arena.ai/blog/ranking-method/
18. Singh, S. et al. "The Leaderboard Illusion." arXiv 2504.20879; NeurIPS 2025 Datasets and Benchmarks. https://arxiv.org/abs/2504.20879 (summary)
19. Hugging Face. "End of the Open LLM Leaderboard" (discussion #1135). https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard/discussions/1135 (summary)
20. Epoch AI. "About: Benchmarking." https://epoch.ai/benchmarks/about
21. OpenRouter. "LLM Rankings." https://openrouter.ai/rankings (summary)
22. Secondary reports on SWE-bench Verified contamination and self-reported top scores, e.g. https://www.digitalapplied.com/blog/swe-bench-verified-june-2026-benchmark-vs-scaffolding-analysis (summary; primary sources not checked)
23. Datawrapper. "What to consider when using text in data visualizations." https://www.datawrapper.de/blog/text-in-data-visualizations (summary)
24. Datawrapper. "What to consider when creating line charts." https://www.datawrapper.de/blog/line-charts (summary)
25. Deque. "1.4.11 Non-text Contrast (AA)." https://dequeuniversity.com/resources/wcag2.1/1.4.11-non-text-contrast (summary)
26. MDN. "prefers-reduced-motion." https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion
27. Social image sizes: (a) https://og-image.org/learn/twitter-card-size (b) https://devcommunity.x.com/t/twitter-card-summary-large-image/144086 (c) https://moda.app/resources/sizes/twitter-card (d) https://buffer.com/resources/social-media-image-sizes/ (e) https://buffer.com/resources/instagram-image-size/ (all summaries)
28. Galesic, M., Garcia-Retamero, R., Gigerenzer, G. "Using icon arrays to communicate medical risks: Overcoming low numeracy." Health Psychology 28(2), 2009. https://pure.mpg.de/view/item_2099767 (summary)
