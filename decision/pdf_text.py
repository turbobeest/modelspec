"""The opt-in, versioned PDF text recipe. Original PDF bytes stay in CopyStore."""

from __future__ import annotations

import io
import math
import re
import sys
from contextlib import contextmanager

from decision.normalise import UnsupportedContentError

# Limits belong to this unpublished recipe rather than library defaults.
MAX_INPUT_BYTES = 25 * 1024 * 1024
MAX_PAGES = 300
MAX_STREAM_BYTES = 4 * 1024 * 1024
MAX_DECODED_BYTES = 25 * 1024 * 1024
MAX_TEXT_BYTES = 5 * 1024 * 1024
MAX_OPERATIONS = 50_000_000


class _OperationLimit(BaseException):
    """Escape pypdf recovery, which can catch ordinary parser exceptions."""


@contextmanager
def _operation_budget():
    remaining = MAX_OPERATIONS
    previous = sys.gettrace()

    def trace(frame, event, arg):
        nonlocal remaining
        module = frame.f_globals.get("__name__", "")
        if module == __name__ or module == "pypdf" or module.startswith("pypdf."):
            if event == "line":
                remaining -= 1
                if remaining < 0:
                    raise _OperationLimit()
            return trace
        return None

    sys.settrace(trace)
    try:
        yield
    finally:
        sys.settrace(previous)


_ACTIVE_NAMES = {b"/JavaScript", b"/JS", b"/Launch", b"/EmbeddedFiles",
                 b"/EmbeddedFile", b"/FileAttachment", b"/RichMedia"}
_PDF_NAME = re.compile(rb"/[^\x00\t\n\f\r ()<>\[\]{}/%]+")
_NAME_ESCAPE = re.compile(rb"#([0-9a-fA-F]{2})")
_DESTINATIONS = re.compile(
    rb"\d+\s+\d+\s+obj\s*<<"
    rb"(?:\s*/[^\s()[\]<>/%]+\s*\[\s*\d+\s+\d+\s+R\s+"
    rb"/(?:XYZ|Fit|FitB|FitH|FitV|FitR|FitBH|FitBV)"
    rb"(?:\s+(?:[+-]?(?:\d+(?:\.\d*)?|\.\d+)|null))*\s*\])*\s*>>\s*"
)


def _reject_active_names(data: bytes) -> None:
    # Also screen raw names: duplicate metadata keys must not hide an action.
    # Streams are screened again after decoding, including object streams.
    for match in _PDF_NAME.finditer(data):
        name = _NAME_ESCAPE.sub(lambda m: bytes([int(m[1], 16)]), match[0])
        if name in _ACTIVE_NAMES or name.startswith(b"/RichMedia"):
            raise UnsupportedContentError("pdf_active_content")


def extract_pdf(body: bytes) -> str:
    if len(body) > MAX_INPUT_BYTES:
        raise UnsupportedContentError("pdf_input_limit")
    if not body.startswith(b"%PDF-"):
        raise UnsupportedContentError("invalid_pdf")
    try:
        import pypdf
    except ImportError as exc:
        raise UnsupportedContentError("pdf_extractor_unavailable") from exc
    if pypdf.__version__ != "6.19.0":
        raise UnsupportedContentError("pdf_extractor_version")
    # 4 MiB holds substantially more than the largest retained technical-PDF
    # stream (181,044 bytes), while bounding every supported decoder explicitly.
    configuration = pypdf.Configuration(
        maximum_declared_stream_length=MAX_STREAM_BYTES,
        array_based_stream_maximum_output_length=MAX_STREAM_BYTES,
        zlib_maximum_output_length=MAX_STREAM_BYTES,
        zlib_maximum_recovery_input_length=MAX_STREAM_BYTES,
        lzw_maximum_output_length=MAX_STREAM_BYTES,
        run_length_maximum_output_length=MAX_STREAM_BYTES,
        jbig2_maximum_output_length=MAX_STREAM_BYTES,
        image_maximum_buffer_size=MAX_STREAM_BYTES,
        flate_maximum_row_length=MAX_STREAM_BYTES,
        xmp_maximum_input_length=MAX_STREAM_BYTES,
        jbig2dec_binary=None,
        disable_legacy_handling=True,
    )
    try:
        with pypdf.apply_configuration(configuration), _operation_budget():
            return _extract_pdf(body, pypdf)
    except _OperationLimit as exc:
        raise UnsupportedContentError("pdf_operation_limit") from exc


def _extract_pdf(body, pypdf):
    from pypdf.generic import (
        ArrayObject,
        ContentStream,
        DictionaryObject,
        IndirectObject,
        NameObject,
        StreamObject,
    )

    def multiply(left, right):
        a, b, c, d, e, f = left
        g, h, i, j, k, offset_y = right
        return (a*g + b*i, a*h + b*j, c*g + d*i, c*h + d*j,
                e*g + f*i + k, e*h + f*j + offset_y)

    try:
        _reject_active_names(body)
        reader = pypdf.PdfReader(io.BytesIO(body), strict=True)
        if reader.is_encrypted:
            raise UnsupportedContentError("encrypted_pdf")
        if not reader.pages:
            raise UnsupportedContentError("empty_pdf")
        if len(reader.pages) > MAX_PAGES:
            raise UnsupportedContentError("pdf_page_limit")

        def check_action(value, *, destination=False):
            value = value.get_object()
            if destination and isinstance(value, ArrayObject):
                return  # An OpenAction destination array navigates internally.
            actions = [value]
            checked = set()
            while actions:
                action = actions.pop().get_object()
                if id(action) in checked:
                    continue
                checked.add(id(action))
                if isinstance(action, ArrayObject):
                    actions.extend(action)
                elif isinstance(action, DictionaryObject) and action.get("/S") == "/GoTo":
                    if "/Next" in action:
                        actions.append(action.raw_get("/Next"))
                else:
                    raise UnsupportedContentError("pdf_active_content")

        # The retained technical PDF has duplicate ordinary destination keys.
        # Accept only that narrow metadata shape after strict parsing fails;
        # a stream or action dictionary must still receive the full inspection.
        root = reader.trailer["/Root"]
        destinations = root.raw_get("/Dests") if "/Dests" in root else None
        skipped = set()
        if isinstance(destinations, IndirectObject):
            try:
                destinations.get_object()
            except pypdf.errors.PdfReadError:
                offset = reader.xref.get(destinations.generation, {}).get(destinations.idnum)
                end = body.find(b"endobj", offset) if offset is not None else -1
                if end < 0 or end - offset > 64 * 1024 \
                        or not _DESTINATIONS.fullmatch(body[offset:end]):
                    raise
                skipped.add((destinations.idnum, destinations.generation))
        pending = [reader.trailer]
        pending.extend(IndirectObject(number, generation, reader)
                       for generation, objects in sorted(reader.xref.items())
                       for number in sorted(objects) if number != 0
                       and (number, generation) not in skipped)
        pending.extend(IndirectObject(number, 0, reader)
                       for number in sorted(reader.xref_objStm)
                       if (number, 0) not in skipped)
        seen = set()
        decoded_bytes = 0
        while pending:
            obj = pending.pop()
            if isinstance(obj, IndirectObject):
                if (obj.idnum, obj.generation) in skipped:
                    continue
                obj = obj.get_object()
            if id(obj) in seen:
                continue
            seen.add(id(obj))
            if isinstance(obj, NameObject):
                _reject_active_names(str(obj).encode())
            if isinstance(obj, StreamObject):
                data = obj.get_data()
                if len(data) > MAX_STREAM_BYTES:
                    raise UnsupportedContentError("pdf_stream_limit")
                decoded_bytes += len(data)
                if decoded_bytes > MAX_DECODED_BYTES:
                    raise UnsupportedContentError("pdf_decoded_limit")
                _reject_active_names(data)
            if isinstance(obj, DictionaryObject):
                for key, value in obj.items():
                    if key == "/OpenAction":
                        check_action(value, destination=True)
                    elif key == "/AA":
                        actions = value.get_object()
                        if not isinstance(actions, DictionaryObject):
                            raise UnsupportedContentError("pdf_active_content")
                        for action in actions.values():
                            check_action(action)
                    pending.append(key)
                    pending.append(value)
            elif isinstance(obj, ArrayObject):
                pending.extend(obj)

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
        text_bytes = 0
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
            text_bytes += len(text.encode("utf-8")) + (1 if texts else 0)
            if text_bytes > MAX_TEXT_BYTES:
                raise UnsupportedContentError("pdf_text_limit")
            texts.append(text)
        return "\n".join(texts)
    except UnsupportedContentError:
        raise
    except pypdf.errors.LimitReachedError as exc:
        raise UnsupportedContentError("pdf_stream_limit") from exc
    except Exception as exc:
        # Parsing arbitrary source bytes is the boundary. A parser error never
        # falls back to accepting a partial or decoded PDF as source text.
        raise UnsupportedContentError("invalid_pdf") from exc
