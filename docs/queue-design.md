# Queue design

The pooled team works **risk flags, not accounts**. Nobody owns an account: a case opens when a signal fires,
the CSM with capacity pulls it, and it closes with a code. All thresholds below live in
[`config/queue_rules.yaml`](../config/queue_rules.yaml).

For the order the engine applies these rules, see [how it works](how-it-works.md). For each setting's unit,
see the [policy reference](policy-reference.md).

## Signals

Flags apply at every configuration maturity level (L1 to L4).

| Signal | Opens a case when | Otherwise | Priority and SLA | Case handled by |
| --- | --- | --- | --- | --- |
| Non-renewal intent | Always, inside the band | n/a | P1, 1 business day | CSM without AI |
| Cancellation started | Always, inside the band | n/a | P1, 1 business day | CSM without AI |
| Dormant (nobody active in 30 days) | L3-L4 any time; L1-L2 within 120 days of renewal | Re-engagement campaign; case at day 21 | P1, P2 or P3; 2-3 days | CSM with AI |
| Solo (one active user) | Within 150 days of renewal (monthly terms always) | "Bring your team" campaign; case at day 21 | P2 or P3; 3 days | CSM with AI |
| Stalled onboarding (in use, still L1 after day 45) | Within 180 days of renewal | Configuration campaign | P3, 3 days | CSM with AI |
| Seat headroom (more active users than seats) | Never a case | Task for the account executive | AE, 2 days | Automation creates the task |
| Customer asks for help (triaged as advisory) | Always, inside the band | Known friction: docs answer; product fault: Support; buying: AE | P3, or P2 if flagged or renewing within 90 days; 2 days | CSM with AI |

Every "Otherwise" route runs on automation alone. Why each signal sits where it does, where AI helps, and what
AI never does without a person are in [automation, AI and the person](ai-and-automation.md).

Accounts under $10k, over $30k or with a named CSM are removed from the queue. Rows whose activity data
contradicts itself are held: no outreach and no campaigns until the data is verified.

## Customer requests

Most cases start from signals; the customer never submits anything. The exception is a customer asking for
help, which comes in through the support queue. Support runs this step in Pylon. The engine doesn't route
requests, because the triage bucket isn't in the export.

**Intake.** A support form or chat-widget flow with four fields: what you're trying to do, the repo, what
you've tried, and how urgent it is (blocked, this week, or a question). The account, plan, configuration
level and renewal date fill in from the CRM and product data, so the customer never types them.

**Triage.** Support puts each request in one bucket:

| Bucket | Example | Goes to |
| --- | --- | --- |
| Advisory | "How do we roll path instructions out to every repo?" | A pooled CSM case |
| Known friction | A question the docs or a campaign step already answers | Support replies with the answer |
| Break/fix | Reviews stopped posting on a repo | Support, with a reproduction |
| Buying | "Can we add ten seats?" | An AE task |

An advisory case joins the same shared queue as every other case and is ranked the same way: P3, or P2 when
the account already carries a flag or renews within 90 days, with a 2-business-day SLA. Non-renewal
intent still wins: a request from an account that has said it may leave opens a P1 case, whatever the bucket.

## Ordering

Priority tier, then renewal window (7, 30, 90, 180 days), then deeper configuration first, then higher ARR.
A P3 case unworked for 5 business days moves up to P2, so nothing starves; nothing is promoted to P1.

## Closing

Close codes: Saved (flag clear for 14 days; a playbook can set a higher bar, as the solo playbook does) ·
Saved, right-sized (record the dollars lost) · Handed to the AE · Handed up to a named CSM · Lost, with
reason · No reply after 2 touches · Back to campaign (engaged, but the flag hasn't cleared).

A closed account gets a 30-day follow-up campaign and the same trigger is muted for 90 days; non-renewal
intent always breaks through. Any fix used three times becomes an
automated step.

## Hand-offs

- **In:** a signal fires in the nightly run, a campaign ends without change, or support triages a customer
  request as advisory (see Customer requests).
- **Out to the account executive:** a buying signal (more users than seats, a request for seats), as a CRM task
  with who, what and by when.
- **Out to support:** a product fault found during a case, filed with a reproduction; the case stays open.
- **Up to a named CSM:** the account crosses $30k. Graduation runs on a rule, not a judgment call; see
  Graduation below.

## Graduation to a named CSM

An account graduates when its ARR in billing crosses the top of the band (`band.max_arr`), whatever the
reason: a seat expansion, a price change, or a move from a monthly to an annual term. The line lives in
config because it is expected to move.

What happens, with no one remembering to do it:

1. **Assign.** The CRM assigns the named CSM and alerts them.
2. **Brief.** The named CSM gets a graduation brief, not a cold account:
   - pooled history: triggers that fired, close codes and the main blocker on each case;
   - usage: active users at day 0, 30, 60 and 90 of the last case, maturity level, repositories connected;
   - what they bought: plan, term, seats before and after, and the ARR change that crossed the line;
   - open support tickets and the AE's notes.
3. **Welcome.** The customer gets a short message naming their CSM, what changes and how to reach them. A
   move to an annual term can make an account eligible without the customer knowing, and a named CSM who
   arrives unannounced tends to meet silence.
4. **Close.** An open pooled case closes as Handed up, with anything the brief can't know added as a note.

Accounts that drop into the band come down by the same rule, but nobody on the pooled team takes them over,
because nobody owns an account. The named CSM's history goes onto the account record, and if a flag later
opens a case, the history is part of the case brief. Before the hand-down, the named CSM records any open risk
where the queue can see it (non-renewal intent the customer has stated, a started cancellation), so a case opens
on the next run. Otherwise the account starts on automation like any other.

Measured monthly: graduations, and how often the named CSM has to re-ask the customer something the brief
already covered.
