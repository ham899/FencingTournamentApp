import copy
import pytest

from dataclasses import FrozenInstanceError

import factories

from poules.results.poule_stage_results import PouleStageResults


# --- Constants ---
from constants import TOURNY_ID1, TOURNY_ID2

RANDOM_SEED = 36


# --- Fixtures ---
@pytest.fixture
def entries_21():
    return factories.make_entries(n=21, tournament_id=TOURNY_ID1)

@pytest.fixture
def entries_poule1(entries_21):
    return (entries_21[0], entries_21[5], entries_21[6], entries_21[11], entries_21[12], entries_21[17], entries_21[18])

@pytest.fixture
def entries_poule2(entries_21):
    return (entries_21[1], entries_21[4], entries_21[7], entries_21[10], entries_21[13], entries_21[16], entries_21[19])

@pytest.fixture
def entries_poule3(entries_21):
    return (entries_21[2], entries_21[3], entries_21[8], entries_21[9], entries_21[14], entries_21[15], entries_21[20])

@pytest.fixture
def poule1_incomplete(entries_poule1):
    return factories.make_poule(1, 1, entries_poule1)

@pytest.fixture
def poule2_incomplete(entries_poule2):
    return factories.make_poule(2, 1, entries_poule2)

@pytest.fixture
def poule3_incomplete(entries_poule3):
    return factories.make_poule(3, 1, entries_poule3)

@pytest.fixture
def poules_incomplete(poule1_incomplete, poule2_incomplete, poule3_incomplete):
    return (poule1_incomplete, poule2_incomplete, poule3_incomplete)

@pytest.fixture
def poule1_partial(entries_poule1):
    match_results = ((0,1), (0,1), (0,1), (0,1), (0,1), (0,1), (0,1))
    
    return factories.make_poule(1, 1, entries_poule1, scores=match_results)

@pytest.fixture
def poule2_partial(entries_poule2):
    match_results = ((0,1), (0,1), (0,1), (0,1), (0,1), (0,1), (0,1))
    
    return factories.make_poule(2, 1, entries_poule2, scores=match_results)

@pytest.fixture
def poule3_partial(entries_poule3):
    match_results = ((0,1), (0,1), (0,1), (0,1), (0,1), (0,1), (0,1))
    
    return factories.make_poule(3, 1, entries_poule3, scores=match_results)

@pytest.fixture
def poules_partially_complete(poule1_partial, poule2_partial, poule3_partial):
    return (poule1_partial, poule2_partial, poule3_partial)

@pytest.fixture
def poule1_complete(entries_poule1):
    match_results = ((0,1), (0,1), (0,1), (0,1), (0,1), (0,1), (0,1), 
                     (0,1), (0,1), (0,1), (0,1), (0,1), (0,1), (0,1), 
                     (0,1), (0,1), (0,1), (0,1), (0,1), (0,1), (0,1))
    
    return factories.make_poule(1, 1, entries_poule1, scores=match_results)

@pytest.fixture
def poule2_complete(entries_poule2):
    match_results = ((0,1), (0,1), (0,1), (0,1), (0,1), (0,1), (0,1), 
                     (0,1), (0,1), (0,1), (0,1), (0,1), (0,1), (0,1), 
                     (0,1), (0,1), (0,1), (0,1), (0,1), (0,1), (0,1))
    
    return factories.make_poule(2, 1, entries_poule2, scores=match_results)

@pytest.fixture
def poule3_complete(entries_poule3):
    match_results = ((0,1), (0,1), (0,1), (0,1), (0,1), (0,1), (0,1), 
                     (0,1), (0,1), (0,1), (0,1), (0,1), (0,1), (0,1), 
                     (0,1), (0,1), (0,1), (0,1), (0,1), (0,1), (0,1))
    
    return factories.make_poule(3, 1, entries_poule3, scores=match_results)

@pytest.fixture
def poules_complete(poule1_complete, poule2_complete, poule3_complete):
    return (poule1_complete, poule2_complete, poule3_complete)


# --- Initialization and Validation Tests ---
def test_tournament_poule_results_creation_valid_incomplete_poules(entries_21, poules_incomplete):
    results = PouleStageResults(poules_incomplete, RANDOM_SEED)

    assert results.tournament_id == TOURNY_ID1
    assert results.random_seed == RANDOM_SEED
    assert isinstance(results.poule_results, tuple)
    assert isinstance(results.stage_results, tuple)
    assert len(results.poule_results) == len(poules_incomplete)
    assert len(results.stage_results) == len(entries_21)

def test_tournament_poule_results_creation_valid_single_poule(poule1_incomplete):
    results = PouleStageResults((poule1_incomplete,), RANDOM_SEED)

    assert len(results.poule_results) == 1

def test_tournament_poule_results_creation_valid_partially_complete_poules(entries_21, poules_partially_complete):
    results = PouleStageResults(poules_partially_complete, RANDOM_SEED)

    assert results.tournament_id == TOURNY_ID1
    assert results.random_seed == RANDOM_SEED
    assert isinstance(results.poule_results, tuple)
    assert isinstance(results.stage_results, tuple)
    assert len(results.poule_results) == len(poules_partially_complete)
    assert len(results.stage_results) == len(entries_21)

def test_tournament_poule_results_creation_valid_complete_poules(entries_21, poules_complete):
    results = PouleStageResults(poules_complete, RANDOM_SEED)

    assert results.tournament_id == TOURNY_ID1
    assert results.random_seed == RANDOM_SEED
    assert isinstance(results.poule_results, tuple)
    assert isinstance(results.stage_results, tuple)
    assert len(results.poule_results) == len(poules_complete)
    assert len(results.stage_results) == len(entries_21)

def test_tournament_poule_results_frozen_attributes(poules_complete):
    results = PouleStageResults(poules_complete, RANDOM_SEED)

    with pytest.raises(FrozenInstanceError):
        results.random_seed = RANDOM_SEED // 2

    with pytest.raises(FrozenInstanceError):
        results.poule_results = None

    with pytest.raises(FrozenInstanceError):
        results.stage_results = None

@pytest.mark.parametrize('invalid_poules_type', [None, 'my_poules', True, False, 0, 1.0, [], {}])
def test_tournament_poule_results_creation_invalid_poules_type(invalid_poules_type):
    with pytest.raises(TypeError):
        PouleStageResults(invalid_poules_type, RANDOM_SEED)

@pytest.mark.parametrize('invalid_poule_type', [None, 'Henry', False, 0, True, 10.0, [], (), {}, object()])
def test_tournament_poule_results_creation_invalid_poules_non_poule_item(poules_incomplete, invalid_poule_type):
    invalid_poules_poule_type = poules_incomplete + (invalid_poule_type,)
    
    with pytest.raises(TypeError):
        PouleStageResults(invalid_poules_poule_type, RANDOM_SEED)

def test_tournament_poule_results_creation_invalid_poules_empty():
    with pytest.raises(ValueError, match='poules cannot be empty'):
        PouleStageResults((), RANDOM_SEED)

def test_tournament_poule_results_creation_invalid_poules_poule_wrong_tournament(poules_incomplete):
    invalid_poule_wrong_tournament = factories.make_poule(4, TOURNY_ID2, factories.make_entries(28, TOURNY_ID2)[21:])

    invalid_poules_poule_wrong_tournament = poules_incomplete + (invalid_poule_wrong_tournament,)

    with pytest.raises(ValueError, match=r"has a tournament ID \d that does not match the other poules' tournament IDs \d"):
        PouleStageResults(invalid_poules_poule_wrong_tournament, RANDOM_SEED)

def test_tournament_poule_results_creation_invalid_poules_duplicate_poule(poules_incomplete):
    duplicate_poule = copy.deepcopy(poules_incomplete[1])

    invalid_poules_duplicate_poule = poules_incomplete + (duplicate_poule,)

    with pytest.raises(ValueError, match='occurs more than once'):
        PouleStageResults(invalid_poules_duplicate_poule, RANDOM_SEED)

@pytest.mark.parametrize('invalid_random_seed_type', ['twelve', False, 42.0, True, [66], (37,), {}])
def test_tournament_poule_results_creation_invalid_random_seed_type(poules_incomplete, invalid_random_seed_type):
    with pytest.raises(TypeError):
        PouleStageResults(poules_incomplete, invalid_random_seed_type)

@pytest.mark.parametrize('invalid_random_seed_value', [-36, -6, -1])
def test_tournament_poule_results_creation_invalid_random_seed_value(poules_incomplete, invalid_random_seed_value):
    with pytest.raises(ValueError):
        PouleStageResults(poules_incomplete, invalid_random_seed_value)

def test_tournament_poule_results_creation_valid_default_random_seed(poules_incomplete):
    results = PouleStageResults(poules_incomplete)

    assert results.random_seed is None

def test_tournament_poule_results_creation_valid_zero_random_seed(poules_incomplete):
    results = PouleStageResults(poules_incomplete, 0)

    assert results.random_seed == 0
