---
name: review-setup
description: Set up reviews for a project so the review skills can run there — choose the review store the first time (a folder outside every git repository where all review records live), then find the project's agent rules, how to run tests and the linter, where the architecture is described, and seed the project's review-records folder in the review store (ENV.md, REVIEW.md, LOG.md, TODO.md, ISSUES.md). Use this when the operator wants to start reviewing a project that has no records yet ("prepare this directory for reviews", "set up reviews for this repo", "install the review skills here", "also review my project in ~/x"), and when a review skill finds no review store or no records for the project.
---

# Setting up reviews for a project

The review skills (`mr-review`, `zoom-in`, `review-followup`, `review-writing`,
`taste`, `upkeep`) are generic. Everything they need to know about one project
comes from two files in its review-records folder: `ENV.md` (the environment)
and `REVIEW.md` (the review standard). This skill writes both, by asking the
operator a short list of questions and detecting what it can.

Templates are in `${CLAUDE_SKILL_DIR}/templates/`. The layout, the review
store and the start check are in `${CLAUDE_PLUGIN_ROOT}/reference/rules.md` §0.

**Talk to the operator in plain words.** "Review store" and "review-records
folder" are the skills' own names; the operator may never have seen them. Ask
for "a folder to keep all reviews in", and say "this project's reviews go in
`~/reviews/shop/`". Show the real paths, not the names.

## While setting up

**First, load and print the rules**: read
`${CLAUDE_PLUGIN_ROOT}/reference/rules.md`, run the start check, and print the
block with `review-setup` as what loaded it. Setup is the one skill that goes
on without the deny rules: the settings file that holds them is one of the
things it writes. It only reads the project, so the protection line says
"none, setting up".

The project is read-only from the first step. This skill writes only the config
file, the review store's `review-settings.json` and the project's review-records
folder. Do not run the tests or the linter to find out whether they work — ask,
and record what the operator says.

If the review-records folder already exists, read it first. Add what is missing
and show the operator the difference. Never overwrite what is there.

## 0. The review store, the first time only

When the start check says there is no review store yet, ask for one before
anything else, in one message:

> To get reviews started, I need a folder to keep all reviews in. Which one?
> Each project you review gets its own subfolder there. Pick one outside your
> git repositories, so review notes never end up in a commit. `~/reviews`
> would do.

Check the answer before using it:

- **Not inside a git repository**, the project's or any other: run
  `git -C <the nearest folder of it that exists> rev-parse --show-toplevel`. It
  must print nothing. If it prints a repository, say which, and ask again.
- **Not inside the plugin**, which an update replaces.

Then:

1. Create the folder, and write `~/.config/review-skills/config.toml`
   (`$XDG_CONFIG_HOME` when set):

   ```toml
   # Where the review skills keep their records. One folder per project.
   review_store = "<the folder>"
   # Which deny rules a review session needs: "plugin" (review-settings.json
   # in the review store) or "own" (the file in own_settings).
   protection = "plugin"
   ```

2. Write the review store's settings file, which review sessions are started
   with:

   ```
   python3 -B ${CLAUDE_PLUGIN_ROOT}/scripts/start.py settings <review-store>
   ```

   It holds the plugin's deny rules, lets Claude write in the review store
   without asking, and lets the start check run without a prompt. It is never
   written into the user's or the project's settings (rules §9).

## 1. Which project

The project is the git repository Claude was started in, unless the operator
names another folder. Its review-records folder is `<review-store>/<name>/`,
`<name>` being the project folder's name. When a folder of that name already
exists in the review store for another remote, say so and offer a name with its
parent folder in it (`clients-api` for `~/clients/api`).

A folder that is not a git repository cannot be reviewed yet: the skills review
branches. Say so in one line and stop.

## 2. Detect first

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
- **Tools on this machine:** `python3`, `uv`/`uvx`, `node`. The start check,
  the note checker and the renderer need `python3` 3.11 or newer
  (`python3 -c 'import tomllib'`).

## 3. Ask, in one message

Ask everything in one numbered message, each question carrying what was
detected. The operator answers in one go, and can skip what you got right.

1. **Review this project, with its reviews kept in `<review-store>/<name>/`?**
   (detected: …, written out as real paths)
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

Rules the operator writes in the prompt are saved to
`<review-records>/RULES.md`, word for word, and listed in `REVIEW.md` like any
other rule doc.

## 4. Write the files

Fill the templates. Keep every `<…>` the operator did not answer as a visible
`TODO:` line, never as an invented value.

- **`<review-records>/ENV.md`** from `templates/ENV.md`: the environment only,
  no rules. Its Path and Remote lines are how the start check finds this folder
  again, so write them exactly as detected. Its Tests and Linter lines say
  exactly what questions 3 and 4 answered (never run, with the command for the
  operator; may be run, with the command; or no test suite), because the rules
  block prints them.
- **`<review-records>/REVIEW.md`** from `templates/REVIEW.md`. Fill §1 from the
  environment, the rule-doc list from question 2, §3 from question 6 (each
  area with a short name in bold, as the §2 rules have), §4 from
  question 5, §5 from question 6 (who meets the effect, what is live, whether
  there is personal data). The columns, scales, verdicts and note shape are
  not in it: they come with the plugin. Keep its format stamp on line 1.
- **`<review-records>/LOG.md`**, **`<review-records>/TODO.md`** and
  **`<review-records>/ISSUES.md`** from their templates. The records name roles
  ("the operator", "the author"), never people.

Then run the start check once more: its `records:` line must now name the new
folder.

## 5. Hand over

Answer in a few lines:

- the files written, with paths;
- every `TODO:` left open, one line each;
- how to start a review from now on, and the alias that saves typing it:

  ```
  claude --settings <review-store>/review-settings.json
  alias claude-review='claude --settings <review-store>/review-settings.json'
  ```

  To keep this conversation, add `--continue`. A session started without it
  is caught before the review reads anything;
- that the scale and verdicts are a starting point: when a review shows one
  is wrong, say so and it gets rewritten in `REVIEW.md`;
- the A list, in one sentence, because it is never shown during a review:
  "Anything I notice on the side goes quietly onto the A list in
  `<review-records>/TODO.md`, so a review stays on track; say 'show the A list'
  whenever you like."

Then print the rules block again, now with the new environment lines filled in,
so the operator sees it exactly as the review skills will print it.
