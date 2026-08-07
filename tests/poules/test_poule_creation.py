import copy
import pytest

import factories

from constants import (
    FENCER_ID2,
    ENTRY_ID3,
    POULE_ID1,
    POULE_ID2,
    TOURNY_ID1,
    TOURNY_ID2
)

from entities.fencer import Fencer
from entities.tournament_entry import TournamentEntry
from poules.poule import Poule


# --- Constants ---
POULE_NUMBER1, POULE_NUMBER2 = 1, 2
NON_POSITIVE_INTS = [-10, -1, 0]
INVALID_ID_TYPES = [None, 'ABC', 1.0, True, ['F81C3'], (1,), {}]


# --- Fixtures ---
@pytest.fixture
def entries(entry1, entry2, entry3, entry4, entry5, entry6, entry7):
    return (entry1, entry2, entry3, entry4, entry5, entry6, entry7)

@pytest.fixture
def poule(entries):
    return Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER2, entries)


# --- Initialization and Validation Tests ---
def test_poule_creation_valid(entries):
    poule = Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries)
    
    assert poule.id == POULE_ID1
    assert poule.tournament_id == TOURNY_ID1
    assert poule.poule_number == POULE_NUMBER1
    assert poule.entries == entries
    assert poule.size == len(entries)
    assert isinstance(poule.matches, tuple)

    expected_number_matches = (len(entries) * (len(entries) - 1)) // 2
    assert poule.number_matches == expected_number_matches

@pytest.mark.parametrize('invalid_id_type', INVALID_ID_TYPES)
def test_poule_creation_invalid_id_type(entries, invalid_id_type):
    with pytest.raises(TypeError):
        Poule(invalid_id_type, TOURNY_ID1, POULE_NUMBER1, entries)

@pytest.mark.parametrize('invalid_id_value', NON_POSITIVE_INTS)
def test_poule_creation_invalid_id_value(entries, invalid_id_value):
    with pytest.raises(ValueError):
        Poule(invalid_id_value, TOURNY_ID1, POULE_NUMBER1, entries)

@pytest.mark.parametrize('invalid_tournament_id_type', INVALID_ID_TYPES)
def test_poule_creation_invalid_tournament_id_type(entries, invalid_tournament_id_type):
    with pytest.raises(TypeError):
        Poule(POULE_ID1, invalid_tournament_id_type, POULE_NUMBER1, entries)

@pytest.mark.parametrize('invalid_tournament_id_value', NON_POSITIVE_INTS)
def test_poule_creation_invalid_tournament_id_value(entries, invalid_tournament_id_value):
    with pytest.raises(ValueError):
        Poule(POULE_ID1, invalid_tournament_id_value, POULE_NUMBER1, entries)

@pytest.mark.parametrize('invalid_poule_number_type', [None, True, 1.0, 'one', (1,), [2], {}])
def test_poule_creation_invalid_poule_number_type(entries, invalid_poule_number_type):
    with pytest.raises(TypeError):
        Poule(POULE_ID1, TOURNY_ID1, invalid_poule_number_type, entries)

@pytest.mark.parametrize('invalid_poule_number_value', NON_POSITIVE_INTS)
def test_poule_creation_invalid_poule_number_value(entries, invalid_poule_number_value):
    with pytest.raises(ValueError):
        Poule(POULE_ID1, TOURNY_ID1, invalid_poule_number_value, entries)

@pytest.mark.parametrize('invalid_entries_type', [None, 'Harry', 0, 1.0, True, False, [0], {}])
def test_poule_creation_invalid_entries_type(invalid_entries_type):
    with pytest.raises(TypeError, match='Entries must be a tuple'):
        Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, invalid_entries_type)

@pytest.mark.parametrize('invalid_entry_type', [None, False, 0, 1.0, 'Harry', [], {}, Fencer(FENCER_ID2, 'Steve')])
def test_poule_creation_invalid_entries_entry_type(entry1, entry3, invalid_entry_type):
    entries_invalid_entry_type = (entry1, invalid_entry_type, entry3)
    
    with pytest.raises(TypeError, match='Each entry must be a TournamentEntry'):
        Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries_invalid_entry_type)

def test_poule_creation_invalid_no_entries():
    with pytest.raises(ValueError, match='at least two entries'):
        Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, ())

def test_poule_creation_invalid_only_one_entry(entry1):
    with pytest.raises(ValueError, match='at least two entries'):
        Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, (entry1,))

def test_poule_creation_invalid_entry_does_not_belong_to_tournament(entry1, entry2, fencer3):
    entry_wrong_tournament = TournamentEntry(ENTRY_ID3, TOURNY_ID2, fencer3)
    
    entries_invalid_entry_tournament_id = (entry1, entry2, entry_wrong_tournament)
    
    with pytest.raises(ValueError, match='belongs to tournament'):
        Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries_invalid_entry_tournament_id)

def test_poule_creation_invalid_duplicate_entry(entry1, entry2):
    duplicate_entry = copy.deepcopy(entry1)

    with pytest.raises(ValueError, match='appears more than once'):
        Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, (entry1, entry2, duplicate_entry))

@pytest.mark.parametrize('unsupported_size', [13, 14, 15, 16])
def test_poule_creation_invalid_unsupported_size(unsupported_size):
    entries = factories.make_entries(n=unsupported_size, tournament_id=TOURNY_ID1, initial_seed=True)

    with pytest.raises(ValueError, match='no official bout order exists for that size'):
        Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries)

@pytest.mark.parametrize(
        ('size', 'expected_number_matches'),
        [
            (2, 1),
            (3, 3),
            (4, 6),
            (5, 10),
            (6, 15),
            (7, 21),
            (8, 28),
            (9, 36),
            (10, 45),
            (11, 55),
            (12, 66)
        ]
)
def test_poule_size_and_number_matches_properties(size, expected_number_matches):
    entries = factories.make_entries(n=size, tournament_id=TOURNY_ID1, initial_seed=True)
    
    poule = Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries)

    assert poule.size == size
    assert poule.number_matches == expected_number_matches
    assert poule.number_matches == len(poule.matches)

def test_poule_equality(entries):
    poule1 = Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries)
    
    poule2 = Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries)
    
    assert poule1 == poule2

def test_poule_equality_ignores_match_state(poule):
    poule_copy = copy.deepcopy(poule)
    
    poule.record_on_piste_match_result(5,3)
    
    assert poule == poule_copy

@pytest.mark.parametrize('other', [None, 1, 'Poule', (), object()])
def test_poule_inequality_different_type(poule, other):
    assert poule != other

def test_poule_inequality_different_poules_same_tournament(entries):
    poule1 = Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries[0:3])
    
    poule2 = Poule(POULE_ID2, TOURNY_ID1, POULE_NUMBER2, entries[3:6])
    
    assert poule1 != poule2

def test_poule_inequality_different_tournaments(entries):
    poule1 = Poule(POULE_ID1, TOURNY_ID1, POULE_NUMBER1, entries)
    
    poule2 = Poule(POULE_ID1, TOURNY_ID2, POULE_NUMBER1, factories.make_entries(n=7, tournament_id=TOURNY_ID2, initial_seed=True))
    
    assert poule1 != poule2
