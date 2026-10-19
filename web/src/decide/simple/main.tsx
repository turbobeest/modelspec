import "../zod-config";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import SimpleApp from "./SimpleApp";
import { legacyDestination } from "./model";

const destination = legacyDestination(location.search, location.hash);
if (destination) location.replace(destination);
else {
  const root = document.getElementById("root");
  if (root) createRoot(root).render(<StrictMode><SimpleApp /></StrictMode>);
}
