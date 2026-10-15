import pytest

import factories

from de.de_matchup import DEMatchup
from matches.de_match import DEMatch


# --- Constants ---
from constants import TOURNY_ID1, TOURNY_ID2

INVALID_ENTRY_INDEX_TYPES = [None, 0.0, False, True, 'first', [], (), {}, object()]
INVALID_ENTRY_INDEX_VALUES = [-10, -1, 2, 10]
INVALID_ENTRY_TYPES = [None, 0, 1.0, False, True, 'Bill', [], (), {}, object()]


# --- Fixtures ---
@pytest.fixture
def empty_matchup():
    return DEMatchup(
        matchup_number=1, 
        round_number=2, # Round 2 so that it is not a BYE when an entry is added 
        stage_number=1, 
        tournament_id=TOURNY_ID1
    )

@pytest.fixture
def bye_matchup_entry1_present(entry1):
    return DEMatchup(
        matchup_number=1,
        round_number=1,
        stage_number=1,
        tournament_id=TOURNY_ID1,
        entry1=entry1
    )

@pytest.fixture
def bye_matchup_entry2_present(entry2):
    return DEMatchup(
        matchup_number=8,
        round_number=1,
        stage_number=1,
        tournament_id=TOURNY_ID1,
        entry2=entry2
    )

@pytest.fixture
def matchup_entry1_only(entry1):
    return DEMatchup(
        matchup_number=1, 
        round_number=2, # Round 2 so that it is not a BYE 
        stage_number=1, 
        tournament_id=TOURNY_ID1, 
        entry1=entry1
    )

@pytest.fixture
def matchup_entry2_only(entry2):
    return DEMatchup(
        matchup_number=1, 
        round_number=2, # Round 2 so that it is not a BYE
        stage_number=1, 
        tournament_id=TOURNY_ID1, 
        entry2=entry2
    )

@pytest.fixture
def matchup(entry1, entry2):
    return DEMatchup(
        matchup_number=1, 
        round_number=1, 
        stage_number=1, 
        tournament_id=TOURNY_ID1, 
        entry1=entry1, 
        entry2=entry2
    )

# --- Predicate Method Tests ---
def test_de_matchup_has_no_entries(empty_matchup, matchup_entry1_only, matchup_entry2_only, matchup):
    assert empty_matchup.has_no_entries()
    assert not matchup_entry1_only.has_no_entries()
    assert not matchup_entry2_only.has_no_entries()
    assert not matchup.has_no_entries()

def test_de_matchup_is_missing_an_entry(empty_matchup, matchup_entry1_only, matchup_entry2_only, matchup):
    assert empty_matchup.is_missing_an_entry()
    assert matchup_entry1_only.is_missing_an_entry()
    assert matchup_entry2_only.is_missing_an_entry()
    assert not matchup.is_missing_an_entry()

def test_de_matchup_has_an_entry(empty_matchup, matchup_entry1_only, matchup_entry2_only, matchup):
    assert not empty_matchup.has_an_entry()
    assert matchup_entry1_only.has_an_entry()
    assert matchup_entry2_only.has_an_entry()
    assert matchup.has_an_entry()

def test_de_matchup_has_exactly_one_entry(empty_matchup, matchup_entry1_only, matchup_entry2_only, matchup):
    assert not empty_matchup.has_exactly_one_entry()
    assert matchup_entry1_only.has_exactly_one_entry()
    assert matchup_entry2_only.has_exactly_one_entry()
    assert not matchup.has_exactly_one_entry()

def test_de_matchup_has_both_entries(empty_matchup, matchup_entry1_only, matchup_entry2_only, matchup):
    assert not empty_matchup.has_both_entries()
    assert not matchup_entry1_only.has_both_entries()
    assert not matchup_entry2_only.has_both_entries()
    assert matchup.has_both_entries()

def test_de_matchup_has_entry(empty_matchup, matchup_entry1_only, matchup_entry2_only, matchup, entry1, entry2):
    for entry in (entry1, entry2):
        assert not empty_matchup.has_entry(entry)
        assert matchup.has_entry(entry)

    assert matchup_entry1_only.has_entry(entry1)
    assert not matchup_entry1_only.has_entry(entry2)

    assert not matchup_entry2_only.has_entry(entry1)
    assert matchup_entry2_only.has_entry(entry2)

@pytest.mark.parametrize('invalid_entry_type', INVALID_ENTRY_TYPES)
def test_de_matchup_has_entry_invalid_entry_type(matchup, invalid_entry_type):
    with pytest.raises(TypeError):
        matchup.has_entry(invalid_entry_type)

def test_de_matchup_has_entry_at(empty_matchup, matchup_entry1_only, matchup_entry2_only, matchup):
    for index in (0, 1):
        assert not empty_matchup.has_entry_at(index)
        assert matchup.has_entry_at(index)

    assert matchup_entry1_only.has_entry_at(0)
    assert not matchup_entry1_only.has_entry_at(1)

    assert not matchup_entry2_only.has_entry_at(0)
    assert matchup_entry2_only.has_entry_at(1)

@pytest.mark.parametrize('invalid_index_type', INVALID_ENTRY_INDEX_TYPES)
def test_de_matchup_has_entry_at_invalid_index_type(matchup, invalid_index_type):
    with pytest.raises(TypeError):
        matchup.has_entry_at(invalid_index_type)

@pytest.mark.parametrize('invalid_index_value', INVALID_ENTRY_INDEX_VALUES)
def test_de_matchup_has_entry_at_invalid_index_value(matchup, invalid_index_value):
    with pytest.raises(ValueError):
        matchup.has_entry_at(invalid_index_value)

def test_de_matchup_has_match(empty_matchup, matchup_entry1_only, matchup_entry2_only, matchup):
    assert not empty_matchup.has_match()
    assert not matchup_entry1_only.has_match()
    assert not matchup_entry2_only.has_match()
    assert matchup.has_match()

def test_de_matchup_is_first_round(empty_matchup, matchup_entry1_only, matchup_entry2_only, matchup):
    assert not empty_matchup.is_first_round()
    assert not matchup_entry1_only.is_first_round()
    assert not matchup_entry2_only.is_first_round()
    assert matchup.is_first_round()

def test_de_matchup_is_bye(empty_matchup, bye_matchup_entry1_present, bye_matchup_entry2_present, matchup_entry1_only, matchup_entry2_only, matchup):
    assert not empty_matchup.is_bye()
    assert not matchup_entry1_only.is_bye()
    assert not matchup_entry2_only.is_bye()
    assert not matchup.is_bye()

    assert bye_matchup_entry1_present.is_bye()
    assert bye_matchup_entry2_present.is_bye()

@pytest.mark.parametrize('result_recording_method', ['score', 'forfeit'])
def test_de_matchup_is_complete_recorded_result(matchup, result_recording_method):
    assert not matchup.is_complete()

    if result_recording_method == 'score':
        matchup.record_match_score(5, 2)

    else:
        matchup.record_forfeit(0)

    assert matchup.is_complete()

def test_de_matchup_is_complete_bye_matchup(bye_matchup_entry1_present, bye_matchup_entry2_present):
    assert bye_matchup_entry1_present.is_complete()
    assert bye_matchup_entry2_present.is_complete()

@pytest.mark.parametrize('result_recording_method', ['score', 'forfeit'])
def test_de_matchup_is_incomplete(empty_matchup, bye_matchup_entry1_present, bye_matchup_entry2_present, matchup_entry1_only, matchup_entry2_only, matchup, result_recording_method):
    assert empty_matchup.is_incomplete()
    assert matchup_entry1_only.is_incomplete()
    assert matchup_entry2_only.is_incomplete()
    assert matchup.is_incomplete()

    assert not bye_matchup_entry1_present.is_incomplete()
    assert not bye_matchup_entry2_present.is_incomplete()

    if result_recording_method == 'score':
        matchup.record_match_score(5, 2)
    
    else:
        matchup.record_forfeit(0)

    assert not matchup.is_incomplete()


# --- Retrieval Method Tests ---
def test_de_matchup_entry_at(empty_matchup, matchup_entry1_only, matchup_entry2_only, matchup, entry1, entry2):
    assert empty_matchup.entry_at(0) is None
    assert empty_matchup.entry_at(1) is None

    assert matchup_entry1_only.entry_at(0) is entry1
    assert matchup_entry1_only.entry_at(1) is None

    assert matchup_entry2_only.entry_at(0) is None
    assert matchup_entry2_only.entry_at(1) is entry2

    assert matchup.entry_at(0) is entry1
    assert matchup.entry_at(1) is entry2

@pytest.mark.parametrize('invalid_index_type', [None, 1.0, 'first', True, False, [], (), {}])
def test_de_matchup_entry_at_invalid_index_type(matchup, invalid_index_type):
    with pytest.raises(TypeError):
        matchup.entry_at(invalid_index_type)

@pytest.mark.parametrize('invalid_index_value', [-10, -1, 2, 10])
def test_de_matchup_entry_at_invalid_index_value(matchup, invalid_index_value):
    with pytest.raises(ValueError):
        matchup.entry_at(invalid_index_value)


# --- Entry Mutation Method Tests ---
def test_de_matchup_add_entry_valid_add_entries_to_an_empty_matchup(empty_matchup, entry1, entry2):
    assert empty_matchup.entries == (None, None)
    
    empty_matchup.add_entry(entry1, index=0)
    assert empty_matchup.entries == (entry1, None)

    empty_matchup.add_entry(entry2, 1)
    assert empty_matchup.entries == (entry1, entry2)
    assert isinstance(empty_matchup.match, DEMatch)
    assert empty_matchup.match.entries == (entry1, entry2)

def test_de_matchup_add_entry_valid_add_entry_to_a_non_empty_matchup(matchup_entry1_only, matchup_entry2_only, entry1, entry2):
    assert matchup_entry1_only.entries == (entry1, None)
    matchup_entry1_only.add_entry(entry2, 1)
    assert matchup_entry1_only.match.entries == (entry1, entry2)

    assert matchup_entry2_only.entries == (None, entry2)
    matchup_entry2_only.add_entry(entry1, 0)
    assert matchup_entry2_only.match.entries == (entry1, entry2)

@pytest.mark.parametrize('invalid_entry_type', INVALID_ENTRY_TYPES)
def test_de_matchup_add_entry_invalid_entry_type(empty_matchup, invalid_entry_type):
    for entry_index in (0, 1):
        with pytest.raises(TypeError):
            empty_matchup.add_entry(invalid_entry_type, entry_index)

def test_de_matchup_add_entry_invalid_entry_belong_to_another_tournament(empty_matchup):
    invalid_entry = factories.make_entry_at_number(number=1, tournament_id=TOURNY_ID2)

    for entry_index in (0, 1):
        with pytest.raises(ValueError):
            empty_matchup.add_entry(invalid_entry, entry_index)

@pytest.mark.parametrize('invalid_entry_index', INVALID_ENTRY_INDEX_TYPES)
def test_de_matchup_add_entry_invalid_index_type(empty_matchup, entry1, invalid_entry_index):
    with pytest.raises(TypeError):
        empty_matchup.add_entry(entry1, invalid_entry_index)

@pytest.mark.parametrize('invalid_index_value', INVALID_ENTRY_INDEX_VALUES)
def test_de_matchup_add_entry_invalid_index_value(empty_matchup, entry1, invalid_index_value):
    with pytest.raises(ValueError):
        empty_matchup.add_entry(entry1, invalid_index_value)

def test_de_matchup_add_entry_invalid_position_already_occupied(matchup_entry1_only, matchup_entry2_only, matchup, entry1, entry2):
    with pytest.raises(ValueError):
        matchup.add_entry(entry1, 0)

    with pytest.raises(ValueError):
        matchup.add_entry(entry2, 1)

    with pytest.raises(ValueError):
        matchup_entry1_only.add_entry(entry2, 0)

    with pytest.raises(ValueError):
        matchup_entry2_only.add_entry(entry1, 1)

def test_de_matchup_add_entry_invalid_entry_already_present(matchup_entry1_only, matchup_entry2_only, entry1, entry2):
    with pytest.raises(ValueError):
        matchup_entry1_only.add_entry(entry1, index=1)

    with pytest.raises(ValueError):
        matchup_entry2_only.add_entry(entry2, index=0)

def test_de_matchup_remove_entry_valid_remove_both_entries(matchup, entry1, entry2):
    assert matchup.entries == (entry1, entry2)
    assert isinstance(matchup.match, DEMatch)

    matchup.remove_entry(1)

    assert matchup.entries == (entry1, None)
    assert matchup.match is None

    matchup.remove_entry(0)

    assert matchup.entries == (None, None)
    assert matchup.match is None

def test_de_matchup_remove_entry_valid_remove_from_a_one_entry_present_matchup(matchup_entry1_only, matchup_entry2_only, entry1, entry2):
    assert matchup_entry1_only.entries == (entry1, None)
    assert matchup_entry1_only.match is None

    matchup_entry1_only.remove_entry(0)

    assert matchup_entry1_only.entries == (None, None)
    assert matchup_entry1_only.match is None

    assert matchup_entry2_only.entries == (None, entry2)
    assert matchup_entry2_only.match is None

    matchup_entry2_only.remove_entry(1)

    assert matchup_entry2_only.entries == (None, None)
    assert matchup_entry2_only.match is None

@pytest.mark.parametrize('invalid_index_type', INVALID_ENTRY_INDEX_TYPES)
def test_de_matchup_remove_entry_invalid_index_type(matchup, invalid_index_type):
    with pytest.raises(TypeError):
        matchup.remove_entry(invalid_index_type)

@pytest.mark.parametrize('invalid_index_value', INVALID_ENTRY_INDEX_VALUES)
def test_de_matchup_remove_entry_invalid_index_value(matchup, invalid_index_value):
    with pytest.raises(ValueError):
        matchup.remove_entry(invalid_index_value)

@pytest.mark.parametrize('entry_index', [0, 1])
def test_de_matchup_remove_entry_invalid_cannot_remove_from_empty_matchup(empty_matchup, entry_index):
    with pytest.raises(ValueError):
        empty_matchup.remove_entry(entry_index)

def test_de_matchup_remove_entry_invalid_cannot_remove_from_empty_positions(matchup_entry1_only, matchup_entry2_only):
    with pytest.raises(ValueError):
        matchup_entry2_only.remove_entry(0)

    with pytest.raises(ValueError):
        matchup_entry1_only.remove_entry(1)

@pytest.mark.parametrize('entry_index', [0, 1])
def test_de_matchup_remove_entry_cannot_remove_entry_from_a_completed_matchup(matchup, entry_index):
    score1, score2 = 5, 3
    matchup.record_match_score(score1, score2)

    with pytest.raises(ValueError):
        matchup.remove_entry(entry_index)

def test_de_matchup_replace_entry_valid(matchup, entry1, entry2, entry3, entry4):
    assert matchup.entries == (entry1, entry2)
    assert isinstance(matchup.match, DEMatch)
    assert matchup.match.entries == (entry1, entry2)

    matchup.replace_entry(entry3, 0)

    assert matchup.entries == (entry3, entry2)
    assert isinstance(matchup.match, DEMatch)
    assert matchup.match.entries == (entry3, entry2)

    matchup.replace_entry(entry4, 1)

    assert matchup.entries == (entry3, entry4)
    assert isinstance(matchup.match, DEMatch)
    assert matchup.match.entries == (entry3, entry4)

@pytest.mark.parametrize('invalid_entry_type', INVALID_ENTRY_TYPES)
def test_de_matchup_replace_entry_invalid_entry_type(matchup, entry1, entry2, invalid_entry_type):
    original_match = matchup.match
    
    for entry_index in (0, 1):
        with pytest.raises(TypeError):
            matchup.replace_entry(invalid_entry_type, entry_index)

    assert matchup.entries == (entry1, entry2)
    assert matchup.match is original_match
    assert matchup.is_incomplete()

@pytest.mark.parametrize('entry_index', [0, 1])
def test_de_matchup_replace_entry_invalid_entry_belongs_to_another_tournament(matchup, entry1, entry2, entry_index):
    invalid_entry = factories.make_entry_at_number(number=1, tournament_id=TOURNY_ID2)

    original_match = matchup.match

    with pytest.raises(ValueError):
        matchup.replace_entry(invalid_entry, entry_index)

    assert matchup.entries == (entry1, entry2)
    assert matchup.match is original_match
    assert matchup.is_incomplete()

@pytest.mark.parametrize('invalid_index_type', INVALID_ENTRY_INDEX_TYPES)
def test_de_matchup_replace_entry_invalid_index_type(matchup, entry1, entry2, invalid_index_type):
    original_match = matchup.match
    
    with pytest.raises(TypeError):
        matchup.replace_entry(entry1, invalid_index_type)

    assert matchup.entries == (entry1, entry2)
    assert matchup.match is original_match
    assert matchup.is_incomplete()

@pytest.mark.parametrize('invalid_index_value', INVALID_ENTRY_INDEX_VALUES)
def test_de_matchup_replace_entry_invalid_index_value(matchup, entry1, entry2, invalid_index_value):
    original_match = matchup.match
    
    with pytest.raises(ValueError):
        matchup.replace_entry(entry1, invalid_index_value)

    assert matchup.entries == (entry1, entry2)
    assert matchup.match is original_match
    assert matchup.is_incomplete()

def test_de_matchup_replace_entry_empty_entry_position(empty_matchup, matchup_entry1_only, matchup_entry2_only, entry3):    
    for entry_index in (0, 1):
        with pytest.raises(ValueError):
            empty_matchup.replace_entry(entry3, entry_index)

    with pytest.raises(ValueError):
        matchup_entry1_only.replace_entry(entry3, 1)

    with pytest.raises(ValueError):
        matchup_entry2_only.replace_entry(entry3, 0)

@pytest.mark.parametrize('entry_index', [0, 1])
def test_de_matchup_replace_entry_invalid_cannot_replace_entry_from_matchup_with_completed_match(matchup, entry1, entry2, entry3, entry_index):
    score1, score2 = 14, 15
    matchup.record_match_score(score1, score2)

    original_match = matchup.match

    with pytest.raises(ValueError):
        matchup.replace_entry(entry3, entry_index)

    assert matchup.entries == (entry1, entry2)
    assert matchup.match is original_match
    assert matchup.match.score == (score1, score2)
    assert matchup.is_complete()

def test_de_matchup_replace_entry_invalid_cannot_have_duplicate_entry(matchup, entry1, entry2):
    original_match = matchup.match
    
    with pytest.raises(ValueError):
        matchup.replace_entry(entry1, 1)

    assert matchup.entries == (entry1, entry2)
    assert matchup.match is original_match
    assert matchup.is_incomplete()

    with pytest.raises(ValueError):
        matchup.replace_entry(entry2, 0)

    assert matchup.entries == (entry1, entry2)
    assert matchup.match is original_match
    assert matchup.is_incomplete()


# --- State Change Method Tests ---
def test_de_matchup_reset(matchup, entry1, entry2):
    matchup_number, round_number, stage_number, tournament_id = 1, 1, 1, TOURNY_ID1

    assert matchup.entry1 is entry1
    assert matchup.entry2 is entry2
    assert isinstance(matchup.match, DEMatch)

    assert matchup.matchup_number == matchup_number
    assert matchup.round_number == round_number
    assert matchup.stage_number == stage_number
    assert matchup.tournament_id == tournament_id

    matchup.reset() # Clears the entire matchup

    assert matchup.entry1 is None
    assert matchup.entry2 is None
    assert matchup.match is None

    assert matchup.matchup_number == matchup_number
    assert matchup.round_number == round_number
    assert matchup.stage_number == stage_number
    assert matchup.tournament_id == tournament_id

def test_de_matchup_reset_match_scored_match(matchup, entry1, entry2):
    score1, score2 = 15, 12

    assert matchup.entries == (entry1, entry2)
    assert matchup.is_incomplete()

    matchup.record_match_score(score1, score2)

    assert matchup.is_complete()
    assert matchup.match.score == (score1, score2)
    assert matchup.match.forfeited_index is None
    assert matchup.winner is entry1
    assert matchup.loser is entry2

    original_match = matchup.match

    matchup.reset_match() # Resets the match result but keeps the match

    assert matchup.entry1 is entry1
    assert matchup.entry2 is entry2

    assert isinstance(matchup.match, DEMatch)
    assert matchup.match is original_match
    assert matchup.match.score1 is None
    assert matchup.match.score2 is None
    assert matchup.match.forfeited_index is None
    assert matchup.match.entry1 is entry1
    assert matchup.match.entry2 is entry2
    assert matchup.match.is_incomplete()

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_de_matchup_reset_match_forfeited_match(matchup, entry1, entry2, forfeiting_index):
    assert matchup.entries == (entry1, entry2)
    assert matchup.is_incomplete()

    matchup.record_forfeit(forfeiting_index)

    assert matchup.is_complete()
    assert matchup.match.score == (None, None)
    assert matchup.match.forfeited_index == forfeiting_index
    assert matchup.winner is (entry1 if forfeiting_index == 1 else entry2)
    assert matchup.loser is (entry2 if forfeiting_index == 1 else entry1)

    original_match = matchup.match

    matchup.reset_match() # Resets the match result but keeps the match

    assert matchup.entry1 is entry1
    assert matchup.entry2 is entry2

    assert isinstance(matchup.match, DEMatch)
    assert matchup.match is original_match
    assert matchup.match.score1 is None
    assert matchup.match.score2 is None
    assert matchup.match.forfeited_index is None
    assert matchup.match.entry1 is entry1
    assert matchup.match.entry2 is entry2
    assert matchup.match.is_incomplete()


# --- Result Recording Method Tests ---
def test_de_matchup_record_match_score_entry1_wins(matchup):
    score1, score2 = 15, 6
    matchup.record_match_score(score1, score2)

    assert matchup.match.score == (score1, score2)
    assert matchup.match.forfeited_index is None
    assert matchup.match.is_complete()

def test_de_matchup_record_match_score_entry2_wins(matchup):
    score1, score2 = 9, 15
    matchup.record_match_score(score1, score2)

    assert matchup.match.score == (score1, score2)
    assert matchup.match.forfeited_index is None
    assert matchup.match.is_complete()

def test_de_matchup_record_match_score_missing_entry(empty_matchup, matchup_entry1_only, matchup_entry2_only):
    with pytest.raises(ValueError, match='does not contain both entries'):
        empty_matchup.record_match_score(15, 9)
    
    with pytest.raises(ValueError, match='does not contain both entries'):
        matchup_entry1_only.record_match_score(15, 10)

    with pytest.raises(ValueError, match='does not contain both entries'):
        matchup_entry2_only.record_match_score(15, 11)

def test_de_matchup_record_match_score_match_is_none(matchup):
    matchup.match = None
    with pytest.raises(RuntimeError, match='DE match is missing'):
        matchup.record_match_score(12, 15)

def test_de_matchup_record_forfeit_entry1_forfeits(matchup):
    matchup.record_forfeit(0)

    assert matchup.match.score == (None, None)
    assert matchup.match.forfeited_index == 0
    assert matchup.match.is_complete()

def test_de_matchup_record_forfeit_entry2_forfeits(matchup):
    matchup.record_forfeit(1)

    assert matchup.match.score == (None, None)
    assert matchup.match.forfeited_index == 1
    assert matchup.match.is_complete()

def test_de_matchup_record_forfeit_missing_entry(empty_matchup, matchup_entry1_only, matchup_entry2_only):
    with pytest.raises(ValueError, match='does not contain both entries'):
        empty_matchup.record_forfeit(1)

    with pytest.raises(ValueError, match='does not contain both entries'):
        matchup_entry1_only.record_forfeit(0)

    with pytest.raises(ValueError, match='does not contain both entries'):
        matchup_entry2_only.record_forfeit(0)

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_de_matchup_record_forfeit_match_is_none(matchup, forfeiting_index):
    matchup.match = None
    with pytest.raises(RuntimeError, match='DE match is missing'):
        matchup.record_forfeit(forfeiting_index)

def test_de_matchup_replace_with_score_valid(matchup):
    forfeiting_index = 0
    matchup.record_forfeit(forfeiting_index)

    assert matchup.match.score == (None, None)
    assert matchup.match.forfeited_index == forfeiting_index
    assert matchup.match.is_complete()

    score1, score2 = 9, 15
    matchup.replace_with_score(score1, score2)

    assert matchup.match.score == (score1, score2)
    assert matchup.match.forfeited_index is None
    assert matchup.match.is_complete()

@pytest.mark.parametrize('invalid_score_type', [None, False, True, 15.0, 'ten', [], (), {}, object()])
def test_de_matchup_replace_with_score_invalid_score_type(matchup, invalid_score_type):
    original_score1, original_score2 = 2, 10
    matchup.record_match_score(original_score1, original_score2)
    
    assert matchup.match.score == (original_score1, original_score2)
    assert matchup.match.forfeited_index is None
    assert matchup.match.is_complete()
    
    with pytest.raises(TypeError):
        matchup.replace_with_score(invalid_score_type, 0)

    assert matchup.match.score == (original_score1, original_score2)
    assert matchup.match.forfeited_index is None
    assert matchup.match.is_complete()

    with pytest.raises(TypeError):
        matchup.replace_with_score(0, invalid_score_type)

    assert matchup.match.score == (original_score1, original_score2)
    assert matchup.match.forfeited_index is None
    assert matchup.match.is_complete()

@pytest.mark.parametrize('invalid_score_value', [-10, -1, 16, 100])
def test_de_matchup_replace_with_score_invalid_score_value(matchup, invalid_score_value):
    original_score1, original_score2 = 2, 10
    matchup.record_match_score(original_score1, original_score2)

    assert matchup.match.score == (original_score1, original_score2)
    assert matchup.match.forfeited_index is None
    assert matchup.match.is_complete()

    with pytest.raises(ValueError):
        matchup.replace_with_score(invalid_score_value, 0)

    assert matchup.match.score == (original_score1, original_score2)
    assert matchup.match.forfeited_index is None
    assert matchup.match.is_complete()

    with pytest.raises(ValueError):
        matchup.replace_with_score(0, invalid_score_value)

    assert matchup.match.score == (original_score1, original_score2)
    assert matchup.match.forfeited_index is None
    assert matchup.match.is_complete()

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_de_matchup_replace_with_forfeit_valid(matchup, forfeiting_index):
    score1, score2 = 15, 2
    matchup.record_match_score(score1, score2)

    assert matchup.match.score == (score1, score2)
    assert matchup.match.forfeited_index is None
    assert matchup.match.is_complete()

    matchup.replace_with_forfeit(forfeiting_index)

    assert matchup.match.score == (None, None)
    assert matchup.match.forfeited_index == forfeiting_index
    assert matchup.match.is_complete()

@pytest.mark.parametrize('invalid_forfeiting_index_type', INVALID_ENTRY_INDEX_TYPES)
def test_de_matchup_replace_with_forfeit_invalid_forfeiting_index_type(matchup, invalid_forfeiting_index_type):
    matchup.record_match_score(15, 10)
    with pytest.raises(TypeError):
        matchup.replace_with_forfeit(invalid_forfeiting_index_type)

@pytest.mark.parametrize('invalid_forfeiting_index_value', INVALID_ENTRY_INDEX_VALUES)
def test_de_matchup_replace_with_forfeit_invalid_forfeiting_index_value(matchup, invalid_forfeiting_index_value):
    matchup.record_match_score(15, 9)
    with pytest.raises(ValueError):
        matchup.replace_with_forfeit(invalid_forfeiting_index_value)


# --- Winner and Loser Property Tests ---
@pytest.mark.parametrize('winning_index', [0, 1])
def test_de_matchup_winner_property_scored_match(matchup, winning_index):
    winning_score, losing_score = matchup.score_to_win, 0

    score1 = winning_score if winning_index == 0 else losing_score
    score2 = winning_score if winning_index == 1 else losing_score

    matchup.record_match_score(score1, score2)

    assert matchup.winner is (matchup.entry1 if winning_index == 0 else matchup.entry2)

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_de_matchup_winner_property_forfeited_match(matchup, forfeiting_index):
    matchup.record_forfeit(forfeiting_index)
    assert matchup.winner is (matchup.entry2 if forfeiting_index == 0 else matchup.entry1)

@pytest.mark.parametrize('losing_index', [0, 1])
def test_de_matchup_losing_property_scored_match(matchup, losing_index):
    winning_score, losing_score = matchup.score_to_win, 0

    score1 = losing_score if losing_index == 0 else winning_score
    score2 = losing_score if losing_index == 1 else winning_score

    matchup.record_match_score(score1, score2)

    assert matchup.loser is (matchup.entry1 if losing_index == 0 else matchup.entry2)

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_de_matchup_losing_property_forfeited_match(matchup, forfeiting_index):
    matchup.record_forfeit(forfeiting_index)
    assert matchup.loser is (matchup.entry1 if forfeiting_index == 0 else matchup.entry2)
