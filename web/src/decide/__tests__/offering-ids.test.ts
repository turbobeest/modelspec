import { expect, it } from "vitest";
import { decisionSchema } from "../adapter/contract";
import decisionFixture from "../__fixtures__/compact-tied-full.json";

it("retains the provider API model ID and separate OpenRouter slug in a 2.17 decision", () => {
  const offerings = decisionFixture.results.map((result) => ({
    ...result.offering,
    api_model_id: "provider-model-id",
    router_slug: "lab/openrouter-slug",
  }));
  const decision = decisionSchema.parse({
    ...decisionFixture,
    contract_version: "2.17",
    results: decisionFixture.results.map((result, index) => ({
      ...result,
      offering: offerings[index],
    })),
  });

  expect(decision.contract_version).toBe("2.17");
  expect(decision.results.map((result) => result.offering)).toEqual(offerings);
});

it("accepts null offering identifiers in a 2.17 decision", () => {
  const decision = decisionSchema.parse({
    ...decisionFixture,
    contract_version: "2.17",
    results: decisionFixture.results.map((result) => ({
      ...result,
      offering: { ...result.offering, api_model_id: null, router_slug: null },
    })),
  });

  expect(decision.results.map((result) => ({
    api_model_id: result.offering.api_model_id,
    router_slug: result.offering.router_slug,
  }))).toEqual(decisionFixture.results.map(() => ({
    api_model_id: null,
    router_slug: null,
  })));
});

it.each(["1.12", "2.16"])("keeps a saved %s decision without offering identifiers readable", (version) => {
  const decision = decisionSchema.parse({ ...decisionFixture, contract_version: version });

  expect(decision.contract_version).toBe(version);
  expect(decision.results.map((result) => result.offering)).toEqual(
    decisionFixture.results.map((result) => result.offering),
  );
  for (const result of decision.results) {
    expect(result.offering).not.toHaveProperty("api_model_id");
    expect(result.offering).not.toHaveProperty("router_slug");
  }
});
