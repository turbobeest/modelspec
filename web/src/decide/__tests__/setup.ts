import "@testing-library/jest-dom/vitest";
import { afterEach, vi } from "vitest";
import { cleanup } from "@testing-library/react";

// Ordinary UI tests mock automatic decisions. Human-gate tests opt in explicitly.
vi.stubEnv("VITE_HUMAN_GATE_ENABLED", "false");

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
