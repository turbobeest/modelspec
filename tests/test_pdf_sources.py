"""Synthetic PDFs only. No provider document bytes belong in these tests."""

from __future__ import annotations

import hashlib
import io
import re
import zlib
from dataclasses import replace
from datetime import UTC, date, datetime

import httpx
import pytest
from pypdf import PdfWriter
from pypdf.generic import (
    ArrayObject,
    DecodedStreamObject,
    DictionaryObject,
    EncodedStreamObject,
    NameObject,
    TextStringObject,
)

from decision.normalise import RuleSet, UnsupportedContentError, normalise_document

RECIPE = "pdf-pypdf-6.19.0-v1"
RULES = RuleSet(RECIPE, "pdf")
TEXT = "Example Model\nMaximum output: 256k tokens"
URL = "https://lab.example.test/spec.pdf"


def pdf(*, lines=None, pages=1, mutate=None, compressed=None, operators=b""):
    writer = PdfWriter()
    font = writer._add_object(DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
    }))
    for _ in range(pages):
        page = writer.add_blank_page(width=612, height=792)
        page[NameObject("/Resources")] = DictionaryObject({
            NameObject("/Font"): DictionaryObject({NameObject("/F1"): font}),
        })
        content = b"BT /F1 12 Tf 40 750 Td 14 TL\n"
        for line in TEXT.splitlines() if lines is None else lines:
            escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            content += b"(" + escaped.encode("ascii") + b") Tj T*\n"
        content += b"ET\n" + operators
        if compressed is None:
            stream = DecodedStreamObject()
            stream.set_data(content)
        else:
            stream = EncodedStreamObject()
            stream._data = zlib.compress(compressed)
            stream[NameObject("/Filter")] = NameObject("/FlateDecode")
        page[NameObject("/Contents")] = writer._add_object(stream)
    if mutate:
        mutate(writer)
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def test_pdf_extracts_repeatable_text_and_hash():
    body = pdf()
    first = normalise_document(body, RULES)
    second = normalise_document(body, RULES)
    assert first.text == second.text == TEXT
    assert hashlib.sha256(first.text.encode()).hexdigest() == (
        "0c51eb072183d2c08edaa6874c040b85ddf3c294c4cf978c6ea782b549548cf2"
    )


@pytest.mark.parametrize("body", [b"%PDF-1.7 ...", b"<html>Not a PDF</html>"])
def test_pdf_recipe_refuses_malformed_or_mislabeled_content(body):
    with pytest.raises(UnsupportedContentError, match="pdf"):
        normalise_document(body, RULES)


def test_pdf_refuses_encryption_including_an_empty_password():
    with pytest.raises(UnsupportedContentError, match="pdf"):
        normalise_document(pdf(mutate=lambda writer: writer.encrypt("")), RULES)


@pytest.mark.parametrize("body", [
    lambda: pdf(pages=301),
    lambda: pdf() + b" " * 26_215_076,
    lambda: pdf(compressed=b"\0" * 1_000_000),
    lambda: pdf(compressed=b"\0" * 80_000_000),
    lambda: pdf(operators=b"q Q\n" * 20_000),
    lambda: pdf(lines=["A" * 2_600_000], pages=2),
])
def test_pdf_refuses_production_resource_overruns(body):
    with pytest.raises(UnsupportedContentError, match="pdf"):
        normalise_document(body(), RULES)


@pytest.mark.parametrize("key,value", [
    ("/OpenAction", DictionaryObject({NameObject("/S"): NameObject("/JavaScript"),
                                     NameObject("/JS"): TextStringObject("alert(1)")})),
    ("/OpenAction", ArrayObject([DictionaryObject({
        NameObject("/S"): NameObject("/URI"),
        NameObject("/URI"): TextStringObject("https://example.test"),
    })])),
    ("/Names", DictionaryObject()),
    ("/Metadata", TextStringObject("hidden")),
])
def test_pdf_refuses_unapproved_catalog_structure(key, value):
    def mutate(writer):
        writer._root_object[NameObject(key)] = value
    with pytest.raises(UnsupportedContentError, match="pdf"):
        normalise_document(pdf(mutate=mutate), RULES)


def test_pdf_refuses_unreferenced_embedded_file():
    def mutate(writer):
        payload = DecodedStreamObject()
        payload.set_data(b"EMBEDDED_SECRET_BYTES")
        writer._add_object(DictionaryObject({
            NameObject("/Type"): NameObject("/Filespec"),
            NameObject("/EF"): DictionaryObject({
                NameObject("/F"): writer._add_object(payload),
            }),
        }))
    with pytest.raises(UnsupportedContentError, match="pdf"):
        normalise_document(pdf(mutate=mutate), RULES)


@pytest.mark.parametrize("lines", [[], [""]])
def test_pdf_refuses_blank_pages(lines):
    with pytest.raises(UnsupportedContentError, match="pdf"):
        normalise_document(pdf(lines=lines), RULES)


@pytest.mark.parametrize("recipe", ["text-default", "html-default", "json-default"])
def test_pdf_never_falls_back_to_another_recipe(recipe):
    from decision.normalise import NORMALISERS
    with pytest.raises(UnsupportedContentError, match="pdf"):
        normalise_document(pdf(), NORMALISERS[recipe])


def test_pdf_recheck_hashes_extraction_and_retains_original_only_with_terms_approval(tmp_path):
    from decision.model import CitedRegion, Source
    from decision.sources import CopyStore, Fetcher, recheck

    body = pdf()
    source = Source(id="pdf", url=URL, normaliser=RECIPE,
                    cited_regions=[CitedRegion(id="page", locator={"kind": "page"})])
    store = CopyStore(tmp_path / "copies")
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(
        200, content=body, headers={"content-type": "application/pdf"},
    ))) as client:
        report = recheck([source], {}, [], fetcher=Fetcher(client=client), store=store,
                         now=datetime(2026, 10, 20, tzinfo=UTC))
    # The registry has no affirmative PDF retention decisions yet.
    assert report.states["pdf"].snapshot is None
    assert report.skipped[0].reason == "pdf_retention_not_approved"
    assert not store.has("sha256:" + hashlib.sha256(body).hexdigest())


def approve(monkeypatch, body, *, text=TEXT):
    from decision import pdf_templates
    from decision.normalise import fingerprint
    template = pdf_templates.PdfTemplate(
        source_url=URL, retention_terms_url="https://lab.example.test/reuse",
        copy_ref="sha256:" + hashlib.sha256(body).hexdigest(),
        extraction_ref=fingerprint(text), subject="example/model", model_name="Example Model",
        field="model.max_output_tokens", source_kind="lab_documentation",
        value_line=1, value_pattern=r"Maximum output: (?P<value>\d+k) tokens", unit="tokens",
    )
    monkeypatch.setattr(pdf_templates, "APPROVED_TEMPLATES", (template,))
    return template


def verification(tmp_path, body, *, value=256000, url=URL, normaliser=RECIPE,
                 field="model.max_output_tokens"):
    from decision.model import Source, SourceRef, TargetRef, VerificationActor
    from decision.sources import CopyStore
    from decision.verify import Claim, StoredRegions, verify

    source = Source(id="pdf", url=url, kind="lab_documentation", normaliser=normaliser,
                    cited_regions=[{"id": "page", "locator": {"kind": "page"}}])
    store = CopyStore(tmp_path / "copies")
    ref = store.put(body, source_url=url)
    claim = Claim(
        target=TargetRef(kind="fact", id="example/model#" + field),
        subject="example/model", names=("Example Model",), field=field, value=value,
        unit="tokens", collector=VerificationActor(
            agent="collector", model_family="test", method="collect",
        ),
        sources=(SourceRef(source_id="pdf", snapshot_ref=ref, cited_regions=["page"]),),
    )

    class ForbiddenReader:
        def accepts(self, text):
            pytest.fail("PDF must not dispatch to a generic or LLM reader")

    return verify(claim, StoredRegions(store, {"pdf": source}), [ForbiddenReader()],
                  today=date(2026, 10, 20))


def test_pdf_approved_template_verifies_value_from_the_bound_line(tmp_path, monkeypatch):
    body = pdf()
    approve(monkeypatch, body)
    result = verification(tmp_path, body)
    assert result.outcome == "verified"
    assert result.verification.verifier.method == "pdf-reviewed-template@1"
    assert verification(tmp_path, body, value=8000).outcome == "mismatch"


def test_pdf_recheck_records_both_hashes_for_approved_copy(tmp_path, monkeypatch):
    from decision.model import Source
    from decision.normalise import fingerprint
    from decision.sources import CopyStore, Fetcher, recheck

    body = pdf()
    template = approve(monkeypatch, body)
    source = Source(id="pdf", url=URL, normaliser=RECIPE,
                    cited_regions=[{"id": "page", "locator": {"kind": "page"}}])
    store = CopyStore(tmp_path / "copies")
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(
        200, content=body, headers={"content-type": "application/pdf"},
    ))) as client:
        report = recheck([source], {}, [], fetcher=Fetcher(client=client), store=store,
                         now=datetime(2026, 10, 20, tzinfo=UTC))
    assert not report.skipped
    snapshot = report.states["pdf"].snapshot
    assert snapshot.copy_ref == template.copy_ref
    assert store.get(snapshot.copy_ref) == body
    assert snapshot.page_fingerprint == fingerprint(TEXT)
    assert snapshot.region_fingerprints == {"page": fingerprint(TEXT)}


@pytest.mark.parametrize("binding,value", [
    ("source_url", "https://other.example.test/spec.pdf"),
    ("copy_ref", "sha256:" + "0" * 64),
    ("extraction_ref", "sha256:" + "0" * 64),
    ("subject", "other/model"),
    ("field", "model.context_window"),
    ("source_kind", "lab_announcement"),
    ("value_line", 5),
    ("value_pattern", r"Input limit: (?P<value>\d+k) tokens"),
])
def test_pdf_template_requires_every_binding(tmp_path, monkeypatch, binding, value):
    from decision import pdf_templates
    body = pdf()
    template = approve(monkeypatch, body)
    monkeypatch.setattr(pdf_templates, "APPROVED_TEMPLATES",
                        (replace(template, **{binding: value}),))
    result = verification(tmp_path, body)
    assert result.outcome == "skipped"
    assert result.reason == "pdf_template_not_approved"


@pytest.mark.parametrize("lines", [
    ["Other Model", "Maximum output: 999k tokens", "Example Model", "See the table above"],
    ["Example Model", "See the table below", "Other Model", "Maximum output: 999k tokens"],
    ["Example Model", "Maximum output: 256k tokens", "Other Model", "Maximum output: 999k tokens"],
    ["Example Model", "Maximum output: 256k tokens", "Maximum output: 256k tokens"],
    ["Maximum output: 256k tokens"],
    ["Example Model", "Caption: Other Model", "Model properties",
     "Input type | Maximum size | Output type | Maximum size",
     "Text | 1 token | Text | 999k tokens"],
    ["Example Model", "Maximum input: 256k tokens", "Maximum output: 8k tokens"],
    ["Example Model", "Maximum output: 256k bytes"],
])
def test_pdf_changed_ownership_or_meaning_never_uses_generic_readers(
    tmp_path, monkeypatch, lines,
):
    approve(monkeypatch, pdf())
    assert verification(tmp_path, pdf(lines=lines)).outcome == "skipped"


@pytest.mark.parametrize("normaliser", [RECIPE, "text-default", "html-default"])
def test_pdf_unapproved_copy_cannot_reach_generic_reader(tmp_path, normaliser):
    assert verification(tmp_path, pdf(), normaliser=normaliser).outcome == "skipped"


@pytest.mark.parametrize("url", ["https://x.ai/spec.pdf", "https://docs.x.ai/spec.pdf",
                               "https://perplexity.ai/spec.pdf"])
def test_pdf_cite_only_policy_precedes_template_verification(tmp_path, monkeypatch, url):
    from decision import pdf_templates
    body = pdf()
    template = approve(monkeypatch, body)
    monkeypatch.setattr(pdf_templates, "APPROVED_TEMPLATES", (replace(template, source_url=url),))
    result = verification(tmp_path, body, url=url)
    assert result.outcome == "cited"
    assert result.verification is None


@pytest.mark.parametrize("locator", [
    {"kind": "page", "value": "::excerpt=Maximum output: 256k tokens"},
    {"kind": "table", "value": "0"},
    {"kind": "heading", "value": "Example Model"},
])
def test_pdf_requires_whole_document_locator(locator):
    from decision.model import Source
    with pytest.raises(ValueError, match="whole-document"):
        Source(id="pdf", url=URL, normaliser=RECIPE,
               cited_regions=[{"id": "r1", "locator": locator}])


def test_pdf_version_mismatch_fails_closed(monkeypatch):
    import pypdf
    body = pdf()
    monkeypatch.setattr(pypdf, "__version__", "future")
    with pytest.raises(UnsupportedContentError, match="pdf_extractor_version"):
        normalise_document(body, RULES)


def test_pdf_unknown_recipe_fails_closed():
    with pytest.raises(UnsupportedContentError, match="pdf_recipe"):
        normalise_document(pdf(), replace(RULES, name="pdf-other"))


def test_pdf_accepts_bounded_flate_text():
    content = b"BT /F1 12 Tf 40 750 Td (Example Model) Tj ET"
    assert normalise_document(pdf(compressed=content), RULES).text == "Example Model"


@pytest.mark.parametrize("location", ["catalog", "page", "annotation"])
@pytest.mark.parametrize("action", ["JavaScript", "Launch", "URI", "GoTo"])
def test_pdf_refuses_actions_at_every_location(location, action):
    def mutate(writer):
        value = DictionaryObject({
            NameObject("/S"): NameObject("/" + action),
            NameObject("/URI"): TextStringObject("https://example.test"),
        })
        if location == "catalog":
            writer._root_object[NameObject("/OpenAction")] = ArrayObject([
                writer.pages[0].indirect_reference, NameObject("/Fit"), value,
            ])
        elif location == "page":
            writer.pages[0][NameObject("/AA")] = value
        else:
            writer.pages[0][NameObject("/Annots")] = ArrayObject([DictionaryObject({
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Link"),
                NameObject("/A"): value,
            })])
    with pytest.raises(UnsupportedContentError, match="pdf"):
        normalise_document(pdf(mutate=mutate), RULES)


@pytest.mark.parametrize("entry", [b"/Prev 0", b"/XRefStm 0", b"/#58RefStm 0"])
def test_pdf_rejects_trailer_extensions_before_constructing_parser(monkeypatch, entry):
    import pypdf
    body = pdf().replace(b"trailer\n<<", b"trailer\n<<\n" + entry)

    def forbidden(*args, **kwargs):
        pytest.fail("unapproved trailer reached PdfReader")

    monkeypatch.setattr(pypdf, "PdfReader", forbidden)
    with pytest.raises(UnsupportedContentError, match="pdf"):
        normalise_document(body, RULES)


@pytest.mark.parametrize("location,key,value", [
    ("catalog", "/Type", TextStringObject("/Catalog")),
    ("page", "/Type", TextStringObject("/Page")),
    ("font", "/Subtype", TextStringObject("/Type1")),
    ("font", "/Encoding", TextStringObject("/WinAnsiEncoding")),
])
def test_pdf_refuses_strings_in_name_fields(location, key, value):
    def mutate(writer):
        target = {"catalog": writer._root_object, "page": writer.pages[0],
                  "font": writer.pages[0]["/Resources"]["/Font"]["/F1"]}[location]
        target[NameObject(key)] = value
    with pytest.raises(UnsupportedContentError, match="pdf"):
        normalise_document(pdf(mutate=mutate), RULES)


def test_pdf_refuses_trailing_operands():
    with pytest.raises(UnsupportedContentError, match="pdf_trailing_operands"):
        normalise_document(pdf(operators=b"123"), RULES)


@pytest.mark.parametrize("transform", [b"0 Tz", b"0 0 0 0 0 0 Tm", b"0 0 0 0 0 0 cm"])
def test_pdf_refuses_text_transforms_outside_the_subset(transform):
    data = b"BT /F1 12 Tf 40 750 Td " + transform + b" (Example Model) Tj ET"
    with pytest.raises(UnsupportedContentError, match="pdf"):
        normalise_document(pdf(compressed=data), RULES)


def test_pdf_worker_imports_do_not_load_operator_parser():
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-c",
         "import sys; import decision.model; import decision.normalise; "
         "assert 'pypdf' not in sys.modules; "
         "assert 'decision.pdf_sources' not in sys.modules"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("body", [
    lambda: pdf(compressed=b"BT /F1 12 Tf (A) Tj " + b"T* " * 10_000 + b"ET"),
    lambda: pdf(pages=16, compressed=b"BT /F1 12 Tf (A) Tj ET" + b" " * 70_000),
    lambda: pdf(pages=2, compressed=b"BT /F1 12 Tf (" + b"A" * 40_000 + b") Tj ET"),
    lambda: pdf(compressed=b"BT /F1 12 Tf (A) Tj ET" + b" " * 262_144),
])
def test_pdf_bounds_cumulative_decoding_operations_and_text(body):
    with pytest.raises(UnsupportedContentError, match="pdf_.*limit"):
        normalise_document(body(), RULES)


def test_pdf_does_not_block_an_independent_non_pdf_source(tmp_path):
    from decision.model import Source, SourceRef, TargetRef, VerificationActor
    from decision.sources import CopyStore
    from decision.verify import Claim, StoredRegions, deterministic_extractors, verify

    store = CopyStore(tmp_path / "copies")
    sources = {
        "pdf": Source(id="pdf", url=URL, normaliser=RECIPE,
                      cited_regions=[{"id": "page", "locator": {"kind": "page"}}]),
        "text": Source(id="text", url="https://lab.example.test/spec.txt",
                       normaliser="text-default", kind="lab_documentation",
                       cited_regions=[{"id": "page", "locator": {"kind": "page"}}]),
    }
    refs = (
        SourceRef(source_id="pdf", snapshot_ref=store.put(pdf(), source_url=URL),
                  cited_regions=["page"]),
        SourceRef(source_id="text", snapshot_ref=store.put(
            b"Model: Example Model\nMaximum output tokens: 256000 tokens",
            source_url="https://lab.example.test/spec.txt",
        ), cited_regions=["page"]),
    )
    claim = Claim(
        target=TargetRef(kind="fact", id="example/model#model.max_output_tokens"),
        subject="example/model", names=("Example Model",), field="model.max_output_tokens",
        label="Maximum output tokens", value=256000, unit="tokens",
        collector=VerificationActor(agent="collector", model_family="test", method="collect"),
        sources=refs,
    )
    result = verify(claim, StoredRegions(store, sources), deterministic_extractors(),
                    today=date(2026, 10, 20))
    assert result.outcome == "verified"


@pytest.mark.parametrize("before,after", [
    (b"40 750 Td", b"-- 750 Td"),
    (b"14 TL", b".. TL"),
    (b"/MediaBox [ 0.0", b"/MediaBox [ ---"),
])
def test_pdf_refuses_numeric_repairs(before, after):
    body = pdf()
    changed = body.replace(before, after)
    assert changed != body and len(changed) == len(body)
    with pytest.raises(UnsupportedContentError, match="pdf"):
        normalise_document(changed, RULES)


@pytest.mark.parametrize("negative", [True, False])
def test_pdf_refuses_stream_length_repairs(negative):
    body = pdf()
    match = re.search(rb"/Length (\d+)", body)
    assert match is not None
    value = b"-" + b"0" * (len(match[1]) - 2) + b"1" if negative else (
        str(int(match[1]) + 1).encode()
    )
    changed = body[:match.start(1)] + value + body[match.end(1):]
    assert len(changed) == len(body)
    with pytest.raises(UnsupportedContentError, match="pdf"):
        normalise_document(changed, RULES)


def test_pdf_refuses_numeric_repairs_inside_text_arrays():
    data = b"BT /F1 12 Tf [(Example Model) --] TJ ET"
    with pytest.raises(UnsupportedContentError, match="pdf"):
        normalise_document(pdf(compressed=data), RULES)
