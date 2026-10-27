# Data dictionary

The columns the engine reads from the account export and the columns it adds to the work list. Column names
are mapped in the `columns` section of [`config/queue_rules.yaml`](../config/queue_rules.yaml), so an export
with different names only needs that section changed.

## Export columns

| Column | Field | Type | Used for |
| --- | --- | --- | --- |
| `account` | `account` | text | The account's name on the work list |
| `arr_usd` | `arr` | USD per year | Band membership, ordering, the price check |
| `plan` | | text | Not used |
| `maturity_level` | `level` | `L1` to `L4` | Deep dormant, stalled onboarding, ordering |
| `seats_purchased` | `seats_purchased` | whole number | Seat headroom, the price check |
| `seats_active_30d` | `seats_active` | whole number | Data checks |
| `active_users_30d` | `active_users` | whole number | Dormant, solo, stalled, seat headroom |
| `days_since_last_review` | `days_since_last_review` | days | Dormant campaign timing, the last review date in the first touch, data checks |
| `repos_connected` | | whole number | Not used |
| `renewal_date` | `renewal_date` | date, `YYYY-MM-DD` | Renewal windows and ordering |
| `term` | `term` | `annual` or `monthly` | Monthly terms count as inside every renewal window |
| `nonrenewal_intent` | `nonrenewal_intent` | yes or no | Opens a P1 case |
| `cancellation_started` | `cancellation_started` | yes or no | Opens a P1 case |
| `support_tickets_30d` | `support_tickets` | whole number | A note to read tickets before the first touch |
| `suggestion_acceptance_30d_pct` | | percent | Not used |
| `days_since_signup` | `days_since_signup` | days | Onboarding, data checks |
| `success_manager` | `success_manager` | text | Any value means a named CSM owns the account |

### How cells are read

- **Numbers** may include commas or a dollar sign (`$21,600`). Decimals are rounded down.
- **Yes or no** cells count `Y`, `yes`, `true` and `1` as yes, in any case. Anything else is no.
- **Maturity level** must look like `L1` to `L4`.
- **Term** is monthly only when the cell says `monthly`; anything else is treated as annual.
- **Blank or unreadable cells** become unknown and add a flag such as `Missing renewal_date`. The row is
  never dropped. Unknown support tickets count as zero.

## Data flags

`data_flags` lists every problem found on the row, in words a CSM can act on.

| Flag | What it means | What happens |
| --- | --- | --- |
| `Missing ...` or `Invalid ...` | A cell is blank or can't be read | Flagged; the rules treat the value as unknown |
| `0 seats purchased` | The account has no seats | Flagged |
| `ARR per seat is $X, not $Y` | ARR doesn't match seats at the list price: a discount or a wrong ARR | Flagged |
| `N active seats but M active user(s): which is right?` | Many active seats and almost no active users | The row is held |
| `N active seats vs M active users` | Active seats well above active users | Flagged; confirm before any seat quote |
| `Last review N days ago but signed up M days ago: impossible` | The last review is older than the account | Flagged |
| `N active users ... but no review for M days` | People counted as active, yet no recent review | Flagged; ask what counts as active |
| `0 active users but a review N days ago` | A recent review, yet nobody counted as active | Flagged; ask what counts as active |
| `Renewal date is in the past` | The renewal has passed or the date is wrong | Flagged |

## Columns added to the work list

| Column | Meaning |
| --- | --- |
| `route` | Work this week, Queue (next), AE, Automated, Hold or Remove; Support for customer requests only |
| `priority` | P1, P2 or P3 for cases; blank otherwise |
| `rank` | Position among all cases, 1 first; blank for other routes |
| `sla_business_days` | Business days to the first human touch, for cases and AE tasks |
| `signals` | The flags on the row, such as `Solo · L2` or `Seat headroom +7` |
| `reason` | Why the account got this route |
| `first_touch` | What the CSM or AE says or does first |
| `also` | Notes for the first touch: seat headroom to pass on, a possible up-tier, tickets to read |
| `data_flags` | Problems found in the row's data |

## Sample data

[`data/sample_export.csv`](../data/sample_export.csv) holds 12 synthetic accounts named `Example ...`. They
cover each route except Queue (next), the dormant and solo flags, seat headroom and the main data
problems. Real exports go in
`data/private/`, which git ignores and CodeRabbit never reviews.
