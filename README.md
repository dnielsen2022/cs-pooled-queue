# cs-pooled-queue

Turns an account export into a pooled customer success work list: which accounts open a case and in what
order, which go to the account executive or an automated campaign, and which rows have data that doesn't
add up.

Built by Derek Nielsen for a pooled customer success exercise. It is also a working example of CodeRabbit
configured from L1 to L4 on a real codebase.

## Where things are

This branch holds the review setup: the CodeRabbit configuration, the code guidelines it reviews against,
lint settings, CI and the pull request template. The engine, its policy file, tests, sample data and the
queue design arrive in the first pull request, so CodeRabbit reviews them against these rules.

| Path | What it is |
| --- | --- |
| [`.coderabbit.yaml`](.coderabbit.yaml) | CodeRabbit configuration: review profile, path instructions, pre-merge checks, tools, knowledge base |
| [`AGENTS.md`](AGENTS.md) | Code guidelines CodeRabbit treats as review criteria |
| [`.github/pull_request_template.md`](.github/pull_request_template.md) | The sections every pull request fills in, including the effect on weekly case volume |
| [`.github/workflows/tests.yml`](.github/workflows/tests.yml) | CI: runs pytest on every pull request |
| [`docs/coderabbit-setup.md`](docs/coderabbit-setup.md) | Every CodeRabbit setting in this repo, why it is there, and how to reproduce it |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | How to change a rule, open a pull request and run the checks locally |

## How to review this repo

The pull requests tell the story in order:

1. **Add the triage engine.** The engine, the policy file, 32 tests, synthetic data and the docs.
   CodeRabbit reviews it against the path instructions and code guidelines; replies to its comments teach
   it learnings for later reviews.
2. **A deliberately flawed "simplification".** It hard-codes a renewal window and a priority and drops the
   monthly-term rule. The tests still pass. The custom pre-merge check "Queue thresholds live in config"
   fails it. Closed without merging.
3. **A policy change.** It narrows the solo-user window. The "Rule change states volume impact" check
   warns until the description says what happens to weekly case volume. Closed afterwards.

## CodeRabbit maturity levels shown here

| Level | What it means | Where it lives |
| --- | --- | --- |
| L1 | Installed with defaults | The CodeRabbit GitHub app on this repo |
| L2 | Told what good looks like | Path instructions in [`.coderabbit.yaml`](.coderabbit.yaml), code guidelines in [`AGENTS.md`](AGENTS.md) |
| L3 | Learns from the team | Learnings taught by replying to review comments |
| L4 | Enforces and reports | Custom pre-merge checks in [`.coderabbit.yaml`](.coderabbit.yaml); a scheduled report and MCP context set up in the CodeRabbit app |

[`docs/coderabbit-setup.md`](docs/coderabbit-setup.md) explains each setting.
