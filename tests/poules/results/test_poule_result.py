import pytest
import copy

from entities.fencer import Fencer
from entities.tournament_entry import TournamentEntry
from matches.poule_match import PouleMatch
from poules.results.poule_entry_result import PouleEntryResult
from poules.results.poule_result import PouleResult
from poules.poule_orders import POULE_BOUT_ORDER


# --- Constants ---
FENCER_ID1 = 1
FENCER_DISPLAY_NAME1 = 'John'
ENTRY_ID1 = 1

FENCER_ID2 = 2
FENCER_DISPLAY_NAME2 = 'Steve'
ENTRY_ID2 = 2

FENCER_ID3 = 3
FENCER_DISPLAY_NAME3 = 'Hannah'
ENTRY_ID3 = 3

FENCER_ID4 = 4
FENCER_DISPLAY_NAME4 = 'Emily'
ENTRY_ID4 = 4

FENCER_ID5 = 5
FENCER_DISPLAY_NAME5 = 'Michael'
ENTRY_ID5 = 5

FENCER_ID6 = 6
FENCER_DISPLAY_NAME6 = 'Sarah'
ENTRY_ID6 = 6

FENCER_ID7 = 7
FENCER_DISPLAY_NAME7 = 'Dave'
ENTRY_ID7 = 7

MATCH_ID = 1
POULE_ID = 1
TOURNY_ID = 1

INVALID_ID_TYPES = [None, 'ABC', 1.0, True, [], (1,), {}]
DIFFERENT_POULE_ID = 2
DIFFERENT_TOURNY_ID = 2


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
def fencer4():
    return Fencer(id=FENCER_ID4, display_name=FENCER_DISPLAY_NAME4)

@pytest.fixture
def fencer5():
    return Fencer(id=FENCER_ID5, display_name=FENCER_DISPLAY_NAME5)

@pytest.fixture
def fencer6():
    return Fencer(id=FENCER_ID6, display_name=FENCER_DISPLAY_NAME6)

@pytest.fixture
def fencer7():
    return Fencer(id=FENCER_ID7, display_name=FENCER_DISPLAY_NAME7)

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
def entry4(fencer4):
    return TournamentEntry(id=ENTRY_ID4, tournament_id=TOURNY_ID, fencer=fencer4)

@pytest.fixture
def entry5(fencer5):
    return TournamentEntry(id=ENTRY_ID5, tournament_id=TOURNY_ID, fencer=fencer5)

@pytest.fixture
def entry6(fencer6):
    return TournamentEntry(id=ENTRY_ID6, tournament_id=TOURNY_ID, fencer=fencer6)

@pytest.fixture
def entry7(fencer7):
    return TournamentEntry(id=ENTRY_ID7, tournament_id=TOURNY_ID, fencer=fencer7)

@pytest.fixture
def entries(entry1, entry2, entry3, entry4, entry5, entry6, entry7):
    return [entry1, entry2, entry3, entry4, entry5, entry6, entry7]

@pytest.fixture
def incomplete_poule_matches(entries):
    matches = []
    for i, fencer_numbers_bout_pair in enumerate(POULE_BOUT_ORDER[len(entries)]):
        fencer1_number, fencer2_number = fencer_numbers_bout_pair
        fencer1_index, fencer2_index = fencer1_number - 1, fencer2_number - 1
        entry1, entry2 = entries[fencer1_index], entries[fencer2_index]

        match = make_poule_match(entry1, entry2, match_id=MATCH_ID+i, match_index=i)

        matches.append(match)

    return matches
    
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

@pytest.fixture()
def poule_result(entries):
    return PouleResult(poule_entries=entries, poule_id=POULE_ID, tournament_id=TOURNY_ID)


# --- Initialization and Validation Tests ---
def test_poule_result_creation_valid(entries):
    poule_result = PouleResult(poule_entries=entries, poule_id=POULE_ID, tournament_id=TOURNY_ID)

    with pytest.raises(AttributeError):
        poule_result.poule_entries

    assert poule_result.poule_id == POULE_ID
    assert poule_result.tournament_id == TOURNY_ID
    
    assert len(poule_result.entry_results) == len(entries)
    assert poule_result.entries == entries

    for i, result in enumerate(poule_result.entry_results):
        assert isinstance(result, PouleEntryResult)
        assert result.entry == entries[i]
        assert result.poule_id == POULE_ID
        assert result.tournament_id == TOURNY_ID
        
        assert result.num_matches == 0
        assert result.num_victories == 0
        assert result.touches_scored == 0
        assert result.touches_received == 0

@pytest.mark.parametrize('invalid_poule_id_type', INVALID_ID_TYPES)
def test_poule_result_creation_invalid_poule_id_type(entries, invalid_poule_id_type):
    with pytest.raises(TypeError):
        PouleResult(entries, invalid_poule_id_type, TOURNY_ID)

def test_poule_result_creation_invalid_poule_id_zero(entries):
    with pytest.raises(ValueError):
        PouleResult(entries, 0, TOURNY_ID)

@pytest.mark.parametrize('negative_poule_id', [-100, -10, -1])
def test_poule_result_creation_invalid_poule_id_negative(entries, negative_poule_id):
    with pytest.raises(ValueError):
        PouleResult(entries, negative_poule_id, TOURNY_ID)

@pytest.mark.parametrize('invalid_tournament_id_type', INVALID_ID_TYPES)
def test_poule_result_creation_invalid_tournament_id_type(entries, invalid_tournament_id_type):
    with pytest.raises(TypeError):
        PouleResult(entries, POULE_ID, invalid_tournament_id_type)

def test_poule_result_creation_invalid_tournament_id_zero(entries):
    with pytest.raises(ValueError):
        PouleResult(entries, POULE_ID, 0)

@pytest.mark.parametrize('negative_tournament_id', [-100, -10, -1])
def test_poule_result_creation_invalid_tournament_id_negative(entries, negative_tournament_id):
    with pytest.raises(ValueError):
        PouleResult(entries, POULE_ID, negative_tournament_id)

@pytest.mark.parametrize('invalid_entries_list_type', [None, False, 'Jack', 0.0, 1, (), {}])
def test_poule_result_creation_invalid_entries_list_type(invalid_entries_list_type):
    with pytest.raises(TypeError):
        PouleResult(invalid_entries_list_type, POULE_ID, TOURNY_ID)

@pytest.mark.parametrize(
        'invalid_entries_list_single_entry_invalid_type', 
        [
            [TournamentEntry(ENTRY_ID1, TOURNY_ID, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)), 'Steve'],
            [TournamentEntry(ENTRY_ID1, TOURNY_ID, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)), False],
            [TournamentEntry(ENTRY_ID1, TOURNY_ID, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)), 0.0],
            [TournamentEntry(ENTRY_ID1, TOURNY_ID, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)), 1]
        ]
)
def test_poule_result_creation_invalid_entries_list_entry_type(invalid_entries_list_single_entry_invalid_type):
    with pytest.raises(TypeError):
        PouleResult(invalid_entries_list_single_entry_invalid_type, POULE_ID, TOURNY_ID)

@pytest.mark.parametrize(
        'invalid_entries_list_single_entry_invalid_tournament_id', 
        [
            [TournamentEntry(ENTRY_ID1, TOURNY_ID, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)), TournamentEntry(ENTRY_ID2, DIFFERENT_TOURNY_ID, Fencer(FENCER_ID2, FENCER_DISPLAY_NAME2))],
            [TournamentEntry(ENTRY_ID1, DIFFERENT_TOURNY_ID, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)), TournamentEntry(ENTRY_ID2, TOURNY_ID, Fencer(FENCER_ID2, FENCER_DISPLAY_NAME2))]
        ]
)
def test_poule_result_creation_invalid_entries_list_entry_not_belong_to_tournament(invalid_entries_list_single_entry_invalid_tournament_id):
    with pytest.raises(ValueError):
        PouleResult(invalid_entries_list_single_entry_invalid_tournament_id, POULE_ID, TOURNY_ID)

@pytest.mark.parametrize(
        'invalid_entries_list_duplicate_entry', 
        [
            [
                TournamentEntry(ENTRY_ID1, TOURNY_ID, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)), 
                TournamentEntry(ENTRY_ID1, TOURNY_ID, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1))
            ],
            [
                TournamentEntry(ENTRY_ID1, TOURNY_ID, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1)), 
                TournamentEntry(ENTRY_ID2, TOURNY_ID, Fencer(FENCER_ID2, FENCER_DISPLAY_NAME2)), 
                TournamentEntry(ENTRY_ID1, TOURNY_ID, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1))
            ]
        ]
)
def test_poule_result_creation_invalid_entries_list_has_duplicate_entry(invalid_entries_list_duplicate_entry):
    with pytest.raises(ValueError):
        PouleResult(invalid_entries_list_duplicate_entry, POULE_ID, TOURNY_ID)

@pytest.mark.parametrize('invalid_entries_list_too_few_entries',
                         [
                             [],
                             [TournamentEntry(ENTRY_ID1, TOURNY_ID, Fencer(FENCER_ID1, FENCER_DISPLAY_NAME1))]
                         ]
)
def test_poule_result_creation_invalid_entries_list_fewer_than_two_entries_present(invalid_entries_list_too_few_entries):
    with pytest.raises(ValueError):
        PouleResult(invalid_entries_list_too_few_entries, POULE_ID, TOURNY_ID)


# --- Alternative Constructor Method Tests ---
def test_poule_result_alternative_creation_method_classmethod(entries, completed_poule_matches):
    poule_result = PouleResult.from_matches(entries, completed_poule_matches, POULE_ID, TOURNY_ID)
    
    assert poule_result.entries == entries

    assert poule_result.entry_results[0].num_matches == 6
    assert poule_result.entry_results[0].num_victories == 3
    assert poule_result.entry_results[0].ratio == 3 / 6
    assert poule_result.entry_results[0].touches_scored == 22
    assert poule_result.entry_results[0].touches_received == 21
    assert poule_result.entry_results[0].indicator == 1

    assert poule_result.entry_results[1].num_matches == 6
    assert poule_result.entry_results[1].num_victories == 1
    assert poule_result.entry_results[1].ratio == 1 / 6
    assert poule_result.entry_results[1].touches_scored == 12
    assert poule_result.entry_results[1].touches_received == 28
    assert poule_result.entry_results[1].indicator == -16


    assert poule_result.entry_results[2].num_matches == 6
    assert poule_result.entry_results[2].num_victories == 6
    assert poule_result.entry_results[2].ratio == 6 / 6
    assert poule_result.entry_results[2].touches_scored == 30
    assert poule_result.entry_results[2].touches_received == 13
    assert poule_result.entry_results[2].indicator == 17


    assert poule_result.entry_results[3].num_matches == 6
    assert poule_result.entry_results[3].num_victories == 4
    assert poule_result.entry_results[3].ratio == 4 / 6
    assert poule_result.entry_results[3].touches_scored == 24
    assert poule_result.entry_results[3].touches_received == 20
    assert poule_result.entry_results[3].indicator == 4


    assert poule_result.entry_results[4].num_matches == 6
    assert poule_result.entry_results[4].num_victories == 5
    assert poule_result.entry_results[4].ratio == 5 / 6
    assert poule_result.entry_results[4].touches_scored == 28
    assert poule_result.entry_results[4].touches_received == 18
    assert poule_result.entry_results[4].indicator == 10

    assert poule_result.entry_results[5].num_matches == 6
    assert poule_result.entry_results[5].num_victories == 1
    assert poule_result.entry_results[5].ratio == 1 / 6
    assert poule_result.entry_results[5].touches_scored == 18
    assert poule_result.entry_results[5].touches_received == 27
    assert poule_result.entry_results[5].indicator == -9


    assert poule_result.entry_results[6].num_matches == 6
    assert poule_result.entry_results[6].num_victories == 1
    assert poule_result.entry_results[6].ratio == 1 / 6
    assert poule_result.entry_results[6].touches_scored == 19
    assert poule_result.entry_results[6].touches_received == 26
    assert poule_result.entry_results[6].indicator == -7


# --- Result Calculation Method Tests ---
def test_poule_result_calculate_standings(entries, completed_poule_matches):
    poule_result = PouleResult.from_matches(entries, completed_poule_matches, POULE_ID, TOURNY_ID)

    expected_results = [poule_result.entry_results[2], 
                        poule_result.entry_results[4], 
                        poule_result.entry_results[3], 
                        poule_result.entry_results[0], 
                        poule_result.entry_results[6], 
                        poule_result.entry_results[5], 
                        poule_result.entry_results[1]]
    
    assert poule_result.calculate_standings() == expected_results

def test_poule_result_calculate_standings_display_names(entries, completed_poule_matches):
    poule_result = PouleResult.from_matches(entries, completed_poule_matches, POULE_ID, TOURNY_ID)
    assert poule_result.calculate_standings_display_names() == ['Hannah', 'Michael', 'Emily', 'John', 'Dave', 'Sarah', 'Steve']


# --- State Update Helper Method Tests ---
def test_poule_result__reset(entries, completed_poule_matches):
    poule_result = PouleResult.from_matches(entries, completed_poule_matches, POULE_ID, TOURNY_ID)

    poule_result._reset()

    for result in poule_result.entry_results:
        assert result.num_matches == 0
        assert result.num_victories == 0
        assert result.touches_scored == 0
        assert result.touches_received == 0

# --- Result Update Helper Method Tests ---
def test_poule_result__add_match_result_valid(poule_result):
    assert poule_result.entry_results[0].num_matches == 0
    assert poule_result.entry_results[0].num_victories == 0
    assert poule_result.entry_results[0].touches_scored == 0
    assert poule_result.entry_results[0].touches_received == 0

    assert poule_result.entry_results[1].num_matches == 0
    assert poule_result.entry_results[1].num_victories == 0
    assert poule_result.entry_results[1].touches_scored == 0
    assert poule_result.entry_results[1].touches_received == 0

    match = PouleMatch(id=MATCH_ID, tournament_id=TOURNY_ID, entry1=poule_result.entries[0], entry2=poule_result.entries[1], poule_id=POULE_ID, match_index=0)
    match.record_score(5,3)
    poule_result._add_match_result(match)

    assert poule_result.entry_results[0].num_matches == 1
    assert poule_result.entry_results[0].num_victories == 1
    assert poule_result.entry_results[0].touches_scored == 5
    assert poule_result.entry_results[0].touches_received == 3

    assert poule_result.entry_results[1].num_matches == 1
    assert poule_result.entry_results[1].num_victories == 0
    assert poule_result.entry_results[1].touches_scored == 3
    assert poule_result.entry_results[1].touches_received == 5

@pytest.mark.parametrize('invalid_match_type', [None, 'Steve vs. Hannah', 0.0, 1, [], (1,), {}])
def test_poule_result__add_match_result_not_a_poule_match(poule_result, invalid_match_type):
    match = invalid_match_type
    with pytest.raises(TypeError):
        poule_result._add_match_result(match)

def test_poule_result__add_match_result_poule_id_does_not_match(poule_result):
    match = PouleMatch(id=MATCH_ID, tournament_id=TOURNY_ID, entry1=poule_result.entries[0], entry2=poule_result.entries[1], poule_id=DIFFERENT_POULE_ID, match_index=0)
    match.record_score(5,3)
    with pytest.raises(ValueError):
        poule_result._add_match_result(match)

def test_poule_result__add_match_result_tournament_id_does_not_match(poule_result):
    poule_result.entry_results[0].entry.tournament_id = DIFFERENT_TOURNY_ID
    poule_result.entry_results[1].entry.tournament_id = DIFFERENT_TOURNY_ID
    
    match = PouleMatch(id=MATCH_ID, tournament_id=DIFFERENT_TOURNY_ID, entry1=poule_result.entries[0], entry2=poule_result.entries[1], poule_id=POULE_ID, match_index=0)
    match.record_score(5,3)
    
    poule_result.entry_results[0].entry.tournament_id = TOURNY_ID
    poule_result.entry_results[1].entry.tournament_id = TOURNY_ID

    with pytest.raises(ValueError):
        poule_result._add_match_result(match)

def test_poule_result__add_match_result_entry_not_in_poule(poule_result):
    unknown_entry = TournamentEntry(8, TOURNY_ID, Fencer(8, 'Joanna'))
    match = PouleMatch(id=MATCH_ID, tournament_id=TOURNY_ID, entry1=poule_result.entries[0], entry2=unknown_entry, poule_id=POULE_ID, match_index=0)
    match.record_score(5,3)
    with pytest.raises(ValueError):
        poule_result._add_match_result(match)

def test_poule_result__add_match_result_incomplete_match(poule_result):
    match = PouleMatch(id=MATCH_ID, tournament_id=TOURNY_ID, entry1=poule_result.entries[0], entry2=poule_result.entries[1], poule_id=POULE_ID, match_index=0)
    with pytest.raises(ValueError):
        poule_result._add_match_result(match)

def test_poule_result__compute_results_from_matches():
    pass

def test_poule_result__compute_results_from_matches_invalid_matches_list_type():
    pass

def test_poule_result__compute_results_from_matches_invalid_element_type():
    pass

def test_poule_result__compute_results_from_matches_any_poule_id_does_not_match():
    pass

def test_poule_result__compute_results_from_matches_any_tournament_id_does_not_match():
    pass

def test_poule_result__compute_results_from_matches_any_match_has_entry_that_does_not_belong_to_poule():
    pass