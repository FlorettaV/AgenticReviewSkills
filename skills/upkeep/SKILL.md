---
name: upkeep
description: Check the state of everything the review skills read in a workspace — REVIEW.md, the project's rule documents, the map (review/MAP.toml), TODO.md, ISSUES.md, LOG.md and the notes — and offer a short list of trims and questions that make it cheaper to read and decide on, for the operator and for Claude. Finds the same rule written twice, rules that contradict each other, rules without a reason, stale items, unexplained terms, and files that are loaded whole but needed only in part. Use when the operator asks to "tidy up", "check the state of our review files", "what's stale", "clean up the rules", "upkeep", or every so often between reviews. Writes only in review/, and only what the operator says yes to.
---

# Keeping the review files cheap to use

Every file the review skills read costs something each time it's read: the
operator's attention, and Claude's. Files grow one review at a time, and
nothing trims them by itself. This skill looks at their state and offers
trims. Why the skills care: `${CLAUDE_PLUGIN_ROOT}/docs/how-people-place-things.md` ("cheap for
Claude too", "one unknown word costs the whole paragraph").

It's light by design: one pass, one short list, then the operator decides.
`review-followup` already tidies the map after each review; this is the wider
check, run now and then.

## The rules

Load and print the rules block from `${CLAUDE_PLUGIN_ROOT}/reference/rules.md`, with `upkeep` as
what loaded it. The project is read-only. In `review/`, nothing changes
without the operator's yes, except what this file marks as automatic.

## What it reads

The workspace `CLAUDE.md`, `review/REVIEW.md`, the rule documents it names
(read only, never changed here), `review/MAP.toml`, `review/TODO.md`,
`review/ISSUES.md`, `review/LOG.md`, and the notes in `review/`.

## What it looks for

1. **The same rule in two places.** In `REVIEW.md` and a rule document, in
   `REVIEW.md` and the map, or twice in `REVIEW.md` with different words.
   Claude has to work out whether they're one rule or two, and sometimes
   guesses wrong. Offer: keep it in one place, and point to it from the
   other.
2. **Rules that disagree.** `REVIEW.md` against a rule document, a rule
   document against the map's counts ("the docs say X, the code does Y in 200
   places"). Never resolved here: each becomes a question for the team, with
   the likely answer and the numbers, as in the `taste` skill.
3. **Rules without a reason.** A rule with no "because" gets applied too
   literally. Offer to add one line of why, only from the operator or a
   document, never invented.
4. **No order of importance.** A long list of rules with equal weight.
   Offer an order, or a short "what matters most".
5. **Stale things.**
   - notes whose MR is merged or closed (offer the deletion `review-followup`
     describes under "When an MR is done");
   - open TODO lines older than a few months, offered as ticket, issue, drop
     or keep, one at a time;
   - issues in `ISSUES.md` whose code has changed since (look at the cited
     lines: still there?);
   - map entries no review has matched for a long time, and whys marked "may
     be out of date".
6. **Unexplained words.** Terms, labels or abbreviations used in `REVIEW.md`
   or the map without their meaning nearby, and not in the plugin's
   `${CLAUDE_PLUGIN_ROOT}/docs/glossary.md`. Offer a plain rewording, or a
   line in the glossary: the plugin's for words every project shares, a
   glossary section in `REVIEW.md` for the project's own.
7. **Loaded whole, needed in part.** A section that only matters for some
   reviews (one area, one kind of change) sitting in a file read every time.
   Offer to move it to its own file, read when that kind of change comes up.
8. **Questions waiting for the team.** `ask_team` lines on the map, and
   `talk` findings in notes that never got an answer. List them, so the
   operator can pick a good moment to ask.

**Automatic, no question:** fixing a pointer to a file that moved, and
re-sorting the LOG by date. Everything else is offered.

## The list

One message, at most about ten lines, the cheapest wins first. Each line:
what was found, in plain words, the proposed trim, and what it saves
("REVIEW.md and AGENTS.md both describe the module layout, in different
words. Keep AGENTS.md's and point to it from REVIEW.md? One less thing to
keep in step."). The operator answers per line: yes, no, or later.

Apply the yeses, then say in one line what changed. A "later" is left as it
is and comes back next time. Never more than one round per run.
