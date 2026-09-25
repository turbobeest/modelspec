import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import App from "../App";
import { DECIDE_ENDPOINT } from "../adapter";

const decision = {
  contract_version: "1.0",
  decision_id: "dec_12345678",
  snapshot: "snap_verified_1234",
  spec_hash: `sha256:${"a".repeat(64)}`,
  explain: "full",
  status: "partial",
  results: [
    {
      rank: 1,
      offering: {
        model: "lab/model-one",
        provider: "cloud-one",
        region: "us-east-1",
        tier: "enterprise",
      },
      harness: "codex-cli@1.4",
      effort: "high",
      evidence: [
        {
          domain: "software_engineering",
          items: [
            {
              benchmark: "swe_bench_pro",
              version: "1.0",
              sub_category: "rust",
              value: 61.2,
              unit: "percent",
              n: 500,
              measured_by: "independent",
              effort: "high",
              harness: "codex-cli@1.4",
              date: "2026-09-20",
              date_type: "observed",
              source: "https://example.test/board",
              source_snapshot: "sha256:source",
              directness: "direct",
            },
          ],
        },
      ],
      estimates: null,
      p_best: null,
      top3_stability: null,
      soft_penalty: 0.2,
      contributions: [
        {
          dimension: "software_engineering",
          weight: 0.7,
          value: 0.81,
          normalisation: "min-max over feasible results",
          evidence: [],
        },
      ],
      warnings: ["provisional"],
    },
  ],
  may_qualify: [
    {
      model: "lab/model-two",
      offering: null,
      unknown: ["offering.data.zero_retention"],
    },
  ],
  eliminated: {
    funnel: [
      {
        condition: "offering.price.input <= 3",
        before: 30,
        after: 12,
        may_qualify: 2,
      },
    ],
    models: [
      {
        model: "lab/model-three",
        condition: "offering.price.input <= 3",
        value: 4.5,
      },
    ],
  },
  constraint_costs: [
    {
      condition: "offering.price.input <= 3",
      admits: 4,
      gain: { software_engineering: 0.06 },
    },
  ],
  tipping_points: [
    {
      description: "Model two takes first when cost weight exceeds 0.4",
      dimension: "-offering.price.input",
      threshold: 0.4,
      new_top: "lab/model-two",
    },
  ],
  relax: ["offering.price.input <= 5"],
  warnings: ["capability_evidence_incomplete"],
};

beforeEach(() => history.replaceState(null, "", "/"));
afterEach(() => vi.unstubAllGlobals());

it("uses the real backend by default and renders every decision field without a fictional badge", async () => {
  const fetch = vi.fn().mockResolvedValue(
    new Response(JSON.stringify(decision), {
      status: 200,
      headers: { "content-type": "application/json" },
    }),
  );
  vi.stubGlobal("fetch", fetch);
  render(<App />);
  expect(screen.queryByText(/fictional/i)).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Run decision" }));
  expect(screen.getByRole("status")).toHaveTextContent("Running decision");
  expect(await screen.findAllByText("snap_verified_1234")).toHaveLength(2);
  expect(fetch).toHaveBeenCalledWith(
    DECIDE_ENDPOINT,
    expect.objectContaining({ method: "POST" }),
  );

  const result = screen.getByRole("article", { name: "Result 1: lab/model-one" });
  for (const text of [
    "cloud-one",
    "us-east-1",
    "enterprise",
    "codex-cli@1.4",
    "high",
    "software_engineering",
    "swe_bench_pro",
    "1.0",
    "rust",
    "61.2",
    "percent",
    "500",
    "independent",
    "2026-09-20",
    "observed",
    "sha256:source",
    "direct",
    "0.2",
    "0.7",
    "0.81",
    "min-max over feasible results",
    "provisional",
  ]) expect(result).toHaveTextContent(text);
  expect(within(result).getAllByText("Not available")).toHaveLength(3);

  for (const text of [
    "dec_12345678",
    `sha256:${"a".repeat(64)}`,
    "partial",
    "full",
    "lab/model-two",
    "offering.data.zero_retention",
    "lab/model-three",
    "30",
    "12",
    "4.5",
    "admits 4",
    "0.06",
    "Model two takes first when cost weight exceeds 0.4",
    "-offering.price.input",
    "lab/model-two",
    "offering.price.input <= 5",
    "capability_evidence_incomplete",
  ]) expect(screen.getAllByText(text, { exact: false }).length).toBeGreaterThan(0);
  expect(screen.getByRole("link", { name: "https://example.test/board" })).toHaveAttribute(
    "href",
    "https://example.test/board",
  );
});

it("clears an old decision before loading and leaves no stale result after an error", async () => {
  let resolveSecond: ((response: Response) => void) | undefined;
  const fetch = vi
    .fn()
    .mockResolvedValueOnce(
      new Response(JSON.stringify(decision), {
        status: 200,
        headers: { "content-type": "application/json" },
      }),
    )
    .mockImplementationOnce(
      () =>
        new Promise<Response>((resolve) => {
          resolveSecond = resolve;
        }),
    );
  vi.stubGlobal("fetch", fetch);
  render(<App />);
  fireEvent.click(screen.getByRole("button", { name: "Run decision" }));
  expect(await screen.findAllByText("snap_verified_1234")).toHaveLength(2);
  fireEvent.click(screen.getByRole("button", { name: "Run decision" }));
  expect(screen.queryAllByText("snap_verified_1234")).toHaveLength(0);
  resolveSecond?.(
    new Response(
      JSON.stringify({ error: { code: "snapshot_unavailable", message: "Try again" } }),
      { status: 503, headers: { "content-type": "application/json" } },
    ),
  );
  await waitFor(() =>
    expect(screen.getByRole("alert")).toHaveTextContent("Try again"),
  );
  expect(screen.queryByText("lab/model-one")).not.toBeInTheDocument();
});

it("keeps the fictional experience only behind demo=1", () => {
  const fetch = vi.fn();
  vi.stubGlobal("fetch", fetch);
  history.replaceState(null, "", "/?demo=1");
  render(<App />);
  expect(screen.getByText("Fictional sample data")).toBeInTheDocument();
  expect(fetch).not.toHaveBeenCalled();
});
