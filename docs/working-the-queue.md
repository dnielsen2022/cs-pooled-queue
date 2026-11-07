# Working the queue

How a pooled CSM gets work, works it and closes it. Read this on day one, then the playbook for each trigger
you pick up.

## How work reaches you

Nobody is assigned accounts. Every night the engine opens a case in the support queue for each account whose
signal fires. Customer requests that support triages as advisory join the same queue during the day. Every
case is ranked across the whole team, and you pull the next one when you have room.

Each case arrives with:

| Field | What it tells you |
| --- | --- |
| Priority and rank | Where it sits in the queue: P1 first, then by renewal date, configuration depth and ARR |
| SLA | Business days you have until the first human touch |
| Signals | Why the account surfaced, such as `Solo · L2` |
| Reason | The rule that opened the case, in a sentence |
| First touch | What to say or do first; the same opening for every CSM on that trigger |
| Also | Notes that change your first touch (below) |
| Data flags | Numbers on the account that don't add up |
| Case brief | Who the users are, seats, configuration, renewal, open tickets and campaigns already sent |
| Handled by | CSM with AI (AI drafts, you check and send) or CSM without AI (you write every word) |

## Pulling a case

1. **Take the top of the queue.** Don't skip a case because the account looks hard or small; ranking already
   decided what matters most.
2. **P1 never waits.** If a P1 is open and unclaimed, it's yours before anything else.
3. **Stay under the cap.** No more than 20 open cases each. Plan on about 5 new cases a week.
4. **Meet the SLA.** The clock runs in business days from when the case opened, not from when you pulled it.

| Trigger | Priority | First touch within |
| --- | --- | --- |
| Non-renewal intent | P1 | 1 business day |
| Cancellation started | P1 | 1 business day |
| Dormant | P1 to P3 | 2 business days |
| Solo user | P2 | 3 business days |
| Stalled onboarding | P3 | 3 business days |
| Campaign ran out | P3 | 3 business days |
| Customer asks for help (advisory) | P3, or P2 if flagged or renewing within 90 days | 2 business days |

A P3 left unworked for 5 business days moves up to P2, so nothing sits forever.

## Notes on a case

| Note | What you do |
| --- | --- |
| Seat headroom | The AE already has a task. Don't quote seats or prices; tell the AE what you learn about the team |
| Graduation coming | Expansion or a move to an annual term will take the account past the band. Note it in the case so the graduation brief carries it. Graduation itself runs on the rule, not a judgment call |
| Read the recent support tickets | Read them before reaching out, and acknowledge any open issue in your first touch |
| Data flags | Don't act on a flagged number. Confirm it with the customer or the analytics engineer first, and note what was wrong |

## When something changes mid-case

- **Non-renewal intent or cancellation appears.** The case becomes P1. Switch to that first touch the same day.
- **The account crosses the band.** Graduation runs on its own: the named CSM is assigned and gets the brief,
  and the customer gets a welcome. Add anything the brief can't know, then close the case as handed up
  (see Graduation to a named CSM in the queue design).
- **You find a product fault.** File it with Support, with a reproduction. Your case stays open.
- **The customer asks for seats or pricing.** Create an AE task with who, what and by when. Keep only the
  retention work.

## Closing

Every case closes with one code and one main blocker, so the team can learn from it.

| Close code | When |
| --- | --- |
| Saved | The flag has been clear for 14 days, or the playbook's higher bar is met |
| Saved, right-sized | Kept the customer at fewer seats; record the dollars lost |
| Handed to the AE | Seats or price are the only blocker |
| Handed up | The account moved to a named CSM |
| Lost, with reason | The customer is leaving; record why |
| No reply | Two touches over 10 business days with no answer |
| Back to campaign | The customer engaged but the flag hasn't cleared by the playbook's last day |

After a case closes, the account gets a 30-day follow-up campaign and the same trigger stays quiet for 90
days. Non-renewal intent always breaks through. Any fix used three times becomes an automated step.

## Working with AI

Most cases are marked **CSM with AI**. AI writes the account summary before your first touch, drafts the first
message from the customer's own setup, proposes the next playbook step and drafts the case note. You check
every fact, edit, and send. Four rules:

1. **You send it, you own it.** Nothing AI writes reaches a customer unless you send it.
2. **The brief wins.** When the AI summary and a brief field disagree, trust the brief field and mark the
   draft wrong on the case.
3. **No AI on CSM-without-AI cases.** Non-renewal intent and cancellation are yours alone, in your own words.
   If a case turns into one mid-way, stop using drafts.
4. **AI never decides.** You pick the close code, the blocker and the next step. The queue order comes from
   the rules, not from AI.

The queue lead checks 10 AI drafts a week. A trigger whose drafts get facts wrong too often goes back to CSM
without AI. [Automation, AI and the person](ai-and-automation.md) has the full design.

## A day on the queue

| When | What |
| --- | --- |
| 9:00, 15 minutes | Standup: open P1s and any case at risk of missing its SLA |
| Morning | Check AI summaries and drafts, then first touches and calls, top of the queue first |
| Afternoon | Rollout sessions, follow-ups and hand-offs |
| Last hour | Close codes, AI-drafted case notes checked and saved |
| Friday, 45 minutes | Pattern review: what keeps coming up, and what should become automation or a rule change |

## Your first 90 days

| When | What |
| --- | --- |
| Week 1 | Take CodeRabbit to L4 on a repository of your own, so you know every level from the inside |
| Week 2 | Work P3 cases, with each one and every AI draft reviewed by the queue lead |
| Weeks 3 to 4 | Half the cap: up to 10 open cases |
| Day 45 | Full cap |
| Day 90 | Own the improvements to one trigger's playbook |

## When there's more work than people

The team watches one number weekly: cases closed over cases opened. Below 1.0 for two weeks means the backlog
is growing, and the team works down this list in order:

1. P1 never waits; P3 cases go back to automation first.
2. Retune the noisiest trigger. If under half its cases are real risk, tighten the rule.
3. Batch: weekly rollout and configuration clinics, one to many.
4. Codify: any fix used three times becomes a campaign step, so that signal runs on automation.
5. Hire, once SLA misses stay above 10% for 3 weeks after steps 1 to 4.

Other weekly numbers: SLA hit rate by priority, open cases per CSM, age of the oldest unclaimed case, touch
minutes per case by trigger, and each trigger's precision (the share of its cases that were real risk).
