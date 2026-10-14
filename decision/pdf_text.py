"""The opt-in, versioned PDF text recipe. Original PDF bytes stay in CopyStore."""

from __future__ import annotations

import io
import math

from decision.normalise import UnsupportedContentError


def extract_pdf(body: bytes) -> str:
    try:
        import pypdf
        from pypdf.generic import ContentStream, DictionaryObject
    except ImportError as exc:
        raise UnsupportedContentError("pdf_extractor_unavailable") from exc
    if pypdf.__version__ != "6.19.0":
        raise UnsupportedContentError("pdf_extractor_version")
    if not body.startswith(b"%PDF-"):
        raise UnsupportedContentError("invalid_pdf")

    def multiply(left, right):
        a, b, c, d, e, f = left
        g, h, i, j, k, offset_y = right
        return (a*g + b*i, a*h + b*j, c*g + d*i, c*h + d*j,
                e*g + f*i + k, e*h + f*j + offset_y)

    try:
        reader = pypdf.PdfReader(io.BytesIO(body), strict=True)
        if reader.is_encrypted:
            raise UnsupportedContentError("encrypted_pdf")
        if not reader.pages:
            raise UnsupportedContentError("empty_pdf")

        def image_area(stream, resources, matrix, ancestors, text_state=None):
            if len(ancestors) > 32:
                raise UnsupportedContentError("pdf_form_depth")
            resources = resources.get_object()
            if resources.get("/Pattern"):
                raise UnsupportedContentError("pdf_pattern")
            for graphics in resources.get("/ExtGState", DictionaryObject()).get_object().values():
                mask = graphics.get_object().get("/SMask")
                if mask is not None and mask != "/None":
                    raise UnsupportedContentError("pdf_graphics_softmask")
            area = 0.0
            stack = []
            font, font_size, horizontal, text_matrix = text_state or (
                None, 0.0, 1.0, (1, 0, 0, 1, 0, 0))
            for operands, operator in ContentStream(stream, reader).operations:
                if operator == b"q":
                    stack.append((matrix, font, font_size, horizontal))
                elif operator == b"Q":
                    matrix, font, font_size, horizontal = stack.pop()
                elif operator == b"cm":
                    values = tuple(float(n) for n in operands)
                    if len(values) != 6 or not all(math.isfinite(n) for n in values):
                        raise UnsupportedContentError("invalid_pdf_transform")
                    matrix = multiply(values, matrix)
                elif operator == b"Tr" and int(operands[0]) in {3, 7}:
                    raise UnsupportedContentError("hidden_pdf_text")
                elif operator == b"BT":
                    text_matrix = (1, 0, 0, 1, 0, 0)
                elif operator == b"Tm":
                    text_matrix = tuple(float(n) for n in operands)
                elif operator == b"Tf":
                    font = resources["/Font"][operands[0]].get_object()
                    font_size = float(operands[1])
                elif operator == b"Tz":
                    horizontal = float(operands[0]) / 100
                elif operator in {b"Tj", b"TJ", b"'", b'"'} and font is not None \
                        and font.get("/Subtype") == "/Type3":
                    scale = (font_size * horizontal, 0, 0, font_size, 0, 0)
                    glyph_matrix = multiply(tuple(float(n) for n in font["/FontMatrix"]),
                                            multiply(scale, multiply(text_matrix, matrix)))
                    # Checking every glyph is conservative: an unused large
                    # bitmap glyph makes this font unsupported too.
                    count = sum(len(item) for item in operands[0]
                                if isinstance(item, (str, bytes))) if operator == b"TJ" \
                        else len(operands[-1])
                    for glyph in font["/CharProcs"].get_object().values():
                        glyph = glyph.get_object()
                        if id(glyph) in ancestors:
                            raise UnsupportedContentError("pdf_font_cycle")
                        area += max(1, count) * image_area(
                            glyph, font.get("/Resources", resources), glyph_matrix,
                            ancestors | {id(glyph)})
                elif operator == b"INLINE IMAGE":
                    raise UnsupportedContentError("pdf_inline_image")
                elif operator == b"Do":
                    obj = resources["/XObject"][operands[0]].get_object()
                    if obj.get("/Subtype") == "/Image":
                        a, b, c, d, _, _ = matrix
                        # Only small raster decorations are supported. A scan
                        # with visible or hidden text must not supply facts.
                        if not all(math.isfinite(n) for n in matrix) \
                                or math.hypot(a, b) > 16 or math.hypot(c, d) > 16:
                            raise UnsupportedContentError("scanned_pdf")
                        area += abs(a*d - b*c)
                    elif obj.get("/Subtype") == "/Form" and id(obj) not in ancestors:
                        form_matrix = tuple(float(n) for n in obj.get(
                            "/Matrix", (1, 0, 0, 1, 0, 0)))
                        area += image_area(obj, obj.get("/Resources", resources),
                                           multiply(form_matrix, matrix), ancestors | {id(obj)},
                                           (font, font_size, horizontal, text_matrix))
                    else:
                        raise UnsupportedContentError("unsupported_pdf_object")
            if stack:
                raise UnsupportedContentError("invalid_pdf_graphics_state")
            return area

        texts = []
        for page in reader.pages:
            if any(annot.get_object().get("/AP") for annot in page.get("/Annots", [])):
                raise UnsupportedContentError("pdf_annotation_appearance")
            area = float(page.mediabox.width * page.mediabox.height)
            raster = image_area(page.get_contents(), page.get("/Resources", DictionaryObject()),
                                (1, 0, 0, 1, 0, 0), set())
            if area <= 0 or raster >= area * 0.01:
                raise UnsupportedContentError("scanned_pdf")
            text = page.extract_text(extraction_mode="layout", layout_mode_space_vertically=False,
                                     layout_mode_scale_weight=1.0, layout_mode_strip_rotated=False)
            if not text or not any(char.isalnum() for char in text):
                raise UnsupportedContentError("image_only_pdf")
            texts.append(text)
        return "\n".join(texts)
    except UnsupportedContentError:
        raise
    except Exception as exc:
        # Parsing arbitrary source bytes is the boundary. A parser error never
        # falls back to accepting a partial or decoded PDF as source text.
        raise UnsupportedContentError("invalid_pdf") from exc
