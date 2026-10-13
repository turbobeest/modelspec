import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { DecisionLinkPage } from "./DecisionLinkPage";

const root = document.getElementById("root");
if (root) createRoot(root).render(<StrictMode><DecisionLinkPage /></StrictMode>);
