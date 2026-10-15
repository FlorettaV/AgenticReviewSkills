---
name: review-followup
description: Keep the review records straight after a review note exists — tick rows, re-score a finding the operator corrected, park items, carry items to the end of a stack, walk through the parked items once a review's findings are all handled, and keep the note, review/TODO.md, the stack plan and the review log in REVIEW.md saying the same thing. Use this whenever the operator responds to findings already written down ("1 is intended, check", "tick 2 and 3", "I'll talk to them", "we decided to remove it", "note this for the end", "keep this for a recheck", "mark a cleanup on these at the end", "let's wait here", "let's go through the other finds"), and whenever a finding's premise changes after the note was written. Writes only in review/; never edits the project, never runs git writes, never runs tests unless the workspace allows it.
---

# After the note: keeping the records straight

`mr-review` writes the note and the first records. This skill handles what the
operator says about them afterwards. It is bookkeeping, done quietly and
exactly: the operator reads these files to decide what to do next, so every
place that names a finding must agree.

Anything written here that a person reads — a TODO line, a re-scored
paragraph — follows the `review-writing` skill.

## Standing constraints

**First, print the rules block** from the workspace `CLAUDE.md`, with
`review-followup` as what loaded it. If the workspace has no rules block, say
so in one line and carry on.

Writes only in `review/`. Read-only over the project folder, no git writes,
tests only if the workspace `CLAUDE.md` allows them — the rules hold here
exactly as in a review.

## Where each finding lives

One finding can appear in up to four places. When one changes, change all of
them in the same step.

| Place | What it holds |
|---|---|
| The note, `review/mr-<n>-<branch>.md` | The finding's row (✓ box, scores, verdict) and its detail block |
| `review/TODO.md` | One `R` line per finding, under the MR's heading |
| The stack plan, `review/<stack>-stack-plan.md` | For a stack: the step's row, items carried to the end, watch lists |
| The review log in `review/REVIEW.md` | One log row per review: the worst row and its verdict |

Pre-existing weaknesses go to `review/ISSUES.md` instead (the revert test in
the `mr-review` skill), never as a finding.

## TODO lines

```
- [ ] **R12** (MR 13) <title, word for word from the note>
- [ ] **A40** (MR 13) <something noticed while reviewing MR 13>
- [ ] **A41** (zoom-in MR 13 #2) <something noticed while explaining finding 2>
- [ ] **A42** (–) <something noticed outside any review>
```

- **`R`** — found by the review that was asked for. **`A`** — additional,
  noticed while doing something else.
- **The tag in brackets is where it came from.** It is what lets the
  walk-through below find a review's parked items. Every new line gets one.
  Lines written before tags existed are left as they are.
- **Numbers continue from the highest in the file** and are never reused.
  Check before adding: `grep -o '\*\*[RA][0-9]*' review/TODO.md | sort -V | tail`.
- The text follows the title rules in `review-writing`.

## Parking

Anything that surfaces and is not the item in hand goes into TODO
**silently** — no "I've added this to the list", no summary of what was
parked. The list is checked when the operator chooses to check it, and at the
end of a review (below).

## Ticking

The operator decides when a row is handled. Tick (`[ ]` → `[x]`) when they say
it is understood, intended, ticketed, will be talked about, or fixed — "1 is
intended, check", "I can see the replacement ticket, check". Do not tick on
your own judgement.

- Tick the note's row **and** the TODO line.
- Add the reason to the TODO line, dated: "Operator 2026-10-12: intended; they
  will talk to the author".
- A ticked row stays where it is. Never delete or move a ticked item.
- "Check" on some rows of a reply ticks those rows only.

## When the last box is ticked

When a tick leaves no open row in the note, the review's findings are done.
Look in `review/TODO.md` for open lines tagged with this review — `(MR <n>)`
and `(zoom-in MR <n> …)` — that are not the note's own findings.

If there are any, ask once, in one line:

> All findings on MR 13 are handled. This review also parked 4 other items —
> go through them now?

If there are none, say only that the findings are all handled.

If the operator says yes, go through them **one at a time**. Show one item,
in one or two sentences, and offer the four choices:

| Choice | What happens to the line |
|---|---|
| ticket | Ticked, with "ticket: <where>" and the date |
| issue | Moved into `review/ISSUES.md` as a new issue; the TODO line is ticked with "→ ISS-<n>" |
| drop | Ticked, with "dropped" and the date. The line stays |
| keep | Left open. Nothing changes |

Wait for the answer before showing the next item. When the list is done, say
how many went each way, in one line. If the operator stops halfway, the
remaining lines simply stay open.

## Re-scoring in the open

When the operator supplies a fact that changes a score — what is deployed,
what was decided, what is served — re-score where everyone can see it:

- Change the row, and show where it came from: `` `–` (was `block`) ``.
- Add a **Re-scored <date>.** paragraph at the top of the detail block: the
  new fact, who gave it, and what it changes.
- Update the TODO line and, if it was the worst row, the review log in
  REVIEW.md.
- If the change leaves something behind (a recheck before merge, a smaller
  finding), say so in the same paragraph.

A score that quietly keeps its number after its premise is gone is how the
table stops being believed. One that quietly drops is no better.

## Carrying items forward

"Note this for the end", "keep it stored to see if we catch it", "I'll mark a
cleanup at the end":

- **For a stack:** a section in the stack plan — "Carried through the stack —
  recheck at the end", "Comment cleanup — once, at the end", "Linter — once,
  at the end". Each item names where it came from, which later steps touch the
  same code (a watch list), what "fixed" looks like, and how to recheck it.
- **A probe that proves it** is copied into `review/probes/`, so it outlives
  the session's scratchpad. The recheck instructions name it.
- **Not a stack:** a heading of its own in TODO ("Sweep — <topic> — to plan"),
  with the starting points listed.

At each later step of the stack, look at the watch list and write one line
under the item: "Step 3 checked: not touched".

## Pausing

"Let's wait here": write in the plan and on the TODO line where it stopped,
why, and what to check first when it resumes — usually that the branch heads
have not moved (list them with the commits already reviewed).

## Stay in the review you are in

A follow-up is about the review in hand. Ticking, re-scoring or fixing a
format applies to that note only. Another note is touched only when the
operator names it. If the same thing clearly applies elsewhere, park one `A`
line in TODO.

## Before you answer

Re-read every place you touched and check they agree: the ✓ box, the verdict,
the TODO line, the plan, the log row. Then run the note checker:

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/review-writing/check_note.py review/<the note>.md
```

Answer in a few lines: what changed, where. No recap of findings that did not
change.
