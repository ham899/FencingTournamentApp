from dataclasses import dataclass

import validation
from entities.fencer import Fencer

@dataclass(eq=False)
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

    initial_seed : int | None
        The initial seed of the entry, which may be assigned upon initialization. 
        The seed values do not have to have a one-to-one mapping with the number of entries upon initialization.
        The one-to-one mapping will be inferred after initialization but before poules are generated.

    de_seed : int | None
        The DE seed of the entry, which should only be assigned if the tournament is a DE only event; otherwise, it should not be assigned. 
        If assigned for a non-DE only event, it will be reassigned after poules are completed.
    """
    id: int
    tournament_id: int
    fencer: Fencer

    initial_seed: int | None = None
    de_seed: int | None = None

    @property
    def display_name(self) -> str:
        """Gets the display name of the entry."""
        return self.fencer.display_name

    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validates the entry ID and tournament ID to be positive integers. Ensures the supplied fencer 
        is a fencer object. Checks that provided seeds are positive integers.

        Raises
        ------
        TypeError
            If any attribute is an invalid type.
        ValueError
            If any of the numeric attributes are not positive integers.
        """
        # Validate IDs
        validation.validate_positive_int(self.id, 'ID', 'TournamentEntry')
        validation.validate_positive_int(self.tournament_id, 'Tournament ID', 'TournamentEntry')

        # Validate fencer
        if not isinstance(self.fencer, Fencer):
            raise TypeError('Fencer parameter must be an instance of a Fencer class')
        
        # Validate Optional Seeds
        validation.validate_optional_positive_int(self.initial_seed, 'Initial seed', 'TournamentEntry')
        validation.validate_optional_positive_int(self.de_seed, 'DE seed', 'TournamentEntry')

    # --- Dunder Methods ---
    def __eq__(self, other: object) -> bool:
        """
        Determines whether two tournament entries represent the same entry based on their entry ID and tournament ID.
        Seeds are not considered in the equality check because they may change during the tournament.

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
        return self.id == other.id and self.tournament_id == other.tournament_id

    # --- Setter Methods ---
    def set_initial_seed(self, seed: int | None) -> None:
        """
        Sets a new initial seed of the entry.
        
        Parameters
        ----------
        seed : int | None
            The initial seed to assign to the entry. Must be a positive integer or None.

        Raises
        ------
        TypeError
            If the seed is not an integer.
        ValueError
            If the seed is not a positive integer.
        """
        validation.validate_optional_positive_int(seed, 'Initial seed', 'TournamentEntry')
        self.initial_seed = seed

    def set_de_seed(self, seed: int | None) -> None:
        """
        Sets a new DE seed of the entry.

        Parameters
        ----------
        seed : int | None
            The DE seed to assign to the entry. Must be a positive integer or None.

        Raises
        ------
        TypeError
            If the seed is not an integer.
        ValueError
            If the seed is not a positive integer.
        """
        validation.validate_optional_positive_int(seed, 'DE seed', 'TournamentEntry')
        self.de_seed = seed