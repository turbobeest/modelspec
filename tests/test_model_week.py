"""The weekly draft's public/private boundary, exercised with real Git history."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
import yaml


def git(root: Path, *args: str, day: str = "2026-10-12T12:00:00Z") -> str:
    result = subprocess.run(
        ["git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false", *args],
        cwd=root, capture_output=True, text=True, check=True,
        env={**os.environ, "GIT_AUTHOR_NAME": "Fixture", "GIT_COMMITTER_NAME": "Fixture",
             "GIT_AUTHOR_EMAIL": "fixture@example.test",
             "GIT_COMMITTER_EMAIL": "fixture@example.test",
             "GIT_AUTHOR_DATE": day, "GIT_COMMITTER_DATE": day},
    )
    return result.stdout.strip()


def write(root: Path, path: str, value: object) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(value)
    target.write_text(f"---\n{text}---\n" if path.endswith(".md") else text)


def commit(root: Path, day: str) -> str:
    git(root, "add", ".")
    git(root, "commit", "--allow-empty", "-qm", "fixture", day=day)
    return git(root, "rev-parse", "HEAD")


def model(mid: str, score: int = 40) -> dict:
    return {
        "model_id": mid, "display_name": mid, "status": "active",
        "release_date": "2026-10-01",
        "benchmarks": {"evidence": [{
            "benchmark_id": "example_bench", "benchmark_version": "v1",
            "model_id_as_evaluated": mid, "configuration": "standard",
            "unit": "percent", "score": score, "evidence_date": "2026-10-10",
            "date_type": "evaluated", "source_url": "https://lab.example/results",
            "source_kind": "independent", "measured_by": "independent",
        }]},
    }


def fact(facet: str, value: object) -> dict:
    return {
        "id": f"lab/subscription/basic#{facet}",
        "subject": {"kind": "offering", "id": "lab/subscription/basic"},
        "facet": facet, "value": value, "state": "known",
        "sources": [{"source_id": "pricing", "snapshot_ref": "sha256:fixture"}],
    }


def repository(root: Path, mid: str) -> Path:
    root.mkdir()
    git(root, "init", "-q")
    write(root, f"models/{mid}.md", model(mid))
    write(root, "registry/sources.yaml", {"sources": [
        {"id": "pricing", "url": "https://lab.example/pricing"},
    ]})
    write(root, "offerings/subscriptions/lab.yaml", [{
        "kind": "subscription", "provider": "lab", "plan": "basic",
        "facts": [fact("offering.subscription.price", 20),
                  fact("offering.subscription.models_covered", [mid])],
    }])
    commit(root, "2026-10-12T12:00:00Z")
    return root


def test_public_draft_is_independent_of_private_values_and_environment(tmp_path, monkeypatch):
    from scripts.model_week import generate

    public = repository(tmp_path / "public", "lab/public")
    private = repository(tmp_path / "private", "secret/unreleased")
    write(public, "models/lab/new-public.md", model("lab/new-public"))
    commit(public, "2026-10-14T12:00:00Z")
    write(private, "models/secret/unreleased.md", model("secret/unreleased", 987654321))
    write(private, "models/secret/hidden.md", model("secret/hidden"))
    commit(private, "2026-10-15T12:00:00Z")

    alone = tmp_path / "alone"
    combined = tmp_path / "combined"
    generate("2026-10-13", public, alone)
    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(private))
    monkeypatch.setenv("MODELSPEC_REQUIRE_DATA_DIR", "1")
    result = generate("2026-10-13", public, combined, private_repo=private)

    text = (combined / "public.md").read_text()
    assert text == (alone / "public.md").read_text()
    assert "lab/new-public" in text
    for secret in ("secret", "987654321", str(private), git(private, "rev-parse", "HEAD")):
        assert secret not in text
        assert secret not in json.dumps(result)
    assert "secret/hidden" in (combined / "private.md").read_text()
    assert "987654321" in (combined / "private.md").read_text()
    assert "DRAFT" in text and "PUBLIC" in text
    assert "PRIVATE" in (combined / "private.md").read_text()
    assert not git(public, "status", "--porcelain")
    assert not git(private, "status", "--porcelain")


def test_draft_cites_each_change_and_respects_utc_week(tmp_path):
    from scripts.model_week import generate

    public = repository(tmp_path / "public", "lab/public")
    before = git(public, "rev-parse", "HEAD")
    updated = model("lab/public", 55)
    updated["benchmarks"]["evidence"][0]["evidence_date"] = "2026-10-13"
    updated["status"] = "retired"
    write(public, "models/lab/public.md", updated)
    write(public, "models/lab/added.md", model("lab/added"))
    write(public, "offerings/subscriptions/lab.yaml", [{
        "facts": [fact("offering.subscription.price", 30),
                  fact("offering.subscription.models_covered", ["lab/added"])],
    }])
    write(public, "offerings/lab/api.yaml", [{
        "facts": [fact("offering.price.input", 3.5)],
    }])
    after = commit(public, "2026-10-13T00:00:00Z")
    write(public, "models/lab/next-week.md", model("lab/next-week"))
    commit(public, "2026-10-20T00:00:00Z")
    out = tmp_path / "draft"

    counts = generate("2026-10-13", public, out)
    text = (out / "public.md").read_text()
    assert counts["public"]["changes"] == {
        "Models added": 1, "Benchmark movers": 2,
        "Price and plan changes": 2, "Lineup changes": 3,
    }
    assert "lab/next-week" not in text
    assert before in text and after in text
    assert '"score": 40' in text and '"score": 55' in text
    assert '"value": 20' in text and '"value": 30' in text
    assert '"value": 3.5' in text
    for line in text.splitlines():
        if line.startswith("- "):
            assert "/blob/" in line
            assert "catalogue commit 2026-10-13T00:00:00+00:00" in line
    assert "https://lab.example/results" in text
    assert "https://lab.example/pricing" in text
    assert '"evidence_date": "2026-10-10"' in text
    assert '"evidence_date": "2026-10-13"' in text


def test_recheck_without_score_change_is_not_a_benchmark_mover(tmp_path):
    from scripts.model_week import generate

    repo = repository(tmp_path / "public", "lab/public")
    updated = model("lab/public")
    updated["benchmarks"]["evidence"][0]["evidence_date"] = "2026-10-16"
    write(repo, "models/lab/public.md", updated)
    commit(repo, "2026-10-17T12:00:00Z")
    counts = generate("2026-10-13", repo, tmp_path / "draft")
    assert counts["public"]["changes"]["Benchmark movers"] == 0


def test_git_environment_cannot_redirect_public_history_to_private_repo(tmp_path, monkeypatch):
    from scripts.model_week import generate

    public = repository(tmp_path / "public", "lab/public")
    private = repository(tmp_path / "private", "secret/model")
    write(private, "models/secret/new.md", model("secret/new", 987654321))
    commit(private, "2026-10-15T12:00:00Z")
    clean = tmp_path / "clean"
    generate("2026-10-13", public, clean)
    monkeypatch.setenv("GIT_DIR", str(private / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(private))
    contaminated = tmp_path / "contaminated"
    generate("2026-10-13", public, contaminated)
    assert (contaminated / "public.md").read_bytes() == (clean / "public.md").read_bytes()


@pytest.mark.parametrize("destination", ["blog/weekly", "dist/draft", "docs/draft"])
def test_refuses_any_output_in_public_repo(tmp_path, destination):
    from scripts.model_week import DraftError, generate

    repo = repository(tmp_path / "public", "lab/public")
    with pytest.raises(DraftError, match="outside"):
        generate("2026-10-13", repo, repo / destination)
    assert not (repo / destination).exists()


def test_symlink_to_repo_and_existing_output_are_refused(tmp_path):
    from scripts.model_week import DraftError, generate

    repo = repository(tmp_path / "public", "lab/public")
    link = tmp_path / "link"
    link.symlink_to(repo, target_is_directory=True)
    with pytest.raises(DraftError, match="outside"):
        generate("2026-10-13", repo, link / "blog/draft")
    out = tmp_path / "existing"
    out.mkdir()
    (out / "private.md").symlink_to(repo / "leaked.md")
    with pytest.raises(DraftError, match="new directory"):
        generate("2026-10-13", repo, out)
    assert not (repo / "leaked.md").exists()


def test_different_measurement_contexts_do_not_become_score_comparisons(tmp_path):
    from scripts.model_week import generate

    repo = repository(tmp_path / "public", "lab/public")
    updated = model("lab/public", 92)
    updated["benchmarks"]["evidence"][0]["configuration"] = "more tools"
    write(repo, "models/lab/public.md", updated)
    commit(repo, "2026-10-14T12:00:00Z")
    out = tmp_path / "draft"
    counts = generate("2026-10-13", repo, out)
    assert counts["public"]["changes"]["Benchmark movers"] == 2
    lines = [line for line in (out / "public.md").read_text().splitlines()
             if line.startswith("- ") and "example_bench" in line]
    assert len(lines) == 2
    assert all("not recorded" in line for line in lines)
    assert not any('"score": 40' in line and '"score": 92' in line for line in lines)


@pytest.mark.parametrize("url", [
    "https://artificial" "analysis.ai/results", "https://zap" "ier.com/results",
    "https://x.com/launch", "https://www.twitter.com/launch",
])
def test_excluded_and_x_sources_are_withheld(tmp_path, url):
    from scripts.model_week import generate

    repo = repository(tmp_path / "public", "lab/public")
    updated = model("lab/public", 77)
    updated["benchmarks"]["evidence"][0]["source_url"] = url
    write(repo, "models/lab/public.md", updated)
    commit(repo, "2026-10-14T12:00:00Z")
    out = tmp_path / "draft"
    counts = generate("2026-10-13", repo, out)
    text = (out / "public.md").read_text()
    assert url not in text and '"score": 77' not in text
    assert counts["public"]["withheld"] == 1


def test_private_parse_failure_does_not_write_drafts_or_echo_private_data(tmp_path, monkeypatch,
                                                                       capsys):
    from scripts import model_week

    public = repository(tmp_path / "public", "lab/public")
    private = repository(tmp_path / "private", "secret/model")
    (private / "models/secret/model.md").write_text("---\nprivate-secret: [broken\n---\n")
    commit(private, "2026-10-14T12:00:00Z")
    monkeypatch.setattr(model_week, "PUBLIC_REPO", public)
    out = tmp_path / "draft"
    status = model_week.main(["--week", "2026-10-13", "--private-repo", str(private),
                              "--out-dir", str(out)])
    assert status == 2
    assert "private-secret" not in str(capsys.readouterr())
    assert not out.exists()


def test_catalogue_documentation_is_not_a_model_card(tmp_path):
    from scripts.model_week import generate

    repo = repository(tmp_path / "public", "lab/public")
    (repo / "models/LICENSE.md").write_text("Catalogue licence text.\n")
    commit(repo, "2026-10-14T12:00:00Z")
    counts = generate("2026-10-13", repo, tmp_path / "draft")
    assert not any(counts["public"]["changes"].values())


@pytest.mark.parametrize("broken", [[], ["private-secret"], {"sources": ["private-secret"]}])
def test_malformed_private_registry_cannot_escape_as_a_traceback(tmp_path, monkeypatch,
                                                                capsys, broken):
    from scripts import model_week

    public = repository(tmp_path / "public", "lab/public")
    private = repository(tmp_path / "private", "secret/model")
    write(private, "registry/sources.yaml", broken)
    write(private, "models/secret/new.md", model("secret/new"))
    commit(private, "2026-10-14T12:00:00Z")
    monkeypatch.setattr(model_week, "PUBLIC_REPO", public)
    out = tmp_path / "draft"
    status = model_week.main(["--week", "2026-10-13", "--private-repo", str(private),
                              "--out-dir", str(out)])
    assert status == 2
    assert "private-secret" not in str(capsys.readouterr())
    assert not out.exists()


def test_excluded_benchmark_id_is_withheld_even_at_an_allowed_url(tmp_path):
    from scripts.model_week import generate

    repo = repository(tmp_path / "public", "lab/public")
    updated = model("lab/public", 123456)
    updated["benchmarks"]["evidence"][0]["benchmark_id"] = "aa_intelligence_index"
    write(repo, "models/lab/public.md", updated)
    commit(repo, "2026-10-14T12:00:00Z")
    out = tmp_path / "draft"
    counts = generate("2026-10-13", repo, out)
    assert "aa_intelligence_index" not in (out / "public.md").read_text()
    assert "123456" not in (out / "public.md").read_text()
    assert counts["public"]["withheld"] == 1


def test_card_and_offering_facts_inherit_subjects_and_keep_price_effective_dates(tmp_path):
    from scripts.model_week import generate

    repo = repository(tmp_path / "public", "lab/public")
    updated = model("lab/public")
    lifecycle = fact("model.lifecycle", "retired")
    del lifecycle["subject"]
    updated["facts"] = [lifecycle]
    updated["lifecycle"] = "retired"
    write(repo, "models/lab/public.md", updated)
    price = fact("offering.price.input", 4)
    del price["subject"]
    price["effective_from"] = "2026-10-15"
    price["effective_until"] = "2026-11-01"
    write(repo, "offerings/lab/lab/public.yaml", [{
        "provider": "lab", "model": "lab/public", "region": "global", "tier": "standard",
        "facts": [price],
    }])
    commit(repo, "2026-10-15T12:00:00Z")
    out = tmp_path / "draft"
    generate("2026-10-13", repo, out)
    text = (out / "public.md").read_text()
    assert "lab/lab/public/global/standard offering.price.input" in text
    assert "lab/public model.lifecycle" in text
    assert '"effective_from": "2026-10-15"' in text
    assert '"effective_until": "2026-11-01"' in text


def test_shared_model_private_changes_and_dirty_public_files_cannot_enter_public_draft(tmp_path):
    from scripts.model_week import generate

    public = repository(tmp_path / "public", "lab/shared")
    private = repository(tmp_path / "private", "lab/shared")
    clean = tmp_path / "clean"
    generate("2026-10-13", public, clean)
    write(private, "models/lab/shared.md", model("lab/shared", 987654321))
    write(private, "offerings/subscriptions/lab.yaml", [{
        "facts": [fact("offering.subscription.price", 456789)],
    }])
    commit(private, "2026-10-15T12:00:00Z")
    write(public, "models/lab/shared.md", model("dirty-uncommitted", 123456789))
    out = tmp_path / "draft"
    generate("2026-10-13", public, out, private_repo=private)
    assert (out / "public.md").read_bytes() == (clean / "public.md").read_bytes()
    assert "987654321" in (out / "private.md").read_text()
    assert "456789" in (out / "private.md").read_text()
    assert (out.stat().st_mode & 0o777) == 0o700
    assert ((out / "private.md").stat().st_mode & 0o777) == 0o600


def test_cite_only_sources_remain_links_and_plan_quotes_are_never_copied(tmp_path):
    from scripts.model_week import generate

    repo = repository(tmp_path / "public", "lab/public")
    write(repo, "registry/sources.yaml", {"sources": [
        {"id": "pricing", "url": "https://docs.x.ai/pricing"},
    ]})
    write(repo, "offerings/subscriptions/lab.yaml", [{
        "facts": [fact("offering.subscription.price", 30),
                  fact("offering.subscription.coverage_quote", "PAGE-BYTES-DO-NOT-COPY"),
                  fact("offering.subscription.coding_tools_quote", "PAGE-BYTES-DO-NOT-COPY"),
                  fact("offering.subscription.usage_allowance", "PAGE-BYTES-DO-NOT-COPY")],
    }])
    commit(repo, "2026-10-15T12:00:00Z")
    out = tmp_path / "draft"
    generate("2026-10-13", repo, out)
    text = (out / "public.md").read_text()
    assert "https://docs.x.ai/pricing" in text
    assert '"value": 30' in text
    assert "PAGE-BYTES-DO-NOT-COPY" not in text
