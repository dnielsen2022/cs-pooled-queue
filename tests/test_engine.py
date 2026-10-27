"""Tests for the queue policy engine. Thresholds are read from the policy file, never restated."""
import datetime as dt
from pathlib import Path

import pytest

from pooled_queue.cli import main
from pooled_queue.engine import decide, load_export, load_rules, triage

RULES = load_rules(Path(__file__).parent.parent / "config" / "queue_rules.yaml")
AS_OF = dt.date(2026, 10, 5)
TRIG = RULES["triggers"]

BASE = {
    "account": "Test Co", "arr_usd": "18000", "plan": "Pro", "maturity_level": "L3", "seats_purchased": "50",
    "seats_active_30d": "40", "active_users_30d": "35", "days_since_last_review": "1", "repos_connected": "10",
    "renewal_date": "2027-03-01", "term": "annual", "nonrenewal_intent": "N", "cancellation_started": "N",
    "support_tickets_30d": "0", "suggestion_acceptance_30d_pct": "50", "days_since_signup": "400",
    "success_manager": "",
}


def row(**kw):
    """A healthy in-band account with the given fields changed."""
    r = dict(BASE)
    r.update({k: str(v) for k, v in kw.items()})
    return r


def renews_in(days):
    """A renewal date this many days after the as-of date."""
    return (AS_OF + dt.timedelta(days=days)).isoformat()


def run(**kw):
    """Decide one account."""
    return decide(row(**kw), RULES, AS_OF)


def test_healthy_account_is_left_to_automation():
    """No signal, no case."""
    assert run().route == "Automated"


def test_nonrenewal_intent_opens_a_case_even_with_bad_data():
    """Intent is read before anything else, and the bad cells are flagged, not fatal."""
    d = run(nonrenewal_intent="Y", arr_usd="", renewal_date="", maturity_level="")
    assert (d.route, d.priority) == ("Case", TRIG["nonrenewal_intent"]["priority"])
    assert len(d.data_flags) == 3


def test_cancellation_started_alone_opens_a_case():
    """A started cancellation is its own trigger."""
    d = run(cancellation_started="Y")
    assert (d.route, d.priority) == ("Case", TRIG["cancellation_started"]["priority"])


def test_deep_dormant_account_is_top_priority_far_from_renewal():
    """Deep configuration gone quiet is urgent whatever the renewal date."""
    d = run(active_users_30d=0, seats_active_30d=0, days_since_last_review=31, renewal_date=renews_in(330))
    assert (d.route, d.priority) == ("Case", TRIG["dormant"]["deep_priority"])


def test_dormant_first_touch_names_the_last_review_date():
    """The first touch cites the customer's own last review date, not a placeholder."""
    d = run(active_users_30d=0, seats_active_30d=0, days_since_last_review=31, renewal_date=renews_in(330))
    assert "{date}" not in d.first_touch
    assert (AS_OF - dt.timedelta(days=31)).isoformat() in d.first_touch


def test_dormant_applies_at_l1():
    """Flags apply at every maturity level."""
    near = TRIG["dormant"]["near_renewal_days"] - 1
    d = run(maturity_level="L1", active_users_30d=0, seats_active_30d=0, days_since_last_review=40,
            renewal_date=renews_in(near))
    assert any(s.startswith("Dormant") for s in d.signals)
    assert d.priority == TRIG["dormant"]["near_renewal_priority"]


def test_dormant_campaign_becomes_a_case_when_it_runs_out():
    """Shallow dormant accounts far from renewal go to automation first, then to a case."""
    fire = RULES["flags"]["dormant"]["idle_days_to_fire"]
    track = TRIG["automation_exhausted"]["track_days"]
    far = renews_in(TRIG["dormant"]["near_renewal_days"] + 60)
    early = run(maturity_level="L2", active_users_30d=0, seats_active_30d=0,
                days_since_last_review=fire + track - 1, renewal_date=far)
    late = run(maturity_level="L2", active_users_30d=0, seats_active_30d=0,
               days_since_last_review=fire + track, renewal_date=far)
    assert early.route == "Automated"
    assert (late.route, late.priority) == ("Case", TRIG["automation_exhausted"]["priority"])


@pytest.mark.parametrize("offset,expected", [(-1, "Case"), (30, "Automated")])
def test_solo_uses_the_policy_window(offset, expected):
    """Solo accounts open a case only inside the configured renewal window."""
    days = TRIG["solo"]["renewal_within_days"] + offset
    d = run(maturity_level="L2", active_users_30d=1, seats_active_30d=1, renewal_date=renews_in(days))
    assert d.route == expected


def test_monthly_terms_are_always_inside_the_window():
    """A monthly account can leave at any month end."""
    d = run(maturity_level="L2", active_users_30d=1, seats_active_30d=1, term="monthly",
            renewal_date=renews_in(330))
    assert d.route == "Case"


@pytest.mark.parametrize("arr,manager", [("9000", ""), ("32000", ""), ("20000", "Named CSM")])
def test_out_of_band_rows_are_removed(arr, manager):
    """Outside the band or with a named CSM: not the pooled team's account."""
    assert run(arr_usd=arr, success_manager=manager).route == "Remove"


def test_seat_headroom_goes_to_the_ae():
    """More users than seats is a buying signal."""
    d = run(active_users_30d=60, seats_active_30d=50)
    assert (d.route, d.sla_business_days) == ("AE", TRIG["seat_headroom"]["sla_business_days"])


def test_contradictory_activity_is_held():
    """Many active seats but one active user: no outreach until verified."""
    d = run(active_users_30d=1, seats_active_30d=40)
    assert d.route == "Hold"
    assert any("active seats" in f for f in d.data_flags)


@pytest.mark.parametrize("fields,phrase", [
    ({"days_since_last_review": 20, "days_since_signup": 10}, "impossible"),
    ({"seats_purchased": 0}, "0 seats"),
    ({"renewal_date": "2026-09-01"}, "in the past"),
    ({"maturity_level": ""}, "maturity_level"),
    ({"arr_usd": "lots"}, "Invalid arr_usd"),
])
def test_bad_data_is_flagged_not_fatal(fields, phrase):
    """Every row gets a decision; problems go in data_flags."""
    d = run(**fields)
    assert d.route
    assert any(phrase in f for f in d.data_flags)


def test_ordering_puts_deeper_configuration_first_within_a_window():
    """Inside one renewal window, the deeper-configured account comes first."""
    days = TRIG["solo"]["renewal_within_days"] - 1
    rows = [row(account="Shallow", maturity_level="L2", active_users_30d=1, seats_active_30d=1,
                renewal_date=renews_in(days - 20)),
            row(account="Deep", maturity_level="L3", active_users_30d=1, seats_active_30d=1,
                renewal_date=renews_in(days))]
    ranked = sorted((d for d in triage(rows, RULES, AS_OF) if d.rank), key=lambda d: d.rank)
    assert [d.account for d in ranked] == ["Deep", "Shallow"]


def test_cli_handles_an_empty_export(tmp_path, capsys):
    """A header-only file is reported, not a crash."""
    path = tmp_path / "empty.csv"
    path.write_text(",".join(BASE) + "\n", encoding="utf-8")
    assert main([str(path), "--out", str(tmp_path / "out.csv")]) == 0
    assert "nothing to triage" in capsys.readouterr().out


def test_cli_writes_the_work_list(tmp_path):
    """The sample export runs end to end."""
    sample = Path(__file__).parent.parent / "data" / "sample_export.csv"
    out = tmp_path / "worklist.csv"
    assert main([str(sample), "--as-of", AS_OF.isoformat(), "--out", str(out)]) == 0
    assert "route" in out.read_text(encoding="utf-8").splitlines()[0]



HANDLING = RULES["handling"]
CASE_TRIGGERS = [name for name, t in TRIG.items() if "first_touch" in t and name != "seat_headroom"]


def test_every_case_trigger_names_who_handles_it():
    """Each trigger that can open a case says: automation, a CSM with AI, or a CSM without AI."""
    for name in CASE_TRIGGERS:
        assert TRIG[name].get("handled_by") in HANDLING["modes"], name


def test_ai_never_assists_the_triggers_the_policy_reserves_for_a_person():
    """Triggers listed under ai.never_assists are never worked with AI."""
    for name in RULES["ai"]["never_assists"]:
        assert TRIG[name]["handled_by"] != "CSM with AI", name


@pytest.mark.parametrize("fields,expected", [
    ({"nonrenewal_intent": "Y"}, TRIG["nonrenewal_intent"]["handled_by"]),
    ({"active_users_30d": 0, "seats_active_30d": 0, "days_since_last_review": 31,
      "renewal_date": renews_in(330)}, TRIG["dormant"]["handled_by"]),
    ({}, HANDLING["automated_route"]),
    ({"active_users_30d": 1, "seats_active_30d": 40}, HANDLING["hold_route"]),
    ({"active_users_30d": 60, "seats_active_30d": 50}, TRIG["seat_headroom"]["handled_by"]),
    ({"arr_usd": "9000"}, HANDLING["below_band"]),
    ({"success_manager": "Named CSM"}, HANDLING["above_band_or_named"]),
])
def test_each_route_carries_the_handler_from_the_policy(fields, expected):
    """The work list says who handles every row, taken from config, never decided in code."""
    assert run(**fields).handled_by == expected


def test_every_row_in_the_sample_has_a_handler():
    """No row leaves the engine without a handling mode."""
    rows = load_export(Path(__file__).parent.parent / "data" / "sample_export.csv")
    assert all(d.handled_by in HANDLING["modes"] for d in triage(rows, RULES, AS_OF))
