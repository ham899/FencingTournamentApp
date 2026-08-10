import copy
import pytest

import factories

from constants import TOURNY_ID1, TOURNY_ID2

from poules.poule_round import PouleRound

# --- Constants ---
POULE_ROUND_ID = 1
POULE_ROUND_NUMBER = 1


# --- Fixtures ---
@pytest.fixture
def entries():
    return factories.make_entries(n = 21, tournament_id = TOURNY_ID1, initial_seed= True)


# --- Initialization and Validation Tests ---
def test_poule_round_creation_valid_21(entries):
    # Poule assignment expectation
    expected_poule1 = (entries[0], entries[5], entries[6], entries[11], entries[12], entries[17], entries[18])
    expected_poule2 = (entries[1], entries[4], entries[7], entries[10], entries[13], entries[16], entries[19])
    expected_poule3 = (entries[2], entries[3], entries[8], entries[9], entries[14], entries[15], entries[20])
    expected_poules = (expected_poule1, expected_poule2, expected_poule3)

    poule_round = PouleRound(POULE_ROUND_ID, TOURNY_ID1, POULE_ROUND_NUMBER, entries)
    
    assert poule_round.id == POULE_ROUND_ID
    assert poule_round.tournament_id == TOURNY_ID1
    assert poule_round.round_number == POULE_ROUND_NUMBER
    assert poule_round.entries == entries

    assert isinstance(poule_round.entries, tuple)
    assert isinstance(poule_round.poules, tuple)

    assert poule_round.num_entries == 21
    assert poule_round.num_poules == 3

    for i, poule in enumerate(poule_round.poules):
        assert poule.id == i + 1
        assert poule.tournament_id == poule_round.tournament_id
        assert poule.poule_number == i + 1
        assert poule.entries == expected_poules[i]
        assert not poule.is_complete()

def test_poule_round_creation_valid_17():
    entries = factories.make_entries(17, TOURNY_ID1, initial_seed=True)

    # Poule assignment expectation
    expected_poule1 = (entries[0], entries[5], entries[6], entries[11], entries[12], entries[16])
    expected_poule2 = (entries[1], entries[4], entries[7], entries[10], entries[13], entries[15])
    expected_poule3 = (entries[2], entries[3], entries[8], entries[9], entries[14])

    expected_poules = (expected_poule1, expected_poule2, expected_poule3)

    poule_round = PouleRound(POULE_ROUND_ID, TOURNY_ID1, POULE_ROUND_NUMBER, entries)
    
    assert poule_round.id == POULE_ROUND_ID
    assert poule_round.tournament_id == TOURNY_ID1
    assert poule_round.round_number == POULE_ROUND_NUMBER
    assert poule_round.entries == entries

    assert isinstance(poule_round.entries, tuple)
    assert isinstance(poule_round.poules, tuple)

    assert poule_round.num_entries == 17
    assert poule_round.num_poules == 3

    for i, poule in enumerate(poule_round.poules):
        assert poule.id == i + 1
        assert poule.tournament_id == poule_round.tournament_id
        assert poule.poule_number == i + 1
        assert poule.entries == expected_poules[i]
        assert not poule.is_complete()

def test_poule_round_creation_valid_38():
    entries = factories.make_entries(38, TOURNY_ID1, initial_seed=True)

    # Poule assignment expectation
    expected_poule1 = (entries[0], entries[11], entries[12], entries[23], entries[24], entries[35], entries[36])
    expected_poule2 = (entries[1], entries[10], entries[13], entries[22], entries[25], entries[34], entries[37])
    expected_poule3 = (entries[2], entries[9], entries[14], entries[21], entries[26], entries[33])
    expected_poule4 = (entries[3], entries[8], entries[15], entries[20], entries[27], entries[32])
    expected_poule5 = (entries[4], entries[7], entries[16], entries[19], entries[28], entries[31])
    expected_poule6 = (entries[5], entries[6], entries[17], entries[18], entries[29], entries[30])

    expected_poules = (expected_poule1, expected_poule2, expected_poule3, expected_poule4, expected_poule5, expected_poule6)

    poule_round = PouleRound(POULE_ROUND_ID, TOURNY_ID1, POULE_ROUND_NUMBER, entries)
    
    assert poule_round.id == POULE_ROUND_ID
    assert poule_round.tournament_id == TOURNY_ID1
    assert poule_round.round_number == POULE_ROUND_NUMBER
    assert poule_round.entries == entries

    assert isinstance(poule_round.entries, tuple)
    assert isinstance(poule_round.poules, tuple)

    assert poule_round.num_entries == 38
    assert poule_round.num_poules == 6

    for i, poule in enumerate(poule_round.poules):
        assert poule.id == i + 1
        assert poule.tournament_id == poule_round.tournament_id
        assert poule.poule_number == i + 1
        assert poule.entries == expected_poules[i]
        assert not poule.is_complete()

def test_poule_round_creation_valid_two_entries():
    entries = factories.make_entries(2, TOURNY_ID1, initial_seed=True)

    poule_round = PouleRound(POULE_ROUND_ID, TOURNY_ID1, POULE_ROUND_NUMBER, entries)

    assert poule_round.entries == entries
    assert poule_round.num_entries == 2
    assert poule_round.num_poules == 1
    assert poule_round.poules[0].entries == entries
    assert poule_round.poules[0].number_matches == 1

@pytest.mark.parametrize('invalid_round_id_type', [None, '1UI3', False, True, 1.0, [], (), {}])
def test_poule_round_creation_invalid_round_id_type(entries, invalid_round_id_type):
    with pytest.raises(TypeError):
        PouleRound(invalid_round_id_type, TOURNY_ID1, POULE_ROUND_NUMBER, entries)

@pytest.mark.parametrize('invalid_round_id_value', [-100, -1, 0])
def test_poule_round_creation_invalid_round_id_value(entries, invalid_round_id_value):
    with pytest.raises(ValueError):
        PouleRound(invalid_round_id_value, TOURNY_ID1, POULE_ROUND_NUMBER, entries)

@pytest.mark.parametrize('invalid_tournament_id_type', [None, '1UI3', False, True, 1.0, [], (), {}])
def test_poule_round_creation_invalid_tournament_id_type(entries, invalid_tournament_id_type):
    with pytest.raises(TypeError):
        PouleRound(POULE_ROUND_ID, invalid_tournament_id_type, POULE_ROUND_NUMBER, entries)

@pytest.mark.parametrize('invalid_tournament_id_value', [-100, -1, 0])
def test_poule_round_creation_invalid_tournament_id_value(entries, invalid_tournament_id_value):
    with pytest.raises(ValueError):
        PouleRound(POULE_ROUND_ID, invalid_tournament_id_value, POULE_ROUND_NUMBER, entries)

@pytest.mark.parametrize('invalid_round_number_type', [None, 'three', False, True, 1.0, [], (), {}])
def test_poule_round_creation_invalid_poule_round_number_type(entries, invalid_round_number_type):
    with pytest.raises(TypeError):
        PouleRound(POULE_ROUND_ID, TOURNY_ID1, invalid_round_number_type, entries)

@pytest.mark.parametrize('invalid_round_number_value', [-100, -1, 0])
def test_poule_round_creation_invalid_poule_round_number_value(entries, invalid_round_number_value):
    with pytest.raises(ValueError):
        PouleRound(POULE_ROUND_ID, TOURNY_ID1, invalid_round_number_value, entries)

@pytest.mark.parametrize('invalid_entries_type', [None, False, True, 0, 1.0, 'John', {}, [1]])
def test_poule_round_creation_invalid_entries_type(invalid_entries_type):
    with pytest.raises(TypeError):
        PouleRound(POULE_ROUND_ID, TOURNY_ID1, POULE_ROUND_NUMBER, invalid_entries_type)

@pytest.mark.parametrize(
        ('index', 'invalid_entry_type'), 
        [
            (4, 'Jennifer'), 
            (7, False), 
            (8, True), 
            (5, 0), 
            (11, 15.0), 
            (17, None), 
            (20, factories.make_fencer(10, 'Jennifer'))
        ]
)
def test_poule_round_creation_invalid_entries_invalid_entry_type(entries, index, invalid_entry_type):
    entries = list(entries)
    
    entries[index] = invalid_entry_type
    
    entries = tuple(entries)

    with pytest.raises(TypeError):
        PouleRound(POULE_ROUND_ID, TOURNY_ID1, POULE_ROUND_NUMBER, entries)

@pytest.mark.parametrize('index', [0, 7, 10, 20])
def test_poule_round_creation_invalid_entries_invalid_entry_tournament_id(entries, index):
    entries[index].tournament_id = TOURNY_ID2

    with pytest.raises(ValueError):
        PouleRound(POULE_ROUND_ID, TOURNY_ID1, POULE_ROUND_NUMBER, entries)

def test_poule_round_creation_invalid_entries_empty():
    with pytest.raises(ValueError):
        PouleRound(POULE_ROUND_ID, TOURNY_ID1, POULE_ROUND_NUMBER, ())

def test_poule_round_creation_invalid_entries_only_one_entry():
    entries = factories.make_entries(1, TOURNY_ID1, initial_seed=True)

    with pytest.raises(ValueError):
        PouleRound(POULE_ROUND_ID, TOURNY_ID1, POULE_ROUND_NUMBER, entries)

def test_poule_round_creation_invalid_entries_duplicate_entry(entries):
    duplicate_entry = copy.deepcopy(entries[7])
    duplicate_entry.set_initial_seed(len(entries) + 1)

    entries = entries + (duplicate_entry,)

    with pytest.raises(ValueError):
        PouleRound(POULE_ROUND_ID, TOURNY_ID1, POULE_ROUND_NUMBER, entries)

def test_poule_round_creation_invalid_entries_entry_missing_initial_seed(entries):
    entries[5].set_initial_seed(None)

    with pytest.raises(ValueError):
        PouleRound(POULE_ROUND_ID, TOURNY_ID1, POULE_ROUND_NUMBER, entries)

@pytest.mark.parametrize('invalid_seed_type', ['five', False, True, 5.0])
def test_poule_round_creation_invalid_entries_entry_initial_seed_type(entries, invalid_seed_type):
    entries[8].initial_seed = invalid_seed_type

    with pytest.raises(TypeError):
        PouleRound(POULE_ROUND_ID, TOURNY_ID1, POULE_ROUND_NUMBER, entries)

@pytest.mark.parametrize('invalid_seed_value', [-5, -1, 0])
def test_poule_round_creation_invalid_entries_entry_initial_seed_value(entries, invalid_seed_value):
    entries[11].initial_seed = invalid_seed_value

    with pytest.raises(ValueError):
        PouleRound(POULE_ROUND_ID, TOURNY_ID1, POULE_ROUND_NUMBER, entries)

def test_poule_round_creation_invalid_entries_entry_duplicate_initial_seed(entries):
    entries[15].initial_seed = entries[4].initial_seed

    with pytest.raises(ValueError):
        PouleRound(POULE_ROUND_ID, TOURNY_ID1, POULE_ROUND_NUMBER, entries)

def test_poule_round_creation_invalid_entries_entry_initial_seed_outside_expected_range(entries):
    entries[-1].set_initial_seed(22)

    with pytest.raises(ValueError):
        PouleRound(POULE_ROUND_ID, TOURNY_ID1, POULE_ROUND_NUMBER, entries)

def test_poule_round_creation_sorts_entries_by_initial_seed(entries):
    reversed_entries = tuple(reversed(entries))

    poule_round = PouleRound(POULE_ROUND_ID, TOURNY_ID1, POULE_ROUND_NUMBER, reversed_entries)

    assert poule_round.entries == entries

    # Poule assignment expectation
    expected_poule1 = (entries[0], entries[5], entries[6], entries[11], entries[12], entries[17], entries[18])
    expected_poule2 = (entries[1], entries[4], entries[7], entries[10], entries[13], entries[16], entries[19])
    expected_poule3 = (entries[2], entries[3], entries[8], entries[9], entries[14], entries[15], entries[20])
    expected_poules = (expected_poule1, expected_poule2, expected_poule3)

    for i, poule in enumerate(poule_round.poules):
        assert poule.entries == expected_poules[i]
