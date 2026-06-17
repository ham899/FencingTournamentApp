import pytest

from utils import (
    is_power_of_two,
    log2_int,
    calculate_number_poule_matches,
    calculate_number_of_de_rounds,
    calculate_number_matches_in_de_round
)

# --- Constants ---
NUMBER_DE_ENTRIES = 14

INVALID_INT_TYPES = (None, 'ten', 10.0, False, True, [], {})

# --- is_power_of_two tests ---
@pytest.mark.parametrize(('n', 'expected_result'), [
    (-10, False),
    (-1, False),
    (0, False),
    (1, True),
    (2, True),
    (3, False),
    (4, True),
    (5, False),
    (8, True),
    (15, False),
    (16, True),
    (30, False),
    (32, True),
    (61, False),
    (64, True),
    (100, False),
    (128, True),
    (199, False),
    (256, True),
    (501, False),
    (512, True)
])
def test_is_power_of_two_valid(n, expected_result):
    assert is_power_of_two(n) is expected_result

@pytest.mark.parametrize('invalid_n_type', INVALID_INT_TYPES)
def test_is_power_of_two_invalid_type(invalid_n_type):
    with pytest.raises(TypeError):
        is_power_of_two(invalid_n_type)
    
# --- log2_int tests ---
@pytest.mark.parametrize(('n', 'expected_result'), [
    (1, 0),
    (2, 1),
    (4, 2),
    (8, 3),
    (16, 4),
    (32, 5),
    (64, 6),
    (128, 7),
    (256, 8),
    (512, 9),
    (1024, 10),
    (2048, 11),
    (4096, 12),
    (8192, 13),
    (16384, 14)
])
def test_log2_int_valid(n, expected_result):
    assert log2_int(n) == expected_result

@pytest.mark.parametrize('invalid_n_type', INVALID_INT_TYPES)
def test_log2_int_invalid_type(invalid_n_type):
    with pytest.raises(TypeError):
        log2_int(invalid_n_type)

@pytest.mark.parametrize('not_a_power_of_two', [-10, -8, -1, 0, 3, 5, 15, 25, 100, 255, 511, 1000])
def test_log2_int_invalid_not_a_power_of_two(not_a_power_of_two):
    with pytest.raises(ValueError):
        log2_int(not_a_power_of_two)

# --- calculate_number_poule_matches tests ---
@pytest.mark.parametrize(('poule_size', 'expected_matches'), [
    (2, 1),
    (3, 3),
    (4, 6),
    (5, 10),
    (6, 15),
    (7, 21),
    (8, 28),
    (9, 36),
    (10, 45),
    (11, 55),
    (12, 66),
    (20, 190)
])
def test_calculate_number_poule_matches_valid(poule_size, expected_matches):
    assert calculate_number_poule_matches(poule_size) == expected_matches

@pytest.mark.parametrize('invalid_poule_size_type', INVALID_INT_TYPES)
def test_calculate_number_poule_matches_invalid_input_type(invalid_poule_size_type):
    with pytest.raises(TypeError):
        calculate_number_poule_matches(invalid_poule_size_type)

@pytest.mark.parametrize('invalid_poule_size_value', [-10, -1, 0, 1])
def test_calculate_number_poule_matches_invalid_input_value(invalid_poule_size_value):
    with pytest.raises(ValueError):
        calculate_number_poule_matches(invalid_poule_size_value)

# --- calculate_number_of_de_rounds tests ---
@pytest.mark.parametrize(('number_de_entries', 'expected_rounds'), [
    (2, 1),
    (3, 2),
    (4, 2),
    (5, 3),
    (6, 3),
    (7, 3),
    (8, 3),
    (9, 4),
    (10, 4),
    (11, 4),
    (12, 4),
    (13, 4),
    (14, 4),
    (15, 4),
    (16, 4),
    (17, 5),
    (32, 5),
    (33, 6),
    (64, 6),
    (65, 7),
    (100, 7),
    (200, 8),
    (500, 9),
    (1000, 10)
])
def test_calculate_number_of_de_rounds_valid(number_de_entries, expected_rounds):
    assert calculate_number_of_de_rounds(number_de_entries=number_de_entries) == expected_rounds

@pytest.mark.parametrize('invalid_number_de_entries_type', INVALID_INT_TYPES)
def test_calculate_number_of_de_rounds_invalid_number_de_entries_type(invalid_number_de_entries_type):
    with pytest.raises(TypeError):
        calculate_number_of_de_rounds(number_de_entries=invalid_number_de_entries_type)

@pytest.mark.parametrize('invalid_number_de_entries_value', [-10, -1, 0, 1])
def test_calculate_number_of_de_rounds_invalid_number_de_entries_value(invalid_number_de_entries_value):
    with pytest.raises(ValueError):
        calculate_number_of_de_rounds(number_de_entries=invalid_number_de_entries_value)

# --- calculate_number_matches_in_de_round tests ---
@pytest.mark.parametrize(('round_index', 'number_de_entries', 'expected_matches'), [
    # 2-entry bracket
    (0, 2, 1),

    # 3-entry bracket: 4-slot bracket with one BYE
    (0, 3, 2),
    (1, 3, 1),

    # 4-entry bracket
    (0, 4, 2),
    (1, 4, 1),

    # 5-entry bracket: 8-slot bracket with BYEs
    (0, 5, 4),
    (1, 5, 2),
    (2, 5, 1),

    # 8-entry bracket
    (0, 8, 4),
    (1, 8, 2),
    (2, 8, 1),

    # 14-entry bracket: 16-slot bracket with BYEs
    (0, 14, 8),
    (1, 14, 4),
    (2, 14, 2),
    (3, 14, 1),

    # 16-entry bracket
    (0, 16, 8),
    (1, 16, 4),
    (2, 16, 2),
    (3, 16, 1),

    # 17-entry bracket: 32-slot bracket with BYEs
    (0, 17, 16),
    (1, 17, 8),
    (2, 17, 4),
    (3, 17, 2),
    (4, 17, 1)
])
def test_calculate_number_matches_in_de_round_valid(round_index, number_de_entries, expected_matches):
    assert calculate_number_matches_in_de_round(round_index=round_index, number_de_entries=number_de_entries) == expected_matches

@pytest.mark.parametrize('invalid_round_index_type', INVALID_INT_TYPES)
def test_calculate_number_matches_in_de_round_invalid_round_index_type(invalid_round_index_type):
    with pytest.raises(TypeError):
        calculate_number_matches_in_de_round(round_index=invalid_round_index_type, number_de_entries=NUMBER_DE_ENTRIES)

@pytest.mark.parametrize('invalid_round_index_negative', [-10, -5, -1])
def test_calculate_number_matches_in_de_round_invalid_round_index_negative(invalid_round_index_negative):
    with pytest.raises(ValueError):
        calculate_number_matches_in_de_round(round_index=invalid_round_index_negative, number_de_entries=NUMBER_DE_ENTRIES)

@pytest.mark.parametrize('invalid_number_de_entries_type', INVALID_INT_TYPES)
def test_calculate_number_matches_in_de_round_invalid_number_de_entries_type(invalid_number_de_entries_type):
    with pytest.raises(TypeError):
        calculate_number_matches_in_de_round(round_index=0, number_de_entries=invalid_number_de_entries_type)

@pytest.mark.parametrize('invalid_number_de_entries_value', [-10, -1, 0, 1])
def test_calculate_number_matches_in_de_round_invalid_number_de_entries_value(invalid_number_de_entries_value):
    with pytest.raises(ValueError):
        calculate_number_matches_in_de_round(round_index=0, number_de_entries=invalid_number_de_entries_value)

@pytest.mark.parametrize(('round_index', 'number_de_entries'), [
    (1, 2),
    (2, 3),
    (3, 6),
    (4, 14),
    (5, 17)
])
def test_calculate_number_matches_in_de_round_invalid_round_index_greater_than_maximum(round_index, number_de_entries):
    with pytest.raises(ValueError):
        calculate_number_matches_in_de_round(round_index=round_index, number_de_entries=number_de_entries)