# Terms of service

Version `1.0`, effective 2026-09-19. Adopted by Sparks & Sawdust LLC.
MODEL-70.

## 1. Who you are contracting with

The ModelSpec API and the modelspec.dev and benchgraph.dev sites are operated by
**Sparks & Sawdust LLC** ("we", "us"). "You" is whoever calls the service,
including an autonomous agent calling it on somebody's behalf. An agent that
accepts these terms binds the person or organisation it acts for.

## 2. What the service is

ModelSpec catalogues AI models and ranks them against a published method. The
service is:

- The **static export** — versioned JSON under `https://modelspec.dev/api/`,
  including the catalogue, the rankings and the ranking policy. No account, no
  key, no charge.
- The **API** at `https://api.modelspec.dev`: `POST /v1/rank`, which computes a
  ranking per request from that same published export; `POST /v1/policy-check`,
  which checks models, and the platforms that serve them, against a policy you
  state; `GET /v1/health`; and `GET /v1/credits`, which reports a key's credit
  balance.
- A **remote MCP server** at `https://api.modelspec.dev/mcp`, which offers the
  same answers as tools and passes each call through to the API or the export.
- **API keys.** A key beginning `live_` identifies a caller and its tier. A key
  beginning `test_` is a sandbox key: it is answered with synthetic results, not
  live data, and is never stored. Whether a call must carry a key, and the
  limits of each tier, are published at `https://modelspec.dev/auth.md` and
  `https://modelspec.dev/pricing`. On the effective date above no key is
  required: a call without one is answered at the free tier, at no charge.
- **Paid access**, metered in credits and bought through Stripe (§6). A key with
  credits remaining receives the paid answer, which includes our commercial-use
  and data-residency determinations on policy-check. A key with none left
  receives the free answer, not an error.

Payment by x402 is not currently offered. We will not bill you under terms you
did not see first.

**What the service is not.** We do not run inference. We do not proxy, relay or
resell access to any model, and your prompts and inference traffic do not pass
through us (§4, §7). We are not your agent, your broker or your advisor, and a
ranking is information, not a recommendation to enter any transaction.

## 3. The honest-broker rule

This is the rule the rest of these terms exist to keep, and it is the reason we
will never sell the thing a ranking is worth most to the people it ranks:

**Charging the consumer of a recommendation is compatible with being an honest
broker. Charging the subjects of one is not.**

We charge the consumer of a recommendation. We do not charge its subjects.

## 4. The neutrality commitment

**No referral fees, no paid placement, no provider-paid visibility,
permanently.**

No model provider, hosting platform, gateway, inference vendor or other subject
of a ranking can pay us for a better position, for inclusion, for visibility, or
for anything else that touches what an answer says. There is no rate card for
this, because there is no price at which it is for sale.

Neutrality does not stop at money. No provider, gateway, hosting route or
inference vendor is privileged at any stage of a recommendation: not in the
ranking, not in the tie-breaks, not in a default hosting suggestion, and not by
any commercial relationship of ours.

We also do not earn on your inference. We recommend and hand off: your calls to
a provider, gateway or local runtime go there directly and never through us. A
margin that grows with your token volume would be a reason to steer you, so we
have arranged not to have one.

**This commitment is machine-readable.** It is published as the `neutrality`
block of the ranking policy, in the same object as the ranking floors, at
`https://modelspec.dev/api/rank/profiles.json`, and in the `policy` block of
every rank response. It is fetchable with no key and no account, so you can
check it rather than trust it. The ranking method itself
(`api/ranking/engine.py`) is public for the same reason.

If we ever break this commitment, the JSON says so before the prose does.

## 5. Using the service

You may call the API, script against it, and build products on it. You may not:

- present our output as something other than what it is, or attribute to us a
  claim we did not make;
- misrepresent the neutrality commitment, or imply a paid or endorsed
  relationship with us that does not exist;
- attempt to obtain data you are not entitled to, interfere with the service, or
  evade a limit or a refusal;
- use the service in a way that breaks the law where you are or where we are.

We may refuse or withdraw service for any of the above.

## 6. Billing

These are the rules that govern every purchase. They were written before any
money moved, so that they could not be written to suit the first dispute.

**Seller and payment.** The seller is **Sparks & Sawdust LLC**. Payments are
processed by Stripe on a Stripe-hosted Checkout page; we never receive your
card number. Charges appear on your card statement as **SPARKS & SAWDUST LLC**.
Current plans, prices and availability are published at
`https://modelspec.dev/pricing`. Checkout asks you to accept these terms before
you pay.

**What you buy.** Paid access is metered in credits, one balance per API key.
There are two ways to buy them:

- **Plans** — Solo ($10 a month, 4,000 credits) and Team ($50 a month, 30,000
  credits). A plan's monthly allowance is set to its full amount on each paid
  invoice. It is reset, not added to: unused monthly credits do not roll over.
- **Packs** — one-off purchases of 1,250, 7,500, 20,000 or 50,000 credits, for
  $5, $25, $50 or $100. Pack credits expire 12 months after purchase.

A call draws the monthly allowance first, then pack credits, the ones expiring
soonest first. How many credits each kind of successful call draws is published
on the pricing page.

**Your key.** A key bought without an existing one is shown to you once, when
you claim it after Checkout. We store only a hash of it and cannot show it to
you again. Anyone holding your key can spend its credits, so keep it as you
would a password. `POST /v1/billing/rotate`, called with the key you hold,
replaces it; the remaining credits move to the new key and the old one stops
working.

**When a plan ends.** If a plan's payment fails, or the subscription is
cancelled or lapses, its monthly allowance goes to zero at once and the key
falls back to the free tier. Pack credits are not affected and remain until
they expire. A later paid invoice restores the monthly allowance. To cancel a
plan, write to sales@modelspec.dev.

**6.1 Only a successful result is charged.** A charge is incurred when, and only
when, the service has delivered a result to you. A request that does not produce
a delivered result is not charged, whatever caused it.

**6.2 What counts as a delivered result.** An HTTP 200 response carrying a
non-empty result: a ranking, or a policy-check answer. A ranking that reports
`ranking_status: "partial"` is a delivered result: it means some models lack the
evidence to be ordered, which is the answer, honestly labelled, and not a
degraded one. A policy-check answer in which some checks are `undetermined` is a
delivered result for the same reason. We would rather tell you what we do not
know than charge you for a guess.

**6.3 What is never charged.** None of the following is a delivered result, and
none of them is charged:

- a refusal for a malformed or invalid request (HTTP 400, 413);
- a request to an endpoint or method that does not exist (HTTP 404, 405);
- a well-formed request that no model survives (HTTP 422). You are told which
  constraint emptied the pool; you are not billed for the finding;
- any failure on our side, including an unreachable or unreadable catalogue
  (HTTP 5xx), a timeout, or a response you never received;
- a payment-required response (HTTP 402), or an answer given at the free tier
  because the key has no credits left;
- **a rate-limit refusal. Being told to slow down costs nothing** (HTTP 429),
  and being refused for a missing, invalid or revoked credential costs nothing
  (HTTP 401, 403). A refusal is not a service.

**6.4 Settlement before delivery.** Credits are paid for in advance. Before an
answer is produced, the credits it costs are reserved from your balance; they
are drawn when the result is delivered and released untouched when it is not.
An unsuccessful call leaves your balance where it was.

**6.5 Partial failure.** If a charge is taken and no result reaches you, that
charge is refunded in full. You do not need to show that the failure was ours.
If you were charged and are not sure you were served, tell us and we will look;
where the record is ambiguous, it resolves in your favour.

**6.6 Refunds.** Charges for delivered results are not refundable merely because
you disliked the answer — the ranking is the product, and a ranking that only
charged when it flattered would not be worth having. We refund: anything charged
without a delivered result (§6.5); anything charged in error, including
duplicate or mis-metered charges; and unused prepaid balance, on request, minus
nothing. If we withdraw the service or these terms change to your material
detriment, unused balance is refunded.

**6.7 Prices.** Prices are published at `https://modelspec.dev/pricing` before
they apply. A price change does not apply retroactively to credits you already
bought.

**6.8 Taxes.** Prices are in US dollars. Any tax charged is shown at Checkout
before you pay. You are responsible for taxes on your own side of the
transaction.

## 7. Your data

The privacy statement is at `https://modelspec.dev/legal/privacy/` and describes
what the service records, including what it keeps about a paid key and a
purchase. Two points belong here because they are terms,
not just practice:

- **We do not receive your prompts.** A rank request carries a profile — use
  case, environment, constraints — computed on your side, and a policy-check
  request carries the policy you want checked. Prompt text is not a field of
  this API. Widening it toward prompt text would be a breach of this
  commitment, not a feature release.
- **We do not proxy your inference tokens**, so we do not see, store or meter
  the content of your model calls. There is nothing for us to hold.

## 8. Data, licences and what you may do with the output

The catalogue data is licensed **CC BY-SA 4.0** (`LICENSE-DATA`). The code,
including the ranking method, is licensed **MIT** (`LICENSE`). Those licences
govern the data and the code; these terms govern the hosted service, and nothing
here takes away a right either licence grants you.

Rankings are computed from that data, so redistributing a substantial part of it
carries the CC BY-SA attribution and share-alike conditions with it. Acting on a
ranking, quoting one, or building a product whose output is informed by one does
not put your product under that licence.

Card data is compiled from third-party sources, each cited with the date it was
read. We do not own those sources and grant you no rights in them.

## 9. Accuracy, and the absence of any warranty

Rankings are computed from published benchmark results and vendor-stated facts,
which are incomplete, sometimes wrong, and always out of date by some margin. We
publish the floors, the provenance of each row and the date each source was
read so you can judge for yourself. A model's position is evidence about
evidence. It is not advice, and it is not a promise about how the model will
behave for you. A policy-check verdict cites the source it rests on so you can
read it yourself; it is not legal advice.

The disclaimer below is the one from the MIT License, which is the licence this
project's code already carries (`LICENSE`), reproduced verbatim rather than
rewritten:

```
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

There is no uptime commitment and no support commitment. Neither is offered, so
neither is promised.

## 10. Changes, suspension and termination

We may change the service. A change to the ranking method is published in the
method itself, which is public. A change to these terms is published here with a
new version, and a change that materially reduces what you get takes effect for
you only after it is published, never before.

You may stop using the service at any time. We may suspend or end access for a
breach of §5. §4 does not expire, is not suspended, and does not change with a
new version of these terms.

## 11. What this version does not address

This version states no governing law, venue, limitation of liability,
indemnity or dispute-resolution procedure. It says so rather than guessing at
them. Where these terms are silent, they add nothing to and take nothing from
the law that applies. Adding any of these later is a change under §10.

## 12. Contact

Sparks & Sawdust LLC. Questions, cancellation and privacy requests:
**sales@modelspec.dev**. Our postal address is available on request at
sales@modelspec.dev.
