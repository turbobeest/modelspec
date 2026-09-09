# The CLI as a priced surface in agent-to-agent commerce

**Assessment for MODEL-17, 2026-09-09.** Written against the interface that now
exists — `modelspec snapshot fetch` plus `modelspec offline rank`, documented in
`docs/cli-contract.md` — rather than a hypothetical one.

## The recommendation, first

**Do not meter ModelSpec yet.** Build the rail's *identity and attestation*
half now, because it is useful whether or not anything is ever charged for, and
leave the payment half until the data is worth paying for.

Two independent reasons, one structural and one about readiness.

## 1. There is almost nothing here an agent must pay for

This is the finding that reframes the question, and it follows from decisions
already taken deliberately.

The corpus is CC BY-SA. The export is public and free. The CLI downloads it once
and ranks locally, forever, offline, with no credential — that is MODEL-4, and
it is the promise the project made. The wizard does the same in a browser.

So an agent that wants rankings does not need an account. It fetches the export
once and computes as many rankings as it likes at zero marginal cost. **Metering
ranking calls would be charging for arithmetic the caller can trivially do
itself**, and the only way to make that stick is to make the free path worse.
That would trade the project's actual advantage — being the open, checkable
catalogue — for a small amount of revenue.

Anything that survives this test has to be something a local copy of the data
cannot produce.

### What actually is scarce

| candidate | scarce? | why |
| --- | --- | --- |
| The catalogue | **no** | CC BY-SA, downloadable, and should stay so |
| A ranking | **no** | pure computation over the free export |
| Freshness | **partly** | today's export versus a month-old one; but the export is free too, so this is only a convenience |
| **Reviewed benchmark evidence** | **yes** | the census contract needs a human reviewer opening sources. That labour is real and recurring |
| **Measured hardware throughput** | **yes** | someone has to actually run the model on the actual device. Today every figure we publish is computed, not measured |
| **Attestation** | **yes** | a signed, timestamped statement that *this* recommendation was made against *that* build under *those* constraints |

The last row is the interesting one, and it is the one that fits agent-to-agent
commerce specifically.

## 2. Attestation is the product, not recommendation

In an agent economy the recommendation itself is cheap — every agent can compute
one. What is expensive, and what agents will actually need, is **being able to
prove afterwards why a choice was made**, to a party that was not present.

When one agent selects a model on another party's behalf and something goes
wrong, the question is not "what did you pick" but "what did you know when you
picked it, and can anyone else check that". A signed attestation — constraints,
build commit, evidence basis, timestamp, the ranking it produced — is verifiable
by a third party who does not trust either agent. A recommendation is not.

ModelSpec is unusually well placed for this because it already refuses to launder
uncertainty. Every answer carries `evidence_basis: unverified-legacy`, hardware
figures say `computed` rather than measured, and benchmark dispositions are
partitioned by whether anyone actually checked. An attestation is only worth
anything if the thing being attested is honest about its own limits, and that
work is already done.

Note the corollary: attestation is worth *more* as the evidence improves. It
gives MODEL-13, MODEL-27, MODEL-28 and MODEL-29 a commercial reason to exist
beyond correctness.

## 3. Who pays decides whether we stay an honest broker

DPF-22 requires ModelSpec to act as an honest broker. That survives one funding
model and not the other, and the distinction is simple enough to state as a rule:

> **Charging the consumer of a recommendation is compatible with being an honest
> broker. Charging the subjects of one is not.**

An agent paying to ask "what should I use" has no stake in which answer comes
back — it wants the true one, which is exactly what it is paying for. A model
provider paying to appear is buying placement, and every ranking afterwards is
suspect whether or not it was actually influenced. The second is not a conflict
to be managed with disclosure; it is a different product.

This should be written into the project's terms before any money moves, not
after someone offers.

## 4. The surface is the MCP server, not the CLI

The ticket asks whether the CLI is the right place. It is not, for paid access:

* A CLI invoked by another agent takes its credential from argv or the
  environment, where it lands in process listings, shell history and logs.
* It has no per-call identity — the caller is whoever ran the process.
* Metering a local binary means either phoning home on every invocation, which
  breaks the offline promise that makes the CLI worth having, or trusting the
  client, which is not metering.

The remote MCP server in MODEL-3 is the natural surface. An agent calls a tool
over Streamable HTTP, identity is per-connection, and metering is server-side.
**The CLI stays free, local and unmetered** — it is the free path, and it should
remain the reason people trust the project.

## 5. The protocol landscape, as of September 2026

* **x402** (Coinbase) revives HTTP 402 for stablecoin machine-to-machine
  micropayments. It has the most production traction — v2 shipped December 2025,
  Stripe integrated it on Base in February 2026, and it reportedly processed on
  the order of 165 million agent transactions in its first months.
* **AP2** (Google, with 60-plus partners) is the authorization layer:
  cryptographically signed mandates binding an agent's purchase to its owner's
  intent and budget, supporting cards and, via an extension, x402.
* **ACP, UCP and MPP** occupy adjacent ground. These are broadly complementary
  rather than competing: AP2-style mandates authorise, x402-style rails settle.

**Cloudflare supports x402**, which matters here because both sites already run
on Cloudflare Pages and MODEL-3 puts a Worker there. If a rail is ever needed,
that is the cheapest possible path.

### Do not build this naively

*Free-Riding the Agentic Web: A Systematic Security Analysis of x402 Payments*
(arXiv 2605.30998) documents free-riding against x402 endpoints along with
time-of-check-to-time-of-use, front-running and payment-verification-ordering
weaknesses. I could not extract the full text, so treat the specifics as
directional — but the shape of the lesson is clear and unsurprising: **verify
settlement before delivering the service**, and assume the caller is adversarial.

For a service whose responses are cheap to produce and valuable to resell, the
free-riding risk is not theoretical. It is another argument for attestation over
metered computation: an attestation is bound to a request and a timestamp, so a
replayed or resold one is detectable in a way that a resold JSON ranking is not.

## What to do now

1. **Identity before payment.** Issue keys, record who called with what
   constraints against which build. Useful immediately for rate limiting, abuse
   and understanding demand, and it is the prerequisite for everything else.
2. **Ship attestation unpriced.** Sign the answers. Publish the verification
   method. Find out whether anyone actually wants a provable recommendation
   before charging for one.
3. **Write the honest-broker rule into the terms**, in the form above.
4. **Revisit metering when the evidence is worth it.** A concrete bar: the
   active benchmark set is meaningfully larger than seven, card scores carry
   per-score sources and dates (MODEL-13), and at least some hardware throughput
   is measured rather than predicted (MODEL-22). Selling recommendations built
   on 14%-complete cards and undated scores would be selling confidence we do
   not have.

## Non-goals, and one refusal

* **Not** selling placement, ranking position, or any form of provider-paid
  visibility. This is the refusal, and it should be permanent.
* **Not** metering the CLI or the downloadable export.
* **Not** building a payment rail before there is a customer. x402 on Cloudflare
  is a few days' work when it is actually needed; building it now means
  maintaining it through everything above.

## What this changes in MODEL-6

MODEL-6 scopes credentials, metering, a 402 rail and a free tier as one piece of
work. On this assessment they separate: identity and attestation are worth doing
now, metering and the rail are premature, and the free tier is not a tier at all
— it is the whole product, with a paid surface eventually sitting beside it.

## Sources

- [Agentic payments protocols compared (Crossmint)](https://www.crossmint.com/learn/agentic-payments-protocols-compared)
- [x402 and Agentic Commerce (AWS)](https://aws.amazon.com/blogs/industries/x402-and-agentic-commerce-redefining-autonomous-payments-in-financial-services/)
- [Agentic Payments 101: ACP, UCP, AP2 and x402](https://medium.com/@adnanmasood/agentic-payments-101-2-2-payment-standards-and-protocols-acp-ucp-ap2-and-x402-26486e6d511f)
- [Free-Riding the Agentic Web: A Systematic Security Analysis of x402 Payments](https://arxiv.org/pdf/2605.30998)
