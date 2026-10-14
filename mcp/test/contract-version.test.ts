import { expect, it } from "vitest";
import { fitDecideEnvelope } from "../src/server";

it("uses contract 2.18 when a bounded trimmed body has neither version field", () => {
  const fitted = fitDecideEnvelope({
    origin: "https://api.modelspec.dev/v1/decide",
    status: 200,
    body: {
      representation: "bounded",
      status: "answered",
      answer: { kind: "tied", members: ["lab/a", "lab/b"] },
      results: [{ rank: 1, offering: { model: "lab/a" }, evidence: ["x".repeat(20_000)] }],
      may_qualify: [],
    },
  });

  expect(fitted.body).toMatchObject({
    representation: "bounded",
    bounded_version: "1.2",
    projects_contract: "2.18",
    status: "answered",
    answer: { kind: "tied", members: ["lab/a", "lab/b"] },
  });
  expect(Buffer.byteLength(JSON.stringify(fitted), "utf8")).toBeLessThanOrEqual(16_384);
});

it("uses contract 2.18 when empty versions reach the over-budget minimal fallback", () => {
  const fitted = fitDecideEnvelope({
    origin: "https://api.modelspec.dev/v1/decide",
    status: 200,
    body: {
      representation: "bounded",
      contract_version: "",
      projects_contract: "",
      decision_id: "d".repeat(20_000),
      status: "partial",
      answer: { kind: "tied", members: [] },
      results: [],
      may_qualify: [],
    },
  });

  expect(fitted.body).toMatchObject({
    representation: "bounded",
    bounded_version: "1.2",
    projects_contract: "2.18",
    status: "partial",
    answer: { kind: "tied", members: [] },
    explanation: { omitted: { trimmed: 2 } },
  });
  expect(Buffer.byteLength(JSON.stringify(fitted), "utf8")).toBeLessThanOrEqual(16_384);
});
