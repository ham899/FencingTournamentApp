import pytest

import factories

from matches.poule_match import PouleMatch
from matches.tournament_match import TournamentMatch


# --- Constants ---
from constants import TOURNY_ID1, TOURNY_ID2
INDEX_VALUES = [0, 1]
INVALID_INDEX_TYPES = [None, '0', 1.0, False, True, [], (), {}]
INVALID_INDEX_VALUES = [-100, -1, 2, 100]


# --- Fixtures ---
@pytest.fixture
def poule_match(entry1, entry2):
    return PouleMatch(entry1, entry2, 1, 1, 1)


# --- Test TournamentMatch Abstract Base Class ---
def test_tournament_match_cannot_instantiate(entry1, entry2):
    with pytest.raises(TypeError):
        TournamentMatch(15, entry1, entry2)


### Test TournamentMatch through PouleMatch ###
# ------------------------------------------- #

# --- Initialization and Validation Tests ---
def test_tournament_match_creation_valid_poule_match(entry1, entry2):
    poule_match = PouleMatch(entry1, entry2, 1, 1, 1)

    assert poule_match.score_to_win == 5

    assert poule_match.score == (None, None)

    assert poule_match.entry1 == entry1
    assert poule_match.entry2 == entry2

    assert poule_match.forfeited_index is None
    assert not poule_match.is_forfeit()

    assert poule_match.tournament_id == entry1.tournament_id
    assert poule_match.tournament_id == entry2.tournament_id

    assert poule_match.fencer1 == entry1.fencer
    assert poule_match.fencer2 == entry2.fencer

    assert poule_match.entries == (entry1, entry2)

@pytest.mark.parametrize('invalid_entry_type', ['Ben', 0, 1, 10.0, -7, False, True, [], (), {}, object()])
def test_tournament_match_creation_invalid_entry_type(entry1, entry2, invalid_entry_type):
    with pytest.raises(TypeError):
        PouleMatch(invalid_entry_type, entry2, 1, 1, 1)

    with pytest.raises(TypeError):
        PouleMatch(entry1, invalid_entry_type, 1, 1, 1)

    with pytest.raises(TypeError):
        PouleMatch(invalid_entry_type, invalid_entry_type, 1, 1, 1)

def test_tournament_match_creation_invalid_entries_equal_entries(entry1):
    with pytest.raises(ValueError):
        PouleMatch(entry1, entry1, 1, 1, 1)

def test_tournament_match_creation_invalid_entries_same_fencer():
    fencer = factories.make_fencer(1, 'John')
    entry1 = factories.make_tournament_entry(1, TOURNY_ID1, fencer)    
    entry2 = factories.make_tournament_entry(2, TOURNY_ID1, fencer)

    with pytest.raises(ValueError):
        PouleMatch(entry1, entry2, 1, 1, 1)

def test_tournament_match_creation_invalid_entries_different_tournament_ids():
    entry1 = factories.make_tournament_entry(1, TOURNY_ID1, factories.make_fencer(1, 'John'))
    entry2 = factories.make_tournament_entry(2, TOURNY_ID2, factories.make_fencer(2, 'Jill'))

    with pytest.raises(ValueError):
        PouleMatch(entry1, entry2, 1, 1, 1)


# --- Predicate Method Tests ---
def test_tournament_match_has_entry_true(entry1, poule_match):
    assert poule_match.has_entry(entry1)

def test_tournament_match_has_entry_false(entry3, poule_match):
    assert not poule_match.has_entry(entry3)


# --- Entry Access Method Tests ---
def test_tournament_match_entry_at(poule_match):
    assert poule_match.entry_at(0) == poule_match.entry1
    assert poule_match.entry_at(1) == poule_match.entry2

@pytest.mark.parametrize('invalid_index_value', INVALID_INDEX_VALUES)
def test_tournament_match_entry_at_invalid_index(poule_match, invalid_index_value):
    with pytest.raises(ValueError):
        poule_match.entry_at(invalid_index_value)

def test_tournament_match_opponent_entry_of_index(poule_match):
    assert poule_match.opponent_entry_of_index(0) == poule_match.entry2
    assert poule_match.opponent_entry_of_index(1) == poule_match.entry1

@pytest.mark.parametrize('invalid_index_value', INVALID_INDEX_VALUES)
def test_tournament_match_opponent_entry_of_index_invalid_index(poule_match, invalid_index_value):
    with pytest.raises(ValueError):
        poule_match.opponent_entry_of_index(invalid_index_value)


# --- State Change Method Tests ---
def test_tournament_match_reset(poule_match):
    assert poule_match.score1 is None
    assert poule_match.score2 is None
    assert not poule_match._completed
    assert poule_match.forfeited_index is None

    poule_match.record_score(5, 2)
    poule_match.reset()

    assert poule_match.score1 is None
    assert poule_match.score2 is None
    assert not poule_match._completed
    assert poule_match.forfeited_index is None


# --- Result Recording Method Tests ---
def test_tournament_match_record_score_invalid_is_forfeit(poule_match):
    poule_match.record_forfeit(0)

    with pytest.raises(ValueError):
        poule_match.record_score(5, 3)

def test_tournament_match_replace_with_score_when_forfeit(poule_match):
    poule_match.record_forfeit(1)
    poule_match.replace_with_score(5, 3)

    assert poule_match.score == (5, 3)
    assert poule_match.forfeited_index is None
    assert poule_match.is_complete()
    assert not poule_match.is_forfeit()

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_tournament_match_record_forfeit(poule_match, forfeiting_index):
    poule_match.record_forfeit(forfeiting_index)

    assert poule_match.forfeited_index == forfeiting_index
    assert poule_match.is_complete()
    assert poule_match.is_forfeit()

def test_tournament_match_forfeit_cannot_forfeit_a_completed_match_scored_match(poule_match):
    poule_match.record_score(5, 1)
    
    with pytest.raises(ValueError):
        poule_match.record_forfeit(1)

def test_tournament_match_forfeit_cannot_forfeit_a_completed_match_forfeited_match(poule_match):
    poule_match.record_forfeit(0)
    
    with pytest.raises(ValueError):
        poule_match.record_forfeit(1)

@pytest.mark.parametrize('invalid_forfeiting_index_type', INVALID_INDEX_TYPES)
def test_tournament_match_forfeit_invalid_forfeiting_index_type(poule_match, invalid_forfeiting_index_type):
    with pytest.raises(TypeError):
        poule_match.record_forfeit(invalid_forfeiting_index_type)

@pytest.mark.parametrize('invalid_forfeiting_index_value', INVALID_INDEX_VALUES)
def test_tournament_match_forfeit_invalid_forfeiting_index_value(poule_match, invalid_forfeiting_index_value):
    with pytest.raises(ValueError):
        poule_match.record_forfeit(invalid_forfeiting_index_value)

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_tournament_match_replace_with_forfeit(poule_match, forfeiting_index):
    poule_match.record_score(5, 3)

    assert poule_match.score == (5, 3)
    assert poule_match.forfeited_index is None
    assert poule_match.is_complete()
    assert not poule_match.is_forfeit()

    poule_match.replace_with_forfeit(forfeiting_index)

    score1 = 0 if forfeiting_index == 0 else 5
    score2 = 0 if forfeiting_index == 1 else 5

    assert poule_match.score == (score1, score2)
    assert poule_match.forfeited_index == forfeiting_index
    assert poule_match.is_complete()
    assert poule_match.is_forfeit()

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_tournament_match_replace_with_forfeit_replace_a_forfeited_match(poule_match, forfeiting_index):
    poule_match.record_forfeit(forfeiting_index)

    score1_original = 0 if forfeiting_index == 0 else 5
    score2_original = 0 if forfeiting_index == 1 else 5

    assert poule_match.score == (score1_original, score2_original)
    assert poule_match.forfeited_index == forfeiting_index
    assert poule_match.is_complete()
    assert poule_match.is_forfeit()

    poule_match.replace_with_forfeit(1 - forfeiting_index)

    score1_new = 0 if (1 - forfeiting_index) == 0 else 5
    score2_new = 0 if (1 - forfeiting_index) == 1 else 5

    assert poule_match.score == (score1_new, score2_new)
    assert poule_match.forfeited_index == 1 - forfeiting_index
    assert poule_match.is_complete()
    assert poule_match.is_forfeit()

@pytest.mark.parametrize('invalid_forfeiting_index_type', INVALID_INDEX_TYPES)
def test_tournament_match_replace_with_forfeit_invalid_forfeiting_index_type(poule_match, invalid_forfeiting_index_type):
    poule_match.record_score(3, 5)

    with pytest.raises(TypeError):
        poule_match.replace_with_forfeit(invalid_forfeiting_index_type)

@pytest.mark.parametrize('invalid_forfeiting_index_value', INVALID_INDEX_VALUES)
def test_tournament_match_replace_with_forfeit_invalid_forfeiting_index_value(poule_match, invalid_forfeiting_index_value):
    poule_match.record_score(3, 5)

    with pytest.raises(ValueError):
        poule_match.replace_with_forfeit(invalid_forfeiting_index_value)

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_tournament_match_replace_with_forfeit_cannot_replace_a_match_with_no_result(poule_match, forfeiting_index):
    with pytest.raises(ValueError):
        poule_match.replace_with_forfeit(forfeiting_index)


# --- Test Winner/Loser Querying Properties ---
def test_tournament_match_winner_index_property_entry1_wins(poule_match):
    poule_match.record_score(5, 2)
    assert poule_match.winner_index == 0

def test_tournament_match_winner_index_property_entry2_wins(poule_match):
    poule_match.record_score(2, 5)
    assert poule_match.winner_index == 1

def test_tournament_match_winner_index_property_entry1_forfeits(poule_match):
    poule_match.record_forfeit(0)
    assert poule_match.winner_index == 1

def test_tournament_match_winner_index_property_entry2_forfeits(poule_match):
    poule_match.record_forfeit(1)
    assert poule_match.winner_index == 0

def test_tournament_match_loser_index_property_entry1_loses(poule_match):
    poule_match.record_score(2, 5)
    assert poule_match.loser_index == 0

def test_tournament_match_loser_index_property_entry2_loses(poule_match):
    poule_match.record_score(5, 2)
    assert poule_match.loser_index == 1

def test_tournament_match_loser_index_property_entry1_forfeits(poule_match):
    poule_match.record_forfeit(0)
    assert poule_match.loser_index == 0

def test_tournament_match_loser_index_property_entry2_forfeits(poule_match):
    poule_match.record_forfeit(1)
    assert poule_match.loser_index == 1

def test_tournament_match_winner_and_loser_index_properties_after_modifying_match_results(poule_match):
    poule_match.record_score(2, 5)

    assert poule_match.winner_index == 1
    assert poule_match.loser_index == 0

    poule_match.replace_with_forfeit(0)

    assert poule_match.winner_index == 1
    assert poule_match.loser_index == 0

    poule_match.replace_with_score(5, 3)

    assert poule_match.winner_index == 0
    assert poule_match.loser_index == 1

    poule_match.replace_with_forfeit(1)

    assert poule_match.winner_index == 0
    assert poule_match.loser_index == 1

    poule_match.reset()

    assert poule_match.winner_index is None
    assert poule_match.loser_index is None
    assert poule_match.score == (None, None)

def test_tournament_match_winner_property_entry1_wins(poule_match):
    poule_match.record_score(5, 2)
    assert poule_match.winner is poule_match.entry1

def test_tournament_match_winner_property_entry2_wins(poule_match):
    poule_match.record_score(2, 5)
    assert poule_match.winner is poule_match.entry2

def test_tournament_match_winner_property_entry1_forfeits(poule_match):
    poule_match.record_forfeit(0)
    assert poule_match.winner is poule_match.entry2

def test_tournament_match_winner_property_entry2_forfeits(poule_match):
    poule_match.record_forfeit(1)
    assert poule_match.winner is poule_match.entry1

def test_tournament_match_loser_property_entry1_loses(poule_match):
    poule_match.record_score(2, 5)
    assert poule_match.loser is poule_match.entry1

def test_tournament_match_loser_property_entry2_loses(poule_match):
    poule_match.record_score(5, 2)
    assert poule_match.loser is poule_match.entry2

def test_tournament_match_loser_property_entry1_forfeits(poule_match):
    poule_match.record_forfeit(0)
    assert poule_match.loser is poule_match.entry1

def test_tournament_match_loser_property_entry2_forfeits(poule_match):
    poule_match.record_forfeit(1)
    assert poule_match.loser is poule_match.entry2

def test_tournament_match_winner_and_loser_properties_after_modifying_match_results(poule_match):
    poule_match.record_score(2, 5)

    assert poule_match.winner is poule_match.entry2
    assert poule_match.loser is poule_match.entry1

    poule_match.replace_with_forfeit(0)

    assert poule_match.winner is poule_match.entry2
    assert poule_match.loser is poule_match.entry1

    poule_match.replace_with_score(5, 3)

    assert poule_match.winner is poule_match.entry1
    assert poule_match.loser is poule_match.entry2

    poule_match.replace_with_forfeit(1)

    assert poule_match.winner is poule_match.entry1
    assert poule_match.loser is poule_match.entry2

    poule_match.reset()

    assert poule_match.winner is None
    assert poule_match.loser is None
    assert poule_match.score == (None, None)
