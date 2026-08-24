import pytest

from matches.match import Match
from matches.poule_match import PouleMatch


# --- Fixtures ---
@pytest.fixture
def poule_match(entry1, entry2):
    return PouleMatch(entry1, entry2, 1, 1, 1)


# --- Test Match Abstract Base Class ---
def test_match_cannot_instantiate_abstract_class():
    with pytest.raises(TypeError):
        Match(10)


### Test Match through a PouleMatch object ###

# --- Test Initialization and Validation ---
def test_match_creation_attributes(entry1, entry2):
    match = PouleMatch(entry1, entry2, 1, 1, 1, score_to_win=10)

    assert match.score_to_win == 10
    
    assert match.score1 is None
    assert match.score2 is None
    assert match.score == (None, None)

    assert match.winner_index is None
    assert match.loser_index is None

    assert not match._completed
    assert not match.is_complete()
    assert match.is_incomplete()

@pytest.mark.parametrize('invalid_score_to_win_type', [None, False, True, 'ten', 15.0, [], (), {}])
def test_match_creation_invalid_score_to_win_type(entry1, entry2, invalid_score_to_win_type):
    with pytest.raises(TypeError):
        PouleMatch(entry1, entry2, 1, 1, 1, score_to_win=invalid_score_to_win_type)

@pytest.mark.parametrize('invalid_score_to_win_value', [-15, -10, -5, -1, 0])
def test_match_creation_invalid_score_to_win_value(entry1, entry2, invalid_score_to_win_value):
    with pytest.raises(ValueError):
        PouleMatch(entry1, entry2, 1, 1, 1, score_to_win=invalid_score_to_win_value)

# --- Test Score Recording Methods ---
@pytest.mark.parametrize(('valid_score1', 'valid_score2'), [(1, 5), (5, 2), (3, 4), (4, 1), (5, 4)])
def test_match_record_score_valid_scores(poule_match, valid_score1, valid_score2):
    poule_match.record_score(valid_score1, valid_score2)

    assert poule_match.score1 == valid_score1
    assert poule_match.score2 == valid_score2
    assert poule_match.score == (valid_score1, valid_score2)

    assert poule_match._completed
    assert poule_match.is_complete()

@pytest.mark.parametrize('invalid_score_type', [None, False, True, 0.0, 1.0, 5.0, 'five', [], (), {}])
def test_match_record_score_invalid_score_type(poule_match, invalid_score_type):
    with pytest.raises(TypeError):
        poule_match.record_score(invalid_score_type, 0)

    with pytest.raises(TypeError):
        poule_match.record_score(0, invalid_score_type)

    with pytest.raises(TypeError):
        poule_match.record_score(invalid_score_type, invalid_score_type)

@pytest.mark.parametrize('invalid_score_value', [-6, -1, 6, 10])
def test_match_record_score_invalid_score_out_of_bounds(poule_match, invalid_score_value):
    with pytest.raises(ValueError):
        poule_match.record_score(invalid_score_value, 0)

    with pytest.raises(ValueError):
        poule_match.record_score(0, invalid_score_value)

    with pytest.raises(ValueError):
        poule_match.record_score(invalid_score_value, invalid_score_value)

@pytest.mark.parametrize(('score1', 'score2'), [(0,0), (1,1), (2,2), (3,3), (4,4), (5,5)])
def test_match_record_score_invalid_equal_scores(poule_match, score1, score2):
    with pytest.raises(ValueError, match='cannot be equal'):
        poule_match.record_score(score1, score2)

# --- Test State Change Methods ---
def test_match_reset(poule_match):
    poule_match.record_score(5, 1)
    poule_match.reset()

    assert poule_match.score1 is None
    assert poule_match.score2 is None
    assert poule_match.is_incomplete()

# --- Test Winner/Loser Index Properties ---
def test_match_winner_property_score1_is_greater(poule_match):
    poule_match.record_score(5, 2)
    assert poule_match.winner_index == 0

def test_match_winner_property_score2_is_greater(poule_match):
    poule_match.record_score(3, 5)
    assert poule_match.winner_index == 1

def test_match_loser_property_score1_is_greater(poule_match):
    poule_match.record_score(5, 1)
    assert poule_match.loser_index == 1

def test_match_loser_property_score2_is_greater(poule_match):
    poule_match.record_score(4, 5)
    assert poule_match.loser_index == 0
