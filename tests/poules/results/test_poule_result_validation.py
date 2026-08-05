import copy
import pytest

from dataclasses import FrozenInstanceError

from entities.fencer import Fencer
from entities.tournament_entry import TournamentEntry
from factories import make_entries, make_poule_match, make_poule_matches
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

def test_poule_result_frozen_attributes(entries, incomplete_poule_matches):
    result = PouleResult(entries, incomplete_poule_matches, POULE_ID1, TOURNY_ID1)

    with pytest.raises(FrozenInstanceError):
        result.entry_results = None

    with pytest.raises(FrozenInstanceError):
        result.poule_id = POULE_ID2

    with pytest.raises(FrozenInstanceError):
        result.tournament_id = TOURNY_ID2

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

@pytest.mark.parametrize(
        ('entries', 'too_few_matches'), 
        [
            (
                make_entries(n=7, tournament_id=TOURNY_ID1, initial_seed=True), 
                make_poule_matches(make_entries(n=2, tournament_id=TOURNY_ID1, initial_seed=True), POULE_ID1, TOURNY_ID1)
            ),
            (
                make_entries(n=10, tournament_id=TOURNY_ID1, initial_seed=True), 
                make_poule_matches(make_entries(n=7, tournament_id=TOURNY_ID1, initial_seed=True), POULE_ID1, TOURNY_ID1)
            ),
            (
                make_entries(n=3, tournament_id=TOURNY_ID1, initial_seed=True),
                make_poule_matches(make_entries(n=2, tournament_id=TOURNY_ID1, initial_seed=True), POULE_ID1, TOURNY_ID1)
            )
        ]
                         
)
def test_poule_result_creation_invalid_matches_too_few_matches(entries, too_few_matches):
    with pytest.raises(ValueError):
        PouleResult(entries, too_few_matches, POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize(
        ('entries', 'too_many_matches'), 
        [
            (
                make_entries(n=3, tournament_id=TOURNY_ID1, initial_seed=True), 
                make_poule_matches(make_entries(n=10, tournament_id=TOURNY_ID1, initial_seed=True), POULE_ID1, TOURNY_ID1)
            ),
            (
                make_entries(n=5, tournament_id=TOURNY_ID1, initial_seed=True), 
                make_poule_matches(make_entries(n=6, tournament_id=TOURNY_ID1, initial_seed=True), POULE_ID1, TOURNY_ID1)
            ),
            (
                make_entries(n=7, tournament_id=TOURNY_ID1, initial_seed=True),
                make_poule_matches(make_entries(n=9, tournament_id=TOURNY_ID1, initial_seed=True), POULE_ID1, TOURNY_ID1)
            )
        ]
                         
)
def test_poule_result_creation_invalid_matches_too_many_matches(entries, too_many_matches):
    with pytest.raises(ValueError):
        PouleResult(entries, too_many_matches, POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize(
        ('entries', 'invalid_matches_match_tournament_id'), 
        [
            (
                make_entries(n=7, tournament_id=TOURNY_ID2, initial_seed=True), 
                make_poule_matches(make_entries(n=7, tournament_id=TOURNY_ID1, initial_seed=True), POULE_ID1, TOURNY_ID1)
            ),
            (
                make_entries(n=3, tournament_id=TOURNY_ID2, initial_seed=True), 
                make_poule_matches(make_entries(n=3, tournament_id=TOURNY_ID1, initial_seed=True), POULE_ID1, TOURNY_ID1)
            ),
            (
                make_entries(n=4, tournament_id=TOURNY_ID2, initial_seed=True),
                make_poule_matches(make_entries(n=2, tournament_id=TOURNY_ID1, initial_seed=True), POULE_ID1, TOURNY_ID1)
            )
        ]
                         
)
def tests_poule_result_creation_invalid_matches_match_wrong_tournament_id(entries, invalid_matches_match_tournament_id):
    with pytest.raises(ValueError):
        PouleResult(entries, invalid_matches_match_tournament_id, POULE_ID1, TOURNY_ID2)

@pytest.mark.parametrize(
        ('entries', 'invalid_matches_match_poule_id'), 
        [
            (
                make_entries(n=7, tournament_id=TOURNY_ID2, initial_seed=True), 
                make_poule_matches(make_entries(n=7, tournament_id=TOURNY_ID1, initial_seed=True), POULE_ID1, TOURNY_ID1)
            ),
            (
                make_entries(n=3, tournament_id=TOURNY_ID2, initial_seed=True), 
                make_poule_matches(make_entries(n=3, tournament_id=TOURNY_ID1, initial_seed=True), POULE_ID1, TOURNY_ID1)
            ),
            (
                make_entries(n=4, tournament_id=TOURNY_ID2, initial_seed=True),
                make_poule_matches(make_entries(n=2, tournament_id=TOURNY_ID1, initial_seed=True), POULE_ID1, TOURNY_ID1)
            )
        ]
                         
)
def tests_poule_result_creation_invalid_matches_match_wrong_poule_id(entries, invalid_matches_match_poule_id):
    with pytest.raises(ValueError):
        PouleResult(entries, invalid_matches_match_poule_id, POULE_ID2, TOURNY_ID1)

@pytest.mark.parametrize(
        ('num_entries', 'match_index', 'entry_index', 'invalid_entry'),
        [
            (3, 1, 0, TournamentEntry(id=100, tournament_id=TOURNY_ID1, fencer=Fencer(100, 'Edith'), initial_seed=4)),
            (4, 6, 1, TournamentEntry(id=125, tournament_id=TOURNY_ID1, fencer=Fencer(125, 'Jackie'), initial_seed=5)),
            (5, 8, 0, TournamentEntry(id=135, tournament_id=TOURNY_ID1, fencer=Fencer(135, 'Ronald'), initial_seed=6))
        ]
)
def tests_poule_result_creation_invalid_matches_match_wrong_entry(num_entries, match_index, entry_index, invalid_entry):
    entries = make_entries(n=num_entries, tournament_id=TOURNY_ID1, initial_seed=True)

    matches = make_poule_matches(entries, POULE_ID1, TOURNY_ID1)

    if entry_index == 0:
        matches[match_index].entry1 = invalid_entry
        
    else:
        matches[match_index].entry2 = invalid_entry

    with pytest.raises(ValueError):
        PouleResult(entries, matches, POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize(('index', 'num_entries'), [(1, 3), (3, 4), (6, 5), (7, 6), (10, 7)])
def tests_poule_result_creation_invalid_matches_match_duplicate_present(index, num_entries):
    entries = make_entries(n=num_entries, tournament_id=TOURNY_ID1, initial_seed=True)

    matches = make_poule_matches(entries, POULE_ID1, TOURNY_ID1)

    duplicate_match = copy.deepcopy(index % len(entries))

    matches[(index % len(entries)) * 2] = duplicate_match
    
    with pytest.raises(ValueError):
        PouleResult(entries, matches, POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize(('index', 'num_entries'), [(1, 3), (3, 4), (6, 5), (7, 6), (10, 7)])
def tests_poule_result_creation_invalid_matches_match_duplicate_entries(index, num_entries):
    entries = make_entries(n=num_entries, tournament_id=TOURNY_ID1, initial_seed=True)

    matches = make_poule_matches(entries, POULE_ID1, TOURNY_ID1)

    duplicate_entry_pair = copy.deepcopy(matches[index % len(entries)].entries)

    matches[(index % len(entries)) * 2].entry1 = duplicate_entry_pair[1]
    matches[(index % len(entries)) * 2].entry2 = duplicate_entry_pair[0]

    with pytest.raises(ValueError):
        PouleResult(entries, matches, POULE_ID1, TOURNY_ID1)

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
