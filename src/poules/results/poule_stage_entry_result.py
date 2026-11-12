from dataclasses import dataclass

from poules.results.poule_stats import PouleStats
from tournament.results.stage.stage_entry_result import StageEntryResult


@dataclass(frozen=True, slots=True)
class PouleStageEntryResult(StageEntryResult):
    """
    Represent a snapshot of an entry's aggregate standing in a poule stage.

    Inherit common standing fields and validation from StageEntryResult.
    The supplied statistics represent completed matches across the included poule rounds. 
    Statistic properties delegate to the immutable PouleStats object.

    Fields cannot be reassigned after initialization. 
    The tournament entry is retained by reference rather than copied.

    Rankings may be provisional while the stage is incomplete. 
    The caller determines the entry's status, position, placement, 
    and tie information from the aggregate stage results.

    Attributes
    ----------
    entry : TournamentEntry
        The tournament entry whose stage standing is represented.
    stage_number : int
        The poule stage's one-based position within the tournament.
    status : StageEntryStatus
        The entry's elimination status within the stage.
    position : int | None
        The entry's unique one-based position in the aggregate stage ranking.
        Used to order advancing entries for seeding into the next stage.
        None if a position has not been assigned.
    place : int | None
        The entry's one-based placement in the aggregate stage ranking.
        Entries tied in the ranking share the same place.
        None if a placement has not been assigned.
    is_tie : bool | None
        Whether the assigned place is shared with another entry.
        None if a placement has not been assigned.
    poule_stats : PouleStats
        The entry's aggregate statistics across the included poule rounds.

    Notes
    -----
    An entry with no completed matches has a victory ratio of 0.0.
    The victory ratio is calculated from the combined victory and match
    totals, rather than averaging individual round ratios.

    ``place`` and ``is_tie`` must either both be assigned or both be None.
    This class validates their consistency but does not calculate rankings
    or verify ties against other entries.
    """
    poule_stats: PouleStats


    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validate the inherited standing fields and supplied statistics object.

        Raises
        ------
        TypeError
            If an inherited field or a checked entry attribute has an invalid type, 
            or if ``poule_stats`` is not a PouleStats object.
        ValueError
            If a required integer is not positive, 
            or if exactly one of ``place`` and ``is_tie`` is None.
        """
        location = self.__class__.__name__

        super(PouleStageEntryResult, self).__post_init__()

        if not isinstance(self.poule_stats, PouleStats):
            raise TypeError(
                f'Poule statistics must be a PouleStats object in {location}'
                f' - got {type(self.poule_stats).__name__}'
            )


    # --- Properties ---
    @property
    def label(self) -> str:
        """Return a descriptive label identifying the entry, stage, and tournament."""
        return (
            f'{self.__class__.__name__} for {self.display_name} (ID={self.entry.id}) '
            f'in stage {self.stage_number} in tournament {self.tournament_id}'
        )

    @property
    def num_matches(self) -> int:
        """Return the number of completed matches represented by the aggregate statistics."""
        return self.poule_stats.num_matches

    @property
    def num_victories(self) -> int:
        """Return the number of victories across the included poule rounds."""
        return self.poule_stats.num_victories

    @property
    def touches_scored(self) -> int:
        """Return the total touches credited to the entry across the included poule rounds."""
        return self.poule_stats.touches_scored

    @property
    def touches_received(self) -> int:
        """Return the total touches credited against the entry across the included poule rounds."""
        return self.poule_stats.touches_received

    @property
    def victory_ratio(self) -> float:
        """Return combined victories divided by combined matches, or 0.0 if no matches are represented."""
        return self.poule_stats.victory_ratio

    @property
    def indicator(self) -> int:
        """Return aggregate touches scored minus aggregate touches received."""
        return self.poule_stats.indicator
