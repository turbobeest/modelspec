"""List joining shared by bounded summaries and their fixed next steps."""

from collections.abc import Sequence


def join_names(names: Sequence[str], *, conjunction: str = "and", serial_comma: bool = True) -> str:
    if len(names) < 2:
        return "".join(names)
    separator = ", " if serial_comma and len(names) > 2 else " "
    return ", ".join(names[:-1]) + separator + conjunction + " " + names[-1]
