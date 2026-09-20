"""MODEL-82: a model is attributed to the organisation that built it, or to nobody.

PR #92 proposed ``models/qwen/kimi-k3.md`` because Alibaba's models.dev page
lists Moonshot's Kimi K3 as a bare ``kimi-k3``. These tests pin the real shape
of that case and the rules around the TypeSafe judgment:

- a prefix naming an organisation settles the creator in code;
- the listing page's organisation never outvotes a prefix naming someone else;
- ambiguous evidence goes to the judgment, which only SELECTS among
  organisations code extracted, with ``cannot_establish`` always offered;
- only the confidence bands in scripts/attribution.yaml decide what is written,
  and a missing key or a failed call leaves the creator null.

No test here calls the TypeSafe API. The judge is a stub throughout.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx
import pytest
import yaml

from schema.card import ModelCard
from scripts import attribution as A  # noqa: N812
from scripts import seed_models_dev as seeder

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "daily-research.yml"
PAGE_ORGS = {pid: cfg["slug"] for pid, cfg in seeder.PROVIDER_MAP.items()}

KIMI = {"id": "kimi-k3", "name": "Kimi K3", "family": "kimi-k3"}


def kimi_on_alibaba_api(
    *, with_moonshot_page: bool = False, with_crosslisting: bool = True
) -> dict:
    """The models.dev shape of 2026-09-17, trimmed to what matters."""
    api = {
        # A seeded page. Alibaba serves Qwen and, since 2026, other labs' models.
        "alibaba": {
            "name": "Alibaba",
            "models": {
                "qwen-plus": {"id": "qwen-plus", "name": "Qwen Plus", "family": "qwen"},
                "kimi-k3": dict(KIMI),
            },
        },
        # Resellers. GreenPT lists it bare; TokenGo names the maker.
        "greenpt": {"name": "GreenPT", "models": {"kimi-k3": dict(KIMI)}},
    }
    if with_crosslisting:
        api["tokengo"] = {
            "name": "TokenGo",
            "models": {
                "moonshotai/kimi-k3": {
                    "id": "moonshotai/kimi-k3",
                    "name": "Kimi K3",
                    "family": "kimi-k3",
                }
            },
        }
        # A gateway whose prefixes name the HOST: the Alibaba route would read
        # as an Alibaba model if prefixes were trusted blindly.
        api["llmgateway-providers"] = {
            "name": "LLM Gateway",
            "models": {
                "alibaba/kimi-k3": {"id": "alibaba/kimi-k3", "name": "Kimi K3"},
                "tencent/kimi-k3": {"id": "tencent/kimi-k3", "name": "Kimi K3"},
                "moonshot/kimi-k3": {"id": "moonshot/kimi-k3", "name": "Kimi K3"},
            },
        }
    if with_moonshot_page:
        api["moonshotai"] = {"name": "Moonshot AI", "models": {"kimi-k3": dict(KIMI)}}
    return api


class NeverCalled:
    model = "jev-test"

    def evaluate(self, state, questions):  # pragma: no cover - failing is the point
        raise AssertionError("the judgment must not be called for this listing")


class StubJudge:
    """Answers like the API does. Records what it was asked."""

    model = "jev-test"

    def __init__(self, choice=None, confidence=0.99, reseller=0.1, probabilities=None):
        self.choice = choice
        self.confidence = confidence
        self.reseller = reseller
        self.probabilities = probabilities
        self.calls: list[tuple[dict, dict]] = []

    def evaluate(self, state, questions):
        self.calls.append((state, questions))
        options = list(questions[A.CREATOR_Q]["criteria"])
        choice = self.choice if self.choice is not None else options[0]
        probs = self.probabilities or {o: (1.0 if o == choice else 0.0) for o in options}
        return {
            "model": self.model,
            "answers": {
                A.CREATOR_Q: {
                    "type": "choice",
                    "choice": choice,
                    "probabilities": probs,
                    "confidence": self.confidence,
                },
                A.RESELLER_Q: {"type": "noul", "noul": self.reseller},
            },
            "usage": {"input_tokens": 800, "output_tokens": 40},
        }


@pytest.fixture(scope="module")
def registry() -> dict[str, A.Org]:
    return A.load_registry(REPO_ROOT / "models", seeder.PROVIDER_MAP)


def attributor(api, registry, judge, **kw) -> A.Attributor:
    return A.Attributor(api, registry, PAGE_ORGS, judge, A.load_config(), **kw)


# ── The Kimi-on-Alibaba regression ───────────────────────────────


def test_kimi_listed_bare_on_alibaba_is_moonshots_not_alibabas(registry):
    api = kimi_on_alibaba_api()
    result = attributor(api, registry, NeverCalled()).attribute(
        "alibaba", api["alibaba"]["models"]["kimi-k3"], "kimi-k3"
    )
    assert result.creator == "moonshot"
    assert result.status == A.DETERMINISTIC


def test_kimi_under_its_own_prefix_on_an_aggregator_page_is_moonshots(registry):
    api = kimi_on_alibaba_api()
    api["alibaba"]["models"]["moonshotai/kimi-k3"] = {"id": "moonshotai/kimi-k3", "name": "Kimi K3"}
    result = attributor(api, registry, NeverCalled()).attribute(
        "alibaba", api["alibaba"]["models"]["moonshotai/kimi-k3"], "moonshotai/kimi-k3"
    )
    assert (result.creator, result.status) == ("moonshot", A.DETERMINISTIC)


def test_the_listing_page_is_never_a_candidate_when_a_prefix_names_someone_else(registry):
    api = kimi_on_alibaba_api()
    ev = attributor(api, registry, None).evidence(
        "alibaba", api["alibaba"]["models"]["kimi-k3"], "kimi-k3"
    )
    assert ev.vendor == "qwen"
    assert "qwen" not in ev.candidates
    assert "moonshot" in ev.candidates


def test_a_gateway_whose_prefixes_name_hosts_is_not_read_as_authorship(registry):
    api = kimi_on_alibaba_api()
    at = attributor(api, registry, None)
    assert "llmgateway-providers" in at.index.routing_pages
    ev = at.evidence("alibaba", api["alibaba"]["models"]["kimi-k3"], "kimi-k3")
    assert set(ev.prefix_orgs) == {"moonshot"}
    assert all(pid != "llmgateway-providers" for pid, _ in ev.elsewhere)


def test_judge_cannot_hand_kimi_to_the_aggregator_even_if_it_tries(registry):
    """No prefix anywhere: the judgment decides, and the page's org is still refused."""
    api = kimi_on_alibaba_api(with_crosslisting=False)
    judge = StubJudge(choice="qwen", confidence=0.99, reseller=0.95)
    result = attributor(api, registry, judge).attribute(
        "alibaba", api["alibaba"]["models"]["kimi-k3"], "kimi-k3"
    )
    assert result.creator is None
    assert result.status == A.WITHHELD
    assert "reseller" in result.basis


def test_seeder_writes_kimi_under_moonshot_and_records_alibaba_as_availability(
    monkeypatch, tmp_path
):
    api = kimi_on_alibaba_api()
    monkeypatch.setattr(seeder, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(seeder, "load_known_identities", lambda *a, **k: {})
    monkeypatch.setattr(seeder, "fetch_models_dev", lambda: api)
    monkeypatch.setattr(seeder, "make_judge", lambda config: NeverCalled())
    monkeypatch.setattr(sys, "argv", ["seed_models_dev.py", "--new-only"])
    seeder.main()

    assert not (tmp_path / "models" / "qwen" / "kimi-k3.md").exists()
    card = ModelCard.from_yaml_file(tmp_path / "models" / "moonshot" / "kimi-k3.md")
    assert card.identity.model_id == "moonshot/kimi-k3"
    assert card.identity.provider == "moonshot"
    assert card.identity.provider_display == "Moonshot AI"
    assert card.licensing.origin_country == "CN"
    assert card.availability.qwen_alibaba.available is True
    assert card.availability.qwen_alibaba.model_id == "kimi-k3"
    # Qwen's own model on Qwen's own page is still Qwen's.
    qwen = ModelCard.from_yaml_file(tmp_path / "models" / "qwen" / "qwen-plus.md")
    assert qwen.identity.provider == "qwen"
    assert qwen.availability.qwen_alibaba.available is False


def test_seeder_cards_kimi_from_moonshots_own_page_when_it_lists_it(monkeypatch, tmp_path):
    api = kimi_on_alibaba_api(with_moonshot_page=True)
    monkeypatch.setattr(seeder, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(seeder, "load_known_identities", lambda *a, **k: {})
    monkeypatch.setattr(seeder, "fetch_models_dev", lambda: api)
    monkeypatch.setattr(seeder, "make_judge", lambda config: NeverCalled())
    monkeypatch.setattr(sys, "argv", ["seed_models_dev.py", "--new-only"])
    seeder.main()

    card = ModelCard.from_yaml_file(tmp_path / "models" / "moonshot" / "kimi-k3.md")
    assert card.sources.models_dev_url == "https://models.dev/moonshotai"
    assert not (tmp_path / "models" / "qwen" / "kimi-k3.md").exists()


def test_existing_card_under_the_creator_holds_the_listing(monkeypatch, tmp_path, capsys):
    """PR #92's day: moonshot/kimi-k3 already existed; nothing must be proposed."""
    api = kimi_on_alibaba_api(with_crosslisting=False)
    existing = tmp_path / "models" / "moonshot" / "kimi-k3.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("model_id: moonshot/kimi-k3\n", encoding="utf-8")
    monkeypatch.setattr(seeder, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(seeder, "load_known_identities", lambda *a, **k: {})
    monkeypatch.setattr(seeder, "fetch_models_dev", lambda: api)
    monkeypatch.setattr(sys, "argv", ["seed_models_dev.py", "--new-only", "--dry-run"])
    seeder.main()
    out = capsys.readouterr().out
    assert "kimi" not in "\n".join(ln for ln in out.splitlines() if ln.startswith("    NEW"))


# ── Failing closed ──────────────────────────────────────────────


def test_without_a_key_an_ambiguous_listing_gets_no_card_and_the_report_says_so(
    monkeypatch, tmp_path
):
    api = kimi_on_alibaba_api(with_crosslisting=False)
    report = tmp_path / "attribution.md"
    monkeypatch.setattr(seeder, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(seeder, "load_known_identities", lambda *a, **k: {})
    monkeypatch.setattr(seeder, "fetch_models_dev", lambda: api)
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    monkeypatch.setattr(
        sys, "argv", ["seed_models_dev.py", "--new-only", "--attribution-report", str(report)]
    )
    seeder.main()

    assert not list((tmp_path / "models").rglob("kimi-k3.md"))
    # Settled in code, so still carded: qwen-plus on Qwen's page, named Qwen.
    assert (tmp_path / "models" / "qwen" / "qwen-plus.md").is_file()
    text = report.read_text(encoding="utf-8")
    assert "TYPESAFE_API_KEY" in text and "was not available" in text
    assert "`alibaba/kimi-k3`" in text


def test_a_failed_call_leaves_the_creator_null(registry):
    class Broken:
        model = "jev-test"

        def evaluate(self, state, questions):
            raise A.JudgeUnavailable("TypeSafe request failed: HTTP 529")

    api = kimi_on_alibaba_api(with_crosslisting=False)
    result = attributor(api, registry, Broken()).attribute(
        "alibaba", api["alibaba"]["models"]["kimi-k3"], "kimi-k3"
    )
    assert (result.creator, result.status) == (None, A.UNAVAILABLE)


def test_malformed_answer_is_a_failed_judgment(registry):
    class Garbled:
        model = "jev-test"

        def evaluate(self, state, questions):
            return {"answers": {A.CREATOR_Q: {"choice": "moonshot"}}, "usage": {}}

    api = kimi_on_alibaba_api(with_crosslisting=False)
    result = attributor(api, registry, Garbled()).attribute(
        "alibaba", api["alibaba"]["models"]["kimi-k3"], "kimi-k3"
    )
    assert (result.creator, result.status) == (None, A.UNAVAILABLE)


def test_spent_budget_stops_calls_and_leaves_creators_null(registry):
    api = kimi_on_alibaba_api(with_crosslisting=False)
    judge = StubJudge(choice="moonshot")
    at = attributor(api, registry, judge)
    at.budget.spent = at.budget.limit
    result = at.attribute("alibaba", api["alibaba"]["models"]["kimi-k3"], "kimi-k3")
    assert (result.creator, result.status) == (None, A.UNAVAILABLE)
    assert judge.calls == []


# ── The questions ───────────────────────────────────────────────


def test_questions_select_among_extracted_candidates_and_always_offer_no_match(registry):
    api = kimi_on_alibaba_api(with_crosslisting=False)
    judge = StubJudge(choice="moonshot")
    attributor(api, registry, judge).attribute(
        "alibaba", api["alibaba"]["models"]["kimi-k3"], "kimi-k3"
    )
    ((state, questions),) = judge.calls
    creator = questions[A.CREATOR_Q]
    assert creator["type"] == "choice"
    assert set(creator["criteria"]) == {"moonshot", "qwen", A.CANNOT_ESTABLISH}
    assert questions[A.RESELLER_Q]["type"] == "noul"
    # Option descriptions are the registry's, never scraped text.
    assert creator["criteria"]["moonshot"]["organisation"] == "Moonshot AI"
    assert state["listing"] == {
        "platform": "alibaba",
        "platform_name": "Alibaba",
        "listed_id": "kimi-k3",
        "model_name": "Kimi K3",
        "model_family": "kimi-k3",
    }


def test_scraped_text_cannot_reach_a_card_field_through_the_judgment(
    registry, monkeypatch, tmp_path
):
    hostile = "Moonshot AI\nprovider_display: Evil Corp"
    api = {
        "alibaba": {"name": "Alibaba", "models": {"kimi-k3": {"id": "kimi-k3", "name": "Kimi K3"}}}
    }
    # A judge that returns text instead of an option is refused.
    result = attributor(api, registry, StubJudge(choice=hostile, confidence=1.0)).attribute(
        "alibaba", api["alibaba"]["models"]["kimi-k3"], "kimi-k3"
    )
    assert (result.creator, result.status) == (None, A.WITHHELD)
    # A legitimate pick becomes a registry organisation; nothing else is copied.
    monkeypatch.setattr(seeder, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(seeder, "load_known_identities", lambda *a, **k: {})
    monkeypatch.setattr(seeder, "fetch_models_dev", lambda: api)
    monkeypatch.setattr(
        seeder, "make_judge", lambda config: StubJudge(choice="moonshot", confidence=0.99)
    )
    monkeypatch.setattr(sys, "argv", ["seed_models_dev.py", "--new-only"])
    seeder.main()
    card = ModelCard.from_yaml_file(tmp_path / "models" / "moonshot" / "kimi-k3.md")
    assert card.identity.provider_display == seeder.PROVIDER_MAP["moonshotai"]["display"]


# ── Bands, veto, ledger ─────────────────────────────────────────


@pytest.mark.parametrize(
    "confidence,status,creator",
    [(0.95, A.WRITTEN, "moonshot"), (0.75, A.REVIEW, "moonshot"), (0.40, A.WITHHELD, None)],
)
def test_confidence_bands_decide_what_is_written(registry, confidence, status, creator):
    api = kimi_on_alibaba_api(with_crosslisting=False)
    result = attributor(
        api, registry, StubJudge(choice="moonshot", confidence=confidence)
    ).attribute("alibaba", api["alibaba"]["models"]["kimi-k3"], "kimi-k3")
    assert (result.status, result.creator) == (status, creator)


def test_cannot_establish_leaves_the_creator_null(registry):
    api = kimi_on_alibaba_api(with_crosslisting=False)
    result = attributor(
        api, registry, StubJudge(choice=A.CANNOT_ESTABLISH, confidence=0.99)
    ).attribute("alibaba", api["alibaba"]["models"]["kimi-k3"], "kimi-k3")
    assert (result.creator, result.status) == (None, A.WITHHELD)


def test_the_page_org_is_allowed_when_the_judgment_does_not_call_it_a_reseller(registry):
    api = {
        "cohere": {
            "name": "Cohere",
            "models": {"north-mini": {"id": "north-mini", "name": "North Mini"}},
        }
    }
    result = attributor(
        api, registry, StubJudge(choice="cohere", confidence=0.97, reseller=0.2)
    ).attribute("cohere", api["cohere"]["models"]["north-mini"], "north-mini")
    assert (result.creator, result.status) == ("cohere", A.WRITTEN)


def test_the_ledger_is_a_cache_and_thresholds_reapply_without_inference(registry, tmp_path):
    api = kimi_on_alibaba_api(with_crosslisting=False)
    raw = api["alibaba"]["models"]["kimi-k3"]
    ledger_path = tmp_path / "judgments.jsonl"
    judge = StubJudge(choice="moonshot", confidence=0.75)
    first = attributor(api, registry, judge, ledger=A.Ledger(ledger_path)).attribute(
        "alibaba", raw, "kimi-k3"
    )
    assert first.status == A.REVIEW and len(judge.calls) == 1

    row = json.loads(ledger_path.read_text(encoding="utf-8").splitlines()[0])
    assert row["answers"]["confidence"] == 0.75
    assert set(row["answers"]) == {"choice", "probabilities", "confidence", "reseller"}

    # A later run with a lower write bar re-reads the stored judgment.
    cfg = A.load_config()
    lowered = A.Config(
        **{**cfg.__dict__, "thresholds": A.Thresholds(write=0.7, review=0.5, reseller_veto=0.85)}
    )
    at = A.Attributor(
        api, registry, PAGE_ORGS, NeverCalled(), lowered, ledger=A.Ledger(ledger_path)
    )
    assert at.attribute("alibaba", raw, "kimi-k3").status == A.WRITTEN


def test_thresholds_live_in_config_and_are_ordered():
    th = A.load_config().thresholds
    assert 0 < th.review < th.write <= 1
    with pytest.raises(ValueError):
        A.Thresholds(write=0.5, review=0.9, reseller_veto=0.5)


def test_configured_thresholds_publish_no_wrong_creator_on_the_stored_evaluation():
    """The evaluation is kept, so a threshold change is checked without a call."""
    from scripts.eval_attribution import load_rows

    rows = load_rows(REPO_ROOT / "scripts" / "attribution_eval_2026-09-17.jsonl.gz")
    th = A.load_config().thresholds
    assert len(rows) > 3000
    wrong = 0
    for r in rows:
        ev = A.Evidence(
            A.Listing(r["platform"], "", r["listed_id"], "", ""),
            "",
            r["vendor"],
            None,
            None,
            [],
            {},
            [],
            set(),
            set(),
        )
        res = A.apply_policy(ev, r["answers"], r["candidates"], th)
        wrong += int(res.creator is not None and res.creator != r["expected"])
    assert wrong == 0


# ── The HTTP client, against a mock transport ──────────────────


def _judge_with(handler) -> A.TypeSafeJudge:
    cfg = A.load_config()
    return A.TypeSafeJudge(
        "test-key-not-real", cfg, client=httpx.Client(transport=httpx.MockTransport(handler))
    )


def test_http_request_matches_the_documented_shape():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers["authorization"]
        seen["body"] = json.loads(request.content)
        return httpx.Response(
            200, json={"model": "jev-1.13.0", "answers": {}, "usage": {"input_tokens": 1}}
        )

    _judge_with(handler).evaluate({"listing": {}}, {"q": {"type": "noul", "instructions": "?"}})
    assert seen["url"] == "https://api.typesafe.ai/v1/systemone"
    assert seen["auth"] == "Bearer test-key-not-real"
    assert seen["body"]["model"] == A.load_config().model
    assert set(seen["body"]) == {"state", "model", "questions"}


def test_http_retries_overload_then_succeeds(monkeypatch):
    monkeypatch.setattr(A.time, "sleep", lambda s: None)
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        if calls["n"] < 3:
            return httpx.Response(529)
        return httpx.Response(200, json={"answers": {}, "usage": {}})

    _judge_with(handler).evaluate({}, {})
    assert calls["n"] == 3


def test_http_auth_failure_is_unavailable_and_never_echoes_the_key(monkeypatch):
    monkeypatch.setattr(A.time, "sleep", lambda s: None)

    def handler(request):
        return httpx.Response(401, json={"detail": "bad key test-key-not-real"})

    with pytest.raises(A.JudgeUnavailable) as exc:
        _judge_with(handler).evaluate({}, {})
    assert "test-key-not-real" not in str(exc.value)
    assert "401" in str(exc.value)


def test_no_key_means_no_judge(monkeypatch):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    assert A.TypeSafeJudge.from_env(A.load_config()) is None
    monkeypatch.setenv("TYPESAFE_API_KEY", "   ")
    assert A.TypeSafeJudge.from_env(A.load_config()) is None


# ── Sweep and workflow ──────────────────────────────────────────


def test_sweep_reports_a_card_seeded_from_a_page_that_did_not_build_it(tmp_path, registry):
    models = tmp_path / "models"
    card = models / "qwen" / "kimi-k3.md"
    card.parent.mkdir(parents=True)
    card.write_text(
        "---\n"
        + yaml.safe_dump(
            {
                "model_id": "qwen/kimi-k3",
                "display_name": "Kimi K3",
                "provider": "qwen",
                "version": "kimi-k3",
                "sources": {"models_dev_url": "https://models.dev/alibaba"},
            }
        )
        + "---\n",
        encoding="utf-8",
    )
    fine = models / "qwen" / "qwen-plus.md"
    fine.write_text(
        "---\n"
        + yaml.safe_dump(
            {
                "model_id": "qwen/qwen-plus",
                "display_name": "Qwen Plus",
                "provider": "qwen",
                "version": "qwen-plus",
                "sources": {"models_dev_url": "https://models.dev/alibaba"},
            }
        )
        + "---\n",
        encoding="utf-8",
    )
    hits = A.sweep_corpus(models, kimi_on_alibaba_api(), registry, PAGE_ORGS)
    assert [(h.model_id, h.evidence_says) for h in hits] == [("qwen/kimi-k3", "moonshot")]
    assert card.read_text(encoding="utf-8").count("provider: qwen") == 1  # reported, not changed


def test_workflow_gives_the_key_only_to_the_write_step_and_reports_in_the_pr():
    steps = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))["jobs"]["research"]["steps"]
    with_key = [s for s in steps if "TYPESAFE_API_KEY" in json.dumps(s)]
    assert [s["name"] for s in with_key] == ["Write the new cards"]
    write = with_key[0]
    assert write["env"]["TYPESAFE_API_KEY"] == "${{ secrets.TYPESAFE_API_KEY }}"
    assert "--attribution-report attribution.md" in write["run"]

    names = [s.get("name") or "" for s in steps]
    report_i = next(i for i, s in enumerate(steps) if s.get("id") == "attribution")
    pr_i = next(
        i
        for i, s in enumerate(steps)
        if (s.get("uses") or "").startswith("peter-evans/create-pull-request")
    )
    assert names.index("Write the new cards") < report_i < pr_i
    assert "openssl rand" in steps[report_i]["run"]
    assert "steps.attribution.outputs.report" in steps[pr_i]["with"]["body"]


def test_page_org_named_only_as_a_base_model_is_still_not_a_candidate(registry):
    """DeepSeek's distil of a Qwen base, listed bare on Alibaba's page."""
    lid = "deepseek-r1-distill-qwen-32b"
    api = {
        "alibaba": {"name": "Alibaba", "models": {lid: {"id": lid, "name": "R1 Distill Qwen 32B"}}},
        "tokengo": {"name": "TokenGo", "models": {f"deepseek-ai/{lid}": {"id": f"deepseek-ai/{lid}"}}},
    }
    at = attributor(api, registry, None)
    ev = at.evidence("alibaba", api["alibaba"]["models"][lid], lid)
    assert ev.candidates == ["deepseek"]
    assert "qwen" in ev.named_orgs


# ── MODEL-101: the judge never writes its own vendor's card ─────


JEV = {"id": "jev-1.13.0", "name": "Jev 1.13", "family": "jev"}
#: A registry with the supplier in it, as it is once models/typesafe/ exists.
SUPPLIER_REGISTRY = {
    "typesafe": A.Org("typesafe", "TypeSafe AI", "US"),
    "moonshot": A.Org("moonshot", "Moonshot AI", "CN"),
}


def jev_on_a_reseller() -> dict:
    """A bare Jev listing on a page that is nobody's own: ambiguous evidence.

    The brand token nominates TypeSafe as a candidate, which is how the listing
    reaches the judgment at all. Nothing else in the evidence names a creator.
    """
    return {"greenpt": {"name": "GreenPT", "models": {"jev-1.13.0": dict(JEV)}}}


def jev_evidence() -> A.Evidence:
    api = jev_on_a_reseller()
    at = A.Attributor(api, SUPPLIER_REGISTRY, PAGE_ORGS, None, A.load_config())
    return at.evidence("greenpt", api["greenpt"]["models"]["jev-1.13.0"], "jev-1.13.0")


def test_the_supplier_is_a_candidate_at_all_so_the_guard_is_load_bearing():
    """Without this, the rule below would hold vacuously and prove nothing."""
    ev = jev_evidence()
    assert "typesafe" in ev.candidates
    assert A.decide_deterministically(ev, SUPPLIER_REGISTRY) is None  # would be judged


def test_an_ambiguous_supplier_listing_is_never_sent_to_the_judgment():
    """The rule itself: no TypeSafe field is ever written by a Jev judgment."""
    api = jev_on_a_reseller()
    at = A.Attributor(api, SUPPLIER_REGISTRY, PAGE_ORGS, NeverCalled(), A.load_config())
    result = at.attribute("greenpt", api["greenpt"]["models"]["jev-1.13.0"], "jev-1.13.0")
    assert result.creator is None
    assert result.writes_creator is False
    assert result.status == A.CONFLICTED
    assert "typesafe" in result.basis
    assert at.budget.spent == 0  # never asked, so never paid for


def test_a_stored_judgment_naming_the_supplier_is_never_applied():
    """The second refusal, which a cached or replayed answer must also meet.

    `decide` refuses to ask; this refuses to apply — a ledger row written
    before the slug was a supplier, or any caller reaching the policy directly.
    Removing either refusal fails a test: they are not one guard written twice.
    """
    answers = {
        "choice": "typesafe",
        "probabilities": {"typesafe": 1.0},
        "confidence": 1.0,
        "reseller": 0.0,
    }
    result = A.apply_policy(
        jev_evidence(), answers, ["typesafe", "moonshot"], A.load_config().thresholds
    )
    assert result.creator is None
    assert result.status == A.CONFLICTED


def test_the_judgment_can_still_answer_about_everyone_else(registry):
    """One organisation wide, not a general refusal to judge."""
    api = kimi_on_alibaba_api(with_crosslisting=False)
    result = attributor(api, registry, StubJudge(choice="moonshot", confidence=0.99)).attribute(
        "alibaba", api["alibaba"]["models"]["kimi-k3"], "kimi-k3"
    )
    assert (result.creator, result.status) == ("moonshot", A.WRITTEN)


def test_a_supplier_prefix_still_settles_deterministically():
    """`typesafe/...` read by code is not the model's opinion about its maker."""
    lid = "typesafe/jev-1.13.0"
    api = {"greenpt": {"name": "GreenPT", "models": {lid: {"id": lid, "name": "Jev 1.13"}}}}
    at = A.Attributor(api, SUPPLIER_REGISTRY, PAGE_ORGS, NeverCalled(), A.load_config())
    result = at.attribute("greenpt", api["greenpt"]["models"][lid], lid)
    assert (result.creator, result.status) == ("typesafe", A.DETERMINISTIC)


def test_the_conflict_is_reported_rather_than_swallowed():
    api = jev_on_a_reseller()
    at = A.Attributor(api, SUPPLIER_REGISTRY, PAGE_ORGS, NeverCalled(), A.load_config())
    at.attribute("greenpt", api["greenpt"]["models"]["jev-1.13.0"], "jev-1.13.0")
    report = A.render_report(at.results, judge_available=True, spent_tokens=0)
    assert "jev-1.13.0" in report
    assert "typesafe supplies the judgment" in report


def test_the_seeder_writes_no_supplier_card_from_a_judgment(monkeypatch, tmp_path):
    """End to end: a new TypeSafe listing appears, and no card is written."""
    lid = "jev-2.0"
    api = {
        "alibaba": {
            "name": "Alibaba",
            "models": {lid: {"id": lid, "name": "Jev 2.0", "family": "jev"}},
        }
    }
    held = tmp_path / "models" / "typesafe" / "jev-1-13.md"
    held.parent.mkdir(parents=True)
    held.write_text(
        "---\n"
        + yaml.safe_dump(
            {
                "model_id": "typesafe/jev-1-13",
                "display_name": "Jev 1.13",
                "provider": "typesafe",
                "provider_display": "TypeSafe AI",
            }
        )
        + "---\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(seeder, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(seeder, "load_known_identities", lambda *a, **k: {})
    monkeypatch.setattr(seeder, "fetch_models_dev", lambda: api)
    monkeypatch.setattr(seeder, "make_judge", lambda config: NeverCalled())
    monkeypatch.setattr(sys, "argv", ["seed_models_dev.py", "--new-only"])
    seeder.main()

    assert not (tmp_path / "models" / "typesafe" / "jev-2-0.md").exists()
    assert [p.name for p in sorted((tmp_path / "models" / "typesafe").glob("*.md"))] == [
        "jev-1-13.md"
    ]


def test_the_guarded_orgs_are_the_disclosed_orgs():
    """One table. The org the guard protects is the org the page discloses."""
    from schema.suppliers import SUPPLIERS, supplier_for

    assert A.SUPPLIER_SLUGS == frozenset(SUPPLIERS)
    assert supplier_for("typesafe") is not None
    assert supplier_for("moonshot") is None


def test_the_real_typesafe_card_is_under_the_rule():
    """The card the rule exists for, tied to the slug the guard protects."""
    card = ModelCard.from_yaml_file(REPO_ROOT / "models" / "typesafe" / "jev-1-13.md")
    assert card.identity.provider in A.SUPPLIER_SLUGS
