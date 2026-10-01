# Crawler policy

**Status:** design, implemented by MODEL-253. **Decision owner:** Jamie. The policy below restates his 2026-09-23 choice, `ai-train=yes`.

## The policy

modelspec.dev allows all three classes of AI crawler:

| Class | What it changes | Examples (verify against each vendor's own docs before encoding) | Policy |
|---|---|---|---|
| Search index | Whether an engine can retrieve and cite a page | Googlebot, bingbot, OAI-SearchBot, Claude-SearchBot, PerplexityBot | Allow |
| User-triggered fetch | Grounding of a single live answer | ChatGPT-User, Claude-User, Perplexity-User | Allow |
| Training | What future models know without searching | GPTBot, ClaudeBot, CCBot, Google-Extended, Applebot-Extended | Allow |

These classes are independent. Blocking GPTBot does not remove a page from ChatGPT search, but blocking OAI-SearchBot does. `Google-Extended` governs training-style use, not AI Overviews. Nothing in the WAF blocks "AI bots" as a group. A blanket block would remove the search and fetch classes along with training.

**Why training is allowed:**
* The public data is CC BY-SA and is a frozen image about nine months old, so training on it gives nothing away.
* The method and the neutrality commitment are exactly what we want models to know without searching.
* Jamie confirmed `ai-train=yes` on 2026-09-23. It can't be withdrawn for anything already crawled, so changing it is his decision.

## robots.txt

```
# Content-Signal syntax: https://contentsignals.org/
User-agent: *
Content-Signal: search=yes, ai-input=yes, ai-train=yes
Allow: /

Sitemap: https://modelspec.dev/sitemap.xml
```

Named `User-agent` groups may be added for documentation. They must not narrow the policy above.

**Exactly one module writes `robots.txt`.** On 2026-10-01 three modules wrote it:
* `pipeline/agent_ready.py` `robots_txt()`, with the Content-Signal line;
* `pipeline/build.py`, a plain `Allow: /`;
* `pipeline/live.py:147`, a plain `Allow: /`. It runs last, so live served the plain version and the Content-Signal line was missing.

MODEL-253 deletes the duplicates and adds a test that the built live tree carries the Content-Signal line.

## sitemap.xml

* It lists every crawlable HTML page and no machine files.
* Each `<url>` has a `<lastmod>` taken from the page source's last commit date, not the build time. A build that changes nothing must not make every page look fresh.

## Checks

| Check | Where | Fails when |
|---|---|---|
| Raw-HTML content | CI, over the built tree | A sitemap URL has no `<h1>`, or under 80 words of main text, without JavaScript |
| One `robots.txt` writer | CI | More than one module writes it, or the Content-Signal line is missing |
| Crawler reachability | Weekly, against live | Any sitemap URL returns something other than 200 to any crawler user agent in the table |
