import pytest

from utils import is_power_of_two, log2_int, snake_numbers


# --- Constants ---
NUMBER_DE_ENTRIES = 14

INVALID_INT_TYPES = (None, 'ten', 10.0, False, True, [], {})


# --- Test is_power_of_two() Function ---
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


# --- Test log2_int() Function ---
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


# --- Test snake_numbers() Function ---
def test_snake_numbers_3():
    expected_sequence = [0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0]
    snake_generator = snake_numbers(3)

    for i in range(len(expected_sequence)):
        assert expected_sequence[i] == next(snake_generator)

def test_snake_numbers_4():
    expected_sequence = [0, 1, 2, 3, 3, 2, 1, 0, 0, 1, 2, 3, 3, 2, 1, 0]
    snake_generator = snake_numbers(4)

    for i in range(len(expected_sequence)):
        assert expected_sequence[i] == next(snake_generator)

def test_snake_numbers_5():
    expected_sequence = [0, 1, 2, 3, 4, 4, 3, 2, 1, 0, 0, 1, 2, 3, 4, 4, 3, 2, 1, 0]
    snake_generator = snake_numbers(5)

    for i in range(len(expected_sequence)):
        assert expected_sequence[i] == next(snake_generator)

def test_snake_numbers_6():
    expected_sequence = [0, 1, 2, 3, 4, 5, 5, 4, 3, 2, 1, 0, 0, 1, 2, 3, 4, 5, 5, 4, 3, 2, 1, 0]
    snake_generator = snake_numbers(6)

    for i in range(len(expected_sequence)):
        assert expected_sequence[i] == next(snake_generator)

def test_snake_numbers_7():
    expected_sequence = [0, 1, 2, 3, 4, 5, 6, 6, 5, 4, 3, 2, 1, 0, 0, 1, 2, 3, 4, 5, 6, 6, 5, 4, 3, 2, 1, 0]
    snake_generator = snake_numbers(7)

    for i in range(len(expected_sequence)):
        assert expected_sequence[i] == next(snake_generator)
