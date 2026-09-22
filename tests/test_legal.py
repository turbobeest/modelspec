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
3. **Nothing claims a capability that is not shipped, and what is shipped is
   described as it is.** The documents were adopted as v1.0 on 2026-09-19. The
   billing terms are checked against `api/worker/tiers.json`, the privacy
   statement against what the Worker binds and writes, and outcome logging and
   x402 must stay described as not live until they are.
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
    assert neutrality["operator"] == "Sparks and Sawdust LLC"
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
    assert "Sparks and Sawdust LLC" in FLAT_TERMS
    assert "Sparks and Sawdust LLC" in FLAT_NEUTRALITY


# ── nothing claims what is not shipped ───────────────────────────────────────

def _billing_prices() -> list[dict]:
    tiers = json.loads((REPO_ROOT / "api" / "worker" / "tiers.json").read_text(encoding="utf-8"))
    return list(tiers["billing"]["prices"].values())


def test_the_terms_state_the_plans_and_packs_that_are_configured() -> None:
    """§6 names each plan and pack. Changing a price in tiers.json without
    changing the terms fails here, because the terms are what a buyer agreed to."""
    for price in _billing_prices():
        credits = f"{price['credits']:,}"
        usd = f"${price['usd']}"
        assert credits in FLAT_TERMS, (price["name"], credits)
        assert usd in FLAT_TERMS, (price["name"], usd)
        if price["kind"] == "plan":
            assert price["name"] in FLAT_TERMS
    tiers = json.loads((REPO_ROOT / "api" / "worker" / "tiers.json").read_text(encoding="utf-8"))
    assert tiers["credits"]["pack_expiry_days"] == 365
    assert "Pack credits expire 12 months after purchase" in FLAT_TERMS
    assert "do not roll over" in FLAT_TERMS
    assert "goes to zero at once" in FLAT_TERMS


def test_the_terms_name_the_seller_processor_and_statement_descriptor() -> None:
    assert "The seller is **Sparks and Sawdust LLC**" in FLAT_TERMS
    assert "processed by Stripe" in FLAT_TERMS
    assert "SPARKS & SAWDUST LLC" in FLAT_TERMS
    assert "https://modelspec.dev/pricing" in FLAT_TERMS


def test_the_terms_neither_deny_nor_promise_that_purchase_is_open() -> None:
    """`BILLING_ENABLED` decides whether Checkout is open, and it can flip without
    a terms change. The terms point at /pricing for availability instead."""
    for stale in ("no metered tier, no billing and no payment rail", "no charge exists",
                  "No price is in force", "None of this is in operation"):
        assert stale not in FLAT_TERMS, stale
    assert "Current plans, prices and availability are published at" in FLAT_TERMS


def test_the_terms_do_not_offer_x402_while_it_is_off() -> None:
    config = _wrangler_config()
    if '"X402_ENABLED": "false"' in config:
        assert "Payment by x402 is not currently offered." in FLAT_TERMS


def test_the_privacy_statement_does_not_describe_outcome_logging_as_built() -> None:
    """Outcome logging is not built. Describing it would be the exact failure to avoid."""
    section = PRIVACY.split("## Not yet live", 1)
    assert len(section) == 2, "the privacy statement must keep a 'Not yet live' section"
    before, after = flat(section[0]), flat(section[1])
    assert "Outcome logging" not in before
    assert "Outcome logging" in after
    assert "Not built" in after


def _wrangler_config() -> str:
    """`wrangler.jsonc` with its comment lines removed: what Wrangler would bind.

    A binding staged as a `//` comment is configuration waiting for a namespace,
    not a store, and the statement describes the two differently.
    """
    text = (REPO_ROOT / "api" / "worker" / "wrangler.jsonc").read_text(encoding="utf-8")
    return "\n".join(line for line in text.splitlines()
                     if not line.lstrip().startswith("//"))


def _kv_bindings(config: str) -> set[str]:
    import re
    block = re.search(r'"kv_namespaces"\s*:\s*\[(.*?)\]', config, flags=re.S)
    return set(re.findall(r'"binding"\s*:\s*"([A-Z_]+)"', block.group(1))) if block else set()


def test_the_privacy_statement_says_keys_are_wired_and_not_enforced() -> None:
    """MODEL-69 is wired with enforcement off. `entry.py` and `wrangler.jsonc` are
    the evidence, so check them rather than the prose alone."""
    entry = (REPO_ROOT / "api" / "worker" / "src" / "entry.py").read_text(encoding="utf-8")
    assert "access.gate(" in entry, "the access gate is no longer wired; the statement says it is"
    assert "not wired into the deployed" not in FLAT_PRIVACY
    config = _wrangler_config()
    enforced = '"ACCESS_ENFORCED": "false"' not in config
    claims_off = "enforcement off" in FLAT_PRIVACY and "no key is required" in FLAT_PRIVACY
    assert enforced != claims_off, (
        "wrangler.jsonc and the privacy statement disagree about whether a key is "
        "required; whichever changed, the other has to change with it")


def test_the_privacy_statement_matches_what_the_worker_binds() -> None:
    """The statement promises nothing of a request's content is written. Keep that true.

    The Worker may bind two KV namespaces, one Durable Object, and no other store:

    * DETERMINATIONS — our own research, read-only from the Worker, disclosed;
    * ACCESS (MODEL-69, MODEL-73) — key records, per-key counters, Stripe event
      ids, subscription rows, session pointers and keyrefs, only alongside the
      statement's section saying exactly what it holds, and described as not
      yet active for as long as the binding is staged as a comment;
    * CREDITS (MODEL-75) — a Durable Object ledger of prepaid x402 balances and
      payment claims, only alongside the statement's section saying exactly
      what it holds.

    Any other store, any write outside the access and credits modules, or an
    access module writing anything taken from a request's body, makes the
    statement false.
    """
    worker = REPO_ROOT / "api" / "worker"
    raw = (worker / "wrangler.jsonc").read_text(encoding="utf-8")
    config = _wrangler_config()
    for binding in ("d1_databases", "r2_buckets", "queues",
                    "hyperdrive", "analytics_engine_datasets"):
        assert binding not in config, (
            f"the Worker now binds {binding}; the privacy statement says nothing "
            "from a request is written anywhere, and that has stopped being true"
        )
    if "durable_objects" in config:
        assert "CreditsObject" in config and '"name": "CREDITS"' in config, (
            "a Durable Object other than CREDITS/CreditsObject is bound; "
            "the privacy statement describes that ledger and nothing else")
        for claim in ("`CREDITS`", "CreditsObject", "SHA-256 hash of",
                      "two integers", "payment claim", "transaction hash",
                      "no request body", "no IP address"):
            assert claim in FLAT_PRIVACY, (
                f"the CREDITS Durable Object is bound and the privacy statement "
                f"does not say {claim!r}")
        assert "X402_ENABLED" in FLAT_PRIVACY
    else:
        assert "CreditsObject" not in FLAT_PRIVACY or "not bound" in FLAT_PRIVACY
    bound = _kv_bindings(config)
    assert bound <= {"DETERMINATIONS", "ACCESS"}, (
        f"a KV namespace other than DETERMINATIONS and ACCESS is bound ({sorted(bound)}); "
        "the privacy statement describes exactly those stores and says what is in each"
    )
    if "DETERMINATIONS" in bound:
        assert "DETERMINATIONS" in FLAT_PRIVACY, (
            "the Worker binds a store the privacy statement does not disclose")
        assert "only ever reads from it" in FLAT_PRIVACY

    # ACCESS, staged or bound, must be disclosed with what it holds.
    access_staged = '"binding": "ACCESS"' in raw
    if access_staged or "ACCESS" in bound:
        for claim in ("`ACCESS`", "SHA-256 hash of the key", "never under the key",
                      "the key value itself is never stored",
                      "Two counters per key", "no request body", "no IP address",
                      "Stripe event id", "subscription record",
                      "Checkout session pointer", "keyref", "Card data never"):
            assert claim in FLAT_PRIVACY, (
                f"the ACCESS store is configured and the privacy statement does not "
                f"say {claim!r}")
    if "ACCESS" in bound:
        assert "configured, not yet active" not in FLAT_PRIVACY, (
            "ACCESS is bound now; the statement still calls the key store not yet active")
    elif access_staged:
        assert "configured, not yet active" in FLAT_PRIVACY and "commented out" in FLAT_PRIVACY

    # Only the access modules write KV. billing*.py decides; access_billing.py stores.
    # credits*.py mutate the Durable Object via SQL, not Workers KV.
    for src in sorted((worker / "src").glob("*.py")):
        body = src.read_text(encoding="utf-8")
        if src.name.startswith("access") or src.name.startswith("credits"):
            continue
        assert ".put(" not in body and ".delete(" not in body, (
            f"{src.name} writes to KV; the privacy statement says the Worker "
            "only ever reads from DETERMINATIONS")
    _assert_access_writes_only_records_and_counters(worker / "src")


def _assert_access_writes_only_records_and_counters(src: Path) -> None:
    """Every KV write in the access modules names a key record or a counter.

    Read from the syntax tree: each `.put(` call's first argument must be
    `storage_name(...)` (a key record, named by the key's hash) or a counter
    name built by `counter_name(...)`, and its value a record's JSON or a count.
    A write of anything else — a body, a header, a prompt — fails here.
    """
    import ast

    allowed_names = {
        "storage_name", "storage_name_from_fingerprint",
        "day_name", "minute_name", "name",
        "event_name", "session_name", "subscription_name", "keyref_name",
    }
    for module in sorted(src.glob("access*.py")):
        tree = ast.parse(module.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "put" and node.args):
                continue
            target = node.args[0]
            label = (target.func.id if isinstance(target, ast.Call)
                     and isinstance(target.func, ast.Name) else getattr(target, "id", None))
            assert label in allowed_names, (
                f"{module.name}:{node.lineno} writes to KV under {ast.unparse(target)}; "
                "the privacy statement says the access store holds named record "
                "kinds only")
            if len(node.args) > 1:
                value = ast.unparse(node.args[1])
                assert ("to_json()" in value or "_used + 1" in value
                        or value == "value"), (
                    f"{module.name}:{node.lineno} writes {value} to KV; only a key "
                    "record's JSON or a count may be written")
    # And the gate is handed no part of the body: the key comes off the headers,
    # and the body reaches only the handlers that answer, never the store.
    entry = ast.parse((src / "entry.py").read_text(encoding="utf-8"))
    gate = next(node for node in ast.walk(entry) if isinstance(node, ast.Call)
                and ast.unparse(node.func) == "access.gate")
    for keyword in gate.keywords:
        names = {n.id for n in ast.walk(keyword.value) if isinstance(n, ast.Name)}
        assert not names & {"payload", "raw"}, (
            f"access.gate({keyword.arg}=...) is handed the request body")
    assert "access_keys.extract" in ast.unparse(
        next(k.value for k in gate.keywords if k.arg == "api_key"))


def test_no_access_module_writes_a_plaintext_key() -> None:
    """The key is stored only as its SHA-256 hash. A `secret` field on a record
    would be the key sitting in ACCESS until someone claims it."""
    import ast

    forbidden = {"secret", "plaintext", "api_key", "key_value"}
    src = REPO_ROOT / "api" / "worker" / "src"
    for module in sorted(src.glob("access*.py")):
        tree = ast.parse(module.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            for stmt in node.body:
                name = None
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                    name = stmt.target.id
                elif (isinstance(stmt, ast.Assign) and stmt.targets
                      and isinstance(stmt.targets[0], ast.Name)):
                    name = stmt.targets[0].id
                assert name not in forbidden, (
                    f"{module.name}::{node.name} field {name!r} would store a key "
                    "value; the privacy statement says the key is stored only as "
                    "its SHA-256 hash")


def test_the_privacy_statement_discloses_cloudflare_observability() -> None:
    """It is on. A statement that says 'we log nothing' would be false by omission."""
    config = (REPO_ROOT / "api" / "worker" / "wrangler.jsonc").read_text(encoding="utf-8")
    assert '"observability": { "enabled": true }' in config
    assert "Workers observability is enabled" in FLAT_PRIVACY


def test_the_privacy_statement_says_pages_load_nothing_third_party() -> None:
    """No page on either site loads a font from a CDN any more (MODEL-92, with
    explorer.html switched in MODEL-24's PR #115), so the draft must not disclose
    a Google Fonts request that no longer happens. tests/test_no_font_cdn.py
    proves the premise against the source tree and a built site."""
    from pipeline import render as r
    assert "fonts.googleapis.com" not in r.FONTS
    assert "fonts.googleapis.com" not in FLAT_PRIVACY
    assert "Google Fonts" not in FLAT_PRIVACY
    assert "pages load nothing from a third party" in FLAT_PRIVACY


def test_the_privacy_statement_claims_no_prompt_field_and_the_api_has_none() -> None:
    """'Profiles, not prompts' is architecture only while the surface has no prompt."""
    source = (REPO_ROOT / "api" / "worker" / "src" / "rank_service.py").read_text(encoding="utf-8")
    for field in ('"prompt"', "'prompt'", '"messages"', '"input_text"'):
        assert field not in source, (
            f"{field} appeared in the rank request surface; §10.2 says a request carries "
            "a profile, not a prompt, and the privacy statement says so to customers"
        )
    assert "There is no field" in FLAT_PRIVACY


def test_every_document_is_adopted_version_1_0() -> None:
    """Adopted by Sparks and Sawdust LLC on 2026-09-19. The version and date are
    at the top of each document, and no draft banner survives."""
    assert legal.DRAFT is False
    for name, text in (("terms", TERMS), ("neutrality", NEUTRALITY), ("privacy", PRIVACY)):
        head = flat(text[:400])
        assert "Version `1.0`, effective 2026-09-19." in head, name
        assert "Adopted by Sparks and Sawdust LLC" in head, name
        assert "DRAFT" not in text, name
        assert "Not adopted" not in text, name


def test_every_document_names_a_contact_and_no_placeholder_remains() -> None:
    for name, text in (("terms", FLAT_TERMS), ("privacy", FLAT_PRIVACY)):
        assert "sales@modelspec.dev" in text, name
        assert "to be filled in" not in text, name
    # The counsel list moved to the README; the terms say plainly what they omit.
    assert "needs a lawyer before adoption" not in FLAT_TERMS
    assert "does not address" in FLAT_TERMS
    readme = flat((DOCS / "README.md").read_text(encoding="utf-8"))
    for item in ("governing law, jurisdiction and venue", "limitation of liability",
                 "indemnity", "class-action waiver", "cooling-off",
                 "sales tax and VAT", "controller/processor", "change of control"):
        assert item in readme, item
    assert "without the counsel review" in readme


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


def test_an_adopted_document_is_indexed_and_in_the_sitemap(tmp_path: Path) -> None:
    """In force: indexable, advertised in sitemap.xml, no draft banner."""
    result = legal.write(tmp_path, REPO_ROOT, _build())
    assert result["draft"] is False
    assert result["sitemap_paths"] == [d.url_path for d in legal.DOCS]
    for doc in legal.DOCS:
        html = (tmp_path / legal.LEGAL_ROOT / doc.slug / "index.html").read_text(encoding="utf-8")
        assert '<meta name="robots" content="index, follow">' in html, doc.slug
        assert "has not been adopted" not in html, doc.slug


def test_the_draft_switch_still_hides_a_draft(tmp_path: Path, monkeypatch) -> None:
    """The mechanism stays correct for a future revision published as a draft."""
    monkeypatch.setattr(legal, "DRAFT", True)
    result = legal.write(tmp_path, REPO_ROOT, _build())
    assert result["sitemap_paths"] == []
    html = (tmp_path / "legal/terms/index.html").read_text(encoding="utf-8")
    assert '<meta name="robots" content="noindex, nofollow">' in html
    assert "has not been adopted" in html


def test_the_landing_page_and_every_generated_page_link_all_three() -> None:
    """MODEL-70's last criterion: reachable from the landing page and the API docs."""
    from pipeline import render as r

    landing = (REPO_ROOT / "site" / "holding" / "index.html").read_text(encoding="utf-8")
    footer = landing.split("<footer>", 1)[1]
    shell = r.shell(title="t", description="d", canonical=None, body="", build=_build(),
                    site="ModelSpec", nav_links=r.MS_NAV)
    api_docs = (REPO_ROOT / "docs" / "api.md").read_text(encoding="utf-8")
    for doc in legal.DOCS:
        assert f'href="{doc.url_path}"' in footer, doc.slug
        assert f'href="{doc.url_path}"' in shell.split("<footer>", 1)[1], doc.slug
        assert f"](https://modelspec.dev{doc.url_path})" in api_docs, doc.slug


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
