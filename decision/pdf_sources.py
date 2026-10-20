"""Offline PDF subset for reviewed sources. This module is never shipped to the Worker.

Only classic, single-revision PDFs with a flat page tree, base Type1 fonts and
text streams are admitted. Unknown structure is an error, including unused objects.
"""

from __future__ import annotations

import io
import re
import zlib

from decision.normalise import UnsupportedContentError

VERSION = "6.19.0"
RECIPE = f"pdf-pypdf-{VERSION}-v1"
MAX_INPUT = 1_048_576
MAX_PAGES = 16
MAX_OBJECTS = 256
MAX_STREAM = 262_144
MAX_DECODED = 1_048_576
MAX_OPERATIONS = 10_000
MAX_TEXT = 65_536
MAX_READ_BYTES = 16_777_216
MAX_READ_CALLS = 262_144


def refuse(reason: str) -> None:
    raise UnsupportedContentError("pdf_" + reason)


def _check_tokens(data: bytes) -> None:
    """Reject numeric repairs and bound nesting before pypdf parses tokens."""
    token = re.compile(rb"[^ \t\r\n\f\0()<>\[\]/%]+")
    newline = re.compile(rb"[\r\n]")
    position = 0
    stack = []
    while position < len(data):
        char = data[position:position + 1]
        if char in b" \t\r\n\f\0":
            position += 1
        elif char == b"%":
            end = newline.search(data, position)
            position = end.end() if end else len(data)
        elif char == b"(":
            depth = 1
            position += 1
            while position < len(data) and depth:
                char = data[position:position + 1]
                position += 1
                if char == b"\\":
                    position += 1
                elif char == b"(":
                    depth += 1
                elif char == b")":
                    depth -= 1
                if depth > 32:
                    refuse("nesting_limit")
            if depth:
                refuse("string")
        elif char == b"<" and data[position:position + 2] != b"<<":
            end = data.find(b">", position + 1)
            if end < 0 or not re.fullmatch(rb"[0-9a-fA-F \t\r\n\f\0]*",
                                         data[position + 1:end]):
                refuse("hex_string")
            position = end + 1
        elif char in (b"[", b"<"):
            stack.append(b"]" if char == b"[" else b">>")
            position += 1 if char == b"[" else 2
            if len(stack) > 32:
                refuse("nesting_limit")
        elif char in (b"]", b">"):
            closing = b"]" if char == b"]" else b">>"
            if not stack or stack.pop() != closing \
                    or data[position:position + len(closing)] != closing:
                refuse("delimiters")
            position += len(closing)
        elif char == b"/":
            position += 1
            match = token.match(data, position)
            if match is None:
                refuse("name")
            position = match.end()
        else:
            match = token.match(data, position)
            if match is None:
                refuse("token")
            value = match[0]
            if value[:1] in b"+-.0123456789" and (
                len(value) > 32 or not re.fullmatch(rb"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", value)
            ):
                refuse("number")
            position = match.end()
    if stack:
        refuse("delimiters")


def _check_raw_objects(body: bytes, offsets: list[int]) -> None:
    for start, end in zip(offsets, offsets[1:]):
        raw = body[start:end]
        header = re.match(
            rb"\d+ 0 obj\s*<<\s*((?:/(?:Length\s+\d{1,6}|Filter\s+/FlateDecode)\s*)"
            rb"{1,2})>>\s*stream(?:\r\n|\r|\n)", raw,
        )
        if header:
            lengths = re.findall(rb"/Length\s+(\d+)", header[1])
            if len(lengths) != 1 or header[1].count(b"/Filter") > 1:
                refuse("stream")
            length = int(lengths[0])
            if length > MAX_STREAM:
                refuse("stream_limit")
            if not re.fullmatch(rb"(?:\r\n|\r|\n)endstream\s+endobj\s*",
                                raw[header.end() + length:]):
                refuse("stream_length")
            _check_tokens(raw[:header.end()])
        else:
            if re.search(rb"\bstream\b", raw):
                refuse("stream")
            _check_tokens(raw)


class _BudgetStream(io.BytesIO):
    """Bound parser work, including retries and backwards scans."""

    def __init__(self, body: bytes):
        super().__init__(body)
        self.remaining_bytes = MAX_READ_BYTES
        self.remaining_calls = MAX_READ_CALLS

    def _charge(self, data: bytes) -> bytes:
        self.remaining_bytes -= len(data)
        self.remaining_calls -= 1
        if self.remaining_bytes < 0 or self.remaining_calls < 0:
            refuse("read_budget")
        return data

    def read(self, size: int = -1) -> bytes:
        return self._charge(super().read(size))

    def readline(self, size: int = -1) -> bytes:
        return self._charge(super().readline(size))


def _classic_index(body: bytes) -> list[int]:
    """Admit one complete classic xref before pypdf can decode any object stream."""
    if len(body) > MAX_INPUT:
        refuse("input_limit")
    header = re.match(rb"%PDF-1\.[0-7]\r?\n(?:%[^\r\n]*\r?\n)?", body)
    ending = re.search(rb"startxref\r?\n(\d{1,10})\r?\n%%EOF\s*\Z", body)
    if header is None or ending is None:
        refuse("structure")
    start = int(ending[1])
    if not header.end() < start < ending.start():
        refuse("structure")
    section = io.BytesIO(body[start:ending.start()])
    if section.readline() not in (b"xref\n", b"xref\r\n"):
        refuse("xref")
    count_line = re.fullmatch(rb"0 (\d{1,4})\r?\n", section.readline())
    if count_line is None or not 1 < int(count_line[1]) <= MAX_OBJECTS + 1:
        refuse("object_limit")
    count = int(count_line[1])
    if not re.fullmatch(rb"0000000000 65535 f ?\r?\n", section.readline()):
        refuse("xref")
    offsets = []
    for number in range(1, count):
        entry = re.fullmatch(rb"(\d{10}) 00000 n ?\r?\n", section.readline())
        if entry is None:
            refuse("xref")
        offset = int(entry[1])
        if not header.end() <= offset < start or (
            offsets and offset <= offsets[-1]
        ) or not body.startswith(f"{number} 0 obj".encode(), offset):
            refuse("xref")
        offsets.append(offset)
    if section.readline() not in (b"trailer\n", b"trailer\r\n"):
        refuse("xref")
    trailer = section.read()
    fields = re.findall(rb"/(Size|Root|Info)\s+(\d{1,4})(\s+0\s+R)?", trailer)
    if not re.fullmatch(
        rb"\s*<<\s*(?:/(?:Size\s+\d{1,4}|(?:Root|Info)\s+\d{1,4}\s+0\s+R)\s*){2,3}>>\s*",
        trailer,
    ) or len({field[0] for field in fields}) != len(fields) \
            or not {b"Root", b"Size"} <= {field[0] for field in fields} \
            or any(int(value) != count if name == b"Size"
                   else not 1 <= int(value) < count for name, value, _ in fields):
        refuse("trailer")
    if body[header.end():offsets[0]].strip():
        refuse("structure")
    return [*offsets, start]


class _Structure:
    def __init__(self, reader, offsets: list[int], body: bytes):
        from pypdf.generic import IndirectObject

        self.reader = reader
        self.objects = {}
        self.used: set[int] = set()
        self.decoded = 0
        self.operations = 0
        # Read every indexed object, including objects unreachable from the catalog.
        for number, end in enumerate(offsets[1:], 1):
            obj = reader.get_object(IndirectObject(number, 0, reader))
            if body[reader.stream.tell():end].strip() != b"endobj":
                refuse("object_boundary")
            self.objects[number] = obj

    def resolve(self, obj):
        from pypdf.generic import IndirectObject

        if isinstance(obj, IndirectObject):
            if obj.generation != 0 or obj.idnum not in self.objects:
                refuse("reference")
            self.used.add(obj.idnum)
            return self.objects[obj.idnum]
        return obj

    def dictionary(self, obj, required: set[str], optional: set[str] = frozenset()):
        from pypdf.generic import DictionaryObject, NameObject, StreamObject

        obj = self.resolve(obj)
        if not isinstance(obj, DictionaryObject) or isinstance(obj, StreamObject) \
                or any(not isinstance(key, NameObject) for key in obj) \
                or not required <= obj.keys() or not obj.keys() <= required | optional:
            refuse("dictionary")
        return obj

    @staticmethod
    def name(obj, key, allowed):
        from pypdf.generic import NameObject

        value = obj.raw_get(key)
        if not isinstance(value, NameObject) or value not in allowed:
            refuse("name")

    def font(self, obj):
        font = self.dictionary(obj, {"/Type", "/Subtype", "/BaseFont"}, {"/Encoding"})
        fonts = {
            "/Helvetica", "/Helvetica-Bold", "/Helvetica-Oblique", "/Helvetica-BoldOblique",
            "/Courier", "/Courier-Bold", "/Courier-Oblique", "/Courier-BoldOblique",
            "/Times-Roman", "/Times-Bold", "/Times-Italic", "/Times-BoldItalic",
        }
        self.name(font, "/Type", {"/Font"})
        self.name(font, "/Subtype", {"/Type1"})
        self.name(font, "/BaseFont", fonts)
        if "/Encoding" in font:
            self.name(font, "/Encoding", {"/WinAnsiEncoding", "/StandardEncoding"})

    def parsed_operations(self, data):
        from pypdf.generic import read_object

        _check_tokens(data)
        stream = _BudgetStream(data)
        operands = []
        operator_token = re.compile(rb"[a-zA-Z*'\"]+")
        while stream.tell() < len(data):
            start = stream.tell()
            char = stream.read(1)
            if char in b" \t\n\r\f\0":
                continue
            if char == b"%":
                stream.readline()
                continue
            if re.match(rb"[a-zA-Z*'\"]", char):
                operator = operator_token.match(data, start)[0]
                stream.seek(start + len(operator))
                self.operations += 1
                if self.operations > MAX_OPERATIONS:
                    refuse("operation_limit")
                yield operands, operator
                operands = []
            else:
                stream.seek(start)
                operands.append(read_object(stream, self.reader))
                if len(operands) > 6:
                    refuse("operands")
        if operands:
            refuse("trailing_operands")

    def content(self, obj, fonts):
        from pypdf.generic import (
            ArrayObject,
            ContentStream,
            FloatObject,
            NameObject,
            NumberObject,
            StreamObject,
            TextStringObject,
        )

        stream = self.resolve(obj)
        if not isinstance(stream, StreamObject) or not stream.keys() <= {"/Filter"}:
            # pypdf removes /Length when reading a stream.
            refuse("stream")
        encoded = stream._data
        if "/Filter" in stream:
            self.name(stream, "/Filter", {"/FlateDecode"})
            decoder = zlib.decompressobj()
            data = decoder.decompress(encoded, MAX_STREAM + 1)
            if len(data) > MAX_STREAM or decoder.unconsumed_tail:
                refuse("stream_limit")
            if not decoder.eof or decoder.unused_data:
                refuse("compression")
        else:
            data = encoded
        self.decoded += len(data)
        if len(data) > MAX_STREAM or self.decoded > MAX_DECODED:
            refuse("stream_limit")
        content = ContentStream(None, self.reader)
        numbers = (NumberObject, FloatObject)
        arities = {b"BT": 0, b"ET": 0, b"T*": 0, b"Td": 2, b"TL": 1}
        in_text = False
        has_font = False
        operations = []
        for operands, operator in self.parsed_operations(data):
            if operator in arities:
                if len(operands) != arities[operator] or any(
                    not isinstance(value, numbers) or abs(value) > 100_000 for value in operands
                ):
                    refuse("operands")
            elif operator == b"Tf":
                if len(operands) != 2 or not isinstance(operands[0], NameObject) \
                        or operands[0] not in fonts or not isinstance(operands[1], numbers) \
                        or not 0 < operands[1] <= 1000:
                    refuse("font")
                has_font = True
            elif operator == b"Tj":
                if len(operands) != 1 or not isinstance(operands[0], TextStringObject):
                    refuse("text")
            elif operator == b"TJ":
                if len(operands) != 1 or not isinstance(operands[0], ArrayObject) or any(
                    not isinstance(value, (TextStringObject, *numbers)) for value in operands[0]
                ):
                    refuse("text")
            else:
                refuse("operator")
            if operator == b"BT":
                if in_text:
                    refuse("text_state")
                in_text = True
                has_font = False
            elif operator == b"ET":
                if not in_text:
                    refuse("text_state")
                in_text = False
            elif not in_text or operator in (b"Tj", b"TJ") and not has_font:
                refuse("text_state")
            operations.append((operands, operator))
        if in_text:
            refuse("content_balance")
        content.operations = operations
        return content

    def pages(self):
        from pypdf.generic import (
            ArrayObject,
            DictionaryObject,
            FloatObject,
            IndirectObject,
            NameObject,
            NumberObject,
            StreamObject,
            TextStringObject,
        )

        trailer = self.dictionary(self.reader.trailer, {"/Size", "/Root"}, {"/Info"})
        if not isinstance(trailer.raw_get("/Size"), NumberObject) \
                or trailer["/Size"] != len(self.objects) + 1:
            refuse("xref")
        if "/Info" in trailer:
            info = self.dictionary(trailer.raw_get("/Info"), set(), {"/Producer"})
            if any(not isinstance(value, TextStringObject) for value in info.values()):
                refuse("info")
        root = self.dictionary(trailer.raw_get("/Root"), {"/Type", "/Pages"})
        self.name(root, "/Type", {"/Catalog"})
        pages_ref = root.raw_get("/Pages")
        if not isinstance(pages_ref, IndirectObject):
            refuse("page_tree")
        tree = self.dictionary(pages_ref, {"/Type", "/Count", "/Kids"})
        children = tree.raw_get("/Kids")
        self.name(tree, "/Type", {"/Pages"})
        if not isinstance(children, ArrayObject) \
                or not isinstance(tree.raw_get("/Count"), NumberObject) \
                or tree["/Count"] != len(children) or not 1 <= len(children) <= MAX_PAGES:
            refuse("page_limit")
        if any(not isinstance(child, IndirectObject) for child in children) \
                or len({child.idnum for child in children}) != len(children):
            refuse("page_tree")
        pages = []
        for child in children:
            page = self.dictionary(child, {"/Type", "/Parent", "/MediaBox", "/Resources",
                                           "/Contents"})
            box = page.raw_get("/MediaBox")
            self.name(page, "/Type", {"/Page"})
            if page.raw_get("/Parent") != pages_ref \
                    or not isinstance(box, ArrayObject) or len(box) != 4 \
                    or any(not isinstance(n, (NumberObject, FloatObject))
                           or abs(n) > 100_000 for n in box) \
                    or box[0] >= box[2] or box[1] >= box[3]:
                refuse("page")
            resources = self.dictionary(page.raw_get("/Resources"), {"/Font"})
            fonts = self.resolve(resources.raw_get("/Font"))
            # Font resource names vary, but their values have one fixed schema.
            if not isinstance(fonts, DictionaryObject) or isinstance(fonts, StreamObject) \
                    or not fonts or any(
                not isinstance(key, NameObject) for key in fonts
            ):
                refuse("font")
            pages.append((page, fonts))
        return pages


def extract_text(body: bytes) -> str:
    """Return complete text or refuse. No partial result or format fallback."""
    try:
        import pypdf
        from pypdf import PageObject
        from pypdf.generic import NameObject

        if pypdf.__version__ != VERSION:
            refuse("extractor_version")
        offsets = _classic_index(body)
        _check_raw_objects(body, offsets)
        with pypdf.apply_configuration(
            maximum_declared_stream_length=MAX_STREAM,
            zlib_maximum_output_length=MAX_STREAM,
            page_tree_maximum_entries=MAX_PAGES + 1,
            page_tree_maximum_depth=2,
            jbig2dec_binary=None,
        ):
            reader = pypdf.PdfReader(_BudgetStream(body), strict=True)
            if reader.is_encrypted:
                refuse("encrypted")
            structure = _Structure(reader, offsets, body)
            pages = structure.pages()
            output = []
            length = 0
            for raw_page, fonts in pages:
                for font in fonts.values():
                    structure.font(font)
                content = structure.content(raw_page.raw_get("/Contents"), fonts)
                page = PageObject(reader)
                page.update(raw_page)
                page[NameObject("/Contents")] = content
                text = "\n".join(line.rstrip() for line in page.extract_text().splitlines()).strip()
                length += len(text.encode("utf-8"))
                if not text or length > MAX_TEXT:
                    refuse("text_limit")
                output.append(text)
            if structure.used != structure.objects.keys():
                refuse("unowned_object")
            return "\n\n".join(output)
    except UnsupportedContentError:
        raise
    except Exception as exc:
        # pypdf malformed-input failures are not limited to PdfReadError.
        raise UnsupportedContentError("pdf_invalid") from exc
