"""Tests poule-specific attributes and methods."""


import pytest

from matches.poule_match import PouleMatch, PouleMatchResultType
from entities.tournament_entry import TournamentEntry
from entities.fencer import Fencer


# --- Constants ---
FENCER_ID1 = 1
FENCER_ID2 = 2
DISPLAY_NAME1 = 'Ben'
DISPLAY_NAME2 = 'Bill'
ENTRY_ID1 = 1
ENTRY_ID2 = 2
TEST_SCORE_TO_WIN = 8
TOURNY_ID = 1
POULE_ID = 1
MATCH_ID1 = 1
MATCH_ID2 = 2


# --- Fixtures ---
@pytest.fixture
def fencer1():
    return Fencer(id=FENCER_ID1, display_name=DISPLAY_NAME1)

@pytest.fixture
def fencer2():
    return Fencer(id=FENCER_ID2, display_name=DISPLAY_NAME2)

@pytest.fixture
def entry1(fencer1):
    return TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer1)

@pytest.fixture
def entry2(fencer2):
    return TournamentEntry(id=ENTRY_ID2, tournament_id=TOURNY_ID, fencer=fencer2)

@pytest.fixture
def standard_poule_match(entry1, entry2):
    return PouleMatch(
        id=MATCH_ID1,
        tournament_id=TOURNY_ID,
        entry1=entry1,
        entry2=entry2,
        poule_id=POULE_ID,
        match_index=0
    )


# --- Initialization and Validation Tests ---
def test_poule_match_creation_valid_with_defaults(entry1, entry2):
    match = PouleMatch(
        id=MATCH_ID1,
        tournament_id=TOURNY_ID,
        entry1=entry1,
        entry2=entry2,
        poule_id=POULE_ID,
        match_index=0
    )
    assert match.id == MATCH_ID1
    assert match.score_to_win == 5
    assert match.tournament_id == TOURNY_ID
    assert match.entry1 == entry1
    assert match.entry2 == entry2
    assert match.poule_id == POULE_ID
    assert match.match_index == 0
    assert match.match_type == 'poule'

def test_poule_match_creation_valid_no_defaults(entry1, entry2):
    match = PouleMatch(
        id=MATCH_ID1,
        score_to_win=TEST_SCORE_TO_WIN,
        tournament_id=TOURNY_ID,
        entry1=entry1,
        entry2=entry2,
        poule_id=POULE_ID,
        match_index=0
    )
    assert match.id == MATCH_ID1
    assert match.score_to_win == TEST_SCORE_TO_WIN
    assert match.tournament_id == TOURNY_ID
    assert match.entry1 == entry1
    assert match.entry2 == entry2
    assert match.poule_id == POULE_ID
    assert match.match_index == 0
    assert match.match_type == 'poule'

@pytest.mark.parametrize('invalid_poule_id_type', [None, 1.0, True, 'first', [], {}])
def test_poule_match_creation_invalid_poule_id_type(entry1, entry2, invalid_poule_id_type):
    with pytest.raises(TypeError):
        PouleMatch(
            id=MATCH_ID1,
            tournament_id=TOURNY_ID,
            entry1=entry1,
            entry2=entry2,
            poule_id=invalid_poule_id_type,
            match_index=0
        )

def test_poule_match_creation_invalid_poule_id_zero(entry1, entry2):
    with pytest.raises(ValueError):
        PouleMatch(
            id=MATCH_ID1,
            tournament_id=TOURNY_ID,
            entry1=entry1,
            entry2=entry2,
            poule_id=0,
            match_index=0
        )

@pytest.mark.parametrize('negative_poule_id', [-10, -5, -1])
def test_poule_match_creation_invalid_poule_id_negative(entry1, entry2, negative_poule_id):
    with pytest.raises(ValueError):
        PouleMatch(
            id=MATCH_ID1,
            tournament_id=TOURNY_ID,
            entry1=entry1,
            entry2=entry2,
            poule_id=negative_poule_id,
            match_index=0
        )

@pytest.mark.parametrize('invalid_match_index_type', [None, 'index1', 0.0, False, [], {}])
def test_poule_match_creation_invalid_match_index_type(entry1, entry2, invalid_match_index_type):
    with pytest.raises(TypeError):
        PouleMatch(
            id=MATCH_ID1,
            tournament_id=TOURNY_ID,
            entry1=entry1,
            entry2=entry2,
            poule_id=POULE_ID,
            match_index=invalid_match_index_type
        )

@pytest.mark.parametrize('negative_match_index', [-15, -10, -5, -1])
def test_poule_match_creation_invalid_match_index_out_of_bounds(entry1, entry2, negative_match_index):
    with pytest.raises(ValueError):
        PouleMatch(
            id=MATCH_ID1,
            tournament_id=TOURNY_ID,
            entry1=entry1,
            entry2=entry2,
            poule_id=POULE_ID,
            match_index=negative_match_index
        )

@pytest.mark.parametrize('invalid_score_to_win_type', [None, 'ten', 15.0, True, [], {}])
def test_poule_match_creation_invalid_score_to_win_type(entry1, entry2, invalid_score_to_win_type):
    with pytest.raises(TypeError):
        PouleMatch(
            id=MATCH_ID1,
            score_to_win=invalid_score_to_win_type,
            tournament_id=TOURNY_ID,
            entry1=entry1,
            entry2=entry2,
            poule_id=POULE_ID,
            match_index=0
        )

def test_poule_match_creation_invalid_score_to_win_zero(entry1, entry2):
    with pytest.raises(ValueError):
        PouleMatch(
            id=MATCH_ID1,
            score_to_win=0,
            tournament_id=TOURNY_ID,
            entry1=entry1,
            entry2=entry2,
            poule_id=POULE_ID,
            match_index=0
        )

@pytest.mark.parametrize('negative_score_to_win', [-15, -10, -5, -1])
def test_poule_match_creation_invalid_score_to_win_negative(entry1, entry2, negative_score_to_win):
    with pytest.raises(ValueError):
        PouleMatch(
            id=MATCH_ID1,
            score_to_win=negative_score_to_win,
            tournament_id=TOURNY_ID,
            entry1=entry1,
            entry2=entry2,
            poule_id=POULE_ID,
            match_index=0
        )

def test_poule_match_creation_invalid_requires_two_entries_none_present():
    # Test implicit case
    with pytest.raises(ValueError):
        PouleMatch(id=MATCH_ID1, 
                   tournament_id=TOURNY_ID, 
                   poule_id=POULE_ID,
                   match_index=0)
        
    # Test explicit case
    with pytest.raises(ValueError):
        PouleMatch(id=MATCH_ID2, 
                   tournament_id=TOURNY_ID, 
                   entry1=None, 
                   entry2=None, 
                   poule_id=POULE_ID,
                   match_index=0)
    
def test_poule_match_creation_invalid_requires_two_entries_only_one_present(entry1, entry2):
    # Test implicit case
    with pytest.raises(ValueError):
        PouleMatch(id=MATCH_ID2, 
                   tournament_id=TOURNY_ID, 
                   entry2=entry2, 
                   poule_id=POULE_ID, 
                   match_index=0)

    # Test explicit case
    with pytest.raises(ValueError):
        PouleMatch(id=MATCH_ID1, 
                   tournament_id=TOURNY_ID, 
                   entry1=entry1, 
                   entry2=None, 
                   poule_id=POULE_ID, 
                   match_index=0)

def test_poule_match_creation_invalid_same_entry_provided(entry1):
    with pytest.raises(ValueError):
        PouleMatch(id=MATCH_ID1,
                   tournament_id=TOURNY_ID,
                   entry1=entry1,
                   entry2=entry1,
                   poule_id=POULE_ID,
                   match_index=0)


# --- Predicate Method Tests ---
def test_poule_match_is_normal_result(standard_poule_match):
    standard_poule_match.start()
    standard_poule_match.touch1()
    standard_poule_match.end()
    assert standard_poule_match.is_complete()
    assert standard_poule_match.is_normal_result()

# --- State Transition Method Tests ---
def test_poule_match_restart_clears_result_status(standard_poule_match):
    standard_poule_match.record_score(score1=5, score2=2)
    assert standard_poule_match.is_complete()
    assert standard_poule_match.is_normal_result()
    assert standard_poule_match.score() == (5, 2)

    standard_poule_match.restart()

    assert not standard_poule_match.is_complete()
    assert not standard_poule_match.is_normal_result()
    assert not standard_poule_match.is_forfeit()
    assert standard_poule_match.score() == (0, 0)
    assert standard_poule_match.result_type is None


# --- Entry Mutation Method Tests ---
def test_poule_match_set_entry_rejects_none(standard_poule_match):
    with pytest.raises(ValueError):
        standard_poule_match.set_entry(None, 0)

    with pytest.raises(ValueError):
        standard_poule_match.set_entry(None, 1)


# --- Result Query Method Tests ---
def test_poule_match__assign_normal_result_status(standard_poule_match):
    standard_poule_match.record_score(score1=2, score2=5)
    assert standard_poule_match.is_complete()
    assert standard_poule_match.is_normal_result()

def test_poule_match__assign_forfeit_status(standard_poule_match):
    # Test forfeit by entry1
    standard_poule_match.forfeit1()
    assert standard_poule_match.is_forfeit()
    assert standard_poule_match.result_type is PouleMatchResultType.FORFEIT
    assert standard_poule_match.score() == (0, standard_poule_match.score_to_win)
    assert standard_poule_match.winner_entry() == standard_poule_match.entry2
    assert standard_poule_match.loser_entry() == standard_poule_match.entry1

    standard_poule_match.reset()

    # Test forfeit by entry2
    standard_poule_match.forfeit2()
    assert standard_poule_match.is_forfeit()
    assert standard_poule_match.result_type is PouleMatchResultType.FORFEIT
    assert standard_poule_match.score() == (standard_poule_match.score_to_win, 0)
    assert standard_poule_match.winner_entry() == standard_poule_match.entry1
    assert standard_poule_match.loser_entry() == standard_poule_match.entry2

def test_poule_match__clear_result_status(standard_poule_match):
    # Normal result case
    standard_poule_match.record_score(2,5)
    assert standard_poule_match.is_complete()
    assert standard_poule_match.is_normal_result()
    assert standard_poule_match.result_type is PouleMatchResultType.NORMAL

    standard_poule_match.reset()
    assert standard_poule_match.result_type is None

    # Forfeit result case
    standard_poule_match.forfeit1()
    assert standard_poule_match.is_complete()
    assert standard_poule_match.is_forfeit()
    assert standard_poule_match.result_type is PouleMatchResultType.FORFEIT

    standard_poule_match.reset()
    assert standard_poule_match.result_type is None

def test_poule_match_winner_entry_incomplete_match(standard_poule_match):
    assert not standard_poule_match.is_complete()
    assert standard_poule_match.result_type == None
    assert standard_poule_match.winner_entry() is None

def test_poule_match_winner_entry_normal_match_entry1_wins(standard_poule_match):
    assert not standard_poule_match.is_complete()
    assert standard_poule_match.result_type == None
    standard_poule_match.record_score(score1=5, score2=1)
    assert standard_poule_match.is_complete()
    assert standard_poule_match.is_normal_result()
    assert standard_poule_match.winner_entry() == standard_poule_match.entry1

def test_poule_match_winner_entry_normal_match_entry2_wins(standard_poule_match):
    assert not standard_poule_match.is_complete()
    assert standard_poule_match.result_type == None
    standard_poule_match.record_score(score1=2, score2=5)
    assert standard_poule_match.is_complete()
    assert standard_poule_match.is_normal_result()
    assert standard_poule_match.winner_entry() == standard_poule_match.entry2

def test_poule_match_winner_entry_normal_match_invalid_none_entry_present(standard_poule_match, entry1):
    standard_poule_match.record_score(score1=5, score2=2)
    standard_poule_match.entry1 = None
    with pytest.raises(RuntimeError):
        standard_poule_match.winner_entry()
    standard_poule_match.entry1 = entry1
    standard_poule_match.entry2 = None
    with pytest.raises(RuntimeError):
        standard_poule_match.winner_entry()
    standard_poule_match.entry1 = None
    with pytest.raises(RuntimeError):
        standard_poule_match.winner_entry()

def test_poule_match_winner_entry_forfeit_match_entry1_forfeits(standard_poule_match):
    assert not standard_poule_match.is_complete()
    assert standard_poule_match.result_type == None
    standard_poule_match.forfeit1()
    assert standard_poule_match.is_complete()
    assert standard_poule_match.is_forfeit()
    assert standard_poule_match.winner_entry() == standard_poule_match.entry2

def test_poule_match_winner_entry_forfeit_match_entry2_forfeits(standard_poule_match):
    assert not standard_poule_match.is_complete()
    assert standard_poule_match.result_type == None
    standard_poule_match.forfeit2()
    assert standard_poule_match.is_complete()
    assert standard_poule_match.is_forfeit()
    assert standard_poule_match.winner_entry() == standard_poule_match.entry1

def test_poule_match_loser_entry_incomplete_match(standard_poule_match):
    assert standard_poule_match.loser_entry() is None

def test_poule_match_loser_entry_normal_match_entry1_loses(standard_poule_match):
    assert not standard_poule_match.is_complete()
    assert standard_poule_match.result_type == None
    standard_poule_match.record_score(score1=3, score2=5)
    assert standard_poule_match.is_complete()
    assert standard_poule_match.result_type == PouleMatchResultType.NORMAL
    assert standard_poule_match.loser_entry() == standard_poule_match.entry1

def test_poule_match_loser_entry_normal_match_entry2_loses(standard_poule_match):
    assert not standard_poule_match.is_complete()
    assert standard_poule_match.result_type == None
    standard_poule_match.record_score(score1=5, score2=1)
    assert standard_poule_match.is_complete()
    assert standard_poule_match.result_type == PouleMatchResultType.NORMAL
    assert standard_poule_match.loser_entry() == standard_poule_match.entry2

def test_poule_match_loser_entry_normal_match_invalid_none_entry_present(standard_poule_match, entry1):
    standard_poule_match.record_score(score1=5, score2=2)
    standard_poule_match.entry1 = None
    with pytest.raises(RuntimeError):
        standard_poule_match.loser_entry()
    standard_poule_match.entry1 = entry1
    standard_poule_match.entry2 = None
    with pytest.raises(RuntimeError):
        standard_poule_match.loser_entry()
    standard_poule_match.entry1 = None
    with pytest.raises(RuntimeError):
        standard_poule_match.loser_entry()

def test_poule_match_loser_entry_forfeit_entry1_forfeits(standard_poule_match):
    assert not standard_poule_match.is_complete()
    assert standard_poule_match.result_type == None
    standard_poule_match.forfeit1()
    assert standard_poule_match.is_complete()
    assert standard_poule_match.is_forfeit()
    assert standard_poule_match.loser_entry() == standard_poule_match.entry1

def test_poule_match_loser_entry_forfeit_entry2_forfeits(standard_poule_match):
    assert not standard_poule_match.is_complete()
    assert standard_poule_match.result_type == None
    standard_poule_match.forfeit2()
    assert standard_poule_match.is_complete()
    assert standard_poule_match.is_forfeit()
    assert standard_poule_match.loser_entry() == standard_poule_match.entry2