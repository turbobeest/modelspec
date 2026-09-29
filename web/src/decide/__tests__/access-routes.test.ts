import { describe, expect, it } from "vitest";
import anyJson from "../__fixtures__/plans-any-full.json";
import chatJson from "../__fixtures__/plans-chat-app-full.json";
import chatUnverifiedJson from "../__fixtures__/plans-chat-app-unverified-full.json";
import codingJson from "../__fixtures__/plans-coding-full.json";
import codingUnverifiedJson from "../__fixtures__/plans-coding-unverified-full.json";
import ownHardwareJson from "../__fixtures__/plans-own-hardware-full.json";
import ownSoftwareJson from "../__fixtures__/plans-own-software-full.json";
import { decisionSchema } from "../adapter/contract";
import type { Decision } from "../adapter/contract";
import {
  ACCESS_ANSWERS, estateAsDecision, estateRouteView, mayQualifyNote, modelRoutes, offeringKey,
  ownSoftwareNote, payee, plansExcludingOwnSoftware,
} from "../facet-board/routes";
import type { AccessAnswer, HeldEstate, RouteContext } from "../facet-board/routes";
import { planVocabulary } from "./plan-vocabulary";

// MODEL-202. The fixtures are the engine's answers on tests/plan_records.py's
// catalogue (tests/test_decide_page_fixtures.py writes them): a Max 20x holder
// asking each of the board's five "How will you use it?" answers.
const ctx: RouteContext = { vocabulary: planVocabulary };
const MAX = "anthropic/subscription/max-20x";
const OPUS = "anthropic/claude-opus-5-5";
const SONNET = "anthropic/claude-sonnet-5";
const holdsMax: HeldEstate = { providers: [], plans: [MAX], hardware: [] };

const parse = (json: unknown): Decision => decisionSchema.parse(json);
const routes = (json: unknown, model: string, access: AccessAnswer) =>
  modelRoutes(ctx, parse(json).results.filter((result) => result.offering.model === model), access);
const summary = (json: unknown, model: string, access: AccessAnswer) =>
  routes(json, model, access).map(({ name, figure }) => [name, figure]);

const FIXTURES: Record<string, [unknown, AccessAnswer]> = {
  "coding tool": [codingJson, "coding_tool"],
  "coding tool, coverage unverified": [codingUnverifiedJson, "coding_tool"],
  "chat app": [chatJson, "chat_app"],
  "chat app, coverage unverified": [chatUnverifiedJson, "chat_app"],
  "own software": [ownSoftwareJson, "own_software"],
  "own hardware": [ownHardwareJson, "own_hardware"],
  "doesn't matter": [anyJson, "any"],
};

it("asks one question with the five answers", () => {
  expect(ACCESS_ANSWERS.map((answer) => [answer.id, answer.label])).toEqual([
    ["chat_app", "In a chat app"],
    ["coding_tool", "In a coding tool"],
    ["own_software", "From my own software or agent"],
    ["own_hardware", "On my own hardware"],
    ["any", "Doesn't matter"],
  ]);
});

describe("the Max 20x example", () => {
  it("in a coding tool: pay per use and the plan, with the engine's break-even", () => {
    const [anthropic, bedrock, max] = routes(codingJson, OPUS, "coding_tool");
    expect([anthropic, bedrock, max].map(({ name, figure }) => [name, figure])).toEqual([
      ["Anthropic · pay per use", "$0.660 per task"],
      ["Amazon Bedrock · pay per use", "$0.792 per task"],
      ["Claude Max 20x · monthly plan", "$200 a month"],
    ]);
    // 200 USD / 0.66 USD per task, as the engine computed it (303.0).
    expect(max.note).toBe(
      "Claude Max 20x costs less than pay per use above ~303 tasks a month, if its allowance covers your volume (not published).",
    );
    expect(anthropic.note).toBeUndefined();
  });

  it("in a coding tool, each plan's break-even is its own engine figure", () => {
    const notes = routes(codingJson, SONNET, "coding_tool").flatMap((route) => route.note ? [route.note] : []);
    expect(notes).toEqual([
      "Claude Pro costs less than pay per use above ~152 tasks a month, if its allowance covers your volume (not published).",
      "Claude Max 20x costs less than pay per use above ~1,515 tasks a month, if its allowance covers your volume (not published).",
    ]);
  });

  it("in a chat app: monthly plans only, priced by the month", () => {
    expect(summary(chatJson, SONNET, "chat_app")).toEqual([
      ["Claude Pro · monthly plan", "$20 a month"],
      ["Claude Max 20x · monthly plan", "$200 a month"],
    ]);
    expect(summary(chatJson, OPUS, "chat_app")).toEqual([["Claude Max 20x · monthly plan", "$200 a month"]]);
  });

  it("from your own software: pay per use per task, and the held plan doesn't cover it", () => {
    expect(summary(ownSoftwareJson, OPUS, "own_software")).toEqual([
      ["Anthropic · pay per use", "$0.660 per task"],
      ["Amazon Bedrock · pay per use", "$0.792 per task"],
    ]);
    const excluded = plansExcludingOwnSoftware(ctx, parse(ownSoftwareJson), holdsMax);
    expect(excluded.map((plan) => plan.id)).toEqual([MAX]);
    expect(ownSoftwareNote(excluded[0])).toBe(
      "Your Claude Max 20x doesn't cover this: it works in chat apps and Claude Code, not your own software.",
    );
    // A coding-tool answer raises no such warning, so no note.
    expect(plansExcludingOwnSoftware(ctx, parse(codingJson), holdsMax)).toEqual([]);
  });

  it("with what you have: the held plan reaches Opus at no cost per task", () => {
    const decision = parse(codingJson);
    const estate = estateAsDecision(decision)!;
    expect(estate.decision.results.map((result) => [result.rank, result.offering.model])).toEqual([
      [1, OPUS], [2, SONNET],
    ]);
    const opus = estate.decision.results[0];
    const view = estateRouteView(ctx, estate.marks.get(offeringKey(opus.offering))!, opus, opus.offering);
    expect([view.name, view.figure]).toEqual(["Claude Max 20x · monthly plan", "included in your plan"]);
    expect(view.explain).toContain("covers “Opus and Sonnet models”");
    // The estate answer keeps the unrestricted row's evidence, not a blank row.
    expect(opus.contributions).toEqual(
      decision.results.find((result) => offeringKey(result.offering) === offeringKey(opus.offering))!.contributions,
    );
  });
});

it("own hardware: run it yourself, and on the device you hold", () => {
  expect(summary(ownHardwareJson, "acme/tiny", "own_hardware")).toEqual([["Run it yourself", "fit published"]]);
  const estate = estateAsDecision(parse(ownHardwareJson))!;
  const row = estate.decision.results[0];
  expect(estateRouteView(ctx, estate.marks.get(offeringKey(row.offering))!, row, row.offering).figure)
    .toBe("on your Apple M3 Max");
  expect(mayQualifyNote(ctx, parse(ownHardwareJson).may_qualify[0], { providers: [], plans: [], hardware: ["apple_m3_max"] }))
    .toBe("Whether it fits your Apple M3 Max isn't published yet.");
});

it("doesn't matter: the cheapest route per model, its type named", () => {
  expect(summary(anyJson, OPUS, "any")).toEqual([["Anthropic · pay per use", "$0.660 per task"]]);
  expect(summary(anyJson, "acme/tiny", "any")).toEqual([["Run it yourself", "no per-task fee"]]);
});

describe("today's catalogue, where no plan's coverage is verified", () => {
  it("says a held plan may cover a row, and that the coverage isn't verified", () => {
    const decision = parse(chatUnverifiedJson);
    expect(decision.results).toEqual([]);
    const notes = decision.may_qualify.map((row) => [row.model, mayQualifyNote(ctx, row, holdsMax)]);
    expect(notes).toEqual([
      [OPUS, "Your Claude Max 20x may cover this; Anthropic's coverage isn't verified yet."],
      [SONNET, "Your Claude Max 20x may cover this; Anthropic's coverage isn't verified yet."],
      ["other/huge", "A monthly plan from OpenAI may cover this; OpenAI's coverage and where its plans work aren't verified yet."],
    ]);
  });

  it("in a coding tool, pay per use ranks and no unverified plan is priced", () => {
    expect(summary(codingUnverifiedJson, OPUS, "coding_tool")).toEqual([
      ["Anthropic · pay per use", "$0.660 per task"],
      ["Amazon Bedrock · pay per use", "$0.792 per task"],
    ]);
    const estate = estateAsDecision(parse(codingUnverifiedJson))!;
    expect(estate.decision.may_qualify.map((row) => mayQualifyNote(ctx, row, holdsMax))).toEqual([
      "Your Claude Max 20x may cover this; Anthropic's coverage isn't verified yet.",
      "Your Claude Max 20x may cover this; Anthropic's coverage isn't verified yet.",
    ]);
  });
});

it.each(Object.entries(FIXTURES))("never names a route \"API\" (%s)", (_, [json, access]) => {
  const decision = parse(json);
  const models = [...new Set(decision.results.map((result) => result.offering.model))];
  const views = models.flatMap((model) => routes(json, model, access));
  const estate = estateAsDecision(decision)!;
  views.push(...estate.decision.results.map((result) =>
    estateRouteView(ctx, estate.marks.get(offeringKey(result.offering))!, result, result.offering)));
  for (const view of views) {
    expect(view.name).toMatch(/ · pay per use$| · monthly plan$|^Run it yourself$/);
    if (view.kind !== "plan") expect(view.name).not.toMatch(/\bAPI\b/);
  }
});

it("drops API from a provider's display name, and only that word", () => {
  expect(payee("Anthropic API")).toBe("Anthropic");
  expect(payee("Gemini API (Google AI Studio)")).toBe("Gemini (Google AI Studio)");
  expect(payee("MiniMax API Platform")).toBe("MiniMax Platform");
  expect(payee("Amazon Bedrock")).toBe("Amazon Bedrock");
});

it("explains each route in one line", () => {
  const [anthropic, , max] = routes(codingJson, OPUS, "coding_tool");
  expect(anthropic.explain).toBe(
    "Billed per call by Anthropic: what your software, or a tool using your own key, pays for Claude Opus 5.5. Not covered by Claude Max 20x or Claude Pro.",
  );
  expect(max.explain).toBe("A flat fee each month. Works in chat apps and Claude Code; not your own software.");
  expect(routes(ownHardwareJson, "acme/tiny", "own_hardware")[0].explain).toBe(
    "Download the open weights and run them on hardware you control; no per-task fee.",
  );
});
