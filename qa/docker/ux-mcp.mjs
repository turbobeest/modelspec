// Official Playwright MCP, with independent evidence and the existing UX gate policy.
import fs from 'node:fs';
import readline from 'node:readline';
import { createRequire } from 'node:module';

process.env.PLAYWRIGHT_BROWSERS_PATH = '/opt/modelspec-browser/browsers';
const require = createRequire('/opt/modelspec-browser/package.json');
const { chromium } = require('playwright');
const { createConnection } = require('@playwright/mcp');
const task = JSON.parse(fs.readFileSync('/work/ux-task.json', 'utf8'));
const dom = fs.readFileSync('/work/dom.js', 'utf8');
const evidence = { states: [], steps: [], screenshots: [], checks: [], lookups: { requests: 0, events: [], blocked: null } };
const hosts = new Set([new URL(task.base_url).hostname, 'modelspec.dev', 'www.modelspec.dev', 'api.modelspec.dev']);
const allowed = new Set(['browser_navigate', 'browser_snapshot', 'browser_press_key', 'browser_wait_for']);
if (task.interaction !== 'keyboard') {
  for (const name of ['browser_click', 'browser_hover', 'browser_type', 'browser_select_option', 'browser_drag']) allowed.add(name);
}
fs.mkdirSync('/work/evidence', { recursive: true });
let browser, context, current, starts = 0;

function persist() {
  fs.writeFileSync('/work/evidence/evidence.json', JSON.stringify(evidence, null, 2));
}

async function checks(page) {
  const rows = [];
  for (const check of task.checks || []) {
    let passed;
    if (check.kind === 'no_horizontal_overflow') {
      passed = await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1);
    } else {
      let matches = page.locator(check.selector);
      if (check.text) matches = matches.filter({ hasText: check.text });
      const count = await matches.count();
      passed = check.kind === 'absent' ? count === 0 : false;
      if (check.kind !== 'absent') for (let i = 0; i < count; i++) passed ||= await matches.nth(i).isVisible();
    }
    rows.push({ ...check, passed });
  }
  return rows;
}

async function capture() {
  const pages = context.pages().filter(p => !p.isClosed());
  current = pages.at(-1);
  if (!current) throw new Error('Browser closed before evidence');
  const name = `step-${String(evidence.states.length).padStart(2, '0')}`;
  const state = await current.evaluate(`(${dom})()`);
  state.checks = await checks(current);
  state.step = name;
  await current.screenshot({ path: `/work/evidence/${name}.png`, animations: 'disabled' });
  evidence.states.push(state);
  evidence.screenshots.push(`evidence/${name}.png`);
  evidence.checks = state.checks.map((check, i) => ({ ...check, passed: check.during_visit ? evidence.states.some(s => s.checks[i].passed) : check.passed }));
  persist();
}

function block(reason) {
  evidence.lookups.blocked = reason;
  evidence.lookups.events.push({ kind: reason });
  persist();
}

async function guard(route) {
  const request = route.request();
  const url = new URL(request.url());
  if (!hosts.has(url.hostname) || url.hostname === 'challenges.cloudflare.com') return route.abort();
  if (url.pathname.replace(/\/$/, '') !== '/v1/decide' || request.method() !== 'POST') {
    return ['GET', 'HEAD', 'OPTIONS'].includes(request.method()) ? route.continue() : route.abort();
  }
  try {
    const response = await context.request.get(`${url.origin}/v1/human-status`, { headers: { Origin: new URL(task.base_url).origin }, timeout: 10000 });
    const status = await response.json();
    if (!response.ok() || typeof status.enabled !== 'boolean') throw new Error('Unavailable status');
    if (status.enabled) block('blocked by human verification');
  } catch {
    block('blocked by unavailable human status');
  }
  if (evidence.lookups.blocked) return route.abort();
  evidence.lookups.requests++;
  evidence.lookups.events.push({ kind: 'lookup', gated: false });
  persist();
  return route.continue();
}

async function getContext() {
  if (context) return context;
  browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  context = await browser.newContext({ viewport: task.viewport, serviceWorkers: 'block' });
  await context.route('**/*', guard);
  context.on('response', async response => {
    if (!['/v1/human-status', '/v1/decide'].includes(new URL(response.url()).pathname.replace(/\/$/, ''))) return;
    try {
      const data = await response.json();
      const code = typeof data.error === 'object' ? data.error?.code : data.error;
      if (data.enabled === true || String(code || '').startsWith('human_')) block('blocked by human verification');
    } catch { /* A malformed decide reply cannot prove task completion. */ }
  });
  current = await context.newPage();
  await current.goto(task.base_url, { waitUntil: 'domcontentloaded' });
  await current.locator('.decide-app').waitFor({ state: 'visible', timeout: 15000 });
  await capture();
  return context;
}

const pending = new Map();
const transport = {
  async start() {
    const input = readline.createInterface({ input: process.stdin });
    input.on('line', line => {
      const message = JSON.parse(line);
      if (message.method === 'tools/call') {
        const { name, arguments: args = {} } = message.params;
        let denied = !allowed.has(name) || evidence.lookups.blocked || starts >= task.max_steps;
        if (name === 'browser_navigate') {
          try {
            const url = new URL(args.url);
            denied ||= !['https:', 'http:'].includes(url.protocol) || !hosts.has(url.hostname) || !!url.search || !!url.hash;
          } catch { denied = true; }
        }
        if (denied) {
          process.stdout.write(JSON.stringify({ jsonrpc: '2.0', id: message.id, result: { isError: true, content: [{ type: 'text', text: evidence.lookups.blocked || 'UX action refused by tool/step policy' }] } }) + '\n');
          return;
        }
        starts++;
        pending.set(message.id, message.params);
      }
      this.onmessage(message);
    });
  },
  async send(message) {
    if (message.result?.tools) message.result.tools = message.result.tools.filter(tool => allowed.has(tool.name));
    const action = pending.get(message.id);
    if (action) {
      pending.delete(message.id);
      evidence.steps.push({ step: evidence.steps.length + 1, actions: [{ [action.name]: action.arguments }], results: [message.result || message.error] });
      if (context) {
        await current.waitForTimeout(500);
        try { await capture(); } catch { block('blocked by unavailable browser evidence'); }
      }
    }
    process.stdout.write(JSON.stringify(message) + '\n');
  },
  async close() { if (browser) await browser.close(); },
};
const server = await createConnection({ browser: { isolated: false }, capabilities: [] }, getContext);
await server.connect(transport);
