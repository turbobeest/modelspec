"""Reproduce the two unrelated Pydantic 2.10 failures with the pre-fix model."""
import subprocess
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
source = subprocess.run(
    ['git', 'show', '4cda4a1:decision/model.py'], cwd=ROOT,
    check=True, capture_output=True, text=True,
).stdout
module = types.ModuleType('decision.model')
module.__file__ = str(ROOT / 'decision/model.py')
module.__package__ = 'decision'
sys.modules[module.__name__] = module
exec(compile(source, module.__file__, 'exec'), module.__dict__)
import pytest

raise SystemExit(pytest.main([
    '-q', '-p', 'no:cacheprovider',
    str(ROOT / 'tests/test_decision_model.py') +
    '::test_repository_subscription_offerings_validate_against_the_real_registry',
    str(ROOT / 'tests/test_decision_contract.py') + '::test_schema_file_is_generated_from_the_types',
]))
