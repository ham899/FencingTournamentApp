from dataclasses import dataclass, field, InitVar

import validation

from entities import TournamentEntry
from tournament.results.stage import StageEntryResult, StageEntryStatus, StageResults
from tournament.results.tournament_entry_result import TournamentEntryResult, TournamentEntryStatus
from tournament.tournament_stage import TournamentStage


@dataclass(frozen=True, slots=True)
class TournamentResults:
    """
    Represent a fixed snapshot of the overall tournament standings.

    Use each entry's latest stage result to determine its tournament standing.
    Entries reaching later stages rank ahead of entries left in earlier stages.
    Within each group, preserve the latest stage's ranking order.

    The supplied stages and completion flag are not stored.
    Fields cannot be reassigned after initialization.
    Entry results retain references to their tournament entries.

    Parameters
    ----------
    stages : list[TournamentStage]
        A nonempty list of stages from one tournament, ordered consecutively from stage 1. 
        All stages except the last must be complete.
    is_complete : bool
        Whether the entire tournament is complete.
        If True, 
        every supplied stage must be complete and every entry must have a confirmed final placement.

    Attributes
    ----------
    ranked_results : tuple[TournamentEntryResult, ...]
        One result per represented entry, in tournament ranking order.
        The ordering may change between snapshots while the tournament is incomplete.
    ranked_entries : tuple[TournamentEntry, ...]
        The entries in the same order as ranked_results.
    ranked_names : tuple[str, ...]
        The display names in the same order as ranked_results.

    Notes
    -----
    The caller determines tournament completion because the supplied stages 
    do not indicate whether additional stages are planned.

    Stage transitions must advance the top-ranked group and preserve the placements of entries left behind. 
    Under this rule, confirmed stage places can be reused as tournament places. 
    Transition eligibility and participant continuity are not validated by this class.

    Active entries have no confirmed tournament place.
    Eliminated entries may also have unresolved places while classification bouts remain unfinished.

    WINNER status is assigned only when the entire tournament is complete.
    Shared first places produce multiple winners.
    """
    stages: InitVar[list[TournamentStage]]
    is_complete: InitVar[bool]
    _ranked_results: tuple[TournamentEntryResult, ...] = field(init=False)


    # --- Initialization and Validation Methods ---
    def __post_init__(self, stages: list[TournamentStage], is_complete: bool) -> None:
        """
        Validate the inputs and calculate the tournament snapshot.

        Parameters
        ----------
        stages : list[TournamentStage]
            The stages from which to calculate tournament standings.
        is_complete : bool
            Whether the entire tournament is complete.

        Raises
        ------
        TypeError
            If is_complete is not a boolean, if stages is not a list,
            or if an item is not a TournamentStage.
        ValueError
            If stages is empty, if the stages belong to different tournaments,
            if stage numbers are not consecutive from 1, if any stage except the last is incomplete,
            if is_complete is True and the last stage is incomplete,
            or if the tournament is complete but an entry's latest stage result has no confirmed place.
        """
        location = self.__class__.__name__
        
        validation.validate_bool(is_complete, 'Is complete', location)
        self._validate_stages(stages, is_complete, location)

        object.__setattr__(self, '_ranked_results', self._calculate_ranked_entry_results(stages, is_complete))


    # --- Properties ---
    @property
    def ranked_results(self) -> tuple[TournamentEntryResult, ...]:
        """Return the stored entry results in tournament ranking order."""
        return self._ranked_results

    @property
    def ranked_entries(self) -> tuple[TournamentEntry, ...]:
        """Return the entries in the same order as ranked_results."""
        return tuple(result.entry for result in self.ranked_results)

    @property
    def ranked_names(self) -> tuple[str, ...]:
        """Return the display names in the same order as ranked_results."""
        return tuple(result.display_name for result in self.ranked_results)


    # --- Result Calculation Helper Methods ---
    def _calculate_ranked_entry_results(self, stages: list[TournamentStage], is_complete: bool) -> tuple[TournamentEntryResult, ...]:
        """
        Calculate tournament standings from each entry's latest stage result.

        Process stage snapshots in reverse order, 
        retaining each entry's first encountered result by entry ID. 
        Preserve stage ranking order among entries whose latest results belong to the same stage.

        For an incomplete tournament, active entries receive no tournament place. 
        Eliminated entries retain their latest stage place, which may remain unresolved.

        For a completed tournament, require a confirmed place for every entry.
        Assign WINNER to entries placed first and ELIMINATED to all others.

        Parameters
        ----------
        stages : list[TournamentStage]
            The previously validated stages in tournament order.
        is_complete : bool
            Whether the entire tournament is complete.

        Returns
        -------
        tuple[TournamentEntryResult, ...]
            One result per represented entry, in tournament ranking order.

        Raises
        ------
        ValueError
            If the tournament is complete but an entry's latest stage result has no confirmed place.
        """
        # Calculate one snapshot per stage
        stage_results: tuple[StageResults, ...] = tuple(stage.calculate_results() for stage in stages)

        ranked_stage_entry_results: list[StageEntryResult] = []
        seen_entry_ids: set[int] = set()

        # Retain each entry's latest stage result, ordered by stage reached
        for stage_result in reversed(stage_results):
            for entry_result in stage_result.ranked_results:
                if entry_result.entry.id not in seen_entry_ids:
                    ranked_stage_entry_results.append(entry_result)
                    seen_entry_ids.add(entry_result.entry.id)

        # Convert stage standings into overall tournament standings
        ranked_tournament_entry_results: list[TournamentEntryResult] = []

        for ranked_entry_result in ranked_stage_entry_results:
            entry: TournamentEntry = ranked_entry_result.entry
            stage_reached: int = ranked_entry_result.stage_number
            entry_status: TournamentEntryStatus
            entry_place: int | None

            if is_complete:
                entry_place = ranked_entry_result.place

                if entry_place is None:
                    raise ValueError(
                        'A completed tournament must have a confirmed place'
                        f' for entry {entry.id} in {self.__class__.__name__}'
                    )

                entry_status = TournamentEntryStatus.WINNER if entry_place == 1 else TournamentEntryStatus.ELIMINATED

            elif ranked_entry_result.status == StageEntryStatus.ACTIVE:
                entry_status = TournamentEntryStatus.ACTIVE
                entry_place = None

            else:
                entry_status = TournamentEntryStatus.ELIMINATED
                entry_place = ranked_entry_result.place

            ranked_tournament_entry_results.append(
                TournamentEntryResult(
                    entry=entry,
                    stage_reached=stage_reached,
                    status=entry_status,
                    place=entry_place
                )
            )

        return tuple(ranked_tournament_entry_results)


    # --- Validation Helper Methods ---
    def _validate_stages(self, stages: list[TournamentStage], is_complete: bool, location: str) -> None:
        """
        Validate the supplied stage sequence and completion consistency.

        Parameters
        ----------
        stages : list[TournamentStage]
            The proposed stage sequence.
        is_complete : bool
            Whether the entire tournament is marked complete.
        location : str
            The calling class name used in validation error messages.

        Raises
        ------
        TypeError
            If stages is not a list or an item is not a TournamentStage.
        ValueError
            If stages is empty, if the stages belong to different tournaments,
            if stage numbers are not consecutive from 1, if any stage except the last is incomplete,
            or if the tournament is marked complete and the last stage is incomplete.
        """
        if not isinstance(stages, list):
            raise TypeError(
                f'Stages must be contained in a list in {location} - got {type(stages).__name__}'
            )

        if not stages:
            raise ValueError(f'Stages list cannot be empty in {location}')

        num_stages = len(stages)
        tournament_id: int | None = None

        for i, stage in enumerate(stages):
            if not isinstance(stage, TournamentStage):
                raise TypeError(
                    f'Stage at index {i} must be a TournamentStage in '
                    f'{location} - got {type(stage).__name__}'
                )

            if i == 0:
                tournament_id = stage.tournament_id

            if stage.tournament_id != tournament_id:
                raise ValueError(
                    f'Stage at index {i} has tournament ID {stage.tournament_id}, '
                    f'which does not match the first stage\'s tournament ID {tournament_id}'
                )
            
            expected_stage_number = i + 1

            if stage.stage_number != expected_stage_number:
                raise ValueError(
                    f'Stage numbers must be consecutive from 1 in {location}'
                    f' - stage at index {i} has stage number {stage.stage_number}'
                    f', expected {expected_stage_number}'
                )
            
            is_last_stage = i == num_stages - 1

            if not is_last_stage and stage.is_incomplete():
                raise ValueError(
                    f'Stage at index {i} is incomplete in {location} - only the '
                    f'last stage at index {num_stages - 1} may be incomplete'
                )

            if is_complete and (is_last_stage and stage.is_incomplete()):
                raise ValueError(
                    f'All stages must be complete when the tournament is marked complete in {location}'
                )
