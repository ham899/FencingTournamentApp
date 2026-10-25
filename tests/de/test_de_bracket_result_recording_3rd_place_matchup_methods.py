import pytest

import factories


# --- Constants ---
from constants import TOURNY_ID1

VALID_STAGE_NUMBER1 = 1


# --- Fixtures ---
@pytest.fixture
def initial_full_top_4_bracket_with_third_place_matchup():
    return factories.make_de_bracket_from_defaults(
        num_entries=4,
        tournament_id=TOURNY_ID1,
        stage_number=VALID_STAGE_NUMBER1,
        has_third_place_match=True
    )

@pytest.fixture
def semi_final_filled_top_4_bracket_with_third_place_matchup():
    bracket = factories.make_de_bracket_from_defaults(
        num_entries=4,
        tournament_id=TOURNY_ID1,
        stage_number=VALID_STAGE_NUMBER1,
        has_third_place_match=True
    )

    bracket.record_match_score(round_index=0, matchup_index=0, score1=15, score2=7)
    bracket.record_match_score(round_index=0, matchup_index=1, score1=13, score2=15)

    return bracket


# --- Third-place Reset Method Tests ---
def test_de_bracket_reset_scored_third_place_match_result(initial_full_top_4_bracket_with_third_place_matchup, entry3, entry4):
    bracket = initial_full_top_4_bracket_with_third_place_matchup
    semi_final_1 = bracket.get_matchup(round_index=0, matchup_index=0)
    semi_final_2 = bracket.get_matchup(round_index=0, matchup_index=1)
    final = bracket.get_matchup(round_index=1, matchup_index=0)

    # Complete the two semi-final matchups
    bracket.record_match_score(round_index=0, matchup_index=0, score1=15, score2=11)
    bracket.record_match_score(round_index=0, matchup_index=1, score1=14, score2=15)

    # Complete the third-place matchup
    bracket.record_third_place_match_score(score1=15, score2=9)

    # Verify the third-place matchup results
    third_place_matchup_entries = (entry3, entry4)
    third_place_matchup = bracket.third_place_matchup

    assert third_place_matchup.is_complete()
    assert third_place_matchup.entries == third_place_matchup_entries
    assert third_place_matchup.has_match()
    assert third_place_matchup.match.score == (15, 9)
    assert third_place_matchup.match.forfeited_index is None

    # Record the final matchup result
    bracket.record_match_score(round_index=1, matchup_index=0, score1=15, score2=4)

    # Verify all other matchup results
    assert semi_final_1.match.score == (15, 11)
    assert semi_final_2.match.score == (14, 15)
    assert final.match.score == (15, 4)

    # Reset the third place matchup
    bracket.reset_third_place_match_result()

    # Verify that the third place matchup has been reset
    assert third_place_matchup.is_incomplete()
    assert third_place_matchup.entries == third_place_matchup_entries
    assert third_place_matchup.has_match()
    assert third_place_matchup.match.score == (None, None)
    assert third_place_matchup.match.forfeited_index is None

    # Verify that all the other matchups remain the same
    assert semi_final_1.match.score == (15, 11)
    assert semi_final_2.match.score == (14, 15)
    assert final.match.score == (15, 4)

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_de_bracket_reset_forfeited_third_place_match_result(initial_full_top_4_bracket_with_third_place_matchup, entry3, entry4, forfeiting_index):
    bracket = initial_full_top_4_bracket_with_third_place_matchup
    semi_final_1 = bracket.get_matchup(round_index=0, matchup_index=0)
    semi_final_2 = bracket.get_matchup(round_index=0, matchup_index=1)
    final = bracket.get_matchup(round_index=1, matchup_index=0)
    third_place_matchup = bracket.third_place_matchup

    # Complete the two semi-final matchups
    bracket.record_match_score(round_index=0, matchup_index=0, score1=15, score2=11)
    bracket.record_match_score(round_index=0, matchup_index=1, score1=14, score2=15)

    # Complete the third-place matchup
    bracket.record_third_place_match_forfeit(forfeiting_index)

    # Verify the third-place matchup results
    third_place_matchup_entries = (entry3, entry4)
    assert third_place_matchup.is_complete()
    assert third_place_matchup.entries == third_place_matchup_entries
    assert third_place_matchup.has_match()
    assert third_place_matchup.match.score == (None, None)
    assert third_place_matchup.match.forfeited_index == forfeiting_index

    # Record the final matchup result
    bracket.record_match_score(round_index=1, matchup_index=0, score1=15, score2=4)

    # Verify all other matchup scores
    assert semi_final_1.match.score == (15, 11)
    assert semi_final_2.match.score == (14, 15)
    assert final.match.score == (15, 4)

    # Reset the third place matchup
    bracket.reset_third_place_match_result()

    # Verify that the third place matchup has been reset
    assert third_place_matchup.is_incomplete()
    assert third_place_matchup.entries == third_place_matchup_entries
    assert third_place_matchup.has_match()
    assert third_place_matchup.match.score == (None, None)
    assert third_place_matchup.match.forfeited_index is None

    # Verify that all the other matchups remain the same
    assert semi_final_1.match.score == (15, 11)
    assert semi_final_2.match.score == (14, 15)
    assert final.match.score == (15, 4)

@pytest.mark.parametrize(('semi_final_matchup_index', 'semi_final_score'), [(0, (15, 7)), (1, (13, 15))])
def test_de_bracket_reset_semi_final_match_when_third_place_result_exists(semi_final_filled_top_4_bracket_with_third_place_matchup, semi_final_matchup_index, semi_final_score):
    bracket = semi_final_filled_top_4_bracket_with_third_place_matchup
    third_place_matchup = bracket.third_place_matchup
    semi_final_matchup = bracket.get_matchup(round_index=0, matchup_index=semi_final_matchup_index)

    # Record a score for the third-place matchup
    bracket.record_third_place_match_score(score1=11, score2=15)

    # Verify the third-place matchup result
    assert third_place_matchup.is_complete()
    assert third_place_matchup.match.score == (11, 15)

    # Attempt to reset a semi-final matchup
    with pytest.raises(ValueError):
        bracket.reset_match_result(round_index=0, matchup_index=semi_final_matchup_index)

    # Verify that the third-place and semi-final matchups remain unchanged
    assert third_place_matchup.is_complete()
    assert third_place_matchup.match.score == (11, 15)

    assert semi_final_matchup.is_complete()
    assert semi_final_matchup.match.score == semi_final_score
    assert semi_final_matchup.match.forfeited_index is None

def test_de_bracket_reset_invalid_no_third_place_match_exists(initial_full_top_4_bracket_with_third_place_matchup):
    with pytest.raises(ValueError):
        initial_full_top_4_bracket_with_third_place_matchup.reset_third_place_match_result()


# --- Third-place Result Recording Method Tests ---
def test_de_bracket_record_third_place_match_score(initial_full_top_4_bracket_with_third_place_matchup, entry1, entry2):
    bracket = initial_full_top_4_bracket_with_third_place_matchup

    # Get the third-place matchup
    matchup = bracket.third_place_matchup

    assert matchup.entries == (None, None)
    assert matchup.is_incomplete()
    assert not matchup.has_match()

    # Record first two semi-final matchups
    bracket.record_forfeit(round_index=0, matchup_index=0, forfeiting_index=0)
    bracket.record_forfeit(round_index=0, matchup_index=1, forfeiting_index=1)

    # Verify that the entries have been moved to the third-place matchup
    assert matchup.entries == (entry2, entry1) # Top bracket moves to bottom of third-place matchup and bottom bracket moves to top
    assert matchup.is_incomplete()

    # Record the results for the third-place matchup
    bracket.record_third_place_match_score(score1=12, score2=15)

    # Verify the new result
    assert matchup.is_complete()
    assert matchup.match.score == (12, 15)
    assert matchup.match.forfeited_index is None

def test_de_bracket_record_third_place_match_score_invalid_atomicity(initial_full_top_4_bracket_with_third_place_matchup, entry4, entry3):
    bracket = initial_full_top_4_bracket_with_third_place_matchup
    semi_final_1 = bracket.get_matchup(round_index=0, matchup_index=0)
    semi_final_2 = bracket.get_matchup(round_index=0, matchup_index=1)
    final = bracket.get_matchup(round_index=1, matchup_index=0)
    third_place_matchup = bracket.third_place_matchup

    # Record first two semi-final matchups
    bracket.record_forfeit(round_index=0, matchup_index=0, forfeiting_index=1)
    bracket.record_match_score(round_index=0, matchup_index=1, score1=14, score2=15)

    # Save the entries that advanced to the third-place matchup
    third_place_entries = (entry3, entry4)

    # Record the final matchup result
    bracket.record_match_score(round_index=1, matchup_index=0, score1=15, score2=7)

    # Verify all the main bracket matchups
    assert semi_final_1.is_complete()
    assert semi_final_1.match.score == (None, None)
    assert semi_final_1.match.forfeited_index == 1

    assert semi_final_2.is_complete()
    assert semi_final_2.match.score == (14, 15)
    assert semi_final_2.match.forfeited_index is None

    assert final.is_complete()
    assert final.match.score == (15, 7)
    assert final.match.forfeited_index is None

    # Verify the third-place matchup is incomplete
    assert third_place_matchup.entries == third_place_entries
    assert third_place_matchup.is_incomplete()
    assert third_place_matchup.has_match()
    assert third_place_matchup.match.score == (None, None)
    assert third_place_matchup.match.forfeited_index is None

    # Attempt to record an invalid third-place matchup result
    with pytest.raises(ValueError):
        bracket.record_third_place_match_score(score1=15, score2=-3)

    # Verify that the main bracket matchups remain unchanged
    assert semi_final_1.is_complete()
    assert semi_final_1.match.score == (None, None)
    assert semi_final_1.match.forfeited_index == 1

    assert semi_final_2.is_complete()
    assert semi_final_2.match.score == (14, 15)
    assert semi_final_2.match.forfeited_index is None

    assert final.is_complete()
    assert final.match.score == (15, 7)
    assert final.match.forfeited_index is None

    # Verify that the third-place matchup state remains unchanged
    assert third_place_matchup.entries == third_place_entries
    assert third_place_matchup.is_incomplete()
    assert third_place_matchup.has_match()
    assert third_place_matchup.match.score == (None, None)
    assert third_place_matchup.match.forfeited_index is None

def test_de_bracket_record_third_place_match_score_invalid_no_entries_present(initial_full_top_4_bracket_with_third_place_matchup):
    bracket = initial_full_top_4_bracket_with_third_place_matchup
    third_place_matchup = bracket.third_place_matchup

    # Verify that the third-place matchup is incomplete and has no entries
    assert third_place_matchup.is_incomplete()
    assert third_place_matchup.entries == (None, None)

    # Attempt to record a third-place matchup result when no entries are present
    with pytest.raises(ValueError):
        bracket.record_third_place_match_score(score1=10, score2=15)

    # Verify that the third-place matchup state remains unchanged
    assert third_place_matchup.is_incomplete()
    assert third_place_matchup.entries == (None, None)

def test_de_bracket_record_third_place_match_score_invalid_one_entry_present(initial_full_top_4_bracket_with_third_place_matchup, entry1):
    bracket = initial_full_top_4_bracket_with_third_place_matchup
    third_place_matchup = bracket.third_place_matchup

    # Record one semi-final matchup
    bracket.record_forfeit(round_index=0, matchup_index=0, forfeiting_index=0)

    # Verify that the third-place matchup is incomplete and has one entry
    assert third_place_matchup.is_incomplete()
    assert third_place_matchup.entries == (None, entry1)

    # Attempt to record a third-place matchup result when only one entry is present
    with pytest.raises(ValueError):
        bracket.record_third_place_match_score(score1=15, score2=11)

    # Verify that the third-place matchup state remains unchanged
    assert third_place_matchup.is_incomplete()
    assert third_place_matchup.entries == (None, entry1)

def test_de_bracket_third_place_match_score_invalid_result_already_exists(semi_final_filled_top_4_bracket_with_third_place_matchup):
    bracket = semi_final_filled_top_4_bracket_with_third_place_matchup
    third_place_matchup = bracket.third_place_matchup

    # Record a third-place result
    bracket.record_third_place_match_score(score1=15, score2=14)

    # Attempt to record a result again
    with pytest.raises(ValueError):
        bracket.record_third_place_match_score(score1=10, score2=15)

    # Verify that the original result remains unchanged
    assert third_place_matchup.is_complete()
    assert third_place_matchup.match.score == (15, 14)
    assert third_place_matchup.match.forfeited_index is None

def test_de_bracket_replace_scored_third_place_match_with_score(semi_final_filled_top_4_bracket_with_third_place_matchup):
    bracket = semi_final_filled_top_4_bracket_with_third_place_matchup
    third_place_matchup = bracket.third_place_matchup

    # Record a score for the third-place matchup
    bracket.record_third_place_match_score(score1=10, score2=15)

    # Verify the third-place matchup result
    assert third_place_matchup.is_complete()
    assert third_place_matchup.match.score == (10, 15)
    assert third_place_matchup.match.forfeited_index is None

    # Replace the third-place matchup result with a new score
    bracket.replace_third_place_match_with_score(score1=15, score2=12)

    # Verify the updated third-place matchup result
    assert third_place_matchup.is_complete()
    assert third_place_matchup.match.score == (15, 12)
    assert third_place_matchup.match.forfeited_index is None

    # Verify that the semi-final matchups remain unchanged
    assert bracket.get_matchup(round_index=0, matchup_index=0).match.score == (15, 7)
    assert bracket.get_matchup(round_index=0, matchup_index=1).match.score == (13, 15)

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_de_bracket_replace_forfeited_third_place_match_with_score(semi_final_filled_top_4_bracket_with_third_place_matchup, forfeiting_index):
    bracket = semi_final_filled_top_4_bracket_with_third_place_matchup
    third_place_matchup = bracket.third_place_matchup

    # Record a forfeit for the third-place matchup
    bracket.record_third_place_match_forfeit(forfeiting_index)

    # Verify the third-place matchup result
    assert third_place_matchup.is_complete()
    assert third_place_matchup.match.is_forfeit()
    assert third_place_matchup.match.score == (None, None)
    assert third_place_matchup.match.forfeited_index == forfeiting_index

    # Replace the third-place matchup result with a new score
    bracket.replace_third_place_match_with_score(score1=10, score2=15)

    # Verify the updated third-place matchup result
    assert third_place_matchup.is_complete()
    assert third_place_matchup.match.score == (10, 15)
    assert third_place_matchup.match.forfeited_index is None

    # Verify that the semi-final matchups remain unchanged
    assert bracket.get_matchup(round_index=0, matchup_index=0).match.score == (15, 7)
    assert bracket.get_matchup(round_index=0, matchup_index=1).match.score == (13, 15)

def test_de_bracket_replace_third_place_match_with_score_invalid_atomicity(semi_final_filled_top_4_bracket_with_third_place_matchup):
    bracket = semi_final_filled_top_4_bracket_with_third_place_matchup

    # Record a score for the third-place matchup
    bracket.record_third_place_match_score(score1=9, score2=15)

    # Verify the third-place matchup result
    third_place_matchup = bracket.third_place_matchup
    assert third_place_matchup.is_complete()
    assert third_place_matchup.match.score == (9, 15)
    assert third_place_matchup.match.forfeited_index is None

    # Attempt to replace the third-place matchup result with an invalid score
    with pytest.raises(ValueError):
        bracket.replace_third_place_match_with_score(score1=-5, score2=15)

    # Verify that the third-place matchup result remains unchanged
    assert third_place_matchup.is_complete()
    assert third_place_matchup.match.score == (9, 15)
    assert third_place_matchup.match.forfeited_index is None

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_de_bracket_record_third_place_match_forfeit(semi_final_filled_top_4_bracket_with_third_place_matchup, forfeiting_index):
    bracket = semi_final_filled_top_4_bracket_with_third_place_matchup
    third_place_matchup = bracket.third_place_matchup
    
    bracket.record_third_place_match_forfeit(forfeiting_index)
    assert third_place_matchup.is_complete()
    assert third_place_matchup.match.is_forfeit()
    assert third_place_matchup.match.score == (None, None)
    assert third_place_matchup.match.forfeited_index == forfeiting_index

def test_de_bracket_record_third_place_match_forfeit_invalid_atomicity(semi_final_filled_top_4_bracket_with_third_place_matchup, entry3, entry4):
    bracket = semi_final_filled_top_4_bracket_with_third_place_matchup

    third_place_matchup_entries = (entry3, entry4)
    third_place_matchup = bracket.third_place_matchup

    # Verify the incompleteness of the third-place matchup
    assert third_place_matchup.entries == third_place_matchup_entries
    assert third_place_matchup.is_incomplete()
    assert third_place_matchup.match.entries == third_place_matchup_entries
    assert third_place_matchup.match.score == (None, None)
    assert third_place_matchup.match.forfeited_index is None

    # Attempt to forfeit the third-place match with an invalid index
    with pytest.raises(ValueError):
        bracket.record_third_place_match_forfeit(-1)

    # Reverify the incompleteness of the third-place matchup
    assert third_place_matchup.is_incomplete()
    assert third_place_matchup.entries == third_place_matchup_entries
    assert third_place_matchup.match.score == (None, None)
    assert third_place_matchup.match.forfeited_index is None

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_de_bracket_record_third_place_match_forfeit_invalid_no_entries_present(initial_full_top_4_bracket_with_third_place_matchup, forfeiting_index):
    bracket = initial_full_top_4_bracket_with_third_place_matchup
    third_place_matchup = bracket.third_place_matchup

    # Verify the incompleteness of the third-place matchup
    assert third_place_matchup.is_incomplete()
    assert third_place_matchup.entries == (None, None)
    assert not third_place_matchup.has_match()

    # Attempt to record a forfeit for the third-place matchup when no entries are present
    with pytest.raises(ValueError):
        bracket.record_third_place_match_forfeit(forfeiting_index)

    # Reverify the incompleteness of the third-place matchup
    assert third_place_matchup.is_incomplete()
    assert third_place_matchup.entries == (None, None)
    assert not third_place_matchup.has_match()

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_de_bracket_record_third_place_match_forfeit_invalid_one_entry_present(initial_full_top_4_bracket_with_third_place_matchup, entry2, forfeiting_index):
    bracket = initial_full_top_4_bracket_with_third_place_matchup
    third_place_matchup = bracket.third_place_matchup

    # Record one semi-final matchup
    bracket.record_match_score(round_index=0, matchup_index=1, score1=15, score2=13)

    # Verify that the third-place matchup is incomplete and has one entry
    assert third_place_matchup.is_incomplete()
    assert third_place_matchup.entries == (entry2, None)

    # Attempt to record a forfeit for the third-place matchup when only one entry is present
    with pytest.raises(ValueError):
        bracket.record_third_place_match_forfeit(forfeiting_index)

    # Verify that the third-place matchup state remains unchanged
    assert third_place_matchup.is_incomplete()
    assert third_place_matchup.entries == (entry2, None)

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_de_bracket_third_place_match_forfeit_invalid_result_already_exists(semi_final_filled_top_4_bracket_with_third_place_matchup, forfeiting_index):
    bracket = semi_final_filled_top_4_bracket_with_third_place_matchup
    third_place_matchup = bracket.third_place_matchup

    # Record a score for the third-place matchup
    bracket.record_third_place_match_score(score1=6, score2=15)

    # Verify the third-place matchup result
    assert third_place_matchup.is_complete()
    assert third_place_matchup.match.score == (6, 15)
    assert third_place_matchup.match.forfeited_index is None

    # Attempt to record a forfeit for the third-place matchup when a result already exists
    with pytest.raises(ValueError):
        bracket.record_third_place_match_forfeit(forfeiting_index)

    # Verify that the third-place matchup state remains unchanged
    assert third_place_matchup.is_complete()
    assert third_place_matchup.match.score == (6, 15)
    assert third_place_matchup.match.forfeited_index is None

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_de_bracket_replace_scored_third_place_match_with_forfeit(semi_final_filled_top_4_bracket_with_third_place_matchup, forfeiting_index):
    bracket = semi_final_filled_top_4_bracket_with_third_place_matchup

    # Record a score for the third-place matchup
    bracket.record_third_place_match_score(score1=6, score2=15)

    # Verify the third-place matchup result
    third_place_matchup = bracket.third_place_matchup
    assert third_place_matchup.is_complete()
    assert third_place_matchup.match.score == (6, 15)
    assert third_place_matchup.match.forfeited_index is None

    # Replace the third-place matchup result with a forfeit
    bracket.replace_third_place_match_with_forfeit(forfeiting_index)

    # Verify the updated third-place matchup result
    assert third_place_matchup.is_complete()
    assert third_place_matchup.match.is_forfeit()
    assert third_place_matchup.match.score == (None, None)
    assert third_place_matchup.match.forfeited_index == forfeiting_index

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_de_bracket_replace_forfeited_third_place_match_with_forfeit(semi_final_filled_top_4_bracket_with_third_place_matchup, forfeiting_index):
    bracket = semi_final_filled_top_4_bracket_with_third_place_matchup
    third_place_matchup = bracket.third_place_matchup

    initial_forfeit_index = forfeiting_index
    replacement_forfeit_index = 1 - initial_forfeit_index

    # Record a forfeit for the third-place matchup
    bracket.record_third_place_match_forfeit(initial_forfeit_index)

    # Verify the third-place matchup result
    assert third_place_matchup.is_complete()
    assert third_place_matchup.match.is_forfeit()
    assert third_place_matchup.match.score == (None, None)
    assert third_place_matchup.match.forfeited_index == initial_forfeit_index

    # Replace the third-place matchup result with the other forfeit index
    bracket.replace_third_place_match_with_forfeit(replacement_forfeit_index)

    # Verify the updated third-place matchup result
    assert third_place_matchup.is_complete()
    assert third_place_matchup.match.is_forfeit()
    assert third_place_matchup.match.score == (None, None)
    assert third_place_matchup.match.forfeited_index == replacement_forfeit_index

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_de_bracket_replace_third_place_match_with_forfeit_invalid_atomicity(semi_final_filled_top_4_bracket_with_third_place_matchup, entry3, entry4, forfeiting_index):
    bracket = semi_final_filled_top_4_bracket_with_third_place_matchup

    third_place_matchup_entries = (entry3, entry4)
    third_place_matchup = bracket.third_place_matchup

    # Record a result for the third-place matchup
    bracket.record_third_place_match_forfeit(forfeiting_index)

    # Verify the third-place matchup result
    assert third_place_matchup.is_complete()
    assert third_place_matchup.match.entries == third_place_matchup_entries
    assert third_place_matchup.match.score == (None, None)
    assert third_place_matchup.match.forfeited_index == forfeiting_index

    # Attempt to replace the third-place match with an invalid forfeit index
    with pytest.raises(ValueError):
        bracket.replace_third_place_match_with_forfeit(2)

    # Verify that the original third-place matchup result remains unchanged
    assert third_place_matchup.is_complete()
    assert third_place_matchup.match.entries == third_place_matchup_entries
    assert third_place_matchup.match.score == (None, None)
    assert third_place_matchup.match.forfeited_index == forfeiting_index
