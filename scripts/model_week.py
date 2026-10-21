"""Draft a Model Week from committed catalogue history, without publishing it."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import subprocess
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlsplit

import yaml

from decision.excluded import excluded_in, excluded_sources, removed_text_hit
from pipeline.load import NOT_CONTENT, split_front_matter

PUBLIC_REPO = Path(__file__).resolve().parents[1]
CATEGORIES = ("Models added", "Benchmark movers", "Price and plan changes", "Lineup changes")
PLAN_FACETS = {
    "availability", "price", "price_cny", "billing_period", "models_covered",
    "families_covered", "surfaces", "allowance.relative_to", "allowance.multiplier",
    "allowance.window", "allowance.tokens",
}
LINEUP_FACETS = {"model.lifecycle", "offering.subscription.models_covered",
                 "offering.subscription.families_covered", "offering.subscription.surfaces"}
DATA_PATHS = ("models", "offerings", "premier/slice-1.yaml")


class DraftError(ValueError):
    """A refusal safe to print even when an input is private."""


def _git(repo: Path, *args: str, data: bytes | None = None) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], input=data, capture_output=True, check=False,
        env={key: value for key, value in os.environ.items() if not key.startswith("GIT_")},
    )
    if result.returncode:
        raise DraftError("Git history could not be read; no draft was written.")
    return result.stdout


@dataclass(frozen=True)
class Revision:
    sha: str
    day: str


def _boundaries(repo: Path, start: date, end: date) -> tuple[Revision, Revision]:
    if _git(repo, "rev-parse", "--is-shallow-repository").strip() != b"false":
        raise DraftError("Complete Git history is required.")
    history = _git(repo, "log", "--first-parent", "--format=%H %ct", "HEAD").decode()

    def before(boundary: date) -> Revision:
        cutoff = datetime.combine(boundary, datetime.min.time(), UTC).timestamp()
        for line in history.splitlines():
            sha, stamp = line.split()
            if int(stamp) < cutoff:
                return Revision(sha, datetime.fromtimestamp(int(stamp), UTC).isoformat())
        raise DraftError("History has no baseline before the requested week.")

    return before(start), before(end)


def _documents(repo: Path, rev: Revision, paths: list[str]) -> dict[str, Any]:
    if not paths:
        return {}
    request = "".join(f"{rev.sha}:{path}\n" for path in paths).encode()
    stream = io.BytesIO(_git(repo, "cat-file", "--batch", data=request))
    result = {}
    for path in paths:
        header = stream.readline().decode().strip()
        if header.endswith(" missing"):
            continue
        _, kind, size = header.split()
        if kind != "blob":
            raise DraftError("Expected catalogue files in history.")
        text = stream.read(int(size)).decode()
        stream.read(1)
        result[path] = (
            split_front_matter(text)[0] if path.endswith(".md") else yaml.safe_load(text)
        )
    return result


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, default=str, allow_nan=False)


def _code(value: object) -> str:
    # Escape Markdown/HTML in catalogue strings; source text cannot inject a new section.
    text = _json(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return "`" + text.replace("`", "&#96;") + "`"


def _link(repo_name: str, rev: Revision, path: str = "") -> str:
    target = f"blob/{rev.sha}/{quote(path, safe='/')}" if path else f"tree/{rev.sha}"
    return f"[{rev.sha[:12]}](https://github.com/turbobeest/{repo_name}/{target})"


@dataclass(frozen=True)
class Record:
    category: str
    label: str
    value: object
    path: str
    urls: tuple[str, ...] = ()
    needs_source: bool = False
    benchmark_id: str | None = None


def _records(documents: dict[str, Any]) -> dict[str, Record]:
    registry = documents.get("registry/sources.yaml", {})
    if not isinstance(registry, dict):
        raise DraftError("Source registry must be a mapping.")
    sources = {
        row["id"]: row["url"]
        for row in registry.get("sources", [])
    }
    records: dict[str, Record] = {}

    def add(key: str, record: Record) -> None:
        if key in records and records[key] != record:
            raise DraftError("Ambiguous catalogue records; no draft was written.")
        records[key] = record

    def facts(rows: list[dict], path: str, owner: str | None = None) -> None:
        for row in rows:
            facet = row["facet"]
            if not (facet.startswith("offering.price.") or facet in LINEUP_FACETS or
                    facet.removeprefix("offering.subscription.") in PLAN_FACETS):
                continue
            urls = tuple(sorted({
                sources[ref["source_id"]] for ref in row.get("sources", [])
                if ref["source_id"] in sources
            }))
            value = {key: row[key] for key in
                     ("state", "value", "effective_from", "effective_until") if key in row}
            subject = (row.get("subject") or {}).get("id") or owner
            if not subject:
                raise DraftError("Fact has no catalogue subject.")
            # Scheduled prices can share a facet, but their effective windows differ.
            window = [row.get("effective_from"), row.get("effective_until")]
            add(_json(["fact", subject, facet, window]), Record(
                "Lineup changes" if facet in LINEUP_FACETS else "Price and plan changes",
                f"{subject} {facet}", value, path, urls, True,
            ))

    for path, doc in sorted(documents.items()):
        if path.startswith("models/"):
            mid = doc["model_id"]
            add(_json(["model", mid]), Record(
                "Models added", mid,
                {"model_id": mid, "display_name": doc.get("display_name", mid),
                 "release_date": doc.get("release_date")}, path,
            ))
            add(_json(["status", mid]), Record(
                "Lineup changes", f"{mid} catalogue status",
                {k: doc[k] for k in ("status", "lifecycle") if k in doc}, path,
            ))
            facts(doc.get("facts") or [], path, mid)
            grouped: dict[str, list[dict]] = {}
            for row in (doc.get("benchmarks") or {}).get("evidence") or []:
                context = {key: row.get(key) for key in (
                    "benchmark_id", "benchmark_version", "model_id_as_evaluated", "unit",
                    "source_url", "source_kind", "measured_by", "configuration", "harness",
                    "effort", "tools",
                )}
                key = _json(["benchmark", mid, context])
                grouped.setdefault(key, []).append(row)
            for key, rows in sorted(grouped.items()):
                # Preserve ties instead of choosing a favourable observation.
                latest = max(str(row.get("evidence_date") or "") for row in rows)
                rows = [row for row in rows if str(row.get("evidence_date") or "") == latest]
                row = rows[0]
                context_id = hashlib.sha256(key.encode()).hexdigest()[:16]
                values = sorted({_json({k: r.get(k) for k in (
                    "score", "unit", "evidence_date", "date_type",
                )}) for r in rows})
                add(key, Record(
                    "Benchmark movers",
                    f"{mid} {row['benchmark_id']} context {context_id}",
                    [json.loads(value) for value in values], path,
                    (row["source_url"],) if row.get("source_url") else (), True,
                    row["benchmark_id"],
                ))
        elif path.startswith("offerings/"):
            for row in doc or []:
                owner = None
                if "plan" in row:
                    owner = f"{row['provider']}/subscription/{row['plan']}"
                elif "model" in row:
                    owner = "/".join(row[k] for k in ("provider", "model", "region", "tier"))
                facts(row.get("facts") or [], path, owner)
        elif path == "premier/slice-1.yaml":
            for row in (doc or {}).get("models", []):
                mid = row["model_id"]
                add(_json(["premier", mid]), Record(
                    "Lineup changes", f"{mid} premier membership", "selected", path,
                ))
    return records


def _allowed(record: Record) -> bool:
    if record.needs_source and not record.urls:
        return False
    if excluded_in([record.label, record.value, record.urls]) or removed_text_hit(record.label):
        return False
    if record.benchmark_id and excluded_sources().benchmark(record.benchmark_id):
        return False
    for url in record.urls:
        parsed = urlsplit(url)
        host = (parsed.hostname or "").lower().rstrip(".")
        if parsed.scheme not in {"http", "https"} or not host or excluded_sources().url(url):
            return False
        if any(host == h or host.endswith("." + h) for h in ("x.com", "twitter.com")):
            return False
    return True


def _citation(record: Record, rev: Revision, repo_name: str) -> str:
    cited = f"{_link(repo_name, rev, record.path)}, catalogue commit {rev.day}"
    for url in record.urls:
        cited += f"; [upstream source]({quote(url, safe=':/?=&%#@+~')})"
    return cited


def _section(repo: Path, start: date, end: date, *, private: bool) -> tuple[str, dict]:
    before, after = _boundaries(repo, start, end)
    paths = _git(repo, "diff", "--name-only", "--no-renames", before.sha, after.sha,
                 "--", *DATA_PATHS).decode().splitlines()
    paths = [p for p in paths if p.endswith((".md", ".yaml", ".yml"))
             and Path(p).name not in NOT_CONTENT]
    if paths:
        paths.append("registry/sources.yaml")
    old = _records(_documents(repo, before, paths))
    new = _records(_documents(repo, after, paths))
    repo_name = "modelspec-data" if private else "modelspec"
    boundary = (f"{_link(repo_name, before)} at {before.day} and "
                f"{_link(repo_name, after)} at {after.day}")
    lines = [
        f"# Model Week DRAFT: {start} through {end - timedelta(days=1)} UTC",
        "", "## PRIVATE" if private else "## PUBLIC", "",
        "Draft for Jamie's review. Publication and any fresh-data publication bundle "
        "require Jamie's approval.",
        "No paid placement. Entries are ordered by catalogue identity.",
        "", f"History endpoints: {boundary}.",
        "This is a net comparison of committed catalogue records across the UTC week. "
        "Commit dates date catalogue observations, not provider announcements. "
        "Records are not independently checked facts.",
        "Benchmark movers are recorded observations in matching measurement contexts, "
        "not a ranking. Configuration changes appear as separate observations.",
        "",
    ]
    changes: dict[str, list[str]] = {category: [] for category in CATEGORIES}
    withheld = 0
    for key in sorted(old.keys() | new.keys()):
        left, right = old.get(key), new.get(key)
        if left and right and left.value == right.value:
            continue
        if left and right and right.category == "Benchmark movers":
            if {row["score"] for row in left.value} == {row["score"] for row in right.value}:
                continue
        record = right or left
        assert record is not None
        if not all(_allowed(r) for r in (left, right) if r):
            withheld += 1
            continue
        category = record.category
        if category == "Models added" and left:
            category = "Lineup changes"
        parts = []
        for side, rev in ((left, before), (right, after)):
            parts.append(
                f"{_code(side.value)}. {_citation(side, rev, repo_name)}" if side else
                f"not recorded. {_link(repo_name, rev)}, catalogue commit {rev.day}"
            )
        changes[category].append(
            f"- {_code(record.label)}: before {parts[0]}; after {parts[1]}."
        )
    for category, entries in changes.items():
        lines.extend([f"### {category}", ""])
        lines.extend(entries or [f"No net recorded changes in this category. {boundary}."])
        lines.append("")
    lines.extend([
        f"Withheld changes with missing or excluded sources: {withheld}. {boundary}.",
        "Coverage: model identities and status, dated benchmark evidence, structured price "
        "and plan facts, and premier membership. Legacy flat scores, free-text plan quotes, "
        "and changes that reverted within the week are outside this comparison.",
        "",
    ])
    return "\n".join(lines), {
        "changes": {category: len(rows) for category, rows in changes.items()},
        "withheld": withheld,
    }


def _output_path(out_dir: Path, public_repo: Path, private_repo: Path | None) -> Path:
    target = out_dir.resolve()
    if target.exists():
        raise DraftError("Output must be a new directory.")
    for root in (public_repo, private_repo, PUBLIC_REPO):
        if root and target.is_relative_to(root.resolve()):
            raise DraftError("Drafts must be outside repository and site trees.")
    for parent in target.parents:
        if (parent / ".git").exists():
            raise DraftError("Drafts must be outside every Git worktree.")
    return target


def generate(week: str, public_repo: Path, out_dir: Path, *,
             private_repo: Path | None = None) -> dict:
    """Write separate drafts outside Git trees; return only category counts.

    ``public_repo`` is the trusted frozen public repository, fixed by the CLI.
    Working-tree edits and MODELSPEC_DATA_DIR never supply draft facts.
    """
    start = date.fromisoformat(week)
    if start.isoformat() != week:
        raise DraftError("Week must be an ISO calendar date.")
    end = start + timedelta(days=7)
    public_repo = public_repo.resolve()
    if private_repo:
        private_repo = private_repo.resolve()
        if private_repo == public_repo or private_repo.is_relative_to(public_repo):
            raise DraftError("Private input must be a separate external checkout.")
    target = _output_path(out_dir, public_repo, private_repo)
    # Render both sections before writing anything; private data never enters public rendering.
    public_text, public_counts = _section(public_repo, start, end, private=False)
    outputs = {"public.md": public_text}
    counts = {"public": public_counts}
    if private_repo:
        private_text, private_counts = _section(private_repo, start, end, private=True)
        outputs["private.md"] = private_text
        counts["private"] = private_counts
    target.mkdir(mode=0o700, parents=True)
    for name, text in outputs.items():
        with (target / name).open("x", encoding="utf-8") as handle:
            os.chmod(handle.name, 0o600)
            handle.write(text)
    return counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--week", required=True, help="First day of the seven-day UTC week")
    parser.add_argument("--private-repo", type=Path, help="Separate local private Git checkout")
    parser.add_argument("--out-dir", type=Path, required=True,
                        help="New directory outside Git trees")
    args = parser.parse_args(argv)
    try:
        counts = generate(args.week, PUBLIC_REPO, args.out_dir, private_repo=args.private_repo)
    except Exception:
        # Parser and Git exceptions can contain private values or paths.
        print("Draft refused: check the date, complete catalogue history, "
              "and external output path.")
        return 2
    print(json.dumps(counts, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
