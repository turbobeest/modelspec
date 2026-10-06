import { expect, it } from "vitest";

import { decisionSummary, defaultDecideRequest } from "../src/server";
import fixture from "./fixtures/default-decide-request.json";

it("defaultDecideRequest and decisionSummary match the shared Python fixture", () => {
  expect(defaultDecideRequest({ spec_version: 1 }).fields).toEqual(fixture.default_fields);
  for (const row of fixture.requests) {
    expect(defaultDecideRequest(row.spec), row.name).toEqual(row.request);
  }
  for (const row of fixture.summaries) {
    expect(decisionSummary(row.body), row.name).toBe(row.text);
  }
  const summary = fixture.requests.find((row) => row.name === "summary");
  expect(summary?.request.fields).toEqual([...fixture.default_fields, ...fixture.explain_row_fields]);
});
