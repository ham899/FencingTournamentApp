from dataclasses import dataclass

import validation

from entities.fencer import Fencer


@dataclass(eq=False)
class TournamentEntry:
    """
    Represents an entry participating in a tournament.
    An entry is a fencer in a specific tournament; 
    one entry can only be associated with one fencer and one tournament.

    Attributes
    ----------
    id : int
        Unique identifier for the tournament entry.
    tournament_id : int
        Identifier for the tournament this entry is associated with.
    fencer : Fencer
        The fencer associated with this tournament entry.
    """
    id: int
    tournament_id: int
    fencer: Fencer


    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validates the entry ID and tournament ID to be positive integers. 
        Ensures the supplied fencer is a fencer object.

        Raises
        ------
        TypeError
            If any attribute is an invalid type.
        ValueError
            If any of the numeric attributes are not positive integers.
        """
        validation.validate_positive_int(self.id, 'ID', 'TournamentEntry')
        validation.validate_positive_int(self.tournament_id, 'Tournament ID', 'TournamentEntry')

        if not isinstance(self.fencer, Fencer):
            raise TypeError(f'Fencer in TournamentEntry must be a Fencer - got {type(self.fencer).__name__}')


    # --- Properties ---
    @property
    def display_name(self) -> str:
        """Gets the display name of the entry."""
        return self.fencer.display_name


    # --- Equality ---
    def __eq__(self, other: object) -> bool:
        """
        Determine whether another object represents the same tournament entry.

        Tournament entries are identified by the combination of their entry ID and tournament ID.

        Parameters
        ----------
        other : object
            The object to compare with this tournament entry.

        Returns
        -------
        bool
            True if `other` is a `TournamentEntry` with the same entry ID and
            tournament ID; otherwise, False.
        """
        if not isinstance(other, TournamentEntry):
            return False
        
        return self.id == other.id and self.tournament_id == other.tournament_id
