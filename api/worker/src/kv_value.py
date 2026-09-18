"""What a Workers KV read means when the key is not there (MODEL-80, MODEL-69).

Workers KV resolves a missing key to JS `null`. Pyodide converts JS `null` to
`pyodide.ffi.jsnull`, **not** to `None` — only JS `undefined` becomes `None` —
so an `is None` test lets it through, and `str()` of it is the four letters
`jsnull`, which is neither JSON nor absent. #104 found this on the determination
store, where an empty namespace was reported as corrupt data. The access store
(`access_kv.CloudflareKV`) had the same hole and a worse consequence: a
mistyped API key became the stored record `"jsnull"` and crashed the parse
instead of being refused.

One definition, used by both stores at the point a value leaves the binding.
Nothing here imports the Workers runtime unconditionally, so it runs under
CPython and the tests exercise it with a stand-in for the sentinel.
"""

from __future__ import annotations

from typing import Any

try:  # Pyodide's JS `null`. Absent under CPython, where tests stub KV.
    from pyodide.ffi import jsnull as _JSNULL  # type: ignore[import-not-found]
except Exception:  # noqa: BLE001 - optional import; `absent` also checks the type name
    _JSNULL = None

#: Pyodide's proxy type names for JS `null` and `undefined`, matched by name so
#: a stand-in under CPython is recognised the same way the real one is.
_SENTINEL_TYPE_NAMES = ("JsNull", "JsUndefined")


def absent(value: Any) -> bool:
    """Whether a `kv.get()` result means "no such key".

    `None`, Pyodide's `jsnull` (by identity when Pyodide is present, by type
    name otherwise), and an empty or blank string. No writer to either store
    ever writes an empty value, and parsing one proves nothing but that it is
    empty.
    """
    if value is None:
        return True
    if _JSNULL is not None and value is _JSNULL:
        return True
    if type(value).__name__ in _SENTINEL_TYPE_NAMES:
        return True
    return isinstance(value, str) and not value.strip()
