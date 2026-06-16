import pytest

from entities.tournament_entry import TournamentEntry
from entities.fencer import Fencer

# --- Constants ---
TOURNY_ID = 1
FENCER_ID1 = 1
FENCER_ID2 = 2
ENTRY_ID1 = 1
ENTRY_ID2 = 2
NAME1 = 'Jane'
NAME2 = 'John'

# --- Fixtures ---
@pytest.fixture
def fencer():
    return Fencer(id=FENCER_ID1, display_name=NAME1)

@pytest.fixture
def entry(fencer):
    return TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer)

# --- Initialization Tests ---
def test_tournament_entry_valid_creation_with_defaults(fencer):
    entry = TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer)
    assert entry.id==ENTRY_ID1
    assert entry.tournament_id==TOURNY_ID
    assert entry.fencer==fencer
    assert entry.initial_seed is None
    assert entry.de_seed is None

def test_tournament_entry_valid_creation_no_defaults(fencer):
    entry = TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer, initial_seed=1, de_seed=1)
    assert entry.id==ENTRY_ID1
    assert entry.tournament_id==TOURNY_ID
    assert entry.fencer==fencer
    assert entry.initial_seed==1
    assert entry.de_seed==1

@pytest.mark.parametrize('invalid_id_types', [None, '1', 1.0, True, [], {}])
def test_tournament_entry_creation_invalid_id_type(fencer, invalid_id_types):
    with pytest.raises(TypeError):
        TournamentEntry(id=invalid_id_types, tournament_id=TOURNY_ID, fencer=fencer)

def test_tournament_entry_creation_invalid_id_zero(fencer):
    with pytest.raises(ValueError):
        TournamentEntry(id=0, tournament_id=TOURNY_ID, fencer=fencer)

@pytest.mark.parametrize('negative_id', [-100, -10, -1])
def test_tournament_entry_creation_invalid_id_negative(fencer, negative_id):
    with pytest.raises(ValueError):
        TournamentEntry(id=negative_id, tournament_id=TOURNY_ID, fencer=fencer)

@pytest.mark.parametrize('invalid_tournament_id_type', [None, '1', 1.0, True, [], {}])
def test_tournament_entry_creation_invalid_tournament_id_type(fencer, invalid_tournament_id_type):
    with pytest.raises(TypeError):
        TournamentEntry(id=ENTRY_ID1, tournament_id=invalid_tournament_id_type, fencer=fencer)

def test_tournament_entry_creation_invalid_tournament_id_zero(fencer):
    with pytest.raises(ValueError):
        TournamentEntry(id=ENTRY_ID1, tournament_id=0, fencer=fencer)

@pytest.mark.parametrize('negative_tournament_id', [-100,-10,-1])
def test_tournament_entry_creation_invalid_tournament_id_negative(fencer, negative_tournament_id):
    with pytest.raises(ValueError):
        TournamentEntry(id=ENTRY_ID1, tournament_id=negative_tournament_id, fencer=fencer)

@pytest.mark.parametrize('invalid_fencer_type', [None, 'John', 1, 1.0, False, [], {}])
def test_tournament_entry_creation_invalid_fencer_type(invalid_fencer_type):
    with pytest.raises(TypeError):
        TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=invalid_fencer_type)

@pytest.mark.parametrize('invalid_initial_seed_type', ['1', 1.0, True, [], {}])
def test_tournament_entry_creation_invalid_initial_seed_type(fencer, invalid_initial_seed_type):
    with pytest.raises(TypeError):
        TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer, initial_seed=invalid_initial_seed_type)

def test_tournament_entry_creation_invalid_initial_seed_zero(fencer):
    with pytest.raises(ValueError):
        TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer, initial_seed=0)

@pytest.mark.parametrize('negative_initial_seed', [-100, -10, -1])
def test_tournament_entry_creation_invalid_initial_seed_negative(fencer, negative_initial_seed):
    with pytest.raises(ValueError):
        TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer, initial_seed=negative_initial_seed)

@pytest.mark.parametrize('invalid_de_seed_type', ['1', 1.0, True, [], {}])
def test_tournament_entry_creation_invalid_de_seed_type(fencer, invalid_de_seed_type):
    with pytest.raises(TypeError):
        TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer, initial_seed=1, de_seed=invalid_de_seed_type)

def test_tournament_entry_creation_invalid_de_seed_zero(fencer):
    with pytest.raises(ValueError):
        TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer, initial_seed=1, de_seed=0)

@pytest.mark.parametrize('negative_de_seed', [-100, -10, -1])
def test_tournament_entry_creation_invalid_de_seed_negative(fencer, negative_de_seed):
    with pytest.raises(ValueError):
        TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer, initial_seed=1, de_seed=negative_de_seed)

def test_tournament_entry_display_name_property(entry):
    assert entry.display_name == 'Jane'

# --- Dunder Method Tests ---
def test_tournament_entry_equality_no_seeds():
    entry1 = TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=Fencer(id=FENCER_ID1, display_name=NAME1))
    entry2 = TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=Fencer(id=FENCER_ID1, display_name=NAME1))
    assert entry1 == entry2 # Same entries

def test_tournament_entry_equality_different_initial_seeds():
    entry1 = TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=Fencer(id=FENCER_ID1, display_name=NAME1), initial_seed=1)
    entry2 = TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=Fencer(id=FENCER_ID1, display_name=NAME1), initial_seed=2)
    assert entry1 == entry2 # Same entries

def test_tournament_entry_equality_different_de_seeds():
    entry1 = TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=Fencer(id=FENCER_ID1, display_name=NAME1), initial_seed=1, de_seed=1)
    entry2 = TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=Fencer(id=FENCER_ID1, display_name=NAME1), initial_seed=1, de_seed=2)
    assert entry1 == entry2 # Same entries

def test_tournament_entry_equality_one_has_seeds_other_has_no_seeds():
    entry1 = TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=Fencer(id=FENCER_ID1, display_name=NAME1))
    entry2 = TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=Fencer(id=FENCER_ID1, display_name=NAME1), initial_seed=1, de_seed=1)
    assert entry1 == entry2

def test_tournament_entry_inequality_non_entry(entry):
    assert entry != "not an entry"

def test_tournament_entry_inequality_different_ids():
    entry1 = TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=Fencer(id=FENCER_ID1, display_name=NAME1))
    entry2 = TournamentEntry(id=ENTRY_ID2, tournament_id=TOURNY_ID, fencer=Fencer(id=FENCER_ID1, display_name=NAME1))
    assert entry1 != entry2 # Same fencer but different entry ID - the tournament controller should not allow this to happen

def test_tournament_entry_inequality_different_tournament_ids():
    entry1 = TournamentEntry(id=ENTRY_ID1, tournament_id=1, fencer=Fencer(id=FENCER_ID1, display_name=NAME1))
    entry2 = TournamentEntry(id=ENTRY_ID1, tournament_id=2, fencer=Fencer(id=FENCER_ID1, display_name=NAME1))
    assert entry1 != entry2 # Same fencer, different tournament, so different entry

def test_tournament_entry_inequality_different_fencers():
    entry1 = TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=Fencer(id=FENCER_ID1, display_name=NAME1))
    entry2 = TournamentEntry(id=ENTRY_ID2, tournament_id=TOURNY_ID, fencer=Fencer(id=FENCER_ID2, display_name=NAME2))
    assert entry1 != entry2 # Two different fencers at the same tournament - most common case of inequality

# --- Public Method Tests ---
def test_tournament_entry_set_initial_seed_valid(entry):
    assert entry.initial_seed is None
    entry.set_initial_seed(1)
    assert entry.initial_seed == 1

def test_tournament_entry_set_initial_seed_valid_none(entry):
    entry.set_initial_seed(1)
    assert entry.initial_seed == 1
    entry.set_initial_seed(None)
    assert entry.initial_seed is None

@pytest.mark.parametrize('invalid_initial_seed_type', ['one', 1.0, True, [], {}])
def test_tournament_entry_set_initial_seed_invalid_type(entry, invalid_initial_seed_type):
    with pytest.raises(TypeError):
        entry.set_initial_seed(invalid_initial_seed_type)

def test_tournament_entry_set_initial_seed_invalid_zero(entry):
    with pytest.raises(ValueError):
        entry.set_initial_seed(0)

@pytest.mark.parametrize('negative_initial_seed', [-100, -10, -1])
def test_tournament_entry_set_initial_seed_invalid_negative(entry, negative_initial_seed):
    with pytest.raises(ValueError):
        entry.set_initial_seed(negative_initial_seed)

def test_tournament_entry_set_de_seed_valid(entry):
    assert entry.de_seed is None
    entry.set_de_seed(1)
    assert entry.de_seed == 1

def test_tournament_entry_set_de_seed_valid_none(entry):
    entry.set_de_seed(1)
    assert entry.de_seed == 1
    entry.set_de_seed(None)
    assert entry.de_seed is None

@pytest.mark.parametrize('invalid_de_seed_type', ['1', 1.0, True, [], {}])
def test_tournament_entry_set_de_seed_invalid_type(entry, invalid_de_seed_type):
    with pytest.raises(TypeError):
        entry.set_de_seed(invalid_de_seed_type)

def test_tournament_entry_set_de_seed_invalid_zero(entry):
    with pytest.raises(ValueError):
        entry.set_de_seed(0)

@pytest.mark.parametrize('negative_de_seed', [-100, -10, -1])
def test_tournament_entry_set_de_seed_invalid_negative(entry, negative_de_seed):
    with pytest.raises(ValueError):
        entry.set_de_seed(negative_de_seed)