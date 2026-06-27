"""Tests DE-specific attributes and methods."""


import pytest

from matches.de_match import DEMatch, DEMatchResultType
from entities.tournament_entry import TournamentEntry
from entities.fencer import Fencer


# --- Constants ---
FENCER_ID1 = 1
FENCER_ID2 = 2
FENCER_ID3 = 3
DISPLAY_NAME1 = 'Ben'
DISPLAY_NAME2 = 'Bill'
DISPLAY_NAME3 = 'Bob'
ENTRY_ID1 = 1
ENTRY_ID2 = 2
ENTRY_ID3 = 3
TEST_SCORE_TO_WIN = 8
TOURNY_ID = 1
MATCH_ID1 = 1
MATCH_ID2 = 2
MATCH_ID3 = 3


# --- Fixtures ---
@pytest.fixture
def fencer1():
    return Fencer(id=FENCER_ID1, display_name=DISPLAY_NAME1)

@pytest.fixture
def fencer2():
    return Fencer(id=FENCER_ID2, display_name=DISPLAY_NAME2)

@pytest.fixture
def fencer3():
    return Fencer(id=FENCER_ID3, display_name=DISPLAY_NAME3)

@pytest.fixture
def entry1(fencer1):
    return TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer1, de_seed=1)

@pytest.fixture
def entry2(fencer2):
    return TournamentEntry(id=ENTRY_ID2, tournament_id=TOURNY_ID, fencer=fencer2, de_seed=2)

@pytest.fixture
def entry3(fencer3):
    return TournamentEntry(id=ENTRY_ID3, tournament_id=TOURNY_ID, fencer=fencer3, de_seed=3)

@pytest.fixture
def standard_de_match(entry1, entry2):
    return DEMatch(id=MATCH_ID1,
                   tournament_id=TOURNY_ID,
                   entry1=entry1,
                   entry2=entry2,
                   round_index=0,
                   match_index=0)

@pytest.fixture
def bye_de_match(entry1):
    return DEMatch(id=MATCH_ID2,
                   tournament_id=TOURNY_ID,
                   entry1=entry1,
                   round_index=0,
                   match_index=0)

@pytest.fixture
def empty_de_match():
    return DEMatch(id=MATCH_ID3,
                   tournament_id=TOURNY_ID,
                   round_index=0,
                   match_index=0)


# --- Initialization and Validation Tests ---
def test_de_match_creation_valid_with_defaults():
    match = DEMatch(
        id=MATCH_ID1,
        tournament_id=TOURNY_ID,
        round_index=0,
        match_index=0
    )
    assert match.id == MATCH_ID1
    assert match.fencer1 is None
    assert match.fencer2 is None
    assert match.score1 is None
    assert match.score2 is None
    assert match.score_to_win == 15
    assert match.tournament_id == TOURNY_ID
    assert match.entry1 is None
    assert match.entry2 is None
    assert match.forfeited_index is None
    assert match.round_index == 0
    assert match.match_index == 0
    assert not match.is_complete()
    assert match.result_type is None
    assert match.match_type == 'de'
    assert match.next_match_index == 0

def test_de_match_creation_valid_no_defaults(entry1, entry2):
    match = DEMatch(
        id=MATCH_ID1,
        score_to_win=TEST_SCORE_TO_WIN,
        tournament_id=TOURNY_ID,
        entry1=entry1,
        entry2=entry2,
        round_index=0,
        match_index=0
    )
    assert match.id == MATCH_ID1
    assert match.fencer1 == entry1.fencer
    assert match.fencer2 == entry2.fencer
    assert match.score1 is None
    assert match.score2 is None
    assert match.score_to_win == TEST_SCORE_TO_WIN
    assert match.tournament_id == TOURNY_ID
    assert match.entry1 == entry1
    assert match.entry2 == entry2
    assert match.forfeited_index is None
    assert match.round_index == 0
    assert match.match_index == 0
    assert not match.is_complete()
    assert match.result_type is None
    assert match.match_type == 'de'
    assert match.next_match_index == 0

def test_de_match_creation_mark_bye_upon_construction(entry1, entry2):
    # Entry 1 provided
    match1 = DEMatch(
        id=MATCH_ID1,
        tournament_id=TOURNY_ID,
        entry1=entry1,
        round_index=0,
        match_index=0
    )
    assert match1.is_complete()
    assert match1.is_bye()
    assert match1.result_type == DEMatchResultType.BYE
    assert match1.score() == (None, None)
    assert match1.winner_entry() == entry1
    assert match1.loser_entry() is None
    assert match1.forfeited_index is None

    # Entry 2 provided
    match2 = DEMatch(
        id=MATCH_ID2,
        tournament_id=TOURNY_ID,
        entry2=entry2,
        round_index=0,
        match_index=0
    )
    assert match2.is_complete()
    assert match2.is_bye()
    assert match2.result_type == DEMatchResultType.BYE
    assert match2.score() == (None, None)
    assert match2.winner_entry() == entry2
    assert match2.loser_entry() is None
    assert match2.forfeited_index is None

def test_de_match_creation_invalid_de_seed_not_provided(entry1, entry2):
    # Entry 1 provided
    entry1.set_de_seed(None)
    with pytest.raises(TypeError):
        DEMatch(
            id=MATCH_ID1,
            tournament_id=TOURNY_ID,
            entry1=entry1,
            entry2=entry2,
            round_index=0,
            match_index=0
        )

    # Entry 2 provided
    entry2.set_de_seed(None)
    with pytest.raises(TypeError):
        DEMatch(
            id=MATCH_ID2,
            tournament_id=TOURNY_ID,
            entry2=entry2,
            round_index=0,
            match_index=0
        )

@pytest.mark.parametrize('invalid_de_seed_type', ['1', 1.0, True, [], {}])
def test_de_match_creation_rejects_invalid_entry1_de_seed_type(entry1, invalid_de_seed_type):
    entry1.de_seed = invalid_de_seed_type
    with pytest.raises(TypeError):
        DEMatch(
            id=MATCH_ID1,
            tournament_id=TOURNY_ID,
            entry1=entry1,
            round_index=0,
            match_index=0,
        )

def test_de_match_creation_rejects_invalid_entry1_de_seed_zero(entry1):
    entry1.de_seed = 0
    with pytest.raises(ValueError):
        DEMatch(
            id=MATCH_ID1,
            tournament_id=TOURNY_ID,
            entry1=entry1,
            round_index=0,
            match_index=0,
        )

@pytest.mark.parametrize('invalid_de_seed_negative', [-10, -5, -1])
def test_de_match_creation_rejects_invalid_entry1_de_seed_value(entry1, invalid_de_seed_negative):
    entry1.de_seed = invalid_de_seed_negative
    with pytest.raises(ValueError):
        DEMatch(
            id=MATCH_ID1,
            tournament_id=TOURNY_ID,
            entry1=entry1,
            round_index=0,
            match_index=0,
        )

@pytest.mark.parametrize('invalid_round_index_type', [None, 0.0, '0', False, [], {}])
def test_de_match_creation_invalid_round_index_type(entry1, entry2, invalid_round_index_type):
    # Entries provided
    with pytest.raises(TypeError):
        DEMatch(id=MATCH_ID1, 
                tournament_id=TOURNY_ID, 
                entry1=entry1, 
                entry2=entry2, 
                round_index=invalid_round_index_type, 
                match_index=0)
    
    # Entries not provided
    with pytest.raises(TypeError):
        DEMatch(id=MATCH_ID2,
                tournament_id=TOURNY_ID,
                round_index=invalid_round_index_type,
                match_index=0)

@pytest.mark.parametrize('round_index_negative', [-15, -10, -5, -1])
def test_de_match_creation_invalid_round_index_negative(entry1, entry2, round_index_negative):
    # Entries provided
    with pytest.raises(ValueError):
        DEMatch(id=MATCH_ID1,
                tournament_id=TOURNY_ID,
                entry1=entry1,
                entry2=entry2,
                round_index=round_index_negative,
                match_index=0)
        
    # Entries not provided
    with pytest.raises(ValueError):
        DEMatch(id=MATCH_ID2,
                tournament_id=TOURNY_ID,
                round_index=round_index_negative,
                match_index=0)

@pytest.mark.parametrize('invalid_match_index_type', [None, '0', 0.0, False, [], {}])
def test_de_match_creation_invalid_match_index_type(entry1, entry2, invalid_match_index_type):
    # Entries provided
    with pytest.raises(TypeError):
        DEMatch(id=MATCH_ID1,
                tournament_id=TOURNY_ID,
                entry1=entry1,
                entry2=entry2,
                round_index=0,
                match_index=invalid_match_index_type)
        
    # Entries not provided
    with pytest.raises(TypeError):
        DEMatch(id=MATCH_ID2,
                tournament_id=TOURNY_ID,
                round_index=0,
                match_index=invalid_match_index_type)

@pytest.mark.parametrize('invalid_match_index_negative', [-10, -5, -1])
def test_de_match_creation_invalid_match_index_negative(entry1, entry2, invalid_match_index_negative):
    # Entries provided
    with pytest.raises(ValueError):
        DEMatch(id=MATCH_ID1,
                tournament_id=TOURNY_ID,
                entry1=entry1,
                entry2=entry2,
                round_index=0,
                match_index=invalid_match_index_negative)

    # Entries not provided    
    with pytest.raises(ValueError):
        DEMatch(id=MATCH_ID2,
                tournament_id=TOURNY_ID,
                round_index=0,
                match_index=invalid_match_index_negative)


# --- Properties Tests ---
def test_de_match_next_match_index(standard_de_match):
    standard_de_match.match_index = 0
    assert standard_de_match.next_match_index == 0
    standard_de_match.match_index = 1
    assert standard_de_match.next_match_index == 0
    standard_de_match.match_index = 2
    assert standard_de_match.next_match_index == 1
    standard_de_match.match_index = 3
    assert standard_de_match.next_match_index == 1
    standard_de_match.match_index = 4
    assert standard_de_match.next_match_index == 2
    standard_de_match.match_index = 5
    assert standard_de_match.next_match_index == 2
    standard_de_match.match_index = 6
    assert standard_de_match.next_match_index == 3
    standard_de_match.match_index = 7
    assert standard_de_match.next_match_index == 3

# --- Predicate Methods ---
def test_de_match_is_normal_result(standard_de_match):
    assert not standard_de_match.is_normal_result()
    standard_de_match.start()
    standard_de_match.touch1()
    standard_de_match.end()
    assert standard_de_match.is_normal_result()
    assert standard_de_match.result_type == DEMatchResultType.NORMAL

def test_de_match_is_bye(empty_de_match, bye_de_match, entry3):
    assert bye_de_match.is_bye()
    assert not empty_de_match.is_bye()
    empty_de_match.add_entry(entry=entry3, entry_index=0)
    empty_de_match.mark_bye()
    assert empty_de_match.is_bye()

def test_de_match_is_double_forfeit(standard_de_match):
    assert not standard_de_match.is_double_forfeit()
    standard_de_match.mark_double_forfeit()
    assert standard_de_match.is_double_forfeit()


# --- Status Marking Method Tests ---
def test_de_match_mark_bye(empty_de_match, entry1):
    assert not empty_de_match.is_complete()
    assert not empty_de_match.is_bye()
    empty_de_match.add_entry(entry=entry1, entry_index=0)
    empty_de_match.mark_bye()
    assert empty_de_match.is_complete()
    assert empty_de_match.is_bye()
    assert empty_de_match.score() == (None, None)

def test_de_match_mark_bye_invalid_two_entries(standard_de_match):
    with pytest.raises(ValueError):
        standard_de_match.mark_bye()

def test_de_match_mark_bye_invalid_no_entries(empty_de_match):
    with pytest.raises(ValueError):
        empty_de_match.mark_bye()

def test_de_match_mark_bye_invalid_already_marked_complete(empty_de_match, entry1, entry2):
    empty_de_match.add_entry(entry1, 0)
    empty_de_match.add_entry(entry2, 1)
    empty_de_match.record_score(score1=1, score2=0)
    empty_de_match.entry2 = None
    with pytest.raises(ValueError):
        empty_de_match.mark_bye()

def test_de_match_mark_double_forfeit(standard_de_match):
    assert not standard_de_match.is_complete()
    assert not standard_de_match.is_double_forfeit()
    standard_de_match.mark_double_forfeit()
    assert standard_de_match.is_complete()
    assert standard_de_match.is_double_forfeit()
    assert standard_de_match.score() == (None, None)

def test_de_match_mark_double_forfeit_invalid_already_marked_complete(standard_de_match):
    standard_de_match.record_score(score1=1, score2=0)
    with pytest.raises(ValueError):
        standard_de_match.mark_double_forfeit()

def test_de_match_mark_double_forfeit_invalid_has_only_one_entry(empty_de_match, entry1):
    empty_de_match.add_entry(entry=entry1, entry_index=0)
    with pytest.raises(ValueError):
        empty_de_match.mark_double_forfeit()

def test_de_match_mark_double_forfeit_invalid_has_no_entries(empty_de_match):
    with pytest.raises(ValueError):
        empty_de_match.mark_double_forfeit()

# --- State Change Method Tests ---
def test_de_match_reset_clears_double_forfeit_result(standard_de_match):
    standard_de_match.mark_double_forfeit()

    standard_de_match.reset()

    assert not standard_de_match.is_complete()
    assert standard_de_match.result_type is None
    assert standard_de_match.score() == (None, None)

def test_de_match_reset_clears_bye_result(bye_de_match):
    bye_de_match.reset()

    assert not bye_de_match.is_complete()
    assert bye_de_match.result_type is None
    assert bye_de_match.score() == (None, None)

def test_de_match_reset_clears_normal_result(standard_de_match):
    standard_de_match.record_score(score1=15, score2=10)

    standard_de_match.reset()

    assert not standard_de_match.is_complete()
    assert standard_de_match.result_type is None
    assert standard_de_match.score() == (None, None)


# --- Entry Mutation Method Tests ---
def test_de_match_add_entry_valid(empty_de_match, entry1, entry2):
    assert empty_de_match.entry1 is None
    assert empty_de_match.entry2 is None
    assert empty_de_match.fencer1 is None
    assert empty_de_match.fencer2 is None

    empty_de_match.add_entry(entry1, 0)
    empty_de_match.add_entry(entry2, 1)
    
    assert empty_de_match.entry1 == entry1
    assert empty_de_match.entry2 == entry2
    assert empty_de_match.fencer1 == entry1.fencer
    assert empty_de_match.fencer2 == entry2.fencer

@pytest.mark.parametrize('invalid_entry_type', [None, 'entry1', 0, 0.0, False, [], {}])
def test_de_match_add_entry_invalid_entry_type(empty_de_match, invalid_entry_type):
    with pytest.raises(TypeError):
        empty_de_match.add_entry(invalid_entry_type, 0)

def test_de_match_add_entry_invalid_entry_no_de_seed(entry1, empty_de_match):
    entry1.set_de_seed(None)
    with pytest.raises(TypeError):
        empty_de_match.add_entry(entry1, 1)

@pytest.mark.parametrize('invalid_de_seed_type', ['1', 1.0, True, [], {}])
def test_de_match_add_entry_invalid_entry_invalid_de_seed_type(entry1, empty_de_match, invalid_de_seed_type):
    entry1.de_seed = invalid_de_seed_type
    with pytest.raises(TypeError):
        empty_de_match.add_entry(entry1, 1)

@pytest.mark.parametrize('de_seed_negative', [-5, -1, 0])
def test_de_match_add_entry_invalid_entry_invalid_de_seed_negative(entry1, empty_de_match, de_seed_negative):
    entry1.de_seed = de_seed_negative
    with pytest.raises(ValueError):
        empty_de_match.add_entry(entry1, 1)

@pytest.mark.parametrize('invalid_entry_index_type', [None, 'top', 0.0, False, [], {}])
def test_de_match_add_entry_invalid_entry_index_type(entry1, empty_de_match, invalid_entry_index_type):
    with pytest.raises(TypeError):
        empty_de_match.add_entry(entry1, invalid_entry_index_type)

@pytest.mark.parametrize('invalid_entry_index_value', [-10, -2, 2, 10])
def test_de_match_add_entry_invalid_entry_index_value(entry1, empty_de_match, invalid_entry_index_value):
    with pytest.raises(ValueError):
        empty_de_match.add_entry(entry1, invalid_entry_index_value)

def test_de_match_add_one_entry_does_not_automatically_mark_bye(empty_de_match, entry1):
    empty_de_match.add_entry1(entry1)

    assert empty_de_match.entry1 == entry1
    assert empty_de_match.entry2 is None
    assert not empty_de_match.is_complete()
    assert not empty_de_match.is_bye()

def test_de_match_add_entry1(entry1, empty_de_match):
    assert empty_de_match.entry1 is None
    assert empty_de_match.entry2 is None
    assert empty_de_match.fencer1 is None
    assert empty_de_match.fencer2 is None

    empty_de_match.add_entry1(entry1)

    assert empty_de_match.entry1 == entry1
    assert empty_de_match.entry2 is None
    assert empty_de_match.fencer1 == entry1.fencer
    assert empty_de_match.fencer2 is None

def test_de_match_add_entry2(entry2, empty_de_match):
    assert empty_de_match.entry1 is None
    assert empty_de_match.entry2 is None
    assert empty_de_match.fencer1 is None
    assert empty_de_match.fencer2 is None

    empty_de_match.add_entry2(entry2)
    
    assert empty_de_match.entry1 is None
    assert empty_de_match.entry2 == entry2
    assert empty_de_match.fencer1 is None
    assert empty_de_match.fencer2 == entry2.fencer

def test_de_match_remove_entry(standard_de_match):
    standard_de_match.remove_entry(0)
    assert standard_de_match.fencer1 is None
    assert standard_de_match.fencer2 is not None
    assert standard_de_match.entry1 is None
    assert standard_de_match.entry2 is not None

def test_de_match_remove_entry_remove_entry2(standard_de_match):
    standard_de_match.remove_entry(1)
    assert standard_de_match.fencer1 is not None
    assert standard_de_match.fencer2 is None
    assert standard_de_match.entry1 is not None
    assert standard_de_match.entry2 is None

def test_de_match_remove_entry1(standard_de_match):
    standard_de_match.remove_entry1()
    assert standard_de_match.fencer1 is None
    assert standard_de_match.fencer2 is not None
    assert standard_de_match.entry1 is None
    assert standard_de_match.entry2 is not None

def test_de_match_remove_entry2(standard_de_match):
    standard_de_match.remove_entry2()
    assert standard_de_match.fencer1 is not None
    assert standard_de_match.fencer2 is None
    assert standard_de_match.entry1 is not None
    assert standard_de_match.entry2 is None

# --- Score Record Method Tests ---
def test_de_match_record_score_invalid_double_forfeit_occurred(standard_de_match):
    standard_de_match.mark_double_forfeit()
    with pytest.raises(ValueError):
        standard_de_match.record_score(1, 0)

def test_de_match_record_score_invalid_bye_occurred(bye_de_match):
    with pytest.raises(ValueError):
        bye_de_match.record_score(1, 0)


# --- Result Query Method Tests ---
def test_de_match_winner_entry_incomplete_match(standard_de_match):
    assert not standard_de_match.is_complete()
    assert standard_de_match.score1 is None
    assert standard_de_match.score2 is None
    assert standard_de_match.winner_entry() is None

def test_de_match_winner_entry_normal_match_entry1_wins(standard_de_match):
    assert not standard_de_match.is_complete()
    assert standard_de_match.score1 is None
    assert standard_de_match.score2 is None
    standard_de_match.record_score(score1=15, score2=12)
    assert standard_de_match.score1 == 15
    assert standard_de_match.score2 == 12
    assert standard_de_match.is_complete()
    assert standard_de_match.winner_entry() == standard_de_match.entry1

def test_de_match_winner_entry_normal_match_entry2_wins(standard_de_match):
    assert not standard_de_match.is_complete()
    assert standard_de_match.score1 is None
    assert standard_de_match.score2 is None
    standard_de_match.record_score(score1=11, score2=12)
    assert standard_de_match.score1 == 11
    assert standard_de_match.score2 == 12
    assert standard_de_match.is_complete()
    assert standard_de_match.winner_entry() == standard_de_match.entry2

def test_de_match_winner_entry_normal_match_invalid_none_entry_present(standard_de_match):
    assert not standard_de_match.is_complete()
    assert standard_de_match.score1 is None
    assert standard_de_match.score2 is None
    standard_de_match.record_score(score1=15, score2=10)
    standard_de_match.entry1 = None
    with pytest.raises(RuntimeError):
        standard_de_match.winner_entry()

def test_de_match_winner_entry_bye_match_entry1_got_a_bye(bye_de_match, entry1):
    assert bye_de_match.is_complete()
    assert bye_de_match.is_bye()
    assert bye_de_match.winner_entry() == entry1

def test_de_match_winner_entry_bye_match_entry2_got_a_bye(entry2):
    bye_match = DEMatch(
        id=MATCH_ID1,
        tournament_id=TOURNY_ID,
        entry2=entry2,
        round_index=0,
        match_index=0
    )
    assert bye_match.is_complete()
    assert bye_match.is_bye()
    assert bye_match.winner_entry() == entry2

def test_de_match_winner_entry_bye_match_invalid_two_nones(bye_de_match):
    assert bye_de_match.is_complete()
    assert bye_de_match.is_bye()
    bye_de_match.entry1 = None
    with pytest.raises(RuntimeError):
        bye_de_match.winner_entry()

def test_de_match_winner_entry_bye_match_invalid_no_nones(standard_de_match):
    standard_de_match.result_type = DEMatchResultType.BYE
    standard_de_match._mark_complete()
    with pytest.raises(RuntimeError):
        standard_de_match.winner_entry()

def test_de_match_winner_entry_forfeit_match_entry1_forfeits(standard_de_match):
    standard_de_match.forfeit1()
    assert standard_de_match.is_complete()
    assert standard_de_match.is_forfeit()
    assert standard_de_match.result_type == DEMatchResultType.FORFEIT
    assert standard_de_match.winner_entry() == standard_de_match.entry2

def test_de_match_winner_entry_forfeit_match_entry2_forfeits(standard_de_match):
    standard_de_match.forfeit2()
    assert standard_de_match.is_complete()
    assert standard_de_match.is_forfeit()
    assert standard_de_match.result_type == DEMatchResultType.FORFEIT
    assert standard_de_match.winner_entry() == standard_de_match.entry1

def test_de_match_winner_entry_double_forfeit(standard_de_match):
    standard_de_match.mark_double_forfeit()
    assert standard_de_match.is_double_forfeit()
    assert standard_de_match.is_complete()
    assert standard_de_match.winner_entry() is None

def test_de_match_loser_entry_incomplete_match(standard_de_match):
    assert not standard_de_match.is_complete()
    assert standard_de_match.loser_entry() is None

def test_de_match_loser_entry_normal_match_entry1_loses(standard_de_match):
    assert not standard_de_match.is_complete()
    standard_de_match.record_score(score1=11, score2=12)
    assert standard_de_match.is_complete()
    assert standard_de_match.loser_entry() == standard_de_match.entry1    

def test_de_match_loser_entry_normal_match_entry2_loses(standard_de_match):
    assert not standard_de_match.is_complete()
    standard_de_match.record_score(score1=15, score2=12)
    assert standard_de_match.loser_entry() == standard_de_match.entry2

def test_de_match_loser_entry_normal_match_invalid_none_entry_present(standard_de_match):
    standard_de_match.record_score(score1=15, score2=10)
    standard_de_match.entry1 = None
    with pytest.raises(RuntimeError):
        standard_de_match.loser_entry()

def test_de_match_loser_entry_bye_match(bye_de_match):
    assert bye_de_match.is_complete()
    assert bye_de_match.is_bye()
    assert bye_de_match.loser_entry() is None

def test_de_match_loser_entry_bye_match_invalid_two_nones(entry2):
    bye_match = DEMatch(
        id=MATCH_ID1,
        tournament_id=TOURNY_ID,
        entry2=entry2,
        round_index=0,
        match_index=0
    )
    bye_match.entry2 = None
    assert bye_match.is_complete()
    assert bye_match.is_bye()
    with pytest.raises(RuntimeError):
        bye_match.loser_entry()

def test_de_match_loser_entry_bye_match_invalid_no_nones(standard_de_match):
    standard_de_match._mark_complete()
    standard_de_match.result_type = DEMatchResultType.BYE
    assert standard_de_match.is_complete()
    assert standard_de_match.is_bye()
    with pytest.raises(RuntimeError):
        standard_de_match.loser_entry()

def test_de_match_loser_entry_forfeit_entry1_forfeits(standard_de_match):
    standard_de_match.forfeit1()
    assert standard_de_match.is_complete()
    assert standard_de_match.is_forfeit()
    assert standard_de_match.loser_entry() == standard_de_match.entry1

def test_de_match_loser_entry_forfeit_entry2_forfeits(standard_de_match):
    standard_de_match.forfeit2()
    assert standard_de_match.is_complete()
    assert standard_de_match.is_forfeit()
    assert standard_de_match.loser_entry() == standard_de_match.entry2

def test_de_match_loser_entry_double_forfeit(standard_de_match):
    standard_de_match.mark_double_forfeit()
    assert standard_de_match.is_complete()
    assert standard_de_match.is_double_forfeit()
    assert standard_de_match.loser_entry() == (standard_de_match.entry1, standard_de_match.entry2)