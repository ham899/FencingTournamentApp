import pytest

import factories

from matches.poule_match import PouleMatch


# --- Constants ---
from constants import TOURNY_ID2

INVALID_NUMBER_TYPES = [None, 'first', 0.0, False, True, [], (), {}, object()]
INVALID_NUMBER_VALUES = [-5, -1, 0]


# --- Fixtures ---
@pytest.fixture
def poule_match(entry1, entry2):
    return PouleMatch(
        entry1=entry1, 
        entry2=entry2, 
        match_number=1, 
        poule_number=1, 
        stage_number=1
    )


# --- Initialization and Validation Tests ---
def test_poule_match_creation_valid_with_defaults(entry1, entry2):
    match = PouleMatch(
        entry1=entry1, 
        entry2=entry2, 
        match_number=1, 
        poule_number=1, 
        stage_number=1
    )

    assert match.entry1 == entry1
    assert match.entry2 == entry2

    assert match.score_to_win == 5

    assert match.match_number == 1
    assert match.match_index == 0

    assert match.poule_number == 1
    assert match.poule_index == 0

    assert match.stage_number == 1
    assert match.stage_index == 0

    assert match.tournament_id == entry1.tournament_id
    assert match.tournament_id == entry2.tournament_id

    assert match.match_type == 'poule'

def test_poule_match_creation_valid_no_defaults(entry1, entry2):
    match = PouleMatch(
        entry1=entry1, 
        entry2=entry2, 
        match_number=1, 
        poule_number=1, 
        stage_number=1, 
        score_to_win=8
    )

    assert match.entry1 == entry1
    assert match.entry2 == entry2

    assert match.score_to_win == 8

    assert match.match_number == 1
    assert match.match_index == 0

    assert match.poule_number == 1
    assert match.poule_index == 0

    assert match.stage_number == 1
    assert match.stage_index == 0

    assert match.tournament_id == entry1.tournament_id
    assert match.tournament_id == entry2.tournament_id

    assert match.match_type == 'poule'

@pytest.mark.parametrize('invalid_match_number_type', INVALID_NUMBER_TYPES)
def test_poule_match_creation_invalid_match_number_type(entry1, entry2, invalid_match_number_type):
    with pytest.raises(TypeError):
        PouleMatch(entry1, entry2, invalid_match_number_type, 1, 1)

@pytest.mark.parametrize('invalid_match_number_value', INVALID_NUMBER_VALUES)
def test_poule_match_creation_invalid_match_numer_value(entry1, entry2, invalid_match_number_value):
    with pytest.raises(ValueError):
        PouleMatch(entry1, entry2, invalid_match_number_value, 1, 1)

@pytest.mark.parametrize('invalid_poule_number_type', INVALID_NUMBER_TYPES)
def test_poule_match_creation_invalid_poule_number_type(entry1, entry2, invalid_poule_number_type):
    with pytest.raises(TypeError):
        PouleMatch(entry1, entry2, 1, invalid_poule_number_type, 1)

@pytest.mark.parametrize('invalid_poule_number_value', INVALID_NUMBER_VALUES)
def test_poule_match_creation_invalid_poule_number_value(entry1, entry2, invalid_poule_number_value):
    with pytest.raises(ValueError):
        PouleMatch(entry1, entry2, 1, invalid_poule_number_value, 1)

@pytest.mark.parametrize('invalid_stage_number_type', INVALID_NUMBER_TYPES)
def test_poule_match_creation_invalid_stage_number_type(entry1, entry2, invalid_stage_number_type):
    with pytest.raises(TypeError):
        PouleMatch(entry1, entry2, 1, 1, invalid_stage_number_type)

@pytest.mark.parametrize('invalid_stage_number_value', INVALID_NUMBER_VALUES)
def test_poule_match_creation_invalid_stage_number_value(entry1, entry2, invalid_stage_number_value):
    with pytest.raises(ValueError):
        PouleMatch(entry1, entry2, 1, 1, invalid_stage_number_value)


# --- Equality Tests ---
def test_poule_match_equality(entry1, entry2):
    match1 = PouleMatch(entry1, entry2, 1, 1, 1)
    match2 = PouleMatch(entry1, entry2, 1, 1, 1)

    assert match1 is match1
    assert match2 is match2
    assert match1 is not match2

    assert match1 == match2

@pytest.mark.parametrize('non_poule_match_object', [None, 0, 1.0, False, True, 'Steve', [], (), {}, object()])
def test_poule_match_inequality_different_object(poule_match, non_poule_match_object):
    assert poule_match != non_poule_match_object

def test_poule_match_inequality_different_match_number(entry1, entry2, entry3, entry4):
    match1 = PouleMatch(entry1, entry2, match_number=1, poule_number=1, stage_number=1)
    match2 = PouleMatch(entry3, entry4, match_number=2, poule_number=1, stage_number=1)

    assert match1 != match2

def test_poule_match_inequality_different_poule_number(entry1, entry2, entry3, entry4):
    match1 = PouleMatch(entry1, entry2, match_number=1, poule_number=1, stage_number=1)
    match2 = PouleMatch(entry3, entry4, match_number=1, poule_number=2, stage_number=1)

    assert match1 != match2

def test_poule_match_inequality_different_stage_number(entry1, entry2, entry3, entry4):
    match1 = PouleMatch(entry1, entry2, match_number=1, poule_number=1, stage_number=1)
    match2 = PouleMatch(entry3, entry4, match_number=1, poule_number=1, stage_number=2)

    assert match1 != match2

def test_poule_match_inequality_different_tournament_id(entry1, entry2):
    entry3 = factories.make_tournament_entry(3, TOURNY_ID2, factories.make_fencer(3, 'Jim'))
    entry4 = factories.make_tournament_entry(4, TOURNY_ID2, factories.make_fencer(4, 'Alfred'))

    match1 = PouleMatch(entry1, entry2, match_number=1, poule_number=1, stage_number=1)
    match2 = PouleMatch(entry3, entry4, match_number=1, poule_number=1, stage_number=1)

    assert match1 != match2


# --- Poule-specific Forfeit Tests ---
@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_poule_match_record_forfeit_default_score_to_win(poule_match, forfeiting_index):
    poule_match.record_forfeit(forfeiting_index)

    assert poule_match.forfeited_index == forfeiting_index
    assert poule_match.winner_index == 1 - forfeiting_index
    assert poule_match.loser_index == forfeiting_index
    assert poule_match.is_forfeit()
    assert poule_match.is_complete()

    score1 = 0 if forfeiting_index == 0 else poule_match.score_to_win
    score2 = 0 if forfeiting_index == 1 else poule_match.score_to_win

    assert poule_match.score == (score1, score2)

@pytest.mark.parametrize(('forfeiting_index', 'score_to_win'), [(0, 1), (1, 1), (0, 8), (1, 8), (0, 10), (1, 10)])
def test_poule_match_record_forfeit_custom_score_to_win(entry1, entry2, forfeiting_index, score_to_win):
    match = PouleMatch(entry1, entry2, 1, 1, 1, score_to_win=score_to_win)
    match.record_forfeit(forfeiting_index)

    assert match.forfeited_index == forfeiting_index
    assert match.winner_index == 1 - forfeiting_index
    assert match.loser_index == forfeiting_index
    assert match.is_forfeit()
    assert match.is_complete()

    score1 = 0 if forfeiting_index == 0 else match.score_to_win
    score2 = 0 if forfeiting_index == 1 else match.score_to_win

    assert match.score == (score1, score2)

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_poule_match_replace_with_forfeit_default_score_to_win(poule_match, forfeiting_index):
    poule_match.record_score(1, 5)

    assert poule_match.is_complete()
    assert poule_match.score == (1, 5)
    assert poule_match.forfeited_index is None

    poule_match.replace_with_forfeit(forfeiting_index)

    assert poule_match.forfeited_index == forfeiting_index
    assert poule_match.winner_index == 1 - forfeiting_index
    assert poule_match.loser_index == forfeiting_index
    assert poule_match.is_forfeit()
    assert poule_match.is_complete()

    score1 = 0 if forfeiting_index == 0 else poule_match.score_to_win
    score2 = 0 if forfeiting_index == 1 else poule_match.score_to_win

    assert poule_match.score == (score1, score2)

@pytest.mark.parametrize(('forfeiting_index', 'score_to_win'), [(0, 1), (1, 1), (0, 8), (1, 8), (0, 10), (1, 10)])
def test_poule_match_replace_with_forfeit_custom_score_to_win(entry1, entry2, forfeiting_index, score_to_win):
    match = PouleMatch(entry1, entry2, 1, 1, 1, score_to_win=score_to_win)
    match.record_score(score_to_win - 1, score_to_win)

    assert match.is_complete()
    assert match.score == (score_to_win - 1, score_to_win)
    assert match.forfeited_index is None

    match.replace_with_forfeit(forfeiting_index)

    assert match.forfeited_index == forfeiting_index
    assert match.winner_index == 1 - forfeiting_index
    assert match.loser_index == forfeiting_index
    assert match.is_forfeit()
    assert match.is_complete()

    score1 = 0 if forfeiting_index == 0 else match.score_to_win
    score2 = 0 if forfeiting_index == 1 else match.score_to_win

    assert match.score == (score1, score2)
