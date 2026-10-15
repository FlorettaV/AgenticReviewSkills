# Reviewing <project>

The single guide for how we review code in `<project>/`: the rules, the
architecture we measure against, how a finding is scored, and the shape every
review note takes. How a finding is *worded* is set by the review skills, not
here.

This file starts small on purpose. When a review turns up a rule we were
applying but had not written down, it gets added. When a score or a verdict
turns out wrong in practice, it gets rewritten here, with the date.

---

## 1. How we work

**Reviews are read-only.** No edits to `<project>/`, no git writes. Reading git
history and diffing branches is fine.

**Tests:** <never run by the reviewer; the review ends with the exact command
for the operator | run with `<command>` from `<folder>`>.

**Linter:** `<command>` from `<folder>`. <What it selects and ignores, if that
matters for what counts as a finding.>

**One note per merge request**, named `mr-<n>-<branch-slug>.md`, in this folder.
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

### Readable by a human

Someone who did not write it can follow it at reading speed. Comments explain
*why*, not *what*. A comment that no longer matches the code it sits above is a
finding — a stale comment is worse than none, because it is trusted.

### Manageable by a human

The next change to this code is obvious and local. A reviewer can name every
place that must change together. When one behaviour is expressed in two places
kept in sync by nothing, say so and name both.

### Passes the linter

The command in §1. Do not raise style the linter does not enforce as a finding.

### Abides by the architecture, or moves toward it

Never away from it. See §4.

### Simple

Prefer the version with fewer moving parts and fewer states. A new sentinel
value, a new parameter with a default, or a new protocol method each need to
earn their place.

### Focused

- **No spreading of configuration.** One fact, one home.
- **No fallback stacked on fallback.** Catch, log, then either stop or do one
  simple thing. Count the quiet degradation paths a value can pass through —
  that count is the **Layers** column in §5.
- **No widening of scope.** A structural change that also adjusts a threshold
  or a config value is two changes.

### Complete

When a change touches one of a group — one error path, one of four routes, one
of two backends — enumerate the group and say what the untouched members now
disagree with.

### Tested

A new test fails when the behaviour it is named for breaks. A test that reads
the source text, or asserts on exactly how something is written, fails when
the code is rephrased and passes when it is wrong. Read what the assertion
reads, not what the test is called.

---

## 3. Extra attention

Checked explicitly every review, and the note says so even when the answer is
"not touched".

<From the setup questions: an admin side, auth, payments, personal data, data
retention, … One heading each, with what exactly to check. Delete this section's
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

## 5. How a finding is scored

The columns are fixed by the review skills. This section says how to score
them **for this project**. The defaults below are a starting point.

A review has two halves, each with its own table: **customer** (what a
customer or operator experiences in normal use) and **code** (what we decided
in the code: §2 and §3, security and GDPR included). Both run unless the
operator asks for one.

### The customer columns

| Column | How we score it here |
|---|---|
| **Chance** | How often <a customer / a user> hits the **visible effect** in normal use. Depends on facts the code does not carry (<who is served, what is live>), so ask rather than infer. |
| **Customer** | How bad it is for <the person affected> when it happens. |
| **Fix effort** | How much work the fix is. This drives sequencing. |

### The developer columns

| Column | How we score it here |
|---|---|
| **Rule** | The §2 rule or §3 area it breaks, by its heading's first word: `Readable`, `Manageable`, `Simple`, `Focused`, `Complete`, `Tested`, `Abides` (the architecture), or a §3 area. In a code-only review, a bug a customer would see is marked `customer-visible`. |
| **Next change** | How much it costs the next developer who touches this code. See below. |
| **Security** | Does it let someone do something they should not be able to do. |
| **GDPR** | Does it expose, mix or over-retain personal data. <`–` throughout if the project handles none.> |
| **Layers** | How many separate places absorb this one failure. See below. |
| **Fix effort** | As in the customer table. |

Security and GDPR sit here, not with the customer: the harm lands on a
customer, but the decision is made in the code, and that is where a reviewer
finds it. Anything with a Security or GDPR score goes in this table, even when
a customer also sees it; its detail block then says how often.

### Layers

Counts **places that absorb the same failure** with the same outcome, so no log
line says which one fired.

| | |
|---|---|
| `–` | Not a layering problem. |
| `0` | Counted, and there is one place. |
| `1` | One guard plus one documented degradation, in the same function. |
| `2` | Two places in one module can swallow the same input. |
| `3` ⚠️ | Two modules, or a catch inside a catch. |
| `4` ❗ | Three or more modules, each covering for the same failure. |
| `5` ❗ | As 4, and one layer substitutes a value, so the failure has no log line anywhere. |

Name every place in the detail block. A Layers score without that list cannot
be argued with.

### Next change

| | |
|---|---|
| `–` | Not about the next change. |
| `0` | Noticed. Costs nothing. |
| `1` | A reader pauses, then gets it. |
| `2` | The next change needs a second look somewhere the reader would not think to look. |
| `3` ⚠️ | The next change is likely to miss a place, with nothing to warn them. |
| `4` ❗ | Something actively misleads: a comment that says the opposite, a test that passes when the behaviour is broken. |
| `5` ❗ | It fails now: a crash, a red suite, a server that will not start. Usually a `block`. |

### The scale

`0`–`5`, or **`–`** when the column does not apply. Do not score a column just
because it exists.

- **❗ on 4–5**, **⚠️ on 3**, plain below.
- **Anything ≥ 3 needs one sentence of justification** in its detail block.
- **`?` in Chance** when nobody has measured it. The first fix is then a
  measurement.
- A score that depends on merge order is written `0 → 4 ❗ (if MR n lands)`.

### Verdict

A recommendation. The operator decides.

| | |
|---|---|
| `block` ❗ | Does not merge until this is fixed on the branch. Argued, not asserted: the detail block names what a customer or operator would experience if it merged as it stands. The same rule in both tables: a developer finding blocks when it can name that (a crash, a red suite), and a nit never can. |
| `ticket` | Merges. The fix becomes tracked work — say where it goes. |
| `talk` | The author has to answer something first, and the answer decides. |
| `–` | Recorded, nothing to do. |

### Three kinds of problem, two destinations

| | Where it goes |
|---|---|
| Defect in the new code | Finding. |
| The new code hands old code something it was never given, and the old code breaks | **Finding.** The MR owns it. |
| Pre-existing weakness the change merely revealed | `ISSUES.md`. |

The revert test separates the last two: would this still be broken if the MR
were reverted?

### The shape of a note

Sections with nothing to say are kept and marked "not touched".

````markdown
# MR <n> — `<branch>`

Reviewed <date>, read-only. Base `<merge-base>`, head `<sha>`.

| | |
|---|---|
| Commits | `<sha>` <subject>, … |
| Diff | <n> files, +<a> / −<b> |
| Author | <name> |

## What it does
Two to six neutral sentences. What the author set out to do and how.

## What the customer experiences
The customer table, worst first, every ✓ empty. Then one detail block per
finding (`### 1. <title>`), as the review skills describe.
Or: "Not run: code-only review (operator, <date>)."

## What the developer sees
The developer table, worst first, every ✓ empty. Then one detail block per
finding (`### D1. <title>`).

### Rules walked
One line per §2 rule and per §3 area: the findings it produced, or "nothing".
- **Readable**: D1
- **Manageable**: nothing
- …
- **Security**: nothing

Or: "Not run: customer-only review (operator, <date>)."

## Verified as not a problem

## Architecture check
Against §4.

## Interaction with other open MRs

## Suggested disposition
What blocks merge, what becomes a ticket, what needs the author.

## Commands for the operator
```
<test command>
<linter command>
```
````

---

## 6. Review log

Kept in `LOG.md`, next to this file: one row per review, newest first. This
file is the standard and is read in full at the start of every review, so the
record of what was reviewed lives apart from it.
