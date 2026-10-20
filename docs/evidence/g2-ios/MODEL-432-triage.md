# Release discovery triage: DRY RUN

No issues were closed or labeled. Review this report before applying any changes.

| Classification | Count |
| --- | ---: |
| duplicate | 19 |
| superseded | 6 |
| real | 151 |
| noise | 1 |

Catalogue checked: yes.
Superseded means an exact release or alias is already carded; newer versions do not supersede older ones automatically.

## Duplicate samples

- [#496](https://github.com/turbobeest/modelspec/issues/496) release discovery: LoopedLM-P1-dense-d112-500b (ifm) `watch:ifm:loopedlm-p1-dense-d112-500b`. Another open issue represents the same canonical release. Keep #495.
- [#499](https://github.com/turbobeest/modelspec/issues/499) release discovery: LoopedLM-P1-dense-huginn-500b (ifm) `watch:ifm:loopedlm-p1-dense-huginn-500b`. Another open issue represents the same canonical release. Keep #498.
- [#508](https://github.com/turbobeest/modelspec/issues/508) release discovery: LoopedLM-P1-moe-ff112-500b (ifm) `watch:ifm:loopedlm-p1-moe-ff112-500b`. Another open issue represents the same canonical release. Keep #507.
- [#511](https://github.com/turbobeest/modelspec/issues/511) release discovery: LoopedLM-P1-moe-huginn-500b (ifm) `watch:ifm:loopedlm-p1-moe-huginn-500b`. Another open issue represents the same canonical release. Keep #510.
- [#513](https://github.com/turbobeest/modelspec/issues/513) release discovery: LoopedLM-P1-moe-middle-500b (ifm) `watch:ifm:loopedlm-p1-moe-middle-500b`. Another open issue represents the same canonical release. Keep #512.

## Superseded samples

- [#468](https://github.com/turbobeest/modelspec/issues/468) release discovery: grok-imagine-video-1.5-lite (xai) `watch:xai:grok-imagine-video-1-5-lite`. An exact canonical release or alias is already carded.
- [#616](https://github.com/turbobeest/modelspec/issues/616) release discovery: mistral-large-4-0 (mistral) `watch:mistral:mistral-large-4-0`. An exact canonical release or alias is already carded.
- [#624](https://github.com/turbobeest/modelspec/issues/624) release discovery: claude-haiku-5-5 (anthropic) `watch:anthropic:claude-haiku-5-5`. An exact canonical release or alias is already carded.
- [#632](https://github.com/turbobeest/modelspec/issues/632) release discovery: step-5-preview (stepfun) `watch:stepfun:step-5-preview`. An exact canonical release or alias is already carded.
- [#722](https://github.com/turbobeest/modelspec/issues/722) release discovery: gemini-4-argon (google) `watch:google:gemini-4-argon`. An exact canonical release or alias is already carded.

## Real samples

- [#413](https://github.com/turbobeest/modelspec/issues/413) release discovery: embed-v5.0-fast (cohere) `watch:cohere:embed-v5-0-fast`. Distinct possible model release; keep for review.
- [#414](https://github.com/turbobeest/modelspec/issues/414) release discovery: embed-v5.0-pro (cohere) `watch:cohere:embed-v5-0-pro`. Distinct possible model release; keep for review.
- [#424](https://github.com/turbobeest/modelspec/issues/424) release discovery: mistral-ocr-4-0 (mistral) `watch:mistral:mistral-ocr-4-0`. Distinct possible model release; keep for review.
- [#425](https://github.com/turbobeest/modelspec/issues/425) release discovery: RWKV7-G1k-2.9B-20260930 (rwkv) `watch:rwkv:rwkv7-g1k-2-9b-20260930`. Distinct possible model release; keep for review.
- [#426](https://github.com/turbobeest/modelspec/issues/426) release discovery: RWKV7-G1k-7.2B-20260930 (rwkv) `watch:rwkv:rwkv7-g1k-7-2b-20260930`. Distinct possible model release; keep for review.

## Noise samples

- [#460](https://github.com/turbobeest/modelspec/issues/460) release discovery: ensemble-forecasting-with-ibm-granite-time-series (ibm) `watch:ibm:ensemble-forecasting-with-ibm-granite-time-series`. forecasting example repository

## Complete proposed classification

This is a review proposal. No actions were applied. `real` retains an unverified candidate.

| Issue | Classification | Keep issue | Canonical release |
| --- | --- | --- | --- |
| [#413](https://github.com/turbobeest/modelspec/issues/413) | real |  | `cohere:embed-v5-0-fast` |
| [#414](https://github.com/turbobeest/modelspec/issues/414) | real |  | `cohere:embed-v5-0-pro` |
| [#424](https://github.com/turbobeest/modelspec/issues/424) | real |  | `mistral:mistral-ocr-4` |
| [#425](https://github.com/turbobeest/modelspec/issues/425) | real |  | `rwkv:rwkv7-g1k-2-9b-20260930` |
| [#426](https://github.com/turbobeest/modelspec/issues/426) | real |  | `rwkv:rwkv7-g1k-7-2b-20260930` |
| [#441](https://github.com/turbobeest/modelspec/issues/441) | real |  | `rwkv:rwkv7-g1k-1-5b-20260930` |
| [#442](https://github.com/turbobeest/modelspec/issues/442) | real |  | `rwkv:rwkv7-g1k-13-3b-20260930` |
| [#460](https://github.com/turbobeest/modelspec/issues/460) | noise |  | `ibm:ensemble-forecasting-with-ibm-granite-time-series` |
| [#468](https://github.com/turbobeest/modelspec/issues/468) | superseded |  | `xai:grok-imagine-video-1-5-lite` |
| [#469](https://github.com/turbobeest/modelspec/issues/469) | real |  | `nvidia:pixeldit2-imagenet` |
| [#470](https://github.com/turbobeest/modelspec/issues/470) | real |  | `nvidia:pixelumm` |
| [#488](https://github.com/turbobeest/modelspec/issues/488) | real |  | `allen-ai:astabrief-8b-sft` |
| [#489](https://github.com/turbobeest/modelspec/issues/489) | real |  | `ifm:k2-type-0-9b` |
| [#490](https://github.com/turbobeest/modelspec/issues/490) | real |  | `inclusionai:ling-3-1-flash` |
| [#494](https://github.com/turbobeest/modelspec/issues/494) | real |  | `microsoft:frognano-4b-2609` |
| [#495](https://github.com/turbobeest/modelspec/issues/495) | real |  | `ifm:loopedlm-p1-dense-d112` |
| [#496](https://github.com/turbobeest/modelspec/issues/496) | duplicate | #495 | `ifm:loopedlm-p1-dense-d112` |
| [#497](https://github.com/turbobeest/modelspec/issues/497) | real |  | `ifm:loopedlm-p1-dense-d28` |
| [#498](https://github.com/turbobeest/modelspec/issues/498) | real |  | `ifm:loopedlm-p1-dense-huginn` |
| [#499](https://github.com/turbobeest/modelspec/issues/499) | duplicate | #498 | `ifm:loopedlm-p1-dense-huginn` |
| [#500](https://github.com/turbobeest/modelspec/issues/500) | real |  | `ifm:loopedlm-p1-dense-middle` |
| [#501](https://github.com/turbobeest/modelspec/issues/501) | real |  | `ifm:loopedlm-p1-dense-middle-prelude-injection` |
| [#502](https://github.com/turbobeest/modelspec/issues/502) | real |  | `ifm:loopedlm-p1-dense-ouro` |
| [#503](https://github.com/turbobeest/modelspec/issues/503) | real |  | `ifm:loopedlm-p1-dense-ouro-raw-injection` |
| [#504](https://github.com/turbobeest/modelspec/issues/504) | real |  | `ifm:loopedlm-p1-dense-shared-hl` |
| [#505](https://github.com/turbobeest/modelspec/issues/505) | real |  | `ifm:loopedlm-p1-dense-split-hl` |
| [#506](https://github.com/turbobeest/modelspec/issues/506) | real |  | `ifm:loopedlm-p1-dense-split-hl-x2` |
| [#507](https://github.com/turbobeest/modelspec/issues/507) | real |  | `ifm:loopedlm-p1-moe-ff112` |
| [#508](https://github.com/turbobeest/modelspec/issues/508) | duplicate | #507 | `ifm:loopedlm-p1-moe-ff112` |
| [#509](https://github.com/turbobeest/modelspec/issues/509) | real |  | `ifm:loopedlm-p1-moe-ff112-prelude-injection` |
| [#510](https://github.com/turbobeest/modelspec/issues/510) | real |  | `ifm:loopedlm-p1-moe-huginn` |
| [#511](https://github.com/turbobeest/modelspec/issues/511) | duplicate | #510 | `ifm:loopedlm-p1-moe-huginn` |
| [#512](https://github.com/turbobeest/modelspec/issues/512) | real |  | `ifm:loopedlm-p1-moe-middle` |
| [#513](https://github.com/turbobeest/modelspec/issues/513) | duplicate | #512 | `ifm:loopedlm-p1-moe-middle` |
| [#514](https://github.com/turbobeest/modelspec/issues/514) | real |  | `ifm:loopedlm-p1-moe-middle-input-injection` |
| [#515](https://github.com/turbobeest/modelspec/issues/515) | duplicate | #514 | `ifm:loopedlm-p1-moe-middle-input-injection` |
| [#516](https://github.com/turbobeest/modelspec/issues/516) | real |  | `ifm:loopedlm-p1-moe-ouro` |
| [#517](https://github.com/turbobeest/modelspec/issues/517) | duplicate | #516 | `ifm:loopedlm-p1-moe-ouro` |
| [#518](https://github.com/turbobeest/modelspec/issues/518) | real |  | `ifm:loopedlm-p1-moe-shared-hl` |
| [#519](https://github.com/turbobeest/modelspec/issues/519) | duplicate | #518 | `ifm:loopedlm-p1-moe-shared-hl` |
| [#520](https://github.com/turbobeest/modelspec/issues/520) | real |  | `ifm:loopedlm-p2-d4-m` |
| [#521](https://github.com/turbobeest/modelspec/issues/521) | real |  | `ifm:loopedlm-p2-d4-s` |
| [#522](https://github.com/turbobeest/modelspec/issues/522) | real |  | `ifm:loopedlm-p2-distilled-m-random-init` |
| [#523](https://github.com/turbobeest/modelspec/issues/523) | real |  | `ifm:loopedlm-p2-distilled-m-teacher-init` |
| [#524](https://github.com/turbobeest/modelspec/issues/524) | real |  | `ifm:loopedlm-p2-distilled-s-random-init` |
| [#525](https://github.com/turbobeest/modelspec/issues/525) | real |  | `ifm:loopedlm-p2-distilled-s-teacher-init` |
| [#526](https://github.com/turbobeest/modelspec/issues/526) | real |  | `ifm:loopedlm-p2-huginn-l-fixed-pln5` |
| [#527](https://github.com/turbobeest/modelspec/issues/527) | real |  | `ifm:loopedlm-p2-huginn-l-fixed-r5` |
| [#528](https://github.com/turbobeest/modelspec/issues/528) | real |  | `ifm:loopedlm-p2-huginn-l-learned-entropy0` |
| [#529](https://github.com/turbobeest/modelspec/issues/529) | real |  | `ifm:loopedlm-p2-huginn-l-learned-entropy0p01` |
| [#530](https://github.com/turbobeest/modelspec/issues/530) | real |  | `ifm:loopedlm-p2-huginn-m-fixed-pln5` |
| [#531](https://github.com/turbobeest/modelspec/issues/531) | real |  | `ifm:loopedlm-p2-huginn-m-fixed-r5` |
| [#532](https://github.com/turbobeest/modelspec/issues/532) | real |  | `ifm:loopedlm-p2-huginn-m-huginn-linear` |
| [#533](https://github.com/turbobeest/modelspec/issues/533) | real |  | `ifm:loopedlm-p2-huginn-m-learned-entropy0` |
| [#534](https://github.com/turbobeest/modelspec/issues/534) | real |  | `ifm:loopedlm-p2-huginn-m-learned-entropy0p01` |
| [#535](https://github.com/turbobeest/modelspec/issues/535) | real |  | `ifm:loopedlm-p2-huginn-m-orthoinj` |
| [#536](https://github.com/turbobeest/modelspec/issues/536) | real |  | `ifm:loopedlm-p2-huginn-m-parcae` |
| [#537](https://github.com/turbobeest/modelspec/issues/537) | real |  | `ifm:loopedlm-p2-huginn-s-fixed-pln5` |
| [#538](https://github.com/turbobeest/modelspec/issues/538) | real |  | `ifm:loopedlm-p2-huginn-s-fixed-r5` |
| [#539](https://github.com/turbobeest/modelspec/issues/539) | real |  | `ifm:loopedlm-p2-huginn-s-huginn-linear` |
| [#540](https://github.com/turbobeest/modelspec/issues/540) | real |  | `ifm:loopedlm-p2-huginn-s-learned-entropy0` |
| [#541](https://github.com/turbobeest/modelspec/issues/541) | real |  | `ifm:loopedlm-p2-huginn-s-learned-entropy0p01` |
| [#542](https://github.com/turbobeest/modelspec/issues/542) | real |  | `ifm:loopedlm-p2-huginn-s-orthoinj` |
| [#543](https://github.com/turbobeest/modelspec/issues/543) | real |  | `ifm:loopedlm-p2-huginn-s-parcae` |
| [#544](https://github.com/turbobeest/modelspec/issues/544) | real |  | `nvidia:switchyard` |
| [#597](https://github.com/turbobeest/modelspec/issues/597) | real |  | `google:diarizationlm-gemma-4-e4b-v1` |
| [#598](https://github.com/turbobeest/modelspec/issues/598) | real |  | `primeintellect:qwen3-5-0-8b-reverse-text-rl` |
| [#599](https://github.com/turbobeest/modelspec/issues/599) | real |  | `primeintellect:qwen3-5-0-8b-reverse-text-sft` |
| [#604](https://github.com/turbobeest/modelspec/issues/604) | real |  | `primeintellect:qwen3-0-6b-reverse-text-sft-untied` |
| [#605](https://github.com/turbobeest/modelspec/issues/605) | real |  | `primeintellect:qwen3-0-6b-untied` |
| [#606](https://github.com/turbobeest/modelspec/issues/606) | real |  | `primeintellect:qwen3-4b-instruct-2507-untied` |
| [#607](https://github.com/turbobeest/modelspec/issues/607) | real |  | `primeintellect:qwen3-5-4b-untied` |
| [#608](https://github.com/turbobeest/modelspec/issues/608) | real |  | `swiss-ai:apertus-v1-5-70b-base` |
| [#609](https://github.com/turbobeest/modelspec/issues/609) | real |  | `swiss-ai:apertus-v1-5-8b-base` |
| [#610](https://github.com/turbobeest/modelspec/issues/610) | real |  | `ibm:granite-timeseries-ensemble-r1` |
| [#615](https://github.com/turbobeest/modelspec/issues/615) | real |  | `google:gemini-nano-banana-2-1` |
| [#616](https://github.com/turbobeest/modelspec/issues/616) | superseded |  | `mistral:mistral-large-4` |
| [#617](https://github.com/turbobeest/modelspec/issues/617) | real |  | `google:embeddinggemma-2` |
| [#618](https://github.com/turbobeest/modelspec/issues/618) | real |  | `openbmb:minicpm-v-4-7-35b-a3b` |
| [#619](https://github.com/turbobeest/modelspec/issues/619) | duplicate | #617 | `google:embeddinggemma-2` |
| [#624](https://github.com/turbobeest/modelspec/issues/624) | superseded |  | `anthropic:claude-haiku-5-5` |
| [#625](https://github.com/turbobeest/modelspec/issues/625) | real |  | `liquid:d1-3b` |
| [#626](https://github.com/turbobeest/modelspec/issues/626) | real |  | `liquid:d1-omni-600m` |
| [#632](https://github.com/turbobeest/modelspec/issues/632) | superseded |  | `stepfun:step-5-preview` |
| [#648](https://github.com/turbobeest/modelspec/issues/648) | real |  | `nvidia:agile-one-s-pick-ssd-n17` |
| [#649](https://github.com/turbobeest/modelspec/issues/649) | duplicate | #648 | `nvidia:agile-one-s-pick-ssd-n17` |
| [#650](https://github.com/turbobeest/modelspec/issues/650) | real |  | `nvidia:agile-one-s-place-ssd-n17` |
| [#651](https://github.com/turbobeest/modelspec/issues/651) | real |  | `nvidia:agile-one-s-walk-n2-1680` |
| [#652](https://github.com/turbobeest/modelspec/issues/652) | real |  | `tencent:youtu-parsing-omni` |
| [#655](https://github.com/turbobeest/modelspec/issues/655) | real |  | `alibaba-qwen-team:qwen-image-2-1-turbo` |
| [#656](https://github.com/turbobeest/modelspec/issues/656) | real |  | `mistral:lidstral-arabic` |
| [#657](https://github.com/turbobeest/modelspec/issues/657) | real |  | `mistral:voxtral-mini-4b-realtime-arabic` |
| [#665](https://github.com/turbobeest/modelspec/issues/665) | real |  | `nvidia:agile-one-s-pick-ssd-n2` |
| [#666](https://github.com/turbobeest/modelspec/issues/666) | real |  | `nvidia:agile-one-s-pickplace-ssd-n2` |
| [#667](https://github.com/turbobeest/modelspec/issues/667) | real |  | `nvidia:agile-one-s-place-ssd-n2` |
| [#692](https://github.com/turbobeest/modelspec/issues/692) | real |  | `agnes-ai:agnes-3-0-qwen` |
| [#703](https://github.com/turbobeest/modelspec/issues/703) | real |  | `microsoft:aescode-32b` |
| [#704](https://github.com/turbobeest/modelspec/issues/704) | real |  | `microsoft:aescode-8b` |
| [#705](https://github.com/turbobeest/modelspec/issues/705) | real |  | `agnes-ai:agnes-video-2-0-moe` |
| [#706](https://github.com/turbobeest/modelspec/issues/706) | real |  | `together:hybridagent-14b-agentic` |
| [#707](https://github.com/turbobeest/modelspec/issues/707) | real |  | `together:hybridagent-8b-agentic` |
| [#708](https://github.com/turbobeest/modelspec/issues/708) | real |  | `openbmb:trident-train` |
| [#709](https://github.com/turbobeest/modelspec/issues/709) | real |  | `openbmb:trident-qwen3vl-2b` |
| [#710](https://github.com/turbobeest/modelspec/issues/710) | real |  | `skywork:matrix-game-4-0` |
| [#711](https://github.com/turbobeest/modelspec/issues/711) | real |  | `openbmb:minicpm-v-4-7-1b` |
| [#712](https://github.com/turbobeest/modelspec/issues/712) | real |  | `openbmb:minicpm-v-4-7-1b-dspark` |
| [#713](https://github.com/turbobeest/modelspec/issues/713) | real |  | `openbmb:minicpm-v-4-7-35b-a3b-dspark` |
| [#722](https://github.com/turbobeest/modelspec/issues/722) | superseded |  | `google:gemini-4-argon` |
| [#723](https://github.com/turbobeest/modelspec/issues/723) | real |  | `google:gemini-4-stable` |
| [#724](https://github.com/turbobeest/modelspec/issues/724) | real |  | `liquid:lfm-2-5-24b-a2b` |
| [#725](https://github.com/turbobeest/modelspec/issues/725) | real |  | `liquid:lfm-2-5-24b-a2b-base` |
| [#726](https://github.com/turbobeest/modelspec/issues/726) | real |  | `liquid:lfm-2-5-24b-a2b-preview` |
| [#727](https://github.com/turbobeest/modelspec/issues/727) | duplicate | #724 | `liquid:lfm-2-5-24b-a2b` |
| [#735](https://github.com/turbobeest/modelspec/issues/735) | real |  | `nvidia:gr00t-n1-7-appletoplate-cosine40k-checkpoint-15000` |
| [#736](https://github.com/turbobeest/modelspec/issues/736) | duplicate | #724 | `liquid:lfm-2-5-24b-a2b` |
| [#754](https://github.com/turbobeest/modelspec/issues/754) | real |  | `mistral:mistral-audio-realtime-fact-checker-01-realtime-fact-checker` |
| [#755](https://github.com/turbobeest/modelspec/issues/755) | real |  | `xai:grok-voice-2-0` |
| [#756](https://github.com/turbobeest/modelspec/issues/756) | real |  | `xai:grok-voice-3-0` |
| [#757](https://github.com/turbobeest/modelspec/issues/757) | real |  | `allen-ai:hiro-acev2` |
| [#761](https://github.com/turbobeest/modelspec/issues/761) | real |  | `microsoft:userrepgen-4b` |
| [#762](https://github.com/turbobeest/modelspec/issues/762) | superseded |  | `deepseek:deepseek-v4-1-flash` |
| [#767](https://github.com/turbobeest/modelspec/issues/767) | duplicate | #632 | `stepfun:step-5-preview` |
| [#769](https://github.com/turbobeest/modelspec/issues/769) | real |  | `ifm:jais-asr` |
| [#770](https://github.com/turbobeest/modelspec/issues/770) | real |  | `mistral:timestral-123m` |
| [#771](https://github.com/turbobeest/modelspec/issues/771) | real |  | `mistral:timestral-209m` |
| [#772](https://github.com/turbobeest/modelspec/issues/772) | real |  | `mistral:timestral-28m` |
| [#773](https://github.com/turbobeest/modelspec/issues/773) | real |  | `mistral:timestral-5m` |
| [#774](https://github.com/turbobeest/modelspec/issues/774) | real |  | `nvidia:nemotron-3-5-bolt-74b-a9b-24gb` |
| [#775](https://github.com/turbobeest/modelspec/issues/775) | real |  | `nvidia:nemotron-3-5-bolt-74b-a9b-24gb-lilicorr` |
| [#776](https://github.com/turbobeest/modelspec/issues/776) | real |  | `nvidia:nemotron-3-5-bolt-74b-a9b` |
| [#777](https://github.com/turbobeest/modelspec/issues/777) | real |  | `nvidia:nemotron-3-5-super-vl-120b-a12b` |
| [#778](https://github.com/turbobeest/modelspec/issues/778) | real |  | `nvidia:nemotron-3-5-super-vl-120b-a12b-base` |
| [#779](https://github.com/turbobeest/modelspec/issues/779) | real |  | `nvidia:nemotron-3-5-rerank-8b` |
| [#780](https://github.com/turbobeest/modelspec/issues/780) | real |  | `black-forest-labs:flux-3-image-klein` |
| [#781](https://github.com/turbobeest/modelspec/issues/781) | real |  | `black-forest-labs:flux-3-image-klein-base` |
| [#782](https://github.com/turbobeest/modelspec/issues/782) | real |  | `black-forest-labs:flux-3-image-klein-comfy` |
| [#783](https://github.com/turbobeest/modelspec/issues/783) | real |  | `black-forest-labs:flux-3-image-klein-pup` |
| [#784](https://github.com/turbobeest/modelspec/issues/784) | real |  | `meta:muse-spark-open-816b-a42b` |
| [#785](https://github.com/turbobeest/modelspec/issues/785) | duplicate | #777 | `nvidia:nemotron-3-5-super-vl-120b-a12b` |
| [#786](https://github.com/turbobeest/modelspec/issues/786) | duplicate | #777 | `nvidia:nemotron-3-5-super-vl-120b-a12b` |
| [#788](https://github.com/turbobeest/modelspec/issues/788) | real |  | `microsoft:scfm-dataselection` |
| [#789](https://github.com/turbobeest/modelspec/issues/789) | real |  | `nvidia:ardy-soma-rp-30fps-kimodorep-horizon60` |
| [#790](https://github.com/turbobeest/modelspec/issues/790) | real |  | `nvidia:kimodo-soma-rp-ardyrep-v1-2` |
| [#791](https://github.com/turbobeest/modelspec/issues/791) | real |  | `nvidia:kimodo-soma-rp-v1-2` |
| [#792](https://github.com/turbobeest/modelspec/issues/792) | real |  | `nvidia:nemotron-3-5-embed-1b` |
| [#793](https://github.com/turbobeest/modelspec/issues/793) | real |  | `nvidia:nemotron-3-5-embed-8b` |
| [#794](https://github.com/turbobeest/modelspec/issues/794) | real |  | `ibm:granite-switch-4-1-30b` |
| [#795](https://github.com/turbobeest/modelspec/issues/795) | real |  | `ibm:granite-switch-4-1-8b` |
| [#796](https://github.com/turbobeest/modelspec/issues/796) | real |  | `nvidia:muse-spark-open-816b-a42b-dflash2` |
| [#797](https://github.com/turbobeest/modelspec/issues/797) | real |  | `nvidia:lidarverse` |
| [#798](https://github.com/turbobeest/modelspec/issues/798) | real |  | `tencent:hy-memory-30b-a3b` |
| [#799](https://github.com/turbobeest/modelspec/issues/799) | duplicate | #780 | `black-forest-labs:flux-3-image-klein` |
| [#800](https://github.com/turbobeest/modelspec/issues/800) | duplicate | #781 | `black-forest-labs:flux-3-image-klein-base` |
| [#801](https://github.com/turbobeest/modelspec/issues/801) | real |  | `tencent:qwen3-8b-dspine-b16` |
| [#802](https://github.com/turbobeest/modelspec/issues/802) | real |  | `nvidia:nemotron-labs-dory1-0-4b` |
| [#803](https://github.com/turbobeest/modelspec/issues/803) | duplicate | #802 | `nvidia:nemotron-labs-dory1-0-4b` |
| [#805](https://github.com/turbobeest/modelspec/issues/805) | real |  | `deepseek:deepseek-v4-1-flash-1017` |
| [#815](https://github.com/turbobeest/modelspec/issues/815) | duplicate | #805 | `deepseek:deepseek-v4-1-flash-1017` |
| [#826](https://github.com/turbobeest/modelspec/issues/826) | real |  | `nvidia:cosmos3-nano-libero10-sdg-export-d` |
| [#827](https://github.com/turbobeest/modelspec/issues/827) | real |  | `nvidia:cosmos3-nano-libero10-sdg-export-d2` |
| [#828](https://github.com/turbobeest/modelspec/issues/828) | real |  | `nvidia:cosmos3-nano-libero10-sdg-export-d5` |
| [#829](https://github.com/turbobeest/modelspec/issues/829) | real |  | `nvidia:cosmos3-nano-libero10-sdg-export-d-half` |
| [#830](https://github.com/turbobeest/modelspec/issues/830) | real |  | `nvidia:cosmos3-nano-libero10-sdg-export-r` |
| [#831](https://github.com/turbobeest/modelspec/issues/831) | real |  | `nvidia:cosmos3-nano-libero10-sdg-export-s2` |
| [#832](https://github.com/turbobeest/modelspec/issues/832) | real |  | `nvidia:cosmos3-nano-libero10-sdg-export-s5-2` |
| [#833](https://github.com/turbobeest/modelspec/issues/833) | real |  | `nvidia:cosmos3-nano-libero10-sdg-export-s5-all` |
| [#834](https://github.com/turbobeest/modelspec/issues/834) | real |  | `nvidia:cosmos3-nano-libero10-sdg-export-s-all` |
| [#835](https://github.com/turbobeest/modelspec/issues/835) | real |  | `nvidia:cosmos3-nano-libero10-sdg-export-s-best` |
| [#836](https://github.com/turbobeest/modelspec/issues/836) | real |  | `nvidia:cosmos3-nano-libero10-sdg-export-s-worst` |
| [#837](https://github.com/turbobeest/modelspec/issues/837) | real |  | `nvidia:cosmos3-nano-libero10-sft-exports` |
| [#838](https://github.com/turbobeest/modelspec/issues/838) | real |  | `trillionlabs:trida2-1-4b` |
| [#842](https://github.com/turbobeest/modelspec/issues/842) | real |  | `inception:mercury-3` |
| [#845](https://github.com/turbobeest/modelspec/issues/845) | real |  | `nvidia:cosmos-anomalygen-glass-nano` |
| [#846](https://github.com/turbobeest/modelspec/issues/846) | real |  | `nvidia:cosmos-anomalygen-metal-nano` |
| [#847](https://github.com/turbobeest/modelspec/issues/847) | real |  | `nvidia:cosmos-anomalygen-pcb-nano` |
| [#854](https://github.com/turbobeest/modelspec/issues/854) | real |  | `nvidia:cdf-sim2real-smt-solderlight` |
| [#855](https://github.com/turbobeest/modelspec/issues/855) | real |  | `meta:sam3-1` |
