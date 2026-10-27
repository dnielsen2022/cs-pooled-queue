"""Command line entry point: triage an export and write the work list.

    python -m pooled_queue.cli data/sample_export.csv --out out/worklist.csv
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from pooled_queue.engine import load_export, load_rules, triage

ADDED = ["route", "priority", "rank", "sla_business_days", "signals", "reason", "also", "data_flags"]


def main(argv: list[str] | None = None) -> int:
    """Triage the export and write it back out with the queue's columns added."""
    p = argparse.ArgumentParser(description="Pooled CS queue triage")
    p.add_argument("export", help="CSV export of accounts in the band")
    p.add_argument("--rules", default="config/queue_rules.yaml")
    p.add_argument("--out", default="out/worklist.csv")
    a = p.parse_args(argv)

    rules = load_rules(a.rules)
    rows = load_export(a.export)
    decisions = triage(rows, rules)

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) + ADDED)
        w.writeheader()
        for d in decisions:
            w.writerow({**d.row, "route": d.route, "priority": d.priority, "rank": d.rank or "",
                        "sla_business_days": d.sla_business_days or "", "signals": "; ".join(d.signals),
                        "reason": d.reason, "also": "; ".join(d.also), "data_flags": "; ".join(d.data_flags)})

    week = sorted((d for d in decisions if d.route == "Work this week"), key=lambda d: d.rank)
    print(f"This week ({len(week)}):")
    for d in week:
        print(f"  {d.rank:>2}. {d.priority} {d.account:<26} {', '.join(d.signals)}")
    flagged = [d for d in decisions if d.data_flags]
    if flagged:
        print(f"\nData to check ({len(flagged)}):")
        for d in flagged:
            print(f"  - {d.account}: {' / '.join(d.data_flags)}")
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
