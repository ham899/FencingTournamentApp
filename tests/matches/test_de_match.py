import pytest

import factories

from matches.de_match import DEMatch


# --- Constants ---
from constants import TOURNY_ID1, TOURNY_ID2

INVALID_INTEGER_TYPES = [None, '0', 0.0, False, True, [], (), {}, object()]
INVALID_POSITION_NUMBERS = [-5, -1, 0]


# --- Fixtures ---
@pytest.fixture
def de_match(entry1, entry2):
    return DEMatch(entry1, entry2, 1, 1, 1)


# --- Initialization and Validation Tests ---
def test_de_match_creation_valid_with_defaults(entry1, entry2):
    match = DEMatch(
        entry1=entry1,
        entry2=entry2,
        match_number=1,
        round_number=1,
        stage_number=1
    )

    assert match.match_number == 1
    assert match.round_number == 1
    assert match.stage_number == 1
    assert match.tournament_id == TOURNY_ID1
    
    assert match.score1 is None
    assert match.score2 is None
    assert match.score_to_win == 15

    assert match.entry1 is entry1
    assert match.entry2 is entry2

    assert match.fencer1 is entry1.fencer
    assert match.fencer2 is entry2.fencer
    
    assert not match._completed
    assert match.forfeited_index is None
    
    assert match.match_type == 'de'

def test_de_match_creation_valid_no_defaults(entry1, entry2):
    match = DEMatch(
        entry1=entry1,
        entry2=entry2,
        match_number=1,
        round_number=1,
        stage_number=1,
        score_to_win=8
    )
    
    assert match.match_number == 1
    assert match.round_number == 1
    assert match.stage_number == 1
    assert match.tournament_id == TOURNY_ID1
    
    assert match.score1 is None
    assert match.score2 is None
    assert match.score_to_win == 8

    assert match.entry1 is entry1
    assert match.entry2 is entry2

    assert match.fencer1 is entry1.fencer
    assert match.fencer2 is entry2.fencer
    
    assert not match._completed
    assert match.forfeited_index is None
    
    assert match.match_type == 'de'

@pytest.mark.parametrize('invalid_match_number_type', INVALID_INTEGER_TYPES)
def test_de_match_creation_invalid_match_number_type(entry1, entry2, invalid_match_number_type):
    with pytest.raises(TypeError):
        DEMatch(
            entry1=entry1,
            entry2=entry2,
            match_number=invalid_match_number_type,
            round_number=1,
            stage_number=1
        )

@pytest.mark.parametrize('invalid_match_number_value', INVALID_POSITION_NUMBERS)
def test_de_match_creation_invalid_match_number_value(entry1, entry2, invalid_match_number_value):
    with pytest.raises(ValueError):
        DEMatch(
            entry1=entry1,
            entry2=entry2,
            match_number=invalid_match_number_value,
            round_number=1,
            stage_number=1
        )

@pytest.mark.parametrize('invalid_round_number_type', INVALID_INTEGER_TYPES)
def test_de_match_creation_invalid_round_number_type(entry1, entry2, invalid_round_number_type):
    with pytest.raises(TypeError):
        DEMatch(
            entry1=entry1,
            entry2=entry2,
            match_number=1,
            round_number=invalid_round_number_type,
            stage_number=1
        )

@pytest.mark.parametrize('invalid_round_number_value', INVALID_POSITION_NUMBERS)
def test_de_match_creation_invalid_round_number_value(entry1, entry2, invalid_round_number_value):
    with pytest.raises(ValueError):
        DEMatch(
            entry1=entry1,
            entry2=entry2,
            match_number=1,
            round_number=invalid_round_number_value,
            stage_number=1
        )

@pytest.mark.parametrize('invalid_stage_number_type', INVALID_INTEGER_TYPES)
def test_de_match_creation_invalid_stage_number_type(entry1, entry2, invalid_stage_number_type):
    with pytest.raises(TypeError):
        DEMatch(
            entry1=entry1,
            entry2=entry2,
            match_number=1,
            round_number=1,
            stage_number=invalid_stage_number_type
        )

@pytest.mark.parametrize('invalid_stage_number_value', INVALID_POSITION_NUMBERS)
def test_de_match_creation_invalid_stage_number_value(entry1, entry2, invalid_stage_number_value):
    with pytest.raises(ValueError):
        DEMatch(
            entry1=entry1,
            entry2=entry2,
            match_number=1,
            round_number=1,
            stage_number=invalid_stage_number_value
        )


# --- Equality Tests ---
def test_de_match_equality(entry1, entry2):
    match1 = DEMatch(entry1, entry2, 1, 1, 1)
    match2 = DEMatch(entry1, entry2, 1, 1, 1)

    assert match1 is not match2
    assert match1 == match2

def test_de_match_inequality_different_tournament_ids():
    entry1_1, entry2_1 = factories.make_entries(2, TOURNY_ID1)
    entry1_2, entry2_2 = factories.make_entries(2, TOURNY_ID2)
    
    match1 = DEMatch(entry1_1, entry2_1, 1, 1, 1)
    match2 = DEMatch(entry1_2, entry2_2, 1, 1, 1)

    assert match1 != match2

def test_de_match_inequality_different_stage_number(entry1, entry2):
    match1 = DEMatch(entry1, entry2, 1, 1, 1)
    match2 = DEMatch(entry1, entry2, 1, 1, 2)

    assert match1 != match2

def test_de_match_equality_different_round_number(entry1, entry2):
    match1 = DEMatch(entry1, entry2, 1, 1, 1)
    match2 = DEMatch(entry1, entry2, 1, 2, 1)

    assert match1 != match2

def test_de_match_equality_different_match_number(entry1, entry2):
    match1 = DEMatch(entry1, entry2, 1, 1, 1)
    match2 = DEMatch(entry1, entry2, 2, 1, 1)

    assert match1 != match2
    

# --- TournamentMatch Hook Implementation Tests ---
def test_de_match__assign_forfeit_scores_entry1_forfeits(de_match):
    de_match.forfeit(0)

    assert de_match.is_forfeit()
    assert de_match.is_complete()
    assert de_match.forfeited_index == 0

    assert de_match.score1 is None
    assert de_match.score2 is None    

    assert de_match.winner is de_match.entry2
    assert de_match.loser is de_match.entry1

def test_de_match__assign_forfeit_scores_entry1_forfeits(de_match):
    de_match.forfeit(1)

    assert de_match.is_forfeit()
    assert de_match.is_complete()
    assert de_match.forfeited_index == 1

    assert de_match.score1 is None
    assert de_match.score2 is None    

    assert de_match.winner is de_match.entry1
    assert de_match.loser is de_match.entry2
