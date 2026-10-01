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
   statement against what the Worker binds and writes, and outcome logging by
   the service and x402 must stay described as not live until they are.
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
    VENDOR_PURCHASE_RULE,
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
    "conceals_purchases_from_catalogued_vendors",
    "lets_supplier_models_write_supplier_cards",
])
def test_every_neutrality_assertion_is_false(assertion: str) -> None:
    """Each is a thing the service does not do. A true value is a different product."""
    assert neutrality_commitment()["assertions"][assertion] is False


def test_neutrality_covers_the_stages_where_a_lean_would_hide() -> None:
    """Refusing payment is the easy half; a tie-break nobody audits is the other."""
    stages = set(neutrality_commitment()["source_neutral_at"])
    assert {"ranking", "tie_breaks", "hosting_suggestions", "route_advice"} <= stages


def test_buying_from_a_catalogued_vendor_is_published_as_data() -> None:
    """Neutrality 1.1. The pledge covers money coming in; this covers money going
    out, to a vendor the catalogue also documents."""
    commitment = neutrality_commitment()
    assert commitment["vendor_purchases"] == VENDOR_PURCHASE_RULE
    assert ranking_policy()["neutrality"]["vendor_purchases"] == VENDOR_PURCHASE_RULE


def test_the_vendor_purchase_assertions_are_held_by_code() -> None:
    """Each published `false` is a mechanism, not a promise.

    `conceals_purchases_from_catalogued_vendors`: every vendor in
    `schema/suppliers.py` gets a disclosure on its card page, derived from the
    same table. `lets_supplier_models_write_supplier_cards`: the guard in
    `scripts/attribution.py` protects exactly that table and refuses any listing
    that puts a supplier in play. `tests/test_attribution.py` tests the refusals
    end to end; this ties them to the published assertions.
    """
    from types import SimpleNamespace

    from pipeline.render import supplier_disclosure
    from schema.suppliers import SUPPLIERS
    from scripts import attribution

    assert SUPPLIERS, "the table is empty, so the assertions would hold vacuously"
    assert attribution.SUPPLIER_SLUGS == frozenset(SUPPLIERS)
    for slug in SUPPLIERS:
        disclosure = supplier_disclosure({"provider": slug})
        assert "Disclosure." in disclosure, slug
        assert 'href="/legal/neutrality/"' in disclosure, slug
        listing = SimpleNamespace(candidates=[slug], vendor=None)
        assert attribution.supplier_conflict(listing) == slug
        on_page = SimpleNamespace(candidates=[], vendor=slug)
        assert attribution.supplier_conflict(on_page) == slug
    assert supplier_disclosure({"provider": "not-a-supplier"}) == ""
    assert callable(attribution.apply_policy)


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


def test_the_vendor_purchase_rule_appears_verbatim_in_the_commitment() -> None:
    """Neutrality 1.1: the sentence in the JSON is the sentence in the document,
    and the document names the files that hold it."""
    assert flat(VENDOR_PURCHASE_RULE) in FLAT_NEUTRALITY
    for path in ("schema/suppliers.py", "scripts/attribution.py", "pipeline/render.py"):
        assert f"`{path}`" in NEUTRALITY, path
        assert (REPO_ROOT / path).is_file(), path
    for symbol in ("supplier_conflict", "apply_policy"):
        assert f"`{symbol}`" in NEUTRALITY, symbol
    for assertion in neutrality_commitment()["assertions"]:
        assert f'"{assertion}": false' in NEUTRALITY, assertion
    assert "1.1, 2026-09-23" in FLAT_NEUTRALITY


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
    assert "The seller is **Sparks & Sawdust LLC**" in FLAT_TERMS
    assert "processed by Stripe" in FLAT_TERMS
    # Stripe refuses an ampersand in a statement descriptor (Jamie, 2026-09-30).
    assert "SPARKS AND SAWDUST LLC" in FLAT_TERMS
    assert "SPARKS & SAWDUST" not in FLAT_TERMS
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
    """The service records no outcomes. Describing it as built would be the exact
    failure to avoid; MODEL-211's log is the CLI's, local and opt-in."""
    section = PRIVACY.split("## Not yet live", 1)
    assert len(section) == 2, "the privacy statement must keep a 'Not yet live' section"
    before, after = flat(section[0]), flat(section[1])
    assert "Outcome logging" not in before
    assert "Outcome logging by the service" in after
    assert "Not built" in after
    assert "docs/design/outcome-upload.md" in after


def test_the_privacy_statement_describes_the_local_outcome_log() -> None:
    """MODEL-211 ships an opt-in log that stays on the machine. v1.2 called outcome
    logging "Not built", which stopped being the whole truth when it merged."""
    assert (REPO_ROOT / "cli" / "modelspec" / "outcome.py").is_file()
    before = flat(PRIVACY.split("## Not yet live", 1)[0])
    for claim in ("`modelspec outcome enable`", "nothing until you turn it on",
                  "It never leaves your machine", "`cli/modelspec/outcome.py`"):
        assert claim in before, claim


def test_the_outcome_modules_open_no_connection() -> None:
    """"It never leaves your machine" holds only while the outcome code imports
    nothing that can reach a network. Upload is a separate, unbuilt path."""
    import ast

    network = {"socket", "ssl", "http", "urllib", "urllib3", "httpx", "requests",
               "aiohttp", "ftplib", "smtplib"}
    for name in ("outcome.py", "outcome_cmd.py"):
        tree = ast.parse((REPO_ROOT / "cli" / "modelspec" / name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots = {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                roots = {node.module.split(".")[0]}
            else:
                continue
            assert not roots & network, (
                f"cli/modelspec/{name} imports {sorted(roots & network)}; the privacy "
                "statement says the outcome log never leaves your machine")


def test_the_privacy_statement_names_every_browser_storage_key() -> None:
    """No cookie is set, but the decide page writes `localStorage` (MODEL-237).
    Every key a shipped page writes must be named, so a new one fails here."""
    import re

    keys = set()
    for folder in ("web", "web3d", "pipeline", "site"):
        for src in (REPO_ROOT / folder).rglob("*"):
            if (src.suffix not in {".ts", ".tsx", ".html", ".js", ".mjs", ".py"}
                    or not src.is_file()
                    or {"node_modules", "__tests__", "vendor", "dist"} & set(src.parts)
                    or ".test." in src.name):
                continue
            text = src.read_text(encoding="utf-8", errors="ignore")
            for other in ("sessionStorage", "indexedDB", "document.cookie"):
                assert other not in text, (
                    f"{src.relative_to(REPO_ROOT)} uses {other}; the privacy statement "
                    "says no cookie is set and names only localStorage")
            if "localStorage.setItem" in text:
                keys |= set(re.findall(r"""["'`](modelspec-[a-z0-9-]+)["'`]""", text))
    assert {"modelspec-theme", "modelspec-estate-v1", "modelspec-alerts"} <= keys
    for key in sorted(keys):
        assert f"`{key}`" in PRIVACY, (
            f"a page writes {key!r} to localStorage and the privacy statement does not name it")
    assert "No cookies are set" in FLAT_PRIVACY


def _meter_hashes_ip_without_a_key(source: str) -> bool:
    """True when the visitor meter reads the address and no HMAC keys it."""
    return "CF-Connecting-IP" in source and "hmac" not in source.lower()


def _x402_is_on_in_production() -> bool:
    from pipeline.worker_flags import parse_jsonc

    config = parse_jsonc((REPO_ROOT / "api" / "worker" / "wrangler.jsonc").read_text(encoding="utf-8"))
    flag = str(config["vars"].get("X402_ENABLED", "false")).strip().lower()
    return flag not in {"", "0", "false", "no", "off"}


def test_x402_stays_off_while_keyless_visitors_are_metered_by_a_bare_ip_hash() -> None:
    """MODEL-237/241. With x402 on, keyless browser meters are named from the
    visitor id. A bare hash of the IP is reversed by enumeration, so the id must
    be keyed (`visitor.py`) and `_site_free_visitor` must go through it."""
    worker = REPO_ROOT / "api" / "worker" / "src"
    visitor_source = (worker / "visitor.py").read_text(encoding="utf-8")
    entry_source = (worker / "entry.py").read_text(encoding="utf-8")
    import ast

    tree = ast.parse(entry_source)
    meter = ast.unparse(next(n for n in ast.walk(tree)
                             if isinstance(n, ast.FunctionDef) and n.name == "_site_free_visitor"))
    assert "hashlib" not in meter and "visitor.visitor_id_for" in meter
    assert not _meter_hashes_ip_without_a_key(visitor_source)
    if _meter_hashes_ip_without_a_key(visitor_source):
        assert not _x402_is_on_in_production()


def test_the_guard_still_fails_for_a_meter_with_no_key() -> None:
    bare = 'def f(r):\n    return sha256(r.headers.get("CF-Connecting-IP"))'
    assert _meter_hashes_ip_without_a_key(bare)
    keyed = 'def f(r):\n    return hmac.new(k, r.headers.get("CF-Connecting-IP"))'
    assert not _meter_hashes_ip_without_a_key(keyed)


def test_the_visitor_key_is_documented_as_a_secret_not_a_var() -> None:
    text = (REPO_ROOT / "api" / "worker" / "wrangler.jsonc").read_text(encoding="utf-8")
    assert "wrangler secret put VISITOR_HMAC_KEY" in text
    assert "VISITOR_HMAC_KEY\":" not in text


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

    # Only the access modules and disclosed release-signal service write KV.
    # billing*.py decides; access_billing.py stores.
    # credits*.py mutate the Durable Object via SQL, not Workers KV.
    # feedback_service.py (MODEL-221) writes only its own FEEDBACK namespace,
    # and may exist undisclosed only while that store can never be reached:
    # see test_feedback_storage_is_unreachable_until_the_statement_covers_it.
    for src in sorted((worker / "src").glob("*.py")):
        body = src.read_text(encoding="utf-8")
        if (src.name.startswith("access") or src.name.startswith("credits")
                or src.name in ("signals_service.py", "feedback_service.py")):
            continue
        assert ".put(" not in body and ".delete(" not in body, (
            f"{src.name} writes to KV; the privacy statement says the Worker "
            "only ever reads from DETERMINATIONS")
    _assert_access_writes_only_records_and_counters(worker / "src")
    for claim in ("release signal", "model name", "provider name", "first-seen X URL",
                  "confidence", "signal id", "1, 7 and 30 days", "SIGNALS_ENABLED"):
        assert claim in FLAT_PRIVACY, (
            f"the signal service writes ACCESS and the privacy statement does not say {claim!r}")


def test_feedback_storage_is_unreachable_until_the_statement_covers_it() -> None:
    """MODEL-221. The feedback endpoint ships with storage off.

    While the privacy statement says nothing of feedback, the Worker must not be
    able to keep any: `FEEDBACK_ENABLED` is off in production and staging and no
    `FEEDBACK` namespace is bound. Turning either on without adopting the
    wording in `docs/design/feedback-privacy.md` fails here. Once the statement
    discloses the store, it must name what a record holds.
    """
    import ast
    import sys

    from pipeline.worker_flags import parse_jsonc

    worker = REPO_ROOT / "api" / "worker"
    config = parse_jsonc((worker / "wrangler.jsonc").read_text(encoding="utf-8"))
    flags = [config["vars"].get("FEEDBACK_ENABLED", "false")] + [
        env.get("vars", {}).get("FEEDBACK_ENABLED", "false")
        for env in config.get("env", {}).values()]
    on = any(str(flag).strip().lower() not in {"", "0", "false", "no", "off"}
             for flag in flags)
    bound = "FEEDBACK" in _kv_bindings(_wrangler_config()) or any(
        kv.get("binding") == "FEEDBACK"
        for env in config.get("env", {}).values() for kv in env.get("kv_namespaces", []))
    disclosed = "`FEEDBACK`" in FLAT_PRIVACY
    if on or bound:
        assert disclosed, (
            "feedback storage is switched on or bound, and the privacy statement does not "
            "disclose the FEEDBACK store; adopt the wording in "
            "docs/design/feedback-privacy.md first")
        section = PRIVACY.split("### The feedback store", 1)[-1].split("\n#", 1)[0]
        assert "not yet live" not in flat(section), (
            "feedback storage is on and the statement still says it is not yet live")
    # A deploy-time `--var FEEDBACK_ENABLED:true` would dodge the check above.
    for workflow in (REPO_ROOT / ".github" / "workflows").glob("*.y*ml"):
        assert "FEEDBACK_ENABLED" not in workflow.read_text(encoding="utf-8"), workflow.name
    if disclosed:
        sys.path.insert(0, str(worker / "src"))
        try:
            import feedback_service
        finally:
            sys.path.remove(str(worker / "src"))
        for name in feedback_service.STORED_FIELDS:
            assert f"`{name}`" in FLAT_PRIVACY, (
                f"a feedback record holds {name!r} and the privacy statement does not say so")

    # Whatever the switch, the service writes only a record, under a name built
    # from the receipt's hash, and two counters.
    tree = ast.parse((worker / "src" / "feedback_service.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "put"):
            target = node.args[0]
            name = (target.func.id if isinstance(target, ast.Call)
                    and isinstance(target.func, ast.Name) else
                    target.id if isinstance(target, ast.Name) else None)
            assert name in {"_record_name", "address_name", "global_name"}, ast.unparse(node)


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


#: Third-party script hosts a page may load, each disclosed in the privacy
#: statement. Cloudflare injects Web Analytics at the edge (MODEL-236), so it is
#: not in the source tree; it is listed so that the live smoke check or a later
#: move into the source cannot add it silently. Adding a host here is a change to
#: the privacy statement.
DISCLOSED_THIRD_PARTY_SCRIPTS = {"static.cloudflareinsights.com": "### Cloudflare Web Analytics"}
_OWN_HOSTS = {"modelspec.dev", "www.modelspec.dev", "api.modelspec.dev"}
_LOADING_RELS = {"stylesheet", "preload", "modulepreload", "preconnect", "prefetch",
                 "dns-prefetch", "icon", "manifest"}


def _third_party_hosts(text: str) -> set[str]:
    """Hosts other than ours that markup or code loads a script, style or font from."""
    import re

    found = set(re.findall(
        r"""<script\b[^>]*?\bsrc\s*=\s*["']?(?:https?:)?//([^/"'\s>]+)""", text, re.I))
    found |= set(re.findall(r"""\b(?:fetch|import)\s*\(\s*["'`]https?://([^/"'`\s]+)""", text))
    for tag in re.findall(r"<link\b[^>]*>", text, re.I):
        rel = re.search(r"""\brel\s*=\s*["']?([^"'>]+)""", tag, re.I)
        href = re.search(r"""\bhref\s*=\s*["']?(?:https?:)?//([^/"'\s>]+)""", tag, re.I)
        if rel and href and _LOADING_RELS & set(rel.group(1).lower().split()):
            found.add(href.group(1))
    return {host.lower() for host in found} - _OWN_HOSTS


def test_the_host_detector_allows_the_beacon_and_nothing_else() -> None:
    """The guard below is only as good as this detector, so prove it on the tag
    Cloudflare injects (as captured from modelspec.dev on 2026-09-29) and on the
    loads it has to refuse."""
    beacon = ('<script defer src="https://static.cloudflareinsights.com/beacon.min.js/v31" '
              'data-cf-beacon=\'{"token":"t","spa":2}\' crossorigin="anonymous"></script>')
    assert _third_party_hosts(beacon) == {"static.cloudflareinsights.com"}
    assert set(_third_party_hosts(beacon)) <= set(DISCLOSED_THIRD_PARTY_SCRIPTS)
    for load, host in (
            ('<script src="https://cdn.jsdelivr.net/npm/x.js"></script>', "cdn.jsdelivr.net"),
            ('<script async src=//www.googletagmanager.com/gtag/js></script>',
             "www.googletagmanager.com"),
            ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2">',
             "fonts.googleapis.com"),
            ('fetch("https://plausible.io/api/event", {})', "plausible.io")):
        assert _third_party_hosts(load) == {host}, load
        assert host not in DISCLOSED_THIRD_PARTY_SCRIPTS
    ours = ('<script src="/assets/decide.js"></script><link rel="canonical" '
            'href="https://modelspec.dev/decide/"><a href="https://github.com/x">x</a>'
            'fetch("https://api.modelspec.dev/v1/decide")')
    assert _third_party_hosts(ours) == set()


def test_pages_load_no_third_party_script_but_the_disclosed_beacon(tmp_path: Path) -> None:
    """MODEL-236 / MODEL-237. The statement says the pages' one third-party request
    is Cloudflare's analytics script. Any other third-party script, stylesheet or
    font in a page's source, or in a rendered legal page, fails here."""
    hits: dict[str, set[str]] = {}
    for folder in ("site", "web", "web3d", "pipeline"):
        for src in (REPO_ROOT / folder).rglob("*"):
            if (src.suffix not in {".html", ".js", ".mjs", ".ts", ".tsx", ".py", ".css"}
                    or not src.is_file()
                    or {"node_modules", "__tests__", "vendor", "dist"} & set(src.parts)
                    or ".test." in src.name):
                continue
            hosts = _third_party_hosts(src.read_text(encoding="utf-8", errors="ignore"))
            if hosts - set(DISCLOSED_THIRD_PARTY_SCRIPTS):
                hits[str(src.relative_to(REPO_ROOT))] = hosts
    legal.write(tmp_path, REPO_ROOT, _build())
    for page in (tmp_path / legal.LEGAL_ROOT).rglob("*.html"):
        hosts = _third_party_hosts(page.read_text(encoding="utf-8"))
        if hosts - set(DISCLOSED_THIRD_PARTY_SCRIPTS):
            hits[str(page.relative_to(tmp_path))] = hosts
    assert hits == {}, (
        f"pages load third-party scripts the privacy statement does not disclose: {hits}")

    for host, section in DISCLOSED_THIRD_PARTY_SCRIPTS.items():
        assert section in PRIVACY, (host, section)
        assert f"`{host}`" in FLAT_PRIVACY, host
    assert "pages load nothing else from a third party" in FLAT_PRIVACY


def test_the_analytics_disclosure_states_its_purpose_and_its_limits() -> None:
    """Jamie's intent (MODEL-236): say why the beacon runs, in the short version
    and in its own section, and say that it does not identify anyone."""
    purpose = ("We want to know where our visitors come from and how they use the site, "
               "so we can make a better product. That is why we run Cloudflare Web Analytics.")
    short = flat(PRIVACY.split("## The short version", 1)[1].split("\n## ", 1)[0])
    section = flat(PRIVACY.split("### Cloudflare Web Analytics", 1)[1].split("\n## ", 1)[0])
    for text in (short, section):
        assert purpose in text
        assert "It does not tell us who you are" in text
    for claim in ("sets no cookie", "never shows us an IP address", "as our processor",
                  "https://www.cloudflare.com/web-analytics/"):
        assert claim in section, claim


def test_no_page_loads_a_font_from_a_cdn() -> None:
    """No page on either site loads a font from a CDN any more (MODEL-92, with
    explorer.html switched in MODEL-24's PR #115), so the statement must not
    disclose a Google Fonts request that no longer happens. tests/test_no_font_cdn.py
    proves the premise against the source tree and a built site."""
    from pipeline import render as r
    assert "fonts.googleapis.com" not in r.FONTS
    assert "fonts.googleapis.com" not in FLAT_PRIVACY
    assert "Google Fonts" not in FLAT_PRIVACY


def test_the_privacy_statement_claims_no_prompt_field_and_the_api_has_none() -> None:
    """'Profiles, not prompts' is architecture only while the surface has no prompt."""
    source = (REPO_ROOT / "api" / "worker" / "src" / "rank_service.py").read_text(encoding="utf-8")
    for field in ('"prompt"', "'prompt'", '"messages"', '"input_text"'):
        assert field not in source, (
            f"{field} appeared in the rank request surface; §10.2 says a request carries "
            "a profile, not a prompt, and the privacy statement says so to customers"
        )
    assert "There is no field" in FLAT_PRIVACY


def test_the_decide_contract_refuses_its_free_text_task() -> None:
    """The statement says `task`, the contract's one free-text field, is refused,
    and that fields a spec does not define are refused rather than ignored."""
    from decision import contract

    base = {"spec_version": 1, "optimize": {"max": "swe_bench_pro"}}
    assert contract.parse_spec(dict(base), facets=None).spec_version == 1
    for extra in ({"task": "summarise my contract"}, {"prompt": "hello"}):
        with pytest.raises(contract.SpecError):
            contract.parse_spec({**base, **extra}, facets=None)
    assert "`task`, is refused" in FLAT_PRIVACY


#: The version in force for each document. A change to what the service records
#: is a change to the privacy statement, and a commitment added to the neutrality
#: commitment is a change to that; each gets a new version and date rather than
#: a silent edit of the adopted one.
IN_FORCE = {
    "terms": "Version `1.2`, effective 2026-09-30.",
    "neutrality": "Version `1.3`, effective 2026-09-30.",
    "privacy": "Version `1.5`, effective 2026-09-30.",
}


def test_every_document_is_adopted_and_versioned() -> None:
    """Adopted by Sparks & Sawdust LLC on 2026-09-19 (v1.0). The version and
    date in force are at the top of each document, and no draft banner survives."""
    assert legal.DRAFT is False
    for name, text in (("terms", TERMS), ("neutrality", NEUTRALITY), ("privacy", PRIVACY)):
        head = flat(text[:400])
        assert IN_FORCE[name] in head, name
        assert "Adopted by Sparks & Sawdust LLC" in head, name
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

    from pipeline import landing as landing_page

    model = landing_page.PlotModel("model", "Model", .1, 1, 0, 2, True)
    data = landing_page.LandingData(
        "2026-09-27", 1, 40_000, 4_000, 10_000, (model,), "model", "model", 1,
        1000, 1000, 0, (), 0,
        landing_page._plot_axes([model]),
    )
    footer = landing_page.render(data, variant="live").split("<footer>", 1)[1]
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


def test_the_privacy_statement_describes_what_refunds_record() -> None:
    """MODEL-106 records, per Stripe pack, the PaymentIntent id and what refunds
    and chargebacks did to its credits. The statement must say so, and must say
    that no card detail is held."""
    assert "PaymentIntent id" in FLAT_PRIVACY
    assert "chargeback" in FLAT_PRIVACY
    assert "no card detail" in FLAT_PRIVACY
    assert "1.1, 2026-09-23" in FLAT_PRIVACY


def test_the_access_model_wording_is_in_the_terms_neutrality_and_licence() -> None:
    """MODEL-249: people free, machines paid and hosted, a delayed public image, no CLI."""
    assert "delayed image" in FLAT_TERMS
    assert "no data download and no command-line client" in FLAT_TERMS
    assert "Machine access is a paid product" in FLAT_TERMS
    assert "No account, no key, no charge" not in FLAT_TERMS
    flat_neutrality = flat(NEUTRALITY)
    assert "the sites and the CLI read" not in flat_neutrality
    assert "about nine months" in flat_neutrality
    licence = flat((REPO_ROOT / "LICENSE").read_text(encoding="utf-8"))
    assert "so the CLI can be embedded anywhere" not in licence
    assert "delayed public image" in licence


def test_the_privacy_statement_describes_the_keyed_visitor_id_and_the_gate_as_not_enabled() -> None:
    """MODEL-249b: the visitor id is keyed and daily, and Turnstile is disclosed as off."""
    assert "HMAC-SHA256(VISITOR_HMAC_KEY, IP | UTC day)" in FLAT_PRIVACY
    body = FLAT_PRIVACY.split("## Changes")[0]  # the Changes list keeps 1.3 as history
    assert "unsalted hash of an IP address" not in body
    assert "is replaced before x402" not in body
    assert "Cloudflare Turnstile" in FLAT_PRIVACY
    assert "not yet enabled" in FLAT_PRIVACY
    assert "`HUMAN_GATE_ENABLED`" in FLAT_PRIVACY
    assert "omit the optional `remoteip` parameter" in FLAT_PRIVACY
