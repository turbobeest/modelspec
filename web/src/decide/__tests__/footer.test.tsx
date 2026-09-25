// MODEL-153: the live page keeps the legal pages and the neutrality commitment linked.
import { render, screen } from "@testing-library/react";
import { beforeEach, expect, it } from "vitest";
import App from "../App";

beforeEach(() => history.replaceState(null, "", "/?demo=1"));

it("links the neutrality, terms and privacy pages on every view", () => {
  render(<App />);
  const nav = screen.getByRole("navigation", { name: "Legal and API" });
  for (const [name, href] of [
    ["Neutrality", "/legal/neutrality/"],
    ["Terms", "/legal/terms/"],
    ["Privacy", "/legal/privacy/"],
  ]) {
    expect(nav.querySelector(`a[href="${href}"]`)?.textContent).toBe(name);
  }
});
