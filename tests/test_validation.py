import pytest

import validation


INVALID_INT_TYPES = [None, 'five', 15.0, False, True, [], {}]
INVALID_NON_NONE_INT_TYPES = ('five', 15.0, False, True, [], {})

def test__validation_location_no_location():
    assert validation._validation_location() == ''

def test__validation_location_class_name_only():
    assert validation._validation_location('MyClass') == ' in MyClass'

def test__validation_location_class_and_method_name():
    assert validation._validation_location('MyClass', 'my_method') == ' in MyClass.my_method()'

def test__validation_location_method_name_only():
    with pytest.raises(ValueError):
        validation._validation_location(method_name='my_method')

def test__validation_location_function_name_only():
    assert validation._validation_location(function_name='my_function') == ' in my_function()'

def test__validation_location_function_name_and_class_name():
    with pytest.raises(ValueError):
        validation._validation_location(class_name='MyClass', function_name='my_function')

def test__validation_location_function_name_and_method_name():
    with pytest.raises(ValueError):
        validation._validation_location(class_name='MyClass', method_name='my_method', function_name='my_function')

@pytest.mark.parametrize('invalid_class_name', [5, True, [], {}])
def test__validation_location_rejects_invalid_class_name_type(invalid_class_name):
    with pytest.raises(TypeError):
        validation._validation_location(class_name=invalid_class_name)

@pytest.mark.parametrize('invalid_method_name', [5, True, [], {}])
def test__validation_location_rejects_invalid_method_name_type(invalid_method_name):
    with pytest.raises(TypeError):
        validation._validation_location(class_name='MyClass', method_name=invalid_method_name)

@pytest.mark.parametrize('invalid_function_name', [5, True, [], {}])
def test__validation_location_rejects_invalid_function_name_type(invalid_function_name):
    with pytest.raises(TypeError):
        validation._validation_location(function_name=invalid_function_name)

@pytest.mark.parametrize('value', INVALID_INT_TYPES)
def test_validate_int_rejects_non_ints(value):
    with pytest.raises(TypeError):
        validation.validate_int(value, 'value')

@pytest.mark.parametrize('value', [-15, -5, 0, 5, 15])
def test_validate_int_accepts_ints(value):
    validation.validate_int(value, 'value')

def test_validate_int_rejects_method_name_without_class_name_for_valid_value():
    with pytest.raises(ValueError):
        validation.validate_int(5, 'value', method_name='my_method')

@pytest.mark.parametrize('value', INVALID_INT_TYPES)
def test_validate_positive_int_rejects_non_ints(value):
    with pytest.raises(TypeError):
        validation.validate_positive_int(value, 'value')

@pytest.mark.parametrize('value', [1, 5, 15])
def test_validate_positive_int_accepts_positive_ints(value):
    validation.validate_positive_int(value, 'value')

@pytest.mark.parametrize('value', [0, -1, -5, -15])
def test_validate_positive_int_rejects_non_positive_ints(value):
    with pytest.raises(ValueError):
        validation.validate_positive_int(value, 'value')

@pytest.mark.parametrize('value', INVALID_INT_TYPES)
def test_validate_non_negative_int_rejects_non_ints(value):
    with pytest.raises(TypeError):
        validation.validate_non_negative_int(value, 'value')

@pytest.mark.parametrize('value', [0, 5, 10, 15])
def test_validate_non_negative_int_accepts_zero_and_positive_ints(value):
    validation.validate_non_negative_int(value, 'value')

@pytest.mark.parametrize('value', [-1, -5, -15])
def test_validate_non_negative_int_rejects_negative_ints(value):
    with pytest.raises(ValueError):
        validation.validate_non_negative_int(value, 'value')

@pytest.mark.parametrize('value', INVALID_NON_NONE_INT_TYPES)
def test_validate_optional_positive_int_rejects_non_ints(value):
    with pytest.raises(TypeError):
        validation.validate_optional_positive_int(value, 'value')

@pytest.mark.parametrize('value', [-15, -10, -5, 0])
def test_validate_optional_positive_int_rejects_non_positive_ints(value):
    with pytest.raises(ValueError):
        validation.validate_optional_positive_int(value, 'value')

@pytest.mark.parametrize('value', [1, 5, 15])
def test_validate_optional_positive_int_accepts_positive_ints(value):
    validation.validate_optional_positive_int(value, 'value')

def test_validate_optional_positive_int_accepts_none():
    validation.validate_optional_positive_int(None, 'value')

def test_validate_optional_positive_int_rejects_invalid_location_for_none():
    with pytest.raises(ValueError):
        validation.validate_optional_positive_int(None, 'value', method_name='my_method')

@pytest.mark.parametrize('value', INVALID_NON_NONE_INT_TYPES)
def test_validate_optional_non_negative_int_rejects_non_ints(value):
    with pytest.raises(TypeError):
        validation.validate_optional_non_negative_int(value, 'value')

@pytest.mark.parametrize('value', [-15, -10, -5])
def test_validate_optional_non_negative_int_rejects_negative_ints(value):
    with pytest.raises(ValueError):
        validation.validate_optional_non_negative_int(value, 'value')

@pytest.mark.parametrize('value', [0, 5, 10, 15])
def test_validate_optional_non_negative_int_accepts_zero_and_positive_ints(value):
    validation.validate_optional_non_negative_int(value, 'value')

def test_validate_optional_non_negative_int_accepts_none():
    validation.validate_optional_non_negative_int(None, 'value')

@pytest.mark.parametrize(('value', 'max_value'), [(-15, -10), (-5, 0), (0, 5), (5, 10), (15, 15)])
def test_validate_int_at_most_accepts_valid_values(value, max_value):
    validation.validate_int_at_most(value, max_value, 'value')

@pytest.mark.parametrize(('value', 'max_value'), [(-10, -15), (0, -5), (5, 0), (10, 5), (15, 10)])
def test_validate_int_at_most_rejects_invalid_values(value, max_value):
    with pytest.raises(ValueError):
        validation.validate_int_at_most(value, max_value, 'value')

@pytest.mark.parametrize('value', INVALID_INT_TYPES)
def test_validate_int_at_most_rejects_non_int_value(value):
    with pytest.raises(TypeError):
        validation.validate_int_at_most(value, 15, 'value')

@pytest.mark.parametrize('max_value', INVALID_INT_TYPES)
def test_validate_int_at_most_rejects_non_int_max_value(max_value):
    with pytest.raises(TypeError):
        validation.validate_int_at_most(10, max_value, 'value')

@pytest.mark.parametrize(('value', 'min_value'), [(-15, -15), (-10, -15), (0, 0), (1, 0), (5, 0), (10, 5), (15, 10)])
def test_validate_int_at_least_accepts_valid_values(value, min_value):
    validation.validate_int_at_least(value, min_value, 'value')

@pytest.mark.parametrize(('value', 'min_value'), [(-5, 0), (-1, 0), (0, 1), (5, 10), (10, 15)])
def test_validate_int_at_least_rejects_invalid_values(value, min_value):
    with pytest.raises(ValueError):
        validation.validate_int_at_least(value, min_value, 'value')

@pytest.mark.parametrize('value', INVALID_INT_TYPES)
def test_validate_int_at_least_rejects_non_int_value(value):
    with pytest.raises(TypeError):
        validation.validate_int_at_least(value, 0, 'value')

@pytest.mark.parametrize('min_value', INVALID_INT_TYPES)
def test_validate_int_at_least_rejects_non_int_min_value(min_value):
    with pytest.raises(TypeError):
        validation.validate_int_at_least(10, min_value, 'value')

@pytest.mark.parametrize('value', [0, 3, 5, 8, 12, 15])
def test_validate_int_in_range_accepts_inclusive_bounds(value):
    validation.validate_int_in_range(value, 0, 15, 'value')

@pytest.mark.parametrize('value', [-5, -1, 16, 20])
def test_validate_int_in_range_rejects_out_of_range_values(value):
    with pytest.raises(ValueError):
        validation.validate_int_in_range(value, 0, 15, 'value')

@pytest.mark.parametrize('value', INVALID_INT_TYPES)
def test_validate_int_in_range_rejects_non_int_value(value):
    with pytest.raises(TypeError):
        validation.validate_int_in_range(value, 0, 10, 'value')

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