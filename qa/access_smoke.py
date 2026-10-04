"""The enforced machine boundary shared by offline-tested deployment smokes."""

PRICING_URL = "https://modelspec.dev/pricing"


def missing_key_problem(status: int, body) -> str | None:
    """Require the refusal and its procurement pointer, never just any 401."""
    if status != 401:
        return f"HTTP {status}, expected 401 missing_api_key"
    error = body.get("error") if isinstance(body, dict) else None
    if not isinstance(error, dict) or error.get("code") != "missing_api_key":
        return "expected error.code missing_api_key"
    if str(error.get("how_to_get_a_key", "")).rstrip("/") != PRICING_URL:
        return "missing the get-a-key pricing pointer"
    if PRICING_URL not in str(error.get("message", "")):
        return "the missing-key message does not name pricing"
    return None
