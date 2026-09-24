"""MODEL-63: benchmark pages render the Markdown body and metric/dataset notes, safely."""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline.export import Build  # noqa: E402
from pipeline.load import Benchmark, Catalogue, load_benchmarks  # noqa: E402
from pipeline.render import benchmark_page, render_markdown_body  # noqa: E402

BUILD = Build(commit="abc", built_at="2026-09-15T00:00:00Z", as_of=date(2026, 9, 15))


def _html(front: dict, body: str = "") -> str:
    bench = Benchmark("demo", Path("benchmarks/demo.md"), {"name": "Demo", **front}, body)
    return benchmark_page(bench, BUILD, Catalogue(as_of=date(2026, 9, 15)), [])


def test_body_markdown_renders_escaped() -> None:
    out = render_markdown_body(
        "Part of the [SWE-bench](swe_bench.md) family.\n\n"
        "## What it *measures*\n\nSome **bold** & `a<b>` text with snake_case_name.\n\n"
        "- one\n- two [site](https://x.example/a?b=1&c=2)\n\n1. first\n2. second\n\n"
        "```\n<tag> & code\n```\n"
    )
    assert '<a href="/b/swe_bench/">SWE-bench</a>' in out
    assert "<h2>What it <em>measures</em></h2>" in out
    assert "<strong>bold</strong> &amp; <code>a&lt;b&gt;</code>" in out
    assert "snake_case_name" in out and "<em>case</em>" not in out
    assert "<ul><li>one</li><li>two <a href=\"https://x.example/a?b=1&amp;c=2\"" in out
    assert "<ol><li>first</li><li>second</li></ol>" in out
    assert "<pre><code>&lt;tag&gt; &amp; code</code></pre>" in out


def test_raw_html_and_script_are_escaped() -> None:
    html = _html({}, "Hello <script>alert(1)</script>\n\n<img src=x onerror=alert(1)>\n")
    assert "<script>alert" not in html and "<img src=x" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html


def test_non_http_links_do_not_link() -> None:
    out = render_markdown_body(
        "[a](javascript:alert(1)) [b](data:text/html,x) [c](//evil.example) "
        "[d](/abs) [e](../../../etc/passwd) [f](vbscript:x)"
    )
    assert "href" not in out
    for label in "abcdef":
        assert f"{label}" in out


def test_relative_repo_link_goes_to_github() -> None:
    out = render_markdown_body("[spec](../docs/agentic-latency-benchmark.md)")
    assert 'href="https://github.com/turbobeest/modelspec/blob/main/docs/agentic-latency-benchmark.md"' in out


def test_notes_render() -> None:
    html = _html({"metric": {"name": "steps", "baseline_note": "No <baseline>."},
                  "dataset": {"size_note": "500 tasks"},
                  "saturation": {"note": "Top models near ceiling."},
                  "contamination": {"note": "Held-out answers."}})
    assert ('<span class="lab">Baseline note</span><div class="val long">No &lt;baseline&gt;.</div>'
            in html)
    assert '<span class="lab">Dataset size note</span><div class="val">500 tasks</div>' in html
    assert "Top models near ceiling." in html and "Held-out answers." in html


def test_empty_body_and_notes_render_nothing() -> None:
    html = _html({"metric": {"name": "x", "baseline_note": "  "}, "dataset": {"size_note": ""},
                  "saturation": {"note": ""}}, "\n\n   \n")
    assert 'class="prose"' not in html
    assert "note</span>" not in html
    assert "<h2></h2>" not in html and "<h3></h3>" not in html
    assert render_markdown_body("") == "" and render_markdown_body("#\n\n") == ""


def test_page_without_body_matches_previous_output_shape() -> None:
    html = _html({"measures": "Things.", "metric": {"name": "acc", "unit": "%"}})
    assert 'class="prose"' not in html
    assert "<h2>What it measures</h2><p>Things.</p>" in html
    assert '<span class="lab">Metric</span><div class="val">acc</div>' in html


def _real(bench_id: str) -> str:
    bench = next(b for b in load_benchmarks(ROOT) if b.benchmark_id == bench_id)
    return benchmark_page(bench, BUILD, Catalogue(as_of=date(2026, 9, 15)), [])


def test_real_swe_bench_steps_page_shows_step_caveat() -> None:
    html = _real("swe_bench_steps_to_completion")
    assert "does not define" in html and "instance_calls" in html
    assert "Baseline note" in html


def test_real_page_has_single_what_it_measures_heading() -> None:
    html = _real("swe_bench_steps_to_completion")
    assert html.count("What it measures</h2>") == 1


def test_front_matter_measures_kept_without_body_heading() -> None:
    html = _html({"measures": "Front text."}, "## Reading the numbers\n\nBody.")
    assert "<h2>What it measures</h2><p>Front text.</p>" in html


def test_front_matter_measures_skipped_on_normalised_match() -> None:
    html = _html({"measures": "Front text."}, "##   what IT  measures:\n\nBody text.")
    assert "Front text." not in html.split('class="prose"')[0].split("</table>")[-1]
    assert html.count("<h2>What it measures</h2>") == 0 and "Body text." in html


def test_front_matter_task_format_kept_without_body_heading() -> None:
    html = _html({"task_format": "Multiple choice."}, "## How it is scored\n\nBody.")
    assert "<h2>Task format</h2><p>Multiple choice.</p>" in html


def test_front_matter_task_format_skipped_when_body_has_heading() -> None:
    html = _html({"task_format": "Multiple choice."}, "## Task format\n\nBody detail.")
    assert html.count("Task format</h2>") == 1 and "Multiple choice." not in html
