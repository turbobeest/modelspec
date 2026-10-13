# Decision links for human lookup

Draft — awaiting Jamie's approval

MODEL-353 prepares a read-only human page for a bounded `/v1/decide` answer.
Jamie owns both decisions below. The implementation follows the ticket's
recommendations behind `DECISION_LINK_ENABLED`, which defaults to false in
the Worker. This note does not approve production activation.

## Visibility and lifetime

The recommendation is a link that is unguessable, shows summary-level content,
and expires 30 days after issuance. Its form is
`https://modelspec.dev/d/<decision_id>?token=<signed-capsule>`.

The engine's `decision_id` remains a deterministic citation. The random nonce
inside the signed capsule makes the complete link an unguessable capability.
Knowing or guessing the citation alone grants no view. The Worker verifies the
signature, the expiry, and the match between the capsule and the path's
`decision_id` before it computes an answer.

The page shows `summary_for_user`, every `must_mention` item, the applied
requirements and any fields the decision did not apply, and the snapshot ID
and content hash. Applied requirements include the normalized conditions,
objective, unknown-value rules, and task-token defaults. It has no full results
table, ranked rows, evidence drill-down, or account information. A shared link
can therefore preserve the answer's qualifications, including ties and missing
evidence, without publishing the full machine response.

The Pages route loads a read-only shell. The browser obtains the existing
Turnstile-backed visit token, then posts the capsule and citation to
`/v1/decision-link`. The Worker always requires valid human visit admission on
this endpoint, even when `ACCESS_ENFORCED` is off. Possession of the link,
an allowlisted Origin, or an API key does not replace that admission. The
endpoint returns only the fields the page renders. Machine callers continue
to use the keyed API.

Jamie could instead require a signed-in recipient or a fresh paid request for
every view. Either reduces sharing and adds a new user step. A public citation
without a secret token would expose decisions to enumeration. A shorter expiry
reduces the leak window but makes links less useful in conversations. An
indefinite link creates an indefinite disclosure and retention obligation.

## Storage and reproducibility

The recommendation is signed decision inputs plus a snapshot pin, recomputed
on view, with no new decision store. `DECISION_LINK_HMAC_KEY` is a Worker
secret. The HMAC protects the capsule's integrity. It does not encrypt its
contents.

The capsule carries validated decision inputs, the citation, a random nonce,
the issue and expiry times, the snapshot ID and content hash, and the deployed
engine revision from `BUILD_COMMIT`. It contains no authorization headers,
API keys, provider credentials, billing identifiers,
or payment records. The implementation omits links for requests with a
non-null `estate`, `profile`, or `save_as`. Those request shapes remain valid
decide inputs, but do not become shareable capsules in this draft.

On view, the Worker requires the loaded snapshot to match both its signed ID
and its content hash. The deployed engine revision must also match the signed
`BUILD_COMMIT`. It never substitutes `latest`. An expired capsule, a bad
signature, a citation mismatch, or an unavailable or changed snapshot or
engine revision refuses the view. Turning the flag off also removes the view.

The Worker currently embeds its snapshot, and this ticket adds no historical
snapshot retention. Replacing that snapshot or deploying a new engine revision
can invalidate a link before its 30-day expiry. Thirty days is the maximum
authorization lifetime, not an availability promise. A future promise to
retain links for that whole period
needs separately approved retention of the data image and a way to execute
the pinned engine revision. Recomputing from inputs does not archive the exact
original response bytes. The matching engine revision produces the summary
from the matching data image.

With no decision store, the operator cannot revoke one leaked link. Rotating
`DECISION_LINK_HMAC_KEY` invalidates all capsules issued with the old secret.
Expiry and the flag provide the other ways to end access.

An alternative store could retain the original summary, support revocation of
individual links, and survive snapshot replacement. It would also introduce
customer-data retention, deletion, storage cost, and access rules. An encrypted
capsule could hide inputs from people who receive the URL, but would still be
a transferable link and would add key management and byte overhead. Neither
alternative is adopted by this draft.

## Privacy and charging

The link becomes free human lookup of an answer obtained through the paid
machine path. A recipient who passes the existing human gate can read the
summary without the purchaser's API key or credits. Jamie must approve that
visibility and charging effect before activation.

Anyone who receives a working link can forward it. Because the capsule is
signed rather than encrypted, anyone who receives the URL can decode its
decision inputs before passing the human gate. Requirements can reveal a
customer's budget, hardware, policy constraints, or model preferences even
when they contain no credentials. Omission of estate and profile inputs limits
that exposure but does not make the remaining requirements confidential.

URLs can enter chat history, browser history, proxy logs, and infrastructure
access logs. The page and endpoint use `no-store`, and the page suppresses
referrers. These controls reduce cache and referrer disclosure. They do not
remove copies held by a recipient or guarantee deletion from infrastructure
logs. Application code must not log capsules, visit credentials, or keys.
Jamie must review whether the published privacy wording covers this flow.
This ticket does not change `docs/legal/` or authorize that wording.

## Contract publication and activation

`decision_url` is a new optional field on successful bounded answers. It is
absent when the flag is off and when a shareable link cannot be issued. Full
decisions keep their current representation. Worker responses and generated
agent copy remain byte-identical with the flag off.

The [decision contract's MODEL-59 rule](../decision-contract.md#versioning-model-59)
explicitly permits new optional response fields without a major bump. The
[CLI contract](../cli-contract.md#contract-versioning-model-59) also permits
new fields. No existing required field becomes optional, nullable, or a new
enum value here. The bounded representation follows MODEL-59 on its own, so
this additive field does not require a major bump. This ticket makes no
contract version bump. A later change that widens an existing field would
require the applicable contract's major bump.

The link must fit within MODEL-334's existing 16,384-byte agent response
budget. Its signed input size counts as part of that response. Issuance must
omit the optional link when it cannot fit rather than raise the budget or
remove required reporting information.

Activation requires Jamie's approval of the visibility and storage decisions,
including the possible loss of a link before expiry. It also requires the
following preparation.

1. Review privacy and charging disclosures. Adopt any legal wording through
   Jamie's separate approval process.
2. Review the experimental optional field in the decision contract and
   response schema, and publish the human-view endpoint in generated OpenAPI
   documentation. Keep
   `docs/api.md` within its existing 800-word budget through separate review.
3. Configure `DECISION_LINK_HMAC_KEY` and `BUILD_COMMIT` in each environment,
   retain the existing visit-gate and Turnstile secrets and bindings, and keep
   `VISIT_GATE_ENABLED` on. Missing link or human-admission configuration
   prevents link issuance and fails closed on view.
4. Build the web app with visit gating and a Turnstile site key, and publish
   the live Pages site with the new `/d/<decision_id>` shell. The holding
   composition does not publish that shell, so activation requires
   `SITE_MODE=live`.
   Regenerate and publish the agent-copy artifacts with the approved flag
   configuration so the trusted-channel rule adds "and give the user
   decision_url" only when enabled.
5. Verify signature rejection, expiry, snapshot and engine-revision mismatch,
   human admission, summary-only rendering, flag-off compatibility, and the
   response byte budget. Jamie can then turn `DECISION_LINK_ENABLED` on in
   the Worker.

This draft leaves `DECISION_LINK_ENABLED` off in `wrangler.jsonc`. It does not
change the other production switches, public API reference, legal terms, or
frozen data.
