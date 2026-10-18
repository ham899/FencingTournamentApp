import pytest

import factories

from de.de_bracket_role import DEBracketRole
from de.de_round import DERound


# --- Constants ---
from constants import TOURNY_ID1, TOURNY_ID2

VALID_ROUND_NUMBER1, VALID_ROUND_NUMBER2 = 1, 2
VALID_STAGE_NUMBER1, VALID_STAGE_NUMBER2 = 1, 2



INVALID_IDENTIFYING_NUMBER_TYPES = [None, 'second', 1.5, False, True, [], (), {}, object()]
INVALID_IDENTIFYING_NUMBER_VALUES = [-10, -1, 0]


# --- Fixtures ---
@pytest.fixture
def valid_top_8_matchups():
    return factories.make_de_matchups_from_defaults(
        num_entries=8,
        round_number=VALID_ROUND_NUMBER1,
        stage_number=VALID_STAGE_NUMBER1,
        tournament_id=TOURNY_ID1
    )

@pytest.fixture
def valid_top_32_matchups():
    return factories.make_de_matchups_from_defaults(
        num_entries=32,
        round_number=VALID_ROUND_NUMBER1,
        stage_number=VALID_STAGE_NUMBER1,
        tournament_id=TOURNY_ID1
    )


# --- Initialization and Validation Tests ---
@pytest.mark.parametrize(
    ('num_entries', 'round_number', 'stage_number', 'bracket_role'),
    [
        (2, 3, 2, DEBracketRole.MAIN),
        (4, 1, 1, DEBracketRole.CONSOLATION),
        (8, 2, 2, DEBracketRole.MAIN),
        (16, 4, 3, DEBracketRole.MAIN),
    ],
)
def test_de_round_creation_valid(num_entries, round_number, stage_number, bracket_role):
    matchups = factories.make_de_matchups_from_defaults(
        num_entries=num_entries,
        round_number=round_number,
        stage_number=stage_number,
        tournament_id=TOURNY_ID1,
        bracket_role=bracket_role,
    )

    de_round = DERound(
        matchups=matchups,
        round_number=round_number,
        stage_number=stage_number,
        bracket_role=bracket_role,
    )

    assert de_round.matchups is matchups
    assert de_round.round_number == round_number
    assert de_round.stage_number == stage_number
    assert de_round.bracket_role == bracket_role
    assert de_round.tournament_id == TOURNY_ID1
    assert de_round.num_matchups == num_entries // 2
    assert de_round.size == num_entries

@pytest.mark.parametrize('invalid_matchups_type', [None, 'Bob vs. Bill', 0, 1.0, False, True, [], {}, object()])
def test_de_round_creation_invalid_matchups_type(invalid_matchups_type):
    with pytest.raises(TypeError):
        DERound(
            matchups=invalid_matchups_type,
            round_number=VALID_ROUND_NUMBER1,
            stage_number=VALID_STAGE_NUMBER1
        )

@pytest.mark.parametrize(
        ('index', 'non_matchup'), 
    [
        (0, 'other_object'),
        (1, None),
        (2, object()),
        (3, 0)
    ]
)
def test_de_round_creation_invalid_matchups_contains_a_non_de_matchup_object(valid_top_8_matchups, index, non_matchup):
    matchups = list(valid_top_8_matchups)
    matchups[index] = non_matchup

    with pytest.raises(TypeError):
        DERound(
            matchups=tuple(matchups),
            round_number=VALID_ROUND_NUMBER1,
            stage_number=VALID_STAGE_NUMBER1
        )

@pytest.mark.parametrize("invalid_match", [False, True, 'match', 0, 1.0, [], (), {}, object()])
def test_de_round_creation_invalid_matchups_invalid_stored_match_present(valid_top_8_matchups, invalid_match):
    valid_top_8_matchups[2].match = invalid_match

    with pytest.raises(TypeError):
        DERound(
            matchups=valid_top_8_matchups,
            round_number=VALID_ROUND_NUMBER1,
            stage_number=VALID_STAGE_NUMBER1,
        )

def test_de_round_creation_invalid_matchups_empty_tuple():
    with pytest.raises(ValueError):
        DERound(
            matchups=(),
            round_number=VALID_ROUND_NUMBER1,
            stage_number=VALID_STAGE_NUMBER1
        )

@pytest.mark.parametrize('invalid_matchups_length', [3, 5, 7, 9, 15])
def test_de_round_creation_invalid_matchups_not_a_power_of_two(valid_top_32_matchups, invalid_matchups_length):
    with pytest.raises(ValueError):
        DERound(
            matchups=valid_top_32_matchups[:invalid_matchups_length],
            round_number=VALID_ROUND_NUMBER1,
            stage_number=VALID_STAGE_NUMBER1
        )

@pytest.mark.parametrize(('index', 'invalid_matchup_number'), [(0, -1), (2, 1), (3, 5)])
def test_de_round_creation_invalid_matchups_invalid_matchup_number_present(valid_top_8_matchups, index, invalid_matchup_number):
    valid_top_8_matchups[index].matchup_number = invalid_matchup_number

    with pytest.raises(ValueError):
        DERound(
            matchups=valid_top_8_matchups,
            round_number=VALID_ROUND_NUMBER1,
            stage_number=VALID_STAGE_NUMBER1
        )

def test_de_round_creation_invalid_matchups_not_matching_stage_number_present(valid_top_8_matchups):
    valid_top_8_matchups[2].stage_number = VALID_STAGE_NUMBER2

    with pytest.raises(ValueError):
        DERound(
            matchups=valid_top_8_matchups,
            round_number=VALID_ROUND_NUMBER1,
            stage_number=VALID_STAGE_NUMBER1
        )

def test_de_round_creation_invalid_matchups_not_matching_round_number_present(valid_top_8_matchups):
    valid_top_8_matchups[2].round_number = VALID_ROUND_NUMBER2

    with pytest.raises(ValueError):
        DERound(
            matchups=valid_top_8_matchups,
            round_number=VALID_ROUND_NUMBER1,
            stage_number=VALID_STAGE_NUMBER1
        )

def test_de_round_creation_invalid_matchups_not_matching_tournament_id_present(valid_top_8_matchups):
    valid_top_8_matchups[2].tournament_id = TOURNY_ID2

    with pytest.raises(ValueError):
        DERound(
            matchups=valid_top_8_matchups,
            round_number=VALID_ROUND_NUMBER1,
            stage_number=VALID_STAGE_NUMBER1
        )

def test_de_round_creation_invalid_matchups_not_matching_bracket_role_present(valid_top_8_matchups):
    valid_top_8_matchups[2].bracket_role = DEBracketRole.CONSOLATION

    with pytest.raises(ValueError):
        DERound(
            matchups=valid_top_8_matchups,
            round_number=VALID_ROUND_NUMBER1,
            stage_number=VALID_STAGE_NUMBER1
        )

def test_de_round_creation_invalid_matchup_not_matching_bracket_role_present_for_consolation_bracket():
    matchups = factories.make_de_matchups_from_defaults(
        num_entries=8,
        round_number=VALID_ROUND_NUMBER1,
        stage_number=VALID_STAGE_NUMBER1,
        tournament_id=TOURNY_ID1,
        bracket_role=DEBracketRole.CONSOLATION
    )

    matchups[2].bracket_role = DEBracketRole.MAIN

    with pytest.raises(ValueError):
        DERound(
            matchups=matchups,
            round_number=VALID_ROUND_NUMBER1,
            stage_number=VALID_STAGE_NUMBER1,
            bracket_role=DEBracketRole.CONSOLATION
        )

def test_de_round_creation_invalid_matchups_duplicate_entry_present(valid_top_8_matchups):
    valid_top_8_matchups[3].entry2 = valid_top_8_matchups[0].entry1

    with pytest.raises(ValueError):
        DERound(
            matchups=valid_top_8_matchups,
            round_number=VALID_ROUND_NUMBER1,
            stage_number=VALID_STAGE_NUMBER1
        )

@pytest.mark.parametrize('invalid_round_number_type', INVALID_IDENTIFYING_NUMBER_TYPES)
def test_de_round_creation_invalid_round_number_type(valid_top_8_matchups, invalid_round_number_type):
    with pytest.raises(TypeError):
        DERound(
            matchups=valid_top_8_matchups,
            round_number=invalid_round_number_type,
            stage_number=VALID_STAGE_NUMBER1
        )

@pytest.mark.parametrize('invalid_round_number_value', INVALID_IDENTIFYING_NUMBER_VALUES)
def test_de_round_creation_invalid_round_number_value(valid_top_8_matchups, invalid_round_number_value):
    with pytest.raises(ValueError):
        DERound(
            matchups=valid_top_8_matchups,
            round_number=invalid_round_number_value,
            stage_number=VALID_STAGE_NUMBER1
        )

@pytest.mark.parametrize('invalid_stage_number_type', INVALID_IDENTIFYING_NUMBER_TYPES)
def test_de_round_creation_invalid_stage_number_type(valid_top_8_matchups, invalid_stage_number_type):
    with pytest.raises(TypeError):
        DERound(
            matchups=valid_top_8_matchups,
            round_number=1,
            stage_number=invalid_stage_number_type
        )

@pytest.mark.parametrize('invalid_stage_number_value', INVALID_IDENTIFYING_NUMBER_VALUES)
def test_de_round_creation_invalid_stage_number_value(valid_top_8_matchups, invalid_stage_number_value):
    with pytest.raises(ValueError):
        DERound(
            matchups=valid_top_8_matchups,
            round_number=VALID_ROUND_NUMBER1,
            stage_number=invalid_stage_number_value
        )

@pytest.mark.parametrize('invalid_bracket_role_type', [None, 'MAIN', 'CONSOLATION', 0, 1.0, False, True, [], {}, object()])
def test_de_round_creation_invalid_bracket_role_type(valid_top_8_matchups, invalid_bracket_role_type):
    with pytest.raises(TypeError):
        DERound(
            matchups=valid_top_8_matchups,
            round_number=VALID_ROUND_NUMBER1,
            stage_number=VALID_STAGE_NUMBER1,
            bracket_role=invalid_bracket_role_type
        )

@pytest.mark.parametrize(
        ('num_entries', 'expected_size', 'expected_name'), 
        (
            (2, 2, 'Final'),
            (3, 4, 'Semi-Final'),
            (4, 4, 'Semi-Final'),
            (5, 8, 'Quarter-Final'),
            (7, 8, 'Quarter-Final'),
            (9, 16, 'Round of 16'),
            (16, 16, 'Round of 16'),
            (17, 32, 'Round of 32'),
            (32, 32, 'Round of 32'),
            (33, 64, 'Round of 64'),
            (48, 64, 'Round of 64')
        )
)
def test_de_round_creation_round_size_and_name_property(num_entries, expected_size, expected_name):
    seed_ordered_entries = factories.make_entries(num_entries, TOURNY_ID1)

    de_round = factories.make_de_round_from_seed_ordered_entries(
        seed_ordered_entries=seed_ordered_entries,
        round_number=1,
        stage_number=1,
        tournament_id=TOURNY_ID1
    )

    assert de_round.size == expected_size
    assert de_round.round_name == expected_name
    assert de_round.num_matchups == expected_size // 2

@pytest.mark.parametrize('tournament_id', [TOURNY_ID1, TOURNY_ID2])
def test_de_round_creation_tournament_id_property(tournament_id):
    matchups = factories.make_de_matchups_from_defaults(
        num_entries=8,
        round_number=VALID_ROUND_NUMBER1,
        stage_number=VALID_STAGE_NUMBER1,
        tournament_id=tournament_id
    )

    de_round = DERound(matchups, VALID_ROUND_NUMBER1, VALID_STAGE_NUMBER1)
    assert de_round.tournament_id == tournament_id

@pytest.mark.parametrize('num_entries', [2, 3, 8, 14])
def test_de_round_entries_property(num_entries):
    seed_ordered_entries = factories.make_entries(num_entries, TOURNY_ID1)

    position_ordered_entries = factories.get_position_ordered_entries_from_seed_ordered_entries(
        seed_ordered_entries=factories.pad_entries_to_next_power_of_two(seed_ordered_entries)
    )

    de_round = factories.make_de_round_from_seed_ordered_entries(
        seed_ordered_entries=seed_ordered_entries,
        round_number=VALID_ROUND_NUMBER1,
        stage_number=VALID_STAGE_NUMBER1,
        tournament_id=TOURNY_ID1
    )

    assert de_round.entries == tuple(entry for entry in position_ordered_entries if entry is not None)

def test_de_round_entries_property_with_missing_entries():
    entry1, entry2 = factories.make_entries(2, TOURNY_ID1)

    de_round = factories.make_de_round_from_position_ordered_entries(
        entries_in_matchup_position_order=(
            None, entry2,
            entry1, None,
        ),
        round_number=2,
        stage_number=1,
        tournament_id=TOURNY_ID1,
    )

    assert de_round.entries == (entry2, entry1)

def test_de_round_entries_property_with_all_missing_entries():
    de_round = factories.make_de_round_from_position_ordered_entries(
        entries_in_matchup_position_order=(
            None, None,
            None, None,
        ),
        round_number=2,
        stage_number=1,
        tournament_id=TOURNY_ID1,
    )

    assert de_round.entries == ()

def test_de_round_equality(valid_top_8_matchups):
    de_round1 = DERound(
        matchups=valid_top_8_matchups,
        round_number=VALID_ROUND_NUMBER1,
        stage_number=VALID_STAGE_NUMBER1
    )

    de_round2 = DERound(
        matchups=valid_top_8_matchups,
        round_number=VALID_ROUND_NUMBER1,
        stage_number=VALID_STAGE_NUMBER1
    )

    assert de_round1.bracket_role == DEBracketRole.MAIN
    assert de_round2.bracket_role == DEBracketRole.MAIN

    assert de_round1 == de_round2

@pytest.mark.parametrize('other_object', [None, 0, 1.0, False, True, 'de_round', [], (), {}, object()])
def test_de_round_inequality_different_object(valid_top_8_matchups, other_object):
    de_round = DERound(
        matchups=valid_top_8_matchups,
        round_number=VALID_ROUND_NUMBER1,
        stage_number=VALID_STAGE_NUMBER1
    )

    assert de_round != other_object

def test_de_round_inequality_different_tournament_id(valid_top_8_matchups):
    de_round1 = DERound(
        matchups=valid_top_8_matchups,
        round_number=VALID_ROUND_NUMBER1,
        stage_number=VALID_STAGE_NUMBER1
    )

    matchups2 = factories.make_de_matchups_from_defaults(
        num_entries=8,
        round_number=VALID_ROUND_NUMBER1,
        stage_number=VALID_STAGE_NUMBER1,
        tournament_id=TOURNY_ID2
    )    

    de_round2 = DERound(
        matchups=matchups2,
        round_number=VALID_ROUND_NUMBER1,
        stage_number=VALID_STAGE_NUMBER1
    )

    assert de_round1 != de_round2

def test_de_round_inequality_different_stage_number(valid_top_8_matchups):
    de_round1 = DERound(
        matchups=valid_top_8_matchups,
        round_number=VALID_ROUND_NUMBER1,
        stage_number=VALID_STAGE_NUMBER1
    )

    matchups2 = factories.make_de_matchups_from_defaults(
        num_entries=8,
        round_number=VALID_ROUND_NUMBER1,
        stage_number=VALID_STAGE_NUMBER2,
        tournament_id=TOURNY_ID1
    )

    de_round2 = DERound(
        matchups=matchups2,
        round_number=VALID_ROUND_NUMBER1,
        stage_number=VALID_STAGE_NUMBER2
    )

    assert de_round1 != de_round2

def test_de_round_inequality_different_round_number(valid_top_8_matchups):
    de_round1 = DERound(
        matchups=valid_top_8_matchups,
        round_number=VALID_ROUND_NUMBER1,
        stage_number=VALID_STAGE_NUMBER1
    )

    matchups2 = factories.make_de_matchups_from_defaults(
        num_entries=8,
        round_number=VALID_ROUND_NUMBER2,
        stage_number=VALID_STAGE_NUMBER1,
        tournament_id=TOURNY_ID1
    )

    de_round2 = DERound(
        matchups=matchups2,
        round_number=VALID_ROUND_NUMBER2,
        stage_number=VALID_STAGE_NUMBER1
    )

    assert de_round1 != de_round2

def test_de_round_inequality_different_bracket_role(valid_top_8_matchups):
    de_round1 = DERound(
        matchups=valid_top_8_matchups,
        round_number=VALID_ROUND_NUMBER1,
        stage_number=VALID_STAGE_NUMBER1,
        bracket_role=DEBracketRole.MAIN
    )

    matchups2 = factories.make_de_matchups_from_defaults(
        num_entries=8,
        round_number=VALID_ROUND_NUMBER1,
        stage_number=VALID_STAGE_NUMBER1,
        tournament_id=TOURNY_ID1,
        bracket_role=DEBracketRole.CONSOLATION
    )

    de_round2 = DERound(
        matchups=matchups2,
        round_number=VALID_ROUND_NUMBER1,
        stage_number=VALID_STAGE_NUMBER1,
        bracket_role=DEBracketRole.CONSOLATION
    )

    assert de_round1 != de_round2
