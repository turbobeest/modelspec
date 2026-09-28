"""The pull-request chart check classifies changed evidence and new fixtures.

Each test builds its own git repository under tmp_path. The script is pointed
at that root, so the developer's checkout and chart cache are not inputs.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "chart_check_pr.py"
WORKFLOW = ROOT / ".github" / "workflows" / "chart-check.yml"
VALIDATE_WORKFLOW = ROOT / ".github" / "workflows" / "validate-cards.yml"

READ_TWO = (
    '      - reader: one\n'
    '        date: "2026-09-24"\n'
    '      - reader: two\n'
    '        date: "2026-09-24"\n'
)
READ_ONE = (
    '      - reader: one\n'
    '        date: "2026-09-24"\n'
)
DISPUTED = (
    "        disputed:\n"
    "          - reader: one\n"
    "            value: 10\n"
    "          - reader: two\n"
    "            value: 12\n"
)
BAD_RESOLUTION = (
    "        resolution:\n"
    "          rule: two_of_three\n"
    "          readings:\n"
    "            - reader: one\n"
    "              value: 10\n"
    "            - reader: two\n"
    "              value: 20\n"
)


def _git(repo: Path, *args: str) -> None:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(f"git {args} failed\n{proc.stderr}")


def init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "chart-check@example.com")
    _git(repo, "config", "user.name", "Chart Check")
    _git(repo, "config", "commit.gpgsign", "false")
    return repo


def write(repo: Path, path: str, text: str) -> None:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def commit(repo: Path, message: str) -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "--no-verify", "-m", message)


def card(rows: list[str], body: str = "Body.") -> str:
    evidence = "  evidence: []\n" if not rows else "  evidence:\n" + "".join(rows)
    return (
        "---\n"
        "model_id: acme/widget\n"
        "display_name: Widget\n"
        "provider: acme\n"
        "benchmarks:\n"
        f"{evidence}"
        "---\n"
        f"\n{body}\n"
    )


def row_yaml(
    score: float,
    source: str = "https://example.com/release",
    benchmark: str = "gpqa_diamond",
    configuration: str = "max",
    unit: str = "percent",
) -> str:
    return (
        f"  - benchmark_id: {benchmark}\n"
        "    model_id_as_evaluated: acme/widget\n"
        f"    score: {score}\n"
        f"    unit: {unit}\n"
        f"    source_url: {source}\n"
        "    source_kind: provider_self_report\n"
        "    evidence_date: '2026-09-24'\n"
        "    date_type: published\n"
        "    verified_at: '2026-09-24'\n"
        "    benchmark_version: ''\n"
        f"    configuration: '{configuration}'\n"
    )


def bar(
    score: str,
    benchmark: str = "gpqa_diamond",
    configuration: str = "max",
    extra: str = "",
    confirmed_by: list[str] | None = None,
    reason: str = "",
) -> str:
    names = ["one", "two"] if confirmed_by is None else confirmed_by
    joined = ", ".join(f'"{name}"' for name in names)
    reason_line = f'        single_read_reason: "{reason}"\n' if reason else ""
    text = (
        "      - model_as_labelled: Widget\n"
        "        model_id: acme/widget\n"
        f"        benchmark_id: {benchmark}\n"
        f"        score: {score}\n"
        "        unit: percent\n"
        "        printed: true\n"
        f'        configuration: "{configuration}"\n'
        "        role: subject\n"
        f"        confirmed_by: [{joined}]\n"
        f"{reason_line}"
    )
    return text + extra


def chart(
    bars: str,
    readings: str = READ_TWO,
    page: str = "https://example.com/release/",
    reason: str = "",
    title: str = "Scores",
) -> str:
    reason_line = f'    single_read_reason: "{reason}"\n' if reason else ""
    return (
        f'page_url: "{page}"\n'
        "publisher: Example\n"
        'read_on: "2026-09-24"\n'
        "charts:\n"
        f'  - title: "{title}"\n'
        "    kind: html_table\n"
        "    competitor_numbers: unstated\n"
        f"{reason_line}"
        "    readings:\n"
        f"{readings}"
        "    bars:\n"
        f"{bars}"
    )


def run(
    repo: Path,
    *args: str,
    summary: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    env.pop("GITHUB_STEP_SUMMARY", None)
    if summary is not None:
        env["GITHUB_STEP_SUMMARY"] = str(summary)
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), *args],
        cwd=repo,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def checked(
    repo: Path, summary: Path | None = None
) -> tuple[subprocess.CompletedProcess[str], dict]:
    proc = run(repo, "--base", "base", "--json", str(repo / "out.json"), summary=summary)
    assert proc.returncode in {0, 1}, proc.stderr + proc.stdout
    report = json.loads((repo / "out.json").read_text(encoding="utf-8"))
    return proc, report


def test_matching_row_is_verified(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    write(repo, "benchmarks/_charts/page.yaml", chart(bar("96.0")))
    write(repo, "models/acme/widget.md", card([]))
    commit(repo, "base")
    _git(repo, "branch", "base")
    write(repo, "models/acme/widget.md", card([row_yaml(96.04)]))
    commit(repo, "head")
    summary = repo / "step.md"
    proc, report = checked(repo, summary)
    assert proc.returncode == 0
    assert report["rows"][0]["change"] == "added"
    assert report["rows"][0]["outcome"] == "verified"
    assert report["rows"][0]["chart_score"] == 96.0
    assert report["blocking"] == 0
    assert summary.read_text(encoding="utf-8") == proc.stdout


def test_different_score_is_a_mismatch(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    write(repo, "benchmarks/_charts/page.yaml", chart(bar("96.0")))
    write(repo, "models/acme/widget.md", card([]))
    commit(repo, "base")
    _git(repo, "branch", "base")
    write(repo, "models/acme/widget.md", card([row_yaml(90.0)]))
    commit(repo, "head")
    proc, report = checked(repo)
    assert proc.returncode == 1
    assert report["rows"][0]["outcome"] == "mismatch"
    assert report["findings"] == []
    assert "90 percent" in proc.stdout
    assert "96 percent" in proc.stdout


def test_fixture_without_a_bar_warns(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    write(repo, "benchmarks/_charts/page.yaml", chart(bar("10", benchmark="mmlu")))
    write(repo, "models/acme/widget.md", card([]))
    commit(repo, "base")
    _git(repo, "branch", "base")
    write(repo, "models/acme/widget.md", card([row_yaml(90.0)]))
    commit(repo, "head")
    proc, report = checked(repo)
    assert proc.returncode == 0
    assert report["rows"][0]["outcome"] == "no_bar"
    assert report["warnings"] == 1
    assert report["blocking"] == 0


def test_dataset_and_page_without_a_fixture(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    write(repo, "models/acme/widget.md", card([]))
    commit(repo, "base")
    _git(repo, "branch", "base")
    write(
        repo,
        "models/acme/widget.md",
        card(
            [
                row_yaml(
                    1.0,
                    source="https://huggingface.co/datasets/example/scores",
                    benchmark="one",
                ),
                row_yaml(2.0, source="https://example.com/scores.json?download=1", benchmark="two"),
                row_yaml(
                    3.0,
                    source="https://raw.githubusercontent.com/example/repo/main/scores.csv",
                    benchmark="three",
                ),
                row_yaml(
                    4.0,
                    source="https://github.com/example/repo/raw/main/board.yml",
                    benchmark="four",
                ),
                row_yaml(5.0, source="https://example.com/blog/launch", benchmark="five"),
                row_yaml(
                    6.0,
                    source="https://raw.githubusercontent.com/example/repo/main/README.md",
                    benchmark="six",
                ),
            ]
        ),
    )
    commit(repo, "head")
    proc, report = checked(repo)
    assert proc.returncode == 0
    counts = {row["benchmark_id"]: row["outcome"] for row in report["rows"]}
    assert counts == {
        "one": "no_fixture_dataset",
        "two": "no_fixture_dataset",
        "three": "no_fixture_dataset",
        "four": "no_fixture_dataset",
        "five": "no_fixture",
        "six": "no_fixture",
    }
    assert "warning, for now" in proc.stdout
    assert report["blocking"] == 0


def _branch_from_base(repo: Path) -> None:
    write(repo, "README.md", "base\n")
    commit(repo, "base")
    _git(repo, "branch", "base")


def test_new_fixture_with_two_confirmers_passes(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    _branch_from_base(repo)
    write(repo, "benchmarks/_charts/new.yaml", chart(bar("96.0") + bar("80.0", benchmark="mmlu")))
    commit(repo, "head")
    proc, report = checked(repo)
    assert proc.returncode == 0
    assert report["findings"] == []
    assert report["blocking"] == 0
    assert proc.stdout.strip() != "nothing to check"


def test_new_bar_with_one_confirmer_blocks(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    _branch_from_base(repo)
    write(
        repo,
        "benchmarks/_charts/new.yaml",
        chart(bar("96.0", confirmed_by=["one"]), readings=READ_TWO),
    )
    commit(repo, "head")
    proc, report = checked(repo)
    assert proc.returncode == 1
    assert report["blocking"] == 1
    assert len(report["findings"]) == 1
    assert report["findings"][0]["level"] == "blocking"
    assert report["findings"][0]["kind"] == "readers"
    assert "fewer than two distinct readers and no single_read_reason" in (
        report["findings"][0]["problem"]
    )
    assert "Widget" in report["findings"][0]["problem"]


def test_bar_single_read_reason_passes(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    _branch_from_base(repo)
    write(
        repo,
        "benchmarks/_charts/new.yaml",
        chart(bar("96.0", confirmed_by=["one"], reason="the page was withdrawn")),
    )
    commit(repo, "head")
    proc, report = checked(repo)
    assert proc.returncode == 0
    assert report["findings"] == []
    assert report["blocking"] == 0


def test_chart_single_read_reason_covers_its_bars(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    _branch_from_base(repo)
    write(
        repo,
        "benchmarks/_charts/new.yaml",
        chart(
            bar("96.0", confirmed_by=["one"]) + bar("80.0", benchmark="mmlu", confirmed_by=["one"]),
            reason="second reader could not fetch the page",
        ),
    )
    commit(repo, "head")
    proc, report = checked(repo)
    assert proc.returncode == 0
    assert report["findings"] == []
    assert report["blocking"] == 0


def test_unchanged_single_read_bar_in_a_changed_fixture_is_not_judged(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    write(
        repo,
        "benchmarks/_charts/page.yaml",
        chart(
            bar("10", benchmark="mmlu", confirmed_by=["one"]) + bar("20", benchmark="gpqa_diamond")
        ),
    )
    commit(repo, "base")
    _git(repo, "branch", "base")
    write(
        repo,
        "benchmarks/_charts/page.yaml",
        chart(
            bar("10", benchmark="mmlu", confirmed_by=["one"]) + bar("21", benchmark="gpqa_diamond")
        ),
    )
    commit(repo, "head")
    proc, report = checked(repo)
    assert proc.returncode == 0
    assert report["findings"] == []
    assert report["blocking"] == 0


def test_confirmed_by_dropping_to_one_reader_blocks(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    write(repo, "benchmarks/_charts/page.yaml", chart(bar("10", confirmed_by=["one", "two"])))
    commit(repo, "base")
    _git(repo, "branch", "base")
    write(repo, "benchmarks/_charts/page.yaml", chart(bar("10", confirmed_by=["one"])))
    commit(repo, "head")
    proc, report = checked(repo)
    assert proc.returncode == 1
    assert any(
        "fewer than two distinct readers and no single_read_reason" in item["problem"]
        for item in report["findings"]
    )
    assert all(item["kind"] == "readers" for item in report["findings"])


def test_removed_bar_is_informational(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    write(
        repo,
        "benchmarks/_charts/page.yaml",
        chart(bar("10", benchmark="mmlu") + bar("20", benchmark="gpqa_diamond")),
    )
    commit(repo, "base")
    _git(repo, "branch", "base")
    write(repo, "benchmarks/_charts/page.yaml", chart(bar("10", benchmark="mmlu")))
    commit(repo, "head")
    proc, report = checked(repo)
    assert proc.returncode == 0
    assert report["blocking"] == 0
    assert len(report["findings"]) == 1
    removed = report["findings"][0]
    assert removed["level"] == "info"
    assert removed["kind"] == "removed"
    assert removed["problem"].startswith("removed bar ")
    assert "gpqa_diamond" in removed["problem"]
    assert "removed bar" in proc.stdout


def test_verified_single_read_warns(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    write(
        repo,
        "benchmarks/_charts/page.yaml",
        chart(bar("96.0", confirmed_by=["one"])),
    )
    write(repo, "models/acme/widget.md", card([]))
    commit(repo, "base")
    _git(repo, "branch", "base")
    write(repo, "models/acme/widget.md", card([row_yaml(96.04)]))
    commit(repo, "head")
    proc, report = checked(repo)
    assert proc.returncode == 0
    assert report["rows"][0]["outcome"] == "verified_single_read"
    assert report["rows"][0]["level"] == "warning"
    assert report["warnings"] == 1
    assert report["blocking"] == 0
    assert report["findings"] == []
    assert "verified_single_read" in proc.stdout


def test_reader_findings_list_at_most_50_rows(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    _branch_from_base(repo)
    bars = "".join(
        bar(str(index), benchmark=f"bench_{index}", confirmed_by=["one"]) for index in range(51)
    )
    write(repo, "benchmarks/_charts/new.yaml", chart(bars))
    commit(repo, "head")
    proc, report = checked(repo)
    assert proc.returncode == 1
    assert len(report["findings"]) == 51
    assert proc.stdout.count("fewer than two distinct readers") == 50
    assert "Blocking bars, 50 of 51." in proc.stdout
    assert "| benchmarks/_charts/new.yaml | Scores | 51 | 0 |" in proc.stdout
    assert "1 further blocking bar is omitted." in proc.stdout


def test_reader_findings_do_not_claim_omitted_rows_when_all_are_shown(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    _branch_from_base(repo)
    bars = "".join(
        bar(str(index), benchmark=f"bench_{index}", confirmed_by=["one"]) for index in range(2)
    )
    write(repo, "benchmarks/_charts/new.yaml", chart(bars))
    commit(repo, "head")
    proc, report = checked(repo)
    assert proc.returncode == 1
    assert len(report["findings"]) == 2
    assert "Blocking bars, 2 of 2." in proc.stdout
    assert "omitted" not in proc.stdout


def test_repeated_bar_key_pairs_by_position(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    bars = bar("10", confirmed_by=["one", "two"]) + bar("20", confirmed_by=["one"])
    write(repo, "benchmarks/_charts/page.yaml", chart(bars))
    commit(repo, "base")
    _git(repo, "branch", "base")
    later = READ_TWO.replace("2026-09-24", "2026-09-25")
    write(repo, "benchmarks/_charts/page.yaml", chart(bars, readings=later))
    commit(repo, "head")
    proc, report = checked(repo)
    assert proc.returncode == 0
    assert report["findings"] == []


def test_changed_fixture_with_a_disputed_bar_blocks(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    write(repo, "README.md", "base\n")
    commit(repo, "base")
    _git(repo, "branch", "base")
    write(repo, "benchmarks/_charts/new.yaml", chart(bar("10", extra=DISPUTED)))
    commit(repo, "head")
    proc, report = checked(repo)
    assert proc.returncode == 1
    assert any(item["problem"].startswith("disputed bar ") for item in report["findings"])


def test_bad_resolution_blocks(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    write(repo, "README.md", "base\n")
    commit(repo, "base")
    _git(repo, "branch", "base")
    write(repo, "benchmarks/_charts/new.yaml", chart(bar("10", extra=BAD_RESOLUTION)))
    commit(repo, "head")
    proc, report = checked(repo)
    assert proc.returncode == 1
    assert any(
        "resolution needs two readings that agree" in item["problem"] for item in report["findings"]
    )


def test_unchanged_single_read_fixture_does_not_block(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    write(
        repo,
        "benchmarks/_charts/old.yaml",
        chart(
            bar("1", confirmed_by=["one"]),
            readings=READ_ONE,
            page="https://example.com/old",
        ),
    )
    write(repo, "benchmarks/_charts/page.yaml", chart(bar("96.0")))
    write(repo, "models/acme/widget.md", card([]))
    commit(repo, "base")
    _git(repo, "branch", "base")
    write(repo, "models/acme/widget.md", card([row_yaml(96.04)]))
    commit(repo, "head")
    proc, report = checked(repo)
    assert proc.returncode == 0
    assert report["findings"] == []
    assert report["rows"][0]["outcome"] == "verified"
    assert report["fixture_files"] == []


def test_unresolvable_base_exits_2(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    write(repo, "README.md", "base\n")
    commit(repo, "base")
    proc = run(repo, "--base", "no-such-ref")
    assert proc.returncode == 2
    assert "cannot resolve base no-such-ref" in proc.stderr
    assert "nothing to check" not in proc.stdout


def test_missing_base_exits_2(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    write(repo, "README.md", "base\n")
    commit(repo, "base")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    env.pop("GITHUB_STEP_SUMMARY", None)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo)],
        cwd=repo,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert proc.returncode == 2
    assert proc.stderr.strip()


def test_changed_score_is_classified(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    write(repo, "benchmarks/_charts/page.yaml", chart(bar("96.0")))
    write(
        repo,
        "models/acme/widget.md",
        card([row_yaml(90.0), row_yaml(1.0, benchmark="mmlu", configuration="other")]),
    )
    commit(repo, "base")
    _git(repo, "branch", "base")
    write(repo, "models/acme/widget.md", card([row_yaml(96.04)]))
    commit(repo, "head")
    proc, report = checked(repo)
    assert proc.returncode == 0
    assert "changed 1" in proc.stdout
    assert len(report["rows"]) == 1
    row = report["rows"][0]
    assert row["change"] == "changed"
    assert row["outcome"] == "verified"
    assert row["previous_score"] == 90.0
    assert len(report["removed_rows"]) == 1
    assert report["removed_rows"][0]["benchmark_id"] == "mmlu"


def test_sibling_configurations(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    write(
        repo,
        "benchmarks/_charts/page.yaml",
        chart(bar("96.0", configuration="max") + bar("80.0", configuration="low")),
    )
    write(repo, "models/acme/widget.md", card([]))
    commit(repo, "base")
    _git(repo, "branch", "base")
    write(
        repo,
        "models/acme/widget.md",
        card(
            [
                row_yaml(96.04, configuration="max"),
                row_yaml(70.0, configuration="other"),
            ]
        ),
    )
    commit(repo, "head")
    proc, report = checked(repo)
    assert proc.returncode == 1
    outcomes = {row["configuration"]: row["outcome"] for row in report["rows"]}
    assert outcomes == {"max": "verified", "other": "mismatch"}
    assert report["findings"] == []


def test_removed_row_alone_is_nothing_to_check(tmp_path: Path) -> None:
    repo = init_repo(tmp_path)
    write(repo, "models/acme/widget.md", card([row_yaml(90.0)]))
    commit(repo, "base")
    _git(repo, "branch", "base")
    write(repo, "models/acme/widget.md", card([]))
    commit(repo, "head")
    proc, report = checked(repo)
    assert proc.returncode == 0
    assert proc.stdout == "nothing to check\n"
    assert report["nothing_to_check"] is True
    assert report["removed_rows"][0]["score"] == 90.0
    assert report["rows"] == []


def test_workflow_job_is_wired() -> None:
    """The chart check is its own workflow so a required check can run on every PR.

    validate-cards.yml filters pull_request by path. A required check with that
    filter stays pending on a pull request that does not touch those paths.
    """
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "    name: Check evidence against release charts\n" in text
    assert "paths:" not in text
    assert "contents: read" in text
    assert "pull-requests:" not in text
    assert "fetch-depth: 0" in text
    assert "git fetch origin main" in text
    assert 'python -m pip install \\\n' in text
    assert '"pydantic==2.13.5"' in text
    assert '"PyYAML==6.0.3"' in text
    assert "FalkorDB" not in text
    assert "-e \".\"" not in text
    assert "python scripts/chart_check_pr.py --base origin/main" in text
    assert "continue-on-error" not in text
    assert "|| true" not in text

    cards = VALIDATE_WORKFLOW.read_text(encoding="utf-8")
    assert "    name: Validate changed model cards\n" in cards
    assert "Check evidence against release charts" not in cards
    assert "- 'models/**'\n" in cards
    assert "- 'schema/**'\n" in cards
    assert "benchmarks/_charts" not in cards
    assert "chart_check" not in cards
