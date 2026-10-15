# The review rules

The one home of the rules every review skill works under. `mr-review`,
`zoom-in`, `review-followup` and `review-setup` load this file and print the
block below before anything else; nothing else in the plugin restates it.
The rules hold only while a review skill runs: they are not written into the
workspace `CLAUDE.md`, because Claude Code also loads a `CLAUDE.md` from every
folder above the one it starts in, and a ban there would reach anyone who
starts Claude inside the project to write code.

## The block to print

Fill in what loaded it and the two environment lines from the workspace
`CLAUDE.md` ("Tests" and "Linter"), and print it exactly:

```
🔒 Read-only rules loaded — <mr-review | zoom-in | review-followup | review-setup>
  • <project>/ is read-only. No edits, however small. A fix goes in a review
    comment. review/ is writable.
  • No git writes, fetch included: the operator fetches. Reading is fine: log,
    diff, show, grep, merge-base, rev-parse, archive, ls-remote.
  • <Tests: never run, the command is handed over | Tests: <command> from <folder>>.
    Probes go in the scratchpad, with made-up data.
  • Linter: <command> from <folder>, cache off. <| No linter.>
  • Anything noticed on the side goes onto the A list, silently.
```

## 1. The project is read-only

No file in the project folder is created, changed or deleted, however small or
obvious the fix: a fix belongs in a review comment, not in the tree. `review/`
is writable. A grant from the operator to do one writing thing covers that
action once; it does not carry to the next step or the next session.

## 2. Git: read, never write

**Never:** `commit`, `add`, `rm`, `mv`, `push`, `pull`, `fetch`, `merge`,
`rebase`, `cherry-pick`, `checkout`, `switch`, `restore`, `reset`, `clean`,
`stash`, `branch`, `tag`, `worktree`, `apply`, `am`, `gc`, `config`. The
operator commits and fetches.

**Fine and expected:** `log`, `diff`, `show`, `grep`, `blame`, `merge-base`,
`rev-parse`, `ls-tree`, `cat-file`, `for-each-ref`, `archive` (into the
scratchpad, see §4), `status`, and `ls-remote`, which asks the server what it
has and writes nothing. Use `for-each-ref refs/remotes` where you would have
used `branch -a`.

**Is the local copy current?** At the start of a review, compare the server
with the local copy for the branch under review:

```
git ls-remote --heads origin <branch>
git rev-parse origin/<branch>
```

When they differ, or the branch is missing locally, say so in one line and
wait: "`feat/x` is at `a1b2c3` on the server and `9f8e7d` here; please fetch
first." Never review a branch the server has moved past.

## 3. Tests

Tests run only if the workspace `CLAUDE.md` allows it, with its command, from
its folder. If it forbids them or says nothing, run none, not even one: the
review ends with the exact command for the operator.

## 4. Probes

A small script that runs the code and prints what happens is not the test
suite. It is encouraged: it turns a claim into a fact. It must not write
anything into the project:

- **Where:** the script lives in the scratchpad, never in the project.
- **Which code:** the branch's code without a checkout, and only the part the
  probe needs:

  ```
  git archive origin/<branch> <path> | tar -x -C <scratchpad>
  ```

  `tar` without `-C` extracts wherever Claude stands.
- **How:** with the project's own interpreter and dependencies, the scratchpad
  copy first on the import path. In Python, always `python3 -B`, so no
  `__pycache__` folder is written next to the code. Not the environment
  variable: `python3 -I` ignores it.
- **What data:** made up, never a real customer's (see `review-writing`).
- **When it is too big:** a probe that needs a build, a database or more than a
  slice of the platform is not run. Write it, hand it to the operator like the
  test command, and mark the finding "argued, not run".

## 5. The linter

The command the workspace `CLAUDE.md` gives, from its folder, with its cache
off (`ruff --no-cache`, `eslint --no-cache`, …), so nothing is written into the
project. If it says "no linter", run none and say so in the note. If it says
nothing, look for a configured one, say which command you ran, and run it with
its cache off.

## 6. Detect: the read-only check

A review checks that it kept its promise. At the start:

```
touch review/.review-start
```

At the end, before the note is published:

```
find <project> -newer review/.review-start
git -C <project> status --porcelain --ignored
```

The note gets one line: "Read-only check: nothing changed in the project", or
the list of what did. **Never clean up**: a clean-up is itself a write, and the
usual tools for it (`git checkout .`, `git clean`, `rm -rf`) can take the
operator's own uncommitted work with them. Report, and let the operator decide.

## 7. Sub-agents

A fresh sub-agent sees neither this block nor the loaded skills, only its
prompt. Every prompt for a sub-agent (the editor pass, a topic in a split
review) **starts with the block above, word for word**, and the agent is
started from the workspace. A sub-agent never writes to `review/`; it reports
back, and what it proposes is checked before it goes anywhere.

## 8. One thing at a time

When the operator is working through an item, answer that item. Anything else
that surfaces goes onto the A list in `review/TODO.md` silently: no "I've added
this to the list". A reply carrying six related findings buries the one
question that was asked.

## 9. What enforces this

The rules above are the first layer. `review-setup` also writes deny rules into
the workspace's own `.claude/settings.json` (never into user settings, so the
plugin restricts nobody outside a review workspace). They block every file edit
under the project folder, for Claude and its sub-agents alike, and the common
forms of the git writes. They are a net, not a wall: a git command with an
option before it (`git -C <project> commit`) or a script that writes files is
not matched by them. The read-only check (§6) is what catches those.
