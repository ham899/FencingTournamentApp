from dataclasses import dataclass

import validation

from entities.tournament_entry import TournamentEntry
from poules.results.poule_stats import PouleStats


@dataclass(frozen=True, slots=True)
class PouleStageEntryResult:
    """
    Represents a single entry's aggregate result snapshot for a poule stage.

    The supplied statistics represent completed poule matches across the
    rounds included in the stage results. 
    Statistic properties delegate to the immutable PouleStats object. 
    This object's fields cannot be reassigned after initialization.

    Attributes
    ----------
    entry : TournamentEntry
        The tournament entry whose stage results are represented.
    stage_number : int
        The poule stage's one-based position within the tournament.
    poule_stats : PouleStats
        The entry's aggregate statistics across the included poule rounds.

    Notes
    -----
    An entry with no completed matches has a victory ratio of 0.0.
    The victory ratio is calculated from the combined victory and match totals, 
    rather than averaging the individual round ratios.
    """
    entry: TournamentEntry
    stage_number: int
    poule_stats: PouleStats


    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validate the supplied entry, stage number, and statistics object.

        Raises
        ------
        TypeError
            If entry is not a TournamentEntry, 
            if its tournament ID or ``stage_number`` is not an integer, 
            or if poule_stats is not a PouleStats object.
        ValueError
            If the entry's tournament ID or ``stage_number`` is not positive.
        """
        location = 'PouleStageEntryResult'

        self._validate_entry(self.entry, location)
        validation.validate_positive_int(self.stage_number, 'Stage number', location)

        if not isinstance(self.poule_stats, PouleStats):
            raise TypeError(
                f'Poule statistics must be a PouleStats object in {location} - '
                f'got {type(self.poule_stats).__name__}'
            )


    # --- Properties ---
    @property
    def label(self) -> str:
        """Return a descriptive label for the object."""
        return (
            f'PouleStageEntryResult for {self.display_name} in stage '
            f'{self.stage_number} in tournament {self.tournament_id}'
        )

    @property
    def display_name(self) -> str:
        """Return the display name of the entry."""
        return self.entry.display_name

    @property
    def tournament_id(self) -> int:
        """Return the tournament ID of this result."""
        return self.entry.tournament_id

    @property
    def num_matches(self) -> int:
        """Return the number of completed matches for the entry in the poule stage."""
        return self.poule_stats.num_matches

    @property
    def num_victories(self) -> int:
        """Return the number of victories for the entry in the poule stage."""
        return self.poule_stats.num_victories

    @property
    def touches_scored(self) -> int:
        """Return the total touches credited to the entry in the poule stage."""
        return self.poule_stats.touches_scored

    @property
    def touches_received(self) -> int:
        """Return the total touches credited against the entry in the poule stage."""
        return self.poule_stats.touches_received

    @property
    def victory_ratio(self) -> float:
        """Return the entry's victory ratio, or 0.0 if no matches have been completed."""
        return self.poule_stats.victory_ratio

    @property
    def indicator(self) -> int:
        """Return touches scored minus touches received for the entry."""
        return self.poule_stats.indicator


    # --- Validation Helper Methods ---
    def _validate_entry(self, entry: TournamentEntry, location: str) -> None:
        """
        Validate the tournament entry represented by this result.

        Parameters
        ----------
        entry : TournamentEntry
            The tournament entry to validate.
        location : str
            The class name to use in validation error messages.

        Raises
        ------
        TypeError
            If entry is not a TournamentEntry, or if its tournament ID is not an integer.
        ValueError
            If the entry's tournament ID is not positive.
        """
        if not isinstance(entry, TournamentEntry):
            raise TypeError(
                f'Entry must be a TournamentEntry in {location} - got {type(entry).__name__}'
            )

        validation.validate_positive_int(entry.tournament_id, 'Entry tournament ID', location)
