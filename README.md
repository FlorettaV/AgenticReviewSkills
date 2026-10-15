# review — merge request reviews with Claude Code

Five skills that review merge requests the same way for everyone: read-only,
every claim verified, every finding written so someone who never opened the
code knows what broke.

| Skill | What it does |
|---|---|
| `review-setup` | Sets up a review workspace for a new project. Asks where the project is, its rules, how to run tests and the linter, and where the architecture is described |
| `mr-review` | Reviews a branch in two halves — what the customer experiences and what the developer sees — with verified findings, a scoring table per half, and what blocks merge |
| `zoom-in` | Opens up one finding as What happens / Why / Fix, ready to paste into an MR comment |
| `review-followup` | Ticks, re-scores and parks items, and walks through the parked items once a review is done |
| `review-writing` | Turns findings into plain language, then has a fresh editor pass check the wording |

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

### Or from a local copy

If this repo is cloned into the review workspace, say
`~/projects/new_project/review-skills/` next to `project_codebase/`, start
Claude in `new_project/` and say:

> Install the review plugin from ./review-skills

Claude runs `claude plugin marketplace add ./review-skills` and
`claude plugin install review@review-skills`. Start a new session so the
skills load, then go on with "First use" below.

## First use

Make a folder for the review workspace, next to the project's repository (not
inside it, so review notes never end up in a commit). Start Claude there and
say:

> set up reviews for ../my-project

`review-setup` asks a handful of questions and writes the workspace
`CLAUDE.md` and a `review/` folder. Then: "review MR 12" or "review feat/x".

A review runs both halves by default:

- **customer**: what a customer or an operator experiences in normal use if
  this merges — behaviour, looks, wording; how often and how bad. Findings
  `1`, `2`, …
- **code**: what we decided in the code — security, GDPR, how failures hide,
  and what the next developer runs into — walked rule by rule against
  `REVIEW.md` §2 and §3. Findings `D1`, `D2`, …

Ask for one with "review MR 12, code only" or "customer only", and add the
other later with "now do the customer side too". A skipped half is marked
"not run" in the note, and a customer-only review says up front that security
and GDPR were not checked. Either half can block: a finding blocks when it names
what breaks if the MR merges as it stands.

## What is shared and what is yours

- **Shared, in this plugin:** the review method, the scoring columns, how a
  finding is worded, and the records. Change these with an MR on this repo, so
  everyone moves together.
- **Per project, in `review/REVIEW.md`:** the rules, the architecture, the
  scale and how each column is scored. It starts with defaults and grows as
  reviews teach it things.

## Requirements

`git` with the project's remote branches fetched, and `python3` for the note
checker.

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
