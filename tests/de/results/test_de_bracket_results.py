import pytest

from dataclasses import FrozenInstanceError

import factories

from de.de_bracket_role import DEBracketRole
from de.results.de_bracket_results import DEBracketResults
from de.results.de_entry_result import DEEntryStatus


# --- Constants ---
from constants import TOURNY_ID1
VALID_STAGE_NUMBER1 = 1
VALID_STAGE_NUMBER2 = 2


# --- Initialization and Validation Tests ---
@pytest.mark.parametrize('invalid_bracket', [None, False, True, 0, 1.0, 'bracket', [], (), {}, set(), object()])
def test_de_bracket_results_creation_invalid_bracket(invalid_bracket):
    with pytest.raises(TypeError):
        DEBracketResults(bracket=invalid_bracket)

def test_de_bracket_results_frozen_instance():
    entries = factories.make_entries(n=4, tournament_id=TOURNY_ID1)
    bracket = factories.make_de_bracket_seed_ordered(stage_number=VALID_STAGE_NUMBER1, seed_ordered_entries=entries)
    results = DEBracketResults(bracket)
    original_entry_results = results.entry_results

    with pytest.raises(FrozenInstanceError):
        results.entry_results = ()

    assert results.entry_results is original_entry_results


# --- Standard Bracket Structure Tests ---
@pytest.mark.parametrize('winner_entry_index', [0, 1])
def test_de_bracket_results_two_entry_bracket(winner_entry_index):
    entries = factories.make_entries(n=2, tournament_id=TOURNY_ID1)
    bracket = factories.make_de_bracket_seed_ordered(stage_number=VALID_STAGE_NUMBER1, seed_ordered_entries=entries)

    assert bracket.num_rounds == 1
    assert bracket.is_incomplete()

    initial_results = DEBracketResults(bracket).entry_results

    assert len(initial_results) == 2

    for i in range(2):
        assert initial_results[i].entry == entries[i]
        assert initial_results[i].stage_number == VALID_STAGE_NUMBER1
        assert initial_results[i].bracket_seed == i + 1
        assert initial_results[i].round_reached == 1
        assert initial_results[i].place is None
        assert initial_results[i].status == DEEntryStatus.ACTIVE

    # The only matchup is the final
    score1, score2 = ((15, 12) if winner_entry_index == 0 else (12, 15))
    bracket.record_match_score(round_index=0, matchup_index=0, score1=score1, score2=score2)

    loser_entry_index = 1 - winner_entry_index

    assert bracket.is_complete()
    assert bracket.winner == entries[winner_entry_index]

    final_results = DEBracketResults(bracket).entry_results

    assert len(final_results) == 2

    assert final_results[0].entry == entries[winner_entry_index]
    assert final_results[0].stage_number == VALID_STAGE_NUMBER1
    assert final_results[0].bracket_seed == winner_entry_index + 1
    assert final_results[0].round_reached == 1
    assert final_results[0].place == 1
    assert final_results[0].status == DEEntryStatus.WINNER

    assert final_results[1].entry == entries[loser_entry_index]
    assert final_results[1].stage_number == VALID_STAGE_NUMBER1
    assert final_results[1].bracket_seed == loser_entry_index + 1
    assert final_results[1].round_reached == 1
    assert final_results[1].place == 2
    assert final_results[1].status == DEEntryStatus.ELIMINATED

@pytest.mark.parametrize('stage_number', [VALID_STAGE_NUMBER1, VALID_STAGE_NUMBER2])
def test_de_bracket_results_full_top_4_bracket_main_bracket_expected_outcomes(stage_number):
    entries = factories.make_entries(n=4, tournament_id=TOURNY_ID1)
    bracket = factories.make_de_bracket_seed_ordered(stage_number=stage_number, seed_ordered_entries=entries)

    # Check the results of the bracket in its initial state
    initial_results = DEBracketResults(bracket).entry_results
    assert len(initial_results) == 4

    for i in range(4):
        assert initial_results[i].entry == entries[i]
        assert initial_results[i].stage_number == stage_number
        assert initial_results[i].bracket_seed == i + 1
        assert initial_results[i].round_reached == 1
        assert initial_results[i].place is None
        assert initial_results[i].status == DEEntryStatus.ACTIVE

    # Perform the first semi-final matchup
    bracket.record_match_score(round_index=0, matchup_index=0, score1=15, score2=8)

    # Check the new results
    state1_results = DEBracketResults(bracket).entry_results

    assert len(state1_results) == 4

    assert state1_results[0].entry == entries[0]
    assert state1_results[0].stage_number == stage_number
    assert state1_results[0].bracket_seed == 1
    assert state1_results[0].round_reached == 2
    assert state1_results[0].place is None
    assert state1_results[0].status == DEEntryStatus.ACTIVE

    assert state1_results[1].entry == entries[1]
    assert state1_results[1].stage_number == stage_number
    assert state1_results[1].bracket_seed == 2
    assert state1_results[1].round_reached == 1
    assert state1_results[1].place is None
    assert state1_results[1].status == DEEntryStatus.ACTIVE

    assert state1_results[2].entry == entries[2]
    assert state1_results[2].stage_number == stage_number
    assert state1_results[2].bracket_seed == 3
    assert state1_results[2].round_reached == 1
    assert state1_results[2].place is None
    assert state1_results[2].status == DEEntryStatus.ACTIVE

    assert state1_results[3].entry == entries[3]
    assert state1_results[3].stage_number == stage_number
    assert state1_results[3].bracket_seed == 4
    assert state1_results[3].round_reached == 1
    assert state1_results[3].place is None
    assert state1_results[3].status == DEEntryStatus.ELIMINATED

    # Perform the second semi-final matchup
    bracket.record_forfeit(round_index=0, matchup_index=1, forfeiting_index=0)

    # Validate the new results
    state2_results = DEBracketResults(bracket).entry_results

    assert len(state2_results) == 4

    assert state2_results[0].entry == entries[0]
    assert state2_results[0].stage_number == stage_number
    assert state2_results[0].bracket_seed == 1
    assert state2_results[0].round_reached == 2
    assert state2_results[0].place is None
    assert state2_results[0].status == DEEntryStatus.ACTIVE

    assert state2_results[1].entry == entries[1]
    assert state2_results[1].stage_number == stage_number
    assert state2_results[1].bracket_seed == 2
    assert state2_results[1].round_reached == 2
    assert state2_results[1].place is None
    assert state2_results[1].status == DEEntryStatus.ACTIVE

    assert state2_results[2].entry == entries[2]
    assert state2_results[2].stage_number == stage_number
    assert state2_results[2].bracket_seed == 3
    assert state2_results[2].round_reached == 1
    assert state2_results[2].place == 3
    assert state2_results[2].status == DEEntryStatus.ELIMINATED

    assert state2_results[3].entry == entries[3]
    assert state2_results[3].stage_number == stage_number
    assert state2_results[3].bracket_seed == 4
    assert state2_results[3].round_reached == 1
    assert state2_results[3].place == 4
    assert state2_results[3].status == DEEntryStatus.ELIMINATED

    # Perform the final
    bracket.record_match_score(round_index=1, matchup_index=0, score1=15, score2=14)

    # Validate the new results
    final_results = DEBracketResults(bracket).entry_results

    assert len(final_results) == 4

    assert final_results[0].entry == entries[0]
    assert final_results[0].stage_number == stage_number
    assert final_results[0].bracket_seed == 1
    assert final_results[0].round_reached == 2 # Note: the final position is not a round
    assert final_results[0].place == 1
    assert final_results[0].status == DEEntryStatus.WINNER

    assert final_results[1].entry == entries[1]
    assert final_results[1].stage_number == stage_number
    assert final_results[1].bracket_seed == 2
    assert final_results[1].round_reached == 2
    assert final_results[1].place == 2
    assert final_results[1].status == DEEntryStatus.ELIMINATED

    assert final_results[2].entry == entries[2]
    assert final_results[2].stage_number == stage_number
    assert final_results[2].bracket_seed == 3
    assert final_results[2].round_reached == 1
    assert final_results[2].place == 3
    assert final_results[2].status == DEEntryStatus.ELIMINATED

    assert final_results[3].entry == entries[3]
    assert final_results[3].stage_number == stage_number
    assert final_results[3].bracket_seed == 4
    assert final_results[3].round_reached == 1
    assert final_results[3].place == 4
    assert final_results[3].status == DEEntryStatus.ELIMINATED

    assert bracket.is_complete()
    assert bracket.winner == entries[0]

@pytest.mark.parametrize('bracket_role_type', [DEBracketRole.MAIN, DEBracketRole.CONSOLATION])
def test_de_bracket_results_full_top_4_bracket_unexpected_outcomes(bracket_role_type):
    entries = factories.make_entries(n=4, tournament_id=TOURNY_ID1)
    bracket = factories.make_de_bracket_seed_ordered(
        stage_number=VALID_STAGE_NUMBER1,
        seed_ordered_entries=entries,
        bracket_role=bracket_role_type
    )

    assert bracket.bracket_role == bracket_role_type

    # Record the first semi-final matchup with an unexpected outcome
    bracket.record_match_score(round_index=0, matchup_index=0, score1=14, score2=15)

    # Verify the new results
    state1_results = DEBracketResults(bracket).entry_results

    assert len(state1_results) == 4

    assert state1_results[0].entry == entries[3]
    assert state1_results[0].bracket_seed == 4
    assert state1_results[0].round_reached == 2
    assert state1_results[0].place is None
    assert state1_results[0].status == DEEntryStatus.ACTIVE

    assert state1_results[1].entry == entries[1]
    assert state1_results[1].bracket_seed == 2
    assert state1_results[1].round_reached == 1
    assert state1_results[1].place is None
    assert state1_results[1].status == DEEntryStatus.ACTIVE

    assert state1_results[2].entry == entries[2]
    assert state1_results[2].bracket_seed == 3
    assert state1_results[2].round_reached == 1
    assert state1_results[2].place is None
    assert state1_results[2].status == DEEntryStatus.ACTIVE

    assert state1_results[3].entry == entries[0]
    assert state1_results[3].bracket_seed == 1
    assert state1_results[3].round_reached == 1
    assert state1_results[3].place is None
    assert state1_results[3].status == DEEntryStatus.ELIMINATED

    # Perform the second semi-final matchup with its expected outcome
    bracket.record_match_score(round_index=0, matchup_index=1, score1=10, score2=15)

    # Verify the new results
    state2_results = DEBracketResults(bracket).entry_results

    assert len(state2_results) == 4

    assert state2_results[0].entry == entries[1]
    assert state2_results[0].bracket_seed == 2
    assert state2_results[0].round_reached == 2
    assert state2_results[0].place is None
    assert state2_results[0].status == DEEntryStatus.ACTIVE

    assert state2_results[1].entry == entries[3]
    assert state2_results[1].bracket_seed == 4
    assert state2_results[1].round_reached == 2
    assert state2_results[1].place is None
    assert state2_results[1].status == DEEntryStatus.ACTIVE

    assert state2_results[2].entry == entries[0]
    assert state2_results[2].bracket_seed == 1
    assert state2_results[2].round_reached == 1
    assert state2_results[2].place == 3
    assert state2_results[2].status == DEEntryStatus.ELIMINATED

    assert state2_results[3].entry == entries[2]
    assert state2_results[3].bracket_seed == 3
    assert state2_results[3].round_reached == 1
    assert state2_results[3].place == 4
    assert state2_results[3].status == DEEntryStatus.ELIMINATED

    # Complete the final with an unexpected outcome
    bracket.record_match_score(round_index=1, matchup_index=0, score1=15, score2=14)

    # Verify the final results
    final_results = DEBracketResults(bracket).entry_results

    assert len(final_results) == 4

    assert final_results[0].entry == entries[3]
    assert final_results[0].bracket_seed == 4
    assert final_results[0].round_reached == 2
    assert final_results[0].place == 1
    assert final_results[0].status == DEEntryStatus.WINNER

    assert final_results[1].entry == entries[1]
    assert final_results[1].bracket_seed == 2
    assert final_results[1].round_reached == 2
    assert final_results[1].place == 2
    assert final_results[1].status == DEEntryStatus.ELIMINATED

    assert final_results[2].entry == entries[0]
    assert final_results[2].bracket_seed == 1
    assert final_results[2].round_reached == 1
    assert final_results[2].place == 3
    assert final_results[2].status == DEEntryStatus.ELIMINATED

    assert final_results[3].entry == entries[2]
    assert final_results[3].bracket_seed == 3
    assert final_results[3].round_reached == 1
    assert final_results[3].place == 4
    assert final_results[3].status == DEEntryStatus.ELIMINATED

def test_de_bracket_results_top_8_bracket_with_byes_and_diverse_outcomes():
    entries = factories.make_entries(n=6, tournament_id=TOURNY_ID1)
    bracket = factories.make_de_bracket_seed_ordered(stage_number=VALID_STAGE_NUMBER1, seed_ordered_entries=entries)

    # Verify initial results
    initial_results = DEBracketResults(bracket).entry_results

    assert len(initial_results) == 6

    for i in range(6):
        assert initial_results[i].entry == entries[i]
        assert initial_results[i].bracket_seed == i + 1
        assert initial_results[i].round_reached == (2 if i < 2 else 1)
        assert initial_results[i].place is None
        assert initial_results[i].status == DEEntryStatus.ACTIVE

    # Entry 5 eliminates Entry 4 in Round 1
    bracket.record_match_score(round_index=0, matchup_index=1, score1=15, score2=13)

    # Verify new results
    state1_results = DEBracketResults(bracket).entry_results

    assert len(state1_results) == 6

    assert state1_results[0].entry == entries[0]
    assert state1_results[0].bracket_seed == 1
    assert state1_results[0].round_reached == 2
    assert state1_results[0].place is None
    assert state1_results[0].status == DEEntryStatus.ACTIVE

    assert state1_results[1].entry == entries[1]
    assert state1_results[1].bracket_seed == 2
    assert state1_results[1].round_reached == 2
    assert state1_results[1].place is None
    assert state1_results[1].status == DEEntryStatus.ACTIVE

    assert state1_results[2].entry == entries[4]
    assert state1_results[2].bracket_seed == 5
    assert state1_results[2].round_reached == 2
    assert state1_results[2].place is None
    assert state1_results[2].status == DEEntryStatus.ACTIVE

    assert state1_results[3].entry == entries[2]
    assert state1_results[3].bracket_seed == 3
    assert state1_results[3].round_reached == 1
    assert state1_results[3].place is None
    assert state1_results[3].status == DEEntryStatus.ACTIVE

    assert state1_results[4].entry == entries[5]
    assert state1_results[4].bracket_seed == 6
    assert state1_results[4].round_reached == 1
    assert state1_results[4].place is None
    assert state1_results[4].status == DEEntryStatus.ACTIVE

    assert state1_results[5].entry == entries[3]
    assert state1_results[5].bracket_seed == 4
    assert state1_results[5].round_reached == 1
    assert state1_results[5].place is None
    assert state1_results[5].status == DEEntryStatus.ELIMINATED

    # Entry 5 forfeits against Entry 1 in Round 2
    bracket.record_forfeit(round_index=1, matchup_index=0, forfeiting_index=1)

    # Verify new results
    state2_results = DEBracketResults(bracket).entry_results

    assert len(state2_results) == 6

    assert state2_results[0].entry == entries[0]
    assert state2_results[0].bracket_seed == 1
    assert state2_results[0].round_reached == 3
    assert state2_results[0].place is None
    assert state2_results[0].status == DEEntryStatus.ACTIVE

    assert state2_results[1].entry == entries[1]
    assert state2_results[1].bracket_seed == 2
    assert state2_results[1].round_reached == 2
    assert state2_results[1].place is None
    assert state2_results[1].status == DEEntryStatus.ACTIVE

    assert state2_results[2].entry == entries[4]
    assert state2_results[2].bracket_seed == 5
    assert state2_results[2].round_reached == 2
    assert state2_results[2].place is None
    assert state2_results[2].status == DEEntryStatus.ELIMINATED

    assert state2_results[3].entry == entries[2]
    assert state2_results[3].bracket_seed == 3
    assert state2_results[3].round_reached == 1
    assert state2_results[3].place is None
    assert state2_results[3].status == DEEntryStatus.ACTIVE

    assert state2_results[4].entry == entries[5]
    assert state2_results[4].bracket_seed == 6
    assert state2_results[4].round_reached == 1
    assert state2_results[4].place is None
    assert state2_results[4].status == DEEntryStatus.ACTIVE

    assert state2_results[5].entry == entries[3]
    assert state2_results[5].bracket_seed == 4
    assert state2_results[5].round_reached == 1
    assert state2_results[5].place is None
    assert state2_results[5].status == DEEntryStatus.ELIMINATED

    # Entry 3 forfeits against Entry 6 in Round 1
    bracket.record_forfeit(round_index=0, matchup_index=2, forfeiting_index=0)

    # Verify new results now after the completetion of round 1
    state3_results = DEBracketResults(bracket).entry_results

    assert len(state3_results) == 6

    assert state3_results[0].entry == entries[0]
    assert state3_results[0].bracket_seed == 1
    assert state3_results[0].round_reached == 3
    assert state3_results[0].place is None
    assert state3_results[0].status == DEEntryStatus.ACTIVE

    assert state3_results[1].entry == entries[1]
    assert state3_results[1].bracket_seed == 2
    assert state3_results[1].round_reached == 2
    assert state3_results[1].place is None
    assert state3_results[1].status == DEEntryStatus.ACTIVE

    assert state3_results[2].entry == entries[5]
    assert state3_results[2].bracket_seed == 6
    assert state3_results[2].round_reached == 2
    assert state3_results[2].place is None
    assert state3_results[2].status == DEEntryStatus.ACTIVE

    assert state3_results[3].entry == entries[4]
    assert state3_results[3].bracket_seed == 5
    assert state3_results[3].round_reached == 2
    assert state3_results[3].place is None
    assert state3_results[3].status == DEEntryStatus.ELIMINATED

    assert state3_results[4].entry == entries[2]
    assert state3_results[4].bracket_seed == 3
    assert state3_results[4].round_reached == 1
    assert state3_results[4].place == 5
    assert state3_results[4].status == DEEntryStatus.ELIMINATED

    assert state3_results[5].entry == entries[3]
    assert state3_results[5].bracket_seed == 4
    assert state3_results[5].round_reached == 1
    assert state3_results[5].place == 6
    assert state3_results[5].status == DEEntryStatus.ELIMINATED

    # Entry 6 eliminates Entry 2 in Round 2
    bracket.record_match_score(round_index=1, matchup_index=1, score1=15, score2=2)

    # Verify new results now after the completetion of round 2
    state4_results = DEBracketResults(bracket).entry_results

    assert len(state4_results) == 6

    assert state4_results[0].entry == entries[0]
    assert state4_results[0].bracket_seed == 1
    assert state4_results[0].round_reached == 3
    assert state4_results[0].place is None
    assert state4_results[0].status == DEEntryStatus.ACTIVE

    assert state4_results[1].entry == entries[5]
    assert state4_results[1].bracket_seed == 6
    assert state4_results[1].round_reached == 3
    assert state4_results[1].place is None
    assert state4_results[1].status == DEEntryStatus.ACTIVE

    assert state4_results[2].entry == entries[1]
    assert state4_results[2].bracket_seed == 2
    assert state4_results[2].round_reached == 2
    assert state4_results[2].place == 3
    assert state4_results[2].status == DEEntryStatus.ELIMINATED

    assert state4_results[3].entry == entries[4]
    assert state4_results[3].bracket_seed == 5
    assert state4_results[3].round_reached == 2
    assert state4_results[3].place == 4
    assert state4_results[3].status == DEEntryStatus.ELIMINATED

    assert state4_results[4].entry == entries[2]
    assert state4_results[4].bracket_seed == 3
    assert state4_results[4].round_reached == 1
    assert state4_results[4].place == 5
    assert state4_results[4].status == DEEntryStatus.ELIMINATED

    assert state4_results[5].entry == entries[3]
    assert state4_results[5].bracket_seed == 4
    assert state4_results[5].round_reached == 1
    assert state4_results[5].place == 6
    assert state4_results[5].status == DEEntryStatus.ELIMINATED

    # Entry 6 eliminates Entry 1 in the final
    bracket.record_match_score(round_index=2, matchup_index=0, score1=14, score2=15)

    # Verify final results
    final_results = DEBracketResults(bracket).entry_results

    assert len(final_results) == 6

    assert final_results[0].entry == entries[5]
    assert final_results[0].bracket_seed == 6
    assert final_results[0].round_reached == 3
    assert final_results[0].place == 1
    assert final_results[0].status == DEEntryStatus.WINNER

    assert final_results[1].entry == entries[0]
    assert final_results[1].bracket_seed == 1
    assert final_results[1].round_reached == 3
    assert final_results[1].place == 2
    assert final_results[1].status == DEEntryStatus.ELIMINATED

    assert final_results[2].entry == entries[1]
    assert final_results[2].bracket_seed == 2
    assert final_results[2].round_reached == 2
    assert final_results[2].place == 3
    assert final_results[2].status == DEEntryStatus.ELIMINATED

    assert final_results[3].entry == entries[4]
    assert final_results[3].bracket_seed == 5
    assert final_results[3].round_reached == 2
    assert final_results[3].place == 4
    assert final_results[3].status == DEEntryStatus.ELIMINATED

    assert final_results[4].entry == entries[2]
    assert final_results[4].bracket_seed == 3
    assert final_results[4].round_reached == 1
    assert final_results[4].place == 5
    assert final_results[4].status == DEEntryStatus.ELIMINATED

    assert final_results[5].entry == entries[3]
    assert final_results[5].bracket_seed == 4
    assert final_results[5].round_reached == 1
    assert final_results[5].place == 6
    assert final_results[5].status == DEEntryStatus.ELIMINATED

    assert bracket.is_complete()

def test_de_bracket_results_snapshot_unchanged_after_bracket_progresses():
    entries = factories.make_entries(n=4, tournament_id=TOURNY_ID1)
    bracket = factories.make_de_bracket_seed_ordered(stage_number=VALID_STAGE_NUMBER2, seed_ordered_entries=entries)

    # Create a snapshot of the initial results
    initial_snapshot = DEBracketResults(bracket)

    # Complete the bracket
    bracket.record_match_score(round_index=0, matchup_index=0, score1=10, score2=15)
    bracket.record_match_score(round_index=0, matchup_index=1, score1=9, score2=15)
    bracket.record_match_score(round_index=1, matchup_index=0, score1=15, score2=12)
    assert bracket.is_complete()

    # Create a snapshot of the final results
    final_snapshot = DEBracketResults(bracket)
    final_results = final_snapshot.entry_results
    assert len(final_results) == 4

    assert final_results[0].entry == entries[3]
    assert final_results[0].stage_number == VALID_STAGE_NUMBER2
    assert final_results[0].bracket_seed == 4
    assert final_results[0].round_reached == 2
    assert final_results[0].place == 1
    assert final_results[0].status == DEEntryStatus.WINNER

    assert final_results[1].entry == entries[1]
    assert final_results[1].stage_number == VALID_STAGE_NUMBER2
    assert final_results[1].bracket_seed == 2
    assert final_results[1].round_reached == 2
    assert final_results[1].place == 2
    assert final_results[1].status == DEEntryStatus.ELIMINATED

    assert final_results[2].entry == entries[0]
    assert final_results[2].stage_number == VALID_STAGE_NUMBER2
    assert final_results[2].bracket_seed == 1
    assert final_results[2].round_reached == 1
    assert final_results[2].place == 3
    assert final_results[2].status == DEEntryStatus.ELIMINATED

    assert final_results[3].entry == entries[2]
    assert final_results[3].stage_number == VALID_STAGE_NUMBER2
    assert final_results[3].bracket_seed == 3
    assert final_results[3].round_reached == 1
    assert final_results[3].place == 4
    assert final_results[3].status == DEEntryStatus.ELIMINATED

    # Now check the initial results even after the bracket has been completed
    initial_results = initial_snapshot.entry_results
    assert len(initial_results) == 4

    for i in range(4):
        assert initial_results[i].entry == entries[i]
        assert initial_results[i].stage_number == VALID_STAGE_NUMBER2
        assert initial_results[i].bracket_seed == i + 1
        assert initial_results[i].round_reached == 1
        assert initial_results[i].place is None
        assert initial_results[i].status == DEEntryStatus.ACTIVE


# --- Brackets with Third-place Matchup Tests ---
@pytest.mark.parametrize('bracket_role_type', [DEBracketRole.MAIN, DEBracketRole.CONSOLATION])
@pytest.mark.parametrize('third_place_winner_entry_index', [0, 1])
def test_de_bracket_results_top_4_bracket_with_third_place_matchup(bracket_role_type, third_place_winner_entry_index):
    entries = factories.make_entries(n=4, tournament_id=TOURNY_ID1)
    bracket = factories.make_de_bracket_seed_ordered(
        stage_number=VALID_STAGE_NUMBER1,
        seed_ordered_entries=entries,
        bracket_role=bracket_role_type,
        has_third_place_match=True
    )

    assert bracket.is_incomplete()
    assert bracket.bracket_role == bracket_role_type

    # Record the first semi-final matchup
    bracket.record_match_score(round_index=0, matchup_index=0, score1=15, score2=5)

    # Record the second semi-final matchup
    bracket.record_match_score(round_index=0, matchup_index=1, score1=9, score2=15)

    # Record the final matchup
    bracket.record_match_score(round_index=1, matchup_index=0, score1=15, score2=10)

    # Check the current results before the third-place matchup
    state_results = DEBracketResults(bracket).entry_results

    assert len(state_results) == 4

    assert state_results[0].entry == entries[0]
    assert state_results[0].bracket_seed == 1
    assert state_results[0].round_reached == 2
    assert state_results[0].place == 1
    assert state_results[0].status == DEEntryStatus.WINNER

    assert state_results[1].entry == entries[1]
    assert state_results[1].bracket_seed == 2
    assert state_results[1].round_reached == 2
    assert state_results[1].place == 2
    assert state_results[1].status == DEEntryStatus.ELIMINATED

    assert state_results[2].entry == entries[2]
    assert state_results[2].bracket_seed == 3
    assert state_results[2].round_reached == 1
    assert state_results[2].place is None
    assert state_results[2].status == DEEntryStatus.ELIMINATED

    assert state_results[3].entry == entries[3]
    assert state_results[3].bracket_seed == 4
    assert state_results[3].round_reached == 1
    assert state_results[3].place is None
    assert state_results[3].status == DEEntryStatus.ELIMINATED

    assert bracket.is_incomplete()

    # Record the third-place matchup
    score1, score2 = ((15, 12) if third_place_winner_entry_index == 0 else (12, 15))
    bracket.record_third_place_match_score(score1=score1, score2=score2)

    assert bracket.is_complete()

    # Verify final results
    final_results = DEBracketResults(bracket).entry_results

    assert len(final_results) == 4

    assert final_results[0].entry == entries[0]
    assert final_results[0].bracket_seed == 1
    assert final_results[0].round_reached == 2
    assert final_results[0].place == 1
    assert final_results[0].status == DEEntryStatus.WINNER

    assert final_results[1].entry == entries[1]
    assert final_results[1].bracket_seed == 2
    assert final_results[1].round_reached == 2
    assert final_results[1].place == 2
    assert final_results[1].status == DEEntryStatus.ELIMINATED

    assert final_results[2].entry == entries[(2 if third_place_winner_entry_index == 0 else 3)]
    assert final_results[2].bracket_seed == (3 if third_place_winner_entry_index == 0 else 4)
    assert final_results[2].round_reached == 1
    assert final_results[2].place == 3
    assert final_results[2].status == DEEntryStatus.ELIMINATED

    assert final_results[3].entry == entries[(3 if third_place_winner_entry_index == 0 else 2)]
    assert final_results[3].bracket_seed == (4 if third_place_winner_entry_index == 0 else 3)
    assert final_results[3].round_reached == 1
    assert final_results[3].place == 4
    assert final_results[3].status == DEEntryStatus.ELIMINATED

def test_de_bracket_results_third_place_matchup_completed_before_final():
    entries = factories.make_entries(n=4, tournament_id=TOURNY_ID1)
    bracket = factories.make_de_bracket_seed_ordered(
        stage_number=VALID_STAGE_NUMBER1,
        seed_ordered_entries=entries,
        has_third_place_match=True
    )

    # Entry 1 and Entry 2 advance to the final
    bracket.record_match_score(round_index=0, matchup_index=0, score1=15, score2=5)
    bracket.record_match_score(round_index=0, matchup_index=1, score1=9, score2=15)

    # Entry 4 beats Entry 3 before the final is played
    bracket.record_third_place_match_score(score1=12, score2=15)

    assert bracket.third_place_matchup.is_complete()
    assert bracket.is_incomplete()

    state_results = DEBracketResults(bracket).entry_results

    assert len(state_results) == 4

    # Finalists remain active with no confirmed places
    for i in range(2):
        assert state_results[i].entry == entries[i]
        assert state_results[i].stage_number == VALID_STAGE_NUMBER1
        assert state_results[i].bracket_seed == i + 1
        assert state_results[i].round_reached == 2
        assert state_results[i].place is None
        assert state_results[i].status == DEEntryStatus.ACTIVE

    # Third and fourth places are already confirmed
    assert state_results[2].entry == entries[3]
    assert state_results[2].stage_number == VALID_STAGE_NUMBER1
    assert state_results[2].bracket_seed == 4
    assert state_results[2].round_reached == 1
    assert state_results[2].place == 3
    assert state_results[2].status == DEEntryStatus.ELIMINATED

    assert state_results[3].entry == entries[2]
    assert state_results[3].stage_number == VALID_STAGE_NUMBER1
    assert state_results[3].bracket_seed == 3
    assert state_results[3].round_reached == 1
    assert state_results[3].place == 4
    assert state_results[3].status == DEEntryStatus.ELIMINATED

    # Entry 2 beats Entry 1 in the final
    bracket.record_match_score(round_index=1, matchup_index=0, score1=10, score2=15)

    assert bracket.is_complete()
    assert bracket.winner == entries[1]

    final_results = DEBracketResults(bracket).entry_results

    assert len(final_results) == 4

    assert final_results[0].entry == entries[1]
    assert final_results[0].stage_number == VALID_STAGE_NUMBER1
    assert final_results[0].bracket_seed == 2
    assert final_results[0].round_reached == 2
    assert final_results[0].place == 1
    assert final_results[0].status == DEEntryStatus.WINNER

    assert final_results[1].entry == entries[0]
    assert final_results[1].stage_number == VALID_STAGE_NUMBER1
    assert final_results[1].bracket_seed == 1
    assert final_results[1].round_reached == 2
    assert final_results[1].place == 2
    assert final_results[1].status == DEEntryStatus.ELIMINATED

    assert final_results[2:] == state_results[2:]


# --- Stopped Bracket Tests ---
def test_de_bracket_results_top_8_stopped_bracket():
    entries = factories.make_entries(n=7, tournament_id=TOURNY_ID1)
    bracket = factories.make_de_bracket_seed_ordered(
        stage_number=VALID_STAGE_NUMBER1,
        seed_ordered_entries=entries,
        stop_at_round=2
    )

    # Stopped bracket checks
    assert bracket.has_stop_round()
    assert bracket.stop_at_round == 2
    assert bracket.num_rounds == 3
    assert bracket.playable_rounds == (bracket.rounds[0], )
    assert len(bracket.playable_rounds) == 1
    
    assert bracket.is_incomplete()
    assert bracket.current_round_index == 0
    assert bracket.num_qualified_entries == 1
    assert bracket.qualified_entries == (entries[0], )
    
    # Entry 4 beats Entry 5 in Round 1
    bracket.record_match_score(round_index=0, matchup_index=1, score1=10, score2=15)

    # Check new results
    assert bracket.is_incomplete()
    assert bracket.current_round_index == 0
    assert bracket.num_qualified_entries == 2
    assert bracket.qualified_entries == (entries[0], entries[3])

    state1_results = DEBracketResults(bracket).entry_results

    assert len(state1_results) == 7

    assert state1_results[0].entry == entries[0]
    assert state1_results[0].bracket_seed == 1
    assert state1_results[0].round_reached == 2
    assert state1_results[0].place is None
    assert state1_results[0].status == DEEntryStatus.ACTIVE

    assert state1_results[1].entry == entries[3]
    assert state1_results[1].bracket_seed == 4
    assert state1_results[1].round_reached == 2
    assert state1_results[1].place is None
    assert state1_results[1].status == DEEntryStatus.ACTIVE

    assert state1_results[2].entry == entries[1]
    assert state1_results[2].bracket_seed == 2
    assert state1_results[2].round_reached == 1
    assert state1_results[2].place is None
    assert state1_results[2].status == DEEntryStatus.ACTIVE

    assert state1_results[3].entry == entries[2]
    assert state1_results[3].bracket_seed == 3
    assert state1_results[3].round_reached == 1
    assert state1_results[3].place is None
    assert state1_results[3].status == DEEntryStatus.ACTIVE

    assert state1_results[4].entry == entries[5]
    assert state1_results[4].bracket_seed == 6
    assert state1_results[4].round_reached == 1
    assert state1_results[4].place is None
    assert state1_results[4].status == DEEntryStatus.ACTIVE

    assert state1_results[5].entry == entries[6]
    assert state1_results[5].bracket_seed == 7
    assert state1_results[5].round_reached == 1
    assert state1_results[5].place is None
    assert state1_results[5].status == DEEntryStatus.ACTIVE

    assert state1_results[6].entry == entries[4]
    assert state1_results[6].bracket_seed == 5
    assert state1_results[6].round_reached == 1
    assert state1_results[6].place is None
    assert state1_results[6].status == DEEntryStatus.ELIMINATED

    # Entry 3 beats Entry 6 in Round 1
    bracket.record_match_score(round_index=0, matchup_index=2, score1=15, score2=5)

    # Check new results
    assert bracket.is_incomplete()
    assert bracket.current_round_index == 0
    assert bracket.num_qualified_entries == 3
    assert bracket.qualified_entries == (entries[0], entries[3], entries[2])
    
    state2_results = DEBracketResults(bracket).entry_results

    assert len(state2_results) == 7

    assert state2_results[0].entry == entries[0]
    assert state2_results[0].bracket_seed == 1
    assert state2_results[0].round_reached == 2
    assert state2_results[0].place is None
    assert state2_results[0].status == DEEntryStatus.ACTIVE

    assert state2_results[1].entry == entries[2]
    assert state2_results[1].bracket_seed == 3
    assert state2_results[1].round_reached == 2
    assert state2_results[1].place is None
    assert state2_results[1].status == DEEntryStatus.ACTIVE

    assert state2_results[2].entry == entries[3]
    assert state2_results[2].bracket_seed == 4
    assert state2_results[2].round_reached == 2
    assert state2_results[2].place is None
    assert state2_results[2].status == DEEntryStatus.ACTIVE

    assert state2_results[3].entry == entries[1]
    assert state2_results[3].bracket_seed == 2
    assert state2_results[3].round_reached == 1
    assert state2_results[3].place is None
    assert state2_results[3].status == DEEntryStatus.ACTIVE

    assert state2_results[4].entry == entries[6]
    assert state2_results[4].bracket_seed == 7
    assert state2_results[4].round_reached == 1
    assert state2_results[4].place is None
    assert state2_results[4].status == DEEntryStatus.ACTIVE

    assert state2_results[5].entry == entries[4]
    assert state2_results[5].bracket_seed == 5
    assert state2_results[5].round_reached == 1
    assert state2_results[5].place is None
    assert state2_results[5].status == DEEntryStatus.ELIMINATED

    assert state2_results[6].entry == entries[5]
    assert state2_results[6].bracket_seed == 6
    assert state2_results[6].round_reached == 1
    assert state2_results[6].place is None
    assert state2_results[6].status == DEEntryStatus.ELIMINATED

    # Entry 2 beats Entry 7 in Round 1
    bracket.record_match_score(round_index=0, matchup_index=3, score1=6, score2=15)

    assert bracket.is_complete()
    assert bracket.current_round_index is None
    assert bracket.num_qualified_entries == 4
    assert bracket.qualified_entries == (entries[0], entries[3], entries[2], entries[1])

    # Check new results
    state3_results = DEBracketResults(bracket).entry_results

    assert len(state3_results) == 7

    assert state3_results[0].entry == entries[0]
    assert state3_results[0].bracket_seed == 1
    assert state3_results[0].round_reached == 2
    assert state3_results[0].place is None
    assert state3_results[0].status == DEEntryStatus.ACTIVE

    assert state3_results[1].entry == entries[1]
    assert state3_results[1].bracket_seed == 2
    assert state3_results[1].round_reached == 2
    assert state3_results[1].place is None
    assert state3_results[1].status == DEEntryStatus.ACTIVE

    assert state3_results[2].entry == entries[2]
    assert state3_results[2].bracket_seed == 3
    assert state3_results[2].round_reached == 2
    assert state3_results[2].place is None
    assert state3_results[2].status == DEEntryStatus.ACTIVE

    assert state3_results[3].entry == entries[3]
    assert state3_results[3].bracket_seed == 4
    assert state3_results[3].round_reached == 2
    assert state3_results[3].place is None
    assert state3_results[3].status == DEEntryStatus.ACTIVE

    assert state3_results[4].entry == entries[4]
    assert state3_results[4].bracket_seed == 5
    assert state3_results[4].round_reached == 1
    assert state3_results[4].place == 5
    assert state3_results[4].status == DEEntryStatus.ELIMINATED

    assert state3_results[5].entry == entries[5]
    assert state3_results[5].bracket_seed == 6
    assert state3_results[5].round_reached == 1
    assert state3_results[5].place == 6
    assert state3_results[5].status == DEEntryStatus.ELIMINATED

    assert state3_results[6].entry == entries[6]
    assert state3_results[6].bracket_seed == 7
    assert state3_results[6].round_reached == 1
    assert state3_results[6].place == 7
    assert state3_results[6].status == DEEntryStatus.ELIMINATED
