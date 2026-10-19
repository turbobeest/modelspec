import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import rawVocabulary from "../__fixtures__/live-vocabulary.json";
import rawDecision from "../__fixtures__/live-assistant-balanced-full.json";
import { vocabularySchema } from "../vocabulary";
import { decisionSchema } from "../adapter/contract";
import { prepareDecisionRequest } from "../adapter/request-spec";
import { decodeBoardState, boardToSpec, sanitizeBoardState } from "../facet-board/model";
import { decodeSpec } from "../state/spec";
import { selectJob, evidenceLink, legacyDestination, defaultChoices } from "../simple/model";
import { SimpleAnswer } from "../simple/Answer";
import SimpleApp from "../simple/SimpleApp";

const vocabulary = vocabularySchema.parse(rawVocabulary);
const decision = decisionSchema.parse(rawDecision);
afterEach(() => vi.unstubAllGlobals());
function selection(overrides: Partial<typeof defaultChoices> = {}) {
  const selected = selectJob(vocabulary, { ...defaultChoices, ...overrides });
  if (!selected) throw new Error("Expected an available template");
  return selected;
}

describe("simple decision question", () => {
  it("uses existing tiers and keeps the high-volume workload", () => {
    expect(selection().template.id).toBe("assistant-balanced");
    expect(selection({ job: "coding", priority: "budget" }).template.id).toBe("budget-coding");
    const volume = selection({ job: "volume" });
    expect(volume.template.id).toBe("high-volume-balanced");
    expect(prepareDecisionRequest(vocabulary, volume.spec, "full").decisionSpec.task_tokens).toEqual({ input: 2000, output: 500 });
  });
  it("keeps self-hosting requirements at every existing priority", () => {
    for (const priority of ["budget", "balanced", "best"] as const) {
      const request = prepareDecisionRequest(vocabulary, selection({ job: "self-host", priority }).spec, "full").decisionSpec;
      expect(request.where).toContain("model.weights_openness = open_weights");
      expect(request.where).toContain("licence.commercial_use in {permitted, permitted_with_conditions}");
    }
  });
  it("keeps residency and training independent and preserves route and limits in evidence state", () => {
    const eu = selection({ limits: ["eu"], route: "own_software" });
    const request = prepareDecisionRequest(vocabulary, eu.spec, "full").decisionSpec;
    expect(request.where).toContain("offering.region in {AT, BE, BG, HR, CY, CZ, DE, DK, EE, ES, FI, FR, GR, HU, IE, IT, LT, LU, LV, MT, NL, PL, PT, RO, SE, SI, SK}");
    expect(request.where).not.toContain("offering.data.trains_on_customer_data = false");
    const combined = selection({ limits: ["eu", "no-training"], route: "own_software" });
    const link = evidenceLink(combined);
    expect(link).toMatch(/^\/decide\/details\/#s=/);
    const hash = link.slice(link.indexOf("#"));
    const decoded = decodeSpec(hash);
    const board = decodeBoardState(hash);
    if (!decoded || !board) throw new Error("Evidence state must decode");
    const sanitized = sanitizeBoardState(board, vocabulary);
    const restored = boardToSpec(decoded.spec, vocabulary, sanitized.selections, sanitized.mustOrder);
    expect(prepareDecisionRequest(vocabulary, restored, "full").decisionSpec).toEqual(prepareDecisionRequest(vocabulary, combined.spec, "full").decisionSpec);
  });
  it("redirects old state before rendering and preserves the exact query and hash", () => {
    expect(legacyDestination("?theme=light&template=coding-balanced", "#a%2Bb")).toBe("/decide/details/?theme=light&template=coding-balanced#a%2Bb");
    expect(legacyDestination("?theme=dark", "#s=abc%2Bdef")).toBe("/decide/details/?theme=dark#s=abc%2Bdef");
    expect(legacyDestination("?theme=dark", "#main")).toBeNull();
  });
  it("does not replace an unavailable tier with a different question", () => {
    const unavailable = { ...vocabulary, templates: vocabulary.templates?.filter((t) => t.id !== "coding-best") };
    expect(selectJob(unavailable, { ...defaultChoices, job: "coding", priority: "best" })).toBeNull();
  });
  it("refuses unsupported selected limits and a self-host question without its required gates", () => {
    const missingRegion = { ...vocabulary, facets: vocabulary.facets.filter((facet) => facet.id !== "offering.region") };
    expect(selectJob(missingRegion, { ...defaultChoices, limits: ["eu"] })).toBeNull();
    expect(selectJob(vocabulary, { ...defaultChoices, job: "self-host", removedFacets: ["model.weights_openness"] })).toBeNull();
  });
});

describe("simple engine answer", () => {
  const props = () => ({ vocabulary, selection: selection(), decision, onRemoveLimit: vi.fn(), onTryAllRoutes: vi.fn() });
  it("shows the whole tie alphabetically with equal rows and no winner marks", () => {
    render(<SimpleAnswer {...props()} />);
    const list = screen.getByRole("list", { name: "Best matches" });
    const rows = within(list).getAllByRole("listitem");
    expect(rows.map((row) => row.querySelector("strong")?.textContent)).toEqual([
      "Claude Opus 5.5", "Gemini 3.7 Flash", "Gemini 3.8 Flash", "GPT-6 Sol", "Grok 4.7", "Qwen3.8 Max 0902",
    ]);
    expect(new Set(rows.map((row) => row.className)).size).toBe(1);
    expect(list).not.toHaveTextContent(/chance|winner|most independently|ranked first/i);
    expect(screen.getByText("Listed alphabetically, not ranked.")).toBeVisible();
    expect(screen.getByText("ModelSpec is neutral: no referral fees, no paid placement.")).toBeVisible();
  });
  it("takes changed prices, cheapest provider, counts, source and blend from the response", () => {
    const changed = structuredClone(decision);
    const row = changed.by_model.find((item) => item.model === "anthropic/claude-opus-5-5");
    if (!row || row.offerings.length < 2) throw new Error("Need two fixture routes");
    row.offerings[1].cost_per_task = 0.012;
    changed.by_model = changed.by_model.filter((item) => item.status !== "may_qualify");
    changed.blend = changed.blend.filter((term) => term.dimension === "chat_preference");
    for (const result of changed.results) {
      for (const group of result.evidence) for (const item of group.items) item.date = "2026-10-16";
      for (const part of result.contributions) for (const item of part.evidence) item.date = "2026-10-16";
    }
    render(<SimpleAnswer {...props()} decision={changed} />);
    const claude = within(screen.getByRole("list", { name: "Best matches" })).getAllByRole("listitem")[0];
    expect(claude).toHaveTextContent("via Amazon Bedrock");
    expect(claude).toHaveTextContent("$0.012 per task");
    expect(screen.getByText(/0 more are missing a fact/)).toBeVisible();
    expect(screen.getByText(/Source:.*2026-10-16/)).toBeVisible();
    expect(screen.getByText(/This choice compares/)).not.toHaveTextContent("running cost");
  });
  it("describes a changed blend without inventing a winner or workload mix", () => {
    const { rerender } = render(<SimpleAnswer {...props()} />);
    expect(screen.getByText(/This choice compares/)).toHaveTextContent("More weight goes to ratings of conversational responses.");
    const changed = { ...decision, blend: decision.blend.map((term) => ({ ...term, share: term.dimension === "chat_preference" ? 0.2 : 0.8 })) };
    rerender(<SimpleAnswer {...props()} decision={changed} />);
    expect(screen.getByText(/This choice compares/)).toHaveTextContent("More weight goes to estimated running cost.");
  });
  it("uses retained best-band routes and directs to full evidence when member evidence is truncated", () => {
    const changed = structuredClone(decision);
    const id = "anthropic/claude-opus-5-5";
    const band = changed.bands?.best.find((row) => row.model === id);
    if (!band) throw new Error("Need best-band fixture");
    band.cost_per_task = 0.432;
    band.offering.provider = "anthropic";
    changed.by_model = changed.by_model.filter((row) => row.model !== id);
    changed.results = changed.results.filter((row) => row.offering.model !== id);
    for (const result of changed.results) result.evidence = [];
    render(<SimpleAnswer {...props()} decision={changed} />);
    const row = within(screen.getByRole("list", { name: "Best matches" })).getAllByRole("listitem")[0];
    expect(row).toHaveTextContent("via Anthropic");
    expect(row).toHaveTextContent("$0.432 per task");
    expect(screen.getByText("Sources and dates: see the full evidence")).toBeVisible();
  });
  it("keeps no-fit and undetermined answers distinct and offers the engine's blocking limit", () => {
    const remove = vi.fn();
    const empty = { ...decision, status: "no_feasible" as const, answer: null, bands: null, results: [], relax: ["offering.data.trains_on_customer_data = false"] };
    const { rerender } = render(<SimpleAnswer {...props()} selection={selection({ limits: ["no-training"] })} decision={empty} onRemoveLimit={remove} />);
    expect(screen.getByRole("heading", { name: "No confirmed match." })).toBeVisible();
    fireEvent.click(screen.getByRole("button", { name: "Remove No customer-data training" }));
    expect(remove).toHaveBeenCalledWith("offering.data.trains_on_customer_data");
    rerender(<SimpleAnswer {...props()} decision={{ ...decision, answer: null }} />);
    expect(screen.getByRole("heading", { name: "No clear pick yet." })).toBeVisible();
    expect(screen.queryByRole("list", { name: "Best matches" })).toBeNull();
    expect(screen.getByRole("link", { name: "See the full evidence" })).toHaveAttribute("href", evidenceLink(selection()));
  });
});

it("loads the labelled example and renders a picked job after request normalization", async () => {
  const requests: unknown[] = [];
  vi.stubGlobal("fetch", vi.fn(async (url: string, init?: RequestInit) => {
    if (url.includes("vocabulary")) return new Response(JSON.stringify(rawVocabulary));
    if (init?.body) requests.push(JSON.parse(String(init.body)));
    return new Response(JSON.stringify(rawDecision));
  }));
  render(<SimpleApp />);
  expect(screen.getByText("Example: Everyday help. Pick a job if this isn't yours.")).toBeVisible();
  expect(await screen.findByRole("heading", { name: "These 6 are too close to call." })).toBeVisible();
  fireEvent.click(screen.getByRole("button", { name: /^Everyday help/ }));
  expect(screen.getByRole("heading", { name: "These 6 are too close to call." })).toHaveFocus();
  fireEvent.click(screen.getByRole("button", { name: /^Coding/ }));
  await waitFor(() => expect(screen.getByRole("heading", { name: "These 6 are too close to call." })).toHaveFocus());
  expect(screen.queryByText("Example: Everyday help. Pick a job if this isn't yours.")).toBeNull();
  expect(requests).toContainEqual(expect.objectContaining({ optimize: { weights: { software_engineering: 0.7, "-offering.cost_per_task": 0.3 } } }));
});
