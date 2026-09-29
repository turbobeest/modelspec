# Release breakdown standard

When a lab releases a model, ModelSpec may publish a **release breakdown**: a
post under `/blog/` that sets everything ModelSpec's evidence says about the
new model beside what the lab announced. This page is the standard every
breakdown meets. It is published, and a post that breaks it is wrong and gets
corrected under [§8](#8-corrections).

The architecture that enforces it is
[`docs/design/release-blog.md`](../design/release-blog.md). Where the two
disagree, this standard wins.

## 1. The rule behind every other rule

**Every number in a breakdown comes from one signed ModelSpec snapshot. No
number is typed by a person or an agent.**

- A number is either a value the snapshot holds or a value the decision engine
  computes from it: a capability estimate and its interval, a rank, P(best),
  a cost per task, a plan's break-even.
- A value is in the snapshot only if it passed the two-key rule: one agent
  collected it, and an independent verifier (a different model family, or a
  deterministic check) re-read it from its source and got the same value.
  It also names a registered source. See
  [`docs/decision-verification.md`](../decision-verification.md).
- Each number in a post links to its source and the date ModelSpec verified it.
- Each post names its snapshot ID and links the signed snapshot file, and it
  lists the ID of every decision it relies on with the spec that produced it.
  Anyone can re-run those specs against that snapshot and get the same
  decision IDs and the same numbers.

A value ModelSpec does not hold is written as unknown. A null beats a guess.
Prose written around the numbers may not contain a number of its own.

## 2. What a breakdown contains

Every breakdown has these five parts, in this order. A part with nothing
verified in it still appears, and it says what is missing.

### 2.1 Claims and evidence

The lab's announced numbers, beside independent readings of the same
benchmarks.

- **The lab's numbers are quoted with their source.** A lab's number appears
  only when a second key has re-read it from the lab's own page, paper or
  model card. A post on X is where ModelSpec hears about a release. It is never
  the source of a number.
- **Independent readings** are those published by a benchmark's authors, by an
  independent evaluator, or measured by ModelSpec under a published method.
  Each shows who measured it, when, and the harness and effort settings when
  they are known.
- **The difference is stated plainly, only when it is a like-for-like
  comparison.** Same benchmark, same version, same unit, same harness and
  effort (or both unstated). Then the post gives the difference as a number:
  "The independent reading is 2.1 points below the lab's figure." When the
  setups differ, the post shows both numbers and names what differs. It does
  not compute a difference.
- **A difference is not an accusation.** Benchmarks run differently across
  harnesses, prompts, effort settings, dates and hardware. The post does not
  say why two numbers differ unless a source says so, and then it quotes that
  source.
- **"Not in the announcement"** lists benchmarks where independent readings
  exist and the lab reported none. It is a list of readings. It says nothing
  about the lab's reasons.
- **"No independent reading yet"** marks every lab number nobody has
  independently measured. The re-check schedule (§2.5) says when ModelSpec
  looks again.

### 2.2 Where it lands

- **Per domain**, the model's capability estimate with its 80% interval.
  Estimates come from ModelSpec's capability model, fitted from every admitted
  benchmark. They are never one benchmark's score.
- **Rank** is always given with its band. When the evidence cannot separate
  the top models, the post says the model is in the leading band with the
  number of others in it. It does not call any of them first.
- **P(best)** is the share of draws from the fitted model in which this model
  scores highest in that domain. It is given for the model and for the leaders
  it is compared with. It is a statement about the evidence, not a forecast.
- **Thin evidence** is named. When an interval is too wide to rank on, the post
  says so before it gives the rank.
- **Template changes.** ModelSpec's decision templates are a grid of jobs
  (coding, writing and so on) by tiers (best, balanced, budget, fastest,
  private). The post lists every template whose answer the new model changes:
  whether the model entered the leading band, and which models left it.

### 2.3 Cost

- **Cost per task** for each offering of the model, from verified prices, at a
  stated task size (by default 40,000 input tokens and 4,000 output tokens).
  The task size is always shown next to the cost.
- **Plans.** For each subscription plan ModelSpec tracks (for example Claude
  Max, Cursor and GitHub Copilot tiers), whether the plan covers the model,
  quoting the plan's own coverage statement. A plan whose coverage is not yet
  verified is listed as unknown, never left out. For coding tools, the post
  gives the break-even: how many tasks a month make the plan cheaper than
  paying per use.
- Links to a provider or plan go to the provider's own page. No link carries a
  referral, affiliate or tracking parameter.

### 2.4 Hardware fit

For a model with open weights, which devices it fits on and at what
quantisation, from verified hardware-fit facts. A prediction, such as an
estimated tokens-per-second, is not a verified fact and is not published.
A closed-weights model has no hardware section.

### 2.5 Not measured yet

- Every fact ModelSpec guarantees for this class of model that is still
  unknown.
- How many readings of this model ModelSpec holds that have not yet passed the
  second key, by reason. The post gives the count, never the unverified
  values.
- Domains with no estimate, and lab numbers with no independent reading.
- **The re-check schedule:** ModelSpec re-checks at +1, +7 and +30 days after
  the first post, and the post gives the dates. Each re-check that changes
  anything becomes a new, dated revision that shows what changed. A re-check
  that changes nothing adds no revision.

## 3. Same-day means verified the same day

A breakdown published on release day holds only what was verified that day.
It does not wait for more, and it does not fill gaps with guesses. It states
what is coming and when. The post shows the time of the announcement and the
time of publication, so the delay is visible. When nothing about the model is
verified yet, ModelSpec publishes no breakdown.

## 4. Neutrality

ModelSpec's published neutrality commitment applies to every post:
**No referral fees, no paid placement, no provider-paid visibility,
permanently.** See [`/legal/neutrality/`](https://modelspec.dev/legal/neutrality/).

### 4.1 No paid placement

No lab or provider pays for, sponsors, or chooses the timing of a breakdown.
Whether a model gets a breakdown depends on the release, not on who made it.

### 4.2 No affiliate or referral links

No post contains an affiliate link, a referral code, or a tracking parameter
for a provider. Outbound links go to the sources the numbers came from, to
providers' own pages, or to ModelSpec.

### 4.3 No embargo deal that shapes the analysis

ModelSpec does not agree to terms that let a lab review, approve, shape, or
delay a breakdown, or that condition access on coverage. If ModelSpec ever
has access to a model before its release, the post says so, and every number
from that access passes the same two keys as any other.

### 4.4 Relationships are disclosed

When ModelSpec has a supplier or data relationship with the lab, the post
states it at the top.

## 5. Tone: never disparage a lab

A breakdown describes evidence. It does not grade a lab's honesty, intent or
marketing.

- Differences are stated as numbers with the words "higher" or "lower". The
  post does not say "inflated", "overstated", "misleading", "cherry-picked" or
  "hype", or anything with the same meaning, about any lab.
- A difference is described by its size and direction only. The post does not
  characterise it, frame it, or return to it in other words.
- The post uses no superlatives the evidence does not support. "Best" appears
  only as ModelSpec's band name. "Leading band" replaces "number one" whenever
  the band holds more than one model.
- Other labs' models appear only as the comparison the evidence calls for:
  the leaders of a domain, or the models a template's answer changed from.
- The same wording rules apply to every lab, including labs ModelSpec has a
  relationship with.

Every post is checked for refused words before it can be published.

## 6. Sources

- Every source is registered, and every number links to its source.
- The publishers excluded under
  [ADR 0003](../adr/0003-excluded-sources.md) are never a source. Nothing they
  publish appears in a post, directly or through another site that republishes
  it. The list is in `decision/excluded.py`. The snapshot build refuses any
  value from them, and a post is checked again before it is written.
- Social media posts start ModelSpec's research. They are not evidence.
- Leaderboard data is used only where its licence permits it.

## 7. Approval and publication

- Every breakdown and every revision is a pull request in
  [the public repository](https://github.com/turbobeest/modelspec). Jamie
  reviews it.
- Nothing is published on the site, or posted to any social platform, without
  Jamie's explicit approval. Publication is a separate change that a person
  merges by hand.
- Social posts are drafts made from the breakdown's own numbers. A person
  posts each one by hand after approval. No script, bot or agent posts, and no
  agent handles social account credentials. The social procedure is
  [`docs/social/playbook.md`](../social/playbook.md).

## 8. Corrections

- **A correction is appended, visibly, and never made by silent edit.** The
  corrected post shows the correction at the top: what was wrong, the old
  value, the new value, the date, what it changes about the conclusions, and
  a link to the change that fixed it.
- The revision that carried the error stays published at its own address,
  unchanged, so anyone can see what was said.
- Corrections go out on every platform where the error was posted, from the
  same account, following the social playbook.
- To report an error, open an issue in the public repository with the post's
  address and the number you believe is wrong.

## 9. What a breakdown is not

- It is not a review of the lab, the launch, or the announcement.
- It is not a prediction of where the model will land when more evidence
  arrives.
- It is not advice for any particular buyer. ModelSpec's decision tools, where
  a reader states their own requirements, are for that.
