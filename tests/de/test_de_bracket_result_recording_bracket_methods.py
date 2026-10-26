import pytest

import factories


# --- Constants ---
from constants import TOURNY_ID1

VALID_STAGE_NUMBER1 = 1


# --- Fixtures ---
@pytest.fixture
def initial_full_top_4_bracket():
    return factories.make_de_bracket_from_defaults(
        num_entries=4,
        tournament_id=TOURNY_ID1,
        stage_number=VALID_STAGE_NUMBER1
    )

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

@pytest.fixture
def initial_full_top_8_bracket():
    return factories.make_de_bracket_from_defaults(
        num_entries=8,
        tournament_id=TOURNY_ID1,
        stage_number=VALID_STAGE_NUMBER1
    )

@pytest.fixture
def initial_top_8_bracket_with_six_entries():
    return factories.make_de_bracket_from_defaults(
        num_entries=6,
        tournament_id=TOURNY_ID1,
        stage_number=VALID_STAGE_NUMBER1
    )

@pytest.fixture
def initial_full_top_8_bracket_with_stop_round():
    return factories.make_de_bracket_from_defaults(
        num_entries=8,
        tournament_id=TOURNY_ID1,
        stage_number=VALID_STAGE_NUMBER1,
        stop_at_round=2
    )


# --- Result Reset Method Tests ---
def test_de_bracket_reset_scored_match_result(initial_full_top_4_bracket, entry1, entry4):
    bracket = initial_full_top_4_bracket

    # Check initial match state
    match = bracket.get_match(round_index=0, matchup_index=0)

    assert match.score == (None, None)
    assert match.is_incomplete()
    assert match.entries == (entry1, entry4)

    # Check next matchup state
    next_matchup = bracket.get_matchup(round_index=1, matchup_index=0)

    assert next_matchup.entries == (None, None)
    assert not next_matchup.has_match()

    # Record a score for the match
    bracket.record_match_score(round_index=0, matchup_index=0, score1=15, score2=13)

    # Verify new match score
    assert match.score == (15, 13)
    assert match.is_complete()
    assert match.entries == (entry1, entry4)

    # Verify that the winner has advanced to the next matchup
    assert next_matchup.entries == (entry1, None)
    assert not next_matchup.has_match()

    # Reset the match result
    bracket.reset_match_result(round_index=0, matchup_index=0)

    # Verify that the match score has been reset
    assert bracket.get_match(round_index=0, matchup_index=0).score == (None, None)
    assert match.is_incomplete()
    assert match.entries == (entry1, entry4)

    # Verify that the advanced entry has been removed from the next matchup
    assert next_matchup.entries == (None, None)
    assert not next_matchup.has_match()

def test_de_bracket_reset_forfeited_match_result(initial_full_top_4_bracket, entry2, entry3):
    bracket = initial_full_top_4_bracket

    # Check initial match state
    match = bracket.get_match(round_index=0, matchup_index=1)

    assert match.entries == (entry3, entry2)
    assert match.score == (None, None)
    assert match.is_incomplete()
    assert match.forfeited_index is None

    # Check next matchup state
    next_matchup = bracket.get_matchup(round_index=1, matchup_index=0)

    assert next_matchup.entries == (None, None)
    assert not next_matchup.has_match()

    # Record a forfeit for the match
    forfeiting_index = 1
    bracket.record_forfeit(round_index=0, matchup_index=1, forfeiting_index=forfeiting_index)

    # Verify that the match is now complete
    assert match.entries == (entry3, entry2)
    assert match.score == (None, None)
    assert match.forfeited_index == forfeiting_index
    assert match.is_forfeit()
    assert match.is_complete()
    
    # Verify that the winner has advanced to the next matchup
    assert next_matchup.entries == (None, entry3)
    assert not next_matchup.has_match()

    # Reset the match result
    bracket.reset_match_result(round_index=0, matchup_index=1)

    # Verify that the forfeit has been reset
    assert match.entries == (entry3, entry2)
    assert match.score == (None, None)
    assert match.forfeited_index is None
    assert match.is_incomplete()

    # Verify that the advanced entry has been removed from the next matchup
    assert next_matchup.entries == (None, None)
    assert not next_matchup.has_match()

def test_de_bracket_reset_final_matchup(initial_full_top_4_bracket):
    bracket = initial_full_top_4_bracket
    final_matchup = bracket.get_matchup(round_index=1, matchup_index=0)

    # Record results for both semi-final matchups
    bracket.record_match_score(round_index=0, matchup_index=0, score1=15, score2=9)
    bracket.record_match_score(round_index=0, matchup_index=1, score1=15, score2=12)

    # Record a result for the final matchup
    bracket.record_match_score(round_index=1, matchup_index=0, score1=15, score2=14)

    # Reset the final matchup
    bracket.reset_match_result(round_index=1, matchup_index=0)

    # Verify that the final matchup has been reset
    assert final_matchup.is_incomplete()
    assert final_matchup.has_match()
    assert final_matchup.match.score == (None, None)
    assert final_matchup.match.forfeited_index is None

@pytest.mark.parametrize('semi_final_index', [0, 1])
def test_de_bracket_reset_match_result_semi_final_matchup_with_third_place_match_enabled(initial_full_top_4_bracket_with_third_place_matchup, entry1, entry2, entry3, entry4, semi_final_index):
    bracket = initial_full_top_4_bracket_with_third_place_matchup
    semi_final = bracket.get_matchup(round_index=0, matchup_index=semi_final_index)
    third_place_match = bracket.third_place_matchup
    final_matchup = bracket.get_matchup(round_index=1, matchup_index=0)

    # Record results for both semi-final matchups
    bracket.record_match_score(round_index=0, matchup_index=0, score1=15, score2=7)
    bracket.record_match_score(round_index=0, matchup_index=1, score1=13, score2=15)

    # Save the losing entries
    third_place_entries = (entry3, entry4)

    # Verify that the third-place matchup contains both entries and a match
    assert third_place_match.entries == third_place_entries
    assert third_place_match.has_match()
    assert third_place_match.is_incomplete()

    # Verify that the final matchup contains the winners and a match
    assert final_matchup.entries == (entry1, entry2)
    assert final_matchup.has_match()
    assert final_matchup.is_incomplete()

    # Reset the first semi-final matchup
    bracket.reset_match_result(round_index=0, matchup_index=semi_final_index)

    # Verify that the semi-final matchup has been reset
    assert semi_final.is_incomplete()
    assert semi_final.has_match()
    assert semi_final.match.score == (None, None)
    assert semi_final.match.forfeited_index is None

    # Verify that the correct entry has been removed from the third-place matchup
    assert third_place_match.entries == ((entry3, None) if semi_final_index == 0 else (None, entry4))
    assert not third_place_match.has_match()
    assert third_place_match.is_incomplete()

    # Verify that entry1 has been removed from the final matchup
    assert final_matchup.entries == ((None, entry2) if semi_final_index == 0 else (entry1, None))
    assert not final_matchup.has_match()
    assert final_matchup.is_incomplete()

def test_de_bracket_reset_match_result_invalid_cannot_reset_a_bye(initial_top_8_bracket_with_six_entries, entry1):
    bracket = initial_top_8_bracket_with_six_entries

    # Record one result first to start the bracket
    bracket.record_match_score(round_index=0, matchup_index=1, score1=11, score2=15)

    # Attempt to reset a bye matchup
    with pytest.raises(ValueError):
        bracket.reset_match_result(round_index=0, matchup_index=0)

    # Verify that the BYE matchup is still a BYE
    bye_matchup = bracket.get_matchup(round_index=0, matchup_index=0)
    assert bye_matchup.entries == (entry1, None)
    assert not bye_matchup.has_match()
    assert bye_matchup.is_bye()

def test_de_bracket_reset_match_result_invalid_cannot_reset_when_next_matchup_is_recorded(initial_full_top_8_bracket):
    bracket = initial_full_top_8_bracket

    # Record a result for the first matchup in round 1
    bracket.record_match_score(round_index=0, matchup_index=0, score1=15, score2=10)

    # Record a result for the second matchup in round 1
    bracket.record_match_score(round_index=0, matchup_index=1, score1=11, score2=15)

    # Record a result for the proceeding matchup in round 2
    bracket.record_match_score(round_index=1, matchup_index=0, score1=15, score2=9)

    # Attempt to reset the first matchup
    with pytest.raises(ValueError):
        bracket.reset_match_result(round_index=0, matchup_index=0)

    # Verify that all the match results are still present
    assert bracket.get_matchup(round_index=0, matchup_index=0).match.score == (15, 10)
    assert bracket.get_matchup(round_index=0, matchup_index=0).match.is_complete()
    assert bracket.get_matchup(round_index=0, matchup_index=0).match.forfeited_index is None

    assert bracket.get_matchup(round_index=0, matchup_index=1).match.score == (11, 15)
    assert bracket.get_matchup(round_index=0, matchup_index=1).match.is_complete()
    assert bracket.get_matchup(round_index=0, matchup_index=1).match.forfeited_index is None

    assert bracket.get_matchup(round_index=1, matchup_index=0).match.score == (15, 9)
    assert bracket.get_matchup(round_index=1, matchup_index=0).match.is_complete()
    assert bracket.get_matchup(round_index=1, matchup_index=0).match.forfeited_index is None

def test_de_bracket_reset_match_result_invalid_cannot_reset_semi_final_match_when_third_place_match_is_recorded():
    bracket = factories.make_de_bracket_from_defaults(
        num_entries=4,
        tournament_id=TOURNY_ID1,
        stage_number=VALID_STAGE_NUMBER1,
        has_third_place_match=True
    )

    # Record results for both semi-final matchups
    bracket.record_match_score(round_index=0, matchup_index=0, score1=6, score2=15)
    bracket.record_match_score(round_index=0, matchup_index=1, score1=15, score2=8)

    # Record a result for the third-place matchup
    bracket.record_third_place_match_score(score1=15, score2=14)

    # Attempt to reset the first semi-final matchup
    with pytest.raises(ValueError):
        bracket.reset_match_result(round_index=0, matchup_index=0)

    # Attempt to reset the second semi-final matchup
    with pytest.raises(ValueError):
        bracket.reset_match_result(round_index=0, matchup_index=1)

def test_de_bracket_reset_match_result_invalid_no_result_to_reset(initial_full_top_4_bracket):
    with pytest.raises(ValueError):
        initial_full_top_4_bracket.reset_match_result(round_index=0, matchup_index=0)


# --- Record Match Score Tests ---
@pytest.mark.parametrize(('index', 'score1', 'score2'), [(0, 10, 15), (1, 15, 8), (2, 5, 15), (3, 4, 15)])
def test_de_bracket_record_match_score(initial_full_top_8_bracket, index, score1, score2):
    bracket = initial_full_top_8_bracket
    
    # Record the score and verify the results
    bracket.record_match_score(round_index=0, matchup_index=index, score1=score1, score2=score2)

    matchup = bracket.get_matchup(round_index=0, matchup_index=index)

    assert matchup.match.score == (score1, score2)
    assert matchup.match.is_complete()
    assert matchup.match.forfeited_index is None
    assert matchup.is_complete()

    # Verify that the winner has advanced to the next matchup
    next_matchup = bracket.get_matchup(round_index=1, matchup_index=index // 2)

    assert next_matchup.entries[index % 2] == matchup.winner
    assert next_matchup.is_incomplete()

def test_de_bracket_record_match_score_invalid_bye_matchup(initial_top_8_bracket_with_six_entries, entry1):
    bracket = initial_top_8_bracket_with_six_entries
    bye_matchup = bracket.get_matchup(round_index=0, matchup_index=0)

    # Attempt to record a score for a BYE matchup
    with pytest.raises(ValueError):
        bracket.record_match_score(round_index=0, matchup_index=0, score1=15, score2=10)

    # Verify that the BYE matchup is still a BYE
    assert bye_matchup.entries == (entry1, None)
    assert bye_matchup.is_bye()

def test_de_bracket_record_match_score_invalid_missing_an_entry(initial_full_top_8_bracket):
    bracket = initial_full_top_8_bracket

    # Record first matchup result
    bracket.record_match_score(round_index=0, matchup_index=0, score1=15, score2=10)

    # Attempt to record a score for the next matchup in the subsequent round
    with pytest.raises(ValueError):
        bracket.record_match_score(round_index=1, matchup_index=0, score1=15, score2=12)

def test_de_bracket_record_match_score_invalid_result_already_recorded(initial_full_top_8_bracket):
    bracket = initial_full_top_8_bracket

    # Record first matchup result
    bracket.record_match_score(round_index=0, matchup_index=0, score1=5, score2=15)

    # Attempt to record a score for the same matchup again
    with pytest.raises(ValueError):
        bracket.record_match_score(round_index=0, matchup_index=0, score1=14, score2=15)

def test_de_bracket_record_match_score_invalid_recording_in_stopping_round_of_stopped_bracket(initial_full_top_8_bracket_with_stop_round):
    bracket = initial_full_top_8_bracket_with_stop_round

    # Record first and second matchup results in round 1
    bracket.record_match_score(round_index=0, matchup_index=0, score1=11, score2=15)
    bracket.record_match_score(round_index=0, matchup_index=1, score1=15, score2=12)

    next_matchup = bracket.get_matchup(round_index=1, matchup_index=0)
    assert next_matchup.has_both_entries()
    assert next_matchup.is_incomplete()
    assert next_matchup.has_match()

    # Attempt to record a score for a matchup in the stopping round (round 2)
    with pytest.raises(ValueError):
        bracket.record_match_score(round_index=1, matchup_index=0, score1=8, score2=15)

def test_de_bracket_record_match_score_invalid_atomicity(initial_full_top_4_bracket):
    bracket = initial_full_top_4_bracket

    matchup = bracket.get_matchup(round_index=0, matchup_index=0)

    # Check initial state of the matchup
    assert matchup.match.score == (None, None)
    assert matchup.match.forfeited_index is None
    assert matchup.is_incomplete()

    # Attempt to record an invalid score
    with pytest.raises(ValueError):
        bracket.record_match_score(round_index=0, matchup_index=0, score1=15, score2=-5)

    # Verify that the matchup state has not changed
    assert matchup.match.score == (None, None)
    assert matchup.match.forfeited_index is None
    assert matchup.is_incomplete()


# --- Replace With Score Tests ---
def test_de_bracket_replace_with_score_scored_match(initial_full_top_8_bracket, entry1):
    bracket = initial_full_top_8_bracket

    matchup = bracket.get_matchup(round_index=0, matchup_index=0)

    # Record an initial score
    bracket.record_match_score(round_index=0, matchup_index=0, score1=10, score2=15)

    assert matchup.is_complete()
    assert matchup.match.score == (10, 15)
    assert matchup.match.forfeited_index is None

    # Replace the score with a new valid score
    bracket.replace_with_score(round_index=0, matchup_index=0, score1=15, score2=11)

    assert matchup.is_complete()
    assert matchup.match.score == (15, 11)
    assert matchup.match.forfeited_index is None

    # Verify that the winner has advanced to the next matchup
    next_matchup = bracket.get_matchup(round_index=1, matchup_index=0)

    assert next_matchup.entries == (entry1, None)
    assert next_matchup.is_incomplete()
    assert not next_matchup.has_match()

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_de_bracket_replace_with_score_forfeited_match(initial_full_top_8_bracket, forfeiting_index, entry3, entry6):
    bracket = initial_full_top_8_bracket

    matchup = bracket.get_matchup(round_index=0, matchup_index=2)
    dest = bracket.get_matchup(round_index=1, matchup_index=1)

    # Record an initial forfeit
    bracket.record_forfeit(round_index=0, matchup_index=2, forfeiting_index=forfeiting_index)

    # Validate the matchup's state after recording the forfeit
    assert matchup.is_complete()
    assert matchup.match.score == (None, None)
    assert matchup.match.forfeited_index == forfeiting_index

    # Validate that the winner progressed to the next matchup
    assert dest.entries == ((entry3, None) if forfeiting_index == 1 else (entry6, None))

    # Replace the forfeit with a new valid score
    bracket.replace_with_score(round_index=0, matchup_index=2, score1=15, score2=9)

    # Validate the matchup's state after replacing the forfeit with a score
    assert matchup.is_complete()
    assert matchup.match.score == (15, 9)
    assert matchup.match.forfeited_index is None

    # Check that the winner of the scored matchup has advanced to the next matchup
    assert dest.entries == (entry3, None)

def test_de_bracket_replace_with_score_final_matchup(initial_full_top_4_bracket):
    bracket = initial_full_top_4_bracket

    # Record both semi-final match results
    bracket.record_match_score(round_index=0, matchup_index=0, score1=12, score2=15)
    bracket.record_match_score(round_index=0, matchup_index=1, score1=1, score2=15)

    final_matchup = bracket.get_matchup(round_index=1, matchup_index=0)

    # Record the final match result
    bracket.record_match_score(round_index=1, matchup_index=0, score1=3, score2=15)

    # Replace the final match result with a new valid score
    bracket.replace_with_score(round_index=1, matchup_index=0, score1=13, score2=15)

    # Validate the final matchup's state after replacing the score
    assert final_matchup.is_complete()
    assert final_matchup.match.score == (13, 15)
    assert final_matchup.match.forfeited_index is None

@pytest.mark.parametrize('semi_final_index', [0, 1])
def test_de_bracket_replace_with_score_replace_semi_final_matchup_with_third_place_match_enabled(semi_final_filled_top_4_bracket_with_third_place_matchup, semi_final_index, entry1, entry2, entry3, entry4):
    bracket = semi_final_filled_top_4_bracket_with_third_place_matchup
    semi_final_matchup = bracket.get_matchup(round_index=0, matchup_index=semi_final_index)
    third_place_matchup = bracket.third_place_matchup
    final_matchup = bracket.get_matchup(round_index=1, matchup_index=0)

    # Verify the semi-final's result
    assert semi_final_matchup.is_complete()
    assert semi_final_matchup.match.score == ((15, 7) if semi_final_index == 0 else (13, 15))
    assert semi_final_matchup.match.forfeited_index is None

    # Verify the final has the winners
    assert final_matchup.entries == (entry1, entry2)
    assert final_matchup.is_incomplete()
    assert final_matchup.has_match()

    # Verify the third-place matchup has the losers
    assert third_place_matchup.entries == (entry3, entry4)
    assert third_place_matchup.is_incomplete()
    assert third_place_matchup.has_match()

    # Replace the semi-final score so that the other entry wins
    score1, score2 = (9, 15) if semi_final_index == 0 else (15, 11)
    bracket.replace_with_score(round_index=0, matchup_index=semi_final_index, score1=score1, score2=score2)

    # Verify that the semi-final matchup has the new score
    assert semi_final_matchup.is_complete()
    assert semi_final_matchup.match.score == (score1, score2)
    assert semi_final_matchup.match.forfeited_index is None

    # Verify that the final matchup has been updated with the new winner
    assert final_matchup.entries == ((entry4, entry2) if semi_final_index == 0 else (entry1, entry3))
    assert final_matchup.is_incomplete()
    assert final_matchup.has_match()

    # Verify that the third-place matchup has been updated with the new loser
    assert third_place_matchup.entries == ((entry3, entry1) if semi_final_index == 0 else (entry2, entry4))
    assert third_place_matchup.is_incomplete()
    assert third_place_matchup.has_match()

def test_de_bracket_replace_with_score_invalid_next_matchup_already_recorded(initial_full_top_8_bracket):
    bracket = initial_full_top_8_bracket

    # Record first two matchups in the top 8
    bracket.record_match_score(round_index=0, matchup_index=0, score1=9, score2=15)
    bracket.record_match_score(round_index=0, matchup_index=1, score1=7, score2=15)

    # Record the first matchup in the top 4
    bracket.record_match_score(round_index=1, matchup_index=0, score1=15, score2=12)
    
    # Attempt to replace the first quarter-final result
    with pytest.raises(ValueError):
        bracket.replace_with_score(round_index=0, matchup_index=0, score1=14, score2=15)

def test_de_bracket_replace_with_score_invalid_third_place_matchup_already_recorded(initial_full_top_4_bracket_with_third_place_matchup):
    bracket = initial_full_top_4_bracket_with_third_place_matchup

    # Record both semi-final match results
    bracket.record_match_score(round_index=0, matchup_index=0, score1=12, score2=15)
    bracket.record_match_score(round_index=0, matchup_index=1, score1=15, score2=11)

    # Record the third-place match result
    bracket.record_third_place_match_score(score1=15, score2=6)

    # Attempt to replace the first semi-final result
    with pytest.raises(ValueError):
        bracket.replace_with_score(round_index=0, matchup_index=0, score1=12, score2=15)

def test_de_bracket_replace_with_score_invalid_no_result_to_replace(initial_full_top_4_bracket):
    bracket = initial_full_top_4_bracket

    # Attempt to replace a match result that has not been recorded yet
    with pytest.raises(ValueError):
        bracket.replace_with_score(round_index=0, matchup_index=0, score1=15, score2=10)

def test_de_bracket_replace_with_score_invalid_input_preserves_state(initial_full_top_4_bracket):
    bracket = initial_full_top_4_bracket

    # Record both semi-final matchups
    bracket.record_match_score(round_index=0, matchup_index=0, score1=14, score2=15)
    bracket.record_forfeit(round_index=0, matchup_index=1, forfeiting_index=0)

    # Store matchup states
    semi_final = bracket.get_matchup(round_index=0, matchup_index=0)
    final = bracket.get_matchup(round_index=1, matchup_index=0)
    original_final_entries = final.entries

    assert final.has_match()
    assert final.is_incomplete()

    # Attempt to replace the first semi-final match with an invalid score
    with pytest.raises(ValueError):
        bracket.replace_with_score(round_index=0, matchup_index=0, score1=-5, score2=15)

    # Verify that the original matchups remain unchanged
    assert semi_final.match.score == (14, 15)
    assert semi_final.match.forfeited_index is None
    assert semi_final.is_complete()

    assert final.entries == original_final_entries
    assert final.has_match()
    assert final.match.score == (None, None)
    assert final.match.forfeited_index is None
    assert final.is_incomplete()

def test_de_bracket_replace_with_score_invalid_next_matchup_complete(initial_full_top_4_bracket):
    bracket = initial_full_top_4_bracket

    # Record both semi-final matchups and the final matchup
    bracket.record_match_score(round_index=0, matchup_index=0, score1=14, score2=15)
    bracket.record_forfeit(round_index=0, matchup_index=1, forfeiting_index=0)
    bracket.record_match_score(round_index=1, matchup_index=0, score1=15, score2=9)

    # Store matchup states
    semi_final = bracket.get_matchup(round_index=0, matchup_index=0)
    final = bracket.get_matchup(round_index=1, matchup_index=0)
    original_final_entries = final.entries

    # Attempt to change a semi-final result after the final has been recorded
    with pytest.raises(ValueError, match="until its next matchup"):
        bracket.replace_with_score(round_index=0, matchup_index=0, score1=15, score2=5)

    # Validate that the semi-final and final matchups remain unchanged
    assert semi_final.match.score == (14, 15)
    assert semi_final.match.forfeited_index is None
    assert semi_final.is_complete()

    assert final.entries == original_final_entries
    assert final.match.score == (15, 9)
    assert final.match.forfeited_index is None
    assert final.is_complete()
    assert bracket.is_complete()


# --- Forfeit Recording Method Tests ---
@pytest.mark.parametrize(('index', 'forfeiting_index'), [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1), (3, 0), (3, 1)])
def test_de_bracket_record_forfeit(initial_full_top_8_bracket, index, forfeiting_index):
    bracket = initial_full_top_8_bracket
    
    # Record the forfeit and verify the results
    bracket.record_forfeit(round_index=0, matchup_index=index, forfeiting_index=forfeiting_index)

    matchup = bracket.get_matchup(round_index=0, matchup_index=index)

    assert matchup.match.score == (None, None)
    assert matchup.match.forfeited_index == forfeiting_index
    assert matchup.match.is_complete()
    assert matchup.is_complete()

    # Verify that the winner has advanced to the next matchup
    next_matchup = bracket.get_matchup(round_index=1, matchup_index=index // 2)

    assert next_matchup.entries[index % 2] == matchup.winner
    assert next_matchup.is_incomplete()

def test_de_bracket_record_forfeit_invalid_atomicity(initial_full_top_4_bracket):
    bracket = initial_full_top_4_bracket

    matchup = bracket.get_matchup(round_index=0, matchup_index=1)

    # Check initial state of the matchup
    assert matchup.is_incomplete()
    assert matchup.match.score == (None, None)
    assert matchup.match.forfeited_index is None

    # Attempt to record an invalid forfeit
    with pytest.raises(ValueError):
        bracket.record_forfeit(round_index=0, matchup_index=1, forfeiting_index=2)

    # Verify that the matchup state has not changed
    assert matchup.is_incomplete()
    assert matchup.match.score == (None, None)
    assert matchup.match.forfeited_index is None

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_de_bracket_record_forfeit_invalid_bye_matchup(initial_top_8_bracket_with_six_entries, entry1, forfeiting_index):
    bracket = initial_top_8_bracket_with_six_entries
    bye_matchup = bracket.get_matchup(round_index=0, matchup_index=0)

    # Attempt to record a forfeit for a BYE matchup
    with pytest.raises(ValueError):
        bracket.record_forfeit(round_index=0, matchup_index=0, forfeiting_index=forfeiting_index)

    # Verify that the BYE matchup is still a BYE
    assert bye_matchup.entries == (entry1, None)
    assert bye_matchup.is_bye()

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_de_bracket_record_forfeit_invalid_missing_an_entry(initial_full_top_8_bracket, forfeiting_index):
    bracket = initial_full_top_8_bracket

    # Record last matchup result
    bracket.record_match_score(round_index=0, matchup_index=3, score1=15, score2=13)

    # Attempt to record a forfeit for the next matchup in the subsequent round
    with pytest.raises(ValueError):
        bracket.record_forfeit(round_index=1, matchup_index=1, forfeiting_index=forfeiting_index)

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_de_bracket_record_forfeit_invalid_result_already_recorded(initial_full_top_8_bracket, forfeiting_index):
    bracket = initial_full_top_8_bracket

    # Record second matchup result
    bracket.record_forfeit(round_index=0, matchup_index=1, forfeiting_index=forfeiting_index)

    # Attempt to record a forfeit for the same matchup again
    with pytest.raises(ValueError):
        bracket.record_forfeit(round_index=0, matchup_index=1, forfeiting_index=forfeiting_index)

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_de_bracket_record_forfeit_invalid_recording_in_stopping_round_of_stopped_bracket(initial_full_top_8_bracket_with_stop_round, forfeiting_index):
    bracket = initial_full_top_8_bracket_with_stop_round

    # Record third and fourth matchup result in round 1
    bracket.record_match_score(round_index=0, matchup_index=2, score1=15, score2=2)
    bracket.record_match_score(round_index=0, matchup_index=3, score1=10, score2=15)

    next_matchup = bracket.get_matchup(round_index=1, matchup_index=1)
    assert next_matchup.has_both_entries()
    assert next_matchup.is_incomplete()
    assert next_matchup.has_match()

    # Attempt to record a forfeit for a matchup in the stopping round (round 2)
    with pytest.raises(ValueError):
        bracket.record_forfeit(round_index=1, matchup_index=1, forfeiting_index=forfeiting_index)


# --- Replace With Forfeit Tests ---
def test_de_bracket_replace_with_forfeit_scored_match(initial_top_8_bracket_with_six_entries, entry6, entry2):
    bracket = initial_top_8_bracket_with_six_entries
    matchup_index = 2
    matchup = bracket.get_matchup(round_index=0, matchup_index=matchup_index)

    # Record an initial score
    bracket.record_match_score(round_index=0, matchup_index=matchup_index, score1=15, score2=8)

    assert matchup.is_complete()
    assert not matchup.match.is_forfeit()
    assert matchup.match.score == (15, 8)
    assert matchup.match.forfeited_index is None

    # Replace the previously scored match with a forfeit
    bracket.replace_with_forfeit(round_index=0, matchup_index=matchup_index, forfeiting_index=0)

    assert matchup.is_complete()
    assert matchup.match.is_forfeit()
    assert matchup.match.score == (None, None)
    assert matchup.match.forfeited_index == 0

    # Verify that the winner has advanced to the next matchup
    next_matchup = bracket.get_matchup(round_index=1, matchup_index=1)
    assert next_matchup.entries == (entry6, entry2)
    assert next_matchup.is_incomplete()
    assert next_matchup.has_match()

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_de_bracket_replace_with_forfeit_forfeited_match(initial_full_top_4_bracket, forfeiting_index, entry3, entry2):
    bracket = initial_full_top_4_bracket
    matchup_index = 1
    matchup = bracket.get_matchup(round_index=0, matchup_index=matchup_index)
    dest = bracket.get_matchup(round_index=1, matchup_index=0)

    # Record an initial forfeit
    bracket.record_forfeit(round_index=0, matchup_index=matchup_index, forfeiting_index=forfeiting_index)

    # Validate the results
    assert matchup.is_complete()
    assert matchup.match.is_forfeit()
    assert matchup.match.score == (None, None)
    assert matchup.match.forfeited_index == forfeiting_index

    # Check that the winner advanced to the next matchup
    assert dest.entries == ((None, entry3) if forfeiting_index == 1 else (None, entry2))

    # Replace the previous forfeit with the opposite forfeit
    bracket.replace_with_forfeit(round_index=0, matchup_index=matchup_index, forfeiting_index = 1 - forfeiting_index)

    # Validate the results after switching the forfeit
    assert matchup.is_complete()
    assert matchup.match.is_forfeit()
    assert matchup.match.score == (None, None)
    assert matchup.match.forfeited_index == 1 - forfeiting_index

    # Check that the new winner has advanced to the next matchup
    assert dest.entries == ((None, entry3) if forfeiting_index == 0 else (None, entry2))

def test_de_bracket_replace_with_forfeit_final_matchup(initial_full_top_4_bracket):
    bracket = initial_full_top_4_bracket
    final_matchup = bracket.get_matchup(round_index=1, matchup_index=0)

    # Record results for both semi-final matchups
    bracket.record_match_score(round_index=0, matchup_index=0, score1=15, score2=9)
    bracket.record_match_score(round_index=0, matchup_index=1, score1=15, score2=12)

    # Record a result for the final matchup
    bracket.record_match_score(round_index=1, matchup_index=0, score1=15, score2=14)

    # Validate that the final matchup result
    assert final_matchup.is_complete()
    assert final_matchup.has_match()
    assert final_matchup.match.score == (15, 14)
    assert final_matchup.match.forfeited_index is None

    # Replace the final matchup result with a forfeit
    bracket.replace_with_forfeit(round_index=1, matchup_index=0, forfeiting_index=1)

    # Verify that the final matchup has been replaced with a forfeit
    assert final_matchup.is_complete()
    assert final_matchup.has_match()
    assert final_matchup.match.score == (None, None)
    assert final_matchup.match.forfeited_index == 1

@pytest.mark.parametrize('semi_final_index', [0, 1])
def test_de_bracket_replace_with_forfeit_replace_semi_final_matchup_with_third_place_match_enabled(semi_final_filled_top_4_bracket_with_third_place_matchup, semi_final_index, entry1, entry2, entry3, entry4):
    bracket = semi_final_filled_top_4_bracket_with_third_place_matchup
    semi_final_matchup = bracket.get_matchup(round_index=0, matchup_index=semi_final_index)
    third_place_matchup = bracket.third_place_matchup
    final_matchup = bracket.get_matchup(round_index=1, matchup_index=0)

    # Verify the semi-final's result
    assert semi_final_matchup.is_complete()
    assert semi_final_matchup.match.score == ((15, 7) if semi_final_index == 0 else (13, 15))
    assert semi_final_matchup.match.forfeited_index is None

    # Verify the final has the winners
    assert final_matchup.entries == (entry1, entry2)
    assert final_matchup.is_incomplete()
    assert final_matchup.has_match()

    # Verify the third-place matchup has its loser
    assert third_place_matchup.entries == (entry3, entry4)
    assert third_place_matchup.is_incomplete()
    assert third_place_matchup.has_match()

    # Replace the semi-final matchup with a forfeit
    forfeiting_index = 0 if semi_final_index == 0 else 1
    bracket.replace_with_forfeit(round_index=0, matchup_index=semi_final_index, forfeiting_index=forfeiting_index)

    # Verify that the semi-final matchup has been replaced with a forfeit
    assert semi_final_matchup.is_complete()
    assert semi_final_matchup.match.score == (None, None)
    assert semi_final_matchup.match.forfeited_index == forfeiting_index

    # Verify that the final matchup has been updated with the new winner
    assert final_matchup.entries == ((entry4, entry2) if semi_final_index == 0 else (entry1, entry3))
    assert final_matchup.is_incomplete()
    assert final_matchup.has_match()

    # Verify that the third-place matchup has been updated with the new loser
    assert third_place_matchup.entries == ((entry3, entry1) if semi_final_index == 0 else (entry2, entry4))
    assert third_place_matchup.is_incomplete()
    assert third_place_matchup.has_match()

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_de_bracket_replace_with_forfeit_invalid_next_matchup_already_recorded(initial_full_top_8_bracket, forfeiting_index):
    bracket = initial_full_top_8_bracket

    # Record third and fourth matchups in the top 8
    bracket.record_match_score(round_index=0, matchup_index=2, score1=15, score2=11)
    bracket.record_match_score(round_index=0, matchup_index=3, score1=14, score2=15)

    # Record the second matchup in the top 4
    bracket.record_match_score(round_index=1, matchup_index=1, score1=15, score2=12)
    
    # Attempt to replace the fourth quarter-final result with a forfeit
    with pytest.raises(ValueError):
        bracket.replace_with_forfeit(round_index=0, matchup_index=3, forfeiting_index=forfeiting_index)

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_de_bracket_replace_with_forfeit_invalid_third_place_matchup_already_recorded(initial_full_top_4_bracket_with_third_place_matchup, forfeiting_index):
    bracket = initial_full_top_4_bracket_with_third_place_matchup

    # Record both semi-final match results
    bracket.record_match_score(round_index=0, matchup_index=0, score1=13, score2=15)
    bracket.record_match_score(round_index=0, matchup_index=1, score1=15, score2=9)

    # Record the third-place match result
    bracket.record_third_place_match_score(score1=8, score2=15)

    # Attempt to replace the second semi-final result with a forfeit
    with pytest.raises(ValueError):
        bracket.replace_with_forfeit(round_index=0, matchup_index=1, forfeiting_index=forfeiting_index)

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_de_bracket_replace_with_forfeit_invalid_no_result_to_replace(initial_full_top_4_bracket, forfeiting_index):
    bracket = initial_full_top_4_bracket

    # Attempt to replace a match result that has not been recorded yet
    with pytest.raises(ValueError):
        bracket.replace_with_forfeit(round_index=0, matchup_index=0, forfeiting_index=forfeiting_index)

def test_de_bracket_replace_with_forfeit_invalid_input_preserves_state(initial_full_top_4_bracket):
    bracket = initial_full_top_4_bracket

    # Record both semi-final match results
    bracket.record_match_score(round_index=0, matchup_index=0, score1=15, score2=12)
    bracket.record_match_score(round_index=0, matchup_index=1, score1=8, score2=15)

    # Store matchup states
    semi_final_1 = bracket.get_matchup(round_index=0, matchup_index=0)
    semi_final_2 = bracket.get_matchup(round_index=0, matchup_index=1)
    final_match = bracket.get_matchup(round_index=1, matchup_index=0)
    original_final_entries = final_match.entries

    # Attempt to replace the first semi-final match with an invalid forfeit index
    with pytest.raises(ValueError):
        bracket.replace_with_forfeit(round_index=0, matchup_index=0, forfeiting_index=-1)

    # Verify that the original matchups remain unchanged
    assert semi_final_1.match.score == (15, 12)
    assert semi_final_1.match.forfeited_index is None
    assert semi_final_1.is_complete()

    assert semi_final_2.match.score == (8, 15)
    assert semi_final_2.match.forfeited_index is None
    assert semi_final_2.is_complete()

    assert final_match.entries == original_final_entries
    assert final_match.match.score == (None, None)
    assert final_match.match.forfeited_index is None
    assert final_match.is_incomplete()

def test_de_bracket_replace_with_forfeit_invalid_next_matchup_complete(initial_full_top_4_bracket):
    bracket = initial_full_top_4_bracket

    # Record both semi-final match results
    bracket.record_match_score(round_index=0, matchup_index=0, score1=15, score2=12)
    bracket.record_match_score(round_index=0, matchup_index=1, score1=8, score2=15)

    # Record the final match result
    bracket.record_match_score(round_index=1, matchup_index=0, score1=15, score2=10)

    # Store matchup states
    semi_final_1 = bracket.get_matchup(round_index=0, matchup_index=0)
    semi_final_2 = bracket.get_matchup(round_index=0, matchup_index=1)
    final_match = bracket.get_matchup(round_index=1, matchup_index=0)
    original_final_entries = final_match.entries

    # Attempt to replace the first semi-final match with a forfeit after the final has been recorded
    with pytest.raises(ValueError):
        bracket.replace_with_forfeit(round_index=0, matchup_index=0, forfeiting_index=1)

    # Validate that the semi-final and final matchups remain unchanged
    assert semi_final_1.match.score == (15, 12)
    assert semi_final_1.match.forfeited_index is None
    assert semi_final_1.is_complete()

    assert semi_final_2.match.score == (8, 15)
    assert semi_final_2.match.forfeited_index is None
    assert semi_final_2.is_complete()

    assert final_match.entries == original_final_entries
    assert final_match.match.score == (15, 10)
    assert final_match.match.forfeited_index is None
    assert final_match.is_complete()
