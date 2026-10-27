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

Customers who ask for help come in a second way: support triages each request, and only how-to and adoption
questions become pooled cases. A product fault goes to a seventh route, Support.

Every decision carries a reason a CSM can read, a priority and SLA for cases, the first thing to say to the
customer, and any data problems found on the row.

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
   1. P1 Example Alpha Labs         Non-renewal intent
   2. P1 Example Beta Works         Dormant · L4
   3. P2 Example Theta Retail       Solo · L2
   4. P2 Example Delta Tools        Solo · L2
   5. P2 Example Zeta Data          Dormant · L1
   6. P2 Example Gamma Apps         Solo · L3
   7. P3 Example Eta Systems        Dormant · L2

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
| L4 | Enforces and reports | Custom pre-merge checks in [`.coderabbit.yaml`](.coderabbit.yaml): thresholds must live in config, playbooks must say how a case closes, rule changes must state their volume impact. A scheduled report and MCP context are set up in the CodeRabbit app |

The pull requests show each step, including a deliberately flawed change that the custom pre-merge check
catches.

## Limits

- Activity signals are only as good as the export. "Active" is assumed to mean anyone reviewed or
  interacting in the last 30 days, seated or not; that definition is the first thing to confirm.
- The engine decides who gets a case. Case tracking, campaigns and hand-offs happen in the team's existing
  support, CRM and campaign tools.
- One run is a snapshot with no campaign history. A dormant account's campaign age is estimated from days
  since the last review. Solo and stalled campaigns have no start date in the export, so their day-21
  cases need campaign data.
