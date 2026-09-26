# MODEL-118 Open LLM Leaderboard migration

Read on 2026-09-25 from the primary Hugging Face datasets:

- OLL v1: [`open-llm-leaderboard-old/results`](https://huggingface.co/datasets/open-llm-leaderboard-old/results)
  at revision `23474373f8874f9057d23b97e5a41e911d2721c5`.
- OLL v2: [`open-llm-leaderboard/results`](https://huggingface.co/datasets/open-llm-leaderboard/results)
  at revision `aa81ecc38fdc5708254b833923368970efdf5ef5`.

## Licence and reuse basis

Neither dataset declares a licence. Their Hugging Face API records returned
`cardData.license: null` on 2026-09-25, and the pinned repositories contain no
licence grant. This migration therefore does not rely on a dataset licence and
does not redistribute the result files or their prose. It records only the
model identity, evaluation date, benchmark key and numerical measurement from
each cited file.

Those individual data points are uncopyrightable facts under United States
law. The [U.S. Copyright Office's database guidance](https://www.copyright.gov/register/tx-databases.html)
states that copyright does not protect individual plain facts. The Copyright
Act also limits compilation copyright to the compiler's contribution and does
not create an exclusive right in the underlying material
([17 U.S.C. § 103(b)](https://www.copyright.gov/title17/92chap1.html#103)).
That public-domain status is the governing reuse basis for the imported facts;
no licence applies. Each evidence row attributes its exact source URL and read
date. ModelSpec does not copy Hugging Face's selection, arrangement or
expressive text.

The collector required the card's Hugging Face repository to match the model
named in the result file. It derived each value from that file and compared it
at the precision written on the card. It used the result's evaluation date,
not the dataset revision or retrieval date. `modelspec verify` independently
checked every proposed row against a retained structured projection.

## Result

| Dataset | Migrated to evidence | Left as `unverified-legacy` |
|---|---:|---:|
| OLL v1 | 2,176 | 827 |
| OLL v2 | 680 | 137 |
| Total | 2,856 | 964 |

All 2,856 proposed rows passed deterministic two-key verification. No proposed
row entered quarantine. Of the 964 retained values, 774 did not match a result
file for the exact model, 176 collide with an evidence row that already owns
the benchmark, and 14 cards lack an exact Hugging Face repository identity.

The full change table is
[`model-118-oll-migration.csv`](model-118-oll-migration.csv). It names the card,
benchmark, legacy and published values, outcome, reason, evaluation date,
source URL and evidence ID. The frozen pre-migration set used by the new-score
guard is
[`model-118-legacy-flat-score-baseline.csv`](model-118-legacy-flat-score-baseline.csv).

## Key correction

MODEL-116 had already found and fixed the OLL v2 key mix before this migration.
The OLL column `MATH Lvl 5` measures the level-5 slice of the MATH test set; it
had been stored as `math_500`. The OLL task `leaderboard_gpqa` pools GPQA Main,
Extended and Diamond; it had been stored as `gpqa_diamond`. The catalogue now
uses `math_lvl5` and `gpqa_pooled` for those OLL values. This migration reads
and writes only those canonical keys.

## Catalogue effect

The counts below cover every catalogue card against every v1 profile, using
`pipeline.ranking._basis` on the same benchmark contributions as the scorer.

| `evidence_basis` | Before | After |
|---|---:|---:|
| `none` | 56,498 | 56,498 |
| `unverified-legacy` | 8,194 | 4,202 |
| `mixed` | 1,587 | 1,479 |
| `partial-verified` | 3,387 | 7,487 |

Cards with flat scores fell from 430 to 326. Cards with flat scores and no
evidence fell from 205 to 107. Cards with evidence rose from 403 to 501.
