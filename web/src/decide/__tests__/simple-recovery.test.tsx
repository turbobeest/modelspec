import { act, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import full from "../__fixtures__/live-assistant-balanced-full.json";
import vocabularyJson from "../__fixtures__/live-vocabulary.json";
import { decisionSpecSchema } from "../adapter/contract";
import { vocabularySchema, type Vocabulary } from "../vocabulary";

const vocabulary = vocabularySchema.parse(vocabularyJson);
const json = (value: unknown, status = 200) => new Response(JSON.stringify(value), { status });
const requestBody = (init?: RequestInit) => decisionSpecSchema.parse(JSON.parse(String(init?.body)));
const advance = async () => {
  await act(async () => {});
  await act(async () => { await vi.advanceTimersByTimeAsync(300); });
};
function network(load: () => Vocabulary, decide: (init?: RequestInit) => Response = () => json(full)) {
  const fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    if (String(input).endsWith("/vocabulary.json")) return json(load());
    if (String(input).endsWith("/v1/decide")) return decide(init);
    throw new Error(`Unexpected request: ${input}`);
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}
const decisions = (fetch: ReturnType<typeof network>) => fetch.mock.calls
  .filter(([url]) => String(url).endsWith("/v1/decide"))
  .map(([, init]) => requestBody(init));

beforeEach(() => { vi.resetModules(); vi.useFakeTimers(); });
afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); vi.unstubAllEnvs(); });

it("keeps an unsupported residency limit until the visitor removes it, preserving the other choices", async () => {
  let loads = 0;
  const fetch = network(() => loads++ === 0 ? vocabulary : {
    ...vocabulary,
    snapshot: "snap_region_removed",
    facets: vocabulary.facets.filter((facet) => facet.id !== "offering.region"),
  }, (init) => requestBody(init).where?.some((condition) => typeof condition === "string" && condition.startsWith("offering.region "))
    ? json({ error: { code: "snapshot_changed", message: "Reload vocabulary" } }, 409)
    : json(full));
  const { default: SimpleApp } = await import("../simple/SimpleApp");
  render(<SimpleApp />);
  await advance();
  expect(screen.getByRole("heading", { name: "These 6 are too close to call." })).toBeVisible();
  expect(decisions(fetch)).toHaveLength(2);

  fireEvent.click(screen.getByRole("button", { name: "Change" }));
  fireEvent.click(screen.getByRole("checkbox", { name: "No customer-data training" }));
  fireEvent.change(screen.getByRole("combobox", { name: "How will you use the model?" }), { target: { value: "own_software" } });
  fireEvent.click(screen.getByRole("checkbox", { name: "EU residency" }));
  await advance();

  expect(decisions(fetch)).toHaveLength(3);
  const refused = decisions(fetch)[2];
  expect(refused.where).toContain("offering.data.trains_on_customer_data = false");
  expect(refused.where?.some((condition) => typeof condition === "string" && condition.startsWith("offering.region in "))).toBe(true);
  expect(refused.access).toBe("own_software");
  expect(screen.queryByRole("region", { name: "Decision answer" })).toBeNull();
  expect(screen.getByRole("alert")).toHaveTextContent("The data changed these choices.");
  const remove = screen.getByRole("button", { name: "Remove EU residency" });
  expect(remove).toBeVisible();
  await advance();
  expect(decisions(fetch)).toHaveLength(3);

  fireEvent.click(remove);
  await advance();
  expect(decisions(fetch)).toHaveLength(5);
  for (const request of decisions(fetch).slice(3)) {
    expect(request.where?.some((condition) => typeof condition === "string" && condition.startsWith("offering.region "))).toBe(false);
    expect(request.where).toContain("offering.data.trains_on_customer_data = false");
    expect(request.access).toBe("own_software");
    expect(request.task_tokens).toEqual({ input: 40000, output: 4000 });
  }
  expect(screen.getByRole("checkbox", { name: "No customer-data training" })).toBeChecked();
  expect(screen.getByRole("combobox", { name: "How will you use the model?" })).toHaveValue("own_software");
  expect(screen.getByRole("heading", { name: "These 6 are too close to call." })).toBeVisible();
  expect(screen.queryByRole("button", { name: "Remove EU residency" })).toBeNull();
});

it("renders mutated snapshot date, available-template count and each template's task size", async () => {
  network(() => vocabulary);
  const { default: SimpleApp } = await import("../simple/SimpleApp");
  const baseline = render(<SimpleApp />);
  await advance();
  expect(screen.getByRole("link", { name: "All 28 templates" })).toBeVisible();
  expect(screen.getByText("Data date unavailable")).toBeVisible();
  expect(screen.getByText(/Task size used for these prices: 40,000 input and 4,000 output tokens/)).toBeVisible();
  baseline.unmount();

  const changed: Vocabulary = {
    ...vocabulary,
    coverage: { as_of: "2026-10-16", models: 24, verified: 24, classes: [], domains: [] },
    templates: vocabulary.templates?.filter((template) => [
      "assistant-balanced", "assistant-best", "high-volume-balanced", "coding-balanced",
    ].includes(template.id)).map((template) => ({
      ...template,
      available: template.id !== "assistant-best",
      task_tokens: template.id === "high-volume-balanced"
        ? { input: 6789, output: 456 }
        : { input: 12345, output: 321 },
    })),
  };
  const fetch = network(() => changed);
  render(<SimpleApp />);
  await advance();
  expect(screen.getByText("Data as of 2026-10-16")).toBeVisible();
  expect(screen.getByRole("link", { name: "All 3 templates" })).toHaveAttribute("href", "/decide/details/");
  expect(screen.queryByRole("link", { name: "All 28 templates" })).toBeNull();
  expect(screen.getByText(/Task size used for these prices: 12,345 input and 321 output tokens/)).toBeVisible();
  expect(decisions(fetch).map((request) => request.task_tokens)).toEqual([
    { input: 12345, output: 321 }, { input: 12345, output: 321 },
  ]);
  fireEvent.click(within(screen.getByRole("group", { name: "Choose your job" })).getByRole("button", { name: /High volume/ }));
  await advance();
  expect(screen.getByText(/Task size used for these prices: 6,789 input and 456 output tokens/)).toBeVisible();
  expect(decisions(fetch).slice(2).map((request) => request.task_tokens)).toEqual([
    { input: 6789, output: 456 }, { input: 6789, output: 456 },
  ]);
});
