"""MODEL-393-r2 exact retained-policy binding, including review probes."""

import hashlib
import json
from datetime import date

import pytest

from decision import verify
from decision.model import Source, SourceRef, TargetRef, VerificationActor
from decision.normalise import NORMALISERS
from decision.sources import CopyStore

TERMS_URL = "https://example.test/legal/terms"
POLICY_URL = "https://example.test/legal/model-policy"
SENTENCE = "Subject to these terms, you may use the Services in your applications."
SENTENCE_HASH = hashlib.sha256(SENTENCE.casefold().encode()).hexdigest()
REVIEWED_POLICY = (
    '<main><p>Nimbus 3 is governed by <a href="/legal/terms">these terms</a>.</p>'
    '<p>Nimbus 4 is governed by <a href="/legal/terms">these terms</a>.</p></main>'
)


@pytest.fixture
def retained_policy(tmp_path, monkeypatch):
    store = CopyStore(tmp_path / "copies")
    # During the red run, retain the recipe the rejected link path used. The
    # replacement hashes retained HTML through text-default, including hrefs,
    # attributes and base tags. The reviewed fixture is never a mutated probe.
    exact_binding = getattr(verify, "LicenceBindingTemplate", None)
    normaliser = "text-default" if exact_binding else (
        "html-links" if "html-links" in NORMALISERS else "html-default"
    )
    source = Source.model_validate({
        "id": "policy", "url": POLICY_URL, "normaliser": normaliser,
        "kind": "provider_documentation",
        "cited_regions": [{"id": "page", "locator": {"kind": "page", "value": ""}}],
    })
    reviewed_ref = store.put(REVIEWED_POLICY.encode())
    reviewed_region = verify.StoredRegions(store, {"policy": source}).text(
        "policy", reviewed_ref, "page",
    )
    assert reviewed_region is not None
    reviewed_hash = hashlib.sha256(reviewed_region.encode()).hexdigest()
    if exact_binding is not None:
        monkeypatch.setattr(verify, "LICENCE_BINDING_TEMPLATES", (
            exact_binding(
                source_url=POLICY_URL,
                region_sha256=reviewed_hash,
                terms_url=TERMS_URL,
                model_ids=("lab/nimbus-3", "lab/nimbus-4"),
            ),
        ))

    def check(page=REVIEWED_POLICY, *, model_id="lab/nimbus-3", name="Nimbus 3",
              policy_url=POLICY_URL, terms_url=TERMS_URL, reader=None):
        terms_ref = store.put(SENTENCE.encode())
        policy_ref = store.put(page.encode())
        sources = {
            "terms": Source.model_validate({
                "id": "terms", "url": terms_url, "normaliser": "text-default",
                "kind": "provider_terms",
                "cited_regions": [{"id": "page", "locator": {"kind": "page", "value": ""}}],
            }),
            "policy": source.model_copy(update={"url": policy_url}),
        }
        # Regions supplies the source's URL spelling verbatim. Preserve aliases
        # here, including uppercase hosts that HttpUrl otherwise canonicalizes.
        sources["terms"] = sources["terms"].model_copy(update={"url": terms_url})
        claim = verify.Claim(
            target=TargetRef(kind="fact", id=model_id + "#licence.commercial_use"),
            subject=model_id, names=(name,),
            field="licence.commercial_use", value="permitted_with_conditions",
            collector=VerificationActor(agent="fixture", model_family="openai", method="collect"),
            sources=(
                SourceRef(source_id="terms", snapshot_ref=terms_ref, cited_regions=["page"]),
                SourceRef(source_id="policy", snapshot_ref=policy_ref, cited_regions=["page"]),
            ),
        )
        sentence = verify.LicenceSentenceTemplate(
            source_family="synthetic-terms", source_url=terms_url,
            region_sha256=SENTENCE_HASH, sentence_sha256=SENTENCE_HASH,
            facet="licence.commercial_use", value="permitted_with_conditions",
            label="Synthetic conditional grant",
        )
        return verify.verify(
            claim, verify.StoredRegions(store, sources),
            [reader or verify.LicenceTermsExtractor(templates=(sentence,))],
            today=date(2026, 10, 14),
        )

    return check


def assert_unbound(result):
    assert result.outcome == "mismatch", result
    assert [(diff.field, diff.found) for diff in result.diffs] == [("model", None)]


@pytest.mark.parametrize(("model_id", "name"), [
    ("lab/nimbus-3", "Nimbus 3"),
    ("lab/nimbus-4", "Nimbus 4"),
])
def test_reviewed_region_binds_only_its_explicit_ids(retained_policy, model_id, name):
    result = retained_policy(model_id=model_id, name=name)
    assert result.outcome == "verified", result
    assert result.verification.verifier.method == "licence-terms@3"


@pytest.mark.parametrize("page", [
    '<main><table><tr><th>Model</th><th>Terms</th></tr>'
    '<tr><td>Nimbus 3</td><td><a href="/legal/other">other terms</a></td></tr>'
    '<tr><td>Nimbus 4</td><td><a href="/legal/terms">these terms</a></td></tr>'
    '</table></main>',
    '<main><p>Nimbus 3 is listed in this catalogue.</p>'
    '<p>Nimbus 4 is governed by <a href="/legal/terms">these terms</a>.</p></main>',
], ids=["table-sibling-link", "paragraph-sibling-link"])
def test_review_1_sibling_terms_link_never_binds(retained_policy, page):
    assert_unbound(retained_policy(page))


@pytest.mark.parametrize("name", ["Nimbus 3 Ultra", "Nimbus 3.1"])
def test_review_2_longer_sibling_name_never_binds(retained_policy, name):
    page = f'<main><p>{name} is governed by <a href="/legal/terms">these terms</a>.</p></main>'
    assert_unbound(retained_policy(page))


def test_review_2_bare_muse_spark_never_binds_versioned_policy(retained_policy):
    page = (
        '<main><p>Muse Spark 1.1 is governed by '
        '<a href="/legal/terms">these terms</a>.</p></main>'
    )
    assert_unbound(retained_policy(page, model_id="meta/muse-spark", name="Muse Spark"))


@pytest.mark.parametrize("link", [
    '<a style="display:none" href="/legal/terms">these terms</a>',
    '<a style="visibility:hidden" href="/legal/terms">these terms</a>',
    '<div style="display:none"><a href="/legal/terms">these terms</a></div>',
    '<a aria-hidden="TRUE" href="/legal/terms">these terms</a>',
    '<a aria-hidden="true " href="/legal/terms">these terms</a>',
    '<a href="/legal/terms"></a>',
    '<a href="/legal/terms">   </a>',
    '<!-- <a href="/legal/terms">these terms</a> -->',
    '<template><a href="/legal/terms">these terms</a></template>',
    '<a hidden href="/legal/terms">these terms</a>',
    '<a hidden="false" href="/legal/terms">these terms</a>',
    '<a aria-hidden="true" href="/legal/terms">these terms</a>',
], ids=["display-none", "visibility-hidden", "hidden-wrapper", "aria-uppercase",
        "aria-trailing-space", "empty-anchor", "whitespace-anchor", "comment",
        "template", "hidden", "hidden-false", "aria-exact"])
def test_review_3_hidden_styled_or_empty_link_never_binds(retained_policy, link):
    assert_unbound(retained_policy(f"<main><p>Nimbus 3 documentation.</p>{link}</main>"))


@pytest.mark.parametrize(("base", "href"), [
    ("https://evil.test/", "/legal/terms"),
    ("https://evil.test/legal/", "terms"),
], ids=["foreign-base-absolute-path", "foreign-base-directory-relative"])
def test_review_3_foreign_base_never_binds(retained_policy, base, href):
    page = (
        f'<html><head><base href="{base}"></head><body><main>'
        f'<p>Nimbus 3 is governed by <a href="{href}">these terms</a>.</p>'
        '</main></body></html>'
    )
    assert_unbound(retained_policy(page))


@pytest.mark.parametrize("page", [
    REVIEWED_POLICY.replace("governed", "restricted", 1),
    REVIEWED_POLICY.replace("/legal/terms", "/legal/other", 1),
    REVIEWED_POLICY.replace("<main>", '<main style="display:none">'),
    REVIEWED_POLICY + "<p>A later policy notice.</p>",
], ids=["operative-word", "one-href", "style-attribute", "added-context"])
def test_changed_reviewed_region_hash_never_binds(retained_policy, page):
    assert_unbound(retained_policy(page))


@pytest.mark.parametrize(("model_id", "name"), [
    ("lab/unlisted", "Nimbus 3"),
    ("lab/nimbus-3-1", "Nimbus 3.1"),
    ("lab/nimbus-3-1", "Nimbus 3"),
    ("meta/muse-spark", "Muse Spark"),
    ("meta/muse-spark-1-2", "Muse Spark 1.2"),
], ids=["unknown-id", "sibling-version", "sibling-display-alias", "bare-meta", "unlisted-meta-1-2"])
def test_unlisted_canonical_id_never_binds(retained_policy, model_id, name):
    assert_unbound(retained_policy(model_id=model_id, name=name))


def test_changed_policy_source_url_never_binds(retained_policy):
    assert_unbound(retained_policy(policy_url="https://other.example.test/legal/model-policy"))


def test_changed_governing_terms_url_never_binds(retained_policy):
    # The synthetic rights sentence is registered at the changed legal URL too.
    # This isolates the binding registry's governing-terms URL check.
    assert_unbound(retained_policy(terms_url="https://example.test/legal/other"))


@pytest.mark.parametrize("terms_url", [
    TERMS_URL,
    TERMS_URL + "/",
    TERMS_URL + ".txt",
    TERMS_URL + "?v=1",
    TERMS_URL + "#terms",
    TERMS_URL.replace("https://", "http://"),
    TERMS_URL.replace("example.test", "EXAMPLE.TEST"),
    TERMS_URL.replace("example.test", "www.example.test"),
], ids=["canonical", "trailing-slash", "txt-suffix", "query", "fragment",
        "http", "uppercase-host", "www-host"])
@pytest.mark.parametrize("page", [
    f"Nimbus 3 is governed by these terms: {TERMS_URL}",
    f"license: other\nlicense_link: {TERMS_URL}\nNimbus 3 documentation.",
], ids=["page-wide-url", "frontmatter-license-link"])
def test_terms_url_alias_never_bypasses_reviewed_policy_or_id(
    retained_policy, terms_url, page,
):
    reader = verify.LicenceExtractor(
        lambda _prompt: json.dumps({
            "value": "permitted_with_conditions", "clauses": [SENTENCE],
        }),
        agent="fixture-reader", model="fixture", model_family="anthropic",
    )
    # Both policy mutations remain outside the immutable reviewed region, and
    # this canonical id is outside that region's explicit model list as well.
    assert_unbound(retained_policy(
        page, model_id="lab/unlisted", terms_url=terms_url, reader=reader,
    ))
