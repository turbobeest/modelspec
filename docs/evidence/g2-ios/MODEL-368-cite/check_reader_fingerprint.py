"""Check the suffix migration without retaining or printing the source sentence.

The expected values below are the fingerprint of the original sentence suffix and
the FAQ template, taken once from the pre-migration reader. They are hashes and a
length only; the sentence itself is not stored here or anywhere in the repository.
"""

import ast
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]

# Fingerprint of the original sentence suffix (UTF-8, SHA-256) and of the FAQ template.
ORIGINAL_SUFFIX_LENGTH = 70
ORIGINAL_SUFFIX_SHA256 = "d08feeac87a47183bd3e1ac74fec9de98a36ebd257bc7e92e7dae433a467c1b0"
ORIGINAL_FAQ_STRUCTURAL_HASH = (
    "sha256:5bbb70cd6701e04065ea2497e4c0498b4bc2ec6b33b9d420f8f09c3713f2a0e2"
)

SCANNED = (
    "decision/perplexity_faq.py",
    "docs/design/perplexity-faq-reader.md",
    "tests/test_model_368_perplexity_faq.py",
)


def _contains_fingerprint(text: str) -> bool:
    """True if any window of the suffix length hashes to the suffix fingerprint."""
    width = ORIGINAL_SUFFIX_LENGTH
    return any(
        hashlib.sha256(text[i:i + width].encode()).hexdigest() == ORIGINAL_SUFFIX_SHA256
        for i in range(len(text) - width + 1)
    )


reader = ast.parse((ROOT / "decision/perplexity_faq.py").read_text())
constants = {target.id: ast.literal_eval(node.value)
             for node in reader.body if isinstance(node, ast.Assign)
             for target in node.targets if isinstance(target, ast.Name)
             and target.id in {"SUFFIX", "SUFFIX_LENGTH", "SUFFIX_SHA256",
                               "FAQ_STRUCTURAL_HASH"}}
assert "SUFFIX" not in constants, "reader stores the suffix literal"
assert constants["SUFFIX_LENGTH"] == ORIGINAL_SUFFIX_LENGTH
assert constants["SUFFIX_SHA256"] == ORIGINAL_SUFFIX_SHA256
assert constants["FAQ_STRUCTURAL_HASH"] == ORIGINAL_FAQ_STRUCTURAL_HASH
for path in SCANNED:
    assert not _contains_fingerprint((ROOT / path).read_text()), path
print("PASS: exact original sentence fingerprint preserved; quoted sentence absent")
