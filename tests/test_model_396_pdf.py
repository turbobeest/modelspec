"""PDF source verification retains original bytes and rejects unsupported documents."""

import io
from datetime import UTC, datetime

import httpx
import pytest
from pypdf import PdfWriter
from pypdf.generic import (
    ArrayObject,
    DecodedStreamObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    NumberObject,
)

from decision.model import Source
from decision.normalise import (
    NORMALISERS,
    Locator,
    UnsupportedContentError,
    normalise_document,
    select_region,
)
from decision.sources import CopyStore, Fetcher, fingerprint_bytes, recheck
from decision.verify import StoredRegions

RECIPE = "pdf-pypdf-6.19.0-v1"


def pdf_bytes(*, text="Mistral Small 4", image=None, encrypted=False, blank_page=False,
              form=False, hidden_text=False, pattern=False, annotation=False, softmask=False,
              type3=False):
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    font = DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
    })
    resources = DictionaryObject({
        NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)}),
    })
    content = b""
    if text:
        content += (
            f"BT /F1 12 Tf {3 if hidden_text else 0} Tr 1 0 0 1 50 740 Tm ({text}) Tj ET\n"
        ).encode()
    if image:
        raster = DecodedStreamObject()
        raster.set_data(b"\xff\xff\xff")
        raster.update({
            NameObject("/Type"): NameObject("/XObject"),
            NameObject("/Subtype"): NameObject("/Image"),
            NameObject("/Width"): NumberObject(1),
            NameObject("/Height"): NumberObject(1),
            NameObject("/ColorSpace"): NameObject("/DeviceRGB"),
            NameObject("/BitsPerComponent"): NumberObject(8),
        })
        objects = DictionaryObject({NameObject("/Scan"): writer._add_object(raster)})
        width, height = image
        placement = f"q {width} 0 0 {height} 0 0 cm /Scan Do Q\n".encode()
        if type3:
            glyph = DecodedStreamObject()
            glyph.set_data(b"612 0 d0\n" + placement)
            bitmap_font = DictionaryObject({
                NameObject("/Type"): NameObject("/Font"),
                NameObject("/Subtype"): NameObject("/Type3"),
                NameObject("/FontBBox"): ArrayObject([FloatObject(n) for n in (0, 0, 612, 792)]),
                NameObject("/FontMatrix"): ArrayObject([
                    FloatObject(n) for n in (1, 0, 0, 1, 0, 0)
                ]),
                NameObject("/CharProcs"): DictionaryObject({
                    NameObject("/A"): writer._add_object(glyph),
                }),
                NameObject("/Encoding"): DictionaryObject({NameObject("/Differences"): ArrayObject(
                    [NumberObject(65), NameObject("/A")],
                )}),
                NameObject("/FirstChar"): NumberObject(65),
                NameObject("/LastChar"): NumberObject(65),
                NameObject("/Widths"): ArrayObject([NumberObject(612)]),
                NameObject("/Resources"): DictionaryObject({NameObject("/XObject"): objects}),
            })
            resources["/Font"][NameObject("/Fg")] = writer._add_object(bitmap_font)
            objects = DictionaryObject()
            placement = b"BT /Fg 1 Tf 1 0 0 1 50 700 Tm (A) Tj ET\n"
        elif annotation or softmask:
            appearance = DecodedStreamObject()
            appearance.set_data(placement)
            appearance.update({
                NameObject("/Type"): NameObject("/XObject"),
                NameObject("/Subtype"): NameObject("/Form"),
                NameObject("/BBox"): ArrayObject([FloatObject(n) for n in (0, 0, 612, 792)]),
                NameObject("/Resources"): DictionaryObject({NameObject("/XObject"): objects}),
            })
            ref = writer._add_object(appearance)
            if annotation:
                stamp = DictionaryObject({
                    NameObject("/Type"): NameObject("/Annot"),
                    NameObject("/Subtype"): NameObject("/Stamp"),
                    NameObject("/Rect"): ArrayObject([FloatObject(n) for n in (0, 0, 612, 792)]),
                    NameObject("/AP"): DictionaryObject({NameObject("/N"): ref}),
                })
                page[NameObject("/Annots")] = ArrayObject([writer._add_object(stamp)])
                placement = b""
            else:
                mask = DictionaryObject({NameObject("/S"): NameObject("/Luminosity"),
                                         NameObject("/G"): ref})
                graphics = DictionaryObject({NameObject("/SMask"): mask})
                resources[NameObject("/ExtGState")] = DictionaryObject({
                    NameObject("/GS"): writer._add_object(graphics),
                })
                placement = b"/GS gs 0 0 612 792 re f\n"
            objects = DictionaryObject()
        elif pattern:
            tile = DecodedStreamObject()
            tile.set_data(placement)
            tile.update({
                NameObject("/Type"): NameObject("/Pattern"),
                NameObject("/PatternType"): NumberObject(1),
                NameObject("/PaintType"): NumberObject(1),
                NameObject("/TilingType"): NumberObject(1),
                NameObject("/BBox"): ArrayObject([FloatObject(n) for n in (0, 0, 612, 792)]),
                NameObject("/XStep"): NumberObject(612),
                NameObject("/YStep"): NumberObject(792),
                NameObject("/Resources"): DictionaryObject({NameObject("/XObject"): objects}),
            })
            resources[NameObject("/Pattern")] = DictionaryObject({
                NameObject("/P"): writer._add_object(tile),
            })
            objects = DictionaryObject()
            placement = b"/Pattern cs /P scn 0 0 612 792 re f\n"
        elif form:
            container = DecodedStreamObject()
            container.set_data(placement)
            container.update({
                NameObject("/Type"): NameObject("/XObject"),
                NameObject("/Subtype"): NameObject("/Form"),
                NameObject("/BBox"): ArrayObject([FloatObject(n) for n in (0, 0, 612, 792)]),
                NameObject("/Resources"): DictionaryObject({NameObject("/XObject"): objects}),
            })
            objects = DictionaryObject({NameObject("/Container"): writer._add_object(container)})
            placement = b"/Container Do\n"
        resources[NameObject("/XObject")] = objects
        content += placement
    stream = DecodedStreamObject()
    stream.set_data(content)
    page[NameObject("/Resources")] = resources
    page[NameObject("/Contents")] = writer._add_object(stream)
    if blank_page:
        writer.add_blank_page(width=612, height=792)
    if encrypted:
        writer.encrypt("")
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def source(**changes):
    return Source.model_validate({
        "id": "technical-pdf", "url": "https://lab.example/technical.pdf",
        "normaliser": RECIPE, "kind": "lab_documentation",
        "cited_regions": [{"id": "page", "locator": {"kind": "page"}}],
        **changes,
    })


def test_pdf_normalization_has_literal_reproducible_text():
    body = pdf_bytes(text="Mistral Small 4 output: 256k tokens")
    for _ in range(2):
        doc = normalise_document(body, NORMALISERS[RECIPE])
        assert doc.text == "Mistral Small 4 output: 256k tokens"
        assert doc.root is None
        assert doc.rules.name == RECIPE


def test_pdf_recheck_and_verifier_use_original_hashed_bytes(tmp_path):
    body = pdf_bytes(text="Mistral Small 4 output: 256k tokens")
    registered = source()
    store = CopyStore(tmp_path)
    client = httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(
        200, content=body, headers={"content-type": "application/pdf"},
    )))
    with client:
        report = recheck([registered], {}, [], fetcher=Fetcher(client), store=store,
                         now=datetime(2026, 10, 14, tzinfo=UTC))
    assert report.skipped == []
    snapshot = report.states[registered.id].snapshot
    assert snapshot is not None
    assert snapshot.copy_ref == fingerprint_bytes(body)
    assert store.get(snapshot.copy_ref) == body
    assert StoredRegions(store, {registered.id: registered}).text(
        registered.id, snapshot.copy_ref, "page",
    ) == "Mistral Small 4 output: 256k tokens"


def test_pdf_recheck_detects_changed_text(tmp_path):
    registered = source(fetch="http")
    body = pdf_bytes(text="Mistral Small 4 output: 256k tokens")
    client = httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(
        200, content=body, headers={"content-type": "application/pdf"},
    )))
    with client:
        fetcher = Fetcher(client, min_host_interval=0)
        store = CopyStore(tmp_path)
        now = datetime(2026, 10, 14, tzinfo=UTC)
        initial = recheck([registered], {}, [], fetcher=fetcher, store=store, now=now)
        unchanged = recheck([registered], initial.states, [], fetcher=fetcher, store=store, now=now)
        assert unchanged.regions[0].status == "unchanged"
        body = pdf_bytes(text="Mistral Small 4 output: 128k tokens")
        changed = recheck([registered], initial.states, [], fetcher=fetcher, store=store, now=now)
        assert changed.regions[0].status == "changed"
        assert changed.states[registered.id].snapshot.copy_ref == fingerprint_bytes(body)


@pytest.mark.parametrize("kwargs", [
    {"encrypted": True},
    {"text": ""},
    {"text": "", "image": (612, 792)},
    {"image": (612, 792)},
    {"image": (612, 792), "form": True},
    {"hidden_text": True},
    {"blank_page": True},
])
def test_unsupported_pdf_fails_closed(kwargs):
    with pytest.raises(UnsupportedContentError):
        normalise_document(pdf_bytes(**kwargs), NORMALISERS[RECIPE])


def test_small_checkbox_images_are_supported():
    assert normalise_document(pdf_bytes(image=(10, 8)), NORMALISERS[RECIPE]).text == (
        "Mistral Small 4"
    )


@pytest.mark.parametrize("body", [b"%PDF-1.7 malformed", b"<p>256k tokens</p>", b""])
def test_pdf_recipe_does_not_decode_non_pdf_or_malformed_input(body):
    with pytest.raises(UnsupportedContentError):
        normalise_document(body, NORMALISERS[RECIPE])


@pytest.mark.parametrize("recipe", ["html-default", "text-default", "json-default"])
def test_pdf_remains_opt_in(recipe):
    with pytest.raises(UnsupportedContentError, match="pdf"):
        normalise_document(pdf_bytes(), NORMALISERS[recipe])


@pytest.mark.parametrize("kind,value", [("css", "table"), ("heading", "Properties"),
                                        ("table", "0")])
def test_pdf_source_rejects_html_locators(kind, value):
    with pytest.raises(ValueError, match="only page locators"):
        source(cited_regions=[{"id": "bad", "locator": {"kind": kind, "value": value}}])


def test_pdf_supports_existing_exact_excerpt_locator():
    doc = normalise_document(pdf_bytes(text="Mistral Small 4 output: 256k tokens"),
                             NORMALISERS[RECIPE])
    assert select_region(doc, Locator("page", "::excerpt=output: 256k tokens")) == (
        "output: 256k tokens"
    )


def test_pdf_extractor_version_mismatch_fails_closed(monkeypatch):
    import pypdf

    monkeypatch.setattr(pypdf, "__version__", "0.0.0")
    with pytest.raises(UnsupportedContentError, match="pdf_extractor_version"):
        normalise_document(pdf_bytes(), NORMALISERS[RECIPE])


def test_scan_painted_through_pattern_cannot_supply_text_overlay():
    with pytest.raises(UnsupportedContentError):
        normalise_document(pdf_bytes(image=(612, 792), pattern=True), NORMALISERS[RECIPE])


@pytest.mark.parametrize("container", ["annotation", "softmask"])
def test_scan_in_unsupported_rendering_container_fails_closed(container):
    with pytest.raises(UnsupportedContentError):
        normalise_document(pdf_bytes(image=(612, 792), **{container: True}), NORMALISERS[RECIPE])


def test_type3_font_cannot_paint_scan_behind_extractable_text():
    with pytest.raises(UnsupportedContentError):
        normalise_document(pdf_bytes(image=(612, 792), type3=True), NORMALISERS[RECIPE])


def test_small_type3_bitmap_glyph_is_supported():
    assert normalise_document(pdf_bytes(image=(10, 8), type3=True), NORMALISERS[RECIPE]).text == (
        "Mistral Small 4\nA"
    )
