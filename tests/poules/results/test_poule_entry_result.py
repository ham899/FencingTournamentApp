import pytest
import copy

from entities.fencer import Fencer
from entities.tournament_entry import TournamentEntry
from matches.poule_match import PouleMatch
from matches.match import Match
from poules.results.poule_entry_result import PouleEntryResult


# --- Constants ---
FENCER_ID1 = 1
FENCER_DISPLAY_NAME1 = 'Jane'
ENTRY_ID1 = 1

FENCER_ID2 = 2
FENCER_DISPLAY_NAME2 = 'John'
ENTRY_ID2 = 2

FENCER_ID3 = 3
FENCER_DISPLAY_NAME3 = 'Steve'
ENTRY_ID3 = 3

MATCH_ID = 1
POULE_ID = 1
TOURNY_ID = 1


# --- Helper Functions ---
def make_poule_match(
    entry1: TournamentEntry, 
    entry2: TournamentEntry, 
    *, 
    match_id: int = MATCH_ID, 
    tournament_id: int = TOURNY_ID, 
    poule_id: int = POULE_ID,
    match_index: int = 0
) -> PouleMatch:
    """Creates a valid uncompleted PouleMatch for use in tests."""
    return PouleMatch(
        id=match_id, 
        tournament_id=tournament_id, 
        entry1=entry1, 
        entry2=entry2, 
        poule_id=poule_id, 
        match_index=match_index
    )


# --- Fixtures ---
@pytest.fixture
def fencer1():
    return Fencer(id=FENCER_ID1, display_name=FENCER_DISPLAY_NAME1)

@pytest.fixture
def fencer2():
    return Fencer(id=FENCER_ID2, display_name=FENCER_DISPLAY_NAME2)

@pytest.fixture
def fencer3():
    return Fencer(id=FENCER_ID3, display_name=FENCER_DISPLAY_NAME3)

@pytest.fixture
def entry1(fencer1):
    return TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer1)

@pytest.fixture
def entry2(fencer2):
    return TournamentEntry(id=ENTRY_ID2, tournament_id=TOURNY_ID, fencer=fencer2)

@pytest.fixture
def entry3(fencer3):
    return TournamentEntry(id=ENTRY_ID3, tournament_id=TOURNY_ID, fencer=fencer3)

@pytest.fixture
def poule_entry1_result(entry1):
    return PouleEntryResult(entry1, POULE_ID, TOURNY_ID)


# --- Initialization and Validation Tests ---
def test_poule_entry_result_creation_valid(entry1):
    poule_entry_result = PouleEntryResult(entry1, POULE_ID, TOURNY_ID)
    assert poule_entry_result.entry == entry1
    assert poule_entry_result.poule_id == POULE_ID
    assert poule_entry_result.tournament_id == TOURNY_ID
    assert poule_entry_result.num_matches == 0
    assert poule_entry_result.num_victories == 0
    assert poule_entry_result.touches_scored == 0
    assert poule_entry_result.touches_received == 0

@pytest.mark.parametrize('invalid_entry_type', [None, False, 0.0, 1, 'Jane', [], (), {}])
def test_poule_entry_result_creation_invalid_entry_type(invalid_entry_type):
    with pytest.raises(TypeError):
        PouleEntryResult(invalid_entry_type, POULE_ID, TOURNY_ID)

def test_poule_entry_result_creation_invalid_entry_tournament_id_value(fencer1):
    DIFFERENT_TOURNY_ID = 2
    entry = TournamentEntry(id=ENTRY_ID1, tournament_id=DIFFERENT_TOURNY_ID, fencer=fencer1)
    with pytest.raises(ValueError):
        PouleEntryResult(entry, POULE_ID, TOURNY_ID)

@pytest.mark.parametrize('invalid_poule_id_type', [None, True, 1.0, '1DF3', [], (), {}])
def test_poule_entry_result_creation_invalid_poule_id_type(entry1, invalid_poule_id_type):
    with pytest.raises(TypeError):
        PouleEntryResult(entry1, invalid_poule_id_type, TOURNY_ID)

def test_poule_entry_result_creation_invalid_poule_id_zero(entry1):
    with pytest.raises(ValueError):
        PouleEntryResult(entry1, 0, TOURNY_ID)

@pytest.mark.parametrize('negative_poule_id', [-100, -10, -1])
def test_poule_entry_result_creation_invalid_poule_id_negative(entry1, negative_poule_id):
    with pytest.raises(ValueError):
        PouleEntryResult(entry1, negative_poule_id, TOURNY_ID)

@pytest.mark.parametrize('invalid_tournament_id_type', [None, True, 1.0, '1DF3', [], (), {}])
def test_poule_entry_result_creation_invalid_tournament_id_type(entry1, invalid_tournament_id_type):
    with pytest.raises(TypeError):
        PouleEntryResult(entry1, POULE_ID, invalid_tournament_id_type)

def test_poule_entry_result_creation_invalid_tournament_id_zero(entry1):
    with pytest.raises(ValueError):
        PouleEntryResult(entry1, POULE_ID, 0)

@pytest.mark.parametrize('negative_tournament_id', [-100, -10, -1])
def test_poule_entry_result_creation_invalid_tournament_id_negative(entry1, negative_tournament_id):
    with pytest.raises(ValueError):
        PouleEntryResult(entry1, POULE_ID, negative_tournament_id)


# --- Property Tests ---
def test_poule_entry_result_display_name_property(poule_entry1_result):
    assert poule_entry1_result.display_name == 'Jane'

def test_poule_entry_result_changing_display_name_property(poule_entry1_result):
    assert poule_entry1_result.display_name == 'Jane'
    poule_entry1_result.entry.fencer.update_display_name('John')
    assert poule_entry1_result.display_name == 'John'

def test_poule_entry_result_ratio_property(poule_entry1_result):
    assert poule_entry1_result.ratio == 0.0

def test_poule_entry_result_changing_ratio_property(poule_entry1_result):
    assert poule_entry1_result.ratio == 0.0
    poule_entry1_result.num_matches = 2
    poule_entry1_result.num_victories = 1
    assert poule_entry1_result.ratio == 1 / 2

def test_poule_entry_result_indicator_property(poule_entry1_result):
    assert poule_entry1_result.indicator == 0

def test_poule_entry_result_changing_indicator_property(poule_entry1_result):
    assert poule_entry1_result.indicator == 0
    poule_entry1_result.touches_scored = 10
    poule_entry1_result.touches_received = 11
    assert poule_entry1_result.indicator == -1


# --- Equality Tests ---
def test_poule_entry_result_equality(entry1, poule_entry1_result):
    poule_entry_result_2 = PouleEntryResult(entry1, POULE_ID, TOURNY_ID)
    assert poule_entry1_result == poule_entry_result_2

def test_poule_entry_result_inequality_same_entry_different_results(poule_entry1_result):
    poule_entry_result_original = copy.deepcopy(poule_entry1_result)
    poule_entry1_result.num_matches = 1
    poule_entry1_result.num_victories = 1
    poule_entry1_result.touches_scored = 5
    poule_entry1_result.touches_received = 2
    assert poule_entry_result_original != poule_entry1_result

def test_poule_entry_result_inequality_different_entries(entry2, poule_entry1_result):
    poule_entry_result_2 = PouleEntryResult(entry2, POULE_ID, TOURNY_ID)
    assert poule_entry1_result != poule_entry_result_2

def test_poule_entry_result_inequality_different_poules(entry1, poule_entry1_result):
    DIFFERENT_POULE_ID = 2
    poule_entry_result_2 = PouleEntryResult(entry1, DIFFERENT_POULE_ID, TOURNY_ID)
    assert poule_entry1_result != poule_entry_result_2

def test_poule_entry_result_inequality_different_tournaments(entry1, poule_entry1_result):
    DIFFERENT_TOURNY_ID = 2

    # Update the tournament ID for entry to belong to this different tournament
    entry1.tournament_id = DIFFERENT_TOURNY_ID

    poule_entry_result_2 = PouleEntryResult(entry1, POULE_ID, DIFFERENT_TOURNY_ID)
    assert poule_entry1_result != poule_entry_result_2


# --- State Update Helper Method Tests ---
def test_poule_entry_result__reset_clears_calculated_totals(poule_entry1_result):
    poule_entry1_result.num_matches = 3
    poule_entry1_result.num_victories = 2
    poule_entry1_result.touches_scored = 13
    poule_entry1_result.touches_received = 9

    poule_entry1_result._reset()

    assert poule_entry1_result.num_matches == 0
    assert poule_entry1_result.num_victories == 0
    assert poule_entry1_result.touches_scored == 0
    assert poule_entry1_result.touches_received == 0

def test_poule_entry_result__reset_does_not_change_entry_or_context(entry1, poule_entry1_result):
    poule_entry1_result.num_matches = 3
    poule_entry1_result.num_victories = 2
    poule_entry1_result.touches_scored = 13
    poule_entry1_result.touches_received = 9

    poule_entry1_result._reset()

    assert poule_entry1_result.entry == entry1
    assert poule_entry1_result.poule_id == POULE_ID
    assert poule_entry1_result.tournament_id == TOURNY_ID
    assert poule_entry1_result.display_name == FENCER_DISPLAY_NAME1


# --- Result Calculation Helper Method Tests ---
@pytest.mark.parametrize('invalid_poule_match_type', [None, False, 0, 0.0, 'match', [], (), {}])
def test_poule_entry_result__add_match_result_rejects_non_poule_match(poule_entry1_result, invalid_poule_match_type):
    with pytest.raises(TypeError):
        poule_entry1_result._add_match_result(invalid_poule_match_type)
    
    MATCH_SCORE_TO_WIN = 5
    match = Match(MATCH_ID, MATCH_SCORE_TO_WIN)
    match.record_score(5,2)
    
    with pytest.raises(TypeError):
        poule_entry1_result._add_match_result(match)

def test_poule_entry_result__add_match_result_rejects_match_from_different_tournament(entry1, entry2, poule_entry1_result):
    DIFFERENT_TOURNAMENT_ID = 2
    entry1.tournament_id = DIFFERENT_TOURNAMENT_ID
    entry2.tournament_id = DIFFERENT_TOURNAMENT_ID
    match = make_poule_match(entry1, entry2, tournament_id=DIFFERENT_TOURNAMENT_ID)

    with pytest.raises(ValueError):
        poule_entry1_result._add_match_result(match)

    assert poule_entry1_result.num_matches == 0
    assert poule_entry1_result.num_victories == 0
    assert poule_entry1_result.touches_scored == 0
    assert poule_entry1_result.touches_received == 0

def test_poule_entry_result__add_match_result_rejects_incomplete_match(entry1, entry2, poule_entry1_result):
    match = make_poule_match(entry1, entry2)

    with pytest.raises(ValueError):
        poule_entry1_result._add_match_result(match)

    assert poule_entry1_result.num_matches == 0
    assert poule_entry1_result.num_victories == 0
    assert poule_entry1_result.touches_scored == 0
    assert poule_entry1_result.touches_received == 0


def test_poule_entry_result__add_match_result_does_nothing_when_entry_is_not_in_match(entry2, entry3, poule_entry1_result):
    match = make_poule_match(entry2, entry3)
    match.record_score(5,2)

    poule_entry1_result._add_match_result(match)

    assert poule_entry1_result.num_matches == 0
    assert poule_entry1_result.num_victories == 0
    assert poule_entry1_result.touches_scored == 0
    assert poule_entry1_result.touches_received == 0

@pytest.mark.parametrize(('score1', 'score2'), 
                         [(5,0), (5,1), (5,2), (5,3), (5,4),
                          (0,5), (1,5), (2,5), (3,5), (4,5)])
def test_poule_entry_result__add_match_result_records_normal_result(score1, score2, entry1, entry2, poule_entry1_result):
    match = make_poule_match(entry1, entry2)
    match.record_score(score1, score2)

    victory = 1 if score1 > score2 else 0

    poule_entry1_result._add_match_result(match)

    assert poule_entry1_result.num_matches == 1
    assert poule_entry1_result.num_victories == victory
    assert poule_entry1_result.touches_scored == score1
    assert poule_entry1_result.touches_received == score2


def test_poule_entry_result__add_match_result_accumulates_results_from_multiple_matches(entry1, entry2, entry3, poule_entry1_result):
    assert poule_entry1_result.num_matches == 0
    assert poule_entry1_result.num_victories == 0
    assert poule_entry1_result.touches_scored == 0
    assert poule_entry1_result.touches_received == 0
    assert poule_entry1_result.ratio == 0.0
    assert poule_entry1_result.indicator == 0
    
    first_match = make_poule_match(entry1, entry2)
    first_match.record_score(5,2)

    poule_entry1_result._add_match_result(first_match)

    assert poule_entry1_result.num_matches == 1
    assert poule_entry1_result.num_victories == 1
    assert poule_entry1_result.touches_scored == 5
    assert poule_entry1_result.touches_received == 2
    assert poule_entry1_result.ratio == 1.0
    assert poule_entry1_result.indicator == 3

    second_match = make_poule_match(entry3, entry1)
    second_match.record_score(5,4)

    poule_entry1_result._add_match_result(second_match)

    assert poule_entry1_result.num_matches == 2
    assert poule_entry1_result.num_victories == 1
    assert poule_entry1_result.touches_scored == 9
    assert poule_entry1_result.touches_received == 7
    assert poule_entry1_result.ratio == 0.5
    assert poule_entry1_result.indicator == 2
