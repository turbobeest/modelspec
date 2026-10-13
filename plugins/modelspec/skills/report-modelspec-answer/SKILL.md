---
name: report-modelspec-answer
description: Use after any ModelSpec decide, compare or rank result (MCP tool or modelspec CLI), before you write the answer to the user. Covers summary_for_user, must_mention, next_move, ties, and partial, null or no_feasible answers.
---

# Report a ModelSpec answer

ModelSpec writes `summary_for_user`, `must_mention` and `next_move` from the
decision itself, with no model in the loop. Your report carries them. It does
not improve on them.

1. Open with `summary_for_user`, unchanged.
2. Keep every `must_mention` item.
3. Name a model as the pick only when `answer.kind` is `separated`. A tie, a
   partial answer, a null answer and `no_feasible` name no pick. Don't
   recommend, shortlist, rank or "start with" a member. Don't break a tie with
   knowledge from outside the response.
4. When `next_move` is present, end with it in place of a pick:
   - `ask_user`: ask its `say` question, list its `options`, and stop until the
     user answers.
   - `decide_by_testing`: give its `steps` for its `candidates`, in the order
     given.
   - `user_tiebreak`: list its `options`. Each one is a non-quality choice that
     belongs to the user.
5. An unknown value is not a pass. Cite only figures that are in the response.

## Why

When ModelSpec names no pick, its evidence does not separate the models. A pick
you add is a guess that the user will read as ModelSpec's finding. `next_move`
is the useful step that the evidence does support.

## Example

ModelSpec returns `status: partial`, a tie between `a/x` and `b/y`, and
`next_move.kind: decide_by_testing`.

Right: the summary verbatim, each `must_mention` item, then "Next step: ..."
with the five test steps for `a/x` and `b/y`.

Wrong: "Both are strong, but I'd start with a/x."
