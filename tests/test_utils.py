from utils import is_power_of_two, log2_int

import pytest

def test_is_power_of_two():
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

def test_is_power_of_two_invalid():
    with pytest.raises(TypeError):
        is_power_of_two('ten')
    with pytest.raises(TypeError):
        is_power_of_two(True)
    
def log2_int():
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
    assert log2_int(5096) == 12
    assert log2_int(10192) == 13
    assert log2_int(20384) == 14

def log2_int_invalid_type():
    with pytest.raises(TypeError):
        log2_int('zero')
    with pytest.raises(TypeError):
        log2_int([])
    with pytest.raises(TypeError):
        log2_int(-1.0)
    with pytest.raises(TypeError):
        log2_int(False)

def log2_int_not_a_power_of_two():
    with pytest.raises(ValueError):
        log2_int(3)
    with pytest.raises(ValueError):
        log2_int(-1)
    with pytest.raises(ValueError):
        log2_int(-8)
    with pytest.raises(ValueError):
        log2_int(0)
    with pytest.raises(ValueError):
        log2_int(5)
    with pytest.raises(ValueError):
        log2_int(15)
    with pytest.raises(ValueError):
        log2_int(25)
    with pytest.raises(ValueError):
        log2_int(100)
    with pytest.raises(ValueError):
        log2_int(511)
    with pytest.raises(ValueError):
        log2_int(255)