// Jamie, 2026-09-25: coding tasks rank on SWE-bench Pro by default. The
// vocabulary publishes the registry's default per domain; the page prefers it
// over the most-covered rule, and says so in the parse trace.
import { describe, expect, it } from "vitest";
import { pickBenchmark, realTemplates, type Vocabulary } from "../vocabulary";
import { realVocabulary } from "./vocab-fixtures";

function withDefault(v: Vocabulary, domain: string, benchmark: string | null): Vocabulary {
  return {
    ...v,
    domains: v.domains.map((d) => (d.id === domain ? { ...d, default_benchmark: benchmark } : d)),
  };
}

describe("default benchmark per domain", () => {
  const offered = realVocabulary.benchmarks.filter((b) =>
    b.domains.some((t) => t.id === "software_engineering" && t.directness === "direct"),
  );

  it("ranks on the published default when it is offered", () => {
    const target = offered[offered.length - 1];
    const v = withDefault(realVocabulary, "software_engineering", target.id);
    expect(pickBenchmark(v, "software_engineering")?.id).toBe(target.id);
  });

  it("falls back to the most-covered direct benchmark without a default", () => {
    const v = withDefault(realVocabulary, "software_engineering", null);
    const expected = [...offered].sort((a, b) => b.models - a.models || a.id.localeCompare(b.id))[0];
    expect(pickBenchmark(v, "software_engineering")?.id).toBe(expected.id);
  });

  it("ignores a default that has no verified data in the vocabulary", () => {
    const v = withDefault(realVocabulary, "software_engineering", "no_such_benchmark");
    expect(pickBenchmark(v, "software_engineering")?.id).not.toBe("no_such_benchmark");
  });
});

describe("templates", () => {
  it("ranks the self-hosted assistant on chat preference, not on the coding default", () => {
    const t = realTemplates(realVocabulary).find((x) => x.id === "private");
    expect(t?.spec.domain).toBe("chat_preference");
    expect(t?.spec.bench).toBe("arena_elo_style_control");
  });
});
