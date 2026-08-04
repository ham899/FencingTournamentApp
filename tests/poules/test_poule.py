import copy
import pytest
import random

from entities.fencer import Fencer
from entities.tournament_entry import TournamentEntry
from poules.poule import Poule


# --- Constants ---
FENCER_ID1, FENCER_DISPLAY_NAME1, ENTRY_ID1 = 1, 'John', 1

FENCER_ID2, FENCER_DISPLAY_NAME2, ENTRY_ID2 = 2, 'Steve', 2

FENCER_ID3, FENCER_DISPLAY_NAME3, ENTRY_ID3 = 3, 'Hannah', 3

FENCER_ID4, FENCER_DISPLAY_NAME4, ENTRY_ID4 = 4, 'Emily', 4

FENCER_ID5, FENCER_DISPLAY_NAME5, ENTRY_ID5 = 5, 'Michael', 5

FENCER_ID6, FENCER_DISPLAY_NAME6, ENTRY_ID6 = 6, 'Sarah', 6

FENCER_ID7, FENCER_DISPLAY_NAME7, ENTRY_ID7 = 7, 'Dave', 7

MATCH_ID1, MATCH_ID2, MATCH_ID3 = 1, 2, 3

POULE_NUMBER1, POULE_NUMBER2 = 1, 2

POULE_ID1, POULE_ID2 = 1, 2

TOURNY_ID1, TOURNY_ID2 = 1, 2

INVALID_ID_TYPES = [None, 'ABC', 1.0, True, ['F81C3'], (1,), {}]


# --- Fixtures ---
@pytest.fixture
def fencer1(): return Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)

@pytest.fixture
def fencer2(): return Fencer(FENCER_ID2, FENCER_DISPLAY_NAME2)

@pytest.fixture
def fencer3(): return Fencer(FENCER_ID3, FENCER_DISPLAY_NAME3)

@pytest.fixture
def fencer4(): return Fencer(FENCER_ID4, FENCER_DISPLAY_NAME4)

@pytest.fixture
def fencer5(): return Fencer(FENCER_ID5, FENCER_DISPLAY_NAME5)

@pytest.fixture
def fencer6(): return Fencer(FENCER_ID6, FENCER_DISPLAY_NAME6)

@pytest.fixture
def fencer7(): return Fencer(FENCER_ID7, FENCER_DISPLAY_NAME7)

@pytest.fixture
def entry1(fencer1): return TournamentEntry(ENTRY_ID1, TOURNY_ID1, fencer1)

@pytest.fixture
def entry2(fencer2): return TournamentEntry(ENTRY_ID2, TOURNY_ID1, fencer2)

@pytest.fixture
def entry3(fencer3): return TournamentEntry(ENTRY_ID3, TOURNY_ID1, fencer3)

@pytest.fixture
def entry4(fencer4): return TournamentEntry(ENTRY_ID4, TOURNY_ID1, fencer4)

@pytest.fixture
def entry5(fencer5): return TournamentEntry(ENTRY_ID5, TOURNY_ID1, fencer5)

@pytest.fixture
def entry6(fencer6): return TournamentEntry(ENTRY_ID6, TOURNY_ID1, fencer6)

@pytest.fixture
def entry7(fencer7): return TournamentEntry(ENTRY_ID7, TOURNY_ID1, fencer7)

@pytest.fixture
def entries(entry1, entry2, 
            entry3, entry4, 
            entry5, entry6, 
            entry7):
    return (entry1, entry2, 
            entry3, entry4, 
            entry5, entry6, 
            entry7)

@pytest.fixture
def poule(entries): return Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries)


# --- Initialization and Validation Tests ---
def test_poule_creation_valid(entries):
    poule = Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries)
    
    assert poule.id == POULE_ID1
    assert poule.tournament_id == TOURNY_ID1
    assert poule.poule_number == POULE_NUMBER1
    assert poule.entries == entries
    assert poule.size == len(entries)
    assert poule.matches is not None

    expected_number_matches = (len(entries) * (len(entries) - 1)) // 2
    assert poule.number_matches == expected_number_matches

@pytest.mark.parametrize('invalid_id_type', INVALID_ID_TYPES)
def test_poule_creation_invalid_id_type(entries, invalid_id_type):
    with pytest.raises(TypeError):
        Poule(invalid_id_type, TOURNY_ID1, POULE_NUMBER1, entries)

@pytest.mark.parametrize('invalid_id_value', [-10, -1, 0])
def test_poule_creation_invalid_id_value(entries, invalid_id_value):
    with pytest.raises(ValueError):
        Poule(invalid_id_value, TOURNY_ID1, POULE_NUMBER1, entries)

@pytest.mark.parametrize('invalid_tournament_id_type', INVALID_ID_TYPES)
def test_poule_creation_invalid_tournament_id_type(entries, invalid_tournament_id_type):
    with pytest.raises(TypeError):
        Poule(POULE_ID1, invalid_tournament_id_type, POULE_NUMBER1, entries)

@pytest.mark.parametrize('invalid_tournament_id_value', [-10, -1, 0])
def test_poule_creation_invalid_tournament_id_value(entries, invalid_tournament_id_value):
    with pytest.raises(ValueError):
        Poule(POULE_ID1, invalid_tournament_id_value, POULE_NUMBER1, entries)

@pytest.mark.parametrize('invalid_poule_number_type', [None, True, 1.0, 'one', (1,), [2], {}])
def test_poule_creation_invalid_poule_number_type(entries, invalid_poule_number_type):
    with pytest.raises(TypeError):
        Poule(POULE_ID1, TOURNY_ID1, invalid_poule_number_type, entries)

@pytest.mark.parametrize('invalid_poule_number_value', [-10, -1, 0])
def test_poule_creation_invalid_poule_number_value(entries, invalid_poule_number_value):
    with pytest.raises(ValueError):
        Poule(POULE_ID1, TOURNY_ID1, invalid_poule_number_value, entries)

@pytest.mark.parametrize('invalid_entries_type', [None, 'Harry', 0, 1.0, True, False])
def test_poule_creation_invalid_entries_type(invalid_entries_type):
    with pytest.raises(TypeError):
        Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, invalid_entries_type)

@pytest.mark.parametrize('invalid_entries_entry_type', [None, False, 0, 1.0, 'Harry', [], {}, Fencer(FENCER_ID2, FENCER_DISPLAY_NAME2)])
def test_poule_creation_invalid_entries_entry_type(entry1, entry3, invalid_entries_entry_type):
    list_with_invalid_entry_type = [entry1, invalid_entries_entry_type, entry3]
    with pytest.raises(TypeError):
        Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, list_with_invalid_entry_type)

def test_poule_creation_invalid_entry_does_not_belong_to_tournament(entry1, entry2, fencer3):
    entry_wrong_tournament = TournamentEntry(ENTRY_ID3, TOURNY_ID2, fencer3)
    list_with_invalid_entry_tournament_id = [entry1, entry2, entry_wrong_tournament]
    with pytest.raises(ValueError):
        Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, list_with_invalid_entry_tournament_id)

def test_poule_size_and_number_matches_properties(entries):
    poule1 = Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries[:2])
    assert poule1.size == 2
    assert poule1.number_matches == 1
    assert poule1.number_matches == len(poule1.matches)

    poule2 = Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries[:3])
    assert poule2.size == 3
    assert poule2.number_matches == 3
    assert poule2.number_matches == len(poule2.matches)

    poule3 = Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries[:4])
    assert poule3.size == 4
    assert poule3.number_matches == 6
    assert poule3.number_matches == len(poule3.matches)

    poule4 = Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries[:5])
    assert poule4.size == 5
    assert poule4.number_matches == 10
    assert poule4.number_matches == len(poule4.matches)

    poule5 = Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries[:6])
    assert poule5.size == 6
    assert poule5.number_matches == 15
    assert poule5.number_matches == len(poule5.matches)

    poule6 = Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries)
    assert poule6.size == 7
    assert poule6.number_matches == 21
    assert poule6.number_matches == len(poule6.matches)

def test_poule_equality(entries):
    poule1 = Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries)
    poule2 = Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries)
    assert poule1 == poule2

def test_poule_equality_after_modification(poule):
    poule_copy = copy.deepcopy(poule)
    poule.record_on_piste_match_result(5,3)
    assert poule == poule_copy

def test_poule_inequality_different_poules_same_tournament(entries):
    poule1 = Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries[0:3])
    poule2 = Poule(POULE_ID2, TOURNY_ID1, POULE_NUMBER2, entries[3:6])
    assert poule1 != poule2

def test_poule_inequality_different_tournaments(entries):
    poule1 = Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries)

    for entry in entries:
        entry.tournament_id = TOURNY_ID2
    
    poule2 = Poule(POULE_ID1, TOURNY_ID2, POULE_NUMBER1, entries)
    
    assert poule1 != poule2

def test_poule__create_match(poule):
    match = poule._create_match(match_id=MATCH_ID1, match_index=0, match_pair=(1, 2), entries=poule.entries)
    
    assert match.id == 1
    assert match.match_index == 0
    
    assert match.poule_id == POULE_ID1
    assert match.tournament_id == TOURNY_ID1
    
    assert match.entries == (poule.entries[0], poule.entries[1])
        
    assert match.is_incomplete()
    assert match.winner() is None

@pytest.mark.parametrize('invalid_match_id_type', INVALID_ID_TYPES)
def test_poule__create_match_invalid_match_id_type(poule, invalid_match_id_type):
    with pytest.raises(TypeError):
        poule._create_match(match_id=invalid_match_id_type, match_index=0, match_pair=(1, 2), entries=poule.entries)

@pytest.mark.parametrize('invalid_match_id_value', [-10, -1, 0])
def test_poule__create_match_invalid_match_id_value(poule, invalid_match_id_value):
    with pytest.raises(ValueError):
        poule._create_match(match_id=invalid_match_id_value, match_index=0, match_pair=(1, 2), entries=poule.entries)

@pytest.mark.parametrize('invalid_match_index_type', [None, 'second', 1.0, True, False, [], (1,), {}])
def test_poule__create_match_invalid_match_index_type(poule, invalid_match_index_type):
    with pytest.raises(TypeError):
        poule._create_match(match_id=MATCH_ID1, match_index=invalid_match_index_type, match_pair=(1, 2), entries=poule.entries)

@pytest.mark.parametrize('invalid_match_index_value', [-10, -1, 21, 22, 100]) # Assumes a poule of size 7 based on current fixture size
def test_poule__create_match_invalid_match_index_value(poule, invalid_match_index_value):
    with pytest.raises(ValueError):
        poule._create_match(match_id=MATCH_ID1, match_index=invalid_match_index_value, match_pair=(1, 2), entries=poule.entries)

@pytest.mark.parametrize('invalid_match_pair_type', [None, 'Ron vs. Bill', 0, 1.0, True, False, [], [1,2], {}])
def test_poule__create_match_invalid_match_pair_type(poule, invalid_match_pair_type):
    with pytest.raises(TypeError):
        poule._create_match(match_id=MATCH_ID1, match_index=0, match_pair=invalid_match_pair_type, entries=poule.entries)

@pytest.mark.parametrize('invalid_match_pair_invalid_element_type', [(None, 1), (1, 'Bob'), (1, 1.0), (False, True), ([], 1), (2, {}), ((1,), 2)])
def test_poule__create_match_invalid_match_tuple_pair_types(poule, invalid_match_pair_invalid_element_type):
    with pytest.raises(TypeError):
        poule._create_match(match_id=MATCH_ID1, match_index=0, match_pair=invalid_match_pair_invalid_element_type, entries=poule.entries)

@pytest.mark.parametrize('invalid_match_pair_length', [(1,), (1, 2, 3), (1, 2, 3, 4)])
def test_poule__create_match_invalid_match_tuple_pair_length(poule, invalid_match_pair_length):
    with pytest.raises(ValueError):
        poule._create_match(match_id=MATCH_ID1, match_index=0, match_pair=invalid_match_pair_length, entries=poule.entries)

@pytest.mark.parametrize('invalid_match_pair_values', [(0, 1), (1, 8), (2, 9), (99, 100), (3, -1), (-1, -2)]) # Assumes a poule of size 7 based on current fixture size
def test_poule__create_match_invalid_match_tuple_pair_values_out_of_bounds(poule, invalid_match_pair_values):
    with pytest.raises(ValueError):
        poule._create_match(match_id=MATCH_ID1, match_index=0, match_pair=invalid_match_pair_values, entries=poule.entries)

def test_poule_generate_matches(poule):
    assert poule.size == 7
    
    # Match 1: (1,4)
    assert poule.matches[0].entries == (poule.entries[0], poule.entries[3])

    # Match 2: (2,5)
    assert poule.matches[1].entries == (poule.entries[1], poule.entries[4])
    
    # Match 3: (3,6)
    assert poule.matches[2].entries == (poule.entries[2], poule.entries[5])

def test_poule_get_on_piste_match(poule):
    # First match in poule of 7: (1,4)
    on_piste_match = poule.get_on_piste_match()

    assert on_piste_match.id == 1
    assert on_piste_match.poule_id == POULE_ID1

    assert on_piste_match.entries == (poule.entries[0], poule.entries[3])

    assert not on_piste_match.is_complete()
    assert on_piste_match.winner() == None

    # Perform all matches
    for _ in range(poule.number_matches):
        poule.record_on_piste_match_result(5, 0)

    assert poule.get_on_piste_match() is None

def test_poule_get_on_deck_match(poule):
    # Second match in poule of 7: (2,5)
    next_match = poule.get_on_deck_match()

    assert next_match.id == 2
    assert next_match.poule_id == POULE_ID1

    assert next_match.entries == (poule.entries[1], poule.entries[4])

    assert not next_match.is_complete()
    assert next_match.winner() == None

    # Complete all matches up to the last match
    for _ in range(poule.number_matches - 1):
        poule.record_on_piste_match_result(5, 0)

    assert poule.get_on_deck_match() is None

def test_poule_record_match_result(poule):
    index = 5
    poule.record_match_result(index=index, score1=2, score2=3)
    
    # Check that first match is still incomplete
    match_1 = poule.matches[0]
    
    assert match_1.id == 1
    assert match_1.poule_id == POULE_ID1

    assert match_1.score1 is None
    assert match_1.score2 is None
    
    assert not match_1.is_complete()
    assert match_1.winner() is None
    
    # Check that the `index+1` match is complete
    match_2 = poule.matches[index]

    assert match_2.id == index + 1
    assert match_2.poule_id == POULE_ID1
    
    assert match_2.score1 == 2
    assert match_2.score2 == 3
    
    assert match_2.is_complete()
    assert match_2.winner() == match_2.entry2

def test_poule_record_match_result_invalid(poule):
    # Invalid match index
    with pytest.raises(TypeError):
        poule.record_match_result(index='ten', score1=5, score2=2)
    with pytest.raises(ValueError):
        poule.record_match_result(index=-1, score1=5, score2=2)
    with pytest.raises(ValueError):
        poule.record_match_result(index=poule.number_matches, score1=2, score2=4)
    
    # Invalid scores
    with pytest.raises(TypeError):
        poule.record_match_result(index=2, score1='five', score2=2)
    with pytest.raises(TypeError):
        poule.record_match_result(index=2, score1=5, score2='two')
    with pytest.raises(ValueError):
        poule.record_match_result(index=2, score1=-1, score2=5)
    with pytest.raises(ValueError):
        poule.record_match_result(index=1, score1=2, score2=-1)

def test_poule_record_current_match_result(poule):    
    for i in range(poule.number_matches):
        # Check match info before recording the result
        m = poule.get_on_piste_match()
        assert m.id == i+1
        assert m.match_index == i
        assert m.poule_id == POULE_ID1
        assert m.tournament_id == TOURNY_ID1
        assert m.is_incomplete()
        assert m.winner() is None

        # Record a score using randomization
        score1 = random.randint(0,5)
        score2 = random.randint(0,5)
        while score1 == score2:
            score2 = random.randint(0,5)
        poule.record_on_piste_match_result(score1=score1, score2=score2)

        # Check match info after recording the result
        m = poule.matches[i]
        assert m.id == i+1
        assert m.match_index == i
        assert m.poule_id == POULE_ID1
        assert m.tournament_id == TOURNY_ID1
        assert m.is_complete()
        assert m.winner() is not None

def test_poule_record_current_match_result_invalid_poule_completed(poule):
    for _ in range(poule.number_matches):
        poule.record_on_piste_match_result(5,2)

    with pytest.raises(RuntimeError):
        poule.record_on_piste_match_result(5,2)

def test_poule_is_complete(poule):
    # Complete all matches
    for _ in range(poule.number_matches):
        poule.record_on_piste_match_result(3,4)

    assert poule.is_complete() == True

def test_poule_calculate_results(entries):
    # Test a poule of 3
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries[:3])

    # Record first match: (1,2)
    poule.record_on_piste_match_result(score1=5, score2=1)

    # Get current poule results
    poule_results = poule.calculate_results()
    assert poule_results.poule_id == poule.id
    
    # Validate John's current results
    assert poule_results.entry_results[0].num_matches == 1
    assert poule_results.entry_results[0].num_victories == 1
    assert poule_results.entry_results[0].touches_scored == 5
    assert poule_results.entry_results[0].touches_received == 1
    # Validate Steve's current results
    assert poule_results.entry_results[1].num_matches == 1
    assert poule_results.entry_results[1].num_victories == 0
    assert poule_results.entry_results[1].touches_scored == 1
    assert poule_results.entry_results[1].touches_received == 5
    # Validate Hannah's current results
    assert poule_results.entry_results[2].num_matches == 0
    assert poule_results.entry_results[2].num_victories == 0
    assert poule_results.entry_results[2].touches_scored == 0
    assert poule_results.entry_results[2].touches_received == 0

    # Record second match: (1,3)
    poule.record_on_piste_match_result(score1=2, score2=5)

    # Get current poule results
    poule_results = poule.calculate_results()
    assert poule_results.poule_id == poule.id

    # Validate John's current results
    assert poule_results.entry_results[0].num_matches == 2
    assert poule_results.entry_results[0].num_victories == 1
    assert poule_results.entry_results[0].touches_scored == 7
    assert poule_results.entry_results[0].touches_received == 6
    # Validate Steve's current results
    assert poule_results.entry_results[1].num_matches == 1
    assert poule_results.entry_results[1].num_victories == 0
    assert poule_results.entry_results[1].touches_scored == 1
    assert poule_results.entry_results[1].touches_received == 5
    # Validate Hannah's current results
    assert poule_results.entry_results[2].num_matches == 1
    assert poule_results.entry_results[2].num_victories == 1
    assert poule_results.entry_results[2].touches_scored == 5
    assert poule_results.entry_results[2].touches_received == 2


    # Record final match: (2,3)
    poule.record_on_piste_match_result(score1=4, score2=5)

    # Get final results
    poule_results = poule.calculate_results()
    assert poule_results.poule_id == poule.id
    
    # Validate John's final results
    assert poule_results.entry_results[0].num_matches == 2
    assert poule_results.entry_results[0].num_victories == 1
    assert poule_results.entry_results[0].touches_scored == 7
    assert poule_results.entry_results[0].touches_received == 6
    # Validate Steve's final results
    assert poule_results.entry_results[1].num_matches == 2
    assert poule_results.entry_results[1].num_victories == 0
    assert poule_results.entry_results[1].touches_scored == 5
    assert poule_results.entry_results[1].touches_received == 10
    # Validate Hannah's final results
    assert poule_results.entry_results[2].num_matches == 2
    assert poule_results.entry_results[2].num_victories == 2
    assert poule_results.entry_results[2].touches_scored == 10
    assert poule_results.entry_results[2].touches_received == 6

    # Validate final ranking
    assert poule_results.ranked_results_display_names == ('Hannah', 'John', 'Steve')

def test_poule_calculate_results_names_only(entries):
    poule = Poule(id=POULE_ID1, tournament_id=TOURNY_ID1, poule_number=POULE_NUMBER1, entries=entries[:3])

    poule.record_on_piste_match_result(5,1)
    poule.record_on_piste_match_result(2,5)
    poule.record_on_piste_match_result(4,5)

    assert poule.calculate_ranked_results_display_names() == ('Hannah', 'John', 'Steve')