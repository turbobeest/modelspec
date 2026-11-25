import { afterEach, expect, it, vi } from "vitest";
import compactJson from "../__fixtures__/compact-full.json";
import { hostedEngine } from "../adapter";
import { decisionSchema } from "../adapter/contract";

const spec = {
  spec_version: 1 as const,
  snapshot: "latest" as const,
  task_type: "refactor" as const,
  where: ["model.class = text-generator"],
  optimize: { min: "offering.price.input" },
  explain: "full" as const,
};

function serve(body: unknown) {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValueOnce(
      new Response(JSON.stringify(body), { status: 200, headers: { "content-type": "application/json" } }),
    ),
  );
}

afterEach(() => vi.unstubAllGlobals());

it("renders a 2.99 response that carries unknown optional keys at the top and nested", async () => {
  const withUnknown = {
    ...compactJson,
    contract_version: "2.99",
    future_top_level: { anything: true },
    results: compactJson.results.map((row, i) => (i === 0 ? { ...row, future_row_field: 1 } : row)),
  };
  serve(withUnknown);
  const decision = await hostedEngine.decide(spec);
  expect(decision.contract_version).toBe("2.99");
  expect(decision.results.length).toBe(compactJson.results.length);
});

it("renders the lowest accepted 2.x minor", () => {
  const decision = decisionSchema.parse({ ...compactJson, contract_version: "2.0" });
  expect(decision.contract_version).toBe("2.0");
});

it.each(["3.0", "3.4", "0.9", "2", "2.", "2.x", "2.01", "2.1.1", "12.1"])(
  "rejects %s through the invalid response path",
  async (version) => {
    expect(decisionSchema.safeParse({ ...compactJson, contract_version: version }).success).toBe(false);
    serve({ ...compactJson, contract_version: version });
    await expect(hostedEngine.decide(spec)).rejects.toMatchObject({ code: "invalid_response" });
  },
);
