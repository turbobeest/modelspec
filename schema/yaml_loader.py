"""Safe catalogue parsing with optional libyaml acceleration."""

from typing import Any

import yaml

_MERGE_KEY = object()


class DuplicateKeyError(yaml.YAMLError):
    """A repeated authored key, with location but no private text."""

    def __init__(self, mark):
        self.problem_mark = yaml.error.Mark("<yaml>", mark.index, mark.line, mark.column, None, None)
        super().__init__(self.diagnostic())

    def diagnostic(self, *, line_offset=0):
        mark = self.problem_mark
        return f"duplicate_yaml_key: line {mark.line + 1 + line_offset}, column {mark.column + 1}"


class _UniqueKeys:
    def flatten_mapping(self, node):
        if not hasattr(self, "_checked_mappings"):
            self._checked_mappings = set()
        if node not in self._checked_mappings:
            self._checked_mappings.add(node)
            keys = set()
            for key_node, _ in node.value:
                if key_node.tag == "tag:yaml.org,2002:merge":
                    key = _MERGE_KEY
                elif key_node.tag == "tag:yaml.org,2002:value":
                    key = "="
                else:
                    key = self.construct_object(key_node)
                try:
                    duplicate = key in keys
                    keys.add(key)
                except TypeError:
                    # Let SafeConstructor retain its unhashable-key diagnostic.
                    continue
                if duplicate:
                    raise DuplicateKeyError(key_node.start_mark)
        super().flatten_mapping(node)


class _PythonLoader(_UniqueKeys, yaml.SafeLoader):
    pass


if hasattr(yaml, "CSafeLoader"):
    class _FastLoader(_UniqueKeys, yaml.CSafeLoader):
        pass


def load_yaml(text: str) -> Any:
    try:
        loader = _FastLoader if hasattr(yaml, "CSafeLoader") else _PythonLoader
        return yaml.load(text, Loader=loader)
    except DuplicateKeyError:
        raise
    except yaml.YAMLError:
        pass
    # The Python parser preserves source snippets in existing diagnostics.
    return yaml.load(text, Loader=_PythonLoader)
