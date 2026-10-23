"""Safe catalogue parsing with optional libyaml acceleration."""

from typing import Any

import yaml


def load_yaml(text: str) -> Any:
    try:
        return yaml.load(text, Loader=getattr(yaml, "CSafeLoader", yaml.SafeLoader))
    except yaml.YAMLError:
        pass
    # The Python parser preserves source snippets in existing diagnostics.
    return yaml.safe_load(text)
