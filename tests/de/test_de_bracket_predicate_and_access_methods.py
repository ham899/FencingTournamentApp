import pytest

import factories

# --- Constants ---
from constants import TOURNY_ID1, TOURNY_ID2

VALID_STAGE_NUMBER1 = 1
INVALID_INDEX_TYPES = [None, False, True, 1.5, 'first', [], (), {}, object()]


# --- Fixtures ---
@pytest.fixture
def initial_full_top_4_bracket():
    return factories.make_de_bracket_from_defaults(
        num_entries=4,
        tournament_id=TOURNY_ID1,
        stage_number=VALID_STAGE_NUMBER1
    )

@pytest.fixture
def initial_top_4_bracket_with_third_place_matchup():
    return factories.make_de_bracket_from_defaults(
        num_entries=4,
        tournament_id=TOURNY_ID1,
        stage_number=VALID_STAGE_NUMBER1,
        has_third_place_match=True
    )

@pytest.fixture
def initial_full_top_8_bracket():
    return factories.make_de_bracket_from_defaults(
        num_entries=8,
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

@pytest.fixture
def initial_full_top_8_bracket_with_third_place_matchup():
    return factories.make_de_bracket_from_defaults(
        num_entries=8,
        tournament_id=TOURNY_ID1,
        stage_number=VALID_STAGE_NUMBER1,
        has_third_place_match=True
    )

@pytest.fixture
def initial_top_8_bracket_with_six_entries():
    return factories.make_de_bracket_from_defaults(
        num_entries=6,
        tournament_id=TOURNY_ID1,
        stage_number=VALID_STAGE_NUMBER1
    )


# --- Predicate Method Tests ---
def test_de_bracket_is_complete(initial_full_top_4_bracket):
    bracket = initial_full_top_4_bracket
    assert not bracket.is_complete()

    bracket.record_forfeit(round_index=0, matchup_index=0, forfeiting_index=1)
    assert not bracket.is_complete()

    bracket.record_forfeit(round_index=0, matchup_index=1, forfeiting_index=0)
    assert not bracket.is_complete()

    bracket.record_forfeit(round_index=1, matchup_index=0, forfeiting_index=1)
    assert bracket.is_complete()

def test_de_bracket_is_complete_stopped_bracket(initial_full_top_8_bracket_with_stop_round):
    bracket = initial_full_top_8_bracket_with_stop_round
    
    assert not bracket.is_complete()

    bracket.record_match_score(round_index=0, matchup_index=0, score1=15, score2=6)
    bracket.record_match_score(round_index=0, matchup_index=1, score1=15, score2=7)
    bracket.record_match_score(round_index=0, matchup_index=2, score1=15, score2=8)

    assert not bracket.is_complete()

    bracket.record_match_score(round_index=0, matchup_index=3, score1=15, score2=9)

    assert bracket.is_complete()

def test_de_bracket_is_complete_with_third_place_matchup(initial_top_4_bracket_with_third_place_matchup):
    bracket = initial_top_4_bracket_with_third_place_matchup

    assert not bracket.is_complete()

    bracket.record_match_score(round_index=0, matchup_index=0, score1=15, score2=1)
    bracket.record_match_score(round_index=0, matchup_index=1, score1=15, score2=2)

    assert not bracket.is_complete()

    bracket.record_match_score(round_index=1, matchup_index=0, score1=15, score2=3)

    assert not bracket.is_complete()

    bracket.record_third_place_match_score(score1=15, score2=4)

    assert bracket.is_complete()

def test_de_bracket_is_incomplete():
    bracket = factories.make_de_bracket_from_defaults(
        num_entries=3,
        tournament_id=TOURNY_ID1,
        stage_number=VALID_STAGE_NUMBER1
    )
    assert bracket.is_incomplete()

    bracket.record_match_score(round_index=0, matchup_index=1, score1=15, score2=7)
    assert bracket.is_incomplete()

    bracket.record_match_score(round_index=1, matchup_index=0, score1=14, score2=15)
    assert not bracket.is_incomplete()

def test_de_bracket_has_third_place_matchup(initial_full_top_8_bracket, initial_full_top_8_bracket_with_third_place_matchup):
    assert not initial_full_top_8_bracket.has_third_place_matchup()
    assert initial_full_top_8_bracket_with_third_place_matchup.has_third_place_matchup()

def test_de_bracket_has_stop_round(initial_full_top_8_bracket, initial_full_top_8_bracket_with_stop_round):
    assert not initial_full_top_8_bracket.has_stop_round()
    assert initial_full_top_8_bracket_with_stop_round.has_stop_round()

def test_de_bracket_has_started(initial_full_top_8_bracket):
    assert not initial_full_top_8_bracket.has_started()

    initial_full_top_8_bracket.record_match_score(round_index=0, matchup_index=0, score1=15, score2=9)

    assert initial_full_top_8_bracket.has_started()

    initial_full_top_8_bracket.record_match_score(round_index=0, matchup_index=1, score1=15, score2=8)

    assert initial_full_top_8_bracket.has_started()

    initial_full_top_8_bracket.reset_match_result(round_index=0, matchup_index=1)

    assert initial_full_top_8_bracket.has_started()

    initial_full_top_8_bracket.reset_match_result(round_index=0, matchup_index=0)

    assert not initial_full_top_8_bracket.has_started()

def test_de_bracket_has_started_one_forfeit_then_reset(initial_full_top_8_bracket):
    assert not initial_full_top_8_bracket.has_started()

    initial_full_top_8_bracket.record_forfeit(round_index=0, matchup_index=0, forfeiting_index=0)

    assert initial_full_top_8_bracket.has_started()

    initial_full_top_8_bracket.reset_match_result(round_index=0, matchup_index=0)

    assert not initial_full_top_8_bracket.has_started()

def test_de_bracket_has_started_bracket_with_byes(initial_top_8_bracket_with_six_entries):
    bracket = initial_top_8_bracket_with_six_entries
    assert not bracket.has_started()

    bracket.record_match_score(round_index=0, matchup_index=1, score1=15, score2=13)
    assert bracket.has_started()

    bracket.reset_match_result(round_index=0, matchup_index=1)
    assert not bracket.has_started()

def test_de_bracket_has_entry(initial_full_top_4_bracket, entry1, entry2, entry3, entry4, entry5, entry6, entry7):
    bracket = initial_full_top_4_bracket

    assert bracket.has_entry(entry1)
    assert bracket.has_entry(entry2)
    assert bracket.has_entry(entry3)
    assert bracket.has_entry(entry4)

    assert not bracket.has_entry(entry5)
    assert not bracket.has_entry(entry6)
    assert not bracket.has_entry(entry7)

    bracket.record_match_score(round_index=0, matchup_index=0, score1=8, score2=15)
    bracket.record_match_score(round_index=0, matchup_index=1, score1=15, score2=12)
    bracket.record_match_score(round_index=1, matchup_index=0, score1=11, score2=15)

    assert bracket.has_entry(entry1)
    assert bracket.has_entry(entry2)
    assert bracket.has_entry(entry3)
    assert bracket.has_entry(entry4)

    assert not bracket.has_entry(entry5)
    assert not bracket.has_entry(entry6)
    assert not bracket.has_entry(entry7)

def test_de_bracket_has_entry_different_tournament(initial_full_top_4_bracket):
    entry = factories.make_entry_at_number(number=1, tournament_id=TOURNY_ID2)

    assert not initial_full_top_4_bracket.has_entry(entry)

@pytest.mark.parametrize('invalid_entry_type', [None, False, True, 0, 1.0, 'Steve', [], (), {}, object()])
def test_de_bracket_has_entry_invalid_entry_type(initial_full_top_4_bracket, invalid_entry_type):
    with pytest.raises(TypeError):
        initial_full_top_4_bracket.has_entry(invalid_entry_type)


# --- Access Tests ---
@pytest.mark.parametrize('index', [0, 1, 2])
def test_de_bracket_get_round(initial_full_top_8_bracket, index):
    de_round = initial_full_top_8_bracket.get_round(index)

    assert initial_full_top_8_bracket.rounds[index] is de_round
    assert de_round.round_number == index + 1

@pytest.mark.parametrize('invalid_index_type', INVALID_INDEX_TYPES)
def test_de_bracket_get_round_invalid_index_type(initial_full_top_8_bracket, invalid_index_type):
    with pytest.raises(TypeError):
        initial_full_top_8_bracket.get_round(invalid_index_type)

@pytest.mark.parametrize('invalid_index_value', [-10, -1, 3, 4, 10])
def test_de_bracket_get_round_invalid_index_value(initial_full_top_8_bracket, invalid_index_value):
    with pytest.raises(ValueError):
        initial_full_top_8_bracket.get_round(invalid_index_value)

@pytest.mark.parametrize(('index', 'expected_round_size'), [(0, 8), (1, 4), (2, 2)])
def test_de_bracket_get_round_size(initial_full_top_8_bracket, index, expected_round_size):
    assert initial_full_top_8_bracket.get_round_size(index) == expected_round_size

@pytest.mark.parametrize('invalid_index_type', INVALID_INDEX_TYPES)
def test_de_bracket_get_round_size_invalid_index_type(initial_full_top_8_bracket, invalid_index_type):
    with pytest.raises(TypeError):
        initial_full_top_8_bracket.get_round_size(invalid_index_type)

@pytest.mark.parametrize('invalid_index_value', [-10, -1, 3, 4, 10])
def test_de_bracket_get_round_size_invalid_index_value(initial_full_top_8_bracket, invalid_index_value):
    with pytest.raises(ValueError):
        initial_full_top_8_bracket.get_round_size(invalid_index_value)

@pytest.mark.parametrize(('round_index', 'matchup_index'), [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (2, 0)])
def test_de_bracket_get_matchup(initial_full_top_8_bracket, round_index, matchup_index):
    matchup = initial_full_top_8_bracket.get_matchup(round_index, matchup_index)

    assert initial_full_top_8_bracket.rounds[round_index].matchups[matchup_index] is matchup
    assert matchup.round_number == round_index + 1
    assert matchup.matchup_number == matchup_index + 1

@pytest.mark.parametrize('invalid_round_index_type', INVALID_INDEX_TYPES)
def test_de_bracket_get_matchup_invalid_round_index_type(initial_full_top_8_bracket, invalid_round_index_type):
    with pytest.raises(TypeError):
        initial_full_top_8_bracket.get_matchup(invalid_round_index_type, 0)

@pytest.mark.parametrize('invalid_round_index_value', [-10, -1, 3, 4, 10])
def test_de_bracket_get_matchup_invalid_round_index_value(initial_full_top_8_bracket, invalid_round_index_value):
    with pytest.raises(ValueError):
        initial_full_top_8_bracket.get_matchup(invalid_round_index_value, 0)

@pytest.mark.parametrize('invalid_matchup_index_type', INVALID_INDEX_TYPES)
def test_de_bracket_get_matchup_invalid_matchup_index_type(initial_full_top_8_bracket, invalid_matchup_index_type):
    with pytest.raises(TypeError):
        initial_full_top_8_bracket.get_matchup(0, invalid_matchup_index_type)

@pytest.mark.parametrize(
    ('round_index', 'invalid_matchup_index_value'), 
    [
        (0, -10), (0, 4), 
        (1, -5), (1, 2), 
        (2, -1), (2, 1)
    ]
)
def test_de_bracket_get_matchup_invalid_matchup_index_value(initial_full_top_8_bracket, round_index, invalid_matchup_index_value):
    with pytest.raises(ValueError):
        initial_full_top_8_bracket.get_matchup(round_index, invalid_matchup_index_value)

@pytest.mark.parametrize(('round_index', 'matchup_index'), [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (2, 0)])
def test_de_bracket_get_match(initial_full_top_8_bracket, round_index, matchup_index):
    match = initial_full_top_8_bracket.get_match(round_index, matchup_index)

    assert initial_full_top_8_bracket.rounds[round_index].matchups[matchup_index].match is match

    if round_index == 0:
        assert match is not None
        assert match.round_number == round_index + 1
        assert match.match_number == matchup_index + 1
    else:
        assert match is None

@pytest.mark.parametrize('invalid_round_index_type', INVALID_INDEX_TYPES)
def test_de_bracket_get_match_invalid_round_index_type(initial_full_top_8_bracket, invalid_round_index_type):
    with pytest.raises(TypeError):
        initial_full_top_8_bracket.get_match(invalid_round_index_type, 0)

@pytest.mark.parametrize('invalid_round_index_value', [-10, -1, 3, 4, 10])
def test_de_bracket_get_match_invalid_round_index_value(initial_full_top_8_bracket, invalid_round_index_value):
    with pytest.raises(ValueError):
        initial_full_top_8_bracket.get_match(invalid_round_index_value, 0)

@pytest.mark.parametrize('invalid_matchup_index_type', INVALID_INDEX_TYPES)
def test_de_bracket_get_match_invalid_matchup_index_type(initial_full_top_8_bracket, invalid_matchup_index_type):
    with pytest.raises(TypeError):
        initial_full_top_8_bracket.get_match(0, invalid_matchup_index_type)

@pytest.mark.parametrize(
    ('round_index', 'invalid_matchup_index_value'), 
    [
        (0, -10), (0, 4), 
        (1, -5), (1, 2), 
        (2, -1), (2, 1)
    ]
)
def test_de_bracket_get_match_invalid_matchup_index_value(initial_full_top_8_bracket, round_index, invalid_matchup_index_value):
    with pytest.raises(ValueError):
        initial_full_top_8_bracket.get_match(round_index, invalid_matchup_index_value)

def test_de_bracket_get_ready_matchups(initial_full_top_8_bracket):
    bracket = initial_full_top_8_bracket
    
    assert bracket.is_incomplete()

    # See ready matchups upon initialization
    assert bracket.get_ready_matchups() == (
        bracket.rounds[0].matchups[0],
        bracket.rounds[0].matchups[1],
        bracket.rounds[0].matchups[2],
        bracket.rounds[0].matchups[3]
    )

    for matchup in bracket.get_ready_matchups():
        assert matchup.has_match()

    # Record results and check new ready matchups
    bracket.record_match_score(round_index=0, matchup_index=0, score1=15, score2=2)

    assert bracket.get_ready_matchups() == (
        bracket.rounds[0].matchups[1],
        bracket.rounds[0].matchups[2],
        bracket.rounds[0].matchups[3]
    )
    for matchup in bracket.get_ready_matchups():
        assert matchup.has_match()

    bracket.record_match_score(round_index=0, matchup_index=3, score1=3, score2=15)

    assert bracket.get_ready_matchups() == (bracket.rounds[0].matchups[1], bracket.rounds[0].matchups[2])
    for matchup in bracket.get_ready_matchups():
        assert matchup.has_match()

    bracket.record_match_score(round_index=0, matchup_index=1, score1=14, score2=15)

    assert bracket.get_ready_matchups() == (bracket.rounds[0].matchups[2], bracket.rounds[1].matchups[0])
    for matchup in bracket.get_ready_matchups():
        assert matchup.has_match()

    bracket.record_match_score(round_index=0, matchup_index=2, score1=15, score2=13)

    assert bracket.get_ready_matchups() == (bracket.rounds[1].matchups[0], bracket.rounds[1].matchups[1])
    for matchup in bracket.get_ready_matchups():
        assert matchup.has_match()

    bracket.record_match_score(round_index=1, matchup_index=1, score1=12, score2=15)

    assert bracket.get_ready_matchups() == (bracket.rounds[1].matchups[0], )
    for matchup in bracket.get_ready_matchups():
        assert matchup.has_match()

    bracket.record_match_score(round_index=1, matchup_index=0, score1=15, score2=10)

    assert bracket.get_ready_matchups() == (bracket.rounds[2].matchups[0], )
    for matchup in bracket.get_ready_matchups():
        assert matchup.has_match()

    bracket.record_match_score(round_index=2, matchup_index=0, score1=15, score2=11)

    assert bracket.get_ready_matchups() == ()
    assert bracket.is_complete()

def test_de_bracket_get_ready_matchups_with_byes(initial_top_8_bracket_with_six_entries):
    bracket = initial_top_8_bracket_with_six_entries

    # BYEs are excluded; only the two playable opening matches
    assert bracket.get_ready_matchups() == (bracket.rounds[0].matchups[1], bracket.rounds[0].matchups[2])

    bracket.record_match_score(round_index=0, matchup_index=1, score1=15, score2=8)

    assert bracket.get_ready_matchups() == (bracket.rounds[0].matchups[2], bracket.rounds[1].matchups[0])

    bracket.record_match_score(round_index=0, matchup_index=2, score1=9, score2=15)

    assert bracket.get_ready_matchups() == (bracket.rounds[1].matchups[0], bracket.rounds[1].matchups[1])


def test_de_bracket_get_ready_matchups_stopped_bracket(initial_full_top_8_bracket_with_stop_round):
    bracket = initial_full_top_8_bracket_with_stop_round

    assert bracket.get_ready_matchups() == bracket.rounds[0].matchups

    # Record first two matchups so matchup in next round is populated
    bracket.record_match_score(round_index=0, matchup_index=0, score1=15, score2=6)
    bracket.record_match_score(round_index=0, matchup_index=1, score1=15, score2=7)

    assert bracket.rounds[1].matchups[0].has_match()
    assert bracket.rounds[1].matchups[0].is_incomplete()

    # Note that no matchups should be present from round 2
    assert bracket.get_ready_matchups() == (bracket.rounds[0].matchups[2], bracket.rounds[0].matchups[3])

    # Record the next two matchups in round 1
    bracket.record_match_score(round_index=0, matchup_index=2, score1=15, score2=8)
    bracket.record_match_score(round_index=0, matchup_index=3, score1=15, score2=9)

    # Matchups in round 2 exist but are not playable
    for matchup in bracket.rounds[1].matchups:
        assert matchup.has_match()
        assert matchup.is_incomplete()

    # Check that there are no ready matchups left in the stopped bracket and that the bracket is complete
    assert bracket.get_ready_matchups() == ()
    assert bracket.is_complete()

def test_de_bracket_get_ready_matchups_with_third_place_matchup(initial_top_4_bracket_with_third_place_matchup):
    bracket = initial_top_4_bracket_with_third_place_matchup

    semi_final_1, semi_final_2 = bracket.rounds[0].matchups
    final = bracket.rounds[1].matchups[0]
    third_place = bracket.third_place_matchup

    assert bracket.get_ready_matchups() == (semi_final_1, semi_final_2)

    bracket.record_match_score(round_index=0, matchup_index=0, score1=15, score2=8)

    # Neither medal match is ready with only one entry present
    assert bracket.get_ready_matchups() == (semi_final_2, )

    bracket.record_match_score(round_index=0, matchup_index=1, score1=15, score2=4)

    # Note: third-place matchup follows the ready main-bracket matchups
    assert bracket.get_ready_matchups() == (final, third_place)

    bracket.record_third_place_match_score(score1=15, score2=10)

    # Completed third-place matches are excluded.
    assert bracket.get_ready_matchups() == (final, )
    assert not bracket.is_complete()

    bracket.record_match_score(round_index=1, matchup_index=0, score1=15, score2=13)

    assert bracket.get_ready_matchups() == ()
    assert bracket.is_complete()
