from dataclasses import FrozenInstanceError

import pytest

from constants import TOURNY_ID1, TOURNY_ID2, POULE_ID1, POULE_ID2, ENTRY_ID1

from entities.tournament_entry import TournamentEntry
from poules.results.poule_entry_result import PouleEntryResult


# --- Constants ---
INVALID_INT_TYPES = [None, False, True, 1.0, 'ten', ['four'], ('five',), {}]
NEGATIVE_INTS = [-10, -5, -1]
NON_POSITIVE_INTS = NEGATIVE_INTS + [0]


# --- Initialization and Validation Tests ---
def test_poule_entry_result_creation_valid_zeros(entry1):
    poule_entry_result = PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, 0, 0, 0, 0)

    assert poule_entry_result.entry == entry1
    assert poule_entry_result.poule_id == POULE_ID1
    assert poule_entry_result.tournament_id == TOURNY_ID1
    assert poule_entry_result.num_matches == 0
    assert poule_entry_result.num_victories == 0
    assert poule_entry_result.touches_scored == 0
    assert poule_entry_result.touches_received == 0

@pytest.mark.parametrize(
        ('num_matches', 'num_victories', 'touches_scored', 'touches_received'), 
        [
            (5, 4, 21, 13),
            (6, 6, 30, 0),
            (7, 4, 25, 20),
            (4, 2, 15, 14),
            (6, 2, 14, 28),
            (5, 0, 0, 25),
            (4, 1, 10, 20),
            (7, 3, 18, 25)
        ]
    )
def test_poule_entry_result_creation_valid(entry1, num_matches, num_victories, touches_scored, touches_received):
    poule_entry_result = PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, num_matches, num_victories, touches_scored, touches_received)
    
    assert poule_entry_result.entry == entry1
    assert poule_entry_result.poule_id == POULE_ID1
    assert poule_entry_result.tournament_id == TOURNY_ID1
    assert poule_entry_result.num_matches == num_matches
    assert poule_entry_result.num_victories == num_victories
    assert poule_entry_result.touches_scored == touches_scored
    assert poule_entry_result.touches_received == touches_received


def test_poule_entry_result_fields_cannot_be_reassigned(entry1):
    poule_entry_result = PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, 0, 0, 0, 0)

    with pytest.raises(FrozenInstanceError):
        poule_entry_result.entry = entry1

    with pytest.raises(FrozenInstanceError):
        poule_entry_result.poule_id = POULE_ID2

    with pytest.raises(FrozenInstanceError):
        poule_entry_result.tournament_id = TOURNY_ID2

    with pytest.raises(FrozenInstanceError):
        poule_entry_result.num_matches = 5

    with pytest.raises(FrozenInstanceError):
        poule_entry_result.num_victories = 3

    with pytest.raises(FrozenInstanceError):
        poule_entry_result.touches_scored = 15

    with pytest.raises(FrozenInstanceError):
        poule_entry_result.touches_received = 10

@pytest.mark.parametrize('invalid_entry_type', [None, False, 0.0, 1, 'Jane', [], (), {}])
def test_poule_entry_result_creation_invalid_entry_type(invalid_entry_type):
    with pytest.raises(TypeError):
        PouleEntryResult(invalid_entry_type, POULE_ID1, TOURNY_ID1, 0, 0, 0, 0)

@pytest.mark.parametrize(('invalid_tournament_id', 'exception_type'), [(None, TypeError), (0, ValueError)])
def test_poule_entry_result_creation_invalid_entry_tournament_id(entry1, invalid_tournament_id, exception_type):
    entry1.tournament_id = invalid_tournament_id

    with pytest.raises(exception_type):
        PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, 0, 0, 0, 0)


def test_poule_entry_result_creation_invalid_entry_tournament_id_does_not_match(entry1):
    with pytest.raises(ValueError):
        PouleEntryResult(entry1, POULE_ID1, TOURNY_ID2, 0, 0, 0, 0)


@pytest.mark.parametrize('invalid_poule_id_type', INVALID_INT_TYPES)
def test_poule_entry_result_creation_invalid_poule_id_type(entry1, invalid_poule_id_type):
    with pytest.raises(TypeError):
        PouleEntryResult(entry1, invalid_poule_id_type, TOURNY_ID1, 0, 0, 0, 0)

@pytest.mark.parametrize('invalid_poule_id_value', NON_POSITIVE_INTS)
def test_poule_entry_result_creation_invalid_poule_id_value(entry1, invalid_poule_id_value):
    with pytest.raises(ValueError):
        PouleEntryResult(entry1, invalid_poule_id_value, TOURNY_ID1, 0, 0, 0, 0)

@pytest.mark.parametrize('invalid_tournament_id_type', INVALID_INT_TYPES)
def test_poule_entry_result_creation_invalid_tournament_id_type(entry1, invalid_tournament_id_type):
    with pytest.raises(TypeError):
        PouleEntryResult(entry1, POULE_ID1, invalid_tournament_id_type, 0, 0, 0, 0)

@pytest.mark.parametrize('invalid_tournament_id_value', NON_POSITIVE_INTS)
def test_poule_entry_result_creation_invalid_tournament_id_value(entry1, invalid_tournament_id_value):
    with pytest.raises(ValueError):
        PouleEntryResult(entry1, POULE_ID1, invalid_tournament_id_value, 0, 0, 0, 0)

@pytest.mark.parametrize('invalid_num_matches_type', INVALID_INT_TYPES)
def test_poule_entry_result_creation_invalid_num_matches_type(entry1, invalid_num_matches_type):
    with pytest.raises(TypeError):
        PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, invalid_num_matches_type, 0, 0, 0)

@pytest.mark.parametrize('invalid_num_matches_value', NEGATIVE_INTS)
def test_poule_entry_result_creation_invalid_num_matches_value(entry1, invalid_num_matches_value):
    with pytest.raises(ValueError):
        PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, invalid_num_matches_value, 0, 0, 0)

@pytest.mark.parametrize('invalid_num_victories_type', INVALID_INT_TYPES)
def test_poule_entry_result_creation_invalid_num_victories_type(entry1, invalid_num_victories_type):
    with pytest.raises(TypeError):
        PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, 0, invalid_num_victories_type, 0, 0)

@pytest.mark.parametrize('invalid_num_victories_negative', NEGATIVE_INTS)
def test_poule_entry_result_creation_invalid_num_victories_negative(entry1, invalid_num_victories_negative):
    with pytest.raises(ValueError):
        PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, 0, invalid_num_victories_negative, 0, 0)

@pytest.mark.parametrize('num_matches, num_victories', [(0, 1), (2, 6), (3, 4)])
def test_poule_entry_result_creation_invalid_num_victories_exceeds_matches(entry1, num_matches, num_victories):
    with pytest.raises(ValueError):
        PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, num_matches, num_victories, 0, 0)

@pytest.mark.parametrize('invalid_touches_scored_type', INVALID_INT_TYPES)
def test_poule_entry_result_creation_invalid_touches_scored_type(entry1, invalid_touches_scored_type):
    with pytest.raises(TypeError):
        PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, 0, 0, invalid_touches_scored_type, 0)

@pytest.mark.parametrize('invalid_touches_scored_value', NEGATIVE_INTS)
def test_poule_entry_result_creation_invalid_touches_scored_value(entry1, invalid_touches_scored_value):
    with pytest.raises(ValueError):
        PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, 0, 0, invalid_touches_scored_value, 0)

@pytest.mark.parametrize('touches_scored', [1, 5, 10, 15, 20])
def test_poule_entry_result_creation_invalid_touches_scored_non_zero_when_no_matches(entry1, touches_scored):
    with pytest.raises(ValueError):
        PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, 0, 0, touches_scored, 0)

@pytest.mark.parametrize('invalid_touches_received_type', INVALID_INT_TYPES)
def test_poule_entry_result_creation_invalid_touches_received_type(entry1, invalid_touches_received_type):
    with pytest.raises(TypeError):
        PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, 0, 0, 0, invalid_touches_received_type)

@pytest.mark.parametrize('invalid_touches_received_value', NEGATIVE_INTS)
def test_poule_entry_result_creation_invalid_touches_received_value(entry1, invalid_touches_received_value):
    with pytest.raises(ValueError):
        PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, 0, 0, 0, invalid_touches_received_value)

@pytest.mark.parametrize('touches_received', [1, 5, 10, 15, 20])
def test_poule_entry_result_creation_invalid_touches_received_non_zero_when_no_matches(entry1, touches_received):
    with pytest.raises(ValueError):
        PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, 0, 0, 0, touches_received)


# --- Property Tests ---
def test_poule_entry_result_display_name_property(entry1, entry2, entry3):
    poule_entry1_result = PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, 0, 0, 0, 0)
    assert poule_entry1_result.display_name == entry1.display_name

    poule_entry2_result = PouleEntryResult(entry2, POULE_ID1, TOURNY_ID1, 0, 0, 0, 0)
    assert poule_entry2_result.display_name == entry2.display_name

    poule_entry3_result = PouleEntryResult(entry3, POULE_ID1, TOURNY_ID1, 0, 0, 0, 0)
    assert poule_entry3_result.display_name == entry3.display_name

def test_poule_entry_result_changing_display_name_property(entry1):
    poule_entry_result = PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, 0, 0, 0, 0)
    
    assert poule_entry_result.display_name == entry1.display_name

    poule_entry_result.entry.fencer.update_display_name('Jane')
    
    assert entry1.display_name == 'Jane'
    
    assert poule_entry_result.display_name == entry1.display_name

@pytest.mark.parametrize(
        ('num_matches', 'num_victories', 'expected_ratio', 'touches_scored', 'touches_received'),
        [
            (0, 0, 0.0, 0, 0),
            (5, 0, 0.0, 0, 25),
            (2, 1, 0.5, 7, 7),
            (5, 5, 1.0, 25, 0),
            (4, 3, 0.75, 17, 10),
            (6, 5, 5 / 6, 26, 14)
        ]
)
def test_poule_entry_result_victory_ratio_property(entry1, num_matches, num_victories, expected_ratio, touches_scored, touches_received):
    result = PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, num_matches, num_victories, touches_scored, touches_received)

    assert result.victory_ratio == expected_ratio

@pytest.mark.parametrize(
        ('num_matches', 'num_victories', 'touches_scored', 'touches_received', 'expected_indicator'),
        [
            (0, 0, 0, 0, 0),
            (5, 0, 0, 25, -25),
            (2, 1, 7, 7, 0),
            (5, 5, 25, 0, 25),
            (4, 2, 12, 16, -4),
            (6, 5, 26, 14, 12)
        ]
)
def test_poule_entry_result_indicator_property(entry1, num_matches, num_victories, touches_scored, touches_received, expected_indicator):
    result = PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, num_matches, num_victories, touches_scored, touches_received)
    
    assert result.indicator == expected_indicator


# --- Equality Tests ---
@pytest.mark.parametrize(('num_matches', 'num_victories', 'touches_scored', 'touches_received'), [(0, 0, 0, 0), (5, 3, 15, 10), (6, 6, 30, 0)])
def test_poule_entry_result_equality(entry1, num_matches, num_victories, touches_scored, touches_received):
    poule_entry_result_1 = PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, num_matches, num_victories, touches_scored, touches_received)
    poule_entry_result_2 = PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, num_matches, num_victories, touches_scored, touches_received)

    assert poule_entry_result_1 == poule_entry_result_2

def test_poule_entry_result_equality_equivalent_entry_objects(entry1):
    equivalent_entry = TournamentEntry(entry1.id, entry1.tournament_id, entry1.fencer)

    num_matches, num_victories, touches_scored, touches_received = 5, 3, 18, 15

    result1 = PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, num_matches, num_victories, touches_scored, touches_received)

    result2 = PouleEntryResult(equivalent_entry, POULE_ID1, TOURNY_ID1,  num_matches, num_victories, touches_scored, touches_received)

    assert entry1 is not equivalent_entry
    assert entry1 == equivalent_entry
    assert result1 == result2

@pytest.mark.parametrize(
        ('result1_stats', 'result2_stats'), 
        [
            ((2, 0, 0, 0), (3, 0, 0, 0)), 
            ((2, 0, 0, 0), (2, 1, 0, 0)), 
            ((2, 0, 0, 0), (2, 0, 1, 0)), 
            ((2, 0, 0, 0), (2, 0, 0, 1))
        ]
)
def test_poule_entry_result_inequality_same_entry_id_different_results(entry1, result1_stats, result2_stats):
    poule_entry_result_1 = PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, *result1_stats)
    poule_entry_result_2 = PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, *result2_stats)

    assert poule_entry_result_1 != poule_entry_result_2

@pytest.mark.parametrize(('num_matches', 'num_victories', 'touches_scored', 'touches_received'), [(0, 0, 0, 0), (5, 3, 15, 10), (6, 6, 30, 0)])
def test_poule_entry_result_inequality_different_entries(entry1, entry2, num_matches, num_victories, touches_scored, touches_received):
    poule_entry1_result = PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, num_matches, num_victories, touches_scored, touches_received)
    poule_entry2_result = PouleEntryResult(entry2, POULE_ID1, TOURNY_ID1, num_matches, num_victories, touches_scored, touches_received)

    assert poule_entry1_result != poule_entry2_result

@pytest.mark.parametrize(('num_matches', 'num_victories', 'touches_scored', 'touches_received'), [(0, 0, 0, 0), (5, 3, 15, 10), (6, 6, 30, 0)])
def test_poule_entry_result_inequality_same_entry_different_poules(entry1, num_matches, num_victories, touches_scored, touches_received):
    poule_entry_result_1 = PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, num_matches, num_victories, touches_scored, touches_received)
    poule_entry_result_2 = PouleEntryResult(entry1, POULE_ID2, TOURNY_ID1, num_matches, num_victories, touches_scored, touches_received)

    assert poule_entry_result_1 != poule_entry_result_2

@pytest.mark.parametrize(('num_matches', 'num_victories', 'touches_scored', 'touches_received'), [(0, 0, 0, 0), (5, 3, 15, 10), (6, 6, 30, 0)])
def test_poule_entry_result_inequality_same_entry_id_different_tournaments(fencer1, num_matches, num_victories, touches_scored, touches_received):
    entry11 = TournamentEntry(ENTRY_ID1, TOURNY_ID1, fencer1)
    entry12 = TournamentEntry(ENTRY_ID1, TOURNY_ID2, fencer1)

    poule_entry_result_1 = PouleEntryResult(entry11, POULE_ID1, TOURNY_ID1, num_matches, num_victories, touches_scored, touches_received)
    poule_entry_result_2 = PouleEntryResult(entry12, POULE_ID1, TOURNY_ID2, num_matches, num_victories, touches_scored, touches_received)

    assert poule_entry_result_1 != poule_entry_result_2