---
id: arena_elo_vision
name: "Arena Elo — Vision"
aliases:
  - "Chatbot Arena Vision leaderboard"
  - "Multimodal Arena"
  - "LMArena Vision"
page_kind: subset
category: human-preference
subcategory: "pairwise human preference, image+text"
status: active
summary: "A separate Elo leaderboard for vision-language models, built only from Arena battles whose prompt included an image."
measures: >
  arena_elo_vision is a separate Arena leaderboard computed only from anonymous battles whose
  prompt included an image: two vision-language models are compared head-to-head on the same
  image-plus-text input, and a voter picks the preferred response before identities are revealed.
  It launched in June 2024 as the Multimodal ("Vision") Arena, drawing over 17,000 votes across
  more than 60 languages in its first two weeks, on tasks the team observed spanning captioning,
  visual math questions, document understanding and meme explanation. It is rated with the same
  Bradley-Terry pipeline as the Text arena, but over its own, separate vote pool.
task_format: "Anonymous, randomized side-by-side chat where the user's prompt includes at least one image; a user votes for the preferred response."
metric:
  name: "Elo"
  direction: higher_is_better
  unit: ""
  max_score: null
  random_baseline: null
  human_baseline: null
  baseline_note: "Same anchored, open-ended scale as the arena_elo family: no fixed random baseline or maximum."
dataset:
  size: null
  size_note: "17,429 votes across roughly two weeks at the June 2024 launch; 1,258,468 votes across 148 rated models as of an August 2026 snapshot read for this page."
  url: "https://huggingface.co/lmarena-ai"
  license: ""
  languages: []
  modalities:
    - text
    - image
  splits: ""
  public_test_set: null
publisher:
  org: "LMSYS (Large Model Systems Organization), UC Berkeley Sky Computing Lab (founding org); operates today as Arena (formerly LMArena)"
  authors:
    - "Christopher Chou"
    - "Lisa Dunlap"
    - "Wei-Lin Chiang"
  url: "https://arena.ai"
paper:
  title: "Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference"
  arxiv: "2403.04132"
  url: "https://arxiv.org/abs/2403.04132"
  year: 2024
leaderboard_url: "https://arena.ai/leaderboard/vision"
repo_url: "https://github.com/lm-sys/FastChat"
released: "2024-06"
last_updated: ""
lineage:
  family: arena_elo
  predecessor: ""
  successors: []
  variants: []
saturation:
  status: open
  top_score: 1313
  as_of: "2026-08"
  note: "On an August 27, 2026 snapshot read for this page, the top rating was 1313 (±8) across 148 rated models, with several models clustered close behind — consistent with an open, still-separating field rather than a fixed ceiling."
contamination:
  risk: low
  note: "Same as the arena_elo family: prompts are live user submissions, not a fixed, publishable answer key."
harness:
  lm_eval: ""
  inspect_evals: ""
  helm: ""
  opencompass: ""
  bigbench: ""
  other: "No offline harness; ratings come only from live votes on the platform's separate Vision arena. A Vision Arena dataset release has since been published as academic research (cited in the family page's Open Research links)."
tags:
  - human-preference
  - chatbot
  - elo
  - vision
  - multimodal
sources:
  - url: "https://arxiv.org/abs/2403.04132"
    title: "Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference (arXiv)"
    accessed: "2026-09-08"
  - url: "https://www.lmsys.org/blog/2024-06-27-multimodal"
    title: "The Multimodal Arena is Here! (LMSYS blog)"
    accessed: "2026-09-08"
  - url: "https://arena.ai/leaderboard/vision"
    title: "Vision Arena leaderboard (Arena)"
    accessed: "2026-09-08"
freshness:
  researched: "2026-09-08"
  researched_by: "sonnet-5 agent, batch 1b, slice J"
  reviewed: ""
  reviewed_by: ""
---

Part of the [Arena Elo](arena_elo.md) family.

## What it measures

arena_elo_vision is a separate Arena leaderboard computed only from anonymous battles whose
prompt included an image: two vision-language models are compared head-to-head on the same
image-plus-text input, and a voter picks the preferred response before identities are revealed.
It launched in June 2024 as the Multimodal ("Vision") Arena, drawing over 17,000 votes across
more than 60 languages in its first two weeks, on tasks the team observed spanning captioning,
visual math questions, document understanding and meme explanation. It uses the same
Bradley-Terry pipeline as the Text arena, but over its own, separate vote pool.

## Reading the numbers

At launch, vision rankings tracked the Text leaderboard fairly closely but not exactly: GPT-4o
and Claude 3.5 Sonnet separated further from Gemini 1.5 Pro and GPT-4 Turbo in vision than in
text, and Claude 3 Opus and Gemini 1.5 Flash landed close together despite a clearer gap on the
text board. As of an August 2026 snapshot read for this page, the board carried 148 rated models
and roughly 1.26 million votes, with the top rating at 1313 (±8). A high score here says a
model's image-grounded chat responses are broadly preferred by voters; it is a single-image,
chat-style test and does not speak to other multimodal skills such as video, audio or
multi-image reasoning.
