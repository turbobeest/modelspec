import { chromium } from "@playwright/test";
import { mkdir, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import {
  TEMPLATES,
  parseTask,
} from "../../docs/design/handoff/core-flow/modelspec-data.js";
const out = fileURLToPath(
  new URL("../../docs/design/handoff/core-flow/screens/", import.meta.url),
);
const browser = await chromium.launch();
const page = await browser.newPage({
  viewport: { width: 1440, height: 1000 },
  reducedMotion: "reduce",
});
const records = [];
const base = {
  task: "",
  tokIn: 40000,
  tokOut: 4000,
  bench: "CodeBench Pro",
  w: { cap: 0.6, cost: 0.3, speed: 0.1 },
  conds: [{ f: "type", v: "llm" }, { f: "active" }],
};
const task = "Refactor a large Rust codebase, precision matters",
  parsed = { ...base, task, ...parseTask(task) };
// The original viewer exposes simulate as a prop. Query injection is only in
// this screenshot browser; the saved reference files remain byte-for-byte.
await page.route("**/ModelSpec.dc.html*", async (route) => {
  const response = await route.fetch();
  let text = await response.text();
  text = text.replace(
    "const sim = this.props.simulate || 'none'",
    "const sim = new URLSearchParams(location.search).get('simulate') || this.props.simulate || 'none'",
  );
  await route.fulfill({ response, body: text });
});
for (const target of ["app", "reference"])
  for (const theme of ["light", "dark"])
    for (const layout of ["canvas", "table"]) {
      const root =
        target === "app"
          ? "http://127.0.0.1:5173/decide.html"
          : "http://127.0.0.1:4174/ModelSpec.dc.html";
      const dir = `${target}/${theme}-${layout}`;
      await mkdir(`${out}/${dir}`, { recursive: true });
      async function load(spec = null, extra = "", axis = "task$") {
        const hash = spec
          ? "#s=" +
            btoa(encodeURIComponent(JSON.stringify({ ...spec, x: axis })))
          : "";
        await page.goto("about:blank");
        await page.goto(
          `${root}?theme=${theme}&layout=${layout}${extra}${hash}`,
        );
        await page
          .getByRole("button", { name: "ModelSpec home", exact: true })
          .waitFor();
        if (spec)
          await page
            .getByRole("button", { name: "Share or act", exact: true })
            .waitFor();
        await page.waitForTimeout(120);
      }
      async function shot(name, fullPage = false) {
        await page.screenshot({ path: `${out}/${dir}/${name}.png`, fullPage });
        records.push({
          target,
          theme,
          layout,
          state: name,
          path: `${dir}/${name}.png`,
        });
      }
      await load();
      await shot("01-arrive");
      await load(base);
      await page.clock.install();
      await page.clock.pauseAt(new Date());
      await page.getByRole("textbox", { name: "Task", exact: true }).fill(task);
      await page
        .getByRole("textbox", { name: "Task", exact: true })
        .press("Enter");
      await page.clock.runFor(20);
      await page.getByText("Reading your task…", { exact: true }).waitFor();
      await shot("02-parsing");
      await page.clock.runFor(500);
      await page.clock.resume();
      await shot("03-decide", true);
      await page
        .getByRole("button", { name: "+ add condition", exact: true })
        .click();
      await page
        .getByRole("textbox", { name: "Search facets" })
        .fill("residency");
      await shot("04-search");
      await page.getByRole("textbox", { name: "Search facets" }).press("Enter");
      await shot("05-editor");
      await page.keyboard.press("Escape");
      await load({
        ...base,
        conds: [...base.conds, { f: "open", v: true, soft: true }],
      });
      await shot("06-soft-preference");
      await load(parsed);
      const may = page.getByRole("button").filter({ hasText: "Cairn 1" });
      await may.first().click();
      const why =
        target === "app"
          ? page.getByRole("region", { name: "Why this model" })
          : page.locator('[data-screen-label="03 Why"]');
      if (await why.count()) await why.scrollIntoViewIfNeeded();
      else
        await page
          .getByText("Provisional.", { exact: false })
          .first()
          .scrollIntoViewIfNeeded()
          .catch(() => {});
      await shot("07-may-provisional");
      await load({ ...TEMPLATES[0].spec, task: TEMPLATES[0].task });
      await shot("08-not-separable", true);
      const prov = page.getByRole("button", { name: /Provenance for/ }).first();
      await prov.click();
      await shot("09-provenance");
      await page.keyboard.press("Escape");
      await load(base);
      const retired =
        target === "app"
          ? page.getByRole("button", { name: "Atlas 2.5", exact: true })
          : page.getByRole("row").filter({ hasText: "Atlas 2.5" });
      await retired.first().click();
      const whyPanel =
        target === "app"
          ? page.getByRole("region", { name: "Why this model" })
          : page.getByText("Retired 2026-03-31.", { exact: false });
      await whyPanel.first().scrollIntoViewIfNeeded();
      await shot("10-retired");
      await load({
        ...base,
        conds: [...base.conds, { f: "task$", max: 0.0001 }],
      });
      await shot("11-nothing-qualifies");
      await load(base, "", "tps");
      await shot("12-not-plotted");
      await load(base);
      await page.getByRole("button", { name: /Cairn 1, Qualifies/ }).focus();
      await shot("13-tooltip");
      await page
        .getByRole("button", { name: "Share or act", exact: true })
        .click();
      for (const [i, tab] of [
        "Permalink",
        "API call",
        "CLI",
        "Spec YAML",
        "Save and alert",
        "Procurement review",
      ].entries()) {
        const button = page.getByRole("tab", { name: tab, exact: true });
        await button.click();
        await shot(`14-share-${i + 1}`);
      }
      await page.keyboard.press("Escape");
      await load(base, "&simulate=loading");
      await shot("15-loading", true);
      await load(base, "&simulate=error");
      await shot("16-error");
      console.log(dir, "captured");
    }
await writeFile(
  `${out}/manifest.json`,
  JSON.stringify(
    { viewport: { width: 1440, height: 1000 }, records },
    null,
    2,
  ) + "\n",
);
await browser.close();
