import pytest

from dataclasses import FrozenInstanceError

from de.results.de_entry_result import DEEntryResult, DEEntryStatus


# --- Constants ---
VALID_STAGE_NUMBER1 = 1
VALID_ROUND_REACHED1 = 1
VALID_BRACKET_SEED1 = 1


# --- Initialization and Validation Tests ---
def test_de_entry_result_creation_valid_active_entry(entry1):
    entry = entry1
    stage_number = VALID_STAGE_NUMBER1
    de_seed = VALID_BRACKET_SEED1
    round_reached = VALID_ROUND_REACHED1
    place = None
    status = DEEntryStatus.ACTIVE

    de_entry_result = DEEntryResult(
        entry=entry, 
        stage_number=stage_number, 
        bracket_seed=de_seed, 
        round_reached=round_reached, 
        place=place, 
        status=status
    )

    assert de_entry_result.entry is entry
    assert de_entry_result.stage_number == stage_number
    assert de_entry_result.bracket_seed == de_seed
    assert de_entry_result.round_reached == round_reached
    assert de_entry_result.place == place
    assert de_entry_result.status == status

def test_de_entry_result_creation_valid_winner_entry(entry1):
    entry = entry1
    stage_number = VALID_STAGE_NUMBER1
    round_reached = 3
    de_seed = VALID_BRACKET_SEED1
    place = 1
    status = DEEntryStatus.WINNER

    de_entry_result = DEEntryResult(
        entry=entry,
        stage_number=stage_number,
        bracket_seed=de_seed,
        round_reached=round_reached,
        place=place,
        status=status
    )

    assert de_entry_result.entry is entry
    assert de_entry_result.stage_number == stage_number
    assert de_entry_result.bracket_seed == de_seed
    assert de_entry_result.round_reached == round_reached
    assert de_entry_result.place == place
    assert de_entry_result.status == status

@pytest.mark.parametrize('place', [None, 2, 7])
def test_de_entry_result_creation_valid_eliminated_entry(entry1, place):
    entry = entry1
    stage_number = VALID_STAGE_NUMBER1
    round_reached = 2
    de_seed = VALID_BRACKET_SEED1
    place = place
    status = DEEntryStatus.ELIMINATED

    de_entry_result = DEEntryResult(
        entry=entry,
        stage_number=stage_number,
        bracket_seed=de_seed,
        round_reached=round_reached,
        place=place,
        status=status
    )

    assert de_entry_result.entry is entry
    assert de_entry_result.stage_number == stage_number
    assert de_entry_result.bracket_seed == de_seed
    assert de_entry_result.round_reached == round_reached
    assert de_entry_result.place == place
    assert de_entry_result.status == status

def test_de_entry_result_creation_valid_is_frozen(entry1):
    de_entry_result = DEEntryResult(
        entry=entry1,
        stage_number=VALID_STAGE_NUMBER1,
        bracket_seed=VALID_BRACKET_SEED1,
        round_reached=VALID_ROUND_REACHED1,
        place=None,
        status=DEEntryStatus.ACTIVE
    )

    with pytest.raises(FrozenInstanceError):
        de_entry_result.stage_number = 2

@pytest.mark.parametrize('invalid_entry', [None, 10, 25.2, False, True, 'Bill', [], (), {}, object()])
def test_de_entry_result_creation_invalid_entry_type(invalid_entry):
    with pytest.raises(TypeError, match=' must be a TournamentEntry in '):
        DEEntryResult(
            entry=invalid_entry,
            stage_number=VALID_STAGE_NUMBER1,
            bracket_seed=VALID_BRACKET_SEED1,
            round_reached=VALID_ROUND_REACHED1,
            place=None,
            status=DEEntryStatus.ACTIVE
        )

@pytest.mark.parametrize('invalid_stage_number_type', [None, 3.14, False, True, 'second', [], (), {}, object()])
def test_de_entry_result_creation_invalid_stage_number_type(entry1, invalid_stage_number_type):
    with pytest.raises(TypeError):
        DEEntryResult(
            entry=entry1,
            stage_number=invalid_stage_number_type,
            bracket_seed=VALID_BRACKET_SEED1,
            round_reached=VALID_ROUND_REACHED1,
            place=None,
            status=DEEntryStatus.ACTIVE
        )

@pytest.mark.parametrize('invalid_stage_number_value', [-10, -1, 0])
def test_de_entry_result_creation_invalid_stage_number_value(entry1, invalid_stage_number_value):
    with pytest.raises(ValueError):
        DEEntryResult(
            entry=entry1,
            stage_number=invalid_stage_number_value,
            bracket_seed=VALID_BRACKET_SEED1,
            round_reached=VALID_ROUND_REACHED1,
            place=None,
            status=DEEntryStatus.ACTIVE
        )

@pytest.mark.parametrize('invalid_bracket_seed_type', [None, 1.0, False, True, 'first', [], (), {}, object()])
def test_de_entry_result_creation_invalid_bracket_seed_type(entry1, invalid_bracket_seed_type):
    with pytest.raises(TypeError):
        DEEntryResult(
            entry=entry1,
            stage_number=VALID_STAGE_NUMBER1,
            bracket_seed=invalid_bracket_seed_type,
            round_reached=VALID_ROUND_REACHED1,
            place=None,
            status=DEEntryStatus.ACTIVE
        )

@pytest.mark.parametrize('invalid_bracket_seed_value', [-2, -1, 0])
def test_de_entry_result_creation_invalid_bracket_seed_value(entry1, invalid_bracket_seed_value):
    with pytest.raises(ValueError):
        DEEntryResult(
            entry=entry1,
            stage_number=VALID_STAGE_NUMBER1,
            bracket_seed=invalid_bracket_seed_value,
            round_reached=VALID_ROUND_REACHED1,
            place=None,
            status=DEEntryStatus.ACTIVE
        )

@pytest.mark.parametrize('invalid_round_reached_type', [None, False, True, 1.5, 'fifth', [], (), {}, object()])
def test_de_entry_result_creation_invalid_round_reached_type(entry1, invalid_round_reached_type):
    with pytest.raises(TypeError):
        DEEntryResult(
            entry=entry1,
            stage_number=VALID_STAGE_NUMBER1,
            bracket_seed=VALID_BRACKET_SEED1,
            round_reached=invalid_round_reached_type,
            place=None,
            status=DEEntryStatus.ACTIVE
        )

@pytest.mark.parametrize('invalid_round_reached_value', [-3, -1, 0])
def test_de_entry_result_creation_invalid_round_reached_value(entry1, invalid_round_reached_value):
    with pytest.raises(ValueError):
        DEEntryResult(
            entry=entry1,
            stage_number=VALID_STAGE_NUMBER1,
            bracket_seed=VALID_BRACKET_SEED1,
            round_reached=invalid_round_reached_value,
            place=None,
            status=DEEntryStatus.ACTIVE
        )

@pytest.mark.parametrize('invalid_place_type', [False, True, 1.0, 'winner', [], (), {}, object()])
def test_de_entry_result_creation_invalid_place_type(entry1, invalid_place_type):
    with pytest.raises(TypeError):
        DEEntryResult(
            entry=entry1,
            stage_number=VALID_STAGE_NUMBER1,
            bracket_seed=VALID_BRACKET_SEED1,
            round_reached=VALID_ROUND_REACHED1,
            place=invalid_place_type,
            status=DEEntryStatus.ELIMINATED
        )

@pytest.mark.parametrize('invalid_place_value', [-10, -2, -1, 0])
def test_de_entry_result_creation_invalid_place_value(entry1, invalid_place_value):
    with pytest.raises(ValueError):
        DEEntryResult(
            entry=entry1,
            stage_number=VALID_STAGE_NUMBER1,
            bracket_seed=VALID_BRACKET_SEED1,
            round_reached=VALID_ROUND_REACHED1,
            place=invalid_place_value,
            status=DEEntryStatus.ELIMINATED
        )

@pytest.mark.parametrize('invalid_status', [None, 1, 0.0, False, True, 'eliminated', [], (), {}, object()])
def test_de_entry_result_creation_invalid_status(entry1, invalid_status):
    with pytest.raises(TypeError, match='Status must be a DEEntryStatus in '):
        DEEntryResult(
            entry=entry1,
            stage_number=VALID_STAGE_NUMBER1,
            bracket_seed=VALID_BRACKET_SEED1,
            round_reached=VALID_ROUND_REACHED1,
            place=None,
            status=invalid_status
        )

@pytest.mark.parametrize('invalid_place', [None, 2, 5, 10, 100])
def test_de_entry_result_creation_invalid_winner_and_place_do_not_match(entry1, invalid_place):
    with pytest.raises(ValueError, match='Winner must have place 1 in '):
        DEEntryResult(
            entry=entry1,
            stage_number=VALID_STAGE_NUMBER1,
            bracket_seed=VALID_BRACKET_SEED1,
            round_reached=VALID_ROUND_REACHED1,
            place=invalid_place,
            status=DEEntryStatus.WINNER
        )

@pytest.mark.parametrize('invalid_place', [1, 2, 3, 5, 100])
def test_de_entry_result_creation_invalid_active_and_place_do_not_match(entry1, invalid_place):
    with pytest.raises(ValueError, match='Active entry cannot have a confirmed finishing place in '):
        DEEntryResult(
            entry=entry1,
            stage_number=VALID_STAGE_NUMBER1,
            bracket_seed=VALID_BRACKET_SEED1,
            round_reached=VALID_ROUND_REACHED1,
            place=invalid_place,
            status=DEEntryStatus.ACTIVE
        )

def test_de_entry_result_creation_invalid_eliminated_and_place_do_not_match(entry1):
    with pytest.raises(ValueError, match=' cannot have place 1 in '):
        DEEntryResult(
            entry=entry1,
            stage_number=VALID_STAGE_NUMBER1,
            bracket_seed=VALID_BRACKET_SEED1,
            round_reached=VALID_ROUND_REACHED1,
            place=1,
            status=DEEntryStatus.ELIMINATED
        )
