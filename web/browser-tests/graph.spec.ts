import { expect, test } from "@playwright/test";

test("the static graph renders nodes in WebGL without console errors", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  page.on("pageerror", (error) => errors.push(error.message));

  await page.goto("/graph/");
  const webgl = await page.evaluate(() => {
    const canvas = document.createElement("canvas");
    return Boolean(canvas.getContext("webgl2") ?? canvas.getContext("webgl"));
  });
  test.skip(!webgl && !process.env.CI, "WebGL is unavailable outside CI");
  expect(webgl, "CI must provide WebGL for the graph smoke test").toBe(true);

  const scene = page.locator("#scene");
  await expect(scene).toHaveAttribute("data-node-count", /[1-9][0-9]*/);
  await expect(scene.locator("canvas")).toBeVisible();
  expect(Number(await scene.getAttribute("data-node-count"))).toBeGreaterThan(0);
  expect(errors).toEqual([]);
});
