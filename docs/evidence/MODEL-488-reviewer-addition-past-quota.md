# MODEL-488: a reviewer-added lineup member is not cut by a full quota

The approved rule (`premier/README.md`, clause 4) says: "A model is in the set
if any of these holds: ... A reviewer added it."

## What the code did

A live proposal (`scripts/premier_slice1.py --data-dir`) read a clause-4 note
from the reviewed `premier/slice-1.yaml`, put the model in its group's
candidate list, and then stopped filling that group at its quota. The only
reviewer addition so far, `typesafe/jev-1-13`, is alone in the decision group
(quota 1), so the cut never showed. A reviewer-added model in a full group
such as frontier-generation was removed from the proposal even though a
reviewer had added it.

## What it does now

In a live proposal a member with a reviewer's clause-4 note is kept whatever
its group's quota says.

- It is seated after every quota fill, so it takes no seat from another model.
  Models the quota kept before are still kept.
- Its row lists clause 4 with the reviewer's note, and it is not listed in
  `near_misses`, so no "not needed to fill a quota" reason is written for it.
- It is counted in `counts.reviewer_additions_past_quota` and
  `counts.reviewer_additions_past_quota_by_group`, apart from
  `over_quota_top10`. A reviewer addition that fits inside its quota is not
  counted.
- A note that is empty, or the admission placeholder text "Admission packet for
  human review", does not protect (the filter in `scripts/premier_live.py` is
  unchanged).
- A retired (sunset) model is not brought back. It stays in `archived`.
- The proposal carries the clause-4 note forward on the row, so the next
  proposal reads it again and keeps the model.
- The approved-file path (`--check` with no `--data-dir`) is unchanged.

## How a reviewer addition is recorded

Add a clause-4 entry to the model's row in the reviewed lineup file with a
note that says who decided, when, and why. An entry has no separate fields for
these, so they go in the note text.
