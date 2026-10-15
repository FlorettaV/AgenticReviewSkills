---
name: review-setup
description: Set up a review workspace for a new project so the review skills can run there — find the project folder, its agent rules, how to run tests and the linter, where the architecture is described, then write the workspace CLAUDE.md and seed review/ (REVIEW.md, LOG.md, TODO.md, ISSUES.md). Use this when the operator wants to start reviewing a project that has no review/ folder yet ("set up reviews for this repo", "install the review skills here", "can we review project X the way we review the others"), and when a review skill finds no review/REVIEW.md.
---

# Setting up a review workspace

The review skills (`mr-review`, `zoom-in`, `review-followup`, `review-writing`)
are generic.
Everything they need to know about one project comes from two files: the
workspace `CLAUDE.md` (the environment) and `review/REVIEW.md` (the review
standard). This skill writes both, by asking the operator a short list of
questions and detecting what it can.

Templates are in `${CLAUDE_SKILL_DIR}/templates/`.

## The shape it builds

One layout, the same in every project (also in `reference/rules.md` §0):

```
~/projects/<name>/             the workspace: start Claude here. Not a git repository
  CLAUDE.md                    the environment: commands, code host, branch
  .claude/settings.json        deny rules, for sessions started here only
  <project>/                   the project, cloned under its own name. Read-only
  review/
    REVIEW.md                  how we review this project. Read first, every time
    LOG.md                     one row per review, newest first
    TODO.md                    open items: R = review found, A = additional
    ISSUES.md                  pre-existing weaknesses a review bumped into
    RULES.md                   the operator's own rules, if given at setup
    mr-<n>-<branch-slug>.md    one note per merge request
    <stack>-stack-plan.md      one per stack of branches
    probes/mr-<n>/             probe scripts kept for an MR, made-up data only
```

Only `CLAUDE.md`, `.claude/settings.json`, `REVIEW.md`, `LOG.md`, `TODO.md` and
`ISSUES.md` are written at setup; the rest appears as reviews need it.

**Check the shape before writing anything.** The start folder is the
workspace:

- It is **not inside a git repository**
  (`git -C <workspace> rev-parse --show-toplevel` says nothing), so review
  notes never end up in a commit.
- It holds **exactly one project repository**, below it. Claude Code asks
  permission for anything above or beside the folder it starts in, so a project
  next to the workspace (`../my-project`) does not work.
- The plugin is installed globally, so there is no copy of it in the workspace.

If the shape is different, say what is off in one line, propose the layout
(`~/projects/<name>/` with the project cloned into it), and ask before moving
or creating anything.

## While setting up

**First, load and print the rules**: read
`${CLAUDE_PLUGIN_ROOT}/reference/rules.md` and print its block, with
`review-setup` as what loaded it. The project folder is read-only from the
first step. This skill writes only the workspace `CLAUDE.md`, the workspace's
`.claude/settings.json` and files in `review/`. Do not run the tests or the
linter to find out whether they work — ask, and record what the operator says.

If the workspace already has a `CLAUDE.md` or a `review/` folder, read them
first. Add what is missing and show the operator the difference. Never
overwrite what is there.

## 1. Detect first

Find out what you can before asking, so each question can offer an answer to
confirm instead of a blank. Read-only commands only:

- **Git:** the remote and its default branch
  (`git -C <project> remote -v`, `git -C <project> symbolic-ref refs/remotes/origin/HEAD`).
- **Code host:** from the remote URL (GitLab, GitHub, self-hosted). Whether
  `gh` or `glab` is on `PATH` (`command -v gh glab`).
- **Agent rules in the project:** `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`,
  `.cursorrules`, `.github/copilot-instructions.md`, a `docs/` folder with
  rules or conventions, a glossary.
- **Tests and linter config:** `pyproject.toml`, `package.json` scripts,
  `Makefile`, `tox.ini`, `.pre-commit-config.yaml`, CI files
  (`.gitlab-ci.yml`, `.github/workflows/`). CI usually shows the exact commands.
- **Architecture docs:** `ARCHITECTURE.md`, `docs/architecture*`, `docs/adr/`,
  diagrams (`*.pdf`, `*.drawio`, `*.mmd`), an import-guard or layering test.
- **Tools on this machine:** `python3`, `uv`/`uvx`, `node`. The note checker
  needs `python3`.

## 2. Ask, in one message

Ask everything in one numbered message, each question carrying what was
detected. The operator answers in one go, and can skip what you got right.

1. **Where is the project folder?** (detected: …)
2. **Does this project have rules for agents or code?** Point me to them, or
   write them down here. (found: …)
3. **Can I run the tests?** If yes, how and from where. If no, I hand over the
   exact command at the end of every review instead. (CI runs: …)
4. **Can I run a linter?** If yes, which command, from where. (configured: …)
5. **Is the architecture documented?** Where — a doc, a diagram, a test that
   enforces it? Is there a target design that differs from today's code?
6. **Light questions for scoring**, one line each:
   - Who sees this code's effect: customers, internal users, other services?
   - Does it handle personal data?
   - Is there an area that should get explicit attention every review (an
     admin side, payments, auth, data retention)?

Do not ask about the scale, the verdicts or how each column is scored beyond
question 6. `REVIEW.md` starts with a default for all of them, and they are
tuned by reviewing, not up front.

Rules the operator writes in the prompt are saved to `review/RULES.md`, word
for word, and listed in `REVIEW.md` like any other rule doc.

## 3. Write the files

Fill the templates. Keep every `<…>` the operator did not answer as a visible
`TODO:` line, never as an invented value.

- **`CLAUDE.md`** from `templates/CLAUDE.md`: the environment only, no rules.
  Its Tests and Linter lines say exactly what questions 3 and 4 answered
  (never run, with the command for the operator; may be run, with the command;
  or no test suite), because the rules block prints them.
- **`.claude/settings.json`** in the workspace, from `templates/settings.json`,
  with `<project>` replaced by the project folder's name. Never in the user's
  settings: the deny rules must hold only for sessions started in this
  workspace. If the workspace already has one, add the deny rules to it and
  show the difference.
- **`review/REVIEW.md`** from `templates/REVIEW.md`. Fill §1 from the
  environment, the rule-doc list from question 2, §3 from question 6 (each
  area with a short name in bold, as the §2 rules have), §4 from
  question 5. Leave the scale, the verdicts and the note shape as the template
  has them.
- **`review/LOG.md`**, **`review/TODO.md`** and **`review/ISSUES.md`** from
  their templates. The records name roles ("the operator", "the author"),
  never people.

The review skills come with this plugin, so nothing needs copying. If the
operator wants the whole team on the same workspace, the plugin can be enabled
for it with `claude plugin install review@review-skills --scope project`.

## 4. Hand over

Answer in a few lines:

- the files written, with paths;
- every `TODO:` left open, one line each;
- that the scale and verdicts are a starting point: when a review shows one
  is wrong, say so and it gets rewritten in `REVIEW.md`;
- the A list, in one sentence, because it is never shown during a review:
  "Anything I notice on the side goes quietly onto the A list in
  `review/TODO.md`, so a review stays on track; say 'show the A list' whenever
  you like."

Then print the rules block again, now with the new environment lines filled in,
so the operator sees it exactly as the review skills will print it.
