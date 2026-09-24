# Historical replay: each 2026 flagship at release + 7 days

Only evidence dated on or before the cutoff; Arena read from the newest snapshot on or
before it. `today` is the flagship's position among the same release-week pool under
today's evidence. v1 is `pipeline.ranking.rank_report` at the CLI floor, fed the
same dated, purged data.

## View: sourced

- **coding**: v2 placed 30/32 (25 ranked, 5 provisional); v1 ranked 0/32. For the 23 placed flagships with 30+ days of later evidence, median |release-week position − today's position| = 1.0, 18/23 within 3 places.
- **reasoning**: v2 placed 27/32 (1 ranked, 26 provisional); v1 ranked 0/32. For the 22 placed flagships with 30+ days of later evidence, median |release-week position − today's position| = 2.5, 15/22 within 3 places.
- **chat**: v2 placed 23/32 (23 ranked, 0 provisional); v1 ranked 0/32. For the 21 placed flagships with 30+ days of later evidence, median |release-week position − today's position| = 1.0, 17/21 within 3 places.

| flagship | cutoff | use case | v2 at +7d | v2 today | v1 at +7d |
|---|---|---|---|---|---|
| anthropic/claude-opus-4-6 | 2026-02-12 | coding | #1 of 146 (ranked) | #1 (ranked) | unranked (0% coverage) |
| anthropic/claude-opus-4-6 | 2026-02-12 | reasoning | #1 of 143 (provisional) | #1 (provisional) | unranked (0% coverage) |
| anthropic/claude-opus-4-6 | 2026-02-12 | chat | #1 of 143 (ranked) | #1 (ranked) | unranked (0% coverage) |
| anthropic/claude-sonnet-4-6 | 2026-02-24 | coding | #2 of 151 (ranked) | #2 (ranked) | unranked (0% coverage) |
| anthropic/claude-sonnet-4-6 | 2026-02-24 | reasoning | #3 of 147 (provisional) | #2 (provisional) | unranked (0% coverage) |
| anthropic/claude-sonnet-4-6 | 2026-02-24 | chat | #4 of 147 (ranked) | #3 (ranked) | unranked (0% coverage) |
| google/gemini-3-1-pro-preview | 2026-02-26 | coding | #5 of 151 (ranked) | #5 (ranked) | unranked (0% coverage) |
| google/gemini-3-1-pro-preview | 2026-02-26 | reasoning | #2 of 150 (provisional) | #4 (provisional) | unranked (0% coverage) |
| google/gemini-3-1-pro-preview | 2026-02-26 | chat | #2 of 150 (ranked) | #2 (ranked) | unranked (0% coverage) |
| openai/gpt-5-4 | 2026-03-12 | coding | #6 of 158 (provisional) | #6 (ranked) | unranked (0% coverage) |
| openai/gpt-5-4 | 2026-03-12 | reasoning | #3 of 154 (provisional) | #3 (provisional) | unranked (0% coverage) |
| openai/gpt-5-4 | 2026-03-12 | chat | #3 of 154 (ranked) | #3 (ranked) | unranked (0% coverage) |
| meta/muse-spark | 2026-04-15 | coding | #9 of 167 (provisional) | #5 (ranked) | unranked (0% coverage) |
| meta/muse-spark | 2026-04-15 | reasoning | #7 of 163 (provisional) | #5 (provisional) | unranked (0% coverage) |
| meta/muse-spark | 2026-04-15 | chat | #5 of 162 (ranked) | #4 (ranked) | unranked (0% coverage) |
| zhipu/glm-5-1 | 2026-04-15 | coding | #3 of 167 (ranked) | #7 (ranked) | unranked (0% coverage) |
| zhipu/glm-5-1 | 2026-04-15 | reasoning | #5 of 163 (provisional) | #9 (provisional) | unranked (16% coverage) |
| zhipu/glm-5-1 | 2026-04-15 | chat | #6 of 162 (ranked) | #8 (ranked) | unranked (0% coverage) |
| anthropic/claude-opus-4-7 | 2026-04-21 | coding | #2 of 168 (ranked) | #2 (ranked) | unranked (0% coverage) |
| anthropic/claude-opus-4-7 | 2026-04-21 | reasoning | #2 of 164 (provisional) | #3 (provisional) | unranked (0% coverage) |
| anthropic/claude-opus-4-7 | 2026-04-21 | chat | #2 of 163 (ranked) | #2 (ranked) | unranked (0% coverage) |
| moonshot/kimi-k2-6 | 2026-04-28 | coding | #7 of 170 (ranked) | #8 (ranked) | unranked (0% coverage) |
| moonshot/kimi-k2-6 | 2026-04-28 | reasoning | #10 of 166 (provisional) | #11 (provisional) | unranked (0% coverage) |
| moonshot/kimi-k2-6 | 2026-04-28 | chat | #10 of 165 (ranked) | #11 (ranked) | unranked (0% coverage) |
| openai/gpt-5-5 | 2026-04-30 | coding | insufficient | #2 (provisional) | unranked (0% coverage) |
| openai/gpt-5-5 | 2026-04-30 | reasoning | insufficient | #4 (provisional) | unranked (0% coverage) |
| openai/gpt-5-5 | 2026-04-30 | chat | insufficient | #3 (ranked) | unranked (0% coverage) |
| google/gemini-3-5-flash | 2026-05-26 | coding | #7 of 177 (ranked) | #12 (ranked) | unranked (0% coverage) |
| google/gemini-3-5-flash | 2026-05-26 | reasoning | #4 of 173 (provisional) | #10 (provisional) | unranked (0% coverage) |
| google/gemini-3-5-flash | 2026-05-26 | chat | #5 of 172 (ranked) | #9 (ranked) | unranked (0% coverage) |
| qwen/qwen3-7-max | 2026-05-28 | coding | insufficient | insufficient | unranked (0% coverage) |
| qwen/qwen3-7-max | 2026-05-28 | reasoning | insufficient | insufficient | unranked (0% coverage) |
| qwen/qwen3-7-max | 2026-05-28 | chat | insufficient | insufficient | unranked (0% coverage) |
| anthropic/claude-opus-4-8 | 2026-06-04 | coding | #1 of 178 (provisional) | #2 (ranked) | unranked (16% coverage) |
| anthropic/claude-opus-4-8 | 2026-06-04 | reasoning | #1 of 174 (provisional) | #4 (provisional) | unranked (16% coverage) |
| anthropic/claude-opus-4-8 | 2026-06-04 | chat | insufficient | #3 (ranked) | unranked (0% coverage) |
| minimax/minimax-m3 | 2026-06-08 | coding | #11 of 180 (ranked) | #17 (ranked) | unranked (0% coverage) |
| minimax/minimax-m3 | 2026-06-08 | reasoning | #16 of 176 (provisional) | #29 (provisional) | unranked (0% coverage) |
| minimax/minimax-m3 | 2026-06-08 | chat | #19 of 175 (ranked) | #28 (ranked) | unranked (0% coverage) |
| anthropic/claude-fable-5 | 2026-06-14 | coding | #1 of 181 (ranked) | #2 (ranked) | unranked (0% coverage) |
| anthropic/claude-fable-5 | 2026-06-14 | reasoning | #2 of 177 (provisional) | #2 (provisional) | unranked (0% coverage) |
| anthropic/claude-fable-5 | 2026-06-14 | chat | #1 of 176 (ranked) | #1 (ranked) | unranked (0% coverage) |
| zhipu/glm-5-2 | 2026-06-20 | coding | #10 of 182 (provisional) | #4 (ranked) | unranked (0% coverage) |
| zhipu/glm-5-2 | 2026-06-20 | reasoning | #13 of 178 (provisional) | #7 (provisional) | unranked (0% coverage) |
| zhipu/glm-5-2 | 2026-06-20 | chat | #13 of 177 (ranked) | #10 (ranked) | unranked (0% coverage) |
| anthropic/claude-sonnet-5 | 2026-07-06 | coding | #8 of 185 (ranked) | #7 (ranked) | unranked (16% coverage) |
| anthropic/claude-sonnet-5 | 2026-07-06 | reasoning | #12 of 181 (provisional) | #8 (provisional) | unranked (0% coverage) |
| anthropic/claude-sonnet-5 | 2026-07-06 | chat | #15 of 179 (ranked) | #12 (ranked) | unranked (0% coverage) |
| xai/grok-4-5 | 2026-07-15 | coding | #9 of 187 (ranked) | #10 (ranked) | unranked (0% coverage) |
| xai/grok-4-5 | 2026-07-15 | reasoning | #10 of 185 (provisional) | #13 (provisional) | unranked (0% coverage) |
| xai/grok-4-5 | 2026-07-15 | chat | #13 of 181 (ranked) | #14 (ranked) | unranked (0% coverage) |
| openai/gpt-5-6-sol | 2026-07-16 | coding | #7 of 189 (provisional) | #4 (provisional) | unranked (0% coverage) |
| openai/gpt-5-6-sol | 2026-07-16 | reasoning | #7 of 187 (provisional) | #4 (provisional) | unranked (16% coverage) |
| openai/gpt-5-6-sol | 2026-07-16 | chat | #6 of 183 (ranked) | #4 (ranked) | unranked (0% coverage) |
| moonshot/kimi-k3 | 2026-07-23 | coding | #1 of 189 (ranked) | #3 (ranked) | unranked (0% coverage) |
| moonshot/kimi-k3 | 2026-07-23 | reasoning | #3 of 187 (provisional) | #6 (provisional) | unranked (0% coverage) |
| moonshot/kimi-k3 | 2026-07-23 | chat | #4 of 183 (ranked) | #5 (ranked) | unranked (0% coverage) |
| anthropic/claude-opus-5 | 2026-07-31 | coding | #1 of 194 (ranked) | #1 (ranked) | unranked (16% coverage) |
| anthropic/claude-opus-5 | 2026-07-31 | reasoning | #3 of 192 (provisional) | #3 (provisional) | unranked (0% coverage) |
| anthropic/claude-opus-5 | 2026-07-31 | chat | #3 of 188 (ranked) | #4 (ranked) | unranked (0% coverage) |
| qwen/qwen3-8-max | 2026-08-10 | coding | #5 of 197 (ranked) | #5 (ranked) | unranked (0% coverage) |
| qwen/qwen3-8-max | 2026-08-10 | reasoning | #5 of 193 (provisional) | #9 (provisional) | unranked (0% coverage) |
| qwen/qwen3-8-max | 2026-08-10 | chat | #4 of 191 (ranked) | #8 (ranked) | unranked (0% coverage) |
| deepseek/deepseek-v4-pro | 2026-08-19 | coding | #34 of 202 (ranked) | #32 (ranked) | unranked (16% coverage) |
| deepseek/deepseek-v4-pro | 2026-08-19 | reasoning | #30 of 197 (provisional) | #32 (provisional) | unranked (28% coverage) |
| deepseek/deepseek-v4-pro | 2026-08-19 | chat | #29 of 195 (ranked) | #28 (ranked) | unranked (10% coverage) |
| xai/grok-4-6 | 2026-08-19 | coding | #7 of 202 (ranked) | #10 (ranked) | unranked (0% coverage) |
| xai/grok-4-6 | 2026-08-19 | reasoning | #11 of 197 (provisional) | #21 (provisional) | unranked (0% coverage) |
| xai/grok-4-6 | 2026-08-19 | chat | #17 of 195 (ranked) | #26 (ranked) | unranked (0% coverage) |
| google/gemini-3-7-flash | 2026-08-20 | coding | #11 of 202 (ranked) | #14 (ranked) | unranked (0% coverage) |
| google/gemini-3-7-flash | 2026-08-20 | reasoning | insufficient | #12 (provisional) | unranked (0% coverage) |
| google/gemini-3-7-flash | 2026-08-20 | chat | insufficient | #8 (ranked) | unranked (0% coverage) |
| zhipu/glm-5-3 | 2026-08-21 | coding | #9 of 205 (ranked) | #7 (ranked) | unranked (0% coverage) |
| zhipu/glm-5-3 | 2026-08-21 | reasoning | #10 of 201 (provisional) | #10 (provisional) | unranked (0% coverage) |
| zhipu/glm-5-3 | 2026-08-21 | chat | #8 of 199 (ranked) | #10 (ranked) | unranked (0% coverage) |
| anthropic/claude-fable-5-1 | 2026-09-08 | coding | #3 of 214 (ranked) | #3 (ranked) | unranked (0% coverage) |
| anthropic/claude-fable-5-1 | 2026-09-08 | reasoning | #2 of 208 (provisional) | #4 (provisional) | unranked (0% coverage) |
| anthropic/claude-fable-5-1 | 2026-09-08 | chat | #2 of 205 (ranked) | #3 (ranked) | unranked (0% coverage) |
| google/gemini-3-8-flash | 2026-09-09 | coding | #16 of 214 (ranked) | #11 (ranked) | unranked (0% coverage) |
| google/gemini-3-8-flash | 2026-09-09 | reasoning | #5 of 208 (ranked) | #3 (ranked) | unranked (16% coverage) |
| google/gemini-3-8-flash | 2026-09-09 | chat | #5 of 205 (ranked) | #5 (ranked) | unranked (0% coverage) |
| openai/gpt-6-astra | 2026-09-11 | coding | #2 of 215 (ranked) | #2 (ranked) | unranked (0% coverage) |
| openai/gpt-6-astra | 2026-09-11 | reasoning | #1 of 209 (provisional) | #8 (provisional) | unranked (16% coverage) |
| openai/gpt-6-astra | 2026-09-11 | chat | insufficient | #11 (ranked) | unranked (0% coverage) |
| deepseek/deepseek-flash | 2026-09-17 | coding | #10 of 215 (ranked) | #10 (ranked) | unranked (0% coverage) |
| deepseek/deepseek-flash | 2026-09-17 | reasoning | #20 of 209 (provisional) | #21 (provisional) | unranked (16% coverage) |
| deepseek/deepseek-flash | 2026-09-17 | chat | insufficient | insufficient | unranked (0% coverage) |
| xai/grok-4-7 | 2026-09-24 | coding | #12 of 218 (ranked) | #12 (ranked) | unranked (0% coverage) |
| xai/grok-4-7 | 2026-09-24 | reasoning | insufficient | insufficient | unranked (0% coverage) |
| xai/grok-4-7 | 2026-09-24 | chat | insufficient | insufficient | unranked (0% coverage) |
| anthropic/claude-opus-5-5 | 2026-09-24 | coding | #1 of 218 (ranked) | #1 (ranked) | unranked (0% coverage) |
| anthropic/claude-opus-5-5 | 2026-09-24 | reasoning | #1 of 210 (provisional) | #1 (provisional) | unranked (0% coverage) |
| anthropic/claude-opus-5-5 | 2026-09-24 | chat | insufficient | insufficient | unranked (0% coverage) |
| openai/gpt-6-sol | 2026-09-24 | coding | #7 of 218 (ranked) | #7 (ranked) | unranked (0% coverage) |
| openai/gpt-6-sol | 2026-09-24 | reasoning | insufficient | insufficient | unranked (0% coverage) |
| openai/gpt-6-sol | 2026-09-24 | chat | insufficient | insufficient | unranked (0% coverage) |

## View: flat

- **coding**: v2 placed 30/32 (25 ranked, 5 provisional); v1 ranked 0/32. For the 23 placed flagships with 30+ days of later evidence, median |release-week position − today's position| = 4.0, 11/23 within 3 places.
- **reasoning**: v2 placed 27/32 (1 ranked, 26 provisional); v1 ranked 0/32. For the 22 placed flagships with 30+ days of later evidence, median |release-week position − today's position| = 2.0, 13/22 within 3 places.
- **chat**: v2 placed 23/32 (23 ranked, 0 provisional); v1 ranked 0/32. For the 21 placed flagships with 30+ days of later evidence, median |release-week position − today's position| = 1.0, 17/21 within 3 places.

| flagship | cutoff | use case | v2 at +7d | v2 today | v1 at +7d |
|---|---|---|---|---|---|
| anthropic/claude-opus-4-6 | 2026-02-12 | coding | #1 of 146 (ranked) | #1 (ranked) | unranked (0% coverage) |
| anthropic/claude-opus-4-6 | 2026-02-12 | reasoning | #1 of 238 (provisional) | #1 (provisional) | unranked (0% coverage) |
| anthropic/claude-opus-4-6 | 2026-02-12 | chat | #1 of 231 (ranked) | #1 (ranked) | unranked (0% coverage) |
| anthropic/claude-sonnet-4-6 | 2026-02-24 | coding | #2 of 151 (ranked) | #5 (ranked) | unranked (0% coverage) |
| anthropic/claude-sonnet-4-6 | 2026-02-24 | reasoning | #3 of 242 (provisional) | #16 (provisional) | unranked (0% coverage) |
| anthropic/claude-sonnet-4-6 | 2026-02-24 | chat | #4 of 235 (ranked) | #4 (ranked) | unranked (0% coverage) |
| google/gemini-3-1-pro-preview | 2026-02-26 | coding | #5 of 151 (ranked) | #12 (ranked) | unranked (0% coverage) |
| google/gemini-3-1-pro-preview | 2026-02-26 | reasoning | #2 of 245 (provisional) | #2 (provisional) | unranked (0% coverage) |
| google/gemini-3-1-pro-preview | 2026-02-26 | chat | #2 of 238 (ranked) | #2 (ranked) | unranked (0% coverage) |
| openai/gpt-5-4 | 2026-03-12 | coding | #6 of 158 (provisional) | #10 (ranked) | unranked (0% coverage) |
| openai/gpt-5-4 | 2026-03-12 | reasoning | #3 of 249 (provisional) | #2 (provisional) | unranked (0% coverage) |
| openai/gpt-5-4 | 2026-03-12 | chat | #4 of 242 (ranked) | #4 (ranked) | unranked (0% coverage) |
| meta/muse-spark | 2026-04-15 | coding | #11 of 197 (provisional) | #7 (ranked) | unranked (0% coverage) |
| meta/muse-spark | 2026-04-15 | reasoning | #3 of 297 (provisional) | #4 (provisional) | unranked (0% coverage) |
| meta/muse-spark | 2026-04-15 | chat | #5 of 287 (ranked) | #5 (ranked) | unranked (0% coverage) |
| zhipu/glm-5-1 | 2026-04-15 | coding | #3 of 197 (ranked) | #10 (ranked) | unranked (20% coverage) |
| zhipu/glm-5-1 | 2026-04-15 | reasoning | #17 of 297 (provisional) | #13 (provisional) | unranked (40% coverage) |
| zhipu/glm-5-1 | 2026-04-15 | chat | #7 of 287 (ranked) | #8 (ranked) | unranked (40% coverage) |
| anthropic/claude-opus-4-7 | 2026-04-21 | coding | #2 of 198 (ranked) | #2 (ranked) | unranked (0% coverage) |
| anthropic/claude-opus-4-7 | 2026-04-21 | reasoning | #3 of 298 (provisional) | #3 (provisional) | unranked (0% coverage) |
| anthropic/claude-opus-4-7 | 2026-04-21 | chat | #2 of 288 (ranked) | #2 (ranked) | unranked (0% coverage) |
| moonshot/kimi-k2-6 | 2026-04-28 | coding | #7 of 201 (ranked) | #11 (ranked) | unranked (0% coverage) |
| moonshot/kimi-k2-6 | 2026-04-28 | reasoning | #9 of 300 (provisional) | #13 (provisional) | unranked (0% coverage) |
| moonshot/kimi-k2-6 | 2026-04-28 | chat | #11 of 290 (ranked) | #15 (ranked) | unranked (0% coverage) |
| openai/gpt-5-5 | 2026-04-30 | coding | insufficient | #2 (provisional) | unranked (0% coverage) |
| openai/gpt-5-5 | 2026-04-30 | reasoning | insufficient | #4 (provisional) | unranked (0% coverage) |
| openai/gpt-5-5 | 2026-04-30 | chat | insufficient | #5 (ranked) | unranked (0% coverage) |
| google/gemini-3-5-flash | 2026-05-26 | coding | #6 of 210 (ranked) | #16 (ranked) | unranked (0% coverage) |
| google/gemini-3-5-flash | 2026-05-26 | reasoning | #7 of 307 (provisional) | #11 (provisional) | unranked (0% coverage) |
| google/gemini-3-5-flash | 2026-05-26 | chat | #7 of 297 (ranked) | #9 (ranked) | unranked (0% coverage) |
| qwen/qwen3-7-max | 2026-05-28 | coding | insufficient | insufficient | unranked (0% coverage) |
| qwen/qwen3-7-max | 2026-05-28 | reasoning | insufficient | insufficient | unranked (0% coverage) |
| qwen/qwen3-7-max | 2026-05-28 | chat | insufficient | insufficient | unranked (0% coverage) |
| anthropic/claude-opus-4-8 | 2026-06-04 | coding | #6 of 211 (provisional) | #2 (ranked) | unranked (16% coverage) |
| anthropic/claude-opus-4-8 | 2026-06-04 | reasoning | #8 of 308 (provisional) | #6 (provisional) | unranked (16% coverage) |
| anthropic/claude-opus-4-8 | 2026-06-04 | chat | insufficient | #4 (ranked) | unranked (0% coverage) |
| minimax/minimax-m3 | 2026-06-08 | coding | #12 of 213 (ranked) | #25 (ranked) | unranked (0% coverage) |
| minimax/minimax-m3 | 2026-06-08 | reasoning | #17 of 310 (provisional) | #36 (provisional) | unranked (0% coverage) |
| minimax/minimax-m3 | 2026-06-08 | chat | #24 of 300 (ranked) | #35 (ranked) | unranked (0% coverage) |
| anthropic/claude-fable-5 | 2026-06-14 | coding | #1 of 214 (ranked) | #2 (ranked) | unranked (0% coverage) |
| anthropic/claude-fable-5 | 2026-06-14 | reasoning | #1 of 311 (provisional) | #1 (provisional) | unranked (0% coverage) |
| anthropic/claude-fable-5 | 2026-06-14 | chat | #1 of 301 (ranked) | #1 (ranked) | unranked (0% coverage) |
| zhipu/glm-5-2 | 2026-06-20 | coding | #11 of 215 (provisional) | #4 (ranked) | unranked (0% coverage) |
| zhipu/glm-5-2 | 2026-06-20 | reasoning | #14 of 312 (provisional) | #11 (provisional) | unranked (0% coverage) |
| zhipu/glm-5-2 | 2026-06-20 | chat | #14 of 302 (ranked) | #11 (ranked) | unranked (0% coverage) |
| anthropic/claude-sonnet-5 | 2026-07-06 | coding | #8 of 218 (ranked) | #7 (ranked) | unranked (16% coverage) |
| anthropic/claude-sonnet-5 | 2026-07-06 | reasoning | #13 of 315 (provisional) | #11 (provisional) | unranked (0% coverage) |
| anthropic/claude-sonnet-5 | 2026-07-06 | chat | #15 of 304 (ranked) | #12 (ranked) | unranked (0% coverage) |
| xai/grok-4-5 | 2026-07-15 | coding | #9 of 220 (ranked) | #11 (ranked) | unranked (0% coverage) |
| xai/grok-4-5 | 2026-07-15 | reasoning | #11 of 319 (provisional) | #15 (provisional) | unranked (0% coverage) |
| xai/grok-4-5 | 2026-07-15 | chat | #13 of 306 (ranked) | #15 (ranked) | unranked (0% coverage) |
| openai/gpt-5-6-sol | 2026-07-16 | coding | #8 of 222 (provisional) | #4 (provisional) | unranked (0% coverage) |
| openai/gpt-5-6-sol | 2026-07-16 | reasoning | #8 of 321 (provisional) | #4 (provisional) | unranked (16% coverage) |
| openai/gpt-5-6-sol | 2026-07-16 | chat | #6 of 308 (ranked) | #4 (ranked) | unranked (0% coverage) |
| moonshot/kimi-k3 | 2026-07-23 | coding | #1 of 222 (ranked) | #3 (ranked) | unranked (0% coverage) |
| moonshot/kimi-k3 | 2026-07-23 | reasoning | #4 of 321 (provisional) | #6 (provisional) | unranked (0% coverage) |
| moonshot/kimi-k3 | 2026-07-23 | chat | #4 of 308 (ranked) | #5 (ranked) | unranked (0% coverage) |
| anthropic/claude-opus-5 | 2026-07-31 | coding | #1 of 227 (ranked) | #1 (ranked) | unranked (16% coverage) |
| anthropic/claude-opus-5 | 2026-07-31 | reasoning | #2 of 326 (provisional) | #4 (provisional) | unranked (0% coverage) |
| anthropic/claude-opus-5 | 2026-07-31 | chat | #3 of 313 (ranked) | #4 (ranked) | unranked (0% coverage) |
| qwen/qwen3-8-max | 2026-08-10 | coding | #4 of 230 (ranked) | #5 (ranked) | unranked (0% coverage) |
| qwen/qwen3-8-max | 2026-08-10 | reasoning | #4 of 327 (provisional) | #8 (provisional) | unranked (0% coverage) |
| qwen/qwen3-8-max | 2026-08-10 | chat | #4 of 316 (ranked) | #9 (ranked) | unranked (0% coverage) |
| deepseek/deepseek-v4-pro | 2026-08-19 | coding | #40 of 234 (ranked) | #36 (ranked) | unranked (16% coverage) |
| deepseek/deepseek-v4-pro | 2026-08-19 | reasoning | #50 of 331 (provisional) | #50 (provisional) | unranked (28% coverage) |
| deepseek/deepseek-v4-pro | 2026-08-19 | chat | #38 of 320 (ranked) | #38 (ranked) | unranked (10% coverage) |
| xai/grok-4-6 | 2026-08-19 | coding | #9 of 234 (ranked) | #10 (ranked) | unranked (0% coverage) |
| xai/grok-4-6 | 2026-08-19 | reasoning | #17 of 331 (provisional) | #23 (provisional) | unranked (0% coverage) |
| xai/grok-4-6 | 2026-08-19 | chat | #18 of 320 (ranked) | #31 (ranked) | unranked (0% coverage) |
| google/gemini-3-7-flash | 2026-08-20 | coding | #11 of 234 (ranked) | #15 (ranked) | unranked (0% coverage) |
| google/gemini-3-7-flash | 2026-08-20 | reasoning | insufficient | #11 (provisional) | unranked (0% coverage) |
| google/gemini-3-7-flash | 2026-08-20 | chat | insufficient | #7 (ranked) | unranked (0% coverage) |
| zhipu/glm-5-3 | 2026-08-21 | coding | #10 of 237 (ranked) | #7 (ranked) | unranked (0% coverage) |
| zhipu/glm-5-3 | 2026-08-21 | reasoning | #9 of 335 (provisional) | #9 (provisional) | unranked (0% coverage) |
| zhipu/glm-5-3 | 2026-08-21 | chat | #8 of 324 (ranked) | #11 (ranked) | unranked (0% coverage) |
| anthropic/claude-fable-5-1 | 2026-09-08 | coding | #2 of 246 (ranked) | #3 (ranked) | unranked (0% coverage) |
| anthropic/claude-fable-5-1 | 2026-09-08 | reasoning | #2 of 342 (provisional) | #3 (provisional) | unranked (0% coverage) |
| anthropic/claude-fable-5-1 | 2026-09-08 | chat | #3 of 330 (ranked) | #4 (ranked) | unranked (0% coverage) |
| google/gemini-3-8-flash | 2026-09-09 | coding | #16 of 246 (ranked) | #13 (ranked) | unranked (0% coverage) |
| google/gemini-3-8-flash | 2026-09-09 | reasoning | #5 of 342 (ranked) | #6 (ranked) | unranked (16% coverage) |
| google/gemini-3-8-flash | 2026-09-09 | chat | #5 of 330 (ranked) | #5 (ranked) | unranked (0% coverage) |
| openai/gpt-6-astra | 2026-09-11 | coding | #2 of 247 (ranked) | #2 (ranked) | unranked (0% coverage) |
| openai/gpt-6-astra | 2026-09-11 | reasoning | #1 of 343 (provisional) | #8 (provisional) | unranked (16% coverage) |
| openai/gpt-6-astra | 2026-09-11 | chat | insufficient | #13 (ranked) | unranked (0% coverage) |
| deepseek/deepseek-flash | 2026-09-17 | coding | #11 of 247 (ranked) | #11 (ranked) | unranked (0% coverage) |
| deepseek/deepseek-flash | 2026-09-17 | reasoning | #35 of 343 (provisional) | #36 (provisional) | unranked (16% coverage) |
| deepseek/deepseek-flash | 2026-09-17 | chat | insufficient | insufficient | unranked (0% coverage) |
| xai/grok-4-7 | 2026-09-24 | coding | #11 of 250 (ranked) | #11 (ranked) | unranked (0% coverage) |
| xai/grok-4-7 | 2026-09-24 | reasoning | insufficient | insufficient | unranked (0% coverage) |
| xai/grok-4-7 | 2026-09-24 | chat | insufficient | insufficient | unranked (0% coverage) |
| anthropic/claude-opus-5-5 | 2026-09-24 | coding | #1 of 250 (ranked) | #1 (ranked) | unranked (0% coverage) |
| anthropic/claude-opus-5-5 | 2026-09-24 | reasoning | #1 of 344 (provisional) | #1 (provisional) | unranked (0% coverage) |
| anthropic/claude-opus-5-5 | 2026-09-24 | chat | insufficient | insufficient | unranked (0% coverage) |
| openai/gpt-6-sol | 2026-09-24 | coding | #7 of 250 (ranked) | #7 (ranked) | unranked (0% coverage) |
| openai/gpt-6-sol | 2026-09-24 | reasoning | insufficient | insufficient | unranked (0% coverage) |
| openai/gpt-6-sol | 2026-09-24 | chat | insufficient | insufficient | unranked (0% coverage) |
