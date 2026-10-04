import { act, fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { DesignedApp } from "../App";
import captures from "../__fixtures__/live-decision-requests.json";
import vocabulary from "../__fixtures__/live-vocabulary.json";
import { decisionSchema } from "../adapter";
import { json, routeFetch, sentSpecs } from "./vocab-fixtures";

const { decisionFixtureFor }: typeof import("../../../scripts/decision-fixtures.mjs") =
  createRequire(`${process.cwd()}/package.json`)("./scripts/decision-fixtures.mjs");

it.each(captures)("returns the captured answer for $file", ({ spec, file }) => {
  const expected = readFileSync(`src/decide/__fixtures__/${file}`, "utf8");
  expect(decisionFixtureFor(spec)).toBe(expected);
  const reordered = Object.fromEntries(Object.entries(spec).reverse());
  expect(decisionFixtureFor({ ...reordered, snapshot: vocabulary.snapshot })).toBe(expected);
  const answer = decisionSchema.parse(JSON.parse(expected));
  expect(answer.contract_version).toBe("2.12");
  expect(answer.snapshot).toBe(vocabulary.snapshot);
  expect(answer.explain).toBe(spec.explain);
});

it("falls back to the current empty board for other specs, preserving explanation depth", () => {
  const assistant = captures[0].spec;
  const other = { ...assistant, where: [...assistant.where, "model.context_window >= 200000"] };
  expect(JSON.parse(decisionFixtureFor(other)).decision_id)
    .toBe(JSON.parse(readFileSync("src/decide/__fixtures__/live-empty-board-summary.json", "utf8")).decision_id);
  expect(JSON.parse(decisionFixtureFor({ ...other, explain: "full" })).decision_id)
    .toBe(JSON.parse(readFileSync("src/decide/__fixtures__/live-empty-board-full.json", "utf8")).decision_id);
});

it("draws the real assistant on opening and the current unranked answer after Clear", async () => {
  vi.useFakeTimers();
  const fetch = routeFetch({
    vocabulary: () => json(vocabulary),
    decide: (init) => json(JSON.parse(decisionFixtureFor(JSON.parse(String(init?.body))))),
  });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);
  for (let i = 0; i < 4; i++) await act(async () => { await vi.advanceTimersByTimeAsync(500); });
  expect(sentSpecs(fetch)).toEqual(captures.slice(0, 3).map((capture) => capture.spec));
  expect(screen.getByLabelText("Facet board answer")).toBeInTheDocument();
  expect(document.querySelector(".template-active")).toHaveTextContent("Starting from: General assistant, balanced");
  const status = screen.getByRole("region", { name: "Narrowing" }).querySelector('[role="status"]');
  expect(status).toHaveTextContent("24 qualify · 10 may qualify · 10 out");
  fireEvent.click(screen.getByRole("button", { name: "Clear" }));
  expect(screen.getByRole("region", { name: "Narrowing" }).querySelector('[role="status"]')).toBe(status);
  for (let i = 0; i < 4; i++) await act(async () => { await vi.advanceTimersByTimeAsync(500); });
  expect(sentSpecs(fetch).slice(3)).toEqual(captures.slice(3).map((capture) => capture.spec));
  expect(screen.getByRole("region", { name: "Narrowing" }).querySelector('[role="status"]')).toBe(status);
  expect(document.querySelector(".board-unranked")).toHaveTextContent("Not ranked yet: listed alphabetically");
  expect(document.querySelector(".template-active")).toBeNull();
  expect(status).toHaveTextContent("28 qualify · 13 may qualify · 3 out");
});

it("numbers the decision table by the engine's model rank, with no gaps (MODEL-313)", async () => {
  vi.useFakeTimers();
  vi.stubGlobal("fetch", routeFetch({
    vocabulary: () => json(vocabulary),
    decide: (init) => json(JSON.parse(decisionFixtureFor(JSON.parse(String(init?.body))))),
  }));
  render(<DesignedApp />);
  for (let i = 0; i < 4; i++) await act(async () => { await vi.advanceTimersByTimeAsync(500); });
  const table = screen.getByRole("region", { name: "Decision table" });
  const shown = [...table.querySelectorAll("tbody tr.status-qualifies td:first-child")].map((cell) => cell.textContent);
  expect(shown.length).toBeGreaterThan(5);
  expect(shown).toEqual(shown.map((_, index) => String(index + 1)));
  expect(within(table).getByRole("columnheader", { name: /#/ })).toHaveAttribute("title", "Model rank on your weights");
  vi.useRealTimers();
});
