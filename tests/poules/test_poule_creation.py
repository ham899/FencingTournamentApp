import copy
import pytest

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
INVALID_ID_TYPES = [None, 'ABC', 1.0, True, ['F81C3'], (1,), {}]


# --- Fixtures ---
@pytest.fixture
def entries(entry1, entry2, entry3, entry4, entry5, entry6, entry7):
    return (entry1, entry2, entry3, entry4, entry5, entry6, entry7)


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

@pytest.mark.parametrize('invalid_entries_entry_type', [None, False, 0, 1.0, 'Harry', [], {}, Fencer(FENCER_ID2, 'Steve')])
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
