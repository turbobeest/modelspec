"""What answer-engine crawlers get from modelspec.dev (MODEL-253)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from urllib.robotparser import RobotFileParser

import pytest

from pipeline import agent_ready, brand_page, entity, live

ROOT = Path(__file__).resolve().parents[1]
NAMED = [agent for _, group in agent_ready.CRAWLERS for agent in group]


# ── robots.txt ───────────────────────────────────────────────────────────────

def test_the_live_tree_publishes_the_content_signal_robots_txt() -> None:
    assert live.ROBOTS == agent_ready.robots_txt(live.BASE)
    assert "Content-Signal: search=yes, ai-input=yes, ai-train=yes" in live.ROBOTS


def test_robots_txt_names_every_crawler_class_and_blocks_none() -> None:
    parser = RobotFileParser()
    parser.parse(live.ROBOTS.splitlines())
    for agent in (*NAMED, "SomeUnlistedBot"):
        for path in live.PAGES:
            assert parser.can_fetch(agent, live.BASE + path), (agent, path)
    for agent in ("GPTBot", "OAI-SearchBot", "ChatGPT-User", "PerplexityBot", "ClaudeBot",
                  "Claude-User", "Google-Extended", "CCBot", "Bytespider"):
        assert f"User-agent: {agent}\n" in live.ROBOTS


def test_only_agent_ready_writes_robots_txt_for_the_site() -> None:
    """Three writers let the last one, a plain copy, win in production."""
    writers = [path.relative_to(ROOT).as_posix() for path in (ROOT / "pipeline").glob("*.py")
               if '"robots.txt").write_text(' in path.read_text(encoding="utf-8")]
    # holding.py writes the dark holding tree's file, which is deliberately different.
    assert sorted(writers) == ["pipeline/agent_ready.py", "pipeline/holding.py", "pipeline/live.py"]
    assert '(tree / "robots.txt").write_text(ROBOTS' in (ROOT / "pipeline/live.py").read_text()


# ── sitemap lastmod ──────────────────────────────────────────────────────────

def _commit(repo: Path, name: str, when: str) -> None:
    (repo / name).write_text(when, encoding="utf-8")
    env = {**os.environ, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when}
    subprocess.run(["git", "add", name], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", name],
                   cwd=repo, check=True, env=env)


def test_lastmod_is_each_pages_last_source_commit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    _commit(tmp_path, "old.py", "2026-09-01T12:00:00+00:00")
    _commit(tmp_path, "new.py", "2026-09-30T12:00:00+00:00")
    monkeypatch.setattr(live, "PAGE_SOURCES", {"/a/": ("old.py",), "/b/": ("new.py", "missing.py")})
    assert live.lastmod("/a/", tmp_path) == "2026-09-01"
    assert live.lastmod("/b/", tmp_path) == "2026-09-30"


def test_every_sitemap_url_has_a_lastmod_and_every_page_has_sources() -> None:
    assert set(live.PAGE_SOURCES) == set(live.PAGES)
    for path, sources in live.PAGE_SOURCES.items():
        assert sources, path
        for source in sources:
            assert (ROOT / source).exists(), (path, source)
    xml = live.sitemap({path: "2026-10-01" for path in live.PAGES})
    assert xml.count("<lastmod>2026-10-01</lastmod>") == xml.count("<loc>") == len(live.PAGES)


# ── the /decide/ capsule and the thin-page gate ──────────────────────────────

def test_the_decide_capsule_is_readable_without_javascript_and_holds_no_model_data() -> None:
    capsule = live.decide_capsule()
    assert "<h1>Which AI model fits your job?</h1>" in capsule
    assert live.visible_words(f"<body>{capsule}</body>") >= live.MIN_WORDS
    assert entity.ONE_SENTENCE in capsule
    assert 'href="/method/"' in capsule
    assert "$" not in capsule  # no prices, no answers: those stay on the board and the API


def _page(tree: Path, path: str, body: str) -> None:
    target = tree / path.lstrip("/") / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(f"<!doctype html><html><head><title>t</title></head><body>{body}</body></html>")


def test_thin_pages_fails_an_empty_app_shell_and_passes_a_real_page(tmp_path: Path,
                                                                   monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(live, "PAGES", ("/shell/", "/real/"))
    _page(tmp_path, "/shell/", '<div id="root"></div><script>render()</script>')
    _page(tmp_path, "/real/", "<h1>Title</h1><p>" + "word " * 90 + "</p>")
    assert live.thin_pages(tmp_path) == ["/shell/: no <h1> without JavaScript",
                                         "/shell/: 0 words without JavaScript; need 80"]


def test_the_brand_page_passes_the_crawler_gate(tmp_path: Path,
                                               monkeypatch: pytest.MonkeyPatch) -> None:
    brand_page.write(tmp_path)
    monkeypatch.setattr(live, "PAGES", ("/brand/",))
    assert live.thin_pages(tmp_path) == []


# ── the weekly probe of live ─────────────────────────────────────────────────

def test_the_crawler_probe_reports_each_refused_crawler_and_path() -> None:
    def fetch(url: str, agent: str) -> int:
        return 403 if agent == "GPTBot" and url.endswith("/method/") else 200

    assert live.crawler_probe("https://modelspec.dev", fetch) == ["GPTBot /method/: 403"]
    asked: list[tuple[str, str]] = []
    live.crawler_probe("https://x", lambda url, agent: asked.append((url, agent)) or 200)
    assert len(asked) == len(NAMED) * (len(live.PAGES) + 1)
