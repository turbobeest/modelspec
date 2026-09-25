import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { beforeEach, expect, it } from "vitest";
import App from "../App";
beforeEach(() => history.replaceState(null, "", "/?demo=1"));
it("parses Enter, shows a loading trace, and keeps the spec in the URL", async () => {
  render(<App />);
  const task = screen.getByLabelText("Describe your task");
  fireEvent.change(task, {
    target: { value: "Refactor a large Rust codebase, precision matters" },
  });
  fireEvent.keyDown(task, { key: "Enter" });
  expect(screen.getByText("Reading your task…")).toBeInTheDocument();
  await screen.findByText("Read from your task:");
  expect(location.hash).toMatch(/^#s=/);
  expect(
    screen.getByRole("region", { name: "Why this model" }),
  ).toHaveTextContent("Qualifies");
});
it("starts with constraints, searches and edits a condition, and Escape closes the editor", () => {
  render(<App />);
  fireEvent.click(screen.getByText("start from constraints"));
  fireEvent.change(screen.getByLabelText("Search facets"), {
    target: { value: "residency" },
  });
  fireEvent.keyDown(screen.getByLabelText("Search facets"), { key: "Enter" });
  expect(screen.getByText("Edit condition")).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "UK" }));
  expect(screen.getAllByText("Data residency: UK").length).toBeGreaterThan(0);
  fireEvent.keyDown(window, { key: "Escape" });
  expect(screen.queryByText("Edit condition")).not.toBeInTheDocument();
});
it("supports keyboard handles, selection, table sorting, layout and modal tabs", async () => {
  render(<App />);
  fireEvent.click(screen.getByText("start from constraints"));
  fireEvent.keyDown(window, { key: "Escape" });
  fireEvent.keyDown(screen.getByRole("slider", { name: /per task cap/ }), {
    key: "ArrowLeft",
    shiftKey: true,
  });
  expect(screen.getAllByText(/per task/).length).toBeGreaterThan(0);
  fireEvent.click(screen.getByRole("button", { name: "Table first" }));
  fireEvent.click(screen.getByRole("button", { name: "Dark mode" }));
  fireEvent.click(screen.getByRole("button", { name: "Share or act" }));
  const modal = screen.getByRole("dialog");
  fireEvent.click(within(modal).getByRole("tab", { name: "Spec YAML" }));
  expect(modal).toHaveTextContent("fictional");
  fireEvent.keyDown(window, { key: "Escape" });
  await waitFor(() =>
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument(),
  );
});
it("hides results on a simulated error and Retry restores them", () => {
  render(<App simulate="error" />);
  fireEvent.click(screen.getByText("start from constraints"));
  expect(screen.getByRole("alert")).toHaveTextContent("Couldn't load snapshot");
  expect(
    screen.queryByRole("region", { name: "Trade-off canvas" }),
  ).not.toBeInTheDocument();
  fireEvent.click(screen.getByText("Retry"));
  expect(
    screen.getByRole("region", { name: "Trade-off canvas" }),
  ).toBeInTheDocument();
});

it("Shift+Enter keeps the arrive textarea and loading hides the decision", () => {
  render(<App simulate="loading" />);
  fireEvent.keyDown(screen.getByLabelText("Describe your task"), {
    key: "Enter",
    shiftKey: true,
  });
  expect(screen.getByLabelText("Describe your task")).toBeInTheDocument();
  fireEvent.click(screen.getByText("start from constraints"));
  expect(screen.getByRole("status")).toHaveTextContent(
    "25 models, 60 offerings",
  );
  expect(
    screen.queryByRole("region", { name: "Decision table" }),
  ).not.toBeInTheDocument();
});
it("changes token-derived cost, normalised weights, axes, and default selection", () => {
  render(<App />);
  fireEvent.click(screen.getByText("start from constraints"));
  fireEvent.keyDown(window, { key: "Escape" });
  const why = screen.getByRole("region", { name: "Why this model" });
  expect(why).toHaveTextContent("Cairn 1");
  fireEvent.change(screen.getByLabelText("Input tokens per task"), {
    target: { value: "80000" },
  });
  expect(why).toHaveTextContent("80,000 ×");
  fireEvent.change(screen.getByLabelText("Weight on $ per task"), {
    target: { value: "1" },
  });
  expect(why).toHaveTextContent("Wren 7B");
  fireEvent.change(screen.getByLabelText("X axis"), {
    target: { value: "tps" },
  });
  expect(
    screen.getByRole("slider", { name: /Output throughput minimum/ }),
  ).toBeInTheDocument();
  fireEvent.change(screen.getByLabelText("Y axis"), {
    target: { value: "ReasonHard" },
  });
  expect(
    screen.getByRole("slider", { name: /ReasonHard floor/ }),
  ).toBeInTheDocument();
});
it("dismisses narrowing questions and selects a canvas point", () => {
  render(<App />);
  fireEvent.click(screen.getByText("start from constraints"));
  fireEvent.keyDown(window, { key: "Escape" });
  expect(screen.getByText("What can you spend per task?")).toBeInTheDocument();
  fireEvent.click(screen.getAllByText("Doesn't matter")[0]);
  expect(
    screen.queryByText("What can you spend per task?"),
  ).not.toBeInTheDocument();
  fireEvent.click(
    screen.getByRole("button", { name: /Fjord Code, Qualifies/ }),
  );
  expect(
    within(screen.getByRole("region", { name: "Why this model" })).getByRole(
      "heading",
      { name: "Fjord Code" },
    ),
  ).toBeInTheDocument();
});
it("restores the saved spec and respects query theme and layout", () => {
  history.replaceState(
    null,
    "",
    "/?demo=1&theme=dark&layout=table#s=" +
      btoa(
        encodeURIComponent(
          JSON.stringify({
            tokIn: 40000,
            tokOut: 4000,
            bench: "CodeBench Pro",
            w: { cap: 0.6, cost: 0.3, speed: 0.1 },
            conds: [{ f: "type", v: "llm" }, { f: "active" }],
          }),
        ),
      ),
  );
  render(<App />);
  expect(screen.getByRole("button", { name: "Table first" })).toHaveAttribute(
    "aria-pressed",
    "true",
  );
  expect(
    screen.getByRole("button", { name: "Light mode" }),
  ).toBeInTheDocument();
  expect(
    screen.getByRole("region", { name: "Decision table" }),
  ).toBeInTheDocument();
});
it("saves alert preferences locally and shows procurement clauses", () => {
  localStorage.clear();
  render(<App />);
  fireEvent.click(screen.getByText("start from constraints"));
  fireEvent.keyDown(window, { key: "Escape" });
  fireEvent.click(screen.getByRole("button", { name: "Share or act" }));
  const dialog = screen.getByRole("dialog");
  fireEvent.click(within(dialog).getByRole("tab", { name: "Save and alert" }));
  fireEvent.click(
    within(dialog).getByRole("checkbox", {
      name: "A new model beats this pick",
    }),
  );
  fireEvent.click(
    within(dialog).getByRole("button", { name: "Save and watch" }),
  );
  expect(localStorage.getItem("modelspec-sample-alerts")).toContain(
    '"alerts":[false,true,false]',
  );
  expect(dialog).toHaveTextContent("Saved locally · preview only");
  fireEvent.click(
    within(dialog).getByRole("tab", { name: "Procurement review" }),
  );
  expect(dialog).toHaveTextContent("Type: LLM");
  expect(dialog).toHaveTextContent("Yes");
});
it("can soften and remove an added condition without a reload", () => {
  render(<App />);
  fireEvent.click(screen.getByText("start from constraints"));
  fireEvent.change(screen.getByLabelText("Search facets"), {
    target: { value: "context" },
  });
  fireEvent.keyDown(screen.getByLabelText("Search facets"), { key: "Enter" });
  fireEvent.click(screen.getByRole("button", { name: "Soft" }));
  expect(
    screen.getByText(
      "Soft: models outside this are kept and flagged. It never adds points.",
    ),
  ).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Remove" }));
  expect(screen.queryByText("Edit condition")).not.toBeInTheDocument();
  expect(
    screen.queryByRole("button", { name: /Edit condition: Context/ }),
  ).not.toBeInTheDocument();
});
