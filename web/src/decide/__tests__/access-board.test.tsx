import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import anyJson from "../__fixtures__/plans-any-full.json";
import chatUnverifiedJson from "../__fixtures__/plans-chat-app-unverified-full.json";
import codingJson from "../__fixtures__/plans-coding-full.json";
import ownHardwareJson from "../__fixtures__/plans-own-hardware-full.json";
import ownSoftwareJson from "../__fixtures__/plans-own-software-full.json";
import { DesignedApp } from "../App";
import { decodeBoardState } from "../facet-board/model";
import { decodeSpec } from "../state/spec";
import { planVocabulary } from "./plan-vocabulary";
import { json, routeFetch, sentSpecs } from "./vocab-fixtures";

// MODEL-202: the board's "How will you use it?" question and "What I already
// have", against the engine's own answers for a Claude Max 20x holder.
const MAX = "anthropic/subscription/max-20x";
const ANSWERS: Record<string, unknown> = {
  coding_tool: codingJson,
  own_software: ownSoftwareJson,
  chat_app: chatUnverifiedJson,
  own_hardware: ownHardwareJson,
};

function engine() {
  return routeFetch({
    vocabulary: () => json(planVocabulary),
    decide: (init) => {
      const body = JSON.parse(String(init?.body));
      return json(ANSWERS[body.access] ?? anyJson);
    },
  });
}

const accessRadio = (label: string) =>
  within(screen.getByRole("radiogroup", { name: "How will you use it?" }))
    .getByRole("radio", { name: new RegExp(`^${label}`) });

async function answerWith(label: string) {
  fireEvent.click(accessRadio(label));
  await waitFor(() => expect(screen.queryByText("The live answer will appear here.")).not.toBeInTheDocument());
}

const lastMain = (fetch: ReturnType<typeof engine>) =>
  sentSpecs(fetch).filter((body) => !("estate" in body)).at(-1);

beforeEach(() => {
  history.replaceState(null, "", "/decide/");
  localStorage.clear();
});
afterEach(() => vi.unstubAllGlobals());

it.each([
  ["In a chat app", "chat_app"],
  ["In a coding tool", "coding_tool"],
  ["From my own software or agent", "own_software"],
  ["On my own hardware", "own_hardware"],
] as const)("%s sets the spec's access to %s, and the link keeps it", async (label, access) => {
  const fetch = engine();
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);
  await screen.findByLabelText("Facet board answer");
  expect(accessRadio("Doesn't matter")).toBeChecked();
  expect(lastMain(fetch)).not.toHaveProperty("access");

  await answerWith(label);
  await waitFor(() => expect(lastMain(fetch)?.access).toBe(access));
  expect(accessRadio(label)).toBeChecked();
  await waitFor(() => expect(decodeSpec(location.hash)?.spec.access).toBe(access));

  await answerWith("Doesn't matter");
  await waitFor(() => expect(lastMain(fetch)).not.toHaveProperty("access"));
});

it("in a coding tool, shows pay per use, the Max 20x plan and the engine's break-even", async () => {
  const fetch = engine();
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);
  await screen.findByLabelText("Facet board answer");
  await answerWith("In a coding tool");

  await waitFor(() => expect(lastMain(fetch)?.access).toBe("coding_tool"));
  await waitFor(() => expect(screen.getAllByText("Claude Max 20x · monthly plan").length).toBeGreaterThan(0));
  const routes = screen.getByRole("list", { name: "Routes to Claude Opus 5.5" });
  const items = within(routes).getAllByRole("listitem");
  expect(items.map((item) => item.querySelector(".route-name")?.textContent)).toEqual([
    "Anthropic · pay per use", "Amazon Bedrock · pay per use", "Claude Max 20x · monthly plan",
  ]);
  const opusRow = routes.closest("li")!;
  expect(within(opusRow).getAllByText("$0.660 per task")).toHaveLength(1);
  expect(opusRow.querySelector(".board-ranked-cost")).toHaveTextContent("Pay per use$0.660 per task");
  expect(items[1]).toHaveTextContent("$0.792 per task");
  expect(items[2]).toHaveTextContent("$200 a month");
  expect(items[2]).toHaveTextContent(
    "Claude Max 20x costs less than pay per use above ~303 tasks a month, if its allowance covers your volume (not published).",
  );
  expect(within(items[0]).getByText("Anthropic · pay per use")).toHaveAccessibleDescription(
    /Billed per call by Anthropic.*Not covered by Claude Max 20x or Claude Pro\./,
  );
  expect(within(items[2]).getByText("Claude Max 20x · monthly plan")).toHaveAccessibleDescription(
    "A flat fee each month. Works in chat apps and Claude Code; not your own software.",
  );
  const answer = screen.getByLabelText("Facet board answer").closest<HTMLElement>(".board-answer")!;
  for (const name of answer.querySelectorAll(".route-name"))
    expect(name.textContent).not.toMatch(/\bAPI\b/);
});

it("from your own software, says the held Max 20x doesn't cover it", async () => {
  const fetch = engine();
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);
  await screen.findByLabelText("Facet board answer");
  await answerWith("From my own software or agent");
  fireEvent.change(screen.getByLabelText("Add plan"), { target: { value: MAX } });

  expect(await screen.findByText(
    "Your Claude Max 20x doesn't cover this: it works in chat apps and Claude Code, not your own software.",
  )).toBeInTheDocument();
  const opus = await screen.findAllByRole("list", { name: "Routes to Claude Opus 5.5" });
  expect(opus.some((list) => within(list).queryByText("Your Claude Max 20x doesn't cover this"))).toBe(true);
  expect(within(opus[0]).getAllByText(/per task$/).length).toBeGreaterThan(0);
  expect(within(opus[0]).queryByText(/a month$/)).not.toBeInTheDocument();

  const estateRequests = sentSpecs(fetch).filter((body) => "estate" in body);
  expect(estateRequests.at(-1)).toMatchObject({ access: "own_software", estate: { plans: [MAX] } });
  expect(sentSpecs(fetch).filter((body) => !("estate" in body)).every((body) => !("estate" in body))).toBe(true);
  expect(JSON.parse(localStorage.getItem("modelspec-estate-v1") ?? "{}").plans).toEqual([MAX]);
  await waitFor(() => expect(decodeBoardState(location.hash)?.estate.plans).toEqual([MAX]));
});

it("in a chat app today, says the Max 20x may cover each Claude row and that coverage isn't verified", async () => {
  localStorage.setItem("modelspec-estate-v1", JSON.stringify({ providers: [], plans: [MAX], hardware: [] }));
  vi.stubGlobal("fetch", engine());
  render(<DesignedApp />);
  await screen.findByLabelText("Facet board answer");
  await answerWith("In a chat app");

  await waitFor(() => expect(screen.getAllByText(
    "Your Claude Max 20x may cover this; Anthropic's coverage isn't verified yet.",
  ).length).toBeGreaterThanOrEqual(2));
  expect(screen.getAllByText(
    "A monthly plan from OpenAI may cover this; OpenAI's coverage and where its plans work aren't verified yet.",
  ).length).toBeGreaterThan(0);
  expect(screen.getAllByRole("heading", { name: /^May qualify — not verified yet/ }).length).toBeGreaterThan(0);
  expect(screen.getByText("With what you have")).toBeInTheDocument();
});

it("on your own hardware, runs it yourself on the device you have", async () => {
  vi.stubGlobal("fetch", engine());
  render(<DesignedApp />);
  await screen.findByLabelText("Facet board answer");
  await answerWith("On my own hardware");
  fireEvent.change(screen.getByLabelText("Add device"), { target: { value: "apple_m3_max" } });

  expect((await screen.findAllByText("on your Apple M3 Max")).length).toBeGreaterThan(0);
  expect(screen.getAllByText("Run it yourself").length).toBeGreaterThanOrEqual(2);
  expect(screen.getByRole("button", { name: "Remove Apple M3 Max" })).toBeInTheDocument();
});

it("when it doesn't matter, names the cheapest route per model", async () => {
  vi.stubGlobal("fetch", engine());
  render(<DesignedApp />);
  await screen.findByLabelText("Facet board answer");

  const opus = await screen.findByRole("list", { name: "Routes to Claude Opus 5.5" });
  expect(within(opus).getAllByRole("listitem")).toHaveLength(1);
  expect(within(opus).getByText("Anthropic · pay per use")).toBeInTheDocument();
  const opusRow = opus.closest("li")!;
  expect(within(opusRow).getAllByText("$0.660 per task")).toHaveLength(1);
  expect(opusRow.querySelector(".board-ranked-cost")).toHaveTextContent("Cheapest route$0.660 per task");
  expect(opusRow).toHaveTextContent("also via Amazon Bedrock");
  const tiny = screen.getByRole("list", { name: "Routes to acme/tiny" });
  expect(tiny).toHaveTextContent("Run it yourself");
  expect(tiny).toHaveTextContent("no per-task fee");
});
