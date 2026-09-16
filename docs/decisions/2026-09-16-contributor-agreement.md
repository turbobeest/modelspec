# Contributor agreement: decision and reasoning (MODEL-11)

**Decided 2026-09-16.** Supersedes the draft contributor agreement that stood in `CLA.md`
from 2026-09-08 to this date.

**This was not reviewed by a lawyer**, by the operator's explicit decision, on the grounds
that ModelSpec is a near-free open source project with unproven revenue. The mitigation
chosen is *adoption of unmodified standard instruments* rather than drafting. Every original
clause is legal surface nobody has tested; the instruments below have been used, in these
exact words, for well over a decade. Where an instrument did not fit, the response was to
change the project's own rules until it did — never to edit the instrument.

Every source carries the date it was read. Where credible sources disagree, both readings are
recorded. Where something could not be verified, it says so.

---

## What was decided

| | |
| --- | --- |
| **Commit mechanic** | Developer Certificate of Origin 1.1, verbatim, in [`DCO`](../../DCO) |
| **Enforcement** | `.github/workflows/dco.yml`, skipping the operator's own commits |
| **Contributor agreement** | Harmony Individual Contributor License Agreement v1.0, Option Five, in [`CLA.md`](../../CLA.md). Asked for only on substantial or ongoing contributions |
| **Contracting party** | Sparks & Sawdust LLC |
| **Governing law** | State of Rhode Island, USA (HA-CLA-I §6.1) |
| **Outbound licences** | Unchanged. Code MIT, data CC BY-SA 4.0 |
| **Retired** | The bespoke `CLA.md` drafted 2026-09-08 |

## Why not simply keep the bespoke agreement

The previous `CLA.md` was written for this project and labelled itself *"Draft, pending legal
review"*. Three specific problems, in descending order of seriousness:

1. **It repurposed `Signed-off-by` to mean something it does not mean anywhere else.**
   `CONTRIBUTING.md`, `README.md` and the pull request template all told contributors that
   `git commit -s` signified agreement to a clause granting the project the right to relicense
   their work under any terms. Since 2004 that line has meant the DCO. A contributor typing
   `git commit -s` would reasonably believe they were certifying provenance, not granting
   relicensing rights. If contested, that gap favours the contributor.
2. **§6, governing law, was blank** — "the jurisdiction to be specified here" — in a document
   three files instructed people to accept, on a public repository.
3. Its patent clause and relicensing clause were original drafting doing load-bearing work.

At the time of the decision the exposure was nil: **269 commits, every author and committer
the owner** (`j@terbeest.com`, `claude@terbeest.com`, `github@terbeest.com`,
`117555601+turbobeest`), no outside contributors, zero forks. The only `Co-authored-by`
trailers name Claude models. So this was the cheapest moment the decision would ever have,
which is what MODEL-11 was for.

## Options considered

### Developer Certificate of Origin 1.1 — adopted
<https://developercertificate.org/>, read 2026-09-16. © 2004, 2006 The Linux Foundation.

The only instrument here that can be adopted as literal unmodified bytes — its own terms
require it: *"Everyone is permitted to copy and distribute verbatim copies of this license
document, but changing it is not allowed."* There is no drafting surface at all. Used by the
Linux kernel, Git, GitLab and much of CNCF. Grants no relicensing right and no patent licence;
the contribution arrives under the project's existing outbound licence and stays there.

Tooling was checked directly against the GitHub API on 2026-09-16:

| Repository | Archived | Last push |
| --- | --- | --- |
| `dcoapp/app` | no | **2026-09-13** |
| `cla-assistant/cla-assistant` | no | 2024-06-06, 248 open issues |
| `contributor-assistant/github-action` | **yes, 2026-03-23** | 2026-03-23 |

The DCO tooling is alive; the CLA bot ecosystem is archived or stale. A self-contained
workflow was written rather than depending on either, so the check has no third-party action
in its supply chain.

The workflow exempts the operator's own commits, as the DCO GitHub App does by default
(`require: members: false`). It matches on the GitHub author login **and** on an explicit list
of the operator's commit addresses, because a commit whose author email is not linked to a
GitHub account reports a null login — which is the case for `j@terbeest.com` on this
repository, and was caught by the check failing on its own introducing pull request. Everyone
else signs off.

### Harmony HA-CLA-I v1.0, Option Five — adopted for substantial contributions
<https://www.harmonyagreements.org/docs/ha-cla-i-v1.pdf>, read 2026-09-16. Version 1.0,
4 July 2011, published under CC BY 3.0.

The only maintained entity-agnostic CLA whose blanks are *designed* to be filled: `[PROJECT_NAME]`,
`[JURISDICTION]`, `[SUBMISSION_INSTRUCTIONS]`, `[NONOWNER_INSTRUCTIONS]`,
`[LIST_OF_MEDIA_LICENSES]`, and five mutually exclusive outbound-licence options. Completing
those is using the document as intended, not modifying it.

It satisfies two requirements of the 2026-09-16 business adjudication natively, with no
drafting:

- **Contracting party** — `[PROJECT_NAME]` is the defined term for "We"/"Us", set to
  Sparks & Sawdust LLC.
- **Assignability to a successor in interest** — §2.1(b) grants a **"transferable"** licence,
  and §6.3 provides: *"If You or We assign the rights or obligations received through this
  Agreement to a third party, as a condition of the assignment, that third party must agree in
  writing to abide by all the rights and obligations in the Agreement."*

**Credible sources disagree about Harmony and both readings are recorded.** Proponents treat it
as the standard non-ASF contributor agreement. Critics argued at its 1.0 release that it
legitimised a maximalist approach to contributor agreements and that its drafting process,
under Chatham House Rules, was insufficiently open — Bradley Kuhn,
["Project Harmony … Considered Harmful"](https://ebb.org/bkuhn/blog/2011/07/07/harmony-harmful.html),
2011, and Richard Fontana, ["The trouble with Harmony"](https://opensource.com/law/11/7/trouble-harmony-part-1),
2011, both read 2026-09-16. It has not been revised since 2011. That staleness is a real cost,
accepted because no maintained alternative fits.

### Apache ICLA v2.2 — rejected
<https://www.apache.org/licenses/icla.pdf>, read 2026-09-16, extracted in full.

**Cannot be adopted unmodified.** It is hard-wired to "The Apache Software Foundation (the
'Foundation')" — §2 and §3 grant rights *to the Foundation*. Renaming the entity throughout is
a modification of a legal instrument.

It also carries a covenant that contradicts the business model: *"the Foundation shall not use
Your Contributions in a way that is contrary to the public benefit or inconsistent with its
nonprofit status and bylaws in effect at the time of the Contribution."* Keeping it binds the
project to nonprofit-style conduct; deleting it is drafting.

Noted for completeness: its §2 grant — "reproduce, prepare derivative works of, publicly
display, publicly perform, sublicense, and distribute" — has **no** scoping to published
material and **no** give-back condition, and so is in fact broader than Harmony's for the
withheld-use case discussed below.

### FSFE Fiduciary Licence Agreement 2.0 — rejected
<https://fsfe.org/activities/fla/fla.en.html>, read 2026-09-16. Entity-agnostic and actively
maintained, and it does permit relicensing. Rejected because its safeguard returns all granted
rights to contributors if the trustee departs from free-software principles — a direct
obstacle to the commercial path.

### Linux Foundation EasyCLA — rejected on eligibility
<https://docs.linuxfoundation.org/lfx/easycla>, read 2026-09-16. Requires hosting the project
under the Linux Foundation. Not available to a solo operator's own repository.

### No agreement at all — rejected, but it is the baseline
GitHub Terms of Service §D.6, "Contributions Under Repository License"
(<https://docs.github.com/en/site-policy/github-terms/github-terms-of-service>, read
2026-09-16, page shows an effective date of 2026-04-27): *"Whenever you add Content to a
repository containing notice of a license, you license that Content under the same terms, and
you agree that you have the right to license that Content under those terms."* This already
applies. The DCO is best understood as this plus an explicit, auditable, per-commit record.

## The requirement no standard instrument met, and what was done about it

The 2026-09-16 business adjudication (`docs/business/decision-record.md`, §2) establishes an
enrichment layer: policy determinations are researched, **never committed to git**, and served
through a paid API. It therefore asked that the contributor grant cover a contribution the
project never publishes and instead serves commercially.

**Harmony does not cover that, and this was verified rather than assumed.** §2.1(b) licenses
the contribution "to reproduce, modify, display, perform and distribute the Contribution **as
part of the Material**", and §1 defines *Material* as "the work of authorship which is made
available by Us to third parties". A contribution never published is arguably outside it.
Option Five additionally carries a give-back: having licensed a contribution under commercial
or proprietary terms, *"We agree to also license the Contribution under the terms of the
license or licenses which We are using for the Material on the Submission Date."* Option Five
is dual-licensing, not proprietary capture.

The response was **not** to edit the instrument, and not to keep bespoke language that happened
to fit. It was to observe that the requirement largely dissolves on inspection:

> **Anything submitted by public pull request is already public at the moment of submission.**
> It cannot meaningfully be withheld. The withheld-value model therefore only ever applies to
> in-house research.

Three rules in `CONTRIBUTING.md` close what remains:

1. Policy determinations are researched in-house and are not accepted through pull requests.
2. Contributions arriving by pull request publish on the normal path; the 90-day delay in
   decision-record §2.2 applies to in-house determinations only.
3. Private, out-of-band submissions are not accepted.

With those, everything a contributor can submit is *published* — and for published
contributions Option Five's give-back costs nothing, because licensing under MIT and
CC BY-SA 4.0 is already what the project does. A standard unmodified instrument now covers the
whole remaining surface.

## Where data contributions fit badly, stated honestly

Every instrument above was written for code. The corpus is not code.

- Much of a model card is **facts**, and facts are not copyrightable —
  *Feist Publications, Inc. v. Rural Telephone Service Co.*, 499 U.S. 340 (1991). Copyright
  reaches only original selection, coordination and arrangement. For a large share of a card
  there may be no copyright for a contributor to license or an agreement to capture.
- What is protectable: the prose, the schema, the editorial selection, and in the EU the
  **sui generis database right** (Directive 96/9/EC), which protects substantial investment in
  obtaining and verifying contents even where the facts are not copyrightable. CC BY-SA 4.0
  licenses that right explicitly
  (<https://wiki.creativecommons.org/wiki/4.0/Sui_generis_database_rights>, read 2026-09-16).
- The real risk in a data contribution is **provenance**, not the grant — material pasted from
  a source whose terms forbid redistribution. No contributor agreement prevents that. The
  project's sourcing rule does more work than any clause here.

## What could not be verified

- **MODEL-11's own ticket text.** The Linear MCP server was not authorised in the session, so
  the ticket body was never read. Scope was taken from the repository's handoff documents.
- **Case law.** No decision testing a DCO sign-off or a CLA click-through was found. Treat
  enforceability as widely assumed and unlitigated, not established.
- **Whether Harmony §2.1(b)'s "as part of the Material" excludes withheld use.** The reading
  above is a plain-language one. It is the reason the structural rules exist, so that the
  question does not need answering.

## Known residual risks

Cheap to mitigate, and mitigated here: the sign-off/agreement collision; sign-off documented
but unenforced (10 of 269 commits carried one); the data licence omitting `hardware/` and
`hosts/`; the stale "ModelRank Contributors" copyright line.

Not cheap, and not resolved by this change:

1. **`[SUBMISSION_INSTRUCTIONS]` in `CLA.md` is unset.** No contributor can be asked to sign
   until a monitored contact address exists. This is the one open blocker.
2. **Third-party source terms across ~2,500 card and benchmark files.** Tracked as REV-2.
   Selling compliance determinations raises questions a free CC BY-SA catalogue never tested.
   This is where an acquirer's diligence will actually go — not to the contributor agreement,
   where there are 269 commits by one author. The mitigation noted in decision-record §7.4
   stands: a determination made by *reading* a licence is the project's own analysis, not
   redistributed scraped data.
3. **Trademark in "ModelSpec"** is untouched by any of this and needs its own search.
4. **No relicensing without contributor consent** once outside contributors exist. Decision
   record §1.1 plans none, and Option Five preserves the option anyway.
