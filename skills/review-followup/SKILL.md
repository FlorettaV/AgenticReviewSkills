---
name: review-followup
description: Keep the review records straight after a review note exists — tick rows, re-score a finding the operator corrected, park items, carry items to the end of a stack, walk through the parked items once a review's findings are all handled, tidy the map of where the team puts things (review/MAP.toml) after a review, and keep the note, review/TODO.md, the stack plan and the review log in review/LOG.md saying the same thing. Use this whenever the operator responds to findings already written down ("1 is intended, check", "tick 2 and 3", "D1 is fine", "I'll talk to them", "we decided to remove it", "note this for the end", "keep this for a recheck", "mark a cleanup on these at the end", "let's wait here", "let's go through the other finds"), and whenever a finding's premise changes after the note was written. Writes only in review/; never edits the project, never runs git writes, never runs tests unless the workspace allows it.
---

# After the note: keeping the records straight

`mr-review` writes the note and the first records. This skill handles what the
operator says about them afterwards. It is bookkeeping, done quietly and
exactly: the operator reads these files to decide what to do next, so every
place that names a finding must agree.

Anything written here that a person reads — a TODO line, a re-scored
paragraph — follows the `review-writing` skill.

## Standing constraints

**First, load and print the rules**: read
`${CLAUDE_PLUGIN_ROOT}/reference/rules.md` and print its block, with
`review-followup` as what loaded it. They hold here exactly as in a review.
This skill writes only in `review/`.

## Where each finding lives

One finding can appear in up to four places. When one changes, change all of
them in the same step.

| Place | What it holds |
|---|---|
| The note's data file, `review/mr-<n>-<branch>.toml` | The finding itself: ticked, scores, verdict, text and draft. The `.md` next to it is rendered from this file, never edited by hand |
| `review/TODO.md` | One `R` line per finding, under the MR's heading |
| The stack plan, `review/<stack>-stack-plan.md` | For a stack: the step's row, items carried to the end, watch lists |
| The review log, `review/LOG.md` | One row per review: the worst row and its verdict |

Pre-existing weaknesses go to `review/ISSUES.md` instead (the revert test in
the `mr-review` skill), never as a finding.

## TODO lines

```
- [ ] **R12** (MR 13) <title, word for word from the note>
- [ ] **R13** (MR 13 D1) <a developer finding's title, word for word>
- [ ] **A40** (MR 13) <something noticed while reviewing MR 13>
- [ ] **A41** (zoom-in MR 13 #2) <something noticed while explaining finding 2>
- [ ] **A42** (–) <something noticed outside any review>
```

- **`R`** — found by the review that was asked for. **`A`** — additional,
  noticed while doing something else.
- **The tag in brackets is where it came from.** It is what lets the
  walk-through below find a review's parked items. Every new line gets one.
  A developer finding's tag carries its `D` number, because the note numbers
  the two halves separately: "tick D1" and "tick 1" are different rows.
  Lines written before tags existed are left as they are.
- **Each letter has its own count**, R1, R2, … and A1, A2, …, and numbers
  are never reused. Find the next one per letter before adding; the `<n>`
  example lines in the file never match:

  ```
  grep -o '\*\*R[0-9]\+\*\*' review/TODO.md | tr -dc '0-9\n' | sort -n | tail -1
  grep -o '\*\*A[0-9]\+\*\*' review/TODO.md | tr -dc '0-9\n' | sort -n | tail -1
  ```
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

- Set `ticked = true` on the finding in the note's data file, **and** tick the
  TODO line.
- Add the reason to the TODO line, dated: "Operator 2026-10-12: intended; they
  will talk to the author".
- A ticked row stays where it is while its MR is open. Never delete or move a
  ticked item before then (see "When an MR is done").
- "Check" on some rows of a reply ticks those rows only.

## When the last box is ticked

When a tick leaves no open row in the note, the review's findings are done.
Look in `review/TODO.md` for open lines tagged with this review — `(MR <n>)`
and `(zoom-in MR <n> …)` — that are not the note's own findings.

If there are any, ask once, in one line, and say in half a sentence what the
list is, because the operator may never have seen it:

> All findings on MR 13 are handled. While reviewing, I parked 4 other things
> I noticed on the side (the A list in `review/TODO.md`) — go through them now?

If there are none, say only that the findings are all handled. Either way,
then tidy the map (below), if there is one.

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

## Tidy the map

When a review's findings are all handled and the project has a
`review/MAP.toml`, tidy the entries that review touched (those whose `find`
patterns match its files). Lightly: it's there to keep the map pleasant to
use, not to audit it. The `taste` skill describes the entries.

- **Without asking:** recount those entries at the current commit, update
  their counts, `direction` and `counted_at`, and add a row to
  `review/taste/scans.md`.
- **Offered, one short message, yes or no per line**, only what applies:
  - a reason the operator gave during the follow-up, as a dated `why` with
    who said it ("you said the address is written out so grep finds it; keep
    that as the why?");
  - "used in MR <n>; operator: on purpose" as evidence on an entry;
  - a status the new counts clearly moved ("mixed → moving");
  - two entries whose patterns hit the same files, to merge;
  - entries no review has matched for a long time, to move to the archive
    section at the bottom.
- **Never:** change what an entry means without the operator's yes, and
  never let a why change a status. Counts may update by themselves; meanings
  only with a yes.

Say in one line what was recounted, and wait for the answers to anything
offered.

## Showing the list

The A list keeps a review on track: what is noticed on the side waits there
instead of interrupting. It is never shown during the work. The operator hears
about it twice, at set moments (once at setup, once when a review's last box is
ticked), and sees it whenever they ask: "show the A list", "what's parked",
"show the open items".

Show it as a table, one row per line, with what it is next to every number:

| # | Status | From | What |
|---|---|---|---|
| A11 | open | zoom-in MR 13 #2 | Read-only in layers: avoid, detect, deny |

By default the open A lines; "all" adds the ticked ones, "the sweep" only the
lines under a "Sweep — … — to plan" heading, "R" the review findings. Skip the
`<n>` example lines at the top of the file.

## Re-scoring in the open

When the operator supplies a fact that changes a score — what is deployed,
what was decided, what is served — re-score where everyone can see it:

- Change the score in the data file, and keep the old value under the
  finding's `[finding.was]` (`verdict = "block"`): the note then shows
  `– (was block)`.
- Write a **Re-scored <date>.** paragraph into the finding's `rescored` field,
  which the note shows at the top of the detail block: the
  new fact, where it came from by role (the operator, the author in an MR
  comment, the deploy config — never a person's name), and what it changes.
- Update the TODO line and, if it was the worst row, the review log in
  `review/LOG.md`.
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
- **A probe that proves it** is copied into `review/probes/mr-<n>/`, so it
  outlives the session's scratchpad. The recheck instructions name it. It holds
  made-up data only, and it goes when its MR's note goes.
- **Not a stack:** a heading of its own in TODO ("Sweep — <topic> — to plan"),
  with the starting points listed.

At each later step of the stack, look at the watch list and write one line
under the item: "Step 3 checked: not touched".

## When an MR is done

`mr-review` offers, at the start of a review, to clean up notes whose MR looks
merged or closed. When the operator says yes for an MR, and only then:

- delete its note (`review/mr-<n>-*`) and its probes (`review/probes/mr-<n>/`);
- delete its ticked R and A lines from `review/TODO.md`, and the MR heading if
  nothing is left under it. Its **open** A lines stay: they are work still to
  do somewhere else;
- keep its row in `review/LOG.md`. That row, the tickets and `ISSUES.md` are
  the history that stays.

Say in one line what went. A probe that was moved into the plugin as a test
fixture is no longer in `review/` and is not touched.

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

Re-read every place you touched and check they agree: the data file, the TODO
line, the plan, the log row. Then check the data file and render the note:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/scripts/note.py render review/<the note>.toml
```

Answer in a few lines: what changed, where. No recap of findings that did not
change.
