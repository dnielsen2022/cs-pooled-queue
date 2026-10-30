# CodeRabbit setup

How CodeRabbit is configured on this repo, why each setting is there, and how to reproduce it on another
repo. Everything that can live in the repo is in [`.coderabbit.yaml`](../.coderabbit.yaml) and
[`AGENTS.md`](../AGENTS.md). Two L4 features, scheduled reports and MCP connections, are set up in the
CodeRabbit app.

## Maturity levels

| Level | What the team has done | In this repo |
| --- | --- | --- |
| L1 | Installed the app; reviews run on defaults | CodeRabbit GitHub app installed on the repo |
| L2 | Told CodeRabbit what good looks like for this codebase | `path_instructions`, `code_guidelines` |
| L3 | Taught it the team's preferences through review replies | `learnings` |
| L4 | Made it enforce rules and report on its own | `pre_merge_checks`, scheduled report, MCP context |

Each level builds on the one before it. A team at L1 gets generic comments. A team at L4 gets comments
that know its rules, and gets told when a pull request breaks one.

## Review settings

| Setting | Value | Why |
| --- | --- | --- |
| `reviews.profile` | `assertive` | More comments, including nitpicks. Right for a small repo where policy errors matter |
| `reviews.high_level_summary` | `true` | Each pull request gets a plain-language summary at the top |
| `reviews.auto_review.enabled` | `true` | Every pull request is reviewed without anyone asking |
| `reviews.auto_review.drafts` | `false` | Draft pull requests are skipped until they are marked ready |
| `reviews.path_filters` | `!data/private/**` | Real exports never reach a review, even if one is committed by mistake |

## Path instructions (L2)

Path instructions tell CodeRabbit what to look for in each part of the repo. Each one is written as the
standard a reviewer on this team would hold that file to.

| Path | What CodeRabbit is told to check |
| --- | --- |
| `pooled_queue/**/*.py` | No hard-coded thresholds; SLAs in business days and renewal windows in calendar days; a readable reason on every decision; bad data flagged, never dropped; non-renewal intent always opens a case |
| `config/queue_rules.yaml` | Review it like a pricing change: every case trigger has a priority, an SLA and a first touch; priorities match the churn evidence; changes that move weekly case volume are called out |
| `docs/playbooks/**` | Read it as a CSM on their first day: every step has an owner, a timing and a next action; the playbook says what closes the case and what is recorded |
| `tests/**` | Tests read thresholds from the policy file; edge cases covered (past renewal dates, blank cells, contradictory data, out-of-band ARR) |
| `data/**` | Only synthetic data: nothing that looks like a real company, person, email or account ID |

## Code guidelines (L2)

`knowledge_base.code_guidelines.filePatterns` points CodeRabbit at [`AGENTS.md`](../AGENTS.md). Its seven
rules apply to every review, on top of the path instructions. Keeping them in a file in the repo means
they are versioned and reviewed like code.

## Learnings (L3)

`knowledge_base.learnings.scope: auto` lets CodeRabbit keep what the team tells it. On a public repo,
`auto` scopes learnings to this repo. To teach one, reply to a review comment and mention the bot:

```text
@coderabbitai SLAs in this repo are business days; renewal windows are calendar days. Please remember that.
```

CodeRabbit confirms it has stored the learning and applies it to later reviews. Stored learnings can be
reviewed and removed in the CodeRabbit app.

## Pre-merge checks (L4)

Pre-merge checks run on every pull request and report pass, warning or fail in the review. A check in
`error` mode is marked failed. It only blocks a merge when automatic approvals are turned on in CodeRabbit.

| Check | Mode | What it checks |
| --- | --- | --- |
| Title | warning | Starts with an imperative verb and stays under 60 characters |
| Description | warning | The description is filled in and matches the change |
| Docstrings | warning | At least 80% of functions have docstrings |
| Issue assessment | off | No linked issues in this repo |

### Custom checks

| Check | Mode | Fails when | How to see it fire |
| --- | --- | --- | --- |
| Queue thresholds live in config | error | A pull request adds or changes a numeric queue threshold in Python instead of `config/queue_rules.yaml` | Pull request 2 hard-codes a 120-day window and a priority |
| Playbook defines how a case closes | warning | A changed playbook has no "Closes when" or "Recorded on close" section | Remove either section from a playbook in a pull request |
| Rule change states volume impact | warning | `config/queue_rules.yaml` changes and the description doesn't say what happens to weekly case volume | Pull request 3, opened with the volume section empty |

To re-run the checks after editing a pull request description, comment:

```text
@coderabbitai run pre-merge checks
```

## Tools

CodeRabbit runs these linters by default, so `.coderabbit.yaml` has no `tools` section, and reports their
findings in the review. The repo's own settings files ([`.flake8`](../.flake8),
[`.markdownlint.yaml`](../.markdownlint.yaml), [`.yamllint.yaml`](../.yamllint.yaml) and `[tool.ruff]` in
[`pyproject.toml`](../pyproject.toml)) keep local runs and CodeRabbit's runs the same.

| Tool | Checks |
| --- | --- |
| ruff, flake8, pylint | Python style and common bugs, at 120 characters |
| markdownlint | Markdown in the docs and playbooks |
| yamllint | The policy file and CI workflow |
| gitleaks | Secrets committed by mistake |

## MCP context (L4)

`knowledge_base.mcp.usage: enabled` lets CodeRabbit pull context from connected MCP servers during reviews.
The default, `auto`, skips MCP on public repos, so it is turned on explicitly here. Connections are added
in the CodeRabbit app under Connections; this repo uses a documentation connector.

## Scheduled report (L4)

Set up in the CodeRabbit app under Recurring Reports: weekly on Friday, filtered to this repo, using the
Sprint Report template, delivered by email. It gives the team a weekly summary of pull request activity
without anyone having to pull it together.

## Reproducing this on another repo

1. Install the CodeRabbit GitHub app on the repo.
2. Copy [`.coderabbit.yaml`](../.coderabbit.yaml) and [`AGENTS.md`](../AGENTS.md), then rewrite the path
   instructions and guidelines for that codebase. The schema line at the top of the YAML gives editor
   autocomplete and validation.
3. Open a pull request and read the review. Reply to comments to teach learnings.
4. Add custom pre-merge checks for the rules the team cares most about, in `warning` mode first. Move a
   check to `error` once it stops producing false alarms.
5. Set up a scheduled report and any MCP connections in the CodeRabbit app.
