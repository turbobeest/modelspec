import { describe, expect, it } from "vitest";
import { priceStaleLabel } from "../adapter/staleness";

const today = new Date("2026-11-21T10:00:00Z");
const ago = (days: number) => new Date(today.getTime() - days * 86_400_000).toISOString().slice(0, 10);

describe("price stale label", () => {
  it("shows at 46 days, not at 45, with the exact text", () => {
    expect(priceStaleLabel(ago(45), today)).toBeNull();
    expect(priceStaleLabel(ago(46), today)).toBe(`Last checked ${ago(46)}, may be out of date`);
  });
  it("shows nothing without a date", () => {
    expect(priceStaleLabel(undefined, today)).toBeNull();
    expect(priceStaleLabel("not a day", today)).toBeNull();
  });
});
