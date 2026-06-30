"""Tests for poule_results.py module."""

import pytest

from entities.fencer import Fencer
from entities.tournament_entry import TournamentEntry
from matches.poule_match import PouleMatch
from poules.poule_results import EntryPouleResult, SinglePouleResults, TournamentPouleResults



# --- Constants ---
FENCER_ID1 = 1
FENCER_ID2 = 2
FENCER_ID3 = 3
FENCER_ID4 = 4
FENCER_ID5 = 5
FENCER_ID6 = 6
FENCER_ID7 = 7

DISPLAY_NAME1 = 'John'
DISPLAY_NAME2 = 'Steve'
DISPLAY_NAME3 = 'Hannah'
DISPLAY_NAME4 = 'Emily'
DISPLAY_NAME5 = 'Michael'
DISPLAY_NAME6 = 'Sarah'
DISPLAY_NAME7 = 'Dave'

ENTRY_ID1 = 1
ENTRY_ID2 = 2
ENTRY_ID3 = 3
ENTRY_ID4 = 4
ENTRY_ID5 = 5
ENTRY_ID6 = 6
ENTRY_ID7 = 7

MATCH_ID1 = 1
MATCH_ID2 = 2

POULE_ID1 = 1
POULE_ID2 = 2

TOURNY_ID1 = 1
TOURNY_ID2 = 2


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
def fencer4():
    return Fencer(id=FENCER_ID4, display_name=DISPLAY_NAME4)

@pytest.fixture
def fencer5():
    return Fencer(id=FENCER_ID5, display_name=DISPLAY_NAME5)

@pytest.fixture
def fencer6():
    return Fencer(id=FENCER_ID6, display_name=DISPLAY_NAME6)

@pytest.fixture
def fencer7():
    return Fencer(id=FENCER_ID7, display_name=DISPLAY_NAME7)

@pytest.fixture
def entry1(fencer1):
    return TournamentEntry(id=1, tournament_id=1, fencer=fencer1)

@pytest.fixture
def entry2(fencer2):
    return TournamentEntry(id=2, tournament_id=1, fencer=fencer2)

@pytest.fixture
def entry3(fencer3):
    return TournamentEntry(id=3, tournament_id=1, fencer=fencer3)

@pytest.fixture
def entry4(fencer4):
    return TournamentEntry(id=4, tournament_id=1, fencer=fencer4)

@pytest.fixture
def entry5(fencer5):
    return TournamentEntry(id=5, tournament_id=1, fencer=fencer5)

@pytest.fixture
def entry6(fencer6):
    return TournamentEntry(id=6, tournament_id=1, fencer=fencer6)

@pytest.fixture
def entry7(fencer7):
    return TournamentEntry(id=7, tournament_id=1, fencer=fencer7)

@pytest.fixture
def entries(entry1, entry2, entry3, entry4, entry5, entry6, entry7):
    return (entry1, entry2, entry3, entry4, entry5, entry6, entry7)

@pytest.fixture
def epr1(entry1):
    return EntryPouleResult(entry=entry1, poule_id=POULE_ID1)

@pytest.fixture
def epr2(entry2):
    return EntryPouleResult(entry=entry2, poule_id=POULE_ID1)

@pytest.fixture
def epr3(entry3):
    return EntryPouleResult(entry=entry3, poule_id=POULE_ID1)

@pytest.fixture
def epr4(entry4):
    return EntryPouleResult(entry=entry4, poule_id=POULE_ID1)

@pytest.fixture
def epr5(entry5):
    return EntryPouleResult(entry=entry5, poule_id=POULE_ID1)

@pytest.fixture
def epr6(entry6):
    return EntryPouleResult(entry=entry6, poule_id=POULE_ID1)

@pytest.fixture
def epr7(entry7):
    return EntryPouleResult(entry=entry7, poule_id=POULE_ID1)


@pytest.fixture
def spr(entries):
    return SinglePouleResults(poule_id=POULE_ID1, entries=entries)


# --- Test EntryPouleResult (EPR) class ---
# Initialization and Validation Tests
def test_entry_poule_result_creation_with_defaults(entry1):
    epr = EntryPouleResult(entry=entry1, poule_id=POULE_ID1)
    assert epr.entry is not None
    assert epr.entry == entry1
    assert epr.poule_id == POULE_ID1
    assert epr.matches == 0
    assert epr.victories == 0
    assert epr.touches_scored == 0
    assert epr.touches_received == 0

def test_entry_poule_result_creation_no_defaults(entry1):
    epr = EntryPouleResult(entry=entry1, poule_id=POULE_ID1, matches=6, victories=4, touches_scored=21, touches_received=18)
    assert epr.entry == entry1
    assert epr.poule_id == POULE_ID1
    assert epr.matches == 6
    assert epr.victories == 4
    assert epr.touches_scored == 21
    assert epr.touches_received == 18

@pytest.mark.parametrize("invalid_entry", [None, 123, "string", 5.5, [], {}, (1,2)])
def test_entry_poule_result_invalid_entry_type(invalid_entry):
    with pytest.raises(TypeError):
        EntryPouleResult(entry=invalid_entry, poule_id=POULE_ID1)

@pytest.mark.parametrize("invalid_poule_id", [None, "string", 5.5, [], {}, (1,2), True, False])
def test_entry_poule_result_invalid_poule_id_type(entry1, invalid_poule_id):
    with pytest.raises(TypeError):
        EntryPouleResult(entry=entry1, poule_id=invalid_poule_id)

@pytest.mark.parametrize("invalid_poule_id_value", [0, -1, -5])
def test_entry_poule_result_invalid_poule_id_value(entry1, invalid_poule_id_value):
    with pytest.raises(ValueError):
        EntryPouleResult(entry=entry1, poule_id=invalid_poule_id_value)

@pytest.mark.parametrize("invalid_matches", [None, "string", 5.5, [], {}, (1,2), True, False])
def test_entry_poule_result_invalid_matches_type(entry1, invalid_matches):
    with pytest.raises(TypeError):
        EntryPouleResult(entry=entry1, poule_id=POULE_ID1, matches=invalid_matches)

@pytest.mark.parametrize("invalid_matches_value", [-1, -5, -10])
def test_entry_poule_result_invalid_matches_value(entry1, invalid_matches_value):
    with pytest.raises(ValueError):
        EntryPouleResult(entry=entry1, poule_id=POULE_ID1, matches=invalid_matches_value)

@pytest.mark.parametrize("invalid_victories", [None, "string", 5.5, [], {}, (1,2), True, False])
def test_entry_poule_result_invalid_victories_type(entry1, invalid_victories):
    with pytest.raises(TypeError):
        EntryPouleResult(entry=entry1, poule_id=POULE_ID1, victories=invalid_victories)

@pytest.mark.parametrize("invalid_victories_value", [-1, -5, -10])
def test_entry_poule_result_invalid_victories_value(entry1, invalid_victories_value):
    with pytest.raises(ValueError):
        EntryPouleResult(entry=entry1, poule_id=POULE_ID1, victories=invalid_victories_value)

@pytest.mark.parametrize("invalid_touches_scored", [None, "string", 5.5, [], {}, (1,2), True, False])
def test_entry_poule_result_invalid_touches_scored_type(entry1, invalid_touches_scored):
    with pytest.raises(TypeError):
        EntryPouleResult(entry=entry1, poule_id=POULE_ID1, touches_scored=invalid_touches_scored)

@pytest.mark.parametrize("invalid_touches_scored_value", [-1, -5, -10])
def test_entry_poule_result_invalid_touches_scored_value(entry1, invalid_touches_scored_value):
    with pytest.raises(ValueError):
        EntryPouleResult(entry=entry1, poule_id=POULE_ID1, touches_scored=invalid_touches_scored_value)

@pytest.mark.parametrize("invalid_touches_received", [None, "string", 5.5, [], {}, (1,2), True, False])
def test_entry_poule_result_invalid_touches_received_type(entry1, invalid_touches_received):
    with pytest.raises(TypeError):
        EntryPouleResult(entry=entry1, poule_id=POULE_ID1, touches_received=invalid_touches_received)

@pytest.mark.parametrize("invalid_touches_received_value", [-1, -5, -10])
def test_entry_poule_result_invalid_touches_received_value(entry1, invalid_touches_received_value):
    with pytest.raises(ValueError):
        EntryPouleResult(entry=entry1, poule_id=POULE_ID1, touches_received=invalid_touches_received_value)

# Dunder Method Tests
def test_entry_poule_result_equality():
    epr1 = EntryPouleResult(entry=TournamentEntry(id=12, tournament_id=1, fencer=Fencer(id=12, display_name='Yvonne')), poule_id=1, matches=5, victories=3, touches_scored=15, touches_received=10)
    epr2 = EntryPouleResult(entry=TournamentEntry(id=12, tournament_id=1, fencer=Fencer(id=12, display_name='Yvonne')), poule_id=1, matches=5, victories=3, touches_scored=15, touches_received=10)
    assert epr1 == epr2

def test_entry_poule_result_inequality(entry1):
    epr1 = EntryPouleResult(entry=entry1, poule_id=1, matches=5, victories=4, touches_scored=18, touches_received=9)
    epr2 = EntryPouleResult(entry=entry1, poule_id=1, matches=5, victories=3, touches_scored=15, touches_received=10)
    assert epr1 != epr2 # Note: equality does not depend on the entry

def test_entry_poule_result_greater_than(entry1):
    epr1 = EntryPouleResult(entry=entry1, poule_id=1, matches=5, victories=4, touches_scored=18, touches_received=9)
    epr2 = EntryPouleResult(entry=entry1, poule_id=1, matches=5, victories=3, touches_scored=15, touches_received=10)
    assert epr1 > epr2

def test_entry_poule_result_less_than(entry1):
    epr1 = EntryPouleResult(entry=entry1, poule_id=1, matches=5, victories=4, touches_scored=18, touches_received=9)
    epr2 = EntryPouleResult(entry=entry1, poule_id=1, matches=5, victories=3, touches_scored=15, touches_received=10)
    assert epr2 < epr1

# Update Methods Tests
def test_entry_poule_result_add_match_result(epr1, entry2, entry3, entry4):
    match1 = PouleMatch(id=MATCH_ID1, tournament_id=TOURNY_ID1, poule_id=POULE_ID1, entry1=epr1.entry, entry2=entry2, match_index=0)
    match1.record_score(5, 3)

    match2 = PouleMatch(id=MATCH_ID2, tournament_id=TOURNY_ID1, poule_id=POULE_ID1, entry1=epr1.entry, entry2=entry3, match_index=1)
    match2.record_score(2, 5)

    match3 = PouleMatch(id=MATCH_ID2, tournament_id=TOURNY_ID1, poule_id=POULE_ID1, entry1=epr1.entry, entry2=entry4, match_index=2)
    match3.record_score(2, 1)

    epr1.add_match_result(match1)
    assert epr1.matches == 1
    assert epr1.victories == 1
    assert epr1.touches_scored == 5
    assert epr1.touches_received == 3

    epr1.add_match_result(match2)
    assert epr1.matches == 2
    assert epr1.victories == 1
    assert epr1.touches_scored == 7
    assert epr1.touches_received == 8
    
    epr1.add_match_result(match3)
    assert epr1.matches == 3
    assert epr1.victories == 2
    assert epr1.touches_scored == 9
    assert epr1.touches_received == 9

@pytest.mark.parametrize("invalid_match_type", [None, 123, "string", 5.5, [], {}, (1,2)])
def test_entry_poule_result_add_match_result_invalid_types(epr1, invalid_match_type):
    with pytest.raises(TypeError):
        epr1.add_match_result(invalid_match_type)


# --- Test SinglePouleResults (PR) class ---
# Initialization and Validation Tests
def test_single_poule_results_creation_with_defaults(entries):
    spr = SinglePouleResults(poule_id=POULE_ID1, entries=entries)
    
    assert spr.poule_id == POULE_ID1
    
    for poule_result in spr.results:
        assert isinstance(poule_result, EntryPouleResult)
        assert poule_result.poule_id == POULE_ID1
        assert poule_result.matches == 0
        assert poule_result.victories == 0
        assert poule_result.touches_scored == 0
        assert poule_result.touches_received == 0


@pytest.mark.parametrize("invalid_poule_id", [None, "string", 5.5, [], {}, (1,2), True, False])
def test_poule_result_creation_invalid_poule_id_type(entries, invalid_poule_id):
    with pytest.raises(TypeError):
        SinglePouleResults(poule_id=invalid_poule_id, entries=entries)

@pytest.mark.parametrize('invalid_poule_id_value', [0, -1, -5])
def test_poule_result_creation_invalid_poule_id_value(entries, invalid_poule_id_value):
    with pytest.raises(ValueError):
        SinglePouleResults(poule_id=invalid_poule_id_value, entries=entries)

@pytest.mark.parametrize("invalid_entries_type", [None, "string", 5.5, [], [TournamentEntry(id=1, tournament_id=1, fencer=Fencer(id=1, display_name='John')), 'not valid type'], {}, (1,2), True, False])
def test_poule_result_creation_invalid_entries_type(invalid_entries_type):
    with pytest.raises(TypeError):
        SinglePouleResults(poule_id=POULE_ID1, entries=invalid_entries_type)

@pytest.mark.parametrize("invalid_entries_value", [[], [TournamentEntry(id=1, tournament_id=1, fencer=Fencer(id=1, display_name='John'))]])
def test_poule_result_creation_invalid_entries_value(invalid_entries_value):
    with pytest.raises(ValueError):
        SinglePouleResults(poule_id=POULE_ID1, entries=invalid_entries_value)

# Update Method Tests
def test_poule_result_add_match_result(spr):
    match = PouleMatch(id=MATCH_ID1, tournament_id=TOURNY_ID1, poule_id=POULE_ID1, entry1=spr.results[0].entry, entry2=spr.results[1].entry, match_index=0)
    
    match.record_score(5, 3)

    spr.add_match_result(match)
    assert spr.results[0].matches == 1
    assert spr.results[0].victories == 1
    assert spr.results[0].touches_scored == 5
    assert spr.results[0].touches_received == 3

    assert spr.results[1].matches == 1
    assert spr.results[1].victories == 0
    assert spr.results[1].touches_scored == 3
    assert spr.results[1].touches_received == 5

def test_single_poule_results_add_match_result_invalid_type(spr):
    pass


# Result Calculatation Method Tests
def test_poule_result_calculate_standings(spr):
    pass


def test_poule_result_calculate_standings_display_names(entries):
    pass



# --- Test TournamentPouleResults (TPRs) class ---
def test_tournaament_poule_results_creation():
    TournamentPouleResults(tournament_id=TOURNY_ID1, poule_results=[])