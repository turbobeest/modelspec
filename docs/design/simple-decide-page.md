# Simple decide page

MODEL-404 starts from `72cd65f81aeae93add87b9a52157ae8cbce698a3`.
Jamie's decisions in the ticket govern where the two UX reviews differ.

## Page anatomy

`/decide/` shows the existing brand and theme control, a snapshot date from
`vocabulary.coverage.as_of`, the hero "Which AI model fits your job?", and
"Pick a job. See your options and what each task costs." A missing snapshot
date says it is unavailable; a hash or build time never substitutes for it.

The opening answer is labelled "Example: Everyday help. Pick a job if this
isn't yours." Six real buttons with `aria-pressed` choose a job. A three-way
priority control follows, then the collapsed "Hard limit: No hard limit.
Change" row. Choices update in place. After a deliberate choice settles,
focus moves to the verdict. The initial example does not claim a personal
choice. Priority and limit changes alone keep the example label until a job
is picked.

The answer begins with job, priority and effective limits. The engine's
`answer.members` determines the best group. Tied names sort alphabetically
and use identical rows, with no winner badge, ordinal or probability. A
separated answer names its leader and puts `bands.rest` in a closed expander.
Each row pairs a model with its cheapest confirmed ranked route and the
cost of that route. Unknown prices remain unknown; plans and hardware never
acquire an invented API price.

The full neutrality sentence sits beside the verdict at the same font size:
"ModelSpec is neutral: no referral fees, no paid placement." The answer
also shows the task token counts actually sent from vocabulary/template
metadata, the API-price qualification, a plain-language explanation derived
from `blend`, one dated benchmark from the response's evidence, model counts
from `by_model`, and the independent-measurement tie-breaker as a separate
sentence when supplied. No outcome, price, source date or count is hardcoded.

"See the full evidence" is the sole primary action. Its existing encoded
`#s=` board state preserves limits, weights, access route and task size.
The text "An agent can ask this same question. A key is required. Looking
this up here is free." links to agent documentation and pricing. The text
link "All {count} templates" uses the vocabulary's available-template count.
Legal, method and pricing navigation remains available.

At 390 by 844, compact job buttons can omit subtitles. Keep 44 px control
targets, all tied names and costs, the verdict and evidence action visible.
Supporting evidence text can follow the primary action when needed for the
fold. Never clip the tie, shrink qualifications below readable sizes, or
hide their meaning on mobile. Larger text and larger ties may scroll.

## Template mapping

Priority ids are the existing `budget`, `balanced`, and `best` tiers, labelled
"Spend less", "Balanced", and "Quality counts most". The helper always says
"Spend less still weighs quality. It is not the lowest price."

| Job | Spend less | Balanced | Quality counts most |
| --- | --- | --- | --- |
| Everyday help | `assistant-budget` | `assistant-balanced` | `assistant-best` |
| Coding | `budget-coding` | `coding-balanced` | `coding-best` |
| Writing | `writing-budget` | `writing-balanced` | `writing-best` |
| Long documents | `documents-budget` | `long-documents` | `documents-best` |
| High volume | `high-volume` | `high-volume-balanced` | `high-volume-best` |
| Self-hosting | `assistant-budget` plus self-host gates | `assistant-balanced` plus self-host gates | `assistant-best` plus self-host gates |

Self-host gates come from `private-self-host`: downloadable weights and
commercial use permitted, including permitted with conditions. They remain
through every priority. No new weights or thresholds are invented. Each
selected template retains its conditions, including built-in budget and
context limits, and its task size. High-volume templates specify 2,000/500;
the other templates use the vocabulary defaults. Effective conditions are
disclosed even when introduced by a priority. Missing or unavailable
templates disable that choice instead of silently choosing another job.

## Limits and route

The opened row says "We will only shortlist confirmed matches." Independent
toggles can combine the supported conditions below. A facet must be editable
in the current vocabulary before the page offers its condition.

| Control | Existing condition or request field |
| --- | --- |
| Open weights | `model.weights_openness = open_weights` from `private-self-host` |
| EU residency | Only the `offering.region in {...}` condition from `eu-data` |
| No customer-data training | Only `offering.data.trains_on_customer_data = false` from `eu-data` |
| Route | Existing `access`: unset, `chat_app`, `coding_tool`, `own_software`, `own_hardware` |

EU residency never implies the training condition. Region availability and
confirmed residency are different: an unknown location stays possible, never
becomes a confirmed match. Route choices live inside this same expanded row.
The initial route is unrestricted and does not assert a plan or hardware fit.
An own-hardware answer labels unpriced hardware costs honestly. Additional
numeric limits remain available on the full board, while the selected
template's existing budget gates remain intact.

## Requests and gates

Reuse `loadVocabulary`, `prepareVisit`, `hostedEngine`,
`prepareDecisionRequest`, `decisionAction`, `HumanGate` and `VisitGate`.
The page sends the same summary/full POST `/v1/decide` requests and headers
as the detailed page. The visit gate precedes vocabulary access. Manual human
mode waits for verification and the explicit lookup; it never auto-spends a
human action. One action covers summary and full. Edits cancel stale work;
snapshot changes reload vocabulary; failures provide retry. No production
switch, endpoint, contract, ranking rule or access policy changes.

## Routing and link inventory

The current board moves intact to `/decide/details/`. Before React mounts
on `/decide/`, a URL whose hash begins `#s=` or whose query has `template`
uses `location.replace('/decide/details/' + search + hash)`. Keep the query
and fragment byte-for-byte. Bare `/decide/` remains the first-visit page.

| Owner | Links that move to details |
| --- | --- |
| Landing page and generated landing chrome | Facet-board, template and refinement links; introductory choose-a-model links stay simple |
| Method and about pages | Links describing requirements, controls, evidence and trade-off board |
| Use-case pages | All template-specific and board-state examples, including the current #811 equivalents |
| Pricing, feedback and brand pages | Links explicitly promising the detailed board |
| Agent copy and generated CLI agent bundle | The detailed structured-question UI and template links |
| MCP copy | Links describing the decision board and template examples |
| Detailed UI and shared decision links | Board reset, permalink, share, feedback page identity and return-to-board links |
| Pipeline entity and social metadata | Board identity and detailed template destinations; distinct simple-page metadata |

Vite serves both production paths in development and preview. The Python
builder, `pipeline.live`, structured data and social-card metadata compose
both pages. Both canonical URLs enter the sitemap with source-derived,
deterministic lastmods. The surface lint inspects both. Existing detailed
browser and corpus checks follow the moved route.

## Empty, undetermined and error states

For `no_feasible`, say "No confirmed match." Display the blocking conditions
the engine supplies in `relax` and offer to remove a named selected limit.
Distinguish missing facts from confirmed failures. Removing one condition
keeps the other requirements and never happens automatically.

A selected route can lack the objective measurements needed for a comparison,
even when no hard condition failed. For that state, explain that no comparison
is available for the selected route and offer "Try all routes". That explicit
action removes only the route restriction; it preserves the job, priority,
other limits and workload. It does not promise a match or change the weights.

When `answer` is absent, say the evidence cannot determine a shortlist for
the selected job. Do not call thin or unranked models a best group. Preserve
the job and link to the evidence. A request failure says the answer could
not load and offers retry; old rows never appear beneath new choices.

If a snapshot refresh changes the actual question, stop before requesting the
changed question and require another lookup. Metadata-only refreshes reuse the
existing action. This avoids spending another admission without a visitor's
choice. Re-selecting a job or priority restores its template's requirements,
including Self-hosting's defining gates, while retaining explicit extra limits.

## Verification

The agreed test seams are the rendered React page, its real board/request
conversion, the intercepted HTTP boundary in Playwright, and the composed
site. Before implementation, record failing tests for the labelled example,
job changes, tie order and emphasis, state handoff, legacy redirects, limits,
empty/undetermined states and mobile fold. Mutation tests change response
members, prices, counts, sources and blend, plus vocabulary token/date/count
metadata, and require the displayed facts to change.

Run the existing detailed suites on their new path and new simple-page
checks under all four build-flag gate combinations. Verify keyboard focus,
44 px targets, light/dark contrast and no horizontal overflow. Save desktop
and mobile screenshots of the example, Coding, a tie, no-fit and details in
`docs/evidence/g2-ios/MODEL-404/`. Run the site build, web build/unit/browser
suites, composition, surface/sitemap/dead-link checks and the full pytest
suite under `/tmp/modelspec-fullsuite.lock`. Record commands, versions,
red/green results, changed pins and unobserved behavior in the fix evidence.

The first commit contains only this design. The PR stays a draft for the
independent cross-model review and Jamie's review.
