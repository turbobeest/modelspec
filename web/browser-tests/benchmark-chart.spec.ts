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
const stripRows = `rows = [{
    "model_id": f"demo/model-{i}", "display_name": f"Model {i}",
    "score": float(i * 10), "unit": "percent", "as_of": "2026-09-01",
    "date_type": "evaluated", "source": f"https://src.example/{i}",
    "source_kind": "independent_evaluator", "benchmark_version": "v1",
    "configuration": "default", "attribution": "verified",
} for i in range(3)]`;
const stripAsset = execFileSync(
  python,
  [
    "-c",
    `from pipeline.render import benchmark_strip_asset
${stripRows}
print(benchmark_strip_asset(rows))`,
  ],
  { cwd: repository, encoding: "utf8" },
);
const stripPage = execFileSync(
  python,
  [
    "-c",
    `from pathlib import Path
from pipeline.load import Benchmark, Model
from pipeline.render import CSS, model_benchmark_strips
${stripRows}
model = Model("demo/model-0", Path("models/demo/model-0.md"), {
    "display_name": "Model 0", "provider": "demo",
    "benchmarks": {"evidence": [{"benchmark_id": "b", "score": 0.0}]},
}, "")
bench = Benchmark("b", Path("benchmarks/b.md"), {"name": "Browser benchmark"}, "")
print(f"<style>{CSS}</style>{model_benchmark_strips(model, {'b': bench}, {'b': rows})}")`,
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

test("tapping a non-focus strip point discloses its evidence and source", async ({
  page,
}) => {
  await page.route("**/assets/benchmark-strips/b.svg", async (route) => {
    await route.fulfill({ body: stripAsset, contentType: "image/svg+xml" });
  });
  await page.route("**/strip-test", async (route) => {
    await route.fulfill({ body: stripPage, contentType: "text/html" });
  });
  await page.goto("/strip-test");

  const asset = page.locator(".benchmark-strip-asset");
  const bounds = await asset.boundingBox();
  if (bounds === null) {
    throw new Error("benchmark strip asset has no browser layout box");
  }

  await page.touchscreen.tap(bounds.x + bounds.width / 2, bounds.y + bounds.height * (17 / 43));

  await expect.poll(async () => asset.evaluate((node) => {
    if (!(node instanceof HTMLObjectElement) || node.contentDocument === null) {
      return null;
    }
    const detail = node.contentDocument.querySelector("#p2");
    const source = detail?.querySelector('[aria-label="Open evidence source"]');
    if (detail === null || source === null) {
      return null;
    }
    return {
      display: getComputedStyle(detail).display,
      source: source.getAttribute("href"),
      text: detail.textContent,
    };
  })).toEqual({
    display: "block",
    source: "https://src.example/1",
    text: expect.stringContaining(
      "Evidence date: 2026-09-01 (evaluated)Configuration: default",
    ),
  });
});
