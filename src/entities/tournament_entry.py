from dataclasses import dataclass

import validation

from entities.fencer import Fencer
from entities.weapon import Weapon


@dataclass(eq=False, frozen=True)
class TournamentEntry:
    """
    Represent a fencer's entry in a tournament.

    The entry's fields are fixed at creation. 
    The tournament ID and entry ID together identify the entry.

    Attributes
    ----------
    id : int
        Identifier unique within this tournament.
    tournament_id : int
        Identifier of the tournament this entry belongs to.
    fencer : Fencer
        The fencer represented by this entry.
    weapon : Weapon
        The weapon the fencer uses in this tournament.
    """
    id: int
    tournament_id: int
    fencer: Fencer
    weapon: Weapon


    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validate the entry identifiers, fencer, and weapon.

        Raises
        ------
        TypeError
            If either identifier has a type other than ``int``, 
            or if ``fencer`` or ``weapon`` has the wrong type.
        ValueError
            If either identifier is zero or negative.
        """
        location = self.__class__.__name__

        validation.validate_positive_int(self.id, 'ID', location)
        validation.validate_positive_int(self.tournament_id, 'Tournament ID', location)

        if not isinstance(self.fencer, Fencer):
            raise TypeError(
                f'Fencer in {location} must be a Fencer - got {type(self.fencer).__name__}'
            )

        if not isinstance(self.weapon, Weapon):
            raise TypeError(
                f'Weapon of entry in {location} must be a Weapon instance - got {type(self.weapon).__name__}'
            )


    # --- Properties ---
    @property
    def display_name(self) -> str:
        """Return the associated fencer's current display name."""
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
