<!-- review format: 2. Rendered from mr-13-feat-currencies.toml by the review plugin; change the .toml and render again, never this file. -->
# MR 13 — `feat/currencies`

Reviewed 2026-10-16, read-only. Base `1a2b3c4`, head `5d6e7f8`.

|  |  |
|---|---|
| Commits | `5d6e7f8` Support several currencies per shop, `9a8b7c6` Remove the old settings upgrade |
| Diff | 6 files, +142 / −58 |

## What it does

A shop can now sell in several currencies. The settings key `currency:` becomes
a list under `currencies:`, and the step that upgraded old settings files is
removed.

## What the customer experiences

| ✓ | # | Finding | Chance | Customer | Fix effort | Verdict | Cause ✎ → Effect |
|---|---|---|---|---|---|---|---|
| [ ] | 1 | We remove the upgrade step for old shops. An old shop then starts without prices | 4 ❗ | 4 ❗ | 1 | block ❗ | ✎ `shop/settings.py:40` → `shop/pricing.py:142` |

Also seen by customers: D2.

### 1. We remove the upgrade step for old shops. An old shop then starts without prices

| Chance | Customer | Fix effort | Verdict |
|---|---|---|---|
| 4 ❗ | 4 ❗ | 1 | block ❗ |

**What happens.** We remove the step that upgraded old settings files. An old shop's settings
still say `currency:`, and nothing reads that key any more. The shop starts
without prices, and every product page shows "price on request".

**Why.** ✎ `shop/settings.py:40` drops the upgrade; → `shop/pricing.py:142` reads only
`currencies:`.

**Fix.** Keep the upgrade step for one more release.

Chance 4: every shop installed before version 2 still has the old key.
Customer 4: no product can be bought.

## What the developer sees

| ✓ | # | Finding | Rule | Next change | Security | GDPR | Layers | Fix effort | Verdict | Cause ✎ → Effect |
|---|---|---|---|---|---|---|---|---|---|---|
| [x] | D2 | We write the fallback currency in three places. The next developer changes one | Manageable | 3 ⚠️ | – | – | – | 1 | ticket (was talk) | ✎ `shop/settings.py:12`, `shop/pricing.py:9`, `shop/feed.py:30` |

### D2. We write the fallback currency in three places. The next developer changes one

| Rule | Next change | Security | GDPR | Layers | Chance | Customer | Fix effort | Verdict |
|---|---|---|---|---|---|---|---|---|
| Manageable | 3 ⚠️ | – | – | – | 1 | 2 | 1 | ticket (was talk) |

**Re-scored 2026-10-16.** The operator confirmed the product feed runs for
every shop, so the customer half adds Chance and Customer here.

**What happens.** We write the fallback currency in three places. A developer changes it for the
checkout. The product feed keeps the old one, and no test notices. A customer
can then see two currencies for one product, once a day.

**Why.** ✎ `shop/settings.py:12`, ✎ `shop/pricing.py:9` and ✎ `shop/feed.py:30` each
hold `"EUR"`.

**Fix.** Read the fallback from the settings service in all three places.

Next change 3: nothing ties the three places together.

### Rules walked

- **Readable**: nothing
- **Manageable**: D2
- **Linter**: nothing
- **Architecture**: nothing
- **Tested**: D2
- **Payments**: nothing

## Verified as not a problem

Prices on the checkout page are rounded as before.

## Architecture check

Against §4: the pricing module still reads settings only through the settings service.

## Interaction with other open MRs

None open.

## Suggested disposition

Finding 1 blocks: an old shop starts without prices. D2 is a ticket.

## Read-only check

Nothing changed in the project.

## Commands for the operator

```
make test
ruff check --no-cache .
```
