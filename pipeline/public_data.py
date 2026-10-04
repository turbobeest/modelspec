"""Publish frozen pages, public policy and uncached tombstones for withdrawn data."""
import argparse
import gzip
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Deny new exports by default. Class-fit examples use only the frozen image.
KEEP_API = {"build.json", "coverage.json", "rank/profiles.json", "rank/class-fit.json", "feedback/v1.schema.json"}

REMOVED = (
    "/api/index.json", "/api/catalogue.json", "/api/hosts.json",
    "/api/rank/candidates.json", "/api/rank/hardware.json", "/api/rank/rankings.json",
    "/api/policy/catalogue.json", "/api/decision/snapshot.json.gz",
    "/api/decision/vocabulary.json",
)
FAMILIES = ("/api/models/*", "/api/benchmarks/*", "/api/graph/*")
TOMBSTONE_PATH = "/api/removed.json"
TOMBSTONE = {
    "error": "removed",
    "message": "Fresh data is served per request by the API",
    "api": "https://api.modelspec.dev",
}
# Pages does not support 404/410 rewrites. Supported 200 proxies cover even
# family members absent from this checkout, without publishing their data.
REDIRECTS = "".join(f"{path}  {TOMBSTONE_PATH}  200\n" for path in FAMILIES)
HEADERS = (
    "/api/*\n"
    "  Cache-Control: no-store\n"
    "  Access-Control-Allow-Origin: *\n"
    "/api/decision/snapshot.json.gz\n"
    "  Content-Type: application/json\n"
    "  Content-Encoding: gzip\n"
)
PROBES = (
    *REMOVED,
    "/api/models/anthropic/claude-sonnet-4.json",
    "/api/benchmarks/gpqa_diamond.json",
    "/api/graph/nodes.json",
    *(family.replace("*", "model-273-missing/nested.json") for family in FAMILIES),
)


def cache_headers(headers: str) -> str:
    """Apply the split cache policy once, preserving unrelated header rules."""
    headers = headers.replace(HEADERS, "")
    headers = headers.replace("/api/*\n  Access-Control-Allow-Origin: *\n", "")
    # Unversioned PNG filenames may change between deploys too. The live
    # composition alone adds long caching for Vite's content-hashed /assets/.
    headers = headers.replace("Cache-Control: public, max-age=604800",
                              "Cache-Control: public, max-age=300")
    return headers.rstrip("\n") + "\n" + HEADERS


def restrict(tree: Path) -> None:
    """Replace bulk API routes with tombstones and stop caching data responses."""
    api = tree / "api"
    for path in api.rglob("*"):
        if path.is_file() and path.relative_to(api).as_posix() not in KEEP_API:
            path.unlink()
    raw = (json.dumps(TOMBSTONE, separators=(",", ":")) + "\n").encode()
    for route in (*REMOVED, TOMBSTONE_PATH):
        path = tree / route.lstrip("/")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(gzip.compress(raw, mtime=0) if route.endswith(".gz") else raw)
    redirects = tree / "_redirects"
    previous = redirects.read_text(encoding="utf-8") if redirects.exists() else ""
    redirects.write_text(REDIRECTS + previous.replace(REDIRECTS, ""), encoding="utf-8")
    headers = tree / "_headers"
    headers.write_text(cache_headers(headers.read_text(encoding="utf-8")), encoding="utf-8")


def enabled() -> bool:
    """The operator-controlled serving switch, read at the build boundary."""
    import os
    return os.environ.get("DATA_SPLIT_ENABLED") == "true"


def smoke(origin: str, fetch=None) -> list[str]:
    """Reject stale data at bare URLs; accept 404/410 or an uncached tombstone."""
    def get(url):
        request = urllib.request.Request(url, headers={"User-Agent": "modelspec-smoke"})
        try:
            response = urllib.request.urlopen(request, timeout=30)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            return response.code, dict(response.headers.items()), response.read(1024 * 1024)

    fetch = fetch or get
    failed = []
    for path in PROBES:
        try:
            status, headers, body = fetch(origin.rstrip("/") + path)
            if status in (404, 410):
                continue
            if status != 200:
                failed.append(f"{path}: unexpected status {status}")
                continue
            if body.startswith(b"\x1f\x8b"):
                body = gzip.decompress(body)
            if json.loads(body) != TOMBSTONE:
                failed.append(f"{path}: 200 serves withdrawn data instead of the tombstone")
                continue
            headers = {key.lower(): value for key, value in headers.items()}
            if headers.get("cache-control", "").strip().lower() != "no-store":
                failed.append(f"{path}: tombstone must have Cache-Control: no-store")
        except (OSError, ValueError, EOFError):
            # Never print a withdrawn response body or its values into public CI.
            failed.append(f"{path}: request failed or 200 body is not a tombstone")
    return failed


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("smoke",))
    parser.add_argument("--origin", required=True)
    args = parser.parse_args(argv)
    failed = smoke(args.origin)
    for line in failed:
        print(f"::error::{args.origin}{line}", file=sys.stderr)
    if not failed:
        print(f"{args.origin}: withdrawn data routes are absent or uncached tombstones")
    return int(bool(failed))


if __name__ == "__main__":
    raise SystemExit(main())
