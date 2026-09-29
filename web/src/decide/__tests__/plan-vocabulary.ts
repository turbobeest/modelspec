// The vocabulary the page would load for tests/plan_records.py's catalogue:
// the real vocabulary's shape, with that catalogue's plans, names and devices.
import type { Vocabulary } from "../vocabulary";
import { realVocabulary } from "./vocab-fixtures";

const CLAUDE_SURFACES = ["chat_app", "coding_tool:claude-code", "desktop_app", "mobile_app"];

export const planVocabulary: Vocabulary = {
  ...realVocabulary,
  models: {
    ...realVocabulary.models,
    "anthropic/claude-sonnet-5": { display_name: "Claude Sonnet 5", lab: "anthropic", lab_name: "Anthropic" },
  },
  estate: {
    providers: ["anthropic", "aws-bedrock", "openai"],
    plans: [
      { id: "anthropic/subscription/max-20x", provider: "anthropic", name: "Claude Max 20x",
        price: { amount: 200, currency: "USD", period: "monthly" }, surfaces: CLAUDE_SURFACES },
      { id: "anthropic/subscription/pro", provider: "anthropic", name: "Claude Pro",
        price: { amount: 20, currency: "USD", period: "monthly" }, surfaces: CLAUDE_SURFACES },
      { id: "anthropic/subscription/team-api", provider: "anthropic", name: "Team API",
        price: null, surfaces: ["api"] },
      { id: "openai/subscription/plus", provider: "openai", name: "ChatGPT Plus",
        price: { amount: 20, currency: "USD", period: "monthly" }, surfaces: null },
    ],
    devices: ["apple_m3_max", "nvidia_rtx_4090"],
  },
};
