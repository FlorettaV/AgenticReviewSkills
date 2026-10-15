# Issue tracker

Things reviews bumped into that are **not the reviewed MR's fault**. The MR
touched an entry point; the module behind it looked wonky; that observation is
worth keeping without letting it hijack the review.

## What belongs here

**The revert test.** Would this still be broken if the MR were reverted?

- **Yes** → it belongs here. Pre-existing. The MR's only role was to make it
  visible.
- **No** → it is a finding in that MR's note. The MR caused it, so the MR owns
  it, even when the broken code is old and untouched.

Each issue is numbered `ISS-<n>`, names the review that found it, and says what
"fixed" would look like.

---
