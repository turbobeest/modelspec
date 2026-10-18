"""Decode JSON containers without holding their complete serialized text."""

from __future__ import annotations

import json
from typing import Any, TextIO

_CHUNK_SIZE = 65536
_WHITESPACE = " \t\r\n"
_VALUE_END = ",]}:" + _WHITESPACE


class JSONStreamReader:
    """Read one value, optionally hashing its exact UTF-8 source as it is consumed."""

    def __init__(self, stream: TextIO, *, initial: str = "", digest: Any = None):
        self._stream = stream
        self._buffer = initial
        self._cursor = 0
        self._hashed = 0
        self._eof = False
        self._decoder = json.JSONDecoder()
        self._keys: dict[str, str] = {}
        self._digest = digest

    def _fill(self, size: int | None = None) -> None:
        self._hash_consumed()
        self._buffer = self._buffer[self._cursor:]
        self._cursor = 0
        self._hashed = 0
        chunk = self._stream.read(_CHUNK_SIZE if size is None else size)
        if not chunk:
            self._eof = True
        self._buffer += chunk

    def _hash_consumed(self) -> None:
        if self._digest is not None:
            for offset in range(self._hashed, self._cursor, 4096):
                self._digest.update(
                    self._buffer[offset:min(offset + 4096, self._cursor)].encode("utf-8"))
        self._hashed = self._cursor

    def _whitespace(self) -> None:
        while True:
            end = self._cursor
            while end < len(self._buffer) and self._buffer[end] in _WHITESPACE:
                end += 1
            self._cursor = end
            if self._cursor < len(self._buffer) or self._eof:
                return
            self._fill()

    def _starts(self, text: str) -> bool:
        return self._buffer.startswith(text, self._cursor)

    def _error(self, message: str) -> json.JSONDecodeError:
        return json.JSONDecodeError(message, self._buffer, self._cursor)

    def _scalar(self) -> Any:
        size = _CHUNK_SIZE
        while True:
            try:
                decoded, end = self._decoder.raw_decode(self._buffer, self._cursor)
            except json.JSONDecodeError:
                pass
            else:
                if ((end < len(self._buffer) and self._buffer[end] in _VALUE_END)
                        or (end == len(self._buffer) and self._eof)):
                    self._cursor = end
                    return decoded
                del decoded
            if self._eof:
                raise self._error("incomplete or invalid JSON value")
            self._fill(size)
            size = min(size * 2, 1024 * 1024)

    def _object(self) -> dict[str, Any]:
        self._cursor += 1
        result = {}
        self._whitespace()
        if self._starts("}"):
            self._cursor += 1
            return result
        while True:
            if not self._starts('"'):
                raise self._error("missing JSON object key")
            key = self._scalar()
            # Match the standard decoder's sharing of dictionary keys.
            key = self._keys.setdefault(key, key)
            self._whitespace()
            if not self._starts(":"):
                raise self._error("missing JSON object key separator")
            self._cursor += 1
            result[key] = self.read_value()
            self._whitespace()
            if self._starts("}"):
                self._cursor += 1
                return result
            if not self._starts(","):
                raise self._error("missing JSON object member separator")
            self._cursor += 1
            self._whitespace()

    def _array(self) -> list[Any]:
        self._cursor += 1
        result = []
        self._whitespace()
        if self._starts("]"):
            self._cursor += 1
            return result
        while True:
            result.append(self.read_value())
            self._whitespace()
            if self._starts("]"):
                self._cursor += 1
                return result
            if not self._starts(","):
                raise self._error("missing JSON array value separator")
            self._cursor += 1

    def read_value(self) -> Any:
        self._whitespace()
        if self._starts("{"):
            return self._object()
        if self._starts("["):
            return self._array()
        return self._scalar()

    def remainder(self) -> str:
        """Read through EOF, including a compressed stream's integrity footer."""
        self._hash_consumed()
        return self._buffer[self._cursor:] + self._stream.read()

    def finish(self) -> None:
        self._whitespace()
        if self._cursor != len(self._buffer):
            raise self._error("extra data after JSON value")
        self._hash_consumed()


def load_json(stream: TextIO) -> Any:
    reader = JSONStreamReader(stream)
    result = reader.read_value()
    reader.finish()
    return result
