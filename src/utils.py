def is_power_of_two(n: int) -> bool:
    """
    Checks whether the input is a power of two.
    
    Parameters
    ----------
    n : int
        The number under scrutiny.
    
    Returns
    -------
    bool
        Returns true if the input is a power of two; otherwise, returns false.
    """
    if type(n) is not int:
        raise TypeError('Input must be an integer')
    if n <= 0:
        return False
    while n % 2 == 0:
        n = n // 2
    return n == 1

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
    if type(n) is not int:
        raise TypeError('Input must be an integer')
    if not is_power_of_two(n):
        raise ValueError('Input must be a power of two')
    count=0
    while n != 1:
        n //= 2
        count+=1
    return count