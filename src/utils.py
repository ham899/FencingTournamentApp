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

def calculate_number_poule_matches(poule_size: int) -> int:
    """
    Calculates the number of poule matches in a poule based on the poule's size.
    """
    if type(poule_size) is not int:
        raise TypeError(f'The poule size input must be an integer - got {type(poule_size)}')
    if poule_size < 2:
        raise ValueError(f'There must be at least two people in a poule - got {poule_size}')
    return poule_size*(poule_size-1) // 2

def calculate_number_of_de_rounds(number_de_entries: int) -> int:
    """
    Calculates the number of rounds in a DE bracket based on the number of entries in the bracket.
    """
    if type(number_de_entries) is not int:
        raise TypeError(f'The number of entries in the DE bracket must be an integer - got {type(number_de_entries)}')
    if number_de_entries < 2:
        raise ValueError(f'The number of entries in the DE bracket must be at least 2 - got {number_de_entries}')
    i = 0
    while not is_power_of_two(number_de_entries+i):
        i+=1
    return log2_int(n=number_de_entries+i)
    
def calculate_number_matches_in_de_round(round_index: int, number_de_entries: int) -> int:
    """
    Calculates the number of matches in a specific round in a DE bracket based on 
    the round index and number of DE entries given.

    Parameters
    ----------
    round_index : int
        The round index under examination.
    number_de_entries : int
        The number of entrants in the DE tableau.
    
    Returns
    -------
    int
        The number of matches in the round.

    Raises
    ------
    TypeError
        If the index inputs are not integers.
    ValueError
        If the index inputs are negative or if the round index input is greater than the maximum.
    """
    if type(round_index) is not int:
        raise TypeError(f'The round index input must be an integer - got {type(round_index)}')
    if type(number_de_entries) is not int:
        raise TypeError(f'The number of DE entries input must be an integer - got {type(number_de_entries)}')
    if number_de_entries < 2:
        raise ValueError(f'The number of DE entries input must be at least 2 - got {number_de_entries}')
    number_of_rounds = calculate_number_of_de_rounds(number_de_entries)
    if round_index < 0 or round_index > number_of_rounds-1:
        raise ValueError(f'The round index must be between 0 and {number_of_rounds-1} - got {round_index}')
    
    return 2**(number_of_rounds-round_index-1)