"""Prepare a gated draft from an already-public release bundle (MODEL-225).

    python -m release_blog.pipeline --signal blog/releases/ID.yaml --out review.json

Inputs are local public files. This command has no private-data credential,
network client, publication switch, or social posting operation. The workflow
opens a draft PR only after this command and its corpus/page gates succeed.
The fresh private-to-public release export remains blocked; see
docs/release-blog-pipeline.md.
"""

from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

from pipeline.blog import Metadata, _post_page, _posts, tag_slug
from pipeline.export import Build
from release_blog.breakdown import build_breakdown, to_bytes
from release_blog.gates import CLAIM, accuracy, guard_output, load_signed, model_rows
from release_blog.model import Breakdown
from release_blog.render import write as write_rendering

RECHECK_DAYS = (1, 7, 30)
COVERAGE_HOURS = 24
FINDINGS = ("claims_vs_evidence", "standing", "template_changes", "cost", "hardware",
            "not_yet_measured")


class ReleaseSignal(BaseModel):
    """An allowlisted public handoff, never a raw private signal or card."""

    model_config = ConfigDict(extra="forbid")
    signal_id: str = Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$")
    model: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*/[a-z0-9][a-z0-9._-]*$")
    announced_at: datetime
    after: str
    before: str | None = None
    accuracy: str
    vocabulary: str | None = None

    @field_validator("announced_at")
    @classmethod
    def _timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("announced_at needs a timezone")
        return value.astimezone(UTC)


@dataclass(frozen=True)
class Draft:
    slug: str
    revision: int
    recheck_day: int | None
    branch: str
    title: str
    body: str
    paths: tuple[str, ...]
    decisions: tuple[str, ...]
    coverage_hours: float
    draft: Literal[True] = True


def _public_path(root: Path, relative: str) -> Path:
    """Keep every handoff read inside the public blog, including symlink targets."""
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or path.parts[:1] != ("blog",):
        raise ValueError("release input must be a public blog path")
    target = root / path
    if not target.resolve().is_relative_to((root / "blog").resolve()):
        raise ValueError("release input must resolve inside the public blog")
    if any(parent.is_symlink() for parent in (target, *target.parents) if parent != root.parent):
        raise ValueError("symlink in public blog input")
    return target


def due_recheck(first_published: date, today: date, last_checked: date) -> int | None:
    """The latest due milestone not covered by the last published snapshot."""
    due = [day for day in RECHECK_DAYS
           if last_checked < first_published + timedelta(days=day) <= today]
    return max(due) if due else None


def _finding(value: Any) -> Any:
    if isinstance(value, dict):
        if "value" in value and "read_date" in value:
            return {key: value.get(key) for key in ("value", "low", "high", "unit")}
        return {key: _finding(item) for key, item in value.items()
                if key not in {"decision", "decisions", "drivers", "record_id", "records",
                               "source_ids", "read_date"}}
    if isinstance(value, list):
        return [_finding(item) for item in value]
    return value


def material_changes(previous: Breakdown, current: Breakdown) -> tuple[str, ...]:
    """Any changed finding is material; provenance/bookkeeping alone is not.

    Numeric tolerance is zero, including P(best). This matches the editorial
    standard's rule that a changed finding gets a revision. Snapshot-seeded
    sampling changes can therefore warrant an update too.
    """
    old = previous.model_dump(mode="json", by_alias=True)
    new = current.model_dump(mode="json", by_alias=True)
    return tuple(key for key in FINDINGS if _finding(old[key]) != _finding(new[key]))


def _platforms(breakdown: Path, folder: Path, slug: str) -> str:
    try:
        module = importlib.import_module("release_blog.platforms")
    except ImportError as exc:
        if exc.name != "release_blog.platforms":
            raise
        return "Skipped: release_blog.platforms unavailable; platform drafts are pending."
    module.generate_from_breakdown(
        breakdown_path=breakdown, post_url=f"https://modelspec.dev/blog/{slug}/",
        output_dir=folder / "social",
    )
    return "Platform drafts generated for manual review and posting."


def prepare_release(
    *, root: Path, signal_path: Path, now: datetime,
    public_keys: Mapping[str, bytes] | None = None,
) -> Draft | None:
    """Generate one append-only revision, or return None if it is not due.

    The caller must supply files already approved for public disclosure.
    The CLI additionally requires all input files to be committed at HEAD.
    No full private Worker snapshot may be supplied here.
    """
    root = root.resolve()
    signal_path = _public_path(root, signal_path.resolve().relative_to(root).as_posix())
    signal = ReleaseSignal.model_validate(yaml.safe_load(signal_path.read_text()))
    if now.tzinfo is None or now < signal.announced_at:
        raise ValueError("run time must be timezone-aware and at or after the announcement")
    after_path = _public_path(root, signal.after)
    before_path = None if signal.before is None else _public_path(root, signal.before)
    report_path = _public_path(root, signal.accuracy)
    vocabulary_path = None if signal.vocabulary is None else _public_path(root, signal.vocabulary)
    after = load_signed(after_path, public_keys=public_keys, include_archive=True)
    if after.as_of is None or after.as_of > now.date():
        raise ValueError("release snapshot needs an as_of date no later than the run")
    report = accuracy(report_path, after.snapshot_id)
    existing = []
    for path in sorted((root / "blog/posts").glob("*/post.yaml")):
        meta = Metadata.model_validate(yaml.safe_load(path.read_text()))
        if meta.model == signal.model:
            existing.append((path, meta))
    if len(existing) > 1:
        raise ValueError("multiple blog posts for the same release model")
    first = None
    latest = None
    day = None
    revision = 1
    first_published = now.date()
    slug = f"{first_published.isoformat()}-{tag_slug(signal.model)}"
    if existing:
        metadata_path, metadata = existing[0]
        if metadata.status != "published" or any(row.published is None for row in metadata.revisions):
            return None
        if not metadata.revisions or metadata.revisions[0].published is None:
            raise ValueError("published release has no first publication date")
        slug = metadata_path.parent.name
        first_published = metadata.revisions[0].published
        revision = metadata.revisions[-1].revision + 1
        first = Breakdown.model_validate_json(
            (metadata_path.parent / "r1/breakdown.json").read_bytes())
        latest = Breakdown.model_validate_json(
            (metadata_path.parent / f"r{revision - 1}/breakdown.json").read_bytes())
        last_checked = latest.generated_from.after.as_of or first_published
        day = due_recheck(first_published, now.date(), max(first_published, last_checked))
        if day is None or after.as_of < first_published + timedelta(days=day):
            return None
        if after.snapshot_id == latest.generated_from.after.snapshot_id:
            return None
        ref = first.generated_from.before
        before_path = (None if ref is None else _public_path(
            root, f"blog/snapshots/{ref.snapshot_id}.json.gz"))
    else:
        metadata = Metadata(schema_version=1, model=signal.model,
                            title="{{model:" + signal.model + "}} release breakdown",
                            status="draft", early_access=None, revisions=[])
    before = None if before_path is None else load_signed(
        before_path, public_keys=public_keys, include_archive=True)
    for path, snapshot in ((after_path, after), (before_path, before)):
        if snapshot is not None and path != root / "blog/snapshots" / f"{snapshot.snapshot_id}.json.gz":
            raise ValueError("public blog snapshot path must name its signed snapshot ID")
    b = build_breakdown(
        model_id=signal.model, after=after, before=before, accuracy=report,
        revision=revision, first_revision=first, first_published=first_published,
        early_access=metadata.early_access,
        vocabulary=None if vocabulary_path is None else vocabulary_path.read_bytes(),
    )
    expected = sorted(row.record_id for row in model_rows(after, signal.model)
                      if row.measured_by == CLAIM)
    if sorted(row.claim.record_id for row in b.claims_vs_evidence.claims) != expected:
        raise ValueError("claims-vs-evidence table is incomplete")
    missing = sorted(row.benchmark for row in b.claims_vs_evidence.claims
                     if row.status == "no_independent_reading_yet")
    if sorted(b.not_yet_measured.claims_without_reading) != missing:
        raise ValueError("missing independent readings must be stated")
    changes = () if latest is None else material_changes(latest, b)
    if latest is not None and not changes:
        return None
    folder = _public_path(root, f"blog/posts/{slug}/r{revision}")
    if folder.exists():
        raise ValueError("refusing to replace an existing release revision")
    # Rendering validates source exclusions, numeric footnotes and tone before a write.
    guard_output(b.sources, to_bytes(b).decode())
    from release_blog.render import render

    render(b)
    folder.mkdir(parents=True)
    breakdown_path = folder / "breakdown.json"
    breakdown_path.write_bytes(to_bytes(b))
    write_rendering(b, folder / "post.md")
    platform_status = _platforms(breakdown_path, folder, slug)
    raw_meta = metadata.model_dump()
    raw_meta["revisions"].append({"revision": revision, "published": None,
                                  "approved_by": None, "approval": None})
    (folder.parent / "post.yaml").write_text(yaml.safe_dump(raw_meta, sort_keys=False))
    coverage_hours = (now - signal.announced_at).total_seconds() / 3600
    decisions = tuple(ref.decision_id for ref in b.decisions)
    timing = "within" if coverage_hours <= COVERAGE_HOURS else "outside"
    body = (
        f"Draft only. Jamie reviews and merges publication separately. Social posting is manual.\n\n"
        f"Signal: `{signal.signal_id}`. Announcement: {signal.announced_at.isoformat()}.\n"
        f"Prepared: {now.isoformat()}, {coverage_hours:.2f} hours after the signal, "
        f"{timing} the {COVERAGE_HOURS}-hour coverage target.\n\n"
        f"check_publishable: pass. Signed snapshots, cited numbers, source exclusions, "
        f"and claims-vs-evidence completeness: pass.\n"
        f"Corpus and page checks must pass before this draft PR is opened.\n\n"
        f"Re-check: {'launch' if day is None else '+' + str(day) + ' days'}. "
        f"Changed sections: {', '.join(changes) or 'initial breakdown'}.\n\n"
        f"Pending\n\n{json.dumps(b.not_yet_measured.model_dump(mode='json'), sort_keys=True, indent=2)}\n\n"
        f"{platform_status}\n\nDecisions\n\n" + "\n".join(f"- `{ref}`" for ref in decisions)
    )
    return Draft(
        slug=slug, revision=revision, recheck_day=day,
        branch=f"blog/{slug}-r{revision}",
        title=f"blog: {b.model.name} {'update ' if day is not None else ''}r{revision}",
        body=body, paths=(f"blog/posts/{slug}",), decisions=decisions,
        coverage_hours=coverage_hours,
    )


def review_draft(
    *, root: Path, proposal: Draft, run_corpus: Callable[[], None],
    open_pr: Callable[[Draft], Any], public_keys: Mapping[str, bytes] | None = None,
) -> Any:
    """Only call the draft transport after real corpus and page checks succeed."""
    run_corpus()
    posts = _posts(root, public_keys=public_keys, preview_slug=proposal.slug)
    if not posts or posts[-1].revision.revision != proposal.revision:
        raise ValueError("prepared revision is absent from the page preview")
    build = Build("release-preview", "release-preview", posts[-1].breakdown.recheck.first_published)
    for post in posts:
        _post_page(post, posts, post.path, build, preview=True)
    return open_pr(proposal)


def _committed_inputs(root: Path, signal: Path) -> None:
    inputs = ReleaseSignal.model_validate(yaml.safe_load(signal.read_text()))
    paths = [signal.relative_to(root).as_posix(), inputs.after, inputs.accuracy,
             *([inputs.before] if inputs.before else []),
             *([inputs.vocabulary] if inputs.vocabulary else [])]
    for relative in paths:
        path = _public_path(root, relative)
        committed = subprocess.run(["git", "show", f"HEAD:{relative}"], cwd=root,
                                   capture_output=True, check=True).stdout
        if committed != path.read_bytes():
            raise ValueError("release inputs must already be committed in the public repository")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--signal", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    signal = root / args.signal
    # A failed or skipped replay cannot leave an earlier success manifest behind.
    args.out.unlink(missing_ok=True)
    try:
        _committed_inputs(root, signal)
        proposal = prepare_release(root=root, signal_path=signal, now=datetime.now(UTC))
        if proposal is None:
            print("No release revision is due.")
            return 0
        def corpus():
            subprocess.run([sys.executable, "-m", "pytest", "-q", "tests/test_corpus.py",
                            "tests/test_blog.py", "tests/test_blog_append_only.py"],
                           cwd=root, check=True)
        def manifest(draft):
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(json.dumps(asdict(draft), sort_keys=True, indent=2) + "\n")
        review_draft(root=root, proposal=proposal, run_corpus=corpus, open_pr=manifest)
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"release pipeline refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
