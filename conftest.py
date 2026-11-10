"""Repository-wide pytest collection rules."""

from scripts.pytest_shards import COLLECT_IGNORE

# This directory is an ignored, locally generated cache of third-party benchmark
# sources. Some downloaded files match pytest's test filename patterns, but they
# are not part of this repository's test suite and may require unavailable
# upstream packages such as ``bigbench`` just to import.
collect_ignore = list(COLLECT_IGNORE)
