# The review rules

The one home of the rules every review skill works under. `mr-review`,
`zoom-in`, `review-followup`, `taste`, `upkeep` and `review-setup` load this
file, run the start check (§0) and print the block below before they read the
project; nothing else in the plugin restates it. The rules hold only while a
review skill runs: Claude runs in the project, where people also write code, so
nothing here is written into the project or its `CLAUDE.md`.

## The block to print

Fill in what loaded it, the protection the start check found, and the two
environment lines from `<review-records>/ENV.md` ("Tests" and "Linter"), and
print it exactly:

```
🔒 Read-only rules loaded — <mr-review | zoom-in | review-followup | taste |
                              upkeep | review-setup>
  • <project>/ is read-only. No edits, however small. A fix goes in a review
    comment. The records, <review-records>/, are writable.
  • Protection: <plugin rules, loaded | own settings, <file> | none, the
    operator's choice for this session>.
  • No git writes, fetch included: the operator fetches. Reading is fine: log,
    diff, show, grep, merge-base, rev-parse, archive, ls-remote.
  • <Tests: never run, the command is handed over | Tests: <command> from <folder>>.
    Probes go in the scratchpad, with made-up data.
  • Linter: <command> from <folder>, cache off. <| No linter.>
  • Anything noticed on the side goes onto the A list, silently.
```

## 0. The start check

Claude runs in the project, the git repository under review. The records live
outside it, in the **review store**: a folder the operator chose once, outside
every git repository, with one folder per project. `<review-records>` means that
project's folder in the review store, and every path in the skills that starts
with `<review-records>/` is in it.

```
~/.config/review-skills/config.toml   where the review store is, and which protection
<review-store>/                              the review store. Not inside a git repository
  review-settings.json                the plugin's deny rules, for --settings
  <name>/                             <review-records>: one project, named after its folder
    ENV.md                            the environment: path, remote, commands
    REVIEW.md                         how we review this project. Read first, every time
    LOG.md                            one row per review, newest first
    TODO.md                           open items: R = review found, A = additional
    ISSUES.md                         pre-existing weaknesses a review bumped into
    RULES.md                          the operator's own rules, if given at setup
    MAP.toml, MAP.md, taste/          the map, if the taste skill made one
    mr-<n>-<branch-slug>.toml         one note per merge request: the data, which
                                      skills read and write
    mr-<n>-<branch-slug>.md           the same note, rendered from it for people
    <stack>-stack-plan.md             one per stack of branches
    probes/mr-<n>/                    probe scripts kept for an MR, made-up data only
```

Every review skill starts with one command, before it reads the project:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/scripts/start.py check [<project>]
```

The project is the folder Claude was started in, unless the operator names
another. The command prints the review store, the project, its review-records
folder and the protection this session loaded, and a `problem:` line for
anything that stops the review. The settings file allows exactly this command,
so it runs without a prompt in every permission mode. If it is blocked anyway (a
session started without the file, in auto mode), ask the operator to approve it,
and never work around it: a review that skips the check has no idea what
protects it. Then:

- **No review store yet, or no records for this project:** offer `review-setup`,
  and stop.
- **Its last line says `next: run review-guard-canary`:** run
  `review-guard-canary`. Claude Code must refuse it: the deny rules are then not
  only on disk but live in this session. If it runs (the shell answers
  `command not found`), the protection is not live; treat it as none.
- **The protection is none, or not live:** stop before reading anything, and
  offer three choices, once:

  > The review rules aren't loaded in this session. Pick one:
  > 1. Restart with ours: `claude --continue --settings <review-store>/review-settings.json`
  > 2. Use my own settings file: tell me which one
  > 3. Go on unprotected, this time only

  1 ends the session here. 2 is saved in the config (`protection = "own"`,
  `own_settings = "<file>"`) and checked like the plugin's file from then on;
  any `gap:` line is said once, in one line, and the operator decides. 3 is
  never saved: a forgotten flag is caught every time.
- **`gap:` lines with the plugin's rules:** the settings file is older than the
  plugin. Offer `start.py settings <review-store>`, which adds
  what is missing and shows it; the session needs a restart to load it.
- **Started outside the project:** the deny rule on edits covers only the
  folder Claude started in. Say so, and offer the same three choices.

The protection goes in the rules block and in the note, so a reader knows how
the review was run.

A folder that holds a `review/` folder and a `CLAUDE.md` is a workspace from
before the review store. Say so in one line: its records move by copying
`review/` into `<review-store>/<name>/`, and its `CLAUDE.md` becomes that
folder's `ENV.md`.

## 1. The project is read-only

No file in the project folder is created, changed or deleted, however small or
obvious the fix: a fix belongs in a review comment, not in the tree.
`<review-records>/` is writable. A grant from the operator to do one writing
thing covers that action once; it does not carry to the next step or the next
session.

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

Tests run only if `<review-records>/ENV.md` allows it, with its command, from
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

The command `<review-records>/ENV.md` gives, from its folder, with its cache
off (`ruff --no-cache`, `eslint --no-cache`, …), so nothing is written into the
project. If it says "no linter", run none and say so in the note. If it says
nothing, look for a configured one, say which command you ran, and run it with
its cache off.

## 6. Detect: the read-only check

A review checks that it kept its promise. At the start, keep the project's
state in a marker file:

```
git -C <project> status --porcelain --ignored > <review-records>/.review-start
```

At the end, before the note is published:

```
find <project> -newer <review-records>/.review-start
git -C <project> status --porcelain --ignored | diff <review-records>/.review-start -
```

The note gets one line: "Read-only check: nothing changed in the project", or
the list of what did. People may work in the project while a review runs, so a
change on that list is not proof the review made it: say what changed, not who.
**Never clean up**: a clean-up is itself a write, and the usual tools for it
(`git checkout .`, `git clean`, `rm -rf`) can take the operator's own
uncommitted work with them. Report, and let the operator decide.

## 7. Sub-agents

A fresh sub-agent sees neither this block nor the loaded skills, only its
prompt. Every prompt for a sub-agent (the editor pass, a topic in a split
review) **starts with the block above, word for word**, and runs in the same
session, under the same deny rules. A sub-agent never writes to
`<review-records>/`; it reports back, and what it proposes is checked before it
goes anywhere.

## 8. One thing at a time

When the operator is working through an item, answer that item. Anything else
that surfaces goes onto the A list in `<review-records>/TODO.md` silently: no
"I've added this to the list". A reply carrying six related findings buries the
one question that was asked.

## 9. What enforces this

The rules above are the first layer. The second is Claude Code's own deny
rules, in the plugin's `reference/deny.json`: they block every file edit under
the current folder, which is the project Claude started in, for Claude and its
sub-agents alike, and the common forms of the git writes. Claude Code refuses
a matching call before it runs, whatever the model decides. The same file lets
Claude write in the review store without asking.

They are loaded with `claude --settings <review-store>/review-settings.json`,
never written into the user's or the project's settings: those also hold when
someone starts Claude in the project to write code. The start check (§0) is what
makes a forgotten flag harmless: no review starts without the rules, the
operator's own, or a choice made in that session.

They are a net, not a wall: a git command with an option before it
(`git -C <project> commit`) or a script that writes files is not matched by
them. The read-only check (§6) is what catches those.
