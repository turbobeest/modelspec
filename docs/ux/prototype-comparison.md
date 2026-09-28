# Downselect prototypes: comparison and recommendation (MODEL-147)

*2026-09-24. Jamie picks the direction; this is a recommendation, not a decision.*
*Open the prototypes locally: `python3 -m http.server -d docs/ux/prototypes 8147`, then http://localhost:8147/a-guided.html. Every page shows the banner **FICTIONAL SAMPLE DATA**: the labs, models, providers, benchmarks and scores are invented.*

All three prototypes, the launch report and the social cards share one component block: the fictional data, a toy engine shaped like the decision response, spec⇄text⇄URL, and the SVG charts. `tests/test_ux_prototypes.py` fails if the blocks drift apart, if a page loads a script from anywhere but the two allowed CDNs (none loads any), or if a page loses its fictional-data label. Every prototype has live counts, a decision with contributions, P(best), why-not-X, constraint costs, tipping points and a share link. A link from any page opens in any other. To change a component, edit its block (between the `ms-components` markers) in one page and copy it into the other three.

| | **A · Guided conversation + chips** | **B · Live trade-off canvas** | **C · Decision table** |
|---|---|---|---|
| Entry | A sentence ("Refactor a Rust service, cheap, EU data only…") | A preset, or dragging on the chart | A condition builder, or a preset |
| The "pop" | The sentence lighting up as it becomes chips; one question at a time | Dragging the budget line and watching points fade, the frontier redraw and #1 change; the winner band; uncertainty as motion | Density: every facet, interval and reason in one place |
| Uncertainty | Icon array + plausible rank | Icon array, P(best) bars, rank spread, HOPs | P(best) bar, rank spread, interval bars in every cell |
| Why not X | Picker + sentence | Click any point | Expand any row: sentence + point deltas against #1 |
| What-if | Clarifying questions; weight steppers | Drag limits; slider with the winner band | Weight sliders; edit any condition |
| Progressive disclosure | Text → chips → raw spec | Toggles → drag → (raw spec via A or C) | Builder → raw spec tab |
| Best for | First-time builders, journalists, anyone with a task but no vocabulary | Cost/quality trade-offs; social posts landing here; demos | Platform engineers, compliance reviewers, researchers |
| Social cards landing here | Good: the spec's chips read as a sentence | **Best**: the card's chart becomes the live chart | Good for claims or eliminations posts |
| Phone | Good (a single column) | Weakest: dragging a 390 px chart is fiddly, so the sliders carry it | Table scrolls sideways; the builder stacks |

## Strengths and risks

**A, Guided.** *Strengths:* the lowest barrier. The conversation asks only what the decision can't yet tell apart (budget, then data rules, then unknowns, then "it's close, which matters more?"), which teaches the facets without a form. The echoed reading makes the resolver's interpretation checkable. *Risks:* it depends on the real resolver (the decision model) being right and fast. The prototype's keyword rules are a stand-in, and a misread chip that the user never notices is the worst failure. The conversation can feel slow to experts, and it is the least visual of the three.

**B, Canvas.** *Strengths:* the most exciting and the most honest at once. You *see* the constraint cost: points leave the feasible zone, near misses glow, the frontier moves. The winner band makes the tipping point a single glance. HOPs make a new model's wide interval visible as jitter, which is exactly the launch-report story. It is the natural landing page for a chart in a post. *Risks:* it shows two dimensions at a time, so governance and extra facets become toggles and a reader can miss that a toggle is on. It is weak on phones. A log-scale cost axis needs its caption. Readers may take the scatter position as the ranking when the weights say otherwise; the winner highlight and top-5 list mitigate this.

**C, Table.** *Strengths:* the most complete and auditable view. It shows every condition's count in order, each unknown policy as an editable field, eliminations grouped with reasons, and interval bars in every capability cell. It is the view a compliance reviewer or a DPF operator will trust. *Risks:* it is dense and intimidating for a first visit, and the least likely to "excite". A sortable table invites people to treat a sort as a recommendation (labelled, but still a risk). It needs horizontal scrolling on phones.

## Recommendation

**Build B as the main surface, with A's language box and chips as its header, and C as a "Table" tab over the same decision.**

- B carries Jamie's two hardest requirements, "graphs that pop" and "variables super intuitive", and it is where social cards land.
- A's box, echoed reading and chips give B a no-vocabulary entry point, and A's clarifying question when two options are close is the best tipping-point interaction found.
- C is the audit view power users will ask for. As a tab it costs little, because it renders the same decision.
- The launch report and cards need no changes. They are already drawn by the same components and link into any of the three.

The alternative, if a single view is wanted for slice 5, is **A+B without C**, adding C later from demand. **A alone** is not recommended: the hard problem is making trade-offs visible, and a conversation can't do that.

## Before building (open questions for Jamie)

1. **Usability tests** on the audit's recall-set questions (design §11), about 5 participants per profile (builder, platform engineer, journalist), using these prototypes with real snapshot data behind a flag. Measure time to a decision they'd defend, and whether they can say why #2 lost.
2. **The short link** (`modelspec.dev/d/<hash>`) needs either a small immutable store on the keyed layer or a static hash manifest. The fragment link works today with no store.
3. **Card copy** should be generated from the decision (P(best), interval, evidence counts), not written by hand. Worth deciding before MODEL-114's posting work.
4. **Colour of the accent:** the prototypes reuse the site's amber (`#f5b342` dark, a darker amber in light mode for contrast).
