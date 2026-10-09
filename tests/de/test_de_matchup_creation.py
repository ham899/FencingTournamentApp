import pytest

import factories

from de.de_bracket_role import DEBracketRole
from de.de_matchup import DEMatchup
from matches.de_match import DEMatch


# --- Constants ---
from constants import TOURNY_ID1, TOURNY_ID2

INVALID_IDENTIFYING_NUMBER_TYPES = [None, False, True, 1.5, 'first', [], (), {}, object()]
INVALID_IDENTIFYING_NUMBER_VALUES = [-10, -1, 0]

INVALID_ENTRY_TYPES = [False, True, 0, 1.0, 'John', [], (), {}, object()]


# --- Fixtures ---
@pytest.fixture
def empty_matchup():
    return DEMatchup(
        matchup_number=1, 
        round_number=2, # Round 2 so that it is not a BYE when an entry is added 
        stage_number=1, 
        tournament_id=TOURNY_ID1
    )

@pytest.fixture
def matchup_entry1_only(entry1):
    return DEMatchup(
        matchup_number=1, 
        round_number=2, # Round 2 so that it is not a BYE 
        stage_number=1, 
        tournament_id=TOURNY_ID1, 
        entry1=entry1
    )

@pytest.fixture
def matchup_entry2_only(entry2):
    return DEMatchup(
        matchup_number=1, 
        round_number=2, # Round 2 so that it is not a BYE
        stage_number=1, 
        tournament_id=TOURNY_ID1, 
        entry2=entry2
    )

@pytest.fixture
def matchup(entry1, entry2):
    return DEMatchup(
        matchup_number=1, 
        round_number=1, 
        stage_number=1, 
        tournament_id=TOURNY_ID1, 
        entry1=entry1, 
        entry2=entry2
    )

# --- Initialization and Validation Tests ---
def test_de_matchup_creation_valid_no_entries():
    matchup_number, round_number, stage_number = 1, 1, 1

    matchup = DEMatchup(
        matchup_number=matchup_number, 
        round_number=round_number, 
        stage_number=stage_number, 
        tournament_id=TOURNY_ID1
    )

    assert matchup.matchup_number == matchup_number
    assert matchup.round_number == round_number
    assert matchup.stage_number == stage_number
    assert matchup.tournament_id == TOURNY_ID1

    assert matchup.entry1 is None
    assert matchup.entry2 is None
    assert matchup.match is None

    assert matchup.score_to_win == 15
    assert matchup.bracket_role == DEBracketRole.MAIN

    assert matchup.winner is None
    assert matchup.loser is None

def test_de_matchup_creation_valid_entry1_provided(entry1):
    matchup_number, round_number, stage_number = 2, 2, 2

    matchup = DEMatchup(
        matchup_number=matchup_number, 
        round_number=round_number, 
        stage_number=stage_number, 
        tournament_id=TOURNY_ID1, 
        entry1=entry1
    )

    assert matchup.matchup_number == matchup_number
    assert matchup.round_number == round_number
    assert matchup.stage_number == stage_number
    assert matchup.tournament_id == TOURNY_ID1

    assert matchup.entry1 is entry1
    assert matchup.entry2 is None
    assert matchup.match is None

    assert matchup.score_to_win == 15
    assert matchup.bracket_role == DEBracketRole.MAIN

    assert matchup.winner is None
    assert matchup.loser is None

def test_de_matchup_creation_valid_bye_for_entry1(entry1):
    matchup_number, round_number, stage_number = 1, 1, 2

    matchup = DEMatchup(
        matchup_number=matchup_number, 
        round_number=round_number, 
        stage_number=stage_number, 
        tournament_id=TOURNY_ID1, 
        entry1=entry1
    )

    assert matchup.matchup_number == matchup_number
    assert matchup.round_number == round_number
    assert matchup.stage_number == stage_number
    assert matchup.tournament_id == TOURNY_ID1

    assert matchup.entry1 is entry1
    assert matchup.entry2 is None
    assert matchup.match is None

    assert matchup.score_to_win == 15
    assert matchup.bracket_role == DEBracketRole.MAIN

    assert matchup.winner is entry1
    assert matchup.loser is None

def test_de_matchup_creation_valid_entry2_provided(entry2):
    matchup_number, round_number, stage_number = 3, 3, 3

    matchup = DEMatchup(
        matchup_number=matchup_number, 
        round_number=round_number, 
        stage_number=stage_number, 
        tournament_id=TOURNY_ID1, 
        entry2=entry2
    )

    assert matchup.matchup_number == matchup_number
    assert matchup.round_number == round_number
    assert matchup.stage_number == stage_number
    assert matchup.tournament_id == TOURNY_ID1

    assert matchup.entry1 is None
    assert matchup.entry2 is entry2
    assert matchup.match is None

    assert matchup.score_to_win == 15
    assert matchup.bracket_role == DEBracketRole.MAIN

    assert matchup.winner is None
    assert matchup.loser is None

def test_de_matchup_creation_valid_bye_for_entry2(entry2):
    matchup_number, round_number, stage_number = 8, 1, 2

    matchup = DEMatchup(
        matchup_number=matchup_number, 
        round_number=round_number, 
        stage_number=stage_number, 
        tournament_id=TOURNY_ID1, 
        entry2=entry2
    )

    assert matchup.matchup_number == matchup_number
    assert matchup.round_number == round_number
    assert matchup.stage_number == stage_number
    assert matchup.tournament_id == TOURNY_ID1

    assert matchup.entry1 is None
    assert matchup.entry2 is entry2
    assert matchup.match is None

    assert matchup.score_to_win == 15
    assert matchup.bracket_role == DEBracketRole.MAIN

    assert matchup.winner is entry2
    assert matchup.loser is None

def test_de_matchup_creation_valid_both_entries_provided(entry1, entry2):
    matchup_number, round_number, stage_number = 3, 2, 2

    matchup = DEMatchup(
        matchup_number=matchup_number,
        round_number=round_number,
        stage_number=stage_number,
        tournament_id=TOURNY_ID1,
        entry1=entry1,
        entry2=entry2
    )

    assert matchup.matchup_number == matchup_number
    assert matchup.round_number == round_number
    assert matchup.stage_number == stage_number
    assert matchup.tournament_id == TOURNY_ID1

    assert matchup.entry1 is entry1
    assert matchup.entry2 is entry2

    assert matchup.score_to_win == 15
    assert matchup.bracket_role == DEBracketRole.MAIN

    assert matchup.winner is None
    assert matchup.loser is None

    assert isinstance(matchup.match, DEMatch)
    assert matchup.match.entry1 is entry1
    assert matchup.match.entry2 is entry2
    assert matchup.match.match_number == matchup_number
    assert matchup.match.round_number == round_number
    assert matchup.match.stage_number == stage_number
    assert matchup.match.score_to_win == matchup.score_to_win
    assert matchup.match.bracket_role == matchup.bracket_role

def test_de_matchup_creation_score_to_win_propagation(entry1, entry2):
    matchup_number, round_number, stage_number = 4, 3, 3
    score_to_win = 10

    matchup = DEMatchup(
        matchup_number=matchup_number,
        round_number=round_number,
        stage_number=stage_number,
        tournament_id=TOURNY_ID1,
        entry1=entry1,
        entry2=entry2,
        score_to_win=score_to_win
    )

    assert matchup.score_to_win == score_to_win
    assert matchup.match.score_to_win == score_to_win

def test_de_matchup_creation_bracket_role_propagation(entry1, entry2):
    matchup_number, round_number, stage_number = 5, 4, 4
    bracket_role = DEBracketRole.CONSOLATION

    matchup = DEMatchup(
        matchup_number=matchup_number,
        round_number=round_number,
        stage_number=stage_number,
        tournament_id=TOURNY_ID1,
        entry1=entry1,
        entry2=entry2,
        bracket_role=bracket_role
    )

    assert matchup.bracket_role == bracket_role
    assert matchup.match.bracket_role == bracket_role

@pytest.mark.parametrize('invalid_matchup_number_type', INVALID_IDENTIFYING_NUMBER_TYPES)
def test_de_matchup_creation_invalid_matchup_number_type(invalid_matchup_number_type):
    round_number, stage_number, tournament_id = 1, 1, TOURNY_ID1
    with pytest.raises(TypeError):
        DEMatchup(invalid_matchup_number_type, round_number, stage_number, tournament_id)

@pytest.mark.parametrize('invalid_matchup_number_value', INVALID_IDENTIFYING_NUMBER_VALUES)
def test_de_matchup_creation_invalid_matchup_number_value(invalid_matchup_number_value):
    round_number, stage_number, tournament_id = 1, 1, TOURNY_ID1
    with pytest.raises(ValueError):
        DEMatchup(invalid_matchup_number_value, round_number, stage_number, tournament_id)

@pytest.mark.parametrize('invalid_round_number_type', INVALID_IDENTIFYING_NUMBER_TYPES)
def test_de_matchup_creation_invalid_round_number_type(invalid_round_number_type):
    matchup_number, stage_number, tournament_id = 1, 1, TOURNY_ID1
    with pytest.raises(TypeError):
        DEMatchup(matchup_number, invalid_round_number_type, stage_number, tournament_id)

@pytest.mark.parametrize('invalid_round_number_value', INVALID_IDENTIFYING_NUMBER_VALUES)
def test_de_matchup_creation_invalid_round_number_value(invalid_round_number_value):
    matchup_number, stage_number, tournament_id = 1, 1, TOURNY_ID1
    with pytest.raises(ValueError):
        DEMatchup(matchup_number, invalid_round_number_value, stage_number, tournament_id)

@pytest.mark.parametrize('invalid_stage_number_type', INVALID_IDENTIFYING_NUMBER_TYPES)
def test_de_matchup_creation_invalid_stage_number_type(invalid_stage_number_type):
    matchup_number, round_number, tournament_id = 1, 1, TOURNY_ID1
    with pytest.raises(TypeError):
        DEMatchup(matchup_number, round_number, invalid_stage_number_type, tournament_id)

@pytest.mark.parametrize('invalid_stage_number_value', INVALID_IDENTIFYING_NUMBER_VALUES)
def test_de_matchup_creation_invalid_stage_number_value(invalid_stage_number_value):
    matchup_number, round_number, tournament_id = 1, 1, TOURNY_ID1
    with pytest.raises(ValueError):
        DEMatchup(matchup_number, round_number, invalid_stage_number_value, tournament_id)

@pytest.mark.parametrize('invalid_tournament_id_type', INVALID_IDENTIFYING_NUMBER_TYPES)
def test_de_matchup_creation_invalid_tournament_id_type(invalid_tournament_id_type):
    matchup_number, round_number, stage_number = 1, 1, 1
    with pytest.raises(TypeError):
        DEMatchup(matchup_number, round_number, stage_number, invalid_tournament_id_type)

@pytest.mark.parametrize('invalid_tournament_id_value', INVALID_IDENTIFYING_NUMBER_VALUES)
def test_de_matchup_creation_invalid_tournament_id_value(invalid_tournament_id_value):
    matchup_number, round_number, stage_number = 1, 1, 1
    with pytest.raises(ValueError):
        DEMatchup(matchup_number, round_number, stage_number, invalid_tournament_id_value)

@pytest.mark.parametrize('invalid_entry_type', INVALID_ENTRY_TYPES)
def test_de_matchup_creation_invalid_entry1_type(invalid_entry_type):
    matchup_number, round_number, stage_number, tournament_id = 1, 1, 1, TOURNY_ID1
    with pytest.raises(TypeError):
        DEMatchup(matchup_number, round_number, stage_number, tournament_id, entry1=invalid_entry_type)

def test_de_matchup_creation_invalid_entry1_tournament_id():
    matchup_number, round_number, stage_number, tournament_id = 1, 1, 1, TOURNY_ID1
    entry = factories.make_entry_at_number(number=1, tournament_id=TOURNY_ID2)
    with pytest.raises(ValueError):
        DEMatchup(matchup_number, round_number, stage_number, tournament_id, entry1=entry)

@pytest.mark.parametrize('invalid_entry_type', INVALID_ENTRY_TYPES)
def test_de_matchup_creation_invalid_entry2_type(invalid_entry_type):
    matchup_number, round_number, stage_number, tournament_id = 1, 1, 1, TOURNY_ID1
    with pytest.raises(TypeError):
        DEMatchup(matchup_number, round_number, stage_number, tournament_id, entry2=invalid_entry_type)

def test_de_matchup_creation_invalid_entry2_tournament_id():
    matchup_number, round_number, stage_number, tournament_id = 1, 1, 1, TOURNY_ID1
    entry = factories.make_entry_at_number(number=1, tournament_id=TOURNY_ID2)
    with pytest.raises(ValueError):
        DEMatchup(matchup_number, round_number, stage_number, tournament_id, entry2=entry)

def test_de_matchup_creation_invalid_same_entry(entry1):
    matchup_number, round_number, stage_number, tournament_id = 1, 1, 1, TOURNY_ID1
    with pytest.raises(ValueError):
        DEMatchup(matchup_number, round_number, stage_number, tournament_id, entry1=entry1, entry2=entry1)

@pytest.mark.parametrize('invalid_score_to_win_type', [None, 'ten', True, False, 15.0, [], (), {}, object()])
def test_de_matchup_creation_invalid_score_to_win_type(invalid_score_to_win_type):
    matchup_number, round_number, stage_number, tournament_id = 1, 1, 1, TOURNY_ID1
    with pytest.raises(TypeError):
        DEMatchup(matchup_number, round_number, stage_number, tournament_id, score_to_win=invalid_score_to_win_type)

@pytest.mark.parametrize('invalid_score_to_win_value', [-100, -1, 0])
def test_de_matchup_creation_invalid_score_to_win_value(invalid_score_to_win_value):
    matchup_number, round_number, stage_number, tournament_id = 1, 1, 1, TOURNY_ID1
    with pytest.raises(ValueError):
        DEMatchup(matchup_number, round_number, stage_number, tournament_id, score_to_win=invalid_score_to_win_value)

@pytest.mark.parametrize('invalid_bracket_role_type', [None, 'main', 'consolation', False, True, 0, 1.0, [], (), {}, object()])
def test_de_matchup_creation_invalid_bracket_role_type(invalid_bracket_role_type):
    matchup_number, round_number, stage_number, tournament_id = 1, 1, 1, TOURNY_ID1
    with pytest.raises(TypeError):
        DEMatchup(matchup_number, round_number, stage_number, tournament_id, bracket_role=invalid_bracket_role_type)


# --- Property Tests ---
@pytest.mark.parametrize(
        ('matchup_number', 'round_number', 'stage_number', 'expected_matchup_index', 'expected_round_index', 'expected_stage_index'),
        [
            (1, 1, 1, 0, 0, 0),
            (2, 3, 4, 1, 2, 3),
            (8, 5, 2, 7, 4, 1)
        ]
)
def test_de_matchup_indices_properties(matchup_number, round_number, stage_number, expected_matchup_index, expected_round_index, expected_stage_index):
    matchup = DEMatchup(
        matchup_number=matchup_number,
        round_number=round_number,
        stage_number=stage_number,
        tournament_id=TOURNY_ID1
    )

    assert matchup.matchup_index == expected_matchup_index
    assert matchup.round_index == expected_round_index
    assert matchup.stage_index == expected_stage_index

@pytest.mark.parametrize(
    ('matchup_number', 'expected_next_index', 'expected_next_number', 'expected_entry_index'),
    [
        (1, 0, 1, 0),
        (2, 0, 1, 1),
        (3, 1, 2, 0),
        (4, 1, 2, 1),
        (7, 3, 4, 0),
        (8, 3, 4, 1)
    ]
)
def test_de_matchup_advancement_indices_properties(matchup_number, expected_next_index, expected_next_number, expected_entry_index):
    round_number, stage_number = 1, 1

    matchup = DEMatchup(
        matchup_number=matchup_number,
        round_number=round_number,
        stage_number=stage_number,
        tournament_id=TOURNY_ID1
    )

    assert matchup.next_matchup_index == expected_next_index
    assert matchup.next_matchup_number == expected_next_number
    assert matchup.next_matchup_entry_index == expected_entry_index


# --- Equality Tests ---
def test_de_matchup_equality(entry1, entry2):
    same_matchup_number, same_round_number, same_stage_number, same_tournament_id = 1, 1, 1, TOURNY_ID1

    matchup1 = DEMatchup(same_matchup_number, same_round_number, same_stage_number, same_tournament_id, entry1, entry2)
    matchup2 = DEMatchup(same_matchup_number, same_round_number, same_stage_number, same_tournament_id, entry1, entry2)

    assert matchup1 == matchup2

def test_de_matchup_equality_ignores_entries(entry1, entry2):
    same_matchup_number, same_round_number, same_stage_number, same_tournament_id = 1, 1, 1, TOURNY_ID1

    matchup1 = DEMatchup(same_matchup_number, same_round_number, same_stage_number, same_tournament_id, entry1, entry2)
    matchup2 = DEMatchup(same_matchup_number, same_round_number, same_stage_number, same_tournament_id)

    assert matchup1 == matchup2

def test_de_matchup_equality_ignores_match_results(entry1, entry2):
    same_matchup_number, same_round_number, same_stage_number, same_tournament_id = 1, 1, 1, TOURNY_ID1

    matchup1 = DEMatchup(same_matchup_number, same_round_number, same_stage_number, same_tournament_id, entry1, entry2)
    matchup2 = DEMatchup(same_matchup_number, same_round_number, same_stage_number, same_tournament_id, entry1, entry2)

    # Record a result only for the first matchup
    matchup1.record_match_score(matchup1.score_to_win, 0)

    assert matchup1 == matchup2

def test_de_matchup_inequality_different_tournament_ids():
    same_matchup_number, same_round_number, same_stage_number = 1, 1, 1

    matchup1_tournament_id, matchup2_tournament_id = TOURNY_ID1, TOURNY_ID2

    matchup1 = DEMatchup(same_matchup_number, same_round_number, same_stage_number, matchup1_tournament_id)
    matchup2 = DEMatchup(same_matchup_number, same_round_number, same_stage_number, matchup2_tournament_id)

    assert matchup1 != matchup2

def test_de_matchup_inequality_different_stage_numbers():
    same_matchup_number, same_round_number, same_tournament_id = 1, 1, TOURNY_ID1

    matchup1_stage_number, matchup2_stage_number = 1, 2

    matchup1 = DEMatchup(same_matchup_number, same_round_number, matchup1_stage_number, same_tournament_id)
    matchup2 = DEMatchup(same_matchup_number, same_round_number, matchup2_stage_number, same_tournament_id)

    assert matchup1 != matchup2

def test_de_matchup_inequality_different_round_numbers():
    same_matchup_number, same_stage_number, same_tournament_id = 1, 1, TOURNY_ID1

    matchup1_round_number, matchup2_round_number = 1, 2

    matchup1 = DEMatchup(same_matchup_number, matchup1_round_number, same_stage_number, same_tournament_id)
    matchup2 = DEMatchup(same_matchup_number, matchup2_round_number, same_stage_number, same_tournament_id)

    assert matchup1 != matchup2

def test_de_matchup_inequality_different_matchup_numbers():
    same_round_number, same_stage_number, same_tournament_id = 1, 1, TOURNY_ID1

    matchup1_matchup_number, matchup2_matchup_number = 1, 2

    matchup1 = DEMatchup(matchup1_matchup_number, same_round_number, same_stage_number, same_tournament_id)
    matchup2 = DEMatchup(matchup2_matchup_number, same_round_number, same_stage_number, same_tournament_id)

    assert matchup1 != matchup2

def test_de_matchup_inequality_different_bracket_roles():
    same_matchup_number, same_round_number, same_stage_number, same_tournament_id = 1, 1, 1, TOURNY_ID1

    matchup1 = DEMatchup(same_matchup_number, same_round_number, same_stage_number, same_tournament_id, bracket_role=DEBracketRole.MAIN)
    matchup2 = DEMatchup(same_matchup_number, same_round_number, same_stage_number, same_tournament_id, bracket_role=DEBracketRole.CONSOLATION)

    assert matchup1 != matchup2
