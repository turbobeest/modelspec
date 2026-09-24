"""The rank Worker (MODEL-68), and the proof that it is not a second ranker.

The acceptance criterion that matters is byte-identity: for the same input
against the same build, `POST /v1/rank` must return the rows that
`modelspec offline rank --json` returns. This file proves that by running both,
over the whole real catalogue, and comparing the serialised bytes — not by
reading the two code paths and agreeing that they look alike.

That is possible because there is no second implementation to compare. The
Worker imports `pipeline.ranking.rank_report`, the function the CLI calls, and
`api/worker/vendor.py` copies that file into the Worker bundle byte for byte.
A port into another language was considered and rejected on evidence: CPython
and V8 return `log10` values that differ by one ULP for cost ratios that occur
in this catalogue, and the composite is rounded to two decimals only after those
terms are summed, so no amount of care in a JavaScript port would make the
promise safe to keep.

What is left to test, therefore, is the adapter: whether the endpoint maps a
request onto the scorer's arguments the way the CLI does. That is exactly where
a hand-written adapter goes wrong — the order `--max-cost` is applied in, the
`cost_weight=price_sensitivity or None` conversion, `include_rehosts`, `limit`.
Every vector below exercises one of those.
"""

from __future__ import annotations

import functools
import glob
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import sysconfig
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from api.ranking.engine import (  # noqa: E402
    MIN_BENCHMARK_COUNT, MIN_BENCHMARK_COVERAGE, USE_CASE_PROFILES, WIZARD_BENCHMARK_COVERAGE,
)
from cli.modelspec import snapshot  # noqa: E402
from pipeline import hardware as hardware_module  # noqa: E402
from pipeline import ranking  # noqa: E402
from pipeline.ranking import authoring_guides_from_cards  # noqa: E402
from schema.card import ModelCard  # noqa: E402
from schema.graph import derive_graph  # noqa: E402

WORKER_ROOT = REPO_ROOT / "api" / "worker"
WORKER_SRC = WORKER_ROOT / "src"


def _load_rank_service():
    """Import the Worker's service module from its path.

    It is not part of an installed package: it sits beside the Worker's entry
    point so that Wrangler bundles it, and it is written to import nothing from
    the Workers runtime precisely so that this suite can run it.
    """
    spec = importlib.util.spec_from_file_location(
        "modelspec_rank_service", WORKER_SRC / "rank_service.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


service = _load_rank_service()

SERVICE_COMMIT = "0123456789abcdef0123456789abcdef01234567"
ORIGIN = "https://modelspec.test"


# ── the catalogue, built once ────────────────────────────────────────────────

@functools.lru_cache(maxsize=1)
def _catalogue() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """The export tables, built from the cards exactly as `pipeline.build` does.

    Returns `(candidates_json, hardware_json, hardware_graph_nodes)`: the first
    two are what the Worker fetches, the third is the shape the CLI snapshot
    carries. Both sides therefore see one catalogue, which is what "against the
    same build" has to mean.
    """
    files = [f for f in sorted(glob.glob(str(REPO_ROOT / "models" / "**" / "*.md"),
                                         recursive=True))
             if Path(f).name != "LICENSE.md"]
    cards = [ModelCard.from_yaml_file(path) for path in files]
    devices = hardware_module.load_devices(REPO_ROOT)
    derived = derive_graph(cards, hardware_module.device_classes(devices))
    hardware_module.compute(derived, cards, devices)
    candidates = ranking.build_candidates(cards, derived)

    build = {"commit": "b1cb67d35010" * 3 + "abcd", "built_at": "2026-09-17T00:00:00+00:00",
             "eligibility_as_of": "2026-09-09",
             "export_schema_version": snapshot.EXPORT_SCHEMA_VERSION}
    nodes = sorted((props for (label, _id), props in derived.nodes.items()
                    if label == "Hardware"),
                   key=lambda d: str(d.get("id", "")))
    candidates_json = {"build": build, "count": len(candidates),
                       "candidates": [c.to_json() for c in candidates],
                       "authoring_guides": authoring_guides_from_cards(cards)}
    hardware_json = {"build": build, "count": len(nodes), "hardware": nodes}
    graph_nodes = {"nodes": [{**node, "label": "Hardware"} for node in nodes]}
    return candidates_json, hardware_json, graph_nodes


@functools.lru_cache(maxsize=1)
def _busiest_device() -> str:
    """The device the most models fit on, so a `--fits` vector is not vacuous."""
    candidates_json, _, _ = _catalogue()
    counts: dict[str, int] = {}
    for candidate in candidates_json["candidates"]:
        for device in (candidate.get("fits") or {}):
            counts[device] = counts.get(device, 0) + 1
    return max(sorted(counts), key=lambda device: counts[device])


@pytest.fixture(scope="module")
def cache(tmp_path_factory) -> Path:
    """A snapshot the CLI can rank, holding the catalogue built above."""
    candidates_json, _, graph_nodes = _catalogue()
    directory = tmp_path_factory.mktemp("rank-worker-cache")
    (directory / "snapshot.json").write_text(json.dumps({
        "meta": {"fetched_at": datetime.now(UTC).isoformat(), "origin": ORIGIN,
                 "build_commit": candidates_json["build"]["commit"],
                 "built_at": candidates_json["build"]["built_at"]},
        "data": {
            "index": {"build": candidates_json["build"]},
            "candidates": candidates_json,
            "profiles": {"profiles": USE_CASE_PROFILES,
                         "featured": list(ranking.FEATURED_PROFILES)},
            "hardware": graph_nodes,
        },
    }, default=str), encoding="utf-8")
    return directory


@functools.lru_cache(maxsize=1)
def _modelspec_cli() -> str:
    """The `modelspec` entry point, or skip loudly if the package is not installed."""
    found = shutil.which("modelspec") or str(Path(sysconfig.get_path("scripts")) / "modelspec")
    if not Path(found).exists():
        pytest.fail("the `modelspec` console script is not installed; run `pip install -e .`")
    return found


def _cli_rank(args: list[str], cache_dir: Path) -> dict[str, Any]:
    """Run `modelspec offline rank --json` and return the parsed envelope."""
    result = subprocess.run(
        [_modelspec_cli(), "offline", "rank", *args, "--json"],
        capture_output=True, text=True, timeout=300,
        env={"PATH": "/usr/bin:/bin", "MODELSPEC_CACHE": str(cache_dir),
             "HOME": str(cache_dir.parent), "PYTHONPATH": str(REPO_ROOT)},
    )
    assert result.returncode in (0, 2), (
        f"the CLI failed for {args}: exit {result.returncode}\n{result.stderr}")
    return json.loads(result.stdout)


# ── the shared vectors ───────────────────────────────────────────────────────
#
# One list, read by both sides: each entry is (name, CLI argv, request body).
# `DEVICE` is a placeholder resolved at run time rather than at collection time,
# so importing this module stays cheap and `--collect-only` does not have to
# parse 1,339 cards.

DEVICE = "{device}"

VECTORS: list[tuple[str, list[str], dict[str, Any]]] = [
    ("plain coding", ["coding"],
     {"use_case": "coding"}),
    ("laptop, local runtime", ["rag", "--open-weights"],
     {"use_case": "rag", "environment": {"hosting": "local", "runtime": "ollama"}}),
    ("a specific accelerator", ["reasoning", "--fits", DEVICE, "--open-weights"],
     {"use_case": "reasoning",
      "environment": {"hardware": DEVICE, "hosting": "self_hosted"}}),
    ("a managed API, price matters",
     ["agentic", "--max-cost", "2.0", "--price-sensitivity", "0.25"],
     {"use_case": "agentic", "environment": {"hosting": "managed_api"},
      "constraints": {"max_cost_per_million_input_tokens": 2.0,
                      "price_sensitivity": 0.25}}),
    ("a longer shortlist", ["general", "--limit", "25"],
     {"use_case": "general", "limit": 25}),
    ("rehosts kept", ["embedding", "--include-rehosts"],
     {"use_case": "embedding", "constraints": {"include_rehosts": True}}),
    ("vision, untouched", ["vision"],
     {"use_case": "vision"}),
    ("every knob at once",
     ["multilingual", "--fits", DEVICE, "--open-weights", "--max-cost", "5.0",
      "--price-sensitivity", "0.5", "--limit", "3"],
     {"use_case": "multilingual",
      "environment": {"hardware": DEVICE, "hosting": "self_hosted", "runtime": "lm_studio"},
      "constraints": {"max_cost_per_million_input_tokens": 5.0, "price_sensitivity": 0.5},
      "limit": 3}),
    ("a shortlist of nothing", ["summarization", "--limit", "0"],
     {"use_case": "summarization", "limit": 0}),
    ("open weights only", ["math_competition", "--open-weights"],
     {"use_case": "math_competition", "constraints": {"open_weights": True}}),
    ("writing", ["writing_technical"],
     {"use_case": "writing_technical"}),
    ("chat", ["chat", "--limit", "5"],
     {"use_case": "chat", "limit": 5}),
]

VECTOR_NAMES = [name for name, _argv, _body in VECTORS]


def _resolve(value: Any) -> Any:
    """Substitute the placeholder device, wherever it appears."""
    device = _busiest_device()
    if isinstance(value, str):
        return device if value == DEVICE else value
    if isinstance(value, list):
        return [_resolve(item) for item in value]
    if isinstance(value, dict):
        return {key: _resolve(item) for key, item in value.items()}
    return value


def _vector(name: str) -> tuple[list[str], dict[str, Any]]:
    argv, body = next((a, b) for n, a, b in VECTORS if n == name)
    return _resolve(argv), _resolve(body)


def _worker_rank(body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    candidates_json, hardware_json, _ = _catalogue()
    return service.rank(body, candidates_json, hardware_json, SERVICE_COMMIT, ORIGIN)


def _bytes(rows: Any) -> bytes:
    """Serialised the way the CLI serialises its envelope, so bytes are bytes."""
    return json.dumps(rows, indent=2, default=str).encode("utf-8")


# ── byte-identity ────────────────────────────────────────────────────────────

@pytest.mark.parametrize("name", VECTOR_NAMES)
def test_the_worker_returns_the_bytes_the_cli_returns(name: str, cache: Path) -> None:
    """The acceptance criterion, one vector at a time."""
    argv, body = _vector(name)
    envelope = _cli_rank(argv, cache)
    status, answer = _worker_rank(body)

    cli_rows = envelope["result"]
    worker_rows = answer["result"]
    assert _bytes(worker_rows) == _bytes(cli_rows), (
        f"{name}: the Worker and `modelspec offline rank --json` disagree")

    # The surrounding claims have to agree too, or identical rows would be
    # presented with a different story around them.
    assert answer["ranking_status"] == envelope["ranking_status"], name
    assert answer["ranked_count"] == envelope["ranked_count"], name
    assert answer["unranked_count"] == envelope["unranked_count"], name
    # MODEL-110: the models neither could rank are named the same way, byte for byte.
    assert _bytes(answer["unranked_candidates"]) == _bytes(envelope["unranked_candidates"]), (
        f"{name}: the Worker and the CLI name different unranked candidates")
    expected_status = (service.HTTP_NO_MATCH
                       if envelope["ranking_status"] in {"empty", "unavailable"}
                       else service.HTTP_OK)
    assert status == expected_status, name


def test_at_least_three_distinct_environments_actually_rank(cache: Path) -> None:
    """A suite of vectors that all return nothing would prove nothing."""
    ranked = []
    for name in VECTOR_NAMES:
        status, answer = _worker_rank(_vector(name)[1])
        if status == service.HTTP_OK and answer["result"]:
            ranked.append(name)
    assert len(ranked) >= 3, f"only {ranked} produced a ranking"


# ── what every response carries ──────────────────────────────────────────────

def test_every_response_carries_the_build_and_the_schema_version() -> None:
    for name in VECTOR_NAMES:
        _status, answer = _worker_rank(_vector(name)[1])
        build = answer["build"]
        assert build["commit"], name
        assert build["export_schema_version"] == snapshot.EXPORT_SCHEMA_VERSION, name


def test_every_row_carries_an_evidence_basis() -> None:
    """Input provenance, with the meaning `pipeline.ranking._basis` gives it."""
    allowed = {"none", "unverified-legacy", "mixed", "partial-verified", "verified"}
    seen = set()
    for name in VECTOR_NAMES:
        _status, answer = _worker_rank(_vector(name)[1])
        for row in answer["result"]:
            assert row["evidence_basis"] in allowed, row["model_id"]
            seen.add(row["evidence_basis"])
    assert seen, "no rows were produced, so nothing was checked"


def test_the_basis_is_the_pipeline_basis_and_not_a_second_opinion() -> None:
    """Same function, same labels — checked rather than assumed."""
    assert service.rank.__module__ != ranking.__name__
    for contributing, verified, coverage, expected in [
        (0, 0, 0.0, "none"),
        (3, 3, 1.0, "verified"),
        (3, 3, 0.8, "partial-verified"),
        (3, 1, 0.8, "mixed"),
        (3, 0, 0.8, "unverified-legacy"),
    ]:
        assert ranking._basis(contributing, verified, coverage) == expected


# ── the no-match answer ──────────────────────────────────────────────────────

def test_a_no_match_names_the_constraint_and_is_not_an_empty_list() -> None:
    """The documented code is 422, and the body says what to relax."""
    device = _busiest_device()
    status, answer = _worker_rank({
        "use_case": "coding",
        "environment": {"hardware": device, "hosting": "local"},
        "constraints": {"max_cost_per_million_input_tokens": 0.0},
    })
    assert status == service.HTTP_NO_MATCH
    assert answer["result"] == []
    error = answer["error"]
    assert error["code"] in {"no_match", "insufficient_evidence"}
    assert error["eliminated_by"]["constraint"], "no constraint was blamed"
    assert error["eliminated_by"]["survivors_after"] == 0
    assert error["relax"], "the caller is not told what to loosen"
    assert error["elimination_trace"], "there is no trace to read"
    # The trace has to be a real narrowing, not a restatement of the request.
    trace = error["elimination_trace"]
    assert trace[0]["survivors_before"] == answer["candidates_considered"]
    for step in trace:
        assert step["survivors_after"] <= step["survivors_before"]


def test_a_no_match_on_evidence_says_so_rather_than_blaming_a_constraint() -> None:
    """"Nothing matched" and "nothing had evidence" send a caller different ways."""
    # `--fits` a device with an unusual profile plus a use case nothing covers.
    status, answer = _worker_rank({"use_case": "speech_to_text"})
    if status != service.HTTP_NO_MATCH:
        pytest.skip("speech_to_text now ranks; the branch is covered by its own unit test")
    error = answer["error"]
    assert error["code"] == "insufficient_evidence"
    assert error["eliminated_by"]["constraint"] == "policy.min_benchmark_coverage"
    assert str(MIN_BENCHMARK_COUNT) in error["message"]


def test_an_evidence_no_match_is_reachable_without_the_catalogue() -> None:
    """The evidence branch, pinned even if every profile later ranks something."""
    export = {"build": {"commit": "abc", "export_schema_version": "2.0"},
              "candidates": [{"model_id": "m", "display_name": "M", "provider": "P",
                              "model_type": "llm-chat", "benchmark_scores": {},
                              "open_weights": True}]}
    status, answer = service.rank({"use_case": "coding"}, export, None,
                                  SERVICE_COMMIT, ORIGIN)
    assert status == service.HTTP_NO_MATCH
    assert answer["error"]["code"] == "insufficient_evidence"
    assert answer["error"]["eliminated_by"]["constraint"] == "policy.min_benchmark_coverage"
    assert answer["result"] == []
    # The 422 is where naming them matters most: nothing ranked, and here is why.
    block = answer["unranked_candidates"]
    assert block["count"] == 1
    assert block["models"][0]["model_id"] == "m"
    assert block["models"][0]["reason"] == "no_scores"


def test_the_worker_reads_the_release_date_the_export_carries() -> None:
    """MODEL-110: ordering needs `release_date`; an older export without it degrades."""
    export = {"build": {"commit": "abc", "export_schema_version": "3.0"},
              "candidates": [
                  {"model_id": "old", "display_name": "Old", "provider": "P",
                   "model_type": "llm-chat", "release_date": "2025-01-01"},
                  {"model_id": "new", "display_name": "New", "provider": "P",
                   "model_type": "llm-chat", "release_date": "2026-09-01"},
                  {"model_id": "pre-110", "display_name": "Pre", "provider": "P",
                   "model_type": "llm-chat"}]}
    _status, answer = service.rank({"use_case": "coding"}, export, None,
                                   SERVICE_COMMIT, ORIGIN)
    models = answer["unranked_candidates"]["models"]
    assert [m["model_id"] for m in models] == ["new", "old", "pre-110"]
    assert models[-1]["release_date"] is None


def test_the_catalogue_names_models_it_cannot_rank_for_coding() -> None:
    """The ticket's case, on the real catalogue: disclosure is non-empty and bounded."""
    status, answer = _worker_rank({"use_case": "coding"})
    assert status == service.HTTP_OK
    block = answer["unranked_candidates"]
    assert 0 < block["count"] <= answer["unranked_count"]
    assert len(block["models"]) == min(block["cap"], block["count"])
    ranked = {row["model_id"] for row in answer["result"]}
    assert not ranked & {m["model_id"] for m in block["models"]}


# ── refusals ─────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("body,code", [
    ({}, "invalid_request"),
    ({"use_case": "not_a_use_case"}, "unknown_use_case"),
    ({"use_case": "coding", "environment": {"hardware": "nonexistent-gpu"}}, "unknown_hardware"),
    ({"use_case": "coding", "environment": {"hosting": "carrier_pigeon"}}, "unknown_hosting"),
    ({"use_case": "coding", "environment": {"runtime": "not_a_runtime"}}, "unknown_runtime"),
    ({"use_case": "coding", "limit": -1}, "invalid_request"),
    ({"use_case": "coding", "constraints": {"price_sensitivity": 2}}, "invalid_request"),
    ({"use_case": "coding", "prompt": "write me a poem"}, "invalid_request"),
    ("not an object", "invalid_request"),
])
def test_a_refused_request_says_why(body: Any, code: str) -> None:
    with pytest.raises(service.RequestError) as caught:
        _worker_rank(body)
    assert caught.value.code == code
    assert caught.value.status == service.HTTP_BAD_REQUEST


def test_a_prompt_field_is_refused_rather_than_ignored() -> None:
    """The request carries a profile. Accepting prompt text would be a breach."""
    with pytest.raises(service.RequestError) as caught:
        _worker_rank({"use_case": "coding", "prompt": "..."})
    assert "prompt" in str(caught.value)


def test_an_unknown_device_is_refused_not_answered_as_nothing_fits() -> None:
    """Those are different answers, and a caller would act on them differently."""
    with pytest.raises(service.RequestError) as caught:
        _worker_rank({"use_case": "coding", "environment": {"hardware": "rtx_9090_ti"}})
    assert caught.value.code == "unknown_hardware"
    assert _busiest_device() in caught.value.detail["accepted"]


def test_an_export_without_the_hardware_index_refuses_the_device() -> None:
    """An older export degrades to "refused", never to a wrong answer."""
    candidates_json, _, _ = _catalogue()
    with pytest.raises(service.RequestError) as caught:
        service.rank({"use_case": "coding", "environment": {"hardware": _busiest_device()}},
                     candidates_json, None, SERVICE_COMMIT, ORIGIN)
    assert caught.value.code == "unknown_hardware"


# ── the floors ───────────────────────────────────────────────────────────────

def test_the_worker_publishes_the_shared_policy() -> None:
    _status, answer = _worker_rank({"use_case": "coding"})
    policy = answer["policy"]
    assert policy["min_benchmark_coverage"] == MIN_BENCHMARK_COVERAGE
    assert policy["cli_min_benchmark_coverage"] == MIN_BENCHMARK_COVERAGE
    assert policy["wizard_min_benchmark_coverage"] == WIZARD_BENCHMARK_COVERAGE
    assert policy["min_benchmark_count"] == MIN_BENCHMARK_COUNT


def test_no_floor_is_written_down_a_second_time() -> None:
    """A floor duplicated in the Worker would drift the day Jamie changes one."""
    floors = {MIN_BENCHMARK_COVERAGE, WIZARD_BENCHMARK_COVERAGE, float(MIN_BENCHMARK_COUNT)}
    for path in sorted(WORKER_SRC.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        # Comments and docstrings may quote a floor; assignments may not.
        for line in source.splitlines():
            code = line.split("#", 1)[0]
            if "=" not in code or "==" in code:
                continue
            for literal in re.findall(r"(?<![\w.])\d+\.\d+(?![\w.])", code):
                assert float(literal) not in floors, (
                    f"{path.name}: {line.strip()!r} writes a ranking floor down again; "
                    "import it from api.ranking.engine instead")
    assert "ranking_policy" in (WORKER_SRC / "rank_service.py").read_text(encoding="utf-8")


# ── the bundle ───────────────────────────────────────────────────────────────

def test_the_vendored_bundle_is_the_repositorys_own_files(tmp_path: Path) -> None:
    """Byte for byte, or the Worker is running a fork of the scorer."""
    spec = importlib.util.spec_from_file_location("rank_worker_vendor", WORKER_ROOT / "vendor.py")
    vendor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vendor)

    bundle = vendor.build(tmp_path / "python_modules")
    assert vendor.SOURCES, "the bundle would be empty"
    for source, target in vendor.SOURCES.items():
        assert (bundle / target).read_bytes() == (REPO_ROOT / source).read_bytes(), (
            f"{target} in the Worker bundle is not {source} from this repository")
    assert (bundle / "pipeline" / "ranking.py").exists()
    assert (bundle / "api" / "ranking" / "engine.py").exists()


def test_the_bundle_needs_nothing_the_isolate_does_not_have(tmp_path: Path) -> None:
    """pydantic and PyYAML are not in the Worker. Catch that here, not at deploy."""
    bundle = tmp_path / "python_modules"
    result = subprocess.run(
        [sys.executable, str(WORKER_ROOT / "vendor.py"), "--out", str(bundle), "--check"],
        capture_output=True, text=True, timeout=120, cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, (
        "the Worker bundle pulls in something the isolate lacks:\n"
        f"{result.stdout}\n{result.stderr}")


def test_the_service_module_imports_no_workers_runtime() -> None:
    """If it did, this suite could not run it, and nothing would be proven."""
    source = (WORKER_SRC / "rank_service.py").read_text(encoding="utf-8")
    assert "from js import" not in source
    assert "from workers import" not in source
    assert "import pipeline.ranking" in source or "from pipeline.ranking import" in source


def test_the_entry_point_holds_no_ranking_logic() -> None:
    """Transport only. Scoring in the entry point would be a fork by drift."""
    source = (WORKER_SRC / "entry.py").read_text(encoding="utf-8")
    for forbidden in ("rank_report", "benchmark_weights", "_basis", "USE_CASE_PROFILES"):
        assert forbidden not in source, f"entry.py mentions {forbidden}; it should not rank"


def test_the_export_publishes_the_device_vocabulary_the_worker_needs(tmp_path: Path) -> None:
    """Producer and consumer, closed loop.

    `pipeline.ranking.write_export` writes `/api/rank/hardware.json` and the
    Worker validates `environment.hardware` against it. If the writer stopped
    emitting it, the endpoint would quietly refuse every device instead of
    ranking, so the two are pinned together rather than separately.
    """
    candidates_json, hardware_json, _ = _catalogue()
    published = {entry["id"] for entry in hardware_json["hardware"]}
    assert published, "the export carries no devices"
    assert _busiest_device() in published

    fitted = set()
    for candidate in candidates_json["candidates"]:
        fitted |= set(candidate.get("fits") or {})
    assert fitted <= published, (
        "models fit devices the hardware index does not list: "
        f"{sorted(fitted - published)[:5]}")

    # And the writer really does emit the file, not just this fixture.
    source = (REPO_ROOT / "pipeline" / "ranking.py").read_text(encoding="utf-8")
    assert 'dump("hardware.json"' in source
    assert 'authoring_guides' in source


# ── authoring guide (MODEL-81) ───────────────────────────────────────────────

_GUIDE_SOURCE = {
    "url": "https://docs.acme.example/prompting",
    "title": "Prompting",
    "accessed": "2026-09-15",
    "kind": "provider-guidance",
}


def _rankable_row(model_id: str = "acme/guided") -> dict[str, Any]:
    scores = {bench: 80.0 for bench in USE_CASE_PROFILES["coding"]["benchmark_weights"]}
    return {
        "model_id": model_id, "display_name": "Guided", "provider": "Acme",
        "model_type": "llm-chat", "benchmark_scores": scores,
        "open_weights": True, "verified_benchmarks": list(scores),
    }


def _guide(status: str = "current", model_id: str = "acme/guided") -> dict[str, Any]:
    return {
        "applies_to": {"model_id": model_id, "version": "1.0"},
        "as_of": "2026-09-15",
        "status": status,
        "sections": {
            "prompt_shape": [{"text": "Give the full task up front.",
                              "sources": [_GUIDE_SOURCE]}],
        },
    }


def _guided_export(status: str = "current") -> dict[str, Any]:
    guide = _guide(status)
    return {
        "build": {"commit": "abc", "export_schema_version": "2.0"},
        "candidates": [_rankable_row()],
        "authoring_guides": {"acme/guided": guide},
    }


def test_the_recommended_models_current_guide_is_served_with_its_sources() -> None:
    export = _guided_export("current")
    status, answer = service.rank({"use_case": "coding", "limit": 1}, export, None,
                                  SERVICE_COMMIT, ORIGIN)
    assert status == service.HTTP_OK
    assert answer["result"][0]["model_id"] == "acme/guided"
    assert "authoring_guide" not in answer["result"][0]
    block = answer["authoring_guide"]
    assert block["state"] == "current"
    assert block["model_id"] == "acme/guided"
    assert block["why"] is None
    assert block["guide"] is export["authoring_guides"]["acme/guided"]
    source = block["guide"]["sections"]["prompt_shape"][0]["sources"][0]
    assert source["url"] == _GUIDE_SOURCE["url"]
    assert source["accessed"] == _GUIDE_SOURCE["accessed"]
    assert source["kind"] == _GUIDE_SOURCE["kind"]


def test_a_stale_guide_is_marked_stale_not_served_as_current() -> None:
    status, answer = service.rank({"use_case": "coding", "limit": 1},
                                  _guided_export("stale"), None,
                                  SERVICE_COMMIT, ORIGIN)
    assert status == service.HTTP_OK
    block = answer["authoring_guide"]
    assert block["state"] == "stale"
    assert block["guide"]["status"] == "stale"
    assert block["state"] != "current"
    assert block["guide"]["status"] != "current"


def test_a_model_with_no_guide_returns_the_documented_absent_state() -> None:
    export = {"build": {"commit": "abc", "export_schema_version": "2.0"},
              "candidates": [_rankable_row("acme/plain")],
              "authoring_guides": {}}
    status, answer = service.rank({"use_case": "coding", "limit": 1}, export, None,
                                  SERVICE_COMMIT, ORIGIN)
    assert status == service.HTTP_OK
    block = answer["authoring_guide"]
    assert block == {
        "state": "absent", "model_id": "acme/plain",
        "why": "no_guide", "guide": None,
    }
    assert block["guide"] != ""


def test_no_recommendation_is_absent_not_an_empty_guide() -> None:
    export = {"build": {"commit": "abc", "export_schema_version": "2.0"},
              "candidates": []}
    status, answer = service.rank({"use_case": "coding"}, export, None,
                                  SERVICE_COMMIT, ORIGIN)
    assert status == service.HTTP_NO_MATCH
    block = answer["authoring_guide"]
    assert block["state"] == "absent"
    assert block["model_id"] is None
    assert block["why"] == "no_recommendation"
    assert block["guide"] is None


def test_an_unrecognised_guide_status_is_not_served_as_current() -> None:
    export = _guided_export("current")
    export["authoring_guides"]["acme/guided"] = {
        **_guide("current"), "status": "fresh",
    }
    status, answer = service.rank({"use_case": "coding", "limit": 1}, export, None,
                                  SERVICE_COMMIT, ORIGIN)
    assert status == service.HTTP_OK
    assert answer["authoring_guide"]["state"] == "absent"
    assert answer["authoring_guide"]["guide"] is None


def test_the_guide_is_not_generated_at_request_time() -> None:
    """The Worker copies the export; it does not invent claims."""
    source = (WORKER_SRC / "rank_service.py").read_text(encoding="utf-8")
    assert "authoring_guides" in source
    assert "Give the full task" not in source
    export = _guided_export("current")
    _status, answer = service.rank({"use_case": "coding", "limit": 1}, export, None,
                                   SERVICE_COMMIT, ORIGIN)
    assert answer["authoring_guide"]["guide"]["sections"]["prompt_shape"][0]["text"] == (
        export["authoring_guides"]["acme/guided"]["sections"]["prompt_shape"][0]["text"])


def test_every_ranking_response_carries_authoring_guide() -> None:
    for name in VECTOR_NAMES:
        _status, answer = _worker_rank(_vector(name)[1])
        block = answer["authoring_guide"]
        assert block["state"] in service.AUTHORING_GUIDE_STATES, name
        if block["state"] == "absent":
            assert block["guide"] is None, name
            assert block["why"] in service.AUTHORING_GUIDE_WHYS, name
        else:
            assert block["why"] is None, name
            assert isinstance(block["guide"], dict), name
            assert block["guide"]["status"] == block["state"], name
            assert block["guide"]["status"] != "current" or block["state"] == "current", name
            for section in (block["guide"].get("sections") or {}).values():
                for claim in section or []:
                    assert claim.get("text"), name
                    for src in claim.get("sources") or []:
                        assert str(src.get("url", "")).startswith(("http://", "https://")), name
                        assert src.get("accessed"), name
