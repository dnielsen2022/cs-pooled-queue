"""Turn an account export into a pooled customer success work list.

Every threshold comes from config/queue_rules.yaml. The engine only applies it.
"""
from __future__ import annotations

import csv
import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# "Case" is an interim route: triage() turns every case into "Work this week" or "Queue (next)".
# "Support" only comes from triage_request(), for a customer request that is a product fault.
ROUTES = ("Case", "Work this week", "Queue (next)", "AE", "Automated", "Hold", "Remove", "Support")


@dataclass
class Decision:
    """The queue's decision for one account, with the reasons a CSM will read."""

    account: str
    route: str = ""
    priority: str = ""
    sla_business_days: int | None = None
    rank: int | None = None
    signals: list[str] = field(default_factory=list)
    reason: str = ""
    first_touch: str = ""
    data_flags: list[str] = field(default_factory=list)
    also: list[str] = field(default_factory=list)
    sort_key: tuple = ()
    row: dict = field(default_factory=dict)


@dataclass
class Account:
    """One export row parsed into the fields the rules need. Missing values are None."""

    name: str
    arr: int | None
    level: int | None
    seats: int | None
    seats_active: int | None
    users: int | None
    idle_days: int | None
    signup_days: int | None
    tickets: int
    days_to_renewal: int | None
    monthly: bool
    nonrenewal_intent: bool
    cancellation_started: bool
    named_csm: bool


def load_rules(path: str | Path) -> dict:
    """Load the queue policy file."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_export(path: str | Path) -> list[dict]:
    """Read the export CSV into a list of row dicts (empty list for an empty file)."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _yes(value: str | None) -> bool:
    """True for the export's yes values."""
    return (value or "").strip().lower() in {"y", "yes", "true", "1"}


def parse(row: dict, rules: dict, as_of: dt.date, flags: list[str]) -> Account:
    """Parse one row. Missing or invalid values become None and are recorded in flags."""
    cols = rules["columns"]

    def raw(key: str) -> str:
        """The cell for a policy field, '' when the column or cell is missing."""
        return (row.get(cols[key]) or "").strip()

    def number(key: str) -> int | None:
        """A whole number, or None with a data flag."""
        text = raw(key)
        if not text:
            flags.append(f"Missing {cols[key]}")
            return None
        try:
            return int(float(text.replace(",", "").replace("$", "")))
        except ValueError:
            flags.append(f"Invalid {cols[key]}: {text!r}")
            return None

    level_text = raw("level").upper()
    level = int(level_text[1:]) if level_text[:1] == "L" and level_text[1:].isdigit() else None
    if level is None:
        flags.append(f"Missing or invalid {cols['level']}: {raw('level')!r}")

    renewal = raw("renewal_date")
    days_to_renewal = None
    try:
        days_to_renewal = (dt.date.fromisoformat(renewal) - as_of).days
    except ValueError:
        flags.append(f"Missing or invalid {cols['renewal_date']}: {renewal!r}")

    return Account(
        name=raw("account") or "(no name)",
        arr=number("arr"),
        level=level,
        seats=number("seats_purchased"),
        seats_active=number("seats_active"),
        users=number("active_users"),
        idle_days=number("days_since_last_review"),
        signup_days=number("days_since_signup"),
        tickets=number("support_tickets") or 0,
        days_to_renewal=days_to_renewal,
        monthly=raw("term").lower() == "monthly",
        nonrenewal_intent=_yes(raw("nonrenewal_intent")),
        cancellation_started=_yes(raw("cancellation_started")),
        named_csm=bool(raw("success_manager")),
    )


def data_checks(a: Account, rules: dict, flags: list[str]) -> bool:
    """Flag contradictions in the row. Returns True when activity data contradicts itself."""
    checks, price = rules["data_checks"], rules["band"]["price_per_seat"]
    window = checks["activity_window_days"]
    contradiction = False
    if a.seats == 0:
        flags.append("0 seats purchased")
    if a.arr is not None and a.seats and abs(a.arr / a.seats - price) > checks["price_tolerance_usd"]:
        flags.append(f"ARR per seat is ${a.arr / a.seats:,.0f}, not ${price}: discount or wrong ARR?")
    if a.users is not None and a.seats_active is not None:
        if a.users <= checks["mismatch_max_users"] and a.seats_active >= checks["mismatch_min_seats"]:
            flags.append(f"{a.seats_active} active seats but {a.users} active user(s): which is right?")
            contradiction = True
        elif a.seats_active - a.users >= checks["seats_vs_users_gap"]:
            flags.append(f"{a.seats_active} active seats vs {a.users} active users: confirm before any seat quote")
    if a.idle_days is not None and a.signup_days is not None and a.idle_days > a.signup_days:
        flags.append(f"Last review {a.idle_days} days ago but signed up {a.signup_days} days ago: impossible")
    if a.users and a.idle_days is not None and a.idle_days > window:
        flags.append(f"{a.users} active users in {window} days but no review for {a.idle_days} days: "
                     "what counts as active?")
    if a.users == 0 and a.idle_days is not None and a.idle_days < window:
        flags.append(f"0 active users but a review {a.idle_days} days ago: what counts as active?")
    if a.days_to_renewal is not None and a.days_to_renewal < 0:
        flags.append("Renewal date is in the past")
    return contradiction


def _within(a: Account, days: int, rules: dict) -> bool:
    """Inside a renewal window. Monthly terms always are; an unknown date never is."""
    if a.monthly and rules.get("monthly_always_in_window", True):
        return True
    return a.days_to_renewal is not None and a.days_to_renewal <= days


def _case(d: Decision, trigger: dict, priority: str, reason: str) -> None:
    """Open a case with the trigger's SLA and first touch."""
    d.route, d.priority, d.reason = "Case", priority, reason
    d.sla_business_days = trigger["sla_business_days"]
    d.first_touch = trigger["first_touch"]


def _signals(a: Account, rules: dict) -> dict[str, bool]:
    """Which flags are on for this account."""
    fl = rules["flags"]
    onboarding = a.signup_days is not None and a.signup_days <= fl["onboarding"]["max_days_since_signup"]
    users_known = a.users is not None
    return {
        "onboarding": onboarding,
        "dormant": users_known and not onboarding and a.users <= fl["dormant"]["max_active_users"],
        "solo": users_known and not onboarding and a.users == fl["solo"]["active_users"],
        "stalled": (users_known and not onboarding and a.level == fl["stalled_onboarding"]["level"]
                    and a.users >= fl["stalled_onboarding"]["min_active_users"]),
    }


def _route_out_of_band(a: Account, d: Decision, rules: dict) -> bool:
    """Remove accounts outside the band or with a named CSM. Returns True when removed."""
    band = rules["band"]
    if a.named_csm:
        d.route, d.reason = "Remove", "Has a named CSM: tell them about any open signal."
    elif a.arr is not None and a.arr > band["max_arr"]:
        d.route, d.reason = "Remove", f"Above the ${band['max_arr']:,} band: belongs with a named CSM."
    elif a.arr is not None and a.arr < band["min_arr"]:
        d.route, d.reason = "Remove", f"Below the ${band['min_arr']:,} band: product and automated programmes."
    return d.route == "Remove"


def _route_flags(a: Account, d: Decision, on: dict[str, bool], rules: dict) -> None:
    """Route an in-band account with no intent signal, in policy order."""
    trig = rules["triggers"]
    dormant, solo, stalled, exhausted = (trig["dormant"], trig["solo"], trig["stalled_onboarding"],
                                         trig["automation_exhausted"])
    track_day = max(0, (a.idle_days or 0) - rules["flags"]["dormant"]["idle_days_to_fire"])
    if on["onboarding"]:
        d.route, d.reason = "Automated", trig["onboarding"]["automated_track"]
    elif on["dormant"] and (a.level or 0) >= dormant["deep_level"]:
        _case(d, dormant, dormant["deep_priority"],
              f"Configured to L{dormant['deep_level']}+ and nobody active: something broke.")
    elif on["dormant"] and a.days_to_renewal is not None and a.days_to_renewal <= 120:  # simpler than _within
        _case(d, dormant, "P2",
              f"Dormant inside {dormant['near_renewal_days']} days of renewal.")
    elif on["dormant"] and track_day >= exhausted["track_days"]:
        _case(d, exhausted, exhausted["priority"],
              f"Dormant {a.idle_days} days: the {exhausted['track_days']}-day campaign ran out without activity.")
    elif on["dormant"]:
        d.route = "Automated"
        d.reason = (f"{dormant['automated_track']}: day {track_day} of {exhausted['track_days']}; "
                    f"a case in {exhausted['track_days'] - track_day} days if still quiet.")
    elif on["solo"] and _within(a, solo["renewal_within_days"], rules):
        _case(d, solo, solo["priority"], f"Solo inside {solo['renewal_within_days']} days of renewal.")
    elif on["solo"]:
        d.route = "Automated"
        d.reason = (f"{solo['automated_track']}: a case at day {exhausted['track_days']} of the campaign, "
                    f"or once inside {solo['renewal_within_days']} days of renewal, whichever is first.")
    elif on["stalled"] and _within(a, stalled["renewal_within_days"], rules):
        _case(d, stalled, stalled["priority"],
              f"In use but not configured, inside {stalled['renewal_within_days']} days of renewal.")
    elif on["stalled"]:
        d.route, d.reason = "Automated", stalled["automated_track"]


def _labels(a: Account, on: dict[str, bool], headroom: int) -> list[str]:
    """The signal labels shown to a CSM."""
    labels = [("Non-renewal intent", a.nonrenewal_intent), ("Cancellation started", a.cancellation_started),
              (f"Dormant · L{a.level or '?'}", on["dormant"]), (f"Solo · L{a.level or '?'}", on["solo"]),
              ("Stalled onboarding", on["stalled"]), ("Onboarding", on["onboarding"]),
              (f"Seat headroom +{headroom}", headroom > 0)]
    return [label for label, is_on in labels if is_on]


def _fill_first_touch(text: str, a: Account, as_of: dt.date) -> str:
    """Fill the first-touch placeholders from the row. {date} is the date of the last review."""
    if "{date}" not in text:
        return text
    last = (as_of - dt.timedelta(days=a.idle_days)).isoformat() if a.idle_days is not None else "an unknown date"
    return text.replace("{date}", last)


def _sort_key(a: Account, priority: str, order: dict) -> tuple:
    """Priority tier, renewal window, deeper configuration first, then higher ARR."""
    renewal = a.days_to_renewal if a.days_to_renewal is not None else 10**6
    bucket = next((i for i, b in enumerate(order["renewal_buckets_days"]) if renewal <= b),
                  len(order["renewal_buckets_days"]))
    return (order["priority_rank"].get(priority, 9), bucket, -(a.level or 0), -(a.arr or 0))


def decide(row: dict, rules: dict, as_of: dt.date) -> Decision:
    """Apply the queue policy to one export row."""
    flags: list[str] = []
    a = parse(row, rules, as_of, flags)
    contradiction = data_checks(a, rules, flags)
    d = Decision(account=a.name, row=row, data_flags=flags)
    trig, band, checks = rules["triggers"], rules["band"], rules["data_checks"]
    on = _signals(a, rules)
    headroom = max(0, (a.users or 0) - a.seats) if a.seats else 0

    d.signals = _labels(a, on, headroom)

    in_band = not _route_out_of_band(a, d, rules)
    if in_band and a.nonrenewal_intent:
        _case(d, trig["nonrenewal_intent"], trig["nonrenewal_intent"]["priority"],
              "Non-renewal intent inside the band always opens a case.")
    elif in_band and a.cancellation_started:
        _case(d, trig["cancellation_started"], trig["cancellation_started"]["priority"],
              "Cancellation started inside the band always opens a case.")
    elif in_band and contradiction and checks["hold_on_contradiction"]:
        d.route, d.reason = "Hold", "Activity data contradicts itself: no outreach or campaigns until verified."
    elif in_band:
        _route_flags(a, d, on, rules)

    if not d.route and headroom > 0:
        d.route, d.sla_business_days = "AE", trig["seat_headroom"]["sla_business_days"]
        d.first_touch = trig["seat_headroom"]["first_touch"]
        d.reason = (f"{headroom} more active users than seats: buying signal, "
                    f"about ${headroom * band['price_per_seat']:,} ARR.")
    elif not d.route:
        d.route, d.reason = "Automated", "Healthy: leave alone; next-level configuration nudges only."

    if d.route not in ("Remove", "AE") and headroom > 0:
        d.also.append("AE: seat headroom")
    if headroom > 0 and (a.arr or 0) + headroom * band["price_per_seat"] > band["max_arr"]:
        d.also.append(f"up-tier to a named CSM once expanded past ${band['max_arr']:,}")
    if a.tickets >= checks["tickets_to_read_first"]:
        d.also.append(f"read the {a.tickets} recent support ticket(s) before the first touch")

    d.first_touch = _fill_first_touch(d.first_touch, a, as_of)
    d.sort_key = _sort_key(a, d.priority, rules["ordering"])
    return d


def triage_request(row: dict, bucket: str, rules: dict, as_of: dt.date) -> Decision:
    """Route a customer request that support has triaged into a bucket (triggers.customer_asks.routes).

    An advisory request becomes a case; a flagged account, or one near renewal, gets the raised priority.
    Non-renewal intent still opens a P1 case, and out-of-band accounts go where they belong.
    """
    ask = rules["triggers"]["customer_asks"]
    if bucket not in ask["routes"]:
        raise ValueError(f"Unknown request bucket {bucket!r}; expected one of {sorted(ask['routes'])}")
    flags: list[str] = []
    a = parse(row, rules, as_of, flags)
    data_checks(a, rules, flags)
    d = Decision(account=a.name, row=row, data_flags=flags)
    on = _signals(a, rules)
    headroom = max(0, (a.users or 0) - a.seats) if a.seats else 0
    d.signals = [f"Customer ask · {bucket}"] + _labels(a, on, headroom)
    flagged = [k for k in ("dormant", "solo", "stalled") if on[k]]
    route = ask["routes"][bucket]

    if _route_out_of_band(a, d, rules):
        pass
    elif a.nonrenewal_intent or a.cancellation_started:
        trigger = rules["triggers"]["nonrenewal_intent" if a.nonrenewal_intent else "cancellation_started"]
        _case(d, trigger, trigger["priority"], "The customer asked for help and has signalled they may leave.")
    elif route == "Case" and (flagged or _within(a, ask["raise_within_days"], rules)):
        why = f"already flagged {', '.join(flagged)}" if flagged else f"renews within {ask['raise_within_days']} days"
        _case(d, ask, ask["raised_priority"], f"Customer asked for help ({bucket}) and is {why}.")
    elif route == "Case":
        _case(d, ask, ask["priority"], f"Customer asked for help ({bucket}).")
    elif route == "AE":
        d.route, d.reason = "AE", "Buying question: an AE task with who, what and by when."
    elif route == "Support":
        d.route, d.reason = "Support", "Product fault: Support owns it, filed with a reproduction."
    else:
        d.route = "Automated"
        d.reason = "Known friction: answer from the docs; a fix that keeps recurring becomes a campaign step."

    d.first_touch = _fill_first_touch(d.first_touch, a, as_of)
    d.sort_key = _sort_key(a, d.priority, rules["ordering"])
    return d


def triage(rows: list[dict], rules: dict, as_of: dt.date) -> list[Decision]:
    """Decide every row, order the cases and mark this week's work list."""
    decisions = [decide(r, rules, as_of) for r in rows]
    cases = sorted((d for d in decisions if d.route == "Case"), key=lambda d: d.sort_key)
    for i, d in enumerate(cases, start=1):
        d.rank = i
        d.route = "Work this week" if i <= rules["capacity"]["this_week_cases"] else "Queue (next)"
    return decisions
