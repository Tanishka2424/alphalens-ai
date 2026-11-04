import pytest

from app.services.consistency import (
    all_numbers, direction_differences, find_differences, key_numbers, number_differences, numbers_grounded,
)


def test_all_numbers_removes_commas_and_percent_signs():
    assert all_numbers("Sensex 22,850 and 5.51 times, up 8%") == {"22850", "5.51", "8"}


def test_key_numbers_skip_single_digits_unless_percent():
    assert set(key_numbers("Day 3 of Q2")) == set()
    assert set(key_numbers("shares jump 4%")) == {"4"}
    assert set(key_numbers("over 600 points")) == {"600"}


def test_empty_text_is_safe():
    assert all_numbers("") == set()
    assert key_numbers(None) == {}
    assert find_differences("", []) == []


def test_numbers_grounded_when_number_comes_from_claim_or_evidence():
    assert numbers_grounded("The claim says 20%, but the article reports 8%.", "rally 20% on order", ["rally over 8% on order"])
    assert numbers_grounded("Order worth Rs 1,140 crore.", "x", ["Rs 1,140 crore order"])


def test_numbers_grounded_rejects_an_invented_number():
    assert not numbers_grounded("The article reports over 800 points.", "jumps over 600 points", ["Sensex jumps over 500 points"])


def test_numbers_grounded_allows_numbers_from_the_publication_date():
    assert numbers_grounded("Published 2026-10-29.", "x", ["headline 2026-10-29T04:00:00Z"])


def test_numbers_grounded_ignores_plain_single_digits():
    assert numbers_grounded("It was day 3.", "x", ["headline"])


def test_number_difference_is_reported_when_claim_number_is_missing():
    notes = number_differences("Jupiter Wagons rally 20% on order", ["Jupiter Wagons shares rally 8% on order"])
    assert len(notes) == 1 and "20%" in notes[0]


def test_no_number_difference_when_numbers_match_even_with_commas():
    assert number_differences("Nifty above 22,850", ["Nifty above 22850 after Fed"]) == []


def test_percent_claim_with_single_digit_is_checked():
    assert number_differences("shares jump 4%", ["shares jump 5%"]) != []


def test_direction_difference_rise_vs_fall():
    notes = direction_differences("Sensex and Nifty fall early in trade", ["Sensex, Nifty rise in early trade"])
    assert len(notes) == 1 and "fall" in notes[0] and "rise" in notes[0]


def test_same_direction_gives_no_note():
    assert direction_differences("Sensex jumps 500 points", ["Sensex surged over 500 points"]) == []


def test_mixed_direction_in_evidence_gives_no_note():
    assert direction_differences("Sensex falls", ["Sensex rose while Trent fell"]) == []


def test_unlikely_vs_likely():
    notes = direction_differences("IPO allotment unlikely today", ["IPO allotment likely today"])
    assert len(notes) == 1 and "unlikely" in notes[0]


def test_rate_hike_vs_cut():
    assert direction_differences("RBI hikes repo rate", ["RBI cuts repo rate"]) != []


def test_find_differences_combines_direction_and_numbers():
    notes = find_differences("Sensex falls 600 points", ["Sensex rises 500 points"])
    assert len(notes) == 2


@pytest.mark.parametrize("claim,evidence", [
    ("Sensex jumps over 500 points after the Fed holds rates", "Sensex jumps over 500 points after Fed keeps rates unchanged"),
])
def test_matching_claim_has_no_differences(claim, evidence):
    assert find_differences(claim, [evidence]) == []