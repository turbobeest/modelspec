"""Check the suffix migration without retaining or printing the source sentence."""

import ast
import hashlib
import subprocess
from pathlib import Path

old = ast.parse(subprocess.check_output(
    ["git", "show", "fe37dad5:decision/perplexity_faq.py"], text=True,
))
suffix = next(ast.literal_eval(node.value) for node in old.body
              if isinstance(node, ast.Assign)
              and any(isinstance(target, ast.Name) and target.id == "SUFFIX"
                      for target in node.targets))
new = ast.parse(Path("decision/perplexity_faq.py").read_text())
constants = {target.id: ast.literal_eval(node.value)
             for node in new.body if isinstance(node, ast.Assign)
             for target in node.targets if isinstance(target, ast.Name)
             and target.id in {"SUFFIX_LENGTH", "SUFFIX_SHA256"}}
assert constants["SUFFIX_LENGTH"] == len(suffix)
assert constants["SUFFIX_SHA256"] == hashlib.sha256(suffix.encode()).hexdigest()
for path in ("decision/perplexity_faq.py", "docs/design/perplexity-faq-reader.md",
             "tests/test_model_368_perplexity_faq.py"):
    assert suffix not in Path(path).read_text(), path
print("PASS: exact original sentence fingerprint preserved; quoted sentence absent")
