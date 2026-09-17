"""Fetch the licence document each Hugging Face repository ships, and name it.

The metadata tag on a Hub repo is a dropdown value its uploader picked. A
LICENSE file in the repo is the document the weights are distributed under.
This fetches the second and identifies it from verbatim title text, so a
disagreement between the two is visible rather than assumed away.

It was written to settle one question and the answer was a negative. On
2026-09-17 it was run over the 27 repositories whose card is typed
`apache-2.0` or `mit` while the Hub declares `cc-by-nc-4.0` or
`cc-by-nc-sa-4.0`, and not one of them ships a LICENSE, LICENCE, COPYING or
NOTICE file. None sets `license_name` or `license_link` either. So the README
is the only licence document at the distribution point, and a correction to a
card's `license_type` has to rest on README body prose naming the licence in
words, independently of the frontmatter tag.

It needs the network, so like `verify_quotes.py` it is a script and not a unit
test. Repository ids arrive on stdin, one per line; `_results.json` and every
licence file found are written to the directory named as the first argument:

    python -m scripts.policy.distribution_licence evidence/ < repos.txt

Rerun it when a repository may have gained a licence file. `licence_files`
empty on every row is the finding above, restated against today's Hub.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

API = "https://huggingface.co/api/models/{repo}"
RAW = "https://huggingface.co/{repo}/resolve/main/{path}"
UA = "modelspec-licence-audit"

#: Verbatim title text from each licence's own legal code. Most specific
#: first: every match is recorded, so an ambiguous file shows as ambiguous
#: rather than silently taking the first hit.
MARKERS: list[tuple[str, tuple[str, ...]]] = [
    ("cc-by-nc-sa-4.0", ("Attribution-NonCommercial-ShareAlike 4.0 International",)),
    ("cc-by-nc-nd-4.0", ("Attribution-NonCommercial-NoDerivatives 4.0 International",)),
    ("cc-by-nc-4.0", ("Attribution-NonCommercial 4.0 International",)),
    ("cc-by-sa-4.0", ("Attribution-ShareAlike 4.0 International",)),
    ("cc-by-4.0", ("Attribution 4.0 International",)),
    ("apache-2.0", ("Apache License", "Version 2.0, January 2004")),
    ("mit", ("Permission is hereby granted, free of charge, to any person obtaining a copy",)),
    ("bsd-3-clause", ("Redistributions of source code must retain the above copyright",)),
]

LICENCE_NAMES = ("license", "licence", "copying", "notice")


def get_json(url: str) -> dict:
    """The JSON document at `url`."""
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def get_text(url: str) -> tuple[str | None, str | None]:
    """`(text, None)`, or `(None, reason)` so a file that will not fetch is recorded."""
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.read().decode("utf-8", "replace"), None
    except urllib.error.HTTPError as exc:
        return None, f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        return None, f"{type(exc).__name__}: {exc}"


def identify(text: str) -> list[str]:
    """Every licence whose title text is present, most specific first."""
    return [key for key, marks in MARKERS if all(mark in text for mark in marks)]


def licence_candidates(filenames: list[str]) -> list[str]:
    """The files that could be a licence document. `.py` and `.json` are code."""
    return [
        name
        for name in filenames
        if any(word in name.lower() for word in LICENCE_NAMES)
        and not name.lower().endswith((".py", ".json"))
    ]


def inspect(repo: str, outdir: Path) -> dict:
    """One row: what the Hub declares, every file listed, and every licence read."""
    row: dict = {"hub_repo": repo}
    try:
        meta = get_json(API.format(repo=repo))
    except Exception as exc:  # noqa: BLE001
        row["api_error"] = f"{type(exc).__name__}: {exc}"
        return row

    card_data = meta.get("cardData") or {}
    row["hub_tag"] = card_data.get("license")
    row["hub_license_name"] = card_data.get("license_name")
    row["hub_license_link"] = card_data.get("license_link")
    row["sha"] = meta.get("sha")
    row["lastModified"] = meta.get("lastModified")
    row["gated"] = meta.get("gated")
    row["all_files"] = [s.get("rfilename", "") for s in (meta.get("siblings") or [])]

    row["licence_files"] = []
    for path in licence_candidates(row["all_files"]):
        text, error = get_text(RAW.format(repo=repo, path=path))
        entry: dict = {"path": path, "error": error}
        if text is not None:
            saved_as = f"{repo.replace('/', '__')}__{path.replace('/', '__')}"
            (outdir / saved_as).write_text(text, encoding="utf-8")
            entry |= {
                "bytes": len(text),
                "identified": identify(text),
                "head": text[:400],
                "saved_as": saved_as,
            }
        row["licence_files"].append(entry)
    return row


def main(repos: list[str], outdir: Path) -> int:
    outdir.mkdir(parents=True, exist_ok=True)
    results = []
    for repo in repos:
        row = inspect(repo, outdir)
        results.append(row)
        if "api_error" in row:
            print(f"{repo}: API ERROR {row['api_error']}", flush=True)
            continue
        found = [key for entry in row["licence_files"] for key in entry.get("identified", [])]
        files = [entry["path"] for entry in row["licence_files"]] or "NONE"
        print(
            f"{repo}: tag={row['hub_tag']} files={files} identified={found or 'NONE'}",
            flush=True,
        )

    (outdir / "_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    shipping = [row["hub_repo"] for row in results if row.get("licence_files")]
    print(
        f"\n{len(results)} repositories; "
        f"{len(shipping)} ship a licence file: {shipping or 'none'}"
    )
    return 1 if any("api_error" in row for row in results) else 0


if __name__ == "__main__":
    ids = [line.strip() for line in sys.stdin if line.strip()]
    raise SystemExit(main(ids, Path(sys.argv[1])))
