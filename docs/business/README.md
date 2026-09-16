# Business context

Read before product, pricing, licensing, API or data-pipeline work.

| File | What it is |
|---|---|
| [`BUSINESS_CONTEXT.md`](BUSINESS_CONTEXT.md) | Jamie's strategy handoff, 2026-09-16, **verbatim**. Goals, positioning, pricing, moats, exit. Its own figures are a claude.ai snapshot |
| [`repo-audit-2026-09-16.md`](repo-audit-2026-09-16.md) | that document measured against the tree. Where they disagree, **the tree wins** |
| [`data-policy.md`](data-policy.md) | what has to be published and how fresh. Open decision |
| [`decision-record.md`](decision-record.md) | **the business model as decided, 2026-09-16.** Newest; supersedes the open questions below |
| [`revenue-backlog.md`](revenue-backlog.md) | proposed tickets (`REV-n`) and the three decisions that gate them |

## Rules

1. **Flag, don't decide.** Open decisions are listed in `BUSINESS_CONTEXT.md`
   §11, `data-policy.md` and `revenue-backlog.md` Gate 0. When code work touches
   one, raise it with Jamie. Update the relevant decision log when it is settled.
2. **MODEL-3 is unblocked as of 2026-09-16**; the payment-rail work follows it.
   See `decision-record.md` §7.5. The holds still written into `CLAUDE.md`,
   `AGENTS.md`, `current.md` and `post-mvp-loop.md` are stale and are updated
   in the pass that starts the work. **MODEL-6 was cancelled on 2026-09-16** and
   superseded by MODEL-68, MODEL-69, MODEL-73 and MODEL-75; the architectural
   rules it carried alone were rescued into `decision-record.md` §10.
3. **Evidence discipline is the product.** Every rule in
   [`../handoff/README.md`](../handoff/README.md) applies here. A savings figure
   on a receipt, a `commercial_use` value and a benchmark score are the same
   kind of claim: sourced and dated, or null.
4. **The refusal is permanent.** No referral fees, no paid placement, no
   provider-paid visibility. See
   [`../agent-commerce-assessment.md`](../agent-commerce-assessment.md) §3.
5. **Three constraints are architectural, not aspirational.** No token
   proxying, profiles instead of prompts, source-neutral advice all the way.
   `decision-record.md` §10. They are the input to MODEL-70 (terms of service
   and privacy statement) and must not be restated from memory.
