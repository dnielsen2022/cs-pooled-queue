# Queue design

The pooled team works **risk flags, not accounts**. Nobody owns an account; a case opens when a signal fires,
is pulled by whichever CSM has capacity, and closes with a code.

## Signals

| Signal | Creates a case when | Otherwise | Priority · SLA |
|---|---|---|---|
| Non-renewal intent | Always | n/a | P1 · 1 business day |
| Dormant (L2+, nobody active 30d) | L3–L4 any time; L2 within 120 days of renewal | Customer.io re-engagement, case at day 21 | P1 / P2 · 2 days |
| Solo (L2+, one active user) | Within 150 days of renewal (monthly terms always) | "Bring your team" track, case at day 21 | P2 · 3 days |
| Stalled onboarding (L1 after day 45) | Within 180 days of renewal | Config track | P3 · 3 days |
| Seat headroom (users above seats) | Never a case | Salesforce task to the AE | AE · 2 days |

Out of band (under $10k, over $30k, or a named CSM) is removed from the queue.

## Ordering
Priority tier → renewal window (≤30, 31–90, 91–180, >180 days) → deeper config level first → higher ARR.
A case unworked for 5 business days moves up a tier so nothing starves.

## Closing
Close codes: Saved (flag clear 14 days) · Saved, right-sized · Handed to AE · Lost, with reason · No reply after 2 touches.
Closed accounts get a 30-day Customer.io follow-up and the same trigger is muted for 90 days
(non-renewal intent always breaks through). Any fix used three times becomes an automated step.

## Hand-offs
- **In:** a signal fires nightly, or a Customer.io track ends without change, or Support routes a how-to request.
- **Out to the AE:** buying signal (more users than seats, a request for seats). Salesforce task: who, what, by when.
- **Out to Support:** a product fault found during a case, filed with a reproduction; the case stays open.
- **Up to a named CSM:** the account crosses $30k. Warm intro, then the case closes.
