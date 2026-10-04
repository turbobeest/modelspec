import { act, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { DesignedApp } from "../App";
import { DECIDE_ENDPOINT } from "../adapter";
import { encodeBoardSpec, decodeBoardState, templateToBoard } from "../facet-board/model";
import { fastTrackTemplates, openingTemplate, templateCanvasAxes } from "../facet-board/templates";
import { realBaseSpec } from "../vocabulary";
import { json, realVocabulary, routeFetch, sentSpecs } from "./vocab-fixtures";
import decision from "../__fixtures__/live-budget-coding-full.json";

afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); });
const emptyEstate = { providers: [], plans: [], hardware: [] };
const assistant = realVocabulary.templates?.find((template) => template.id === "assistant-balanced");
if (!assistant) throw new Error("The default assistant template is missing from the catalogue fixture");

async function settle() {
  for (let i = 0; i < 4; i++) await act(async () => { await vi.advanceTimersByTimeAsync(500); });
}

it("chooses the available balanced assistant only for a fresh visit", () => {
  expect(openingTemplate(realVocabulary, false)?.id).toBe("assistant-balanced");
  expect(openingTemplate(realVocabulary, true)).toBeNull();
  expect(openingTemplate({ ...realVocabulary, templates: [] }, false)).toBeNull();
  expect(openingTemplate({ ...realVocabulary, templates: realVocabulary.templates?.map((template) => ({ ...template, available: false })) }, false)).toBeNull();
});

it("selects four balanced jobs, budget volume and private assistant, in that order", () => {
  expect(fastTrackTemplates(realVocabulary).map((template) => template.id)).toEqual([
    "assistant-balanced", "coding-balanced", "writing-balanced", "long-documents", "high-volume", "private-self-host",
  ]);
  expect(fastTrackTemplates({ ...realVocabulary, templates: realVocabulary.templates?.map((template) => ({ ...template, available: template.id !== "writing-balanced" && template.available })) }).map((template) => template.id))
    .toEqual(["assistant-balanced", "coding-balanced", "long-documents", "high-volume", "private-self-host"]);
});

it("opens ranked templates on their capability and task cost without changing their specs", () => {
  for (const template of realVocabulary.templates?.filter((row) => row.available) ?? []) {
    expect(templateCanvasAxes(template, realVocabulary)?.x, template.id).toBe("facet:offering.cost_per_task");
    expect(templateCanvasAxes(template, realVocabulary)?.y, template.id).toMatch(/^capability:/);
  }
});

it("applies and labels the default before the normal three requests, then clears it", async () => {
  vi.useFakeTimers();
  const fetch = routeFetch({ vocabulary: () => json(realVocabulary), decide: () => json(decision) });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);
  await settle();
  expect(document.querySelector(".template-active")).toHaveTextContent("Starting from: General assistant, balanced");
  expect(screen.getByRole("button", { name: /^General assistant, balanced/ })).toHaveAttribute("aria-pressed", "true");
  const requests = sentSpecs(fetch);
  expect(requests).toHaveLength(3);
  expect(requests[0]).toMatchObject({ explain: "summary", where: assistant.spec.where, optimize: assistant.spec.optimize });
  expect(requests[1]).toMatchObject({ explain: "full", where: assistant.spec.where, optimize: assistant.spec.optimize });
  const intents = fetch.mock.calls.filter(([url]) => url === DECIDE_ENDPOINT).map(([, init]) => new Headers(init.headers).get("x-modelspec-intent"));
  expect(new Set(intents).size).toBe(1);
  expect(screen.getByLabelText("X axis")).toHaveValue("facet:offering.cost_per_task");
  expect(screen.getByLabelText("Y axis")).toHaveValue("capability:chat_preference");
  expect(screen.getByText("Up and left is better")).toBeInTheDocument();
  const templates = document.querySelector(".template-picker");
  // MODEL-325: the answer, led by its counter, follows the templates directly.
  expect(templates?.nextElementSibling).toHaveClass("answer-block");
  expect(templates?.nextElementSibling?.querySelector(".answer-region .board-answer > :first-child")).toHaveAttribute("aria-label", "Narrowing");
  expect(screen.getByRole("button", { name: /^General assistant, balanced/ }).querySelector(".template-check")).toHaveTextContent("✓");
  expect(screen.queryByRole("region", { name: "Was this answer reliable?" })).not.toBeInTheDocument();

  fireEvent.click(screen.getByRole("button", { name: "Clear" }));
  await settle();
  expect(decodeBoardState(location.hash)?.selections).toEqual({});
  expect(document.querySelector(".template-active")).not.toBeInTheDocument();
  expect(sentSpecs(fetch).filter((spec) => spec.explain === "summary").at(-1)).toMatchObject({ where: [], optimize: { weights: { "-offering.cost_per_task": 1 } } });
  expect(within(screen.getByRole("region", { name: "Decision table" })).getByText("Not ranked yet: listed alphabetically")).toBeInTheDocument();
});

it.each(["empty", "coding"] as const)("restores a saved %s board instead of the assistant default", async (kind) => {
  vi.useFakeTimers();
  const coding = realVocabulary.templates?.find((template) => template.id === "coding-balanced");
  if (!coding) throw new Error("The coding template is missing");
  const converted = kind === "empty" ? { selections: {}, mustOrder: [] } : templateToBoard(coding, realVocabulary);
  const hash = encodeBoardSpec({ ...realBaseSpec(realVocabulary), conds: [] }, "task$", {
    ...converted, estate: emptyEstate, canvas: { x: "facet:model.context_window", y: "capability:software_engineering" },
  });
  history.replaceState(null, "", `/decide/${hash}`);
  const fetch = routeFetch({ vocabulary: () => json(realVocabulary), decide: () => json(decision) });
  vi.stubGlobal("fetch", fetch);
  const app = render(<DesignedApp />);
  await settle();
  expect(document.querySelector(".template-active")).not.toBeInTheDocument();
  expect(sentSpecs(fetch)[0]).toMatchObject(kind === "empty"
    ? { where: [], optimize: { weights: { "-offering.cost_per_task": 1 } } }
    : { where: coding.spec.where, optimize: coding.spec.optimize });
  expect(screen.getByLabelText("X axis")).toHaveValue("facet:model.context_window");
  expect(screen.getByLabelText("Y axis")).toHaveValue("capability:software_engineering");
  const saved = location.hash;
  app.unmount();
  render(<DesignedApp />);
  await settle();
  expect(location.hash).toBe(saved);
  expect(document.querySelector(".template-active")).not.toBeInTheDocument();
});
