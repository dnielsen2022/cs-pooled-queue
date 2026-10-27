"""Turn a CodeRabbit account export into a pooled CS work list.

Every threshold comes from config/queue_rules.yaml. The engine only applies it.
"""
from __future__ import annotations

import csv
import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Decision:
    """The queue's decision for one account, with the reasons a CSM will read."""

    account: str
    route: str = ""            # Work this week | Queue (next) | Automated | AE | Remove
    priority: str = ""         # P1, P2, P3 for cases
    sla_business_days: int | None = None
    rank: int | None = None
    signals: list[str] = field(default_factory=list)
    reason: str = ""
    data_flags: list[str] = field(default_factory=list)
    also: list[str] = field(default_factory=list)   # secondary routes, e.g. AE alongside a case
    sort_key: tuple = ()
    row: dict = field(default_factory=dict)


def load_rules(path: str | Path) -> dict:
    """Load the queue policy file."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_export(path: str | Path) -> list[dict]:
    """Read the export CSV into a list of row dicts."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _level(v: str) -> int:
    v = (v or "").strip().upper()
    return int(v[1:]) if v.startswith("L") and v[1:].isdigit() else 0


def _yes(v: str) -> bool:
    return (v or "").strip().lower() in {"y", "yes", "true", "1"}


def _bucket(days: int, buckets: list[int]) -> int:
    for i, b in enumerate(buckets):
        if days <= b:
            return i
    return len(buckets)


def decide(row: dict, rules: dict) -> Decision:
    """Apply the queue policy to one export row."""
    c = rules["columns"]
    band, flags, trig = rules["band"], rules["flags"], rules["triggers"]
    as_of = dt.date.fromisoformat(rules["as_of"])

    name = row[c["account"]]
    arr = int(row[c["arr"]])
    level = _level(row[c["level"]])
    seats = int(row[c["seats_purchased"]])
    seats_active = int(row[c["seats_active"]])
    users = int(row[c["active_users"]])
    last_review = int(row[c["days_since_last_review"]])
    signup = int(row[c["days_since_signup"]])
    monthly = row[c["term"]].strip().lower() == "monthly"
    renew = dt.date.fromisoformat(row[c["renewal_date"]])
    dtr = (renew - as_of).days
    monthly_in_window = monthly and rules.get("monthly_always_in_window", True)

    def within(days: int) -> bool:
        return dtr <= days or monthly_in_window

    d = Decision(account=name, row=row)

    # ---- data checks: flag, never drop ----
    if seats and abs(arr / seats - band["price_per_seat"]) > 1:
        d.data_flags.append(f"ARR/seat is ${arr / seats:,.0f}, not ${band['price_per_seat']}: discount or wrong ARR?")
    if users <= 1 and seats_active > 5:
        d.data_flags.append(f"{seats_active} active seats but {users} active user(s): which is right?")
    if last_review > signup:
        d.data_flags.append(f"Last review {last_review} days ago but signed up {signup} days ago: impossible")
    if users > 0 and last_review > 30:
        d.data_flags.append(f"{users} active users in 30 days but no review for {last_review} days: what counts as active?")
    if dtr < 0:
        d.data_flags.append("Renewal date is in the past")

    nri = _yes(row[c["nonrenewal_intent"]])
    cancel = _yes(row[c["cancellation_started"]])
    tickets = int(row[c["support_tickets"]] or 0)

    is_dormant = level >= flags["dormant"]["min_level"] and users <= flags["dormant"]["max_active_users"]
    is_solo = level >= flags["solo"]["min_level"] and users == flags["solo"]["active_users"]
    is_stalled = level == flags["stalled_onboarding"]["level"] and signup >= flags["stalled_onboarding"]["min_days_since_signup"]
    is_onboarding = signup < flags["stalled_onboarding"]["min_days_since_signup"]
    headroom = users - seats if users > seats else 0

    for label, on in [("Non-renewal intent", nri), ("Cancellation started", cancel), ("Dormant", is_dormant),
                      ("Solo", is_solo), ("Stalled onboarding", is_stalled and not is_onboarding),
                      ("Onboarding (<45d)", is_onboarding), (f"Seat headroom +{headroom}", headroom > 0)]:
        if on:
            d.signals.append(label)

    # ---- out of band ----
    if row[c["success_manager"]].strip() or arr > band["max_arr"]:
        d.route = "Remove"
        d.reason = "Above the band and/or already has a named CSM; alert the named CSM to any open signal."
        return _finish(d, rules, dtr, level, arr)
    if arr < band["min_arr"]:
        d.route = "Remove"
        d.reason = "Below $10k: covered by the product and automated programmes."
        return _finish(d, rules, dtr, level, arr)

    # ---- cases ----
    if nri:
        d.route, d.priority, d.sla_business_days = "Case", "P1", 1  # 1 day
        d.reason = "Non-renewal intent always opens a P1 case."
    elif is_dormant and level >= trig["dormant"]["p1_min_level"]:
        d.route, d.priority, d.sla_business_days = "Case", "P1", trig["dormant"]["sla_business_days"]
        d.reason = "Deeply configured (L3+) and nobody active: something broke. P1 whenever it fires."
    elif is_dormant and dtr <= 120:  # quick fix: same as config for now
        d.route, d.priority, d.sla_business_days = "Case", "P2", trig["dormant"]["sla_business_days"]
        d.reason = "Dormant L2 inside the renewal window."
    elif is_dormant:
        d.route, d.reason = "Automated", trig["dormant"]["automated_track"]
    elif is_solo and within(trig["solo"]["renewal_within_days"]):
        d.route, d.priority, d.sla_business_days = "Case", "P2", trig["solo"]["sla_business_days"]
        d.reason = "Solo inside 150 days of renewal (monthly terms are always inside)."
    elif is_solo:
        d.route, d.reason = "Automated", trig["solo"]["automated_track"]
    elif is_stalled and within(trig["stalled_onboarding"]["renewal_within_days"]):
        d.route, d.priority, d.sla_business_days = "Case", "P3", trig["stalled_onboarding"]["sla_business_days"]
        d.reason = "Still L1 after onboarding and inside 180 days of renewal."
    elif is_stalled:
        d.route, d.reason = "Automated", trig["stalled_onboarding"]["automated_track"]
    elif is_onboarding:
        d.route, d.reason = "Automated", trig["onboarding"]["automated_track"]
    elif headroom > 0:
        d.route = "AE"
        d.reason = f"{headroom} more active users than seats: buying signal, ~${headroom * band['price_per_seat']:,} ARR."
    else:
        d.route, d.reason = "Automated", "Healthy: leave alone; next-level config nudges only."

    if headroom > 0 and d.route != "AE":
        d.also.append("AE: seat headroom")
    if headroom > 0 and arr + headroom * band["price_per_seat"] > band["max_arr"]:
        d.also.append("Up-tier to named CSM once expanded past $30k")
    if tickets >= 2:
        d.also.append(f"Read the {tickets} open support tickets before the first touch")
    return _finish(d, rules, dtr, level, arr)


def _finish(d: Decision, rules: dict, dtr: int, level: int, arr: int) -> Decision:
    rank = rules["ordering"]["priority_rank"].get(d.priority, 9)
    d.sort_key = (rank, _bucket(dtr, rules["ordering"]["renewal_buckets_days"]), -level, -arr)
    return d


def triage(rows: list[dict], rules: dict) -> list[Decision]:
    """Decide every row, order the cases and mark this week's work list."""
    decisions = [decide(r, rules) for r in rows]
    cases = sorted((d for d in decisions if d.route == "Case"), key=lambda d: d.sort_key)
    for i, d in enumerate(cases, start=1):
        d.rank = i
        d.route = "Work this week" if i <= rules["capacity"]["this_week_cases"] else "Queue (next)"
    return decisions
