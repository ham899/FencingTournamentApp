import pytest

from dataclasses import FrozenInstanceError

from entities.fencer import Fencer
from entities.tournament_entry import TournamentEntry
from poules.results.poule_entry_result import PouleEntryResult


# --- Constants ---
FENCER_ID1, FENCER_DISPLAY_NAME1, ENTRY_ID1  = 1, 'Jane', 1

FENCER_ID2, FENCER_DISPLAY_NAME2, ENTRY_ID2 = 2, 'John', 2

FENCER_ID3, FENCER_DISPLAY_NAME3, ENTRY_ID3 = 3, 'Steve', 3

POULE_ID1, POULE_ID2 = 1, 2

TOURNY_ID1, TOURNY_ID2 = 1, 2


# --- Fixtures ---
@pytest.fixture
def fencer1(): return Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)

@pytest.fixture
def fencer2(): return Fencer(FENCER_ID2, FENCER_DISPLAY_NAME2)

@pytest.fixture
def fencer3(): return Fencer(FENCER_ID3, FENCER_DISPLAY_NAME3)

@pytest.fixture
def entry1(fencer1): return TournamentEntry(ENTRY_ID1, TOURNY_ID1, fencer1)

@pytest.fixture
def entry2(fencer2): return TournamentEntry(ENTRY_ID2, TOURNY_ID1, fencer2)

@pytest.fixture
def entry3(fencer3): return TournamentEntry(ENTRY_ID3, TOURNY_ID2, fencer3)


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
            (4, 2, 15, 14)
        ]
    )
def test_poule_entry_result_creation_valid_majority_victories(entry1, num_matches, num_victories, touches_scored, touches_received):
    poule_entry_result = PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, num_matches, num_victories, touches_scored, touches_received)
    assert poule_entry_result.entry == entry1
    assert poule_entry_result.poule_id == POULE_ID1
    assert poule_entry_result.tournament_id == TOURNY_ID1
    assert poule_entry_result.num_matches == num_matches
    assert poule_entry_result.num_victories == num_victories
    assert poule_entry_result.touches_scored == touches_scored
    assert poule_entry_result.touches_received == touches_received

@pytest.mark.parametrize(
        ('num_matches', 'num_victories', 'touches_scored', 'touches_received'), 
        [
            (6, 2, 14, 28),
            (5, 0, 0, 25),
            (4, 1, 10, 20),
            (7, 3, 18, 25)
        ]
    )
def test_poule_entry_result_creation_valid_majority_defeats(entry1, num_matches, num_victories, touches_scored, touches_received):
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

def test_poule_entry_result_creation_invalid_entry_tournament_id_value(entry3):
    with pytest.raises(ValueError):
        PouleEntryResult(entry3, POULE_ID1, TOURNY_ID1, 0, 0, 0, 0)

@pytest.mark.parametrize('invalid_poule_id_type', [None, True, 1.0, '1DF3', [], (), {}])
def test_poule_entry_result_creation_invalid_poule_id_type(entry1, invalid_poule_id_type):
    with pytest.raises(TypeError):
        PouleEntryResult(entry1, invalid_poule_id_type, TOURNY_ID1, 0, 0, 0, 0)

@pytest.mark.parametrize('invalid_poule_id_value', [-100, -10, -1, 0])
def test_poule_entry_result_creation_invalid_poule_id_value(entry1, invalid_poule_id_value):
    with pytest.raises(ValueError):
        PouleEntryResult(entry1, invalid_poule_id_value, TOURNY_ID1, 0, 0, 0, 0)

@pytest.mark.parametrize('invalid_tournament_id_type', [None, True, 1.0, '1DF3', [], (), {}])
def test_poule_entry_result_creation_invalid_tournament_id_type(entry1, invalid_tournament_id_type):
    with pytest.raises(TypeError):
        PouleEntryResult(entry1, POULE_ID1, invalid_tournament_id_type, 0, 0, 0, 0)

@pytest.mark.parametrize('invalid_tournament_id_value', [-100, -10, -1, 0])
def test_poule_entry_result_creation_invalid_tournament_id_value(entry1, invalid_tournament_id_value):
    with pytest.raises(ValueError):
        PouleEntryResult(entry1, POULE_ID1, invalid_tournament_id_value, 0, 0, 0, 0)

@pytest.mark.parametrize('invalid_num_matches_type', [None, True, 1.0, 'ten', ['four'], ('five',), {}])
def test_poule_entry_result_creation_invalid_num_matches_type(entry1, invalid_num_matches_type):
    with pytest.raises(TypeError):
        PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, invalid_num_matches_type, 0, 0, 0)

@pytest.mark.parametrize('invalid_num_matches_value', [-100, -10, -1])
def test_poule_entry_result_creation_invalid_num_matches_value(entry1, invalid_num_matches_value):
    with pytest.raises(ValueError):
        PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, invalid_num_matches_value, 0, 0, 0)

@pytest.mark.parametrize('invalid_num_victories_type', [None, True, 1.0, 'ten', ['four'], ('five',), {}])
def test_poule_entry_result_creation_invalid_num_victories_type(entry1, invalid_num_victories_type):
    with pytest.raises(TypeError):
        PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, 0, invalid_num_victories_type, 0, 0)

@pytest.mark.parametrize('invalid_num_victories_negative', [-100, -10, -1])
def test_poule_entry_result_creation_invalid_num_victories_negative(entry1, invalid_num_victories_negative):
    with pytest.raises(ValueError):
        PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, 0, invalid_num_victories_negative, 0, 0)

@pytest.mark.parametrize('num_matches, num_victories', [(0, 1), (2, 6), (3, 4)])
def test_poule_entry_result_creation_invalid_num_victories_exceeds_matches(entry1, num_matches, num_victories):
    with pytest.raises(ValueError):
        PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, num_matches, num_victories, 0, 0)

@pytest.mark.parametrize('invalid_touches_scored_type', [None, True, 1.0, 'ten', ['four'], ('five',), {}])
def test_poule_entry_result_creation_invalid_touches_scored_type(entry1, invalid_touches_scored_type):
    with pytest.raises(TypeError):
        PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, 0, 0, invalid_touches_scored_type, 0)

@pytest.mark.parametrize('invalid_touches_scored_value', [-100, -10, -1])
def test_poule_entry_result_creation_invalid_touches_scored_value(entry1, invalid_touches_scored_value):
    with pytest.raises(ValueError):
        PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, 0, 0, invalid_touches_scored_value, 0)

@pytest.mark.parametrize('touches_scored', [1, 5, 10, 15, 20])
def test_poule_entry_result_creation_invalid_touches_scored_non_zero_when_no_matches(entry1, touches_scored):
    with pytest.raises(ValueError):
        PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, 0, 0, touches_scored, 0)

@pytest.mark.parametrize('invalid_touches_received_type', [None, True, 1.0, 'ten', ['four'], ('five',), {}])
def test_poule_entry_result_creation_invalid_touches_received_type(entry1, invalid_touches_received_type):
    with pytest.raises(TypeError):
        PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, 0, 0, 0, invalid_touches_received_type)

@pytest.mark.parametrize('invalid_touches_received_value', [-100, -10, -1])
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
    assert poule_entry1_result.display_name == 'Jane'

    poule_entry2_result = PouleEntryResult(entry2, POULE_ID1, TOURNY_ID1, 0, 0, 0, 0)
    assert poule_entry2_result.display_name == 'John'

    poule_entry3_result = PouleEntryResult(entry3, POULE_ID1, TOURNY_ID2, 0, 0, 0, 0)
    assert poule_entry3_result.display_name == 'Steve'

def test_poule_entry_result_changing_display_name_property(entry1):
    poule_entry_result = PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, 0, 0, 0, 0)
    assert poule_entry_result.display_name == 'Jane'

    poule_entry_result.entry.fencer.update_display_name('John')
    assert poule_entry_result.display_name == 'John'

def test_poule_entry_result_ratio_property_zero_matches(entry1):
    poule_entry_result = PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, 0, 0, 0, 0)
    assert poule_entry_result.victory_ratio == 0.0

@pytest.mark.parametrize(('num_matches', 'num_victories'), [(2, 1), (4, 3), (6, 5)])
def test_poule_entry_result_ratio_property_non_zero_matches(entry1, num_matches, num_victories):
    num_losses = num_matches - num_victories
    poule_entry_result = PouleEntryResult(entry1, 
                                          POULE_ID1, 
                                          TOURNY_ID1, 
                                          num_matches, 
                                          num_victories, 
                                          5 * num_victories + 2 * num_losses, 
                                          5 * num_losses + 3 * num_victories)

    assert poule_entry_result.num_matches == num_matches
    assert poule_entry_result.num_victories == num_victories
    assert poule_entry_result.touches_scored == 5 * num_victories + 2 * num_losses
    assert poule_entry_result.touches_received == 5 * num_losses + 3 * num_victories
    assert poule_entry_result.victory_ratio == num_victories / num_matches

@pytest.mark.parametrize(('num_matches', 'num_victories', 'touches_scored', 'touches_received'), [(2, 1, 7, 8), (4, 2, 15, 13), (6, 6, 30, 10)])
def test_poule_entry_result_indicator_property(entry1, num_matches, num_victories, touches_scored, touches_received):
    poule_entry_result = PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, num_matches, num_victories, touches_scored, touches_received)
    assert poule_entry_result.indicator == touches_scored - touches_received


# --- Equality Tests ---
@pytest.mark.parametrize(('num_matches', 'num_victories', 'touches_scored', 'touches_received'), [(0, 0, 0, 0), (5, 3, 15, 10), (6, 6, 30, 0)])
def test_poule_entry_result_equality(entry1, num_matches, num_victories, touches_scored, touches_received):
    poule_entry_result_1 = PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, num_matches, num_victories, touches_scored, touches_received)
    poule_entry_result_2 = PouleEntryResult(entry1, POULE_ID1, TOURNY_ID1, num_matches, num_victories, touches_scored, touches_received)

    assert poule_entry_result_1 == poule_entry_result_2

@pytest.mark.parametrize(
        ('result1_stats', 'result2_stats'), 
        [
            ((2, 0, 0, 0), (3, 0, 0, 0)), 
            ((2, 0, 0, 0), (2, 1, 0, 0)), 
            ((2, 0, 0, 0), (2, 0, 1, 0)), 
            ((2, 0, 0, 0), (2, 0, 0, 1))
        ]
)
def test_poule_entry_result_inequality_same_entry_different_results(entry1, result1_stats, result2_stats):
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
def test_poule_entry_result_inequality_same_entry_different_tournaments(fencer1, num_matches, num_victories, touches_scored, touches_received):
    entry11 = TournamentEntry(ENTRY_ID1, TOURNY_ID1, fencer1)
    entry12 = TournamentEntry(ENTRY_ID1, TOURNY_ID2, fencer1)

    poule_entry_result_1 = PouleEntryResult(entry11, POULE_ID1, TOURNY_ID1, num_matches, num_victories, touches_scored, touches_received)
    poule_entry_result_2 = PouleEntryResult(entry12, POULE_ID1, TOURNY_ID2, num_matches, num_victories, touches_scored, touches_received)

    assert poule_entry_result_1 != poule_entry_result_2