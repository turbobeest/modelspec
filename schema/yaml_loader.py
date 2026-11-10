"""Safe catalogue parsing with optional libyaml acceleration.

``load_yaml`` keeps the last repeated mapping key, the same construction the
catalogue used before duplicate-key diagnostics. The diagnostics are a separate
scan for the validator and the data-trust inventory.
"""

from typing import Any

import yaml

_MERGE_KEY = object()


class DuplicateKeyDiagnostic:
    """A repeated authored key, with location but no private text."""

    def __init__(self, mark):
        self.problem_mark = yaml.error.Mark(
            "<yaml>", mark.index, mark.line, mark.column, None, None
        )

    def diagnostic(self, *, line_offset=0):
        mark = self.problem_mark
        return f"duplicate_yaml_key: line {mark.line + 1 + line_offset}, column {mark.column + 1}"


class _RecordDuplicates:
    def flatten_mapping(self, node):
        if not hasattr(self, "_checked_mappings"):
            self._checked_mappings = set()
            self._duplicate_marks = []
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
                    self._duplicate_marks.append(key_node.start_mark)
        super().flatten_mapping(node)


class _PythonScanner(_RecordDuplicates, yaml.SafeLoader):
    pass


if hasattr(yaml, "CSafeLoader"):
    class _FastScanner(_RecordDuplicates, yaml.CSafeLoader):
        pass


def load_yaml(text: str) -> Any:
    try:
        return yaml.load(text, Loader=getattr(yaml, "CSafeLoader", yaml.SafeLoader))
    except yaml.YAMLError:
        pass
    # The Python parser preserves source snippets in existing diagnostics.
    return yaml.safe_load(text)


def _scan(text: str, loader_cls) -> list[DuplicateKeyDiagnostic]:
    loader = loader_cls(text)
    try:
        loader.get_single_data()
        marks = list(getattr(loader, "_duplicate_marks", ()))
    finally:
        loader.dispose()
    return [DuplicateKeyDiagnostic(mark) for mark in marks]


def duplicate_key_diagnostics(text: str) -> list[DuplicateKeyDiagnostic]:
    """Locate repeated mapping keys without changing the constructed document."""
    loaders = []
    if hasattr(yaml, "CSafeLoader"):
        loaders.append(_FastScanner)
    loaders.append(_PythonScanner)
    error = None
    for loader_cls in loaders:
        try:
            return _scan(text, loader_cls)
        except yaml.YAMLError as exc:
            error = exc
    if error is not None:
        raise error
    return []
