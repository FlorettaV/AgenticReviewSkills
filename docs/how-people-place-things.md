# How people place things — what reviews learned about humans

Status: lessons from one long session with the operator (2026-10-18), tested
on two merge requests of a frontend project and a first look at a large backend project. The full notes, with
the evidence, are local only, in `research/why-humans-comment.md` (not in git). This file keeps what the skills
are built on.

## Where we started

The goal was "catch what the developers catch". Blind reviews found every bug
the developers raised and more, but almost none of what they *said*: 0 of 4
human threads on one merge request, 3.5 of 7 on another. Learning more review history (a year
instead of six months) added half a hit. The missing part wasn't in the
volume of comments.

## What humans are like, as far as reviews go

The words used here (paths, tokens, pebbles and rocks, personal MDs,
triggers, displace, and the rest) are explained in `docs/glossary.md`.

What follows from it:

1. **People group things to spend less energy.** Same things in one place:
   next time there's one place to look. A codebase's shape is a map built to
   save its own people effort.
2. **A review comment is recorded friction.** It marks where a reader had to
   stop, jump to another file, or ask "why is this here?". AI finds what
   breaks; humans mark what slows them down. All 8 missed threads were
   friction, none were bugs.
3. **"The same" is decided by feeling and memory, not by a rule.** It's
   measured against an example ("like the other pages in that folder"), and
   by how the user or reader experiences it, not by where it comes from. The
   human grouped two error messages as one, because staff see *an error*; the
   review kept them apart, because they come from different places.
4. **Feelings come first, then budget, then reasons.** The reasons are the
   last and most personal step, so the "why" in a thread is often made up
   afterwards, or missing. 75 of 300 records gave none.
5. **Comments depend on the day.** The same code gets a comment on a good
   day and silence on a bad one. Two-thirds of merge requests get no comment
   at all. No two reviewers would write the same notes. So "match the human
   comments" is the wrong target.
6. **A comment often displaces cost.** "Do it this way" is the way that's
   cheap *for the reviewer*. Because teams want a shared understanding, one
   person's cheapest move spreads and becomes team habit. In the frontend project, two
   reviewers are on 238 of 300 records.
7. **Rules get in by a scar, by trust, or by copying.** A pebble can sit under
   a rock that doesn't make sense, because someone copied it.
8. **The code is a snapshot; people know which way it's moving.** Old and new
   ways sit side by side in the code. Only the history shows the direction.
9. **One unknown word costs the whole paragraph.** The reader can't skip it,
   so they re-read everything around it to guess what it means.
10. **Checking an answer is cheaper than finding one.** A question that offers
    the likely answer only asks for a yes or no.

## What the skills do with it

**Share the costs.** The review does the careful reading (cheap for Claude)
and hands it over cheaply: short, plain, pointing at code the reader may
know. The reader sorts it with their feelings and memory. Success: the reader
quickly knew what to do with each point.

**Look at the neighbours** (`mr-review`, the Neighbours walk). For each new
thing: does it look like its neighbours? Is any of it already done somewhere
else? Where would a reader stop and ask why? On one merge request a blind run with only
these questions got 1.5 of 4 human threads, against 0 of 4 before. The two
misses were near misses: the reviewer stood next to them while asking a
different question.

**Know where the answer lives.** Some answers are in the code (neighbours
that agree). Some are in people's history (one reviewer asked four times).
Some are facts in someone's head (how many items a list will ever hold). The last
kind can only be asked, so ask it cheaply.

**A map of where the team puts things** (`taste`, `review/MAP.toml`). Built
from the code and its history, because that's where most of the taste is:
moves (a pebble put under another rock), copies (which file is the example),
spread over time (which way it's moving). Review comments are extra evidence.
When the project has written docs on structure, the map starts from them and
measures how well the code follows them.

The map's value is in the spots **where logic doesn't (fully) explain why
the pebbles are there.** Not right or wrong. Those spots become short
questions for the team.

**Each layer has one job, and none overrules another:**
- counts decide the status;
- eras only shape the question, and only on mixed entries ("these used to go
  here, newer ones go there; did we switch?");
- whys are only context: a dated quote with who said it, never a reason to
  stop flagging something.

**Cheap for Claude too.** One rule, one place. A rule with its reason. Say
what matters most. Load a part only when it's needed (a search pattern per
map entry). The map is tidied lightly after each review.

## What it's for (operator, 2026-10-18)

Reviews that:
1. **catch the bugs**: technicalities and logic, which Claude is very good at,
   and which stay the review's first job;
2. **understand how the team places things**, to help people put their
   pebbles somewhere that feels right;
3. **work towards rules and a codebase that cost little to read and decide
   on**, for people and for Claude.

Nobody expects it to be perfect. Questions are fine.

## The full circle

1. **People place pebbles by feeling.** That's fine; a codebase doesn't need
   to be 100% consistent.
2. **The map catches the essence:** where the team puts things, and the
   spots where neither logic nor feeling explains the placement.
3. **Those spots become short questions**, so the people who decide meet
   the inconsistency and can answer it on a good day.
4. **The answer is made true in the code, not written down as a rule:** one
   mechanical refactor MR (with its recipe in the description, so reviewers
   check the recipe and a few samples), plus a lint rule or test where one
   fits. Then the map entry settles by itself.

So the fewer rules anyone has to read, the better: what's settled is in the
code, what's chaos becomes a question, and what's decided gets made true.
What stays outside the circle: bugs, security and personal data are still
reviewed on their own terms, and a decision that depends on a fact (how long
a list will get) stays a question.

## Mistakes worth not repeating

- A hand check made with hindsight looked cleaner than the blind test (the
  "neighbours write URLs out" claim missed the two constants in the very
  pages the change had copied). Test blind, with a fresh agent.
- The same blind reviewer still invented labels ("Reader stop") despite a
  rule against them. The editor has to check for it.
- Era dates break when a big move rewrote the files (a backend that moved its whole `app/` →
  `src/`); split where the dates are trustworthy.
- One pattern can be two stories (domain code importing infrastructure code: shared
  interfaces kept in Infra, and client DTOs used directly). Look at what is in
  a pattern before calling it one rock.
