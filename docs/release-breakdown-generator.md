# The release breakdown generator (MODEL-224)

`release_blog/` turns one model's entry in a signed decision snapshot into a
release breakdown: `breakdown.json`, a Markdown draft post and SVG charts. It
is ticket 3 of the release-blog series. The architecture is
[`docs/design/release-blog.md`](design/release-blog.md) and the editorial
standard is
[`docs/method/release-breakdown-standard.md`](method/release-breakdown-standard.md).

## Run it

```bash
python -m release_blog draft \
  --model anthropic/claude-sonnet-5-5 --name "Claude Sonnet 5.5" \
  --after S1.json.gz --before S0.json.gz \
  --accuracy accuracy.json \
  --out-dir out/
# out/breakdown.json, out/post.md, out/charts/{claims,standing,cost}.svg
```

- `--after` is the first signed snapshot the model is in, `--before` the last
  one without it. Omit `--before` for a backfill: the post then has no
  template-change section and says why.
- `--accuracy` is `scripts/accuracy.py --profile pr --snapshot-file S1` output.
  The generator refuses any report that did not pass all four pr layers for S1.
- `breakdown` writes only `breakdown.json`; `render` turns an existing
  `breakdown.json` into the post and charts.

Both snapshots must carry an Ed25519 signature from a key pinned in
`decision/snapshot_keys.json`. The generator never uses the Worker's HMAC
secret. A refusal writes nothing and exits 2 with the reason.

The command is `python -m release_blog`, not a `modelspec` subcommand:
`release_blog/` is a maintainer tool and is not in the PyPI wheel.

## What it guarantees

- **Every number is cited.** Each number in `breakdown.json` is a `Cited`:
  the snapshot record behind it, or the computation that produced it, with
  its input records or its decision ID. Validation fails on a number with
  neither. The only bare numbers are inputs, not findings: the revision, the
  task size a cost is for, the re-check day offsets and the decision specs.
  `tests/test_release_blog.py` walks the JSON to keep it that way.
- **Every number in the post has a footnote** naming that fact.
  `render.untraced_numbers` finds any number without one, and `render`
  refuses to return such a post, a post with an orphaned footnote, or a post
  with a refused word (`release_blog/tone.py`).
- **Byte-reproducible.** Canonical JSON, the snapshot's own encoding. The
  same inputs give the same `breakdown.json`, post and charts.
- **Decision IDs reproduce.** `decisions[]` holds every spec the post relies
  on. Re-running a spec against its snapshot gives the same decision ID.
- **No written claims.** Prose is fixed sentences in `release_blog/wording.py`
  over computed facts. The headline is chosen by rules from the numbers and
  its rule is recorded beside it.
- **An LLM may only smooth wording.** `release_blog/smoothing.py` hands prose
  paragraphs to a caller's rewriter and refuses the result if a number, a
  footnote, a link, a model ID, a direction or negation word, or the sentence
  count changed, or a refused word appeared. Tables, headings, lists, charts
  and footnotes are never handed over. There is no model client in the
  package.
- **Refusals.** An excluded source (ADR 0003) or its text, a source on `x.com`
  or `twitter.com`, an unsigned or wrongly signed snapshot, a model with
  nothing admitted, or an accuracy report that did not pass.

Drafts stay private: this package writes files and renders nothing on the
site. Publishing a post is ticket 2's `pipeline/blog.py`, which renders only
`status: published` posts.

## Choices made where the design left room

1. **The domain standing spec.** The design points at the social generator's
   per-domain spec, which ranks by one default benchmark. That objective
   returns no estimate, no bands and no P(best), which §3.4 needs. The
   breakdown uses the model's class ranked by the domain's capability
   estimate (`standing.domain_spec`), the objective the `coding-best`
   template uses. The social generator's function moved to
   `release_blog/standing.py` unchanged; ticket 5 makes the social cards
   views of `breakdown.json`, which ends the difference.
2. **Rank** is `Result.model_rank`, the model's place among models, not
   `Result.rank`, which counts offerings.
3. **Template changes** list only templates whose answer the model is in.
   Displacements elsewhere between S0 and S1 are other catalogue changes, not
   this model's doing.
4. **`content.held_back`** needs no format version bump. The snapshot format
   has one integer version and no minor; the key is additive and follows the
   `subscriptions` precedent. It is present whenever anything was held back,
   so a reader can tell "none of this model's" from "snapshot predates the
   key" (see [`decision-snapshot.md`](decision-snapshot.md)).
5. **Display names** come from `--vocabulary`, the decision vocabulary
   published beside S1 (`/api/decision/vocabulary.json`), or `--name`. The
   snapshot holds IDs only. Names are labels, never figures; the vocabulary
   must name S1 as its snapshot and its SHA-256 is recorded in
   `generated_from.vocabulary`, so the output stays reproducible.
7. **Inapplicable is not unknown (MODEL-97).** A domain the model's class
   cannot be measured on (`release_blog/applicability.py`, derived only from
   what the class consumes and emits in `api/classes.py`) is listed apart
   from domains not yet measured, and is not a gap. A domain a verified
   `model.input_modalities` rules out (vision for a text-only model) is a
   third list, citing that fact.
8. **Scale.** Each domain gives the spread of estimates across models of the
   same class (count, low, median, high, all cited), because an estimate on
   the capability model's scale means nothing alone. The leading band is
   listed whole, up to ten models.
6. **Plans** use a `coding_tool` decision for break-even, the only access the
   contract computes it for. Every tracked plan is listed: covering, not
   covering, or coverage not yet verified.
