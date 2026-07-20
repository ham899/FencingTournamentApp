import pytest
import copy
import random

from entities.fencer import Fencer
from entities.tournament_entry import TournamentEntry
from poules.poule import Poule


# --- Constants ---
FENCER_ID1 = 1
FENCER_DISPLAY_NAME1 = 'John'
ENTRY_ID1 = 1

FENCER_ID2 = 2
FENCER_DISPLAY_NAME2 = 'Steve'
ENTRY_ID2 = 2

FENCER_ID3 = 3
FENCER_DISPLAY_NAME3 = 'Hannah'
ENTRY_ID3 = 3

FENCER_ID4 = 4
FENCER_DISPLAY_NAME4 = 'Emily'
ENTRY_ID4 = 4

FENCER_ID5 = 5
FENCER_DISPLAY_NAME5 = 'Michael'
ENTRY_ID5 = 5

FENCER_ID6 = 6
FENCER_DISPLAY_NAME6 = 'Sarah'
ENTRY_ID6 = 6

FENCER_ID7 = 7
FENCER_DISPLAY_NAME7 = 'Dave'
ENTRY_ID7 = 7

MATCH_ID = 1
POULE_ID = 1
POULE_NUMBER = 1
TOURNY_ID = 1

INVALID_ID_TYPES = [None, 'ABC', 1.0, True, [], (1,), {}]
DIFFERENT_POULE_ID = 2
DIFFERENT_TOURNY_ID = 2


# --- Fixtures ---
@pytest.fixture
def fencer1():
    return Fencer(id=FENCER_ID1, display_name=FENCER_DISPLAY_NAME1)

@pytest.fixture
def fencer2():
    return Fencer(id=FENCER_ID2, display_name=FENCER_DISPLAY_NAME2)

@pytest.fixture
def fencer3():
    return Fencer(id=FENCER_ID3, display_name=FENCER_DISPLAY_NAME3)

@pytest.fixture
def fencer4():
    return Fencer(id=FENCER_ID4, display_name=FENCER_DISPLAY_NAME4)

@pytest.fixture
def fencer5():
    return Fencer(id=FENCER_ID5, display_name=FENCER_DISPLAY_NAME5)

@pytest.fixture
def fencer6():
    return Fencer(id=FENCER_ID6, display_name=FENCER_DISPLAY_NAME6)

@pytest.fixture
def fencer7():
    return Fencer(id=FENCER_ID7, display_name=FENCER_DISPLAY_NAME7)

@pytest.fixture
def entry1(fencer1):
    return TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer1)

@pytest.fixture
def entry2(fencer2):
    return TournamentEntry(id=ENTRY_ID2, tournament_id=TOURNY_ID, fencer=fencer2)

@pytest.fixture
def entry3(fencer3):
    return TournamentEntry(id=ENTRY_ID3, tournament_id=TOURNY_ID, fencer=fencer3)

@pytest.fixture
def entry4(fencer4):
    return TournamentEntry(id=ENTRY_ID4, tournament_id=TOURNY_ID, fencer=fencer4)

@pytest.fixture
def entry5(fencer5):
    return TournamentEntry(id=ENTRY_ID5, tournament_id=TOURNY_ID, fencer=fencer5)

@pytest.fixture
def entry6(fencer6):
    return TournamentEntry(id=ENTRY_ID6, tournament_id=TOURNY_ID, fencer=fencer6)

@pytest.fixture
def entry7(fencer7):
    return TournamentEntry(id=ENTRY_ID7, tournament_id=TOURNY_ID, fencer=fencer7)

@pytest.fixture
def entries(entry1, entry2, entry3, entry4, entry5, entry6, entry7):
    return [entry1, entry2, entry3, entry4, entry5, entry6, entry7]

@pytest.fixture
def poule(entries):
    return Poule(POULE_ID, TOURNY_ID, POULE_NUMBER, entries)


# --- Initialization and Validation Tests ---
def test_poule_creation_valid(entries):
    poule = Poule(POULE_ID, TOURNY_ID, POULE_NUMBER, entries)
    assert poule.id == POULE_ID
    assert poule.tournament_id == TOURNY_ID
    assert poule.poule_number == POULE_NUMBER
    assert poule.entries == entries
    assert poule.size == len(entries)
    assert poule.matches is not None

@pytest.mark.parametrize('invalid_id_type', INVALID_ID_TYPES)
def test_poule_creation_invalid_id_type(entries, invalid_id_type):
    with pytest.raises(TypeError):
        Poule(invalid_id_type, TOURNY_ID, POULE_NUMBER, entries)

@pytest.mark.parametrize('invalid_id_value', [-100, -10, -1, 0])
def test_poule_creation_invalid_id_value(entries, invalid_id_value):
    with pytest.raises(ValueError):
        Poule(invalid_id_value, TOURNY_ID, POULE_NUMBER, entries)

@pytest.mark.parametrize('invalid_tournament_id_type', INVALID_ID_TYPES)
def test_poule_creation_invalid_tournament_id_type(entries, invalid_tournament_id_type):
    with pytest.raises(TypeError):
        Poule(POULE_ID, invalid_tournament_id_type, POULE_NUMBER, entries)

@pytest.mark.parametrize('invalid_tournament_id_value', [-100, -10, -1, 0])
def test_poule_creation_invalid_tournament_id_value(entries, invalid_tournament_id_value):
    with pytest.raises(ValueError):
        Poule(POULE_ID, invalid_tournament_id_value, POULE_NUMBER, entries)

@pytest.mark.parametrize('invalid_poule_number_type', [None, True, 1.0, 'one', (1,), [], {}])
def test_poule_creation_invalid_poule_number_type(entries, invalid_poule_number_type):
    with pytest.raises(TypeError):
        Poule(POULE_ID, TOURNY_ID, invalid_poule_number_type, entries)

@pytest.mark.parametrize('invalid_poule_number_value', [-100, -10, -1, 0])
def test_poule_creation_invalid_poule_number_value(entries, invalid_poule_number_value):
    with pytest.raises(ValueError):
        Poule(POULE_ID, TOURNY_ID, invalid_poule_number_value, entries)

@pytest.mark.parametrize('invalid_entries_list_type', [None, 'Harry', 0, 1.0, True, False, {}, (1,)])
def test_poule_creation_invalid_entries_type(invalid_entries_list_type):
    with pytest.raises(TypeError):
        Poule(POULE_ID, TOURNY_ID, POULE_NUMBER, invalid_entries_list_type)

@pytest.mark.parametrize('invalid_entry_type', [None, False, 0, 1.0, 'Harry', [], {}, Fencer(FENCER_ID2, FENCER_DISPLAY_NAME2)])
def test_poule_creation_invalid_element_entry_type(entry1, entry3, invalid_entry_type):
    list_with_invalid_entry_type = [entry1, invalid_entry_type, entry3]
    with pytest.raises(TypeError):
        Poule(POULE_ID, TOURNY_ID, POULE_NUMBER, list_with_invalid_entry_type)

def test_poule_creation_invalid_entry_does_not_belong_to_tournament(entry1, entry2, fencer3):
    entry_wrong_tournament = TournamentEntry(ENTRY_ID3, DIFFERENT_TOURNY_ID, fencer3)
    list_with_invalid_entry_tournament_id = [entry1, entry2, entry_wrong_tournament]
    with pytest.raises(ValueError):
        Poule(POULE_ID, TOURNY_ID, POULE_NUMBER, list_with_invalid_entry_tournament_id)

def test_poule_size_and_number_matches_properties(entries):
    poule1 = Poule(id=POULE_ID, tournament_id=TOURNY_ID, poule_number=POULE_NUMBER, entries=entries[:2])
    assert poule1.size == 2
    assert poule1.number_matches == 1
    assert poule1.number_matches == len(poule1.matches)
    
    poule2 = Poule(id=POULE_ID, tournament_id=TOURNY_ID, poule_number=POULE_NUMBER, entries=entries[:3])
    assert poule2.size == 3
    assert poule2.number_matches == 3
    assert poule2.number_matches == len(poule2.matches)
    
    poule3 = Poule(id=POULE_ID, tournament_id=TOURNY_ID, poule_number=POULE_NUMBER, entries=entries[:4])
    assert poule3.size == 4
    assert poule3.number_matches == 6
    assert poule3.number_matches == len(poule3.matches)
    
    poule4 = Poule(id=POULE_ID, tournament_id=TOURNY_ID, poule_number=POULE_NUMBER, entries=entries[:5])
    assert poule4.size == 5
    assert poule4.number_matches == 10
    assert poule4.number_matches == len(poule4.matches)
    
    poule5 = Poule(id=POULE_ID, tournament_id=TOURNY_ID, poule_number=POULE_NUMBER, entries=entries[:6])
    assert poule5.size == 6
    assert poule5.number_matches == 15
    assert poule5.number_matches == len(poule5.matches)
    
    poule6 = Poule(id=POULE_ID, tournament_id=TOURNY_ID, poule_number=POULE_NUMBER, entries=entries)
    assert poule6.size == 7
    assert poule6.number_matches == 21
    assert poule6.number_matches == len(poule6.matches)

def test_poule_equality(entries, poule):
    poule2 = Poule(POULE_ID, TOURNY_ID, POULE_NUMBER, entries)
    assert poule == poule2

def test_poule_equality_after_modification(poule):
    poule_copy = copy.deepcopy(poule)
    poule.record_current_match_result(5,3)
    assert poule == poule_copy

def test_poule_inequality_different_poules_same_tournament(entries):
    poule1 = Poule(id=POULE_ID, tournament_id=TOURNY_ID, poule_number=POULE_NUMBER, entries=entries)
    poule2 = Poule(id=DIFFERENT_POULE_ID, tournament_id=TOURNY_ID, poule_number=POULE_NUMBER, entries=entries)
    assert poule1 != poule2

def test_poule_inequality_different_tournaments(entries):
    poule1 = Poule(id=POULE_ID, tournament_id=TOURNY_ID, poule_number=POULE_NUMBER, entries=entries)
    for entry in entries:
        entry.tournament_id = DIFFERENT_TOURNY_ID
    poule2 = Poule(id=POULE_ID, tournament_id=DIFFERENT_TOURNY_ID, poule_number=POULE_NUMBER, entries=entries)
    assert poule1 != poule2

def test_poule__create_match(poule):
    match = poule._create_match(entries=poule.entries, match_id=1, match_index=0, match_pair=(1, 2))
    assert match.id == 1
    assert match.match_index == 0
    assert match.entry1 == poule.entries[0]
    assert match.entry2 == poule.entries[1]
    assert match.poule_id == POULE_ID
    assert match.tournament_id == TOURNY_ID
    assert match.is_incomplete()
    assert match.winner() is None

@pytest.mark.parametrize('invalid_entries_type', [None, 'Harry', 0, 1.0, True, False, {}, (1,)])
def test_poule__create_match_invalid_entries_type(poule, invalid_entries_type):
    with pytest.raises(TypeError):
        poule._create_match(entries=invalid_entries_type, match_id=1, match_index=0, match_pair=(1, 2))

def test_poule__create_match_invalid_entries_list_length(poule):
    with pytest.raises(ValueError):
        poule._create_match(entries=poule.entries[:1], match_id=1, match_index=0, match_pair=(1, 2))

def test_poule__create_match_invalid_entries_invalid_entry_type(poule, fencer3):
    invalid_entry = fencer3
    list_with_invalid_entry_type = [poule.entries[0], poule.entries[1], invalid_entry]
    with pytest.raises(TypeError):
        poule._create_match(entries=list_with_invalid_entry_type, match_id=1, match_index=0, match_pair=(1, 2))

def test_poule__create_match_an_entry_does_not_belong_to_tournament(poule, fencer3):
    entry_wrong_tournament = TournamentEntry(ENTRY_ID3, DIFFERENT_TOURNY_ID, fencer3)
    list_with_invalid_entry_tournament_id = [poule.entries[0], poule.entries[1], entry_wrong_tournament]
    with pytest.raises(ValueError):
        poule._create_match(entries=list_with_invalid_entry_tournament_id, match_id=1, match_index=0, match_pair=(1, 2))

@pytest.mark.parametrize('invalid_match_id_type', INVALID_ID_TYPES)
def test_poule__create_match_invalid_match_id_type(poule, invalid_match_id_type):
    with pytest.raises(TypeError):
        poule._create_match(entries=poule.entries, match_id=invalid_match_id_type, match_index=0, match_pair=(1, 2))

@pytest.mark.parametrize('invalid_match_id_value', [-100, -10, -1, 0])
def test_poule__create_match_invalid_match_id_value(poule, invalid_match_id_value):
    with pytest.raises(ValueError):
        poule._create_match(entries=poule.entries, match_id=invalid_match_id_value, match_index=0, match_pair=(1, 2))

@pytest.mark.parametrize('invalid_match_index_type', [None, 'second', 1.0, True, False, [], (1,), {}])
def test_poule__create_match_invalid_match_index_type(poule, invalid_match_index_type):
    with pytest.raises(TypeError):
        poule._create_match(entries=poule.entries, match_id=1, match_index=invalid_match_index_type, match_pair=(1, 2))

@pytest.mark.parametrize('invalid_match_index_value', [-100, -10, -1, 21, 22, 100]) # Assumes a poule of size 7 based on current fixture size
def test_poule__create_match_invalid_match_index_value(poule, invalid_match_index_value):
    with pytest.raises(ValueError):
        poule._create_match(entries=poule.entries, match_id=1, match_index=invalid_match_index_value, match_pair=(1, 2))

@pytest.mark.parametrize('invalid_match_pair_type', [None, 'Ron vs. Bill', 0, 1.0, True, False, [], [1,2], {}])
def test_poule__create_match_invalid_match_pair_type(poule, invalid_match_pair_type):
    with pytest.raises(TypeError):
        poule._create_match(entries=poule.entries, match_id=1, match_index=0, match_pair=invalid_match_pair_type)

@pytest.mark.parametrize('invalid_match_pair_invalid_element_type', [(None, 1), (1, 'Bob'), (1, 1.0), (False, True), ([], 1), (2, {}), ((1,), 2)])
def test_poule__create_match_invalid_match_tuple_pair_types(poule, invalid_match_pair_invalid_element_type):
    with pytest.raises(TypeError):
        poule._create_match(entries=poule.entries, match_id=1, match_index=0, match_pair=invalid_match_pair_invalid_element_type)

@pytest.mark.parametrize('invalid_match_pair_length', [(1,), (1, 2, 3), (1, 2, 3, 4)])
def test_poule__create_match_invalid_match_tuple_pair_length(poule, invalid_match_pair_length):
    with pytest.raises(ValueError):
        poule._create_match(entries=poule.entries, match_id=1, match_index=0, match_pair=invalid_match_pair_length)

@pytest.mark.parametrize('invalid_match_pair_values', [(0, 1), (1, 8), (2, 9), (99, 100), (3, -1), (-1, -2)]) # Assumes a poule of size 7 based on current fixture size
def test_poule__create_match_invalid_match_tuple_pair_values_out_of_bounds(poule, invalid_match_pair_values):
    with pytest.raises(ValueError):
        poule._create_match(entries=poule.entries, match_id=1, match_index=0, match_pair=invalid_match_pair_values)

def test_poule_add_entry(poule):
    old_matches = poule.matches[:]
    old_size = poule.size
    old_entries = poule.entries[:]
    new_entry = TournamentEntry(id=8, tournament_id=1, fencer=Fencer(id=8, display_name='Carol'))
    poule.add_entry(new_entry)
    assert poule.entries == old_entries + [new_entry]
    assert poule.matches != old_matches
    assert poule.size == old_size + 1

def test_poule_add_invalid_entry(poule):
    with pytest.raises(TypeError):
        poule.add_entry(10)
    duplicate_new_entry = copy.deepcopy(poule.entries[3])
    with pytest.raises(ValueError):
        poule.add_entry(duplicate_new_entry)

def test_poule_remove_entry(poule):
    old_matches = poule.matches[:]
    old_size = poule.size
    old_entries = poule.entries[:]
    poule.remove_entry(poule.entries[0])
    assert poule.entries == old_entries[1:]
    assert poule.matches != old_matches
    assert poule.size == old_size - 1

def test_poule_remove_entry_invalid(poule):
    with pytest.raises(TypeError):
        poule.remove_entry('John')
    with pytest.raises(ValueError):
        poule.remove_entry(TournamentEntry(id=12, tournament_id=1, fencer=Fencer(id=12, display_name='Jake')))

def test_poule_generate_matches(poule):
    assert poule.size == 7
    # Match 1: (1,4)
    assert poule.matches[0].entry1 == poule.entries[0]
    assert poule.matches[0].entry2 == poule.entries[3]
    # Match 2: (2,5)
    assert poule.matches[1].entry1 == poule.entries[1]
    assert poule.matches[1].entry2 == poule.entries[4]
    # Match 3: (3,6)
    assert poule.matches[2].entry1 == poule.entries[2]
    assert poule.matches[2].entry2 == poule.entries[5]

def test_poule_get_current_match(poule):
    # First match in poule of 7: (1,4)
    current_match = poule.get_current_match()
    assert current_match.entry1 == poule.entries[0]
    assert current_match.entry2 == poule.entries[3]
    assert current_match.is_complete() == False
    assert current_match.winner() == None
    assert current_match.poule_id == 1
    assert current_match.id == 1

    # Perform all matches
    for _ in range(poule.number_matches):
        poule.record_current_match_result(5, 0)
    
    assert poule.get_current_match() is None

def test_poule_get_next_match(poule):
    # Second match in poule of 7: (2,5)
    next_match = poule.get_next_match()
    assert next_match.entry1 == poule.entries[1]
    assert next_match.entry2 == poule.entries[4]
    assert next_match.poule_id == 1
    assert next_match.id == 2
    assert next_match.is_complete() == False
    assert next_match.winner() == None

    # Complete all matches up to the last match
    for _ in range(poule.number_matches-1):
        poule.record_current_match_result(score1=5, score2=0)
    
    assert poule.get_next_match() is None

def test_poule_record_match_result(poule):
    index = 5
    poule.record_match_result(index=index, score1=2, score2=3)
    # Check that first match is still incomplete
    m1 = poule.matches[0]
    assert m1.is_complete() == False
    assert m1.winner() is None
    assert m1.id == 1
    assert m1.poule_id == 1
    # Check that the `index+1` match is complete
    m2 = poule.matches[index]
    assert m2.score1 == 2
    assert m2.score2 == 3
    assert m2.is_complete()
    assert m2.winner() == m2.entry2
    assert m2.id == index+1
    assert m2.poule_id == 1

def test_poule_record_match_result_invalid(entries):
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries)

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

def test_poule_record_current_match_result(entries):
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries)
    
    for i in range(poule.number_matches):
        # Check match info before recording the result
        m = poule.get_current_match()
        assert m.id == i+1
        assert m.match_index == i
        assert m.poule_id == POULE_ID
        assert m.tournament_id == TOURNY_ID
        assert m.is_incomplete()
        assert m.winner() is None

        # Record a score using randomization
        score1 = random.randint(0,5)
        score2 = random.randint(0,5)
        while score1 == score2:
            score2 = random.randint(0,5)
        poule.record_current_match_result(score1=score1, score2=score2)

        # Check match info after recording the result
        m = poule.matches[i]
        assert m.id == i+1
        assert m.match_index == i
        assert m.poule_id == POULE_ID
        assert m.tournament_id == TOURNY_ID
        assert m.is_complete()
        assert m.winner() is not None

def test_poule_record_current_match_result_invalid_poule_completed(poule):
    for _ in range(poule.number_matches):
        poule.record_current_match_result(5,2)

    with pytest.raises(RuntimeError):
        poule.record_current_match_result(5,2)

def test_poule_is_complete(entries):
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries)
    # Complete all matches
    for _ in range(poule.number_matches):
        poule.record_current_match_result(3,4)

    assert poule.is_complete() == True

def test_poule_calculate_results(entries):
    # Test a poule of 3
    poule = Poule(id=1, tournament_id=1, poule_number=1, entries=entries[:3])

    # Record first match: (1,2)
    poule.record_current_match_result(score1=5, score2=1)

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
    poule.record_current_match_result(score1=2, score2=5)

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
    poule.record_current_match_result(score1=4, score2=5)

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
    assert poule_results.calculate_standings_display_names() == ['Hannah', 'John', 'Steve']

def test_poule_calculate_results_names_only(entries):
    poule = Poule(id=POULE_ID, tournament_id=TOURNY_ID, poule_number=POULE_NUMBER, entries=entries[:3])

    poule.record_current_match_result(5,1)
    poule.record_current_match_result(2,5)
    poule.record_current_match_result(4,5)

    assert poule.calculate_results_names_only() == ['Hannah', 'John', 'Steve']