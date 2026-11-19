"""The credit a source's licence asks for, wherever its data is shown (MODEL-508).

Epoch AI publishes its benchmark data under CC BY 4.0, which asks for credit
where the data is shown. One place holds the wording, the licence link and the
source link, so the add path that writes a row's ``limitations`` and every
surface that shows an Epoch value say the same thing. Detection reads the
source URL of the row, so a new Epoch benchmark needs no list to update.
"""

from __future__ import annotations

from collections.abc import Iterable
from urllib.parse import urlsplit

EPOCH_CREDIT = "Epoch AI data, CC BY 4.0."
EPOCH_LICENCE_URL = "https://creativecommons.org/licenses/by/4.0/"
EPOCH_SOURCE_URL = "https://epoch.ai/benchmarks/use-this-data"


def is_epoch_url(url: object) -> bool:
    """True for a page of Epoch AI's own benchmark data.

    The ``/data/`` archive is not one: it also carries the ``*_external`` files,
    which keep their original licences and are not Epoch's CC BY 4.0 data. A
    row that cites the archive itself is not credited here.
    """
    if not isinstance(url, str):
        return False
    parts = urlsplit(url.strip())
    host = (parts.hostname or "").lower()
    if host != "epoch.ai" and not host.endswith(".epoch.ai"):
        return False
    return not (parts.path or "/").startswith("/data/")


def credit_for(url: object) -> str | None:
    """The credit line a value read from this URL carries, or None."""
    return EPOCH_CREDIT if is_epoch_url(url) else None


def any_epoch(urls: Iterable[object]) -> bool:
    return any(is_epoch_url(url) for url in urls)


def credit_html() -> str:
    """The credit as a sentence with the licence and the source linked."""
    return (
        'Epoch AI data, <a href="' + EPOCH_LICENCE_URL + '" rel="nofollow noopener">CC BY 4.0</a>. '
        'Source: <a href="' + EPOCH_SOURCE_URL + '" rel="nofollow noopener">Epoch AI benchmark data</a>.'
    )


def credit_text() -> str:
    """The credit as plain text with both links, for Markdown and JSON."""
    return f"{EPOCH_CREDIT} Licence: {EPOCH_LICENCE_URL} Source: {EPOCH_SOURCE_URL}"


def credit_record() -> dict[str, str]:
    """The credit as a JSON object, for an export that lists what it credits."""
    return {
        "credit": EPOCH_CREDIT,
        "licence_url": EPOCH_LICENCE_URL,
        "source_url": EPOCH_SOURCE_URL,
    }
