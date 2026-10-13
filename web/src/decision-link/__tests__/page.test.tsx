import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";

const decisionId = "dec_3a97fadf7a200027c618b3a3";
const capsule = "signed-inputs.signature";
const summary = {
  decision_id: decisionId,
  snapshot: { id: "snap_pinned", content_hash: "sha256:pinned-content" },
  summary_for_user: "Alpha fits the requirements you applied.",
  must_mention: ["The answer uses the pinned snapshot.", "Task type was not applied."],
  requirements: {
    applied: { where: [{ facet: "model.weights_open", op: "eq", value: true }], optimize: { max: "software_engineering" }, unknowns: "exclude", task_tokens: 2000 },
    not_applied: ["task_type"],
  },
};
const json = (value: unknown, status = 200) => new Response(JSON.stringify(value), { status });

beforeEach(() => {
  vi.resetModules();
  vi.stubEnv("VITE_VISIT_GATE_ENABLED", "true");
  vi.stubEnv("VITE_TURNSTILE_SITE_KEY", "public-test-key");
  history.replaceState(null, "", `/d/${decisionId}?token=${capsule}`);
  window.turnstile = {
    render: vi.fn((container, options) => {
      const button = document.createElement("button");
      button.textContent = "Verify fixture";
      button.onclick = () => options.callback("single-use");
      container.append(button);
      return "widget";
    }),
    remove: vi.fn(),
  };
});

afterEach(() => {
  delete window.turnstile;
  vi.unstubAllGlobals();
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
});

function serve({ enabled = true, response = json(summary) }: { enabled?: boolean; response?: Response } = {}) {
  const requests: { url: string; options?: RequestInit }[] = [];
  vi.stubGlobal("fetch", vi.fn(async (url: string, options?: RequestInit) => {
    requests.push({ url, options });
    if (url.endsWith("/human-status")) return json(enabled ? { enabled: true, mode: "visit", day_limit: 300, burst_limit: 30 } : { enabled: false });
    if (url.endsWith("/visit-token")) return json({ token: "human-visit", expires_at: Math.floor(Date.now() / 1000) + 1800 });
    if (url.endsWith("/decision-link")) return response;
    throw new Error(`Unexpected request ${url}`);
  }));
  return requests;
}

it("verifies the human visit before posting the capsule and shows only summary-level content", async () => {
  const requests = serve();
  const { DecisionLinkPage } = await import("../DecisionLinkPage");
  render(<DecisionLinkPage />);
  const verify = await screen.findByRole("button", { name: "Verify fixture" });
  expect(requests.map(({ url }) => url)).toEqual(["https://api.modelspec.dev/v1/human-status"]);
  expect(screen.queryByText(summary.summary_for_user)).not.toBeInTheDocument();
  fireEvent.click(verify);
  expect(await screen.findByText(summary.summary_for_user)).toBeVisible();
  const caveats = screen.getByRole("region", { name: "What to keep in mind" });
  expect(within(caveats).getByText(summary.must_mention[0])).toBeVisible();
  expect(within(caveats).getByText(summary.must_mention[1])).toBeVisible();
  expect(screen.getByRole("region", { name: "Applied requirements" })).toHaveTextContent("model.weights_open");
  expect(screen.getByRole("region", { name: "Pinned snapshot" })).toHaveTextContent("snap_pinned");
  expect(screen.getByRole("region", { name: "Pinned snapshot" })).toHaveTextContent("sha256:pinned-content");
  expect(screen.queryByRole("table")).not.toBeInTheDocument();
  expect(screen.queryByRole("link")).not.toBeInTheDocument();
  expect(document.body).not.toHaveTextContent(capsule);
  expect(localStorage.length).toBe(0);
  expect(sessionStorage.length).toBe(0);
  const request = requests.find(({ url }) => url.endsWith("/decision-link"));
  expect(request?.options).toMatchObject({ method: "POST", cache: "no-store", referrerPolicy: "no-referrer", body: JSON.stringify({ decision_id: decisionId, token: capsule }) });
  expect(new Headers(request?.options?.headers).get("X-ModelSpec-Visit-Token")).toBe("human-visit");
  expect(new Headers(request?.options?.headers).get("Authorization")).toBeNull();
});

it.each([false, true])("refuses to request private content when build gate enabled is %s and Worker gate is off", async (buildEnabled) => {
  vi.stubEnv("VITE_VISIT_GATE_ENABLED", String(buildEnabled));
  const requests = serve({ enabled: false });
  const { DecisionLinkPage } = await import("../DecisionLinkPage");
  render(<DecisionLinkPage />);
  expect(await screen.findByRole("alert")).toHaveTextContent(/Human verification is temporarily unavailable/);
  expect(requests.filter(({ url }) => url.endsWith("/decision-link"))).toHaveLength(0);
  expect(screen.queryByText(summary.summary_for_user)).not.toBeInTheDocument();
});

it("never sends the capsule if human status is unavailable", async () => {
  const requests = serve();
  vi.mocked(fetch).mockResolvedValue(json({ error: "unavailable" }, 503));
  const { DecisionLinkPage } = await import("../DecisionLinkPage");
  render(<DecisionLinkPage />);
  expect(await screen.findByRole("alert")).toHaveTextContent(/Human verification is temporarily unavailable/);
  expect(requests).toHaveLength(0);
});

it.each([404, 409, 410])("shows an unavailable-link notice for HTTP %s without showing request data", async (status) => {
  const requests = serve({ response: json({ error: { code: "decision_link_unavailable", message: "server-details" } }, status) });
  const { DecisionLinkPage } = await import("../DecisionLinkPage");
  render(<DecisionLinkPage />);
  fireEvent.click(await screen.findByRole("button", { name: "Verify fixture" }));
  expect(await screen.findByRole("alert")).toHaveTextContent(status === 410 ? /expired/ : /unavailable/);
  expect(document.body).not.toHaveTextContent("server-details");
  expect(document.body).not.toHaveTextContent(capsule);
  expect(requests.filter(({ url }) => url.endsWith("/decision-link"))).toHaveLength(1);
});

it("renders response strings as text and discards any full results data", async () => {
  serve({ response: json({ ...summary, summary_for_user: '<script>alert("private")</script>', results: [{ model: "secret-table-row" }] }) });
  const { DecisionLinkPage } = await import("../DecisionLinkPage");
  render(<DecisionLinkPage />);
  fireEvent.click(await screen.findByRole("button", { name: "Verify fixture" }));
  expect(await screen.findByText('<script>alert("private")</script>')).toBeVisible();
  expect(document.querySelector("main script")).toBeNull();
  expect(document.body).not.toHaveTextContent("secret-table-row");
});

it("rejects an incomplete summary response", async () => {
  serve({ response: json({ decision_id: decisionId, summary_for_user: "Incomplete answer" }) });
  const { DecisionLinkPage } = await import("../DecisionLinkPage");
  render(<DecisionLinkPage />);
  fireEvent.click(await screen.findByRole("button", { name: "Verify fixture" }));
  expect(await screen.findByRole("alert")).toHaveTextContent(/unavailable/);
  expect(screen.queryByText("Incomplete answer")).not.toBeInTheDocument();
});

it("does not request anything for a missing capsule", async () => {
  history.replaceState(null, "", `/d/${decisionId}`);
  const requests = serve();
  const { DecisionLinkPage } = await import("../DecisionLinkPage");
  render(<DecisionLinkPage />);
  expect(await screen.findByRole("alert")).toHaveTextContent(/incomplete/);
  await waitFor(() => expect(requests).toHaveLength(0));
});
