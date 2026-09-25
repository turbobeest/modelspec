import { render } from "@testing-library/react";
import { beforeEach, expect, it } from "vitest";
import App from "../App";

beforeEach(() => history.replaceState(null, "", "/?demo=1"));

function headerMark(container: HTMLElement) {
  const mark = container.querySelector(".global-header .brand svg");
  if (!mark) throw new Error("no mark in the header");
  return mark;
}

it("renders the 2a mark in the header, with the package's ids and colours", () => {
  const { container } = render(<App />);
  const mark = headerMark(container);
  expect(mark.getAttribute("viewBox")).toBe("0 0 40 40");
  expect(
    ["tile", "y-axis", "x-axis", "m", "dots"].map(
      (id) => mark.querySelector(`#${id}`)?.id,
    ),
  ).toEqual(["tile", "y-axis", "x-axis", "m", "dots"]);
  expect(mark.querySelector("#tile")?.getAttribute("fill")).toBe("#0B1426");
  expect(mark.querySelector("#y-axis")?.getAttribute("stroke")).toBe("#F2C94C");
  expect(mark.querySelector("#x-axis")?.getAttribute("stroke")).toBe("#3FB68B");
  expect(mark.querySelector("#m")?.getAttribute("stroke")).toBe("#FFFFFF");
  expect(mark.querySelector("#dots")?.getAttribute("fill")).toBe("#5AA9EC");
  expect(mark.querySelector("#dots")?.getAttribute("stroke")).toBe("#0B1426");
  expect(mark.querySelectorAll("#dots circle")).toHaveLength(5);
  expect(mark.querySelector("metadata")).toBeNull();
  expect(container.querySelector(".global-header .brand")).toHaveTextContent(
    "ModelSpec",
  );
});

it("uses the transparent mark in dark mode, where the tile matches the page", () => {
  history.replaceState(null, "", "/?demo=1&theme=dark");
  const { container } = render(<App />);
  const mark = headerMark(container);
  expect(mark.querySelector("#tile")?.getAttribute("fill")).toBe("none");
  expect(mark.querySelector("#dots")?.getAttribute("stroke")).toBe("none");
  expect(mark.querySelector("#m")?.getAttribute("stroke")).toBe("#FFFFFF");
});
