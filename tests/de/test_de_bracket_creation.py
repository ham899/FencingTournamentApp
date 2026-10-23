import pytest

import factories

from de.de_bracket import DEBracket
from de.de_bracket_role import DEBracketRole
from de.de_matchup import DEMatchup


# --- Constants ---
from constants import TOURNY_ID1, TOURNY_ID2

VALID_STAGE_NUMBER1, VALID_STAGE_NUMBER2 = 1, 2
DE_BRACKET_DEFAULT_SCORE_TO_WIN = 15


# --- Fixtures ---
@pytest.fixture
def four_seed_ordered_entries():
    return factories.make_entries(n=4, tournament_id=TOURNY_ID1)

@pytest.fixture
def five_seed_ordered_entries():
    return factories.make_entries(n=5, tournament_id=TOURNY_ID1)

@pytest.fixture
def six_seed_ordered_entries():
    return factories.make_entries(n=6, tournament_id=TOURNY_ID1)

@pytest.fixture
def seven_seed_ordered_entries():
    return factories.make_entries(n=7, tournament_id=TOURNY_ID1)

@pytest.fixture
def eight_seed_ordered_entries():
    return factories.make_entries(n=8, tournament_id=TOURNY_ID1)


# --- Initialization and Validation Tests ---
def test_de_bracket_creation_all_defaults(eight_seed_ordered_entries):
    bracket = DEBracket(
        stage_number=VALID_STAGE_NUMBER1,
        seed_ordered_entries=eight_seed_ordered_entries
    )

    # Attribute checks
    assert bracket.stage_number == VALID_STAGE_NUMBER1
    assert bracket.bracket_role == DEBracketRole.MAIN
    assert bracket.stop_at_round is None
    assert isinstance(bracket.rounds, tuple)
    assert bracket.third_place_matchup is None
    assert bracket.score_to_win == DE_BRACKET_DEFAULT_SCORE_TO_WIN

    # Property checks
    assert bracket.tournament_id == TOURNY_ID1
    assert bracket.num_entries == 8
    assert bracket.num_rounds == 3
    assert bracket.playable_rounds is bracket.rounds
    assert bracket.bracket_size == 8
    assert bracket.current_round_index == 0
    assert bracket.current_round_number == 1
    assert bracket.current_round is bracket.rounds[0]
    assert bracket.current_round_size == 8
    assert bracket.current_round_name == 'Quarter-Final'
    assert bracket.first_round is bracket.rounds[0]
    assert bracket.round_one_seed_order == (1, 8, 5, 4, 3, 6, 7, 2)
    assert bracket.entries == factories.get_position_ordered_entries_from_seed_ordered_entries(eight_seed_ordered_entries)
    assert bracket.winner is None

def test_de_bracket_creation_consolation_bracket(eight_seed_ordered_entries):
    score_to_win = 8
    
    bracket = DEBracket(
        stage_number=VALID_STAGE_NUMBER1,
        seed_ordered_entries=eight_seed_ordered_entries,
        bracket_role=DEBracketRole.CONSOLATION,
        score_to_win=score_to_win
    )

    # Attribute checks
    assert bracket.stage_number == VALID_STAGE_NUMBER1
    assert bracket.bracket_role == DEBracketRole.CONSOLATION
    assert bracket.stop_at_round is None
    assert isinstance(bracket.rounds, tuple)
    assert bracket.third_place_matchup is None
    assert bracket.score_to_win == score_to_win

    # Property checks
    assert bracket.tournament_id == TOURNY_ID1
    assert bracket.num_entries == 8
    assert bracket.num_rounds == 3
    assert bracket.playable_rounds is bracket.rounds
    assert bracket.bracket_size == 8
    assert bracket.current_round_index == 0
    assert bracket.current_round_number == 1
    assert bracket.current_round is bracket.rounds[0]
    assert bracket.current_round_size == 8
    assert bracket.current_round_name == 'Quarter-Final'
    assert bracket.first_round is bracket.rounds[0]
    assert bracket.round_one_seed_order == (1, 8, 5, 4, 3, 6, 7, 2)
    assert bracket.entries == factories.get_position_ordered_entries_from_seed_ordered_entries(eight_seed_ordered_entries)
    assert bracket.winner is None

    # Check that all matchups match the bracket's score_to_win
    for de_round in bracket.rounds:
        for matchup in de_round.matchups:
            assert matchup.score_to_win == score_to_win

def test_de_bracket_creation_with_stop_at_round(eight_seed_ordered_entries):
    bracket = DEBracket(
        stage_number=VALID_STAGE_NUMBER1,
        seed_ordered_entries=eight_seed_ordered_entries,
        stop_at_round=2
    )

    # Attribute checks
    assert bracket.stage_number == VALID_STAGE_NUMBER1
    assert bracket.bracket_role == DEBracketRole.MAIN
    assert bracket.stop_at_round == 2
    assert isinstance(bracket.rounds, tuple)
    assert bracket.third_place_matchup is None
    assert bracket.score_to_win == DE_BRACKET_DEFAULT_SCORE_TO_WIN

    # Property checks
    assert bracket.tournament_id == TOURNY_ID1
    assert bracket.num_entries == 8
    assert bracket.num_rounds == 3
    assert bracket.playable_rounds == bracket.rounds[:1] # Only one round is playable since we stop at round 2
    assert bracket.bracket_size == 8
    assert bracket.current_round_index == 0
    assert bracket.current_round_number == 1
    assert bracket.current_round is bracket.rounds[0]
    assert bracket.current_round_size == 8
    assert bracket.current_round_name == 'Quarter-Final'
    assert bracket.first_round is bracket.rounds[0]
    assert bracket.round_one_seed_order == (1, 8, 5, 4, 3, 6, 7, 2)
    assert bracket.entries == factories.get_position_ordered_entries_from_seed_ordered_entries(eight_seed_ordered_entries)
    assert bracket.winner is None

def test_de_bracket_creation_with_third_place_matchup(eight_seed_ordered_entries):
    bracket = DEBracket(
        stage_number=VALID_STAGE_NUMBER1,
        seed_ordered_entries=eight_seed_ordered_entries,
        has_third_place_match=True
    )

    # Attribute checks
    assert bracket.stage_number == VALID_STAGE_NUMBER1
    assert bracket.bracket_role == DEBracketRole.MAIN
    assert bracket.stop_at_round is None
    assert isinstance(bracket.rounds, tuple)
    assert isinstance(bracket.third_place_matchup, DEMatchup)
    assert bracket.score_to_win == DE_BRACKET_DEFAULT_SCORE_TO_WIN

    # Property checks
    assert bracket.tournament_id == TOURNY_ID1
    assert bracket.num_entries == 8
    assert bracket.num_rounds == 3
    assert bracket.playable_rounds is bracket.rounds
    assert bracket.bracket_size == 8
    assert bracket.current_round_index == 0
    assert bracket.current_round_number == 1
    assert bracket.current_round is bracket.rounds[0]
    assert bracket.current_round_size == 8
    assert bracket.current_round_name == 'Quarter-Final'
    assert bracket.first_round is bracket.rounds[0]
    assert bracket.round_one_seed_order == (1, 8, 5, 4, 3, 6, 7, 2)
    assert bracket.entries == factories.get_position_ordered_entries_from_seed_ordered_entries(eight_seed_ordered_entries)
    assert bracket.winner is None

def test_de_bracket_creation_with_byes(six_seed_ordered_entries):
    bracket = DEBracket(stage_number=VALID_STAGE_NUMBER1, seed_ordered_entries=six_seed_ordered_entries)

    position_ordered_entries = factories.get_position_ordered_entries_from_seed_ordered_entries(
        seed_ordered_entries=factories.pad_entries_to_next_power_of_two(six_seed_ordered_entries)
    )
    position_ordered_entries = tuple(entry for entry in position_ordered_entries if entry is not None)

    # Attribute checks
    assert bracket.stage_number == VALID_STAGE_NUMBER1
    assert bracket.bracket_role == DEBracketRole.MAIN
    assert bracket.stop_at_round is None
    assert isinstance(bracket.rounds, tuple)
    assert tuple(len(de_round.matchups) for de_round in bracket.rounds) == (4, 2, 1)
    assert bracket.third_place_matchup is None
    assert bracket.score_to_win == DE_BRACKET_DEFAULT_SCORE_TO_WIN

    # Property checks
    assert bracket.tournament_id == TOURNY_ID1
    assert bracket.num_entries == 6
    assert bracket.num_rounds == 3
    assert len(bracket.rounds) == 3
    assert bracket.playable_rounds == bracket.rounds
    assert bracket.bracket_size == 8
    assert bracket.current_round_index == 0
    assert bracket.current_round_number == 1
    assert bracket.current_round is bracket.rounds[0]
    assert bracket.current_round_size == 8
    assert bracket.current_round_name == 'Quarter-Final'
    assert bracket.first_round is bracket.rounds[0]
    assert bracket.round_one_seed_order == (1, 8, 5, 4, 3, 6, 7, 2)
    assert bracket.entries == position_ordered_entries
    assert bracket.winner is None

    # Check that byes are present and winners were progressed correctly
    first_round = bracket.first_round

    assert first_round.matchups[0].is_bye()
    assert not first_round.matchups[1].is_bye()
    assert not first_round.matchups[2].is_bye()
    assert first_round.matchups[3].is_bye()

    assert first_round.matchups[0].winner is six_seed_ordered_entries[0]
    assert first_round.matchups[3].winner is six_seed_ordered_entries[1]

    second_round = bracket.rounds[1]
    assert second_round.matchups[0].entry1 is six_seed_ordered_entries[0]
    assert second_round.matchups[0].entry2 is None
    assert second_round.matchups[1].entry1 is None
    assert second_round.matchups[1].entry2 is six_seed_ordered_entries[1]

def test_de_bracket_creation_invalid_cannot_create_a_stopped_bracket_with_a_third_place_matchup(eight_seed_ordered_entries):
    with pytest.raises(ValueError, match='Cannot enable a third-place match when a stopping round is'):
        DEBracket(
            stage_number=VALID_STAGE_NUMBER1,
            seed_ordered_entries=eight_seed_ordered_entries,
            stop_at_round=2,
            has_third_place_match=True
        )

@pytest.mark.parametrize('invalid_stage_number_type', [None, False, True, 0.0, 'first', [], (), {}, object()])
def test_de_bracket_creation_invalid_stage_number_type(eight_seed_ordered_entries, invalid_stage_number_type):
    with pytest.raises(TypeError):
        DEBracket(
            stage_number=invalid_stage_number_type,
            seed_ordered_entries=eight_seed_ordered_entries
        )

@pytest.mark.parametrize('invalid_stage_number_value', [-10, -1, 0])
def test_de_bracket_creation_invalid_stage_number_value(eight_seed_ordered_entries, invalid_stage_number_value):
    with pytest.raises(ValueError):
        DEBracket(
            stage_number=invalid_stage_number_value,
            seed_ordered_entries=eight_seed_ordered_entries
        )

@pytest.mark.parametrize('invalid_seed_ordered_entries_type', [None, False, True, 0, 1.0, 'Ellie, John', [], {}, object()])
def test_de_bracket_creation_invalid_seed_ordered_entries_type(invalid_seed_ordered_entries_type):
    with pytest.raises(TypeError):
        DEBracket(
            stage_number=VALID_STAGE_NUMBER1,
            seed_ordered_entries=invalid_seed_ordered_entries_type
        )
@pytest.mark.parametrize(('index', 'invalid_entry_type'), [(0, None), (1, False), (2, True), (3, 0), (4, 1.0), (5, 'John'), (6, []), (7, {}), (0, object())])
def test_de_bracket_creation_invalid_seed_ordered_entries_invalid_entry_type(index, invalid_entry_type):
    seed_ordered_entries = list(factories.make_entries(n=8, tournament_id=TOURNY_ID1))
    seed_ordered_entries[index] = invalid_entry_type
    seed_ordered_entries = tuple(seed_ordered_entries)
    with pytest.raises(TypeError):
        DEBracket(stage_number=VALID_STAGE_NUMBER1, seed_ordered_entries=seed_ordered_entries)

@pytest.mark.parametrize('invalid_seed_ordered_entries_size', [(), factories.make_entries(n=1, tournament_id=TOURNY_ID1)])
def test_de_bracket_creation_invalid_seed_ordered_entries_too_few_entries(invalid_seed_ordered_entries_size):
    with pytest.raises(ValueError):
        DEBracket(stage_number=VALID_STAGE_NUMBER1, seed_ordered_entries=invalid_seed_ordered_entries_size)

def test_de_bracket_creation_invalid_seed_ordered_entries_duplicate_entry_ids_present(eight_seed_ordered_entries):
    
    eight_seed_ordered_entries = list(eight_seed_ordered_entries)
    eight_seed_ordered_entries[3] = eight_seed_ordered_entries[6]
    eight_seed_ordered_entries = tuple(eight_seed_ordered_entries)
    
    with pytest.raises(ValueError):
        DEBracket(stage_number=VALID_STAGE_NUMBER1, seed_ordered_entries=eight_seed_ordered_entries)

def test_de_bracket_creation_invalid_seed_ordered_entries_duplicate_fencer_ids_present(seven_seed_ordered_entries):
    seven_seed_ordered_entries[2].fencer = seven_seed_ordered_entries[0].fencer

    with pytest.raises(ValueError):
        DEBracket(stage_number=VALID_STAGE_NUMBER1, seed_ordered_entries=seven_seed_ordered_entries)

def test_de_bracket_creation_invalid_seed_ordered_entries_wrong_tournament_id(six_seed_ordered_entries):
    six_seed_ordered_entries[5].tournament_id = TOURNY_ID2

    with pytest.raises(ValueError):
        DEBracket(stage_number=VALID_STAGE_NUMBER1, seed_ordered_entries=six_seed_ordered_entries)

@pytest.mark.parametrize('invalid_has_third_place_match_type', [None, 0, 1.0, 'True', [], (), {}, object()])
def test_de_bracket_creation_invalid_has_third_place_match_type(five_seed_ordered_entries, invalid_has_third_place_match_type):
    with pytest.raises(TypeError):
        DEBracket(
            stage_number=VALID_STAGE_NUMBER1,
            seed_ordered_entries=five_seed_ordered_entries,
            has_third_place_match=invalid_has_third_place_match_type
        )

@pytest.mark.parametrize('invalid_stop_at_round_type', [False, True, 0.0, '2', [], (), {}, object()])
def test_de_bracket_creation_invalid_stop_at_round_type(six_seed_ordered_entries, invalid_stop_at_round_type):
    with pytest.raises(TypeError):
        DEBracket(
            stage_number=VALID_STAGE_NUMBER1,
            seed_ordered_entries=six_seed_ordered_entries,
            stop_at_round=invalid_stop_at_round_type
        )

@pytest.mark.parametrize('invalid_stop_at_round_value', [-10, -1, 0, 1, 3, 4, 10])
def test_de_bracket_creation_invalid_stop_at_round_value(seven_seed_ordered_entries, invalid_stop_at_round_value):
    with pytest.raises(ValueError):
        DEBracket(
            stage_number=VALID_STAGE_NUMBER1,
            seed_ordered_entries=seven_seed_ordered_entries,
            stop_at_round=invalid_stop_at_round_value
        )

@pytest.mark.parametrize('invalid_bracket_role_type', [None, False, True, 0, 1.0, 'consolation', [], (), {}, object()])
def test_de_bracket_creation_invalid_bracket_role_type(five_seed_ordered_entries, invalid_bracket_role_type):
    with pytest.raises(TypeError):
        DEBracket(
            stage_number=VALID_STAGE_NUMBER1,
            seed_ordered_entries=five_seed_ordered_entries,
            bracket_role=invalid_bracket_role_type
        )

@pytest.mark.parametrize('invalid_score_to_win_type', [None, False, True, 5.0, 15.0, 'ten', [], (), {}, object()])
def test_de_bracket_creation_invalid_score_to_win_type(eight_seed_ordered_entries, invalid_score_to_win_type):
    with pytest.raises(TypeError):
        DEBracket(
            stage_number=VALID_STAGE_NUMBER1,
            seed_ordered_entries=eight_seed_ordered_entries,
            score_to_win=invalid_score_to_win_type
        )

@pytest.mark.parametrize('invalid_score_to_win_value', [-10, -1, 0])
def test_de_bracket_creation_invalid_score_to_win_value(four_seed_ordered_entries, invalid_score_to_win_value):
    with pytest.raises(ValueError):
        DEBracket(
            stage_number=VALID_STAGE_NUMBER1,
            seed_ordered_entries=four_seed_ordered_entries,
            score_to_win=invalid_score_to_win_value
        )

# --- Equality Tests ---
@pytest.mark.parametrize('bracket_role', [DEBracketRole.MAIN, DEBracketRole.CONSOLATION])
def test_de_bracket_equality(eight_seed_ordered_entries, bracket_role):
    bracket1 = DEBracket(
        stage_number=VALID_STAGE_NUMBER1,
        seed_ordered_entries=eight_seed_ordered_entries,
        bracket_role=bracket_role
    )

    bracket2 = DEBracket(
        stage_number=VALID_STAGE_NUMBER1,
        seed_ordered_entries=eight_seed_ordered_entries,
        bracket_role=bracket_role
    )

    assert bracket1 is not bracket2
    assert bracket1 == bracket1
    assert bracket1 == bracket2
    assert bracket2 == bracket1

def test_de_bracket_inequality_different_tournament_id(eight_seed_ordered_entries):
    other_entries = factories.make_entries(n=8, tournament_id=TOURNY_ID2)

    bracket1 = DEBracket(
        stage_number=VALID_STAGE_NUMBER1,
        seed_ordered_entries=eight_seed_ordered_entries
    )

    bracket2 = DEBracket(
        stage_number=VALID_STAGE_NUMBER1,
        seed_ordered_entries=other_entries
    )

    assert bracket1 is not bracket2
    assert bracket1 != bracket2

def test_de_bracket_inequality_different_stage_number(eight_seed_ordered_entries):
    bracket1 = DEBracket(
        stage_number=VALID_STAGE_NUMBER1,
        seed_ordered_entries=eight_seed_ordered_entries
    )

    bracket2 = DEBracket(
        stage_number=VALID_STAGE_NUMBER2,
        seed_ordered_entries=eight_seed_ordered_entries
    )

    assert bracket1 is not bracket2
    assert bracket1 != bracket2

def test_de_bracket_inequality_different_bracket_role(eight_seed_ordered_entries):
    bracket1 = DEBracket(
        stage_number=VALID_STAGE_NUMBER1,
        seed_ordered_entries=eight_seed_ordered_entries,
        bracket_role=DEBracketRole.MAIN
    )

    bracket2 = DEBracket(
        stage_number=VALID_STAGE_NUMBER1,
        seed_ordered_entries=eight_seed_ordered_entries,
        bracket_role=DEBracketRole.CONSOLATION
    )

    assert bracket1 is not bracket2
    assert bracket1 != bracket2

@pytest.mark.parametrize('other_object', [None, False, True, 0, 1.0, 'bracket', [], (), {}, object()])
def test_de_bracket_inequality_different_object(eight_seed_ordered_entries, other_object):
    bracket = DEBracket(
        stage_number=VALID_STAGE_NUMBER1,
        seed_ordered_entries=eight_seed_ordered_entries
    )

    assert bracket != other_object
