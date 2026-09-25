# Verification log

Written by `decision/verify.py` (MODEL-140). See
[`docs/decision-verification.md`](../docs/decision-verification.md).

- `log.jsonl`: append-only, one `decision.model.Verification` per line. The
  latest outcome per target wins (latest `date`; on a tie, the later line).
  `decision/snapshot.py` reads every `*.jsonl` file in this directory as the log,
  so put nothing else here with that suffix.
- `queue/events.jsonl`: the work queue (claims filed by collectors, re-queues
  from source change detection, checks done). Not read by the snapshot.

Never edit or delete a line. A correction is a new line.
