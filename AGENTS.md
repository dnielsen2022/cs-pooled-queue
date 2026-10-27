# Code guidelines for cs-pooled-queue

CodeRabbit reads this file as review criteria (`knowledge_base.code_guidelines`).

## What this repo is

A small engine that turns an account export into a pooled customer success work list. The policy lives in
`config/queue_rules.yaml`; the code only applies it.

## Rules

1. **Config, not code.** No queue threshold (ARR band, renewal window, maturity level, priority, SLA,
   data-check limit, capacity) is hard-coded in Python. Reason strings are built from config values.
2. **Explain every decision.** Each routing decision carries a reason a CSM can read.
3. **Flag, never drop.** Missing or contradictory data goes into `data_flags`; the row still gets a decision.
4. **Inside the band, non-renewal intent always opens a case**, whatever else is wrong with the row.
   Out-of-band accounts belong to a named CSM or the automated tier.
5. **Business days for SLAs**, calendar days for renewal windows.
6. **Flags apply at every maturity level:** dormant = nobody active in 30 days; solo = exactly one active user.
7. **Synthetic data only** in `data/`. Real exports go in `data/private/`, which git ignores.

## Style

Python 3.11+, type hints and docstrings on every function, ruff clean at 120 characters, tests in `tests/`
with pytest that read thresholds from the policy file.
