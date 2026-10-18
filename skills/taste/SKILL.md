---
name: taste
description: Build and keep a map of where a project's team puts things — the house habits nobody fully wrote down — from the code and its git history, with past review comments as optional extra evidence. Writes review/MAP.toml (and MAP.md for people), points out where the team's placement doesn't follow plain logic or its own docs, and turns those spots into short questions for the team. Three modes: scan (build the map), rescan (recount what changed since), status (what the map says and what waits for the operator). Use when the operator asks to "scan our taste", "map where things go", "learn this codebase's habits", "what does this team care about", "rescan", "taste status", or after review-setup. Optional: reviews work without it.
---

# Mapping where the team puts things

Why the skill works this way: `${CLAUDE_PLUGIN_ROOT}/docs/how-people-place-things.md` in this
plugin. This skill is the working method.

A team groups things that look alike under the same rock, so that next time
there's one place to look. Most of that is never written down, much of it is
in no review comment, and some of it doesn't follow plain logic at all. The
code and its history show it: where things are, what moved, which file got
copied, which way new code goes. This skill turns that into a map that reviews
(and code writing) can compare against cheaply. It never decides what the
team wants: the operator does.

## The rules

Load and print the rules block from `${CLAUDE_PLUGIN_ROOT}/reference/rules.md`, with `taste` as what
loaded it. On top of those, three hold here:

- **Git is read-only, and so is the code host.** `git log`, `git show`,
  `git grep`, `git ls-tree`; never a write. On the code host: read merge
  requests and threads only; never post, approve, resolve or merge.
- **No names and no e-mail addresses in any file.** Authors and reviewers
  become pseudonyms (`a-` or `r-` plus four hex characters of a hash of their
  e-mail or user id). Quotes keep their words, with names replaced by roles.
- **Counting scripts live in the scratchpad**, run with `python3 -I`, and get
  the project path as an argument. A script worth rerunning is copied into
  `review/taste/` with a line saying what it counts.

## Files

| File | What it holds |
|---|---|
| `review/MAP.toml` | the map: one `[[rock]]` per kind of thing. The source of everything else |
| `review/MAP.md` | the same, written for people: one table and the questions for the team |
| `review/taste/scans.md` | one row per scan or rescan: date, mode, commit counted at, entries added or changed |
| `review/taste/records.jsonl` | only when review comments were read: one decision record per human thread |

`REVIEW.md` says where the map is and when it was last counted
(`Map: review/MAP.toml, counted <date> at <commit>`). It never copies map
entries: placement lives in the map only, so the same rule never sits in two
places with different wording.

## An entry

```toml
[[rock]]
kind          = "types for a module's API (request and response shapes)"
find          = ["src/modules/*/src/hook.ts", "src/modules/*/src/*types.ts"]
team_does     = "in a separate file only: 17 modules. In the hook only: 7. Both: 9"
logic_expects = "next to the hook that uses them"
docs_say      = "<name>-types.ts"
example       = "src/modules/orders/src/hook.ts"
direction     = "hooks holding types: 0 (Jan 2025) -> 16 now; separate files still added too"
eras          = "both ways keep being added: 9 and 18 before 2026, 8 and 8 since"
review_asks   = "4 times, 1 reviewer, marked required"
authors       = "7 authors use the hook, 6 the separate file"
status        = "mixed"
why           = "unknown"
ask_team      = "AGENTS.md says types go in <name>-types.ts, but reviews ask for them in the hook, and the code does both. Which one do we want?"
counted_at    = "a1b2c3d4"
```

- **kind** is a name from the map's list of kinds. A new entry uses an
  existing name, or adds one with the operator's yes. That keeps "API hook
  types" from appearing next to "hook type definitions".
- **find** says where to look. Every count in the entry can be made again
  from it, and a review loads only the entries whose patterns match the files
  an MR touches.
- **team_does** is what the code does, with counts. **logic_expects** is what
  plain logic would suggest instead, and **docs_say** what the project's own
  docs say. They're there to show the gap, not to say who's right.
- **example** is the file to compare new code with: the one the team copies,
  or the clearest one that follows the entry.
- **status**, from the counts only:

  | Status | Means |
  |---|---|
  | settled | one way, nearly everywhere; the odd ones are few |
  | mixed | two or more ways, each with real numbers |
  | moving | new code goes one way, old code the other |
  | questioned | one way, but someone in a review asked why |

- **why** is `unknown` until a person gives a reason. Then it's a dated quote
  with who said it, by role: `operator, 2026-10: "written out so grep finds the
  path"`. Several can stand side by side, even when they disagree.
- **ask_team**, on mixed and questioned entries and where code and docs
  disagree: one plain question, with the likely answer in it (below).

## Each layer has one job

- **The counts decide the status.** Nothing else moves an entry between
  settled, mixed, moving and questioned.
- **Eras only shape the question**, and only on a mixed entry. A split by when
  things were written ("before 2026 / since") can show that the team switched
  rocks and old pebbles were never moved. It never decides anything.
- **Whys are only context.** A why never changes a status and never stops a
  review from pointing at something. It's one person's memory, not a rule.

A new layer is fine as long as it says when it applies and overrules none of
these.

## What to look for

Work from the code and its history. In this order, each one cheap:

1. **The docs first.** If the project describes its own structure (an
   `AGENTS.md`, a project-structure doc, coding guidelines), every placement
   rule in it becomes a candidate entry, with `docs_say` filled. Note when
   each doc was written: that's an era boundary you get for free.
2. **Where things are now.** For each kind of thing (a page, an action, an
   API hook, its types, a URL, a component folder, a test), count the ways
   it's done today.
3. **Moves.** Files moved to another folder (`git log -M --diff-filter=R`).
   A move is a pebble someone put under another rock, on purpose. Group
   moves by date: a batch of moves on one day is a decision.
4. **Spread over time.** The same counts at a few points in time, or split by
   when each file was created. Which way does new code go?
5. **Copies.** A new file that starts as a near-copy of an existing one shows
   which file the team treats as the example.
6. **Who.** How many authors do it each way (pseudonyms). One author is a
   habit; many authors is the team.

Then sort each entry: where `team_does` and `logic_expects` (or `docs_say`)
agree, the entry is short and mostly there for the example. **Where they
don't, the entry is the point of the map**: that's where feeling, effort and
history did the placing, and where reviews and new code need it most.

Four checks before writing an entry down:

- **Look at what's in a pattern before calling it one rock.** "Domain code
  imports Infra" turned out to be two stories: shared interfaces the team
  keeps in Infra, and client DTOs used straight away. Count them apart.
- **Trust dates only where they hold.** A big move that rewrote files (new
  namespaces, a new root folder) makes their creation dates the move's date.
  Split eras after such a move, and say so.
- **A text search is rough.** Say so in the entry when a count comes from
  one, and read a few hits to check they're what the pattern says.
- **The odd ones out matter.** "A constant in 2 files, written out 215
  times": name the two files. They're the ones someone will copy next.

## Questions for the team

A mixed or questioned entry, or one where the code and the docs disagree,
gets one question in `ask_team`. Written so it can be answered at a glance,
on a good day, by someone who never touched that code:

- **Plain words**, no labels or terms the reader has to look up.
- **Offer the likely answer**, so it only needs a yes or no: "Did we decide
  that shared interfaces like these live in Infra?" Checking an answer costs
  far less than coming up with one. Where the eras show a switch, say it:
  "these used to go loose in components/; since 2026 most go in a subfolder.
  Did we switch, with the old ones just not moved yet?"
- **The evidence next to it**, in a few numbers, so a quick "yes" is still an
  informed one.

The operator decides which questions go to the team, and when.

## scan

Builds the map. Before counting, say in one line what you'll look at and
wait: "This project has an AGENTS.md from last month and 3 years of history. I'll
start from its layout rules, then count about ten kinds of things over five
points in time. Go?"

1. Read the docs the workspace `CLAUDE.md` and `REVIEW.md` name, and find the
   project's own structure docs.
2. Count, as in "What to look for", in a scratchpad script.
3. Write `review/MAP.toml`: about ten entries for a first scan, the ones
   where logic and the team disagree first. Then `review/MAP.md`: one line
   saying what the columns mean (the logic column shows the gap, not what the
   code does), one table (what, what the code does, what logic or the docs
   suggest, status, in words: "settled on writing them out"), and the
   questions for the team.
4. Add the row to `review/taste/scans.md` and the `Map:` line to `REVIEW.md`.
5. **Ask the operator**, in one short list: the entries, to veto ("which feel
   wrong, useless or obvious?"), and the questions for the team. Only the
   operator's yes makes the map the one reviews use.

### Review comments (optional, extra evidence)

When the code host can be read (a code host MCP server, `glab`/`gh`, or an API
token the workspace `CLAUDE.md` names), past review threads add what the code
can't show: a reviewer who keeps asking for something the code doesn't do
yet. Read them only when the operator asks, after the code-based map exists.

- Show the plan in one line first ("84 merge requests since April, in batches
  of 20, about 2 calls each. Go?"). Skip dependency upgrades, reverts, bots,
  and changes over the size cap (`REVIEW.md`, default 1000 lines of real
  code).
- One record per human thread, where the thread **ended**:

  ```json
  {"id": 10, "mr": 942, "date": "2026-10-12", "kind": "code",
   "question": "Should this list be paginated?", "decision": "no pagination",
   "condition": "the list stays small: about 5 providers",
   "why": "pagination on a 5-item list is noise", "strength": "required",
   "outcome": "enforced", "reviewers": ["r-3fa9"]}
  ```

  `kind` is `code`, `process` (never a finding) or `other-repo`. `strength` is
  `optional` when the reviewer says so; an optional ask is mentioned at most.
  Check `outcome` in the code: a suggestion can be applied without a note.
- Batches go to sub-agents that write records to the scratchpad and return
  counts only. Their prompt starts with the rules block.
- A record becomes `review_asks` on the entry it belongs to, as a count:
  "asked 4 times, by 1 reviewer". Never the reviewer's pseudonym in a finding.
  A record that fits no entry is a candidate for a new one, shown to the
  operator.
- One reviewer asking is a person's rock; several reviewers is the team's.
  Keep them apart: an average of several people's rocks is a rule nobody
  holds.

## rescan

Recounts the map at the current commit, from each entry's `find`, without
reading the code host. For each entry:

- new counts, `counted_at`, and `direction` when it moved;
- a status change only when the numbers clearly moved, said in one line:
  "types for the API: mixed → moving (the last 6 new hooks hold their types)";
- a why marked "may be out of date" when its entry is moving away from it;
- entries that matched no merge request since the last rescan are offered for
  the archive section at the bottom of the file, which reviews don't load.

Then the same short list to the operator as after a scan, with only what
changed. `review-followup` runs a small rescan of the entries one review
touched (its "Tidy the map").

## status

No counting, only the files: when the map was last counted, the entries by
status (questioned and mixed first), the questions for the team that are
still open, and entries waiting for a yes.

## The hint

`mr-review` says this once, in the reply, when a project has no
`review/MAP.toml` yet:

> 💡 **Reviews that know your team's habits?** Run `/review:taste scan`. It
> maps where the team puts things from the code and its history, and turns the
> spots that don't add up into short questions for the team. Optional:
> reviews work fine without it.
