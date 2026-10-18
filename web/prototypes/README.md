# PROTO-DECIDE

Three throwaway first-visit pages answer one question: how much should a person
need to understand before seeing a useful ModelSpec answer?

From this worktree:

```bash
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
cd /Users/terbeest/dev/worktrees/proto-decide-simple/web
npm ci
npm exec vite -- --config prototypes/vite.config.mjs --host 127.0.0.1 --port 5197 --strictPort
```

The offline snapshot takes about 35 seconds to compile at startup. Keep the
server running while viewing the pages. Ctrl-C also stops its Python engine.
`PROTO_DECIDE_PYTHON` can name another Python environment with the repository's
dependencies installed.

- A, answer first: http://127.0.0.1:5197/prototypes/proto-a.html
- B, guided: http://127.0.0.1:5197/prototypes/proto-b.html
- C, simplified current page: http://127.0.0.1:5197/prototypes/proto-c.html
- Current detailed page: http://127.0.0.1:5197/decide/

Use the A/B/C links in the header to switch variants, and Light mode to inspect
the alternate palette. Add `?theme=light` to open directly in light mode.

All requests stay on the local server. The existing vocabulary and recorded
decisions come from the browser fixtures. The fixture helper contains only
default-assistant and empty-board captures, so the prototype checks for an exact
request match before calling `decisionFixtureFor()`. Other choices use the real
offline engine over frozen repository data; they never receive the unrelated
empty-board fallback. No production Worker, provider API, or paid call is used.

The two data sources have different snapshots. Saved responses retain
`snap_483dd2fb6c5915b5`; locally calculated responses retain
`snap_e9c30eaacfa8f2f2`, built as of 2026-10-04 with the incomplete-data gate off,
as in the repository corpus. This is a UI comparison, not a current model
recommendation. Writing and long-document choices can honestly return no clear
pick. Every shown tie, model and cost is read from the response to that exact
spec; names are resolved through the specified vocabulary.

Budget options use existing category/tier templates. Self-hosting retains the
open-weights and commercial-use gates. The Cheapest control means the existing
budget template, which still weights quality; it does not promise the absolute
lowest price. Task costs use each template's task size, and self-hosting prices
are API alternatives, not a hardware running-cost estimate.

The full-evidence links use the existing `#s=` board encoding. CLI/API/MCP handoff
is explicitly keyed. These entries never replace `/decide/` or change production
configuration.

With Vite running, reproduce the mobile interaction checks and screenshots:

```bash
node prototypes/verify.mjs
node prototypes/handoff-audit.mjs
node prototypes/accessibility-audit.mjs
node prototypes/capture.mjs
```

Run the existing web suite and compile these entries separately:

```bash
npm test
npm exec tsc -- -p prototypes/tsconfig.json
npm exec vite -- build --config prototypes/vite.config.mjs
```

The measurement script writes to `.scratch/proto/` in the worktree and copies the
owner's original current-page images from the UX-panel worktree. It also saves
remeasured current-page images. Screenshots use 1440×900 and 390×844 viewports.
Visible-word counts exclude closed expanders, select options and hidden text;
they include visible content below the fold. Inputs include inputs, selects and
textareas. Native expander summaries are counted separately from buttons.

| Page | Desktop height | Mobile height | Buttons | Inputs | Desktop words | Mobile words |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Current | 9,697 | 15,363 | 122 | 92 | 3,093 | 3,089 |
| A | 900 | 844 | 11 | 0 | 187 | 156 |
| B, first step | 900 | 844 | 7 | 0 | 90 | 90 |
| C | 3,128 | 4,941 | 10 | 0 | 1,021 | 1,021 |

B's first step has no answer yet, so its word count is not an equal-value
comparison with A. C has three closed expander summaries in addition to its
buttons. A is the strongest starting point: its complete default shortlist and
next actions fit the requested desktop and mobile screens. B's limit step is a
useful later addition; C still exposes a long answer before refinement.
