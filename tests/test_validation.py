import pytest

import validators

INVALID_INT_TYPES = [None, 'five', 15.0, False, True, [], {}]

@pytest.mark.parametrize('value', INVALID_INT_TYPES)
def test_validate_int_rejects_non_ints(value):
    with pytest.raises(TypeError):
        validators.validate_int(value, 'value', 'TestClass')

@pytest.mark.parametrize('value', [0, 5, 15])
def test_validate_int_accepts_ints(value):
    validators.validate_int(value, 'value', 'TestClass')

@pytest.mark.parametrize('value', [1, 5, 15])
def test_validate_positive_int_accepts_positive_ints(value):
    validators.validate_positive_int(value, 'value', 'TestClass')

@pytest.mark.parametrize('value', [0, -1, -5, -15])
def test_validate_positive_int_rejects_non_positive_ints(value):
    with pytest.raises(ValueError):
        validators.validate_positive_int(value, 'value', 'TestClass')

@pytest.mark.parametrize('value', [0, 5, 15])
def test_validate_non_negative_int_accepts_zero_and_positive_ints(value):
    validators.validate_non_negative_int(value, 'value', 'TestClass')

@pytest.mark.parametrize('value', [-1, -5, -15])
def test_validate_non_negative_int_rejects_negative_ints(value):
    with pytest.raises(ValueError):
        validators.validate_non_negative_int(value, 'value', 'TestClass')

def test_validate_optional_positive_int_accepts_none():
    validators.validate_optional_positive_int(None, 'value', 'TestClass')

def test_validate_optional_non_negative_int_accepts_none():
    validators.validate_optional_non_negative_int(None, 'value', 'TestClass')

@pytest.mark.parametrize('value', [0, 3, 5, 8, 12, 15])
def test_validate_int_in_range_accepts_inclusive_bounds(value):
    validators.validate_int_in_range(value, 0, 15, 'value', 'TestClass')

@pytest.mark.parametrize('value', [-1, 16])
def test_validate_int_in_range_rejects_out_of_range_values(value):
    with pytest.raises(ValueError):
        validators.validate_int_in_range(value, 0, 15, 'value', 'TestClass')