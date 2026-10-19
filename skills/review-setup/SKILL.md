---
name: review-setup
description: Set up reviews for a project so the review skills can run there — choose the review store the first time (a folder outside every git repository where all review records live), then find the project's agent rules, how to run tests and the linter, where the architecture is described, and seed the project's review-records folder in the review store (ENV.md, REVIEW.md, LOG.md, TODO.md, ISSUES.md). Use this when the operator wants to start reviewing a project that has no records yet ("prepare this directory for reviews", "set up reviews for this repo", "install the review skills here", "also review my project in ~/x"), and when a review skill finds no review store or no records for the project.
---

# Setting up reviews for a project

The review skills (`mr-review`, `zoom-in`, `review-followup`, `review-writing`,
`taste`, `upkeep`) are generic. Everything they need to know about one project
comes from two files in its review-records folder: `ENV.md` (the environment)
and `REVIEW.md` (the review standard). This skill writes both, by
detecting what it can, writing that down, and asking only what the code
can't answer.

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
   written into the user's or the project's settings (rules §10).

## 1. Which project

The project is the git repository Claude was started in, unless the operator
names another folder. Its review-records folder is `<review-store>/<name>/`,
`<name>` being the project folder's name. When a folder of that name already
exists in the review store for another remote, say so and offer a name with its
parent folder in it (`clients-api` for `~/clients/api`).

A folder that is not a git repository cannot be reviewed yet: the skills review
branches. Say so in one line and stop.

## 2. Detect first

Find out what you can before asking anything. Read-only commands only, and
keep for each finding the file or command it came from:

- **Git:** the remote and its default branch
  (`git -C <project> remote -v`, `git -C <project> symbolic-ref refs/remotes/origin/HEAD`).
- **Code host:** from the remote URL (GitLab, GitHub, self-hosted). Whether
  `gh` or `glab` is on `PATH` (`command -v gh glab`).
- **Agent rules in the project:** `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`,
  `.cursorrules`, `.github/copilot-instructions.md`, a `docs/` folder with
  rules or conventions, a glossary. Follow imports: a `CLAUDE.md` that imports
  a missing file points at where its rules really come from.
- **Tests and linter config:** `pyproject.toml`, `package.json` scripts,
  `composer.json` scripts, `Makefile`, `tox.ini`, `.pre-commit-config.yaml`,
  CI files (`.gitlab-ci.yml`, `.github/workflows/`). CI usually shows the
  exact commands. Baseline files (`phpstan-baseline.neon`, `*-baseline.*`).
- **Architecture docs:** `ARCHITECTURE.md`, `docs/architecture*`, `docs/adr/`,
  diagrams (`*.pdf`, `*.drawio`, `*.mmd`, `*.puml`), an import-guard or
  layering test.
- **Tools on this machine:** `python3`, `uv`/`uvx`, `node`, and the runtime
  the tests need. The start check, the note checker and the renderer need
  `python3` 3.11 or newer (`python3 -c 'import tomllib'`).

## 3. Settle what the detection answers, ask only the rest

What the detection answers clearly is settled and written down, not asked.
The operator corrects it afterwards. Each topic has a default for the clear
case and says when it still needs a question:

| Topic | Settled when | Then | Ask when |
|---|---|---|---|
| Project and folder | it is a git repository and `<review-store>/<name>/` is free or already names this remote | review it, reviews in `<review-store>/<name>/` | the name is taken by another remote (offer `<parent>-<name>`) |
| Rules | rule docs were found | every one found is a rule doc; a missing generated file is read from its sources | none found, or two docs contradict each other on the same point |
| Tests | a test command is configured (scripts, Makefile, CI) | never run, the command is handed over at the end of each review, as CI or the scripts write it | no test command found, or several that disagree |
| Linter | a linter is configured | never run, handed over the same way; a baseline file means the warnings in it are not findings | several linters with no command that runs them together: list them all as the handover |
| Architecture | a doc describes the layers or modules | that doc is the architecture; nothing enforces it unless a layering test was found; target design: today's doc | no doc found (is it written down anywhere: a wiki, a diagram?), or the doc says the code doesn't match it yet *and* gives no target |

Never running the tests and the linter is the safe default: the operator
says "you may run them" when that's wanted, and ENV.md changes then.

Something found that fits no topic (a draft file next to the repository, a
second rules folder) is mentioned in the report, not asked about. It is left
out until the operator says otherwise.

The scoring questions stay questions, because the code can't answer them.
Offer a guess for each, from the code:

- Who sees this code's effect: customers, internal users, other services?
- Does it handle personal data?
- Is there an area that should get explicit attention every review (an
  admin side, payments, auth, data retention)?

Do not ask about the scale, the verdicts or how each column is scored.
`REVIEW.md` starts with a default for all of them, and they are tuned by
reviewing, not up front.

## 4. Write the files, then report, in one message

Write the files (below) with what was settled, the scoring guesses filled in
and marked `(guess, not confirmed)`, before saying anything. Then one message:

> I set up reviews for `<project>`; its reviews go in `<review-store>/<name>/`.
> Here's what I configured and where I found it. If anything is off, say so
> and I'll fix it.
>
> - **Project:** `<path>`, remote `<remote>`, default branch `<branch>`, <host>.
>   <gh/glab found, or: neither gh nor glab, so MR numbers are matched to branches by hand>.
> - **Rules:** <the docs, grouped by folder> (from <where>).
> - **Tests:** I never run them; at the end of each review I hand you
>   `<command>` (from <where>). <One line on where they seem to run, if the
>   runtime isn't on this machine.>
> - **Linter:** handed over the same way: <commands>. Baselines: old warnings
>   aren't findings.
> - **Architecture:** <doc> (layers: …). Nothing enforces it <or: enforced by …>.
> - **Also noticed:** <anything left out, one line each>.
>
> Three questions I can't answer from the code. My guesses are in already;
> correct what's wrong:
> 1. **Who sees the effect:** <guess>
> 2. **Personal data:** <guess>
> 3. **Areas every review checks:** <guess list>
>
> Next I'll look at how the code is written: where the team puts things and
> which habits show in its history. That takes a few minutes and only reads.
> Say "skip" if you'd rather not.

Every open question goes under the three scoring questions, numbered on from
them, and only when the table above says to ask.

When the operator answers, fix what they corrected, drop the
`(guess, not confirmed)` marks they confirmed, and go on to §5.

### The files

Fill the templates. A value the detection did not find and the operator did
not give stays a visible `TODO:` line, never an invented value.

- **`<review-records>/ENV.md`** from `templates/ENV.md`: the environment only,
  no rules. Its Path and Remote lines are how the start check finds this folder
  again, so write them exactly as detected. Its Tests and Linter lines say
  exactly what was settled (never run, with the command for the operator; may
  be run, with the command; or no test suite), because the rules block prints
  them.
- **`<review-records>/REVIEW.md`** from `templates/REVIEW.md`. Fill §1 from the
  environment, the rule-doc list from the rules found, §3 from the areas every
  review checks (each with a short name in bold, as the §2 rules have), §4
  from the architecture found, §5 from the other two scoring questions (who
  meets the effect, what is live, whether there is personal data). The columns, scales, verdicts and note shape are
  not in it: they come with the plugin. Keep its format stamp on line 1.
- **`<review-records>/LOG.md`**, **`<review-records>/TODO.md`** and
  **`<review-records>/ISSUES.md`** from their templates. The records name roles
  ("the operator", "the author"), never people.

Then run the start check once more: its `records:` line must now name the new
folder.

## 5. Map how the code is written

Unless the operator said "skip", run a `taste` scan now
(`${CLAUDE_PLUGIN_ROOT}/skills/taste/SKILL.md`, mode scan), in this session.
Two things differ from a scan on its own:

- **No second go:** the report in §4 already said what comes next, and the
  operator's answer is the go. Say in one line what you're counting, and start.
- **No deny rules needed:** the scan only reads the project and writes in the
  review-records folder, like setup. The protection stays "none, setting up".

At the end, show the map's questions for the team as optional, in a few lines:

> The map is in `<review-records>/MAP.md`: <n> habits, <m> of them settled.
> <k> spots where the code goes one way and logic or the docs another. A
> question for each is in MAP.md. They're optional: answer any now, take them
> to the team, or leave them. Reviews work without them.

Whatever the operator answers is handled as the scan's step 5. No answer is
fine: go on.

## 6. Hand over

Say it's ready, in a few lines:

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
