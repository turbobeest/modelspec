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


def commit(root: Path, day: str, *, published: bool = True) -> str:
    git(root, "add", ".")
    git(root, "commit", "--allow-empty", "-qm", "fixture", day=day)
    if published:
        git(root, "update-ref", "refs/remotes/origin/main", "HEAD")
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


def test_public_history_ignores_local_only_commits(tmp_path):
    from scripts.model_week import generate

    repo = repository(tmp_path / "public", "lab/public")
    write(repo, "models/lab/published.md", model("lab/published"))
    published = commit(repo, "2026-10-14T12:00:00Z")
    write(repo, "models/secret/local-only.md", model("secret/local-only", 987654321))
    local = commit(repo, "2026-10-15T12:00:00Z", published=False)
    out = tmp_path / "draft"
    counts = generate("2026-10-13", repo, out)

    assert counts["public"]["changes"] == {
        "Models added": 1, "Benchmark movers": 1,
        "Price and plan changes": 0, "Lineup changes": 1,
    }
    for name in ("public.md", "public-appendix.md"):
        text = (out / name).read_text()
        assert "lab/published" in text and published in text
        assert "secret/local-only" not in text
        assert "987654321" not in text and local not in text


def test_public_history_uses_origin_main_when_head_is_behind(tmp_path):
    from scripts.model_week import generate

    repo = repository(tmp_path / "public", "lab/public")
    baseline = git(repo, "rev-parse", "HEAD")
    write(repo, "models/lab/published.md", model("lab/published"))
    commit(repo, "2026-10-14T12:00:00Z")
    git(repo, "checkout", "--detach", baseline)
    out = tmp_path / "draft"
    counts = generate("2026-10-13", repo, out)
    assert counts["public"]["changes"]["Models added"] == 1
    assert "lab/published" in (out / "public.md").read_text()


def test_missing_origin_main_refuses_before_writing(tmp_path):
    from scripts.model_week import DraftError, generate

    repo = repository(tmp_path / "public", "lab/public")
    git(repo, "update-ref", "-d", "refs/remotes/origin/main")
    out = tmp_path / "draft"
    with pytest.raises(DraftError):
        generate("2026-10-13", repo, out)
    assert not out.exists()


def test_model_and_status_changes_cite_the_card_announcement(tmp_path):
    from scripts.model_week import generate

    repo = repository(tmp_path / "public", "lab/public")
    updated = model("lab/public")
    updated["status"] = "retired"
    updated["sources"] = {"provider_docs_url": "https://lab.example/public-release"}
    added = model("lab/added")
    added["sources"] = {"provider_docs_url": "https://lab.example/added-release"}
    write(repo, "models/lab/public.md", updated)
    write(repo, "models/lab/added.md", added)
    commit(repo, "2026-10-14T12:00:00Z")
    out = tmp_path / "draft"
    generate("2026-10-13", repo, out)
    lines = (out / "public.md").read_text().splitlines()
    added_line, = [line for line in lines if line.startswith('- `"lab/added"`:')]
    status_line, = [line for line in lines
                   if line.startswith('- `"lab/public catalogue status"`:')]
    assert "[upstream source](https://lab.example/added-release)" in added_line
    assert "[upstream source](https://lab.example/public-release)" in status_line


@pytest.mark.parametrize("removal", [False, True])
def test_premier_only_changes_cite_unchanged_member_cards(tmp_path, removal):
    from scripts.model_week import generate

    repo = repository(tmp_path / "public", "lab/public")
    card = model("lab/public")
    card["sources"] = {"provider_docs_url": "https://lab.example/public-release"}
    write(repo, "models/lab/public.md", card)
    members = [{"model_id": "lab/public"}]
    write(repo, "premier/slice-1.yaml", {"models": members if removal else []})
    commit(repo, "2026-10-12T18:00:00Z")
    write(repo, "premier/slice-1.yaml", {"models": [] if removal else members})
    commit(repo, "2026-10-14T12:00:00Z")
    out = tmp_path / "draft"
    counts = generate("2026-10-13", repo, out)
    assert counts["public"]["changes"] == {
        "Models added": 0, "Benchmark movers": 0,
        "Price and plan changes": 0, "Lineup changes": 1,
    }
    line, = [line for line in (out / "public.md").read_text().splitlines()
             if line.startswith("- ")]
    assert '"lab/public premier membership"' in line
    assert "[upstream source](https://lab.example/public-release)" in line


@pytest.mark.parametrize("url", [
    "https://artificial" "analysis.ai/release", "https://zap" "ier.com/release",
    "https://news.zap" "ier.com/release", "https://x.com/release",
    "javascript:alert(1)",
])
def test_unsafe_card_links_are_withheld_from_summary_and_appendix(tmp_path, url):
    from scripts.model_week import generate

    repo = repository(tmp_path / "public", "lab/public")
    card = model("lab/unsafe")
    card["sources"] = {"provider_docs_url": url}
    card["benchmarks"] = {}
    write(repo, "models/lab/unsafe.md", card)
    write(repo, "premier/slice-1.yaml", {"models": [{"model_id": "lab/unsafe"}]})
    commit(repo, "2026-10-14T12:00:00Z")
    out = tmp_path / "draft"
    counts = generate("2026-10-13", repo, out)
    assert counts["public"]["withheld"] == 3
    for name in ("public.md", "public-appendix.md"):
        text = (out / name).read_text()
        assert "lab/unsafe" not in text and url not in text


@pytest.mark.parametrize("publisher", ["zap" "ier", "artificial" "-analysis"],
                         ids=["publisher-one", "publisher-two"])
@pytest.mark.parametrize("output_name", ["public.md", "public-appendix.md"])
def test_excluded_publishers_in_paths_are_withheld(tmp_path, publisher, output_name):
    from scripts.model_week import generate

    repo = repository(tmp_path / "public", "lab/public")
    write(repo, f"models/{publisher}-bot.md", model("lab/path-only"))
    blocked_price = fact("offering.subscription.price", 30)
    blocked_price["subject"]["id"] = "lab/subscription/path-only"
    write(repo, f"offerings/{publisher}/prices.yaml", [{"facts": [blocked_price]}])
    write(repo, "models/lab/clean.md", model("lab/clean"))
    clean_price = fact("offering.subscription.price", 25)
    clean_price["subject"]["id"] = "lab/subscription/clean"
    write(repo, "offerings/lab/clean.yaml", [{"facts": [clean_price]}])
    commit(repo, "2026-10-14T12:00:00Z")
    out = tmp_path / "draft"

    counts = generate("2026-10-13", repo, out)
    text = (out / output_name).read_text()
    assert publisher not in text
    assert "lab/path-only" not in text
    assert "lab/subscription/path-only" not in text
    assert "models/lab/clean.md" in text
    assert "offerings/lab/clean.yaml" in text
    assert counts["public"] == {
        "changes": {"Models added": 1, "Benchmark movers": 1,
                    "Price and plan changes": 1, "Lineup changes": 1},
        "withheld": 4,
    }


@pytest.fixture
def busy_repository(tmp_path):
    repo = repository(tmp_path / "public", "lab/public")
    for i in range(12):
        write(repo, f"models/lab/m{i:02}.md", model(f"lab/m{i:02}"))
        price = fact("offering.subscription.price", 30)
        price["subject"]["id"] = f"lab/subscription/plan{i:02}"
        write(repo, f"offerings/subscriptions/plan{i:02}.yaml", [{"facts": [price]}])
    commit(repo, "2026-10-14T12:00:00Z")
    return repo


def category_entries(text, category):
    section = text.split(f"### {category}\n\n", 1)[1].split("\n### ", 1)[0]
    return [line for line in section.splitlines() if line.startswith("- ")]


def test_default_category_caps_keep_full_counts_and_separate_appendix(tmp_path, busy_repository):
    from scripts.model_week import generate

    out = tmp_path / "draft"
    counts = generate("2026-10-13", busy_repository, out)
    summary = (out / "public.md").read_text()
    assert counts["public"]["changes"] == {
        "Models added": 12, "Benchmark movers": 12,
        "Price and plan changes": 12, "Lineup changes": 12,
    }
    assert len(category_entries(summary, "Models added")) == 10
    assert summary.count("and 2 more") == 4
    appendix = (out / "public-appendix.md").read_text()
    for category in ("Models added", "Benchmark movers",
                     "Price and plan changes", "Lineup changes"):
        assert len(category_entries(summary, category)) == 10
        assert len(category_entries(appendix, category)) == 12
    assert '"lab/m09"' in summary
    assert '"lab/m10"' not in summary and '"lab/m11"' not in summary
    assert '"lab/m10"' in appendix and '"lab/m11"' in appendix
    assert "[Full list](public-appendix.md)" in summary
    assert "and 2 more" not in appendix


def test_cli_category_caps_are_independent(tmp_path, busy_repository, monkeypatch, capsys):
    from scripts import model_week

    monkeypatch.setattr(model_week, "PUBLIC_REPO", busy_repository)
    out = tmp_path / "draft"
    status = model_week.main([
        "--week", "2026-10-13", "--out-dir", str(out),
        "--limit", "Models added=2", "--limit", "Benchmark movers=3",
        "--limit", "Price and plan changes=1", "--limit", "Lineup changes=0",
    ])
    assert status == 0
    assert json.loads(capsys.readouterr().out)["public"]["changes"] == {
        "Models added": 12, "Benchmark movers": 12,
        "Price and plan changes": 12, "Lineup changes": 12,
    }
    text = (out / "public.md").read_text()
    assert [json.loads(line.split("`", 2)[1])
            for line in category_entries(text, "Models added")] == [
        "lab/m00", "lab/m01",
    ]
    assert [json.loads(line.split("`", 2)[1]).split(" context ")[0]
            for line in category_entries(text, "Benchmark movers")] == [
        "lab/m00 example_bench", "lab/m01 example_bench", "lab/m02 example_bench",
    ]
    assert [json.loads(line.split("`", 2)[1])
            for line in category_entries(text, "Price and plan changes")] == [
        "lab/subscription/plan00 offering.subscription.price",
    ]
    assert category_entries(text, "Lineup changes") == []
    for notice in ("and 10 more", "and 9 more", "and 11 more", "and 12 more"):
        assert notice in text


@pytest.mark.parametrize("limits", [{"Models added": -1}, {"Models added": 1.5},
                                    {"Models added": True}, {"Unknown": 2}])
def test_invalid_category_limits_refuse_without_output(tmp_path, limits):
    from scripts.model_week import DraftError, generate

    repo = repository(tmp_path / "public", "lab/public")
    out = tmp_path / "draft"
    with pytest.raises(DraftError):
        generate("2026-10-13", repo, out, category_limits=limits)
    assert not out.exists()


def test_exact_limit_has_no_overflow_and_other_categories_keep_defaults(tmp_path, busy_repository):
    from scripts.model_week import generate

    out = tmp_path / "draft"
    generate("2026-10-13", busy_repository, out, category_limits={"Models added": 12})
    text = (out / "public.md").read_text()
    assert len(category_entries(text, "Models added")) == 12
    assert len(category_entries(text, "Benchmark movers")) == 10
    assert text.count("and 2 more") == 3
    assert "and 0 more" not in text


@pytest.mark.parametrize("limit", ["Models added=-1", "Models added=1.5", "Unknown=2", "2"])
def test_cli_invalid_limits_refuse_without_writing(tmp_path, monkeypatch, capsys, limit):
    from scripts import model_week

    repo = repository(tmp_path / "public", "lab/public")
    monkeypatch.setattr(model_week, "PUBLIC_REPO", repo)
    out = tmp_path / "draft"
    assert model_week.main([
        "--week", "2026-10-13", "--out-dir", str(out), "--limit", limit,
    ]) == 2
    assert capsys.readouterr().out == (
        "Draft refused: check the date, complete catalogue history including origin/main, "
        "category limits, and external output path.\n"
    )
    assert not out.exists()


def test_appendices_preserve_private_separation_and_permissions(tmp_path):
    from scripts.model_week import generate

    public = repository(tmp_path / "public", "lab/public")
    private = repository(tmp_path / "private", "secret/private")
    write(public, "models/lab/added.md", model("lab/added"))
    commit(public, "2026-10-14T12:00:00Z")
    write(private, "models/secret/added.md", model("secret/added", 987654321))
    commit(private, "2026-10-14T12:00:00Z", published=False)
    alone = tmp_path / "alone"
    combined = tmp_path / "combined"
    generate("2026-10-13", public, alone)
    generate("2026-10-13", public, combined, private_repo=private)
    assert sorted(path.name for path in combined.iterdir()) == [
        "private-appendix.md", "private.md", "public-appendix.md", "public.md",
    ]
    for name in ("public.md", "public-appendix.md"):
        assert (alone / name).read_bytes() == (combined / name).read_bytes()
        assert "secret" not in (combined / name).read_text()
    for name in ("private.md", "private-appendix.md"):
        text = (combined / name).read_text()
        assert "## PRIVATE" in text and "987654321" in text
    assert combined.stat().st_mode & 0o777 == 0o700
    for path in combined.iterdir():
        assert path.stat().st_mode & 0o777 == 0o600
