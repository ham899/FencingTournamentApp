import pytest

import validation

INVALID_INT_TYPES = [None, 'five', 15.0, False, True, [], {}]

@pytest.mark.parametrize('value', INVALID_INT_TYPES)
def test_validate_int_rejects_non_ints(value):
    with pytest.raises(TypeError):
        validation.validate_int(value, 'value')

@pytest.mark.parametrize('value', [0, 5, 15])
def test_validate_int_accepts_ints(value):
    validation.validate_int(value, 'value')

@pytest.mark.parametrize('value', [1, 5, 15])
def test_validate_positive_int_accepts_positive_ints(value):
    validation.validate_positive_int(value, 'value')

@pytest.mark.parametrize('value', [0, -1, -5, -15])
def test_validate_positive_int_rejects_non_positive_ints(value):
    with pytest.raises(ValueError):
        validation.validate_positive_int(value, 'value')

@pytest.mark.parametrize('value', [0, 5, 15])
def test_validate_non_negative_int_accepts_zero_and_positive_ints(value):
    validation.validate_non_negative_int(value, 'value')

@pytest.mark.parametrize('value', [-1, -5, -15])
def test_validate_non_negative_int_rejects_negative_ints(value):
    with pytest.raises(ValueError):
        validation.validate_non_negative_int(value, 'value')

def test_validate_optional_positive_int_accepts_none():
    validation.validate_optional_positive_int(None, 'value')

def test_validate_optional_non_negative_int_accepts_none():
    validation.validate_optional_non_negative_int(None, 'value')

@pytest.mark.parametrize('value', [0, 3, 5, 8, 12, 15])
def test_validate_int_in_range_accepts_inclusive_bounds(value):
    validation.validate_int_in_range(value, 0, 15, 'value')

@pytest.mark.parametrize('value', [-1, 16])
def test_validate_int_in_range_rejects_out_of_range_values(value):
    with pytest.raises(ValueError):
        validation.validate_int_in_range(value, 0, 15, 'value')

@pytest.mark.parametrize('min_value', INVALID_INT_TYPES)
def test_validate_int_in_range_rejects_non_int_min_value(min_value):
    with pytest.raises(TypeError):
        validation.validate_int_in_range(5, min_value, 10, 'value')

@pytest.mark.parametrize('max_value', INVALID_INT_TYPES)
def test_validate_int_in_range_rejects_non_int_max_value(max_value):
    with pytest.raises(TypeError):
        validation.validate_int_in_range(5, 0, max_value, 'value')

def test_validate_int_in_range_rejects_min_greater_than_max():
    with pytest.raises(ValueError):
        validation.validate_int_in_range(5, 10, 0, 'value')

@pytest.mark.parametrize('value', INVALID_INT_TYPES)
def test_validate_int_in_range_rejects_non_int_value(value):
    with pytest.raises(TypeError):
        validation.validate_int_in_range(value, 0, 10, 'value')