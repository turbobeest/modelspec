import { act, fireEvent, render } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { DesignedApp } from "../App";
import { DECIDE_ENDPOINT } from "../adapter/hosted";
import fixture from "../__fixtures__/full-decision.json";
import { json, realVocabulary, routeFetch, sentSpecs } from "./vocab-fixtures";
import { templateCell } from "./board-helpers";

afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); });

async function settle() {
  for (let i = 0; i < 5; i++)
    await act(async () => { await vi.advanceTimersByTimeAsync(500); });
}

it("sends only displayed variants and shares one intent for load and template apply", async () => {
  vi.useFakeTimers();
  const fetch = routeFetch({ vocabulary: () => json(realVocabulary), decide: () => json(fixture) });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);
  await settle();
  const calls = () => fetch.mock.calls.filter(([url]) => url === DECIDE_ENDPOINT);
  const ids = () => calls().map(([, init]) => new Headers(init.headers).get("x-modelspec-intent"));
  expect(sentSpecs(fetch)).toHaveLength(3);
  expect(new Set(ids()).size).toBe(1);
  expect(ids()[0]).toMatch(/^[A-Za-z0-9_-]{21}[AQgw]$/);
  const initial = ids()[0];
  const inventory = () => sentSpecs(fetch).reduce<Record<string, number>>((counts, spec) => {
    counts[spec.explain] = (counts[spec.explain] ?? 0) + 1;
    return counts;
  }, {});
  expect(inventory()).toEqual({ summary: 1, full: 2 });
  fetch.mockClear();
  fireEvent.click(templateCell(/^Coding · Budget:/));
  await settle();
  expect(sentSpecs(fetch)).toHaveLength(3);
  expect(inventory()).toEqual({ summary: 1, full: 2 });
  expect(new Set(ids()).size).toBe(1);
  expect(ids()[0]).not.toBe(initial);
}, 20_000);


it("keeps snapshot-change retries and a burst of edits within one intent", async () => {
  vi.useFakeTimers();
  let loads = 0;
  let requests = 0;
  const fetch = routeFetch({
    vocabulary: () => json({ ...realVocabulary, snapshot: loads++ ? "fresh-snapshot" : realVocabulary.snapshot }),
    decide: () => requests++ === 0
      ? json({ error: { code: "snapshot_changed", message: "Reload" } }, 409)
      : json(fixture),
  });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);
  await settle();
  const calls = () => fetch.mock.calls.filter(([url]) => url === DECIDE_ENDPOINT);
  const ids = () => new Set(calls().map(([, init]) => new Headers(init.headers).get("x-modelspec-intent")));
  expect(loads).toBe(2);
  expect(calls().length).toBe(4);
  expect(ids().size).toBe(1);
  expect(new Headers(calls()[1][1].headers).get("X-ModelSpec-Snapshot")).toBe("fresh-snapshot");
  fetch.mockClear();
  const template = templateCell(/^Coding · Budget:/);
  fireEvent.click(template);
  await act(async () => { await vi.advanceTimersByTimeAsync(100); });
  fireEvent.click(template);
  await act(async () => { await vi.advanceTimersByTimeAsync(100); });
  fireEvent.click(template);
  expect(calls()).toHaveLength(0);
  await settle();
  expect(calls()).toHaveLength(3);
  expect(ids().size).toBe(1);
}, 20_000);
