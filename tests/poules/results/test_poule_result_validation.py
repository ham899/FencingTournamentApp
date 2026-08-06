import copy
from dataclasses import FrozenInstanceError

import pytest

from constants import (
    FENCER_ID1,
    FENCER_ID2,
    ENTRY_ID1,
    ENTRY_ID2,
    POULE_ID1,
    POULE_ID2,
    TOURNY_ID1,
    TOURNY_ID2
)

import factories

from entities.fencer import Fencer
from entities.tournament_entry import TournamentEntry
from poules.results.poule_result import PouleResult
from sample_names import SAMPLE_NAMES


# --- Constants ---
INVALID_ID_TYPES = [None, 'ABC', 1.0, True, [], (1,), {}]
NON_POSITIVE_INTS = [-5, -1, 0]


# --- Fixtures ---
@pytest.fixture
def entries(entry1, entry2, entry3, entry4, entry5, entry6, entry7):
    return (entry1, entry2, entry3, entry4, entry5, entry6, entry7)

@pytest.fixture
def incomplete_poule_matches(entries):
    return factories.make_poule_matches(entries, POULE_ID1, TOURNY_ID1)


# --- Initialization and Validation Tests ---
def test_poule_result_creation_valid_incomplete_matches(entries, incomplete_poule_matches):
    poule_result = PouleResult(entries, incomplete_poule_matches, POULE_ID1, TOURNY_ID1)

    with pytest.raises(AttributeError):
        poule_result.poule_entries

    with pytest.raises(AttributeError):
        poule_result.poule_matches

    assert poule_result.entries == entries
    assert len(poule_result.entry_results) == len(entries)
    assert poule_result.poule_id == POULE_ID1
    assert poule_result.tournament_id == TOURNY_ID1

    for i, entry_result in enumerate(poule_result.entry_results):
        assert entry_result.entry == entries[i]
        assert entry_result.tournament_id == TOURNY_ID1
        assert entry_result.poule_id == POULE_ID1
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

@pytest.mark.parametrize('invalid_entries_type', [None, False, 'Jack', 0.0, 1, [TournamentEntry(101, TOURNY_ID1, Fencer(101, 'Abby'), 10)], {}])
def test_poule_result_creation_invalid_entries_type(invalid_entries_type, incomplete_poule_matches):
    with pytest.raises(TypeError, match='entries in PouleResult must be a tuple'):
        PouleResult(invalid_entries_type, incomplete_poule_matches, POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize('invalid_entry_type', ['Steve', False, 0.0, 1, Fencer(27, 'Jane'), [10], {}])
def test_poule_result_creation_invalid_entries_entry_type(invalid_entry_type, incomplete_poule_matches):
    entries = factories.make_entries(n=3, tournament_id=TOURNY_ID1, initial_seed=True)

    invalid_entries_entry_invalid_type = entries + (invalid_entry_type,)

    with pytest.raises(TypeError, match='must be a TournamentEntry object'):
        PouleResult(invalid_entries_entry_invalid_type, incomplete_poule_matches, POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize(
        'invalid_entries_entry_invalid_tournament_id', 
        [
            (TournamentEntry(ENTRY_ID1, TOURNY_ID1, Fencer(FENCER_ID1, SAMPLE_NAMES[0])), TournamentEntry(ENTRY_ID2, TOURNY_ID2, Fencer(FENCER_ID2, SAMPLE_NAMES[1]))),
            (TournamentEntry(ENTRY_ID1, TOURNY_ID2, Fencer(FENCER_ID1, SAMPLE_NAMES[0])), TournamentEntry(ENTRY_ID2, TOURNY_ID1, Fencer(FENCER_ID2, SAMPLE_NAMES[1])))
        ]
)
def test_poule_result_creation_invalid_entries_entry_not_belong_to_tournament(invalid_entries_entry_invalid_tournament_id, incomplete_poule_matches):
    with pytest.raises(ValueError, match='does not equal this PouleResult container\'s tournament ID'):
        PouleResult(invalid_entries_entry_invalid_tournament_id, incomplete_poule_matches, POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize(('num_entries', 'index_to_duplicate', 'index_to_overwrite'), [(2, 0, 1), (3, 2, 0), (5, 2, 4), (7, 1, 5)])
def test_poule_result_creation_invalid_entries_has_duplicate_entry(num_entries, index_to_duplicate, index_to_overwrite, incomplete_poule_matches):
    entries = list(factories.make_entries(num_entries, TOURNY_ID1, initial_seed=True))

    duplicate_entry = copy.deepcopy(entries[index_to_duplicate])

    entries[index_to_overwrite] = duplicate_entry

    invalid_entries_duplicate_entry = tuple(entries)

    with pytest.raises(ValueError, match='occurs more than once in entries'):
        PouleResult(invalid_entries_duplicate_entry, incomplete_poule_matches, POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize('invalid_entries_too_few_entries', [tuple(), (TournamentEntry(ENTRY_ID1, TOURNY_ID1, Fencer(FENCER_ID1, SAMPLE_NAMES[0])),)])
def test_poule_result_creation_invalid_entries_fewer_than_two_entries_present(invalid_entries_too_few_entries, incomplete_poule_matches):
    with pytest.raises(ValueError, match='must contain at least 2 items'):
        PouleResult(invalid_entries_too_few_entries, incomplete_poule_matches, POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize('invalid_matches_type', [None, True, False, 1, 0.0, 'matches', [1], {}])
def test_poule_result_creation_invalid_matches_type(entries, invalid_matches_type):
    with pytest.raises(TypeError, match='matches must be a tuple'):
        PouleResult(entries, invalid_matches_type, POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize('invalid_match_type', [0, False, 1.0, True, 'Henry', [], (), {}])
def test_poule_result_creation_invalid_matches_item_type(invalid_match_type):
    entries = factories.make_entries(n=3, tournament_id=TOURNY_ID1, initial_seed=True)

    matches = factories.make_poule_matches(entries, POULE_ID1, TOURNY_ID1)
    matches = list(matches)

    matches[1] = invalid_match_type

    invalid_matches_match_type = tuple(matches)

    with pytest.raises(TypeError, match='must be a PouleMatch object'):
        PouleResult(entries, invalid_matches_match_type, POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize(('num_entries', 'num_entries_in_matches'), [(7, 2), (10, 7), (3, 2)])
def test_poule_result_creation_invalid_matches_too_few_matches(num_entries, num_entries_in_matches):
    entries = factories.make_entries(n=num_entries, tournament_id=TOURNY_ID1, initial_seed=True)
    
    too_few_matches = factories.make_poule_matches(factories.make_entries(n=num_entries_in_matches, tournament_id=TOURNY_ID1, initial_seed=True), POULE_ID1, TOURNY_ID1)

    with pytest.raises(ValueError, match=' entries, but actually got '):
        PouleResult(entries, too_few_matches, POULE_ID1, TOURNY_ID1)

def test_poule_result_creation_invalid_matches_empty(entries):
    with pytest.raises(ValueError, match='at least one match'):
        PouleResult(entries, tuple(), POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize(('num_entries', 'num_entries_in_matches'), [(3, 10), (5, 6), (7, 9)])
def test_poule_result_creation_invalid_matches_too_many_matches(num_entries, num_entries_in_matches):
    entries = factories.make_entries(n=num_entries, tournament_id=TOURNY_ID1, initial_seed=True)
    
    too_many_matches = factories.make_poule_matches(factories.make_entries(n=num_entries_in_matches, tournament_id=TOURNY_ID1, initial_seed=True), POULE_ID1, TOURNY_ID1)    
    
    with pytest.raises(ValueError, match=' entries, but actually got '):
        PouleResult(entries, too_many_matches, POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize(('num_entries', 'index'), [(2, 0), (4, 2), (7, 10)])
def test_poule_result_creation_invalid_matches_match_wrong_tournament_id(num_entries, index):
    entries = factories.make_entries(n=num_entries, tournament_id=TOURNY_ID1, initial_seed=True)

    matches = list(factories.make_poule_matches(entries, POULE_ID1, TOURNY_ID1))

    matches[index].tournament_id = TOURNY_ID2

    matches_match_wrong_tournament_id = tuple(matches)
    
    with pytest.raises(ValueError, match=' does not have the same tournament ID '):
        PouleResult(entries, matches_match_wrong_tournament_id, POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize(('num_entries', 'index'), [(7, 3), (2, 0), (5, 9)])
def test_poule_result_creation_invalid_matches_match_wrong_poule_id(num_entries, index):
    entries = factories.make_entries(n=num_entries, tournament_id=TOURNY_ID1, initial_seed=True)

    matches = list(factories.make_poule_matches(entries, POULE_ID1, TOURNY_ID1))

    matches[index].poule_id = POULE_ID2

    matches_match_wrong_poule_id = tuple(matches)

    with pytest.raises(ValueError, match=' matches does not have the same poule ID '):
        PouleResult(entries, matches_match_wrong_poule_id, POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize(
        ('num_entries', 'match_index', 'entry_index', 'invalid_entry'),
        [
            (3, 1, 0, TournamentEntry(id=100, tournament_id=TOURNY_ID1, fencer=Fencer(100, 'Edith'), initial_seed=4)),
            (4, 5, 1, TournamentEntry(id=125, tournament_id=TOURNY_ID1, fencer=Fencer(125, 'Jackie'), initial_seed=5)),
            (5, 8, 0, TournamentEntry(id=135, tournament_id=TOURNY_ID1, fencer=Fencer(135, 'Ronald'), initial_seed=6))
        ]
)
def test_poule_result_creation_invalid_matches_match_wrong_entry(num_entries, match_index, entry_index, invalid_entry):
    entries = factories.make_entries(n=num_entries, tournament_id=TOURNY_ID1, initial_seed=True)

    matches = factories.make_poule_matches(entries, POULE_ID1, TOURNY_ID1)

    matches[match_index].set_entry(invalid_entry, entry_index)

    with pytest.raises(ValueError, match='which is not a valid entry ID in this poule result'):
        PouleResult(entries, matches, POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize(('index', 'num_entries'), [(1, 3), (3, 4), (6, 5), (7, 6), (10, 7)])
def test_poule_result_creation_invalid_matches_match_duplicate_present(index, num_entries):
    entries = factories.make_entries(n=num_entries, tournament_id=TOURNY_ID1, initial_seed=True)

    matches = list(factories.make_poule_matches(entries, POULE_ID1, TOURNY_ID1))

    duplicate_match = copy.deepcopy(matches[index % len(matches)])

    matches[(index + 1) % len(matches)] = duplicate_match
    
    with pytest.raises(ValueError, match='occurs more than once in matches'):
        PouleResult(entries, tuple(matches), POULE_ID1, TOURNY_ID1)

def test_poule_result_creation_invalid_matches_duplicate_match_index():
    entries = factories.make_entries(3, TOURNY_ID1, initial_seed=True)
    matches = list(factories.make_poule_matches(entries, POULE_ID1, TOURNY_ID1))

    matches[1].match_index = matches[0].match_index

    with pytest.raises(ValueError, match='Match index'):
        PouleResult(entries, tuple(matches), POULE_ID1, TOURNY_ID1)

def test_poule_result_creation_invalid_matches_duplicate_match_id():
    entries = factories.make_entries(3, TOURNY_ID1, initial_seed=True)
    matches = list(factories.make_poule_matches(entries, POULE_ID1, TOURNY_ID1))

    matches[1].id = matches[0].id

    with pytest.raises(ValueError, match='occurs more than once in matches'):
        PouleResult(entries, tuple(matches), POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize(('index', 'num_entries'), [(1, 3), (3, 4), (6, 5), (7, 6), (10, 7)])
def test_poule_result_creation_invalid_matches_match_duplicate_entries(index, num_entries):
    entries = factories.make_entries(n=num_entries, tournament_id=TOURNY_ID1, initial_seed=True)

    matches = factories.make_poule_matches(entries, POULE_ID1, TOURNY_ID1)

    duplicate_entry_pair = copy.deepcopy(matches[index % len(matches)].entries)

    matches[(index + 1) % len(matches)].entry1 = duplicate_entry_pair[1]
    matches[(index + 1) % len(matches)].entry2 = duplicate_entry_pair[0]

    with pytest.raises(ValueError, match='occur together in more than one match'):
        PouleResult(entries, matches, POULE_ID1, TOURNY_ID1)

def test_poule_result_creation_invalid_matches_nonconsecutive_match_indices():
    entries = factories.make_entries(3, TOURNY_ID1, initial_seed=True)
    matches = list(factories.make_poule_matches(entries, POULE_ID1, TOURNY_ID1))

    matches[-1].match_index = len(matches)

    with pytest.raises(ValueError, match='consecutive and start at 0'):
        PouleResult(entries, tuple(matches), POULE_ID1, TOURNY_ID1)

@pytest.mark.parametrize('invalid_poule_id_type', INVALID_ID_TYPES)
def test_poule_result_creation_invalid_poule_id_type(entries, incomplete_poule_matches, invalid_poule_id_type):
    with pytest.raises(TypeError):
        PouleResult(entries, incomplete_poule_matches, invalid_poule_id_type, TOURNY_ID1)

@pytest.mark.parametrize('invalid_poule_id_value', NON_POSITIVE_INTS)
def test_poule_result_creation_invalid_poule_id_value(entries, incomplete_poule_matches, invalid_poule_id_value):
    with pytest.raises(ValueError):
        PouleResult(entries, incomplete_poule_matches, invalid_poule_id_value, TOURNY_ID1)

@pytest.mark.parametrize('invalid_tournament_id_type', INVALID_ID_TYPES)
def test_poule_result_creation_invalid_tournament_id_type(entries, incomplete_poule_matches, invalid_tournament_id_type):
    with pytest.raises(TypeError):
        PouleResult(entries, incomplete_poule_matches, POULE_ID1, invalid_tournament_id_type)

@pytest.mark.parametrize('invalid_tournament_id_value', NON_POSITIVE_INTS)
def test_poule_result_creation_invalid_tournament_id_value(entries, incomplete_poule_matches, invalid_tournament_id_value):
    with pytest.raises(ValueError):
        PouleResult(entries, incomplete_poule_matches, POULE_ID1, invalid_tournament_id_value)
