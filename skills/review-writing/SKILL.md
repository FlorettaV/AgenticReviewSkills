---
name: review-writing
description: Turn review findings into plain language — titles, What happens / Why / Fix, TODO lines and replies — from a structured draft, then run a fresh editor pass over the result. Loaded by mr-review, zoom-in and review-followup whenever they write anything the operator or an author will read. Use it directly when the operator asks to rewrite, simplify or check the wording of a finding, a note or a TODO line ("the titles sound off", "make this readable", "say it plainer").
---

# Writing findings in plain language

A finding is read to decide what to do. The reader may not know the code. If
they have to decode a sentence, they put the finding off.

The writer follows these rules from the first sentence. The editor pass is a
second reading, not the place where a finding becomes legible.

Writing happens in three steps, always in this order:

1. **Draft.** Collect the facts per finding in a fixed shape. No prose yet.
2. **Write.** Turn each draft into a title and What happens / Why / Fix, using
   the rules below.
3. **Edit.** A fresh reader with only this skill checks the wording against the
   draft.

Keeping the facts apart from the wording means the editor can change every
sentence without changing a single fact.

## 1. The draft

One block per finding. Every field is filled, or says `none`.

```
#            3
Scores       Chance 3 · Customer 3 · Fix effort 1 · Verdict ticket
Cause        ✎ shop/settings.py:40 → shop/pricing.py:142
Sequence     1. We delete the upgrade step for old settings files.
             2. An old shop's settings still say currency:, and nothing reads that key any more.
             3. The shop starts without prices. Every product page shows "price on request".
Who sees it  every visitor of a shop installed before the change
Mechanism    the four or five lines that matter, quoted, each with file:line (verified on the branch)
Fix          the smallest change that closes it; a structural fix named separately, if there is one
Justify      one sentence per score of 3 or more
Proof        what a probe printed, if one ran
Must keep    the conditions, numbers and qualifiers the finding depends on:
             "only shops installed before version 2", "only when the cache is on"
Glossary     domain nouns used above, and whether the project's glossary has them
```

What the draft must hold before anything is written:

- **Sequence** is the argument. Each line has someone who does something: we,
  the shop, the customer, the browser. The lines are in the order things
  happen. The last line is what someone sees.
- **Who sees it** is a person or a role, never a module.
- **Mechanism** cites only lines that were printed and read back on the branch.
- **Must keep** lists every condition that makes the finding true. If a
  sentence without it would be wrong or would overstate, it belongs here. It
  is what stops a plainer sentence from becoming a less true one.
- **Scores** use the project's scale from `review/REVIEW.md`. Every score of 3
  or more has its sentence in **Justify**.

A draft that cannot fill Sequence or Who sees it is not a finding yet. It is a
question for the author (a `talk`) or a line in `review/ISSUES.md`.

### A developer finding

A finding from the developer half (`D1`, `D2`, …) uses the same draft, with two
differences:

```
#            D2
Scores       Rule Manageable · Next change 3 · Security – · GDPR – · Layers – · Fix effort 1 · Verdict ticket
Sequence     1. We write the fallback colour for the buttons in three places.
             2. A developer changes it for the chat button.
             3. The send button keeps the old colour, and no test notices.
Who sees it  the next developer who changes a button's colour
```

- **The developer is the actor.** The Sequence ends with what the next person
  who touches this code runs into: the place they miss, the comment that
  misleads them, the test that stays green.
- **Who sees it** is that developer, named by what they set out to do ("the
  next developer who adds a brand"), not "maintainers".

Everything else — Mechanism, Fix, Must keep, Justify — is the same, and so are
the writing rules and the editor pass below.

## 2. Writing

### Say it as a sequence, not as a category

The standard, in the operator's own words:

> We're including fontawesome. Then we decide not to use those icons on
> location X, Y, Z.

Two short sentences. We did something, then we did something else, and the two
do not fit. The reader sees the problem because the facts are next to each
other, not because a label was put on it.

| Not this | This |
|---|---|
| "The site now has two icon systems" | "We load Font Awesome. We don't use it for the cart, search, menu or close buttons." |
| "A client-supplied identifier is now trusted for authorisation" | "The browser sends the customer number. We now load that customer's orders with it, without checking it against the login." |
| "Three modules absorb the failure identically" | "Saving an order can fail four ways. Three of them write nothing to the log, and the customer sees the same thank-you page as when it worked." |

Four habits behind it:

1. **Name who does it.** We, the shop, the browser, the customer. An abstract
   subject ("a validator with a narrower view") hides which code to open.
2. **Put the facts in the order they happen.** First we do this, then that
   happens. The order carries the argument, so no "however" is needed.
3. **Name the places, not the category.** "the cart, search and menu buttons",
   not "the remaining controls".
4. **Do not invent a noun for the problem.** No *asymmetry*, *second home*,
   *coupling*, *drift*, *surface*, *grounded*. If a word is not in the
   project's glossary and would not survive being said out loud to the author,
   it is a label standing where a sentence should be.

**Name a thing by what people see, not by the code's word for it.** "The
fallback string", used a dozen times as a label, means nothing to the shop
owner. "The 'We're closed' text the shop owner sets under Opening hours" does.

**"We" is the inclusive we.** All of us are responsible for the code and work
on it together, so it is "we" whoever wrote the change.

Short sentences. One idea each. Say it once: no hedging, no second version of
the same point, no sentence that only introduces the next one.

### Titles

The title is the Finding column of the table. It is also the heading of the
finding's detail block, word for word, and the start of its TODO line.

It comes from the first and last lines of **Sequence**: what we did, and what
someone then sees.

- One or two short sentences.
- No file names, function names, commit hashes, config keys or paths. They
  go in the Cause column. A commit may be named by its quoted title ("a commit
  called "rename variables""), never by its hash.
- Only what someone needs in order to decide whether to care. "And logs
  nothing", "step 1 passed", the numbers: those go in the detail block.

| Before | After |
|---|---|
| We delete `migrate_v1_settings()`. A shop whose `settings.yaml` still has `currency:` and no `currencies:` starts with no prices, and logs nothing. Every product page then shows "price on request" | We remove the upgrade step for old shops. An old shop then starts without prices, and its product pages show none |
| We move `checkout.test.js` to `tests/e2e/`. `npm test` only runs `tests/unit/`, so the checkout tests now run from nowhere | We move the checkout tests to a folder nothing runs. They stop running |
| `a1b2c3d` says "rename variables". It also changes the rounding in `calc_vat()` and deletes the `/admin/export` route | A commit called "rename variables" also changes how VAT is rounded, and removes the export page from the admin |
| We commit `config/local.yaml` with the test payment keys. Main ignores that file on purpose. Merging puts it into every checkout and can overwrite a shop's own keys | We commit the local settings file, which main keeps out of git. Merging can replace a shop's own payment keys with test keys |

### What happens / Why / Fix

Every finding in a note, and every zoom-in, has the same shape:

```
### <n>. <the title, word for word>        (### D<n>. for a developer finding)

<its score row>

**What happens.** ...
**Why.** ...
**Fix.** ...
```

The three parts answer three different questions. Blending them into prose
loses all three.

- **What happens.** The **Sequence**, written out for someone who has not read
  the code. The trigger, then what the customer or operator sees. No file
  names. The test: could the operator repeat it to a colleague? For a
  developer finding, the trigger is the next change and the end is what that
  developer runs into: "A developer changes the chat button's colour. The send
  button keeps the old one, and no test notices." Still no file names: they go
  in Why.
- **Why.** The **Mechanism**. This is where the citations live. Mark what the
  change touched (✎) and unchanged code it reaches (→). Most real findings sit
  on the → side: the new code is fine, and an old reader breaks. Quote the four
  or five lines that matter rather than describing them — a reader who can see
  `if order.status != "paid"` does not need it paraphrased.
- **Fix.** The smallest change, not the best refactor. If a one-line fix and a
  structural fix both exist, give the one-liner and name the structural one
  separately. They are different decisions with different risk, and tangling
  them makes the blocker wait for the design debate.

Then one sentence for every score of 3 or more, from **Justify**. A high score
with no argument behind it is how a scoring table rots.

### TODO lines

A TODO line starts with the finding's title, word for word. The same title
rules apply.

## 3. The editor pass

Run it on every note before it is shown, and on every zoom-in. It reads the
way a colleague would: without knowing the code. That makes it a good judge of
wording and a bad judge of facts, so it gets the last word on the first and
none on the second.

**It covers the title and What happens only.** Those are the parts a reader
without the code has to understand. Why and Fix stay as the writer wrote them:
they name code and changes, and rewording them without knowing the code is how
a fix stops being exact.

Start a **fresh** sub-agent: a general-purpose agent, never a fork, because a
fork carries the writer's context and reads past the same jargon. Give it:

- the path of this file, `${CLAUDE_SKILL_DIR}/SKILL.md`, to read first;
- the drafts;
- each finding's title and What happens.

Tell it to return a rewritten title and What happens per finding, under these
rules:

- **It changes wording only.** It adds no fact and drops none.
- **Every item in Must keep stays.** It may reword one ("before version 2" →
  "installed before version 2"), never drop or soften it.
- **Every sentence must be supported by the draft.** Where the text says
  something the draft does not support, it flags it rather than fixing it.
- **It asks only when it cannot tell what a sentence means**, and then it
  asks rather than guesses: "Which shops count as old?" A sentence the editor
  cannot follow is one a colleague cannot follow either. A sentence it merely
  would have written differently gets a rewrite or nothing, not a question.
- **It lists each change**, old → new, with the rule it applied.

**The questions and flags come back to the writer**, not to the operator. The
writer knows the code and answers each one by changing the text, or by fixing
the draft and re-verifying the citation. Only a question the writer cannot
answer from the code goes further: it becomes a question for the operator in
the reply, or a `talk` for the author.

The writer then applies the edits one by one, checking each against the draft
and the code, and reverts any that changed a fact or dropped a Must keep item.
The editor wins on wording. The draft wins on facts.

**One round, never a loop.** The writer does not send the result back to the
editor. Two readers who each guard one thing would otherwise trade "you lost
my nuance" and "that is still unclear" without end. The editor reads once;
the writer decides, and that is final.

Then run the checker on the note:

```
python3 ${CLAUDE_SKILL_DIR}/check_note.py review/<the note>.md
```

It reports a table row with the wrong number of cells, a title over two
sentences or holding code, a detail heading that is not the title word for
word, a block without its score row or one of the three labels, and the banned
nouns in titles and What happens. Fix what it reports. Whether the words are
right is still a read.

## Replying

The note is complete. The reply is short.

- **Compact by default.** A reply about findings shows the **full** findings
  tables — both halves, every column, never a cut-down one; a half that did
  not run gets one line saying so — then what blocks, the questions for the
  operator, and the commands. What / Why / Fix stays in the note until
  the operator asks for one.
- **Answer, stop, wait.** Do not re-show a table, re-list findings or recap
  earlier conclusions unless asked.
- **One thing at a time.** Answer the item asked. Anything else that surfaced
  goes into `review/TODO.md` silently (see `review-followup`).
- **Never a bare item number.** Parking is silent, so the operator has never
  seen most TODO items. Every item number in a reply carries what it is, in a
  few words, at least the first time in that reply: "A11 (read-only in
  layers)", not "A11". Three or more numbers become a small table of number
  and title. A finding's number from the note is enough on its own only while
  that note is the one being discussed.
- **When the operator paraphrases a finding back**, correct only what would
  change what they do. A wrong noun that leads to the wrong fix is worth
  correcting. A loose word that still lands on the right conclusion is not.
