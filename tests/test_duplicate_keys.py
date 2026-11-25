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
    with pytest.raises(RepeatedKeyError, match=r"^line 2: .* \(2 line\(s\) repeat a key\)$"):
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
    with pytest.raises(RepeatedKeyError, match="^line 1: "):
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


def test_only_the_frozen_public_pages_warn_on_a_repeated_key(tmp_path, monkeypatch, caplog):
    """The public image predates the refusal and this repository may not change it: its known
    pages warn, as a count, and keep the last value. Nothing else is let through."""
    import pipeline.load as load

    _repo(tmp_path, benchmark=BENCHMARK)
    front = BENCHMARK.split("---\n")[1].rstrip("\n")
    monkeypatch.setattr(load, "FROZEN_DUPLICATE_PAGES", frozenset(
        {hashlib.sha256(front.encode()).hexdigest()}))
    with caplog.at_level("WARNING", logger="pipeline.load"):
        [page] = load_benchmarks(tmp_path)
    assert page.front["metric"]["direction"] == "lower_is_better"
    [record] = [r for r in caplog.records if "duplicate_yaml_key" in r.getMessage()]
    assert "line 6, column 3 (1 repeated key(s))" in record.getMessage()
    assert "lower_is_better" not in record.getMessage()
    # A card beside it is still refused.
    (tmp_path / f"models/{MID}.md").parent.mkdir(parents=True)
    (tmp_path / f"models/{MID}.md").write_text(CARD)
    with pytest.raises(LoadError, match="duplicate_yaml_key"):
        load_models(tmp_path)
    # So is the same page with any other text.
    (tmp_path / "benchmarks/bench-a.md").write_text(BENCHMARK.replace("Bench A", "Bench B"))
    with pytest.raises(LoadError, match="duplicate_yaml_key"):
        load_benchmarks(tmp_path)


def test_every_page_of_the_public_image_that_repeats_a_key_is_a_known_frozen_page():
    """The frozen image still builds; a new repeat could not be added without failing it."""
    from pipeline.load import FRONT_MATTER, FROZEN_DUPLICATE_PAGES, REPO_ROOT
    from schema.yaml_loader import duplicate_key_diagnostics

    repeating = set()
    for path in sorted((REPO_ROOT / "benchmarks").glob("*.md")):
        match = FRONT_MATTER.match(path.read_text(encoding="utf-8", errors="replace"))
        if match and duplicate_key_diagnostics(match.group(1)):
            repeating.add(hashlib.sha256(match.group(1).encode()).hexdigest())
    assert repeating <= FROZEN_DUPLICATE_PAGES
