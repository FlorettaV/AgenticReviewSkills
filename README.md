# review — merge request reviews with Claude Code

Seven skills that review merge requests the same way for everyone: read-only,
every claim verified, every finding written so someone who never opened the
code knows what broke.

| Skill | What it does |
|---|---|
| `review-setup` | Sets up a review workspace for a new project. Asks where the project is, its rules, how to run tests and the linter, and where the architecture is described |
| `mr-review` | Reviews a branch in two halves — what the customer experiences and what the developer sees — with verified findings, a scoring table per half, and what blocks merge |
| `zoom-in` | Opens up one finding as What happens / Why / Fix, ready to paste into an MR comment |
| `review-followup` | Ticks, re-scores and parks items, and walks through the parked items once a review is done |
| `review-writing` | Turns findings into plain language, then has a fresh editor pass check the wording |
| `upkeep` | Checks the state of the review files (the same rule twice, contradictions, stale items, unexplained words) and offers a short list of trims and questions |
| `taste` | Maps where the team puts things, from the code and its history, and turns the spots that don't add up into short questions for the team. Optional |

## Install

```bash
claude plugin marketplace add <https or ssh URL of this repo>
claude plugin install review@review-skills --scope user
```

Update later with:

```bash
claude plugin marketplace update review-skills
claude plugin update review@review-skills
```

Auto-update is off for team marketplaces. Turn it on in `/plugin` →
**Marketplaces** if you want it.

Install it once, for your user. Every project then gets the same skills, and
an update reaches all of them at once. What differs per project lives in that
project's `review/REVIEW.md`, never in an edited copy of the skills.

## First use

Make a folder for the review workspace, clone the project into it, and start
Claude in the workspace folder:

```
~/projects/my-project/          the workspace: start Claude here
  my-project/                   the project, cloned under its own name
```

The workspace itself is not a git repository, so review notes never end up in
a commit, and the project sits below the folder Claude starts in, so reading
it needs no permission prompts. Then say:

> set up reviews for ./my-project

`review-setup` asks a handful of questions and writes the workspace
`CLAUDE.md`, its `.claude/settings.json` and a `review/` folder. Before every
review, fetch the project (`git -C my-project fetch`); then say "review MR 12"
or "review feat/x".

A review runs both halves by default:

- **customer**: what a customer or an operator experiences in normal use if
  this merges — behaviour, looks, wording; how often and how bad. Findings
  `1`, `2`, …
- **developer**: what we decided in the code — security, GDPR, how failures hide,
  and what the next developer runs into — walked rule by rule against
  `REVIEW.md` §2 and §3, and compared with the code around it (its
  neighbours, and the map from `taste` if there is one). Findings `D1`, `D2`, …

Ask for one with "review MR 12, code only" (the developer half) or "customer only", and add the
other later with "now do the customer side too". A skipped half is marked
"not run" in the note, and a customer-only review says up front that security
and GDPR were not checked. Either half can block: a finding blocks when it names
what breaks if the MR merges as it stands.

### The A list

Anything Claude notices on the side during a review goes quietly onto the A
list in `review/TODO.md` instead of interrupting. It is offered once a
review's findings are all handled, and shown whenever you ask: "show the A
list".

## What is shared and what is yours

- **Shared, in this plugin:** the review method, the read-only rules
  (`reference/rules.md`), the columns, default scales and verdicts
  (`reference/scoring.md`), the note's shape (its renderer), how a finding is
  worded, and the records. Change these with an MR on this repo, so everyone
  moves together.
- **Per project, in `review/REVIEW.md`:** the project's rules, the areas that
  get extra attention, the architecture, and how the columns are scored there.
  It starts small and grows as reviews teach it things. It carries a format
  number; when the plugin's format moves on, the next review offers to update
  it and shows the difference first.

## Requirements

`git` with the project's remote branches fetched, and `python3` 3.11 or newer
for the note checker and renderer.

## Working on the plugin itself

Clone this repository anywhere, make the change on a branch, and try it in a
session that loads the plugin straight from your working tree:

```bash
claude --plugin-dir ~/projects/review-skills
```

Review the change with the installed, released version, from a workspace that
has a clone of this repository as its project: the released skills review the
new ones. The tests run with `python3 -B tests/run.py`; after an intended
change to the note's shape, `python3 -B tests/run.py --regenerate` rewrites the
golden note, and its diff shows what changed.

## Releasing a change to the plugin

Teammates only receive a change when the `version` in
`.claude-plugin/plugin.json` changes: with a version set, `claude plugin update`
ignores new commits until the number moves. So:

1. Make the change on a branch, and review it like any other MR.
2. Once it has passed review and is merged, raise the version in
   `.claude-plugin/plugin.json` in its own commit: the minor number for a
   change in how reviews run, the patch number for wording and fixes.
3. Push. Teammates get it with the update commands above.

Never push to the shared branch without raising the version, or the change
reaches nobody.
