import { expect, test } from "@playwright/test";
test("dragging a cap updates the spec and keyboard floor respects Shift", async ({
  page,
}) => {
  await page.goto("/decide.html?demo=1");
  await page.getByText("start from constraints", { exact: true }).click();
  await page.keyboard.press("Escape");
  const plot = page.locator(".plot");
  const bounds = await plot.boundingBox();
  if (!bounds) throw new Error("Plot missing");
  const handle = page.getByRole("slider", { name: /per task cap/ });
  const box = await handle.boundingBox();
  if (!box) throw new Error("Cap missing");
  await page.mouse.move(box.x + 1, box.y + 100);
  await page.mouse.down();
  await page.mouse.move(bounds.x + bounds.width * 0.6, bounds.y + 100, {
    steps: 10,
  });
  await page.mouse.up();
  await expect(
    page.getByRole("button", { name: /Edit condition: ≤ .* per task/ }),
  ).toBeVisible();
  const floor = page.getByRole("slider", { name: /CodeBench Pro floor/ });
  await floor.focus();
  await page.keyboard.press("ArrowUp");
  const first = Number(await floor.getAttribute("aria-valuenow"));
  await page.keyboard.press("Shift+ArrowUp");
  await expect(floor).toHaveAttribute("aria-valuenow", String(first + 5));
  await page.reload();
  await expect(
    page.getByRole("button", { name: /Edit condition: CodeBench Pro/ }),
  ).toBeVisible();
});
test("table selection, sorting and excluded toggle drive the Why panel", async ({
  page,
}) => {
  await page.goto("/decide.html?demo=1&layout=table&theme=dark");
  await page.getByText("start from constraints", { exact: true }).click();
  await page.keyboard.press("Escape");
  const table = page.getByRole("region", {
    name: "Decision table",
    exact: true,
  });
  await table.getByRole("button", { name: "Atlas 2.5", exact: true }).click();
  await expect(
    page.getByRole("region", { name: "Why this model" }),
  ).toContainText("Retired 2026-03-31");
  await table.getByRole("button", { name: "$ per task", exact: true }).click();
  await expect(
    table.getByRole("columnheader", { name: "$ per task ↑" }),
  ).toHaveAttribute("aria-sort", "ascending");
  await table.getByRole("checkbox").uncheck();
  await expect(
    table.getByRole("button", { name: "Atlas 2.5", exact: true }),
  ).toHaveCount(0);
});
test("native modal traps focus, exports CSV, copies links and restores trigger focus", async ({
  page,
  context,
}) => {
  await context.grantPermissions(["clipboard-read", "clipboard-write"]);
  await page.goto("/decide.html?demo=1");
  await page.getByText("start from constraints", { exact: true }).click();
  await page.keyboard.press("Escape");
  await page.getByRole("button", { name: "Share or act", exact: true }).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByRole("button", { name: "Copy", exact: true }).click();
  expect(await page.evaluate(() => navigator.clipboard.readText())).toContain(
    "#s=",
  );
  await dialog.getByRole("tab", { name: "Procurement review" }).click();
  const download = page.waitForEvent("download");
  await dialog.getByRole("button", { name: "Download CSV" }).click();
  expect((await download).suggestedFilename()).toContain(
    "modelspec-snap_2026-09-24_",
  );
  await page.keyboard.press("Escape");
  await expect(dialog).not.toBeVisible();
  await expect(
    page.getByRole("button", { name: "Share or act", exact: true }),
  ).toBeFocused();
});
test("reduced motion disables transitions and narrow desktop collapses result grid", async ({
  page,
}) => {
  await page.goto("/decide.html?demo=1");
  await page.getByText("start from constraints", { exact: true }).click();
  await page.keyboard.press("Escape");
  expect(
    await page
      .locator(".point")
      .first()
      .evaluate((el) => getComputedStyle(el).transitionDuration),
  ).toBe("0s");
  await page.setViewportSize({ width: 1050, height: 1000 });
  expect(
    await page
      .locator(".results")
      .evaluate(
        (el) => getComputedStyle(el).gridTemplateColumns.split(" ").length,
      ),
  ).toBe(1);
  await expect(page.locator(".snapshot")).not.toBeVisible();
});
test("context arrows move between standard sizes rather than snapping back", async ({
  page,
}) => {
  await page.goto("/decide.html?demo=1");
  await page.getByText("start from constraints", { exact: true }).click();
  await page.keyboard.press("Escape");
  await page.getByLabel("X axis", { exact: true }).selectOption("ctx");
  const slider = page.getByRole("slider", { name: /Context length minimum/ });
  await slider.focus();
  await page.keyboard.press("ArrowRight");
  const first = Number(await slider.getAttribute("aria-valuenow"));
  await page.keyboard.press("ArrowRight");
  expect(Number(await slider.getAttribute("aria-valuenow"))).toBeGreaterThan(
    first,
  );
});
