from dataclasses import dataclass
from typing import Optional

from fencer import Fencer

@dataclass
class TournamentEntry:
    """
    Represents an entry participating in a tournament.
    An entry is a fencer in a specific tournament; one entry can only be associated with one fencer and one tournament.

    Attributes
    ----------
    id : int
        Unique identifier for the tournament entry.
    tournament_id : int
        Identifier for the tournament this entry is associated with.
    fencer : Fencer
        The fencer associated with this tournament entry.
    initial_seed : Optional[int]
        The initial seed of the entry, which may be assigned upon initialization. 
        The seed values do not have to have a one-to-one mapping with the number of entries upon initialization.
        The one-to-one mapping will be inferred after initialization but before poules are generated.
    de_seed : Optional[int]
        The DE seed of the entry, which should only be assigned if the tournament is a DE only event; otherwise, it should not be assigned. 
        If assigned for a non-DE only event, it will be reassigned after poules are completed.
    """
    id: int
    tournament_id: int
    fencer: Fencer

    initial_seed: Optional[int] = None
    de_seed: Optional[int] = None

    def __post_init__(self) -> None:
        """
        Validates the entry ID and tournament ID to be positive integers.
        Ensures the supplied fencer is a fencer object.
        Checks that provided seeds are positive integers.

        Raises
        ------
        TypeError
            If any attribute is an invalid type.
        ValueError
            If any of the numberic attributes are not positive integers.
        """
        # Validate types
        if type(self.id) is not int:
            raise TypeError('ID must be an integer')
        
        if type(self.tournament_id) is not int:
            raise TypeError('Tournament ID must be an integer')
        
        if not isinstance(self.fencer, Fencer):
            raise TypeError('Fencer parameter must be an instance of a Fencer class')
        
        if self.initial_seed is not None and type(self.initial_seed) is not int:
            raise TypeError('Provided initial seed must be an integer')

        if self.de_seed is not None and type(self.de_seed) is not int:
            raise TypeError('Provided DE seed must be an integer')

        # Validate values
        if self.id <= 0:
            raise ValueError('ID must be a positive integer')
        
        if self.tournament_id <= 0:
            raise ValueError('Tournament ID must be a positive integer')

        if self.initial_seed is not None and self.initial_seed <= 0:
            raise ValueError('Provided initial seed must be a positive integer')

        if self.de_seed is not None and self.de_seed <= 0:
            raise ValueError('Provided DE seed must be a positive integer')

    def __eq__(self, other: object) -> bool:
        """
        Determines if two tournament entries are equal based on their entry IDs, tournament IDs, and the fencers associated with the objects.
        Seeds are not considered in the equality check because they may change after initialization.

        Parameters
        ----------
        other : object
            The object to compare with this tournament entry.

        Returns
        -------
        bool
            True if the other object is a TournamentEntry with the same ID, False otherwise.
        """
        if not isinstance(other, TournamentEntry):
            return False
        return self.id == other.id and self.tournament_id == other.tournament_id and self.fencer == other.fencer

    def set_initial_seed(self, seed: int) -> None:
        """
        Sets a new initial seed of the entry.
        
        Parameters
        ----------
        seed : int
            The initial seed to assign to the entry. Must be a positive integer.

        Raises
        ------
        TypeError
            If the seed is not an integer.
        ValueError
            If the seed is not a positive integer.
        """
        if seed is not None and type(seed) is not int:
            raise TypeError(f'Provided seed must be an integer when setting initial seed for entry with ID {self.id}; got {type(seed)} instead')
        if seed is not None and seed <= 0:
            raise ValueError(f'Provided seed must be a positive integer when setting initial seed for entry with ID {self.id}; got {seed} instead')

        self.initial_seed = seed

    def set_de_seed(self, seed: int) -> None:
        """
        Sets a new DE seed of the entry.

        Parameters
        ----------
        seed : int
            The DE seed to assign to the entry. Must be a positive integer.

        Raises
        ------
        TypeError
            If the seed is not an integer.
        ValueError
            If the seed is not a positive integer.
        """
        if seed is not None and type(seed) is not int:
            raise TypeError(f'Provided seed must be an integer when setting a DE seed for entry with ID {self.id}; got {type(seed)} instead')
        if seed is not None and seed <= 0:
            raise ValueError(f'Provided seed must be a positive integer when setting a DE seed for entry with ID {self.id}; got {seed} instead')

        self.de_seed = seed

    def display_name(self) -> str:
        """
        Gets the display name of this entry.
        
        Returns
        -------
        str
            The display name of the fencer associated with this tournament entry.
        """
        return self.fencer.display_name