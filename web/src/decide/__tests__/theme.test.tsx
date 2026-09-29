/// <reference types="node" />
import { readFileSync } from "node:fs";
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, expect, it } from "vitest";
import App from "../App";
import { THEME_KEY, initialTheme, storedTheme } from "../theme";

beforeEach(() => {
  localStorage.removeItem(THEME_KEY);
  history.replaceState(null, "", "/decide/?demo=1");
});

const pageTheme = () =>
  document.querySelector(".decide-app")?.getAttribute("data-theme");

it("opens dark on a first visit with no stored preference", () => {
  render(<App />);
  expect(pageTheme()).toBe("dark");
  expect(document.documentElement.dataset.decideTheme).toBe("dark");
  expect(screen.getByRole("button", { name: "Light mode" })).toBeInTheDocument();
});

it("remembers the visitor's toggle across visits", () => {
  const first = render(<App />);
  fireEvent.click(screen.getByRole("button", { name: "Light mode" }));
  expect(pageTheme()).toBe("light");
  expect(localStorage.getItem(THEME_KEY)).toBe("light");
  first.unmount();

  const second = render(<App />);
  expect(pageTheme()).toBe("light");
  fireEvent.click(screen.getByRole("button", { name: "Dark mode" }));
  expect(localStorage.getItem(THEME_KEY)).toBe("dark");
  second.unmount();

  render(<App />);
  expect(pageTheme()).toBe("dark");
});

it("lets a ?theme= link override the stored choice without replacing it", () => {
  localStorage.setItem(THEME_KEY, "dark");
  history.replaceState(null, "", "/decide/?demo=1&theme=light");
  render(<App />);
  expect(pageTheme()).toBe("light");
  expect(localStorage.getItem(THEME_KEY)).toBe("dark");
});

const bootScript = (() => {
  const html = readFileSync("decide.html", "utf8");
  const match = html.match(/<script>([\s\S]*?)<\/script>/);
  if (!match) throw new Error("decide.html has no inline theme script");
  return match[1];
})();

it.each(
  ["", "?theme=light", "?theme=dark", "?theme=sepia"].flatMap((search) =>
    [null, "light", "dark", "sepia"].map((stored) => [search, stored] as const),
  ),
)("paints the theme initialTheme() picks, for %j with %j stored", (search, stored) => {
  history.replaceState(null, "", `/decide/${search}`);
  if (stored) localStorage.setItem(THEME_KEY, stored);
  delete document.documentElement.dataset.decideTheme;
  new Function(bootScript)();
  expect(document.documentElement.dataset.decideTheme).toBe(
    initialTheme(location.search, storedTheme()),
  );
});

it("defaults to dark, and only a link or a stored choice makes it light", () => {
  expect(initialTheme("", null)).toBe("dark");
  expect(initialTheme("", "light")).toBe("light");
  expect(initialTheme("?theme=light", "dark")).toBe("light");
  expect(initialTheme("?theme=dark", "light")).toBe("dark");
  expect(initialTheme("?theme=sepia", "sepia")).toBe("dark");
});
