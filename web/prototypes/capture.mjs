import { mkdir, writeFile, copyFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const origin = process.env.PROTO_ORIGIN ?? "http://127.0.0.1:5197";
const output = fileURLToPath(new URL("../../.scratch/proto/", import.meta.url));
const baseline = "/Users/terbeest/dev/worktrees/ux-panel/.scratch/ux-panel";
await mkdir(output, { recursive: true });
const browser = await chromium.launch();
const metrics = [];
try {
  for (const [size, viewport] of Object.entries({ desktop: { width: 1440, height: 900 }, mobile: { width: 390, height: 844 } })) {
    for (const variant of ["current", "a", "b", "c"]) {
      const context = await browser.newContext({ viewport, reducedMotion: "reduce" });
      const page = await context.newPage();
      const errors = [];
      page.on("pageerror", (error) => errors.push(error.message));
      await page.route("**/*", (route) => new URL(route.request().url()).origin === origin ? route.continue() : route.abort());
      await page.goto(`${origin}/${variant === "current" ? "decide/" : `prototypes/proto-${variant}.html`}`);
      await page.getByRole("heading", { name: "Which AI model fits your job?", exact: true }).waitFor();
      if (variant === "current" || variant === "c") await page.locator(".ranked-answer").waitFor();
      if (variant === "a") await page.locator("[data-decision-id]").waitFor();
      await page.evaluate(() => document.fonts.ready);
      const measurement = await page.evaluate(() => {
        const visible = (element) => element.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true }) && element.getClientRects().length > 0;
        const words = [];
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        let node;
        while ((node = walker.nextNode())) {
          if (!node.textContent.trim() || !node.parentElement || ["SCRIPT", "STYLE", "OPTION"].includes(node.parentElement.tagName)) continue;
          if (!visible(node.parentElement)) continue;
          const range = document.createRange();
          range.selectNodeContents(node);
          if ([...range.getClientRects()].some((rect) => rect.width > 0 && rect.height > 0)) words.push(node.textContent.trim());
        }
        const count = (selector) => [...document.querySelectorAll(selector)].filter(visible).length;
        return { height: document.documentElement.scrollHeight, width: document.documentElement.scrollWidth,
          buttons: count("button"), inputs: count("input, select, textarea"), expanders: count("summary"),
          visibleWords: words.join(" ").split(/\s+/).filter(Boolean).length,
          visibleText: words.join("\n") };
      });
      metrics.push({ variant, size, viewport, ...measurement, errors });
      await writeFile(`${output}/${variant}-${size}-text.txt`, measurement.visibleText + "\n");
      for (const kind of ["fold", "full"]) {
        if (variant === "current") {
          await copyFile(`${baseline}/${size}-${kind}.png`, `${output}/current-${size}-${kind}.png`);
          await page.screenshot({ path: `${output}/current-remeasured-${size}-${kind}.png`, fullPage: kind === "full" });
        } else await page.screenshot({ path: `${output}/${variant}-${size}-${kind}.png`, fullPage: kind === "full" });
      }
      await page.close();
      await context.close();
      console.log(`${variant} ${size}: ${measurement.height}px, ${measurement.buttons} buttons, ${measurement.inputs} inputs, ${measurement.visibleWords} words; errors=${errors.length}`);
    }
  }
  await writeFile(`${output}/metrics.json`, JSON.stringify(metrics, null, 2) + "\n");
} finally { await browser.close(); }
