import copy
import pytest

import factories

from poules.poule_stage import PouleStage


# --- Constants ---
from constants import TOURNY_ID1, TOURNY_ID2


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


# --- Initialization and Validation Tests ---
def test_poule_stage_creation_valid_21(entries, seeded_entries):
    # Poule assignment expectation
    expected_poule1 = (entries[0], entries[5], entries[6], entries[11], entries[12], entries[17], entries[18])
    expected_poule2 = (entries[1], entries[4], entries[7], entries[10], entries[13], entries[16], entries[19])
    expected_poule3 = (entries[2], entries[3], entries[8], entries[9], entries[14], entries[15], entries[20])
    expected_poules = (expected_poule1, expected_poule2, expected_poule3)

    poule_stage = PouleStage(stage_number=1, seeded_entries=seeded_entries)
    
    assert poule_stage.stage_number == 1
    assert poule_stage.tournament_id == TOURNY_ID1
    assert poule_stage.seeded_entries == seeded_entries
    assert poule_stage.entries == entries

    assert isinstance(poule_stage.seeded_entries, tuple)
    assert isinstance(poule_stage.poules, tuple)

    assert poule_stage.num_entries == 21
    assert poule_stage.num_poules == 3

    for i, poule in enumerate(poule_stage.poules):
        assert poule.poule_number == i + 1
        assert poule.tournament_id == poule_stage.tournament_id
        assert poule.poule_number == i + 1
        assert poule.entries == expected_poules[i]
        assert not poule.is_complete()

def test_poule_stage_creation_valid_17():
    entries = factories.make_entries(17, TOURNY_ID1)
    seeded_entries = factories.make_seeded_entries(17, TOURNY_ID1)

    # Poule assignment expectation
    expected_poule1 = (entries[0], entries[5], entries[6], entries[11], entries[12], entries[16])
    expected_poule2 = (entries[1], entries[4], entries[7], entries[10], entries[13], entries[15])
    expected_poule3 = (entries[2], entries[3], entries[8], entries[9], entries[14])

    expected_poules = (expected_poule1, expected_poule2, expected_poule3)

    poule_stage = PouleStage(1, seeded_entries)
    
    assert poule_stage.stage_number == 1
    assert poule_stage.tournament_id == TOURNY_ID1
    assert poule_stage.seeded_entries == seeded_entries
    assert poule_stage.entries == entries

    assert isinstance(poule_stage.seeded_entries, tuple)
    assert isinstance(poule_stage.poules, tuple)

    assert poule_stage.num_entries == 17
    assert poule_stage.num_poules == 3

    for i, poule in enumerate(poule_stage.poules):
        assert poule.poule_number == i + 1
        assert poule.tournament_id == poule_stage.tournament_id
        assert poule.poule_number == i + 1
        assert poule.entries == expected_poules[i]
        assert not poule.is_complete()

def test_poule_stage_creation_valid_38():
    entries = factories.make_entries(38, TOURNY_ID1)
    seeded_entries = factories.make_seeded_entries(38, TOURNY_ID1)

    # Poule assignment expectation
    expected_poule1 = (entries[0], entries[11], entries[12], entries[23], entries[24], entries[35], entries[36])
    expected_poule2 = (entries[1], entries[10], entries[13], entries[22], entries[25], entries[34], entries[37])
    expected_poule3 = (entries[2], entries[9], entries[14], entries[21], entries[26], entries[33])
    expected_poule4 = (entries[3], entries[8], entries[15], entries[20], entries[27], entries[32])
    expected_poule5 = (entries[4], entries[7], entries[16], entries[19], entries[28], entries[31])
    expected_poule6 = (entries[5], entries[6], entries[17], entries[18], entries[29], entries[30])

    expected_poules = (expected_poule1, expected_poule2, expected_poule3, expected_poule4, expected_poule5, expected_poule6)

    poule_stage = PouleStage(1, seeded_entries)
    
    assert poule_stage.stage_number == 1
    assert poule_stage.tournament_id == TOURNY_ID1
    assert poule_stage.seeded_entries == seeded_entries
    assert poule_stage.entries == entries

    assert isinstance(poule_stage.entries, tuple)
    assert isinstance(poule_stage.poules, tuple)

    assert poule_stage.num_entries == 38
    assert poule_stage.num_poules == 6

    for i, poule in enumerate(poule_stage.poules):
        assert poule.poule_number == i + 1
        assert poule.tournament_id == poule_stage.tournament_id
        assert poule.poule_number == i + 1
        assert poule.entries == expected_poules[i]
        assert not poule.is_complete()

def test_poule_stage_creation_valid_two_entries():
    entries = factories.make_entries(2, TOURNY_ID1)
    seeded_entries = factories.make_seeded_entries(2, TOURNY_ID1)

    poule_stage = PouleStage(1, seeded_entries)

    assert poule_stage.seeded_entries == seeded_entries
    assert poule_stage.entries == entries
    assert poule_stage.num_entries == 2
    assert poule_stage.num_poules == 1
    assert poule_stage.poules[0].entries == entries
    assert poule_stage.poules[0].number_matches == 1

@pytest.mark.parametrize('invalid_stage_id_type', [None, '1UI3', False, True, 1.0, [], (), {}])
def test_poule_stage_creation_invalid_stage_id_type(seeded_entries, invalid_stage_id_type):
    with pytest.raises(TypeError):
        PouleStage(invalid_stage_id_type, seeded_entries)

@pytest.mark.parametrize('invalid_stage_id_value', [-100, -1, 0])
def test_poule_stage_creation_invalid_stage_id_value(seeded_entries, invalid_stage_id_value):
    with pytest.raises(ValueError):
        PouleStage(invalid_stage_id_value, seeded_entries)

@pytest.mark.parametrize('invalid_seeded_entries_type', [None, False, True, 0, 1.0, 'John', {}])
def test_poule_stage_creation_invalid_seeded_entries_type(invalid_seeded_entries_type):
    with pytest.raises(TypeError):
        PouleStage(1, invalid_seeded_entries_type)

def test_poule_stage_creation_invalid_seeded_entries_list(seeded_entries):
    with pytest.raises(TypeError):
        PouleStage(1, list(seeded_entries))

@pytest.mark.parametrize(
        ('index', 'invalid_seeded_entry_type'), 
        [
            (4, 'Jennifer'), 
            (7, False), 
            (8, True), 
            (5, 0), 
            (11, 15.0), 
            (17, None), 
            (20, factories.make_fencer(10, 'Jennifer'))
        ]
)
def test_poule_stage_creation_invalid_seeded_entries_invalid_entry_type(seeded_entries, index, invalid_seeded_entry_type):
    seeded_entries = list(seeded_entries)
    
    seeded_entries[index] = invalid_seeded_entry_type
    
    seeded_entries = tuple(seeded_entries)

    with pytest.raises(TypeError):
        PouleStage(1, seeded_entries)

@pytest.mark.parametrize('index', [0, 7, 10, 20])
def test_poule_stage_creation_invalid_seeded_entries_invalid_seeded_entry_tournament_id(seeded_entries, index):
    seeded_entries = list(seeded_entries)

    seeded_entries[index] = factories.make_seeded_entry_at_number(index + 1, TOURNY_ID2)

    seeded_entries = tuple(seeded_entries)

    with pytest.raises(ValueError):
        PouleStage(1, seeded_entries)

def test_poule_stage_creation_invalid_seeded_entries_empty():
    with pytest.raises(ValueError):
        PouleStage(1, ())

def test_poule_stage_creation_invalid_seeded_entries_only_one_entry():
    seeded_entries = factories.make_seeded_entries(1, TOURNY_ID1)

    with pytest.raises(ValueError):
        PouleStage(1, seeded_entries)

def test_poule_stage_creation_invalid_seeded_entries_duplicate_entry(seeded_entries):
    duplicate_entry = copy.deepcopy(seeded_entries[7])

    seeded_entries = seeded_entries + (duplicate_entry,)

    with pytest.raises(ValueError):
        PouleStage(1, seeded_entries)

@pytest.mark.parametrize('invalid_seed_type', [None, 'five', False, True, 5.0, [], (), {}, object()])
def test_poule_stage_creation_invalid_seeded_entries_seeded_entry_seed_type(seeded_entries, invalid_seed_type):
    object.__setattr__(seeded_entries[8], 'seed', invalid_seed_type)

    with pytest.raises(TypeError):
        PouleStage(1, seeded_entries)

@pytest.mark.parametrize('invalid_seed_value', [-5, -1, 0])
def test_poule_stage_creation_invalid_seeded_entries_seeded_entry_seed_value(seeded_entries, invalid_seed_value):
    object.__setattr__(seeded_entries[11], 'seed', invalid_seed_value)

    with pytest.raises(ValueError):
        PouleStage(1, seeded_entries)

def test_poule_stage_creation_invalid_seeded_entries_seeded_entry_duplicate_seed(seeded_entries):
    object.__setattr__(seeded_entries[15], 'seed', seeded_entries[4].seed)

    with pytest.raises(ValueError):
        PouleStage(1, seeded_entries)

def test_poule_stage_creation_invalid_seeded_entries_seeded_entry_seed_outside_expected_range(seeded_entries):
    object.__setattr__(seeded_entries[-1], 'seed', 22)

    with pytest.raises(ValueError):
        PouleStage(1, seeded_entries)

def test_poule_stage_creation_sorts_seeded_entries_by_seed(entries, seeded_entries):
    reversed_entries = tuple(reversed(seeded_entries))

    poule_stage = PouleStage(1, reversed_entries)

    assert poule_stage.seeded_entries == seeded_entries

    # Poule assignment expectation
    expected_poule1 = (entries[0], entries[5], entries[6], entries[11], entries[12], entries[17], entries[18])
    expected_poule2 = (entries[1], entries[4], entries[7], entries[10], entries[13], entries[16], entries[19])
    expected_poule3 = (entries[2], entries[3], entries[8], entries[9], entries[14], entries[15], entries[20])
    expected_poules = (expected_poule1, expected_poule2, expected_poule3)

    for i, poule in enumerate(poule_stage.poules):
        assert poule.entries == expected_poules[i]


# --- Equality Tests ---
def test_poule_stage_equality_same_attributes(seeded_entries):
    poule_stage1 = PouleStage(1, seeded_entries)
    poule_stage2 = PouleStage(1, seeded_entries)

    assert poule_stage1 == poule_stage2

@pytest.mark.parametrize('non_poule_stage_object', [None, 15.0, 7, False, True, [], {}, object()])
def test_poule_stage_inequality_different_objects(poule_stage, non_poule_stage_object):
    assert poule_stage != non_poule_stage_object

def test_poule_stage_inequality_different_stage_id(seeded_entries):
    poule_stage1 = PouleStage(1, seeded_entries)
    poule_stage2 = PouleStage(2, seeded_entries)

    assert poule_stage1 != poule_stage2

def test_poule_stage_inequality_different_tournament_id(seeded_entries):
    poule_stage1 = PouleStage(1, seeded_entries)
    poule_stage2 = PouleStage(1, factories.make_seeded_entries(7, TOURNY_ID2))

    assert poule_stage1 != poule_stage2


# --- Creation Helper Method Tests ---
@pytest.mark.parametrize('invalid_n_type', [None, False, True, 10.0, 'twenty', [17], (30,), {7:21}])
def test_poule_stage__calculate_poule_sizes_invalid_n_type(poule_stage, invalid_n_type):
    with pytest.raises(TypeError):
        poule_stage._calculate_poule_sizes(invalid_n_type)

@pytest.mark.parametrize('invalid_n_size', [-100, -10, -1, 0, 1])
def test_poule_stage__calculate_poule_sizes_invalid_n_size(poule_stage, invalid_n_size):
    with pytest.raises(ValueError):
        poule_stage._calculate_poule_sizes(invalid_n_size)

@pytest.mark.parametrize(('num_entries', 'poule_sizes'), 
                         [(2, (2,)), (3, (3,)), (4, (4,)), (5, (5,)), (6, (6,)), (7, (7,)), 
                          (8, (4, 4)), (9, (5, 4)), (10, (5, 5)), (11, (6, 5)), (12, (6, 6)), (13, (7, 6)), (14, (7, 7)), 
                          (15, (5, 5, 5)), (16, (6, 5, 5)), (17, (6, 6, 5)), (18, (6, 6, 6)), (19, (7, 6, 6)), (20, (7, 7, 6)), (21, (7, 7, 7)), 
                          (100, (7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 6, 6, 6, 6, 6))])
def test_poule_stage__calculate_poule_sizes_default_priority_size(poule_stage, num_entries, poule_sizes):
    assert poule_stage._calculate_poule_sizes(num_entries) == poule_sizes
