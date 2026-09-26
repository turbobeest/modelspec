"""Offline guards for the MODEL-112 research harness."""

from scripts.research import eval_jev_recommendations as research


def test_confidence_bands_are_code_owned_and_include_no_match() -> None:
    assert research.confidence_band(0.90) == "act"
    assert research.confidence_band(0.60) == "flag"
    assert research.confidence_band(0.59) == "null"
    assert research.confidence_band(0.99, no_match=True) == "null"


def test_label_sets_are_fixed_and_each_choice_has_no_match() -> None:
    cases = research.all_cases()
    assert len([case for case in cases if case.candidate == "task_routing"]) == 60
    assert {case.candidate for case in cases} == {
        "task_routing",
        "evidence_attribution",
        "second_key",
        "explanation_check",
    }
    for case in cases:
        for question in case.questions.values():
            if question["type"] == "choice":
                assert research.NO_MATCH in question["criteria"]


def test_scoring_requires_every_typed_answer() -> None:
    body = {
        "answers": {
            "pick": {
                "type": "choice",
                "choice": "supported",
                "probabilities": {"supported": 0.92, "no_match": 0.08},
                "confidence": 0.84,
            },
            "condition": {"type": "noul", "noul": 0.7},
        }
    }
    correct, confidence, no_match, values = research.score_answers(
        body, {"pick": "supported", "condition": True}
    )
    assert correct
    assert confidence == 0.7
    assert not no_match
    assert values == {"pick": "supported", "condition": True}
