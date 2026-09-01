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
    """
    entry: TournamentEntry
    seed: int

    def __post_init__(self) -> None:
        """
        Validate the tournament entry and seed.
        
        Raises
        ------
        TypeError
            If ``entry`` is not a TournamentEntry, or if ``seed`` is not an integer.
        ValueError
            If ``seed`` is not positive.
        """
        if not isinstance(self.entry, TournamentEntry):
            raise TypeError(
                f'Entry must be a TournamentEntry in SeededEntry - got {type(self.entry).__name__}'
            )

        validation.validate_positive_int(self.seed, 'Seed', 'SeededEntry')
