import { expect, type Page, type Route } from "@playwright/test";
import { test } from "./human-gate-fixtures";
import { existsSync, readFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

// MODEL-203: the built decide page renders every answered corpus spec. The
// Worker gate is disabled; vocabulary and /v1/decide use the engine's answers for each
// case (`python -m tests.corpus decisions --out DIR`), so a decision the page
// cannot draw fails here rather than on modelspec.dev.
const dir = resolve(process.env.MODELSPEC_CORPUS_DIR ?? fileURLToPath(new URL("../src/decide/__corpus__", import.meta.url)));

interface Row {
  id: string;
  intent: string;
  snapshot: string;
  http: number;
  file: string;
  generated: boolean;
}
const index: { cases: Row[]; vocabularies: Record<string, string> } | null = existsSync(
  join(dir, "index.json"),
)
  ? JSON.parse(readFileSync(join(dir, "index.json"), "utf8"))
  : null;
const read = (file: string) => readFileSync(join(dir, file), "utf8");

// Every hand-written answer, and each template at full. The generated facet and
// domain cases are parsed by the web suite; drawing ~170 more boards adds
// minutes and no new shape.
const drawn = (index?.cases ?? []).filter(
  (row) => row.http === 200 && (!row.generated || /^template-.*-full$/.test(row.id)),
);

const CORS = {
  "access-control-allow-origin": "*",
  "access-control-allow-headers": "content-type, x-modelspec-snapshot",
  "access-control-expose-headers": "x-modelspec-snapshot",
};

async function stub(page: Page, snapshot: string, decision: string) {
  const vocabulary = read(index!.vocabularies[snapshot]);
  await page.route(/\/(?:api\/decision\/vocabulary\.json|v1\/vocabulary)(?:\?.*)?$/, (route) =>
    route.fulfill({ status: 200, contentType: "application/json", headers: CORS, body: vocabulary }),
  );
  await page.route("**/v1/decide", (route: Route) =>
    route.request().method() === "OPTIONS"
      ? route.fulfill({ status: 204, headers: CORS })
      : route.fulfill({ status: 200, contentType: "application/json", headers: CORS, body: decision }),
  );
}

/** Loads the board and waits until it has drawn an answer or an error. */
async function openBoard(page: Page) {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("");
  await expect(page.getByRole("heading", { name: "Set what matters. Watch the field narrow." })).toBeVisible();
  await expect(page.getByText("The live answer will appear here.")).toHaveCount(0, { timeout: 15000 });
  return errors;
}

test.skip(index === null, `no corpus at ${dir}; run python -m tests.corpus decisions --out ${dir}`);

for (const row of drawn) {
  test(`${row.id}: ${row.intent}`, async ({ page }) => {
    await stub(page, row.snapshot, read(row.file));
    const errors = await openBoard(page);

    await expect(page.getByLabel("Facet board answer")).toBeVisible();
    await expect(page.getByText(/invalid_response|Decision unavailable/)).toHaveCount(0);
    await expect(page.getByRole("region", { name: "Manual lookups" })).toHaveCount(0);
    expect(errors, "uncaught page errors").toEqual([]);

    // No blank tables: every table drawn has rows, and every row says something.
    for (const table of await page.locator("table").all()) {
      if (!(await table.isVisible())) continue;
      const rows = table.locator("tbody tr");
      expect(await rows.count(), "a drawn table has no rows").toBeGreaterThan(0);
      for (const text of await rows.allInnerTexts()) expect(text.trim()).not.toBe("");
    }

    // A route is never called "API" (MODEL-202).
    for (const text of await page.locator(".board-routes").allInnerTexts()) {
      expect(text).not.toMatch(/\bAPI\b/);
    }
  });
}

async function applyTemplateThenReset(page: Page) {
  const template = drawn.find((row) => row.id.startsWith("template-") && row.snapshot === "repo");
  expect(template, "no template decision in the corpus").toBeTruthy();
  await stub(page, "repo", read(template!.file));
  await openBoard(page);
  // The template card starts collapsed (MODEL-277).
  await page.getByRole("button", { name: /Start from a template/ }).click();
  const templates = page.locator(".board-templates");
  await expect(templates.getByRole("button").first()).toBeVisible();
  await templates.getByRole("button").first().click();
  await expect(page.getByLabel("Facet board answer")).toBeVisible();
  await page.getByRole("button", { name: "Reset all" }).click();
}

test("a template applies and Reset all runs", async ({ page }) => {
  await applyTemplateThenReset(page);
  await expect(page.getByRole("heading", { name: "Set what matters. Watch the field narrow." })).toBeVisible();
});

test("the templates are offered again after Reset all", async ({ page }) => {
  await applyTemplateThenReset(page);
  const bar = page.getByRole("button", { name: /Start from a template/ });
  await expect(bar).toBeVisible({ timeout: 5000 });
  await expect(bar).toHaveAttribute("aria-expanded", "false");
  await bar.click();
  await expect(page.locator(".board-templates").getByRole("button").first()).toBeVisible();
});
