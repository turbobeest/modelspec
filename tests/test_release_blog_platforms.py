"""Platform drafts for a release breakdown (MODEL-226).

Drafts are text views of the MODEL-224 sample breakdown. Nothing is posted.
Expected draft text is written out in this file. It is not built by the
production formatters.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from decision.excluded import excluded_sources
from release_blog import platforms
from release_blog.breakdown import to_bytes
from release_blog.model import Breakdown
from release_blog.platforms import AUTOMATIC_POSTING, generate_from_breakdown, render_drafts
from release_blog.tone import refused_words

_LAB = "https://lab.example.com/alpha-launch"
_BOARD = "https://board.example.org/results"
_PRICE = "https://lab.example.com/pricing"
_SNAPSHOT = "https://modelspec.dev/api/decision/snapshots/snap_ee376ecc9678d46b.json.gz"
_READ_LAB = "2026-09-20"
_READ_SNAP = "2026-09-26"
_URL = "https://modelspec.dev/blog/lab-alpha/"
_NEUTRALITY = "No referral fees, no paid placement, no provider-paid visibility, permanently."
_SUPPLIER = "ModelSpec supplies evaluation services to this lab."
_EARLY = "ModelSpec received early access without editorial conditions."
_HAND = "Make the image by hand."


@pytest.fixture(scope="module")
def breakdown(tmp_path_factory) -> Breakdown:
    """The MODEL-224 sample: signed snapshots and the real decision engine."""
    from release_blog.gates import load_signed
    from tests import test_release_blog as sample

    root = tmp_path_factory.mktemp("platforms")
    after = load_signed(
        sample._write(root / "after.json.gz", with_new=True), public_keys=sample.PUBLIC
    )
    before = load_signed(
        sample._write(root / "before.json.gz", with_new=False), public_keys=sample.PUBLIC
    )
    return sample._build(after, before)


def _with_repeated_readings(breakdown: Breakdown, benchmark: str, repeats: int) -> Breakdown:
    rows = breakdown.claims_vs_evidence.claims
    original = next(row for row in rows if row.benchmark == benchmark)
    longer = original.model_copy(update={"readings": original.readings * repeats})
    claims = breakdown.claims_vs_evidence.model_copy(
        update={"claims": [longer if row.benchmark == benchmark else row for row in rows]}
    )
    return breakdown.model_copy(update={"claims_vs_evidence": claims})


def _related(breakdown: Breakdown, **disclosures: str) -> Breakdown:
    related = breakdown.model_copy(
        update={
            "disclosures": breakdown.disclosures.model_copy(update=disclosures),
        }
    )
    Breakdown.model_validate(related.model_dump(by_alias=True))
    return related


# Checked against the signed fixture fields, then written here as text.
# swe_bench_pro: lab 70% and board 67.9%, both read 2026-09-20, gap 2.1
# points lower from the snapshot read 2026-09-26. mmlu_pro: 80% and 0.78
# fraction. terminal_bench: 50% and 48%. livecodebench: 72%, no lab figure.
# Leading band size 2. General reasoning is place 3 of 3. Task price is
# 40,000 input tokens, 4,000 output tokens, $0.112. Held back: 1 quarantined.
_ORACLE = {
    "x": (
        "Alpha 2.5: on swe_bench_pro the lab reports 70% and the independent reading is 67.9%, 2."
        "1 points lower.\n\nThis model is in the leading band for software engineering; independe"
        "nt readings sit beside the lab's figures\n\nIn software engineering, Alpha 2.5 is in the"
        " leading band. The band holds 2 models, and the evidence does not separate them.\n\nIn g"
        "eneral reasoning, Alpha 2.5 is outside the leading band, at place 3 of 3 ranked models."
        "\n\nAt 40,000 input tokens and 4,000 output tokens, the list price is $0.112 a task.\n\n"
        "Lab figures with no independent reading yet: cursorbench.\n\nModelSpec holds readings of"
        " this model that have not yet passed the second key: quarantined: 1. Their values are no"
        "t shown.\n\nlivecodebench has an independent reading of 72% and no lab figure.\n\nNo ref"
        "erral fees, no paid placement, no provider-paid visibility, permanently.\n\nhttps://mode"
        "lspec.dev/blog/lab-alpha/\n\nSource: https://modelspec.dev/api/decision/snapshots/snap_e"
        "e376ecc9678d46b.json.gz (read 2026-09-26).\n\nSource: https://lab.example.com/alpha-laun"
        "ch (read 2026-09-20).\n\nSource: https://board.example.org/results (read 2026-09-20).\n"
        "\nSource: https://lab.example.com/pricing (read 2026-09-26).\n"
    ),
    "linkedin": (
        "Alpha 2.5 is an analysis of alternatives for teams choosing a text generator.\n\nThis mo"
        "del is in the leading band for software engineering; independent readings sit beside the"
        " lab's figures\n\nAlpha 2.5: on swe_bench_pro the lab reports 70% and the independent re"
        "ading is 67.9%, 2.1 points lower.\n\nIn software engineering, Alpha 2.5 is in the leadin"
        "g band. The band holds 2 models, and the evidence does not separate them.\n\nIn general "
        "reasoning, Alpha 2.5 is outside the leading band, at place 3 of 3 ranked models.\n\nAt 4"
        "0,000 input tokens and 4,000 output tokens, the list price is $0.112 a task.\n\nOn mmlu_"
        "pro, the two use a different unit, so ModelSpec does not compare them. The lab reports 8"
        "0% and the independent reading is 0.78 fraction.\n\nOn terminal_bench, the setups differ"
        " in effort, so ModelSpec shows both numbers and computes no difference. The lab reports "
        "50% and the independent reading is 48%.\n\nLab figures with no independent reading yet: "
        "cursorbench.\n\nModelSpec holds readings of this model that have not yet passed the seco"
        "nd key: quarantined: 1. Their values are not shown.\n\nlivecodebench has an independent "
        "reading of 72% and no lab figure.\n\nSpeed is not measured yet.\n\nDomains with no estim"
        "ate yet: engineering_stem, maths, legal, medical, finance, writing, marketing_seo, agent"
        "ic_tool_use, vision_documents, multilingual, chat_preference.\n\nLite: does not cover th"
        "e model.\n\nPro: covers the model.\n\nTeam: coverage not yet verified.\n\nGuaranteed fac"
        "ts still unknown: feature.batch, feature.effort_controls, feature.streaming, feature.str"
        "uctured_output, feature.tool_calling, licence.commercial_use, licence.fine_tuning, licen"
        "ce.output_training, model.max_output_tokens, model.output_modalities, model.release_date"
        ", offering.attestation.baa, offering.attestation.soc2, offering.data.retention, offering"
        ".data.trains_on_customer_data, offering.data.zero_retention, offering.price.batch_input,"
        " offering.price.batch_output, offering.price.cached_input, origin.base_lineage, origin.l"
        "ab_jurisdiction, origin.weights_hosting.\n\nDomains this class cannot be measured on, so"
        " not a gap: retrieval, because retrieval is graded on an embedding or reranking model's "
        "ranking, and this class is neither.\n\nSource: https://modelspec.dev/api/decision/snapsh"
        "ots/snap_ee376ecc9678d46b.json.gz (read 2026-09-26).\nSource: https://lab.example.com/al"
        "pha-launch (read 2026-09-20).\nSource: https://board.example.org/results (read 2026-09-2"
        "0).\nSource: https://lab.example.com/pricing (read 2026-09-26).\n\nNo referral fees, no "
        "paid placement, no provider-paid visibility, permanently.\n\nhttps://modelspec.dev/blog/"
        "lab-alpha/\n"
    ),
    "facebook": (
        "On swe_bench_pro the lab reports 70% and the independent reading is 67.9%.\n\nSource: ht"
        "tps://lab.example.com/alpha-launch (read 2026-09-20).\nSource: https://board.example.org"
        "/results (read 2026-09-20).\n\nNo referral fees, no paid placement, no provider-paid vis"
        "ibility, permanently.\n\nhttps://modelspec.dev/blog/lab-alpha/\n"
    ),
    "instagram": (
        "Make the image by hand.\n\nAlpha 2.5 is an analysis of alternatives for a text generator"
        ".\n\nThis model is in the leading band for software engineering; independent readings si"
        "t beside the lab's figures\n\nAlpha 2.5: on swe_bench_pro the lab reports 70% and the in"
        "dependent reading is 67.9%, 2.1 points lower.\n\nIn software engineering, Alpha 2.5 is i"
        "n the leading band. The band holds 2 models, and the evidence does not separate them.\n"
        "\nIn general reasoning, Alpha 2.5 is outside the leading band, at place 3 of 3 ranked mo"
        "dels.\n\nAt 40,000 input tokens and 4,000 output tokens, the list price is $0.112 a task"
        ".\n\nOn mmlu_pro, the two use a different unit, so ModelSpec does not compare them. The "
        "lab reports 80% and the independent reading is 0.78 fraction.\n\nOn terminal_bench, the "
        "setups differ in effort, so ModelSpec shows both numbers and computes no difference. The"
        " lab reports 50% and the independent reading is 48%.\n\nLab figures with no independent "
        "reading yet: cursorbench.\n\nModelSpec holds readings of this model that have not yet pa"
        "ssed the second key: quarantined: 1. Their values are not shown.\n\nlivecodebench has an"
        " independent reading of 72% and no lab figure.\n\nSpeed is not measured yet.\n\nDomains "
        "with no estimate yet: engineering_stem, maths, legal, medical, finance, writing, marketi"
        "ng_seo, agentic_tool_use, vision_documents, multilingual, chat_preference.\n\nLite: does"
        " not cover the model.\n\nPro: covers the model.\n\nTeam: coverage not yet verified.\n\nS"
        "ource: https://modelspec.dev/api/decision/snapshots/snap_ee376ecc9678d46b.json.gz (read "
        "2026-09-26).\nSource: https://lab.example.com/alpha-launch (read 2026-09-20).\nSource: h"
        "ttps://board.example.org/results (read 2026-09-20).\nSource: https://lab.example.com/pri"
        "cing (read 2026-09-26).\n\nNo referral fees, no paid placement, no provider-paid visibil"
        "ity, permanently.\n\nhttps://modelspec.dev/blog/lab-alpha/\n"
    ),
    "reddit": (
        "This model is in the leading band for software engineering; independent readings sit bes"
        "ide the lab's figures\n\nThis is ModelSpec.\n\nAlpha 2.5 is an analysis of alternatives "
        "for a text generator.\n\nThis model is in the leading band for software engineering; ind"
        "ependent readings sit beside the lab's figures\n\nAlpha 2.5: on swe_bench_pro the lab re"
        "ports 70% and the independent reading is 67.9%, 2.1 points lower.\n\nIn software enginee"
        "ring, Alpha 2.5 is in the leading band. The band holds 2 models, and the evidence does n"
        "ot separate them.\n\nIn general reasoning, Alpha 2.5 is outside the leading band, at pla"
        "ce 3 of 3 ranked models.\n\nAt 40,000 input tokens and 4,000 output tokens, the list pri"
        "ce is $0.112 a task.\n\nOn mmlu_pro, the two use a different unit, so ModelSpec does not"
        " compare them. The lab reports 80% and the independent reading is 0.78 fraction.\n\nOn t"
        "erminal_bench, the setups differ in effort, so ModelSpec shows both numbers and computes"
        " no difference. The lab reports 50% and the independent reading is 48%.\n\nLab figures w"
        "ith no independent reading yet: cursorbench.\n\nModelSpec holds readings of this model t"
        "hat have not yet passed the second key: quarantined: 1. Their values are not shown.\n\nl"
        "ivecodebench has an independent reading of 72% and no lab figure.\n\nSpeed is not measur"
        "ed yet.\n\nDomains with no estimate yet: engineering_stem, maths, legal, medical, financ"
        "e, writing, marketing_seo, agentic_tool_use, vision_documents, multilingual, chat_prefer"
        "ence.\n\nLite: does not cover the model.\n\nPro: covers the model.\n\nTeam: coverage not"
        " yet verified.\n\nGuaranteed facts still unknown: feature.batch, feature.effort_controls"
        ", feature.streaming, feature.structured_output, feature.tool_calling, licence.commercial"
        "_use, licence.fine_tuning, licence.output_training, model.max_output_tokens, model.outpu"
        "t_modalities, model.release_date, offering.attestation.baa, offering.attestation.soc2, o"
        "ffering.data.retention, offering.data.trains_on_customer_data, offering.data.zero_retent"
        "ion, offering.price.batch_input, offering.price.batch_output, offering.price.cached_inpu"
        "t, origin.base_lineage, origin.lab_jurisdiction, origin.weights_hosting.\n\nDomains this"
        " class cannot be measured on, so not a gap: retrieval, because retrieval is graded on an"
        " embedding or reranking model's ranking, and this class is neither.\n\nSource: https://m"
        "odelspec.dev/api/decision/snapshots/snap_ee376ecc9678d46b.json.gz (read 2026-09-26).\nSo"
        "urce: https://lab.example.com/alpha-launch (read 2026-09-20).\nSource: https://board.exa"
        "mple.org/results (read 2026-09-20).\nSource: https://lab.example.com/pricing (read 2026-"
        "09-26).\n\nTarget subreddit: r/LocalLLaMA. Its Limit Self-Promotion rule requires affili"
        "ation to be disclosed, and self-promotion to stay a small share of the account's posts a"
        "nd comments. No engagement farming. Its low-effort rule refuses undisclosed LLM-written "
        "copy. This draft is for a person to post, and only in r/LocalLLaMA. Do not cross-post.\n"
        "\nNo referral fees, no paid placement, no provider-paid visibility, permanently.\n\nhttp"
        "s://modelspec.dev/blog/lab-alpha/\n"
    ),
    "hackernews": (
        "This model is in the leading band for software engineering\n\nhttps://modelspec.dev/blog"
        "/lab-alpha/\n\nThis model is in the leading band for software engineering; independent r"
        "eadings sit beside the lab's figures\n\nSource: https://modelspec.dev/api/decision/snaps"
        "hots/snap_ee376ecc9678d46b.json.gz (read 2026-09-26).\nSource: https://lab.example.com/a"
        "lpha-launch (read 2026-09-20).\nSource: https://board.example.org/results (read 2026-09-"
        "20).\n\nAlpha 2.5: on swe_bench_pro the lab reports 70% and the independent reading is 6"
        "7.9%, 2.1 points lower.\n\nNo referral fees, no paid placement, no provider-paid visibil"
        "ity, permanently.\n\nJamie decides whether to submit.\n"
    ),
}


def test_signed_fixture_drafts_match_the_written_oracle(breakdown) -> None:
    """Expected text is written in this file. The test does not format it."""
    drafts = render_drafts(breakdown)
    for name, expected in _ORACLE.items():
        assert drafts[name].output == expected, name


def test_sample_drafts_exist_for_every_platform(breakdown) -> None:
    drafts = render_drafts(breakdown)
    assert set(drafts) == {"x", "linkedin", "facebook", "instagram", "reddit", "hackernews"}
    assert AUTOMATIC_POSTING is False
    assert all(draft.posted is False and draft.platform == name for name, draft in drafts.items())
    assert all(not hasattr(draft, "images") for draft in drafts.values())
    again = render_drafts(breakdown)
    assert [draft.output for draft in again.values()] == [draft.output for draft in drafts.values()]


def test_drafts_stay_neutral_and_never_name_an_excluded_source(breakdown) -> None:
    blob = "\n".join(draft.output for draft in render_drafts(breakdown).values())
    assert refused_words(blob) == []
    assert excluded_sources().text.search(blob) is None
    assert "router" not in blob.lower()


def test_x_thread_fits_and_opens_on_the_claims_gap(breakdown) -> None:
    draft = render_drafts(breakdown)["x"]
    assert draft.posts
    too_long = [(index, len(post)) for index, post in enumerate(draft.posts) if len(post) > 280]
    assert too_long == []
    hook = draft.posts[0]
    assert "swe_bench_pro" in hook
    assert "2.1" in hook and "lower" in hook
    assert "70%" in hook and "67.9%" in hook
    assert "lab reports 70%" in hook
    assert "independent reading is 67.9%" in hook
    assert draft.link in draft.output
    assert _LAB in draft.output and _BOARD in draft.output and _SNAPSHOT in draft.output


def test_linkedin_keeps_the_full_url(breakdown) -> None:
    draft = render_drafts(breakdown)["linkedin"]
    assert "analysis of alternatives" in draft.text
    assert len(draft.text) <= 3000
    assert draft.link in draft.text
    assert _NEUTRALITY in draft.text
    assert "text generator" in draft.text


def test_facebook_post_carries_the_hook_the_link_and_the_sources(breakdown) -> None:
    draft = render_drafts(breakdown)["facebook"]
    assert len(draft.text) <= 500
    assert draft.link in draft.text
    assert "70%" in draft.text and "67.9%" in draft.text
    assert _LAB in draft.text and _BOARD in draft.text and _READ_LAB in draft.text
    assert _NEUTRALITY in draft.text


def test_instagram_is_a_caption_and_tells_the_person_to_make_the_image(breakdown) -> None:
    draft = render_drafts(breakdown)["instagram"]
    assert _HAND in draft.text
    assert draft.link in draft.text
    assert len(draft.text) <= 2200
    assert "<svg" not in draft.output
    assert "70%" in draft.text and _LAB in draft.text


def test_reddit_draft_names_one_subreddit_and_does_not_cross_post(breakdown) -> None:
    draft = render_drafts(breakdown)["reddit"]
    assert draft.subreddit == "r/LocalLLaMA"
    assert len(draft.title) <= 300
    assert len(draft.text) <= 40_000
    assert draft.title == breakdown.headline.text
    assert "ModelSpec" in draft.text
    assert "Do not cross-post." in draft.text
    assert draft.cross_post is False
    assert set(re.findall(r"r/[A-Za-z0-9_]+", draft.text)) == {"r/LocalLLaMA"}
    assert "self-promotion" in draft.rules.lower()
    assert "disclos" in draft.rules.lower()
    assert draft.link in draft.text
    assert not any(character.isdigit() for character in draft.title)


def test_hacker_news_is_a_title_and_url_jamie_decides(breakdown) -> None:
    draft = render_drafts(breakdown)["hackernews"]
    assert draft.posts == ()
    assert len(draft.title) <= 80
    assert breakdown.headline.text.startswith(draft.title)
    assert draft.link in draft.submission
    assert draft.title in draft.submission
    assert "Jamie decides whether to submit" in draft.submission
    assert draft.jamie_decides is True
    assert _NEUTRALITY in draft.output
    assert not any(character.isdigit() for character in draft.title)


def test_caller_can_supply_the_breakdown_url(breakdown) -> None:
    url = "https://modelspec.dev/blog/lab-alpha-r1/"
    draft = render_drafts(breakdown, post_url=url)["x"]
    assert draft.link == url
    assert url in draft.output


def test_platform_module_has_no_posting_client() -> None:
    modules: list[str] = []
    for path in (Path("release_blog/platforms.py"), Path("release_blog/slots.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.append(node.module)
    banned = ("requests", "httpx", "urllib", "tweepy", "praw", "socket", "http", "subprocess")
    for name in modules:
        assert not any(name == item or name.startswith(item + ".") for item in banned), name
    source = Path("release_blog/platforms.py").read_text(encoding="utf-8")
    assert "render_card_html" not in source
    assert "<svg" not in source
    slots = Path("release_blog/slots.py").read_text(encoding="utf-8")
    assert "def data" not in slots
    assert "svg_claim_text" not in slots


def test_long_threads_keep_the_linkedin_url_and_disclosure(breakdown) -> None:
    url = "https://modelspec.dev/blog/example/"
    for repeats in (9, 15, 20):
        longer = _with_repeated_readings(breakdown, "terminal_bench", repeats)
        draft = render_drafts(longer, post_url=url)["linkedin"]
        assert url in draft.text
        assert breakdown.disclosures.neutrality in draft.text
        assert "analysis of alternatives" in draft.text
        assert len(draft.text) <= 3000


def test_disclosures_are_in_every_platforms_written_copy(breakdown) -> None:
    related = _related(breakdown, supplier=_SUPPLIER, early_access=_EARLY)
    for name, draft in render_drafts(related).items():
        assert _SUPPLIER in draft.output, name
        assert _EARLY in draft.output, name


def test_source_lines_accompany_the_numbers_they_belong_to(breakdown) -> None:
    for name, draft in render_drafts(breakdown).items():
        text = draft.output
        if "70%" in text:
            assert _LAB in text and _READ_LAB in text, name
        if "67.9%" in text:
            assert _BOARD in text and _READ_LAB in text, name
        if "2.1" in text:
            assert _SNAPSHOT in text and _READ_SNAP in text, name
        if "$0.112" in text:
            assert _PRICE in text and _READ_SNAP in text, name


@pytest.mark.parametrize(
    ("field", "value", "label"),
    [
        ("headline", "Alpha scored 99", "headline.text"),
        ("supplier", "ModelSpec delivers 99% accuracy.", "disclosures.supplier"),
        ("early_access", "Access started on day 1.", "disclosures.early_access"),
        ("neutrality", "No fees, pledge 1.", "disclosures.neutrality"),
    ],
)
def test_a_digit_in_prose_from_the_breakdown_is_rejected(breakdown, field, value, label) -> None:
    if field == "headline":
        related = breakdown.model_copy(
            update={"headline": breakdown.headline.model_copy(update={"text": value})}
        )
    else:
        related = _related(breakdown, **{field: value})
    with pytest.raises(ValueError, match=re.escape(label)):
        render_drafts(related)


def test_swapping_claim_and_reading_is_rejected(breakdown, monkeypatch) -> None:
    original = platforms._emit

    def swapped(pieces, source, post_url):
        text = original(pieces, source, post_url)
        return text.replace("70%", "SWAP").replace("67.9%", "70%").replace("SWAP", "67.9%")

    monkeypatch.setattr(platforms, "_emit", swapped)
    with pytest.raises(ValueError, match="manifest"):
        render_drafts(breakdown)


def test_a_digit_in_a_literal_is_rejected(breakdown, monkeypatch) -> None:
    from release_blog.slots import Literal

    with pytest.raises(ValueError, match="literal"):
        Literal("The extra figure is 70%.")
    original = platforms._hook_pieces

    def extra(source):
        original(source)
        return [Literal("The extra figure is 70%.")]

    monkeypatch.setattr(platforms, "_hook_pieces", extra)
    with pytest.raises(ValueError, match="literal"):
        render_drafts(breakdown)


def test_a_glued_digit_sequence_is_rejected(breakdown, monkeypatch) -> None:
    original = platforms._emit

    def extra(pieces, source, post_url):
        return original(pieces, source, post_url) + " score70%"

    monkeypatch.setattr(platforms, "_emit", extra)
    with pytest.raises(ValueError, match="digit sequence"):
        render_drafts(breakdown)


def test_bypassing_the_manifest_is_rejected(breakdown, monkeypatch) -> None:
    original = platforms._emit

    def extra(pieces, source, post_url):
        return original(pieces, source, post_url) + " Unreviewed."

    monkeypatch.setattr(platforms, "_emit", extra)
    with pytest.raises(ValueError, match="manifest"):
        render_drafts(breakdown)


def test_generate_writes_six_text_files_and_no_images(breakdown, tmp_path) -> None:
    folder = tmp_path / "release"
    folder.mkdir()
    breakdown_path = tmp_path / "breakdown.json"
    breakdown_path.write_bytes(to_bytes(breakdown))
    written = generate_from_breakdown(
        breakdown_path=breakdown_path,
        post_url=_URL,
        output_dir=folder / "social",
    )
    social = folder / "social"
    names = sorted(path.name for path in social.iterdir())
    assert names == [
        "facebook.txt",
        "hn.txt",
        "instagram.txt",
        "linkedin.txt",
        "reddit.md",
        "x.txt",
    ]
    assert set(written) == set(names)
    linkedin = (social / "linkedin.txt").read_text(encoding="utf-8")
    assert _URL in linkedin
    assert breakdown.disclosures.neutrality in linkedin
    assert "<svg" not in linkedin


def test_model_225_hook_uses_the_merged_pipeline(breakdown, tmp_path) -> None:
    """The merged #807 module calls this signature. No local author branch."""
    from release_blog.pipeline import _platforms

    folder = tmp_path / "release"
    folder.mkdir()
    breakdown_path = tmp_path / "breakdown.json"
    breakdown_path.write_bytes(to_bytes(breakdown))
    message = _platforms(breakdown_path, folder, "lab-alpha")
    assert message == "Platform drafts generated for manual review and posting."
    social = folder / "social"
    for name in ("x.txt", "linkedin.txt", "facebook.txt", "instagram.txt", "reddit.md", "hn.txt"):
        assert (social / name).is_file(), name
        assert "<svg" not in (social / name).read_text(encoding="utf-8")
    linkedin = (social / "linkedin.txt").read_text(encoding="utf-8")
    assert "https://modelspec.dev/blog/lab-alpha/" in linkedin
    assert breakdown.disclosures.neutrality in linkedin
