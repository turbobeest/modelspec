"""Load the decision spec corpus and run it through the CLI and the Worker.

A case names the snapshot it runs against, the spec (a mapping, or raw text
for a spec that is not even YAML) and what it must answer: an HTTP status and,
where the snapshot makes it deterministic, the decision's ``status`` and answer
kind, or the error code. Cases on the ``repo`` snapshot run against the
repository's own premier lineup, so their status is left open where the data
decides it; cases whose answer the corpus asserts run on a synthetic snapshot.
"""

from __future__ import annotations

import functools
import importlib.util
import json
import os
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
CASES_PATH = Path(__file__).with_name("cases.yaml")
#: The HMAC key every corpus snapshot is signed with; never a real key.
KEY = b"model-203-corpus-key"
EXPLAIN_LEVELS = ("none", "summary", "full")
#: The board's five answers to "How will you use it?"; ``None`` is "Doesn't matter".
ACCESS_ANSWERS = (None, "chat_app", "coding_tool", "own_software", "own_hardware")
AS_OF = date(2026, 9, 25)


@dataclass(frozen=True)
class Expect:
    http: int
    code: str | None = None
    status: tuple[str, ...] | None = None
    answer: str | None = None
    #: Text the first refusal issue's reason must contain.
    reason: str | None = None


@dataclass(frozen=True)
class Case:
    id: str
    intent: str
    snapshot: str
    spec: Any
    expect: Expect
    covers: tuple[str, ...] = ()
    #: The ``X-ModelSpec-Snapshot`` header, for the Worker only. ``stale`` sends
    #: an ID that is not the loaded snapshot's.
    header: str | None = None
    #: Why ``modelspec decide`` does not answer this case as the Worker does.
    #: The parity test expects the divergence, and fails when it goes away.
    divergence: str | None = None
    #: Another case this one must answer byte for byte as.
    same_as: str | None = None
    #: POSTed to api.modelspec.dev after each deploy.
    live: bool = False
    generated: bool = field(default=False, compare=False)


def _expect(raw: Mapping[str, Any]) -> Expect:
    status = raw.get("status")
    if isinstance(status, str):
        status = (status,)
    return Expect(http=int(raw["http"]), code=raw.get("code"),
                  status=tuple(status) if status else None, answer=raw.get("answer"),
                  reason=raw.get("reason"))


def _hand_written() -> list[Case]:
    document = yaml.safe_load(CASES_PATH.read_text(encoding="utf-8"))
    return [
        Case(
            id=row["id"], intent=row["intent"], snapshot=row.get("snapshot", "repo"),
            spec=row["spec"], expect=_expect(row["expect"]),
            covers=tuple(row.get("covers", ())), header=row.get("header"),
            divergence=row.get("divergence"), same_as=row.get("same_as"),
            live=bool(row.get("live", False)),
        )
        for row in document["cases"]
    ]


def _template_cases() -> Iterator[Case]:
    from decision.templates import load_templates

    for template in load_templates():
        for level in EXPLAIN_LEVELS:
            yield Case(
                id=f"template-{template['id']}-{level}",
                intent=f"the {template['name']} template at explain {level}",
                snapshot="repo",
                spec=dict(template["spec"]) | {"explain": level},
                expect=Expect(http=200),
                covers=(f"template:{template['id']}:{level}",),
                live=level == "summary",
                generated=True,
            )


def board_facets() -> list[Any]:
    """The facets the board offers: ``build_vocabulary``'s filter over the registry."""
    from decision.registry import default

    return [
        facet for facet in default().facets()
        if not facet.id.startswith(("offering.subscription.", "offering.plan."))
        and facet.parameter is None and facet.addressable
    ]


def _kind(facet: Any) -> str:
    value_type = facet.value_type
    return value_type if isinstance(value_type, str) else value_type.kind


def _a_value(facet: Any) -> str | None:
    values = facet.preference_values or getattr(facet.value_type, "values", None)
    return values[0] if values else None


def _must(facet: Any) -> Any:
    kind = _kind(facet)
    if kind in ("int", "float", "number", "integer"):
        return f"{facet.id} >= 0"
    if kind == "date":
        return f"{facet.id} >= 2000-01-01"
    if kind in ("bool", "boolean"):
        return f"{facet.id} = true"
    value = _a_value(facet)
    if kind == "enum" and value is not None:
        return {"facet": facet.id, "op": "=", "value": value}
    return {"known": facet.id}


def _prefer(facet: Any) -> tuple[Any, Expect]:
    kind = _kind(facet)
    if kind in ("bool", "boolean"):
        return {facet.id: {"prefer": True, "weight": 1}}, Expect(http=200)
    if kind == "enum":
        value = _a_value(facet)
        if value is not None:
            return {facet.id: {"prefer": value, "weight": 1}}, Expect(http=200)
        return {facet.id: 1}, Expect(http=400, code="invalid_spec")
    if kind == "set":
        # A set has no order and no single preferred value: the board offers no
        # Prefer for it, and the engine refuses a weight on one.
        return {facet.id: 1}, Expect(http=400, code="invalid_spec")
    return {facet.id: 1}, Expect(http=200)


def _facet_cases() -> Iterator[Case]:
    for facet in board_facets():
        yield Case(
            id=f"facet-must-{facet.id}",
            intent=f"{facet.id} as a Must",
            snapshot="repo",
            spec={"spec_version": 1, "where": [_must(facet)],
                  "optimize": {"max": "software_engineering"}, "explain": "summary",
                  "limit": 5},
            expect=Expect(http=200),
            covers=(f"must:{facet.id}",),
            generated=True,
        )
        weights, expect = _prefer(facet)
        yield Case(
            id=f"facet-prefer-{facet.id}",
            intent=f"{facet.id} as a Prefer"
                   + ("" if expect.http == 200 else ", which has no order to prefer"),
            snapshot="repo",
            # Beside a capability weight, as the board sends it, and at full: a
            # value preference's explanation failed only there (MODEL-203).
            spec={"spec_version": 1,
                  "optimize": {"weights": weights | {"software_engineering": 1}},
                  "explain": "full", "limit": 5},
            expect=expect,
            covers=(f"prefer:{facet.id}",),
            generated=True,
        )


def _domain_cases() -> Iterator[Case]:
    from decision.registry import default

    for domain in default().domains():
        yield Case(
            id=f"domain-must-{domain.id}",
            intent=f"{domain.name} as a required capability",
            snapshot="repo",
            spec={"spec_version": 1, "capabilities": {domain.id: "required"},
                  "optimize": {"max": domain.id}, "explain": "summary", "limit": 5},
            expect=Expect(http=200),
            covers=(f"must:{domain.id}",),
            generated=True,
        )
        yield Case(
            id=f"domain-prefer-{domain.id}",
            intent=f"{domain.name} as a Prefer weight",
            snapshot="repo",
            spec={"spec_version": 1, "optimize": {"weights": {domain.id: 1}},
                  "explain": "summary", "limit": 5},
            expect=Expect(http=200),
            covers=(f"prefer:{domain.id}",),
            generated=True,
        )


def load_cases() -> list[Case]:
    """Every case: the hand-written ones, then the templates, facets and domains."""
    return [*_hand_written(), *_template_cases(), *_facet_cases(), *_domain_cases()]


# ── snapshots ──────────────────────────────────────────────────────────────

def _repo_snapshot():
    from decision.excluded import excluded_sources
    from decision.registry import default
    from decision.snapshot import build_snapshot, collect_repo, load_premier

    return build_snapshot(
        collect_repo(REPO), registry=default(),
        premier=load_premier(REPO / "premier" / "slice-1.yaml"),
        as_of=AS_OF, guard=excluded_sources(), gate=False,
    )


def _plans_snapshot(*, verified: bool):
    from decision.snapshot import build_snapshot
    from tests.plan_records import inputs

    return build_snapshot(inputs(max_coverage=verified), as_of=date(2026, 9, 29))


def _lineup_snapshot(*, tied: bool):
    from tests.snapshot_records import TIED_INTERVALS, build_lineup_snapshot

    return build_lineup_snapshot(TIED_INTERVALS if tied else None)


#: The snapshots a case can name. ``repo`` is the published premier lineup;
#: the others are the synthetic catalogues the page fixtures come from.
BUILDERS = {
    "repo": _repo_snapshot,
    "lineup": lambda: _lineup_snapshot(tied=False),
    "lineup-tied": lambda: _lineup_snapshot(tied=True),
    "plans": lambda: _plans_snapshot(verified=True),
    "plans-unverified": lambda: _plans_snapshot(verified=False),
}


def snapshot_bytes(name: str, cache: Path | None = None) -> bytes:
    """The signed snapshot ``name``, built once per ``cache`` directory."""
    path = cache / f"{name}.json.gz" if cache is not None else None
    if path is not None and path.is_file():
        return path.read_bytes()
    raw = BUILDERS[name]().to_bytes(key=KEY)
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    return raw


def load(raw: bytes):
    from decision.snapshot import load_snapshot_bytes

    return load_snapshot_bytes(raw, key=KEY, include_archive=True, source="corpus snapshot")


@functools.cache
def _benchmark_pages() -> dict[str, Any]:
    from pipeline.load import load_benchmarks

    return {b.benchmark_id: b.front for b in load_benchmarks(REPO)}


def _cards(snapshot) -> dict[str, Any]:
    """The lineup's cards only: ``models/<id>.md``. Parsing all ~1,400 takes a minute."""
    from pipeline.load import split_front_matter

    cards = {}
    for model_id in {snapshot.model_of(cid) for cid in snapshot.candidates()}:
        path = REPO / "models" / f"{model_id}.md"
        if path.is_file():
            front, _ = split_front_matter(path.read_text(encoding="utf-8"))
            if front.get("model_id") == model_id:
                cards[model_id] = front
    return cards


def vocabulary(snapshot) -> dict[str, Any]:
    """What the page loads beside ``snapshot``: ``pipeline.build``'s vocabulary."""
    from decision.vocabulary import build_vocabulary

    return build_vocabulary(snapshot, pages=_benchmark_pages(), cards=_cards(snapshot))


# ── surfaces ───────────────────────────────────────────────────────────────

#: Where ``worker_service`` loads ``decide_service.py`` from. ``python -m
#: tests.corpus decisions --bundle`` points it, and ``sys.path``, at the vendored
#: bundle, so the corpus runs on what the isolate holds (MODEL-203).
WORKER_SRC = REPO / "api" / "worker" / "src"


def worker_service():
    source = WORKER_SRC / "decide_service.py"
    loader = importlib.util.spec_from_file_location("modelspec_corpus_decide_service", source)
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    return module


#: A snapshot ID no corpus snapshot has: what a page built from an older vocabulary sends.
STALE_SNAPSHOT = "snap_" + "0" * 16


def header_for(case: Case, snapshot) -> str | None:
    return STALE_SNAPSHOT if case.header == "stale" else case.header


def payload(case: Case) -> Any:
    """What a client sends: the spec, or for raw text, the text YAML would parse to."""
    if isinstance(case.spec, str):
        from decision.contract import SpecError, load_yaml

        try:
            return load_yaml(case.spec)
        except SpecError:
            return case.spec
    return case.spec


def run_worker(case: Case, snapshot, service=None) -> tuple[int, bytes]:
    """The Worker's answer: HTTP status and the exact body bytes it sends.

    An exception is what the isolate turns into a 500 (Cloudflare 1101), so it
    is recorded as one and fails this case alone, not the whole corpus.
    """
    service = service or worker_service()
    try:
        status, body = service.decide(payload(case), snapshot,
                                      expected_snapshot=header_for(case, snapshot))
    except Exception as exc:  # noqa: BLE001 - the Worker would have thrown this
        return 500, json.dumps({"error": {"code": "worker_exception",
                                          "message": f"{type(exc).__name__}: {exc}"}}).encode()
    return status, service.serialise(body)


def run_cli(case: Case, snapshot_path: Path, workdir: Path) -> tuple[int, bytes, bytes]:
    """``modelspec decide SPEC --snapshot-file SNAPSHOT --json``: exit code, stdout, stderr."""
    from typer.testing import CliRunner

    from cli.modelspec import legacy as cli_mod

    spec_path = workdir / f"{case.id}.yaml"
    text = case.spec if isinstance(case.spec, str) else json.dumps(case.spec)
    spec_path.write_text(text, encoding="utf-8")
    result = CliRunner().invoke(
        cli_mod.app,
        ["decide", str(spec_path), "--snapshot-file", str(snapshot_path), "--json"],
        env={"MODELSPEC_SNAPSHOT_KEY": KEY.decode(), "MODELSPEC_CACHE": str(workdir / "cache")},
    )
    return result.exit_code, result.stdout_bytes, result.stderr_bytes


# ── what a case must answer ────────────────────────────────────────────────

def problems(case: Case, status: int, body: Mapping[str, Any]) -> list[str]:
    """Where the Worker's answer to ``case`` departs from what the case expects."""
    expect = case.expect
    found = []
    if status != expect.http:
        found.append(f"HTTP {status}, expected {expect.http}: {json.dumps(body)[:300]}")
        return found
    if expect.code is not None:
        error = body.get("error")
        code = error.get("code") if isinstance(error, Mapping) else error
        if code != expect.code:
            found.append(f"error code {code!r}, expected {expect.code!r}")
    if expect.reason is not None:
        issues = (body.get("error") or {}).get("issues") or [{}]
        if expect.reason not in str(issues[0].get("reason")):
            found.append(f"refused because {issues[0].get('reason')!r}, "
                         f"expected {expect.reason!r}")
    if expect.status is not None and body.get("status") not in expect.status:
        found.append(f"status {body.get('status')!r}, expected one of {expect.status}")
    if expect.answer is not None:
        answer = body.get("answer")
        kind = answer.get("kind") if isinstance(answer, Mapping) else "none"
        if kind != expect.answer:
            found.append(f"answer {kind!r}, expected {expect.answer!r}")
    return found


#: What the Worker's error code is at the CLI. A spec the engine rejects after
#: parsing is ``invalid_spec`` from the Worker and ``decision_failed`` from the
#: CLI (docs/decision-contract.md, "--check"); so is a pin to another snapshot,
#: which the Worker answers ``snapshot_not_loaded``.
CLI_CODES = {"invalid_spec": {"invalid_spec", "decision_failed"},
             "snapshot_not_loaded": {"decision_failed"}}


def cli_matches_worker(case: Case, worker: tuple[int, bytes],
                       cli: tuple[int, bytes, bytes]) -> list[str]:
    """The CLI's ``--json`` against the Worker's body: byte-identical when both answer."""
    status, body = worker
    code, stdout, stderr = cli
    if status == 200:
        if code != 0:
            return [f"the Worker answered but the CLI exited {code}: {stderr[:300]!r}"]
        if stdout != body:
            return [f"the CLI's --json differs from the Worker's body "
                    f"({len(stdout)} bytes against {len(body)})"]
        return []
    if code == 0:
        return [f"the Worker refused with HTTP {status} but the CLI answered"]
    worker_code = json.loads(body)["error"]
    worker_code = worker_code["code"] if isinstance(worker_code, Mapping) else worker_code
    try:
        cli_code = json.loads(stderr)["error"]["code"]
    except (ValueError, KeyError, TypeError):
        return [f"the CLI's error is not the structured --json error: {stderr[:300]!r}"]
    if cli_code not in CLI_CODES.get(worker_code, {worker_code}):
        return [f"the Worker refused {worker_code!r} but the CLI refused {cli_code!r}"]
    return []


def write_decisions(out: Path, cases: list[Case], cache: Path | None, *,
                    vocabularies: bool = True) -> dict[str, Any]:
    """One ``<case>.json`` per case (the Worker's status and body), and each
    snapshot's vocabulary."""
    out.mkdir(parents=True, exist_ok=True)
    service = worker_service()
    index: dict[str, Any] = {"cases": [], "vocabularies": {}}
    loaded = {}
    for case in cases:
        if case.snapshot not in loaded:
            loaded[case.snapshot] = load(snapshot_bytes(case.snapshot, cache))
            if vocabularies:
                name = f"vocabulary-{case.snapshot}.json"
                vocab = vocabulary(loaded[case.snapshot])
                (out / name).write_text(json.dumps(vocab, ensure_ascii=False) + "\n",
                                        encoding="utf-8")
                index["vocabularies"][case.snapshot] = name
        status, body = run_worker(case, loaded[case.snapshot], service)
        (out / f"{case.id}.json").write_bytes(body)
        index["cases"].append({"id": case.id, "intent": case.intent, "snapshot": case.snapshot,
                               "http": status, "file": f"{case.id}.json",
                               "generated": case.generated})
    (out / "index.json").write_text(json.dumps(index, indent=1) + "\n", encoding="utf-8")
    return index


def env_path(name: str) -> Path | None:
    value = os.environ.get(name)
    return Path(value) if value else None
