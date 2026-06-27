"""Tests tournament-specific methods and attributes. The subclass test files will be for subclass-specific attributes and method."""


import pytest

from matches.tournament_match import TournamentMatch
from matches.match import MatchStatus
from matches.poule_match import PouleMatch
from matches.de_match import DEMatch
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
MATCH_ID1 = 1
MATCH_ID2 = 2
MATCH_ID3 = 3
MATCH_ID4 = 4
TEST_SCORE_TO_WIN = 8
TOURNY_ID = 1
POULE_ID = 1


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
    return TournamentEntry(id=ENTRY_ID1, tournament_id=TOURNY_ID, fencer=fencer1)

@pytest.fixture
def entry2(fencer2):
    return TournamentEntry(id=ENTRY_ID2, tournament_id=TOURNY_ID, fencer=fencer2)

@pytest.fixture
def entry3(fencer3):
    return TournamentEntry(id=ENTRY_ID3, tournament_id=TOURNY_ID, fencer=fencer3)

@pytest.fixture
def poule_match(entry1, entry2):
    return PouleMatch(
        id=MATCH_ID1,
        tournament_id=TOURNY_ID,
        entry1=entry1,
        entry2=entry2,
        poule_id=POULE_ID,
        match_index=0
    )

@pytest.fixture
def de_match(entry1, entry2):
    entry1.de_seed = 1
    entry2.de_seed = 2
    return DEMatch(
        id=MATCH_ID2,
        tournament_id=TOURNY_ID,
        entry1=entry1,
        entry2=entry2,
        round_index=0,
        match_index=0
    )

@pytest.fixture
def empty_de_match():
    return DEMatch(
        id=MATCH_ID3,
        tournament_id=TOURNY_ID,
        round_index=0,
        match_index=0
    )

@pytest.fixture
def de_match_with_one_entry(entry1):
    entry1.set_de_seed(1)
    de_match = DEMatch(
        id=MATCH_ID4,
        tournament_id=TOURNY_ID,
        round_index=0,
        match_index=0
    )
    de_match.set_entry(entry1, 0)
    return de_match

# --- Test for abstract base class ---
def test_tournament_match_cannot_instantiate(entry1, entry2):
    with pytest.raises(TypeError):
        TournamentMatch(id=MATCH_ID1, 
                        score_to_win=TEST_SCORE_TO_WIN, 
                        tournament_id=TOURNY_ID)

    with pytest.raises(TypeError):
        TournamentMatch(id=MATCH_ID1, 
                        score_to_win=TEST_SCORE_TO_WIN, 
                        tournament_id=TOURNY_ID,
                        entry1=entry1,
                        entry2=entry2)


# --- Initialization and Validation Tests ---
def test_tournament_match_creation_valid_poule_match(entry1, entry2):
    poule_match = PouleMatch(
        id=MATCH_ID1,
        tournament_id=TOURNY_ID,
        entry1=entry1,
        entry2=entry2,
        poule_id=POULE_ID,
        match_index=0
    )
    assert poule_match.id == MATCH_ID1
    assert poule_match.score_to_win == 5
    assert poule_match.fencer1 == entry1.fencer
    assert poule_match.fencer2 == entry2.fencer
    assert poule_match.score1 is None
    assert poule_match.score2 is None
    assert poule_match.status == MatchStatus.NOT_STARTED
    assert poule_match.tournament_id == TOURNY_ID
    assert poule_match.entry1 == entry1
    assert poule_match.entry2 == entry2
    assert poule_match.forfeited_index is None
    assert poule_match.poule_id == POULE_ID
    assert poule_match.match_index == 0
    assert poule_match.result_type is None
    assert poule_match.match_type == 'poule'

def test_tournament_match_creation_valid_de_match():
    de_match = DEMatch(
        id=MATCH_ID2,
        tournament_id=TOURNY_ID,
        round_index=0,
        match_index=0
    )
    assert de_match.id == MATCH_ID2
    assert de_match.score_to_win == 15
    assert de_match.fencer1 is None
    assert de_match.fencer2 is None
    assert de_match.score1 is None
    assert de_match.score2 is None
    assert de_match.status == MatchStatus.NOT_STARTED
    assert de_match.tournament_id == TOURNY_ID
    assert de_match.entry1 is None
    assert de_match.entry2 is None
    assert de_match.forfeited_index is None
    assert de_match.round_index == 0
    assert de_match.match_index == 0
    assert de_match.result_type is None
    assert de_match.match_type == 'de'

def test_tournament_match_creation_invalid_reject_providing_fencers(fencer1, fencer2, entry1, entry2):
    with pytest.raises(ValueError):
        PouleMatch(
            id=MATCH_ID1,
            fencer1=fencer1,
            tournament_id=TOURNY_ID,
            entry1=entry1,
            entry2=entry2,
            poule_id=POULE_ID,
            match_index=0
        )

    with pytest.raises(ValueError):
        PouleMatch(
            id=MATCH_ID1,
            fencer2=fencer2,
            tournament_id=TOURNY_ID,
            entry1=entry1,
            entry2=entry2,
            poule_id=POULE_ID,
            match_index=0
        )

    with pytest.raises(ValueError):
        PouleMatch(
            id=MATCH_ID1,
            fencer1=fencer1,
            fencer2=fencer2,
            tournament_id=TOURNY_ID,
            entry1=entry1,
            entry2=entry2,
            poule_id=POULE_ID,
            match_index=0
        )

    with pytest.raises(ValueError):
        DEMatch(
            id=MATCH_ID2,
            fencer1=fencer1,
            tournament_id=TOURNY_ID,
            round_index=0,
            match_index=0
        )

    with pytest.raises(ValueError):
        DEMatch(
            id=MATCH_ID2,
            fencer2=fencer2,
            tournament_id=TOURNY_ID,
            round_index=0,
            match_index=0
        )

    with pytest.raises(ValueError):
        DEMatch(
            id=MATCH_ID2,
            fencer1=fencer1,
            fencer2=fencer2,
            tournament_id=TOURNY_ID,
            round_index=0,
            match_index=0
        )

@pytest.mark.parametrize('invalid_tournament_id_type', [None, '1', 1.0, True, [], {}])
def test_tournament_match_creation_invalid_tournament_id_type(entry1, entry2, invalid_tournament_id_type):
    with pytest.raises(TypeError):
        PouleMatch(
            id=MATCH_ID1,
            tournament_id=invalid_tournament_id_type,
            entry1=entry1,
            entry2=entry2,
            poule_id=POULE_ID,
            match_index=0
        )
    with pytest.raises(TypeError):
        DEMatch(
            id=MATCH_ID2,
            tournament_id=invalid_tournament_id_type,
            round_index=0,
            match_index=0
        )

def test_tournament_match_creation_invalid_tournament_id_zero(entry1, entry2):
    with pytest.raises(ValueError):
        PouleMatch(
            id=MATCH_ID1,
            tournament_id=0,
            entry1=entry1,
            entry2=entry2,
            poule_id=POULE_ID,
            match_index=0
        )
    with pytest.raises(ValueError):
        DEMatch(
            id=MATCH_ID2,
            tournament_id=0,
            round_index=0,
            match_index=0
        )

@pytest.mark.parametrize('invalid_tournament_id_negative', [-100, -10, -1])
def test_tournament_match_creation_invalid_tournament_id_negative(entry1, entry2, invalid_tournament_id_negative):
    with pytest.raises(ValueError):
        PouleMatch(
            id=MATCH_ID1,
            tournament_id=invalid_tournament_id_negative,
            entry1=entry1,
            entry2=entry2,
            poule_id=POULE_ID,
            match_index=0
        )
    with pytest.raises(ValueError):
        DEMatch(
            id=MATCH_ID2,
            tournament_id=invalid_tournament_id_negative,
            round_index=0,
            match_index=0
        )

@pytest.mark.parametrize('invalid_entry_type', ['Ben', 0, 1, 10.0, -7, False, [], {}])
def test_tournament_match_creation_invalid_entry_type(entry1, entry2, invalid_entry_type):
    with pytest.raises(TypeError):
        PouleMatch(
            id=MATCH_ID1,
            tournament_id=TOURNY_ID,
            entry1=invalid_entry_type,
            entry2=entry2,
            poule_id=POULE_ID,
            match_index=0
        )

    with pytest.raises(TypeError):
        PouleMatch(
            id=MATCH_ID1,
            tournament_id=TOURNY_ID,
            entry1=entry1,
            entry2=invalid_entry_type,
            poule_id=POULE_ID,
            match_index=0
        )

    with pytest.raises(TypeError):
        PouleMatch(
            id=MATCH_ID1,
            tournament_id=TOURNY_ID,
            entry1=invalid_entry_type,
            entry2=invalid_entry_type,
            poule_id=POULE_ID,
            match_index=0
        )

    with pytest.raises(TypeError):
        DEMatch(
            id=MATCH_ID2,
            tournament_id=TOURNY_ID,
            entry1=invalid_entry_type,
            entry2=entry2,
            round_index=0,
            match_index=0
        )

    with pytest.raises(TypeError):
        DEMatch(
            id=MATCH_ID2,
            tournament_id=TOURNY_ID,
            entry1=entry1,
            entry2=invalid_entry_type,
            round_index=0,
            match_index=0
        )

    with pytest.raises(TypeError):
        DEMatch(
            id=MATCH_ID2,
            tournament_id=TOURNY_ID,
            entry1=invalid_entry_type,
            entry2=invalid_entry_type,
            round_index=0,
            match_index=0
        )

def test_tournament_match_creation_invalid_entry_equal_entries(entry1, entry2):
    with pytest.raises(ValueError):
        PouleMatch(
            id=MATCH_ID1,
            tournament_id=TOURNY_ID,
            entry1=entry1,
            entry2=entry1,
            poule_id=POULE_ID,
            match_index=0
        )
    
    # Assign DE seed to entry2 for the DE match
    entry2.de_seed = 1

    with pytest.raises(ValueError):
        DEMatch(
            id=MATCH_ID2,
            tournament_id=TOURNY_ID,
            entry1=entry2,
            entry2=entry2,
            round_index=0,
            match_index=0
        )

def test_tournament_match_creation_validate_entry_fencer_sync(entry1, entry2):
    poule_match = PouleMatch(
        id=MATCH_ID1,
        tournament_id=TOURNY_ID,
        entry1=entry1,
        entry2=entry2,
        poule_id=POULE_ID,
        match_index=0
    )
    assert poule_match.fencer1 == entry1.fencer
    assert poule_match.fencer2 == entry2.fencer

    # Assign a DE seed to the entries for the DE match
    entry1.de_seed = 1
    entry2.de_seed = 2

    de_match = DEMatch(
        id=MATCH_ID2,
        tournament_id=TOURNY_ID,
        entry1=entry1,
        entry2=entry2,
        round_index=0,
        match_index=0
    )
    assert de_match.fencer1 == entry1.fencer
    assert de_match.fencer2 == entry2.fencer


# --- Dunder Method Tests ---
def test_tournament_match_equality(poule_match, de_match, entry1, entry2):
    same_poule_match = PouleMatch(
        id=MATCH_ID1,
        tournament_id=TOURNY_ID,
        entry1=entry1,
        entry2=entry2,
        poule_id=POULE_ID,
        match_index=0
    )
    assert poule_match == same_poule_match

    same_de_match = DEMatch(
        id=MATCH_ID2,
        tournament_id=TOURNY_ID,
        entry1=entry1,
        entry2=entry2,
        round_index=0,
        match_index=0
    )
    assert de_match == same_de_match

def test_tournament_match_inequality_different_types(poule_match, de_match):
    # Set de_match to have same id as poule_match for testing purposes
    de_match.id = poule_match.id
    assert poule_match != de_match

def test_tournament_match_inequality_different_id(poule_match, de_match, entry1, entry2):
    different_poule_match = PouleMatch(
        id=MATCH_ID3,
        tournament_id=TOURNY_ID,
        entry1=entry1,
        entry2=entry2,
        poule_id=POULE_ID,
        match_index=0
    )
    assert poule_match != different_poule_match

    different_de_match = DEMatch(
        id=MATCH_ID4,
        tournament_id=TOURNY_ID,
        entry1=entry1,
        entry2=entry2,
        round_index=0,
        match_index=0
    )
    assert de_match != different_de_match

def test_tournament_match_inequality_different_tournament_id(poule_match, de_match, entry1, entry2):
    # Different tournament ID for testing purposes
    DIF_TOURNY_ID = 2
    
    # Update the tournament_id of the entries for the DE match to match the different tournament ID
    entry1.tournament_id = DIF_TOURNY_ID
    assert entry1.tournament_id == DIF_TOURNY_ID
    entry2.tournament_id = DIF_TOURNY_ID
    assert entry2.tournament_id == DIF_TOURNY_ID
    
    different_poule_match = PouleMatch(
        id=poule_match.id,
        tournament_id=DIF_TOURNY_ID,
        entry1=entry1,
        entry2=entry2,
        poule_id=POULE_ID,
        match_index=0
    )
    assert poule_match != different_poule_match

    # Assign a DE seed to the entries for the DE match
    entry1.de_seed = 1
    entry2.de_seed = 2

    different_de_match = DEMatch(
        id=de_match.id,
        tournament_id=DIF_TOURNY_ID,
        entry1=entry1,
        entry2=entry2,
        round_index=0,
        match_index=0
    )
    assert de_match != different_de_match


# --- Predicate Method Tests ---
def test_tournament_match_has_no_entries(de_match, empty_de_match):
    assert not de_match.has_no_entries()
    assert empty_de_match.has_no_entries()

def test_tournament_match_has_exactly_one_entry(de_match, empty_de_match, de_match_with_one_entry):
    assert not empty_de_match.has_exactly_one_entry()
    assert de_match_with_one_entry.has_exactly_one_entry()
    assert not de_match.has_exactly_one_entry()

def test_tournament_match_has_at_least_one_entry(de_match, empty_de_match, de_match_with_one_entry):
    assert not empty_de_match.has_at_least_one_entry()
    assert de_match_with_one_entry.has_at_least_one_entry()
    assert de_match.has_at_least_one_entry()

def test_tournament_match_has_both_entries(de_match, empty_de_match, de_match_with_one_entry):
    assert not empty_de_match.has_both_entries()
    assert not de_match_with_one_entry.has_both_entries()
    assert de_match.has_both_entries()

def test_tournament_match_is_forfeit(poule_match, de_match):
    assert not poule_match.is_forfeit()
    assert not de_match.is_forfeit()

    poule_match.forfeit1()
    de_match.forfeit2()

    assert poule_match.is_forfeit()
    assert de_match.is_forfeit()


# --- Entry Access Method Tests ---
def test_tournament_match_entry_at_index(poule_match, de_match):
    assert poule_match.entry_at_index(0) == poule_match.entry1
    assert poule_match.entry_at_index(1) == poule_match.entry2  

    assert de_match.entry_at_index(0) == de_match.entry1
    assert de_match.entry_at_index(1) == de_match.entry2

def test_tournament_match_entry_at_index_invalid_index(poule_match, de_match):
    with pytest.raises(ValueError):
        poule_match.entry_at_index(2)
    with pytest.raises(ValueError):
        poule_match.entry_at_index(-1)

    with pytest.raises(ValueError):
        de_match.entry_at_index(2)
    with pytest.raises(ValueError):
        de_match.entry_at_index(-1)

def test_tournament_match_opponent_entry_of_index(poule_match, de_match):
    assert poule_match.opponent_entry_of_index(0) == poule_match.entry2
    assert poule_match.opponent_entry_of_index(1) == poule_match.entry1

    assert de_match.opponent_entry_of_index(0) == de_match.entry2
    assert de_match.opponent_entry_of_index(1) == de_match.entry1

def test_tournament_match_opponent_entry_of_index_invalid_index(poule_match, de_match):
    with pytest.raises(ValueError):
        poule_match.opponent_entry_of_index(2)
    with pytest.raises(ValueError):
        poule_match.opponent_entry_of_index(-1)

    with pytest.raises(ValueError):
        de_match.opponent_entry_of_index(2)
    with pytest.raises(ValueError):
        de_match.opponent_entry_of_index(-1)

def test_tournament_match_entries(poule_match, de_match):
    assert poule_match.entries() == (poule_match.entry1, poule_match.entry2)
    assert de_match.entries() == (de_match.entry1, de_match.entry2)


# --- Result Query Method Tests ---
def test_tournament_match_winner_alias_function(poule_match, de_match):
    assert poule_match.winner() == poule_match.winner_entry()
    assert de_match.winner() == de_match.winner_entry()

def test_tournament_match_loser_alias_function(poule_match, de_match):
    assert poule_match.loser() == poule_match.loser_entry()
    assert de_match.loser() == de_match.loser_entry()


# --- Entry Mutation Method Tests ---
def test_tournament_match_set_entry(poule_match, empty_de_match, entry1, entry2, entry3):
    poule_match.set_entry(entry3, 0)
    assert poule_match.entry1 == entry3
    poule_match.set_entry(entry1, 1)
    assert poule_match.entry2 == entry1

    # Assign DE seeds to entries for the DE match
    entry1.de_seed = 1
    entry2.de_seed = 2

    empty_de_match.set_entry(entry1, 0)
    empty_de_match.set_entry(entry2, 1)
    assert empty_de_match.entry1 == entry1
    assert empty_de_match.entry2 == entry2

def test_tournament_match_set_entry__to_none(de_match):
    de_match.set_entry(None, 0)
    assert de_match.entry1 is None
    de_match.set_entry(None, 1)
    assert de_match.entry2 is None

def test_tournament_match_set_entry_updates_derived_fencer(entry1, entry2):
    entry3 = TournamentEntry(
        id=3,
        tournament_id=1,
        fencer=Fencer(id=3, display_name='Bob'),
    )

    match = PouleMatch(
        id=1,
        tournament_id=1,
        entry1=entry1,
        entry2=entry2,
        poule_id=1,
        match_index=0,
    )

    match.set_entry(entry3, 0)

    assert match.entry1 is entry3
    assert match.fencer1 is entry3.fencer

@pytest.mark.parametrize('invalid_entry_type', ['Ben', 0, 1, 10.0, -7, False, [], {}])
def test_tournament_match_set_entry_invalid_entry_type(poule_match, empty_de_match, invalid_entry_type):
    with pytest.raises(TypeError):
        poule_match.set_entry(invalid_entry_type, 0)
    with pytest.raises(TypeError):
        poule_match.set_entry(invalid_entry_type, 1)

    with pytest.raises(TypeError):
        empty_de_match.set_entry(invalid_entry_type, 0)
    with pytest.raises(TypeError):
        empty_de_match.set_entry(invalid_entry_type, 1)

@pytest.mark.parametrize('invalid_index_type', ['0', 1.0, True, [], {}])
def test_tournament_match_set_entry_invalid_index_type(poule_match, de_match, entry3, invalid_index_type):
    with pytest.raises(TypeError):
        poule_match.set_entry(entry3, invalid_index_type)
    with pytest.raises(TypeError):
        de_match.set_entry(entry3, invalid_index_type)

def test_tournament_match_set_entry_invalid_index(poule_match, empty_de_match, entry1, entry2, entry3):
    with pytest.raises(ValueError):
        poule_match.set_entry(entry3, 2)
    with pytest.raises(ValueError):
        poule_match.set_entry(entry1, -1)

    with pytest.raises(ValueError):
        empty_de_match.set_entry(entry1, 2)
    with pytest.raises(ValueError):
        empty_de_match.set_entry(entry2, -1)

def test_tournament_match_set_entry_invalid_entry_equal_entries(poule_match, de_match, entry1, entry2):
    with pytest.raises(ValueError):
        poule_match.set_entry(entry1, 1)

    with pytest.raises(ValueError):
        de_match.set_entry(entry2, 0)

def test_tournament_match_set_entry_rejects_changes_after_match_starts(poule_match, de_match, entry3):
    poule_match.start()
    with pytest.raises(ValueError):
        poule_match.set_entry(entry3, 0)

    de_match.start()
    with pytest.raises(ValueError):
        de_match.set_entry(entry3, 0)


# --- State Transition Method Tests ---
def test_tournament_match_start_requires_both_entries(empty_de_match, de_match_with_one_entry):
    with pytest.raises(ValueError):
        empty_de_match.start()
    with pytest.raises(ValueError):
        de_match_with_one_entry.start()

def test_tournament_match_restart(poule_match, de_match):
    poule_match.forfeit1()
    poule_match.restart()
    assert poule_match.score1 == 0
    assert poule_match.score2 == 0
    assert poule_match.forfeited_index is None

    de_match.start()
    de_match.touch1()
    de_match.touch1()
    de_match.touch2()
    de_match.restart()
    assert de_match.score1 == 0
    assert de_match.score2 == 0
    assert de_match.forfeited_index is None

def test_tournament_match_reset(poule_match, de_match):
    poule_match.start()
    poule_match.touch1()
    poule_match.touch2()
    poule_match.touch1()
    poule_match.end()
    poule_match.reset()
    assert poule_match.score1 is None
    assert poule_match.score2 is None
    assert poule_match.forfeited_index is None

    de_match.forfeit2()
    de_match.reset()
    assert de_match.score1 is None
    assert de_match.score2 is None
    assert de_match.forfeited_index is None


# --- Result Recording Method Tests ---
def test_tournament_match_record_score_invalid_is_forfeit(poule_match, de_match):
    poule_match.forfeit1()
    with pytest.raises(ValueError):
        poule_match.record_score(5, 3)

    de_match.forfeit2()
    with pytest.raises(ValueError):
        de_match.record_score(15, 10)

def test_tournament_match_record_score_invalid_doesnt_have_both_entries(empty_de_match, de_match_with_one_entry):  
    with pytest.raises(ValueError):
        empty_de_match.record_score(5, 3)
    with pytest.raises(ValueError):
        de_match_with_one_entry.record_score(15, 10)

def test_tournament_match_forfeit(poule_match, de_match):
    poule_match.forfeit(0)
    assert poule_match.forfeited_index == 0
    assert poule_match.is_complete()
    assert poule_match.is_forfeit()

    de_match.forfeit(1)
    assert de_match.forfeited_index == 1
    assert de_match.is_complete()
    assert de_match.is_forfeit()

def test_tournament_match_forfeit_cannot_forfeit_a_completed_match(poule_match, de_match):
    poule_match.start()
    poule_match.touch1()
    poule_match.touch1()
    poule_match.end()
    with pytest.raises(ValueError):
        poule_match.forfeit(1)

    de_match.record_score(15,10)
    with pytest.raises(ValueError):
        de_match.forfeit(0)

def test_tournament_match_forfeit_requires_both_entries(empty_de_match, de_match_with_one_entry):
    with pytest.raises(ValueError):
        empty_de_match.forfeit(0)
    with pytest.raises(ValueError):
        empty_de_match.forfeit(1)

    with pytest.raises(ValueError):
        de_match_with_one_entry.forfeit(0)
    with pytest.raises(ValueError):
        de_match_with_one_entry.forfeit(1)

@pytest.mark.parametrize('invalid_forfeiting_index_type', ['0', 1.0, True, [], {}])
def test_tournament_match_forfeit_invalid_forfeiting_index_type(invalid_forfeiting_index_type, poule_match, de_match):
    with pytest.raises(TypeError):
        poule_match.forfeit(invalid_forfeiting_index_type)
    with pytest.raises(TypeError):
        de_match.forfeit(invalid_forfeiting_index_type)

@pytest.mark.parametrize('invalid_forfeiting_index_value', [-1, 2])
def test_tournament_match_forfeit_invalid_forfeiting_index_value(invalid_forfeiting_index_value, poule_match, de_match):
    with pytest.raises(ValueError):
        poule_match.forfeit(invalid_forfeiting_index_value)
    with pytest.raises(ValueError):
        de_match.forfeit(invalid_forfeiting_index_value)

def test_tournament_match_forfeit1(poule_match, de_match):
    poule_match.forfeit1()
    assert poule_match.forfeited_index == 0
    assert poule_match.is_complete()
    assert poule_match.is_forfeit()

    de_match.forfeit1()
    assert de_match.forfeited_index == 0
    assert de_match.is_complete()
    assert de_match.is_forfeit()
    
def test_tournament_match_forfeit2(poule_match, de_match):
    poule_match.forfeit2()
    assert poule_match.forfeited_index == 1
    assert poule_match.is_complete()
    assert poule_match.is_forfeit()

    de_match.forfeit2()
    assert de_match.forfeited_index == 1
    assert de_match.is_complete()
    assert de_match.is_forfeit()


