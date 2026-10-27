# Playbook: solo user

**Trigger:** one active user for 30 days, within 120 days of renewal (monthly terms always).
**Owner:** the pooled CSM who pulls the case. **First touch:** within 3 business days. **Goal:** turn one
champion into a team of three or more.

A solo user already believes in the tool. Their teammates' pull requests aren't being reviewed, so the team
has never seen the value, and the person who signs the renewal usually isn't the solo user. This is a
rollout conversation, not a rescue: unlike a dormant account, nothing broke.

## How the case reaches you

- **P2 from the nightly run:** the account is solo and inside the window above.
- **P3 when the "bring your team" campaign runs 21 days** without a second active user.

Accounts in the holdout (see Did it work?) never get a solo case. If one reaches you, return it to the
campaign and tell the queue lead. Non-renewal intent still opens a case for them.

## Before the first touch (15 minutes, from the case brief)

| You need | From |
| --- | --- |
| Who the solo user is, and whether they are the CodeRabbit admin | CRM, billing system |
| Seats bought, assigned and active | Billing system, product analytics |
| Developers opening pull requests in connected repos | Review data. Until that query exists, ask on the first call |
| Configuration level, what is set up, and on which repo | Product analytics |
| The engineering lead or billing contact | CRM |
| Renewal date, term and ARR | Billing system, CRM |
| Open support tickets and campaigns already sent | Support queue, campaign tool |

Read any open tickets first. If the case has a data flag (for example, active seats far above active users),
confirm the real numbers before you mention seats.

## Steps

Business days until the first touch; calendar days from the case opening after that.

| When | Who | What |
| --- | --- | --- |
| Day 0 | System | The case opens in the queue with the brief attached. |
| By business day 3 | CSM | First email to the solo user (below). |
| Day 7, no reply | CSM | One short follow-up with a booking link. |
| Within 10 days | Customer's admin, guided by the CSM | 25-minute rollout call. Pick 2-3 teammates and the repos they work in. The admin assigns idle seats and connects those repos. Check `knowledge_base.learnings.scope` covers the team's repos. Schedule a weekly CodeRabbit report to the engineering lead. If the account is at L1, add starter path instructions for the main repo first. |
| Same day as the call | CSM | Recap email with a one-page rollout plan. Newly seated developers enter the 3-email "first review" campaign. More developers than seats: an AE task the same day. |
| Day 14 | CSM | Check active users. Three or more: watch. Fewer: a second touch to the engineering lead, showing the reviews their team is missing. |
| Day 30 | CSM | Close with a code. Two active users: extend once to day 44, then close. |

The CSM never changes the customer's settings. The admin does, on the call, with the CSM guiding. If the solo
user isn't the admin, invite the admin to the call with the solo user's agreement.

### First email

> **Subject:** Your CodeRabbit setup on {repo}, for the rest of your team
>
> Hi {name}, you've set up {what they configured} on {repo}, but only your pull requests are being reviewed,
> so only you see it working. {N} of your {seats} seats aren't assigned yet. Could we take 25 minutes to roll
> your setup out to two or three teammates? {booking link}

At L1, swap the first sentence for: "You're the only one on {repo} getting reviews, and it's running on
defaults. In 25 minutes we can add starter instructions for that repo and get two or three teammates
reviewed too."

## If this happens

| If | Then |
| --- | --- |
| Non-renewal intent or cancellation appears | The case becomes P1. Switch to that first touch within 1 business day |
| The champion is leaving | Go to the engineering lead the same day. Record the blocker as champion leaving |
| They say the team won't use it | Ask once what's in the way and record it. If seats are the issue, offer a right-size from active seats |
| The team really is one developer | Right-size to the seats they use. Close as Saved, right-sized |
| They ask for more seats or pricing | AE task the same day. You keep the retention work |
| You find a product fault | File it with Support, with a reproduction. The case stays open |

## Closes when

- **Saved:** three or more active users for 14 days running. This is stricter than "flag clear", because two
  users still carry most of the risk.
- **Saved, right-sized:** seats cut to what the team uses. Record the dollars lost.
- **Handed to the AE:** seats or price are the only blocker.
- **Lost, with reason:** the customer has said they are leaving.
- **No reply:** two touches and no answer by business day 10. The account returns to the campaign.
- **Back to campaign:** engaged but under three active users at day 44.

After any close, the account gets a 30-day follow-up campaign and the solo trigger stays quiet for 90 days.
Non-renewal intent always breaks through.

## Recorded on close

In the case fields, synced to the CRM:

- close code
- active users at day 0, 14, 30, 60 and 90 (60 and 90 fill in after close)
- main blocker: no idle seats, lead not bought in, review noise, champion leaving, tool consolidation, price
- seats before and after, and dollars lost on a right-size
- touches and minutes spent

## Did it work?

One in five eligible solo accounts is held out at random in the campaign tool and marked on the account
record. Those accounts get the campaign only.

- **After one quarter:** compare the share reaching three or more active users by day 60, worked against held
  out. The bar is a 10-point lift.
- **After two quarters:** compare gross revenue retention at renewal, worked against held out.

Pool both quarters before calling it.
