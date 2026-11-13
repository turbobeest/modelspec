"""Scope a queued signal with the watcher's Hugging Face rules when it is processed."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from release_signals.pipeline import FetchResult, clear_catalogue_cache
from scripts import process_release_signals as processor

HUB_UNREAD = "Hub metadata could not be read"
ORG = "acme-lab"
PAGE_HOST = "models.acme.example"


@pytest.fixture(autouse=True)
def _clear_catalogue_index() -> None:
    clear_catalogue_cache()


class _PriceFetcher:
    credits_spent = 0


def _card(root: Path) -> None:
    path = root / "models" / "acme" / "orbit-1.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        "model_id: acme/orbit-1\n"
        "display_name: Orbit 1\n"
        "provider: acme\n"
        "provider_display: Acme\n"
        "version: orbit-1\n"
        "---\n",
        encoding="utf-8",
    )


def _watch(root: Path, *, lab_page: bool = False) -> None:
    registry = root / "registry"
    registry.mkdir(parents=True, exist_ok=True)
    lines = ["sources:"]
    if lab_page:
        lines.extend([
            "- id: acme-models",
            "  kind: page",
            f"  url: https://{PAGE_HOST}/models",
            "  provider: acme",
            "  pattern: orbit",
            "  confidence: 0.9",
        ])
    lines.extend([
        "- id: hf-acme",
        "  kind: huggingface",
        f"  org: {ORG}",
        "  provider: acme",
        "  confidence: 0.7",
    ])
    (registry / "release-watch.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _signal(model_name: str, repo: str, *, url: str | None = None) -> dict[str, object]:
    slug = repo.replace("/", "-")
    return {
        "model_name": model_name,
        "provider": "Acme",
        "first_seen_url": url or f"https://huggingface.co/{ORG}/{repo}",
        "timestamp": "2026-09-26T13:14:15Z",
        "confidence": 0.7,
        "signal_id": f"watch:acme:{slug}",
    }


def _http_error(url: str, status: int) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", url)
    response = httpx.Response(status, request=request)
    return httpx.HTTPStatusError(f"HTTP {status}", request=request, response=response)


def _run(
    monkeypatch: pytest.MonkeyPatch,
    root: Path,
    row: dict[str, object],
    metadata: object,
    *,
    lab_page: bool = False,
    recheck_day: int | None = None,
    failure: BaseException | None = None,
    final_url: str | None = None,
    raw_body: bytes | None = None,
) -> tuple[dict, list[str]]:
    _card(root)
    _watch(root, lab_page=lab_page)
    repo = str(row["first_seen_url"]).rstrip("/").rsplit("/", 1)[-1]
    meta = f"https://huggingface.co/api/models/{ORG}/{repo}"
    models_dev = "https://models.dev/api.json"
    page = str(row["first_seen_url"])
    if recheck_day is None:
        payload: dict[str, object] = {"signals": [row]}
    else:
        payload = {"rechecks": [{
            "day": recheck_day,
            "due": "2026-09-27",
            "pr_url": "https://github.com/example/repo/pull/9",
            "signal": row,
        }]}
    (root / "pending.json").write_text(json.dumps(payload), encoding="utf-8")
    seen: list[str] = []
    unexpected: list[str] = []

    def fetch(url: str) -> FetchResult:
        seen.append(url)
        if url == meta:
            if failure is not None:
                raise failure
            landed = final_url or url
            raw = raw_body if raw_body is not None else json.dumps(metadata).encode()
            return FetchResult(landed, raw, "application/json")
        if url == page:
            return FetchResult(url, b"<h1>Orbit 9</h1>", "text/html")
        if url == models_dev:
            return FetchResult(url, b"{}", "application/json")
        if url.startswith("https://huggingface.co/api/"):
            return FetchResult(url, b"[]", "application/json")
        # Every fetch exception is an unread hub read, so raising here would
        # hide a request for an unexpected URL. Fail after process returns.
        unexpected.append(url)
        raise AssertionError(url)

    monkeypatch.setattr(processor, "_fetch", fetch)
    monkeypatch.setattr(
        processor.refresh_leaderboards, "run",
        lambda **_: processor.refresh_leaderboards.RefreshReport(),
    )
    result = processor.process(
        root / "pending.json",
        root / "result.json",
        root=root,
        signal_id=str(row["signal_id"]),
        recheck_day=recheck_day,
        price_fetcher=_PriceFetcher(),
    )
    if unexpected:
        raise AssertionError(unexpected[0])
    return result, seen


def _meta(repo: str) -> str:
    return f"https://huggingface.co/api/models/{ORG}/{repo}"


@pytest.mark.parametrize(
    ("repo", "model_name", "metadata", "reason"),
    [
        (
            "canvas-1",
            "Canvas 1",
            {
                "id": f"{ORG}/canvas-1",
                "pipeline_tag": "text-to-image",
                "tags": ["text-to-image"],
            },
            "text-to-image",
        ),
        (
            "policy-1",
            "Policy 1",
            {
                "id": f"{ORG}/policy-1",
                "pipeline_tag": "reinforcement-learning",
                "tags": ["reinforcement-learning"],
            },
            "reinforcement-learning",
        ),
        (
            "probe-1",
            "Probe 1",
            {
                "id": f"{ORG}/probe-1",
                "pipeline_tag": "feature-extraction",
                "library_name": "transformers",
                "tags": ["transformers", "feature-extraction", "transcoder"],
            },
            "interpretability artefact (tag: transcoder)",
        ),
        (
            "orbit-1-sparse",
            "orbit-1-sparse",
            {
                "id": f"{ORG}/orbit-1-sparse",
                "pipeline_tag": "text-generation",
                "library_name": "transformers",
                "tags": ["text-generation", "transformers", "base_model:other-lab/Orbit-1"],
                "cardData": {"base_model": "other-lab/Orbit-1"},
            },
            "derivative of other-lab/Orbit-1",
        ),
    ],
)
def test_hub_metadata_ends_the_signal_out_of_scope_before_a_card(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    repo: str,
    model_name: str,
    metadata: dict,
    reason: str,
) -> None:
    result, seen = _run(monkeypatch, tmp_path, _signal(model_name, repo), metadata)

    assert result["status"] == "out_of_scope"
    assert result["reason"] == reason
    assert result["model_id"] is None
    assert seen == [_meta(repo)]
    assert not (tmp_path / "models" / "acme" / f"{repo}.md").exists()
    assert json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))["reason"] == reason


def test_the_run_summary_groups_reasons_the_way_the_watcher_does(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    image, _seen = _run(
        monkeypatch, tmp_path / "image",
        _signal("Canvas 1", "canvas-1"),
        {"id": f"{ORG}/canvas-1", "pipeline_tag": "text-to-image", "tags": ["text-to-image"]},
    )
    again, _seen = _run(
        monkeypatch, tmp_path / "again",
        _signal("Canvas 2", "canvas-2"),
        {"id": f"{ORG}/canvas-2", "pipeline_tag": "text-to-image", "tags": ["text-to-image"]},
    )
    probe, _seen = _run(
        monkeypatch, tmp_path / "probe",
        _signal("Probe 1", "probe-1"),
        {
            "id": f"{ORG}/probe-1",
            "pipeline_tag": "feature-extraction",
            "tags": ["feature-extraction", "transcoder"],
        },
    )
    derived, _seen = _run(
        monkeypatch, tmp_path / "derived",
        _signal("orbit-1-sparse", "orbit-1-sparse"),
        {
            "id": f"{ORG}/orbit-1-sparse",
            "pipeline_tag": "text-generation",
            "tags": ["text-generation", "base_model:other-lab/Orbit-1"],
            "cardData": {"base_model": "other-lab/Orbit-1"},
        },
    )
    unread, _seen = _run(
        monkeypatch, tmp_path / "unread",
        _signal("Orbit 9", "orbit-9"),
        {},
    )

    text = processor.summary([image, again, probe, derived, unread])

    assert text.splitlines() == [
        "- derivative: 1",
        "- interpretability artefact: 1",
        "- text-to-image: 2",
        HUB_UNREAD + ".",
    ]
    assert image["reason"] == "text-to-image"
    assert probe["reason"] == "interpretability artefact (tag: transcoder)"
    assert derived["reason"] == "derivative of other-lab/Orbit-1"
    assert unread["status"] == "new"
    assert unread["hub_metadata"] == HUB_UNREAD


def test_a_text_generation_repository_is_processed_as_it_is_today(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    result, seen = _run(
        monkeypatch, tmp_path,
        _signal("Orbit 9", "orbit-9"),
        {
            "id": f"{ORG}/orbit-9",
            "pipeline_tag": "text-generation",
            "tags": ["text-generation", "transformers"],
        },
    )

    assert result["status"] == "new"
    assert result["model_id"] == "acme/orbit-9"
    assert "reason" not in result
    assert "hub_metadata" not in result
    assert _meta("orbit-9") in seen
    assert (tmp_path / "models" / "acme" / "orbit-9.md").is_file()


def test_a_repository_with_no_pipeline_tag_and_no_artefact_tag_is_processed_as_today(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    result, seen = _run(
        monkeypatch, tmp_path,
        _signal("Orbit 9", "orbit-9"),
        {"id": f"{ORG}/orbit-9", "tags": ["transformers", "en", "license:mit"]},
    )

    assert result["status"] == "new"
    assert result["model_id"] == "acme/orbit-9"
    assert "hub_metadata" not in result
    assert _meta("orbit-9") in seen


def test_a_chat_model_with_an_interpretability_tag_is_kept(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    result, seen = _run(
        monkeypatch, tmp_path,
        _signal("Orbit 9", "orbit-9"),
        {
            "id": f"{ORG}/orbit-9",
            "pipeline_tag": "text-generation",
            "tags": ["text-generation", "interpretability", "transformers"],
        },
    )

    assert result["status"] == "new"
    assert result["model_id"] == "acme/orbit-9"
    assert result.get("reason") != "interpretability artefact (tag: interpretability)"
    assert "hub_metadata" not in result
    assert _meta("orbit-9") in seen


def test_a_keeping_task_tag_alone_is_kept(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    result, seen = _run(
        monkeypatch, tmp_path,
        _signal("Orbit 9", "orbit-9"),
        {"id": f"{ORG}/orbit-9", "tags": ["text-generation"]},
    )

    assert result["status"] == "new"
    assert result["model_id"] == "acme/orbit-9"
    assert "hub_metadata" not in result
    assert _meta("orbit-9") in seen


@pytest.mark.parametrize("day", [1, 7, 30])
def test_a_recheck_row_is_rescoped(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, day: int,
) -> None:
    row = _signal("Canvas 1", "canvas-1")
    result, seen = _run(
        monkeypatch, tmp_path, row,
        {"id": f"{ORG}/canvas-1", "pipeline_tag": "text-to-image", "tags": ["text-to-image"]},
        recheck_day=day,
    )

    assert result["status"] == "out_of_scope"
    assert result["reason"] == "text-to-image"
    assert result["recheck_day"] == day
    assert result["recheck_due"] == "2026-09-27"
    assert result["pr_url"] == "https://github.com/example/repo/pull/9"
    assert seen == [_meta("canvas-1")]
    assert not (tmp_path / "models" / "acme" / "canvas-1.md").exists()


def test_a_non_huggingface_first_seen_url_makes_no_hub_request(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    page = f"https://{PAGE_HOST}/orbit-9"
    row = _signal("Orbit 9", "orbit-9", url=page)
    result, seen = _run(monkeypatch, tmp_path, row, {}, lab_page=True)

    assert result["status"] == "new"
    assert result["model_id"] == "acme/orbit-9"
    assert all("/api/models/" not in url for url in seen)
    assert page in seen
    assert "hub_metadata" not in result


def test_a_dataset_url_makes_no_hub_request(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    page = f"https://huggingface.co/datasets/{ORG}/orbit-9"
    row = _signal("Orbit 9", "orbit-9", url=page)
    result, seen = _run(monkeypatch, tmp_path, row, {})

    assert result["status"] == "uncertain"
    assert all(not url.startswith(f"https://huggingface.co/api/models/{ORG}/") for url in seen)
    assert "hub_metadata" not in result


@pytest.mark.parametrize(
    ("label", "failure", "metadata"),
    [
        ("exception", RuntimeError("network down"), None),
        ("timeout", httpx.TimeoutException("timed out"), None),
        ("404", None, None),
        ("429", None, None),
        ("empty", None, {}),
        ("null-fields", None, {"pipeline_tag": None, "tags": None}),
    ],
)
def test_a_failed_hub_read_is_not_out_of_scope(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    label: str,
    failure: BaseException | None,
    metadata: object,
) -> None:
    row = _signal("Orbit 9", "orbit-9")
    meta = _meta("orbit-9")
    if label == "404":
        failure = _http_error(meta, 404)
    elif label == "429":
        failure = _http_error(meta, 429)
    result, seen = _run(monkeypatch, tmp_path, row, metadata, failure=failure)

    assert result["status"] == "new", label
    assert result["model_id"] == "acme/orbit-9"
    assert result["hub_metadata"] == HUB_UNREAD
    assert result.get("reason") is None
    assert meta in seen
    assert (tmp_path / "models" / "acme" / "orbit-9.md").is_file()
    assert HUB_UNREAD in processor.summary([result])


def test_unreadable_metadata_does_not_apply_the_repository_name(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """An empty read must not borrow the name rules. The repo name would be out of scope."""
    result, _seen = _run(
        monkeypatch, tmp_path,
        _signal("Orbit 9", "robotics-arm"),
        {},
    )

    assert result["status"] != "out_of_scope"
    assert result.get("reason") != "robotics or embodied checkpoint"
    assert result["hub_metadata"] == HUB_UNREAD
    assert result["status"] == "uncertain"


def _poison(repo: str = "orbit-9") -> dict[str, object]:
    """An out-of-scope body that names this repository. Trusting it ends the signal."""
    return {
        "id": f"{ORG}/{repo}",
        "pipeline_tag": "text-to-image",
        "tags": ["text-to-image"],
    }


def _assert_unread_continues(result: dict, root: Path) -> None:
    """The end when the hub check does not run, plus the unread note on this row."""
    assert result["status"] == "new"
    assert result["model_id"] == "acme/orbit-9"
    assert result.get("reason") is None
    assert result["hub_metadata"] == HUB_UNREAD
    assert result["summary"] == f"{HUB_UNREAD}."
    assert (root / "models" / "acme" / "orbit-9.md").is_file()


@pytest.mark.parametrize("shape", [
    "off-host-redirect",
    "same-host-other-repository",
    "query",
    "fragment",
    "non-default-port",
    "userinfo",
    "id-names-another-repository",
    "model-id-names-another-repository",
    "no-id",
    "string-tags",
    "tags-list-with-a-non-string",
    "http-500",
    "non-json",
    "json-list",
    "assertion-error",
])
def test_a_read_that_is_not_this_repository_metadata_is_unread(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, shape: str,
) -> None:
    row = _signal("Orbit 9", "orbit-9")
    meta = _meta("orbit-9")
    metadata: dict[str, object] = _poison()
    final_url = None
    raw_body = None
    failure = None
    if shape == "off-host-redirect":
        final_url = f"https://other.example/api/models/{ORG}/orbit-9"
    elif shape == "same-host-other-repository":
        final_url = "https://huggingface.co/api/models/other-lab/not-this"
    elif shape == "query":
        final_url = f"https://huggingface.co/api/models/{ORG}/orbit-9?x=1"
    elif shape == "fragment":
        final_url = f"https://huggingface.co/api/models/{ORG}/orbit-9#frag"
    elif shape == "non-default-port":
        final_url = f"https://huggingface.co:8443/api/models/{ORG}/orbit-9"
    elif shape == "userinfo":
        final_url = f"https://user@huggingface.co/api/models/{ORG}/orbit-9"
    elif shape == "id-names-another-repository":
        metadata["id"] = "other-lab/not-this"
    elif shape == "model-id-names-another-repository":
        metadata = {
            "modelId": "other-lab/not-this",
            "pipeline_tag": "text-to-image",
            "tags": ["text-to-image"],
        }
    elif shape == "no-id":
        metadata = {"pipeline_tag": "text-to-image", "tags": ["text-to-image"]}
    elif shape == "string-tags":
        metadata["tags"] = "text-generation"
    elif shape == "tags-list-with-a-non-string":
        metadata["tags"] = ["text-generation", 1]
    elif shape == "http-500":
        failure = _http_error(meta, 500)
    elif shape == "non-json":
        raw_body = b"not-json"
    elif shape == "json-list":
        raw_body = json.dumps([_poison()]).encode()
    elif shape == "assertion-error":
        failure = AssertionError("fetch failed closed")
    else:
        raise AssertionError(shape)

    result, seen = _run(
        monkeypatch, tmp_path, row, metadata,
        failure=failure, final_url=final_url, raw_body=raw_body,
    )

    _assert_unread_continues(result, tmp_path)
    assert meta in seen


@pytest.mark.parametrize("identity", ["id", "modelId"])
def test_a_correct_read_of_this_repository_is_applied(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, identity: str,
) -> None:
    """Case and one trailing slash still name this repository. ``modelId`` can."""
    metadata: dict[str, object] = {
        "pipeline_tag": "text-to-image",
        "tags": ["text-to-image"],
    }
    if identity == "id":
        metadata["id"] = f"{ORG.upper()}/CANVAS-1"
    else:
        metadata["modelId"] = "Acme-Lab/Canvas-1"
    result, seen = _run(
        monkeypatch, tmp_path,
        _signal("Canvas 1", "canvas-1"),
        metadata,
        final_url=f"https://huggingface.co/api/models/{ORG.upper()}/Canvas-1/",
    )

    assert result["status"] == "out_of_scope"
    assert result["reason"] == "text-to-image"
    assert "hub_metadata" not in result
    assert seen == [_meta("canvas-1")]
    assert not (tmp_path / "models" / "acme" / "canvas-1.md").exists()


@pytest.mark.parametrize("pipeline_tag", ["text-to-image", "text-generation"])
@pytest.mark.parametrize("tags", ["absent", "null"])
def test_absent_or_null_tags_with_a_pipeline_tag_stay_a_valid_read(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, pipeline_tag: str, tags: str,
) -> None:
    """Missing or null ``tags`` is a decision from the pipeline tag.

    The watcher does the same: ``relevant_hub_tags`` keeps nothing from a
    missing or null list, and ``tag_scope`` uses the pipeline tag. A present
    ``tags`` that is not a list of strings is a different case.
    """
    repo = "canvas-1" if pipeline_tag == "text-to-image" else "orbit-9"
    model_name = "Canvas 1" if repo == "canvas-1" else "Orbit 9"
    metadata: dict[str, object] = {"id": f"{ORG}/{repo}", "pipeline_tag": pipeline_tag}
    if tags == "null":
        metadata["tags"] = None
    result, seen = _run(monkeypatch, tmp_path, _signal(model_name, repo), metadata)

    assert "hub_metadata" not in result
    assert seen[0] == _meta(repo)
    if pipeline_tag == "text-to-image":
        assert result["status"] == "out_of_scope"
        assert result["reason"] == "text-to-image"
        return
    assert result["status"] == "new"
    assert result["model_id"] == "acme/orbit-9"
    assert result.get("reason") is None


@pytest.mark.parametrize(
    ("label", "pipeline_tag"),
    [
        ("list", ["text-generation"]),
        ("dict", {"name": "text-generation"}),
        ("number", 1),
        ("false", False),
    ],
)
def test_a_present_non_string_pipeline_tag_is_unread(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, label: str, pipeline_tag: object,
) -> None:
    """A present pipeline tag that is not a string is not a decision.

    The body also carries an out-of-scope tag. The watcher would ignore the
    odd pipeline tag and end the signal from that tag. This read does not.
    """
    metadata: dict[str, object] = {
        "id": f"{ORG}/orbit-9",
        "pipeline_tag": pipeline_tag,
        "tags": ["text-to-image"],
    }
    result, seen = _run(
        monkeypatch, tmp_path, _signal("Orbit 9", "orbit-9"), metadata,
    )

    _assert_unread_continues(result, tmp_path)
    assert _meta("orbit-9") in seen, label


@pytest.mark.parametrize("pipeline_tag", ["absent", "null"])
def test_absent_or_null_pipeline_tag_with_a_tag_list_stays_a_valid_read(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, pipeline_tag: str,
) -> None:
    """Missing or null ``pipeline_tag`` is a decision from the tag list.

    The watcher does the same. A present value that is not a string is unread.
    """
    metadata: dict[str, object] = {"id": f"{ORG}/canvas-1", "tags": ["text-to-image"]}
    if pipeline_tag == "null":
        metadata["pipeline_tag"] = None
    result, seen = _run(
        monkeypatch, tmp_path, _signal("Canvas 1", "canvas-1"), metadata,
    )

    assert result["status"] == "out_of_scope"
    assert result["reason"] == "text-to-image"
    assert "hub_metadata" not in result
    assert seen == [_meta("canvas-1")]
    assert not (tmp_path / "models" / "acme" / "canvas-1.md").exists()
