"""The build refuses a repeated key in verification log rows and fact YAML (MODEL-554).

Last-key-wins would let a row that says ``mismatch`` and then ``verified`` read as verified,
and a fact that repeats ``value`` read as its last spelling. Every fixture is synthetic.
"""

from __future__ import annotations

import hashlib
import json

import pytest
import yaml
from decision.cited_change import LookupFailed, quarantine_verdicts
from decision.owner_ruling import (
    RULINGS_FILE,
    RepeatedKeyError,
    read_json_lines,
    read_ruling_inputs,
)
from decision.snapshot import SnapshotBuildError, collect_repo
from decision.verify import VerificationLog
from pipeline.load import LoadError, load_benchmarks, load_models

from tests.snapshot_records import verification

MID = "lab/alpha"
FACT_ID = f"{MID}#model.context_window"


def _row(outcome="mismatch") -> str:
    return json.dumps(verification("fact", FACT_ID, outcome))


#: The same row, with ``outcome`` repeated: plainly, escaped, and inside ``target``.
REPEATED_OUTCOME = _row()[:-1] + ', "outcome": "verified"}'
ESCAPED_OUTCOME = _row()[:-1] + ', "outc\\u006fme": "verified"}'
NESTED_ESCAPED = _row().replace('"kind": "fact"', '"kind": "fact", "\\u006bind": "evidence"')


def _repo(root, *, log=(), card=None, benchmark=None, offering=None, subscription=None):
    """A synthetic data checkout with only what each test needs."""
    (root / "registry").mkdir(parents=True)
    (root / "registry/sources.yaml").write_text(yaml.safe_dump(
        {"schema_version": 1, "sources": [{"id": "src-a", "url": "https://example.com/a"}]}))
    (root / "verification").mkdir()
    (root / "verification/log.jsonl").write_text("".join(line + "\n" for line in log))
    if card is not None:
        (root / f"models/{MID}.md").parent.mkdir(parents=True)
        (root / f"models/{MID}.md").write_text(card)
    if benchmark is not None:
        (root / "benchmarks").mkdir()
        (root / "benchmarks/bench-a.md").write_text(benchmark)
    if offering is not None:
        (root / f"offerings/host/{MID}.yaml").parent.mkdir(parents=True)
        (root / f"offerings/host/{MID}.yaml").write_text(offering)
    if subscription is not None:
        (root / "offerings/subscriptions").mkdir(parents=True)
        (root / "offerings/subscriptions/host.yaml").write_text(subscription)
    return root


# --- verification/log.jsonl ----------------------------------------------------------------------


@pytest.mark.parametrize("line", [REPEATED_OUTCOME, ESCAPED_OUTCOME, NESTED_ESCAPED],
                         ids=["repeated-outcome", "escaped-outcome", "nested-escaped"])
def test_the_snapshot_refuses_a_log_row_that_repeats_a_key(tmp_path, line):
    assert json.loads(line)["outcome"] in {"verified", "mismatch"}  # last-key-wins reads it
    _repo(tmp_path, log=[_row("verified"), line, _row()])
    with pytest.raises(SnapshotBuildError) as refused:
        collect_repo(tmp_path)
    message = str(refused.value)
    assert message.endswith("log.jsonl: line 2: a JSON object repeats a key "
                            "(1 line(s) repeat a key)")
    assert "verified" not in message and "mismatch" not in message and MID not in message


def test_the_refusal_counts_every_line_that_repeats_a_key(tmp_path):
    _repo(tmp_path, log=[_row(), REPEATED_OUTCOME, "", ESCAPED_OUTCOME])
    with pytest.raises(RepeatedKeyError,
                       match=r"log\.jsonl: line 2: .* \(2 line\(s\) repeat a key\)$"):
        read_json_lines(tmp_path / "verification/log.jsonl")


def test_a_log_without_a_repeated_key_reads_as_json_loads_reads_it(tmp_path):
    lines = [_row("verified"), _row(), "[1, 2]"]
    _repo(tmp_path, log=lines)
    assert read_json_lines(tmp_path / "verification/log.jsonl") == [json.loads(x) for x in lines]
    assert collect_repo(tmp_path).verifications == [json.loads(x) for x in lines]


@pytest.mark.parametrize("line", [REPEATED_OUTCOME, ESCAPED_OUTCOME],
                         ids=["repeated-outcome", "escaped-outcome"])
def test_every_other_reader_of_the_log_refuses_it_too(tmp_path, line):
    _repo(tmp_path, log=[line])
    # The site's owner-ruling inputs (``pipeline.load.load_models`` reads the log through them).
    (tmp_path / RULINGS_FILE).write_text("{}\n")
    with pytest.raises(RepeatedKeyError, match=r"log\.jsonl: line 1: a JSON object"):
        read_ruling_inputs(tmp_path)
    # The rule-15 quarantine lookup, which parses the log as the build parses it.
    with pytest.raises(LookupFailed, match="RepeatedKeyError"):
        quarantine_verdicts([FACT_ID], {}, tmp_path)
    # The verification tooling's own reader (its message is redacted for private data).
    with pytest.raises(ValueError, match="line 1: .*RepeatedKeyError|line 1: a JSON object"):
        VerificationLog(tmp_path / "verification").records()


# --- fact YAML -----------------------------------------------------------------------------------


CARD = """---
model_id: lab/alpha
display_name: Alpha
facts:
  - facet: model.context_window
    value: 128000
    state: known
    value: 262144
    sources:
      - source_id: src-a
---
Synthetic fixture.
"""

#: The same card with the repeated key in a quoted spelling.
QUOTED_CARD = CARD.replace("    value: 262144", '    "value": 262144')

BENCHMARK = """---
id: bench-a
name: Bench A
metric:
  direction: higher_is_better
  direction: lower_is_better
---
Synthetic fixture.
"""

OFFERING = """- provider: host
  model: lab/alpha
  facts:
    - facet: offering.price.input
      value: 1.0
      value: 0.5
"""

SUBSCRIPTION = """- provider: host
  plan: pro
  plan: plus
  facts: []
"""


@pytest.mark.parametrize("card", [CARD, QUOTED_CARD], ids=["plain", "quoted"])
def test_both_paths_refuse_a_card_fact_that_repeats_a_key(tmp_path, card):
    _repo(tmp_path, card=card)
    for path in (collect_repo, load_models):  # the snapshot path, then the site path
        with pytest.raises(LoadError) as refused:
            path(tmp_path)
        message = str(refused.value)
        assert message.endswith("alpha.md: duplicate_yaml_key: line 8, column 5 "
                                "(1 repeated key(s))")
        assert "262144" not in message and "128000" not in message


def test_both_paths_refuse_a_benchmark_page_that_repeats_a_key(tmp_path):
    _repo(tmp_path, benchmark=BENCHMARK)
    for path in (collect_repo, load_benchmarks):
        with pytest.raises(LoadError, match=r"bench-a\.md: duplicate_yaml_key: line 6, column 3"):
            path(tmp_path)


@pytest.mark.parametrize(("kind", "line"), [("offering", 6), ("subscription", 3)])
def test_the_build_refuses_an_offering_file_that_repeats_a_key(tmp_path, kind, line):
    # The site reads offerings only through the snapshot build (``build_from_repo``).
    _repo(tmp_path, **{kind: OFFERING if kind == "offering" else SUBSCRIPTION})
    with pytest.raises(SnapshotBuildError) as refused:
        collect_repo(tmp_path)
    message = str(refused.value)
    assert message.endswith(f".yaml: duplicate_yaml_key: line {line}, column "
                            f"{7 if kind == 'offering' else 3} (1 repeated key(s))")
    assert "0.5" not in message and "plus" not in message


#: A page that repeats only ``aliases``, the frozen image's one repeated key.
ALIASES_PAGE = """---
id: bench-a
aliases: ["bench-a"]
name: Bench A
aliases:
  - Bench A
---
Synthetic fixture.
"""


def _pin(monkeypatch, path):
    """Exempt exactly this file, as ``FROZEN_DUPLICATE_PAGES`` exempts the image's pages."""
    import pipeline.load as load

    monkeypatch.setattr(load, "FROZEN_DUPLICATE_PAGES",
                        {path.name: hashlib.sha256(path.read_bytes()).hexdigest()})


def test_a_pinned_frozen_page_warns_as_a_count_and_keeps_its_last_value(
        tmp_path, monkeypatch, caplog):
    _repo(tmp_path, benchmark=ALIASES_PAGE)
    _pin(monkeypatch, tmp_path / "benchmarks/bench-a.md")
    with caplog.at_level("WARNING", logger="pipeline.load"):
        [page] = load_benchmarks(tmp_path)
    assert page.front["aliases"] == ["Bench A"]
    [record] = [r for r in caplog.records if "duplicate_yaml_key" in r.getMessage()]
    assert "line 5, column 1 (1 repeated key(s))" in record.getMessage()
    assert "Bench A" not in record.getMessage()


@pytest.mark.parametrize("change", ["body", "front", "renamed", "card", "other-key"])
def test_anything_but_the_exact_pinned_page_is_refused(tmp_path, monkeypatch, change):
    """The exemption holds for one file name, its exact bytes and ``aliases`` alone."""
    _repo(tmp_path, benchmark=BENCHMARK if change == "other-key" else ALIASES_PAGE)
    page = tmp_path / "benchmarks/bench-a.md"
    _pin(monkeypatch, page)
    if change == "body":
        page.write_text(page.read_text() + "One more line.\n")
    elif change == "front":
        page.write_text(page.read_text().replace("name: Bench A", "name: Bench B"))
    elif change == "renamed":
        page.rename(page.with_name("bench-b.md"))
    elif change == "card":
        # The same bytes at a card path, under the pinned name.
        card = tmp_path / "models/lab/bench-a.md"
        card.parent.mkdir(parents=True)
        card.write_bytes(page.read_bytes().replace(b"id: bench-a", b"model_id: lab/bench-a"))
        _pin(monkeypatch, card)
        with pytest.raises(LoadError, match="duplicate_yaml_key"):
            load_models(tmp_path)
        return
    with pytest.raises(LoadError, match="duplicate_yaml_key"):
        load_benchmarks(tmp_path)


def test_a_page_read_without_its_path_is_never_exempt(monkeypatch, tmp_path):
    from pipeline.load import split_front_matter

    _repo(tmp_path, benchmark=ALIASES_PAGE)
    _pin(monkeypatch, tmp_path / "benchmarks/bench-a.md")
    with pytest.raises(LoadError, match="^front matter: duplicate_yaml_key"):
        split_front_matter(ALIASES_PAGE)


def test_the_public_image_repeats_only_on_its_pinned_pages_and_still_loads():
    """The frozen image still builds, and every page of it that repeats a key is pinned by
    name and bytes; a new repeat could not be added without failing this."""
    from pipeline.load import FRONT_MATTER, FROZEN_DUPLICATE_PAGES, REPO_ROOT
    from schema.yaml_loader import duplicate_key_diagnostics

    repeating = {}
    for path in sorted((REPO_ROOT / "benchmarks").glob("*.md")):
        match = FRONT_MATTER.match(path.read_text(encoding="utf-8", errors="replace"))
        if match and duplicate_key_diagnostics(match.group(1)):
            repeating[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert repeating.items() <= FROZEN_DUPLICATE_PAGES.items()
    assert load_benchmarks(REPO_ROOT)


# --- merge keys and the card re-read -------------------------------------------------------------


#: A fact that inherits ``value`` through a merge and sets it again: an override, refused.
MERGED_CARD = """---
model_id: lab/alpha
display_name: Alpha
base: &base {facet: model.context_window, value: 128000, state: known}
facts:
  - <<: *base
    value: 262144
---
Synthetic fixture.
"""


def test_both_paths_refuse_a_key_inherited_through_a_merge_and_set_again(tmp_path):
    _repo(tmp_path, card=MERGED_CARD)
    for path in (collect_repo, load_models):
        with pytest.raises(LoadError, match=r"alpha\.md: duplicate_yaml_key: line 7, column 5"):
            path(tmp_path)


def test_a_merge_without_an_override_still_loads():
    from schema.yaml_loader import load_yaml_unique

    text = "base: &base {a: 1}\nmerged: {<<: *base, b: 2}\n"
    assert load_yaml_unique(text)["merged"] == {"a": 1, "b": 2}


@pytest.mark.parametrize("card", [CARD, MERGED_CARD], ids=["repeated", "merge-override"])
def test_the_graph_and_ranking_card_reader_refuses_a_repeated_key(tmp_path, card):
    """``pipeline.build`` and ``pipeline.ranking`` re-read cards with ``ModelCard``."""
    from schema.card import ModelCard

    path = tmp_path / "card.md"
    path.write_text(card)
    with pytest.raises(ValueError, match="DuplicateKeyError|duplicate_yaml_key"):
        ModelCard.from_yaml_file(path)
    with pytest.raises((ValueError, yaml.YAMLError), match="DuplicateKeyError|duplicate_yaml_key"):
        ModelCard.from_yaml_string(card)


def test_the_frozen_hash_is_of_the_text_parsed_not_a_second_read(tmp_path, monkeypatch):
    """The exemption binds what was parsed: pinned bytes on disk do not exempt other text,
    and the pinned text is exempt whatever the disk holds."""
    from pipeline.load import split_front_matter

    _repo(tmp_path, benchmark=ALIASES_PAGE)
    page = tmp_path / "benchmarks/bench-a.md"
    _pin(monkeypatch, page)
    with pytest.raises(LoadError, match="duplicate_yaml_key"):
        split_front_matter(ALIASES_PAGE.replace("name: Bench A", "name: Bench B"), path=page)
    page.write_text("not the pinned page\n")
    front, _ = split_front_matter(ALIASES_PAGE, path=page)
    assert front["aliases"] == ["Bench A"]


# --- the rule-15 readers, the trust audit and the PR validator -----------------------------------


def test_the_cited_change_readers_refuse_a_card_or_offering_that_repeats_a_key(tmp_path):
    from decision.cited_change import _front, cited_change_facts, cited_change_readings, lookup
    from schema.yaml_loader import DuplicateKeyError

    _repo(tmp_path, card=CARD, subscription=SUBSCRIPTION)
    with pytest.raises(LookupFailed, match="^DuplicateKeyError$"):
        lookup(MID, "model.context_window", tmp_path)
    with pytest.raises(LookupFailed, match="^DuplicateKeyError$"):
        lookup("host/subscription/pro", "offering.subscription.price", tmp_path)
    with pytest.raises(DuplicateKeyError):
        _front(tmp_path / f"models/{MID}.md")
    # The scans never read a repeated key as its last value: the file is not read at all.
    assert cited_change_facts(tmp_path) == [] and cited_change_readings(tmp_path) == []


def test_the_trust_audit_flags_a_log_row_that_repeats_a_key_and_never_counts_it(tmp_path):
    from scripts.data_trust.catalogue import load

    _repo(tmp_path, log=[_row("verified"), ESCAPED_OUTCOME])
    catalogue = load(tmp_path)
    assert [(f.id, f.rule) for f in catalogue.findings if f.field == "record"] == [
        ("verification/log.jsonl:2", "duplicate_json_key")]
    [(_, counted)] = catalogue.verifications.items()
    assert counted["outcome"] == "verified" and counted == json.loads(_row("verified"))


def test_the_pr_validator_still_treats_a_card_that_repeats_a_key_as_a_card(tmp_path):
    from scripts.validate_pr import is_model_card, validate_card

    _repo(tmp_path, card=CARD)
    path = str(tmp_path / f"models/{MID}.md")
    assert is_model_card(path)
    result = validate_card(path, compute_diff=False)
    assert result["status"] != "valid"
