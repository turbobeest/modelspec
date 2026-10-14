"""MODEL-393 licence binding through retained, visible HTML links."""

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


def links_recipe():
    # Before html-links exists, exercise the loss of hrefs through the current
    # recipe so the positive cases report a failed verification, not a setup error.
    return NORMALISERS.get("html-links", NORMALISERS["html-default"])


def binding_page(href: str, *, name: str = "Nimbus 3", label: str = "these terms") -> str:
    return f'<main><p>{name} is governed by <a href="{href}">{label}</a>.</p></main>'


def check(tmp_path: Path, page: str, *, terms: str = SENTENCE,
          terms_url: str = TERMS_URL, policy_url: str = POLICY_URL,
          terms_kind: str = "provider_terms"):
    store = CopyStore(tmp_path / "copies")
    terms_ref = store.put(terms.encode())
    policy_ref = store.put(page.encode())
    sources = {
        "terms": Source.model_validate({
            "id": "terms", "url": terms_url, "normaliser": "text-default",
            "kind": terms_kind,
            "cited_regions": [{"id": "page", "locator": {"kind": "page", "value": ""}}],
        }),
        "policy": Source.model_validate({
            "id": "policy", "url": policy_url, "normaliser": links_recipe().name,
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
    return verify.verify(
        claim, verify.StoredRegions(store, sources),
        [verify.LicenceTermsExtractor(templates=(TEMPLATE,))],
        today=date(2026, 10, 14),
    )


def assert_unbound(result):
    assert result.outcome == "mismatch", result
    assert [(diff.field, diff.found) for diff in result.diffs] == [("model", None)]


def test_html_links_preserves_href_and_leaves_html_default_text_unchanged():
    page = binding_page("/legal/terms", label="<strong>these</strong> terms").encode()
    assert normalise_document(page, NORMALISERS["html-default"]).text == (
        "Nimbus 3 is governed by these terms."
    )
    assert normalise_document(page, links_recipe()).text == (
        "Nimbus 3 is governed by [these terms](/legal/terms)."
    )


@pytest.mark.parametrize("href", [
    "/legal/terms", "../legal/terms", "terms", TERMS_URL,
    "//example.test/legal/terms",
])
def test_retained_relative_and_absolute_terms_links_verify(tmp_path, href):
    result = check(tmp_path, binding_page(href))
    assert result.outcome == "verified", result
    assert result.verification.verifier.method == "licence-terms@3"


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


def test_relative_terms_link_uses_the_binding_sources_actual_host(tmp_path):
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


def test_visible_nested_markup_in_a_terms_link_verifies(tmp_path):
    result = check(tmp_path, binding_page("/legal/terms", label="<b>these</b> <em>terms</em>"))
    assert result.outcome == "verified", result


def test_html_links_preserves_terms_anchors_in_table_cells(tmp_path):
    page = (
        '<main><table><tr><th>Model</th><th>Terms</th></tr>'
        '<tr><td>Nimbus 3</td><td><a href="/legal/terms"><b>these</b> terms</a></td></tr>'
        '</table></main>'
    )
    assert normalise_document(page.encode(), NORMALISERS["html-default"]).text == (
        "Model | Terms\nNimbus 3 | these terms"
    )
    assert normalise_document(page.encode(), links_recipe()).text == (
        "Model | Terms\nNimbus 3 | [these terms](/legal/terms)"
    )
    result = check(tmp_path, page)
    assert result.outcome == "verified", result


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
