import pytest

from matches.match import Match, MatchStatus
from entities.fencer import Fencer

# --- Constants ---
FENCER_ID1 = 1
FENCER_ID2 = 2
DISPLAY_NAME1 = 'Ben'
DISPLAY_NAME2 = 'Bill'
MATCH_ID1 = 1
MATCH_ID2 = 2
TEST_SCORE_TO_WIN = 8 # Must be greater than 2 for certain test cases

# --- Fixtures ---
@pytest.fixture
def fencer1():
    return Fencer(id=FENCER_ID1, display_name=DISPLAY_NAME1)

@pytest.fixture
def fencer2():
    return Fencer(id=FENCER_ID2, display_name=DISPLAY_NAME2)

@pytest.fixture
def standard_match_no_fencers():
    return Match(id=MATCH_ID1, score_to_win=TEST_SCORE_TO_WIN)

@pytest.fixture
def standard_match_fencer1_only(fencer1):
    return Match(id=MATCH_ID1, score_to_win=TEST_SCORE_TO_WIN, fencer1=fencer1)

@pytest.fixture
def standard_match_fencer2_only(fencer2):
    return Match(id=MATCH_ID1, score_to_win=TEST_SCORE_TO_WIN, fencer2=fencer2)

@pytest.fixture
def standard_match_fencers(fencer1, fencer2):
    return Match(id=MATCH_ID1, score_to_win=TEST_SCORE_TO_WIN, fencer1=fencer1, fencer2=fencer2)


# --- Initialization and Validation Tests ---
def test_match_creation_valid_with_defaults():
    match = Match(id=MATCH_ID1, score_to_win=TEST_SCORE_TO_WIN)
    assert match.id == MATCH_ID1
    assert match.score_to_win == TEST_SCORE_TO_WIN
    assert match.fencer1 is None
    assert match.fencer2 is None
    assert match.score1 is None
    assert match.score2 is None
    assert match.status == MatchStatus.NOT_STARTED
    assert match.match_type == 'standard'

def test_match_creation_valid_with_no_defaults(fencer1, fencer2):
    match = Match(id=MATCH_ID1, 
                  score_to_win=TEST_SCORE_TO_WIN,
                  fencer1=fencer1,
                  fencer2=fencer2)
    assert match.id == MATCH_ID1
    assert match.score_to_win == TEST_SCORE_TO_WIN
    assert match.fencer1 == fencer1
    assert match.fencer2 == fencer2
    assert match.score1 is None
    assert match.score2 is None
    assert match.status == MatchStatus.NOT_STARTED
    assert match.match_type == 'standard'

@pytest.mark.parametrize('invalid_id_type', [None, '1', 1.0, True, [], {}])
def test_match_creation_invalid_id_type(invalid_id_type):
    with pytest.raises(TypeError):
        Match(id=invalid_id_type, score_to_win=TEST_SCORE_TO_WIN)

@pytest.mark.parametrize('invalid_score_to_win_type', [None, '15', 5.0, True, [], {}])
def test_match_creation_invalid_score_to_win_type(invalid_score_to_win_type):
    with pytest.raises(TypeError):
        Match(id=MATCH_ID1, score_to_win=invalid_score_to_win_type)

@pytest.mark.parametrize('invalid_fencer_type', ['Ben', 0, True, 8.0, [], {}])
def test_match_creation_invalid_fencer_type(invalid_fencer_type):
    with pytest.raises(TypeError):
        Match(id=MATCH_ID1, score_to_win=TEST_SCORE_TO_WIN, fencer1=invalid_fencer_type)
    with pytest.raises(TypeError):
        Match(id=MATCH_ID1, score_to_win=TEST_SCORE_TO_WIN, fencer2=invalid_fencer_type)
    with pytest.raises(TypeError):
        Match(id=MATCH_ID1, score_to_win=TEST_SCORE_TO_WIN, fencer1=invalid_fencer_type, fencer2=invalid_fencer_type)

@pytest.mark.parametrize('negative_id', [-100,-10,-1])
def test_match_creation_invalid_id_negative(negative_id):
    with pytest.raises(ValueError):
        Match(id=negative_id, score_to_win=TEST_SCORE_TO_WIN)

@pytest.mark.parametrize('non_positive_score_to_win', [-100,-1,0])
def test_match_creation_invalid_score_to_win_non_positive(non_positive_score_to_win):
    with pytest.raises(ValueError):
        Match(id=MATCH_ID1, score_to_win=non_positive_score_to_win)

def test_match_creation_invalid_fencers_same_fencers(fencer1):
    with pytest.raises(ValueError):
        Match(id=MATCH_ID1, score_to_win=TEST_SCORE_TO_WIN, fencer1=fencer1, fencer2=fencer1)

def test_match_creation_invalid_fencers_same_fencer_id():
    fencer1 = Fencer(id=1, display_name='Ben')
    fencer1_same = Fencer(id=1, display_name='Benjamin')
    with pytest.raises(ValueError):
        Match(id=MATCH_ID1, score_to_win=TEST_SCORE_TO_WIN, fencer1=fencer1, fencer2=fencer1_same)


# --- Dunder Method Tests ---
def test_match_equality_same_type_same_id():
    match1 = Match(id=MATCH_ID1, score_to_win=5)
    match2 = Match(id=MATCH_ID1, score_to_win=15)
    assert match1 == match2

def test_match_equality_does_not_depend_on_score_or_status():
    match1 = Match(id=MATCH_ID1, score_to_win=5)
    match2 = Match(id=MATCH_ID1, score_to_win=5)
    match1.start()
    match1.touch1()
    assert match1 == match2

def test_match_inequality_different_id():
    match1 = Match(id=MATCH_ID1, score_to_win=5)
    match2 = Match(id=MATCH_ID2, score_to_win=5)
    assert match1 != match2

def test_match_inequality_different_type():
    match = Match(id=MATCH_ID1, score_to_win=5)
    assert match != "non-match"

def test_match_inequality_different_match_subclass():
    class CustomMatch(Match):
        pass
    match1 = Match(id=MATCH_ID1, score_to_win=5)
    match2 = CustomMatch(id=MATCH_ID1, score_to_win=5)
    assert match1 != match2


# --- Predicate Method Tests ---
def test_match_has_not_started(standard_match_no_fencers):
    assert standard_match_no_fencers.status == MatchStatus.NOT_STARTED
    assert standard_match_no_fencers.has_not_started()

def test_match_has_scores(standard_match_no_fencers):
    assert not standard_match_no_fencers.has_scores()
    standard_match_no_fencers.start()
    assert standard_match_no_fencers.has_scores()

def test_match_is_in_progress(standard_match_no_fencers):
    assert standard_match_no_fencers.has_not_started()
    assert not standard_match_no_fencers.is_in_progress()
    standard_match_no_fencers.start()
    assert standard_match_no_fencers.status == MatchStatus.IN_PROGRESS
    assert standard_match_no_fencers.is_in_progress()
    standard_match_no_fencers.touch1()
    standard_match_no_fencers.end()
    assert standard_match_no_fencers.status == MatchStatus.COMPLETED
    assert not standard_match_no_fencers.is_in_progress()

def test_match_is_tied(standard_match_no_fencers):
    assert not standard_match_no_fencers.is_tied()
    standard_match_no_fencers.start()
    assert standard_match_no_fencers.is_tied()
    standard_match_no_fencers.touch1()
    assert not standard_match_no_fencers.is_tied()

def test_match_has_both_fencers_none_present(standard_match_no_fencers):
    assert not standard_match_no_fencers.has_both_fencers()

def test_match_has_both_fencers_one_present(standard_match_fencer1_only, standard_match_fencer2_only):
    assert not standard_match_fencer1_only.has_both_fencers()
    assert not standard_match_fencer2_only.has_both_fencers()

def test_match_has_both_fencers_both_present(standard_match_fencers):
    assert standard_match_fencers.has_both_fencers()

def test_match_is_complete(standard_match_no_fencers):
    assert standard_match_no_fencers.has_not_started()
    standard_match_no_fencers.mark_complete()
    assert standard_match_no_fencers.is_complete()

def test_match_is_incomplete(standard_match_no_fencers):
    assert standard_match_no_fencers.has_not_started()
    assert standard_match_no_fencers.is_incomplete()
    standard_match_no_fencers.mark_complete()
    assert standard_match_no_fencers.is_complete()
    assert not standard_match_no_fencers.is_incomplete()

def test_match_has_reached_score_to_win(standard_match_no_fencers):
    standard_match_no_fencers.start()
    assert not standard_match_no_fencers.has_reached_score_to_win()
    standard_match_no_fencers.set_score(TEST_SCORE_TO_WIN, TEST_SCORE_TO_WIN - 1)
    assert standard_match_no_fencers.has_reached_score_to_win()
    assert standard_match_no_fencers.is_in_progress()


# --- State Transition Method Tests ---
def test_match_start(standard_match_no_fencers):
    assert standard_match_no_fencers.score1 is None
    assert standard_match_no_fencers.score2 is None
    assert standard_match_no_fencers.status == MatchStatus.NOT_STARTED
    standard_match_no_fencers.start()
    assert standard_match_no_fencers.score1 == 0
    assert standard_match_no_fencers.score2 == 0
    assert standard_match_no_fencers.status == MatchStatus.IN_PROGRESS

def test_match_start_cannot_start_match_already_in_progress(standard_match_no_fencers):
    standard_match_no_fencers.start()
    with pytest.raises(ValueError):
        standard_match_no_fencers.start()

def test_match_start_cannot_restart_completed_match(standard_match_no_fencers):
    standard_match_no_fencers.record_score(TEST_SCORE_TO_WIN, TEST_SCORE_TO_WIN - 1)
    with pytest.raises(ValueError):
        standard_match_no_fencers.start()

def test_match_restart(standard_match_no_fencers):
    standard_match_no_fencers.start()
    standard_match_no_fencers.touch1()
    standard_match_no_fencers.touch2()
    assert standard_match_no_fencers.score1 == 1
    assert standard_match_no_fencers.score2 == 1
    standard_match_no_fencers.restart()
    assert standard_match_no_fencers.score1 == 0
    assert standard_match_no_fencers.score2 == 0
    assert standard_match_no_fencers.status == MatchStatus.IN_PROGRESS

def test_match_reset(standard_match_no_fencers):
    standard_match_no_fencers.start()
    standard_match_no_fencers.touch1()
    standard_match_no_fencers.touch2()
    assert standard_match_no_fencers.score1 == 1
    assert standard_match_no_fencers.score2 == 1
    standard_match_no_fencers.reset()
    assert standard_match_no_fencers.score1 is None
    assert standard_match_no_fencers.score2 is None
    assert standard_match_no_fencers.status == MatchStatus.NOT_STARTED

def test_match_mark_complete(standard_match_no_fencers):
    assert standard_match_no_fencers.status == MatchStatus.NOT_STARTED
    standard_match_no_fencers.mark_complete()
    assert standard_match_no_fencers.status == MatchStatus.COMPLETED

def test_match_mark_complete_allows_non_tied_scores(standard_match_no_fencers):
    standard_match_no_fencers.start()
    standard_match_no_fencers.set_score(3, 2)
    standard_match_no_fencers.mark_complete()
    assert standard_match_no_fencers.status == MatchStatus.COMPLETED

def test_match_mark_complete_rejects_tied_scores(standard_match_no_fencers):
    standard_match_no_fencers.start()
    standard_match_no_fencers.set_score(3, 3)
    with pytest.raises(ValueError):
        standard_match_no_fencers.mark_complete()

def test_match_mark_complete_rejects_only_score1_present(standard_match_no_fencers):
    standard_match_no_fencers.score1 = 1
    standard_match_no_fencers.score2 = None
    with pytest.raises(ValueError):
        standard_match_no_fencers.mark_complete()

def test_match_mark_complete_rejects_only_score2_present(standard_match_no_fencers):
    standard_match_no_fencers.score1 = None
    standard_match_no_fencers.score2 = 1
    with pytest.raises(ValueError):
        standard_match_no_fencers.mark_complete()

def test_match_end(standard_match_no_fencers):
    standard_match_no_fencers.start()
    standard_match_no_fencers.touch1()
    standard_match_no_fencers.end()
    assert standard_match_no_fencers.status == MatchStatus.COMPLETED

def test_match_end_requires_match_in_progress(standard_match_no_fencers):
    with pytest.raises(ValueError):
        standard_match_no_fencers.end()

def test_match_end_rejects_tied_score(standard_match_no_fencers):
    standard_match_no_fencers.start()
    standard_match_no_fencers.set_score(2, 2)
    with pytest.raises(ValueError):
        standard_match_no_fencers.end()


# --- Live Score Update Method Tests ---
def test_match_touch1(standard_match_no_fencers):
    standard_match_no_fencers.start()
    assert standard_match_no_fencers.score1 == 0
    standard_match_no_fencers.touch1()
    assert standard_match_no_fencers.score1 == 1
    standard_match_no_fencers.touch1()
    assert standard_match_no_fencers.score1 == 2
    for _ in range(TEST_SCORE_TO_WIN-2):
        standard_match_no_fencers.touch1()
    assert standard_match_no_fencers.score1 == TEST_SCORE_TO_WIN
    with pytest.raises(ValueError):
        standard_match_no_fencers.touch1()

def test_match_touch1_requires_match_in_progress_before_start(standard_match_no_fencers):
    with pytest.raises(ValueError):
        standard_match_no_fencers.touch1()

def test_match_touch1_requires_match_in_progress_after_completion(standard_match_no_fencers):
    standard_match_no_fencers.record_score(TEST_SCORE_TO_WIN, TEST_SCORE_TO_WIN - 1)
    with pytest.raises(ValueError):
        standard_match_no_fencers.touch1()

def test_match_subtract1(standard_match_no_fencers):
    standard_match_no_fencers.start()
    assert standard_match_no_fencers.score1 == 0
    standard_match_no_fencers.touch1()
    standard_match_no_fencers.touch1()
    assert standard_match_no_fencers.score1 == 2
    standard_match_no_fencers.subtract1()
    assert standard_match_no_fencers.score1 == 1
    standard_match_no_fencers.subtract1()
    assert standard_match_no_fencers.score1 == 0
    with pytest.raises(ValueError):
        standard_match_no_fencers.subtract1()

def test_match_subtract1_requires_match_in_progress_before_start(standard_match_no_fencers):
    with pytest.raises(ValueError):
        standard_match_no_fencers.subtract1()

def test_match_subtract1_requires_match_in_progress_after_completion(standard_match_no_fencers):
    standard_match_no_fencers.record_score(TEST_SCORE_TO_WIN, TEST_SCORE_TO_WIN - 1)
    with pytest.raises(ValueError):
        standard_match_no_fencers.subtract1()

def test_match_touch2(standard_match_no_fencers):
    standard_match_no_fencers.start()
    assert standard_match_no_fencers.score2 == 0
    standard_match_no_fencers.touch2()
    assert standard_match_no_fencers.score2 == 1
    standard_match_no_fencers.touch2()
    assert standard_match_no_fencers.score2 == 2
    for _ in range(TEST_SCORE_TO_WIN-2):
        standard_match_no_fencers.touch2()
    assert standard_match_no_fencers.score2 == TEST_SCORE_TO_WIN
    with pytest.raises(ValueError):
        standard_match_no_fencers.touch2()

def test_match_touch2_requires_match_in_progress_before_start(standard_match_no_fencers):
    with pytest.raises(ValueError):
        standard_match_no_fencers.touch2()

def test_match_touch2_requires_match_in_progress_after_completion(standard_match_no_fencers):
    standard_match_no_fencers.record_score(TEST_SCORE_TO_WIN, TEST_SCORE_TO_WIN - 1)
    with pytest.raises(ValueError):
        standard_match_no_fencers.touch2()

def test_match_subtract2(standard_match_no_fencers):
    standard_match_no_fencers.start()
    assert standard_match_no_fencers.score2 == 0
    standard_match_no_fencers.touch2()
    standard_match_no_fencers.touch2()
    assert standard_match_no_fencers.score2 == 2
    standard_match_no_fencers.subtract2()
    assert standard_match_no_fencers.score2 == 1
    standard_match_no_fencers.subtract2()
    assert standard_match_no_fencers.score2 == 0
    with pytest.raises(ValueError):
        standard_match_no_fencers.subtract2()

def test_match_subtract2_requires_match_in_progress_before_start(standard_match_no_fencers):
    with pytest.raises(ValueError):
        standard_match_no_fencers.subtract2()

def test_match_subtract2_requires_match_in_progress_after_completion(standard_match_no_fencers):
    standard_match_no_fencers.record_score(TEST_SCORE_TO_WIN, TEST_SCORE_TO_WIN - 1)
    with pytest.raises(ValueError):
        standard_match_no_fencers.subtract2()

def test_match_set_score(standard_match_no_fencers):
    standard_match_no_fencers.start()
    standard_match_no_fencers.set_score(score1=TEST_SCORE_TO_WIN-1, score2=TEST_SCORE_TO_WIN-2)
    assert standard_match_no_fencers.score1 == TEST_SCORE_TO_WIN-1
    assert standard_match_no_fencers.score2 == TEST_SCORE_TO_WIN-2
    assert standard_match_no_fencers.is_in_progress()

def test_match_set_score_requires_in_progress_before_start(standard_match_no_fencers):
    with pytest.raises(ValueError):
        standard_match_no_fencers.set_score(1, 0)

def test_match_set_score_requires_in_progress_after_completion(standard_match_no_fencers):
    standard_match_no_fencers.record_score(TEST_SCORE_TO_WIN, TEST_SCORE_TO_WIN - 1)
    with pytest.raises(ValueError):
        standard_match_no_fencers.set_score(1, 0)

@pytest.mark.parametrize('invalid_score_type', [None, 'one', 1.0, False, [], {}])
def test_match_set_score_invalid_score_type(standard_match_no_fencers, invalid_score_type):
    standard_match_no_fencers.start()

    with pytest.raises(TypeError):
        standard_match_no_fencers.set_score(invalid_score_type, 0)

    with pytest.raises(TypeError):
        standard_match_no_fencers.set_score(0, invalid_score_type)

@pytest.mark.parametrize('score_out_of_bounds', [-1, TEST_SCORE_TO_WIN + 1])
def test_match_set_score_invalid_score_value(standard_match_no_fencers, score_out_of_bounds):
    standard_match_no_fencers.start()

    with pytest.raises(ValueError):
        standard_match_no_fencers.set_score(score_out_of_bounds, 0)

    with pytest.raises(ValueError):
        standard_match_no_fencers.set_score(0, score_out_of_bounds)

def test_match_set_score_allows_tie(standard_match_no_fencers):
    standard_match_no_fencers.start()
    standard_match_no_fencers.set_score(3, 3)

    assert standard_match_no_fencers.score() == (3, 3)
    assert standard_match_no_fencers.is_in_progress()


# --- Score Recording Method Tests ---
def test_match_record_score_without_fencers(standard_match_no_fencers):
    assert standard_match_no_fencers.score1 is None
    assert standard_match_no_fencers.score2 is None
    standard_match_no_fencers.record_score(score1=TEST_SCORE_TO_WIN, score2=TEST_SCORE_TO_WIN-2)
    assert standard_match_no_fencers.score1 == TEST_SCORE_TO_WIN
    assert standard_match_no_fencers.score2 == TEST_SCORE_TO_WIN-2
    assert standard_match_no_fencers.status == MatchStatus.COMPLETED

def test_match_record_score_with_fencers(standard_match_fencers):
    assert standard_match_fencers.score1 is None
    assert standard_match_fencers.score2 is None
    standard_match_fencers.record_score(score1=TEST_SCORE_TO_WIN-1, score2=TEST_SCORE_TO_WIN)
    assert standard_match_fencers.score1 == TEST_SCORE_TO_WIN-1
    assert standard_match_fencers.score2 == TEST_SCORE_TO_WIN
    assert standard_match_fencers.status == MatchStatus.COMPLETED

def test_match_record_score_can_overwrite_previous_result(standard_match_no_fencers):
    standard_match_no_fencers.record_score(TEST_SCORE_TO_WIN, TEST_SCORE_TO_WIN - 1)
    assert standard_match_no_fencers.score() == (TEST_SCORE_TO_WIN, TEST_SCORE_TO_WIN - 1)

    standard_match_no_fencers.record_score(TEST_SCORE_TO_WIN - 2, TEST_SCORE_TO_WIN)
    assert standard_match_no_fencers.score() == (TEST_SCORE_TO_WIN - 2, TEST_SCORE_TO_WIN)
    assert standard_match_no_fencers.status == MatchStatus.COMPLETED
    assert standard_match_no_fencers.winner_index() == 1

@pytest.mark.parametrize('invalid_score_type', [None, 'one', 1.0, False, [], {}])
def test_match_record_score_invalid_score_type(standard_match_no_fencers, invalid_score_type):
    with pytest.raises(TypeError):
        standard_match_no_fencers.record_score(score1=invalid_score_type, score2=0)
    with pytest.raises(TypeError):
        standard_match_no_fencers.record_score(score1=0, score2=invalid_score_type)
    with pytest.raises(TypeError):
        standard_match_no_fencers.record_score(score1=invalid_score_type, score2=invalid_score_type)    

@pytest.mark.parametrize('score_out_of_bounds', [-2*TEST_SCORE_TO_WIN, -1, TEST_SCORE_TO_WIN+1, 2*TEST_SCORE_TO_WIN])
def test_match_record_score_invalid_score_value(standard_match_no_fencers, score_out_of_bounds):
    with pytest.raises(ValueError):
        standard_match_no_fencers.record_score(score1=score_out_of_bounds ,score2=0)
    with pytest.raises(ValueError):
        standard_match_no_fencers.record_score(score1=0 ,score2=score_out_of_bounds)
    with pytest.raises(ValueError):
        standard_match_no_fencers.record_score(score1=score_out_of_bounds ,score2=score_out_of_bounds)

@pytest.mark.parametrize('score', [0, 1, TEST_SCORE_TO_WIN - 1, TEST_SCORE_TO_WIN])
def test_match_record_score_rejects_tie(standard_match_no_fencers, score):
    with pytest.raises(ValueError):
        standard_match_no_fencers.record_score(score, score)


# --- Result Query Method Tests ---
def test_match_score(standard_match_no_fencers):
    assert standard_match_no_fencers.score() == (None, None)
    standard_match_no_fencers.record_score(score1=TEST_SCORE_TO_WIN-1, score2=TEST_SCORE_TO_WIN-2)
    assert standard_match_no_fencers.score() == (TEST_SCORE_TO_WIN-1, TEST_SCORE_TO_WIN-2)


def test_match_leader_index(standard_match_no_fencers):
    assert standard_match_no_fencers.leader_index() is None

    standard_match_no_fencers.start()
    assert standard_match_no_fencers.leader_index() is None

    standard_match_no_fencers.touch1()
    assert standard_match_no_fencers.leader_index() == 0

    standard_match_no_fencers.touch2()
    standard_match_no_fencers.touch2()
    assert standard_match_no_fencers.leader_index() == 1

def test_match_winner_index_normal_0_wins(standard_match_no_fencers):
    assert standard_match_no_fencers.winner_index() is None
    standard_match_no_fencers.record_score(score1=TEST_SCORE_TO_WIN-1, score2=TEST_SCORE_TO_WIN-2)
    assert standard_match_no_fencers.winner_index() == 0

def test_match_winner_index_normal_1_wins(standard_match_no_fencers):
    assert standard_match_no_fencers.winner_index() is None
    standard_match_no_fencers.record_score(score1=TEST_SCORE_TO_WIN-1, score2=TEST_SCORE_TO_WIN)
    assert standard_match_no_fencers.winner_index() == 1

def test_match_winner_index_complete_no_scores_returns_none(standard_match_no_fencers):
    standard_match_no_fencers.mark_complete()
    assert standard_match_no_fencers.winner_index() is None

def test_match_winner_index_raises_if_completed_match_is_tied(standard_match_no_fencers):
    standard_match_no_fencers.status = MatchStatus.COMPLETED
    standard_match_no_fencers.score1 = 3
    standard_match_no_fencers.score2 = 3
    with pytest.raises(ValueError):
        standard_match_no_fencers.winner_index()

def test_match_loser_index_normal_0_loses(standard_match_no_fencers):
    assert standard_match_no_fencers.loser_index() is None
    standard_match_no_fencers.record_score(score1=TEST_SCORE_TO_WIN-2, score2=TEST_SCORE_TO_WIN)
    assert standard_match_no_fencers.loser_index() == 0

def test_match_loser_index_normal_1_loses(standard_match_no_fencers):
    assert standard_match_no_fencers.loser_index() is None
    standard_match_no_fencers.record_score(score1=TEST_SCORE_TO_WIN-1, score2=TEST_SCORE_TO_WIN-2)
    assert standard_match_no_fencers.loser_index() == 1

def test_match_loser_index_complete_no_scores_returns_none(standard_match_no_fencers):
    standard_match_no_fencers.mark_complete()
    assert standard_match_no_fencers.loser_index() is None

def test_match_loser_index_raises_if_completed_match_is_tied(standard_match_no_fencers):
    standard_match_no_fencers.status = MatchStatus.COMPLETED
    standard_match_no_fencers.score1 = 3
    standard_match_no_fencers.score2 = 3
    with pytest.raises(ValueError):
        standard_match_no_fencers.loser_index()

def test_match_winner_fencer_fencer1_wins(standard_match_fencers):
    standard_match_fencers.record_score(score1=TEST_SCORE_TO_WIN, score2=TEST_SCORE_TO_WIN-1)
    assert standard_match_fencers.winner_fencer() == standard_match_fencers.fencer1

def test_match_winner_fencer_fencer2_wins(standard_match_fencers):
    standard_match_fencers.record_score(score1=TEST_SCORE_TO_WIN-2, score2=TEST_SCORE_TO_WIN-1)
    assert standard_match_fencers.winner_fencer() == standard_match_fencers.fencer2

def test_match_winner_fencer_fencer_not_present(standard_match_no_fencers):
    standard_match_no_fencers.record_score(score1=TEST_SCORE_TO_WIN, score2=TEST_SCORE_TO_WIN-1)
    assert standard_match_no_fencers.winner_fencer() is None

def test_match_winner_fencer_returns_known_fencer_when_other_slot_is_none(standard_match_fencer1_only):
    standard_match_fencer1_only.record_score(TEST_SCORE_TO_WIN, TEST_SCORE_TO_WIN - 1)
    assert standard_match_fencer1_only.winner_fencer() == standard_match_fencer1_only.fencer1

def test_match_winner_fencer_returns_none_when_winning_slot_is_none(standard_match_fencer1_only):
    standard_match_fencer1_only.record_score(TEST_SCORE_TO_WIN - 1, TEST_SCORE_TO_WIN)
    assert standard_match_fencer1_only.winner_fencer() is None

def test_match_loser_fencer_fencer1_loses(standard_match_fencers):
    standard_match_fencers.record_score(score1=TEST_SCORE_TO_WIN-2, score2=TEST_SCORE_TO_WIN)
    assert standard_match_fencers.loser_fencer() == standard_match_fencers.fencer1

def test_match_loser_fencer_fencer2_loses(standard_match_fencers):
    standard_match_fencers.record_score(score1=TEST_SCORE_TO_WIN, score2=TEST_SCORE_TO_WIN-1)
    assert standard_match_fencers.loser_fencer() == standard_match_fencers.fencer2

def test_match_loser_fencer_fencer_not_present(standard_match_no_fencers):
    standard_match_no_fencers.record_score(score1=TEST_SCORE_TO_WIN, score2=TEST_SCORE_TO_WIN-1)
    assert standard_match_no_fencers.loser_fencer() is None

def test_match_loser_fencer_returns_known_fencer_when_other_slot_is_none(standard_match_fencer2_only):
    standard_match_fencer2_only.record_score(TEST_SCORE_TO_WIN, TEST_SCORE_TO_WIN - 1)
    assert standard_match_fencer2_only.loser_fencer() == standard_match_fencer2_only.fencer2

def test_match_loser_fencer_returns_none_when_losing_slot_is_none(standard_match_fencer2_only):
    standard_match_fencer2_only.record_score(TEST_SCORE_TO_WIN - 1, TEST_SCORE_TO_WIN)
    assert standard_match_fencer2_only.loser_fencer() is None