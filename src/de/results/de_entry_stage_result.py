from dataclasses import dataclass

from tournament.results.stage import StageEntryResult


@dataclass(frozen=True, slots=True)
class DEEntryStageResult(StageEntryResult):
    """
    Represent an entry's overall result within a direct-elimination stage.

    Inherits the shared stage result fields from StageEntryResult.
    Bracket-specific details are stored separately in bracket entry results.

    Attributes
    ----------
    entry : TournamentEntry
        The entry whose result is being represented.
    stage_number : int
        The one-based position of the stage within the tournament.
    status : StageEntryStatus
        The status of the entry in the stage - either ACTIVE or ELIMINATED.
    position : int
        The entry's unique one-based index in the stage snapshot's ranked_results.
        Defines display order and the relative seeding order of advancing entries.
        Does not imply a confirmed placement.
    place : int | None
        The placement of the entry in the stage.
        None if placement has not been assigned yet.
    is_tie : bool | None
        Indicates whether the placement is a tie or not.
        None if the placement has not been assigned yet.
    """
    @property
    def label(self) -> str:
        """Return a label identifying the entry, stage, and tournament."""
        return (
            f'{self.__class__.__name__} for {self.display_name} (ID={self.entry.id}) '
            f'in stage {self.stage_number} in tournament {self.tournament_id}'
        )
