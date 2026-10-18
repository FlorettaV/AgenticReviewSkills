# How a finding is scored

The parts of scoring that are the same in every project: the columns, the
default scales, the verdicts, and where a problem goes. `mr-review`, `zoom-in`
and `review-followup` read this file together with the project's
`<review-records>/REVIEW.md` §5, which says how the columns are scored **for
that project** (who the customer is, what is live, whether there is personal
data) and where its scale differs from the defaults below. Where the two
disagree, the project's §5 wins for that project.

## The columns

Both tables share these:

| Column | |
|---|---|
| ✓ | `[ ]` until the operator says the row is handled. The reviewer leaves every box empty |
| # | The finding's number: `1`, `2`, … in the customer table, `D1`, `D2`, … in the developer table. It never changes once published, and a finding never changes table |
| Finding | The title, written by `review-writing` |
| Fix effort | How much work the fix is. This drives sequencing |
| Verdict | `block`, `ticket`, `talk` or `–` |
| Cause ✎ → Effect | Where to start reading |

**What the customer experiences** adds, between Finding and Fix effort:

| Column | |
|---|---|
| Chance | How often a customer hits the **visible effect** in normal use. It depends on facts the code does not carry (who is served, what is live), so ask rather than infer |
| Customer | How bad it is for the person affected when it happens |

**What the developer sees** adds:

| Column | |
|---|---|
| Rule | The §2 rule or §3 area it breaks, by its short name: the bold word in its heading in `REVIEW.md`. `customer-visible` for a bug a customer would see |
| Next change | How much it costs the next developer who touches this code |
| Security | Does it let someone do what they should not be able to |
| GDPR | Does it expose, mix or over-retain personal data |
| Layers | How many separate places absorb this one failure |

Security and GDPR sit with the developer, not the customer: the harm lands on
a customer, but the decision is made in the code, and that is where a reviewer
finds it. Anything with a Security or GDPR score is a developer finding, even
when a customer also sees it; its detail block says how often.

## Layers

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

## Next change

| | |
|---|---|
| `–` | Not about the next change. |
| `0` | Noticed. Costs nothing. |
| `1` | A reader pauses, then gets it. |
| `2` | The next change needs a second look somewhere the reader would not think to look. |
| `3` ⚠️ | The next change is likely to miss a place, with nothing to warn them. |
| `4` ❗ | Something actively misleads: a comment that says the opposite, a test that passes when the behaviour is broken. |
| `5` ❗ | It fails now: a crash, a red suite, a server that will not start. Usually a `block`. |

## The scale

`0`–`5`, or **`–`** when the column does not apply. Do not score a column just
because it exists.

- **❗ on 4–5**, **⚠️ on 3**, plain below. The renderer adds them; the data
  file holds only the number.
- **Anything ≥ 3 needs one sentence of justification** (the finding's
  `justify`).
- **`?` in Chance** when nobody has measured it. The first fix is then a
  measurement.
- A score that depends on merge order is written `"0 → 4 (if MR n lands)"`.

## Verdict

A recommendation. The operator decides.

| | |
|---|---|
| `block` ❗ | Does not merge until this is fixed on the branch. Argued, not asserted: the detail block names what a customer or operator would experience if it merged as it stands. The same rule in both tables: a developer finding blocks when it can name that (a crash, a red suite), and a nit never can. |
| `ticket` | Merges. The fix becomes tracked work — say where it goes. |
| `talk` | The author has to answer something first, and the answer decides. |
| `–` | Recorded, nothing to do. |

## Three kinds of problem, two destinations

| | Where it goes |
|---|---|
| Defect in the new code | Finding. |
| The new code hands old code something it was never given, and the old code breaks | **Finding.** The MR owns it. |
| Pre-existing weakness the change merely revealed | `<review-records>/ISSUES.md`. |

**The revert test** separates the last two: would this still be broken if the
MR were reverted? No → finding. Yes → issue. "The old code was fragile" does
not move responsibility for a regression onto the old code.
