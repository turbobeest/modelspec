"""Surface drift fails the same pure checks and CLI used by CI (MODEL-255)."""

from __future__ import annotations

import json
import urllib.error
from pathlib import Path

import pytest
import yaml

from api.ranking.engine import neutrality_commitment
from decision.excluded import REMOVED_TEXT
from pipeline import agent_copy, entity, holding, live, worker_flags
from pipeline import surface_lint as sl
from scripts.aeo import surface_drift as drift

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def copy() -> dict:
    return agent_copy.copy(json.loads(agent_copy.TIERS.read_text()))


def page(body: str, ld: object | None = None, title: str = entity.TITLE) -> str:
    script = (
        '<script type="application/ld+json">' + json.dumps(ld) + "</script>"
        if ld is not None
        else ""
    )
    return (
        f"<html><head><title>{title}</title>"
        f'<meta name="description" content="{entity.ONE_SENTENCE}">'
        f'<meta property="og:description" content="{entity.ONE_SENTENCE}">{script}</head>'
        f"<body>{body}</body></html>"
    )


@pytest.fixture
def texts(copy: dict) -> dict[str, str]:
    org = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": entity.NAME,
        "description": entity.ONE_SENTENCE,
    }
    return {
        "index.html": page(f"<p>{entity.ONE_SENTENCE}</p>", org),
        "method/index.html": page(
            f"<h1>Method</h1><p>{entity.ONE_SENTENCE} {entity.DISAMBIGUATION}</p>"
        ),
        "llms.txt": entity.ONE_SENTENCE + "\n\n" + entity.DISAMBIGUATION,
        "index.md": entity.ONE_SENTENCE,
        "brand/index.html": page(entity.ONE_SENTENCE),
        ".well-known/agent-skills/modelspec/SKILL.md": entity.ONE_SENTENCE,
        sl.CARD: json.dumps(
            {
                "description": entity.SHORT,
                "tools": [
                    {"name": name, "description": text} for name, text in copy["card"].items()
                ],
            }
        ),
        sl.BUNDLE: json.dumps(copy),
        "openapi.yaml": yaml.safe_dump(
            {
                "paths": {
                    "/" + name: {
                        "post": {
                            "operationId": name,
                            "summary": description["summary"],
                            "description": description["lead"] + "\n\nTechnical details.",
                        }
                    }
                    for name, description in copy["openapi"].items()
                }
            }
        ),
        "api/build.json": json.dumps(
            {"built_at": "2026-10-10T12:00:00+00:00", "commit": "fixture"}
        ),
        "sitemap.xml": live.sitemap({path: "2026-10-10" for path in live.PAGES}),
    }


def lint(texts: dict[str, str], copy: dict) -> list[sl.Finding]:
    return sl.lint(
        texts, variables={"X402_ENABLED": "false"}, commitment=neutrality_commitment(), copy=copy
    )


def ci_exit(texts: dict[str, str], tree: Path) -> int:
    for path, text in texts.items():
        if path == sl.BUNDLE:
            continue
        target = tree / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
    return sl.main(["--tree", str(tree)])


def test_current_registry_surfaces_pass(texts: dict[str, str], copy: dict) -> None:
    assert lint(texts, copy) == []


def test_fixture_old_title_fails_ci(
    texts: dict[str, str], copy: dict, tmp_path: Path, capsys
) -> None:
    texts["index.html"] = texts["index.html"].replace(entity.TITLE, entity.SUPERSEDED[0])
    assert ci_exit(texts, tmp_path) == 1
    assert "index.html | presence.title" in capsys.readouterr().out
    assert any(f.check == "presence.superseded" for f in lint(texts, copy))


def test_fixture_knowledge_graph_fails_ci(
    texts: dict[str, str], copy: dict, tmp_path: Path
) -> None:
    texts["extra.html"] = page("ModelSpec is a knowledge graph.")
    assert [f.check for f in lint(texts, copy)] == ["lexicon.positioning"]
    assert ci_exit(texts, tmp_path) == 1


def test_fixture_x402_fails_ci(texts: dict[str, str], copy: dict, tmp_path: Path) -> None:
    texts["extra.html"] = page("Pay with x402.")
    assert [f.check for f in lint(texts, copy)] == ["lexicon.x402"]
    assert ci_exit(texts, tmp_path) == 1


def test_fixture_jsonld_text_not_visible_fails_ci(
    texts: dict[str, str], copy: dict, tmp_path: Path
) -> None:
    texts["extra.html"] = page(
        "Visible text.",
        {
            "@context": "https://schema.org",
            "@type": "Thing",
            "description": "A claim only in JSON-LD.",
        },
    )
    findings = lint(texts, copy)
    assert [f.check for f in findings] == ["jsonld.visible"]
    assert findings[0].excerpt == "A claim only in JSON-LD."
    assert ci_exit(texts, tmp_path) == 1


@pytest.mark.parametrize("old", entity.SUPERSEDED)
def test_every_superseded_sentence_is_rejected(old: str) -> None:
    assert sl.lexicon({"llms.txt": old}, {}, {})[0].check == "presence.superseded"


def test_an_unregistered_title_fails_even_without_a_superseded_string(
    texts: dict[str, str],
) -> None:
    texts["index.html"] = texts["index.html"].replace(entity.TITLE, "A different product title")
    assert [f.check for f in sl.presence(texts)] == ["presence.title"]


@pytest.mark.parametrize("path", ["index.html", "method/index.html"])
def test_the_sentence_must_open_the_first_paragraph(texts: dict[str, str], path: str) -> None:
    texts[path] = page(
        f"<p>Something else.</p><footer>{entity.ONE_SENTENCE} {entity.DISAMBIGUATION}</footer>"
    )
    assert any(f.surface == path and f.check == "presence.lead" for f in sl.presence(texts))


@pytest.mark.parametrize(
    "path",
    [
        "llms.txt",
        "index.md",
        "brand/index.html",
        "method/index.html",
        ".well-known/agent-skills/modelspec/SKILL.md",
    ],
)
def test_each_registry_surface_requires_the_sentence(texts: dict[str, str], path: str) -> None:
    del texts[path]
    assert any(f.surface == path and f.check == "presence.one_sentence" for f in sl.presence(texts))


@pytest.mark.parametrize("path", ["method/index.html", "llms.txt"])
def test_disambiguation_is_required(texts: dict[str, str], path: str) -> None:
    texts[path] = texts[path].replace(entity.DISAMBIGUATION, "")
    assert any(
        f.surface == path and f.check == "presence.disambiguation" for f in sl.presence(texts)
    )


@pytest.mark.parametrize(
    "bad,good,check",
    [
        (
            "ModelSpec is a knowledge graph.",
            "A knowledge graph links facts.",
            "lexicon.positioning",
        ),
        (
            "ModelSpec, a knowledge graph, finds models.",
            "This is not our knowledge graph.",
            "lexicon.positioning",
        ),
        ("Explore our knowledge graph.", "Explore their knowledge graph.", "lexicon.positioning"),
        ("ModelSpec is a model router.", "A router chooses per request.", "lexicon.positioning"),
        ("ModelSpec routes your requests.", entity.CLAIMS[3].statement, "lexicon.positioning"),
        ("Pay with x402.", "Machine callers need an API key.", "lexicon.x402"),
        ("Find us in Bazaar.", "Find us through MCP.", "lexicon.x402"),
        ("Pay per call without a key.", "Pay with a funded API key.", "lexicon.x402"),
        ("pip install modelspec", agent_copy.PACKAGE_WARNING, "lexicon.cli"),
        ("pip install modelspec", "pip install modelspec-dev", "lexicon.cli"),
        ("Use the offline decision CLI.", "There is no offline decision CLI.", "lexicon.cli"),
        ("Use our local decision CLI.", "A local CLI calls the keyed hosted API.", "lexicon.cli"),
        (
            "The CLI makes decisions offline.",
            "The CLI never makes decisions offline.",
            "lexicon.cli",
        ),
        ("The CLI downloads the data.", "The CLI never downloads the data.", "lexicon.cli"),
        ("Download the catalogue with our CLI.", agent_copy.ACCESS, "lexicon.cli"),
        (
            "Our featured partner ranks first.",
            "No featured partner ranks first.",
            "lexicon.neutrality",
        ),
        (
            "We sell sponsored rankings.",
            "No referral fees, no paid placement, no sponsored slots.",
            "lexicon.neutrality",
        ),
        ("Try our promoted models.", "There are no promoted models.", "lexicon.neutrality"),
        ("We earn affiliate fees.", "We never earn affiliate fees.", "lexicon.neutrality"),
        ("ModelSpec versus OpenRouter.", "ModelSpec versus a router.", "lexicon.competitor"),
        (
            "ModelSpec is an alternative to Portkey.",
            "Portkey is a model gateway.",
            "lexicon.competitor",
        ),
    ],
)
def test_each_lexicon_rule_has_a_failing_and_passing_claim(bad: str, good: str, check: str) -> None:
    commitment = neutrality_commitment()
    assert any(f.check == check for f in sl.lexicon({"llms.txt": bad}, {}, commitment))
    assert sl.lexicon({"llms.txt": good}, {}, commitment) == []


@pytest.mark.parametrize(
    "path",
    ["extra.html", "llms.txt", "extra.md", ".well-known/card.json", "openapi.yaml", "auth.md"],
)
def test_all_owned_formats_and_legal_pages_get_lexicon_checks(path: str) -> None:
    text = (
        page("ModelSpec is a knowledge graph.")
        if path.endswith(".html")
        else "ModelSpec is a knowledge graph."
    )
    assert sl.lexicon({path: text}, {}, {})[0].check == "lexicon.positioning"
    assert (
        sl.lexicon({"legal/neutrality/index.html": text}, {}, {})[0].check == "lexicon.positioning"
    )
    assert sl.lexicon({"api/models.json": text, "assets/app.js": text}, {}, {}) == []


def test_removed_sources_reuse_the_catalogue_rule() -> None:
    # Get a witness from the shared expression, without duplicating its names.
    witness = REMOVED_TEXT.pattern.split("|")[1]
    assert REMOVED_TEXT.search(witness)
    assert (
        sl.lexicon({"llms.txt": "Source: " + witness}, {}, {})[0].check == "lexicon.removed-source"
    )
    assert sl.lexicon({"llms.txt": "Sources link to the original measurements."}, {}, {}) == []


@pytest.mark.parametrize("state", ["true", "1", True, "false", "0", False])
def test_x402_rule_follows_production_vars(state: object, tmp_path: Path) -> None:
    config = tmp_path / worker_flags.WRANGLER_REL
    config.parent.mkdir(parents=True)
    config.write_text(
        json.dumps(
            {
                "vars": {"X402_ENABLED": state},
                "env": {"preview": {"vars": {"X402_ENABLED": "true"}}},
            }
        )
    )
    variables = worker_flags.production_vars(tmp_path)
    findings = sl.lexicon({"llms.txt": "x402 Bazaar pay per call without a key"}, variables, {})
    assert bool(findings) is not worker_flags.enabled(variables, "X402_ENABLED")


@pytest.mark.parametrize(
    "assertions,banned",
    [
        ({"accepts_paid_placement": False}, "sponsored"),
        ({"accepts_provider_paid_visibility": False}, "featured partner"),
        ({"accepts_referral_fees": False}, "affiliate"),
    ],
)
def test_sponsorship_rule_follows_the_specific_neutrality_assertion(
    assertions: dict, banned: str
) -> None:
    text = "We offer " + banned + " rankings."
    assert sl.lexicon({"llms.txt": text}, {}, {"assertions": assertions})
    assert (
        sl.lexicon({"llms.txt": text}, {}, {"assertions": {key: True for key in assertions}}) == []
    )
    assert sl.lexicon({"llms.txt": text}, {}, {}) == []


def test_a_disclaimer_does_not_exempt_the_next_claim() -> None:
    findings = sl.lexicon(
        {"llms.txt": "No paid placement. Our sponsored models rank first."},
        {},
        neutrality_commitment(),
    )
    assert [f.check for f in findings] == ["lexicon.neutrality"]


def test_benchmark_sponsorship_is_provenance_but_paid_ranking_is_drift() -> None:
    assert (
        sl.lexicon(
            {"b/example/index.md": "Benchmark authors sponsored by a university."},
            {},
            neutrality_commitment(),
        )
        == []
    )
    assert (
        sl.lexicon({"b/example/index.md": "Our sponsored rankings."}, {}, neutrality_commitment())[
            0
        ].check
        == "lexicon.neutrality"
    )


def test_legal_payment_disclosure_does_not_offer_the_disabled_rail() -> None:
    path = "legal/terms/index.html"
    assert sl.lexicon({path: page("Payment by x402 is not currently offered.")}, {}, {}) == []
    assert (
        sl.lexicon({path: page("ModelSpec accepts x402 payments.")}, {}, {})[0].check
        == "lexicon.x402"
    )


def test_jsonld_checks_nested_names_descriptions_and_all_type_values() -> None:
    node = {
        "@context": "https://schema.org",
        "@type": ["WebAPI", "SoftwareApplication"],
        "name": "API",
        "provider": {"@type": "Organization", "name": "Publisher"},
    }
    assert sl.structured_data({"a.html": page("API Publisher", node)}) == []
    node["provider"]["name"] = "Invisible publisher"
    assert sl.structured_data({"a.html": page("API Publisher", node)})[0].check == "jsonld.visible"


@pytest.mark.parametrize(
    "kind", ["MadeUpType", "https://example.org/Organization", "schema:NotASchemaType", 5]
)
def test_non_schema_types_fail(kind: object) -> None:
    assert (
        sl.structured_data(
            {"a.html": page("Visible", {"@context": "https://schema.org", "@type": kind})}
        )[0].check
        == "jsonld.type"
    )


def test_external_jsonld_context_fails() -> None:
    assert (
        sl.structured_data(
            {"a.html": page("Visible", {"@context": "https://example.org", "@type": "Thing"})}
        )[0].check
        == "jsonld.context"
    )


def test_malformed_jsonld_fails() -> None:
    text = '<body>Visible<script type="application/ld+json">{"@type":</script></body>'
    assert sl.structured_data({"a.html": text})[0].check == "jsonld.parse"


def test_visible_comparison_decodes_entities_and_preserves_inline_spacing() -> None:
    text = page(
        '<p>Fish &amp; <a href="/">chips</a>   today.</p>',
        {"@context": "https://schema.org", "@type": "Thing", "description": "Fish & chips today."},
    )
    assert sl.structured_data({"a.html": text}) == []


@pytest.mark.parametrize(
    "hidden",
    [
        "<script>Hidden claim</script>",
        "<style>Hidden claim</style>",
        "<p hidden>Hidden claim</p>",
        '<p aria-hidden="true">Hidden claim</p>',
    ],
)
def test_invisible_text_does_not_satisfy_jsonld(hidden: str) -> None:
    text = page(
        hidden, {"@context": "https://schema.org", "@type": "Thing", "name": "Hidden claim"}
    )
    assert sl.structured_data({"a.html": text})[0].check == "jsonld.visible"


def test_head_title_does_not_satisfy_a_visible_claim() -> None:
    text = page(
        "Visible", {"@context": "https://schema.org", "@type": "Thing", "name": entity.TITLE}
    )
    assert sl.structured_data({"a.html": text})[0].check == "jsonld.visible"


def test_mcp_card_and_bundle_descriptions_require_generated_copy(
    texts: dict[str, str], copy: dict
) -> None:
    card = json.loads(texts[sl.CARD])
    card["description"] = "Handwritten."
    card["tools"][0]["description"] = "Handwritten."
    texts[sl.CARD] = json.dumps(card)
    bundle = json.loads(texts[sl.BUNDLE])
    bundle["tools"]["decide"] = "Handwritten."
    texts[sl.BUNDLE] = json.dumps(bundle)
    assert {f.check for f in sl.agent_surfaces(texts, copy)} == {
        "agent.description",
        "agent.tool.decide",
    }


def test_missing_duplicate_and_unknown_mcp_tools_fail(copy: dict) -> None:
    tools = [
        {"name": name, "description": description} for name, description in copy["tools"].items()
    ]
    assert sl.tool_descriptions("mcp", tools, copy["tools"]) == []
    assert sl.tool_descriptions("mcp", tools[:-1], copy["tools"])
    assert sl.tool_descriptions("mcp", [*tools, tools[0]], copy["tools"])
    assert sl.tool_descriptions("mcp", [*tools, {"name": "unknown"}], copy["tools"])


def test_tool_prices_are_checked_against_tiers(copy: dict, texts: dict[str, str]) -> None:
    tiers = json.loads(agent_copy.TIERS.read_text())
    tiers["credits"]["weights"]["rank"] += 1
    expected = agent_copy.copy(tiers)
    findings = sl.agent_surfaces(texts, expected)
    assert any(f.check == "agent.tool.rank" for f in findings)
    assert any(f.surface == sl.CARD and f.check == "agent.tool.rank" for f in findings)
    assert any(f.check == "agent.openapi.rank.description" for f in findings)


def test_short_card_credit_prices_follow_tiers() -> None:
    tiers = json.loads(agent_copy.TIERS.read_text())
    tiers["credits"]["weights"].update(
        {
            "decide.none": 3,
            "decide.summary": 5,
            "decide.full": 7,
            "rank": 2,
            "policy-check": 9,
        }
    )
    card = agent_copy.copy(tiers)["card"]
    assert card["decide"].endswith("Key; 3–7 credits.")
    assert card["rank"].endswith("Key; 2 credits.")
    assert card["policy_check"].endswith("Key; 9 credits.")


def test_openapi_summary_and_lead_require_generated_copy(texts: dict[str, str], copy: dict) -> None:
    spec = yaml.safe_load(texts["openapi.yaml"])
    spec["paths"]["/decide"]["post"].update(summary="Handwritten.", description="Handwritten.")
    texts["openapi.yaml"] = yaml.safe_dump(spec)
    assert {f.check for f in sl.agent_surfaces(texts, copy)} == {
        "agent.openapi.decide.summary",
        "agent.openapi.decide.description",
    }


def test_future_sitemap_date_fails(texts: dict[str, str]) -> None:
    texts["sitemap.xml"] = live.sitemap({path: "2026-10-11" for path in live.PAGES})
    assert {f.check for f in sl.freshness(texts)} == {"freshness.future"}


def test_changed_source_requires_the_expected_new_date(texts: dict[str, str]) -> None:
    assert sl.freshness(texts, lastmods={"/method/": "2026-10-10"}) == []
    texts["sitemap.xml"] = live.sitemap({path: "2026-10-09" for path in live.PAGES})
    findings = sl.freshness(texts, lastmods={"/method/": "2026-10-10"})
    assert [(f.surface, f.check, f.expected) for f in findings] == [
        ("/method/", "freshness.source", "2026-10-10")
    ]


def test_full_build_lastmods_follow_the_build_date(texts: dict[str, str]) -> None:
    texts["models/index.html"] = ""
    dates, notice = sl.expected_lastmods(texts, deployed=False)
    assert dates == {path: "2026-10-10" for path in live.PAGES}
    assert notice == ""


def test_live_source_dates_do_not_compare_different_commits(texts: dict[str, str]) -> None:
    dates, notice = sl.expected_lastmods(texts, deployed=True)
    assert dates is None
    assert "differs from this checkout" in notice


def fetcher(texts: dict[str, str], requested: list[str]):
    def fetch(url: str):
        requested.append(url)
        path = url.removeprefix(entity.SITE + "/")
        path = "index.html" if not path else path + "index.html" if path.endswith("/") else path
        return (200, {}, texts[path].encode()) if path in texts else (404, {}, b"Missing")

    return fetch


def test_live_holding_skips_only_files_the_holding_builder_omits(
    texts: dict[str, str], copy: dict
) -> None:
    texts["robots.txt"] = holding.ROBOTS
    del texts["sitemap.xml"]
    texts["index.html"] = page(f"<p>{entity.ONE_SENTENCE}</p>")
    for path in live.PAGES:
        rel = path.lstrip("/") + "index.html"
        if sl.holding_serves(rel) and rel not in texts:
            texts[rel] = page("ModelSpec")
    requested = []
    fetched, absent, is_holding, failures = sl.live_tree(entity.SITE, fetcher(texts, requested))
    assert is_holding
    assert failures == []
    assert "method/index.html" in absent and sl.CARD in absent and "sitemap.xml" in absent
    assert "openapi.yaml" not in absent and "brand/index.html" not in absent
    assert entity.SITE + "/method/" not in requested
    assert (
        sl.lint(
            fetched,
            variables={},
            commitment=neutrality_commitment(),
            copy=copy,
            absent=absent,
            holding=True,
        )
        == []
    )


def test_live_missing_discovery_is_drift_outside_holding(texts: dict[str, str]) -> None:
    texts["robots.txt"] = live.ROBOTS
    del texts[sl.CARD]
    _, absent, is_holding, failures = sl.live_tree(entity.SITE, fetcher(texts, []))
    assert not is_holding and absent == frozenset()
    assert any(f.surface == sl.CARD and f.check == "live.fetch" for f in failures)


@pytest.mark.parametrize("stream", [False, True])
def test_mcp_metadata_probe_uses_only_tools_list_without_a_key(
    copy: dict, monkeypatch: pytest.MonkeyPatch, stream: bool
) -> None:
    tools = [{"name": name, "description": text} for name, text in copy["tools"].items()]
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "result": {"tools": tools}})

    class Response:
        headers = {"content-type": "text/event-stream" if stream else "application/json"}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return ("event: message\ndata:" + payload + "\n\n" if stream else payload).encode()

    def urlopen(request, *, timeout):
        assert request.full_url == entity.MCP_ENDPOINT and request.method == "POST"
        assert json.loads(request.data) == {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }
        assert request.get_header("Authorization") is None
        assert timeout == 15
        return Response()

    monkeypatch.setattr(sl.urllib.request, "urlopen", urlopen)
    actual, notice = sl.mcp_tools()
    assert sl.tool_descriptions("mcp", actual, copy["tools"]) == []
    assert "checked without an API key" in notice


@pytest.mark.parametrize("status", [401, 403])
def test_mcp_auth_refusal_is_not_drift(monkeypatch: pytest.MonkeyPatch, status: int) -> None:
    def refuse(request, *, timeout):
        raise urllib.error.HTTPError(
            entity.MCP_ENDPOINT, status, "Authentication required", {}, None
        )

    monkeypatch.setattr(sl.urllib.request, "urlopen", refuse)
    tools, notice = sl.mcp_tools()
    assert tools is None
    assert f"HTTP {status}, authentication required" in notice


def test_get_only_mode_sends_no_mcp_request(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*args, **kwargs):
        pytest.fail("GET-only probe sent an MCP request")

    monkeypatch.setattr(sl.urllib.request, "urlopen", forbidden)
    tools, notice = sl.mcp_tools(get_only=True)
    assert tools is None and "GET-only probe" in notice


def report(findings: bool = True) -> dict:
    return {
        "origin": entity.SITE,
        "findings": [
            {
                "surface": "llms.txt",
                "check": "presence.one_sentence",
                "excerpt": "old",
                "expected": entity.ONE_SENTENCE,
            }
        ]
        if findings
        else [],
        "notices": ["MCP tools/list not checked."],
    }


def test_issue_drift_creates_then_updates_the_same_issue() -> None:
    assert [a.verb for a in drift.issue_actions(report(), [])] == ["create"]
    issues = [{"number": 7, "title": drift.TITLE, "state": "OPEN"}]
    actions = drift.issue_actions(report(), issues)
    assert [(a.verb, a.number) for a in actions] == [("edit", 7)]
    assert "llms.txt | presence.one_sentence" in actions[0].body
    assert "MCP tools/list not checked" in actions[0].body


def test_issue_clean_closes_and_new_drift_reopens_the_same_issue() -> None:
    issue = {"number": 7, "title": drift.TITLE, "state": "OPEN"}
    assert [(a.verb, a.number) for a in drift.issue_actions(report(False), [issue])] == [
        ("close", 7)
    ]
    issue["state"] = "CLOSED"
    assert drift.issue_actions(report(False), [issue]) == []
    assert [(a.verb, a.number) for a in drift.issue_actions(report(), [issue])] == [
        ("reopen", 7),
        ("edit", 7),
    ]


def test_issue_duplicates_converge_and_other_issues_are_untouched() -> None:
    issues = [
        {"number": 7, "title": drift.TITLE, "state": "OPEN"},
        {"number": 8, "title": drift.TITLE, "state": "OPEN"},
        {"number": 6, "title": "Unrelated", "state": "OPEN"},
    ]
    assert [(a.verb, a.number) for a in drift.issue_actions(report(), issues)] == [
        ("close", 8),
        ("edit", 7),
    ]


def test_issue_body_stays_within_githubs_size_limit() -> None:
    long_report = report()
    long_report["findings"] *= 1000
    body = drift.issue_actions(long_report, [])[0].body
    assert len(body) <= drift.MAX_BODY
    assert "Report truncated" in body


def test_issue_offline_dry_run_makes_no_gh_calls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    def forbidden(arguments):
        pytest.fail("dry-run called gh")

    monkeypatch.setattr(drift, "gh", forbidden)
    report_path, issues_path = tmp_path / "report.json", tmp_path / "issues.json"
    report_path.write_text(json.dumps(report()))
    issues_path.write_text("[]")
    assert (
        drift.main(
            [
                "--report",
                str(report_path),
                "--repo",
                "owner/repo",
                "--issues",
                str(issues_path),
                "--dry-run",
            ]
        )
        == 0
    )
    assert "create: owner/repo" in capsys.readouterr().out


def test_weekly_workflow_and_build_step_run_the_lint() -> None:
    workflow = yaml.safe_load((ROOT / ".github/workflows/surface-lint-live.yml").read_text())
    triggers = workflow.get("on", workflow.get(True))
    assert triggers["schedule"] and "workflow_dispatch" in triggers
    assert workflow["permissions"] == {"contents": "read", "issues": "write"}
    assert workflow["concurrency"]["cancel-in-progress"] is False
    steps = workflow["jobs"]["lint"]["steps"]
    assert any("scripts.aeo.surface_drift" in step.get("run", "") for step in steps)
    build = yaml.safe_load((ROOT / ".github/workflows/deploy-sites.yml").read_text())["jobs"][
        "build"
    ]
    assert (
        sum(
            "pipeline.surface_lint --tree dist/modelspec" in step.get("run", "")
            for step in build["steps"]
        )
        == 2
    )
