"""The key-value store the access modules are written against (MODEL-69).

Nothing here knows the name of a Workers KV binding, and nothing here imports
the Workers runtime. The Worker passes `CloudflareKV(env.<WHATEVER>)`; the tests
pass `MemoryKV()`. Both satisfy `AsyncKV`, which is the only thing
`access_keys` and `access_limits` are allowed to assume.

Two properties of Workers KV that the callers above are written around, rather
than surprised by:

* **Eventual consistency.** A value written in one location can take up to a
  minute to be visible in another. The daily counter is therefore a good-faith
  meter, not a ledger: a caller racing itself across colos can overshoot a quota
  slightly. That is an acceptable trade for a free tier and is stated in
  `docs/api-access.md`; a Durable Object is the answer if it ever has to be
  exact, and the interface here is what would be swapped.
* **A 60-second floor on `expirationTtl`.** The burst window is exactly one
  minute, which is the shortest TTL KV will accept.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

#: Workers KV refuses a shorter expiry than this.
MIN_EXPIRATION_TTL = 60


@runtime_checkable
class AsyncKV(Protocol):
    """The three operations the access path needs. Names, not bindings."""

    async def get(self, name: str) -> str | None: ...

    async def put(self, name: str, value: str, *,
                  expiration_ttl: int | None = None) -> None: ...

    async def delete(self, name: str) -> None: ...


class MemoryKV:
    """An in-process store for tests and local development.

    Expiry is recorded but not enforced: every test that cares about a window
    boundary moves the clock instead, which is the thing actually under test.
    """

    def __init__(self, initial: dict[str, str] | None = None) -> None:
        self.data: dict[str, str] = dict(initial or {})
        self.ttl: dict[str, int] = {}
        #: Every operation, in order, for tests that assert the sandbox never
        #: reached the store at all.
        self.calls: list[tuple[str, str]] = []

    async def get(self, name: str) -> str | None:
        self.calls.append(("get", name))
        return self.data.get(name)

    async def put(self, name: str, value: str, *,
                  expiration_ttl: int | None = None) -> None:
        self.calls.append(("put", name))
        self.data[name] = value
        if expiration_ttl is not None:
            self.ttl[name] = expiration_ttl

    async def delete(self, name: str) -> None:
        self.calls.append(("delete", name))
        self.data.pop(name, None)
        self.ttl.pop(name, None)


class CloudflareKV:
    """Adapter over a Workers KV binding.

    Constructed as `CloudflareKV(env.API_KEYS)` — or whatever the binding ends
    up being called. Holding the binding rather than reading a name off `env`
    is what lets this ship before the Worker's configuration exists.
    """

    def __init__(self, binding: Any) -> None:
        self._binding = binding

    async def get(self, name: str) -> str | None:
        value = await self._binding.get(name)
        return None if value is None else str(value)

    async def put(self, name: str, value: str, *,
                  expiration_ttl: int | None = None) -> None:
        if expiration_ttl is None:
            await self._binding.put(name, value)
            return
        await self._binding.put(name, value, _options(expirationTtl=max(
            MIN_EXPIRATION_TTL, int(expiration_ttl))))

    async def delete(self, name: str) -> None:
        await self._binding.delete(name)


def _options(**fields: Any) -> Any:
    """A JS options object in the isolate, a plain dict under CPython."""
    try:  # pragma: no cover - the isolate's half is not exercised by CPython
        from js import Object  # type: ignore[import-not-found]
        from pyodide.ffi import to_js  # type: ignore[import-not-found]
    except ImportError:
        return dict(fields)
    return to_js(fields, dict_converter=Object.fromEntries)  # pragma: no cover
