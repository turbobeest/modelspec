import { z } from "zod";

// The site's CSP forbids eval; zod's JIT probe would trip it on every load.
z.config({ jitless: true });
