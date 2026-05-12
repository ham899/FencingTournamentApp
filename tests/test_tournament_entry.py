import pytest
from tournament_entry import TournamentEntry
from fencer import Fencer

@pytest.fixture
def fencer():
    return Fencer(id=1, display_name='Jane')

def test_entry_creation_valid_left_optional(fencer):
    entry = TournamentEntry(id=1, tournament_id=1, fencer=fencer)
    assert entry.id==1
    assert entry.tournament_id==1
    assert entry.fencer==fencer
    assert entry.initial_seed is None
    assert entry.de_seed is None

def test_entry_creation_valid_full(fencer):
    entry = TournamentEntry(id=1, tournament_id=1, fencer=fencer, initial_seed=1, de_seed=1)
    assert entry.id==1
    assert entry.tournament_id==1
    assert entry.fencer==fencer
    assert entry.initial_seed==1
    assert entry.de_seed==1

def test_entry_creation_invalid_id_type(fencer):
    with pytest.raises(TypeError):
        TournamentEntry(id='1', tournament_id=1, fencer=fencer)

def test_entry_creation_invalid_id_zero(fencer):
    with pytest.raises(ValueError):
        TournamentEntry(id=0, tournament_id=1, fencer=fencer)

def test_entry_creation_invalid_id_negative(fencer):
    with pytest.raises(ValueError):
        TournamentEntry(id=-2, tournament_id=1, fencer=fencer)

def test_entry_creation_invalid_tournament_id_type(fencer):
    with pytest.raises(TypeError):
        TournamentEntry(id=1, tournament_id=3.2, fencer=fencer)

def test_entry_creation_invalid_tournament_id_zero(fencer):
    with pytest.raises(ValueError):
        TournamentEntry(id=1, tournament_id=0, fencer=fencer)

def test_entry_creation_invalid_tournament_id_negative(fencer):
    with pytest.raises(ValueError):
        TournamentEntry(id=1, tournament_id=-4, fencer=fencer)

def test_entry_creation_invalid_fencer_type(fencer):
    with pytest.raises(TypeError):
        TournamentEntry(id=1, tournament_id=1, fencer=1)

def test_entry_creation_invalid_initial_seed_type(fencer):
    with pytest.raises(TypeError):
        TournamentEntry(id=1, tournament_id=1, fencer=fencer, initial_seed=7.1)

def test_entry_creation_invalid_initial_seed_zero(fencer):
    with pytest.raises(ValueError):
        TournamentEntry(id=1, tournament_id=1, fencer=fencer, initial_seed=0)

def test_entry_creation_invalid_initial_seed_negative(fencer):
    with pytest.raises(ValueError):
        TournamentEntry(id=1, tournament_id=1, fencer=fencer, initial_seed=-1)

def test_entry_creation_invalid_de_seed_type(fencer):
    with pytest.raises(TypeError):
        TournamentEntry(id=1, tournament_id=1, fencer=fencer, initial_seed=1, de_seed='10')

def test_entry_creation_invalid_de_seed_zero(fencer):
    with pytest.raises(ValueError):
        TournamentEntry(id=1, tournament_id=1, fencer=fencer, initial_seed=1, de_seed=0)

def test_entry_creation_invalid_de_seed_negative(fencer):
    with pytest.raises(ValueError):
        TournamentEntry(id=1, tournament_id=1, fencer=fencer, initial_seed=1, de_seed=-5)

def test_set_initial_seed_valid_number(fencer):
    entry = TournamentEntry(id=1, tournament_id=1, fencer=fencer)
    entry.set_initial_seed(3)
    assert entry.initial_seed == 3

def test_set_initial_seed_valid_none(fencer):
    entry = TournamentEntry(id=1, tournament_id=1, fencer=fencer)
    entry.set_initial_seed(None)
    assert entry.initial_seed is None

def test_set_initial_seed_invalid_type(fencer):
    entry = TournamentEntry(id=1, tournament_id=1, fencer=fencer)
    with pytest.raises(TypeError):
        entry.set_initial_seed(2.5)

def test_set_initial_seed_invalid_zero(fencer):
    entry = TournamentEntry(id=1, tournament_id=1, fencer=fencer)
    with pytest.raises(ValueError):
        entry.set_initial_seed(0)

def test_set_initial_seed_invalid_negative(fencer):
    entry = TournamentEntry(id=1, tournament_id=1, fencer=fencer)
    with pytest.raises(ValueError):
        entry.set_initial_seed(-3)

def test_set_de_seed_valid_number(fencer):
    entry = TournamentEntry(id=1, tournament_id=1, fencer=fencer)
    entry.set_de_seed(10)
    assert entry.de_seed == 10

def test_set_de_seed_valid_none(fencer):
    entry = TournamentEntry(id=1, tournament_id=1, fencer=fencer)
    entry.set_de_seed(None)
    assert entry.de_seed is None

def test_set_de_seed_invalid_type(fencer):
    entry = TournamentEntry(id=1, tournament_id=1, fencer=fencer)
    with pytest.raises(TypeError):
        entry.set_de_seed('5')

def test_set_de_seed_invalid_zero(fencer):
    entry = TournamentEntry(id=1, tournament_id=1, fencer=fencer)
    with pytest.raises(ValueError):
        entry.set_de_seed(0)

def test_set_de_seed_invalid_negative(fencer):
    entry = TournamentEntry(id=1, tournament_id=1, fencer=fencer)
    with pytest.raises(ValueError):
        entry.set_de_seed(-7)

def test_display_name_method(fencer):
    entry = TournamentEntry(id=1, tournament_id=1, fencer=fencer)
    assert entry.display_name() == 'Jane'

def test_entry_equality(fencer):
    entry1 = TournamentEntry(id=1, tournament_id=1, fencer=fencer, initial_seed=1)
    entry2 = TournamentEntry(id=1, tournament_id=1, fencer=fencer, initial_seed=1, de_seed=3)
    assert entry1 == entry2

def test_entry_inequality(fencer):
    entry1 = TournamentEntry(id=1, tournament_id=1, fencer=fencer, initial_seed=1)
    entry2 = TournamentEntry(id=2, tournament_id=1, fencer=fencer, initial_seed=1)
    assert entry1 != entry2