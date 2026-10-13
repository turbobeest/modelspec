import assert from "node:assert/strict";
import { spawn, spawnSync } from "node:child_process";
import { mkdir, readFile } from "node:fs/promises";
import { once } from "node:events";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const webRequire = createRequire(new URL("../web/package.json", import.meta.url));
const { chromium } = webRequire("playwright");

// Build with VITE_VISIT_GATE_ENABLED=true VITE_TURNSTILE_SITE_KEY=public-test-key.
// Run from any directory with MODELSPEC_TEST_PYTHON pointing at the repo Python.
const cwd = fileURLToPath(new URL("../", import.meta.url));
const artifacts = `${cwd}/.scratch/model-353-page`;
await mkdir(artifacts, { recursive: true });
const server = spawn(process.execPath, ["node_modules/vite/bin/vite.js", "preview", "--host", "127.0.0.1", "--port", "5193", "--strictPort"], { cwd: `${cwd}/web`, stdio: "ignore" });
const serverExit = once(server, "exit");
let browser;
try {
  for (let attempt = 0; attempt < 50; attempt++) {
    try { if ((await fetch("http://127.0.0.1:5193/decision.html")).ok) break; } catch {}
    if (server.exitCode !== null) throw new Error(`Preview exited with ${server.exitCode}`);
    await new Promise((resolve) => setTimeout(resolve, 200));
  }
  const policy = spawnSync(process.env.MODELSPEC_TEST_PYTHON ?? "python3", ["-c", "from pathlib import Path; from pipeline.security_headers import csp; print(csp(Path('web/dist')))"], { cwd, encoding: "utf8" });
  assert.equal(policy.status, 0);
  const shell = await readFile(`${cwd}/web/dist/decision.html`, "utf8");
  browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1100, height: 1000 } });
  const requests = [];
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error" && /content security policy|violat/i.test(message.text())) errors.push(message.text());
  });
  await page.route("http://127.0.0.1:5193/d/**", (route) => route.fulfill({ contentType: "text/html", body: shell, headers: { "Content-Security-Policy": policy.stdout.trim(), "Referrer-Policy": "no-referrer", "Cache-Control": "no-store" } }));
  await page.addInitScript(() => {
    const widgets = new Map();
    window.turnstile = {
      render(container, options) {
        const button = document.createElement("button");
        button.textContent = "Verify fixture";
        button.onclick = () => options.callback("verified-human");
        container.append(button);
        widgets.set("widget", container);
        return "widget";
      },
      remove(id) { widgets.get(id)?.replaceChildren(); widgets.delete(id); },
    };
  });
  const summary = {
    decision_id: "dec_3a97fadf7a200027c618b3a3",
    snapshot: { id: "snap_pinned", content_hash: `sha256:${"a".repeat(64)}` },
    summary_for_user: "Alpha fits the requirements you applied. The pinned snapshot is the source of this answer.",
    must_mention: ["The models are tied in the best band.", "Task type was not applied."],
    requirements: { applied: { where: [{ facet: "model.max_output_tokens", op: ">=", value: 8000 }], optimize: { max: { facet: "swe_bench_pro" } }, unknowns: "default", task_tokens: { input: 40000, output: 4000 }, capabilities: { software_engineering: "required" } }, not_applied: ["task_type"] },
  };
  await page.route("**/v1/**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    requests.push({ url: request.url(), headers: request.headers(), body: request.postData() });
    let body;
    if (url.pathname.endsWith("/human-status")) body = { enabled: true, mode: "visit", day_limit: 300, burst_limit: 30 };
    else if (url.pathname.endsWith("/visit-token")) body = { token: "visit-token", expires_at: Math.floor(Date.now() / 1000) + 1800 };
    else if (url.pathname.endsWith("/decision-link")) body = { ...summary, results: [{ model: "must-not-render" }] };
    else throw new Error(`Unexpected API request ${url.pathname}`);
    await route.fulfill({ contentType: "application/json", headers: { "access-control-allow-origin": "*" }, body: JSON.stringify(body) });
  });
  await page.goto(`http://127.0.0.1:5193/d/${summary.decision_id}?token=signed-capsule.signature`);
  await page.getByRole("button", { name: "Verify fixture" }).waitFor();
  assert.equal(requests.length, 1);
  await page.getByRole("button", { name: "Verify fixture" }).click();
  await page.getByText(summary.summary_for_user).waitFor();
  assert.equal(await page.getByRole("table").count(), 0);
  assert.equal(await page.getByRole("link").count(), 0);
  assert.equal((await page.locator("body").innerText()).includes("must-not-render"), false);
  const lookup = requests.find((request) => request.url.endsWith("/decision-link"));
  assert.deepEqual(JSON.parse(lookup.body), { decision_id: summary.decision_id, token: "signed-capsule.signature" });
  assert.equal(lookup.headers["x-modelspec-visit-token"], "visit-token");
  for (const request of requests) assert.equal(request.headers.referer, undefined);
  assert.deepEqual(errors, []);
  await page.screenshot({ path: `${artifacts}/browser-desktop.png`, fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), true);
  await page.screenshot({ path: `${artifacts}/browser-mobile.png`, fullPage: true });
  console.log(JSON.stringify({ result: "PASS", browser: await browser.version(), requests: requests.map((request) => new URL(request.url).pathname), referrers: "none", cspErrors: errors, tableCount: 0, mobileOverflow: false }));
} finally {
  try { await browser?.close(); }
  finally {
    if (server.exitCode === null) server.kill("SIGTERM");
    await serverExit;
  }
}
