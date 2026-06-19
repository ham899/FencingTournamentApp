
def _validation_location(class_name: str, method_name: str | None = None) -> str:
    """Builds a location string for validation error messages."""
    location = f'in {class_name}'
    if method_name is not None:
        location += f'.{method_name}()'
    return location

def validate_int(value: int, var_name: str, class_name: str, method_name: str | None = None) -> None:
    """
    Validates that the value is an integer; raises a TypeError if not.
    
    Parameters
    ----------
    value : int
        The value to validate.
    var_name : str
        The name of the variable being validated.
    class_name : str
        The name of the class where the variable is being validated.
    method_name : str | None, default=None
        The name of the method where the variable is being validated, by default None.

    Raises
    ------
    TypeError
        If the value is not an integer.
    """
    if type(value) is not int:
        location = _validation_location(class_name, method_name)
        raise TypeError(f'{var_name} must be an integer {location} - got {type(value).__name__}')

def validate_positive_int(value: int, var_name: str, class_name: str, method_name: str | None = None) -> None:
    """
    Validates that the value is a positive integer; raises a ValueError if not.
    
    Parameters
    ----------
    value : int
        The value to validate.
    var_name : str
        The name of the variable being validated.
    class_name : str
        The name of the class where the variable is being validated.
    method_name : str | None, default=None
        The name of the method where the variable is being validated, by default None.

    Raises
    ------
    TypeError
        If the value is not an integer.
    ValueError
        If the value is not a positive integer.
    """
    validate_int(value, var_name, class_name, method_name)
    if value <= 0:
        location = _validation_location(class_name, method_name)
        raise ValueError(f'{var_name} must be a positive integer {location} - got {value}')

def validate_non_negative_int(value: int, var_name: str, class_name: str, method_name: str | None = None) -> None:
    """
    Validates that the value is a non-negative integer; raises a ValueError if not.
    
    Parameters
    ----------
    value : int
        The value to validate.
    var_name : str
        The name of the variable being validated.
    class_name : str
        The name of the class where the variable is being validated.
    method_name : str | None, default=None
        The name of the method where the variable is being validated, by default None.

    Raises
    ------
    TypeError
        If the value is not an integer.
    ValueError
        If the value is not a non-negative integer.
    """
    validate_int(value, var_name, class_name, method_name)
    if value < 0:
        location = _validation_location(class_name, method_name)
        raise ValueError(f'{var_name} must be a non-negative integer {location} - got {value}')

def validate_optional_positive_int(value: int | None, var_name: str, class_name: str, method_name: str | None = None) -> None:
    """
    Validates that the value is a positive integer or None; raises a ValueError if not.
    
    Parameters
    ----------
    value : int
        The value to validate.
    var_name : str
        The name of the variable being validated.
    class_name : str
        The name of the class where the variable is being validated.
    method_name : str | None, default=None
        The name of the method where the variable is being validated, by default None.

    Raises
    ------
    ValueError
        If the value is not a positive integer or None.
    """
    if value is not None:
        validate_positive_int(value, var_name, class_name, method_name)

def validate_optional_non_negative_int(value: int | None, var_name: str, class_name: str, method_name: str | None = None) -> None:
    """
    Validates that the value is a non-negative integer or None; raises a ValueError if not.
    
    Parameters
    ----------
    value : int
        The value to validate.
    var_name : str
        The name of the variable being validated.
    class_name : str
        The name of the class where the variable is being validated.
    method_name : str | None, default=None
        The name of the method where the variable is being validated, by default None.

    Raises
    ------
    ValueError
        If the value is not a non-negative integer or None.
    """
    if value is not None:
        validate_non_negative_int(value, var_name, class_name, method_name)

def validate_int_in_range(value: int, min_value: int, max_value: int, var_name: str, class_name: str, method_name: str | None = None) -> None:
    """
    Validates that the value is an integer within a specified range; raises a ValueError if not.
    
    Parameters
    ----------
    value : int
        The value to validate.
    min_value : int
        The minimum allowed value (inclusive).
    max_value : int
        The maximum allowed value (inclusive).
    var_name : str
        The name of the variable being validated.
    class_name : str
        The name of the class where the variable is being validated.
    method_name : str | None, default=None
        The name of the method where the variable is being validated.

    Raises
    ------
    TypeError
        If the value, minimum value, or maximum value is not an integer.
    ValueError
        If min_value is greater than max_value, or if value is outside the range.
    """
    if type(min_value) is not int:
        raise TypeError(f'The minimum value must be an integer - got {min_value}.')
    if type(max_value) is not int:
        raise TypeError(f'The maximum value must be an integer - got {max_value}.')
    if min_value > max_value:
        raise ValueError(f'The minimum value must be less than or equal to the maximum value - got min={min_value}, max={max_value}')
    validate_int(value, var_name, class_name, method_name)

    if value < min_value or value > max_value:
        location = _validation_location(class_name, method_name)
        raise ValueError(f'{var_name} must be between {min_value} and {max_value} (inclusive) {location} - got {value}')
