from utils import is_power_of_two, log2_int
from utils import calculate_number_poule_matches
from utils import calculate_number_of_de_rounds, calculate_number_matches_in_de_round

import pytest

### CONSTANTS ###
NUMBER_DE_ENTRIES = 14

### TESTS ###
def test_is_power_of_two_valid():
    assert is_power_of_two(-10) == False
    assert is_power_of_two(-1) == False
    assert is_power_of_two(0) == False
    assert is_power_of_two(1) == True
    assert is_power_of_two(2) == True
    assert is_power_of_two(3) == False
    assert is_power_of_two(4) == True
    assert is_power_of_two(5) == False
    assert is_power_of_two(8) == True
    assert is_power_of_two(15) == False
    assert is_power_of_two(16) == True
    assert is_power_of_two(30) == False
    assert is_power_of_two(32) == True
    assert is_power_of_two(61) == False
    assert is_power_of_two(64) == True
    assert is_power_of_two(100) == False
    assert is_power_of_two(128) == True
    assert is_power_of_two(199) == False
    assert is_power_of_two(256) == True
    assert is_power_of_two(501) == False
    assert is_power_of_two(512) == True

@pytest.mark.parametrize('invalid_n_type', [None, 'ten', True, 20.0, [], {}])
def test_is_power_of_two_invalid_type(invalid_n_type):
    with pytest.raises(TypeError):
        is_power_of_two(invalid_n_type)
    
def test_log2_int_valid():
    assert log2_int(1) == 0
    assert log2_int(2) == 1
    assert log2_int(4) == 2
    assert log2_int(8) == 3
    assert log2_int(16) == 4
    assert log2_int(32) == 5
    assert log2_int(64) == 6
    assert log2_int(128) == 7
    assert log2_int(256) == 8
    assert log2_int(512) == 9
    assert log2_int(1024) == 10
    assert log2_int(2048) == 11
    assert log2_int(4096) == 12
    assert log2_int(8192) == 13
    assert log2_int(16384) == 14

@pytest.mark.parametrize('invalid_n_type', [None, 'zero', 8.0, True, [], {}])
def test_log2_int_invalid_type(invalid_n_type):
    with pytest.raises(TypeError):
        log2_int(invalid_n_type)

@pytest.mark.parametrize('not_a_power_of_two', [-1, -8, 0, 3, 5, 15, 25, 100, 511, 255])
def test_log2_int_invalid_not_a_power_of_two(not_a_power_of_two):
    with pytest.raises(ValueError):
        log2_int(not_a_power_of_two)

def test_calculate_number_poule_matches_valid():
    assert calculate_number_poule_matches(2) == 1
    assert calculate_number_poule_matches(3) == 3
    assert calculate_number_poule_matches(4) == 6
    assert calculate_number_poule_matches(5) == 10
    assert calculate_number_poule_matches(6) == 15
    assert calculate_number_poule_matches(7) == 21
    assert calculate_number_poule_matches(8) == 28
    assert calculate_number_poule_matches(9) == 36
    assert calculate_number_poule_matches(10) == 45
    assert calculate_number_poule_matches(11) == 55
    assert calculate_number_poule_matches(12) == 66
    assert calculate_number_poule_matches(20) == 190

@pytest.mark.parametrize('invalid_poule_size_type', [None, 7.0, 'six', False, [], {}])
def test_calculate_number_poule_matches_invalid_input_type(invalid_poule_size_type):
    with pytest.raises(TypeError):
        calculate_number_poule_matches(invalid_poule_size_type)

@pytest.mark.parametrize('invalid_poule_size_value', [-10, -1, 0, 1])
def test_calculate_number_poule_matches_invalid_input_value(invalid_poule_size_value):
    with pytest.raises(ValueError):
        calculate_number_poule_matches(invalid_poule_size_value)

def test_calculate_number_de_rounds_valid():
    assert calculate_number_of_de_rounds(number_de_entries=2) == 1
    assert calculate_number_of_de_rounds(number_de_entries=3) == 2
    assert calculate_number_of_de_rounds(number_de_entries=4) == 2
    assert calculate_number_of_de_rounds(number_de_entries=5) == 3
    assert calculate_number_of_de_rounds(number_de_entries=6) == 3
    assert calculate_number_of_de_rounds(number_de_entries=7) == 3
    assert calculate_number_of_de_rounds(number_de_entries=8) == 3
    assert calculate_number_of_de_rounds(number_de_entries=9) == 4
    assert calculate_number_of_de_rounds(number_de_entries=10) == 4
    assert calculate_number_of_de_rounds(number_de_entries=11) == 4
    assert calculate_number_of_de_rounds(number_de_entries=12) == 4
    assert calculate_number_of_de_rounds(number_de_entries=13) == 4
    assert calculate_number_of_de_rounds(number_de_entries=14) == 4
    assert calculate_number_of_de_rounds(number_de_entries=15) == 4
    assert calculate_number_of_de_rounds(number_de_entries=16) == 4
    assert calculate_number_of_de_rounds(number_de_entries=17) == 5
    assert calculate_number_of_de_rounds(number_de_entries=32) == 5
    assert calculate_number_of_de_rounds(number_de_entries=33) == 6
    assert calculate_number_of_de_rounds(number_de_entries=64) == 6
    assert calculate_number_of_de_rounds(number_de_entries=65) == 7
    assert calculate_number_of_de_rounds(number_de_entries=100) == 7
    assert calculate_number_of_de_rounds(number_de_entries=200) == 8
    assert calculate_number_of_de_rounds(number_de_entries=500) == 9
    assert calculate_number_of_de_rounds(number_de_entries=1000) == 10

@pytest.mark.parametrize('invalid_number_de_entries_type', [None, 100.0, True, 'thirty', [], {}])
def test_calculate_number_of_de_rounds_invalid_number_de_entries_type(invalid_number_de_entries_type):
    with pytest.raises(TypeError):
        calculate_number_of_de_rounds(number_de_entries=invalid_number_de_entries_type)

@pytest.mark.parametrize('invalid_number_de_entries_value', [-10, -1, 0, 1])
def test_calculate_number_of_de_rounds_invalid_number_de_entries_value(invalid_number_de_entries_value):
    with pytest.raises(ValueError):
        calculate_number_of_de_rounds(number_de_entries=invalid_number_de_entries_value)

def test_calculate_number_matches_in_de_round_valid():
    assert calculate_number_matches_in_de_round(round_index=0, number_de_entries=2) == 1
    assert calculate_number_matches_in_de_round(round_index=0, number_de_entries=4) == 2
    assert calculate_number_matches_in_de_round(round_index=1, number_de_entries=4) == 1
    assert calculate_number_matches_in_de_round(round_index=0, number_de_entries=8) == 4
    assert calculate_number_matches_in_de_round(round_index=1, number_de_entries=8) == 2
    assert calculate_number_matches_in_de_round(round_index=2, number_de_entries=8) == 1
    assert calculate_number_matches_in_de_round(round_index=0, number_de_entries=16) == 8
    assert calculate_number_matches_in_de_round(round_index=1, number_de_entries=16) == 4
    assert calculate_number_matches_in_de_round(round_index=2, number_de_entries=16) == 2
    assert calculate_number_matches_in_de_round(round_index=3, number_de_entries=16) == 1
    assert calculate_number_matches_in_de_round(round_index=0, number_de_entries=32) == 16
    assert calculate_number_matches_in_de_round(round_index=1, number_de_entries=32) == 8
    assert calculate_number_matches_in_de_round(round_index=2, number_de_entries=32) == 4
    assert calculate_number_matches_in_de_round(round_index=3, number_de_entries=32) == 2
    assert calculate_number_matches_in_de_round(round_index=4, number_de_entries=32) == 1

@pytest.mark.parametrize('invalid_round_index_type', [None, '0', 0.0, False, [], {}])
def test_calculate_number_matches_in_de_round_invalid_round_index_type(invalid_round_index_type):
    with pytest.raises(TypeError):
        calculate_number_matches_in_de_round(round_index=invalid_round_index_type, number_de_entries=NUMBER_DE_ENTRIES)

@pytest.mark.parametrize('invalid_round_index_negative', [-10, -1])
def test_calculate_number_matches_in_de_round_invalid_round_index_negative(invalid_round_index_negative):
    with pytest.raises(ValueError):
        calculate_number_matches_in_de_round(round_index=invalid_round_index_negative, number_de_entries=NUMBER_DE_ENTRIES)

@pytest.mark.parametrize('invalid_number_de_entries_type', [None, 15.0, 'sixty', True, [], {}])
def test_calculate_number_matches_in_de_round_invalid_number_de_entries_type(invalid_number_de_entries_type):
    with pytest.raises(TypeError):
        calculate_number_matches_in_de_round(round_index=0, number_de_entries=invalid_number_de_entries_type)

@pytest.mark.parametrize('invalid_number_de_entries_value', [-10, -1, 0, 1])
def test_calculate_number_matches_in_de_round_invalid_number_de_entries_value(invalid_number_de_entries_value):
    with pytest.raises(ValueError):
        calculate_number_matches_in_de_round(round_index=0, number_de_entries=invalid_number_de_entries_value)

def test_calculate_number_matches_in_de_round_invalid_round_index_greater_than_maximum():
    with pytest.raises(ValueError):
        calculate_number_matches_in_de_round(round_index=10, number_de_entries=2)
    with pytest.raises(ValueError):
        calculate_number_matches_in_de_round(round_index=4, number_de_entries=3)
    with pytest.raises(ValueError):
        calculate_number_matches_in_de_round(round_index=3, number_de_entries=6)