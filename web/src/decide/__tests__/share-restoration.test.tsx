import { act, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import App from "../App";
import { decisionSpecSchema, type DecisionSpec } from "../adapter/contract";
import { prepareDecisionRequest } from "../adapter/request-spec";
import { encodeBoardSpec } from "../facet-board/model";
import { defaultChoices, selectJob } from "../simple/model";
import { baseSpec, encodeSpec } from "../state/spec";
import { vocabularySchema } from "../vocabulary";
import rawVocabulary from "../__fixtures__/live-vocabulary.json";
import rawDecision from "../__fixtures__/live-assistant-balanced-full.json";

const vocabulary = vocabularySchema.parse(rawVocabulary);
const json = (value: unknown) => new Response(JSON.stringify(value));

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

function navigate(hash: string) {
  act(() => {
    history.pushState(null, "", `/decide/details/${hash}`);
    window.dispatchEvent(new HashChangeEvent("hashchange"));
  });
}

async function settle() {
  await act(async () => { await vi.advanceTimersByTimeAsync(600); });
}

async function delayedVocabulary() {
  vi.useFakeTimers();
  let release: (response: Response) => void = () => { throw new Error("Vocabulary was not requested"); };
  const response = new Promise<Response>((resolve) => { release = resolve; });
  const requests: DecisionSpec[] = [];
  vi.stubGlobal("fetch", vi.fn(async (url: string, init?: RequestInit) => {
    if (url.includes("vocabulary")) return response;
    if (init?.body) requests.push(decisionSpecSchema.parse(JSON.parse(String(init.body))));
    return json(rawDecision);
  }));
  render(<App />);
  await settle();
  return { requests, release: async () => {
    await act(async () => { release(json(rawVocabulary)); });
    await settle();
  } };
}

it("restores a board navigated to while vocabulary loads before submitting it", async () => {
  const selection = selectJob(vocabulary, { ...defaultChoices, job: "volume", route: "own_software" });
  if (!selection) throw new Error("High-volume fixture must be selectable");
  const expected = prepareDecisionRequest(vocabulary, selection.spec, "summary").decisionSpec;
  const pending = await delayedVocabulary();
  navigate(encodeBoardSpec({ ...selection.spec, task: "Refactor the billing processor" }, "task$", selection.board));
  await settle();
  expect.soft(pending.requests).toHaveLength(0);
  await pending.release();
  expect(pending.requests.filter((request) => request.explain === "summary")).toEqual([expected]);
});

it("migrates legacy navigation during vocabulary loading without interpreting task text", async () => {
  const pending = await delayedVocabulary();
  navigate(encodeSpec({ ...baseSpec, task: "Refactor the billing processor", conds: [],
    domain: "software_engineering", basis: "estimate", tokIn: 2000, tokOut: 500,
    w: { cap: 1, cost: 0, speed: 0 } }, "ctx"));
  await settle();
  expect.soft(pending.requests).toHaveLength(0);
  await pending.release();
  const summaries = pending.requests.filter((request) => request.explain === "summary");
  expect(summaries).toHaveLength(1);
  expect(summaries[0]).not.toHaveProperty("task_type");
  expect(summaries[0]).toMatchObject({ task_tokens: { input: 2000, output: 500 },
    optimize: { weights: { software_engineering: 1 } } });
  expect(screen.getByRole("note", { name: "Notes from your old decision link" }))
    .toHaveTextContent("The board does not interpret free text.");
});

it("submits only the last board when two hashes arrive before vocabulary", async () => {
  const first = selectJob(vocabulary, { ...defaultChoices, job: "coding" });
  const last = selectJob(vocabulary, { ...defaultChoices, job: "volume", route: "own_software" });
  if (!first || !last) throw new Error("Navigation fixtures must be selectable");
  const pending = await delayedVocabulary();
  navigate(encodeBoardSpec(first.spec, "task$", first.board));
  await settle();
  navigate(encodeBoardSpec(last.spec, "task$", last.board));
  await settle();
  expect.soft(pending.requests).toHaveLength(0);
  await pending.release();
  expect(pending.requests.filter((request) => request.explain === "summary"))
    .toEqual([prepareDecisionRequest(vocabulary, last.spec, "summary").decisionSpec]);
});
