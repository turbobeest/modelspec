"""MODEL-393 reviewed-policy binding and exact licence sentence regressions."""

import hashlib
from datetime import date
from pathlib import Path

import pytest

from decision import verify
from decision.model import Source, SourceRef, TargetRef, VerificationActor
from decision.normalise import NORMALISERS, normalise_document
from decision.sources import CopyStore

TERMS_URL = "https://example.test/legal/terms"
POLICY_URL = "https://example.test/legal/model-policy"
SENTENCE = "Subject to these terms, you may use the Services in your applications."
DIGEST = hashlib.sha256(SENTENCE.casefold().encode()).hexdigest()
TEMPLATE = verify.LicenceSentenceTemplate(
    source_family="synthetic-terms",
    source_url=TERMS_URL,
    region_sha256=DIGEST,
    sentence_sha256=DIGEST,
    facet="licence.commercial_use",
    value="permitted_with_conditions",
    label="Synthetic conditional grant",
)


def binding_page(href: str, *, name: str = "Nimbus 3", label: str = "these terms") -> str:
    return f'<main><p>{name} is governed by <a href="{href}">{label}</a>.</p></main>'


def check(tmp_path: Path, page: str, *, terms: str = SENTENCE,
          terms_url: str = TERMS_URL, policy_url: str = POLICY_URL,
          terms_kind: str = "provider_terms", binding_registered: bool = True):
    store = CopyStore(tmp_path / "copies")
    terms_ref = store.put(terms.encode(), source_url="https://fixture.example/")
    policy_ref = store.put(page.encode(), source_url="https://fixture.example/")
    sources = {
        "terms": Source.model_validate({
            "id": "terms", "url": terms_url, "normaliser": "text-default",
            "kind": terms_kind,
            "cited_regions": [{"id": "page", "locator": {"kind": "page", "value": ""}}],
        }),
        "policy": Source.model_validate({
            "id": "policy", "url": policy_url, "normaliser": "text-default",
            "kind": "provider_documentation",
            "cited_regions": [{"id": "page", "locator": {"kind": "page", "value": ""}}],
        }),
    }
    claim = verify.Claim(
        target=TargetRef(kind="fact", id="lab/nimbus-3#licence.commercial_use"),
        subject="lab/nimbus-3", names=("Nimbus 3",),
        field="licence.commercial_use", value="permitted_with_conditions",
        collector=VerificationActor(agent="fixture", model_family="openai", method="collect"),
        sources=(
            SourceRef(source_id="terms", snapshot_ref=terms_ref, cited_regions=["page"]),
            SourceRef(source_id="policy", snapshot_ref=policy_ref, cited_regions=["page"]),
        ),
    )
    # Only this reviewed fixture is approved. Never hash the current probe or
    # reapprove a changed href, label, table, attribute or source URL.
    reviewed_source = sources["policy"].model_copy(update={"url": POLICY_URL})
    reviewed_ref = store.put(binding_page("/legal/terms").encode(), source_url="https://fixture.example/")
    reviewed_text = verify.StoredRegions(store, {"policy": reviewed_source}).text(
        "policy", reviewed_ref, "page",
    )
    assert reviewed_text is not None
    binding = verify.LicenceBindingTemplate(
        source_url=POLICY_URL,
        region_sha256=hashlib.sha256(reviewed_text.encode()).hexdigest(),
        terms_url=TERMS_URL,
        model_ids=("lab/nimbus-3",),
    )
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(verify, "LICENCE_BINDING_TEMPLATES", (binding,) if binding_registered else ())
        return verify.verify(
            claim, verify.StoredRegions(store, sources),
            [verify.LicenceTermsExtractor(templates=(TEMPLATE,))],
            today=date(2026, 10, 14),
        )


def assert_unbound(result):
    assert result.outcome == "mismatch", result
    assert [(diff.field, diff.found) for diff in result.diffs] == [("model", None)]


def test_policy_recipe_retains_markup_and_leaves_html_default_text_unchanged():
    page = binding_page("/legal/terms", label="<strong>these</strong> terms").encode()
    assert normalise_document(page, NORMALISERS["html-default"]).text == (
        "Nimbus 3 is governed by these terms."
    )
    assert normalise_document(page, NORMALISERS["text-default"]).text == page.decode()


@pytest.mark.parametrize("href", [
    "/legal/terms", "../legal/terms", "terms", TERMS_URL,
    "//example.test/legal/terms",
])
def test_only_the_reviewed_href_spelling_verifies(tmp_path, href):
    result = check(tmp_path, binding_page(href))
    if href == "/legal/terms":
        assert result.outcome == "verified", result
        assert result.verification.verifier.method == "licence-terms@3"
    else:
        assert_unbound(result)


@pytest.mark.parametrize("href", [
    "/legal/terms-other", "/legal/terms/other", "/other/terms",
    "https://other.example.test/legal/terms", "//other.example.test/legal/terms",
    "https://example.test.evil.test/legal/terms",
    "https://other.example.test/legal/terms?next=https://example.test/legal/terms",
    "https://other.example.test/legal/terms#https://example.test/legal/terms",
    "/legal/other?next=https://example.test/legal/terms",
])
def test_near_identical_or_foreign_terms_links_do_not_bind(tmp_path, href):
    assert_unbound(check(tmp_path, binding_page(href)))


@pytest.mark.parametrize("href", [
    TERMS_URL + "-other", TERMS_URL + "/other",
    "https://other.example.test/legal/terms?next=" + TERMS_URL,
])
def test_visible_near_identical_url_does_not_bind_by_substring(tmp_path, href):
    assert_unbound(check(tmp_path, binding_page(href, label=href)))


def test_the_reviewed_binding_source_url_is_required(tmp_path):
    assert_unbound(check(tmp_path, binding_page("/legal/terms"),
                         policy_url="https://other.example.test/legal/model-policy"))


@pytest.mark.parametrize("name", ["Cirrus 4", "Nimbus-3-Pro"])
def test_correct_terms_link_for_another_model_does_not_bind(tmp_path, name):
    assert_unbound(check(tmp_path, binding_page("/legal/terms", name=name)))


def test_frontmatter_licence_link_remains_exclusive(tmp_path):
    page = (
        '<main><p>license: other</p><p>license_link: https://example.test/legal/other</p>'
        '<p>Nimbus 3 is governed by <a href="/legal/terms">these terms</a>.</p></main>'
    )
    assert_unbound(check(tmp_path, page))


@pytest.mark.parametrize("hidden", [
    '<!-- <a href="/legal/terms">these terms</a> -->',
    '<script><a href="/legal/terms">these terms</a></script>',
    '<style><a href="/legal/terms">these terms</a></style>',
    '<template><a href="/legal/terms">these terms</a></template>',
    '<noscript><a href="/legal/terms">these terms</a></noscript>',
    '<nav><a href="/legal/terms">these terms</a></nav>',
    '<span hidden><a href="/legal/terms">these terms</a></span>',
    '<span aria-hidden="true"><a href="/legal/terms">these terms</a></span>',
    '<a hidden href="/legal/terms">these terms</a>',
])
def test_nonrendered_terms_links_do_not_bind(tmp_path, hidden):
    assert_unbound(check(tmp_path, f"<main><p>Nimbus 3 documentation.</p>{hidden}</main>"))


def test_changed_visible_nested_markup_requires_a_policy_review(tmp_path):
    result = check(tmp_path, binding_page("/legal/terms", label="<b>these</b> <em>terms</em>"))
    assert_unbound(result)


def test_unreviewed_table_policy_does_not_bind(tmp_path):
    page = (
        '<main><table><tr><th>Model</th><th>Terms</th></tr>'
        '<tr><td>Nimbus 3</td><td><a href="/legal/terms"><b>these</b> terms</a></td></tr>'
        '</table></main>'
    )
    assert normalise_document(page.encode(), NORMALISERS["html-default"]).text == (
        "Model | Terms\nNimbus 3 | these terms"
    )
    assert normalise_document(page.encode(), NORMALISERS["text-default"]).text == page
    result = check(tmp_path, page)
    assert_unbound(result)


@pytest.mark.parametrize("label", [
    "bad](" + TERMS_URL + ")",
    "[these terms](" + TERMS_URL + ")",
    "bad](/legal/terms)",
    "[these terms](/legal/terms)",
])
def test_markdown_delimiters_in_anchor_label_cannot_replace_its_real_href(tmp_path, label):
    assert_unbound(check(tmp_path, binding_page("/legal/other", label=label)))


@pytest.mark.parametrize("href", [
    "/legal/other) [these terms](" + TERMS_URL + ")",
    "/legal/other[these terms](" + TERMS_URL + ")",
])
def test_markdown_delimiters_in_anchor_href_do_not_create_a_binding(tmp_path, href):
    assert_unbound(check(tmp_path, binding_page(href)))


@pytest.mark.parametrize("href", ["/legal/other(abc)", "/legal/other[abc]"])
def test_ambiguous_href_cannot_bind_the_legal_url_displayed_in_its_label(tmp_path, href):
    assert_unbound(check(tmp_path, binding_page(href, label=TERMS_URL)))


@pytest.mark.parametrize("terms", [
    "Subject to these terms, you may not use the Services in your applications.",
    "Subject to these terms, you may use the Services only in your applications.",
    "Subject to these terms, you may use the Services in your applications?",
    "This is an example. " + SENTENCE,
    SENTENCE + " This grant has been revoked.",
])
def test_near_identical_operative_sentence_or_changed_context_stays_unread(tmp_path, terms):
    result = check(tmp_path, binding_page("/legal/terms"), terms=terms)
    assert result.outcome == "skipped", result
    assert result.verification is None


def test_exact_operative_sentence_from_another_legal_url_stays_unread(tmp_path):
    result = check(tmp_path, binding_page("https://other.example.test/legal/terms"),
                   terms_url="https://other.example.test/legal/terms")
    assert result.outcome == "skipped", result
    assert result.verification is None


def test_exact_operative_sentence_in_documentation_stays_unread(tmp_path):
    result = check(tmp_path, binding_page("/legal/terms"), terms_kind="provider_documentation")
    assert result.outcome == "skipped", result
    assert result.verification is None
