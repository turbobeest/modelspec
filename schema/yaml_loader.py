"""Safe catalogue parsing with optional libyaml acceleration.

``load_yaml`` keeps the last repeated mapping key, the same construction the
catalogue used before duplicate-key diagnostics. The diagnostics are a separate
scan for the validator and the data-trust inventory.

``load_yaml_unique`` is the build's one reader for fact YAML (cards, offerings and
benchmark pages, on the snapshot and the site path): the same construction, but a
document that repeats a mapping key is refused (MODEL-554), since last-key-wins would
let a second key hide the first.
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


class DuplicateKeyError(yaml.YAMLError):
    """A document repeats a mapping key. The message has counts and a location only,
    never a key or a value."""

    def __init__(self, marks):
        self.count = len(marks)
        self.problem_mark = DuplicateKeyDiagnostic(marks[0]).problem_mark
        super().__init__(str(self))

    def diagnostic(self, *, line_offset=0):
        mark = self.problem_mark
        return (f"duplicate_yaml_key: line {mark.line + 1 + line_offset}, "
                f"column {mark.column + 1} ({self.count} repeated key(s))")

    def __str__(self):
        return self.diagnostic()


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


def _load_recording(text: str, loader_cls) -> tuple[Any, list]:
    """The document as ``load_yaml`` constructs it, and the marks of its repeated keys."""
    loader = loader_cls(text)
    try:
        data = loader.get_single_data()
        marks = list(getattr(loader, "_duplicate_marks", ()))
    finally:
        loader.dispose()
    return data, marks


def _scan(text: str, loader_cls) -> list[DuplicateKeyDiagnostic]:
    _, marks = _load_recording(text, loader_cls)
    return [DuplicateKeyDiagnostic(mark) for mark in marks]


def load_yaml_unique(text: str) -> Any:
    """``load_yaml``, refusing a document that repeats a mapping key at any depth, in any
    spelling that constructs an equal key (``a`` and ``"a"``, ``yes`` and ``1``, an alias),
    and a repeated merge directive. Raises ``DuplicateKeyError`` (a ``yaml.YAMLError``)."""
    loader_cls = _FastScanner if hasattr(yaml, "CSafeLoader") else _PythonScanner
    try:
        data, marks = _load_recording(text, loader_cls)
    except yaml.YAMLError:
        if loader_cls is _PythonScanner:
            raise
        data = marks = None
    if marks is None:
        # The Python parser preserves source snippets in existing diagnostics.
        data, marks = _load_recording(text, _PythonScanner)
    if marks:
        raise DuplicateKeyError(marks)
    return data


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
