# cs-pooled-queue

A small engine that turns an account export into a pooled customer success work list: which accounts open a case,
in what order, which go to automation or the account executive, and which rows have data that doesn't add up.

Built for the CodeRabbit Pooled Customer Success exercise by Derek Nielsen. The queue policy lives in
[`config/queue_rules.yaml`](config/queue_rules.yaml); the code only applies it, so the team can tune the queue
without a code change. The design is written up in [`docs/queue-design.md`](docs/queue-design.md) and the solo-user
playbook in [`docs/playbooks/solo-user.md`](docs/playbooks/solo-user.md).

## Run it

```bash
pip install -r requirements.txt
python -m pooled_queue.cli data/sample_export.csv     # writes out/worklist.csv and prints this week's list
pytest
```

`data/` holds synthetic accounts only. Real exports go in `data/private/`, which git ignores.

## CodeRabbit on this repo, L1 to L4

| Level | What's configured here |
|---|---|
| L1 | CodeRabbit installed with defaults; reviews every PR into `main` |
| L2 | [`.coderabbit.yaml`](.coderabbit.yaml) with path instructions for the engine, the policy file, playbooks, tests and data; `AGENTS.md` as code guidelines; ruff, markdownlint, yamllint and gitleaks |
| L3 | Learnings taught by replying to review comments (business-day SLAs, "flag, never drop", non-renewal intent always opens a case) |
| L4 | Pre-merge checks (thresholds must live in config, playbooks must say how a case closes, rule changes must state volume impact), a weekly scheduled report, and an MCP connection used as review context |

The pull requests in this repo show each step and what CodeRabbit caught.
