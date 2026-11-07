# cs-pooled-queue

Turns an account export into a pooled customer success work list: which accounts open a case and in what
order, which go to the account executive or an automated campaign, and which rows have data that doesn't
add up.

Built by Derek Nielsen for a pooled customer success exercise. It is also a working example of CodeRabbit
configured from L1 to L4 on a real codebase.

## The idea

A pooled team doesn't own accounts. It works **risk flags** across every account in its band, here $10k to
$30k ARR. Every night the engine reads the account export and gives each account one of six routes:

| Route | Meaning |
| --- | --- |
| Work this week | A case, inside this week's capacity, in priority order |
| Queue (next) | A case, waiting for capacity |
| AE | A buying signal for the account executive, never a CSM case |
| Automated | A campaign, or healthy and left alone |
| Hold | The row's activity data contradicts itself, so nobody reaches out until it's verified |
| Remove | Outside the band or owned by a named CSM |

Customers who ask for help come in a second way. Support triages each request in Pylon, and only how-to and
adoption questions become pooled cases. That step is a Support process, not part of the engine (see
[queue design](docs/queue-design.md#customer-requests)).

Every decision carries a reason a CSM can read, a priority and SLA for cases, the first thing to say to the
customer, any data problems found on the row, and **who handles it**: Automation, a CSM with AI (AI drafts,
the CSM checks and sends) or a CSM without AI. AI never sends a customer message, sets a close code or
orders the queue; see [automation, AI and the person](docs/ai-and-automation.md).

The policy lives in [`config/queue_rules.yaml`](config/queue_rules.yaml). The code in
[`pooled_queue/`](pooled_queue) only applies it, so the queue can be tuned without a code change.

## Run it

```bash
pip install -r requirements.txt
python -m pooled_queue.cli data/sample_export.csv --as-of 2026-10-05
pytest
```

The command prints this week's cases and the rows with data to check, and writes the full work list to
`out/worklist.csv`:

```text
This week (7):
   1. P1 Example Alpha Labs         CSM without AI  Non-renewal intent
   2. P1 Example Beta Works         CSM with AI     Dormant · L4
   3. P2 Example Theta Retail       CSM with AI     Solo · L2
   4. P2 Example Delta Tools        CSM with AI     Solo · L2
   5. P2 Example Zeta Data          CSM with AI     Dormant · L1
   6. P2 Example Gamma Apps         CSM with AI     Solo · L3
   7. P3 Example Eta Systems        CSM with AI     Dormant · L2

Data to check (3):
  - Example Alpha Labs: 44 active seats vs 33 active users: confirm before any seat quote
  - Example Iota Freight: 49 active seats but 1 active user(s): which is right?
  - Example Mu Robotics: 28 active seats vs 15 active users: confirm before any seat quote
```

| Option | Default | Meaning |
| --- | --- | --- |
| `export` | required | The account export as CSV |
| `--as-of` | today | The date the export was taken; renewal windows count from it |
| `--rules` | `config/queue_rules.yaml` | The policy file to apply |
| `--out` | `out/worklist.csv` | Where to write the work list |

`data/` holds synthetic accounts only. Real exports go in `data/private/`, which git ignores.

## Documentation

| Doc | Read it for |
| --- | --- |
| [Walkthrough](docs/walkthrough.md) | Start here: from signal to closed case, step by step, and where each part of the exercise lives |
| [Automation, AI and the person](docs/ai-and-automation.md) | Who handles each signal and why, where AI sits in a CSM's day, what AI never does, and how the automated share is tested |
| [Working the queue](docs/working-the-queue.md) | How a pooled CSM pulls, works and closes cases: SLAs, the cap, a day on the queue, the first 90 days |
| [Queue design](docs/queue-design.md) | The signals, ordering, close codes and hand-offs, in one page |
| [How it works](docs/how-it-works.md) | The order the engine applies the rules, with a flowchart, and how to read its output |
| [Policy reference](docs/policy-reference.md) | Every setting in `config/queue_rules.yaml`: what it does and its unit |
| [Data dictionary](docs/data-dictionary.md) | The export columns the engine reads and the columns it adds |
| [Solo-user playbook](docs/playbooks/solo-user.md) | One trigger worked end to end: brief, steps, close, measurement |
| [Glossary](docs/glossary.md) | Terms used across the docs |
| [CodeRabbit setup](docs/coderabbit-setup.md) | Every CodeRabbit setting in this repo and how to reproduce it |
| [Contributing](CONTRIBUTING.md) | How to change a rule, open a pull request and run the checks |

## Repo layout

```text
config/queue_rules.yaml    the queue policy: every threshold, priority, SLA and first touch
pooled_queue/engine.py     applies the policy to each row and orders the cases
pooled_queue/cli.py        command line entry point; writes the work list
tests/test_engine.py       one test per rule and edge case, reading thresholds from the policy
data/sample_export.csv     12 synthetic accounts across the routes and data problems
docs/                      design, reference and playbooks
.coderabbit.yaml           CodeRabbit configuration
AGENTS.md                  code guidelines CodeRabbit reviews against
```

## CodeRabbit on this repo

| Level | What it means | Where it lives |
| --- | --- | --- |
| L1 | Installed with defaults | The CodeRabbit GitHub app on this repo |
| L2 | Told what good looks like | Path instructions in [`.coderabbit.yaml`](.coderabbit.yaml), code guidelines in [`AGENTS.md`](AGENTS.md) |
| L3 | Learns from the team | Learnings taught by replying to review comments |
| L4 | Enforces and reports | Custom pre-merge checks in [`.coderabbit.yaml`](.coderabbit.yaml): thresholds must live in config, playbooks must say how a case closes, rule changes must state their volume impact, and every trigger must say who handles it. A scheduled report and MCP context are set up in the CodeRabbit app |

The pull requests show each step, including a deliberately flawed change that the custom pre-merge check
catches.

## Simplifications and assumptions

This is the smallest version of the queue that does the job. Each item below is deliberate.

### Scope

- The engine reads a CSV and writes one. It decides who gets a case; tracking cases, sending campaigns and
  hand-offs happen in Pylon, Customer.io and Salesforce, which it doesn't connect to.
- The engine doesn't call an AI model. It records who handles each case; AI drafting runs in the team's own
  tools, with a person reviewing every draft before it reaches a customer.
- Graduation to a named CSM (assignment, the brief and the customer welcome) runs in Salesforce and
  Customer.io. The engine routes accounts above the band to a named CSM and stops there.
- Customer requests for help are routed by Support, not by the engine, because the triage bucket isn't in
  the export.
- One run is a snapshot with no campaign history. A dormant account's campaign age is estimated from days
  since the last review. Solo and stalled campaigns have no start date in the export, so their day-21
  cases need campaign data. For the same reason, the 90-day mute after a close and the P3-to-P2 aging after
  5 unworked business days run in Pylon, not in the engine.

### Data

- "Active" is assumed to mean anyone reviewed or interacting in the last 30 days, seated or not. It decides
  every seat headroom route, so it's the first thing to confirm.
- Three columns aren't used to route. `plan` is Pro on every row. `repos_connected` and
  `suggestion_acceptance_30d_pct` describe how the tool is used, not who is at risk, and have no baseline
  yet. Both stay on the work list for the CSM to read.
- Seat headroom dollars use one list price, $360 a seat a year. Rows priced differently are flagged as a
  possible discount or wrong ARR, not modelled.
- Renewal windows count calendar days and SLAs count business days, with no holiday calendar.

### Policy

- The windows (120, 150 and 180 days), the 21-day campaign and the priority tiers are starting judgments,
  not values fitted to data. They follow the brief's churn rates and live in config, so the monthly readout
  can retune them through a reviewed pull request.
- Cases are ordered by a plain sort, not a score: priority tier, renewal window, configuration depth, ARR.
  Every step comes straight from the export and explains itself in one line. A weighted score would need
  weights the export can't justify.
- `capacity.this_week_cases` is 10 because the exercise asks for this week's ten. The steady-state plan is
  about 5 new cases per CSM a week, about 20 for four CSMs, so the setting rises as the team ramps.
- `data/` holds 12 synthetic rows that exercise every route. The exercise's 40-row export is worked in the
  submitted sheet.
