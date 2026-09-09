#!/usr/bin/env python3
"""Benchmark census: find every LLM benchmark we can, from every source we can, and queue it.

    /opt/homebrew/bin/python3.11 scripts/benchmarks/census.py [--skip firecrawl,arxiv,...]

Writes benchmarks/_census/candidates.jsonl (one line per lead, with source and evidence),
benchmarks/_census/queue_p2.json (registry-backed benchmarks not yet in P1),
benchmarks/_census/queue_p3.json (everything else, deduped) and a report.
Nothing here writes a page; humans and the writing agents do that.
"""
from __future__ import annotations

import collections
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch import resolve_key, scrape  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
CENSUS = ROOT / "benchmarks" / "_census"
SOURCES = yaml.safe_load((CENSUS / "sources.yaml").read_text())
UA = {"User-Agent": "modelspec-benchmark-census/0.1 (+https://modelspec.dev; mailto:claude@terbeest.com)"}
SKIP = set((sys.argv[sys.argv.index("--skip") + 1] if "--skip" in sys.argv else "").split(",")) - {""}

leads: list[dict] = []
counts: collections.Counter = collections.Counter()


def add(name: str, source: str, url: str = "", evidence: str = "", category: str = "", kind: str = "lead", extra: dict | None = None) -> None:
    name = re.sub(r"\s+", " ", name).strip(" -:–—*`")
    if not name or len(name) > 80 or is_noise(name):
        return
    leads.append({"name": name, "slug": slugify(name), "source": source, "url": url, "evidence": evidence[:240],
                  "category_hint": category, "kind": kind, **(extra or {})})
    counts[source] += 1


GENERIC = {"benchmark", "benchmarks", "leaderboard", "leaderboards", "eval", "evals", "evaluation", "evaluations", "dataset", "datasets", "paper", "papers", "code",
           "survey", "github", "website", "demo", "results", "result", "test", "tests", "blog", "license", "star", "stars", "badge", "prs welcome", "awesome", "data",
           "model", "models", "llm", "llms", "agent", "agents", "tool", "tools", "task", "tasks", "arxiv", "pdf", "link", "home", "docs", "documentation", "readme", "contents", "table of contents"}


def is_noise(name: str) -> bool:
    n = name.strip()
    low = n.lower()
    if low in GENERIC or low.startswith(("![", "[", "http", "www.", "<")) or "](" in n:
        return True
    if re.search(r"\b(survey|awesome|tutorial|roadmap|cheatsheet|course|lecture|workshop|newsletter)\b", low):
        return True
    if len(n.split()) > 6 or not re.search(r"[A-Za-z]", n):
        return True
    return False


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[\-–—/.]", "_", s)
    s = re.sub(r"[^a-z0-9_ ]", "", s)
    s = re.sub(r"\s+", "_", s.strip())
    s = re.sub(r"_+", "_", s)
    return s.strip("_")[:80]


def get(url: str, timeout: int = 60) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def gh_api(path: str) -> list | dict:
    r = subprocess.run(["gh", "api", path, "--paginate"], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[:200])
    out = r.stdout.strip()
    # --paginate concatenates JSON arrays; join them
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        parts = re.findall(r"\[.*?\](?=\[|$)", out, re.S)
        merged = []
        for p in parts:
            merged.extend(json.loads(p))
        return merged


NAME_IN_TITLE = re.compile(r"^\s*\$?([A-Za-z][\w\-\.]{1,40}(?:\s?[A-Za-z0-9\-]{1,12}){0,3}?):\s")
BENCHY = re.compile(r"(bench|eval|qa\b|arena|leaderboard|suite|test\b|exam|olympiad|challenge)", re.I)


def name_from_title(title: str) -> str | None:
    m = NAME_IN_TITLE.match(title)
    if not m:
        return None
    name = m.group(1).strip()
    if len(name.split()) > 4:
        return None
    if not (BENCHY.search(name) or BENCHY.search(title) or re.search(r"[A-Z]{2,}", name)):
        return None
    return name


# ---------- 1. the model cards ----------
def src_cards() -> None:
    q = json.loads((CENSUS / "queue_p1.json").read_text())
    for e in q:
        add(e["id"], "cards", "", f"{e['models_reporting']} models report it", kind="registry", extra={"priority": 1, "id_hint": e["id"]})


# ---------- 2. lm-evaluation-harness ----------
def src_lm_eval() -> None:
    md = get(SOURCES["registries"][0]["url"])
    for line in md.splitlines():
        if not line.startswith("|") or "---" in line or line.lower().startswith("| task family") or line.lower().startswith("| name"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        name = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", cells[0]).strip("`")
        desc = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", cells[1])
        if name and name.lower() not in ("task family", "name"):
            # Do NOT build a per-task directory url: many tasks live inside a shared directory
            # (the Bangla tasks all sit under lm_eval/tasks/bangla/), so a fabricated path 404s.
            # Point at the registry table instead and let the writer find the real task file.
            add(name, "lm_eval", "https://github.com/EleutherAI/lm-evaluation-harness/blob/main/lm_eval/tasks/README.md",
                desc, kind="registry", extra={"priority": 2, "harness": {"lm_eval": name},
                                              "url_note": "registry table; the task file may live in a shared directory"})


# ---------- 3. inspect_evals ----------
def src_inspect() -> None:
    items = gh_api("repos/UKGovernmentBEIS/inspect_evals/contents/src/inspect_evals")
    for it in items if isinstance(items, list) else []:
        n = it.get("name", "")
        if it.get("type") == "dir" and not n.startswith(("_", ".")) and n not in ("utils", "metadata", "common", "tests"):
            add(n, "inspect_evals", it.get("html_url", ""), "inspect_evals task package", kind="registry", extra={"priority": 2, "harness": {"inspect_evals": n}})

# ---------- 4. BIG-bench ----------
def src_bigbench() -> None:
    items = gh_api("repos/google/BIG-bench/contents/bigbench/benchmark_tasks")
    for it in items if isinstance(items, list) else []:
        n = it.get("name", "")
        if it.get("type") == "dir" and not n.startswith(("_", ".")):
            add(n, "bigbench", it.get("html_url", ""), "BIG-bench task", kind="registry", extra={"priority": 2, "harness": {"bigbench": n}})

# ---------- 5. HELM scenarios and OpenCompass datasets (GitHub API) ----------
def src_helm() -> None:
    reg = SOURCES["registries"][3]
    items = gh_api(f"repos/{reg['repo']}/contents/{reg['path']}")
    for it in items if isinstance(items, list) else []:
        n = it.get("name", "")
        if n.endswith("_scenario.py") and not n.startswith("test_"):
            name = n[:-len("_scenario.py")]
            add(name, "helm", it.get("html_url", ""), "HELM scenario", kind="registry", extra={"priority": 2, "harness": {"helm": name}})


def src_opencompass() -> None:
    reg = SOURCES["registries"][4]
    items = gh_api(f"repos/{reg['repo']}/contents/{reg['path']}")
    for it in items if isinstance(items, list) else []:
        if it.get("type") == "dir" and not it["name"].startswith(("_", ".")):
            add(it["name"], "opencompass", it.get("html_url", ""), "OpenCompass dataset config", kind="registry", extra={"priority": 2, "harness": {"opencompass": it["name"]}})


# ---------- 6. Hugging Face datasets and leaderboard spaces ----------
def src_hf() -> None:
    for term in ("benchmark", "bench", "eval", "leaderboard", "arena"):
        try:
            data = json.loads(get(f"https://huggingface.co/api/datasets?search={term}&limit=1000&sort=downloads&direction=-1"))
        except Exception as e:
            print("hf datasets", term, "failed:", e)
            continue
        for d in data:
            did = d.get("id", "")
            short = did.split("/")[-1]
            if BENCHY.search(short) or "benchmark" in " ".join(d.get("tags", [])):
                add(short, "hf_datasets", "https://huggingface.co/datasets/" + did, f"downloads={d.get('downloads', 0)} tags={','.join(t for t in d.get('tags', []) if 'task' in t)[:120]}", extra={"priority": 3, "hf_id": did, "downloads": d.get("downloads", 0)})
        time.sleep(1)
    try:
        data = json.loads(get("https://huggingface.co/api/spaces?search=leaderboard&limit=1000&sort=likes&direction=-1"))
        for s in data:
            sid = s.get("id", "")
            add(sid.split("/")[-1], "hf_spaces", "https://huggingface.co/spaces/" + sid, f"likes={s.get('likes', 0)}", kind="leaderboard", extra={"priority": 3, "likes": s.get("likes", 0)})
    except Exception as e:
        print("hf spaces failed:", e)


# ---------- 7. arXiv titles ----------
def src_arxiv() -> None:
    base = "https://export.arxiv.org/api/query?"
    queries = ['ti:benchmark AND (cat:cs.CL OR cat:cs.AI OR cat:cs.LG OR cat:cs.CV)', 'ti:bench AND (cat:cs.CL OR cat:cs.AI)',
               'ti:"evaluation suite" AND cat:cs.CL', 'ti:leaderboard AND cat:cs.CL', 'abs:"we introduce" AND ti:benchmark AND cat:cs.CL']
    for q in queries:
        for start in range(0, 800, 200):
            url = base + urllib.parse.urlencode({"search_query": q, "start": start, "max_results": 200, "sortBy": "submittedDate", "sortOrder": "descending"})
            xml = None
            for attempt in range(4):
                try:
                    xml = get(url, timeout=120)
                    break
                except Exception as e:
                    print("arxiv retry", attempt, e)
                    time.sleep(20 * (attempt + 1))
            if xml is None:
                break
            root = ET.fromstring(xml)
            ns = {"a": "http://www.w3.org/2005/Atom"}
            entries = root.findall("a:entry", ns)
            if not entries:
                break
            for en in entries:
                title = re.sub(r"\s+", " ", en.findtext("a:title", "", ns))
                name = name_from_title(title)
                if not name:
                    continue
                aid = en.findtext("a:id", "", ns).rsplit("/", 1)[-1]
                pub = en.findtext("a:published", "", ns)[:10]
                add(name, "arxiv", "https://arxiv.org/abs/" + aid, title, extra={"priority": 3, "arxiv": aid, "published": pub})
            time.sleep(6)


# ---------- 8. awesome lists on GitHub ----------
def src_awesome() -> None:
    seen = set()
    for q in ("awesome llm benchmarks", "awesome llm evaluation", "awesome-llm-eval", "awesome benchmarks language models", "llm leaderboard list awesome", "awesome agent benchmarks"):
        try:
            res = json.loads(subprocess.run(["gh", "api", f"search/repositories?q={urllib.parse.quote(q)}&sort=stars&per_page=8"], capture_output=True, text=True, timeout=60).stdout)
        except Exception as e:
            print("gh search failed:", e)
            continue
        for repo in res.get("items", []):
            full = repo["full_name"]
            if full in seen:
                continue
            seen.add(full)
            for branch in (repo.get("default_branch") or "main",):
                try:
                    md = get(f"https://raw.githubusercontent.com/{full}/{branch}/README.md")
                except Exception:
                    continue
                for m in re.finditer(r"\[([^\]]{2,60})\]\((https?://[^)\s]+)\)", md):
                    label, link = m.group(1), m.group(2)
                    if re.search(r"(arxiv|github|huggingface|openreview|\.ai/|\.org/|\.io/)", link) and (BENCHY.search(label) or re.search(r"[A-Z]{2,}", label)) and not re.search(r"(paper|pdf|code|website|blog|awesome|star|license|badge)", label, re.I):
                        add(label, "awesome:" + full, link, "listed in " + full, extra={"priority": 3})
        time.sleep(1)


# ---------- 9. Firecrawl search: startups, Reddit, papers, every genre ----------
GENRES = ["reasoning", "math olympiad", "coding", "software engineering agent", "tool use function calling", "web agent browsing", "computer use GUI agent",
          "long context", "multilingual", "translation", "safety red teaming", "hallucination factuality", "instruction following", "RAG retrieval", "embedding reranking",
          "vision language", "video understanding", "audio speech", "medical clinical", "legal", "finance", "science chemistry biology", "cybersecurity CTF",
          "robotics embodied", "multi-agent", "games planning", "spatial reasoning", "OCR document understanding", "data science analysis", "hardware verilog EDA",
          "education tutoring", "creative writing", "conversation dialogue", "theory of mind social", "efficiency latency cost"]


def firecrawl_search(query: str, limit: int = 10) -> list[dict]:
    import hashlib
    cache_dir = CENSUS / "cache"; cache_dir.mkdir(parents=True, exist_ok=True)
    cpath = cache_dir / ("search_" + hashlib.sha256(f"{query}|{limit}".encode()).hexdigest()[:24] + ".json")
    if cpath.exists():
        return json.loads(cpath.read_text())
    key = resolve_key()
    body = json.dumps({"query": query, "limit": limit}).encode()
    req = urllib.request.Request("https://api.firecrawl.dev/v2/search", data=body, method="POST", headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.load(r)
            data = d.get("data")
            res = (data.get("web") if isinstance(data, dict) else data) or []
            cpath.write_text(json.dumps(res))
            return res
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                time.sleep(12 * (attempt + 1))
                continue
            print("firecrawl search", query[:40], "failed:", e.code)
            return []
        except Exception as e:
            print("firecrawl search", query[:40], "failed:", e)
            return []
    return []


def src_firecrawl_search() -> None:
    queries = [f"{g} benchmark for large language models" for g in GENRES]
    queries += [f"new {g} benchmark 2026 LLM" for g in GENRES[::3]]
    queries += ["site:reddit.com new LLM benchmark", "site:reddit.com/r/LocalLLaMA benchmark results", "site:reddit.com/r/MachineLearning benchmark language models 2026",
                "site:huggingface.co/papers benchmark LLM 2026", "startup LLM evaluation benchmark launch 2026", "obscure LLM benchmarks nobody reports",
                "site:github.com LLM benchmark leaderboard 2026", "benchmark saturated successor harder LLM 2026", "agent benchmark leaderboard 2026",
                "site:openreview.net benchmark language models 2026", "site:x.com new benchmark LLM release", "Chinese LLM benchmark C-Eval CMMLU successors"]
    for q in queries:
        for r in firecrawl_search(q, 10):
            title = (r.get("title") or "").strip()
            url = r.get("url") or ""
            desc = (r.get("description") or "")[:240]
            name = name_from_title(title)
            if name:
                add(name, "firecrawl_search", url, title + " — " + desc, extra={"priority": 3, "query": q})
            else:
                # keep the page as a lead of kind 'page' for a human/agent to mine
                add(title[:80], "firecrawl_search_page", url, desc, kind="page", extra={"priority": 4, "query": q})
        time.sleep(3)


# ---------- 10. aggregator pages (scrape allowlisted hosts only) ----------
def src_aggregators() -> None:
    allow = set(SOURCES["scrape_allow"])
    for url in SOURCES["aggregator_pages"]:
        host = urllib.parse.urlparse(url).netloc.replace("www.", "")
        if host not in allow:
            print("not allowlisted, skipped:", url)
            continue
        try:
            data = scrape(url, ["markdown", "links"])
        except Exception as e:
            print("scrape failed", url, e)
            continue
        md = data.get("markdown") or ""
        for m in re.finditer(r"\[([^\]]{2,60})\]\((https?://[^)\s]+)\)", md):
            label = m.group(1)
            if BENCHY.search(label) or re.search(r"[A-Z]{2,}", label):
                add(label, "aggregator:" + host, m.group(2), "linked from " + url, kind="lead", extra={"priority": 3})
        for line in md.splitlines():
            for tok in re.findall(r"\b([A-Z][A-Za-z0-9]+(?:-[A-Za-z0-9]+)*(?:Bench|Eval|QA|Arena|Exam)\b(?:\s?(?:Verified|Pro|Hard|Diamond|v\d))?)", line):
                add(tok, "aggregator:" + host, url, line.strip()[:160], extra={"priority": 3})
        time.sleep(1)


def main() -> None:
    steps = [("cards", src_cards), ("lm_eval", src_lm_eval), ("inspect_evals", src_inspect), ("bigbench", src_bigbench), ("helm", src_helm),
             ("opencompass", src_opencompass), ("hf", src_hf), ("arxiv", src_arxiv), ("awesome", src_awesome), ("firecrawl", src_firecrawl_search), ("aggregators", src_aggregators)]
    for name, fn in steps:
        if name in SKIP:
            print("skip", name)
            continue
        t0 = time.time()
        try:
            fn()
        except Exception as e:
            print(f"{name} FAILED: {e}")
        n_leads = sum(v for k, v in counts.items() if k == name or k.startswith(name.rstrip("s") + ":") or (name == "firecrawl" and k.startswith("firecrawl")) or (name == "hf" and k.startswith("hf_")))
        print(f"{name}: {n_leads} leads in {time.time() - t0:.0f}s", flush=True)
    CENSUS.mkdir(parents=True, exist_ok=True)
    with (CENSUS / "candidates.jsonl").open("w") as f:
        for l in leads:
            f.write(json.dumps(l) + "\n")
    # dedupe by slug
    by_slug: dict[str, dict] = {}
    for l in leads:
        if l["kind"] == "page":
            continue
        s = l["slug"]
        if not s or len(s) < 3:
            continue
        e = by_slug.setdefault(s, {"slug": s, "names": collections.Counter(), "sources": [], "urls": [], "priority": 9, "harness": {}, "category_hints": collections.Counter()})
        e["names"][l["name"]] += 1
        e["sources"].append(l["source"])
        if l.get("url"):
            e["urls"].append(l["url"])
        e["priority"] = min(e["priority"], l.get("priority", 9))
        e["harness"].update(l.get("harness", {}))
        if l.get("category_hint"):
            e["category_hints"][l["category_hint"]] += 1
    p1 = {json.loads(x)["slug"] for x in (CENSUS / "candidates.jsonl").read_text().splitlines() if json.loads(x)["source"] == "cards"}
    q2, q3 = [], []
    for s, e in by_slug.items():
        entry = {"slug": s, "name": e["names"].most_common(1)[0][0], "aliases": [n for n, _ in e["names"].most_common()[1:6]],
                 "sources": sorted(set(e["sources"])), "source_count": len(set(e["sources"])), "urls": sorted(set(e["urls"]))[:8],
                 "harness": e["harness"], "category_hint": (e["category_hints"].most_common(1) or [("", 0)])[0][0], "priority": e["priority"]}
        if s in p1:
            continue
        (q2 if e["priority"] <= 2 else q3).append(entry)
    CURATED = ("awesome:", "aggregator:", "firecrawl_search", "lm_eval", "helm", "opencompass", "inspect_evals", "bigbench", "arxiv")
    dl = {}
    for l in leads:
        if l["source"] == "hf_datasets":
            dl[l["slug"]] = max(dl.get(l["slug"], 0), int(l.get("downloads") or 0))
    import math
    for e in q2 + q3:
        curated = any(s.startswith(CURATED) for s in e["sources"])
        benchy = bool(BENCHY.search(e["name"]) or re.search(r"[A-Z]{2,}", e["name"]))
        e["downloads"] = dl.get(e["slug"], 0)
        e["score"] = round(10 * e["source_count"] + (5 if curated else 0) + (3 if benchy else 0) + min(5.0, math.log10(e["downloads"] + 1)), 1)
    q2.sort(key=lambda x: (-x["score"], x["slug"]))
    q3.sort(key=lambda x: (-x["score"], x["slug"]))
    short = [e for e in q3 if e["source_count"] >= 2 or (any(s.startswith(CURATED) for s in e["sources"]) and (BENCHY.search(e["name"]) or re.search(r"[A-Z]{2,}", e["name"]))) or e["downloads"] >= 5000]
    (CENSUS / "queue_p2.json").write_text(json.dumps(q2, indent=1))
    (CENSUS / "queue_p3.json").write_text(json.dumps(q3, indent=1))
    (CENSUS / "queue_p3_short.json").write_text(json.dumps(short, indent=1))
    report = [f"# Benchmark census report ({time.strftime('%Y-%m-%d %H:%M')})", "", f"leads: {len(leads)}", f"unique slugs: {len(by_slug)}",
              f"P1 (cards): {len(p1)}", f"P2 (registries): {len(q2)}", f"P3 (discoveries): {len(q3)}, of which shortlist: {len(short)}", "", "## Leads by source", ""]
    report += [f"- {k}: {v}" for k, v in counts.most_common()]
    multi = [e for e in q3 if e["source_count"] >= 3][:60]
    report += ["", "## P3 candidates seen in three or more sources", ""] + [f"- {e['name']} ({e['source_count']}: {', '.join(e['sources'][:5])})" for e in multi]
    (CENSUS / "REPORT.md").write_text("\n".join(report) + "\n")
    print("\n".join(report[:12]))


if __name__ == "__main__":
    main()
