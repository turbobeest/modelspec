"""MODEL-348 collector runs offline and retains every input without writing outcomes."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
import yaml

from decision.model import Verification, VerificationActor, VerificationTarget, value_hash
from decision.sources import CopyStore, FetchResult, load_sources
from decision.verify import Queue, StoredRegions, VerificationLog, deterministic_extractors, verify
from scripts.model_348_architecture import collect, resolve_repo

SHA = "a" * 40
API = "https://huggingface.co/api/models/lab/Alpha"
CONFIG = f"https://huggingface.co/lab/Alpha/resolve/{SHA}/config.json"
README = f"https://huggingface.co/lab/Alpha/raw/{SHA}/README.md"


def tree(root, total=703):
    (root / "models" / "lab").mkdir(parents=True)
    (root / "premier").mkdir()
    (root / "registry").mkdir()
    (root / "premier" / "slice-1.yaml").write_text(
        yaml.safe_dump(
            {
                "models": [
                    {"model_id": "lab/alpha", "open_weights": True},
                ]
            }
        )
    )
    (root / "registry" / "sources.yaml").write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "sources": [
                    {
                        "id": "model-174-alpha",
                        "url": API,
                        "normaliser": "text-default",
                        "cited_regions": [{"id": "rows", "locator": {"kind": "page", "value": ""}}],
                    },
                ],
            },
            sort_keys=False,
        )
    )
    card = {
        "model_id": "lab/alpha",
        "display_name": "Alpha",
        "card_updated": "2026-09-28",
        "sources": {"huggingface_url": "https://huggingface.co/lab/Alpha"},
        "architecture": {
            "type": None,
            "total_parameters": total,
            "active_parameters": None,
            "num_experts": None,
            "experts_per_token": None,
            "num_layers": 32,
        },
        "facts": [
            {
                "facet": "model.parameters_total",
                "value": total,
                "state": "known",
                "sources": [
                    {
                        "source_id": "model-174-alpha",
                        "snapshot_ref": "sha256:" + "b" * 64,
                        "cited_regions": ["rows"],
                    }
                ],
            }
        ],
    }
    (root / "models" / "lab" / "alpha.md").write_text(
        "---\n" + yaml.safe_dump(card, sort_keys=False) + "---\n\nCard body.\n"
    )
    VerificationLog(root / "verification").append(
        Verification(
            target=VerificationTarget(
                kind="fact", id="lab/alpha#model.parameters_total", value_hash=value_hash(total)
            ),
            collector=VerificationActor(
                agent="old-collector", model_family="openai", method="hf-api"
            ),
            verifier=VerificationActor(
                agent="verifier", model_family="deterministic", method="census"
            ),
            method="census",
            outcome="verified",
            date=date(2026, 10, 10),
        )
    )


class FakeFetcher:
    def __init__(self, config, readme="# Alpha\nAlpha is released.", api_config=None, census=None):
        self.calls = []
        self.bodies = {
            API: json.dumps(
                {
                    "id": "lab/Alpha",
                    "sha": SHA,
                    "config": api_config or {"architectures": ["AlphaModel"]},
                    "safetensors": census or {"total": 2, "parameters": {"BF16": 700, "F32": 3}},
                }
            ).encode(),
            CONFIG: json.dumps(config, indent=2).encode() if config is not None else None,
            README: readme.encode(),
        }

    def fetch(self, url, **kwargs):
        self.calls.append(url)
        body = self.bodies[url]
        return (
            FetchResult("ok", 200, body=body, content_type="text/plain")
            if body is not None
            else FetchResult("unreachable", 401, error="HTTP 401")
        )


def bytes_in(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def test_dry_run_fetches_pinned_copies_and_leaves_data_byte_for_byte_unchanged(tmp_path):
    root = tmp_path / "data"
    tree(root)
    before = bytes_in(root)
    fetcher = FakeFetcher({"model_type": "llama", "num_attention_heads": 32})
    report = tmp_path / "scratch" / "report.json"
    payload = collect(root, dry_run=True, fetcher=fetcher, report_path=report)
    assert bytes_in(root) == before
    assert fetcher.calls == [API, CONFIG, README]
    assert json.loads(report.read_text()) == payload
    rows = {r["facet"]: r for r in payload["rows"]}
    assert rows["model.architecture"]["value"] == "dense-transformer"
    assert rows["model.parameters_total"]["value"] == 703
    assert rows["model.parameters_active"]["value"] == 703
    assert rows["model.parameters_active"]["methods"] == ["dense-active-equals-total@1"]
    assert {r["url"] for r in rows["model.parameters_active"]["sources"]} == {API, CONFIG, README}
    assert rows["model.experts_total"]["state"] == "dense_exempt"
    assert rows["model.experts_per_token"]["state"] == "dense_exempt"
    store = CopyStore(Path(payload["copy_store"]))
    assert all(
        store.has(ref["snapshot_ref"]) for row in payload["rows"] for ref in row.get("sources", [])
    )


def test_gated_config_uses_public_api_and_readme_and_reports_checked_sources(tmp_path):
    tree(tmp_path)
    fetcher = FakeFetcher(
        None,
        "# Alpha\n| Activated Params | 32B |",
        api_config={
            "architectures": ["AlphaMoeForCausalLM"],
            "model_type": "alpha_moe",
            "tokenizer_config": {"bos_token": "<bos>"},
        },
    )
    rows = {
        r["facet"]: r
        for r in collect(
            tmp_path, dry_run=True, fetcher=fetcher, store=CopyStore(tmp_path.parent / "copies")
        )["rows"]
    }
    assert rows["model.parameters_active"]["value"] == 32_000_000_000
    for facet in ("model.architecture", "model.experts_total", "model.experts_per_token"):
        assert rows[facet]["state"] == "missing"
        assert rows[facet]["value"] is None
        assert "no retained config.json" in rows[facet]["reason"]
    assert list(rows["model.architecture"]["failures"].values()) == ["HTTP 401"]


def test_collection_files_facts_and_legacy_values_but_only_verifier_writes_outcomes(tmp_path):
    tree(tmp_path)
    logfile = tmp_path / "verification" / "log.jsonl"
    before_log = logfile.read_bytes()
    store = CopyStore(tmp_path / "copies")
    payload = collect(
        tmp_path,
        dry_run=False,
        fetcher=FakeFetcher(
            {
                "model_type": "deepseek_v3",
                "n_routed_experts": 256,
                "n_shared_experts": 1,
                "num_experts_per_tok": 8,
            },
            "# Alpha\nAlpha has 37B activated parameters.",
        ),
        store=store,
    )
    assert logfile.read_bytes() == before_log
    front = yaml.safe_load(
        (tmp_path / "models" / "lab" / "alpha.md").read_text().split("---", 2)[1]
    )
    assert front["architecture"] == {
        "type": "MoE",
        "total_parameters": 703,
        "active_parameters": 37_000_000_000,
        "num_experts": 256,
        "experts_per_token": 8,
        "num_layers": 32,
    }
    facts = {f["facet"]: f for f in front["facts"]}
    assert len(facts) == 5
    assert facts["model.parameters_active"]["value"] == 37_000_000_000
    assert all("verification" not in f for f in front["facts"])
    assert (tmp_path / "models" / "lab" / "alpha.md").read_text().endswith("Card body.\n")
    pending, unknown = Queue(tmp_path / "verification").pending()
    assert not unknown and len(pending) == 5
    sources = load_sources(tmp_path / "registry" / "sources.yaml")
    assert sources["model-174-alpha"].kind == "weights_repository"
    regions = StoredRegions(store, sources)
    for c in pending:
        assert (
            verify(c, regions, deterministic_extractors(), today=date(2026, 10, 10)).outcome
            == "verified"
        )
    assert payload["problems"] == []


def test_undisclosed_active_parameters_are_sourced_and_queued(tmp_path):
    tree(tmp_path)
    collect(
        tmp_path,
        dry_run=False,
        fetcher=FakeFetcher({"model_type": "deepseek_v3", "num_experts": 8}),
        store=CopyStore(tmp_path / "copies"),
    )
    claims, _ = Queue(tmp_path / "verification").pending()
    active = next(c for c in claims if c.field == "model.parameters_active")
    assert active.value is None
    front = yaml.safe_load(
        (tmp_path / "models" / "lab" / "alpha.md").read_text().split("---", 2)[1]
    )
    fact = next(f for f in front["facts"] if f["facet"] == "model.parameters_active")
    assert fact["state"] == "not_disclosed"
    assert len(fact["checked_sources"]) == 3
    assert len(fact["sources"]) == 3


def test_disagree_and_failed_retained_copy_check_refuse_all_data_writes(tmp_path, capsys):
    tree(tmp_path, total=704)
    before = bytes_in(tmp_path)
    with pytest.raises(ValueError, match="retained API total 703 != verified total 704"):
        collect(
            tmp_path,
            dry_run=False,
            fetcher=FakeFetcher({"num_attention_heads": 32}),
            store=CopyStore(tmp_path.parent / "copies"),
        )
    assert "DISAGREE lab/alpha architecture.total_parameters 704 -> 703" in capsys.readouterr().out
    assert bytes_in(tmp_path) == before


@pytest.mark.parametrize(
    "readme",
    [
        "# Alpha\n| Property | Alpha |\n| Activated Params | 8B / 16B |\n",
        "# Alpha\nAlpha activates 3B parameters per token.\n",
        "# Alpha\n- Number of Parameters: 30B with 3B activated\n",
    ],
)
def test_unparsed_active_wording_is_a_reported_gap_and_never_filed(tmp_path, readme):
    tree(tmp_path)
    payload = collect(
        tmp_path,
        dry_run=False,
        fetcher=FakeFetcher({"model_type": "deepseek_v3", "num_experts": 8}, readme),
        store=CopyStore(tmp_path / "copies"),
    )
    active = next(row for row in payload["rows"] if row["facet"] == "model.parameters_active")
    assert active["state"] == "missing"
    assert active["value"] is None
    assert "wording" in active["reason"]
    assert readme.splitlines()[-1] in active["reason"]
    front = yaml.safe_load(
        (tmp_path / "models" / "lab" / "alpha.md").read_text().split("---", 2)[1]
    )
    assert "model.parameters_active" not in {fact["facet"] for fact in front["facts"]}
    pending, _ = Queue(tmp_path / "verification").pending()
    assert "model.parameters_active" not in {c.field for c in pending}
    assert payload["problems"] == []


def test_missing_config_never_files_config_absence_facts(tmp_path):
    tree(tmp_path)
    collect(
        tmp_path,
        dry_run=False,
        fetcher=FakeFetcher(None),
        store=CopyStore(tmp_path / "copies"),
    )
    pending, _ = Queue(tmp_path / "verification").pending()
    assert {c.field for c in pending} == {"model.parameters_total", "model.parameters_active"}


def test_parameter_field_shorthand_is_verified_from_the_card_and_verified_total(tmp_path):
    tree(tmp_path, total=4_919_641_986)
    store = CopyStore(tmp_path / "copies")
    collect(
        tmp_path,
        dry_run=False,
        fetcher=FakeFetcher(
            {"model_type": "deepseek_v3", "num_experts": 128},
            "# Alpha\n### Model Description\n- **Number of Total Parameters:** 4.92B-A0.43B",
            census={"parameters": {"BF16": 4_919_641_986}},
        ),
        store=store,
    )
    pending, _ = Queue(tmp_path / "verification").pending()
    active = next(c for c in pending if c.field == "model.parameters_active")
    assert active.value == 430_000_000
    regions = StoredRegions(store, load_sources(tmp_path / "registry" / "sources.yaml"))
    result = verify(active, regions, deterministic_extractors(), today=date(2026, 10, 10))
    assert result.outcome == "verified"
    assert result.verification.method == "model-card-params@1"
    assert {regions.source_url(ref.source_id) for ref in active.sources} == {API, README}


def test_repo_resolution_refuses_conflicting_variants():
    assert resolve_repo({"huggingface": "https://huggingface.co/lab/Alpha", "facts": []}, {}) == (
        "lab/Alpha",
        None,
    )
    assert resolve_repo(
        {"huggingface": "lab/Alpha", "links": ["https://huggingface.co/lab/Beta"]}, {}
    ) == (None, None)


def test_dry_run_refuses_artifact_paths_inside_the_data_checkout(tmp_path):
    tree(tmp_path)
    before = bytes_in(tmp_path)
    with pytest.raises(ValueError, match="outside the data checkout"):
        collect(
            tmp_path,
            dry_run=True,
            report_path=tmp_path / "report.json",
            fetcher=FakeFetcher({"num_attention_heads": 32}),
        )
    assert bytes_in(tmp_path) == before


@pytest.mark.parametrize(
    "config,facet",
    [
        ({"model_type": "qwen4", "num_attention_heads": 32}, "model.architecture"),
        ({"model_type": "qwen4", "num_attention_heads": 32}, "model.experts_total"),
        (
            {"model_type": "x_moe", "num_experts": [64, 128], "num_experts_per_tok": 8},
            "model.experts_total",
        ),
        (
            {"model_type": "llama", "num_attention_heads": 32, "moe_intermediate_size": 1408},
            "model.architecture",
        ),
        ({"model_type": "mixtral", "num_experts": 8}, "model.experts_per_token"),
    ],
)
def test_round4_unreadable_config_facets_are_gaps_and_never_filed(tmp_path, config, facet):
    tree(tmp_path)
    payload = collect(
        tmp_path, dry_run=False, fetcher=FakeFetcher(config), store=CopyStore(tmp_path / "copies")
    )
    row = next(row for row in payload["rows"] if row["facet"] == facet)
    assert (row["state"], row["value"]) == ("missing", None)
    pending, _ = Queue(tmp_path / "verification").pending()
    assert facet not in {c.field for c in pending}
    front = yaml.safe_load((tmp_path / "models/lab/alpha.md").read_text().split("---", 2)[1])
    assert facet not in {fact["facet"] for fact in front["facts"]}
    assert payload["problems"] == []


def test_round4_multimodal_gap_reports_card_total_and_vision_encoder(tmp_path):
    tree(tmp_path, total=31_273_088_876)
    payload = collect(
        tmp_path,
        dry_run=True,
        fetcher=FakeFetcher(
            {
                "model_type": "gemma4",
                "text_config": {
                    "model_type": "gemma4_text",
                    "num_attention_heads": 32,
                    "hidden_size_per_layer_input": 0,
                    "vocab_size_per_layer_input": 262144,
                },
                "vision_config": {"model_type": "gemma4_vision", "num_attention_heads": 16},
                "enable_moe_block": False,
                "num_experts": None,
            },
            (
                "# Alpha\n| Property | Alpha |\n| Total Parameters | 30.7B |\n| Vision Encoder "
                "Parameters | ~550M |\nBeta has 2B effective parameters."
            ),
            census={"parameters": {"BF16": 31_273_088_876}},
        ),
        store=CopyStore(tmp_path.parent / "copies"),
    )
    active = next(row for row in payload["rows"] if row["facet"] == "model.parameters_active")
    assert (active["state"], active["value"]) == ("missing", None)
    assert "30.7B" in active["reason"]
    assert "~550M" in active["reason"]
    assert "non-text encoder" in active["reason"]
    assert payload["problems"] == []


def test_round4_missing_readme_leaves_active_count_as_a_gap(tmp_path):
    tree(tmp_path)
    fetcher = FakeFetcher({"model_type": "llama", "num_attention_heads": 32})
    fetcher.bodies[README] = None
    payload = collect(
        tmp_path, dry_run=False, fetcher=fetcher, store=CopyStore(tmp_path / "copies")
    )
    active = next(row for row in payload["rows"] if row["facet"] == "model.parameters_active")
    assert (active["state"], active["value"]) == ("missing", None)
    pending, _ = Queue(tmp_path / "verification").pending()
    assert "model.parameters_active" not in {c.field for c in pending}
    assert payload["problems"] == []
