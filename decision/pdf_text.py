"""The opt-in, versioned PDF text recipe. Original PDF bytes stay in CopyStore."""

from __future__ import annotations

import io
import math

from decision.normalise import UnsupportedContentError


def extract_pdf(body: bytes) -> str:
    try:
        import pypdf
        from pypdf.generic import ContentStream
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

        def image_area(stream, resources, matrix, ancestors):
            if len(ancestors) > 32:
                raise UnsupportedContentError("pdf_form_depth")
            area = 0.0
            stack = []
            for operands, operator in ContentStream(stream, reader).operations:
                if operator == b"q":
                    stack.append(matrix)
                elif operator == b"Q":
                    matrix = stack.pop()
                elif operator == b"cm":
                    values = tuple(float(n) for n in operands)
                    if len(values) != 6 or not all(math.isfinite(n) for n in values):
                        raise UnsupportedContentError("invalid_pdf_transform")
                    matrix = multiply(values, matrix)
                elif operator == b"Tr" and int(operands[0]) in {3, 7}:
                    raise UnsupportedContentError("hidden_pdf_text")
                elif operator == b"INLINE IMAGE":
                    raise UnsupportedContentError("pdf_inline_image")
                elif operator == b"Do":
                    obj = resources["/XObject"][operands[0]].get_object()
                    if obj.get("/Subtype") == "/Image":
                        a, b, c, d, _, _ = matrix
                        # Only small raster decorations are supported. A scan
                        # with visible or hidden text must not supply facts.
                        if math.hypot(a, b) > 16 or math.hypot(c, d) > 16:
                            raise UnsupportedContentError("scanned_pdf")
                        area += abs(a*d - b*c)
                    elif obj.get("/Subtype") == "/Form" and id(obj) not in ancestors:
                        form_matrix = tuple(float(n) for n in obj.get(
                            "/Matrix", (1, 0, 0, 1, 0, 0)))
                        area += image_area(obj, obj.get("/Resources", resources),
                                           multiply(form_matrix, matrix), ancestors | {id(obj)})
                    else:
                        raise UnsupportedContentError("unsupported_pdf_object")
            if stack:
                raise UnsupportedContentError("invalid_pdf_graphics_state")
            return area

        texts = []
        for page in reader.pages:
            area = float(page.mediabox.width * page.mediabox.height)
            raster = image_area(page.get_contents(), page.get("/Resources", {}),
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
