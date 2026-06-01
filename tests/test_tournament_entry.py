import pytest
from tournament_entry import TournamentEntry
from fencer import Fencer

### Constants ###
TOURNY_ID = 1
FENCER_ID1 = 1
FENCER_ID2 = 2
ENTRY_ID1 = 1
ENTRY_ID2 = 2
NAME1 = 'Jane'
NAME2 = 'John'

### Fixtures ###
@pytest.fixture
def fencer():
    return Fencer(id=FENCER_ID1, display_name=NAME1)

@pytest.fixture
def entry(fencer):
    return TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer)

def test_tournament_entry_creation_valid_seeds_left_optional(fencer):
    entry = TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer)
    assert entry.id==ENTRY_ID1
    assert entry.tournament_id==TOURNY_ID
    assert entry.fencer==fencer
    assert entry.initial_seed is None
    assert entry.de_seed is None

def test_tournament_entry_creation_valid_all_parameters_filled(fencer):
    entry = TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer, initial_seed=1, de_seed=1)
    assert entry.id==ENTRY_ID1
    assert entry.tournament_id==TOURNY_ID
    assert entry.fencer==fencer
    assert entry.initial_seed==1
    assert entry.de_seed==1

def test_tournament_entry_creation_invalid_id_type(fencer):
    with pytest.raises(TypeError):
        TournamentEntry(id='1', tournament_id=TOURNY_ID, fencer=fencer)

def test_tournament_entry_creation_invalid_id_zero(fencer):
    with pytest.raises(ValueError):
        TournamentEntry(id=0, tournament_id=TOURNY_ID, fencer=fencer)

def test_tournament_entry_creation_invalid_id_negative(fencer):
    with pytest.raises(ValueError):
        TournamentEntry(id=-1, tournament_id=TOURNY_ID, fencer=fencer)

def test_tournament_entry_creation_invalid_tournament_id_type(fencer):
    with pytest.raises(TypeError):
        TournamentEntry(id=ENTRY_ID1, tournament_id=3.2, fencer=fencer)

def test_tournament_entry_creation_invalid_tournament_id_zero(fencer):
    with pytest.raises(ValueError):
        TournamentEntry(id=ENTRY_ID1, tournament_id=0, fencer=fencer)

def test_tournament_entry_creation_invalid_tournament_id_negative(fencer):
    with pytest.raises(ValueError):
        TournamentEntry(id=ENTRY_ID1, tournament_id=-1, fencer=fencer)

def test_tournament_entry_creation_invalid_fencer_type():
    with pytest.raises(TypeError):
        TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=1)

def test_tournament_entry_creation_invalid_initial_seed_type(fencer):
    with pytest.raises(TypeError):
        TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer, initial_seed=7.1)

def test_tournament_entry_creation_invalid_initial_seed_zero(fencer):
    with pytest.raises(ValueError):
        TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer, initial_seed=0)

def test_tournament_entry_creation_invalid_initial_seed_negative(fencer):
    with pytest.raises(ValueError):
        TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer, initial_seed=-1)

def test_tournament_entry_creation_invalid_de_seed_type(fencer):
    with pytest.raises(TypeError):
        TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer, initial_seed=1, de_seed='10')

def test_tournament_entry_creation_invalid_de_seed_zero(fencer):
    with pytest.raises(ValueError):
        TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer, initial_seed=1, de_seed=0)

def test_tournament_entry_creation_invalid_de_seed_negative(fencer):
    with pytest.raises(ValueError):
        TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer, initial_seed=1, de_seed=-1)

def test_tournament_entry_set_initial_seed_valid(entry):
    assert entry.initial_seed is None
    entry.set_initial_seed(1)
    assert entry.initial_seed == 1

def test_tournament_entry_set_initial_seed_valid_none(entry):
    entry.set_initial_seed(1)
    assert entry.initial_seed == 1
    entry.set_initial_seed(None)
    assert entry.initial_seed is None

def test_tournament_entry_set_initial_seed_invalid_type(entry):
    with pytest.raises(TypeError):
        entry.set_initial_seed(1.5)

def test_tournament_entry_set_initial_seed_invalid_zero(entry):
    with pytest.raises(ValueError):
        entry.set_initial_seed(0)

def test_tournament_entry_set_initial_seed_invalid_negative(entry):
    with pytest.raises(ValueError):
        entry.set_initial_seed(-1)

def test_tournament_entry_set_de_seed_valid(entry):
    assert entry.de_seed is None
    entry.set_de_seed(1)
    assert entry.de_seed == 1

def test_tournament_entry_set_de_seed_valid_none(entry):
    entry.set_de_seed(1)
    assert entry.de_seed == 1
    entry.set_de_seed(None)
    assert entry.de_seed is None

def test_tournament_entry_set_de_seed_invalid_type(entry):
    with pytest.raises(TypeError):
        entry.set_de_seed('1')

def test_tournament_entry_set_de_seed_invalid_zero(entry):
    with pytest.raises(ValueError):
        entry.set_de_seed(0)

def test_tournament_entry_set_de_seed_invalid_negative(entry):
    with pytest.raises(ValueError):
        entry.set_de_seed(-1)

def test_tournament_entry_display_name(entry):
    assert entry.display_name() == 'Jane'

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