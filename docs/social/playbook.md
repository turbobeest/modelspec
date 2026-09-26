# Run ModelSpec social publishing

This playbook covers human-approved posts derived from the MODEL-114 generator. Nothing posts automatically. Grok Bot drafts copy variations, and a human checks every fact and publishes the approved version.

## Use the generator's post types

Run MODEL-114 only against a signed decision snapshot and a passing accuracy report. The generator writes text and image cards. It has no posting interface.

Use each draft type for this event:

| Draft type | Publish when |
|---|---|
| `new_entrant` | A verified model enters a domain's top five or takes first place. Publish after the launch report and accuracy report are live. |
| `honest_gaps` | A launch has material unknown facts or missing evidence. Publish with the first launch post, not as a later footnote. |
| `value` | Verified evidence and current offering prices support the value claim. Publish at the +1-day or +7-day update. |
| `local` | The snapshot has a sourced hardware-fit fact for the named device. Publish at the +1-day or +7-day update. |
| `weekly_movers` | Two signed weekly snapshots show a change. Publish in the weekly roundup, never from a one-off comparison. |

Do not force every draft type into a campaign. If the generator omits a type, the snapshot does not support that claim.

## Follow the cadence

For a verified model launch:

1. On launch day, publish the launch report link and any `new_entrant` and `honest_gaps` drafts that the snapshot supports.
2. At +1 day, publish one supported `value` or `local` draft after the refreshed accuracy report passes.
3. At +7 days, publish the material change. Use `weekly_movers` only when the prior signed snapshot supports it.
4. At +30 days, publish a final update if new independent evidence or a changed decision exists. Do not post an unchanged recap.

Outside a launch cycle, publish one weekly roundup at most. Skip the roundup when the signed snapshots show no material change.

## Approve every post

1. Generate the draft and card locally.
2. Have Grok Bot draft platform-specific wording without changing any number, source, read date, relationship disclosure, or neutrality statement.
3. Compare every number with the signed snapshot and the source named on the card.
4. Check that the linked launch report or decision uses the same snapshot ID.
5. Check the crop and alt text on each platform preview.
6. Send the first batch to Jamie. Jamie approves each post in writing before publication.
7. Publish manually. No script, bot, scheduler, or platform integration may press the final publish control.
8. Record the published URL, approver, snapshot ID, and publication time in the campaign notes.

After the first batch, a named human approver may follow the same flow. Jamie remains the approver for a new claim type, a changed disclosure, or a correction.

## Disclose the source and relationship

Keep the generator's disclosure with the post. Every numeric claim must carry its source URL and the date ModelSpec read it. If space moves those details to the image card, the post must say that the card contains the sources and read dates.

State any supplier relationship that `schema.suppliers.supplier_for()` returns. Keep this pledge unchanged: `No referral fees, no paid placement, no provider-paid visibility, permanently.` The rule comes from `neutrality_commitment()` in `api/ranking/engine.py`.

If Grok Bot rewrites the draft, add `Drafted with Grok Bot; reviewed and posted by a human.` to the campaign notes and to any platform field that provides room for methodology or disclosure. Grok Bot does not select evidence, approve a claim, or publish.

## Correct a wrong number

1. Pause every queued post that repeats the number.
2. Open a fix PR that corrects the source snapshot, fact, evidence, or generator logic. Include the failing test or accuracy gate.
3. Publish a public correction from the same account. State the old number, the corrected number, and the effect on the decision.
4. Link the fix PR in the correction. Reply to or edit the original post where the platform permits it.
5. Keep the original post unless safety, legal, or privacy concerns require removal. A visible correction is the record.
6. Regenerate the card from the corrected signed snapshot and passing accuracy report.
7. Record the correction URL beside the original publication URL.
