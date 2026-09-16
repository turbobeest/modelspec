"""Refetch every cited document and check the quoted clause is really in it.

This is the guard for a specific, quiet failure: writing a "verbatim" quote that
has been tidied on the way in. Two entries in the first draft of
`licences.py` had a parenthetical silently dropped out of the middle of the
clause. Neither changed what the licence meant, and both would have been
indefensible the first time a customer diffed the quote against the source —
which is precisely what the quote is there to let them do.

It needs the network, so it is not a unit test. Run it when adding or editing a
reading, and whenever a licence may have been rewritten:

    python -m scripts.policy.verify_quotes

An elision is legal, but it has to be marked with `...`; each run-together
segment is checked against the document independently. Exit status is non-zero
if any quote cannot be found.
"""

from __future__ import annotations

import html
import http.cookiejar  # noqa: F401
import re
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.policy.licences import READINGS  # noqa: E402

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def as_text(url: str) -> str:
    """The document at `url` as flat text, or a marker starting `__FAILED__`."""
    headers = {
        "User-Agent": UA,
        # Several of these hosts answer a bare urllib request with a redirect
        # loop or a 403 and serve the document to anything that looks like a
        # browser. Asking for HTML is not a circumvention; it is what the
        # document is published as.
        "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    opener = urllib.request.build_opener(
        urllib.request.HTTPRedirectHandler(), urllib.request.HTTPCookieProcessor()
    )
    try:
        request = urllib.request.Request(url, headers=headers)
        with opener.open(request, timeout=60) as response:
            raw = response.read().decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        return f"__FAILED__ {type(exc).__name__}: {exc}"
    body = re.sub(r"(?s)<(script|style).*?</\1>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body)))


def comparable(text: str) -> str:
    """Lowercase alphanumerics only, so typography is not the thing being tested."""
    for fancy, plain in (("’", "'"), ("“", '"'), ("”", '"'), ("—", "-")):
        text = text.replace(fancy, plain)
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def main() -> int:
    documents: dict[str, str] = {}
    failures = 0
    for key in sorted(READINGS):
        reading = READINGS[key]
        url = reading.source.url
        if url not in documents:
            documents[url] = as_text(url)
        document = documents[url]

        if document.startswith("__FAILED__"):
            print(f"UNREACHABLE  {key:20s} {document[11:70]}")
            failures += 1
            continue

        haystack = comparable(document)
        missing = [
            segment
            for segment in reading.source.quote.split("...")
            if segment.strip() and comparable(segment) not in haystack
        ]
        if missing:
            print(f"NOT FOUND    {key:20s} {url}")
            for segment in missing:
                print(f"               {segment.strip()[:100]}")
            failures += 1
        else:
            print(f"ok           {key:20s}")

    print(f"\n{len(READINGS) - failures}/{len(READINGS)} quotes verified against source")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
