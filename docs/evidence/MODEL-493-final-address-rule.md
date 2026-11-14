# MODEL-493: a board read must end on the address it asked for

The weekly leaderboard refresh reads each declared live board and files the
rows under the declared address. Until this change it followed redirects and
never compared where it ended. A declared board address that began to answer
with a redirect to another board was read, and the other board filed under the
declared name.

## The rule

`_fetch` in `scripts/refresh_leaderboards.py` compares the final address of
every read with the address it asked for. If they differ it raises
`RedirectedRead`, which carries both. The rule is the default for every read,
including each second address derived from a first page (the Vending-Bench data
chunk, the MathArena index and tables, the Epoch archive, the MTEB backends,
the tau files), the Hugging Face dataset API read that resolves the Arena
revision, and every other script that imports `_fetch`.

A board whose read raises it is a failure in the refresh report, with the
reason `redirected: declared <address>, final <address>`. Nothing is filed for
that board: no observation, no row change, `observed_at` does not move, and
`not_published_since` is neither set nor removed. Other boards in the run are
unaffected. A cite-only address or hop is still refused first, by the existing
retention rule, and reported as before.

## The two declared exceptions

A read declares what final address it accepts by passing `accept_final` to
`_fetch`. Only two reads do; a structural test fails if a third appears.

1. **Arena parquet files** (`_fetch_arena`, `accept_arena_cdn`). The requested
   address must be a commit-pinned `resolve/<40 hex>/` path on
   `huggingface.co`, and the final address must be `https` on `hf.co` or a host
   ending in `.hf.co`. Hugging Face answers a pinned file with a redirect to
   its CDN; that resolves the file at that commit and is not a change of board.
   The suffix rule is narrow on purpose: `hf.co.example` and `evilhf.co` do
   not match. An unpinned address (a branch name) names a moving target and
   gets no exception.
2. **Scale SWE-bench Pro** (`_fetch_scale_pro`, `accept_scale_pro_final`). The
   declared address answers a permanent redirect to
   `https://labs.scale.com/leaderboard/swe_bench_pro`. On 2026-11-14 the page
   there names SWE-Bench Pro, the refresh projector yields 25 rows from it, and
   all 13 stored rows citing this board that matched a name on the page
   carried the page value. Exactly that address is accepted for exactly that
   request; any other final address fails.

Terminal-Bench is not an exception. Its 4.0 address redirects to the board that
now serves 4.1, so its read fails with `redirected` each week until a later
change re-declares the board.

## What a `redirected` failure means

The declared address no longer serves the board it was declared for, or serves
it from a new address. Read what the final address serves. If it is the same
board, declare the new address in the code beside the declaration. If it is a
new version of the board, add that version as its own declaration and leave the
old one failing or retire it. Do not add an exception to make the failure go
away.

The report, which names addresses, goes to a file and the private data pull
request, not to the public log.

## The limit

The rule sees an address, not a board. A board that changes version at an
unchanged address passes it. A check of the board's own name in the page is a
separate, later rule.
