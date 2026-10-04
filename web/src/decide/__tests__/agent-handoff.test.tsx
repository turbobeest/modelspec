import { createRequire } from "node:module";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, it, vi } from "vitest";
import App from "../App";
import { decisionSpecSchema } from "../adapter/contract";
import { AgentHandoff, AnswerAssurances } from "../components/AgentHandoff";
import { encodeBoardSpec, type BoardSelections } from "../facet-board/model";
import { realBaseSpec, vocabularySchema } from "../vocabulary";
import vocabularyJson from "../__fixtures__/live-vocabulary.json";
import { handoffData } from "../handoff-data";
import { json, routeFetch, sentSpecs } from "./vocab-fixtures";
import { openGroup } from "./board-helpers";

const { decisionFixtureFor }: typeof import("../../../scripts/decision-fixtures.mjs") =
  createRequire(`${process.cwd()}/package.json`)("./scripts/decision-fixtures.mjs");
const vocabulary = vocabularySchema.parse(vocabularyJson);
const boards: { name: string; selections: BoardSelections | null }[] = [
  { name: "default assistant template", selections: null },
  { name: "empty board", selections: {} },
  { name: "custom Must and Prefer board", selections: {
    "model.context_window": { mode: "must", op: ">=", value: 200000 },
    "capability.software_engineering": { mode: "prefer", weight: 0.7 },
    "offering.cost_per_task": { mode: "both", op: "<=", value: 0.25, weight: 0.3 },
  } },
  { name: "custom categorical board", selections: {
    "model.class": { mode: "must", op: "=", value: "text-generator" },
    "model.weights_openness": { mode: "must", op: "=", value: "open_weights" },
    "offering.data.zero_retention": { mode: "must", op: "=", value: true },
  } },
];

function liveFetch() {
  const fetch = routeFetch({
    vocabulary: () => json(vocabulary),
    decide: (init) => json(JSON.parse(decisionFixtureFor(JSON.parse(String(init?.body))))),
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

afterEach(() => { vi.unstubAllGlobals(); vi.restoreAllMocks(); });

it.each(boards)("shows and copies the exact API Spec for the $name", async ({ selections }) => {
  const user = userEvent.setup();
  const clipboard = vi.spyOn(navigator.clipboard, "writeText").mockResolvedValue();
  const fetch = liveFetch();
  if (selections !== null) history.replaceState(null, "", `/decide/${encodeBoardSpec(
    { ...realBaseSpec(vocabulary), conds: [], access: "own_software" }, "task$", {
      selections, mustOrder: Object.keys(selections), estate: { providers: [], plans: [], hardware: [] },
    },
  )}`);
  render(<App />);
  const card = await screen.findByRole("region", { name: "Give this to my agent" });
  const shown = within(card).getByLabelText("Spec snippet").textContent ?? "";
  const spec: unknown = JSON.parse(shown);
  expect(decisionSpecSchema.safeParse(spec).success).toBe(true);
  expect(spec).toEqual(sentSpecs(fetch).find((sent) => sent.explain === "summary"));
  expect(shown).toBe(JSON.stringify(spec, null, 2));
  await user.click(within(card).getByRole("button", { name: "Copy for my agent" }));
  expect(clipboard).toHaveBeenLastCalledWith(shown);
  expect(JSON.parse(clipboard.mock.calls[0][0])).toEqual(spec);
  expect(within(card).getByRole("status")).toHaveTextContent("Spec copied for your agent.");
  expect(within(card).getByRole("status")).toHaveAttribute("aria-live", "polite");
  expect(within(card).getByRole("status")).toHaveAttribute("aria-atomic", "true");
});

it("follows current edits and removes the previous board's copy confirmation", async () => {
  const user = userEvent.setup();
  const clipboard = vi.spyOn(navigator.clipboard, "writeText").mockResolvedValue();
  const fetch = liveFetch();
  render(<App />);
  const card = await screen.findByRole("region", { name: "Give this to my agent" });
  const oldSnippet = within(card).getByLabelText("Spec snippet").textContent;
  await user.click(within(card).getByRole("button", { name: "Copy for my agent" }));
  openGroup("Size of work");
  const facet = document.querySelector<HTMLElement>('[data-facet="model.context_window"]');
  if (!facet) throw new Error("context facet did not render");
  fireEvent.click(within(facet).getByLabelText("Must"));
  fireEvent.change(within(facet).getByLabelText("Threshold"), { target: { value: "200000" } });
  const current = within(card).getByLabelText("Spec snippet").textContent;
  expect(current).not.toBe(oldSnippet);
  expect(within(card).getByRole("status")).toBeEmptyDOMElement();
  await waitFor(() => expect(sentSpecs(fetch).filter((spec) => spec.explain === "summary")).toHaveLength(2));
  const updated = await screen.findByRole("region", { name: "Give this to my agent" });
  expect(JSON.parse(within(updated).getByLabelText("Spec snippet").textContent ?? ""))
    .toEqual(sentSpecs(fetch).filter((spec) => spec.explain === "summary").at(-1));
  await user.click(within(updated).getByRole("button", { name: "Copy for my agent" }));
  expect(clipboard).toHaveBeenLastCalledWith(current);
});

const sampleSpec = decisionSpecSchema.parse({
  spec_version: 1, snapshot: "latest", where: [], optimize: { weights: { "-offering.cost_per_task": 1 } }, explain: "summary",
});

it("lets a keyboard user toggle and copy the keyed curl and CLI snippets", async () => {
  const user = userEvent.setup();
  const clipboard = vi.spyOn(navigator.clipboard, "writeText").mockResolvedValue();
  render(<AgentHandoff spec={sampleSpec} />);
  await user.tab();
  expect(screen.getByRole("button", { name: "Spec" })).toHaveFocus();
  await user.tab();
  expect(screen.getByRole("button", { name: "curl" })).toHaveFocus();
  await user.keyboard("{Enter}");
  expect(screen.getByRole("button", { name: "curl" })).toHaveAttribute("aria-pressed", "true");
  const curl = screen.getByLabelText("curl snippet").textContent;
  expect(curl).toBe('curl -X POST https://api.modelspec.dev/v1/decide -H "Authorization: Bearer $MODELSPEC_API_KEY" -H "content-type: application/json" -d @spec.json');
  await user.tab();
  await user.keyboard(" ");
  expect(screen.getByLabelText("CLI snippet")).toHaveTextContent("uvx --from modelspec-dev modelspec decide --spec spec.json");
  await user.tab();
  expect(screen.getByLabelText("CLI snippet")).toHaveFocus();
  await user.tab();
  expect(screen.getByRole("button", { name: "Copy for my agent" })).toHaveFocus();
  await user.keyboard("{Enter}");
  expect(clipboard).toHaveBeenLastCalledWith("uvx --from modelspec-dev modelspec decide --spec spec.json");
  expect(screen.getByRole("status")).toHaveTextContent("CLI copied for your agent.");
  await user.tab();
  expect(screen.getByRole("link", { name: "Get an API key" })).toHaveFocus();
  expect(screen.getByText(/Set/)).toHaveTextContent("MODELSPEC_API_KEY");
});

it("announces clipboard failure and clears it when another snippet is selected", async () => {
  const user = userEvent.setup();
  vi.spyOn(navigator.clipboard, "writeText").mockRejectedValue(new Error("denied"));
  render(<AgentHandoff spec={sampleSpec} />);
  await user.click(screen.getByRole("button", { name: "Copy for my agent" }));
  expect(screen.getByRole("status")).toHaveTextContent("Could not copy. Select the snippet and copy it.");
  await user.click(screen.getByRole("button", { name: "curl" }));
  expect(screen.getByRole("status")).toBeEmptyDOMElement();
});

it("renders the built price, explanation credits, neutrality excerpt and flag-aware key link", () => {
  render(<><AnswerAssurances /><AgentHandoff spec={sampleSpec} /></>);
  expect(screen.getByText(`Your agent gets this answer from ${handoffData.summary_price_cents}¢`)).toBeInTheDocument();
  expect(screen.getByText(`A full explanation costs ${handoffData.full_credits} credits.`)).toBeInTheDocument();
  expect(screen.getByRole("link", { name: `${handoffData.neutrality.text} · sourced` })).toHaveAttribute("href", handoffData.neutrality.href);
  const key = screen.getByRole("link", { name: "Get an API key" });
  expect(key).toHaveAttribute("href", handoffData.key_link.href);
  expect(key).toHaveAccessibleDescription(handoffData.key_link.note);
});
