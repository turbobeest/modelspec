import json

from qa.providers import redact


def test_bearer_redaction_keeps_a_serialized_report_valid_json():
    report = json.dumps({"final_answer": "send Authorization: Bearer sk-abcdefghijkl1234", "runs": 2})
    out = redact(report)
    assert "sk-abcdefghijkl1234" not in out
    assert json.loads(out) == {"final_answer": "send Authorization: [REDACTED]", "runs": 2}


def test_bearer_redaction_still_covers_a_plain_header():
    assert redact("Authorization: Bearer abc.def-ghi_123") == "Authorization: [REDACTED]"


def test_a_quoted_bearer_token_is_redacted_and_the_report_stays_valid():
    report = json.dumps({"final_answer": 'header: Bearer "abc.def-ghi_123"'})
    out = redact(report)
    assert "abc.def-ghi_123" not in out
    json.loads(out)
