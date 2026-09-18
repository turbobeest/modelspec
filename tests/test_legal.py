"""The terms, the neutrality commitment and the privacy statement (MODEL-70).

Three things are worth a test here, and they are not the prose.

1. **The commitment is fetchable as data, without a key.** It rides in
   `ranking_policy()`, so it reaches `/api/rank/profiles.json` — a static file
   on Cloudflare Pages with no auth in front of it — and the `policy` block of
   every rank response. An agent that cannot verify a claim has to trust it, and
   a neutrality claim that has to be trusted is worth what any such claim is
   worth.
2. **The prose and the JSON cannot drift.** The honest-broker rule has to appear
   verbatim in the published terms, and the pledge verbatim in the published
   commitment. One string, asserted in both places, so editing the constant
   without editing the document (or the reverse) fails here rather than on a
   customer's reading of a term we no longer keep.
3. **Nothing claims a capability that is not shipped.** The tests that matter
   most are the negative ones at the bottom: keys, prices and outcome logging
   are not live, and a document that starts describing them as live should not
   reach a reader before someone has looked again.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.ranking.engine import (
    HONEST_BROKER_RULE,
    LEGAL_BASE_URL,
    MIN_BENCHMARK_COUNT,
    MIN_BENCHMARK_COVERAGE,
    NEUTRALITY_PLEDGE,
    neutrality_commitment,
    ranking_policy,
)
from pipeline import legal

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS = legal.source_dir(REPO_ROOT)


def _text(name: str) -> str:
    return (DOCS / name).read_text(encoding="utf-8")


TERMS = _text("terms-of-service.md")
NEUTRALITY = _text("neutrality.md")
PRIVACY = _text("privacy.md")


def flat(text: str) -> str:
    """Collapse the source wrapping, so a reflowed paragraph is not a failure."""
    return " ".join(text.split())


FLAT_TERMS = flat(TERMS)
FLAT_NEUTRALITY = flat(NEUTRALITY)
FLAT_PRIVACY = flat(PRIVACY)


# ── the machine-readable half ────────────────────────────────────────────────

def test_the_commitment_rides_with_the_floors() -> None:
    """Same object as the numbers it constrains, or a caller has to fetch twice."""
    policy = ranking_policy()
    assert policy["min_benchmark_coverage"] == MIN_BENCHMARK_COVERAGE
    assert policy["min_benchmark_count"] == MIN_BENCHMARK_COUNT
    neutrality = policy["neutrality"]
    assert neutrality["rule"] == HONEST_BROKER_RULE
    assert neutrality["pledge"] == NEUTRALITY_PLEDGE
    assert neutrality["operator"] == "Sparks & Sawdust LLC"
    assert neutrality["permanent"] is True


@pytest.mark.parametrize("assertion", [
    "accepts_referral_fees",
    "accepts_paid_placement",
    "accepts_provider_paid_visibility",
    "proxies_inference_tokens",
    "stores_customer_prompts",
])
def test_every_neutrality_assertion_is_false(assertion: str) -> None:
    """Each is a thing the service does not do. A true value is a different product."""
    assert neutrality_commitment()["assertions"][assertion] is False


def test_neutrality_covers_the_stages_where_a_lean_would_hide() -> None:
    """Refusing payment is the easy half; a tie-break nobody audits is the other."""
    stages = set(neutrality_commitment()["source_neutral_at"])
    assert {"ranking", "tie_breaks", "hosting_suggestions", "route_advice"} <= stages


def test_the_commitment_survives_json_serialisation() -> None:
    """It is published as JSON, so it has to be JSON — no sets, no tuples, no dates."""
    round_tripped = json.loads(json.dumps(neutrality_commitment(), sort_keys=True))
    assert round_tripped == json.loads(json.dumps(neutrality_commitment(), sort_keys=True))
    assert round_tripped["rule"] == HONEST_BROKER_RULE


def test_a_caller_cannot_mutate_the_published_commitment() -> None:
    """`ranking_policy()` is embedded in many reports; a shared dict would leak edits."""
    first = ranking_policy()
    first["neutrality"]["assertions"]["accepts_paid_placement"] = True
    assert ranking_policy()["neutrality"]["assertions"]["accepts_paid_placement"] is False


def test_the_exported_profiles_carry_the_commitment(tmp_path: Path) -> None:
    """`/api/rank/profiles.json` is the keyless copy. This is the acceptance criterion."""
    from pipeline.ranking import write_export
    from schema.graph import derive_graph

    write_export(tmp_path, [], derive_graph([], {}), {"commit": "test"})
    published = json.loads((tmp_path / "profiles.json").read_text(encoding="utf-8"))
    neutrality = published["ranking_policy"]["neutrality"]
    assert neutrality["rule"] == HONEST_BROKER_RULE
    assert neutrality["pledge"] == NEUTRALITY_PLEDGE
    # Next to the floors, in the same object, so one fetch answers both.
    assert published["ranking_policy"]["min_benchmark_coverage"] == MIN_BENCHMARK_COVERAGE


def test_the_rank_endpoint_publishes_the_commitment_too() -> None:
    """An agent should read the commitment out of the answer it acted on."""
    import sys
    sys.path.insert(0, str(REPO_ROOT / "api" / "worker" / "src"))
    try:
        import rank_service as service
    finally:
        sys.path.pop(0)
    assert service.ranking_policy()["neutrality"]["rule"] == HONEST_BROKER_RULE


# ── prose that has to match the data ─────────────────────────────────────────

def test_the_honest_broker_rule_appears_verbatim_in_the_terms() -> None:
    """The ticket's own acceptance criterion, and the reason the ticket exists."""
    assert flat(HONEST_BROKER_RULE) in FLAT_TERMS


def test_the_rule_and_the_pledge_appear_verbatim_in_the_commitment() -> None:
    assert flat(HONEST_BROKER_RULE) in FLAT_NEUTRALITY
    assert flat(NEUTRALITY_PLEDGE) in FLAT_NEUTRALITY


def test_the_pledge_appears_verbatim_in_the_terms() -> None:
    assert flat(NEUTRALITY_PLEDGE) in FLAT_TERMS


def test_permanently_is_not_quietly_dropped() -> None:
    """A commitment that lasts until the offer is good enough is a price."""
    assert "permanently" in NEUTRALITY_PLEDGE
    assert neutrality_commitment()["permanent"] is True


def test_the_published_urls_agree_with_where_the_pages_are_written() -> None:
    """A terms_url in the JSON that 404s is worse than no terms_url."""
    commitment = neutrality_commitment()
    by_slug = {d.slug: d for d in legal.DOCS}
    for slug, key in (("terms", "terms_url"), ("neutrality", "neutrality_url"),
                      ("privacy", "privacy_url")):
        assert commitment[key] == by_slug[slug].absolute_url("https://modelspec.dev")
    assert LEGAL_BASE_URL.endswith("/" + legal.LEGAL_ROOT)


# ── billing terms the ticket names explicitly ────────────────────────────────

def test_the_terms_say_only_successful_results_are_charged() -> None:
    assert "Only a successful result is charged" in FLAT_TERMS


def test_the_terms_price_a_rate_limit_refusal_at_nothing() -> None:
    assert "Being told to slow down costs nothing" in FLAT_TERMS


@pytest.mark.parametrize("status", ["400", "404", "422", "429", "5xx"])
def test_the_terms_name_each_uncharged_outcome(status: str) -> None:
    """Every refusal the endpoint can actually return is accounted for."""
    assert status in FLAT_TERMS


def test_the_terms_state_a_refund_position() -> None:
    assert "**6.6 Refunds.**" in FLAT_TERMS
    assert "refunded in full" in FLAT_TERMS


def test_the_operator_is_named() -> None:
    assert "Sparks & Sawdust LLC" in FLAT_TERMS
    assert "Sparks & Sawdust LLC" in FLAT_NEUTRALITY


# ── nothing claims what is not shipped ───────────────────────────────────────

def test_the_terms_say_no_billing_is_live() -> None:
    """MODEL-73 and MODEL-75 are not merged. The terms must not read as if they were."""
    assert "no metered tier, no billing and no payment rail" in FLAT_TERMS
    assert "no charge exists" in FLAT_TERMS


def test_the_privacy_statement_does_not_describe_outcome_logging_as_built() -> None:
    """Outcome logging is not built. Describing it would be the exact failure to avoid."""
    section = PRIVACY.split("## Not yet live", 1)
    assert len(section) == 2, "the privacy statement must keep a 'Not yet live' section"
    before, after = flat(section[0]), flat(section[1])
    assert "Outcome logging" not in before
    assert "Outcome logging" in after
    assert "Not built" in after


def test_the_privacy_statement_marks_keys_as_not_wired() -> None:
    """MODEL-69 is merged and not wired. `entry.py` is the evidence, so check it."""
    entry = (REPO_ROOT / "api" / "worker" / "src" / "entry.py").read_text(encoding="utf-8")
    wired = "import access" in entry or "access.serve" in entry
    claims_not_wired = "not wired into the deployed" in FLAT_PRIVACY
    assert wired != claims_not_wired, (
        "the Worker's entry point and the privacy statement disagree about whether "
        "API keys are live; whichever changed, the other has to change with it"
    )


def test_the_privacy_statement_matches_what_the_worker_binds() -> None:
    """The statement promises nothing of a request is written. Keep that true.

    The Worker may bind the DETERMINATIONS KV namespace — that holds our own
    research, is read-only from the Worker, and is disclosed. Any OTHER store,
    or any write to this one, makes the statement false.
    """
    worker = REPO_ROOT / "api" / "worker"
    config = (worker / "wrangler.jsonc").read_text(encoding="utf-8")
    for binding in ("d1_databases", "r2_buckets", "queues",
                    "durable_objects", "hyperdrive", "analytics_engine_datasets"):
        assert binding not in config, (
            f"the Worker now binds {binding}; the privacy statement says nothing "
            "from a request is written anywhere, and that has stopped being true"
        )
    if "kv_namespaces" in config:
        assert '"binding": "DETERMINATIONS"' in config, (
            "a KV namespace other than DETERMINATIONS is bound; the privacy "
            "statement describes exactly one store and says what is in it"
        )
        assert "DETERMINATIONS" in FLAT_PRIVACY, (
            "the Worker binds a store the privacy statement does not disclose"
        )
        for src in sorted((worker / "src").glob("*.py")):
            if src.name.startswith("access"):
                continue  # MODEL-69's own store, covered by its own tests
            body = src.read_text(encoding="utf-8")
            assert ".put(" not in body and ".delete(" not in body, (
                f"{src.name} writes to KV; the privacy statement says the Worker "
                "only ever reads from DETERMINATIONS"
            )
    assert "only ever reads from it" in FLAT_PRIVACY


def test_the_privacy_statement_discloses_cloudflare_observability() -> None:
    """It is on. A statement that says 'we log nothing' would be false by omission."""
    config = (REPO_ROOT / "api" / "worker" / "wrangler.jsonc").read_text(encoding="utf-8")
    assert '"observability": { "enabled": true }' in config
    assert "Workers observability is enabled" in FLAT_PRIVACY


def test_the_privacy_statement_discloses_the_one_third_party_request() -> None:
    """The shell loads Google Fonts on every page. That is a disclosure, not a detail."""
    from pipeline import render as r
    assert "fonts.googleapis.com" in r.FONTS
    assert "fonts.googleapis.com" in FLAT_PRIVACY


def test_the_privacy_statement_claims_no_prompt_field_and_the_api_has_none() -> None:
    """'Profiles, not prompts' is architecture only while the surface has no prompt."""
    source = (REPO_ROOT / "api" / "worker" / "src" / "rank_service.py").read_text(encoding="utf-8")
    for field in ('"prompt"', "'prompt'", '"messages"', '"input_text"'):
        assert field not in source, (
            f"{field} appeared in the rank request surface; §10.2 says a request carries "
            "a profile, not a prompt, and the privacy statement says so to customers"
        )
    assert "There is no field" in FLAT_PRIVACY


def test_every_document_says_it_is_a_draft() -> None:
    """Nothing here is adopted, and a reader should not have to infer that."""
    for name, text in (("terms", TERMS), ("neutrality", NEUTRALITY), ("privacy", PRIVACY)):
        assert "DRAFT" in text.split("\n\n", 3)[1] or "DRAFT" in text[:400], name
    assert legal.DRAFT is True


# ── publication ──────────────────────────────────────────────────────────────

def _build():
    from pipeline.export import Build
    from datetime import date
    return Build(commit="0" * 40, built_at="2026-09-17T00:00:00Z", as_of=date(2026, 9, 17))


def test_every_document_renders_to_its_stable_url(tmp_path: Path) -> None:
    result = legal.write(tmp_path, REPO_ROOT, _build())
    assert result["documents"] == len(legal.DOCS)
    for doc in legal.DOCS:
        page = tmp_path / legal.LEGAL_ROOT / doc.slug / "index.html"
        assert page.is_file(), doc.url_path
        html = page.read_text(encoding="utf-8")
        assert f'<link rel="canonical" href="https://modelspec.dev{doc.url_path}">' in html


def test_the_rendered_terms_carry_the_rule_verbatim(tmp_path: Path) -> None:
    """Verbatim in the *published* page, which is what the criterion asks for."""
    legal.write(tmp_path, REPO_ROOT, _build())
    html = (tmp_path / "legal/terms/index.html").read_text(encoding="utf-8")
    # The renderer escapes and re-wraps, so compare on collapsed text with the
    # emphasis markup removed rather than on the raw bytes.
    flattened = flat(html.replace("<strong>", "").replace("</strong>", ""))
    assert flat(HONEST_BROKER_RULE) in flattened


def test_a_draft_is_published_but_not_advertised(tmp_path: Path) -> None:
    """Stable URL from the first build; no crawler presenting it as terms in force."""
    result = legal.write(tmp_path, REPO_ROOT, _build())
    assert result["sitemap_paths"] == []
    html = (tmp_path / "legal/terms/index.html").read_text(encoding="utf-8")
    assert '<meta name="robots" content="noindex, nofollow">' in html
    assert "has not been adopted" in html


def test_a_missing_source_document_fails_the_build(tmp_path: Path) -> None:
    """A legal page that silently stops being published is the worst failure mode."""
    empty = tmp_path / "root"
    (empty / "docs" / "legal").mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        legal.write(tmp_path / "out", empty, _build())


def test_the_title_is_not_rendered_twice(tmp_path: Path) -> None:
    title, body = legal.split_title("# Terms of service\n\nSome text.\n")
    assert title == "Terms of service"
    assert "# Terms of service" not in body


def test_each_page_reaches_the_other_two(tmp_path: Path) -> None:
    legal.write(tmp_path, REPO_ROOT, _build())
    for doc in legal.DOCS:
        html = (tmp_path / legal.LEGAL_ROOT / doc.slug / "index.html").read_text(encoding="utf-8")
        for other in legal.DOCS:
            if other.slug != doc.slug:
                assert f'href="{other.url_path}"' in html
