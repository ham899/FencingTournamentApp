from dataclasses import dataclass

import validation

from entities.tournament_entry import TournamentEntry


@dataclass(frozen=True)
class SeededEntry:
    """
    Associate a tournament entry with its seed for a particular stage.

    A seeded entry represents an entry's positional ordering within the stage to which it is supplied. 

    Attributes
    ----------
    entry : TournamentEntry
        The tournament entry assigned the seed.
    seed : int
        The entry's one-based seed within the stage.
    previous_place : int | None, optional
        The entry's place in the previous stage. 
        None if there was no previous stage.
    """
    entry: TournamentEntry
    seed: int
    previous_place: int | None = None


    def __post_init__(self) -> None:
        """
        Validate the tournament entry and seed.
        
        Raises
        ------
        TypeError
            If ``entry`` is not a TournamentEntry, 
            if ``seed`` or ``previous_place`` is not an integer.
        ValueError
            If ``seed`` or ``previous_place`` is not positive.
        """
        location = self.__class__.__name__

        if not isinstance(self.entry, TournamentEntry):
            raise TypeError(
                f'Entry must be a TournamentEntry in {location} - got {type(self.entry).__name__}'
            )

        validation.validate_positive_int(self.seed, 'Seed', location)
        validation.validate_optional_positive_int(self.previous_place, 'Previous place', location)
