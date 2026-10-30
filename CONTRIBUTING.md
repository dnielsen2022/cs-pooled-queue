# Contributing

Every change goes through a pull request into `main`. CodeRabbit reviews it, CI runs the tests, and a
person merges it.

## Set up

```bash
pip install -r requirements.txt
pytest
```

Python 3.11 or later. The optional linters match what CodeRabbit runs:

```bash
pip install ruff yamllint
ruff check .
yamllint .
npx markdownlint-cli2 "**/*.md"
```

## Changing a queue rule

The queue's policy lives in `config/queue_rules.yaml`. The code only applies it, so most changes to who
gets a case, how soon and in what order are a one-line edit to that file.

1. Change the value in `config/queue_rules.yaml`. Don't add the number to Python: the "Queue thresholds
   live in config" check fails any pull request that does.
2. Run the work list before and after on the sample data and compare:

   ```bash
   python -m pooled_queue.cli data/sample_export.csv --as-of 2026-10-05 --out out/before.csv
   # make the change
   python -m pooled_queue.cli data/sample_export.csv --as-of 2026-10-05 --out out/after.csv
   ```

3. Update any doc that states the old value, such as `docs/queue-design.md` or a playbook.
4. In the pull request, fill in **Effect on weekly case volume**: more, fewer or unchanged, with a rough
   number. The "Rule change states volume impact" check warns until it's there.

## Changing the code

- Read [`AGENTS.md`](AGENTS.md) first. CodeRabbit reviews against it.
- Every function has type hints and a docstring.
- Every routing decision carries a reason a CSM can read.
- Missing or contradictory data goes into `data_flags`. Never drop a row or guess a value.
- Add a test for every new rule or edge case. Tests read thresholds from the policy file instead of
  restating them.

## Adding a playbook

Playbooks live in `docs/playbooks/`. Each one needs a trigger, an owner, steps with a time and an owner for
each, and two sections the "Playbook defines how a case closes" check looks for: **Closes when** and
**Recorded on close**.

## Pull requests

- **Title:** start with an imperative verb, under 60 characters ("Tighten the solo renewal window").
- **Description:** fill in every section of the template.
- **Review:** answer CodeRabbit's comments. If a comment reflects a rule the team wants kept, reply with
  `@coderabbitai` and the rule so it becomes a learning.
- **Merge:** use "Create a merge commit" so each pull request's history stays readable.

## Data

Only synthetic data goes in `data/`. Real exports go in `data/private/`, which git ignores and CodeRabbit
never reviews.
