# Saved price re-read page excerpts

These fixtures are trimmed `html-default` text projections of the supplied
2026-10-14 copies. No words or prices were added to the provider text.
The copy digests identify the complete original bytes.

| Fixture | Source | Original SHA-256 |
|---|---|---|
| `mistral-pro.txt` | `https://mistral.ai/pricing/` | `4c6fe583d9fdd4e348fbce195062047e0af5ef5f4386feafcf7db59157abc847` |
| `gemini-flash-lite.txt` | `https://ai.google.dev/gemini-api/docs/pricing` | `dfbd1d4d4ff9dfd7d740fd15b1269b84d4e9f04570457ce6454db0013ff05025` |
| `vertex-cited-table-38.txt` | `https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing` | `2fdbbdc8863bfa35130356e83a236ce9fffe0b2cd9d686be1604ffe212b33ea4` |
| `minimax-m-plan.txt` | `https://platform.minimax.io/docs/m-plan/intro` | `66eef9fec7a5652123bfd97649da8b591f936d40f32f39d4cc1318dfa8b0bfd5` |
| `minimax-faq.txt` | `https://platform.minimax.io/docs/m-plan/faq` | `111e69be5a5db7cff93a08658d762203fd66b00d772a9bd90f3a4e6c561e1d06` |
| `moonshot-current-plans.txt` | `https://www.kimi.com/en/help/membership/membership-pricing` | `e36f1b22c4c6ac45962dccda6076f1ed63c043d6dcd8d91853cf11f19380d6e8` |

The Mistral excerpt keeps the Pro card and its following Team card. The MiniMax
FAQ excerpt keeps its exact tier table, a sentence that identifies the supported
subscription tools, and the code example with the literal `<API Key>` placeholder.
The other excerpts prove that a missing model or legacy plan cannot borrow a
newer model or plan's price. Vertex table 38 is the table selected by the filed
`partner-anthropic-regional` citation, even though it now contains Codey.

Only the Mistral and MiniMax FAQ regressions failed before the reader changes.
The absent-subject tests are safety checks and passed before the changes.
