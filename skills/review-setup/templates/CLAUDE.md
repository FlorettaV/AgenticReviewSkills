# Working rules for this workspace

Standing instructions. They do not expire at the end of a session and do not
need repeating.

## 1. Read-only over `<project>/`

`<project>/` is the project and its code. **Never edit anything under it.** No
file changes, no fixes, however small or obvious — a fix belongs in a review
comment, not in the tree.

`review/` is the review workspace and **is** writable.

## 2. Never write with git

No `commit`, `add`, `push`, `pull`, `merge`, `checkout`, `branch`, `stash`,
`reset`, `gc` — nothing that writes, in any repo here. The operator commits.

Reading is fine and expected: `log`, `diff`, `show`, `grep`, `merge-base`,
`rev-parse`, `branch -a`, `archive`. A grant to do one writing thing covers
that action once; it does not carry to the next step or the next session.

## 3. Tests

<ONE OF THE TWO:>

**Never run the test suite.** Not the full suite, not one file, not one test.
Hand over the exact command instead and stop:

    <test command>

<OR:>

Tests may be run, from `<folder>`:

    <test command>

<END>

A throwaway script that runs the code and prints a measurement is **not** the
suite. Those are encouraged — they turn a claim into a fact. Put them in the
scratchpad, never in the project.

## 4. Where things are

```
<project>/                    the code under review. READ-ONLY.
  <main source folders>
  <test folder>
  <rule docs>                 read before judging any code

review/                       the review workspace. Writable.
  REVIEW.md                   how we review. The authority, and it evolves —
                              read it at the start of every review
  ISSUES.md                   pre-existing weaknesses a review bumped into
  TODO.md                     open items. R = review found, A = additional
  mr-<n>-<branch-slug>.md     one note per merge request
```

## 5. This environment

- Code host: <GitLab / GitHub / self-hosted …>. <`gh`/`glab` available, or:
  no CLI, so an MR number has to be confirmed against a branch by hand.>
- Remote `<origin>`, default branch `<main>`.
- Linter: `<command>`, from `<folder>`. <Or: no linter.>
- <Anything else that is missing or different: no `python` on `PATH`, …>

## 6. One thing at a time

When the operator is working through an item, answer **that** item. Anything
else that surfaces goes into `review/TODO.md` silently — no "I've added this to
the list". A reply carrying six related findings buries the one question that
was asked.

## 7. Say when the rules are loaded

At the start of every session, and every time the `mr-review`, `zoom-in` or
`review-followup` skill loads, print this block to the operator, filling in
what loaded it. It tells the operator the rules were re-read.

```
🔒 Read-only rules loaded — <session start | mr-review | zoom-in | review-followup>
  • <project>/ is read-only. No edits, however small. A fix goes in a review
    comment. review/ is writable.
  • No git writes: commit, add, push, pull, merge, checkout, branch, stash,
    reset, gc. Reading is fine: log, diff, show, grep, merge-base, archive.
  • <Never run the test suite. Not one file, not one test. Hand over the
    exact command and stop. | Tests: <command> from <folder>.> Probe
    scripts go in the scratchpad.
  • Linter: <command> from <folder>. <| No linter.>
```
