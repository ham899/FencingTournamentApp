import pytest

import factories

from de.de_bracket import DEBracket
from de.de_bracket_role import DEBracketRole
from de.de_stage import DEStage
from entities.seeded_entry import SeededEntry


# --- Constants ---
from constants import TOURNY_ID1, TOURNY_ID2
VALID_STAGE_NUMBER1 = 1
VALID_STAGE_NUMBER2 = 2
DEFAULT_DE_SCORE_TO_WIN = 15


# --- Fixtures ---
@pytest.fixture
def eight_seeded_entries():
    return factories.make_seeded_entries(n=8, tournament_id=TOURNY_ID1)


# --- Initialization and Validation Tests ---
def test_de_stage_creation_defaults(eight_seeded_entries):
    stage = DEStage(stage_number=VALID_STAGE_NUMBER1, seeded_entries=eight_seeded_entries)

    assert stage.stage_number == VALID_STAGE_NUMBER1
    assert stage.seeded_entries == eight_seeded_entries
    
    assert stage.score_to_win == DEFAULT_DE_SCORE_TO_WIN
    assert not stage.use_consolation_bracket
    assert stage.stop_at_round is None
    assert isinstance(stage.main_bracket, DEBracket)
    assert stage.consolation_bracket is None
    
    assert stage.main_bracket.bracket_role == DEBracketRole.MAIN
    assert not stage.main_bracket.has_third_place_matchup()

def test_de_stage_creation_with_third_place_match_and_consolation_bracket(eight_seeded_entries):
    custom_score_to_win = 8

    stage = DEStage(
        stage_number=VALID_STAGE_NUMBER1,
        seeded_entries=eight_seeded_entries,
        score_to_win=custom_score_to_win,
        has_third_place_match=True,
        use_consolation_bracket=True
    )

    assert stage.stage_number == VALID_STAGE_NUMBER1
    assert stage.seeded_entries == eight_seeded_entries
    assert stage.score_to_win == custom_score_to_win
    assert stage.use_consolation_bracket
    assert isinstance(stage.main_bracket, DEBracket)
    assert stage.main_bracket.has_third_place_matchup()
    assert stage.consolation_bracket is None # It still starts out as None and is created later

    assert stage.main_bracket.bracket_role == DEBracketRole.MAIN
    assert stage.main_bracket.stage_number == VALID_STAGE_NUMBER1
    assert stage.main_bracket.score_to_win == custom_score_to_win

def test_de_stage_creation_with_stop_at_round(eight_seeded_entries):
    stop_at_round = 2

    stage = DEStage(
        stage_number=VALID_STAGE_NUMBER1,
        seeded_entries=eight_seeded_entries,
        stop_at_round=stop_at_round
    )

    assert stage.stage_number == VALID_STAGE_NUMBER1
    assert stage.seeded_entries == eight_seeded_entries
    assert stage.stop_at_round == stop_at_round
    assert isinstance(stage.main_bracket, DEBracket)
    assert stage.consolation_bracket is None

    assert stage.main_bracket.bracket_role == DEBracketRole.MAIN
    assert stage.main_bracket.stop_at_round == stop_at_round

def test_de_stage_creation_sorts_unsorted_seeded_entries():
    seeded_entries = factories.make_seeded_entries(n=6, tournament_id=TOURNY_ID1)
    reversed_seeded_entries = tuple(reversed(seeded_entries))  # Reverse the order

    stage = DEStage(stage_number=VALID_STAGE_NUMBER1, seeded_entries=reversed_seeded_entries)

    assert stage.stage_number == VALID_STAGE_NUMBER1
    assert stage.seeded_entries == seeded_entries

def test_de_stage_creation_with_third_place_match_minimum_entries():
    seeded_entries = factories.make_seeded_entries(n=4, tournament_id=TOURNY_ID1)

    stage = DEStage(
        stage_number=VALID_STAGE_NUMBER1,
        seeded_entries=seeded_entries,
        has_third_place_match=True
    )

    assert stage.seeded_entries == seeded_entries
    assert stage.main_bracket.num_entries == 4
    assert stage.main_bracket.has_third_place_matchup()
    assert not stage.use_consolation_bracket
    assert stage.consolation_bracket is None

def test_de_stage_creation_with_consolation_bracket_minimum_entries():
    seeded_entries = factories.make_seeded_entries(n=6, tournament_id=TOURNY_ID1)

    stage = DEStage(
        stage_number=VALID_STAGE_NUMBER1,
        seeded_entries=seeded_entries,
        use_consolation_bracket=True
    )

    assert stage.seeded_entries == seeded_entries
    assert stage.main_bracket.num_entries == 6
    assert stage.use_consolation_bracket
    assert stage.consolation_bracket is None
    assert not stage.main_bracket.has_third_place_matchup()

@pytest.mark.parametrize('invalid_stage_number_type', [None, False, True, 'first', 1.0, [], (), {}, object()])
def test_de_stage_creation_invalid_stage_number_type(eight_seeded_entries, invalid_stage_number_type):
    with pytest.raises(TypeError):
        DEStage(
            stage_number=invalid_stage_number_type,
            seeded_entries=eight_seeded_entries
        )

@pytest.mark.parametrize('invalid_stage_number_value', [-10, -1, 0])
def test_de_stage_creation_invalid_stage_number_value(eight_seeded_entries, invalid_stage_number_value):
    with pytest.raises(ValueError):
        DEStage(
            stage_number=invalid_stage_number_value,
            seeded_entries=eight_seeded_entries
        )

@pytest.mark.parametrize('invalid_seeded_entries_type', [None, False, True, 'John, Steve, Hannah', 0, 1.0, [], {}, object()])
def test_de_stage_creation_invalid_seeded_entries_type(invalid_seeded_entries_type):
    with pytest.raises(TypeError):
        DEStage(stage_number=VALID_STAGE_NUMBER1, seeded_entries=invalid_seeded_entries_type)

@pytest.mark.parametrize('index', [0, 3, 7])
@pytest.mark.parametrize('invalid_seeded_entry_type', [None, False, True, 'John', 0, 1.0, [], (), {}, object()])
def test_de_stage_creation_invalid_seeded_entries_seeded_entry_type(eight_seeded_entries, index, invalid_seeded_entry_type):
    eight_seeded_entries = list(eight_seeded_entries)
    eight_seeded_entries[index] = invalid_seeded_entry_type
    eight_seeded_entries = tuple(eight_seeded_entries)
    
    with pytest.raises(TypeError):
        DEStage(stage_number=VALID_STAGE_NUMBER1, seeded_entries=eight_seeded_entries)

@pytest.mark.parametrize('invalid_seeded_entries_length', [0, 1])
def test_de_stage_creation_invalid_seeded_entries_too_few_entries(invalid_seeded_entries_length):
    if invalid_seeded_entries_length == 0:
        invalid_seeded_entries = ()
    else:
        invalid_seeded_entries = (factories.make_seeded_entry_at_number(number=1, tournament_id=TOURNY_ID1), )

    with pytest.raises(ValueError):
        DEStage(stage_number=VALID_STAGE_NUMBER1, seeded_entries=invalid_seeded_entries)

def test_de_stage_creation_invalid_seeded_entries_duplicate_entry(eight_seeded_entries):
    eight_seeded_entries = list(eight_seeded_entries)
    eight_seeded_entries[3] = SeededEntry(entry=eight_seeded_entries[6].entry, seed=eight_seeded_entries[3].seed)
    eight_seeded_entries = tuple(eight_seeded_entries)

    with pytest.raises(ValueError):
        DEStage(stage_number=VALID_STAGE_NUMBER1, seeded_entries=eight_seeded_entries)

def test_de_stage_creation_invalid_seeded_entries_duplicate_seed(eight_seeded_entries):
    seeded_entries = list(eight_seeded_entries)
    seeded_entries[4] = SeededEntry(entry=seeded_entries[4].entry, seed=seeded_entries[6].seed)

    with pytest.raises(ValueError):
        DEStage(stage_number=VALID_STAGE_NUMBER1, seeded_entries=tuple(seeded_entries))

def test_de_stage_creation_invalid_seeded_entries_seed_exceeds_number_of_entries(eight_seeded_entries):
    seeded_entries = list(eight_seeded_entries)
    seeded_entries[3] = SeededEntry(entry=seeded_entries[3].entry, seed=9)

    with pytest.raises(ValueError):
        DEStage(stage_number=VALID_STAGE_NUMBER1, seeded_entries=tuple(seeded_entries))

def test_de_stage_creation_invalid_seeded_entries_mixed_tournament_ids(eight_seeded_entries):
    eight_seeded_entries[7].entry.tournament_id = TOURNY_ID2

    with pytest.raises(ValueError):
        DEStage(stage_number=VALID_STAGE_NUMBER1, seeded_entries=eight_seeded_entries)

@pytest.mark.parametrize('invalid_seeded_entries_length', [2, 3, 4, 5])
def test_de_stage_creation_invalid_not_enough_entries_for_consolation_bracket(invalid_seeded_entries_length):
    seeded_entries = factories.make_seeded_entries(n=invalid_seeded_entries_length, tournament_id=TOURNY_ID1)

    with pytest.raises(ValueError):
        DEStage(
            stage_number=VALID_STAGE_NUMBER1, 
            seeded_entries=seeded_entries, 
            use_consolation_bracket=True
        )

def test_de_stage_creation_invalid_cannot_have_stopped_bracket_and_consolation_bracket(eight_seeded_entries):
    with pytest.raises(ValueError):
        DEStage(
            stage_number=VALID_STAGE_NUMBER1,
            seeded_entries=eight_seeded_entries,
            stop_at_round=2,
            use_consolation_bracket=True
        )

@pytest.mark.parametrize('invalid_score_to_win_type', [None, False, True, 'fifteen', 15.0, [], (), {}, object()])
def test_de_stage_creation_invalid_score_to_win_type(eight_seeded_entries, invalid_score_to_win_type):
    with pytest.raises(TypeError):
        DEStage(
            stage_number=VALID_STAGE_NUMBER1,
            seeded_entries=eight_seeded_entries,
            score_to_win=invalid_score_to_win_type
        )

@pytest.mark.parametrize('invalid_score_to_win_value', [-15, -1, 0])
def test_de_stage_creation_invalid_score_to_win_value(eight_seeded_entries, invalid_score_to_win_value):
    with pytest.raises(ValueError):
        DEStage(
            stage_number=VALID_STAGE_NUMBER1,
            seeded_entries=eight_seeded_entries,
            score_to_win=invalid_score_to_win_value
        )

@pytest.mark.parametrize('invalid_has_third_place_match_type', [None, 0, 1.0, 'yes', [], (), {}, object()])
def test_de_stage_creation_invalid_has_third_place_match_type(eight_seeded_entries, invalid_has_third_place_match_type):
    with pytest.raises(TypeError):
        DEStage(
            stage_number=VALID_STAGE_NUMBER1,
            seeded_entries=eight_seeded_entries,
            has_third_place_match=invalid_has_third_place_match_type
        )

@pytest.mark.parametrize('invalid_use_consolation_bracket_type', [None, 0.0, 1, 'no', [], (), {}, object()])
def test_de_stage_creation_invalid_use_consolation_bracket_type(eight_seeded_entries, invalid_use_consolation_bracket_type):
    with pytest.raises(TypeError):
        DEStage(
            stage_number=VALID_STAGE_NUMBER1,
            seeded_entries=eight_seeded_entries,
            use_consolation_bracket=invalid_use_consolation_bracket_type
        )

@pytest.mark.parametrize('invalid_stop_at_round_type', [False, True, 'second', 2.0, [], (), {}, object()])
def test_de_stage_creation_invalid_stop_at_round_type(eight_seeded_entries, invalid_stop_at_round_type):
    with pytest.raises(TypeError):
        DEStage(
            stage_number=VALID_STAGE_NUMBER1,
            seeded_entries=eight_seeded_entries,
            stop_at_round=invalid_stop_at_round_type
        )

@pytest.mark.parametrize('invalid_stop_at_round_value', [-10, -1, 0, 3, 4, 10]) # Uses 8-entry bracket
def test_de_stage_creation_invalid_stop_at_round_value(eight_seeded_entries, invalid_stop_at_round_value):
    with pytest.raises(ValueError):
        DEStage(
            stage_number=VALID_STAGE_NUMBER1,
            seeded_entries=eight_seeded_entries,
            stop_at_round=invalid_stop_at_round_value
        )

@pytest.mark.parametrize('num_entries', [2, 3])
def test_de_stage_creation_invalid_not_enough_entries_for_third_place_match(num_entries):
    seeded_entries = factories.make_seeded_entries(n=num_entries, tournament_id=TOURNY_ID1)

    with pytest.raises(ValueError):
        DEStage(
            stage_number=VALID_STAGE_NUMBER1,
            seeded_entries=seeded_entries,
            has_third_place_match=True
        )

def test_de_stage_creation_invalid_cannot_have_stopped_bracket_and_third_place_match(eight_seeded_entries):
    with pytest.raises(ValueError):
        DEStage(
            stage_number=VALID_STAGE_NUMBER1,
            seeded_entries=eight_seeded_entries,
            stop_at_round=2,
            has_third_place_match=True
        )


# --- Equality Tests ---
def test_de_stage_equality(eight_seeded_entries):
    stage1 = DEStage(stage_number=VALID_STAGE_NUMBER1, seeded_entries=eight_seeded_entries)
    stage2 = DEStage(stage_number=VALID_STAGE_NUMBER1, seeded_entries=eight_seeded_entries)

    assert stage1 is not stage2
    assert stage1 == stage2

def test_de_stage_equality_ignores_other_attributes(eight_seeded_entries):
    stage1 = DEStage(
        stage_number=VALID_STAGE_NUMBER1, 
        seeded_entries=eight_seeded_entries,
        stop_at_round=2
    )

    stage2 = DEStage(
        stage_number=VALID_STAGE_NUMBER1, 
        seeded_entries=eight_seeded_entries,
        score_to_win=8,
        has_third_place_match=True,
        use_consolation_bracket=True
    )

    assert stage1 == stage2

@pytest.mark.parametrize('not_a_de_stage', [None, False, True, 'stage_three', 1, 2.0, [], (), {}, object()])
def test_de_stage_inequality_different_object(eight_seeded_entries, not_a_de_stage):
    stage = DEStage(stage_number=VALID_STAGE_NUMBER1, seeded_entries=eight_seeded_entries)

    assert stage != not_a_de_stage

def test_de_stage_inequality_different_tournament_id():
    seeded_entries1 = factories.make_seeded_entries(n=2, tournament_id=TOURNY_ID1)
    seeded_entries2 = factories.make_seeded_entries(n=2, tournament_id=TOURNY_ID2)

    stage1 = DEStage(stage_number=VALID_STAGE_NUMBER1, seeded_entries=seeded_entries1)
    stage2 = DEStage(stage_number=VALID_STAGE_NUMBER1, seeded_entries=seeded_entries2)

    assert stage1 != stage2

def test_de_stage_inequality_different_stage_number(eight_seeded_entries):
    stage1 = DEStage(stage_number=VALID_STAGE_NUMBER1, seeded_entries=eight_seeded_entries)
    stage2 = DEStage(stage_number=VALID_STAGE_NUMBER2, seeded_entries=eight_seeded_entries)

    assert stage1 != stage2
