"""Platform drafts for a release breakdown (MODEL-226).

A draft is one string. It names what changed and which model, and it points
at the breakdown for every number. Expected text is written in this file.
"""

from __future__ import annotations

import ast
import json
import re
import unicodedata
from itertools import product
from pathlib import Path
from types import SimpleNamespace

import pytest

from decision.excluded import excluded_publisher, excluded_sources
from release_blog import platforms
from release_blog.breakdown import to_bytes
from release_blog.model import Breakdown
from release_blog.platforms import (
    AUTOMATIC_POSTING,
    generate_from_breakdown,
    posts_of,
    render_drafts,
)
from release_blog.tone import refused_words

_URL = "https://modelspec.dev/blog/lab-alpha/"
_NEUTRALITY = "No referral fees, no paid placement, no provider-paid visibility, permanently."
_SUPPLIER = "ModelSpec supplies evaluation services to this lab."
_EARLY = "ModelSpec received early access without editorial conditions."
_SUPPLIER_LINE = "ModelSpec has a supplier relationship with this lab; details in the breakdown."
_EARLY_LINE = "ModelSpec received early access to this model; details in the breakdown."
_HAND = "Make the image by hand."
_HOOK = "New model, new evidence: here is how it compares."
_HEADLINE = (
    "This model is in the leading band for software engineering; "
    "independent readings sit beside the lab's figures"
)
_COVER = "The breakdown covers the new model from lab."
_ANALYSIS = "ModelSpec is an analysis of alternatives."
_TEAMS = "ModelSpec is an analysis of alternatives for teams choosing a model."
_LINK = f"Read the full breakdown, with sources: {_URL}"
_RULES = (
    "Target subreddit: r/LocalLLaMA. "
    "Its Limit Self-Promotion rule requires affiliation to be disclosed, "
    "and self-promotion to stay a small share of the account's posts and comments. "
    "No engagement farming. "
    "Its low-effort rule refuses undisclosed LLM-written copy. "
    "This draft is for a person to post, and only in r/LocalLLaMA. "
    "Do not cross-post."
)
_BANNED_DRAFT = re.compile(
    r"(?<!\w)(?:best|fastest|cheapest|top|leading|greatest|strongest|smartest|"
    r"unbeatable|unmatched|number[\s-]+one|no\.\s*1|#1)(?!\w)",
    re.IGNORECASE,
)
_JAMIE = "Jamie decides whether to submit."
_NUMBER_CATEGORIES = frozenset({"Nd", "No", "Nl"})


# The headline, the benchmark sentence, and disclosure prose stay in the
# breakdown. A draft is reviewed copy plus a validated name, lab, and URL.
# Alpha 2.5 has a digit, so the draft says "the new model". The fixture
# provider is the copyable name "lab".
_ORACLE = {
    "x": (
        "New model, new evidence: here is how it compares.\n\n"
        "The breakdown covers the new model from lab.\n\n"
        "ModelSpec is an analysis of alternatives.\n\n"
        "No referral fees, no paid placement, no provider-paid visibility, permanently.\n\n"
        "Read the full breakdown, with sources: https://modelspec.dev/blog/lab-alpha/"
    ),
    "linkedin": (
        "New model, new evidence: here is how it compares.\n\n"
        "The breakdown covers the new model from lab.\n\n"
        "ModelSpec is an analysis of alternatives for teams choosing a model.\n\n"
        "No referral fees, no paid placement, no provider-paid visibility, permanently.\n\n"
        "Read the full breakdown, with sources: https://modelspec.dev/blog/lab-alpha/"
    ),
    "facebook": (
        "New model, new evidence: here is how it compares.\n\n"
        "The breakdown covers the new model from lab.\n\n"
        "ModelSpec is an analysis of alternatives.\n\n"
        "No referral fees, no paid placement, no provider-paid visibility, permanently.\n\n"
        "Read the full breakdown, with sources: https://modelspec.dev/blog/lab-alpha/"
    ),
    "instagram": (
        "Make the image by hand.\n\n"
        "New model, new evidence: here is how it compares.\n\n"
        "The breakdown covers the new model from lab.\n\n"
        "ModelSpec is an analysis of alternatives.\n\n"
        "No referral fees, no paid placement, no provider-paid visibility, permanently.\n\n"
        "Read the full breakdown, with sources: https://modelspec.dev/blog/lab-alpha/"
    ),
    "reddit": (
        "New model, new evidence: here is how it compares.\n\n"
        "This is ModelSpec.\n\n"
        "The breakdown covers the new model from lab.\n\n"
        "ModelSpec is an analysis of alternatives.\n\n"
        "Target subreddit: r/LocalLLaMA. "
        "Its Limit Self-Promotion rule requires affiliation to be disclosed, "
        "and self-promotion to stay a small share of the account's posts and comments. "
        "No engagement farming. "
        "Its low-effort rule refuses undisclosed LLM-written copy. "
        "This draft is for a person to post, and only in r/LocalLLaMA. "
        "Do not cross-post.\n\n"
        "No referral fees, no paid placement, no provider-paid visibility, permanently.\n\n"
        "Read the full breakdown, with sources: https://modelspec.dev/blog/lab-alpha/"
    ),
    "hackernews": (
        "New model, new evidence: here is how it compares.\n\n"
        "The breakdown covers the new model from lab.\n\n"
        "ModelSpec is an analysis of alternatives.\n\n"
        "No referral fees, no paid placement, no provider-paid visibility, permanently.\n\n"
        "Read the full breakdown, with sources: https://modelspec.dev/blog/lab-alpha/\n\n"
        "Jamie decides whether to submit."
    ),
}


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
        update={"disclosures": breakdown.disclosures.model_copy(update=disclosures)}
    )
    Breakdown.model_validate(related.model_dump(by_alias=True))
    return related


def _named(breakdown: Breakdown, name: str) -> Breakdown:
    return breakdown.model_copy(update={"model": breakdown.model.model_copy(update={"name": name})})


def _numberless(text: str, url: str) -> None:
    prose = " ".join(token for token in text.split() if token != url)
    assert url not in prose
    for character in prose:
        assert unicodedata.category(character) not in _NUMBER_CATEGORIES
        assert not character.isdigit()
        assert not character.isnumeric()
    folded = unicodedata.normalize("NFKC", prose).casefold()
    letters = "".join(character for character in folded if character.isalpha())
    assert "%" not in folded
    assert "percent" not in letters
    assert "percentage" not in letters
    assert _BANNED_DRAFT.search(prose) is None


def test_signed_fixture_drafts_match_the_written_oracle(breakdown) -> None:
    """Expected text is written in this file. The test does not format it."""
    drafts = render_drafts(breakdown)
    for name, expected in _ORACLE.items():
        assert drafts[name] == expected, name
        assert posts_of(drafts[name])
        assert "\n\n".join(posts_of(drafts[name])) == drafts[name]


def test_oracle_values_are_literals() -> None:
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    assignment = next(
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "_ORACLE" for target in node.targets)
    )
    oracle = ast.literal_eval(assignment.value)
    assert set(oracle) == set(_ORACLE)
    for text in oracle.values():
        assert isinstance(text, str)
        assert "Alpha 2.5" not in text
        _numberless(text, _URL)


def test_a_draft_has_no_second_text_attribute(breakdown) -> None:
    assert not hasattr(platforms, "Draft")
    drafts = render_drafts(breakdown)
    assert all(type(draft) is str for draft in drafts.values())


def test_sample_drafts_exist_for_every_platform(breakdown) -> None:
    drafts = render_drafts(breakdown)
    assert set(drafts) == {"x", "linkedin", "facebook", "instagram", "reddit", "hackernews"}
    assert AUTOMATIC_POSTING is False
    assert all(type(draft) is str for draft in drafts.values())
    assert render_drafts(breakdown) == drafts


def test_drafts_name_modelspec_and_carry_no_number(breakdown) -> None:
    assert breakdown.headline.text == _HEADLINE
    for name, draft in render_drafts(breakdown).items():
        assert "ModelSpec is an analysis of alternatives" in draft, name
        assert "Alpha 2.5" not in draft
        assert "the new model" in draft
        assert "text generator" not in draft
        assert "swe_bench_pro" not in draft
        assert _HEADLINE not in draft
        assert _HOOK in draft
        assert _LINK in draft
        assert _NEUTRALITY in draft
        _numberless(draft, _URL)
        assert refused_words(draft) == []
        assert excluded_sources().text.search(draft) is None
        assert excluded_publisher(draft) is False
        assert "router" not in draft.lower()


def test_x_thread_fits_and_opens_on_the_hook(breakdown) -> None:
    draft = render_drafts(breakdown)["x"]
    posts = posts_of(draft)
    assert posts
    assert [(index, len(post)) for index, post in enumerate(posts) if len(post) > 280] == []
    assert posts[0] == _HOOK
    assert "70%" not in draft
    assert "67.9%" not in draft
    assert "2.1" not in draft
    assert _URL in draft


def test_linkedin_keeps_the_full_url(breakdown) -> None:
    draft = render_drafts(breakdown)["linkedin"]
    assert "ModelSpec is an analysis of alternatives" in draft
    assert "teams choosing" in draft
    assert len(draft) <= 3000
    assert _URL in draft
    assert draft.split().count(_URL) == 1
    assert _NEUTRALITY in draft
    assert "text generator" not in draft


def test_facebook_post_carries_the_hook_and_the_link(breakdown) -> None:
    draft = render_drafts(breakdown)["facebook"]
    assert len(draft) <= 500
    assert _URL in draft
    assert _HOOK in draft
    assert _NEUTRALITY in draft
    assert "70%" not in draft


def test_instagram_is_a_caption_and_tells_the_person_to_make_the_image(breakdown) -> None:
    draft = render_drafts(breakdown)["instagram"]
    assert draft.startswith(_HAND)
    assert _URL in draft
    assert len(draft) <= 2200
    assert "<svg" not in draft
    assert "70%" not in draft


def test_reddit_draft_names_one_subreddit_and_does_not_cross_post(breakdown) -> None:
    draft = render_drafts(breakdown)["reddit"]
    posts = posts_of(draft)
    assert posts[0] == _HOOK
    assert breakdown.headline.text not in draft
    assert len(posts[0]) <= 300
    assert len(draft) <= 40_000
    assert "This is ModelSpec." in draft
    assert "ModelSpec is an analysis of alternatives" in draft
    assert "Do not cross-post." in draft
    assert set(re.findall(r"r/[A-Za-z0-9_]+", draft)) == {"r/LocalLLaMA"}
    assert "self-promotion" in draft.lower()
    assert "disclos" in draft.lower()
    assert _URL in draft
    _numberless(posts[0], _URL)


def test_hacker_news_is_a_title_and_url_jamie_decides(breakdown) -> None:
    draft = render_drafts(breakdown)["hackernews"]
    posts = posts_of(draft)
    assert posts[0] == _HOOK
    assert len(posts[0]) <= 80
    assert breakdown.headline.text not in draft
    assert _HOOK in draft
    assert _URL in draft
    assert _JAMIE in draft
    assert _NEUTRALITY in draft
    _numberless(posts[0], _URL)


def test_caller_can_supply_the_breakdown_url(breakdown) -> None:
    url = "https://modelspec.dev/blog/lab-alpha-r1/"
    draft = render_drafts(breakdown, post_url=url)["x"]
    assert url in draft
    assert f"Read the full breakdown, with sources: {url}" in draft
    _numberless(draft, url)


def test_platform_module_has_no_posting_client_or_fact_slots() -> None:
    assert not Path("release_blog/slots.py").exists()
    path = Path("release_blog/platforms.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    banned = ("requests", "httpx", "urllib", "tweepy", "praw", "socket", "http", "subprocess")
    for name in modules:
        assert not any(name == item or name.startswith(item + ".") for item in banned), name
    source = path.read_text(encoding="utf-8")
    assert "release_blog.slots" not in source
    assert "render_card_html" not in source
    assert "<svg" not in source


def test_long_threads_keep_the_linkedin_url_and_disclosure(breakdown) -> None:
    url = "https://modelspec.dev/blog/example/"
    for repeats in (9, 15, 20):
        longer = _with_repeated_readings(breakdown, "terminal_bench", repeats)
        draft = render_drafts(longer, post_url=url)["linkedin"]
        assert url in draft
        assert breakdown.disclosures.neutrality in draft
        assert "ModelSpec is an analysis of alternatives" in draft
        assert len(draft) <= 3000
        _numberless(draft, url)


def test_disclosures_are_in_every_platforms_written_copy(breakdown, tmp_path) -> None:
    """A disclosure flag selects a fixed sentence. The breakdown sentence stays out."""
    related = _related(breakdown, supplier=_SUPPLIER, early_access=_EARLY)
    files = _saved(related, tmp_path)
    for name, draft in files.items():
        assert _SUPPLIER_LINE in draft, name
        assert _EARLY_LINE in draft, name
        assert _SUPPLIER not in draft, name
        assert _EARLY not in draft, name
        assert len(draft) <= {"facebook": 500, "x": 10_000}.get(name, 40_000)
        _numberless(draft, _URL)


def test_a_digit_free_name_is_used_and_versioned_names_are_not(breakdown) -> None:
    versioned = render_drafts(breakdown)
    assert all("Alpha 2.5" not in draft for draft in versioned.values())
    assert all("the new model" in draft for draft in versioned.values())
    clean = render_drafts(_named(breakdown, "Alpha"))
    assert all("Alpha 2.5" not in draft for draft in clean.values())
    assert all("The breakdown covers Alpha from lab." in draft for draft in clean.values())
    assert all(
        f"Read the full breakdown of Alpha, with sources: {_URL}" in draft
        for draft in clean.values()
    )
    aliased = breakdown.model_copy(update={"names": {breakdown.model.id: "Alpha"}})
    drafts = render_drafts(aliased)
    assert all("Alpha 2.5" not in draft for draft in drafts.values())
    assert all("The breakdown covers Alpha from lab." in draft for draft in drafts.values())


@pytest.mark.parametrize(
    ("field", "value", "label"),
    [
        ("headline", "Alpha scored 99", "headline.text"),
        ("supplier", "ModelSpec delivers 99% accuracy.", "disclosures.supplier"),
        ("early_access", "Access started on day 1.", "disclosures.early_access"),
        ("neutrality", "No fees, pledge 1.", "disclosures.neutrality"),
    ],
)
def test_a_digit_in_prose_from_the_breakdown_is_rejected(
    breakdown, tmp_path, field, value, label
) -> None:
    """Free text is not copied, so a digit in it cannot reach a saved draft."""
    if field == "headline":
        related = breakdown.model_copy(
            update={"headline": breakdown.headline.model_copy(update={"text": value})}
        )
    else:
        related = _related(breakdown, **{field: value})
    files = _saved(related, tmp_path)
    assert files
    for name, draft in files.items():
        assert value not in draft, (label, name)
        _numberless(draft, _URL)


@pytest.mark.parametrize("character", ["⁷⁰", "②", "①", "٣", "½", "Ⅳ"])
def test_unicode_digits_in_a_literal_are_rejected(breakdown, monkeypatch, character) -> None:
    monkeypatch.setattr(platforms, "_HAND", platforms._HAND + character)
    with pytest.raises(ValueError, match="digit"):
        render_drafts(breakdown)


@pytest.mark.parametrize("character", ["⁷⁰", "②", "①", "٣"])
@pytest.mark.parametrize(
    ("field", "label"),
    [
        ("headline", "headline.text"),
        ("supplier", "disclosures.supplier"),
        ("early_access", "disclosures.early_access"),
        ("neutrality", "disclosures.neutrality"),
    ],
)
def test_unicode_digits_in_inputs_are_rejected(
    breakdown, tmp_path, character, field, label
) -> None:
    value = f"Noted {character}"
    if field == "headline":
        related = breakdown.model_copy(
            update={"headline": breakdown.headline.model_copy(update={"text": value})}
        )
    else:
        related = _related(breakdown, **{field: value})
    files = _saved(related, tmp_path)
    for name, draft in files.items():
        assert value not in draft, (label, name)
        assert character not in draft, (label, name)


def test_a_unicode_digit_in_a_model_name_is_not_copied(breakdown) -> None:
    drafts = render_drafts(_named(breakdown, "Alpha⁷⁰"))
    blob = "\n".join(draft for draft in drafts.values())
    assert "Alpha⁷⁰" not in blob
    assert "⁷⁰" not in blob
    assert "the new model" in blob


def test_a_swapped_number_is_rejected(breakdown, monkeypatch) -> None:
    original = platforms._draft_text

    def swapped(breakdown, platform, post_url):
        text = original(breakdown, platform, post_url)
        return text + "\n\nThe lab reports 67.9% and the independent reading is 70%."

    monkeypatch.setattr(platforms, "_draft_text", swapped)
    with pytest.raises(ValueError, match="digit"):
        render_drafts(breakdown)


def test_a_glued_digit_sequence_is_rejected(breakdown, monkeypatch) -> None:
    original = platforms._draft_text

    def extra(breakdown, platform, post_url):
        return original(breakdown, platform, post_url) + " score70%"

    monkeypatch.setattr(platforms, "_draft_text", extra)
    with pytest.raises(ValueError, match="digit"):
        render_drafts(breakdown)


def test_a_number_via_any_attribute_is_rejected(breakdown, monkeypatch) -> None:
    original = platforms._assemble

    def leaky(breakdown, post_url):
        drafts = original(breakdown, post_url)
        return {name: SimpleNamespace(text=draft, aside="70") for name, draft in drafts.items()}

    monkeypatch.setattr(platforms, "_assemble", leaky)
    with pytest.raises(ValueError, match="aside"):
        render_drafts(breakdown)


@pytest.mark.parametrize("addition", [" percent", " per cent", " %"])
def test_a_spelled_percent_is_rejected(breakdown, monkeypatch, addition) -> None:
    original = platforms._draft_text

    def extra(breakdown, platform, post_url):
        return original(breakdown, platform, post_url) + addition

    monkeypatch.setattr(platforms, "_draft_text", extra)
    with pytest.raises(ValueError, match="percent"):
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
    drafts = render_drafts(breakdown, post_url=_URL)
    files = {
        "x": "x.txt",
        "linkedin": "linkedin.txt",
        "facebook": "facebook.txt",
        "instagram": "instagram.txt",
        "reddit": "reddit.md",
        "hackernews": "hn.txt",
    }
    for platform, filename in files.items():
        assert (social / filename).read_text(encoding="utf-8") == drafts[platform] + "\n"
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
        text = (social / name).read_text(encoding="utf-8")
        assert text
        assert "<svg" not in text
        assert "https://modelspec.dev/blog/lab-alpha/" in text
    linkedin = (social / "linkedin.txt").read_text(encoding="utf-8")
    assert breakdown.disclosures.neutrality in linkedin


def _with_headline(breakdown: Breakdown, text: str) -> Breakdown:
    return breakdown.model_copy(
        update={"headline": breakdown.headline.model_copy(update={"text": text})}
    )


def _saved(breakdown: Breakdown, tmp_path: Path, post_url: str = _URL) -> dict[str, str]:
    """The six files `generate_from_breakdown` writes for one breakdown."""
    source = tmp_path / "breakdown.json"
    source.write_bytes(to_bytes(breakdown))
    written = generate_from_breakdown(
        breakdown_path=source, post_url=post_url, output_dir=tmp_path / "social"
    )
    assert len(written) == 6
    return {name: Path(path).read_text(encoding="utf-8") for name, path in written.items()}


def _set_path(breakdown: Breakdown, path: str, value: str) -> Breakdown:
    data = breakdown.model_dump(by_alias=True)
    node = data
    parts = path.split(".")
    for part in parts[:-1]:
        node = node[part]
    node[parts[-1]] = value
    return Breakdown.model_validate(data)


@pytest.mark.parametrize(
    ("kind", "value"),
    [
        ("changed", "https://modelspec.dev/blog/lab-alpha/extra/"),
        ("changed", "https://modelspec.dev/blog/alpha-r1/wrong/"),
        ("nested", "https://example.org/?destination=https://modelspec.dev/blog/lab-alpha/"),
        ("nested", "https://example.org/?destination=https://modelspec.dev/blog/alpha-r1/"),
        ("whitespace", "https://modelspec.dev/blog/ 70%"),
        ("whitespace", "https://modelspec.dev/blog/ seventy percent"),
    ],
)
def test_the_breakdown_url_is_an_exact_token(breakdown, monkeypatch, kind, value) -> None:
    """The URL is validated, then accepted only as a whole token equal to it."""
    source = Path("release_blog/platforms.py").read_text(encoding="utf-8")
    assert "replace(post_url" not in source
    if kind == "whitespace":
        with pytest.raises(ValueError, match="post_url"):
            render_drafts(breakdown, post_url=value)
        return
    url = (
        "https://modelspec.dev/blog/alpha-r1/"
        if "alpha-r1" in value
        else "https://modelspec.dev/blog/lab-alpha/"
    )
    original = platforms._draft_text

    def mutated(source, name, target):
        return " ".join(
            value if token == target else token for token in original(source, name, target).split()
        )

    monkeypatch.setattr(platforms, "_draft_text", mutated)
    with pytest.raises(ValueError, match="url"):
        render_drafts(breakdown, post_url=url)


@pytest.mark.parametrize(
    "value",
    ["seventypercent", "seventyPercent", "seventyper cent", "per-cent"],
)
def test_a_glued_percent_word_is_rejected(breakdown, tmp_path, value) -> None:
    related = _related(breakdown, supplier=f"Reported {value}.")
    files = _saved(related, tmp_path)
    for draft in files.values():
        assert value not in draft
        _numberless(draft, _URL)


@pytest.mark.parametrize(
    ("kind", "value"),
    [
        ("headline", "The best coding model."),
        ("headline", "The fastest coding model."),
        ("headline", "The number-one coding model."),
        ("headline", "The number one coding model."),
        ("draft", "The leading release."),
        ("draft", "The number-one release."),
        ("draft", "This is number one."),
        ("draft", "It is no. 1 today."),
        ("draft", "Ranked #1 overall."),
    ],
)
def test_a_superlative_is_rejected(breakdown, tmp_path, monkeypatch, kind, value) -> None:
    if kind == "headline":
        files = _saved(_with_headline(breakdown, value), tmp_path)
        for draft in files.values():
            assert value not in draft
            assert _BANNED_DRAFT.search(draft) is None
        return
    original = platforms._draft_text

    def extra(source, name, target):
        return original(source, name, target) + "\n\n" + value

    monkeypatch.setattr(platforms, "_draft_text", extra)
    with pytest.raises(ValueError, match="superlative"):
        render_drafts(breakdown)


def test_returned_drafts_are_plain_strings(breakdown) -> None:
    drafts = render_drafts(breakdown)
    assert [type(draft) for draft in drafts.values()] == [str, str, str, str, str, str]


def test_a_band_headline_stays_in_the_breakdown_and_out_of_the_draft(breakdown) -> None:
    sole = "This model is the only model in the best band for software engineering."
    drafts = render_drafts(_with_headline(breakdown, sole))
    assert all(type(draft) is str for draft in drafts.values())
    assert all("best" not in draft.casefold() for draft in drafts.values())
    assert all(sole not in draft for draft in drafts.values())


def test_platforms_do_not_read_breakdown_prose() -> None:
    """The allowlist is structural: those fields are not mentioned in the writer."""
    source = Path("release_blog/platforms.py").read_text(encoding="utf-8")
    assert "headline" not in source
    assert "disclosures.neutrality" not in source
    assert "claims_vs_evidence" not in source
    assert ".benchmark" not in source


_AA_WIDE = "Artificial" + "  " + "Analysis"
_AA_MIXED = "Artificial" + " - . " + "Analysis"
_ZAP = "Zap" + "ier"


@pytest.mark.parametrize(
    ("finding", "path", "payload", "banned"),
    [
        ("r1-chart-text", "headline.text", "<text>99%</text>", ("<text>99%</text>", "99%")),
        ("r1-card-html", "headline.text", "<p>The score is 99%.</p>", ("99%", "<p>")),
        (
            "r2-unrelated-number",
            "headline.text",
            '<text x="50" y="50">70%</text>',
            ("70%",),
        ),
        (
            "r3-supplier-digit",
            "disclosures.supplier",
            "ModelSpec delivers 99% accuracy.",
            ("99%", "delivers 99%"),
        ),
        (
            "r3-svg-paragraph",
            "disclosures.early_access",
            "<p>The score is 99%.</p>",
            ("99%",),
        ),
        (
            "r3-source-url",
            "headline.text",
            "See https://lab.example.com/alpha-launch today.",
            ("https://lab.example.com/alpha-launch",),
        ),
        ("r4-superscript", "headline.text", "Noted score⁷⁰ here", ("⁷⁰", "score⁷⁰")),
        (
            "r4-swapped-percents",
            "headline.text",
            "the lab reports 67.9% and the independent reading is 70%",
            ("67.9", "70%"),
        ),
        (
            "r5-glued-percent",
            "disclosures.supplier",
            "Reported seventypercent.",
            ("seventypercent",),
        ),
        ("r5-hyphen-percent", "disclosures.supplier", "Reported per-cent.", ("per-cent",)),
        ("r5-best", "headline.text", "The best coding model.", ("The best coding model.",)),
        (
            "r5-fastest",
            "headline.text",
            "The fastest coding model.",
            ("The fastest coding model.",),
        ),
        (
            "r6-scheme-relative-link",
            "disclosures.supplier",
            "See [source](//example.org/).",
            ("[source](//example.org/)", "//example.org"),
        ),
        (
            "r6-wide-publisher",
            "headline.text",
            _AA_WIDE + " measured this model.",
            (_AA_WIDE,),
        ),
        (
            "r6-number-one",
            "headline.text",
            "The number-one coding model.",
            ("number-one",),
        ),
        ("name-number-one", "model.name", "Number-one", ("Number-one",)),
        ("name-mixed-publisher", "model.name", _AA_MIXED, (_AA_MIXED,)),
        ("name-wide-publisher", "model.name", _AA_WIDE, (_AA_WIDE,)),
        ("name-underscore", "model.name", "Beta_Two", ("Beta_Two",)),
        ("lab-publisher", "model.provider", _ZAP, (_ZAP,)),
        ("lab-underscore", "model.provider", "Lab_Alpha", ("Lab_Alpha",)),
        ("class-prose", "model.class", "Special Class", ("Special Class",)),
        (
            "neutrality-prose",
            "disclosures.neutrality",
            "A different pledge sentence for this lab.",
            ("A different pledge sentence for this lab.",),
        ),
    ],
)
def test_review_finding_never_enters_a_saved_draft(
    breakdown, tmp_path, finding, path, payload, banned
) -> None:
    """One file-backed probe per REV-808 finding that carried breakdown text."""
    if path == "alias":
        related = breakdown.model_copy(update={"names": {breakdown.model.id: payload}})
    else:
        related = _set_path(breakdown, path, payload)
    files = _saved(related, tmp_path)
    for name, draft in files.items():
        for piece in banned:
            assert piece not in draft, (finding, name, piece)
        prose = " ".join(token for token in draft.split() if token != _URL)
        assert "[" not in prose, finding
        assert "](" not in prose, finding
        assert "//" not in prose, finding
        _numberless(draft, _URL)
        if path == "model.provider":
            assert "from the lab." in draft, finding
        if path == "model.name":
            assert "the new model" in draft, finding
        if path == "disclosures.neutrality":
            assert _NEUTRALITY in draft, finding


def test_a_copyable_name_and_lab_are_used(breakdown, tmp_path) -> None:
    named = _set_path(_named(breakdown, "Beta Prime"), "model.provider", "Lab Alpha")
    files = _saved(named, tmp_path)
    for draft in files.values():
        assert "The breakdown covers Beta Prime from Lab Alpha." in draft
        assert f"Read the full breakdown of Beta Prime, with sources: {_URL}" in draft


def test_repeated_readings_still_keep_the_exact_url(breakdown, tmp_path) -> None:
    """R1 LinkedIn dropped the link once optional copy filled the post."""
    longer = _with_repeated_readings(breakdown, "terminal_bench", 20)
    files = _saved(longer, tmp_path, post_url="https://modelspec.dev/blog/example/")
    assert set(files) == {
        "x.txt",
        "linkedin.txt",
        "facebook.txt",
        "instagram.txt",
        "reddit.md",
        "hn.txt",
    }
    for name, draft in files.items():
        assert "<svg" not in draft, name
        assert draft.split().count("https://modelspec.dev/blog/example/") == 1
        assert "70%" not in draft
        assert "67.9%" not in draft
        assert "2.1" not in draft
        assert "$0.112" not in draft
    assert len(files["linkedin.txt"]) <= 3000


def test_every_separator_run_rejects_both_publishers(breakdown, tmp_path: Path) -> None:
    """Every separator run is excluded, including inside a longer name."""
    runs = [
        "".join(parts)
        for length in range(1, 5)
        for parts in product(" \t\n-_.", repeat=length)
    ]
    assert len(runs) == 1554
    pairs = (("Artificial", "Analysis"), ("Zap", "ier"))
    predicate_misses = []
    for left, right in pairs:
        for sep in runs:
            for text in (f"{left}{sep}{right}", f"Model {left}{sep}{right} name"):
                if not excluded_publisher(text):
                    predicate_misses.append(text)
    for text in (
        "ArtificialAnalysisPro",
        "artificialanalysis.ai",
        "zapier.com",
        "https://artificialanalysis.ai/models",
        "https://zapier.com/apps",
    ):
        if not excluded_publisher(text):
            predicate_misses.append(text)
    assert excluded_publisher("The artificial lighting analysis is separate.") is False

    data = breakdown.model_dump(mode="json", by_alias=True)
    model_id = data["model"]["id"]
    original_name = data["model"]["name"]
    original_provider = data["model"]["provider"]
    original_alias = data["names"].get(model_id)
    source = tmp_path / "breakdown.json"
    out = tmp_path / "social"
    leaks = []

    def drafts_for(field: str, payload: str) -> dict[str, str]:
        data["model"]["name"] = original_name
        data["model"]["provider"] = original_provider
        if original_alias is None:
            data["names"].pop(model_id, None)
        else:
            data["names"][model_id] = original_alias
        if field == "name":
            data["model"]["name"] = payload
        elif field == "provider":
            data["model"]["provider"] = payload
        else:
            data["names"][model_id] = payload
        source.write_text(json.dumps(data), encoding="utf-8")
        written = generate_from_breakdown(
            breakdown_path=source, post_url=_URL, output_dir=out
        )
        assert len(written) == 6
        return {name: Path(path).read_text(encoding="utf-8") for name, path in written.items()}

    payloads = [
        text
        for left, right in pairs
        for sep in runs
        for text in (f"{left}{sep}{right}", f"Model {left}{sep}{right} name")
    ]
    payloads.extend(("ArtificialAnalysisPro", "artificialanalysis.ai", "zapier.com"))
    for payload in payloads:
        for field in ("name", "alias", "provider"):
            drafts = drafts_for(field, payload)
            kept = any(payload in draft for draft in drafts.values())
            if field == "provider":
                replaced = all("from the lab." in draft for draft in drafts.values())
            else:
                replaced = all("the new model" in draft for draft in drafts.values())
            if kept or not replaced:
                leaks.append((field, payload))
    assert predicate_misses == [] and leaks == [], (
        f"{len(predicate_misses)} predicate misses, {len(leaks)} drafts kept a publisher; "
        f"first miss {predicate_misses[:2]!r}; first leak {leaks[:2]!r}"
    )
