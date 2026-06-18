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
    message = f'{var_name} must be an integer in {class_name}'
    if method_name is not None:
        message += f' in method {method_name}'
    if type(value) is not int:
        raise TypeError(message)

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
    ValueError
        If the value is not a positive integer.
    """
    message = f'{var_name} must be a positive integer in {class_name}'
    if method_name is not None:
        message += f' in method {method_name}'
    validate_int(value, var_name, class_name, method_name)
    if value <= 0:
        raise ValueError(message)

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
    ValueError
        If the value is not a non-negative integer.
    """
    message = f'{var_name} must be a non-negative integer in {class_name}'
    if method_name is not None:
        message += f' in method {method_name}'
    validate_int(value, var_name, class_name, method_name)
    if value < 0:
        raise ValueError(message)

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
    message = f'{var_name} must be a positive integer or None in {class_name}'
    if method_name is not None:
        message += f' in method {method_name}'
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
    message = f'{var_name} must be a non-negative integer or None in {class_name}'
    if method_name is not None:
        message += f' in method {method_name}'
    if value is not None:
        validate_non_negative_int(value, var_name, class_name, method_name)
