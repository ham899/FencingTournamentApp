import copy
import pytest

from dataclasses import FrozenInstanceError

from entities.fencer import Fencer
from entities.tournament_entry import TournamentEntry
from factories import make_entries, make_poule_match, make_poule
from matches.poule_match import PouleMatch
from poules.poule_orders import POULE_BOUT_ORDER
from poules.results.poule_result import PouleResult, _PouleEntryStats


# --- Constants ---
FENCER_ID1, FENCER_DISPLAY_NAME1, ENTRY_ID1 = 1, 'John', 1

FENCER_ID2, FENCER_DISPLAY_NAME2, ENTRY_ID2 = 2, 'Steve', 2

FENCER_ID3, FENCER_DISPLAY_NAME3, ENTRY_ID3 = 3, 'Hannah', 3

FENCER_ID4, FENCER_DISPLAY_NAME4, ENTRY_ID4 = 4, 'Emily', 4

FENCER_ID5, FENCER_DISPLAY_NAME5, ENTRY_ID5 = 5, 'Michael', 5

FENCER_ID6, FENCER_DISPLAY_NAME6, ENTRY_ID6 = 6, 'Sarah', 6

FENCER_ID7, FENCER_DISPLAY_NAME7, ENTRY_ID7 = 7, 'Dave', 7

MATCH_ID1, MATCH_ID2, MATCH_ID3 = 1, 2, 3

POULE_ID1, POULE_ID2 = 1, 2

TOURNY_ID1, TOURNY_ID2 = 1, 2

INVALID_ID_TYPES = [None, 'ABC', 1.0, True, [], (1,), {}]


# --- Fixtures ---
@pytest.fixture
def fencer1(): return Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)

@pytest.fixture
def fencer2(): return Fencer(FENCER_ID2, FENCER_DISPLAY_NAME2)

@pytest.fixture
def fencer3(): return Fencer(FENCER_ID3, FENCER_DISPLAY_NAME3)

@pytest.fixture
def fencer4(): return Fencer(FENCER_ID4, FENCER_DISPLAY_NAME4)

@pytest.fixture
def fencer5(): return Fencer(FENCER_ID5, FENCER_DISPLAY_NAME5)

@pytest.fixture
def fencer6(): return Fencer(FENCER_ID6, FENCER_DISPLAY_NAME6)

@pytest.fixture
def fencer7(): return Fencer(FENCER_ID7, FENCER_DISPLAY_NAME7)

@pytest.fixture
def entry1(fencer1): return TournamentEntry(ENTRY_ID1, TOURNY_ID1, fencer1)

@pytest.fixture
def entry2(fencer2): return TournamentEntry(ENTRY_ID2, TOURNY_ID1, fencer2)

@pytest.fixture
def entry3(fencer3): return TournamentEntry(ENTRY_ID3, TOURNY_ID1, fencer3)

@pytest.fixture
def entry4(fencer4): return TournamentEntry(ENTRY_ID4, TOURNY_ID1, fencer4)

@pytest.fixture
def entry5(fencer5): return TournamentEntry(ENTRY_ID5, TOURNY_ID1, fencer5)

@pytest.fixture
def entry6(fencer6): return TournamentEntry(ENTRY_ID6, TOURNY_ID1, fencer6)

@pytest.fixture
def entry7(fencer7): return TournamentEntry(ENTRY_ID7, TOURNY_ID1, fencer7)

@pytest.fixture
def entries(entry1, entry2, entry3, entry4, entry5, entry6, entry7):
    return (entry1, entry2, entry3, entry4, entry5, entry6, entry7)

@pytest.fixture
def incomplete_poule_matches(entries):
    matches = []
    for i, fencer_numbers_bout_pair in enumerate(POULE_BOUT_ORDER[len(entries)]):
        fencer1_number, fencer2_number = fencer_numbers_bout_pair
        fencer1_index, fencer2_index = fencer1_number - 1, fencer2_number - 1
        entry1, entry2 = entries[fencer1_index], entries[fencer2_index]

        match = PouleMatch(id=MATCH_ID1+i, tournament_id=TOURNY_ID1, entry1=entry1, entry2=entry2, poule_id=POULE_ID1, match_index=i)

        matches.append(match)

    return tuple(matches)

@pytest.fixture
def partially_completed_poule_matches(incomplete_poule_matches):
    # Make a list of tuples holding the scores of the matches based on the paper example
    match_scores = [
        (3,5), (1,5), (5,4), (4,5), (5,2), (1,5), (5,2),
        (5,4), (2,5), (3,5), (5,3), (5,0), (5,2), (5,1), 
        (5,3), (5,1), (3,5), (3,5), (3,5), (5,1), (5,2)
    ]

    # Copy the incomplete poule matches
    partially_completed_poule_matches = copy.deepcopy(incomplete_poule_matches)

    # Record results for each match based on the set match scores
    for i in range(10):
        score1, score2 = match_scores[i]
        partially_completed_poule_matches[i].record_score(score1, score2)

    return partially_completed_poule_matches
    
@pytest.fixture
def completed_poule_matches(incomplete_poule_matches):
    # Make a list of tuples holding the scores of the matches based on the paper example
    match_scores = [
        (3,5), (1,5), (5,4), (4,5), (5,2), (1,5), (5,2),
        (5,4), (2,5), (3,5), (5,3), (5,0), (5,2), (5,1), 
        (5,3), (5,1), (3,5), (3,5), (3,5), (5,1), (5,2)
    ]

    # Copy the incomplete poule matches
    completed_poule_matches = copy.deepcopy(incomplete_poule_matches)

    # Record results for each match based on the set match scores
    for i, match in enumerate(completed_poule_matches):
        score1, score2 = match_scores[i]
        match.record_score(score1, score2)

    return completed_poule_matches

@pytest.fixture
def poule_result(entries, completed_poule_matches):
    return PouleResult(entries, completed_poule_matches, POULE_ID1, TOURNY_ID1)

@pytest.fixture
def poule_entry_stats():
    return _PouleEntryStats()


##### _PouleEntryStats Tests #####

# --- Initialization and Validation Tests ---
def test__poule_entry_stats_creation_valid():
    entry_stats = _PouleEntryStats()
    assert entry_stats.num_matches == 0
    assert entry_stats.num_victories == 0
    assert entry_stats.touches_scored == 0
    assert entry_stats.touches_received == 0


# --- Property Tests ---
def test__poule_entry_stats_property(poule_entry_stats):
    assert poule_entry_stats.stats == (0, 0, 0, 0)

    poule_entry_stats.add_match_info(True, 5, 2)
    assert poule_entry_stats.stats == (1, 1, 5, 2)

    poule_entry_stats.add_match_info(False, 3, 5)
    assert poule_entry_stats.stats == (2, 1, 8, 7)


# --- Stat Update Method Tests ---
def test__poule_entry_stats_add_match_info_valid_entry_loses(poule_entry_stats):
    poule_entry_stats.add_match_info(False, 1, 5)

    assert poule_entry_stats.num_matches == 1
    assert poule_entry_stats.num_victories == 0
    assert poule_entry_stats.touches_scored == 1
    assert poule_entry_stats.touches_received == 5

def test__poule_entry_stats_add_match_info_valid_entry_wins(poule_entry_stats):
    poule_entry_stats.add_match_info(True, 4, 2)

    assert poule_entry_stats.num_matches == 1
    assert poule_entry_stats.num_victories == 1
    assert poule_entry_stats.touches_scored == 4
    assert poule_entry_stats.touches_received == 2

def test__poule_entry_stats_add_match_info_valid_cumulative(poule_entry_stats):
    poule_entry_stats.add_match_info(False, 4, 5)

    assert poule_entry_stats.num_matches == 1
    assert poule_entry_stats.num_victories == 0
    assert poule_entry_stats.touches_scored == 4
    assert poule_entry_stats.touches_received == 5

    poule_entry_stats.add_match_info(True, 5, 3)

    assert poule_entry_stats.num_matches == 2
    assert poule_entry_stats.num_victories == 1
    assert poule_entry_stats.touches_scored == 9
    assert poule_entry_stats.touches_received == 8

    poule_entry_stats.add_match_info(True, 5, 4)

    assert poule_entry_stats.num_matches == 3
    assert poule_entry_stats.num_victories == 2
    assert poule_entry_stats.touches_scored == 14
    assert poule_entry_stats.touches_received == 12

@pytest.mark.parametrize('invalid_is_victory_type', [None, 'yes', 0, 1.0, [0], (1,), {}])
def test__poule_entry_stats_add_match_info_invalid_is_victory_type(poule_entry_stats, invalid_is_victory_type):
    with pytest.raises(TypeError):
        poule_entry_stats.add_match_info(invalid_is_victory_type, 1, 0)

@pytest.mark.parametrize('invalid_touches_scored_type', [None, 5.0, 'two', True, [7], (1,), {}])
def test__poule_entry_stats_add_match_info_invalid_touches_scored_type(poule_entry_stats, invalid_touches_scored_type):
    with pytest.raises(TypeError):
        poule_entry_stats.add_match_info(True, invalid_touches_scored_type, 0)

@pytest.mark.parametrize('invalid_touches_scored_value', [-10, -5, -1])
def test__poule_entry_stats_add_match_info_invalid_touches_scored_value(poule_entry_stats, invalid_touches_scored_value):
    with pytest.raises(ValueError):
        poule_entry_stats.add_match_info(False, invalid_touches_scored_value, 0)

@pytest.mark.parametrize('invalid_touches_received_type', [None, 5.0, 'two', True, [7], (1,), {}])
def test__poule_entry_stats_add_match_info_invalid_touches_received_type(poule_entry_stats, invalid_touches_received_type):
    with pytest.raises(TypeError):
        poule_entry_stats.add_match_info(False, 0, invalid_touches_received_type)

@pytest.mark.parametrize('invalid_touches_received_value', [-10, -5, -1])
def test__poule_entry_stats_add_match_info_invalid_touches_received_value(poule_entry_stats, invalid_touches_received_value):
    with pytest.raises(ValueError):
        poule_entry_stats.add_match_info(True, 0, invalid_touches_received_value)

@pytest.mark.parametrize(('touches_scored', 'touches_received'), [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])
def test__poule_entry_stats_add_match_info_invalid_touches_scored_equal_to_received(poule_entry_stats, touches_scored, touches_received):
    with pytest.raises(ValueError):
        poule_entry_stats.add_match_info(False, touches_scored, touches_received)

    with pytest.raises(ValueError):
        poule_entry_stats.add_match_info(True, touches_scored, touches_received)

@pytest.mark.parametrize(('touches_scored', 'touches_received'), [(0, 5), (1, 4), (2, 3), (3, 5), (4, 5)])
def test__poule_entry_stats_add_match_info_invalid_victory_score(poule_entry_stats, touches_scored, touches_received):
    with pytest.raises(ValueError):
        poule_entry_stats.add_match_info(True, touches_scored, touches_received)

@pytest.mark.parametrize(('touches_scored', 'touches_received'), [(5, 0), (4, 1), (3, 2), (5, 3), (5, 4)])
def test__poule_entry_stats_add_match_info_invalid_defeat_score(poule_entry_stats, touches_scored, touches_received):
    with pytest.raises(ValueError):
        poule_entry_stats.add_match_info(False, touches_scored, touches_received)


##### PouleResult Tests #####

# --- Initialization and Validation Tests ---
def test_poule_result_creation_valid_incomplete_matches(entries, incomplete_poule_matches):
    poule_result = PouleResult(entries, incomplete_poule_matches, POULE_ID1, TOURNY_ID1)

    with pytest.raises(AttributeError):
        poule_result.poule_entries

    with pytest.raises(AttributeError):
        poule_result.poule_matches

    assert poule_result.entry_results is not None
    assert poule_result.poule_id == POULE_ID1
    assert poule_result.tournament_id == TOURNY_ID1

    for i, entry_result in enumerate(poule_result.entry_results):
        assert entry_result.entry == entries[i]
        assert entry_result.tournament_id == TOURNY_ID1
        assert entry_result.num_matches == 0
        assert entry_result.num_victories == 0
        assert entry_result.touches_scored == 0
        assert entry_result.touches_received == 0
        assert entry_result.victory_ratio == 0

def test_poule_result_creation_valid_completed_matches(entries, completed_poule_matches):
    poule_result = PouleResult(entries, completed_poule_matches, POULE_ID1, TOURNY_ID1)

    assert poule_result.entries == entries

    assert poule_result.entry_results[0].num_matches == 6
    assert poule_result.entry_results[0].num_victories == 3
    assert poule_result.entry_results[0].victory_ratio == 3 / 6
    assert poule_result.entry_results[0].touches_scored == 22
    assert poule_result.entry_results[0].touches_received == 21
    assert poule_result.entry_results[0].indicator == 1

    assert poule_result.entry_results[1].num_matches == 6
    assert poule_result.entry_results[1].num_victories == 1
    assert poule_result.entry_results[1].victory_ratio == 1 / 6
    assert poule_result.entry_results[1].touches_scored == 12
    assert poule_result.entry_results[1].touches_received == 28
    assert poule_result.entry_results[1].indicator == -16

    assert poule_result.entry_results[2].num_matches == 6
    assert poule_result.entry_results[2].num_victories == 6
    assert poule_result.entry_results[2].victory_ratio == 6 / 6
    assert poule_result.entry_results[2].touches_scored == 30
    assert poule_result.entry_results[2].touches_received == 13
    assert poule_result.entry_results[2].indicator == 17

    assert poule_result.entry_results[3].num_matches == 6
    assert poule_result.entry_results[3].num_victories == 4
    assert poule_result.entry_results[3].victory_ratio == 4 / 6
    assert poule_result.entry_results[3].touches_scored == 24
    assert poule_result.entry_results[3].touches_received == 20
    assert poule_result.entry_results[3].indicator == 4

    assert poule_result.entry_results[4].num_matches == 6
    assert poule_result.entry_results[4].num_victories == 5
    assert poule_result.entry_results[4].victory_ratio == 5 / 6
    assert poule_result.entry_results[4].touches_scored == 28
    assert poule_result.entry_results[4].touches_received == 18
    assert poule_result.entry_results[4].indicator == 10

    assert poule_result.entry_results[5].num_matches == 6
    assert poule_result.entry_results[5].num_victories == 1
    assert poule_result.entry_results[5].victory_ratio == 1 / 6
    assert poule_result.entry_results[5].touches_scored == 18
    assert poule_result.entry_results[5].touches_received == 27
    assert poule_result.entry_results[5].indicator == -9

    assert poule_result.entry_results[6].num_matches == 6
    assert poule_result.entry_results[6].num_victories == 1
    assert poule_result.entry_results[6].victory_ratio == 1 / 6
    assert poule_result.entry_results[6].touches_scored == 19
    assert poule_result.entry_results[6].touches_received == 26
    assert poule_result.entry_results[6].indicator == -7

@pytest.mark.parametrize('invalid_entries_type', [None, False, 'Jack', 0.0, 1])
def test_poule_result_creation_invalid_entries_type(invalid_entries_type, completed_poule_matches):
    with pytest.raises(TypeError):
        PouleResult(invalid_entries_type, completed_poule_matches, POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize(
        'invalid_entries_entry_invalid_type', 
        [
            (TournamentEntry(ENTRY_ID1, TOURNY_ID1, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)), 'Steve'),
            (TournamentEntry(ENTRY_ID1, TOURNY_ID1, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)), False),
            (TournamentEntry(ENTRY_ID1, TOURNY_ID1, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)), 0.0),
            (TournamentEntry(ENTRY_ID1, TOURNY_ID1, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)), 1)
        ]
)
def test_poule_result_creation_invalid_entries_entry_type(invalid_entries_entry_invalid_type, completed_poule_matches):
    with pytest.raises(TypeError):
        PouleResult(invalid_entries_entry_invalid_type, completed_poule_matches, POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize(
        'invalid_entries_entry_invalid_tournament_id', 
        [
            (TournamentEntry(ENTRY_ID1, TOURNY_ID1, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)), TournamentEntry(ENTRY_ID2, TOURNY_ID2, Fencer(FENCER_ID2, FENCER_DISPLAY_NAME2))),
            (TournamentEntry(ENTRY_ID1, TOURNY_ID2, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)), TournamentEntry(ENTRY_ID2, TOURNY_ID1, Fencer(FENCER_ID2, FENCER_DISPLAY_NAME2)))
        ]
)
def test_poule_result_creation_invalid_entries_entry_not_belong_to_tournament(invalid_entries_entry_invalid_tournament_id, completed_poule_matches):
    with pytest.raises(ValueError):
        PouleResult(invalid_entries_entry_invalid_tournament_id, completed_poule_matches, POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize(
        'invalid_entries_duplicate_entry', 
        [
            (
                TournamentEntry(ENTRY_ID1, TOURNY_ID1, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)), 
                TournamentEntry(ENTRY_ID1, TOURNY_ID1, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1))
            ),
            (
                TournamentEntry(ENTRY_ID1, TOURNY_ID1, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)), 
                TournamentEntry(ENTRY_ID2, TOURNY_ID1, Fencer(FENCER_ID2, FENCER_DISPLAY_NAME2)), 
                TournamentEntry(ENTRY_ID1, TOURNY_ID1, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1))
            )
        ]
)
def test_poule_result_creation_invalid_entries_has_duplicate_entry(invalid_entries_duplicate_entry, completed_poule_matches):
    with pytest.raises(ValueError):
        PouleResult(invalid_entries_duplicate_entry, completed_poule_matches, POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize('invalid_entries_too_few_entries',
                         [
                             tuple(),
                             (TournamentEntry(ENTRY_ID1, TOURNY_ID1, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)),)
                         ]
)
def test_poule_result_creation_invalid_entries_fewer_than_two_entries_present(invalid_entries_too_few_entries, completed_poule_matches):
    with pytest.raises(ValueError):
        PouleResult(invalid_entries_too_few_entries, completed_poule_matches, POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize('invalid_matches_type', [None, True, False, 1, 0.0, 'matches'])
def test_poule_result_creation_invalid_matches_type(entries, invalid_matches_type):
    with pytest.raises(TypeError):
        PouleResult(entries, invalid_matches_type, POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize('invalid_matches_item_type',
                         [
                             (
                                 PouleMatch(id=1, 
                                            tournament_id=TOURNY_ID1, 
                                            entry1=TournamentEntry(ENTRY_ID1, TOURNY_ID1, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)), 
                                            entry2=TournamentEntry(ENTRY_ID2, TOURNY_ID1, Fencer(FENCER_ID2, FENCER_DISPLAY_NAME2)),
                                            poule_id=POULE_ID1,
                                            match_index=0), 
                                 PouleMatch(id=2, 
                                            tournament_id=TOURNY_ID1, 
                                            entry1=TournamentEntry(ENTRY_ID1, TOURNY_ID1, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)), 
                                            entry2=TournamentEntry(ENTRY_ID3, TOURNY_ID1, Fencer(FENCER_ID3, FENCER_DISPLAY_NAME3)),
                                            poule_id=POULE_ID1,
                                            match_index=1), 
                                True
                             ),
                             (
                                 PouleMatch(id=1, 
                                            tournament_id=TOURNY_ID1, 
                                            entry1=TournamentEntry(ENTRY_ID1, TOURNY_ID1, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)), 
                                            entry2=TournamentEntry(ENTRY_ID2, TOURNY_ID1, Fencer(FENCER_ID2, FENCER_DISPLAY_NAME2)),
                                            poule_id=POULE_ID1,
                                            match_index=0), 
                                 'Henry',
                                 PouleMatch(id=2, 
                                            tournament_id=TOURNY_ID1, 
                                            entry1=TournamentEntry(ENTRY_ID2, TOURNY_ID1, Fencer(FENCER_ID2, FENCER_DISPLAY_NAME2)), 
                                            entry2=TournamentEntry(ENTRY_ID3, TOURNY_ID1, Fencer(FENCER_ID3, FENCER_DISPLAY_NAME3)),
                                            poule_id=POULE_ID1,
                                            match_index=2)
                             ),
                             (
                                 0.0,
                                 PouleMatch(id=2, 
                                            tournament_id=TOURNY_ID1, 
                                            entry1=TournamentEntry(ENTRY_ID1, TOURNY_ID1, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)), 
                                            entry2=TournamentEntry(ENTRY_ID3, TOURNY_ID1, Fencer(FENCER_ID3, FENCER_DISPLAY_NAME3)),
                                            poule_id=POULE_ID1,
                                            match_index=1), 
                                 PouleMatch(id=3, 
                                            tournament_id=TOURNY_ID1, 
                                            entry1=TournamentEntry(ENTRY_ID2, TOURNY_ID1, Fencer(FENCER_ID2, FENCER_DISPLAY_NAME2)), 
                                            entry2=TournamentEntry(ENTRY_ID3, TOURNY_ID1, Fencer(FENCER_ID3, FENCER_DISPLAY_NAME3)),
                                            poule_id=POULE_ID1,
                                            match_index=2)
                             )
                         ]
)
def test_poule_result_creation_invalid_matches_item_type(entries, invalid_matches_item_type):
    with pytest.raises(TypeError):
        PouleResult(entries[:3], invalid_matches_item_type, POULE_ID1, TOURNY_ID1)

def test_poule_result_creation_invalid_matches_too_few_matches():
    pass

def test_poule_result_creation_invalid_matches_too_many_matches():
    pass

def tests_poule_result_creation_invalid_matches_match_wrong_tournament_id():
    pass

def tests_poule_result_creation_invalid_matches_match_wrong_poule_id():
    pass

def tests_poule_result_creation_invalid_matches_match_wrong_entry():
    pass

def tests_poule_result_creation_invalid_matches_match_duplicate_present():
    pass

def tests_poule_result_creation_invalid_matches_match_duplicate_entries():
    pass

@pytest.mark.parametrize('invalid_poule_id_type', INVALID_ID_TYPES)
def test_poule_result_creation_invalid_poule_id_type(entries, completed_poule_matches, invalid_poule_id_type):
    with pytest.raises(TypeError):
        PouleResult(entries, completed_poule_matches, invalid_poule_id_type, TOURNY_ID1)

@pytest.mark.parametrize('invalid_poule_id_value', [-10, -1, 0])
def test_poule_result_creation_invalid_poule_id_value(entries, completed_poule_matches, invalid_poule_id_value):
    with pytest.raises(ValueError):
        PouleResult(entries, completed_poule_matches, invalid_poule_id_value, TOURNY_ID1)

@pytest.mark.parametrize('invalid_tournament_id_type', INVALID_ID_TYPES)
def test_poule_result_creation_invalid_tournament_id_type(entries, completed_poule_matches, invalid_tournament_id_type):
    with pytest.raises(TypeError):
        PouleResult(entries, completed_poule_matches, POULE_ID1, invalid_tournament_id_type)

@pytest.mark.parametrize('invalid_tournament_id_value', [-10, -1, 0])
def test_poule_result_creation_invalid_tournament_id_value(entries, completed_poule_matches, invalid_tournament_id_value):
    with pytest.raises(ValueError):
        PouleResult(entries, completed_poule_matches, POULE_ID1, invalid_tournament_id_value)


# --- Property Tests ---
def test_poule_result_entries_property(entries, poule_result):
    assert poule_result.entries == entries

def test_poule_result_ranked_results_property(poule_result):
    expected_results = (poule_result.entry_results[2], 
                        poule_result.entry_results[4], 
                        poule_result.entry_results[3], 
                        poule_result.entry_results[0], 
                        poule_result.entry_results[6], 
                        poule_result.entry_results[5], 
                        poule_result.entry_results[1])
    
    assert poule_result.ranked_results == expected_results

def test_poule_result_ranked_results_display_names_property(poule_result):
    assert poule_result.ranked_results_display_names == ('Hannah', 'Michael', 'Emily', 'John', 'Dave', 'Sarah', 'Steve')