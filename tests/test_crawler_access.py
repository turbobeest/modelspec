"""What answer-engine crawlers get from modelspec.dev (MODEL-253)."""

from __future__ import annotations

import os
import subprocess
from contextlib import nullcontext
from functools import partial
from pathlib import Path
from types import SimpleNamespace
from urllib.error import HTTPError
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


def test_the_client_probe_passes_when_every_client_matches_curl() -> None:
    asked: list[str] = []

    def fetch(method: str, url: str, agent: str, body: bytes | None) -> tuple[int, str]:
        asked.append(agent)
        content_type = "Application/JSON; charset=utf-8" if agent == "curl/8.7.1" else "application/json"
        return (200 if method == "GET" else 400), content_type

    assert live.client_probe("https://api.modelspec.dev/", fetch) == []
    assert asked == [
        "curl/8.7.1", "Python-urllib/3.12", "python-requests/2.32.3", "node",
        "node-fetch/1.0 (+https://github.com/bitinn/node-fetch)",
        "Go-http-client/1.1", "Go-http-client/2.0",
    ] * 2


def test_the_client_probe_reports_the_urllib_edge_refusals() -> None:
    def fetch(method: str, url: str, agent: str, body: bytes | None) -> tuple[int, str]:
        if agent.startswith("Python-urllib/"):
            return 403, "text/plain; charset=utf-8"
        return (200 if method == "GET" else 400), "application/json"

    assert live.client_probe("https://api.modelspec.dev", fetch) == [
        "Python-urllib/3.12 GET /v1/health: 403 text/plain, curl got 200 application/json",
        "Python-urllib/3.12 POST /v1/decide: 403 text/plain, curl got 400 application/json",
    ]


@pytest.mark.parametrize(("status", "content_type", "expected"), [
    (403, "Text/Plain; charset=utf-8", [
        "curl/8.7.1 GET /v1/health: 403 text/plain, not a JSON answer from the Worker",
        "curl/8.7.1 POST /v1/decide: 403 text/plain, not a JSON answer from the Worker",
    ]),
    (0, "application/json", [
        "curl/8.7.1 GET /v1/health: 0 application/json, not a JSON answer from the Worker",
        "curl/8.7.1 POST /v1/decide: 0 application/json, not a JSON answer from the Worker",
    ]),
])
def test_the_client_probe_requires_a_usable_curl_baseline(status: int, content_type: str,
                                                        expected: list[str]) -> None:
    assert live.client_probe("https://api.modelspec.dev", lambda *args: (status, content_type)) == expected


def test_the_client_probe_sends_explicit_user_agents_and_the_decide_body(monkeypatch: pytest.MonkeyPatch) -> None:
    asked: dict[str, list[str]] = {"GET": [], "POST": []}

    def urlopen(request, timeout):
        method = request.get_method()
        asked[method].append(request.get_header("User-agent"))
        assert timeout == 30
        assert request.get_header("Authorization") is None
        if method == "POST":
            assert request.full_url == "https://api.modelspec.dev/v1/decide"
            assert request.data == b"{}"
            assert request.get_header("Content-type") == "application/json"
            raise HTTPError(request.full_url, 400, "invalid_spec", {"Content-Type": "application/json"}, None)
        assert request.full_url == "https://api.modelspec.dev/v1/health"
        assert request.data is None
        return nullcontext(SimpleNamespace(status=200, headers={"Content-Type": "application/json"}))

    monkeypatch.setattr(live.urllib.request, "urlopen", urlopen)
    assert live.client_probe("https://api.modelspec.dev/") == []
    assert asked["GET"] == asked["POST"] == [
        "curl/8.7.1", "Python-urllib/3.12", "python-requests/2.32.3", "node",
        "node-fetch/1.0 (+https://github.com/bitinn/node-fetch)",
        "Go-http-client/1.1", "Go-http-client/2.0",
    ]


def test_the_client_probe_passes_when_the_site_clients_match_curl() -> None:
    asked: list[str] = []

    def fetch(method: str, url: str, agent: str, body: bytes | None) -> tuple[int, str]:
        if url.startswith("https://api.modelspec.dev/"):
            return (200 if method == "GET" else 400), "application/json"
        assert method == "GET"
        assert body is None
        content_type = {
            "https://modelspec.dev/agents.md": "text/markdown",
            "https://modelspec.dev/llms.txt": "text/plain",
            "https://modelspec.dev/openapi.yaml": "application/yaml",
            "https://modelspec.dev/api/build.json": "application/json",
        }[url]
        if agent == "curl/8.7.1":
            asked.append(url)
            return 200, content_type.upper() + "; charset=utf-8"
        return 200, content_type

    assert live.client_probe("https://api.modelspec.dev", fetch, "https://modelspec.dev/") == []
    assert asked == [
        "https://modelspec.dev/agents.md", "https://modelspec.dev/llms.txt",
        "https://modelspec.dev/openapi.yaml", "https://modelspec.dev/api/build.json",
    ]


def _site_urllib_refusal(method: str, url: str, agent: str, body: bytes | None) -> tuple[int, str]:
    if url.startswith("https://modelspec.dev/"):
        return (403 if agent.startswith("Python-urllib/") else 200), "text/plain; charset=utf-8"
    return (200 if method == "GET" else 400), "application/json"


def test_the_client_probe_reports_the_four_site_urllib_refusals() -> None:
    assert live.client_probe("https://api.modelspec.dev", _site_urllib_refusal, "https://modelspec.dev") == [
        "Python-urllib/3.12 GET /agents.md: 403 text/plain, curl got 200 text/plain",
        "Python-urllib/3.12 GET /llms.txt: 403 text/plain, curl got 200 text/plain",
        "Python-urllib/3.12 GET /openapi.yaml: 403 text/plain, curl got 200 text/plain",
        "Python-urllib/3.12 GET /api/build.json: 403 text/plain, curl got 200 text/plain",
    ]


def test_the_client_probe_requires_a_200_site_curl_baseline() -> None:
    def fetch(method: str, url: str, agent: str, body: bytes | None) -> tuple[int, str]:
        if url.startswith("https://modelspec.dev/"):
            return 403, "Text/Plain; charset=utf-8"
        return (200 if method == "GET" else 400), "application/json"

    assert live.client_probe("https://api.modelspec.dev", fetch, "https://modelspec.dev") == [
        "curl/8.7.1 GET /agents.md: 403 text/plain, not a 200 response from the site",
        "curl/8.7.1 GET /llms.txt: 403 text/plain, not a 200 response from the site",
        "curl/8.7.1 GET /openapi.yaml: 403 text/plain, not a 200 response from the site",
        "curl/8.7.1 GET /api/build.json: 403 text/plain, not a 200 response from the site",
    ]


def test_the_client_probe_cli_fails_when_only_the_site_fails(monkeypatch: pytest.MonkeyPatch,
                                                           capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(live, "client_probe", partial(live.client_probe, fetch=_site_urllib_refusal))

    assert live.main(["client-probe", "--origin", "https://api.modelspec.dev", "--site", "https://modelspec.dev"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == (
        "::error::https://api.modelspec.dev and https://modelspec.dev: "
        "Python-urllib/3.12 GET /agents.md: 403 text/plain, curl got 200 text/plain\n"
        "::error::https://api.modelspec.dev and https://modelspec.dev: "
        "Python-urllib/3.12 GET /llms.txt: 403 text/plain, curl got 200 text/plain\n"
        "::error::https://api.modelspec.dev and https://modelspec.dev: "
        "Python-urllib/3.12 GET /openapi.yaml: 403 text/plain, curl got 200 text/plain\n"
        "::error::https://api.modelspec.dev and https://modelspec.dev: "
        "Python-urllib/3.12 GET /api/build.json: 403 text/plain, curl got 200 text/plain\n"
    )


@pytest.mark.parametrize(("site", "expected"), [
    ([], "https://api.modelspec.dev: every common HTTP client matches curl on health and decide\n"),
    (["--site", "https://modelspec.dev"],
     "https://api.modelspec.dev and https://modelspec.dev: "
     "every common HTTP client matches curl on health, decide and the site agent files\n"),
])
def test_the_client_probe_cli_names_every_probed_origin_on_success(site: list[str], expected: str,
                                                                monkeypatch: pytest.MonkeyPatch,
                                                                capsys: pytest.CaptureFixture[str]) -> None:
    def fetch(method: str, url: str, agent: str, body: bytes | None) -> tuple[int, str]:
        return (200 if method == "GET" else 400), "application/json"

    monkeypatch.setattr(live, "client_probe", partial(live.client_probe, fetch=fetch))

    assert live.main(["client-probe", "--origin", "https://api.modelspec.dev", *site]) == 0
    captured = capsys.readouterr()
    assert captured.out == expected
    assert captured.err == ""
