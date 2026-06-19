"""Module for validating common project values with detailed error messages."""


def _validation_location(class_name: str | None = None, method_name: str | None = None, function_name: str | None = None) -> str:
    """Builds a location string for validation error messages."""
    if method_name is not None and class_name is None:
        raise ValueError('method_name cannot be provided without class_name')

    if function_name is not None and (class_name is not None or method_name is not None):
        raise ValueError('function_name cannot be provided with class_name or method_name')

    if class_name is not None and method_name is not None:
        return f' in {class_name}.{method_name}()'

    if class_name is not None:
        return f' in {class_name}'

    if function_name is not None:
        return f' in {function_name}()'

    return ''

def validate_int(value: int, 
                 var_name: str, 
                 class_name: str | None = None, 
                 method_name: str | None = None, 
                 *, 
                 function_name: str | None = None) -> None:
    """
    Validates that the value is an integer.
    
    Parameters
    ----------
    value : int
        The value to validate.
    var_name : str
        The name of the variable being validated.
    class_name : str | None, default=None
        The class in which the value is being validated.
    method_name : str | None, default=None
        The method in which the value is being validated.
    function_name : str | None, default=None
        The standalone function in which the value is being validated.
    Raises
    ------
    TypeError
        If the value is not an integer.
    """
    if type(value) is not int:
        location = _validation_location(class_name, method_name, function_name)
        raise TypeError(f'{var_name} must be an integer{location} - got {type(value).__name__}')

def validate_positive_int(value: int, 
                          var_name: str, 
                          class_name: str | None = None, 
                          method_name: str | None = None, 
                          *, 
                          function_name: str | None = None) -> None:
    """
    Validates that the value is a positive integer.
    
    Parameters
    ----------
    value : int
        The value to validate.
    var_name : str
        The name of the variable being validated.
    class_name : str | None, default=None
        The class in which the value may be being validated.
    method_name : str | None, default=None
        The method in which the value is being validated.
    function_name : str | None, default=None
        The standalone function in which the value is being validated.

    Raises
    ------
    TypeError
        If the value is not an integer.
    ValueError
        If the value is not a positive integer.
    """
    validate_int(value, var_name, class_name, method_name, function_name=function_name)
    if value <= 0:
        location = _validation_location(class_name, method_name, function_name)
        raise ValueError(f'{var_name} must be a positive integer{location} - got {value}')

def validate_non_negative_int(value: int, 
                              var_name: str, 
                              class_name: str | None = None, 
                              method_name: str | None = None, 
                              *, 
                              function_name: str | None = None) -> None:
    """
    Validates that the value is a non-negative integer.
    
    Parameters
    ----------
    value : int
        The value to validate.
    var_name : str
        The name of the variable being validated.
    class_name : str | None, default=None
        The class in which the value may be being validated.
    method_name : str | None, default=None
        The method in which the value is being validated.
    function_name : str | None, default=None
        The standalone function in which the value is being validated.

    Raises
    ------
    TypeError
        If the value is not an integer.
    ValueError
        If the value is negative.
    """
    validate_int(value, var_name, class_name, method_name, function_name=function_name)
    if value < 0:
        location = _validation_location(class_name, method_name, function_name)
        raise ValueError(f'{var_name} must be a non-negative integer{location} - got {value}')

def validate_optional_positive_int(value: int | None, 
                                   var_name: str, 
                                   class_name: str | None = None, 
                                   method_name: str | None = None, 
                                   *, 
                                   function_name: str | None = None) -> None:
    """
    Validates that the value is a positive integer or None.
    
    Parameters
    ----------
    value : int | None
        The value to validate.
    var_name : str
        The name of the variable being validated.
    class_name : str | None, default=None
        The class in which the value is being validated.
    method_name : str | None, default=None
        The method in which the value is being validated.
    function_name : str | None, default=None
        The standalone function in which the value is being validated.

    Raises
    ------
    TypeError
        If the value is not an integer or None.
    ValueError
        If the value is an integer but not positive.
    """
    if value is not None:
        validate_positive_int(value, var_name, class_name, method_name, function_name=function_name)

def validate_optional_non_negative_int(value: int | None, 
                                       var_name: str, 
                                       class_name: str | None = None, 
                                       method_name: str | None = None, 
                                       *, 
                                       function_name: str | None = None) -> None:
    """
    Validates that the value is a non-negative integer or None.
    
    Parameters
    ----------
    value : int | None
        The value to validate.
    var_name : str
        The name of the variable being validated.
    class_name : str | None, default=None
        The class in which the value is being validated.
    method_name : str | None, default=None
        The method in which the value is being validated.
    function_name : str | None, default=None
        The standalone function in which the value is being validated.

    Raises
    ------
    TypeError
        If the value is not an integer or None.
    ValueError
        If the value is an integer but negative.
    """
    if value is not None:
        validate_non_negative_int(value, var_name, class_name, method_name, function_name=function_name)

def validate_int_in_range(value: int, 
                          min_value: int, 
                          max_value: int, 
                          var_name: str, 
                          class_name: str | None = None, 
                          method_name: str | None = None, 
                          *, 
                          function_name: str | None = None) -> None:
    """
    Validates that the value is an integer within a specified range.
    
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
    class_name : str | None, default=None
        The class in which the value may be being validated.
    method_name : str | None, default=None
        The method in which the value is being validated.
    function_name : str | None, default=None
        The standalone function in which the value is being validated.

    Raises
    ------
    TypeError
        If the value, minimum value, or maximum value is not an integer.
    ValueError
        If min_value is greater than max_value, or if value is outside the range.
    """
    validate_int(min_value, 'Minimum value', function_name='validate_int_in_range')
    validate_int(max_value, 'Maximum value', function_name='validate_int_in_range')

    if min_value > max_value:
        raise ValueError(f'The minimum value must be less than or equal to the maximum value in validate_int_in_range() - got min={min_value}, max={max_value}')

    validate_int(value, var_name, class_name, method_name, function_name=function_name)

    if value < min_value or value > max_value:
        location = _validation_location(class_name, method_name, function_name)
        raise ValueError(f'{var_name} must be between {min_value} and {max_value} (inclusive){location} - got {value}')