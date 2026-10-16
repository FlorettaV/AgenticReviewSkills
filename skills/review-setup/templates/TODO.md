# Open items

**The operator ticks these**, once an item is either understood or handled
somewhere else — a ticket, a comment, a fix. A ticked item stays where it is
while its MR is open. When the MR is done and its note is deleted, its ticked
lines go too; its open A lines stay.

- **`R`** — found by the review that was asked for.
- **`A`** — additional. Noticed while doing something else, parked here rather
  than derailing the thing in hand.

Each letter has its own count: R1, R2, … and A1, A2, …. A new line takes the
next number of its letter, and numbers are never reused. Always name an item
with its letter. Each line names where it came from:

```
- [ ] **R<n>** (MR <n>) <the finding's title>
- [ ] **A<n>** (MR <n>) <something noticed while reviewing that MR>
- [ ] **A<n>** (–) <something noticed outside any review>
```

New MRs are added directly below, newest first.

---

## Active

## `REVIEW.md` / process

## Additional finds
