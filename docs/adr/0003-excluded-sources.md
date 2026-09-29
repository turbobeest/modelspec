---
status: accepted
---
# Sources whose terms forbid our use are excluded entirely

On 2026-09-24 we found that two publishers' terms forbid reusing their data in a commercial model-selection product, which is what ModelSpec is. We decided to remove every value sourced from them, every benchmark they own, and every fetcher that read them, rather than seek licences or keep the data behind a switch. The list of excluded sources lives in exactly one place, `tests/test_removed_sources.py`, which fails the build if any of them re-enters the repository or the export. Before adopting any new source for bulk use, read its terms. Leaderboard data is used only where its licence permits commercial redistribution, such as a CC BY dataset rather than a scraped web page. Git history still contains the removed data; rewriting it was deliberately not done.
