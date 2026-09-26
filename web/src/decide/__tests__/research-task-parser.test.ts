import { readFile, writeFile } from "node:fs/promises";
import { describe, expect, it } from "vitest";
import { parseRealTask, vocabularySchema } from "../vocabulary";

type Input = Readonly<{
  vocabulary: string;
  tasks: readonly Readonly<{ id: string; text: string }>[];
}>;

function isInput(value: unknown): value is Input {
  if (typeof value !== "object" || value === null) return false;
  if (!("vocabulary" in value) || typeof value.vocabulary !== "string") return false;
  if (!("tasks" in value) || !Array.isArray(value.tasks)) return false;
  return value.tasks.every(
    (task) =>
      typeof task === "object" &&
      task !== null &&
      "id" in task &&
      typeof task.id === "string" &&
      "text" in task &&
      typeof task.text === "string",
  );
}

function conditionNames(conds: ReturnType<typeof parseRealTask>["conds"]): string[] {
  const names = new Set<string>();
  for (const condition of conds) {
    switch (condition.f) {
      case "ctx":
        names.add("context_200k");
        break;
      case "open":
        if (condition.v) names.add("open_weights");
        break;
      case "commercial":
        names.add("commercial_use");
        break;
      case "ttft":
        names.add("low_latency");
        break;
      default:
        break;
    }
  }
  return [...names].sort();
}

const inputPath = process.env.MODELSPEC_JEV_TASK_INPUT;
const outputPath = process.env.MODELSPEC_JEV_TASK_OUTPUT;

describe("MODEL-112 parseRealTask baseline", () => {
  it.skipIf(!inputPath || !outputPath)("writes the actual parser results", async () => {
    if (!inputPath || !outputPath) throw new Error("the input and output paths are required");
    const raw: unknown = JSON.parse(await readFile(inputPath, "utf8"));
    if (!isInput(raw)) throw new Error("input must contain a vocabulary path and task rows");
    const vocabularyRaw: unknown = JSON.parse(await readFile(raw.vocabulary, "utf8"));
    const vocabulary = vocabularySchema.parse(vocabularyRaw);
    const classIds = new Map([
      ["llm", "text-generator"],
      ["embed", "vectoriser"],
      ["rerank", "orderer"],
    ]);
    const results = raw.tasks.map((task) => {
      const started = performance.now();
      const parsed = parseRealTask(vocabulary, task.text);
      const latencyMs = performance.now() - started;
      const classCondition = parsed.conds.find((condition) => condition.f === "type");
      const classId = classCondition?.f === "type" ? classIds.get(classCondition.v) : undefined;
      return {
        id: task.id,
        domain: parsed.domain ?? "no_match",
        class: classId ?? "no_match",
        conditions: conditionNames(parsed.conds),
        latency_ms: latencyMs,
      };
    });
    await writeFile(outputPath, `${JSON.stringify(results)}\n`, "utf8");
    expect(results).toHaveLength(raw.tasks.length);
  });
});
