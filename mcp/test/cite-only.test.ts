import { expect, it } from "vitest";
import { AGENT_BYTES, decideReportContent, fitDecideEnvelope } from "../src/server";

const warning = "cite_only_not_machine_verified";
const notice = "Cited, not machine-verified: some facts retain a source reference without a page copy.";

it.each(["coverage", "minimal"])("retains citation assurance through the %s size fallback", (fallback) => {
  const fitted = fitDecideEnvelope({
    origin: "https://api.modelspec.dev/v1/decide",
    status: 200,
    body: {
      contract_version: "2.14",
      status: "answered",
      answer: null,
      warnings: [warning],
      results: [{
        rank: 1,
        offering: { model: "lab/ordinary" },
        warnings: fallback === "minimal" ? ["x".repeat(20_000)] : [],
      }],
      coverage: { detail: "x".repeat(20_000) },
      summary_for_user: notice,
      must_mention: [notice],
    },
  });
  expect(fitted.body).toMatchObject({ warnings: [warning], summary_for_user: notice, must_mention: [notice] });
  expect(fitted.body).toMatchObject({ results: fallback === "minimal" ? [] : [{ rank: 1 }] });
  expect(Buffer.byteLength(JSON.stringify(fitted)) + Buffer.byteLength(decideReportContent(fitted.body).text))
    .toBeLessThanOrEqual(AGENT_BYTES);
});
