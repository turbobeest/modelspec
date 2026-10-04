// MODEL-221: the per-answer "Was this answer reliable?" prompt and the page-wide control.
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { FeedbackForm, FeedbackLauncher } from "../feedback/FeedbackForm";
import { FEEDBACK_ENDPOINT, feedbackResultSchema } from "../feedback/client";
import { decisionSchema } from "../adapter/contract";
import full from "../__fixtures__/compact-full.json";

const NOT_RECORDED = {
  schema_version: "1.0",
  endpoint: "feedback",
  status: "not_recorded",
  recorded: false,
  receipt: null,
  retention_days: null,
  redacted: [],
  message: "Thank you. Feedback storage is switched off until the privacy statement covers it, so nothing was kept.",
  privacy: "https://modelspec.dev/legal/privacy/",
  service_commit: "c0ffee",
};
const RECORDED = {
  ...NOT_RECORDED,
  status: "recorded",
  recorded: true,
  receipt: "fbr_20260929_0123456789abcdef0123456789abcdef",
  retention_days: 180,
  redacted: ["email"],
};

function answering(...bodies: unknown[]) {
  const calls: { url: string; init: RequestInit }[] = [];
  const queue = [...bodies];
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string, init: RequestInit) => {
      calls.push({ url, init });
      const body = queue.shift();
      return new Response(JSON.stringify(body), { status: (body as { recorded?: boolean })?.recorded ? 202 : 200 });
    }),
  );
  return calls;
}

afterEach(() => vi.unstubAllGlobals());

describe("the per-answer prompt", () => {
  it("asks with the five fixed choices, and sends them tied to the decision", async () => {
    const calls = answering(NOT_RECORDED);
    const user = userEvent.setup();
    render(<FeedbackForm compact question="Was this answer reliable?" decisionId="dec_3f9a1c2b7d4e" template="coding" page="/decide/" />);

    const group = screen.getByRole("group", { name: "Was this answer reliable?" });
    expect(within(group).getAllByRole("radio").map((r) => r.getAttribute("value"))).toEqual([
      "reliable", "unreliable", "trustworthy", "untrustworthy", "confusing",
    ]);
    // Compact: the optional fields appear only once a choice is made.
    expect(screen.queryByLabelText(/Anything else/)).toBeNull();
    await user.click(screen.getByRole("radio", { name: "Unreliable" }));
    expect(screen.getByLabelText(/Anything else\? \(optional\)/)).toBeInTheDocument();
    expect(screen.getByLabelText(/What were you trying to decide\? \(optional\)/)).toBeInTheDocument();
    await user.type(screen.getByLabelText(/What were you trying to decide/), "a cheap coder");
    await user.click(screen.getByRole("button", { name: "Send feedback" }));

    expect(await screen.findByRole("status")).toHaveTextContent("nothing was kept");
    expect(calls).toHaveLength(1);
    expect(calls[0].url).toBe(FEEDBACK_ENDPOINT);
    expect(calls[0].init.credentials).toBe("omit");
    expect(JSON.parse(String(calls[0].init.body))).toEqual({
      rating: "unreliable",
      client: "page",
      decision_id: "dec_3f9a1c2b7d4e",
      template: "coding",
      page: "/decide/",
      trying_to_decide: "a cheap coder",
    });
  });

  it("says when it was recorded, what was removed, and can undo it by receipt", async () => {
    const calls = answering(RECORDED, { schema_version: "1.0", endpoint: "feedback", status: "deleted", recorded: false, service_commit: "c0ffee" });
    const user = userEvent.setup();
    render(<FeedbackForm question="Was this answer reliable?" decisionId="dec_3f9a1c2b7d4e" page="/decide/" />);
    await user.click(screen.getByRole("radio", { name: "Confusing" }));
    await user.type(screen.getByLabelText(/Anything else/), "mail a@b.test");
    await user.click(screen.getByRole("button", { name: "Send feedback" }));

    const status = await screen.findByRole("status");
    expect(status).toHaveTextContent("Your feedback was recorded");
    expect(status).toHaveTextContent("We removed what looked like email before it was kept");
    await user.click(screen.getByRole("button", { name: "Undo and delete it" }));
    expect(await screen.findByText("Deleted. Nothing of it is kept.")).toBeInTheDocument();
    expect(calls[1].init.method).toBe("DELETE");
    expect(JSON.parse(String(calls[1].init.body))).toEqual({ receipt: RECORDED.receipt });
  });

  it("shows the Worker's refusal instead of pretending", async () => {
    answering(undefined);
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({
      schema_version: "1.0", endpoint: "feedback", service_commit: "c0ffee",
      error: { code: "rate_limited", message: "at most 5 a minute", retry_after: 60 },
    }), { status: 429 })));
    const user = userEvent.setup();
    render(<FeedbackForm question="Was this answer reliable?" page="/decide/" />);
    await user.click(screen.getByRole("radio", { name: "Reliable" }));
    await user.click(screen.getByRole("button", { name: "Send feedback" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("at most 5 a minute");
  });
});

describe("the page-wide control", () => {
  it("is a labelled, keyboard-reachable button that opens the form", async () => {
    const user = userEvent.setup();
    render(<FeedbackLauncher page="/decide/" />);
    const button = screen.getByRole("button", { name: "Feedback" });
    await user.tab();
    expect(button).toHaveFocus();
    await user.keyboard("{Enter}");
    expect(screen.getByRole("group", { name: "What did you think of this page?" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Close feedback" }));
    expect(screen.queryByRole("group", { name: "What did you think of this page?" })).toBeNull();
  });
});

describe("the response schemas are strict", () => {
  it("refuses a field the page does not know", () => {
    expect(feedbackResultSchema.safeParse(NOT_RECORDED).success).toBe(true);
    expect(feedbackResultSchema.safeParse({ ...NOT_RECORDED, extra: 1 }).success).toBe(false);
    expect(feedbackResultSchema.safeParse({ ...NOT_RECORDED, status: "recorded" }).success).toBe(false);
  });

  it("parses the 2.10 feedback pointer on a decision, and nothing looser", () => {
    const decision = decisionSchema.parse(full);
    expect(decision.contract_version).toBe("2.14");
    expect(decision.feedback?.endpoint).toBe("https://api.modelspec.dev/v1/feedback");
    expect(decisionSchema.safeParse({ ...full, feedback: { ...full.feedback, extra: 1 } }).success).toBe(false);
  });
});
