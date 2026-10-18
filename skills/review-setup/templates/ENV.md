# Review environment for <project>

What this environment has, for the review skills. They bring their own rules
and load them when they run; this file holds no rules. The start check finds
this folder by the Path and Remote lines, so keep them exact.

- **Path:** `<the project's folder>`
- **Remote:** `<origin's URL>`, default branch `<main>`. The operator fetches
  before a review.
- **Code host:** <GitLab / GitHub / self-hosted …>. <`gh`/`glab` available, or:
  no CLI, so an MR number is confirmed against a branch by hand.>
- **Tests:** <never run by the reviewer; the command for the operator is
  `<test command>`, from `<folder>` | may be run: `<test command>`, from
  `<folder>` | there is no test suite>.
- **Linter:** `<command>`, from `<folder>`. <Or: no linter.>
- <Anything else that is missing or different: no `python` on `PATH`, …>

## In the project

```
<main source folders>
<test folder>
<rule docs>                   read before judging any code
```
