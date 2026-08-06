import pytest

import factories

from constants import POULE_ID1, TOURNY_ID1

from poules.results.poule_result import PouleResult


# --- Fixtures ---
@pytest.fixture
def entries(entry1, entry2, entry3, entry4, entry5, entry6, entry7):
    return (entry1, entry2, entry3, entry4, entry5, entry6, entry7)

@pytest.fixture
def incomplete_poule_matches(entries):
    return factories.make_poule_matches(entries, POULE_ID1, TOURNY_ID1)

@pytest.fixture
def partially_completed_poule_matches(entries):
    match_scores = (
        (3,5), (1,5), (5,4), (4,5), (5,2), (1,5), (5,2),
        (5,4), (2,5)
    )

    return factories.make_poule_matches(entries, POULE_ID1, TOURNY_ID1, scores=match_scores)
    
@pytest.fixture
def completed_poule_matches(entries):
    match_scores = (
        (3,5), (1,5), (5,4), (4,5), (5,2), (1,5), (5,2),
        (5,4), (2,5), (3,5), (5,3), (5,0), (5,2), (5,1), 
        (5,3), (5,1), (3,5), (3,5), (3,5), (5,1), (5,2)
    )

    return factories.make_poule_matches(entries, POULE_ID1, TOURNY_ID1, scores=match_scores)


# --- Tests ---
def test_poule_result_creation_valid_incomplete_matches(entries, incomplete_poule_matches):
    result = PouleResult(entries, incomplete_poule_matches, POULE_ID1, TOURNY_ID1)

    assert result.entries == entries

    for i in range(len(entries)):
        assert result.entry_results[i].num_matches == 0
        assert result.entry_results[i].num_victories == 0
        assert result.entry_results[i].victory_ratio == 0.0
        assert result.entry_results[i].touches_scored == 0
        assert result.entry_results[i].touches_received == 0
        assert result.entry_results[i].indicator == 0

def test_poule_result_ranked_results_incomplete_matches(entries, incomplete_poule_matches):
    result = PouleResult(entries, incomplete_poule_matches, POULE_ID1, TOURNY_ID1)

    expected_results = (result.entry_results[6], 
                        result.entry_results[3], 
                        result.entry_results[2], 
                        result.entry_results[0], 
                        result.entry_results[4], 
                        result.entry_results[5], 
                        result.entry_results[1])
    
    assert result.ranked_results == expected_results

def test_poule_result_ranked_results_display_names_property_incomplete_matches(entries, incomplete_poule_matches):
    result = PouleResult(entries, incomplete_poule_matches, POULE_ID1, TOURNY_ID1)
    
    assert result.ranked_results_display_names == ('Dave', 'Emily', 'Hannah', 'John', 'Michael', 'Sarah', 'Steve')

def test_poule_result_creation_valid_partially_completed_matches(entries, partially_completed_poule_matches):
    result = PouleResult(entries, partially_completed_poule_matches, POULE_ID1, TOURNY_ID1)

    assert result.entries == entries

    assert result.entry_results[0].num_matches == 3
    assert result.entry_results[0].num_victories == 1
    assert result.entry_results[0].victory_ratio == 1 / 3
    assert result.entry_results[0].touches_scored == 12
    assert result.entry_results[0].touches_received == 14
    assert result.entry_results[0].indicator == -2

    assert result.entry_results[1].num_matches == 2
    assert result.entry_results[1].num_victories == 0
    assert result.entry_results[1].victory_ratio == 0.0
    assert result.entry_results[1].touches_scored == 2
    assert result.entry_results[1].touches_received == 10
    assert result.entry_results[1].indicator == -8

    assert result.entry_results[2].num_matches == 3
    assert result.entry_results[2].num_victories == 3
    assert result.entry_results[2].victory_ratio == 1.0
    assert result.entry_results[2].touches_scored == 15
    assert result.entry_results[2].touches_received == 7
    assert result.entry_results[2].indicator == 8

    assert result.entry_results[3].num_matches == 3
    assert result.entry_results[3].num_victories == 1
    assert result.entry_results[3].victory_ratio == 1 / 3
    assert result.entry_results[3].touches_scored == 9
    assert result.entry_results[3].touches_received == 13
    assert result.entry_results[3].indicator == -4

    assert result.entry_results[4].num_matches == 3
    assert result.entry_results[4].num_victories == 3
    assert result.entry_results[4].victory_ratio == 1.0
    assert result.entry_results[4].touches_scored == 15
    assert result.entry_results[4].touches_received == 7
    assert result.entry_results[4].indicator == 8

    assert result.entry_results[5].num_matches == 2
    assert result.entry_results[5].num_victories == 1
    assert result.entry_results[5].victory_ratio == 0.5
    assert result.entry_results[5].touches_scored == 9
    assert result.entry_results[5].touches_received == 7
    assert result.entry_results[5].indicator == 2

    assert result.entry_results[6].num_matches == 2
    assert result.entry_results[6].num_victories == 0
    assert result.entry_results[6].victory_ratio == 0.0
    assert result.entry_results[6].touches_scored == 6
    assert result.entry_results[6].touches_received == 10
    assert result.entry_results[6].indicator == -4

def test_poule_result_ranked_results_property_partially_completed_matches(entries, partially_completed_poule_matches):
    result = PouleResult(entries, partially_completed_poule_matches, POULE_ID1, TOURNY_ID1)

    expected_results = (result.entry_results[2], 
                        result.entry_results[4], 
                        result.entry_results[5], 
                        result.entry_results[0], 
                        result.entry_results[3], 
                        result.entry_results[6], 
                        result.entry_results[1])
    
    assert result.ranked_results == expected_results

def test_poule_result_ranked_results_display_names_property_partially_completed_matches(entries, partially_completed_poule_matches):
    result = PouleResult(entries, partially_completed_poule_matches, POULE_ID1, TOURNY_ID1)
    
    assert result.ranked_results_display_names == ('Hannah', 'Michael', 'Sarah', 'John', 'Emily', 'Dave', 'Steve')

def test_poule_result_creation_valid_completed_matches(entries, completed_poule_matches):
    result = PouleResult(entries, completed_poule_matches, POULE_ID1, TOURNY_ID1)

    assert result.entries == entries

    assert result.entry_results[0].num_matches == 6
    assert result.entry_results[0].num_victories == 3
    assert result.entry_results[0].victory_ratio == 3 / 6
    assert result.entry_results[0].touches_scored == 22
    assert result.entry_results[0].touches_received == 21
    assert result.entry_results[0].indicator == 1

    assert result.entry_results[1].num_matches == 6
    assert result.entry_results[1].num_victories == 1
    assert result.entry_results[1].victory_ratio == 1 / 6
    assert result.entry_results[1].touches_scored == 12
    assert result.entry_results[1].touches_received == 28
    assert result.entry_results[1].indicator == -16

    assert result.entry_results[2].num_matches == 6
    assert result.entry_results[2].num_victories == 6
    assert result.entry_results[2].victory_ratio == 6 / 6
    assert result.entry_results[2].touches_scored == 30
    assert result.entry_results[2].touches_received == 13
    assert result.entry_results[2].indicator == 17

    assert result.entry_results[3].num_matches == 6
    assert result.entry_results[3].num_victories == 4
    assert result.entry_results[3].victory_ratio == 4 / 6
    assert result.entry_results[3].touches_scored == 24
    assert result.entry_results[3].touches_received == 20
    assert result.entry_results[3].indicator == 4

    assert result.entry_results[4].num_matches == 6
    assert result.entry_results[4].num_victories == 5
    assert result.entry_results[4].victory_ratio == 5 / 6
    assert result.entry_results[4].touches_scored == 28
    assert result.entry_results[4].touches_received == 18
    assert result.entry_results[4].indicator == 10

    assert result.entry_results[5].num_matches == 6
    assert result.entry_results[5].num_victories == 1
    assert result.entry_results[5].victory_ratio == 1 / 6
    assert result.entry_results[5].touches_scored == 18
    assert result.entry_results[5].touches_received == 27
    assert result.entry_results[5].indicator == -9

    assert result.entry_results[6].num_matches == 6
    assert result.entry_results[6].num_victories == 1
    assert result.entry_results[6].victory_ratio == 1 / 6
    assert result.entry_results[6].touches_scored == 19
    assert result.entry_results[6].touches_received == 26
    assert result.entry_results[6].indicator == -7

def test_poule_result_ranked_results_property_completed_matches(entries, completed_poule_matches):
    result = PouleResult(entries, completed_poule_matches, POULE_ID1, TOURNY_ID1)

    expected_results = (result.entry_results[2], 
                        result.entry_results[4], 
                        result.entry_results[3], 
                        result.entry_results[0], 
                        result.entry_results[6], 
                        result.entry_results[5], 
                        result.entry_results[1])
    
    assert result.ranked_results == expected_results

def test_poule_result_ranked_results_display_names_property_completed_matches(entries, completed_poule_matches):
    result = PouleResult(entries, completed_poule_matches, POULE_ID1, TOURNY_ID1)
    
    assert result.ranked_results_display_names == ('Hannah', 'Michael', 'Emily', 'John', 'Dave', 'Sarah', 'Steve')

def test_poule_result_creation_valid_completed_matches_reversed_match_order(entries, completed_poule_matches):
    reversed_matches = tuple(reversed(completed_poule_matches))

    result = PouleResult(entries, reversed_matches, POULE_ID1, TOURNY_ID1)

    assert result.entries == entries

    assert result.entry_results[0].num_matches == 6
    assert result.entry_results[0].num_victories == 3
    assert result.entry_results[0].victory_ratio == 3 / 6
    assert result.entry_results[0].touches_scored == 22
    assert result.entry_results[0].touches_received == 21
    assert result.entry_results[0].indicator == 1

    assert result.entry_results[1].num_matches == 6
    assert result.entry_results[1].num_victories == 1
    assert result.entry_results[1].victory_ratio == 1 / 6
    assert result.entry_results[1].touches_scored == 12
    assert result.entry_results[1].touches_received == 28
    assert result.entry_results[1].indicator == -16

    assert result.entry_results[2].num_matches == 6
    assert result.entry_results[2].num_victories == 6
    assert result.entry_results[2].victory_ratio == 6 / 6
    assert result.entry_results[2].touches_scored == 30
    assert result.entry_results[2].touches_received == 13
    assert result.entry_results[2].indicator == 17

    assert result.entry_results[3].num_matches == 6
    assert result.entry_results[3].num_victories == 4
    assert result.entry_results[3].victory_ratio == 4 / 6
    assert result.entry_results[3].touches_scored == 24
    assert result.entry_results[3].touches_received == 20
    assert result.entry_results[3].indicator == 4

    assert result.entry_results[4].num_matches == 6
    assert result.entry_results[4].num_victories == 5
    assert result.entry_results[4].victory_ratio == 5 / 6
    assert result.entry_results[4].touches_scored == 28
    assert result.entry_results[4].touches_received == 18
    assert result.entry_results[4].indicator == 10

    assert result.entry_results[5].num_matches == 6
    assert result.entry_results[5].num_victories == 1
    assert result.entry_results[5].victory_ratio == 1 / 6
    assert result.entry_results[5].touches_scored == 18
    assert result.entry_results[5].touches_received == 27
    assert result.entry_results[5].indicator == -9

    assert result.entry_results[6].num_matches == 6
    assert result.entry_results[6].num_victories == 1
    assert result.entry_results[6].victory_ratio == 1 / 6
    assert result.entry_results[6].touches_scored == 19
    assert result.entry_results[6].touches_received == 26
    assert result.entry_results[6].indicator == -7

def test_poule_result_ranked_results_uses_touches_scored_tiebreaker(entries):
    entries = factories.make_entries(n=3, tournament_id=TOURNY_ID1, initial_seed=True)
    
    match_scores = ((5, 3), (2, 5), (5, 4))

    matches = factories.make_poule_matches(
        entries,
        POULE_ID1,
        TOURNY_ID1,
        scores=match_scores
    )

    result = PouleResult(entries, matches, POULE_ID1, TOURNY_ID1)
    assert result.entry_results[0].victory_ratio == 0.5
    assert result.entry_results[0].indicator == -1
    assert result.entry_results[0].touches_scored == 7

    assert result.entry_results[1].victory_ratio == 0.5
    assert result.entry_results[1].indicator == -1
    assert result.entry_results[1].touches_scored == 8

    assert result.entry_results[2].victory_ratio == 0.5
    assert result.entry_results[2].indicator == 2
    assert result.entry_results[2].touches_scored == 9

    expected_results = (
        result.entry_results[2],
        result.entry_results[1],
        result.entry_results[0]
    )

    assert result.ranked_results == expected_results

@pytest.mark.parametrize('forfeiting_index', (0, 1))
def test_poule_result_calculates_forfeited_match(entries, incomplete_poule_matches, forfeiting_index):
    forfeited_match = incomplete_poule_matches[0]
    forfeited_match.forfeit(forfeiting_index)

    result = PouleResult(entries, incomplete_poule_matches, POULE_ID1, TOURNY_ID1)

    winner_entry = forfeited_match.entry_at_index(1 - forfeiting_index)
    loser_entry = forfeited_match.entry_at_index(forfeiting_index)
    
    winner_result = result.entry_results[entries.index(winner_entry)]
    loser_result = result.entry_results[entries.index(loser_entry)]

    assert winner_result.num_matches == 1
    assert winner_result.num_victories == 1
    assert winner_result.victory_ratio == 1.0
    assert winner_result.touches_scored == forfeited_match.score_to_win
    assert winner_result.touches_received == 0
    assert winner_result.indicator == forfeited_match.score_to_win

    assert loser_result.num_matches == 1
    assert loser_result.num_victories == 0
    assert loser_result.victory_ratio == 0.0
    assert loser_result.touches_scored == 0
    assert loser_result.touches_received == forfeited_match.score_to_win
    assert loser_result.indicator == -forfeited_match.score_to_win

    for entry_result in result.entry_results:
        if entry_result not in (winner_result, loser_result):
            assert entry_result.num_matches == 0
            assert entry_result.num_victories == 0
            assert entry_result.touches_scored == 0
            assert entry_result.touches_received == 0

def test_poule_result_is_snapshot_of_matches(entries, incomplete_poule_matches):
    original_result = PouleResult(entries, incomplete_poule_matches, POULE_ID1, TOURNY_ID1)
    
    completed_match = incomplete_poule_matches[0]

    completed_match.record_score(5, 3)

    new_result = PouleResult(entries, incomplete_poule_matches, POULE_ID1, TOURNY_ID1)

    original_entry1_result = original_result.entry_results[entries.index(completed_match.entry1)]
    original_entry2_result = original_result.entry_results[entries.index(completed_match.entry2)]

    new_entry1_result = new_result.entry_results[entries.index(completed_match.entry1)]
    new_entry2_result = new_result.entry_results[entries.index(completed_match.entry2)]

    assert original_entry1_result.num_matches == 0
    assert original_entry1_result.num_victories == 0
    assert original_entry1_result.touches_scored == 0
    assert original_entry1_result.touches_received == 0

    assert original_entry2_result.num_matches == 0
    assert original_entry2_result.num_victories == 0
    assert original_entry2_result.touches_scored == 0
    assert original_entry2_result.touches_received == 0

    assert new_entry1_result.num_matches == 1
    assert new_entry1_result.num_victories == 1
    assert new_entry1_result.touches_scored == 5
    assert new_entry1_result.touches_received == 3

    assert new_entry2_result.num_matches == 1
    assert new_entry2_result.num_victories == 0
    assert new_entry2_result.touches_scored == 3
    assert new_entry2_result.touches_received == 5