import pytest

from poules.results.poule_result import _PouleEntryStats


# --- Constants ---
INVALID_SCORE_VALUES = [-15, -10, -5, -1]

# --- Fixtures ---
@pytest.fixture
def entry_stats():
    return _PouleEntryStats()


# --- Initialization and Validation Tests ---
def test__poule_entry_stats_creation_valid():
    entry_stats = _PouleEntryStats()

    assert entry_stats.num_matches == 0
    assert entry_stats.num_victories == 0
    assert entry_stats.touches_scored == 0
    assert entry_stats.touches_received == 0


# --- Property Tests ---
def test__poule_entry_stats_stats_property(entry_stats):
    assert entry_stats.stats == (0, 0, 0, 0)

    entry_stats.add_match_info(True, 5, 2)
    
    assert entry_stats.stats == (1, 1, 5, 2)

    entry_stats.add_match_info(False, 3, 5)
    
    assert entry_stats.stats == (2, 1, 8, 7)


# --- Stat Update Method Tests ---
def test__poule_entry_stats_add_match_info_valid_defeat(entry_stats):
    entry_stats.add_match_info(False, 1, 5)

    assert entry_stats.num_matches == 1
    assert entry_stats.num_victories == 0
    assert entry_stats.touches_scored == 1
    assert entry_stats.touches_received == 5

def test__poule_entry_stats_add_match_info_valid_victory(entry_stats):
    entry_stats.add_match_info(True, 4, 2)

    assert entry_stats.num_matches == 1
    assert entry_stats.num_victories == 1
    assert entry_stats.touches_scored == 4
    assert entry_stats.touches_received == 2

@pytest.mark.parametrize(
        ('is_victory', 'touches_scored', 'touches_received'),
        [
            (True, 1, 0),
            (False, 0, 1),
            (True, 5, 4),
            (False, 4, 5)
        ]
)
def test__poule_entry_stats_add_match_info_valid_boundary_scores(entry_stats, is_victory, touches_scored, touches_received):
    entry_stats.add_match_info(is_victory, touches_scored, touches_received)

    assert entry_stats.stats == (1, int(is_victory), touches_scored, touches_received)

def test__poule_entry_stats_add_match_info_valid_cumulative(entry_stats):
    entry_stats.add_match_info(False, 4, 5)

    assert entry_stats.num_matches == 1
    assert entry_stats.num_victories == 0
    assert entry_stats.touches_scored == 4
    assert entry_stats.touches_received == 5

    entry_stats.add_match_info(True, 5, 3)

    assert entry_stats.num_matches == 2
    assert entry_stats.num_victories == 1
    assert entry_stats.touches_scored == 9
    assert entry_stats.touches_received == 8

    entry_stats.add_match_info(True, 5, 4)

    assert entry_stats.num_matches == 3
    assert entry_stats.num_victories == 2
    assert entry_stats.touches_scored == 14
    assert entry_stats.touches_received == 12


@pytest.mark.parametrize(
        ('is_victory', 'touches_scored', 'touches_received', 'exception_type'),
        [
            (True, 2, 3, ValueError),
            (False, -1, 3, ValueError),
            (True, 4, None, TypeError)
        ]
)
def test__poule_entry_stats_add_match_info_invalid_does_not_update_stats(entry_stats, is_victory, touches_scored, touches_received, exception_type):
    entry_stats.add_match_info(True, 5, 2)
    
    original_stats = entry_stats.stats

    with pytest.raises(exception_type):
        entry_stats.add_match_info(is_victory, touches_scored, touches_received)

    assert entry_stats.stats == original_stats

@pytest.mark.parametrize('invalid_is_victory_type', [None, 'yes', 0, 1.0, [0], (1,), {}])
def test__poule_entry_stats_add_match_info_invalid_is_victory_type(entry_stats, invalid_is_victory_type):
    with pytest.raises(TypeError):
        entry_stats.add_match_info(invalid_is_victory_type, 1, 0)

@pytest.mark.parametrize('invalid_touches_scored_type', [None, 5.0, 'two', True, [7], (1,), {}])
def test__poule_entry_stats_add_match_info_invalid_touches_scored_type(entry_stats, invalid_touches_scored_type):
    with pytest.raises(TypeError):
        entry_stats.add_match_info(True, invalid_touches_scored_type, 0)

@pytest.mark.parametrize('invalid_touches_scored_value', INVALID_SCORE_VALUES)
def test__poule_entry_stats_add_match_info_invalid_touches_scored_value(entry_stats, invalid_touches_scored_value):
    with pytest.raises(ValueError):
        entry_stats.add_match_info(False, invalid_touches_scored_value, 0)

@pytest.mark.parametrize('invalid_touches_received_type', [None, 5.0, 'two', True, [7], (1,), {}])
def test__poule_entry_stats_add_match_info_invalid_touches_received_type(entry_stats, invalid_touches_received_type):
    with pytest.raises(TypeError):
        entry_stats.add_match_info(False, 0, invalid_touches_received_type)

@pytest.mark.parametrize('invalid_touches_received_value', INVALID_SCORE_VALUES)
def test__poule_entry_stats_add_match_info_invalid_touches_received_value(entry_stats, invalid_touches_received_value):
    with pytest.raises(ValueError):
        entry_stats.add_match_info(True, 0, invalid_touches_received_value)

@pytest.mark.parametrize(('touches_scored', 'touches_received'), [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])
def test__poule_entry_stats_add_match_info_invalid_tied_score(entry_stats, touches_scored, touches_received):
    with pytest.raises(ValueError):
        entry_stats.add_match_info(False, touches_scored, touches_received)

    with pytest.raises(ValueError):
        entry_stats.add_match_info(True, touches_scored, touches_received)

@pytest.mark.parametrize(('touches_scored', 'touches_received'), [(0, 5), (1, 4), (2, 3), (3, 5), (4, 5)])
def test__poule_entry_stats_add_match_info_invalid_victory_score(entry_stats, touches_scored, touches_received):
    with pytest.raises(ValueError):
        entry_stats.add_match_info(True, touches_scored, touches_received)

@pytest.mark.parametrize(('touches_scored', 'touches_received'), [(5, 0), (4, 1), (3, 2), (5, 3), (5, 4)])
def test__poule_entry_stats_add_match_info_invalid_defeat_score(entry_stats, touches_scored, touches_received):
    with pytest.raises(ValueError):
        entry_stats.add_match_info(False, touches_scored, touches_received)