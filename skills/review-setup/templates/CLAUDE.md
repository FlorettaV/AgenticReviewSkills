# Review workspace for <project>

This folder is a review workspace. The review skills (`mr-review`, `zoom-in`,
`review-followup`) bring their own rules and load them when they run; this file
only says what this environment has. It holds no rules on purpose: Claude Code
also loads this file when it is started inside `<project>/` to write code, and
nothing here should get in the way of that.

## Where things are

```
<project>/                    the code under review
  <main source folders>
  <test folder>
  <rule docs>                 read before judging any code

review/                       the review records
  REVIEW.md                   how we review this project. Read at the start of
                              every review
  LOG.md                      one row per review, newest first
  ISSUES.md                   pre-existing weaknesses a review bumped into
  TODO.md                     open items. R = review found, A = additional
  RULES.md                    the operator's own rules, if given at setup
  mr-<n>-<branch-slug>.toml   one note per merge request, as data
  mr-<n>-<branch-slug>.md     the same note, rendered for people to read
  <stack>-stack-plan.md       one per stack of branches
  probes/mr-<n>/              probe scripts kept for an MR, made-up data only

.claude/settings.json         deny rules: no edits under <project>/, no git
                              writes. For sessions started in this folder only
```

## This environment

- **Code host:** <GitLab / GitHub / self-hosted …>. <`gh`/`glab` available, or:
  no CLI, so an MR number is confirmed against a branch by hand.>
- **Remote** `<origin>`, default branch `<main>`. The operator fetches before a
  review.
- **Tests:** <never run by the reviewer; the command for the operator is
  `<test command>`, from `<folder>` | may be run: `<test command>`, from
  `<folder>` | there is no test suite>.
- **Linter:** `<command>`, from `<folder>`. <Or: no linter.>
- <Anything else that is missing or different: no `python` on `PATH`, …>
