import copy
import pytest

from itertools import combinations

import factories


from entities.fencer import Fencer
from entities.tournament_entry import TournamentEntry
from poules.poule import Poule
from poules.poule_orders import POULE_BOUT_ORDER


# --- Constants ---
from constants import TOURNY_ID1, TOURNY_ID2


# --- Fixtures ---
@pytest.fixture
def entries(entry1, entry2, entry3, entry4, entry5, entry6, entry7):
    return (entry1, entry2, entry3, entry4, entry5, entry6, entry7)

@pytest.fixture
def poule(entries): 
    return Poule(1, 1, entries)


# --- Match Generation Tests ---
@pytest.mark.parametrize('size', [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
def test_poule_generate_matches(size):
    entries = factories.make_entries(size, TOURNY_ID1)

    poule = Poule(1, 1, entries)

    assert poule.size == size

    bout_order = POULE_BOUT_ORDER[poule.size]

    # Verify that all entry pairs are present exactly once in the generated matches
    expected_entry_pairs = {frozenset((entry1.id, entry2.id)) for entry1, entry2 in combinations(entries, 2)}
    generated_entry_pairs = {frozenset((match.entry1.id, match.entry2.id)) for match in poule.matches}

    assert len(poule.matches) == len(bout_order)
    assert generated_entry_pairs == expected_entry_pairs

    # Verify that the generated match sequence follows the official bout order
    for i, (fencer_number1, fencer_number2) in enumerate(bout_order):
        index1, index2 = fencer_number1 - 1, fencer_number2 - 1

        match = poule.matches[i]

        entry_pair = (poule.entries[index1], poule.entries[index2])

        assert match.match_number == i + 1
        assert match.match_index == i
        assert match.poule_number == poule.poule_number
        assert match.tournament_id == poule.tournament_id
        assert match.entries == entry_pair




# --- Predicate Method Tests ---
def test_poule_has_not_started_initially(poule):
    assert not poule.has_started()

def test_poule_has_started(poule):
    poule.record_match_score(5, 5, 2)

    assert poule.has_started()

def test_poule_is_not_complete_initially(poule):
    assert not poule.is_complete()

def test_poule_is_not_complete_with_remaining_matches(poule):
    for _ in range(poule.number_matches // 2):
        poule.record_on_piste_match_score(5, 2)

    assert not poule.is_complete()

def test_poule_is_complete(poule):
    for _ in range(poule.number_matches):
        poule.record_on_piste_match_score(3, 5)

    assert poule.is_complete()

def test_poule_has_entry_valid_returns_true(poule):
    valid_entry_in_poule = copy.deepcopy(poule.entries[0])

    assert poule.has_entry(valid_entry_in_poule)

def test_poule_has_entry_valid_returns_false(poule):
    valid_entry_not_in_poule = TournamentEntry(8, TOURNY_ID1, Fencer(8, 'Robert'))

    assert not poule.has_entry(valid_entry_not_in_poule)

@pytest.mark.parametrize('invalid_entry_type', [None, False, True, 0, 1.0, 'Rob', Fencer(8, 'Robert'), [], (), {}])
def test_poule_has_entry_invalid_entry_type(poule, invalid_entry_type):
    with pytest.raises(TypeError):
        poule.has_entry(invalid_entry_type)

def test_poule_has_entry_invalid_entry_wrong_tournament(poule):
    invalid_entry_wrong_tournament = TournamentEntry(8, TOURNY_ID2, Fencer(8, 'Robert'))

    with pytest.raises(ValueError):
        poule.has_entry(invalid_entry_wrong_tournament)
        

# --- Match Access Method Tests ---
@pytest.mark.parametrize('index', [0, 5, 10, 15, 20])
def test_poule_get_match_at(poule, index):
    assert poule.get_match_at(index) is poule.matches[index]

@pytest.mark.parametrize('invalid_index_type', [None, False, True, 0.0, 1.0, 'first', (), [], {}])
def test_poule_get_match_at_invalid_index_type(poule, invalid_index_type):
    with pytest.raises(TypeError):
        poule.get_match_at(invalid_index_type)

@pytest.mark.parametrize('invalid_index_value', [-100, -1, 21, 100])
def test_poule_get_match_at_invalid_index_value(poule, invalid_index_value):
    with pytest.raises(ValueError):
        poule.get_match_at(invalid_index_value)

def test_poule_get_on_piste_match_first_match(poule):
    on_piste_match = poule.get_on_piste_match() # First match in poule of 7: (1,4)

    assert on_piste_match.match_number == 1
    assert on_piste_match.poule_number == 1

    assert on_piste_match.entries == (poule.entries[0], poule.entries[3])

    assert not on_piste_match.is_complete()
    assert on_piste_match.winner is None

def test_poule_get_on_piste_match_match_done_out_of_order(poule):
    poule.record_match_score(5, 5, 2)

    assert poule.get_on_piste_match() is poule.matches[0]

def test_poule_get_on_piste_match_no_on_piste_match(poule):
    for _ in range(poule.number_matches):
        poule.record_on_piste_match_score(5, 0)

    assert poule.get_on_piste_match() is None

def test_poule_get_on_deck_match_first_on_deck_match(poule):
    # Second match in poule of 7: (2,5)
    next_match = poule.get_on_deck_match()

    assert next_match.match_number == 2
    assert next_match.poule_number == poule.poule_number

    assert next_match.entries == (poule.entries[1], poule.entries[4])

    assert not next_match.is_complete()
    assert next_match.winner is None

def test_poule_get_on_deck_match_skips_completed_match(poule):
    poule.record_match_score(1, 5, 0)

    assert poule.get_on_deck_match() is poule.matches[2]

def test_poule_get_on_deck_match_when_no_match_on_deck(poule):
    for _ in range(poule.number_matches - 1):
        poule.record_on_piste_match_score(5, 0)

    assert poule.get_on_deck_match() is None

def test_poule_get_on_deck_match_when_poule_complete(poule):
    for _ in range(poule.number_matches):
        poule.record_on_piste_match_score(5, 0)

    assert poule.get_on_deck_match() is None


# --- Match Result Recording Tests ---
def test_poule_record_match_score(poule):
    index = 5
    poule.record_match_score(index, 2, 3)
    
    # Check that first match is still incomplete
    match_1 = poule.matches[0]
    
    assert match_1.match_number == 1
    assert match_1.poule_number == 1

    assert match_1.score1 is None
    assert match_1.score2 is None
    
    assert not match_1.is_complete()
    assert match_1.winner is None
    
    # Check that the `index+1` match is complete
    match_2 = poule.matches[index]

    assert match_2.match_number == index + 1
    assert match_2.poule_number == 1
    
    assert match_2.score1 == 2
    assert match_2.score2 == 3
    
    assert match_2.is_complete()
    assert match_2.winner is match_2.entry2

@pytest.mark.parametrize('invalid_index_type', [None, False, True, 0.0, 1.0, 'first', [], (), {}])
def test_poule_record_match_score_invalid_index_type(poule, invalid_index_type):
    with pytest.raises(TypeError):
        poule.record_match_score(invalid_index_type, 5, 2)

@pytest.mark.parametrize('invalid_index_value', [-100, -1, 21, 100])
def test_poule_record_match_score_invalid_index_value(poule, invalid_index_value):
    with pytest.raises(ValueError):
        poule.record_match_score(invalid_index_value, 5, 2)

@pytest.mark.parametrize('invalid_score_type', [None, False, True, 0.0, 5.0, 'two', [], (), {}])
def test_poule_record_match_score_invalid_score_type(poule, invalid_score_type):
    index = 3
    
    with pytest.raises(TypeError):
        poule.record_match_score(index, invalid_score_type, 2)

    with pytest.raises(TypeError):
        poule.record_match_score(index, 5, invalid_score_type)

@pytest.mark.parametrize('invalid_score_value', [-100, -6, 6, 100])
def test_poule_record_match_score_invalid_score_value(poule, invalid_score_value):
    index = 5
    
    with pytest.raises(ValueError):
        poule.record_match_score(index, invalid_score_value, 2)

    with pytest.raises(ValueError):
        poule.record_match_score(index, 5, invalid_score_value)

def test_poule_record_on_piste_match_score(poule):  
    score1, score2 = 2, 5

    for i in range(poule.number_matches):
        # Check match info before recording the result
        match = poule.get_on_piste_match()
        
        assert match.match_number == i + 1
        assert match.match_index == i
        assert match.poule_number == 1
        assert match.tournament_id == TOURNY_ID1
        assert match.is_incomplete()
        assert match.winner is None

        # Record score
        poule.record_on_piste_match_score(score1=score1, score2=score2)

        # Check match info after recording the result
        match = poule.matches[i]
        
        assert match.match_number == i + 1
        assert match.match_index == i
        assert match.poule_number == 1
        assert match.tournament_id == TOURNY_ID1
        assert match.is_complete()
        assert match.winner is match.entry2

def test_poule_record_on_piste_match_score_invalid_poule_is_completed(poule):
    for _ in range(poule.number_matches):
        poule.record_on_piste_match_score(5,2)

    with pytest.raises(RuntimeError):
        poule.record_on_piste_match_score(5,2)

def test_poule_replace_with_score(poule):
    match_index = 10
    match = poule.matches[match_index]

    assert match.is_incomplete()
    assert match.forfeited_index is None
    assert match.score == (None, None)

    poule.record_match_score(10, 5, 2)

    assert match.is_complete()
    assert match.forfeited_index is None
    assert match.score == (5, 2)

    on_piste_match = poule.get_on_piste_match()
    on_deck_match = poule.get_on_deck_match()

    poule.replace_with_score(10, 2, 5)

    assert match.is_complete()
    assert match.forfeited_index is None
    assert match.score == (2, 5)

    assert poule.get_on_piste_match() is on_piste_match
    assert poule.get_on_deck_match() is on_deck_match

def test_poule_replace_with_score_invalid_preserves_original_score(poule):
    match_index = 1
    match = poule.get_match_at(match_index)

    original_score1, original_score2 = 5, 1
    poule.record_match_score(match_index, original_score1, original_score2)

    assert match.is_complete()
    assert match.score == (original_score1, original_score2)
    assert match.forfeited_index is None

    with pytest.raises(ValueError):
        score_to_win = poule.score_to_win
        poule.replace_with_score(match_index, score_to_win - 1, score_to_win + 1)

    assert match.is_complete()
    assert match.score == (original_score1, original_score2)
    assert match.forfeited_index is None

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_poule_replace_with_score_invalid_preserves_original_forfeit(poule, forfeiting_index):
    match_index = 7
    match = poule.get_match_at(match_index)

    losing_score, winning_score = 0, poule.score_to_win

    score1 = losing_score if forfeiting_index == 0 else winning_score
    score2 = losing_score if forfeiting_index == 1 else winning_score

    poule.record_forfeit(match_index, forfeiting_index)

    assert match.is_complete()
    assert match.score == (score1, score2)
    assert match.forfeited_index == forfeiting_index

    with pytest.raises(ValueError):
        poule.replace_with_score(match_index, losing_score - 1, winning_score + 1)

    assert match.is_complete()
    assert match.score == (score1, score2)
    assert match.forfeited_index == forfeiting_index

@pytest.mark.parametrize(('match_index', 'forfeiting_index'), [(0, 0), (3, 0), (5, 0), (0, 1), (3, 1), (5, 1)])
def test_poule_record_forfeit(poule, match_index, forfeiting_index):
    poule.record_forfeit(match_index, forfeiting_index)

    if match_index - 1 >= 0:
        assert poule.matches[match_index - 1].is_incomplete()

    forfeited_match = poule.matches[match_index]
    assert forfeited_match.is_complete()
    assert forfeited_match.forfeited_index == forfeiting_index

    if match_index + 1 < poule.number_matches:
        assert poule.matches[match_index + 1].is_incomplete()

def test_poule_replace_with_forfeit(poule):
    match_index = 5
    match = poule.matches[match_index]

    assert match.is_incomplete()
    assert match.forfeited_index is None
    assert match.score == (None, None)

    poule.record_match_score(5, 0, 5)

    assert match.is_complete()
    assert match.forfeited_index is None
    assert match.score == (0, 5)

    on_piste_match = poule.get_on_piste_match()
    on_deck_match = poule.get_on_deck_match()

    poule.replace_with_forfeit(5, 1)

    assert match.is_complete()
    assert match.is_forfeit()
    assert match.forfeited_index == 1
    assert match.score == (5, 0)

    assert poule.get_on_piste_match() is on_piste_match
    assert poule.get_on_deck_match() is on_deck_match

def test_poule_replace_with_forfeit_invalid_preserves_original_score(poule):
    match_index = 10
    match = poule.get_match_at(match_index)

    original_score1, original_score2 = 1, 5
    poule.record_match_score(match_index, original_score1, original_score2)

    assert match.is_complete()
    assert match.score == (original_score1, original_score2)
    assert match.forfeited_index is None

    with pytest.raises(TypeError):
        poule.replace_with_forfeit(match_index, 'Harry')

    assert match.is_complete()
    assert match.score == (original_score1, original_score2)
    assert match.forfeited_index is None

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_poule_replace_with_forfeit_invalid_preserves_original_forfeit(poule, forfeiting_index):
    match_index = 4
    match = poule.get_match_at(match_index)

    poule.record_forfeit(match_index, forfeiting_index)

    score1 = 0 if forfeiting_index == 0 else poule.score_to_win
    score2 = 0 if forfeiting_index == 1 else poule.score_to_win

    assert match.is_complete()
    assert match.score == (score1, score2)
    assert match.forfeited_index == forfeiting_index

    invalid_forfeiting_index = -1 if forfeiting_index == 0 else 2

    with pytest.raises(ValueError):
        poule.replace_with_forfeit(match_index, invalid_forfeiting_index)

    assert match.is_complete()
    assert match.score == (score1, score2)
    assert match.forfeited_index == forfeiting_index


# --- Result Calculation Tests ---
def test_poule_calculate_results_intermediate_result(poule):
    poule.record_on_piste_match_score(3, 5)

    results = poule.calculate_results()

    entry1_result = results.entry_results[0]
    entry4_result = results.entry_results[3]

    assert entry1_result.num_matches == 1
    assert entry1_result.num_victories == 0
    assert entry1_result.touches_scored == 3
    assert entry1_result.touches_received == 5

    assert entry4_result.num_matches == 1
    assert entry4_result.num_victories == 1
    assert entry4_result.touches_scored == 5
    assert entry4_result.touches_received == 3

def test_poule_calculate_results_entire_poule_complete(poule):
    # Match 1: (1,4)
    poule.record_on_piste_match_score(3, 5)

    # Match 2: (2,5)
    poule.record_on_piste_match_score(1, 5)

    # Match 3: (3,6)
    poule.record_on_piste_match_score(5, 4)

    # Match 4: (7,1)
    poule.record_on_piste_match_score(4, 5)

    # Match 5: (5,4)
    poule.record_on_piste_match_score(5, 2)

    # Match 6: (2,3)
    poule.record_on_piste_match_score(1, 5)

    # Match 7: (6,7)
    poule.record_on_piste_match_score(5, 2)

    # Match 8: (5,1)
    poule.record_on_piste_match_score(5, 4)

    # Match 9: (4,3)
    poule.record_on_piste_match_score(2, 5)

    # Match 10: (6,2)
    poule.record_on_piste_match_score(3, 5)

    # Match 11: (5,7)
    poule.record_on_piste_match_score(5, 3)

    # Match 12: (3,1)
    poule.record_on_piste_match_score(5, 0)

    # Match 13: (4,6)
    poule.record_on_piste_match_score(5, 2)

    # Match 14: (7,2)
    poule.record_on_piste_match_score(5, 1)

    # Match 15: (3,5)
    poule.record_on_piste_match_score(5, 3)

    # Match 16: (1,6)
    poule.record_on_piste_match_score(5, 1)

    # Match 17: (2,4)
    poule.record_on_piste_match_score(3, 5)

    # Match 18: (7,3)
    poule.record_on_piste_match_score(3, 5)

    # Match 19: (6,5)
    poule.record_on_piste_match_score(3, 5)

    # Match 20: (1,2)
    poule.record_on_piste_match_score(5, 1)

    # Match 21: (4,7)
    poule.record_on_piste_match_score(5, 2)

    # Check final results
    expected_final_results = (
        (3, 0.5, 22, 21, 1), 
        (1, 1 / 6, 12, 28, -16), 
        (6, 1.0, 30, 13, 17), 
        (4, 2 / 3, 24, 20, 4), 
        (5, 5 / 6, 28, 18, 10), 
        (1, 1 / 6, 18, 27, -9), 
        (1, 1 / 6, 19, 26, -7)
    )

    final_results = poule.calculate_results()

    assert final_results.poule_number == poule.poule_number
    assert final_results.tournament_id == poule.tournament_id

    for i, entry_result in enumerate(final_results.entry_results):
        assert entry_result.num_matches == 6
        assert entry_result.num_victories == expected_final_results[i][0]
        assert entry_result.victory_ratio == expected_final_results[i][1]
        assert entry_result.touches_scored == expected_final_results[i][2]
        assert entry_result.touches_received == expected_final_results[i][3]
        assert entry_result.indicator == expected_final_results[i][4]


    # Validate final ranking display name order
    expected_final_results_names = ('Hannah', 'Michael', 'Emily', 'John', 'Dave', 'Sarah', 'Steve')

    assert poule.calculate_ranked_results_display_names() == expected_final_results_names

def test_poule_calculate_ranked_results(entry1, entry2, entry3):
    entries = (entry1, entry2, entry3)

    poule = Poule(1, 1, entries)

    poule.record_on_piste_match_score(5,1)
    poule.record_on_piste_match_score(2,5)
    poule.record_on_piste_match_score(4,5)

    ranked_results = poule.calculate_ranked_results()

    assert tuple(result.display_name for result in ranked_results) == ('Hannah', 'John', 'Steve')

def test_poule_calculate_results_names_only_poule_of_size_three(entry1, entry2, entry3):
    entries = (entry1, entry2, entry3)

    poule = Poule(1, 1, entries)

    poule.record_on_piste_match_score(5,1)
    poule.record_on_piste_match_score(2,5)
    poule.record_on_piste_match_score(4,5)

    assert poule.calculate_ranked_results_display_names() == ('Hannah', 'John', 'Steve')


# --- Propagation of score_to_win Tests ---
def test_poule_score_to_win_propagation(entries):
    custom_score_to_win_value = 8

    poule = Poule(
        poule_number=1,
        stage_number=1,
        entries=entries,
        score_to_win=custom_score_to_win_value
    )

    assert poule.score_to_win == custom_score_to_win_value
    assert all(match.score_to_win == custom_score_to_win_value for match in poule.matches)

def test_poule_score_to_win_propagation_accepts_valid_scores(entries):
    custom_score_to_win_value = 10
    match_index = 6

    poule = Poule(
        poule_number=1,
        stage_number=1,
        entries=entries,
        score_to_win=custom_score_to_win_value
    )

    poule.record_match_score(match_index, custom_score_to_win_value-1, custom_score_to_win_value)
    match = poule.get_match_at(match_index)
    assert match.score == (custom_score_to_win_value - 1, custom_score_to_win_value)

def test_poule_score_to_win_propagation_rejects_invalid_scores(entries):
    custom_score_to_win_value = 3

    poule = Poule(
        poule_number=1,
        stage_number=1,
        entries=entries,
        score_to_win=custom_score_to_win_value
    )

    with pytest.raises(ValueError):
        poule.record_match_score(1, custom_score_to_win_value+1, custom_score_to_win_value-1)

    with pytest.raises(ValueError):
        poule.record_match_score(5, custom_score_to_win_value-1, custom_score_to_win_value+1)

    with pytest.raises(ValueError):
        poule.record_on_piste_match_score(custom_score_to_win_value, custom_score_to_win_value)
