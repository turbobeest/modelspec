"""MODEL-368 reads Perplexity Pro's expanded FAQ with an exact template."""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from api.worker.vendor import SOURCES
from decision.model import CitedRegion, Source, SourceRef, TargetRef, VerificationActor
from decision.perplexity_faq import (
    FAQ_STRUCTURAL_HASH,
    LIVE_ITEMS,
    QUESTION,
    PerplexityFaqExtractor,
    prepare_pro_faq,
    structural_hash,
)
from decision.sources import RENDERED_PREPARATIONS, CopyStore
from decision.verify import (
    Claim,
    ExtractorError,
    Queue,
    StoredRegions,
    VerificationLog,
    deterministic_extractors,
    run,
    verify,
)

TODAY = date(2026, 10, 18)
URL = "https://www.perplexity.ai/pro"
SUBJECT = "perplexity/subscription/pro"
FIELD = "offering.subscription.models_covered"
COLLECTOR = VerificationActor(agent="codex", model_family="openai", method="collect")
RETAINED = Path("/tmp/model-368/pro-expanded.html")
PREFIX = "Pro includes "
SUFFIX = ". You can switch between models with one click depending on your task."


def sentence(items: tuple[str, ...] | list[str]) -> str:
    body = ", ".join(items[:-1]) + ", and " + items[-1]
    return PREFIX + body + SUFFIX


def faq_page(items: list[str], *, question: str = QUESTION, question_inside: bool = True,
             answer_inside: bool = True) -> str:
    button = f'<button aria-expanded="true"><div>{question}</div></button>'
    answer = f'<div class="answer"><div>{sentence(items)}</div></div>'
    other = "<div><button><div>How is Pro different from the Free plan?</div></button></div>"
    item = f"<div>{button}{answer}</div>" if question_inside and answer_inside else ""
    if question_inside and not answer_inside:
        item = f"<div>{button}</div>"
    if answer_inside and not question_inside:
        item = f"<div>{answer}</div>"
    outside = ""
    if not question_inside:
        outside += button
    if not answer_inside:
        outside += answer
    return f"<html><body><section id=\"faq\">{other}{item}</section>{outside}</body></html>"


def read(tmp_path, html: str, *, value: list[str], subject: str = SUBJECT, url: str = URL,
         field: str = FIELD, template_hash: str | None = None,
         mapping: dict[str, str] | None = None, order: tuple[str, ...] | None = None):
    store = CopyStore(tmp_path / "copies")
    ref = store.put(html.encode())
    source = Source(
        id="perplexity-pro", url=url, kind="provider_documentation",
        normaliser="html-icon-labels",
        cited_regions=[CitedRegion(id="faq", locator={"kind": "css", "value": "#faq"})],
    )
    claim = Claim(
        target=TargetRef(kind="fact", id=f"{subject}#{field}"),
        subject=subject, names=("Perplexity Pro",), field=field, value=value,
        collector=COLLECTOR,
        sources=(SourceRef(source_id=source.id, snapshot_ref=ref, cited_regions=["faq"]),),
    )
    regions = StoredRegions(store, {source.id: source})
    extractors = []
    for extractor in deterministic_extractors():
        if isinstance(extractor, PerplexityFaqExtractor) and (
            template_hash is not None or mapping is not None or order is not None
        ):
            extractors.append(PerplexityFaqExtractor(
                template_hash=template_hash or extractor.template_hash,
                mapping=mapping if mapping is not None else extractor.mapping,
                reviewed_order=order if order is not None else extractor.reviewed_order,
            ))
        else:
            extractors.append(extractor)
    return verify(claim, regions, extractors, today=TODAY)


def test_reordered_mapped_list_is_template_drifted(tmp_path):
    order = ("Alpha", "Beta", "Gamma")
    html = faq_page(["Beta", "Alpha", "Gamma"])
    mapping = {"Alpha": "lab/alpha", "Beta": "lab/beta", "Gamma": "lab/gamma"}
    result = read(tmp_path, html, value=["lab/alpha", "lab/beta", "lab/gamma"],
                  template_hash=structural_hash(faq_page(list(order))), mapping=mapping,
                  order=order)
    assert result.outcome == "skipped"
    assert result.reason is not None and "template drifted" in result.reason
    assert result.verification is None


def test_extra_item_is_template_drifted(tmp_path):
    base = ["Alpha", "Beta", "Gamma"]
    html = faq_page([*base, "Delta"])
    mapping = {name: f"lab/{name.casefold()}" for name in [*base, "Delta"]}
    result = read(
        tmp_path, html, value=["lab/alpha"], template_hash=structural_hash(faq_page(base)),
        mapping=mapping, order=tuple(base),
    )
    assert result.outcome == "skipped"
    assert result.reason is not None and "template drifted" in result.reason


def test_renamed_question_is_template_drifted(tmp_path):
    items = ["Alpha", "Beta"]
    html = faq_page(items, question="Which models are included?")
    mapping = {"Alpha": "lab/alpha", "Beta": "lab/beta"}
    result = read(tmp_path, html, value=["lab/alpha", "lab/beta"],
                  template_hash=structural_hash(html), mapping=mapping, order=tuple(items))
    assert result.outcome == "skipped"
    assert result.reason is not None and "template drifted" in result.reason


def test_near_miss_name_is_incomplete_mapping(tmp_path):
    items = ["Claude Sonnet 5.5", "Grok 4.1 Fast"]
    html = faq_page(items)
    result = read(
        tmp_path, html, value=["anthropic/claude-sonnet-5", "xai/grok-4-1-fast"],
        template_hash=structural_hash(html),
        mapping={"Claude Sonnet 5": "anthropic/claude-sonnet-5", "Grok 4.1": "xai/grok-4-1"},
        order=("Claude Sonnet 5", "Grok 4.1"),
    )
    assert result.outcome == "skipped"
    assert result.verification is None
    assert result.reason is not None
    assert "incomplete mapping" in result.reason
    assert "Claude Sonnet 5.5" in result.reason
    assert "Grok 4.1 Fast" in result.reason


def test_moved_region_is_template_drifted(tmp_path):
    items = ["Alpha", "Beta"]
    html = faq_page(items, question_inside=False)
    mapping = {"Alpha": "lab/alpha", "Beta": "lab/beta"}
    result = read(tmp_path, html, value=["lab/alpha", "lab/beta"],
                  template_hash=structural_hash(html), mapping=mapping, order=tuple(items))
    assert result.outcome == "skipped"
    assert result.reason is not None and "template drifted" in result.reason


def test_live_literals_do_not_verify_a_partial_set(tmp_path):
    html = faq_page(list(LIVE_ITEMS))
    result = read(
        tmp_path, html,
        value=["anthropic/claude-sonnet-5", "openai/gpt-5-6-terra"],
        template_hash=structural_hash(html),
    )
    assert result.outcome == "skipped"
    assert result.verification is None
    assert result.reason is not None
    assert "incomplete mapping" in result.reason
    for literal in (
        "Gemini 3.1 Pro Thinking", "Grok 4.1", "Perplexity's in-house Sonar 2 model",
    ):
        assert literal in result.reason
    assert "GPT-5.6 Terra" not in result.reason.split("incomplete mapping", 1)[1]


def test_complete_mapping_verifies_canonical_ids(tmp_path):
    items = ["GPT-5.6 Terra", "Claude Sonnet 5"]
    html = faq_page(items)
    mapping = {
        "GPT-5.6 Terra": "openai/gpt-5-6-terra",
        "Claude Sonnet 5": "anthropic/claude-sonnet-5",
    }
    result = read(
        tmp_path, html,
        value=["anthropic/claude-sonnet-5", "openai/gpt-5-6-terra"],
        template_hash=structural_hash(html), mapping=mapping, order=tuple(items),
    )
    assert result.outcome == "verified"
    assert result.verification is not None
    assert result.verification.verifier.method == "perplexity-pro-faq@1"


def test_other_plan_and_host_are_not_bound(tmp_path):
    html = faq_page(["Alpha", "Beta"])
    digest = structural_hash(html)
    mapping = {"Alpha": "lab/alpha", "Beta": "lab/beta"}
    order = ("Alpha", "Beta")
    other_plan = read(
        tmp_path, html, value=["lab/alpha", "lab/beta"], subject="perplexity/subscription/max",
        template_hash=digest, mapping=mapping, order=order,
    )
    other_host = read(
        tmp_path, html, value=["lab/alpha", "lab/beta"], url="https://example.com/pro",
        template_hash=digest, mapping=mapping, order=order,
    )
    queried = read(
        tmp_path, html, value=["lab/alpha", "lab/beta"], url=URL + "?plan=pro",
        template_hash=digest, mapping=mapping, order=order,
    )
    for result in (other_plan, other_host, queried):
        assert result.outcome != "verified"
        assert result.verification is None or (
            result.verification.verifier.method != "perplexity-pro-faq@1"
        )


def test_missing_page_bytes_are_template_drifted():
    html = faq_page(list(LIVE_ITEMS))
    source = SourceRef(source_id="perplexity-pro", snapshot_ref="sha256:" + "ab" * 32,
                       cited_regions=["faq"])
    filed = Claim(
        target=TargetRef(kind="fact", id=f"{SUBJECT}#{FIELD}"),
        subject=SUBJECT, names=("Perplexity Pro",), field=FIELD,
        value=["openai/gpt-5-6-terra"], collector=COLLECTOR, sources=(source,),
    )

    class _TextOnly:
        def text(self, source_id: str, copy_ref: str, region_id: str) -> str:
            return "normalised region"

        def source_url(self, source_id: str) -> str:
            return URL

        def source_kind(self, source_id: str) -> str:
            return "provider_documentation"

    result = verify(
        filed, _TextOnly(), [PerplexityFaqExtractor(template_hash=structural_hash(html))],
        today=TODAY,
    )
    assert result.outcome == "skipped"
    assert result.reason is not None and "template drifted" in result.reason


def test_scratch_queue_skip_is_not_logged(tmp_path):
    html = faq_page(list(LIVE_ITEMS))
    store = CopyStore(tmp_path / "copies")
    ref = store.put(html.encode())
    source = Source(
        id="perplexity-pro", url=URL, kind="provider_documentation",
        normaliser="html-icon-labels",
        cited_regions=[CitedRegion(id="faq", locator={"kind": "css", "value": "#faq"})],
    )
    filed = Claim(
        target=TargetRef(kind="fact", id=f"{SUBJECT}#{FIELD}"),
        subject=SUBJECT, names=("Perplexity Pro",), field=FIELD,
        value=["anthropic/claude-sonnet-5", "openai/gpt-5-6-terra"],
        collector=COLLECTOR,
        sources=(SourceRef(source_id=source.id, snapshot_ref=ref, cited_regions=["faq"]),),
    )
    queue, log = Queue(tmp_path / "verification"), VerificationLog(tmp_path / "verification")
    queue.file(filed, at=datetime(2026, 10, 18, tzinfo=UTC))
    extractors = [
        PerplexityFaqExtractor(template_hash=structural_hash(html))
        if isinstance(extractor, PerplexityFaqExtractor) else extractor
        for extractor in deterministic_extractors()
    ]
    report = run(queue, log, StoredRegions(store, {source.id: source}), extractors, today=TODAY)
    assert report.counts["skipped"] == 1
    assert report.counts["verified"] == 0
    assert report.counts["mismatch"] == 0
    assert not log.path.exists()
    pending, _unknown = queue.pending()
    assert [item.target.id for item in pending] == [filed.target.id]


def test_faq_reader_stays_out_of_the_worker_bundle():
    assert Path("decision/perplexity_faq.py") not in SOURCES
    for path in SOURCES:
        text = path.read_text(encoding="utf-8")
        assert "perplexity_faq" not in text
        assert "PerplexityFaqExtractor" not in text


def test_preparation_expands_the_models_question():
    page = _FaqPage()
    prepare_pro_faq(page, 5)
    assert page.clicked == QUESTION
    assert page.waited == QUESTION
    assert RENDERED_PREPARATIONS["model-368-perplexity-pro-faq"] is prepare_pro_faq


def test_reviewed_hash_matches_the_retained_page():
    if not RETAINED.is_file():
        pytest.skip("retained Perplexity page is local and is not committed")
    html = RETAINED.read_text(encoding="utf-8")
    assert structural_hash(html) == FAQ_STRUCTURAL_HASH
    filed = Claim(
        target=TargetRef(kind="fact", id=f"{SUBJECT}#{FIELD}"),
        subject=SUBJECT, names=("Perplexity Pro",), field=FIELD,
        value=["anthropic/claude-sonnet-5", "openai/gpt-5-6-terra"],
        collector=COLLECTOR,
        sources=(SourceRef(
            source_id="perplexity-pro", snapshot_ref="sha256:" + "cd" * 32, cited_regions=["faq"],
        ),),
    )
    with pytest.raises(ExtractorError, match="incomplete mapping") as caught:
        PerplexityFaqExtractor().extract(filed, html)
    message = str(caught.value)
    for literal in (
        "Gemini 3.1 Pro Thinking", "Grok 4.1", "Perplexity's in-house Sonar 2 model",
    ):
        assert literal in message


class _FaqPage:
    def __init__(self) -> None:
        self.clicked = None
        self.waited = None

    def locator(self, selector: str) -> _FaqPage:
        assert selector == "#faq"
        return self

    def get_by_role(self, role: str, *, name: str, exact: bool) -> _FaqPage:
        assert (role, exact) == ("button", True)
        self.clicked = name
        return self

    def click(self, *, timeout: float) -> None:
        assert timeout > 0

    def wait_for_function(self, expression: str, *, arg: str, timeout: float) -> None:
        assert "aria-expanded" in expression
        assert timeout > 0
        self.waited = arg
