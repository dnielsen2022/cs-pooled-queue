from pathlib import Path

import pytest

from pooled_queue.engine import decide, load_rules, triage

RULES = load_rules(Path(__file__).parent.parent / "config" / "queue_rules.yaml")

BASE = {
    "account": "Test Co", "arr_usd": "18000", "plan": "Pro", "maturity_level": "L3", "seats_purchased": "50",
    "seats_active_30d": "40", "active_users_30d": "35", "days_since_last_review": "1", "repos_connected": "10",
    "renewal_date": "2027-03-01", "term": "annual", "nonrenewal_intent": "N", "cancellation_started": "N",
    "support_tickets_30d": "0", "suggestion_acceptance_30d_pct": "50", "days_since_signup": "400",
    "success_manager": "",
}


def row(**kw):
    r = dict(BASE)
    r.update({k: str(v) for k, v in kw.items()})
    return r


def test_healthy_account_is_left_to_automation():
    assert decide(row(), RULES).route == "Automated"


def test_nonrenewal_intent_is_always_p1_even_with_bad_data():
    d = decide(row(nonrenewal_intent="Y", days_since_last_review=500), RULES)
    assert (d.route, d.priority) == ("Case", "P1")
    assert d.data_flags  # still flagged, never dropped


def test_dormant_l3_is_p1_even_far_from_renewal():
    d = decide(row(active_users_30d=0, seats_active_30d=0, renewal_date="2027-09-01"), RULES)
    assert (d.route, d.priority) == ("Case", "P1")


def test_l1_with_nobody_active_is_stalled_not_dormant():
    d = decide(row(maturity_level="L1", active_users_30d=0, seats_active_30d=0, renewal_date="2026-12-01"), RULES)
    assert "Dormant" not in d.signals
    assert d.priority == "P3"


@pytest.mark.parametrize("renewal,expected", [("2027-01-15", "Case"), ("2027-06-01", "Automated")])
def test_solo_uses_the_150_day_window(renewal, expected):
    d = decide(row(maturity_level="L2", active_users_30d=1, seats_active_30d=1, renewal_date=renewal), RULES)
    assert d.route == expected


def test_monthly_terms_are_always_inside_the_window():
    d = decide(row(maturity_level="L2", active_users_30d=1, seats_active_30d=1, term="monthly",
                   renewal_date="2027-09-01"), RULES)
    assert d.route == "Case"


@pytest.mark.parametrize("arr,manager", [("9000", ""), ("32000", ""), ("20000", "Named CSM")])
def test_out_of_band_rows_are_removed(arr, manager):
    assert decide(row(arr_usd=arr, success_manager=manager), RULES).route == "Remove"


def test_seat_headroom_goes_to_the_ae():
    d = decide(row(active_users_30d=60, seats_active_30d=50), RULES)
    assert d.route == "AE"


def test_contradictions_are_flagged():
    d = decide(row(active_users_30d=1, seats_active_30d=40), RULES)
    assert any("active seats" in f for f in d.data_flags)
    d = decide(row(days_since_last_review=20, days_since_signup=10), RULES)
    assert any("impossible" in f for f in d.data_flags)


def test_ordering_puts_deeper_config_first_within_a_window():
    rows = [row(account="Shallow", maturity_level="L2", active_users_30d=1, seats_active_30d=1, renewal_date="2027-01-08"),
            row(account="Deep", maturity_level="L3", active_users_30d=1, seats_active_30d=1, renewal_date="2027-02-02")]
    ranked = sorted((d for d in triage(rows, RULES) if d.rank), key=lambda d: d.rank)
    assert [d.account for d in ranked] == ["Deep", "Shallow"]
