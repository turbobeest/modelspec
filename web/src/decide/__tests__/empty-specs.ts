// Three recall questions the verified lineup cannot answer yet (MODEL-153),
// as page specs, and what the engine returned for each on snap_898e29e1f0c39d6e
// (`scripts/decide_dev_server.py`'s module, explain=full).
import q10Json from "../__fixtures__/empty-q10.json";
import q17Json from "../__fixtures__/empty-q17.json";
import q20Json from "../__fixtures__/empty-q20.json";
import { decisionSchema } from "../adapter/contract";
import type { Spec } from "../engine/types";

const base = { tokIn: 40000, tokOut: 4000, w: { cap: 1, cost: 0, speed: 0 } };

export const EMPTY_SPECS: Record<"q10" | "q17" | "q20", Spec> = {
  q10: {
    ...base,
    task: "A high-volume assistant whose input price is at most $0.20 per million tokens",
    bench: "arena_elo_style_control",
    domain: "chat_preference",
    conds: [
      { f: "type", v: "llm" },
      { f: "active" },
      { f: "open", v: false },
      { f: "in$", max: 0.2 },
    ],
  },
  q17: {
    ...base,
    task: "A coding model I can self-host on one RTX 4090",
    bench: "swe_bench_verified",
    domain: "software_engineering",
    conds: [
      { f: "type", v: "llm" },
      { f: "active" },
      { f: "open", v: true },
      { f: "facet", facet: "model.fits_hardware", op: "in", value: ["nvidia_rtx_4090"] },
    ],
  },
  q20: {
    ...base,
    task: "A speech recognition model for transcription",
    bench: "arena_elo_style_control",
    w: { cap: 0, cost: 1, speed: 0 },
    conds: [{ f: "type", v: "speech" }, { f: "active" }],
  },
};

export const EMPTY_DECISIONS = {
  q10: decisionSchema.parse(q10Json),
  q17: decisionSchema.parse(q17Json),
  q20: decisionSchema.parse(q20Json),
};
