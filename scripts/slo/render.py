"""The coverage report as Markdown (job summary, issues), HTML (the page) and JSON."""

from __future__ import annotations

import html
import json
from pathlib import Path

from scripts.slo.report import Report, Result

LABEL = {"met": "met", "breach": "BREACH", "error": "NOT MEASURED",
         "not_in_force": "not in force"}
#: Findings listed per target before the rest are counted; the JSON has all.
SHOWN = 40


def headline(report: Report) -> str:
    counts = report.to_json()["counts"]
    if report.status == "met":
        return (f"All {counts['met']} in-force targets met; "
                f"{counts['not_in_force']} not yet in force.")
    return (f"{counts['breach']} target(s) in breach, {counts['error']} not measured, "
            f"{counts['met']} met, {counts['not_in_force']} not yet in force.")


def target_markdown(r: Result, *, shown: int = SHOWN) -> str:
    lines = [f"**{LABEL[r.status]}**: {r.title} (`{r.target}`, {r.measured} measured, "
             f"{len(r.findings)} finding(s))", ""]
    lines += [f"- could not measure: {e}" for e in r.errors]
    lines += [f"- `{f.subject}`: {f.detail}" for f in r.findings[:shown]]
    if len(r.findings) > shown:
        lines.append(f"- and {len(r.findings) - shown} more; see the JSON report")
    return "\n".join(lines).rstrip() + "\n"


def markdown(report: Report, report_url: str) -> str:
    parts = [f"# Coverage report, {report.as_of.isoformat()}", "",
             headline(report), "",
             f"Page: {report_url} · JSON: {report_url}coverage.json"
             + (f" · Run: {report.run_url}" if report.run_url else ""), "",
             "| Target | Status | Measured | Findings |", "| --- | --- | ---: | ---: |"]
    parts += [f"| `{r.target}` | {LABEL[r.status]} | {r.measured} | {len(r.findings)} |"
              for r in report.results]
    parts.append("")
    for r in report.results:
        if r.status != "met":
            parts += [f"## {r.target}", "", target_markdown(r)]
    return "\n".join(parts)


_CSS = """
:root{--bg:#fff;--fg:#1a1a1a;--muted:#5c5c5c;--line:#ddd;--bad:#b3261e;--ok:#1b6e3a;--warn:#8a5a00}
@media (prefers-color-scheme:dark){:root{--bg:#111;--fg:#eee;--muted:#aaa;--line:#333;
--bad:#ff8a80;--ok:#7fd49b;--warn:#ffcc66}}
body{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;margin:0 auto;
max-width:960px;padding:24px 16px}
h1{font-size:1.4rem}h2{font-size:1.1rem;margin-top:2rem}table{border-collapse:collapse;width:100%}
td,th{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
.breach,.error{color:var(--bad);font-weight:600}.met{color:var(--ok)}.not_in_force{color:var(--warn)}
.muted{color:var(--muted)}code{font-size:.9em;overflow-wrap:anywhere}ul{padding-left:1.2rem}
"""


def page(report: Report, report_url: str) -> str:
    e = html.escape
    rows = "".join(
        f"<tr><td><a href='#{e(r.target)}'><code>{e(r.target)}</code></a><br>"
        f"<span class='muted'>{e(r.title)}</span></td>"
        f"<td class='{r.status}'>{e(LABEL[r.status])}</td><td>{r.measured}</td>"
        f"<td>{len(r.findings)}</td></tr>" for r in report.results)
    sections = []
    for r in report.results:
        items = [f"<li class='error'>could not measure: {e(x)}</li>" for x in r.errors]
        items += [f"<li><code>{e(f.subject)}</code>: {e(f.detail)}</li>" for f in r.findings]
        body = f"<ul>{''.join(items)}</ul>" if items else "<p class='muted'>No findings.</p>"
        sections.append(f"<h2 id='{e(r.target)}'>{e(r.title)} "
                        f"<span class='{r.status}'>({e(LABEL[r.status])})</span></h2>{body}")
    run = f" · <a href='{e(report.run_url)}'>workflow run</a>" if report.run_url else ""
    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<meta name='robots' content='noindex,nofollow'>"
        f"<title>Coverage report</title><style>{_CSS}</style></head><body>"
        f"<h1>Coverage report, {e(report.as_of.isoformat())}</h1>"
        f"<p class='{report.status}'>{e(headline(report))}</p>"
        f"<p class='muted'>Generated {e(report.generated_at.isoformat())} from commit "
        f"<code>{e(report.commit or 'unknown')}</code>, snapshot "
        f"<code>{e(report.snapshot_id or 'none')}</code>. "
        f"<a href='coverage.json'>JSON</a>{run}. Targets: docs/method/coverage-slo.md.</p>"
        f"<table><thead><tr><th>Target</th><th>Status</th><th>Measured</th><th>Findings</th>"
        f"</tr></thead><tbody>{rows}</tbody></table>{''.join(sections)}</body></html>\n"
    )


def write(report: Report, out: Path, report_url: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "coverage.json").write_text(
        json.dumps(report.to_json(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "index.html").write_text(page(report, report_url), encoding="utf-8")
    (out / "summary.md").write_text(markdown(report, report_url), encoding="utf-8")
    # Pages: keep the report out of search indexes and every cache.
    (out / "_headers").write_text(
        "/*\n  X-Robots-Tag: noindex, nofollow\n  Cache-Control: no-store\n", encoding="utf-8")
