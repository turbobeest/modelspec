---
status: accepted
---
# ModelSpec returns decisions; it does not carry model traffic

ModelSpec answers which model and offering should handle a task, and the caller then calls that model itself. We decided on 2026-09-24 not to act as a proxy or traffic router. A proxy would hold customers' keys and see their prompts, add latency and uptime obligations, and let us earn more from some providers' traffic than others', which breaks the published neutrality commitment. As a decision engine, ModelSpec can answer from a local snapshot at many decisions per second, never sees client content, and has no financial stake in which model wins. Revenue comes from decisions and determinations, never from traffic.
