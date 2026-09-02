import pytest

from entities.tournament_entry import TournamentEntry


# --- Constants ---
from constants import (
    ENTRY_ID1, 
    ENTRY_ID2, 
    TOURNY_ID1,
    TOURNY_ID2
)

INVALID_ID_TYPES = [None, '1', 1.0, False, True, [], (), {}, object()]
INVALID_ID_VALUES = [-10, -5, -1, 0]


# --- Initialization and Validation Tests ---
def test_tournament_entry_valid_creation(fencer1):
    entry = TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID1, fencer=fencer1)
    
    assert entry.id==ENTRY_ID1
    assert entry.tournament_id==TOURNY_ID1
    assert entry.fencer==fencer1
    assert entry.display_name == fencer1.display_name

@pytest.mark.parametrize('invalid_id_type', INVALID_ID_TYPES)
def test_tournament_entry_creation_invalid_id_type(fencer1, invalid_id_type):
    with pytest.raises(TypeError):
        TournamentEntry(id=invalid_id_type, tournament_id=TOURNY_ID1, fencer=fencer1)

@pytest.mark.parametrize('invalid_id_value', INVALID_ID_VALUES)
def test_tournament_entry_creation_invalid_id_value(fencer1, invalid_id_value):
    with pytest.raises(ValueError):
        TournamentEntry(id=invalid_id_value, tournament_id=TOURNY_ID1, fencer=fencer1)

@pytest.mark.parametrize('invalid_tournament_id_type', INVALID_ID_TYPES)
def test_tournament_entry_creation_invalid_tournament_id_type(fencer1, invalid_tournament_id_type):
    with pytest.raises(TypeError):
        TournamentEntry(id=ENTRY_ID1, tournament_id=invalid_tournament_id_type, fencer=fencer1)

@pytest.mark.parametrize('invalid_tournament_id_value', INVALID_ID_VALUES)
def test_tournament_entry_creation_invalid_tournament_id_value(fencer1, invalid_tournament_id_value):
    with pytest.raises(ValueError):
        TournamentEntry(id=ENTRY_ID1, tournament_id=invalid_tournament_id_value, fencer=fencer1)

@pytest.mark.parametrize('invalid_fencer_type', [None, 'John', 1, 1.0, False, [], (), {}, object()])
def test_tournament_entry_creation_invalid_fencer_type(invalid_fencer_type):
    with pytest.raises(TypeError):
        TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID1, fencer=invalid_fencer_type)


# --- Equality Tests ---
def test_tournament_entry_equality(fencer1, entry1):
    entry2 = TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID1, fencer=fencer1)
    
    assert entry1 == entry2 # Same entries

@pytest.mark.parametrize('non_entry_object', [None, False, True, 0, 1.0, 'non_entry', (), [], {}, object()])
def test_tournament_entry_inequality_different_object(entry1, non_entry_object):
    assert entry1 != non_entry_object

def test_tournament_entry_inequality_different_ids(fencer1, entry1):
    entry2 = TournamentEntry(id=ENTRY_ID2, tournament_id=TOURNY_ID1, fencer=fencer1)
    
    assert entry1 != entry2 # Same fencer but different entry ID - the tournament controller should not allow this to happen

def test_tournament_entry_inequality_different_tournament_ids(fencer1, entry1):
    entry2 = TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID2, fencer=fencer1)
    
    assert entry1 != entry2 # Same fencer, different tournament, so different entry

def test_tournament_entry_inequality_different_fencers(entry1, entry2):
    assert entry1 != entry2 # Two different fencers/entries at the same tournament - most common case of inequality
