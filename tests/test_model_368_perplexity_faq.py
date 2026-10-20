"""MODEL-368 parses synthetic FAQ pages transiently without retained copies."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from api.worker.vendor import SOURCES
from decision import perplexity_faq
from decision.model import SourceRef, TargetRef, VerificationActor
from decision.perplexity_faq import (
    LIVE_ITEMS,
    PREFIX,
    QUESTION,
    PerplexityFaqExtractor,
    prepare_pro_faq,
    structural_hash,
)
from decision.sources import RENDERED_PREPARATIONS
from decision.verify import Claim, ExtractorError, Reading, deterministic_extractors

URL = "https://www.perplexity.ai/pro"
SUBJECT = "perplexity/subscription/pro"
FIELD = "offering.subscription.models_covered"
COLLECTOR = VerificationActor(agent="codex", model_family="openai", method="collect")
SUFFIX = ". Synthetic sentence used only by parser fixtures."


@pytest.fixture(autouse=True)
def synthetic_sentence_frame(monkeypatch):
    monkeypatch.setattr(perplexity_faq, "SUFFIX_LENGTH", len(SUFFIX))
    monkeypatch.setattr(perplexity_faq, "SUFFIX_SHA256",
                        hashlib.sha256(SUFFIX.encode()).hexdigest())


def sentence(items: tuple[str, ...] | list[str]) -> str:
    body = ", ".join(items[:-1]) + ", and " + items[-1]
    return PREFIX + body + SUFFIX


def faq_page(items: list[str], *, question: str = QUESTION, question_inside: bool = True,
             answer_inside: bool = True) -> str:
    button = f'<button aria-expanded="true"><div>{question}</div></button>'
    answer = f'<div class="answer"><div>{sentence(items)}</div></div>'
    other = "<div><button><div>Synthetic unrelated question?</div></button></div>"
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
    return f'<html><body><section id="faq">{other}{item}</section>{outside}</body></html>'


def claim(value: list[str], *, subject: str = SUBJECT, field: str = FIELD) -> Claim:
    return Claim(
        target=TargetRef(kind="fact", id=f"{subject}#{field}"),
        subject=subject, names=("Perplexity Pro",), field=field, value=value,
        collector=COLLECTOR,
        sources=(SourceRef(source_id="perplexity-pro", snapshot_ref="sha256:" + "ab" * 32,
                           cited_regions=["faq"]),),
    )


def read(html: str, *, value: list[str], template_hash: str,
         mapping: dict[str, str] | None = None, order: tuple[str, ...] | None = None
         ) -> list[Reading]:
    extractor = PerplexityFaqExtractor(
        template_hash=template_hash, mapping=mapping, reviewed_order=order,
    )
    return extractor.extract(claim(value), html)


def test_reordered_mapped_list_is_template_drifted():
    order = ("Alpha", "Beta", "Gamma")
    html = faq_page(["Beta", "Alpha", "Gamma"])
    mapping = {"Alpha": "lab/alpha", "Beta": "lab/beta", "Gamma": "lab/gamma"}
    with pytest.raises(ExtractorError, match="template drifted"):
        read(html, value=["lab/alpha", "lab/beta", "lab/gamma"],
             template_hash=structural_hash(faq_page(list(order))), mapping=mapping,
             order=order)


def test_extra_item_is_template_drifted():
    base = ["Alpha", "Beta", "Gamma"]
    html = faq_page([*base, "Delta"])
    mapping = {name: f"lab/{name.casefold()}" for name in [*base, "Delta"]}
    with pytest.raises(ExtractorError, match="template drifted"):
        read(html, value=["lab/alpha"], template_hash=structural_hash(faq_page(base)),
             mapping=mapping, order=tuple(base))


def test_renamed_question_is_template_drifted():
    items = ["Alpha", "Beta"]
    html = faq_page(items, question="Synthetic replacement question?")
    mapping = {"Alpha": "lab/alpha", "Beta": "lab/beta"}
    with pytest.raises(ExtractorError, match="template drifted"):
        read(html, value=["lab/alpha", "lab/beta"], template_hash=structural_hash(html),
             mapping=mapping, order=tuple(items))


def test_changed_sentence_frame_is_template_drifted():
    items = ["Alpha", "Beta"]
    html = faq_page(items).replace(SUFFIX, ". A different synthetic sentence.")
    with pytest.raises(ExtractorError, match="template drifted"):
        read(html, value=["lab/alpha", "lab/beta"],
             template_hash=structural_hash(faq_page(items)),
             mapping={"Alpha": "lab/alpha", "Beta": "lab/beta"}, order=tuple(items))


def test_near_miss_name_is_incomplete_mapping():
    items = ["Claude Sonnet 5.5", "Grok 4.1 Fast"]
    html = faq_page(items)
    with pytest.raises(ExtractorError, match="incomplete mapping") as caught:
        read(
            html, value=["anthropic/claude-sonnet-5", "xai/grok-4-1-fast"],
            template_hash=structural_hash(html),
            mapping={"Claude Sonnet 5": "anthropic/claude-sonnet-5", "Grok 4.1": "xai/grok-4-1"},
            order=("Claude Sonnet 5", "Grok 4.1"),
        )
    assert "Claude Sonnet 5.5" in str(caught.value)
    assert "Grok 4.1 Fast" in str(caught.value)


@pytest.mark.parametrize("question_inside,answer_inside", [(False, True), (True, False)])
def test_moved_region_is_template_drifted(question_inside, answer_inside):
    items = ["Alpha", "Beta"]
    html = faq_page(items, question_inside=question_inside, answer_inside=answer_inside)
    mapping = {"Alpha": "lab/alpha", "Beta": "lab/beta"}
    with pytest.raises(ExtractorError, match="template drifted"):
        read(html, value=["lab/alpha", "lab/beta"], template_hash=structural_hash(html),
             mapping=mapping, order=tuple(items))


def test_live_literals_do_not_read_a_partial_set():
    html = faq_page(list(LIVE_ITEMS))
    with pytest.raises(ExtractorError, match="incomplete mapping") as caught:
        read(html, value=["anthropic/claude-sonnet-5", "openai/gpt-5-6-terra"],
             template_hash=structural_hash(html))
    message = str(caught.value)
    for literal in (
        "Gemini 3.1 Pro Thinking", "Grok 4.1", "Perplexity's in-house Sonar 2 model",
    ):
        assert literal in message
    assert "GPT-5.6 Terra" not in message.split("incomplete mapping", 1)[1]


def test_complete_mapping_reads_unchanged_canonical_ids():
    items = ["GPT-5.6 Terra", "Claude Sonnet 5"]
    html = faq_page(items)
    mapping = {
        "GPT-5.6 Terra": "openai/gpt-5-6-terra",
        "Claude Sonnet 5": "anthropic/claude-sonnet-5",
    }
    value = ["anthropic/claude-sonnet-5", "openai/gpt-5-6-terra"]
    readings = read(html, value=value, template_hash=structural_hash(html),
                    mapping=mapping, order=tuple(items))
    assert readings == [Reading("Perplexity Pro", "openai/gpt-5-6-terra, anthropic/claude-sonnet-5")]
    assert value == ["anthropic/claude-sonnet-5", "openai/gpt-5-6-terra"]


def test_other_plan_and_host_are_not_bound():
    extractor = PerplexityFaqExtractor()
    filed = claim(["lab/alpha", "lab/beta"])
    assert extractor.bound_to(filed, URL)
    assert not extractor.bound_to(claim(filed.value, subject="perplexity/subscription/max"), URL)
    assert not extractor.bound_to(claim(filed.value, field="offering.subscription.price"), URL)
    for url in ("https://example.com/pro", URL + "?plan=pro", URL + "#faq", None):
        assert not extractor.bound_to(filed, url)


def test_missing_page_bytes_are_template_drifted():
    with pytest.raises(ExtractorError, match="template drifted"):
        PerplexityFaqExtractor().extract(claim(["openai/gpt-5-6-terra"]), "")


def test_faq_reader_is_registered():
    extractors = [reader for reader in deterministic_extractors()
                  if isinstance(reader, PerplexityFaqExtractor)]
    assert len(extractors) == 1
    assert extractors[0].actor.method == "perplexity-pro-faq@1"


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
