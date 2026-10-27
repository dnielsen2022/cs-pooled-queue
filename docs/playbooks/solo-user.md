# Playbook: solo user

**Trigger:** one active user for 30 days, configured at L2 or deeper, within 150 days of renewal (monthly terms always).
**Owner:** the pooled CSM who pulls the case. **Goal:** turn one champion into a team.

## Before the first touch (15 minutes, from the case brief)
| In the brief | From |
|---|---|
| Who the solo user is, and whether they are the admin | Salesforce, Chargebee |
| Seats bought, assigned and active | Chargebee, PostHog |
| Developers opening PRs in connected repos | PostHog |
| Config level and features in use (path instructions, learnings, pre-merge checks, reports, MCP) | PostHog |
| Renewal date and ARR | Chargebee, Salesforce |
| Open support issues and campaigns already sent | Pylon, Customer.io |

## Steps
| When | Who | What |
|---|---|---|
| Day 0 | System | Case opens in Pylon with the brief attached. |
| By day 3 | CSM | Email the solo user about their own setup: "Your [n] learnings only shape your PRs. 25 minutes to make them the team's?" |
| By day 7 | CSM + champion | Rollout call: pick 2–3 teammates and repos, assign idle seats, promote learnings to org scope, schedule a weekly report to the eng lead. |
| Day 7 | CSM, Customer.io | Recap with a one-page rollout plan. New reviewers enter the 3-email "first review" track. More developers than seats: Salesforce task to the AE the same day. |
| Day 14 | CSM | Check PostHog. Three or more active: watch. Still one: second touch, to the eng lead or billing contact. |
| Day 30 | CSM | Close the case with a code. |

## Closes when
- **Saved:** three or more active users for 14 days running.
- **No reply:** two touches over 10 business days with no answer. Back to the "bring your team" track; reopens at renewal minus 90.
- **Handed to AE** when seats are the only blocker.

## Recorded on close
Close code · active users at day 0, 14, 30 and 90 · main blocker (no idle seats, lead not bought in, review noise,
champion leaving, tool consolidation) · touches and minutes spent.

## Did it work?
One in five eligible solo accounts stays automation-only, chosen at random. Compare the share reaching 3+ users at day 60
(leading) and GRR at renewal (lagging), worked vs held out. Pool two quarters before calling it.
