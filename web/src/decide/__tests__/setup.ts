import "@testing-library/jest-dom/vitest";
import { afterEach, beforeEach, vi } from "vitest";
import { cleanup } from "@testing-library/react";

// Ordinary UI tests mock automatic decisions. Human-gate tests opt in explicitly.
// Once for statically imported modules, and again per test: a test that calls
// vi.unstubAllEnvs() would otherwise hand the next test's dynamic imports the
// CI job's VITE_*_GATE_ENABLED values.
const gatesOff = () => {
  vi.stubEnv("VITE_HUMAN_GATE_ENABLED", "false");
  vi.stubEnv("VITE_VISIT_GATE_ENABLED", "false");
};
gatesOff();
beforeEach(gatesOff);

afterEach(() => {
  cleanup();
  history.replaceState(null, "", "/decide/");
  localStorage.removeItem("modelspec-theme");
});

// jsdom has no native top layer. Browser tests exercise the real dialog.
HTMLDialogElement.prototype.showModal = function () {
  this.setAttribute("open", "");
};
HTMLDialogElement.prototype.close = function () {
  this.removeAttribute("open");
};
