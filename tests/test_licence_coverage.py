"""MODEL-345: open-weights lineup licence coverage."""

from __future__ import annotations

from datetime import date

import yaml

from decision.model import Verification, VerificationActor, VerificationTarget, value_hash
from decision.verify import VerificationLog
from decision.sources import CopyStore
from scripts.policy.licence_coverage import (
    ALL_NOT_DISCLOSED_DESPITE_LINK,
    coverage_report,
    links_licence_file,
    main,
)

FACETS = (
    "licence.commercial_use",
    "licence.user_cap",
    "licence.output_training",
    "licence.fine_tuning",
)
COLLECTOR = VerificationActor(agent="grok-model-345", model_family="xai", method="licence-text-read@1")
VERIFIER = VerificationActor(
    agent="claude-cli", model_family="anthropic", method="licence-extract:claude-sonnet-5",
)


def _card(facts: list[dict]) -> str:
    body = {"model_id": "lab/open-one", "display_name": "Open One", "facts": facts}
    return "---\n" + yaml.safe_dump(body) + "---\n"


def _fact(facet: str, value, state: str, source_id: str) -> dict:
    row = {
        "facet": facet,
        "value": value,
        "state": state,
        "sources": [{
            "source_id": source_id,
            "snapshot_ref": "sha256:" + "0" * 64,
            "cited_regions": ["page"],
        }],
    }
    if state == "not_disclosed":
        row["checked_sources"] = [source_id]
    return row


def _verify(log: VerificationLog, facet: str, value) -> None:
    log.append(Verification(
        target=VerificationTarget(
            kind="fact", id=f"lab/open-one#{facet}", value_hash=value_hash(value),
        ),
        collector=COLLECTOR,
        verifier=VERIFIER,
        method=VERIFIER.method,
        outcome="verified",
        date=date(2026, 10, 8),
    ))


def _tree(tmp_path) -> None:
    (tmp_path / "models" / "lab").mkdir(parents=True)
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry" / "sources.yaml").write_text(
        """schema_version: 1
sources:
  - id: readme
    url: https://example.test/README.md
    normaliser: text-default
    fetch: http
  - id: terms
    url: https://example.test/terms
    kind: provider_terms
    normaliser: text-default
    fetch: http
  - id: licence
    url: https://example.test/LICENSE
    kind: licence_text
    normaliser: text-default
    fetch: http
""",
        encoding="utf-8",
    )
    (tmp_path / "premier.yaml").write_text(
        """models:
  - model_id: lab/open-one
    open_weights: true
  - model_id: lab/closed
    open_weights: false
""",
        encoding="utf-8",
    )


def test_gaps_are_absent_unknown_unverified_and_not_disclosed_from_the_wrong_kind(tmp_path) -> None:
    _tree(tmp_path)
    (tmp_path / "models" / "lab" / "open-one.md").write_text(_card([
        _fact("licence.commercial_use", None, "not_disclosed", "terms"),
        _fact("licence.user_cap", None, "not_disclosed", "terms"),
        _fact("licence.output_training", None, "not_disclosed", "licence"),
        _fact("licence.fine_tuning", "permitted", "known", "readme"),
    ]), encoding="utf-8")
    log = VerificationLog(tmp_path / "verification")
    _verify(log, "licence.commercial_use", None)
    _verify(log, "licence.user_cap", None)
    _verify(log, "licence.output_training", None)
    # fine_tuning is known but the log does not verify it.

    report = coverage_report(tmp_path, tmp_path / "premier.yaml")

    assert report["gaps"] == [
        "lab/open-one licence.user_cap not_disclosed without permitted citation",
        "lab/open-one licence.fine_tuning unverified",
    ]
    assert report["counts"]["licence.commercial_use"] == {
        "known_verified": 0, "not_disclosed_cited": 1, "failing": 0,
    }
    assert report["counts"]["licence.output_training"]["not_disclosed_cited"] == 1
    assert report["counts"]["licence.user_cap"]["failing"] == 1
    assert report["counts"]["licence.fine_tuning"]["failing"] == 1
    assert main(["--root", str(tmp_path), "--premier", str(tmp_path / "premier.yaml")]) == 1


def test_a_covered_lineup_exits_zero_and_ignores_closed_weights(tmp_path) -> None:
    _tree(tmp_path)
    (tmp_path / "models" / "lab" / "open-one.md").write_text(_card([
        _fact("licence.commercial_use", "permitted", "known", "licence"),
        _fact("licence.user_cap", "unbounded", "known", "licence"),
        _fact("licence.output_training", None, "not_disclosed", "licence"),
        _fact("licence.fine_tuning", "permitted", "known", "licence"),
    ]), encoding="utf-8")
    log = VerificationLog(tmp_path / "verification")
    _verify(log, "licence.commercial_use", "permitted")
    _verify(log, "licence.user_cap", "unbounded")
    _verify(log, "licence.output_training", None)
    _verify(log, "licence.fine_tuning", "permitted")

    assert coverage_report(tmp_path, tmp_path / "premier.yaml")["gaps"] == []
    assert main(["--root", str(tmp_path), "--premier", str(tmp_path / "premier.yaml")]) == 0


def _all_undisclosed(source_id: str) -> list[dict]:
    return [_fact(facet, None, "not_disclosed", source_id) for facet in FACETS]


def test_every_facet_not_disclosed_fails_when_the_card_links_a_licence(tmp_path) -> None:
    _tree(tmp_path)
    body = {
        "model_id": "lab/open-one",
        "display_name": "Open One",
        "licensing": {"license_url": "https://example.test/LICENSE"},
        "facts": _all_undisclosed("licence"),
    }
    (tmp_path / "models" / "lab" / "open-one.md").write_text(
        "---\n" + yaml.safe_dump(body) + "---\n", encoding="utf-8",
    )
    log = VerificationLog(tmp_path / "verification")
    for facet in FACETS:
        _verify(log, facet, None)

    report = coverage_report(tmp_path, tmp_path / "premier.yaml")

    assert report["gaps"] == [
        f"lab/open-one {facet} {ALL_NOT_DISCLOSED_DESPITE_LINK}" for facet in FACETS
    ]
    assert all(row["failing"] == 1 and row["not_disclosed_cited"] == 0
               for row in report["counts"].values())
    assert main(["--root", str(tmp_path), "--premier", str(tmp_path / "premier.yaml")]) == 1


def test_readme_license_link_is_a_linked_licence(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("MODELSPEC_SOURCE_CACHE", str(tmp_path / "cache"))
    readme = (
        "---\nlicense: apache-2.0\n"
        "license_link: https://example.test/LICENSE\n"
        "---\nOpen One\n"
    )
    ref = CopyStore().put(readme.encode())
    _tree(tmp_path)
    rows = []
    for facet in FACETS:
        row = _fact(facet, None, "not_disclosed", "readme")
        row["sources"][0]["snapshot_ref"] = ref
        rows.append(row)
    (tmp_path / "models" / "lab" / "open-one.md").write_text(_card(rows), encoding="utf-8")
    log = VerificationLog(tmp_path / "verification")
    for facet in FACETS:
        _verify(log, facet, None)

    report = coverage_report(tmp_path, tmp_path / "premier.yaml")

    assert report["gaps"] == [
        f"lab/open-one {facet} {ALL_NOT_DISCLOSED_DESPITE_LINK}" for facet in FACETS
    ]
    assert links_licence_file({}, [readme]) is True
    assert links_licence_file({}, ["---\nlicense: mit\n---\n"]) is False
