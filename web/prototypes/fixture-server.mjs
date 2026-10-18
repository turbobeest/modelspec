import { spawn } from "node:child_process";
import { readFileSync } from "node:fs";
import { createInterface } from "node:readline";
import { fileURLToPath } from "node:url";
import { decisionFixtureFor } from "../scripts/decision-fixtures.mjs";

const fixtures = new URL("../src/decide/__fixtures__/", import.meta.url);
const vocabulary = readFileSync(new URL("live-vocabulary.json", fixtures), "utf8");
const captures = JSON.parse(readFileSync(new URL("live-decision-requests.json", fixtures), "utf8"));

function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (value !== null && typeof value === "object")
    return Object.fromEntries(Object.entries(value)
      .filter(([, item]) => item !== undefined)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([key, item]) => [key, canonical(item)]));
  return value;
}

export function requestKey(spec) {
  const { snapshot: _snapshot, ...request } = spec;
  return JSON.stringify(canonical(request));
}

const captured = new Set(captures.map(({ spec }) => requestKey(spec)));

/** The browser helper's fallback is deliberately excluded from this prototype. */
export function capturedDecision(spec) {
  return spec && typeof spec === "object" && captured.has(requestKey(spec))
    ? decisionFixtureFor(spec) : null;
}

export function createFixtureResponder() {
  const python = process.env.PROTO_DECIDE_PYTHON ?? "/Users/terbeest/dev/modelspec/.venv/bin/python";
  const child = spawn(python, [fileURLToPath(new URL("decide-local.py", import.meta.url))], {
    cwd: fileURLToPath(new URL("../../", import.meta.url)),
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: "1" },
    stdio: ["pipe", "pipe", "pipe"],
  });
  let nextId = 0;
  const pending = new Map();
  const cache = new Map();
  let resolveReady;
  let rejectReady;
  const ready = new Promise((resolve, reject) => { resolveReady = resolve; rejectReady = reject; });
  let diagnostics = "";
  child.stderr.on("data", (chunk) => { diagnostics = (diagnostics + chunk).slice(-8000); });
  const lines = createInterface({ input: child.stdout });
  const fail = (error) => {
    rejectReady(error);
    for (const waiter of pending.values()) waiter.reject(error);
    pending.clear();
  };
  lines.on("line", (line) => {
    try {
      const message = JSON.parse(line);
      if (message.ready) return resolveReady(message.snapshot);
      const waiter = pending.get(message.id);
      if (waiter) {
        pending.delete(message.id);
        waiter.resolve({ status: message.status, body: JSON.stringify(message.body), source: "frozen-repository" });
      }
    } catch (error) { fail(error); }
  });
  child.on("error", fail);
  child.on("exit", (code, signal) => fail(new Error(`Prototype engine exited (${code ?? signal}). ${diagnostics}`)));
  const close = () => {
    lines.close();
    child.stdin.end();
    child.kill("SIGTERM");
  };
  const exit = () => close();
  process.once("exit", exit);
  return {
    ready,
    async decide(spec) {
      const recorded = capturedDecision(spec);
      if (recorded !== null) return { status: 200, body: recorded, source: "recorded-browser-fixture" };
      await ready;
      const key = JSON.stringify(canonical(spec));
      if (!cache.has(key)) {
        const id = nextId++;
        const response = new Promise((resolve, reject) => {
          pending.set(id, { resolve, reject });
          child.stdin.write(JSON.stringify({ id, spec }) + "\n");
        });
        cache.set(key, response);
        response.catch(() => cache.delete(key));
      }
      return cache.get(key);
    },
    close() { process.removeListener("exit", exit); close(); },
  };
}

function json(res, status, body, source) {
  res.statusCode = status;
  res.setHeader("content-type", "application/json");
  res.setHeader("cache-control", "no-store");
  if (source) res.setHeader("x-prototype-source", source);
  res.end(body);
}

export function prototypeFixtures() {
  let responder;
  return {
    name: "proto-decide-offline-fixtures",
    async configureServer(server) {
      responder = createFixtureResponder();
      await responder.ready;
      server.httpServer?.once("close", () => responder.close());
      server.middlewares.use(async (req, res, next) => {
        const path = (req.url ?? "").split("?")[0];
        if (path === "/decide/" || path === "/decide") {
          req.url = req.url.replace(/^\/decide\/?/, "/decide.html");
          return next();
        }
        if (path === "/api/decision/vocabulary.json" || path === "/v1/vocabulary")
          return json(res, 200, vocabulary, "recorded-browser-fixture");
        if (path === "/v1/human-status") return json(res, 200, '{"enabled":false}');
        if (path !== "/v1/decide") return next();
        if (req.method !== "POST") return json(res, 405, '{"error":"POST required"}');
        try {
          const chunks = [];
          let bytes = 0;
          for await (const chunk of req) {
            bytes += chunk.length;
            if (bytes > 65536) return json(res, 413, '{"error":"request too large"}');
            chunks.push(chunk);
          }
          const spec = JSON.parse(Buffer.concat(chunks).toString("utf8"));
          if (!spec || typeof spec !== "object" || Array.isArray(spec))
            return json(res, 400, '{"error":"decision spec must be an object"}');
          const response = await responder.decide(spec);
          json(res, response.status, response.body, response.source);
        } catch (error) {
          json(res, error instanceof SyntaxError ? 400 : 500, JSON.stringify({ error: String(error) }));
        }
      });
    },
    closeBundle() { responder?.close(); },
  };
}
