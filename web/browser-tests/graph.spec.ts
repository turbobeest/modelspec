import { expect, test, type Page } from "@playwright/test";

const graphData = process.env.DATA_SPLIT_ENABLED === "true" ? "/graph/data" : "/api/graph";

interface View {
  key: string;
  title: string;
  legible: boolean;
  bytes?: number;
}

async function openGraph(page: Page): Promise<string[]> {
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
  expect(webgl, "CI must provide WebGL for the graph tests").toBe(true);
  return errors;
}

test("the static graph renders nodes in WebGL without console errors", async ({
  page,
}) => {
  const errors = await openGraph(page);

  const scene = page.locator("#scene");
  await expect(scene).toHaveAttribute("data-node-count", /[1-9][0-9]*/);
  await expect(scene.locator("canvas")).toBeVisible();
  expect(Number(await scene.getAttribute("data-node-count"))).toBeGreaterThan(0);
  expect(errors).toEqual([]);
});

test("dense views say how much they will download before loading", async ({
  page,
}) => {
  await openGraph(page);
  const { views } = (await (
    await page.request.get(`${graphData}/views.json`)
  ).json()) as { views: View[] };
  const dense = views.filter((v) => !v.legible && v.bytes);
  expect(dense.length, "the export must publish a dense view").toBeGreaterThan(0);

  await expect(page.locator("#view option")).toHaveCount(views.length);
  for (const view of views) {
    const option = page.locator(`#view option[value="${view.key}"]`);
    if (!view.legible && view.bytes) {
      const megabytes = (view.bytes / 1_000_000).toFixed(1);
      await expect(option).toHaveText(
        `Load ${megabytes} MB ${view.title.toLowerCase()} view`,
      );
    } else {
      await expect(option).toHaveText(view.title);
    }
  }
});

test("opening a node shows its facts and no link to a catalogue page", async ({
  page,
}) => {
  await openGraph(page);
  const { views } = (await (
    await page.request.get(`${graphData}/views.json`)
  ).json()) as { views: View[] };
  const first = (await (
    await page.request.get(`${graphData}/views/${views[0].key}.json`)
  ).json()) as {
    nodes: { key: string; display_name?: string; name?: string; id?: string }[];
    edges: { from: string }[];
  };
  const node = first.nodes.find((n) => n.key === first.edges[0].from)!;
  const name = String(node.display_name ?? node.name ?? node.id);

  await expect(page.locator("#scene")).toHaveAttribute(
    "data-node-count",
    /[1-9][0-9]*/,
  );
  await page.locator("#search").fill(name);
  await expect(page.locator("#detail")).toBeVisible();
  await expect(page.locator("#dName")).toHaveText(name);

  await expect(page.locator("#detail a")).toHaveCount(0);
  await expect(
    page.locator('a[href^="/m/"], a[href^="/p/"], a[href^="/b/"]'),
  ).toHaveCount(0);
});

test.describe("reduced motion", () => {
  test.use({ reducedMotion: "reduce" });

  test("frames the laid-out graph with an instant camera move", async ({
    page,
  }) => {
    await openGraph(page);
    await expect(page.locator("#scene")).toHaveAttribute("data-frame-ms", "0");
  });
});

test.describe("full motion", () => {
  test.use({ reducedMotion: "no-preference" });

  test("frames the laid-out graph with an animated camera move", async ({
    page,
  }) => {
    await openGraph(page);
    await expect(page.locator("#scene")).toHaveAttribute(
      "data-frame-ms",
      "900",
    );
  });
});
