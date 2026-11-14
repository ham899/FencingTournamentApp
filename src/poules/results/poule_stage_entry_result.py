from dataclasses import dataclass

import validation

from poules.results.poule_stats import PouleStats
from tournament.results.stage import StageEntryResult


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
    position : int
        The entry's unique one-based index in the stage snapshot's ranked_results.
        Defines display order and the relative seeding order of advancing entries.
        Does not imply a confirmed placement.
    place : int | None
        The entry's confirmed placement within the poule stage.
        Equals current_place once the entire stage is complete; otherwise None.
    is_tie : bool | None
        Whether the confirmed place is shared with another entry.
        None while the stage is incomplete.
    poule_stats : PouleStats
        The entry's aggregate statistics across the included poule rounds.
    current_place : int
        The entry's current one-based placement in the aggregate stage ranking.
        Entries equal on all ranking criteria share the same current place.
        May change while the stage is incomplete.
    is_current_tie : bool
        Whether another entry shares the same current ranking criteria
        and current place. May change while the stage is incomplete.

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
    current_place: int
    is_current_tie: bool


    # --- Initialization and Validation ---
    def __post_init__(self) -> None:
        """
        Validate the inherited fields, statistics, and current standing.

        Raises
        ------
        TypeError
            If an inherited field or a checked entry attribute has an invalid type,
            if ``poule_stats`` is not a PouleStats object, if ``current_place`` is not an integer,
            or if ``is_current_tie`` is not a boolean.
        ValueError
            If a required integer is not positive, if exactly one of ``place`` and ``is_tie`` is None,
            or if a confirmed place or tie flag differs from its current counterpart.
        """
        location = self.__class__.__name__

        super(PouleStageEntryResult, self).__post_init__()

        if not isinstance(self.poule_stats, PouleStats):
            raise TypeError(
                f'Poule statistics must be a PouleStats object in {location}'
                f' - got {type(self.poule_stats).__name__}'
            )

        validation.validate_positive_int(self.current_place, 'Current place', location)

        if self.place is not None and self.place != self.current_place:
            raise ValueError(
                f'A confirmed poule stage place must equal current_place in {location}'
                f' - got place={self.place}, current_place={self.current_place}'
            )
        
        validation.validate_bool(self.is_current_tie, 'Is current tie', location)

        if self.place is not None and self.is_tie != self.is_current_tie:
            raise ValueError(
                f'Confirmed and current tie flags must agree in {location}'
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
