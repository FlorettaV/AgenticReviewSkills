---
name: mr-review
description: Review a merge request against review/REVIEW.md in two halves — customer (what a customer or operator experiences, scored on chance and harm) and code (what the next developer runs into, walked rule by rule) — with branch identity, verified findings tables, architecture and rules checks, disposition. Use this whenever the operator asks to review an MR, a branch, or a set of changes ("review MR 13", "can we do a review on feat/x", "what do you think of this branch", "code only review of SWD-12", "just the customer side"), when they ask to add the missing half to an existing note ("now do the code side too"), and when they ask what changed on a branch or whether a change is safe to merge. Read-only: it never edits the project, never runs git writes, and runs tests only if the workspace allows it.
---

# Reviewing an MR

`review/REVIEW.md` is the project's review standard: the rules, the
architecture we measure against, how each score column is scored, the note
shape and the review log. It is rewritten as reviews teach it things, so **read
it first, every time**. This skill is the working method, and it fixes the parts
that are the same in every project: the score columns and the records. How
anything is worded belongs to the `review-writing` skill.

If the workspace has no `review/REVIEW.md`, stop before reviewing and offer the
`review-setup` skill. A review without a standard has nothing to score against.

## Two halves: customer and code

A review asks two different questions, and each gets its own pass, its own
table and its own columns in the note:

| Half | The question | Table in the note | Numbers |
|---|---|---|---|
| **customer** | What does a customer or an operator experience if this merges? Behaviour, looks, security, GDPR, what gets logged or cached | What the customer experiences | `1`, `2`, … |
| **code** | What does the next developer run into? The §2 rules of `REVIEW.md`, walked one by one | What the developer sees | `D1`, `D2`, … |

**Both run by default.** The operator can ask for one: "customer only", "code
only". A half that did not run keeps its section in the note, with one line:

```
Not run: code-only review (operator, <date>).
```

That says the ground was not walked, so nobody reads a missing table as "no
problems". **A code-only review states at the top of the note, under the
header: "Security and GDPR not checked."** A quick code pass must not pass for a
full review.

**"Now do the other half"** on an existing note runs the missing pass and
fills its section. Numbers carry on from what is there; nothing already
published is renumbered.

**The half is where we looked, not how bad it is.** One `block` rule holds in
both tables: a blocking row names what someone experiences if this merges as
it stands. A nit cannot name that, so it cannot block. A crash, a red suite, a
server that will not start, a wrong result: those can, whichever pass found
them.

**A bug the code pass finds goes to the customer table** when both halves
run, scored on Chance and Customer like any other. In a code-only review it
stays in the developer table, may `block`, and its Rule cell says
`customer-visible`, so a later customer pass knows it was not scored for
Chance. One bug never appears in both tables.

## The workspace

A review workspace has two folders side by side:

- **The project folder**, the code under review. Read-only.
- **`review/`**, where the review lives. Writable.

The workspace `CLAUDE.md` names the project folder and says what this
environment has and lacks: the linter command, whether tests may be run, the
code host and its CLI, the default branch. Read it rather than assuming. Where
this skill writes `origin/main`, it means the remote's default branch.

`review/` holds:

```
REVIEW.md                 the project's review standard. Read first, every time
ISSUES.md                 pre-existing weaknesses a review bumped into
TODO.md                   open items — R = review found, A = additional
<stack>-stack-plan.md     one per stack of branches
probes/                   probe scripts worth keeping past the session
mr-<n>-<branch-slug>.md   one note per merge request
```

`REVIEW.md` lists the project's own rule documents (coding rules, conventions,
glossary, repo rules). Read the ones it names before judging any code.

## Standing constraints

**First, print the rules block** from the workspace `CLAUDE.md`, with
`mr-review` as what loaded it. The operator uses it to see the rules were
re-read, so it comes before any other output. If the workspace has no rules
block, say so in one line and carry on.

The constraints, repeated here because breaking one silently invalidates the
review and the operator should never have to restate them:

- **Read-only over the project folder.** No edits, however small or obvious. A
  fix belongs in a review comment, not in the tree. `review/` is writable.
- **No git writes.** No `commit`, `add`, `push`, `pull`, `merge`, `checkout`,
  `branch`, `stash`, `reset`. Reading is expected: `log`, `diff`, `show`,
  `grep`, `merge-base`, `archive`.
- **Tests run only if the workspace `CLAUDE.md` allows it.** If it forbids them
  or says nothing, do not run any, not even one. The review ends with the exact
  commands for the operator to run. A throwaway script that exercises the code
  and prints a measurement is *not* the suite — it is encouraged, and it is the
  difference between a claim and a fact.
- **The linter is the command the workspace `CLAUDE.md` gives.** If it gives
  none, find the configured one and say in the note which command you ran.

## The method

### 1. Identity before anything

MRs are identified by branch. When there is no code-host CLI (`gh`, `glab`) in
the environment, the number-to-branch mapping has to be confirmed by hand.

```
git merge-base origin/main origin/<branch>
git log --format='%h %an %ad %s' --date=short origin/main..origin/<branch>
git log --format='%h %ad %s' --date=short origin/<branch>..origin/main   # drift
git diff --stat <base>..origin/<branch>
```

A branch that is `0 ahead / n behind` is already merged. Check before reviewing
a ghost.

**A stacked branch** (one built on another open branch) is diffed against the
branch directly below it, not against `main`: the step below has its own
review. Check the ancestry with `git merge-base --is-ancestor <below> <this>`,
and keep a plan file (`review/<stack>-stack-plan.md`) with one row per step and
the commit each was reviewed at.

### 2. Read the intent, then the code

If the branch carries a design doc or a detailed commit body, read it first —
it tells you what the author *considered*, and the gap between that list and the
code is where most real findings live.

### 3. The two standing checks

Both of these have produced the majority of real findings. Run them every time.

**Who else reads this?** For any value the change adds to a shared structure —
a field on a shared object, a logged record, a cache key, a template slot —
enumerate every consumer and check each one. Most findings are not in the new
code. They are in old code that suddenly receives something it was never given
before.

**Does the test actually test it?** Read what the assertion reads, not what it
is named. A test that checks the page the customer sees does not cover what
gets logged, cached or e-mailed.

### 4. Ask whether it was decided or missed

For anything that looks wrong, work out whether the author *chose* it before
writing it up — the answer changes the verdict, and the evidence is usually
right there. Three things to look at:

- **What the commit body and the design doc list.** An author who names three
  things the change affects and handles each carefully, then never mentions a
  fourth, almost certainly did not see the fourth. That is the strongest signal
  available.
- **Whether anything reads it.** If a value were being kept deliberately,
  something would read it. Nothing reading it back is strong evidence of a
  leftover.
- **What the author's own stated model implies.** "Same as the invoices" is a
  commitment — go and look at how invoices are actually handled.

When the evidence is genuinely ambiguous, that is a `talk`, not an assertion in
either direction. Guessing at intent and being wrong costs the review more
credibility than asking does.

### 5. Confirm what is actually deployed before scoring Chance

Chance is *"how often a customer hits the visible effect"*, so it depends on
facts a reviewer cannot read off the code: who is actually served, which
settings are live, whether the code that would read a bad value runs at all.
Ask.

This routinely moves a score by several points in either direction, and the
answer often turns up a better finding than the one it retires. A bug that
needs two shops cannot fire when only one runs, but that one shop may still
show something wrong. Re-score openly when the operator supplies context. A
finding that quietly keeps its number after its premise is corrected is how the
whole table stops being believed.

### 6. When a change touches one of a set, check the whole set

Most partial changes are not visible in a diff, because the diff only shows what
moved. Four of nine buttons get the new colour. Six error paths catch the same
failure, and two of them log it. Whenever a change edits *one* member of a
group — a stylesheet rule, an error path, one of four payment methods, one of
two databases — list the group and ask what the other members now disagree
with.

### 7. Sort what you find

| | Destination |
|---|---|
| Defect in the new code | Finding |
| New code hands old code something it never got before, and it breaks | **Finding** — the MR caused it, so the MR owns it |
| Pre-existing weakness the change merely revealed | `review/ISSUES.md` |

**The revert test** separates the last two: *would this still be broken if the
MR were reverted?* No → finding. Yes → issue. "The old code was fragile" does
not move responsibility for a regression onto the old code.

### 8. When it is too big for one pass

A diff whose findings cannot all be verified in one sitting gets split, at
commit boundaries, by topic (removals, a rewritten module, logging, ...). One
note still covers the branch; its header lists which commits belong to which
topic.

Topics can go to sub-agents (forks) in parallel. They report back drafts (see
`review-writing`); they never write to `review/`. Every draft a sub-agent
proposes is re-checked before it goes into the note: print its cited lines,
re-run its probe or read the code it quotes. The topic most likely to hold a
GDPR or security finding is reviewed directly, not delegated.

### 9. Prove it before you write it

A finding that can be demonstrated is worth five that are argued. Write a small
script in the scratchpad that runs the code in question (in Python: imports the
module) and prints the behaviour with and without the change.
`git archive <branch> <path> | tar -x` gives you the branch's code without
touching the working tree.

Then verify every citation. Line numbers are **on the MR branch, never on
main** — an inserted hunk shifts everything below it:

```
git grep -n -F "<exact text>" origin/<branch> -- <path>
```

`git grep` returns every hit, and the first is often the wrong one. Print them
all and pick deliberately. Mark what the MR actually changed: `✎` prefixes a
line the MR touches, anything after `→` is unchanged code the change *reaches*.
Confirm with `git diff -U0 <base>..origin/<branch> -- <file>`.

Steps 1–9 are the customer half. Steps 1, 2 and 9 also serve the code half,
which adds step 10.

### 10. The code pass: every §2 rule, by name

The customer half finds what breaks. This pass finds what the next developer
trips over, and it has to be walked on purpose, because a reviewer looking for
bugs reads straight past a stale comment.

Take the rules in `REVIEW.md` §2 **one at a time**, in their order, and hold
every changed hunk against each. Not "does anything look off", but, for
example:

- **Readable**: does every comment the MR adds or sits next to still say what
  the code does? Would a name make someone open the function to find out what
  it is?
- **Manageable**: what does the next change to this code have to touch? Is one
  fact now written in two places, kept the same by nothing?
- **Simple**: does each new parameter, sentinel, fallback or setting earn its
  place? What would the code look like without it?
- **Focused**: does the MR also change something its title does not mention?
- **Tested**: does each new test fail when the behaviour breaks, or only when
  the text changes?

The rules are the project's, so the list is whatever §2 holds. A rule that is
not worth checking is rewritten or dropped in `REVIEW.md`, never quietly skipped
here.

**Write down what each rule turned up, "nothing" included**, in the note's
"Rules walked" list (below). A rule with no line in that list was not walked.
That list is the guard: a skipped rule becomes visible.

Every developer finding is verified like any other (step 9): print the lines,
run the probe. "This test only checks the text" is proven by showing the
change it lets through.

## Output

### The columns

Fixed, the same in every project. `REVIEW.md` says how each is scored there.
Both tables share these:

| Column | |
|---|---|
| ✓ | `[ ]` until the operator says the row is handled. The reviewer leaves every box empty |
| # | The finding's number: `1`, `2`, … in the customer table, `D1`, `D2`, … in the developer table. It never changes once published |
| Finding | The title, written by `review-writing` |
| Fix effort | How much work the fix is |
| Verdict | `block`, `ticket`, `talk` or `–` |
| Cause ✎ → Effect | Where to start reading |

**What the customer experiences** adds, between Finding and Fix effort:

| Column | |
|---|---|
| Chance | How often a customer hits the visible effect |
| Customer | How bad it is for the customer when it happens |
| Security | Does it let someone do what they should not be able to |
| GDPR | Does it expose, mix or over-retain personal data |
| Arch | Does it move away from the target architecture or break a rule |
| Layers | How many separate places absorb this one failure |

```
| ✓ | # | Finding | Chance | Customer | Security | GDPR | Arch | Layers | Fix effort | Verdict | Cause ✎ → Effect |
```

**What the developer sees** adds:

| Column | |
|---|---|
| Rule | The §2 rule it breaks, by its heading's first word: `Readable`, `Simple`, … `customer-visible` for a bug in a code-only review |
| Next change | How much it costs the next developer who touches this code |

```
| ✓ | # | Finding | Rule | Next change | Fix effort | Verdict | Cause ✎ → Effect |
```

### Writing the note

**Load the `review-writing` skill now** (`review:review-writing`), and follow its three steps:

1. **Draft** every finding in its draft shape, from what steps 1–10 verified.
2. **Write** the note from the drafts. Each half's section holds its table,
   then for **every** finding, in table order, its detail block: `### 3. …` in
   the customer half, `### D2. …` in the developer half. One heading per
   finding: no grouped `### 8–11`, no prose-only block, no heading that renames
   the finding. The developer half ends with the "Rules walked" list: one line
   per §2 rule, naming the findings it produced, or "nothing". The rest of the
   note follows the section list in `REVIEW.md`.
3. **Edit**: run the editor pass, then the checker. Both are described there.

Then print the content at every cited line on the branch and read it back one
last time.

Sections with nothing to say are kept and marked "not touched". An empty
section is information — it says the ground was walked.

Two things are worth stating plainly in every note, because they are what the
operator actually decides on:

- **What blocks merge**, argued rather than asserted. A blocking row names the
  specific thing a customer or an operator would experience if this merged as
  it stands. Anything less is a ticket.
- **What could not be checked**, and why. An unrun linter is a gap in the
  review, not a silent pass.

### The reply

Short, as `review-writing` describes under "Replying": both findings tables in
full (or the one that ran, with a line saying which did not), what blocks, the
questions for the operator, the commands. The What / Why / Fix stays in the
note until the operator asks; the `zoom-in` skill produces it.

### On publishing

Three small writes, then hand over to `review-followup` for everything the
operator says afterwards:

- a row in the review log in `review/REVIEW.md`. Its worst row may be a `D`
  row; say which half a single-half review covered;
- one `R` line per finding in `review/TODO.md`, under a heading for this MR,
  developer findings tagged with their number: `(MR <n> D1)`;
- for a stack, the step's row in the plan file.

## Parking what you did not come for

A review turns up things that are not this MR's job. They go in `review/TODO.md`
**silently** — no "I've added this to the list", no summary of what was parked.
Each parked line carries the review it came from, `(MR <n>)`, so the
end-of-review walk-through in `review-followup` can find it. Line format and
numbering are in `review-followup`.

This matters more than it sounds. A reply carrying six related findings buries
the one question that was asked, and the reviewer stops being useful exactly
when they become thorough.

## Stay in the review you are in

A question asked during a review is about **this** review — the branch, the
note and the findings in hand. That holds for meta questions too: "why does
this table look weird", "the titles sound off", "can you check the format".
Answer and fix them in the current note only.

Other notes, earlier reviews and other branches are touched only when the
operator names them ("check all of today's notes", "fix step 2 too"). If the
same problem obviously exists in another note, park one line in
`review/TODO.md`, silently, as for any side-quest — do not go and fix it.

A fix that spreads to four notes turns one question into a session.
