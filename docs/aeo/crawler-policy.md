# Crawler policy

**Status:** built (MODEL-253). **Decision owner:** Jamie. The policy below restates his 2026-09-23 choice, `ai-train=yes`.

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

The published file also names every crawler in the table above (`pipeline/agent_ready.py` `CRAWLERS`), grouped by class, in the same group as `*` with the same rules (RFC 9309). The names document the policy; they don't narrow it.

**Exactly one module writes the site's `robots.txt`: `pipeline/agent_ready.py` `robots_txt()`.** `pipeline/live.py` publishes that same string as `ROBOTS`. The holding tree's dark `robots.txt` (`pipeline/holding.py`) is deliberately separate.

Until 2026-10-01 three modules wrote it: `agent_ready.py`, with the Content-Signal line; `build.py`, a plain `Allow: /`; and `live.py`, another plain copy. `live.py` ran last, so production served a file without the Content-Signal line. `tests/test_crawler_access.py` now holds this to one writer.

## sitemap.xml

* It lists every crawlable HTML page and no machine files.
* Each `<url>` has a `<lastmod>`: the date of the last commit that touched that page's sources (`pipeline/live.py` `PAGE_SOURCES`), not the build time. A build that changes nothing doesn't make every page look fresh. The site build checks out full history, treeless, so `git log` can answer.

## /decide/

The board is a JavaScript app behind a human gate, so a crawler used to get an empty `<div id="root">`. The live build now puts a short server-rendered description in that div (`pipeline/live.py` `decide_capsule()`). It covers what the board does, how Must and Prefer work, that it is free for people and rate-limited, where machines go, and a link to `/method/`. The app replaces it when it mounts. It holds no model data, so answers stay on the board and the API.

## Checks

| Check | Where | Fails when |
|---|---|---|
| Raw-HTML content | Every live build (`python -m pipeline.live build` exits 3) and `tests/test_holding.py` | A sitemap URL has no `<h1>`, or fewer than 80 words of body text, without JavaScript |
| One `robots.txt` writer | `tests/test_crawler_access.py` | A second module writes the site's file, or the Content-Signal line is missing |
| Crawler reachability | `.github/workflows/crawler-access.yml`, weekly (Mondays 09:17 UTC) and on demand | `robots.txt` or any sitemap URL answers anything other than 200 to any named crawler (`python -m pipeline.live crawler-probe`) |
