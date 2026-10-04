import { createRequire } from "node:module";
import { act, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, it, vi } from "vitest";
import App from "../App";
import { decisionSpecSchema } from "../adapter/contract";
import { AgentHandoff, AnswerAssurances } from "../components/AgentHandoff";
import { encodeBoardSpec, type BoardSelections } from "../facet-board/model";
import { realBaseSpec, vocabularySchema } from "../vocabulary";
import vocabularyJson from "../__fixtures__/live-vocabulary.json";
import { handoffData, handoffMessage } from "../handoff-data";
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

const ORIENT = "uvx --from modelspec-dev modelspec help agent";
const PREFIX = `Run \`${ORIENT}\`, then decide with this spec:\n\n`;

function specFromMessage(message: string): unknown {
  expect(message.startsWith(PREFIX)).toBe(true);
  return JSON.parse(message.slice(PREFIX.length));
}

it.each(boards)("shows the exact API Spec and copies one hand-off message for the $name", async ({ selections }) => {
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
  await user.click(within(card).getByRole("button", { name: "Spec" }));
  const shown = within(card).getByLabelText("Spec snippet").textContent ?? "";
  const spec: unknown = JSON.parse(shown);
  expect(decisionSpecSchema.safeParse(spec).success).toBe(true);
  expect(spec).toEqual(sentSpecs(fetch).find((sent) => sent.explain === "summary"));
  expect(shown).toBe(JSON.stringify(spec, null, 2));
  await user.click(within(card).getByRole("button", { name: "Copy for my agent" }));
  const message = clipboard.mock.lastCall?.[0] ?? "";
  expect(message).toBe(`${PREFIX}${shown}`);
  expect(specFromMessage(message)).toEqual(spec);
  expect(within(card).getByRole("status")).toHaveTextContent("Hand-off copied for your agent.");
  expect(within(card).getByRole("status")).toHaveAttribute("aria-live", "polite");
  expect(within(card).getByRole("status")).toHaveAttribute("aria-atomic", "true");
  const price = screen.getByText(/^Your agent gets this answer from/).closest(".answer-assurances") as HTMLElement;
  await user.click(within(price).getByRole("button", { name: "Copy for my agent" }));
  expect(clipboard).toHaveBeenLastCalledWith(message);
  expect(within(price).getByRole("status")).toHaveTextContent("Hand-off copied for your agent.");
});

it("never sends task_type the board did not ask for", async () => {
  const fetch = liveFetch();
  render(<App />);
  await screen.findByRole("region", { name: "Give this to my agent" });
  const sent = sentSpecs(fetch).find((spec) => spec.explain === "summary");
  expect(sent).toBeDefined();
  expect(sent).not.toHaveProperty("task_type");
});

it("follows current edits and removes the previous board's copy confirmation", async () => {
  const user = userEvent.setup();
  const clipboard = vi.spyOn(navigator.clipboard, "writeText").mockResolvedValue();
  const fetch = liveFetch();
  render(<App />);
  const card = await screen.findByRole("region", { name: "Give this to my agent" });
  await user.click(within(card).getByRole("button", { name: "Spec" }));
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
  expect(clipboard).toHaveBeenLastCalledWith(`${PREFIX}${current}`);
});

const sampleSpec = decisionSpecSchema.parse({
  spec_version: 1, snapshot: "latest", where: [], optimize: { weights: { "-offering.cost_per_task": 1 } }, explain: "summary",
});

it("leads with the CLI, then MCP, Spec and keyed curl, all reachable by keyboard", async () => {
  const user = userEvent.setup();
  const clipboard = vi.spyOn(navigator.clipboard, "writeText").mockResolvedValue();
  render(<AgentHandoff spec={sampleSpec} />);
  const formats = within(screen.getByRole("group", { name: "Agent snippet format" })).getAllByRole("button");
  expect(formats.map((button) => button.textContent)).toEqual(["CLI", "MCP", "Spec", "curl"]);
  expect(screen.getByRole("button", { name: "CLI" })).toHaveAttribute("aria-pressed", "true");
  expect(screen.getByLabelText("CLI snippet").textContent).toBe(
    `${ORIENT}\nuvx --from modelspec-dev modelspec decide --spec spec.json`);
  await user.tab();
  expect(screen.getByRole("button", { name: "CLI" })).toHaveFocus();
  await user.tab();
  expect(screen.getByRole("button", { name: "MCP" })).toHaveFocus();
  await user.keyboard("{Enter}");
  expect(screen.getByLabelText("MCP snippet").textContent).toBe("uvx --from modelspec-dev modelspec setup mcp --client claude-code");
  const client = screen.getByRole("combobox", { name: "MCP client" });
  expect(client).toHaveAccessibleDescription("Prints the config for that client.");
  expect(within(client).getAllByRole("option").map((option) => option.textContent)).toEqual(handoffData.mcp_clients);
  await user.selectOptions(client, "codex");
  expect(screen.getByLabelText("MCP snippet").textContent).toBe("uvx --from modelspec-dev modelspec setup mcp --client codex");
  expect(screen.getByRole("region")).not.toHaveTextContent("mcpServers");
  await user.click(screen.getByRole("button", { name: "curl" }));
  expect(screen.getByLabelText("curl snippet").textContent).toBe('curl -X POST https://api.modelspec.dev/v1/decide -H "Authorization: Bearer $MODELSPEC_API_KEY" -H "content-type: application/json" -d @spec.json');
  await user.click(screen.getByRole("button", { name: "Copy curl" }));
  expect(clipboard).toHaveBeenLastCalledWith(screen.getByLabelText("curl snippet").textContent);
  expect(screen.getByRole("status")).toHaveTextContent("curl copied.");
  screen.getByLabelText("curl snippet").focus();
  await user.tab();
  expect(screen.getByRole("button", { name: "Copy for my agent" })).toHaveFocus();
  await user.keyboard("{Enter}");
  expect(clipboard).toHaveBeenLastCalledWith(handoffMessage(sampleSpec));
  expect(screen.getByRole("status")).toHaveTextContent("Hand-off copied for your agent.");
  // The button itself confirms; the status line is for screen readers only.
  expect(screen.getByRole("button", { name: "Copied ✓" })).toHaveFocus();
  expect(screen.getByRole("status")).toHaveClass("template-sr");
  await user.tab();
  expect(screen.getByRole("button", { name: "Copy curl" })).toHaveClass("text-button");
  await user.tab();
  expect(screen.getByRole("link", { name: handoffData.key_link.label })).toHaveFocus();
  expect(screen.getByText(/covers keys, MCP and curl/)).toHaveTextContent(
    "Paste it into your agent; modelspec help agent covers keys, MCP and curl.");
});

it("announces clipboard failure and clears it when another snippet is selected", async () => {
  const user = userEvent.setup();
  vi.spyOn(navigator.clipboard, "writeText").mockRejectedValue(new Error("denied"));
  render(<AgentHandoff spec={sampleSpec} />);
  await user.click(screen.getByRole("button", { name: "Copy for my agent" }));
  expect(screen.getByRole("status")).toHaveTextContent("Could not copy. Select the CLI and Spec snippets and copy them.");
  await user.click(screen.getByRole("button", { name: "curl" }));
  expect(screen.getByRole("status")).toBeEmptyDOMElement();
});

it("renders the built price, explanation credits, neutrality excerpt and flag-aware key link", () => {
  render(<><AnswerAssurances spec={sampleSpec} /><AgentHandoff spec={sampleSpec} /></>);
  expect(screen.getByText(`Your agent gets this answer from ${handoffData.summary_price_cents}¢`)).toBeInTheDocument();
  expect(screen.getByText(`A full explanation costs ${handoffData.full_credits} credits.`)).toBeInTheDocument();
  expect(screen.getByRole("link", { name: `${handoffData.neutrality.text} · sourced` })).toHaveAttribute("href", handoffData.neutrality.href);
  const key = screen.getByRole("link", { name: handoffData.key_link.label });
  expect(key).toHaveAttribute("href", handoffData.key_link.href);
  expect(key).toHaveAccessibleDescription(handoffData.key_link.note);
  expect(screen.getAllByRole("button", { name: "Copy for my agent" })).toHaveLength(2);
});

it("confirms a copy on the price-line button for two seconds", async () => {
  vi.useFakeTimers();
  vi.spyOn(navigator.clipboard, "writeText").mockResolvedValue();
  render(<AnswerAssurances spec={sampleSpec} />);
  await act(async () => { fireEvent.click(screen.getByRole("button", { name: "Copy for my agent" })); });
  expect(screen.getByRole("button", { name: "Copied ✓" })).toBeInTheDocument();
  expect(screen.getByRole("status")).toHaveClass("template-sr");
  act(() => { vi.advanceTimersByTime(2000); });
  expect(screen.getByRole("button", { name: "Copy for my agent" })).toBeInTheDocument();
  vi.useRealTimers();
});
