# Queue design

The pooled team works **risk flags, not accounts**. Nobody owns an account: a case opens when a signal fires,
the CSM with capacity pulls it, and it closes with a code. All thresholds below live in
[`config/queue_rules.yaml`](../config/queue_rules.yaml).

For the order the engine applies these rules, see [how it works](how-it-works.md). For each setting's unit,
see the [policy reference](policy-reference.md).

## Signals

Flags apply at every configuration maturity level (L1 to L4).

| Signal | Opens a case when | Otherwise | Priority and SLA |
| --- | --- | --- | --- |
| Non-renewal intent | Always, inside the band | n/a | P1, 1 business day |
| Cancellation started | Always, inside the band | n/a | P1, 1 business day |
| Dormant (nobody active in 30 days) | L3-L4 any time; L1-L2 within 120 days of renewal | Re-engagement campaign; case at day 21 | P1, P2 or P3; 2-3 days |
| Solo (one active user) | Within 120 days of renewal (monthly terms always) | "Bring your team" campaign; case at day 21 | P2 or P3; 3 days |
| Stalled onboarding (in use, still L1 after day 45) | Within 180 days of renewal | Configuration campaign | P3, 3 days |
| Seat headroom (more active users than seats) | Never a case | Task for the account executive | AE, 2 days |
| Customer asks for help (triaged as advisory) | Always, inside the band | Known friction: docs answer; product fault: Support; buying: AE | P3, or P2 if flagged or renewing within 90 days; 2 days |

Accounts under $10k, over $30k or with a named CSM are removed from the queue. Rows whose activity data
contradicts itself are held: no outreach and no campaigns until the data is verified.

## Customer requests

Most cases start from signals; the customer never submits anything. The exception is a customer asking for
help, which comes in through the support queue.

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

An advisory case joins the same shared queue as every other case and is ranked the same way. Non-renewal
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
- **Up to a named CSM:** the account crosses $30k. Warm introduction, then the case closes.
