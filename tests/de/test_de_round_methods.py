import pytest

import factories

from de.de_round import DERound
from matches.de_match import DEMatch


# --- Constants ---
from constants import TOURNY_ID1, TOURNY_ID2

VALID_STAGE_NUMBER1 = 1
VALID_ROUND_NUMBER1 = 1


# --- Fixtures ---
@pytest.fixture
def top_16_round():
    return factories.make_de_round_from_defaults(16, 16, VALID_ROUND_NUMBER1, VALID_STAGE_NUMBER1, TOURNY_ID1)

@pytest.fixture
def top_8_round():
    return factories.make_de_round_from_defaults(8, 8, VALID_ROUND_NUMBER1, VALID_STAGE_NUMBER1, TOURNY_ID1)

@pytest.fixture
def final_round():
    return factories.make_de_round_from_defaults(2, 2, VALID_ROUND_NUMBER1, VALID_STAGE_NUMBER1, TOURNY_ID1)

@pytest.fixture
def empty_later_top_8_round():
    return factories.make_de_round_from_defaults(8, 0, round_number=3, stage_number=VALID_STAGE_NUMBER1, tournament_id=TOURNY_ID1)

@pytest.fixture
def partially_filled_and_scored_later_top_8_round():
    de_round = factories.make_de_round_from_defaults(8, 6, round_number=3, stage_number=VALID_STAGE_NUMBER1, tournament_id=TOURNY_ID1)
    de_round.get_matchup_at(1).record_match_score(10, 15)

    return de_round

@pytest.fixture
def top_8_first_round_with_byes():
    return factories.make_de_round_from_defaults(8, 6, round_number=1, stage_number=VALID_STAGE_NUMBER1, tournament_id=TOURNY_ID1)

@pytest.fixture
def top_8_completed_later_round():
    de_round = factories.make_de_round_from_defaults(8, 8, round_number=3, stage_number=VALID_STAGE_NUMBER1, tournament_id=TOURNY_ID1)

    de_round.get_matchup_at(0).record_match_score(15, 2)
    de_round.get_matchup_at(1).record_match_score(10, 15)
    de_round.get_matchup_at(2).record_match_score(15, 13)
    de_round.get_matchup_at(3).record_match_score(7, 15)

    return de_round


# --- Predicate Method Tests ---
def test_de_round_is_complete_full_completed_later_round(top_8_completed_later_round):
    assert top_8_completed_later_round.is_complete()
    assert not top_8_completed_later_round.is_incomplete()

def test_de_round_is_complete_completed_first_round_with_byes(top_8_first_round_with_byes):
    top_8_first_round_with_byes.get_matchup_at(1).record_match_score(10, 15)
    top_8_first_round_with_byes.get_matchup_at(2).record_match_score(15, 13)

    assert top_8_first_round_with_byes.is_complete()
    assert not top_8_first_round_with_byes.is_incomplete()

def test_de_round_is_incomplete_empty_round(empty_later_top_8_round):
    assert not empty_later_top_8_round.is_complete()
    assert empty_later_top_8_round.is_incomplete()

def test_de_round_is_incomplete_partially_filled_round(partially_filled_and_scored_later_top_8_round):
    # Complete the remaining incomplete matchup with both entries present
    partially_filled_and_scored_later_top_8_round.get_matchup_at(2).record_match_score(15, 14)

    assert not partially_filled_and_scored_later_top_8_round.is_complete()
    assert partially_filled_and_scored_later_top_8_round.is_incomplete()

def test_de_round_is_incomplete_first_round_with_byes(top_8_first_round_with_byes):
    assert not top_8_first_round_with_byes.is_complete()
    assert top_8_first_round_with_byes.is_incomplete()

def test_de_round_has_entry_entry_present(entry1, top_16_round):
    assert top_16_round.has_entry(entry1)

def test_de_round_has_entry_entry_not_present(top_16_round):
    entry17 = factories.make_entry_at_number(17, tournament_id=TOURNY_ID1)
    assert not top_16_round.has_entry(entry17)

@pytest.mark.parametrize('invalid_entry_type', [None, False, True, 'John', 0, 1.0, [], (), {}, object()])
def test_de_round_has_entry_invalid_entry_type(final_round, invalid_entry_type):
    with pytest.raises(TypeError):
        final_round.has_entry(invalid_entry_type)


# --- Access Method Tests ---
def test_de_round_get_matchup_at(top_8_round):
    for matchup_index in range(top_8_round.num_matchups):
        matchup = top_8_round.get_matchup_at(matchup_index)
        assert matchup is top_8_round.matchups[matchup_index]
        assert matchup.matchup_index == matchup_index

@pytest.mark.parametrize('invalid_index_type', [None, False, True, 0.0, 1.0, 'first', [], (), {}, object()])
def test_de_round_get_matchup_at_invalid_index_type(top_8_round, invalid_index_type):
    with pytest.raises(TypeError):
        top_8_round.get_matchup_at(invalid_index_type)

@pytest.mark.parametrize('invalid_index_value', [-100, -1, 4, 100])
def test_de_round_get_matchup_at_invalid_index_value(top_8_round, invalid_index_value):
    with pytest.raises(ValueError):
        top_8_round.get_matchup_at(invalid_index_value)

def test_de_round_get_round_losers_empty_round(empty_later_top_8_round):
    losers = empty_later_top_8_round.get_round_losers()
    
    assert losers == ()

def test_de_round_get_round_losers_partially_filled_round(partially_filled_and_scored_later_top_8_round, entry5):
    losers = partially_filled_and_scored_later_top_8_round.get_round_losers()
    
    assert losers == (entry5, )

def test_de_round_get_round_losers_completed_round(top_8_completed_later_round, entry5, entry6, entry7):
    entry8 = factories.make_entry_at_number(8, tournament_id=TOURNY_ID1)

    losers = top_8_completed_later_round.get_round_losers()
    assert losers == (entry8, entry5, entry6, entry7)

def test_de_round_get_round_losers_with_byes_and_forfeit(top_8_first_round_with_byes, entry5, entry6):
    # Record matchup 2 first as entry6 forfeiting
    top_8_first_round_with_byes.get_matchup_at(2).record_forfeit(forfeiting_index=1)

    # Record matchup 1 second with entry5 losing by a score
    top_8_first_round_with_byes.get_matchup_at(1).record_match_score(10, 15)

    # Note that the order of the losers is preserved in matchup-order
    losers = top_8_first_round_with_byes.get_round_losers()
    assert losers == (entry5, entry6)


# --- Entry Management Method Tests ---
@pytest.mark.parametrize(('matchup_index_to_add_to', 'entry_index_to_add_to'), [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1), (3, 0), (3, 1)])
def test_de_round_add_entry_to_matchup_to_an_empty_matchup(empty_later_top_8_round, entry1, matchup_index_to_add_to, entry_index_to_add_to):
    matchup_to_add_to = empty_later_top_8_round.get_matchup_at(matchup_index_to_add_to)

    empty_later_top_8_round.add_entry_to_matchup(entry1, matchup_index=matchup_index_to_add_to, entry_index=entry_index_to_add_to)

    assert empty_later_top_8_round.has_entry(entry1)

    assert matchup_to_add_to.has_entry(entry1)
    assert matchup_to_add_to.entry_at(entry_index_to_add_to) is entry1

    expected_entries = (entry1, None) if entry_index_to_add_to == 0 else (None, entry1)
    assert matchup_to_add_to.entries == expected_entries

    assert matchup_to_add_to.match is None

@pytest.mark.parametrize(('matchup_index_to_add_to', 'entry_index_to_add_to'), [(0, 1), (3, 0)])
def test_de_round_add_entry_to_matchup_to_a_matchup_with_one_entry(partially_filled_and_scored_later_top_8_round, entry1, entry2, entry7, matchup_index_to_add_to, entry_index_to_add_to):
    matchup_to_add_to = partially_filled_and_scored_later_top_8_round.get_matchup_at(matchup_index_to_add_to)

    partially_filled_and_scored_later_top_8_round.add_entry_to_matchup(
        entry=entry7, 
        matchup_index=matchup_index_to_add_to, 
        entry_index=entry_index_to_add_to
    )

    assert partially_filled_and_scored_later_top_8_round.has_entry(entry7)

    assert matchup_to_add_to.has_entry(entry7)
    assert matchup_to_add_to.entry_at(entry_index_to_add_to) is entry7

    expected_entries = (entry1, entry7) if matchup_index_to_add_to == 0 else (entry7, entry2)
    assert matchup_to_add_to.entries == expected_entries

    assert isinstance(matchup_to_add_to.match, DEMatch)
    assert matchup_to_add_to.match.entries == expected_entries

@pytest.mark.parametrize('invalid_entry_type', [None, False, True, 'John', 0, 1.0, [], (), {}, object()])
def test_de_round_add_entry_to_matchup_invalid_entry_type(empty_later_top_8_round, invalid_entry_type):
    with pytest.raises(TypeError):
        empty_later_top_8_round.add_entry_to_matchup(entry=invalid_entry_type, matchup_index=1, entry_index=1)

def test_de_round_add_entry_to_matchup_invalid_entry_wrong_tournament(empty_later_top_8_round):
    invalid_entry = factories.make_entry_at_number(1, tournament_id=TOURNY_ID2)

    with pytest.raises(ValueError):
        empty_later_top_8_round.add_entry_to_matchup(entry=invalid_entry, matchup_index=0, entry_index=1)

def test_de_round_add_entry_to_matchup_invalid_entry_already_in_round(partially_filled_and_scored_later_top_8_round, entry1):
    with pytest.raises(ValueError):
        partially_filled_and_scored_later_top_8_round.add_entry_to_matchup(entry=entry1, matchup_index=3, entry_index=0)

@pytest.mark.parametrize('invalid_matchup_index_type', [None, False, True, 0.0, 1.0, 'first', [], (), {}, object()])
def test_de_round_add_entry_to_matchup_invalid_index_type(empty_later_top_8_round, entry1, invalid_matchup_index_type):
    with pytest.raises(TypeError):
        empty_later_top_8_round.add_entry_to_matchup(entry=entry1, matchup_index=invalid_matchup_index_type, entry_index=0)

@pytest.mark.parametrize('invalid_matchup_index_value', [-100, -1, 4, 100])
def test_de_round_add_entry_to_matchup_invalid_index_value(empty_later_top_8_round, entry1, invalid_matchup_index_value):
    with pytest.raises(ValueError):
        empty_later_top_8_round.add_entry_to_matchup(entry=entry1, matchup_index=invalid_matchup_index_value, entry_index=0)

@pytest.mark.parametrize('invalid_entry_index_type', [None, False, True, 0.0, 1.0, 'first', 'second', [], (), {}, object()])
def test_de_round_add_entry_to_matchup_invalid_entry_index_type(empty_later_top_8_round, entry1, invalid_entry_index_type):
    with pytest.raises(TypeError):
        empty_later_top_8_round.add_entry_to_matchup(entry=entry1, matchup_index=0, entry_index=invalid_entry_index_type)

@pytest.mark.parametrize('invalid_entry_index_value', [-100, -1, 2, 100])
def test_de_round_add_entry_to_matchup_invalid_entry_index_value(empty_later_top_8_round, entry1, invalid_entry_index_value):
    with pytest.raises(ValueError):
        empty_later_top_8_round.add_entry_to_matchup(entry=entry1, matchup_index=0, entry_index=invalid_entry_index_value)

@pytest.mark.parametrize(('matchup_index', 'entry_index'), [(0, 0), (1, 0), (1, 1), (2, 0), (2, 1), (3, 1)])
def test_de_round_add_entry_to_matchup_destination_position_occupied(partially_filled_and_scored_later_top_8_round, entry7, matchup_index, entry_index):
    matchup = partially_filled_and_scored_later_top_8_round.get_matchup_at(matchup_index)

    position1_entry = matchup.entry_at(0)
    position2_entry = matchup.entry_at(1)

    entries = (position1_entry, position2_entry)

    with pytest.raises(ValueError):
        partially_filled_and_scored_later_top_8_round.add_entry_to_matchup(entry=entry7, matchup_index=matchup_index, entry_index=entry_index)

    assert matchup.entries == entries


# --- Bracket Position Generation Helper Method Tests ---
@pytest.mark.parametrize(
        ('depth, expected_bracket_level'), 
        [
            (0, (1, )),
            (1, (1, 2)),
            (2, (1, 4, 3, 2)),
            (3, (1, 8, 5, 4, 3, 6, 7, 2)),
            (4, (1, 16, 9, 8, 5, 12, 13, 4, 3, 14, 11, 6, 7, 10, 15, 2)),
            (
                5, 
                (1, 32, 17, 16, 9, 24, 25, 8, 5, 28, 21, 12, 13, 20, 29, 4, 
                 3, 30, 19, 14, 11, 22, 27, 6, 7, 26, 23, 10, 15, 18, 31, 2)
            )
        ]
)
def test_de_round_static_method__generate_tree_bracket_level(depth, expected_bracket_level):
    assert DERound.generate_tree_bracket_level(depth) == expected_bracket_level

@pytest.mark.parametrize('invalid_depth_type', [None, False, True, 0.0, 4.0, 'root', [], (), {}, object()])
def test_de_round_static_method__generate_tree_bracket_level_invalid_depth_type(invalid_depth_type):
    with pytest.raises(TypeError):
        DERound.generate_tree_bracket_level(invalid_depth_type)

@pytest.mark.parametrize('invalid_depth_value', [-100, -10, -1])
def test_de_round_static_method__generate_tree_bracket_level_invalid_depth_value(invalid_depth_value):
    with pytest.raises(ValueError):
        DERound.generate_tree_bracket_level(invalid_depth_value)
