# Code guidelines for cs-pooled-queue

CodeRabbit reads this file as review criteria (knowledge_base.code_guidelines).

## What this repo is
A small engine that turns an account export into a pooled customer success work list.
The policy lives in `config/queue_rules.yaml`; the code only applies it.

## Rules
1. **Config, not code.** No queue threshold (ARR band, renewal window, config level, SLA, capacity) is hard-coded in Python.
2. **Explain every decision.** Each routing decision carries a reason a CSM can read in the sheet.
3. **Flag, never drop.** Missing or contradictory data goes into `data_flags`; the row still gets a decision.
4. **Non-renewal intent always opens a case**, whatever else is wrong with the row.
5. **Business days for SLAs**, calendar days for renewal windows.
6. **Definitions follow the scenario:** dormant = configured (L2+) with nobody active in 30 days; solo = configured with exactly one active user; L1 with nobody active is stalled onboarding.
7. **Synthetic data only** in `data/`. Real exports go in `data/private/`, which is ignored.

## Style
Python 3.11+, type hints on public functions, docstrings on public functions, `ruff` clean, tests in `tests/` with pytest.
