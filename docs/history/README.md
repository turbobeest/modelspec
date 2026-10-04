# History

Records that explain how ModelSpec got here. None of it is current policy; the
current entry is [`AGENTS.md`](../../AGENTS.md) and open work is in Linear.

| File | What it records |
| --- | --- |
| [`2026-09-20-current-state.md`](2026-09-20-current-state.md) | The last `docs/handoff/current.md`: billing paused on Rhode Island sales tax, schema 3.0, the MODEL-100/101/102 drafts, the offline-snapshot serving path. |
| [`2026-09-25-overnight-decisions.md`](2026-09-25-overnight-decisions.md) | The go-live night's delegated decision log. |
| [`session-freeze-2026-09-12.md`](session-freeze-2026-09-12.md) | The 2026-09-12 hold, since lifted. |
| [`mvp-remainder.md`](mvp-remainder.md) | MODEL-5/7/30/34 as the MVP closed. |
| [`post-mvp-loop.md`](post-mvp-loop.md) | The retired Grok Build autonomous loop prompt. |
| [`offline-cli-contract.md`](offline-cli-contract.md) | The offline CLI contract retired by MODEL-307; still served by `python -m cli.modelspec.legacy`. |

## Decisions that used to sit in the entry files

Before MODEL-311, `CLAUDE.md` and `AGENTS.md` carried this lineage. Git history
has the full text.

- **MODEL-2** closed on a static Pages export: no R2 and no D1 on the static
  serving path. That described the static path only; it never forbade the keyed
  Worker beside it, nor the Workers KV store MODEL-80 added for policy
  determinations.
- **MODEL-3** was not a one-Worker rebuild: the site stays on Pages (Jamie,
  2026-09-18). **MODEL-6** was cancelled, superseded by MODEL-68/69/73/75.
- **MODEL-68/69/73/75/93** built the rank Worker, keys, Stripe Checkout, x402
  credits and the credit ledger. **MODEL-221** added `/v1/feedback`.
- **DPF** was the first consumer, through the offline CLI. MODEL-307 replaced
  that CLI with the keyed client.
- `docs/system-architecture-v3.md` (2026-04, FalkorDB-served) and
  `docs/superpowers/` (dated plans) are historical too.
- The old handoff README sent taste calls (naming, copy, how a refusal reads)
  to Jamie as prepared options. Later delegation replaced that; the binding
  rules in `AGENTS.md` list what still needs him.
