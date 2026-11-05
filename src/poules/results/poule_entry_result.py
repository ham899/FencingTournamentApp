from dataclasses import dataclass

import validation

from entities.tournament_entry import TournamentEntry
from poules.results.poule_stats import PouleStats


@dataclass(frozen=True, slots=True)
class PouleEntryResult:
    """
    Represents a single entry's calculated result snapshot for a poule.

    The supplied statistics represent completed matches in the specified poule.
    Statistic properties delegate to the immutable PouleStats object.
    This object's fields cannot be reassigned after initialization.

    Attributes
    ----------
    entry : TournamentEntry
        The tournament entry whose poule results are represented.
    poule_number : int
        The poule's one-based position within its round.
    round_number : int
        The poule round's one-based position within the poule stage.
    stage_number : int
        The poule stage's one-based position within the tournament.
    poule_stats : PouleStats
        The immutable statistics for the entry in the poule.

    Notes
    -----
    An entry with no completed matches has a victory ratio of 0.0.
    """
    entry: TournamentEntry
    poule_number: int
    round_number: int
    stage_number: int
    poule_stats: PouleStats


    # --- Initialization and Validation Methods ---
    def __post_init__(self) -> None:
        """
        Validate the supplied entry, poule number, round number, stage number, and statistics object.

        Raises
        ------
        TypeError
            If entry is not a TournamentEntry, if its tournament ID,
            poule_number, round_number, or stage_number is not an integer,
            or if poule_stats is not a PouleStats object.
        ValueError
            If the entry's tournament ID, poule number, round number, or stage number is not positive.
        """
        location = 'PouleEntryResult'

        # Validate the provided entry
        self._validate_entry(self.entry)

        # Validate the poule number, round number, and stage number
        validation.validate_positive_int(self.stage_number, 'Stage number', location)
        validation.validate_positive_int(self.round_number, 'Round number', location)
        validation.validate_positive_int(self.poule_number, 'Poule number', location)

        # Validate the provided statistics object
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
            f'PouleEntryResult for {self.display_name} in poule {self.poule_number} ' 
            f'of round {self.round_number} in stage {self.stage_number} in tournament {self.tournament_id}'
        )

    @property
    def tournament_id(self) -> int:
        """Return the tournament ID of this result."""
        return self.entry.tournament_id

    @property
    def display_name(self) -> str:
        """Return the display name of the entry."""
        return self.entry.display_name

    @property
    def num_matches(self) -> int:
        """Return the number of completed matches for the entry in the poule."""
        return self.poule_stats.num_matches

    @property
    def num_victories(self) -> int:
        """Return the number of victories for the entry in the poule."""
        return self.poule_stats.num_victories

    @property
    def touches_scored(self) -> int:
        """Return the total touches credited to the entry in the poule."""
        return self.poule_stats.touches_scored

    @property
    def touches_received(self) -> int:
        """Return the total touches credited against the entry in the poule."""
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
    def _validate_entry(self, entry: TournamentEntry) -> None:
        """
        Validate the tournament entry represented by this result.

        Parameters
        ----------
        entry : TournamentEntry
            The tournament entry to validate.

        Raises
        ------
        TypeError
            If `entry` is not a `TournamentEntry`, or if its tournament ID is not an integer.
        ValueError
            If the entry's tournament ID is not positive.
        """
        location = 'PouleEntryResult'
        if not isinstance(entry, TournamentEntry):
            raise TypeError(f'Entry must be TournamentEntry in {location} - got {type(entry).__name__}')

        validation.validate_positive_int(entry.tournament_id, 'Entry tournament ID', location)
