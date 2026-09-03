"""Module for calculating tournament specific values and properties."""


import validation
from collections.abc import Iterator


def is_power_of_two(n: int) -> bool:
    """
    Checks whether the input is a power of two.
    
    Parameters
    ----------
    n : int
        The number being examined.
    
    Returns
    -------
    bool
        True if the input is a power of two; otherwise, False.

    Raises
    ------
    TypeError
        If the input is not an integer.
    """
    validation.validate_int(n, 'n', function_name='is_power_of_two')

    return n > 0 and (n & (n - 1)) == 0


def log2_int(n: int) -> int:
    """
    Returns the base-2 logarithm as an integer of the input, which must be a power of 2. 
    
    Parameters
    ----------
    n : int
        The integer to take the logarithm of.

    Returns
    -------
    int
        The base-two logarithm of the input value.

    Raises
    ------
    TypeError
        If the input is not an integer.
    ValueError
        If the input is not a power of two.
    """
    validation.validate_int(n, 'n', function_name='log2_int')

    if not is_power_of_two(n):
        raise ValueError(f'n must be a power of two in log2_int() - got {n}')
    
    return n.bit_length() - 1


def snake_numbers(stop: int, start: int = 0) -> Iterator[int]:
    """
    Yield integers repeatedly in ascending and descending order.

    Both endpoints of the yielded range are repeated when the direction changes.

    Parameters
    ----------
    stop : int
        The exclusive upper bound of the yielded numbers.
    start : int, optional
        The inclusive lower bound of the yielded numbers. Default is 0.

    Yields
    ------
    int
        The next integer in the repeating snake pattern.

    Raises
    ------
    TypeError
        If `start` or `stop` is not an integer.
    ValueError
        If `stop` is not greater than `start`.
    """
    validation.validate_int(stop, 'stop', function_name='snake_numbers')
    validation.validate_int(start, 'start', function_name='snake_numbers')

    if stop <= start:
        raise ValueError(f'stop must be greater than start in snake_numbers() - got start={start}, stop={stop}')

    while True:
        yield from range(start, stop)
        yield from range(stop - 1, start - 1, -1)
