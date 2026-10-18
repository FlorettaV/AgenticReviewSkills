# Words we use

The words the review skills and their operator built together. One place for
all of them: a skill or note may use a word from this list without explaining
it again; any other term is explained where it appears (`review-writing`).
A new word goes in here only with the operator's yes.

The columns, scales and verdicts of a review note (Chance, Customer, Next
change, Layers, `block` / `ticket` / `talk`, ✎ and →) are explained in
`reference/scoring.md` and the `review-writing` skill, not here.

## How people work

| Word | Means |
|---|---|
| **paths** | a person's thinking capacity. Careful thinking uses it up ("from Opus to Sonnet to Haiku"); sleep brings it back. Low on paths, people ask for "simpler" because their brain stops taking in hard things, not because they can't understand |
| **tokens** | a person's allowance for actions: opening the editor, clicking, finding the file, reading (about 238 words a minute). Food and drink top it up |
| **bonus energy** | energy a person gets back from work they enjoy. Different people get it from different things |
| **outage** | a bad day: little sleep, bad food or something emotional, and the "Opus" just isn't there today |
| **empathise / resolve / displace** | three ways out when code doesn't match what someone expected: imagine how the author got there; look for a compromise; or push the cost onto someone else ("why?", "do it my way") |
| **personal MDs** | a person's own experience, like their own set of notes. Cheap to use once it's opened |
| **trigger** | a cue that opens the right MD: "remember when …?" |
| **ripple** | one person's cheapest way spreading through a team, because people want a shared understanding |
| **scar** | a lesson from one bad moment, kept as a habit; its story is rarely told |

## Where things go

| Word | Means |
|---|---|
| **pebbles and rocks** | the things in the code (pebbles) and the places the team puts them, with the ones that look alike (rocks) |
| **neighbours** | existing code to compare new code with: of the same **kind** (the other details pages, wherever they are) or in the same **place** (the other files in that folder) |
| **differs from neighbours** | new code that does something differently from its neighbours |
| **the map** | `review/MAP.toml` (and `MAP.md` for people): where a project's team puts each kind of thing, built by the `taste` skill |
| **rock** (in the map) | one entry: one kind of thing, where the team puts it, and the counts behind it |
| **settled / mixed / moving / questioned** | a rock's status: one way nearly everywhere / two or more ways / new code goes another way than old code / one way, but someone asked why |
| **odd ones out** | the few places that do it differently from the rest. Name them: they're the ones someone copies next |
| **eras** | a split by when code was written (before and after a big change). Only used to word a question, never to decide |
| **why** (in the map) | a reason someone gave, kept as a dated quote with who said it. Context only: it never decides anything |
| **questions for the team** | short questions for the spots where logic doesn't explain the placement, with the likely answer offered (`ask_team` in the map) |

## How we work together

| Word | Means |
|---|---|
| **share the costs** | Claude does the careful reading, which is cheap for Claude, and hands it over cheaply. The person decides with their feelings and MDs, which is cheap for them |
| **the full circle** | people place pebbles by feeling → the map catches it and finds the chaos → chaos becomes a question → the answer is made true in the code (a refactor and, where possible, a lint rule), not written down as a rule |
| **make it true in the code** | record a decision by changing the code to follow it, instead of writing it down |
| **blind** (a review) | done without reading the MR's comments or the commits after the version reviewed, so it can be compared fairly with what the reviewers said |
| **prediction** | the comments a blind review expects the human reviewers to make, written down before reading them |
| **upkeep** | the check of the review files' state (the skill of that name): duplicates, contradictions, stale items, unexplained words |
| **tidy the map** | the small recount of the map after each review (`review-followup`) |
| **research/** | the plugin's local-only folder for notes that name real projects; never in git |
