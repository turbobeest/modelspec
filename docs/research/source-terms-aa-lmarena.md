# What Artificial Analysis's and LMArena's terms allow

**MODEL-117. Read 2026-09-23. This summarises two other companies' terms as
they stood on that date. It is not legal advice, and it drafts no terms of our
own.**

Scores are facts, and copyright does not protect facts. The risk here is
**contract**: terms we accept by using a site can forbid reuse, scraping or
commercial redistribution even where copyright would not. Of the 1,223
per-score `evidence` rows on cards, **1,046 (86%) cite artificialanalysis.ai**
(across 312 cards) and **90 cite lmarena.ai** (90 cards, all
`arena_elo_style_control`). All of them came from one manual run of
`scripts/fetch_ranking_leaderboards.py` on 2026-09-10, which fetched each
leaderboard page over plain HTTP and parsed the page data. No workflow runs
that script.

## The answer

- **Artificial Analysis: its terms forbid almost everything we do with its
  numbers.** Its website licence covers personal, non-commercial use only. The
  licence forbids scraping, commercial exploitation of anything shown on the
  site, and use of the site to build a competing product. The terms for its
  API allow brief, attributed citations of single numbers. They forbid
  structured or machine-readable reproduction, delivery through any
  customer-facing API, and any product that gives model-selection guidance.
  ModelSpec is that kind of product. **Ask them for a licence.** Until they
  answer, do not sign up for their free API as a workaround (see
  [Recommendation](#recommendation)).
- **LMArena: its website terms are just as strict, but it publishes the
  leaderboard itself under CC BY 4.0** on Hugging Face
  (`lmarena-ai/leaderboard-dataset`). It is updated several times a month
  and keeps the full history. Take the 90 rows from that dataset instead of the web page, and
  attribute them as CC BY requires. Then every use listed below is allowed.
  There is no need to ask.
- **For the MODEL-108 profiles (draft PR #169):** the Arena-based keys can
  go ahead once they are re-sourced from the dataset. Keys that depend on
  Artificial Analysis numbers should wait for Artificial Analysis's answer.

## What was read

All pages were fetched with plain HTTP GET on 2026-09-23. Firecrawl was not
used (0 credits). A dated copy of each page is kept outside the repository,
because these are other parties' copyrighted pages.

| Document | URL | Version it states |
| --- | --- | --- |
| AA Website Terms of Use | `artificialanalysis.ai/terms-of-use` | "Last revised: September 15 2026" |
| AA Terms of Use, PDF | `artificialanalysis.ai/docs/legal/Terms-of-Use.pdf` | v1.0, 28 April 2024. Same text as the HTML page, sentence by sentence. sha256 `3456cc92…` |
| AA Data Platform Terms and Conditions | `artificialanalysiscdn.com/legal/ProDataPlatformTerms.pdf` | v1.1, 19 August 2026. sha256 `6596b1b4…` |
| AA API reference (free API) | `artificialanalysis.ai/api-reference` | undated |
| AA FAQ, contact, methodology, robots.txt | `artificialanalysis.ai/{faq,contact,methodology,robots.txt}` | undated |
| Arena Terms of Use Agreement | `arena.ai/terms-of-use`, which redirects to `help.arena.ai/articles/5629909088-terms-of-use` | "Last Updated Date: 2026-02-23" |
| Arena FAQ, help centre, robots.txt | `arena.ai/{faq,robots.txt}`, `help.arena.ai` | undated |
| Arena leaderboard dataset | `huggingface.co/datasets/lmarena-ai/leaderboard-dataset` | `license: cc-by-4.0`. Created 2026-04-02, last modified 2026-09-23 |
| CC BY 4.0 legal code | `creativecommons.org/licenses/by/4.0/legalcode.en` | 4.0 |

`lmarena.ai` now redirects to `arena.ai`. The company is Arena Intelligence,
Inc. Neither site offered a separate "how to cite" page. The Arena help centre
has no article on data reuse. The Arena FAQ points researchers to its Hugging
Face datasets.

Clauses are paraphrased below with section references, not quoted, so that
their text is not reproduced. The only verbatim text is the attribution
strings that Artificial Analysis requires, because those strings are the
answer. The Arena help-centre page shows its headings without numbers. The
section numbers below are inferred from the terms' own cross-references
(§1.1, §3.3, §7.1 and §15 are cited by number in the text).

## Artificial Analysis

**Which document binds us.** The Website Terms of Use bind anyone who visits
or uses the site. They claim acceptance from use alone (preamble). The Data
Platform Terms bind a "Customer" (§1.2): someone who has subscribed, or who has
registered for the API, and that includes the free tier (Scope). We have never
registered. Our rows came from reading the public leaderboard page. So today
the Website Terms are the ones that bind us. The Data Platform Terms matter in
two ways. They show the terms we would accept by taking the API. They also show
how Artificial Analysis views uses like ours.

| Question | Answer | Where |
| --- | --- | --- |
| Commercial reuse of published scores? | **No.** The site licence is personal and non-commercial only. It forbids commercial exploitation of any content displayed on the site. The API terms allow one narrow public use: brief citations of single numbers in articles or posts, with attribution, and never in structured, tabular or machine-readable form. | Website ToU §2.1, §2.2(a). DPT §2.3 "All Tiers" (c) |
| Redistribution in our dataset or API? | **No.** The site may not be copied, republished, downloaded or distributed. Under the API terms, raw Data may not be delivered through any customer-facing product, API or dashboard. It may not be combined with other sources to make a product for third parties. Structured reproductions do not count as "Derived Data". Artificial Analysis reserves the exclusive right to distribute the Data. | ToU §2.2(d). DPT §2.4(a)–(d), §1.10(a)–(c), §7.2 |
| Automated access? | **Scraping is forbidden.** Automated queries, and stripping or mining data, are banned. The one exception lets public search engines build indices, and only within robots.txt. robots.txt says `Allow: /`, but that permits crawling. It grants no licence. | ToU §3.3(b)(vi). robots.txt |
| Is there an API? | **Yes. It is free, it needs an account key, and it allows 1,000 requests a day.** Cache the responses, and keep the key out of client-side code. The API is subject to both documents. A commercial API is available to partners separately. | API reference ("Overview & Access", "Attribution & Sharing of Data", "Free … Data API") |
| Attribution | **Always required.** The API page asks for a link to `https://artificialanalysis.ai/`. The exact forms are in DPT §5.1. **Data and metrics:** `Source: Artificial Analysis (artificialanalysis.ai)`, with a hyperlink where feasible. **Derived Data:** `Based on data from Artificial Analysis`, plus a statement that it is ours and not endorsed by Artificial Analysis (§5.2). **Charts:** the Artificial Analysis logo must be visible on the chart, used as their brand guidelines require (§5.3). | API reference. DPT §2.3, §5.1–5.3 |
| Charts from their numbers | **Not under the site licence.** Under the API terms, customers may share charts publicly if the logo is on the chart. A chart of our own that shows individual scores is not "Derived Data", because the data points can still be identified. | ToU §2.2. DPT §2.3(b), §1.10(d), §5.1 |
| Competing service | **Forbidden.** The site may not be accessed to build a similar or competing product. The API terms define "Competitive Product" to include model or provider selection guidance for AI models. They forbid using the Data to run one without written consent, and allow immediate termination if we do. Artificial Analysis runs its own "Model Recommender". | ToU §2.2(c). DPT §1.9, §2.5, §11.5(b) |
| Anything else that bites | We may not change values while presenting them as Artificial Analysis's. We may not select or omit data in a misleading way that implies their endorsement, and they may demand a correction (§3.1–3.2). There is no liability cap for breaching the redistribution or anti-competitive clauses, and we would owe an indemnity (§10.3–10.4). On termination, raw Data must be deleted (§11.7). These clauses survive for 5 years (§15). The Data may not be used to train AI (§2.6(d)). The logo and marks need consent (ToU §10.7). The contact page sells licences for customer-facing products and feeds, which is the route they intend. | DPT as cited. ToU §10.7. Contact page |

## LMArena (Arena)

**The website terms.** Use of the service must be personal or internal
business use only (§1). The terms forbid reproducing, mirroring,
distributing or commercially exploiting the service (§5(i)). They forbid
programmatic or automated access (§5(vi)). They forbid scrapers, and they name
extracting model names, identifiers and versions (§5(vii)). The only exception
is for search-engine indexing. robots.txt allows `/leaderboard` and disallows
`/api/` and `/nextjs-api/`. Our script parsed the data embedded in the
`/leaderboard` HTML. robots.txt does not make that permitted: §5(vii) covers
scrapers whatever robots.txt says. The Arena marks may not be used with our
products without permission (§4.2). No API for leaderboard data is offered.

**The open route.** `lmarena-ai/leaderboard-dataset` holds "historical
snapshots" of the Arena leaderboard. There is one subset per arena (`text`,
`text_style_control`, `vision`, `webdev`, `search`, `document`, image, video
and agent). Each subset has a `full` split and a `latest` split. The columns
are rating, confidence bounds, vote count, rank, category and
`leaderboard_publish_date`. The dataset is licensed CC BY 4.0. That licence:

- allows reproduction and sharing, including commercial use, and allows
  adapted material (§2(a)(1)).
- licenses any sui generis database rights along with copyright (§4).
- requires, when we share: the creator's name, any copyright, licence and
  disclaimer notices supplied, a link to the licence, a link to the material
  where reasonable, and a note of any changes we made (§3(a)(1)). Any
  reasonable manner that suits the medium is enough (§3(a)(2)).
- forbids adding terms that stop recipients from exercising the licence
  (§2(a)(5)(B)). A licence we apply to adapted material must still let
  recipients comply (§3(a)(4)). Our CC BY-SA 4.0 data licence meets that.

The dataset card gives no preferred attribution wording. Arena's other
Hugging Face datasets carry mixed licences (Apache-2.0, CC BY 4.0, MIT, or
none). Only the leaderboard dataset matters here.

**The re-source is a fresh reading, not a URL swap.** Our rows were observed
on 2026-09-10. In `text_style_control` the published dates nearest to that are
2026-09-02 and 2026-09-11, and the latest is 2026-09-13. Each re-sourced row
should take its score and date from one published snapshot.

| Question | Answer (from the CC BY dataset) | Where |
| --- | --- | --- |
| Commercial reuse | Yes | CC BY 4.0 §2(a)(1) |
| Redistribution in our dataset or API | Yes, with attribution. Recipients must be able to follow CC BY. | §2(a)(1), §2(a)(5)(B), §3(a)(4) |
| Automated access | Downloading the dataset from Hugging Face: yes. Scraping arena.ai: no. | Arena ToU §5(vi)–(vii) |
| Attribution | Creator (Arena / LMArena), a link to the dataset, "CC BY 4.0" with a link, and a note of changes, such as normalising or re-keying | CC BY 4.0 §3(a) |
| Charts | Yes. Attribute them, and say what we changed. Do not use the Arena logo. | §3(a)(1)(B). ToU §4.2 |
| Anything else | No limit on competing services and no rate limit in the licence. Do not suggest that Arena endorses us (§2(a)(6)). | CC BY 4.0 |

## The EU database right

Neither source relies on it in its terms. Artificial Analysis claims ownership
of the Data and trade secrets instead (DPT §7.1). The right is available only
to makers who are nationals or residents of an EU member state, or companies
established in one (Directive 96/9/EC, Art. 11). Artificial Analysis, Inc.
and Arena Intelligence, Inc. are both US companies. For the Arena dataset the
question does not arise, because CC BY 4.0 §4 licenses any such right.

## Our uses

"Arena" below means Arena scores taken from the CC BY dataset. The 90 rows we
hold today were scraped. Until they are re-sourced, they carry the same "not
allowed" as scraping.

| Our use | Artificial Analysis | Arena (CC BY dataset) |
| --- | --- | --- |
| Card evidence rows in the public repo, labelled CC BY-SA | **Not allowed.** Structured reproduction, released under our licence. | Allowed with attribution |
| Static export, `modelspec.dev/api/*.json` | **Not allowed.** Machine-readable redistribution (ToU §2.2(d). DPT §2.3, §2.4(b)) | Allowed with attribution |
| Model and benchmark pages, which show evidence tables | **Not allowed.** Tabular reproduction on a commercial site. | Allowed with attribution |
| Paid `POST /v1/rank`, and the MCP server | **Not allowed.** Commercial exploitation, a customer-facing API, and a competing product (ToU §2.2(a),(c). DPT §2.4(c), §2.5) | Allowed with attribution. The response or its docs must carry it. |
| A `rank_score` computed from their numbers without showing them | **Not allowed.** §2.5 forbids using the Data to run a selection product at all, whether or not it is displayed. | Allowed with attribution |
| CLI `snapshot fetch` | **Not allowed.** Bulk machine-readable download. | Allowed with attribution. The snapshot needs the notice. |
| Weekly refresh (MODEL-124) | **Not allowed** by scraping. The free API allows the fetch, but it binds us to DPT §2.4–2.5, which forbid what we would do next. | Allowed from Hugging Face. Not allowed by scraping arena.ai. |
| New-model pipeline (MODEL-113) | Same as MODEL-124 | Same as MODEL-124 |
| Charts (MODEL-119, MODEL-121) | **Not allowed** without a licence. With one, the logo goes on the chart. | Allowed with attribution. Say what was changed. No Arena logo. |
| Social posts (MODEL-114) | **Unclear.** DPT §2.3 allows a brief, attributed citation of a single number, but only for customers, and §2.5 still applies. The website terms allow none. | Allowed with attribution |

## Recommendation

1. **Ask Artificial Analysis for a licence.** Use the draft below. Expect a
   paid licence or a refusal: they sell licences for customer-facing products
   and run a model recommender of their own.
2. **Until they answer.** These are decisions for Jamie. This document does
   not make them.
   - Stop automated fetches of artificialanalysis.ai. That means
     `scripts/fetch_ranking_leaderboards.py` and the Artificial Analysis
     parts of MODEL-124 and MODEL-113.
   - **Do not register for the free API to make the refresh legitimate.**
     Registering makes us a Customer. The anti-competitive clause (§2.5)
     would then clearly bind us, with no liability cap (§10.3).
   - Decide whether the 1,046 Artificial Analysis values stay in the export,
     `/v1/rank` and the snapshot while we wait. Taking them out leaves most
     models unranked. Leaving them in is the exposure a lawyer should size.
   - The fallback: take each benchmark's score from the benchmark's own
     authors or from the model vendor, where one exists. Artificial
     Analysis's own indices, such as AA-LCR and the Intelligence Index, have
     no substitute.
3. **Arena: move to the dataset.** Re-source the 90 rows from
   `lmarena-ai/leaderboard-dataset`. Point MODEL-124 and MODEL-113 at it, and
   add the CC BY attribution (see the gaps below). There is no need to ask
   Arena. A courtesy note is optional.
4. **A lawyer's read is warranted on one question**, and only for Artificial
   Analysis: *Are Artificial Analysis's Website Terms, accepted only by
   browsing, enforceable against Sparks and Sawdust LLC for public pages read
   without an account? If they are, can a contract term restrict our reuse of
   uncopyrightable scores (copyright preemption, 17 U.S.C. §301)? What is our
   exposure for the values we have already published?* Arena needs no lawyer.
   CC BY 4.0 is a standard licence.

### Draft email to Artificial Analysis (for Jamie. Not sent.)

> **To:** hello@artificialanalysis.ai (the contact in the Terms of Use §10.8),
> or the contact form under "Partnerships"
> **Subject:** Licensing request: benchmark scores in ModelSpec
>
> Hello,
>
> I run ModelSpec (modelspec.dev), a catalogue of AI models, through Sparks
> and Sawdust LLC. It ranks models for a use case from published benchmark
> results. The site is free. We also sell a ranking API, and we ship an MCP
> server and an offline CLI that downloads a snapshot of our data.
>
> About 1,000 of our per-score records cite your leaderboard, each with its
> source link and date. We read them from your public pages on 10 September.
> Having now read your Terms of Use and Data Platform Terms, I don't think
> that use is covered. We are not fetching your pages while I ask.
>
> Would you license us to store individual scores, show them with the
> attribution you specify, and use them in our rankings, API and snapshot? If
> that needs a commercial licence, what would it cost and what would it
> cover? If you would rather we only link to you and not hold your numbers, I
> would like to know that too.
>
> We take no referral fees or paid placement, and we publish that commitment.
> Your numbers would be attributed to you and never presented as endorsed by
> you.
>
> Thank you,
> Jamie Ter Beest, Sparks and Sawdust LLC

## What modelspec.dev shows today

This section checks the source (`pipeline/render.py`, `pipeline/export.py`,
`web3d/`) and the live site on 2026-09-23 (`modelspec.dev/m/tii/falcon-h1r-7b/`
and `/api/rank/candidates.json`). Neither source's attribution is met. The
gaps:

1. **Evidence tables name no source.** Each row links to the source URL with
   the anchor text "source" (`evidence_section()`, and the benchmark "Verified
   results" table). Artificial Analysis requires `Source: Artificial Analysis
   (artificialanalysis.ai)`. CC BY requires Arena to be named, with a link to
   the licence.
2. **The page footer says "Data CC BY-SA" with no exception for third-party
   numbers.** Read as written, it releases Artificial Analysis's numbers
   under our licence. The README says sources keep their own licences, and
   the Terms of Service say we grant no rights in them. The footer on every
   page says neither.
3. **`/api/rank/candidates.json` carries the scores with no source.** Its
   `benchmark_scores` hold the Artificial Analysis values, for example
   `aa_lcr`, `critpt` and `gpqa_diamond` on `tii/falcon-h1r-7b`, with no
   source, no attribution and no licence notice. The same file feeds
   `/v1/rank`, the CLI snapshot and the wizard. The per-model JSON does carry
   `source_url` for each evidence row, but no name and no licence.
4. **The wizard (`web3d/downselect.v2.html`) and the explorer name no
   source.** The wizard's footer links "The data behind this" and GitHub
   only.
5. **There is no non-endorsement statement.** DPT §5.2 asks for one wherever
   derived output, such as our rank, is published.
6. **The Arena rows cite `lmarena.ai/leaderboard`,** which is a scraped page
   that now redirects to arena.ai. They should cite the CC BY dataset and its
   publish date.
7. **There are no charts yet.** When MODEL-119 and MODEL-121 add them, a
   chart with Artificial Analysis numbers needs their logo, and only under a
   licence. A chart with Arena numbers needs the CC BY credit and a note of
   what was changed.
