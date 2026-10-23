import pytest

import factories

from de.de_bracket import DEBracket
from de.de_bracket_role import DEBracketRole
from de.de_round import DERound


# --- Constants ---
from constants import TOURNY_ID1

VALID_STAGE_NUMBER1 = 1


# --- Tests ---
def test_top_16_bracket_with_a_bye_and_forfeits_and_out_of_order_results():
    # Create bracket of 15 entries
    seed_ordered_entries = factories.make_entries(n=15, tournament_id=TOURNY_ID1)    
    bracket = DEBracket(stage_number=VALID_STAGE_NUMBER1, seed_ordered_entries=seed_ordered_entries)

    # Create position ordered entries for comparison
    position_ordered_entries = factories.get_position_ordered_entries_from_seed_ordered_entries(
        factories.pad_entries_to_next_power_of_two(seed_ordered_entries)
    )
    position_ordered_entries_without_nones = tuple(entry for entry in position_ordered_entries if entry is not None)

    # Check bracket attributes
    assert bracket.stage_number == VALID_STAGE_NUMBER1
    assert bracket.bracket_role == DEBracketRole.MAIN
    assert bracket.stop_at_round is None
    assert isinstance(bracket.rounds, tuple)
    assert all(isinstance(round, DERound) for round in bracket.rounds)
    assert bracket.third_place_matchup is None
    assert bracket.score_to_win == 15

    # Check static bracket properties
    assert bracket.tournament_id == TOURNY_ID1
    assert bracket.entries == position_ordered_entries_without_nones
    assert bracket.num_entries == 15
    assert bracket.num_rounds == 4
    assert bracket.playable_rounds is bracket.rounds
    assert bracket.bracket_size == 16
    assert bracket.first_round is bracket.rounds[0]
    assert bracket.round_one_seed_order == (1, 16, 9, 8, 5, 12, 13, 4, 3, 14, 11, 6, 7, 10, 15, 2)
    assert not bracket.has_third_place_matchup()
    assert not bracket.has_stop_round()

    # Check dynamic bracket properties
    assert bracket.current_round_index == 0
    assert bracket.current_round_number == 1
    assert bracket.current_round is bracket.rounds[0]
    assert bracket.current_round_size == 16
    assert bracket.current_round_name == 'Round of 16'
    assert bracket.winner is None

    # Check bracket state before any matches have been played
    assert bracket.is_incomplete()
    assert not bracket.has_started()
    assert bracket.first_round.entries == position_ordered_entries_without_nones

    assert bracket.get_matchup(0, 0).is_complete() # BYE due to 15 entries only
    assert bracket.get_matchup(0, 0).winner is seed_ordered_entries[0]
    assert bracket.get_matchup(0, 0).is_bye()
    assert bracket.get_matchup(1, 0).entry_at(0) is seed_ordered_entries[0]

    assert bracket.rounds[0].entries == (
        seed_ordered_entries[0],
        seed_ordered_entries[8],
        seed_ordered_entries[7],
        seed_ordered_entries[4],
        seed_ordered_entries[11],
        seed_ordered_entries[12],
        seed_ordered_entries[3],
        seed_ordered_entries[2],
        seed_ordered_entries[13],
        seed_ordered_entries[10],
        seed_ordered_entries[5],
        seed_ordered_entries[6],
        seed_ordered_entries[9],
        seed_ordered_entries[14],
        seed_ordered_entries[1]
    )

    assert bracket.rounds[1].entries == (seed_ordered_entries[0], )

    # Record a match result and recheck bracket state
    bracket.record_match_score(round_index=0, matchup_index=1, score1=9, score2=15)

    assert bracket.is_incomplete()
    assert bracket.has_started()
    assert bracket.current_round_index == 0
    assert bracket.winner is None
    assert bracket.rounds[1].entries == (seed_ordered_entries[0], seed_ordered_entries[7])

    # Record a forfeit and recheck bracket state
    bracket.record_forfeit(round_index=0, matchup_index=2, forfeiting_index=0)

    assert bracket.is_incomplete()
    assert bracket.has_started()
    assert bracket.current_round_index == 0
    assert bracket.winner is None
    assert bracket.rounds[1].entries == (seed_ordered_entries[0], seed_ordered_entries[7], seed_ordered_entries[11])

    bracket.record_match_score(round_index=0, matchup_index=7, score1=3, score2=15)
    bracket.record_match_score(round_index=0, matchup_index=3, score1=7, score2=15)

    assert bracket.rounds[1].entries == (
        seed_ordered_entries[0],
        seed_ordered_entries[7],
        seed_ordered_entries[11], 
        seed_ordered_entries[3], 
        seed_ordered_entries[1]
    )

    assert bracket.current_round_index == 0

    bracket.record_match_score(round_index=1, matchup_index=0, score1=14, score2=15)
    assert bracket.rounds[2].entries == (seed_ordered_entries[7], )
    assert bracket.current_round_index == 0

    bracket.record_match_score(round_index=0, matchup_index=5, score1=15, score2=8)
    bracket.record_match_score(round_index=1, matchup_index=1, score1=5, score2=15)

    assert bracket.rounds[1].entries == (
        seed_ordered_entries[0],
        seed_ordered_entries[7],
        seed_ordered_entries[11], 
        seed_ordered_entries[3],
        seed_ordered_entries[10],
        seed_ordered_entries[1]
    )

    assert bracket.rounds[2].entries == (seed_ordered_entries[7], seed_ordered_entries[3])

    bracket.record_match_score(round_index=0, matchup_index=4, score1=15, score2=4)

    assert bracket.is_incomplete()
    assert bracket.has_started()
    assert bracket.current_round_index == 0

    bracket.record_forfeit(round_index=0, matchup_index=6, forfeiting_index=1)

    assert bracket.current_round_index == 1
    assert bracket.current_round_name == 'Quarter-Final'
    assert bracket.rounds[1].entries == (
        seed_ordered_entries[0],
        seed_ordered_entries[7],
        seed_ordered_entries[11], 
        seed_ordered_entries[3],
        seed_ordered_entries[2],
        seed_ordered_entries[10],
        seed_ordered_entries[6],
        seed_ordered_entries[1]
    )

    assert bracket.rounds[2].entries == (seed_ordered_entries[7], seed_ordered_entries[3])

    bracket.record_match_score(round_index=1, matchup_index=2, score1=14, score2=15)

    assert bracket.rounds[2].entries == (seed_ordered_entries[7], seed_ordered_entries[3], seed_ordered_entries[10])

    bracket.record_match_score(round_index=2, matchup_index=0, score1=15, score2=10)

    assert bracket.rounds[3].entries == (seed_ordered_entries[7], )

    assert bracket.is_incomplete()
    assert bracket.winner is None
    assert bracket.current_round_index == 1

    bracket.record_match_score(round_index=1, matchup_index=3, score1=0, score2=15)

    assert bracket.rounds[2].entries == (seed_ordered_entries[7], seed_ordered_entries[3], seed_ordered_entries[10], seed_ordered_entries[1])
    assert bracket.current_round_index == 2
    assert bracket.current_round_name == 'Semi-Final'

    bracket.record_match_score(round_index=2, matchup_index=1, score1=15, score2=2)

    assert bracket.rounds[3].entries == (seed_ordered_entries[7], seed_ordered_entries[10])
    assert bracket.current_round_index == 3
    assert bracket.current_round_name == 'Final'
    assert bracket.is_incomplete()
    assert bracket.winner is None

    bracket.record_match_score(round_index=3, matchup_index=0, score1=15, score2=13)
    
    assert bracket.current_round_index is None
    assert bracket.current_round_number is None
    assert bracket.current_round is None
    assert bracket.current_round_name is None

    assert bracket.is_complete()

    assert bracket.rounds[0].entries == (
        seed_ordered_entries[0],
        seed_ordered_entries[8],
        seed_ordered_entries[7],
        seed_ordered_entries[4],
        seed_ordered_entries[11],
        seed_ordered_entries[12],
        seed_ordered_entries[3],
        seed_ordered_entries[2],
        seed_ordered_entries[13],
        seed_ordered_entries[10],
        seed_ordered_entries[5],
        seed_ordered_entries[6],
        seed_ordered_entries[9],
        seed_ordered_entries[14],
        seed_ordered_entries[1]
    )

    assert bracket.rounds[1].entries == (
        seed_ordered_entries[0],
        seed_ordered_entries[7],
        seed_ordered_entries[11],
        seed_ordered_entries[3],
        seed_ordered_entries[2],
        seed_ordered_entries[10],
        seed_ordered_entries[6],
        seed_ordered_entries[1]
    )

    assert bracket.rounds[2].entries == (
        seed_ordered_entries[7],
        seed_ordered_entries[3],
        seed_ordered_entries[10],
        seed_ordered_entries[1]
    )

    assert bracket.rounds[3].entries == (
        seed_ordered_entries[7],
        seed_ordered_entries[10]
    )

    assert bracket.winner is seed_ordered_entries[7]
    assert bracket.current_round_index is None
    assert bracket.current_round_size is None
    assert bracket.is_complete()
    assert bracket.has_started()
