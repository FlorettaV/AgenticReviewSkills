<!-- review format: 2 -->
# Reviewing <project>

The single guide for how we review code in `<project>/`: the rules, the
architecture we measure against, and how a finding is scored. How a finding is
*worded*, and the shape of a note, are set by the review skills, not here.

This file starts small on purpose. When a review turns up a rule we were
applying but had not written down, it gets added. When a score or a verdict
turns out wrong in practice, it gets rewritten here, with the date.

---

## 1. How we work

**Reviews are read-only**, by the rules the review skills bring with them. The
test and linter commands are in the workspace `CLAUDE.md`.

**What the linter covers:** <what it selects and ignores, if that matters for
what counts as a finding.>

**One note per merge request**: its data file `mr-<n>-<branch-slug>.toml`, and
the `.md` rendered from it, in this folder.
Pre-existing weaknesses go in `ISSUES.md` instead — see §5.

**Merge requests are identified by branch.** <With `gh`/`glab`: the CLI maps
number to branch. Without: confirm the mapping by hand at the start.>

### Rule documents

Read before judging any code. Where they disagree with this file on a code
rule, they win.

| Document | What it governs |
|---|---|
| `<path>` | <e.g. coding rules, conventions, glossary, repo rules for agents> |

---

## 2. What we review for

Each rule says what it means concretely, so a finding can point at the rule and
the rule can be argued with. A starting set — sharpen it as reviews go.

Each rule has a short name, in bold in its heading. Findings (the Rule column)
and the note's "Rules walked" list use exactly that name; a new rule gets one
when it is added.

### **Readable** — by a human

Someone who did not write it can follow it at reading speed. Comments explain
*why*, not *what*. A comment that no longer matches the code it sits above is a
finding — a stale comment is worse than none, because it is trusted.

### **Manageable** — by a human

The next change to this code is obvious and local. A reviewer can name every
place that must change together. When one behaviour is expressed in two places
kept in sync by nothing, say so and name both.

### **Linter** — passes it

The command in §1. Do not raise style the linter does not enforce as a finding.

### **Architecture** — abides by it, or moves toward it

Never away from it. See §4.

### **Simple**

Prefer the version with fewer moving parts and fewer states. A new sentinel
value, a new parameter with a default, or a new protocol method each need to
earn their place.

### **Focused**

- **No spreading of configuration.** One fact, one home.
- **No fallback stacked on fallback.** Catch, log, then either stop or do one
  simple thing. Count the quiet degradation paths a value can pass through —
  that count is the **Layers** column in §5.
- **No widening of scope.** A structural change that also adjusts a threshold
  or a config value is two changes.

### **Complete**

When a change touches one of a group — one error path, one of four routes, one
of two backends — enumerate the group and say what the untouched members now
disagree with.

### **Tested**

A new test fails when the behaviour it is named for breaks. A test that reads
the source text, or asserts on exactly how something is written, fails when
the code is rephrased and passes when it is wrong. Read what the assertion
reads, not what the test is called.

---

## 3. Extra attention

Checked explicitly every review, and the note says so even when the answer is
"not touched".

<From the setup questions: an admin side, auth, payments, personal data, data
retention, … One heading each, with a short name in bold (`### **Payments** —
refunds and charges`) and what exactly to check. Delete this section's
placeholder if there is nothing yet.>

---

## 4. The architecture

### 4.1 Where we are going

<The target design and where it is described: a doc, a diagram. "None
documented yet" is a valid answer, and is written down.>

### 4.2 What the code is today

<Short. The main parts and how a request flows through them. Grows as reviews
learn it.>

### 4.3 What is enforced

<A layering or import-guard test, a dependency rule in CI. Name the file. A
change that weakens it to make an import work is a finding.>

---

## 5. How we score here

The columns, the default scales and the verdicts are the same in every project
and come with the review skills (`reference/scoring.md` in the plugin). This
section says how to score **for this project**, and where its scale differs
from the defaults. Where they disagree, this section wins here.

| Column | Here |
|---|---|
| **Chance** | How often <a customer / a user / another service> hits the visible effect in normal use. What is live: <which sites, shops or tenants are served; which settings are on>. Ask when it is not known. |
| **Customer** | How bad it is for <the person affected> when it happens. |
| **GDPR** | <Scored: the project handles <which personal data> | `–` throughout: the project handles none.> |

<Changes to a default scale, with the date and why: "Layers 2 also covers two
modules that share one log line (2026-11-02, after MR 18)." None yet.>

---

## 6. Review log

Kept in `LOG.md`, next to this file: one row per review, newest first. This
file is the standard and is read in full at the start of every review, so the
record of what was reviewed lives apart from it.
