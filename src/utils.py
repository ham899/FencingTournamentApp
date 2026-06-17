# --- Helper functions ---
def _validate_int(value: int, name: str) -> None:
    """
    Validates that a value is an integer.

    Parameters
    ----------
    value : int
        The value to validate.
    name : str
        The name of the value, used in the error message.

    Raises
    ------
    TypeError
        If the value is not an integer.
    """
    if type(value) is not int:
        raise TypeError(f'{name} must be an integer - got {type(value)}')

# --- Main functions ---
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
    _validate_int(n, 'n')
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
    _validate_int(n, 'n')
    if not is_power_of_two(n):
        raise ValueError('Input must be a power of two')

    return n.bit_length() - 1

def calculate_number_poule_matches(poule_size: int) -> int:
    """
    Calculates the number of poule matches in a poule based on the poule's size.
    
    Parameters
    ----------
    poule_size : int
        The number of people in the poule.
    
    Returns
    -------
    int
        The number of matches in the poule.
    
    Raises
    ------
    TypeError
        If the poule size input is not an integer.
    ValueError
        If the poule size input is less than 2.
    """
    _validate_int(poule_size, 'poule_size')
    if poule_size < 2:
        raise ValueError(f'There must be at least two people in a poule - got {poule_size}')
    
    return poule_size * (poule_size - 1) // 2

def calculate_number_of_de_rounds(number_de_entries: int) -> int:
    """
    Calculates the number of rounds in a DE bracket based on the number of entries in the bracket.
    
    Parameters
    ----------
    number_de_entries : int
        The number of entries in the DE bracket.

    Returns
    -------
    int
        The number of rounds in the DE bracket.

    Raises
    ------
    TypeError
        If the number of entries input is not an integer.
    ValueError
        If the number of entries input is less than 2.
    """
    _validate_int(number_de_entries, 'number_de_entries')
    if number_de_entries < 2:
        raise ValueError(f'The number of entries in the DE bracket must be at least 2 - got {number_de_entries}')

    return (number_de_entries - 1).bit_length()

def calculate_number_matches_in_de_round(round_index: int, number_de_entries: int) -> int:
    """
    Calculates the number of matches in a specific round in a DE bracket based on 
    the round index and number of DE entries given.

    **Note:** BYEs are counted as matches because they occupy positions in the DE bracket
    and can be represented as automatically completed matches.

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
        If the round index or number of entries is not an integer.
    ValueError
        If the number of entries is less than 2, or if the round index is outside the valid range of rounds.
    """
    _validate_int(round_index, 'round_index')
    _validate_int(number_de_entries, 'number_de_entries')
    
    if number_de_entries < 2:
        raise ValueError(f'The number of DE entries input must be at least 2 - got {number_de_entries}')
    
    number_of_rounds = calculate_number_of_de_rounds(number_de_entries)
    
    if round_index < 0 or round_index > number_of_rounds - 1:
        raise ValueError(f'The round index must be between 0 and {number_of_rounds - 1} - got {round_index}')
    
    return 2 ** (number_of_rounds - round_index - 1)