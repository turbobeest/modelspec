"""The published JSON tree is pin-able: commit plus export_schema_version.

`export_schema_version` is the shape of `/api/*.json`. It is not the CLI
`--json` envelope and not the ranking-report document in rankings.json.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline.export import EXPORT_SCHEMA_VERSION, Build, write  # noqa: E402
from pipeline.load import Benchmark, Catalogue, Model  # noqa: E402


def test_export_schema_version_is_not_the_other_schema_versions() -> None:
    """Three version numbers; conflating them is the expensive mistake."""
    from cli.modelspec.offline import SCHEMA_VERSION
    from cli.modelspec.snapshot import EXPORT_SCHEMA_VERSION as consumed

    assert EXPORT_SCHEMA_VERSION == consumed
    assert EXPORT_SCHEMA_VERSION[0].isdigit()
    # The ranking-report document is 2.0; the tree this names is 1.x. They
    # must keep different values so a consumer can tell them apart.
    assert EXPORT_SCHEMA_VERSION != "2.0"
    # The CLI envelope happens to also be 1.0 today; the field *names* differ.
    assert SCHEMA_VERSION == "1.0"
    assert "schema_version" != "export_schema_version"


def test_every_export_file_carries_version_and_build_identity(tmp_path: Path) -> None:
    model = Model(
        "prov/one",
        tmp_path / "one.md",
        {
            "model_id": "prov/one",
            "display_name": "One",
            "provider": "prov",
            "family": "f",
            "status": "active",
            "model_type": "llm-chat",
            "benchmarks": {"scores": {"humaneval": 50.0}},
        },
        "body",
    )
    bench = Benchmark(
        "humaneval",
        tmp_path / "humaneval.md",
        {"id": "humaneval", "name": "HumanEval", "category": "coding"},
        "",
    )
    catalogue = Catalogue(as_of=date(2026, 9, 1))
    build = Build(
        commit="abc123def456",
        built_at="2026-09-10T00:00:00+00:00",
        as_of=catalogue.as_of,
    )
    out = tmp_path / "api"
    write(out, [model], [bench], catalogue, build)

    identity = {
        "commit": "abc123def456",
        "built_at": "2026-09-10T00:00:00+00:00",
        "eligibility_as_of": "2026-09-01",
        "export_schema_version": EXPORT_SCHEMA_VERSION,
    }
    build_file = json.loads((out / "build.json").read_text(encoding="utf-8"))
    assert build_file == identity
    assert "schema_version" not in build_file

    index = json.loads((out / "index.json").read_text(encoding="utf-8"))
    assert index["build"] == identity
    assert "schema_version" not in index

    card = json.loads((out / "models/prov/one.json").read_text(encoding="utf-8"))
    assert card["build"] == identity

    catalogue_file = json.loads((out / "catalogue.json").read_text(encoding="utf-8"))
    assert catalogue_file["build"] == identity

    page = json.loads((out / "benchmarks/humaneval.json").read_text(encoding="utf-8"))
    assert page["build"] == identity
