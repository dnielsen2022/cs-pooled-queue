# Automation, AI and the person

Every signal the queue acts on is handled one of three ways, set by `handled_by` in
[`config/queue_rules.yaml`](../config/queue_rules.yaml) and shown on every row of the work list:

- **Automation:** the next step is the same for every account, so Customer.io runs it end to end.
- **CSM with AI:** the conversation depends on the customer's own setup. AI prepares the summary and the
  drafts; the CSM decides and sends.
- **CSM without AI:** one wrong word can cost the account, so a person writes every word.

The rule under all three: AI drafts, a person decides and sends. No AI output reaches a customer, sets a close
code or orders the queue without a person.

## By signal

| Signal | Handled by | Why | What moves it |
| --- | --- | --- | --- |
| Onboarding, days 0 to 44 | Automation | The first steps are the same for every new account | A support ticket goes to Support; still at L1 by day 45 becomes stalled onboarding |
| Healthy, no flag | Automation | Nothing is at risk; next-level configuration nudges only | Any flag |
| Dormant, shallow and far from renewal | Automation first | Most teams come back after a reminder; it's the cheapest save | 21 days of campaign without activity, or inside 120 days of renewal: a case |
| Dormant, deep (L3 to L4) or near renewal | CSM with AI | Something broke. AI finds when and where reviews stopped and what changed; the CSM writes the ask | n/a |
| Solo, outside the solo window | Automation | A "bring your team" campaign works for most | 21 days without a second user, or inside the window: a case |
| Solo, inside the window | CSM with AI | The rollout depends on their own setup. AI drafts the email from it; the call is a person | n/a |
| Stalled onboarding, inside the window | CSM with AI | AI drafts starter path instructions for their main repo; the CSM checks them before sending | n/a |
| Stalled onboarding, outside the window | Automation | A configuration campaign with starter path instructions | Inside 180 days of renewal: a case |
| Non-renewal intent or cancellation | CSM without AI | A save conversation. The customer has to hear a person, in their own words | n/a |
| Seat headroom | Automation | The CRM task for the AE is created automatically; the AE is the person who acts | n/a |
| Data that contradicts itself | CSM without AI | Verify with the analytics engineer first. AI would repeat the bad number in its summary | Verified data: the row is routed again |
| Customer asks for help, triaged as advisory | CSM with AI | AI drafts an answer from the docs and similar past cases; the CSM checks it | Support routes it; see [queue design](queue-design.md#customer-requests) |

In the exercise's 40-account sample, 20 of the 36 in-band accounts need no pooled CSM: 14 stay on automation
and 6 become AE tasks. Across the whole band the automated share is higher, because the sample was drawn from
the queue. People are used only where the customer's situation decides what to say.

## Where AI sits in a pooled CSM's day

| Moment | What AI does | What the CSM does |
| --- | --- | --- |
| Before the first touch | Writes a short account summary from the case brief: usage, billing, CRM notes, support history | Checks it against the brief fields and fixes anything wrong |
| The first message | Drafts it from the trigger's first touch and the account's own setup | Edits it and sends it. Nothing goes out unless a person sends it |
| During the case | Proposes the next playbook step from the account's activity | Decides the step |
| Closing | Drafts the case note from emails and call notes | Picks the close code and the blocker |
| Ordering the queue | Nothing | Nothing: the order comes from the rules in [how it works](how-it-works.md) |

AI runs inside the tools the team already has (Pylon for the case and drafts), not on a separate platform.

## What AI never does without a person

The `ai` section of the policy file holds these limits, and CodeRabbit flags any pull request that loosens them.

- **Never without review:** any message to a customer, a close code, a seat or price figure.
- **Never at all:** drafting for non-renewal intent or cancellation; anything on a held account; ordering
  the queue.

## How we catch AI getting an account wrong

1. **The sender checks.** The CSM who sends a draft owns every fact in it. A wrong fact gets marked on the
   case, so it's counted.
2. **A weekly sample.** The queue lead checks 10 AI drafts a week against the account record.
3. **A revert rule.** If more than 5% of a trigger's drafts get a fact wrong, that trigger goes back to CSM
   without AI until the cause is fixed.
4. **Edit rate.** The team tracks how much each draft is rewritten before it's sent. Heavy rewrites on one
   trigger mean the draft isn't helping there.

## Testing the automated share against the human share

Two random samples, both applied by the campaign tool:

- **Holdout:** 1 in 5 accounts that qualify for a case stays on automation only. If worked accounts don't
  beat held-out ones, the person isn't adding value on that trigger.
- **Reverse sample:** 1 in 10 accounts left to automation gets a CSM-with-AI case. If those do better, the
  trigger should move toward a person.

Compare a leading measure first (the flag cleared by day 60: three or more active users for solo, activity
back for dormant), then gross revenue retention at renewal. Pool two quarters before moving a trigger.

## What to build first with the Success Analytics Engineer

1. **The nightly trigger job,** writing route, handled_by, priority and the holdout flag onto each case, so
   automated and human outcomes can be compared from the first week.
2. **Developers opening pull requests,** last 30 and prior 30 days, from review data. It separates a solo
   account from one whose teammates just aren't seated, and it makes the AI summary for a solo case specific.
3. **The outcome join:** renewal results from billing against handled_by and the holdout flag, for the
   monthly readout.
