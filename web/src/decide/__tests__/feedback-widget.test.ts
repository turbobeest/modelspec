// MODEL-221: the Feedback control every pipeline-built page loads
// (pipeline/feedback_assets/feedback.js), driven in jsdom.
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// Vitest runs from web/; the script lives with the pipeline that ships it.
const WIDGET = readFileSync(resolve(process.cwd(), "../pipeline/feedback_assets/feedback.js"), "utf-8");

async function load(search = "") {
  history.replaceState(null, "", `/method/${search}`);
  document.body.innerHTML =
    '<main>page</main><a class="ms-fb-launch" href="/feedback/" data-feedback-launch>Feedback</a>';
  // The script is a classic script, run once per page load.
  new Function(WIDGET)();
}

function answering(body: unknown, status = 200) {
  const fetch = vi.fn(async () => new Response(JSON.stringify(body), { status }));
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

beforeEach(() => {
  document.body.innerHTML = "";
});
afterEach(() => vi.unstubAllGlobals());

describe("the page-wide Feedback control", () => {
  it("turns the link into a button that opens the five-choice form", async () => {
    await load();
    const link = document.querySelector<HTMLAnchorElement>("[data-feedback-launch]")!;
    expect(link.getAttribute("href")).toBe("/feedback/");
    expect(link.getAttribute("role")).toBe("button");
    link.click();
    const dialog = document.querySelector("dialog.ms-fb-dialog")!;
    expect(dialog.hasAttribute("open")).toBe(true);
    const values = [...dialog.querySelectorAll<HTMLInputElement>("input[type=radio]")].map((i) => i.value);
    expect(values).toEqual(["reliable", "unreliable", "trustworthy", "untrustworthy", "confusing"]);
    expect(dialog.textContent).toContain("Anything else? (optional)");
    expect(dialog.textContent).toContain("What were you trying to decide? (optional)");
  });

  it("sends the rating, the page path and only the text given, with no credentials", async () => {
    const fetch = answering({ status: "not_recorded", recorded: false, redacted: [] });
    await load("?spec=secret");
    document.querySelector<HTMLAnchorElement>("[data-feedback-launch]")!.click();
    const dialog = document.querySelector("dialog")!;
    dialog.querySelector<HTMLInputElement>("input[value=confusing]")!.checked = true;
    dialog.querySelector("textarea")!.value = "  which band?  ";
    dialog.querySelector("form")!.dispatchEvent(new Event("submit", { cancelable: true }));
    await vi.waitFor(() => expect(dialog.querySelector("[role=status]")!.textContent).toContain("nothing was kept"));
    const [url, init] = fetch.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("https://api.modelspec.dev/v1/feedback");
    expect(init.credentials).toBe("omit");
    expect(JSON.parse(String(init.body))).toEqual({
      rating: "confusing", client: "page", page: "/method/", note: "which band?",
    });
  });

  it("asks for a choice before sending anything", async () => {
    const fetch = answering({});
    await load();
    document.querySelector<HTMLAnchorElement>("[data-feedback-launch]")!.click();
    document.querySelector("form")!.dispatchEvent(new Event("submit", { cancelable: true }));
    expect(document.querySelector("[role=alert]")!.textContent).toContain("Choose one");
    expect(fetch).not.toHaveBeenCalled();
  });

  it("lets a local page test against a local Worker, and nothing else", async () => {
    await load("?feedback_endpoint=http://localhost:8787/v1/feedback");
    const api = (window as unknown as { ModelSpecFeedback: { endpoint(): string } }).ModelSpecFeedback;
    expect(api.endpoint()).toBe("http://localhost:8787/v1/feedback");
    await load("?feedback_endpoint=https://evil.test/collect");
    expect(api.endpoint()).toBe("https://api.modelspec.dev/v1/feedback");
  });
});
