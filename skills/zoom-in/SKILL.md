---
name: zoom-in
description: Explain one finding, bug or defect in depth as What happens / Why / Fix, with verified file:line citations, ready to paste into an MR comment. Use this whenever the operator points at a single item and wants it opened up — "zoom in on 3", "zoom in on D2", "explain finding 2", "what's actually wrong with this one", "why does that happen" — and whenever a defect needs explaining well enough that someone else can act on it. Covers one item only; other findings stay parked.
---

# Zooming in on one finding

One finding, opened up: its score row, then its title and What happens / Why /
Fix. **Load the `review-writing` skill** (`review:review-writing`) — it owns the shape and every rule
about wording. This skill owns the evidence and the paste format.

The finding can come from either half of the note. A customer finding (`3`)
carries the customer score row; a developer finding (`D2`) carries its own
(Rule, Next change, Security, GDPR, Layers, Fix effort, Verdict), and its
What happens follows the
next developer, as `review-writing` describes.

## Constraints while you do it

**First, print the rules block** from the workspace `CLAUDE.md`, with
`zoom-in` as what loaded it. The operator uses it to see the rules were
re-read, so it comes before any other output. If the workspace has no rules
block, say so in one line and carry on.

Read-only over the project folder — no edits, however obvious the fix is; it
goes in the **Fix** section, not the tree. No git writes (`log`, `diff`, `show`,
`grep`, `archive` are all fine). Tests run only if the workspace `CLAUDE.md`
allows it; if it forbids them or says nothing, run none, not even one.
`review/` is writable, and the scratchpad is where probe scripts go.

`review/REVIEW.md` says how each score column is scored and holds the scale;
read it rather than assuming, because it changes.

## The steps

1. **Start from the draft.** If the finding is in a note, rebuild its draft (the
   shape is in `review-writing`) from the note and the branch. If it is new — a
   bug the operator points at — fill the draft from scratch.
2. **Verify the evidence** (below). Every line in Mechanism is printed on the
   branch before it is quoted.
3. **Write** title, What happens, Why and Fix from the draft.
4. **Run the editor pass** from `review-writing` on the title and What happens.
5. **Deliver** in the paste format (below).

## Verify before you publish

Every cited line gets printed and read back. It costs one command and it is the
only check that actually works:

```
git grep -n -F "<exact text>" origin/<branch> -- <path>
```

Line numbers are on the branch, never on main. `git grep` returns every hit,
and the first is often the wrong one — print them all and pick deliberately.

Where the claim is about behaviour rather than structure, prove it. A short
script that runs the code in question (in Python: imports the module) and
prints the outcome with and without the change turns an argument into a fact,
and it is not the test suite. Two lines of real output beat three paragraphs of
reasoning:

```
with the change    -> price None
without the change -> price 12.99
```

## The paste format

The operator copies zoom-ins into MR comments (GitLab, GitHub). **The terminal
renders Markdown, so copying rendered text loses every `**` and backtick** —
only a code block is copied literally. So deliver the zoom-in itself as raw
Markdown inside one outer fence of **four** backticks with the `markdown` tag
(` ````markdown ` … ` ```` `). The inner code blocks keep their normal three
backticks, and the four-backtick fence stops them closing the outer one. Any
remark for the operator that is not part of the comment goes outside the
fence.

**The score table stays outside the fence, rendered, above it.** It is for the
operator to read, not to paste, and it reads far better as a real table. The
fence starts at the `### <n>. <title>` heading, so the title is pasted along
with the comment. A comment without it makes the author guess which finding
it answers.

Inside the fence, write the Markdown that GitLab and GitHub both read:

- **The three labels are bold**, each starting its own paragraph:
  `**What happens.**`, `**Why.**`, `**Fix.**`.
- **Every `file:line` is inline code**: `` `shop/pricing.py:142` ``. The `✎` /
  `→` marker goes outside the backticks: ✎ `pricing.py:142`. Function,
  variable and setting names are inline code too: `VAT_RATE`, `round_price()`.
- **Code is always a fenced block with a language tag** (` ```python `,
  ` ```bash `, ` ```yaml `), so the code host highlights it and the reader can
  copy it. Never indent code, and never put multi-line code inline.
- **Code only where a few lines say it better than a sentence.** The rule is
  about how code is formatted when it appears, not a reason to write more of
  it. Why quotes the four or five lines that matter. Fix shows code only when
  the change is a handful of lines, about ten at most. A bigger fix is
  described in one or two sentences, naming the function and the call sites,
  and the author writes it. When code does appear, it can be copied as is:
  real lines, no `…` inside, no prose in the block.
- **Probe output** (what a script printed) is a plain ` ``` ` fence with no
  language, so it is not highlighted as code.

## When the operator corrects the premise

A finding's score rests on facts the code does not carry — what is deployed,
what is served, what is planned. When the operator supplies one that undercuts
the row, re-score it in the open rather than defending the number. Often the
retired finding leaves a sharper one behind: a bug that cannot reach a second
shop may still be visibly wrong in the only shop there is.

Saying "that drops this to 0, and here is what survives" keeps the table worth
reading. Quietly leaving the old score does not. The records are updated by
`review-followup`.

## Stay on the one item

This is the part that is easy to get wrong while being helpful. Explaining one
finding turns up neighbours — a related defect, a better architecture, a second
reader of the same field. Do not append them. The operator asked about one
thing; a reply carrying five is how a clear explanation becomes a wall.

Park the neighbours in `review/TODO.md` without mentioning it, tagged with the
review they came from (format in `review-followup`), and answer what was asked.
If a neighbouring finding genuinely changes the fix for *this* one, that
belongs in **Fix** in a sentence — not as a second finding.

The same goes for scope. A question asked while zooming in — including a meta
one, "why does this look weird" — is about this finding and its note. Other
notes and earlier reviews are touched only when the operator names them.
