# Policy reference

Every setting in [`config/queue_rules.yaml`](../config/queue_rules.yaml), what it controls and its unit.
Current values are in the file itself; [queue design](queue-design.md) states them in plain language.

To change a setting, follow [Changing a queue rule](../CONTRIBUTING.md#changing-a-queue-rule). Every pull
request that modifies this file must state its effect on weekly case volume.

## `version`

The policy file's format version. Change it only when the structure of the file changes.

## `band`

| Key | Unit | Controls |
| --- | --- | --- |
| `min_arr` | USD per year | Accounts below this are removed: they belong to the automated tier |
| `max_arr` | USD per year | Accounts above this are removed: they belong to a named CSM |
| `price_per_seat` | USD per seat per year | Sizes seat headroom in dollars and checks ARR against seats |

## `columns`

Maps each field the engine needs to a column name in the export. If the export renames a column, change it
here, not in code. The [data dictionary](data-dictionary.md) describes each field.

## `flags`

Account flags. They apply at every maturity level.

| Key | Unit | Controls |
| --- | --- | --- |
| `dormant.max_active_users` | users | At or below this many active users, the account is dormant |
| `dormant.idle_days_to_fire` | calendar days | Days without a review before the dormant flag fires; the campaign clock starts then |
| `solo.active_users` | users | Exactly this many active users makes an account solo |
| `stalled_onboarding.level` | maturity level | The level an account is stuck at |
| `stalled_onboarding.min_active_users` | users | At least this many people using it, so it is in use but not configured |
| `onboarding.max_days_since_signup` | calendar days | Accounts this new stay in the onboarding nurture; no other flag applies yet |

## `triggers`

What each signal does. Every trigger that can open a case has a `priority`, an `sla_business_days` and a
`first_touch`.

| Key | Unit | Controls |
| --- | --- | --- |
| `*.priority` | P1, P2 or P3 | The case priority |
| `*.sla_business_days` | business days | Time to the first human touch |
| `*.first_touch` | text | What the CSM says first. `{date}` is filled with the date of the last review |
| `*.automated_track` | text | The campaign an account goes to when it doesn't open a case |
| `*.handled_by` | handling mode | Who works the case: Automation, CSM with AI or CSM without AI |
| `dormant.deep_level` | maturity level | At or above this level, a dormant account opens a case at any distance from renewal |
| `dormant.deep_priority` | P1, P2 or P3 | Priority for a deep dormant case |
| `dormant.near_renewal_days` | calendar days | Below `deep_level`, a dormant account opens a case inside this window |
| `dormant.near_renewal_priority` | P1, P2 or P3 | Priority for a near-renewal dormant case |
| `solo.renewal_within_days` | calendar days | A solo account opens a case inside this window |
| `stalled_onboarding.renewal_within_days` | calendar days | A stalled account opens a case inside this window |
| `automation_exhausted.track_days` | calendar days | A campaign that runs this long without the account moving becomes a case |
| `seat_headroom.route` | route | Where a buying signal goes; always the AE, never a CSM case |

`nonrenewal_intent` and `cancellation_started` have only a priority, an SLA and a first touch: inside the
band they always open a case.

## `handling`

Who works the routes that aren't cases. Case triggers carry their own `handled_by`.

| Key | Unit | Controls |
| --- | --- | --- |
| `modes` | list | The allowed handling modes; a test fails on any other value |
| `automated_route` | handling mode | Campaigns and healthy accounts |
| `hold_route` | handling mode | Held rows: a person verifies the data before anyone acts |
| `below_band` | handling mode | Accounts below the band, left to the automated tier |
| `above_band_or_named` | handling mode | Accounts above the band or with a named CSM |

## `ai`

What AI does for a pooled CSM and its limits. The engine doesn't call AI; these settings are the team's
rules, reviewed by CodeRabbit like any other policy change.

| Key | Unit | Controls |
| --- | --- | --- |
| `drafts` | list | What AI prepares for the CSM to check: account summary, first message, proposed playbook step, case note |
| `never_without_review` | list | What a person approves every time |
| `never_assists` | trigger names | Triggers AI never drafts for (it only prepares the CSM's internal brief); they must be CSM without AI |
| `orders_queue` | `true` or `false` | Whether AI may order the queue; `false`, so the rules decide |
| `review_sample_per_week` | drafts | How many AI drafts the queue lead checks each week |
| `revert_if_wrong_fact_rate_over` | share, 0 to 1 | Above this wrong-fact rate, measured over a rolling four weeks of reviewed drafts, a trigger goes back to CSM without AI |

## `measurement`

Settings for testing the automated share against the human share. The campaign tool applies them.

| Key | Unit | Controls |
| --- | --- | --- |
| `holdout_share` | share, 0 to 1 | Of accounts that qualify for a case, the share kept on automation only |
| `reverse_sample_share` | share, 0 to 1 | Of accounts left to automation, the share given a CSM-with-AI case |

## `monthly_always_in_window`

`true` or `false`. When `true`, monthly-term accounts count as inside every renewal window, because they can
leave at any month end.

## `data_checks`

Flag, never drop. These only add `data_flags` and, for one contradiction, hold the row.

| Key | Unit | Controls |
| --- | --- | --- |
| `price_tolerance_usd` | USD | ARR per seat further than this from `band.price_per_seat` is flagged |
| `mismatch_max_users` | users | With this many active users or fewer... |
| `mismatch_min_seats` | seats | ...and at least this many active seats, the row contradicts itself |
| `seats_vs_users_gap` | seats | Active seats above active users by this much is flagged before any seat quote |
| `activity_window_days` | calendar days | The window active users are counted in; used to spot activity that doesn't add up |
| `tickets_to_read_first` | tickets | With this many recent tickets or more, the CSM reads them before the first touch |
| `hold_on_contradiction` | `true` or `false` | Hold contradictory rows from outreach. Non-renewal intent still opens a case |

## `ordering`

| Key | Unit | Controls |
| --- | --- | --- |
| `priority_rank` | number per priority | Sort order of priorities; lower comes first |
| `renewal_buckets_days` | calendar days | Renewal windows used as the second sort key, nearest first |

After these, cases with deeper configuration come first, then higher ARR.

## `capacity`

| Key | Unit | Controls |
| --- | --- | --- |
| `this_week_cases` | cases | How many cases become Work this week; the rest are Queue (next) |
