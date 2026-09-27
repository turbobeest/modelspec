import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

import { expect, test } from "@playwright/test";

const repository = fileURLToPath(new URL("../..", import.meta.url));
const python = process.env.MODELSPEC_PYTHON ?? "python3";
const chartPage = execFileSync(
  python,
  [
    "-c",
    `from pathlib import Path
from pipeline.load import Benchmark
from pipeline.render import CSS, benchmark_chart
rows = [{
    "model_id": f"demo/model-{i}", "display_name": f"Model {i}",
    "score": float(i), "unit": "percent", "as_of": "2026-09-01",
    "date_type": "evaluated", "source": f"https://src.example/{i}",
    "source_kind": "independent_evaluator", "benchmark_version": "v1",
    "configuration": "default", "attribution": "verified",
    "release_date": f"2025-{(i % 12) + 1:02d}-01",
} for i in range(20)]
bench = Benchmark("b", Path("benchmarks/b.md"), {"name": "Browser benchmark"}, "")
print(f"<style>{CSS}</style>{benchmark_chart(bench, rows)}")`,
  ],
  { cwd: repository, encoding: "utf8" },
);

test.use({ hasTouch: true });

test("tapping a chart point persistently discloses evidence and its source", async ({
  page,
}) => {
  await page.setContent(chartPage);
  const trigger = page.locator(".point-trigger").first();
  const detail = page.locator("#p1");

  await trigger.tap();

  await expect(page).toHaveURL(/#p1$/);
  await expect(detail).toBeVisible();
  await expect(detail).toContainText("Evidence date: 2026-09-01 (evaluated)");
  await expect(detail).toContainText("Configuration: default");
  await expect(detail.getByRole("link", { name: "Open evidence source" })).toHaveAttribute(
    "href",
    "https://src.example/0",
  );
});
