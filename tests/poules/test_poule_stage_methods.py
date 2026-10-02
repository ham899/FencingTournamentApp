import pytest

import factories

from poules.poule_stage import PouleStage


# --- Constants ---
from constants import TOURNY_ID1

RANDOM_SEED = 36

INVALID_SCORES_TYPES = [None, False, True, 0.0, 5.0, '15', [], (), {}]
INVALID_SCORES_VALUES = [-100, -1, 6, 100]

INVALID_INDEX_TYPES = [None, False, True, 0.0, 1.0, 'first', [], (), {}]

# Both constant lists below assume 3 poules of 7 entries
INVALID_POULE_INDEX_VALUES = [-100, -1, 3, 100]
INVALID_MATCH_INDEX_VALUES = [-100, -1, 21, 100]


# --- Fixtures ---
@pytest.fixture
def entries():
    return factories.make_entries(n=21, tournament_id=TOURNY_ID1)

@pytest.fixture
def seeded_entries():
    return factories.make_seeded_entries(n=21, tournament_id=TOURNY_ID1)

@pytest.fixture
def poule_stage(seeded_entries):
    return PouleStage(stage_number=1, seeded_entries=seeded_entries)

@pytest.fixture
def poule1_scores():
    return ((5,3), (5,1), (0,5), (4,5), (2,5), (5,0), (5,0), 
            (5,2), (4,5), (5,3), (5,3), (1,5), (2,5), (3,5), 
            (4,5), (0,5), (5,4), (2,5), (5,4), (3,5), (5,1))

@pytest.fixture
def poule2_scores():
    return ((3,5), (2,5), (5,4), (5,0), (4,5), (1,5), (3,5), 
            (5,1), (5,4), (5,3), (5,2), (5,2), (5,1), (5,2), 
            (5,3), (5,4), (2,5), (3,5), (0,5), (5,4), (4,5))
    
@pytest.fixture
def poule3_scores():
    return ((5,0), (5,3), (4,5), (2,5), (5,2), (5,3), (5,4), 
            (2,5), (3,5), (5,3), (5,4), (0,5), (2,5), (0,5), 
            (5,4), (5,4), (5,1), (5,2), (5,1), (5,4), (4,5))

@pytest.fixture
def poule_scores(poule1_scores, poule2_scores, poule3_scores):
    return (poule1_scores, poule2_scores, poule3_scores)

@pytest.fixture
def expected_poule_stage_results():
    return (
        'Catherine', 'Hannah', 'Sarah', 'Jill', 'Joanna', 'Jack', 'Jane',
        'Emily', 'Isabella', 'Edward', 'John', 'Jessica', 'Albert', 'Stephen',
        'Parsa', 'Dave', 'Steve', 'Robert', 'Michael', 'Peter', 'Chantelle'
    ) # Note: Jack/Joanna and Albert/Stephen are exact ties. Their displayed order is produced by RANDOM_SEED = 36.


# --- Predicate Method Tests ---
def test_poule_stage_has_started(poule_stage):
    assert not poule_stage.has_started()

    poule_stage.record_on_piste_match_score(1, 5, 0)

    assert poule_stage.has_started()

def test_poule_stage_is_complete(poule_stage):
    assert not poule_stage.is_complete()

    # Complete poule 1
    for _ in poule_stage.poules[0].matches:
        poule_stage.record_on_piste_match_score(0, 5, 0)

    assert not poule_stage.is_complete()

    # Complete poule 2 and 3
    for i, poule in enumerate(poule_stage.poules[1:], start=1):
        for _ in poule.matches:
            poule_stage.record_on_piste_match_score(i, 5, 0)

    assert poule_stage.is_complete()


# --- Poule Access Method Tests ---
def test_poule_stage_get_poule_at(poule_stage):
    assert poule_stage.get_poule_at(0) is poule_stage.poules[0]
    assert poule_stage.get_poule_at(1) is poule_stage.poules[1]
    assert poule_stage.get_poule_at(2) is poule_stage.poules[2]

@pytest.mark.parametrize('invalid_index_type', INVALID_INDEX_TYPES)
def test_poule_stage_get_poule_at_invalid_index_type(poule_stage, invalid_index_type):
    with pytest.raises(TypeError):
        poule_stage.get_poule_at(invalid_index_type)

@pytest.mark.parametrize('invalid_index_value', INVALID_POULE_INDEX_VALUES)
def test_poule_stage_get_poule_at_invalid_index_value(poule_stage, invalid_index_value):
    with pytest.raises(ValueError):
        poule_stage.get_poule_at(invalid_index_value)

def test_poule_stage_get_match_at(poule_stage):
    for i, poule in enumerate(poule_stage.poules):
        for j, match in enumerate(poule.matches):
            assert poule_stage.get_match_at(i, j) is match

@pytest.mark.parametrize('invalid_poule_index_type', INVALID_INDEX_TYPES)
def test_poule_stage_get_match_invalid_poule_index_type(poule_stage, invalid_poule_index_type):
    with pytest.raises(TypeError):
        poule_stage.get_match_at(invalid_poule_index_type, 0)

@pytest.mark.parametrize('invalid_poule_index_value', INVALID_POULE_INDEX_VALUES)
def test_poule_stage_get_match_invalid_poule_index_value(poule_stage, invalid_poule_index_value):
    with pytest.raises(ValueError):
        poule_stage.get_match_at(invalid_poule_index_value, 0)

@pytest.mark.parametrize('invalid_match_index_type', INVALID_INDEX_TYPES)
def test_poule_stage_get_match_invalid_match_index_type(poule_stage, invalid_match_index_type):
    with pytest.raises(TypeError):
        poule_stage.get_match_at(0, invalid_match_index_type)

@pytest.mark.parametrize('invalid_match_index_value', INVALID_MATCH_INDEX_VALUES)
def test_poule_stage_get_match_invalid_match_index_value(poule_stage, invalid_match_index_value):
    with pytest.raises(ValueError):
        poule_stage.get_match_at(0, invalid_match_index_value)

def test_poule_stage_get_on_piste_match(poule_stage):
    for i, poule in enumerate(poule_stage.poules):
        assert poule_stage.get_on_piste_match(i) is poule.matches[0]

@pytest.mark.parametrize('invalid_index_type', INVALID_INDEX_TYPES)
def test_poule_stage_get_on_piste_match_invalid_index_type(poule_stage, invalid_index_type):
    with pytest.raises(TypeError):
        poule_stage.get_on_piste_match(invalid_index_type)

@pytest.mark.parametrize('invalid_index_value', INVALID_POULE_INDEX_VALUES)
def test_poule_stage_get_on_piste_match_invalid_index_value(poule_stage, invalid_index_value):
    with pytest.raises(ValueError):
        poule_stage.get_on_piste_match(invalid_index_value)

def test_poule_stage_get_on_deck_match(poule_stage):
    for i, poule in enumerate(poule_stage.poules):
        assert poule_stage.get_on_deck_match(i) is poule.matches[1]

@pytest.mark.parametrize('invalid_index_type', INVALID_INDEX_TYPES)
def test_poule_stage_get_on_deck_match_invalid_index_type(poule_stage, invalid_index_type):
    with pytest.raises(TypeError):
        poule_stage.get_on_deck_match(invalid_index_type)

@pytest.mark.parametrize('invalid_index_value', INVALID_POULE_INDEX_VALUES)
def test_poule_stage_get_on_deck_match_invalid_index_value(poule_stage, invalid_index_value):
    with pytest.raises(ValueError):
        poule_stage.get_on_deck_match(invalid_index_value)


# --- Match Result Recording Method Tests ---
def test_poule_stage_record_match_score(poule_stage):
    poule_index, match_index = 2, 10

    match = poule_stage.get_match_at(poule_index, match_index)

    assert match.is_incomplete()
    
    poule_stage.record_match_score(poule_index, match_index, 5, 0)

    assert match.is_complete()
    assert match.score1 == 5
    assert match.score2 == 0

@pytest.mark.parametrize('invalid_poule_index_type', INVALID_INDEX_TYPES)
def test_poule_stage_record_match_score_invalid_poule_index_type(poule_stage, invalid_poule_index_type):
            with pytest.raises(TypeError):
                poule_stage.record_match_score(invalid_poule_index_type, 0, 5, 0)

@pytest.mark.parametrize('invalid_poule_index_value', INVALID_POULE_INDEX_VALUES)
def test_poule_stage_record_match_score_invalid_poule_index_value(poule_stage, invalid_poule_index_value):
    with pytest.raises(ValueError):
        poule_stage.record_match_score(invalid_poule_index_value, 0, 5, 0)

@pytest.mark.parametrize('invalid_match_index_type', INVALID_INDEX_TYPES)
def test_poule_stage_record_match_score_invalid_match_index_type(poule_stage, invalid_match_index_type):
    with pytest.raises(TypeError):
        poule_stage.record_match_score(0, invalid_match_index_type, 5, 0)

@pytest.mark.parametrize('invalid_match_index_value', INVALID_MATCH_INDEX_VALUES)
def test_poule_stage_record_match_score_invalid_match_index_value(poule_stage, invalid_match_index_value):
    with pytest.raises(ValueError):
        poule_stage.record_match_score(0, invalid_match_index_value, 5, 0)

@pytest.mark.parametrize('invalid_scores_type', INVALID_SCORES_TYPES)
def test_poule_stage_record_match_score_invalid_scores_type(poule_stage, invalid_scores_type):
    with pytest.raises(TypeError):
        poule_stage.record_match_score(0, 0, invalid_scores_type, 0)

    with pytest.raises(TypeError):
        poule_stage.record_match_score(0, 0, 5, invalid_scores_type)

@pytest.mark.parametrize('invalid_scores_value', INVALID_SCORES_VALUES)
def test_poule_stage_record_match_score_invalid_scores_value(poule_stage, invalid_scores_value):
    with pytest.raises(ValueError):
        poule_stage.record_match_score(0, 0, invalid_scores_value, 0)

    with pytest.raises(ValueError):
        poule_stage.record_match_score(0, 0, 5, invalid_scores_value)

def test_poule_stage_record_on_piste_match_score(poule_stage):
    poule_index = 1
    
    match = poule_stage.get_match_at(poule_index, 0)

    assert match.is_incomplete()

    poule_stage.record_on_piste_match_score(poule_index, 0, 5)

    assert match.is_complete()
    assert match.score1 == 0
    assert match.score2 == 5

@pytest.mark.parametrize('invalid_poule_index_type', INVALID_INDEX_TYPES)
def test_poule_stage_record_on_piste_match_score_invalid_poule_index_type(poule_stage, invalid_poule_index_type):
    with pytest.raises(TypeError):
        poule_stage.record_on_piste_match_score(invalid_poule_index_type, 5, 0)

@pytest.mark.parametrize('invalid_poule_index_value', INVALID_POULE_INDEX_VALUES)
def test_poule_stage_record_on_piste_match_score_invalid_poule_index_value(poule_stage, invalid_poule_index_value):
    with pytest.raises(ValueError):
        poule_stage.record_on_piste_match_score(invalid_poule_index_value, 5, 0)

@pytest.mark.parametrize('invalid_scores_type', INVALID_SCORES_TYPES)
def test_poule_stage_record_on_piste_match_score_invalid_scores_type(poule_stage, invalid_scores_type):
    with pytest.raises(TypeError):
        poule_stage.record_on_piste_match_score(0, invalid_scores_type, 0)

    with pytest.raises(TypeError):
        poule_stage.record_on_piste_match_score(0, 0, invalid_scores_type)

@pytest.mark.parametrize('invalid_scores_value', INVALID_SCORES_VALUES)
def test_poule_stage_record_on_piste_match_score_scores_value(poule_stage, invalid_scores_value):
    with pytest.raises(ValueError):
        poule_stage.record_on_piste_match_score(0, invalid_scores_value, 0)

    with pytest.raises(ValueError):
        poule_stage.record_on_piste_match_score(0, 5, invalid_scores_value)

def test_poule_stage_record_on_piste_match_score_complete_poule(poule_stage):
    for _ in poule_stage.poules[0].matches:
        poule_stage.record_on_piste_match_score(0, 5, 0)

    with pytest.raises(RuntimeError, match='already complete'):
        poule_stage.record_on_piste_match_score(0, 5, 0)

def test_poule_stage_replace_with_score(poule_stage):
    poule_index, match_index = 0, 4

    match = poule_stage.get_match_at(poule_index, match_index)

    poule_stage.record_forfeit(poule_index, match_index, 1)

    assert match.is_complete()
    assert match.is_forfeit()
    assert match.forfeited_index == 1

    poule_stage.replace_with_score(poule_index, match_index, 5, 3)

    assert match.is_complete()
    assert not match.is_forfeit()
    assert match.forfeited_index is None
    assert match.score == (5, 3)

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_poule_stage_record_forfeit(poule_stage, forfeiting_index):
    poule_index, match_index = 1, 3

    match = poule_stage.get_match_at(poule_index, match_index)

    assert match.is_incomplete()

    poule_stage.record_forfeit(poule_index, match_index, forfeiting_index)

    assert match.is_complete()
    assert match.forfeited_index == forfeiting_index
    assert match.is_forfeit()

    assert match.score1 == (0 if forfeiting_index == 0 else poule_stage.score_to_win)
    assert match.score2 == (0 if forfeiting_index == 1 else poule_stage.score_to_win)

@pytest.mark.parametrize('forfeiting_index', [0, 1])
def test_poule_stage_replace_with_forfeit(poule_stage, forfeiting_index):
    poule_index = 2

    match = poule_stage.get_match_at(poule_index, 0)

    poule_stage.record_on_piste_match_score(poule_index, 5, 2)

    assert match.is_complete()
    assert not match.is_forfeit()
    assert match.score == (5, 2)

    poule_stage.replace_with_forfeit(poule_index, 0, forfeiting_index)

    assert match.is_complete()
    assert match.forfeited_index == forfeiting_index
    assert match.is_forfeit()

    assert match.score1 == (0 if forfeiting_index == 0 else poule_stage.score_to_win)
    assert match.score2 == (0 if forfeiting_index == 1 else poule_stage.score_to_win)


# --- Result Calculation Method Tests ---
def test_poule_stage_calculate_results(poule_stage, poule_scores, expected_poule_stage_results):    
    # Record the results for the first seven matches
    for match_index in range(7):
        for poule_index in range(len(poule_scores)):
            poule_stage.record_on_piste_match_score(poule_index, *poule_scores[poule_index][match_index])

    # Calculate the results after the first seven matches
    results_7 = poule_stage.calculate_results(RANDOM_SEED)

    # Validate the resutls after the first seven matches
    expected_results_7 = (
        (
            ('John', 2, 2, 10, 7, 1.0, 3), 
            ('Sarah', 2, 2, 10, 1, 1.0, 9), 
            ('Dave', 2, 0, 0, 10, 0.0, -10), 
            ('Jessica', 2, 1, 8, 7, 0.5, 1), 
            ('Edward', 2, 0, 3, 10, 0.0, -7), 
            ('Catherine', 2, 2, 10, 0, 1.0, 10), 
            ('Peter', 2, 0, 4, 10, 0.0, -6)
        ),
        (
            ('Steve', 2, 0, 3, 10, 0.0, -7), 
            ('Michael', 2, 0, 3, 10, 0.0, -7), 
            ('Jill', 2, 2, 10, 5, 1.0, 5), 
            ('Jack', 2, 2, 10, 7, 1.0, 3), 
            ('Jane', 2, 1, 9, 7, 0.5, 2), 
            ('Robert', 2, 0, 7, 10, 0.0, -3), 
            ('Isabella', 2, 2, 10, 3, 1.0, 7)
        ),
        (
            ('Hannah', 2, 2, 10, 2, 1.0, 8), 
            ('Emily', 2, 2, 10, 6, 1.0, 4), 
            ('Parsa', 2, 0, 7, 10, 0.0, -3), 
            ('Chantelle', 2, 0, 2, 10, 0.0, -8), 
            ('Stephen', 2, 1, 8, 7, 0.5, 1), 
            ('Joanna', 2, 2, 10, 8, 1.0, 2), 
            ('Albert', 2, 0, 6, 10, 0.0, -4)
        )
    )

    assert len(results_7.poule_results) == 3

    for i, poule_result in enumerate(results_7.poule_results):
        assert poule_result.poule_number == i + 1
        assert poule_result.tournament_id == TOURNY_ID1

        assert len(poule_result.entry_results) == 7

        for j, entry_result in enumerate(poule_result.entry_results):
            assert entry_result.poule_number == i + 1
            assert entry_result.tournament_id == TOURNY_ID1

            assert entry_result.entry.display_name == expected_results_7[i][j][0]
            assert entry_result.num_matches == expected_results_7[i][j][1]
            assert entry_result.num_victories == expected_results_7[i][j][2]
            assert entry_result.touches_scored == expected_results_7[i][j][3]
            assert entry_result.touches_received == expected_results_7[i][j][4]
            assert entry_result.victory_ratio == expected_results_7[i][j][5]
            assert entry_result.indicator == expected_results_7[i][j][6]
    
    # Finish the remaining matches
    for match_index in range(7, 21):
        for poule_index in range(len(poule_scores)):
            poule_stage.record_on_piste_match_score(poule_index, *poule_scores[poule_index][match_index])

    # Calculate the results for all the matches
    results_final = poule_stage.calculate_results(RANDOM_SEED)

    # Validate the results for all the matches
    expected_final_results = (
        (
            ('John', 6, 3, 20, 23, 0.5, -3), 
            ('Sarah', 6, 5, 28, 16, 5 / 6, 12), 
            ('Dave', 6, 2, 15, 26, 1 / 3, -11), 
            ('Jessica', 6, 2, 23, 23, 1 / 3, 0), 
            ('Edward', 6, 3, 22, 24, 0.5, -2), 
            ('Catherine', 6, 6, 30, 9, 1.0, 21), 
            ('Peter', 6, 0, 13, 30, 0.0, -17)
        ),
        (
            ('Steve', 6, 2, 16, 28, 1 / 3, -12), 
            ('Michael', 6, 0, 14, 30, 0.0, -16), 
            ('Jill', 6, 5, 29, 18, 5 / 6, 11), 
            ('Jack', 6, 5, 29, 19, 5 / 6, 10), 
            ('Jane', 6, 4, 27, 15, 2 / 3, 12), 
            ('Robert', 6, 1, 17, 28, 1 / 6, -11), 
            ('Isabella', 6, 4, 25, 19, 2 / 3, 6)
        ),
        (
            ('Hannah', 6, 6, 30, 12, 1.0, 18), 
            ('Emily', 6, 4, 27, 17, 2 / 3, 10), 
            ('Parsa', 6, 2, 19, 27, 1 / 3, -8), 
            ('Chantelle', 6, 0, 12, 30, 0.0, -18), 
            ('Stephen', 6, 2, 20, 26, 1 / 3, -6), 
            ('Joanna', 6, 5, 29, 19, 5 / 6, 10), 
            ('Albert', 6, 2, 20, 26, 1 / 3, -6)
        )
    )

    assert len(results_final.poule_results) == 3
    
    for i, poule_result in enumerate(results_final.poule_results):
        assert poule_result.poule_number == i + 1
        assert poule_result.tournament_id == TOURNY_ID1

        assert len(poule_result.entry_results) == 7

        for j, entry_result in enumerate(poule_result.entry_results):
            assert entry_result.poule_number == i + 1
            assert entry_result.tournament_id == TOURNY_ID1

            assert entry_result.entry.display_name == expected_final_results[i][j][0]
            assert entry_result.num_matches == expected_final_results[i][j][1]
            assert entry_result.num_victories == expected_final_results[i][j][2]
            assert entry_result.touches_scored == expected_final_results[i][j][3]
            assert entry_result.touches_received == expected_final_results[i][j][4]
            assert entry_result.victory_ratio == expected_final_results[i][j][5]
            assert entry_result.indicator == expected_final_results[i][j][6]
    
    # Validate the poule stage's final ranked results by name
    assert results_final.stage_results_display_names == expected_poule_stage_results

@pytest.mark.parametrize('invalid_random_seed_type', [False, True, '21', 64.3, [], (), {}])
def test_poule_stage_calculate_results_invalid_random_seed_type(poule_stage, invalid_random_seed_type):
    with pytest.raises(TypeError):
        poule_stage.calculate_results(invalid_random_seed_type)

@pytest.mark.parametrize('invalid_random_seed_value', [-100, -10, -1])
def test_poule_stage_calculate_results_invalid_random_seed_value(poule_stage, invalid_random_seed_value):
    with pytest.raises(ValueError):
        poule_stage.calculate_results(invalid_random_seed_value)

def test_poule_stage_calculate_ranked_results(poule_stage, poule_scores, expected_poule_stage_results):
    # Record match results
    for match_index in range(21):
        for poule_index in range(len(poule_scores)):
            poule_stage.record_on_piste_match_score(poule_index, *poule_scores[poule_index][match_index])

    # Calculate the ranked results
    ranked_results = poule_stage.calculate_ranked_results(RANDOM_SEED)

    # Validate the order of the ranked results by verifying display names
    ranked_results_names = tuple(entry_result.display_name for entry_result in ranked_results)

    assert ranked_results_names == expected_poule_stage_results

@pytest.mark.parametrize('invalid_random_seed_type', [False, True, '21', 64.3, [], (), {}])
def test_poule_stage_calculate_ranked_results_invalid_random_seed_type(poule_stage, invalid_random_seed_type):
    with pytest.raises(TypeError):
        poule_stage.calculate_ranked_results(invalid_random_seed_type)

@pytest.mark.parametrize('invalid_random_seed_value', [-100, -10, -1])
def test_poule_stage_calculate_ranked_results_invalid_random_seed_value(poule_stage, invalid_random_seed_value):
    with pytest.raises(ValueError):
        poule_stage.calculate_ranked_results(invalid_random_seed_value)

def test_poule_stage_calculate_ranked_results_display_names(poule_stage, poule_scores, expected_poule_stage_results):
    for match_index in range(21):
        for poule_index in range(len(poule_scores)):
            poule_stage.record_on_piste_match_score(poule_index, *poule_scores[poule_index][match_index])

    assert poule_stage.calculate_ranked_results_display_names(RANDOM_SEED) == expected_poule_stage_results

@pytest.mark.parametrize('invalid_random_seed_type', [False, True, '21', 64.3, [], (), {}])
def test_poule_stage_calculate_ranked_results_display_names_invalid_random_seed_type(poule_stage, invalid_random_seed_type):
    with pytest.raises(TypeError):
        poule_stage.calculate_ranked_results_display_names(invalid_random_seed_type)

@pytest.mark.parametrize('invalid_random_seed_value', [-100, -10, -1])
def test_poule_stage_calculate_ranked_results_display_names_invalid_random_seed_value(poule_stage, invalid_random_seed_value):
    with pytest.raises(ValueError):
        poule_stage.calculate_ranked_results_display_names(invalid_random_seed_value)
